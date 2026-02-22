## Etapa 02 – Dataset de treino auditável e sem vazamento

### Adicionado
- Documento de decisão de modelagem em `docs/modeling-decisions.md`.
- Construtor reproduzível de dataset em `src/data/build_training_dataset.py`.
- Novos artefatos de dados: `artifacts/training_dataset.csv` e `artifacts/training_dataset_metadata.json`.

### Alterado
- `src/model/train.py` passou a treinar com dataset real gerado por regra temporal e anti-leakage.
- `tests/test_train_artifacts.py` ampliado para validar artefatos de dataset da etapa 02.

### Removido
- N/A.

### Decisões Técnicas
- Formalização do dataset antes de otimização de modelo.
- Target binário definido como `DEFASAGEM_2021 < 0`.
- Features limitadas a colunas `_2020` para prevenção de leakage temporal.

### Impacto
- Pipeline passa a ter regra de formação auditável e reproduzível em container.
- Reduz risco de vazamento por uso de variáveis de 2021/2022.

### Riscos Conhecidos
- Interpretação de risco pela regra `DEFASAGEM_2021 < 0` pode exigir confirmação final de negócio.
