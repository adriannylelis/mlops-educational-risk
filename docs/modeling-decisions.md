# Decisões de Modelagem — Etapa 02

## Objetivo
Formalizar a regra de formação do dataset de treino para predição de risco de defasagem escolar sem vazamento de informação.

## Definição de target
- Coluna bruta de referência: `DEFASAGEM_2021`
- Coluna de modelagem: `target_risco_defasagem`
- Regra: `target_risco_defasagem = 1` quando `DEFASAGEM_2021 < 0`, caso contrário `0`
- Linhas consideradas: somente registros com `DEFASAGEM_2021` numérica não nula

## Recorte temporal
- Janela de predição: prever risco em 2021 com informações disponíveis até 2020
- Features permitidas no MVP: colunas com sufixo `_2020`

## Colunas proibidas por leakage
1. Todas as colunas de 2021 e 2022
   - Regra: excluir qualquer coluna com sufixo `_2021` e `_2022`
   - Motivo: representam informação de período igual ou posterior ao alvo
2. Identificador nominal
   - Coluna: `NOME`
   - Motivo: não generalizável e não representa sinal causal de risco
3. Target bruta em features
   - Coluna: `DEFASAGEM_2021`
   - Motivo: usada apenas para construção do alvo binário

## Implementação reprodutível
- Script de formação do dataset: `src/data/build_training_dataset.py`
- Entrada: `base_dados/PEDE_PASSOS_DATASET_FIAP.csv`
- Saídas:
  - `artifacts/training_dataset.csv`
  - `artifacts/training_dataset_metadata.json`

## Comando de execução
```bash
docker compose run --rm train
```

## Decisão anti-overengineering
- Não aplicar, nesta etapa, seleção avançada de features, tuning extensivo ou múltiplas janelas temporais.
- Foco em regra auditável, simples e reproduzível para habilitar as próximas etapas.
