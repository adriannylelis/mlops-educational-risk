# Etapa 03 — Modelo candidato e seleção objetiva

## Objetivo da etapa
Treinar até 2 candidatos e selecionar 1 modelo final por critério objetivo alinhado ao risco.

## Estado de execução
- Status técnico: concluído
- Candidatos treinados: `logistic_regression` e `random_forest`
- Seleção realizada por `Recall` com desempate por `F1`
- Modelo selecionado: `logistic_regression`
- Documento de decisão: `docs/model-selection.md`

## Subetapas
1. Treinar candidatos no mesmo pipeline.
   - O que será feito: executar treino de até 2 algoritmos em condições comparáveis.
   - Onde no código: `src/model/train.py`.
   - Artefato esperado: métricas por candidato.
2. Comparar por métrica principal.
   - O que será feito: priorizar `Recall` da classe de risco e registrar métricas de apoio.
   - Onde no código: `artifacts/metrics.json`.
   - Artefato esperado: ranking objetivo de modelos.
3. Selecionar e serializar modelo final.
   - O que será feito: persistir modelo vencedor para inferência.
   - Onde no código: `artifacts/model.joblib`.
   - Artefato esperado: modelo pronto para API.

## Comandos executados
```bash
docker compose run --rm train
docker compose run --rm tests
```

## Artefatos gerados
- `artifacts/model.joblib`
- `artifacts/metrics.json`

## Resultado da validação binária
- PASSA: existem métricas por candidato em `artifacts/metrics.json`
- PASSA: métrica principal `Recall` registrada e aplicada na seleção
- PASSA: métricas de apoio (`PR-AUC`, `F1`) registradas
- PASSA: modelo final serializado em `artifacts/model.joblib`

## Critério de pronto
- PASSA se existir 1 modelo serializado e decisão de seleção documentada por métrica.

## Riscos e decisões
- Fora de escopo: tuning extensivo e busca de hiperparâmetros avançada.
- Decisão: manter comparação enxuta para cumprir prazo e auditabilidade.
- Risco conhecido: possível variação de modelo vencedor com novas amostras de treino.

## Aprovação explícita
- Status: `CONCLUÍDA`
- Registro esperado: `APROVADO ETAPA 03`
