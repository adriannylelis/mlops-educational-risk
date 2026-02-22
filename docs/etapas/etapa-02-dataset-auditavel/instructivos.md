# Etapa 02 — Dataset de treino auditável e sem vazamento

## Objetivo da etapa
Documentar e consolidar target, recorte temporal e regras anti-leakage para treino reproduzível.

## Estado de execução
- Status técnico: concluído
- Documento de decisão criado: `docs/modeling-decisions.md`
- Regra implementada no código: `src/data/build_training_dataset.py`
- Reprodução validada via container: `docker compose run --rm train`

## Subetapas
1. Definir target e janela temporal.
   - O que será feito: registrar regra do alvo e data de corte de predição.
   - Onde no código: `docs/modeling-decisions.md`.
   - Artefato esperado: definição clara e auditável do problema supervisionado.
2. Definir colunas proibidas por leakage.
   - O que será feito: listar features vetadas e justificativa objetiva.
   - Onde no código: `docs/modeling-decisions.md`, `src/data`, `src/features`.
   - Artefato esperado: lista de exclusões no pipeline.
3. Validar reprodução da formação do dataset.
   - O que será feito: rodar pipeline de treino em container após decisões.
   - Onde no código: `src/model/train.py`.
   - Artefato esperado: geração consistente de dados de treino.

## Comandos executados
```bash
docker compose run --rm train
docker compose run --rm tests
```

## Artefatos gerados
- `docs/modeling-decisions.md`
- `artifacts/training_dataset.csv`
- `artifacts/training_dataset_metadata.json`
- Evidência de execução reproduzível da formação do dataset em container

## Resultado da validação binária
- PASSA: target e janela temporal documentados
- PASSA: regras anti-leakage implementadas
- PASSA: formação do dataset reproduzível por comando Docker
- PASSA: testes em container aprovados

## Critério de pronto
- PASSA se target, janela temporal e regras anti-leakage estiverem documentados e reproduzíveis.

## Riscos e decisões
- Fora de escopo: expansão de schema além do necessário para o MVP.
- Decisão: priorizar rastreabilidade da regra de dados sobre complexidade analítica.
- Regra temporal adotada: prever `DEFASAGEM_2021` com variáveis disponíveis até 2020.

## Aprovação explícita
- Status: `CONCLUÍDA`
- Registro recebido para execução: `avance para etapa 2`
