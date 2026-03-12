#!/bin/bash
# Deploy script para Cloud Run via Cloud Build e Artifact Registry
# Uso: PROJECT_ID=meu-projeto ./scripts/deploy_cloud_run.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validação de variáveis obrigatórias
if [ -z "$PROJECT_ID" ]; then
  echo -e "${RED}❌ Erro: PROJECT_ID não definido${NC}"
  echo "Uso: PROJECT_ID=meu-projeto $0"
  exit 1
fi

# Variáveis com valores padrão
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-mlops-risk}"
IMAGE_NAME="${IMAGE_NAME:-risk-api}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
SERVICE_NAME="${SERVICE_NAME:-risk-api}"
MEMORY="${MEMORY:-512Mi}"
CPU="${CPU:-1}"
MAX_INSTANCES="${MAX_INSTANCES:-10}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
TIMEOUT="${TIMEOUT:-300}"

echo -e "${GREEN}🚀 Iniciando deploy na GCP${NC}"
echo "────────────────────────────────────────"
echo "Projeto: $PROJECT_ID"
echo "Região: $REGION"
echo "Repositório: $REPOSITORY"
echo "Imagem: $IMAGE_NAME:$IMAGE_TAG"
echo "Serviço: $SERVICE_NAME"
echo "────────────────────────────────────────"

# Configurar projeto
echo -e "${YELLOW}📋 Configurando projeto GCP...${NC}"
gcloud config set project "$PROJECT_ID"

# Habilitar APIs necessárias
echo -e "${YELLOW}🔌 Habilitando APIs necessárias...${NC}"
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  --project="$PROJECT_ID"

# Criar repositório no Artifact Registry (se não existir)
echo -e "${YELLOW}📦 Verificando Artifact Registry...${NC}"
if ! gcloud artifacts repositories describe "$REPOSITORY" \
  --location="$REGION" \
  --project="$PROJECT_ID" &>/dev/null; then
  echo -e "${YELLOW}📦 Criando repositório $REPOSITORY...${NC}"
  gcloud artifacts repositories create "$REPOSITORY" \
    --repository-format=docker \
    --location="$REGION" \
    --description="MLOps Educational Risk - Docker images" \
    --project="$PROJECT_ID"
else
  echo -e "${GREEN}✅ Repositório $REPOSITORY já existe${NC}"
fi

# Build da imagem usando Cloud Build
echo -e "${YELLOW}🔨 Construindo imagem com Cloud Build...${NC}"
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION="$REGION",_REPOSITORY="$REPOSITORY",_IMAGE="$IMAGE_NAME",_TAG="$IMAGE_TAG" \
  --project="$PROJECT_ID"

# Deploy no Cloud Run
echo -e "${YELLOW}🚢 Fazendo deploy no Cloud Run...${NC}"
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE_URL" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory="$MEMORY" \
  --cpu="$CPU" \
  --max-instances="$MAX_INSTANCES" \
  --min-instances="$MIN_INSTANCES" \
  --timeout="$TIMEOUT" \
  --port=8080 \
  --project="$PROJECT_ID"

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format='value(status.url)')

echo ""
echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo "────────────────────────────────────────"
echo -e "🌐 URL do serviço: ${GREEN}$SERVICE_URL${NC}"
echo ""
echo "📚 Endpoints disponíveis:"
echo "  • Health Check: $SERVICE_URL/health"
echo "  • Predict: $SERVICE_URL/predict"
echo "  • Docs (Swagger): $SERVICE_URL/docs"
echo "  • ReDoc: $SERVICE_URL/redoc"
echo ""
echo "🧪 Testar health check:"
echo "  curl $SERVICE_URL/health"
echo ""
echo "🧪 Testar predição:"
echo '  curl -X POST '$SERVICE_URL'/predict \\'
echo '    -H "Content-Type: application/json" \\'
echo '    -d '"'"'{"INDE": 5.2, "IAA": 6.1, "IAN": 5.8, "IDA": 6.5, "IEG": 7.2, "IPP": 5.9, "IPS": 6.3, "IPV": 5.7, "PEDRA": "Ametista", "PONTO_VIRADA": 0, "FASE": 3, "ANO_REFERENCIA": 2021}'"'"
echo ""
echo "────────────────────────────────────────"
