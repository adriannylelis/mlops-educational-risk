## Etapa 06 – Build e deploy em GCP

### Adicionado
- Template com fluxo de build e deploy via Cloud Build/Artifact Registry/Cloud Run.

### Alterado
- N/A.

### Removido
- N/A.

### Decisões Técnicas
- Build executado na GCP para aderência ao modelo Docker-first.

### Impacto
- Habilita endpoint de produção para avaliação final.

### Riscos Conhecidos
- Erros de permissão IAM podem bloquear deploy.
