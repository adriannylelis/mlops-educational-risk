## Etapa 03 – Modelo candidato e seleção objetiva

### Adicionado
- Comparação de dois candidatos no pipeline (`logistic_regression` e `random_forest`).
- Registro de seleção de modelo em `docs/model-selection.md`.
- Estrutura de métricas por candidato em `artifacts/metrics.json` com `Recall`, `F1` e `PR-AUC`.

### Alterado
- `src/model/train.py` para seleção automática do modelo por `Recall` com desempate por `F1`.
- `tests/test_train_artifacts.py` para validar novo schema de métricas e seleção.

### Removido
- N/A.

### Decisões Técnicas
- Critério principal: `Recall` da classe de risco.
- Desempate por `F1` para estabilidade da escolha.
- Escopo limitado a 2 algoritmos no MVP.

### Impacto
- Torna a escolha do modelo auditável e reproduzível.
- Mantém coerência com requisito de seleção objetiva do datathon.

### Riscos Conhecidos
- Queda de precisão geral ao priorizar recall.
- Mudança do modelo vencedor com evolução da distribuição dos dados.
