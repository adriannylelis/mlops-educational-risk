from functools import lru_cache
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import logging
import time

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

_LOG_FILE = Path("src/artifacts/api_logs.jsonl")


class PredictRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "features": {
                    "IDADE_ALUNO_2020": 13,
                    "ANOS_PM_2020": 4,
                    "PONTO_VIRADA_2020": "Sim",
                    "INDE_2020": 7.5,
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
            }
        }
    )

    score_risco: float
    classe_risco: str


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
    request.state.score_risco = score_risco
    predict_payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "event": "prediction",
        "score_risco": score_risco,
        "classe_risco": classe_risco,
    }
    logger.info(json.dumps(predict_payload, ensure_ascii=False))

    return PredictResponse(score_risco=score_risco, classe_risco=classe_risco)
