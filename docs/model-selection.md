# Seleção de Modelo — Etapa 03

## Objetivo
Selecionar 1 modelo de produção entre até 2 candidatos, usando critério objetivo alinhado ao risco.

## Candidatos treinados
- `logistic_regression`
- `random_forest`

## Critério de seleção
- Métrica principal: `Recall` da classe de risco
- Desempate: `F1`
- Métrica de apoio: `PR-AUC`

## Implementação
- Treino e comparação em: `src/model/train.py`
- Artefato de decisão: `artifacts/metrics.json`
- Modelo selecionado salvo em: `artifacts/model.joblib`

## Comando de execução
```bash
docker compose run --rm train
```

## Regra anti-overengineering
- Restrição a dois candidatos no MVP.
- Sem tuning extensivo nesta etapa.
- Seleção direta por métrica definida previamente.
