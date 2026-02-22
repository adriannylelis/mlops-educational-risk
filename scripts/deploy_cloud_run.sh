#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-mlops-risk}"
IMAGE_NAME="${IMAGE_NAME:-risk-api}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
SERVICE_NAME="${SERVICE_NAME:-risk-api}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "Defina PROJECT_ID antes de executar."
  echo "Exemplo: PROJECT_ID=meu-projeto ./scripts/deploy_cloud_run.sh"
  exit 1
fi

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project "${PROJECT_ID}"

gcloud artifacts repositories create "${REPOSITORY}" \
  --repository-format=docker \
  --location "${REGION}" \
  --project "${PROJECT_ID}" \
  || true

gcloud builds submit \
  --config cloudbuild.yaml \
  --project "${PROJECT_ID}" \
  --substitutions _REGION="${REGION}",_REPOSITORY="${REPOSITORY}",_IMAGE="${IMAGE_NAME}",_TAG="${IMAGE_TAG}"

gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_URI}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --project "${PROJECT_ID}"

echo "Deploy concluído: ${SERVICE_NAME}"
