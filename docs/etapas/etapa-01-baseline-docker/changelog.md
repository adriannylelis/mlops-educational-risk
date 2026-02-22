## Etapa 01 – Baseline reprodutível em Docker

### Adicionado
- Estrutura mínima do projeto: `src/`, `app/`, `tests/`, `monitoring/`, `artifacts/`.
- Base Docker-first: `Dockerfile`, `docker-compose.yml`, `requirements.txt`.
- Pipeline de treino mínimo em `src/model/train.py` gerando `model.joblib` e `metrics.json`.
- Teste mínimo de geração de artefatos em `tests/test_train_artifacts.py`.

### Alterado
- `docker-compose.yml` com `PYTHONPATH=/workspace` para serviços `train` e `tests`.
- `instructivos.md` da etapa para status de execução concluída com checklist PASSA.

### Removido
- N/A.

### Decisões Técnicas
- Operação 100% via containers para garantir reprodutibilidade.
- Escopo intencionalmente mínimo para viabilizar baseline sem overengineering.

### Impacto
- Etapa 01 passa a ser executável e verificável por comandos reais.
- Artefatos base de modelo e métricas agora são produzidos por container.

### Riscos Conhecidos
- Dependência de Docker disponível no ambiente para execução local.
