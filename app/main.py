from functools import lru_cache
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import logging
import time

import joblib
import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

_LOG_FILE = Path("src/artifacts/api_logs.jsonl")

# Mapeamento de siglas para descrições completas das features
_FEATURE_DESCRIPTIONS = {
    "INDE": "Índice de Desenvolvimento Educacional (INDE)",
    "IAA": "Índice de Autoavaliação (IAA)",
    "IAN": "Índice de Avaliação (IAN)",
    "IDA": "Índice de Desenvolvimento Acadêmico (IDA)",
    "IEG": "Índice de Engajamento (IEG)",
    "IPP": "Índice de Ponto de Partida (IPP)",
    "IPS": "Índice Psicossocial (IPS)",
    "IPV": "Índice de Ponto de Virada (IPV)",
    "PEDRA": "Pedra (PEDRA)",
    "PONTO_VIRADA": "Ponto de Virada (PONTO_VIRADA)",
    "FASE": "Fase (FASE)",
    "ANO_REFERENCIA": "Ano de Referência (ANO_REFERENCIA)",
}

# Valores ideais/recomendados para cada feature (baseado em análise do dataset)
_FEATURE_IDEALS = {
    "INDE": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "IAA": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "IAN": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "IDA": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "IEG": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "IPP": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "IPS": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "IPV": ("≥ 7.0", lambda v: v is not None and v >= 7.0),
    "PEDRA": ("Topázio ou Diamante", lambda v: v in ["Topázio", "Diamante"]),
    "PONTO_VIRADA": ("1 (atingido)", lambda v: v == 1),
    "FASE": ("≥ 4", lambda v: v is not None and v >= 4),
}


class PredictRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "features": {
                    "INDE": 7.5,
                    "IAA": 7.8,
                    "PEDRA": "Topázio",
                    "PONTO_VIRADA": 1,
                    "FASE": 4,
                    "ANO_REFERENCIA": 2021,
                }
            }
        }
    )

    features: dict[str, Any] = Field(
        default_factory=dict,
        description="Dicionário de features de entrada para inferência.",
    )


class PredictResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score_risco": 0.59,
                "classe_risco": "alto",
                "possivel_motivo": [
                    "Índice de Desenvolvimento Educacional (INDE) = 3.2 (ideal: ≥ 7.0)",
                    "Ponto de Virada (PONTO_VIRADA) = 0 (ideal: 1 (atingido))",
                    "Índice de Autoavaliação (IAA) = 7.8 (ideal: ≥ 7.0 ✓)",
                ],
            }
        }
    )

    score_risco: float
    classe_risco: str
    possivel_motivo: list[str]


app = FastAPI(
    title="Passos Mágicos Risk API",
    description="API de inferência para predição de risco de defasagem escolar.",
    version="1.0.0",
)

# Permite que o dashboard (porta 8501) acesse a API (porta 8000) sem bloqueio de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO, format="%(message)s")

# File handler — persiste logs em JSONL para auditoria e evidência de monitoramento
_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
_file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_file_handler)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    status_code = 500
    error_message = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as error:
        error_message = str(error)
        raise
    finally:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        payload = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "event": "request",
            "path": request.url.path,
            "method": request.method,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "score_risco": getattr(request.state, "score_risco", None),
            "error": error_message,
        }
        logger.info(json.dumps(payload, ensure_ascii=False))


def _extract_feature_columns(model: Any) -> tuple[list[str], list[str]]:
    preprocessing = model.named_steps["preprocessing"]
    numeric_columns = list(preprocessing.transformers[0][2])
    categorical_columns = list(preprocessing.transformers[1][2])
    return numeric_columns, categorical_columns


@lru_cache(maxsize=1)
def _load_model() -> Any:
    model_path = Path("src/artifacts/model.joblib")
    if not model_path.exists():
        raise FileNotFoundError("Modelo não encontrado. Execute: docker compose run --rm train")
    return joblib.load(model_path)


def _compute_shap_explanation(
    model: Any,
    feature_frame: pd.DataFrame,
    original_features: dict[str, Any],
    top_n: int = 3,
) -> list[str]:
    """Calcula explicação SHAP para a predição.

    Args:
        model: Pipeline scikit-learn com preprocessing + classifier.
        feature_frame: DataFrame com features já preprocessadas.
        original_features: Dicionário original de features (para exibir valores).
        top_n: Número de features mais importantes a retornar.

    Returns:
        Lista de strings explicando as top_n features que mais contribuíram.
    """
    # Aplica preprocessing e extrai features transformadas
    X_transformed = model.named_steps["preprocessing"].transform(feature_frame)
    classifier = model.named_steps["classifier"]

    # TreeExplainer para Random Forest (rápido, exato para árvores)
    explainer = shap.TreeExplainer(classifier)
    shap_values = explainer.shap_values(X_transformed)

    # shap_values retorna [shap_class_0, shap_class_1] para classificação binária
    # Queremos classe 1 (risco alto)
    if isinstance(shap_values, list):
        # Classificação binária: shap_values[1] tem shape [n_samples, n_features]
        shap_values_class_1 = shap_values[1][0]  # Pega primeira (e única) amostra
    else:
        # Caso edge: apenas uma classe
        shap_values_class_1 = shap_values[0]
    
    # Garante que é um array 1D (flatten caso seja [1, n_features])
    shap_values_class_1 = np.asarray(shap_values_class_1).flatten()

    # Extrai nomes das features depois do preprocessing
    feature_names = _get_transformed_feature_names(model)

    # Mapeia cada feature transformada para o score SHAP
    # shap_values_class_1 agora é um array 1D de tamanho n_features
    # Converte cada score numpy para float Python
    feature_contributions = []
    for name, score in zip(feature_names, shap_values_class_1):
        # score pode ser numpy scalar, usa .item() para converter para Python float
        try:
            score_value = float(score)
        except (TypeError, ValueError):
            score_value = score.item() if hasattr(score, 'item') else 0.0
        feature_contributions.append((name, score_value))

    # Ordena por valor absoluto da contribuição (mais importante primeiro)
    feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)

    # Formata as top_n explicações com valores ideais
    explanations = []
    for feature_name, contribution in feature_contributions[:top_n]:
        # Tenta mapear feature transformada de volta para original
        original_name = _map_to_original_feature(feature_name)
        description = _FEATURE_DESCRIPTIONS.get(original_name, original_name)
        value = original_features.get(original_name)
        
        # Obtém valor ideal e função de validação
        ideal_info = _FEATURE_IDEALS.get(original_name)
        
        if value is None:
            # Feature ausente
            if ideal_info:
                ideal_str, _ = ideal_info
                explanations.append(f"{description} ausente (ideal: {ideal_str})")
            else:
                explanations.append(f"{description} ausente")
        else:
            # Feature presente — verifica se está no ideal
            if ideal_info:
                ideal_str, is_ideal_fn = ideal_info
                if is_ideal_fn(value):
                    explanations.append(f"{description} = {value} ✓")
                else:
                    explanations.append(f"{description} = {value} (ideal: {ideal_str})")
            else:
                explanations.append(f"{description} = {value}")

    return explanations


def _get_transformed_feature_names(model: Any) -> list[str]:
    """Extrai nomes das features após preprocessing."""
    preprocessing = model.named_steps["preprocessing"]
    feature_names = []
    
    for name, transformer, columns in preprocessing.transformers_:
        if name == "numeric":
            feature_names.extend(columns)
        elif name == "categorical":
            # OneHotEncoder gera múltiplas colunas
            encoder = transformer.named_steps["encoder"]
            if hasattr(encoder, "get_feature_names_out"):
                feature_names.extend(encoder.get_feature_names_out(columns))
            else:
                feature_names.extend(columns)
    
    return feature_names


def _map_to_original_feature(transformed_name: str) -> str:
    """Mapeia nome de feature transformada de volta para original.
    
    OneHotEncoder transforma 'PEDRA' em 'PEDRA_Quartzo', 'PEDRA_Ágata', etc.
    Esta função remove o sufixo para recuperar 'PEDRA'.
    """
    for original in _FEATURE_DESCRIPTIONS.keys():
        if transformed_name.startswith(original):
            return original
    return transformed_name


@app.get("/", tags=["docs"])
def root() -> dict[str, str]:
    return {
        "message": "Passos Mágicos Risk API",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health",
        "predict": "/predict",
    }


@app.get("/health", tags=["health"], summary="Health check da API")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/logs", tags=["monitoring"], summary="Retorna as últimas N linhas do log da API")
def get_logs(n: int = 100) -> JSONResponse:
    if not _LOG_FILE.exists():
        return JSONResponse(content={"logs": [], "total": 0})
    lines = _LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    recent = lines[-n:]
    parsed = []
    for line in recent:
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            parsed.append({"raw": line})
    return JSONResponse(content={"logs": parsed, "total": len(lines)})


@app.post(
    "/predict",
    response_model=PredictResponse,
    tags=["prediction"],
    summary="Realiza predição de risco",
)
def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    try:
        model = _load_model()
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    numeric_columns, categorical_columns = _extract_feature_columns(model)
    expected_columns = numeric_columns + categorical_columns

    row = {column: payload.features.get(column) for column in expected_columns}
    feature_frame = pd.DataFrame([row])

    for column in numeric_columns:
        feature_frame[column] = pd.to_numeric(feature_frame[column], errors="coerce")

    probabilities = model.predict_proba(feature_frame)
    score_risco = float(probabilities[0][1])
    classe_risco = "alto" if score_risco >= 0.5 else "baixo"
    
    # Computa explicação SHAP
    possivel_motivo = _compute_shap_explanation(
        model=model,
        feature_frame=feature_frame,
        original_features=payload.features,
        top_n=3,
    )
    
    request.state.score_risco = score_risco
    predict_payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "event": "prediction",
        "score_risco": score_risco,
        "classe_risco": classe_risco,
        "possivel_motivo": possivel_motivo,
    }
    logger.info(json.dumps(predict_payload, ensure_ascii=False))

    return PredictResponse(
        score_risco=score_risco,
        classe_risco=classe_risco,
        possivel_motivo=possivel_motivo,
    )
