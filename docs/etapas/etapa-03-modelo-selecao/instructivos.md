# Etapa 03 — Modelo candidato e seleção objetiva

## Objetivo da etapa
Treinar até 2 candidatos e selecionar 1 modelo final por critério objetivo alinhado ao risco.

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
```

## Artefatos gerados
- `artifacts/model.joblib`
- `artifacts/metrics.json`

## Critério de pronto
- PASSA se existir 1 modelo serializado e decisão de seleção documentada por métrica.

## Riscos e decisões
- Fora de escopo: tuning extensivo e busca de hiperparâmetros avançada.
- Decisão: manter comparação enxuta para cumprir prazo e auditabilidade.

## Aprovação explícita
- Status: `PENDENTE`
- Registro esperado: `APROVADO ETAPA 03`
