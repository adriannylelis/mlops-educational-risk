# 🎓 MLOps - Sistema de Predição de Risco Educacional
## Passos Mágicos: Educational Risk Prediction

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-4%2F4%20passing-success)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-91%25-brightgreen)](tests/)

---

## 📋 Índice

1. [Problema de Negócio](#-problema-de-negócio)
2. [Arquitetura e Componentes](#-arquitetura-e-componentes)
3. [Instruções para Subir o Ambiente](#-instruções-para-subir-o-ambiente)
4. [Pipeline de Machine Learning](#-pipeline-de-machine-learning)
5. [Métricas e Confiabilidade do Modelo](#-métricas-e-confiabilidade-do-modelo)
6. [Testes e Qualidade](#-testes-e-qualidade)
7. [API e Explicabilidade](#-api-e-explicabilidade)
8. [Monitoramento](#-monitoramento)
9. [Decisões Técnicas](#-decisões-técnicas)

---

## 🎯 Problema de Negócio

### Contexto
A **Associação Passos Mágicos** atende crianças e adolescentes em situação de vulnerabilidade social, oferecendo educação de qualidade e acompanhamento psicossocial. Um desafio crítico é **identificar precocemente alunos em risco de defasagem escolar** para direcionar intervenções pedagógicas e psicossociais de forma eficaz.

#### Definição de Defasagem
Um aluno está em **defasagem** quando sua fase escolar atual está abaixo do nível ideal esperado para sua idade/ano de ingresso:
```
DEFASAGEM = FASE_ATUAL - NIVEL_IDEAL
```
- **Defasagem < 0**: Aluno abaixo do esperado ⚠️
- **Defasagem ≥ 0**: Aluno no nível adequado ✅

### Objetivo do Modelo
Prever a **probabilidade de um aluno entrar em defasagem no ano seguinte** com base em seus indicadores educacionais e psicossociais do ano atual. Isso permite:

✅ **Intervenção precoce** — identificar alunos de risco antes que a defasagem se concretize  
✅ **Otimização de recursos** — priorizar ações pedagógicas nos casos mais críticos  
✅ **Acompanhamento personalizado** — adaptar apoio psicossocial às necessidades reais  
✅ **Auditabilidade** — explicar por que um aluno foi classificado como "alto risco"

---

## 🏗️ Arquitetura e Componentes

### Visão Geral
```
┌─────────────────────────────────────────────────────────────────┐
│                    DATASET PANEL (2020→2021 + 2021→2022)        │
│                        1.548 linhas | 12 features               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────▼─────────────┐
                │  TRAIN PIPELINE          │
                │  • Imputation            │
                │  • Scaling               │
                │  • OneHotEncoder         │
                │  • Model Selection       │
                └────────────┬─────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
    ┌─────────┐      ┌──────────────┐   ┌──────────┐
    │ MODEL   │      │  METRICS     │   │ DATASET  │
    │ .joblib │      │  .json       │   │ .csv     │
    └────┬────┘      └──────────────┘   └──────────┘
         │
         │
    ┌────▼─────────────────────────────────────────────┐
    │           FASTAPI INFERENCE SERVER               │
    │  • POST /predict → score + classe + motivos      │
    │  • GET /logs     → auditoria JSONL               │
    │  • SHAP explanations (TreeExplainer)             │
    └────┬─────────────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────────────┐
    │           MONITORING DASHBOARD                    │
    │  • PSI Drift Report                              │
    │  • Últimas Predições                             │
    │  • Distribuição de Scores                        │
    └──────────────────────────────────────────────────┘
```

### Estrutura de Diretórios
```
mlops-educational-risk/
├── app/
│   └── main.py                    # FastAPI server (inference + logs)
├── src/
│   ├── data/
│   │   └── build_training_dataset.py  # Formação do dataset panel
│   ├── model/
│   │   └── train.py               # Treinamento e seleção de modelo
│   ├── monitoring/
│   │   ├── drift_report.py        # Cálculo de PSI drift
│   │   └── dashboard.html         # Painel HTML de monitoramento
│   └── artifacts/                 # Artefatos gerados (modelo, logs, etc.)
├── tests/
│   ├── test_api.py                # Testes da API
│   ├── test_monitoring.py         # Testes de drift
│   └── test_train_artifacts.py    # Testes do treinamento
├── base_dados/
│   └── PEDE_PASSOS_DATASET_FIAP.csv  # Dataset fonte original
├── docs/                          # Documentação técnica
├── docker-compose.yml             # Orquestração de serviços
├── Dockerfile                     # Imagem base Python 3.11
└── requirements.txt               # Dependências fixadas
```

---

## 🚀 Instruções para Subir o Ambiente

### Pré-requisitos
- **Docker** ≥ 20.10
- **Docker Compose** ≥ 2.0
- **Git** (para clonar o repositório)

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/adriannylelis/mlops-educational-risk.git
cd mlops-educational-risk
```

### Passo 2: Treinar o Modelo
```bash
docker compose run --rm train
```
**O que acontece:**
- Lê `base_dados/PEDE_PASSOS_DATASET_FIAP.csv`
- Cria dataset longitudinal (2020→2021 + 2021→2022)
- Treina 2 candidatos: `LogisticRegression` e `RandomForestClassifier`
- Seleciona o melhor modelo por **Recall** (tiebreak: F1)
- Gera artefatos em `src/artifacts/`:
  - `model.joblib` — Pipeline scikit-learn completo
  - `metrics.json` — Métricas de validação
  - `training_dataset.csv` — Dataset processado
  - `training_dataset_metadata.json` — Metadados

**Saída esperada:**
```
Selected model: random_forest (Recall: 0.776, F1: 0.796, PR-AUC: 0.851)
```

### Passo 3: Executar Testes
```bash
docker compose run --rm tests
```
**Saída esperada:**
```
4 passed in ~5s
Coverage: 91%
```

### Passo 4: Subir a API
```bash
docker compose up api
```
**API disponível em:** `http://localhost:8000`  
**Swagger Docs:** `http://localhost:8000/docs`

### Passo 5: Gerar Relatório de Drift (Opcional)
```bash
docker compose run --rm monitor
```
Gera `src/artifacts/drift_report.json` com PSI de cada feature.

### Passo 6: Visualizar Dashboard de Monitoramento (Opcional)
```bash
docker compose up dashboard
```
**Dashboard disponível em:** `http://localhost:8501/src/monitoring/dashboard.html`

---

## ⚙️ Pipeline de Machine Learning

### 1. Pré-processamento dos Dados

#### Estratégia: Dataset Longitudinal (Panel)
O modelo é **ano-agnóstico**: usa features do ano N para prever defasagem no ano N+1. Empilhamos dois períodos:

| Período | Features (ano N) | Target (ano N+1) | Linhas |
|---------|------------------|------------------|--------|
| 2020→2021 | Índices de 2020 | `DEFASAGEM_2021 < 0` | 686 |
| 2021→2022 | Índices de 2021 | `FASE_2022 - NIVEL_IDEAL_2022 < 0` | 862 |
| **Total** | | | **1.548** |

**Vantagens:**
- ✅ ~2.3x mais dados (de 686 → 1.548 linhas)
- ✅ Generaliza para anos futuros sem retreinamento
- ✅ Melhora recall de 0.571 → 0.776 (+36%)

#### Imputação de Valores Ausentes
| Tipo de Feature | Estratégia | Justificativa |
|-----------------|-----------|---------------|
| Numéricas (INDE, IAA, IAN, IDA, IEG, IPP, IPS, IPV, FASE, ANO_REFERENCIA) | **Mediana** | Robusta a outliers, preserva distribuição central |
| Categóricas (PEDRA) | **Moda** | Mantém a categoria mais frequente como baseline |
| Booleanas (PONTO_VIRADA) | **-1 → Mediana** | Normalizado para int (1/0/-1), trata como numérica |

#### Normalização e Encoding
- **StandardScaler** nas numéricas → média 0, desvio-padrão 1
- **OneHotEncoder** em PEDRA → colunas binárias (`PEDRA_Quartzo`, `PEDRA_Ágata`, etc.)

### 2. Engenharia de Features

#### Features Selecionadas (12 total)
```python
COMMON_INDEX_FEATURES = [
    "INDE",  # Índice de Desenvolvimento Educacional (agregado)
    "IAA",   # Índice de Autoavaliação
    "IAN",   # Índice de Avaliação
    "IDA",   # Índice de Desenvolvimento Acadêmico
    "IEG",   # Índice de Engajamento
    "IPP",   # Índice de Ponto de Partida
    "IPS",   # Índice Psicossocial
    "IPV",   # Índice de Ponto de Virada
]
COMMON_CATEGORICAL_FEATURES = ["PEDRA"]  # Quartzo, Ágata, Topázio, Diamante
COMMON_BOOLEAN_FEATURES = ["PONTO_VIRADA"]  # 0/1
OUTROS = ["FASE", "ANO_REFERENCIA"]
```



### 3. Treinamento e Validação

#### Divisão de Dados
```python
train_test_split(
    test_size=0.2,       # 80% train (1.238 linhas) | 20% test (310 linhas)
    random_state=42,     # Reprodutibilidade
    stratify=target      # Mantém proporção de classes
)
```

#### Pipeline Completo
```python
Pipeline([
    ("preprocessing", ColumnTransformer([
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore"))
        ]))
    ])),
    ("classifier", RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42
    ))
])
```

### 4. Seleção de Modelo

#### Candidatos Avaliados
| Modelo | Recall | Precision | F1 | PR-AUC | Decisão |
|--------|--------|-----------|----|----|---------|
| **RandomForestClassifier** | **0.776** | 0.817 | 0.796 | 0.851 | ✅ Selecionado |
| LogisticRegression | 0.726 | 0.832 | 0.776 | 0.843 | ❌ |

#### Critério de Seleção: Recall
**Por que Recall é a métrica principal?**

No contexto de risco educacional:
- **Falso Negativo (FN)** → Aluno em risco identificado como "baixo risco"  
  → **Crítico!** Não recebe intervenção, defasagem se concretiza
- **Falso Positivo (FP)** → Aluno saudável identificado como "alto risco"  
  → Menos grave: recebe apoio extra, sem malefícios

```
Recall = TP / (TP + FN)
```
**Interpretação:** 77.6% dos alunos que realmente entrarão em defasagem são identificados pelo modelo.

**Tiebreaker: F1** → Balanceia Recall e Precision quando empate.

---

## 📊 Métricas e Confiabilidade do Modelo

### Desempenho em Validação (Test Set)

```json
{
  "selected_model": "random_forest",
  "rows_train": 1238,
  "rows_test": 310,
  "positive_rate": 0.707,  // 70.7% dos alunos estão em risco (dataset desbalanceado)
  "metrics": {
    "recall": 0.776,        // Captura 77.6% dos casos de risco real
    "precision": 0.817,     // 81.7% das predições "alto risco" estão corretas
    "f1": 0.796,            // Média harmônica balanceada
    "pr_auc": 0.851         // Área sob curva Precision-Recall (excelente)
  }
}
```


#### 1. **Métrica Recall Alinhada ao Negócio** ✅
- **77.6% de recall** → 3 em cada 4 alunos em risco real são identificados
- Comparação: baseline ingênuo (prever sempre "alto risco") teria Precision muito baixa

#### 2. **Validação em Dados Não Vistos** ✅
- **Holdout 20%** estratificado → modelo nunca viu esses 310 alunos durante treinamento
- **PR-AUC 0.851** → performance robusta em diferentes thresholds de decisão

#### 3. **Explicabilidade via SHAP** ✅
- Cada predição vem com **top 3 features** que mais influenciaram o score
- Exemplo:
  ```json
  "possivel_motivo": [
    "Índice de Desenvolvimento Educacional (INDE) = 4.5 (ideal: ≥ 7.0)",
    "Ponto de Virada (PONTO_VIRADA) = 0 (ideal: 1 (atingido))",
    "Índice de Engajamento (IEG) ausente (ideal: ≥ 7.0)"
  ]
  ```
- **Auditabilidade:** Gestores podem validar se a decisão faz sentido pedagógico

#### 4. **Generalização Temporal** ✅
- Dataset panel (2020+2021) → modelo funciona em anos futuros sem retreinamento
- Feature `ANO_REFERENCIA` captura padrões específicos de cada período

#### 5. **Pipeline Reprodutível e Testado** ✅
- **91% de cobertura de testes** (acima dos 80% exigidos)
- Docker Compose → ambiente idêntico dev/prod
- Artefatos versionados (model.joblib, metrics.json)

#### 6. **Regularização e Prevenção de Overfitting** ✅
- `class_weight="balanced"` → compensa desbalanceamento
- `min_samples_leaf=3` → previne árvores muito profundas
- Random Forest → ensemble reduz variância

#### 7. **Monitoramento de Drift** ✅
- PSI (Population Stability Index) calcula drift de cada feature
- Dashboard em tempo real mostra últimas predições e distribuição de scores

---

## ✅ Testes e Qualidade

### Cobertura de Testes: 91% ✅
```
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
app/main.py                            152     30    80%
src/data/build_training_dataset.py      53      1    98%
src/model/train.py                      46      1    98%
src/monitoring/drift_report.py          63      3    95%
tests/test_api.py                       20      0   100%
tests/test_monitoring.py                16      0   100%
tests/test_train_artifacts.py           29      0   100%
--------------------------------------------------------
TOTAL                                  379     35    91%
```
> **Critério atendido:** Cobertura acima de 80% ✅

### Suíte de Testes (4 testes, 100% passing)

#### 1. `test_health_endpoint` (test_api.py)
```python
def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```
**Valida:** Liveness da API.

#### 2. `test_predict_endpoint_returns_score_and_class` (test_api.py)
```python
def test_predict_endpoint_returns_score_and_class() -> None:
    train_and_save_artifacts(artifacts_dir=Path("src/artifacts"))
    response = client.post("/predict", json={"features": {}})
    
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"score_risco", "classe_risco", "possivel_motivo"}
    assert 0.0 <= payload["score_risco"] <= 1.0
    assert payload["classe_risco"] in {"alto", "baixo"}
    assert isinstance(payload["possivel_motivo"], list)
```
**Valida:**
- Treinamento gera modelo funcional
- Endpoint `/predict` retorna schema correto
- Explicabilidade SHAP retorna lista de motivos

#### 3. `test_generate_drift_report` (test_monitoring.py)
```python
def test_generate_drift_report() -> None:
    generate_drift_report(...)
    
    assert report_path.exists()
    report = json.loads(report_path.read_text())
    assert "psi_scores" in report
    for feature, psi in report["psi_scores"].items():
        assert isinstance(psi, (int, float))
        assert psi >= 0.0
```
**Valida:**
- Cálculo de PSI para cada feature
- Formato JSON correto do drift report

#### 4. `test_train_generates_model_and_metrics` (test_train_artifacts.py)
```python
def test_train_generates_model_and_metrics() -> None:
    train_and_save_artifacts(artifacts_dir=temp_dir)
    
    assert (temp_dir / "model.joblib").exists()
    assert (temp_dir / "metrics.json").exists()
    
    model = joblib.load(temp_dir / "model.joblib")
    metrics = json.loads((temp_dir / "metrics.json").read_text())
    
    assert hasattr(model, "predict_proba")
    assert "recall" in metrics["selected_metrics"]
    assert 0.0 <= metrics["selected_metrics"]["recall"] <= 1.0
```
**Valida:**
- Pipeline de treinamento gera artefatos obrigatórios
- Modelo serializado é carregável
- Métricas contêm valores válidos

### Execução Local (sem Docker)
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
pytest tests/ -v
```

---

## 🔌 API e Explicabilidade

### Endpoints Disponíveis

#### `POST /predict` — Predição de Risco
**Request:**
```json
{
  "features": {
    "INDE": 4.5,
    "IAA": 5.0,
    "PEDRA": "Quartzo",
    "PONTO_VIRADA": 0,
    "FASE": 2,
    "ANO_REFERENCIA": 2020
  }
}
```

**Response:**
```json
{
  "score_risco": 0.796,
  "classe_risco": "alto",
  "possivel_motivo": [
    "Índice de Desenvolvimento Educacional (INDE) = 4.5 (ideal: ≥ 7.0)",
    "Índice de Autoavaliação (IAA) = 5.0 (ideal: ≥ 7.0)",
    "Índice de Engajamento (IEG) ausente (ideal: ≥ 7.0)"
  ]
}
```

**Explicabilidade:**
- `score_risco` → Probabilidade P(risco=1) ∈ [0, 1]
- `classe_risco` → "alto" se score ≥ 0.5, "baixo" caso contrário
- `possivel_motivo` → Top 3 features ordenadas por **importância SHAP** para aquela predição específica
  - Features no ideal mostram ✓
  - Features fora do ideal mostram valor esperado

#### `GET /logs?n=100` — Auditoria
**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2026-03-12 02:51:20 UTC",
      "event": "prediction",
      "score_risco": 0.82,
      "classe_risco": "alto",
      "possivel_motivo": ["..."]
    },
    {
      "timestamp": "2026-03-12 02:51:20 UTC",
      "event": "request",
      "path": "/predict",
      "method": "POST",
      "status_code": 200,
      "latency_ms": 104.56,
      "score_risco": 0.82,
      "error": null
    }
  ],
  "total": 200
}
```
Persiste em `src/artifacts/api_logs.jsonl` para auditoria externa.

#### `GET /health` — Liveness Probe
```json
{"status": "ok"}
```

#### `GET /` — Docs Index
```json
{
  "message": "Passos Mágicos Risk API",
  "docs": "/docs",
  "redoc": "/redoc",
  "openapi": "/openapi.json"
}
```

### Coleção Postman
Importar: `docs/passos-magicos-risk-api.postman_collection.json`

---

## 📈 Monitoramento

### 1. Drift Detection (PSI)
**Population Stability Index** mede se a distribuição de cada feature mudou entre treino e produção.

**Comando:**
```bash
docker compose run --rm monitor
```

**Saída:** `src/artifacts/drift_report.json`
```json
{
  "psi_scores": {
    "INDE": 0.023,         // < 0.1 → Sem drift
    "IAA": 0.045,
    "PEDRA": 0.012,
    "PONTO_VIRADA": 0.008
  },
  "interpretation": {
    "INDE": "No drift detected (PSI < 0.1)"
  }
}
```

**Thresholds:**
- PSI < 0.1 → ✅ Sem drift
- 0.1 ≤ PSI < 0.25 → ⚠️ Drift moderado (investigar)
- PSI ≥ 0.25 → 🚨 Drift severo (retreinar modelo)

### 2. Dashboard HTML
**URL:** `http://localhost:8501/src/monitoring/dashboard.html`

**Seções:**
1. **Drift de Features (PSI)** — Gráfico de barras com threshold 0.1
2. **Últimas Predições** — Tabela com timestamp, score, classe, motivos (fetch via `/logs`)

---

## 🧠 Decisões Técnicas

### 1. Random Forest vs Logistic Regression
**Escolhido:** Random Forest  
**Motivo:** +5% de recall (0.776 vs 0.726) sem perda significativa de precision

### 2. Recall como métrica principal
**Motivo:** Falsos Negativos são mais custosos no contexto educacional (criança em risco não identificada)

### 3. Dataset Longitudinal (Panel)
**Motivo:** +862 linhas (2021→2022) sem coletar novos dados, melhora generalização temporal

### 4. SHAP para Explicabilidade
**Motivo:** 
- TreeExplainer é rápido (~100ms por predição) para Random Forest
- Fornece importância específica da predição (vs feature importance global)
- Auditável por gestores não-técnicos


### 5. Docker Compose
**Motivo:** 
- Ambiente dev/prod idêntico
- Serviços isolados (train, tests, api, monitor, dashboard)
- Reprodutibilidade garantida

### 6. Versionamento de Dependências
`requirements.txt` com versões fixadas (ex: `scikit-learn==1.6.1`) → evita quebras em deploys futuros

---

## 📚 Documentação Adicional

- [Decisões de Modelagem](docs/modeling-decisions.md) — Formação do dataset panel
- [Seleção de Modelo](docs/model-selection.md) — Comparativo de candidatos
- [Documentação da API](docs/api-documentacao.md) — Schemas e exemplos
- [Deploy GCP](docs/gcp-deploy.md) — Instruções para Cloud Run



## 📄 Licença

[MIT License](LICENSE)

