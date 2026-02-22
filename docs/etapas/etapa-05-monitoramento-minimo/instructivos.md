# Etapa 05 — Monitoramento mínimo auditável

## Objetivo da etapa
Implementar monitoramento contínuo mínimo exigido no edital com evidência auditável.

## Estado de execução
- Status técnico: concluído
- Logging estruturado implementado na API em `app/main.py`
- Relatório de drift gerado por lote em `artifacts/drift_report.json`
- Dashboard mínimo publicado em `monitoring/dashboard.html`
- Serviços adicionados no compose: `monitor` e `dashboard`

## Subetapas
1. Estruturar logging da API.
   - O que será feito: registrar latência, status, erros e score de inferência.
   - Onde no código: `app/`.
   - Artefato esperado: logs estruturados de execução.
2. Gerar relatório de drift por lote.
   - O que será feito: calcular drift por feature e gerar relatório.
   - Onde no código: `monitoring/drift_report.py`.
   - Artefato esperado: relatório de drift persistido.
3. Expor visualização mínima do relatório.
   - O que será feito: publicar dashboard simples ou saída consumível.
   - Onde no código: serviço `dashboard` no compose.
   - Artefato esperado: evidência visual do monitoramento.

## Comandos executados
```bash
docker compose run --rm monitor
docker compose up -d dashboard
curl -s http://localhost:8501/monitoring/dashboard.html
docker compose up -d api
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"features":{}}'
docker compose logs api --tail 20
docker compose run --rm tests
docker compose down
```

## Artefatos gerados
- Relatório de drift por feature
- Evidência de monitoramento contínuo mínimo

## Evidências coletadas
- Relatório encontrado: `artifacts/drift_report.json`
- Status global do drift: `drift`
- Features analisadas: `18`
- Features com drift: `1`
- Dashboard acessível em: `http://localhost:8501/monitoring/dashboard.html`
- Log estruturado de inferência observado:
   - `{"event": "prediction", "score_risco": 0.5990625103596919, "classe_risco": "alto"}`
   - `{"event": "request", "path": "/predict", "method": "POST", "status_code": 200, "latency_ms": 350.63, "score_risco": 0.5990625103596919, "error": null}`
- Testes: `4 passed`
- Cobertura: `93.08%`

## Resultado da validação binária
- PASSA: logging estruturado com latência, status, score e erro
- PASSA: relatório de drift por lote gerado com dados válidos
- PASSA: visualização mínima do relatório disponível via dashboard

## Critério de pronto
- PASSA se relatório de drift for gerado com dados válidos.

## Riscos e decisões
- Fora de escopo: plataforma completa de observabilidade.
- Decisão: monitoramento essencial para conformidade com o datathon.

## Aprovação explícita
- Status: `CONCLUÍDA - AGUARDANDO APROVAÇÃO`
- Registro esperado: `APROVADO ETAPA 05`
