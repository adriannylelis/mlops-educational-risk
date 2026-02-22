# Etapa 07 — Evidências finais para submissão

## Objetivo da etapa
Consolidar evidências técnicas e documentação final para entrega auditável do datathon.

## Subetapas
1. Atualizar documentação principal.
   - O que será feito: consolidar README com execução Docker, API, testes e deploy GCP.
   - Onde no código: `README.md`, `docs/`.
   - Artefato esperado: documentação única de execução e operação.
2. Consolidar evidências de qualidade e operação.
   - O que será feito: anexar métricas, cobertura de testes, monitoramento e URL da API.
   - Onde no código: `artifacts/`, `docs/`.
   - Artefato esperado: pacote de evidências verificável.
3. Preparar roteiro executivo da apresentação.
   - O que será feito: estruturar narrativa de até 5 minutos com foco em resultado.
   - Onde no código: `docs/`.
   - Artefato esperado: roteiro final de apresentação.

## Comandos executados
```bash
docker compose run --rm tests
docker compose run --rm monitor
```

## Artefatos gerados
- README final atualizado
- Evidências de métricas/cobertura/monitoramento
- Roteiro de apresentação

## Critério de pronto
- PASSA se todos os requisitos do edital estiverem mapeados para evidências verificáveis.

## Riscos e decisões
- Fora de escopo: material adicional não exigido para banca.
- Decisão: evidências objetivas e sucintas para maximizar clareza.

## Aprovação explícita
- Status: `PENDENTE`
- Registro esperado: `APROVADO ETAPA 07`
