# Etapa 02 — Dataset de treino auditável e sem vazamento

## Objetivo da etapa
Documentar e consolidar target, recorte temporal e regras anti-leakage para treino reproduzível.

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
```

## Artefatos gerados
- `docs/modeling-decisions.md`
- Evidência de execução reproduzível da formação do dataset

## Critério de pronto
- PASSA se target, janela temporal e regras anti-leakage estiverem documentados e reproduzíveis.

## Riscos e decisões
- Fora de escopo: expansão de schema além do necessário para o MVP.
- Decisão: priorizar rastreabilidade da regra de dados sobre complexidade analítica.

## Aprovação explícita
- Status: `PENDENTE`
- Registro esperado: `APROVADO ETAPA 02`
