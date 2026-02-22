# Etapa 06 — Build e deploy em GCP

## Objetivo da etapa
Publicar API de inferência em Cloud Run com build na GCP e imagem versionada.

## Subetapas
1. Habilitar serviços de plataforma.
   - O que será feito: habilitar Cloud Run, Cloud Build e Artifact Registry.
   - Onde no código/infra: projeto GCP.
   - Artefato esperado: serviços ativos para CI/CD mínimo.
2. Criar repositório de imagens e buildar.
   - O que será feito: criar repositório Docker e enviar imagem com Cloud Build.
   - Onde no código/infra: Artifact Registry.
   - Artefato esperado: imagem publicada e versionada.
3. Realizar deploy e validar endpoint.
   - O que será feito: publicar serviço no Cloud Run e validar `/health` e `/predict`.
   - Onde no código/infra: Cloud Run.
   - Artefato esperado: URL ativa da API.

## Comandos executados
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

gcloud artifacts repositories create mlops-risk \
  --repository-format=docker \
  --location=us-central1

gcloud builds submit \
  --tag us-central1-docker.pkg.dev/$PROJECT_ID/mlops-risk/risk-api:latest

gcloud run deploy risk-api \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/mlops-risk/risk-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

## Artefatos gerados
- Imagem em Artifact Registry
- URL do Cloud Run com serviço ativo

## Critério de pronto
- PASSA se `/health` e `/predict` responderem na URL do Cloud Run.

## Riscos e decisões
- Fora de escopo: múltiplos ambientes com promoção automatizada.
- Decisão: manter deploy único e auditável para submissão.

## Aprovação explícita
- Status: `PENDENTE`
- Registro esperado: `APROVADO ETAPA 06`
