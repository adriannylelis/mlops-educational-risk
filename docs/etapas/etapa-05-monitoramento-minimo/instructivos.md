# Etapa 05 — Monitoramento mínimo auditável

## Objetivo da etapa
Implementar monitoramento contínuo mínimo exigido no edital com evidência auditável.

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
```

## Artefatos gerados
- Relatório de drift por feature
- Evidência de monitoramento contínuo mínimo

## Critério de pronto
- PASSA se relatório de drift for gerado com dados válidos.

## Riscos e decisões
- Fora de escopo: plataforma completa de observabilidade.
- Decisão: monitoramento essencial para conformidade com o datathon.

## Aprovação explícita
- Status: `PENDENTE`
- Registro esperado: `APROVADO ETAPA 05`
