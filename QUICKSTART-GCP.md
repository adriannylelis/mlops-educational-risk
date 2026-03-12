# 🚀 Quickstart: Deploy na GCP em 5 Minutos

Guia ultra-rápido para fazer o primeiro deploy da API de Predição de Risco na Google Cloud Platform.

## ⚡ Deploy Rápido (TL;DR)

```bash
# 1. Autenticar no GCP
gcloud auth login

# 2. Definir projeto
export PROJECT_ID="seu-projeto-gcp"
gcloud config set project $PROJECT_ID

# 3. Deploy
PROJECT_ID=$PROJECT_ID ./scripts/deploy_cloud_run.sh

# 4. Testar
SERVICE_URL=$(gcloud run services describe risk-api --region=us-central1 --format='value(status.url)')
curl $SERVICE_URL/health
```

**Pronto!** API em produção em ~5 minutos.

---

## 📋 Pré-requisitos (Primeira vez)

### 1. Instalar Google Cloud SDK

**MacOS:**
```bash
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**  
Baixar: https://cloud.google.com/sdk/docs/install#windows

### 2. Criar Projeto GCP

1. Acesse: https://console.cloud.google.com
2. Crie novo projeto ou selecione existente
3. Habilite billing (necessário para Cloud Run)
4. Anote o `PROJECT_ID`

### 3. Treinar Modelo Localmente

```bash
# Treinar modelo (gera artifacts)
docker compose run --rm train

# Verificar artefatos
ls -lh src/artifacts/model.joblib
ls -lh src/artifacts/metrics.json

# Testar localmente
docker compose up api
curl http://localhost:8000/health
docker compose down
```

---

## 🌐 Deploy

### Opção 1: Deploy Automático (Recomendado)

```bash
export PROJECT_ID="seu-projeto-gcp"
PROJECT_ID=$PROJECT_ID ./scripts/deploy_cloud_run.sh
```

**O que acontece:**
1. Habilita APIs (Cloud Build, Artifact Registry, Cloud Run)
2. Cria repositório Docker
3. Constrói imagem
4. Faz deploy
5. Retorna URL pública

**Tempo:** ~3-5 minutos

### Opção 2: Deploy Manual (Passo a Passo)

```bash
# 1. Habilitar APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com

# 2. Criar repositório Docker
gcloud artifacts repositories create mlops-risk \
  --repository-format=docker \
  --location=us-central1 \
  --description="MLOps Risk API"

# 3. Build com Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_REPOSITORY=mlops-risk,_IMAGE=risk-api,_TAG=latest

# 4. Deploy no Cloud Run
gcloud run deploy risk-api \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/mlops-risk/risk-api:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --port=8080
```

---

## ✅ Verificar Deploy

### Pegar URL da API
```bash
SERVICE_URL=$(gcloud run services describe risk-api \
  --region=us-central1 \
  --format='value(status.url)')

echo "URL da API: $SERVICE_URL"
```

### Health Check
```bash
curl $SERVICE_URL/health
```

**Esperado:** `{"status": "ok"}`

### Predição de Teste
```bash
curl -X POST $SERVICE_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "INDE": 5.2,
    "IAA": 6.1,
    "IAN": 5.8,
    "IDA": 6.5,
    "IEG": 7.2,
    "IPP": 5.9,
    "IPS": 6.3,
    "IPV": 5.7,
    "PEDRA": "Ametista",
    "PONTO_VIRADA": 0,
    "FASE": 3,
    "ANO_REFERENCIA": 2021
  }'
```

**Esperado:**
```json
{
  "score_risco": 0.73,
  "classe_risco": "alto",
  "possivel_motivo": [
    "Índice de Desenvolvimento Educacional (INDE) = 5.2 (ideal: ≥ 7.0)",
    "..."
  ]
}
```

### Documentação Interativa
```bash
# MacOS
open $SERVICE_URL/docs

# Linux
xdg-open $SERVICE_URL/docs

# Windows
start $SERVICE_URL/docs
```

---

## 📊 Monitorar

### Ver Logs em Tempo Real
```bash
gcloud run services logs tail risk-api --region=us-central1
```

### Ver Console GCP
```bash
gcloud run services describe risk-api --region=us-central1
```

---

## 💰 Custos

**Tier Gratuito Cloud Run:**
- 2 milhões requisições/mês
- 360.000 GB-segundos memória
- 180.000 vCPU-segundos

**Estimativa real:**
- 10k requisições/mês: **$0** (tier gratuito)
- 100k requisições/mês: **~$3**
- 1M requisições/mês: **~$25**

---

## 🔄 Atualizar API

```bash
# 1. Fazer mudanças no código
# 2. Treinar novo modelo (se necessário)
docker compose run --rm train

# 3. Re-deploy
PROJECT_ID=$PROJECT_ID ./scripts/deploy_cloud_run.sh
```

**Tempo de atualização:** ~3 minutos

---

## 🧹 Deletar

```bash
# Deletar serviço
gcloud run services delete risk-api --region=us-central1

# Deletar imagens
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/$PROJECT_ID/mlops-risk/risk-api:latest

# Deletar repositório
gcloud artifacts repositories delete mlops-risk --location=us-central1
```

---

## 🆘 Problemas Comuns

### Erro: "Permission denied"
```bash
gcloud auth login
gcloud auth application-default login
```

### Erro: "Billing not enabled"
- Ativar billing no console: https://console.cloud.google.com/billing

### Erro: "API not enabled"
```bash
gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com
```

### API retorna 500
```bash
# Ver logs
gcloud run services logs read risk-api --region=us-central1 --limit=50
```

---

## 📚 Documentação Completa

Para setup detalhado e troubleshooting:
- **Setup Completo:** [docs/gcp-setup.md](gcp-setup.md)
- **Guia de Deploy:** [docs/gcp-deploy.md](gcp-deploy.md)
- **Checklist:** [docs/deploy-checklist.md](deploy-checklist.md)

---

**Última atualização:** 12 de março de 2026
