#!/bin/bash
# Setup GitHub Actions Service Account para deploy no GCP
# Uso: PROJECT_ID=meu-projeto ./scripts/setup_github_actions.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validação de variáveis
if [ -z "$PROJECT_ID" ]; then
  echo -e "${RED}❌ Erro: PROJECT_ID não definido${NC}"
  echo "Uso: PROJECT_ID=meu-projeto $0"
  exit 1
fi

SA_NAME="${SA_NAME:-github-actions-deploy}"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="github-sa-key.json"

echo -e "${BLUE}🔐 Configurando GitHub Actions para GCP${NC}"
echo "────────────────────────────────────────"
echo "Projeto: $PROJECT_ID"
echo "Service Account: $SA_EMAIL"
echo "────────────────────────────────────────"
echo ""

# Configurar projeto
echo -e "${YELLOW}📋 Configurando projeto GCP...${NC}"
gcloud config set project "$PROJECT_ID"

# Habilitar APIs necessárias
echo -e "${YELLOW}🔌 Habilitando APIs necessárias...${NC}"
gcloud services enable \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  --project="$PROJECT_ID"

# Criar service account
echo -e "${YELLOW}👤 Criando service account...${NC}"
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
  echo -e "${GREEN}✅ Service account já existe${NC}"
else
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name="GitHub Actions Deploy" \
    --description="Service account for GitHub Actions CI/CD" \
    --project="$PROJECT_ID"
  echo -e "${GREEN}✅ Service account criado${NC}"
fi

# Conceder permissões
echo -e "${YELLOW}🔑 Concedendo permissões...${NC}"

ROLES=(
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
  "roles/artifactregistry.admin"
  "roles/cloudbuild.builds.editor"
  "roles/storage.admin"
  "roles/serviceusage.serviceUsageAdmin"
)

for ROLE in "${ROLES[@]}"; do
  echo "  → Aplicando $ROLE"
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$ROLE" \
    --condition=None \
    --project="$PROJECT_ID" \
    --quiet > /dev/null
done

echo -e "${GREEN}✅ Permissões aplicadas${NC}"

# Gerar chave JSON
echo -e "${YELLOW}🔐 Gerando chave JSON...${NC}"

# Verificar se já existe chave
EXISTING_KEYS=$(gcloud iam service-accounts keys list \
  --iam-account="$SA_EMAIL" \
  --filter="keyType=USER_MANAGED" \
  --format="value(name)" \
  --project="$PROJECT_ID")

if [ -n "$EXISTING_KEYS" ]; then
  echo -e "${YELLOW}⚠️  Chaves USER_MANAGED existentes encontradas:${NC}"
  echo "$EXISTING_KEYS"
  echo ""
  read -p "Deseja criar uma nova chave? (digite 'sim' para confirmar): " CONFIRM
  if [ "$CONFIRM" != "sim" ]; then
    echo -e "${RED}❌ Operação cancelada${NC}"
    exit 1
  fi
fi

# Criar nova chave
gcloud iam service-accounts keys create "$KEY_FILE" \
  --iam-account="$SA_EMAIL" \
  --project="$PROJECT_ID"

echo -e "${GREEN}✅ Chave criada: $KEY_FILE${NC}"
echo ""

# Exibir instruções
echo -e "${BLUE}📋 Próximos Passos:${NC}"
echo "────────────────────────────────────────"
echo ""
echo "1. Acesse: https://github.com/SEU_USUARIO/SEU_REPO/settings/secrets/actions"
echo ""
echo "2. Adicione os seguintes secrets:"
echo ""
echo -e "${YELLOW}Secret: GCP_PROJECT_ID${NC}"
echo "Valor:"
echo -e "${GREEN}$PROJECT_ID${NC}"
echo ""
echo -e "${YELLOW}Secret: GCP_SA_KEY${NC}"
echo "Valor (copie o conteúdo abaixo):"
echo -e "${GREEN}────────── INÍCIO DO JSON ──────────${NC}"
cat "$KEY_FILE"
echo -e "${GREEN}────────── FIM DO JSON ──────────${NC}"
echo ""
echo ""
echo -e "${RED}⚠️  IMPORTANTE:${NC}"
echo "  1. Copie o conteúdo JSON COMPLETO (incluindo { e })"
echo "  2. Cole no GitHub Secret 'GCP_SA_KEY'"
echo "  3. DELETE o arquivo local após copiar:"
echo -e "     ${YELLOW}rm $KEY_FILE${NC}"
echo ""
echo -e "${YELLOW}Exemplo de comando para copiar para clipboard (MacOS):${NC}"
echo "  cat $KEY_FILE | pbcopy"
echo ""
echo -e "${YELLOW}Exemplo para copiar para clipboard (Linux):${NC}"
echo "  cat $KEY_FILE | xclip -selection clipboard"
echo ""

# Verificar configuração
echo -e "${BLUE}🔍 Verificação da Configuração:${NC}"
echo "────────────────────────────────────────"
echo ""
echo "Service Account: $SA_EMAIL"
echo ""
echo "Roles aplicadas:"
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:serviceAccount:${SA_EMAIL}" \
  --project="$PROJECT_ID"
echo ""

echo -e "${GREEN}✅ Configuração concluída!${NC}"
echo ""
echo -e "${YELLOW}⚠️  NÃO SE ESQUEÇA:${NC}"
echo "  1. Adicionar secrets no GitHub"
echo "  2. Deletar arquivo: rm $KEY_FILE"
echo ""
echo "Documentação completa: docs/github-actions-setup.md"
echo "────────────────────────────────────────"
