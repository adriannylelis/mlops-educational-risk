# Decisões de Modelagem

## Objetivo
Formalizar a regra de formação do dataset de treino para predição de risco de defasagem escolar sem vazamento de informação.

## Estratégia: Dataset Longitudinal (Panel)

O modelo é **ano-agnóstico**: usa features do ano N para prever defasagem no ano N+1,
independente do ano de referência. O dataset é formado empilhando dois períodos:

| Período | Features | Target | Linhas |
|---------|----------|--------|--------|
| 2020 → 2021 | Índices e avaliações de 2020 | `DEFASAGEM_2021 < 0` | 686 |
| 2021 → 2022 | Índices e avaliações de 2021 | `DEFASAGEM_2022 < 0` (computada) | 862 |
| **Total** | | | **1.548** |

**Motivo**: Aproximadamente dobra o volume de dados, generaliza para novos anos e melhora
o desempenho sem necessidade de novos dados externos.

## Definição de target

- **Regra**: `target_risco_defasagem = 1` quando defasagem do ano seguinte < 0
- **Cálculo direto** (2020→2021): `DEFASAGEM_2021 < 0` (coluna fornecida no dataset)
- **Cálculo derivado** (2021→2022): `(FASE_2022 - número_extraído(NIVEL_IDEAL_2022)) < 0`
  - Hipótese validada contra `DEFASAGEM_2021`: 92% de correspondência
- **Linhas consideradas**: somente registros com target calculável (não nulo)

## Features utilizadas

Features comuns aos anos 2020 e 2021, renomeadas sem sufixo de ano:

| Feature | Tipo | Tratamento |
|---------|------|-----------|
| `INDE`, `IAA`, `IAN`, `IDA`, `IEG`, `IPP`, `IPS`, `IPV` | Numérica | Imputation mediana + StandardScaler |
| `PEDRA` | Categórica | Imputation moda + OneHotEncoder |
| `PONTO_VIRADA` | Booleana → int (1/0/-1) | Imputation mediana + StandardScaler |
| `FASE` | Numérica | Imputation mediana + StandardScaler |
| `ANO_REFERENCIA` | Numérica (2020/2021) | Imputation mediana + StandardScaler |

**`ANO_REFERENCIA`** permite ao modelo aprender padrões distintos por período sem criar features separadas.

## Colunas proibidas por leakage

- Todas as colunas do ano-alvo e anos posteriores (ex: features de 2021 quando target é 2021)
- `NOME` — identificador nominal, sem poder preditivo generalizável

## Implementação reprodutível

- Script de formação do dataset: `src/data/build_training_dataset.py`
- Entrada: `base_dados/PEDE_PASSOS_DATASET_FIAP.csv`
- Saídas:
  - `src/artifacts/training_dataset.csv`
  - `src/artifacts/training_dataset_metadata.json`

## Comando de execução

```bash
docker compose run --rm train
```

## Decisão anti-overengineering

- Features limitadas às disponíveis nos dois anos de referência (10 índices + FASE + ANO).
- Sem join com tabelas externas (TbAluno, TbTurma) nesta etapa.
- Seleção de modelo e hiperparâmetros mantidos simples (sem Optuna/GridSearch).
