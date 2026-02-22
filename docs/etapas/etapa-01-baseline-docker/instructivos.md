# Etapa 01 — Baseline reprodutível em Docker

## Objetivo da etapa
Estabelecer execução reprodutível do pipeline MVP via Docker, sem dependências locais de Python.

## Estado atual do repositório (levantamento)
- Data de referência: 2026-02-21
- Estrutura encontrada: `base_dados/`, `docs/`, `.github/`, `src/`, `app/`, `tests/`, `monitoring/`, `artifacts/`
- Arquivos de base encontrados: `Dockerfile`, `docker-compose.yml`, `requirements.txt`
- Conclusão: baseline Docker-first implantado e validado em execução real.

## Subetapas
1. Validar estrutura mínima de módulos.
   - O que será feito: conferir organização em `src`, `app`, `tests`, `monitoring`, `artifacts`, `docs`.
   - Onde no código: raiz do repositório e diretórios de código.
   - Artefato esperado: estrutura consistente para execução Docker-first.
2. Validar build dos serviços.
   - O que será feito: buildar imagens dos serviços definidos em compose.
   - Onde no código: `Dockerfile` e `docker-compose.yml`.
   - Artefato esperado: imagens buildadas com sucesso.
3. Validar execução do treino e testes em container.
   - O que será feito: executar fluxo base de treino e testes.
   - Onde no código: serviços `train` e `tests` do compose.
   - Artefato esperado: artefatos de modelo/métricas e relatório de testes.

## Checklist de execução (binário)
- [x] S1 PASSA: estrutura `src/app/tests/monitoring/artifacts/docs` presente
- [x] S2 PASSA: `docker compose build` executa sem erro
- [x] S3 PASSA: `docker compose run --rm train` executa sem erro
- [x] S4 PASSA: `docker compose run --rm tests` executa sem erro
- [x] Etapa 01 PASSA: S1+S2+S3+S4 verdadeiros

## Comandos executados
- `docker compose build`
- `docker compose run --rm train`
- `docker compose run --rm tests`

## Comandos executados após aprovação
```bash
docker compose build
docker compose run --rm train
docker compose run --rm tests
```

## Artefatos gerados
- `artifacts/model.joblib`
- `artifacts/metrics.json`
- Logs de execução de build/treino/testes em container

## Critério de pronto
- PASSA se build, treino e testes executarem em container sem erro.

## Riscos e decisões
- Fora de escopo: qualquer setup local de ambiente Python.
- Decisão: manter stack mínima em Docker para reduzir variabilidade de execução.
- Ajuste aplicado: inclusão de `PYTHONPATH=/workspace` nos serviços `train` e `tests` para importação de `src` em container.

## Aprovação explícita
- Status: `CONCLUÍDA`
- Registro recebido: `APROVADO ETAPA 01`
