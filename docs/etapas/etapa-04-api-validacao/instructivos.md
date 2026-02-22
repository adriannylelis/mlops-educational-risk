# Etapa 04 — API de inferência pronta para validação

## Objetivo da etapa
Disponibilizar inferência com contratos mínimos e evidência de funcionamento por teste.

## Estado de execução
- Status técnico: concluído
- Endpoints implementados: `GET /health` e `POST /predict`
- Schema de entrada: `{"features": {...}}`
- Contrato de saída: `{"score_risco": <float>, "classe_risco": "alto|baixo"}`
- Cobertura validada: 94.39%

## Subetapas
1. Publicar endpoints mínimos.
   - O que será feito: disponibilizar `GET /health` e `POST /predict`.
   - Onde no código: `app/`.
   - Artefato esperado: API funcional em container.
2. Validar contrato de entrada e saída.
   - O que será feito: validar payload e retorno com schema.
   - Onde no código: `app/`.
   - Artefato esperado: contrato estável de inferência.
3. Executar testes de API e cobertura.
   - O que será feito: testar endpoint e regressão mínima.
   - Onde no código: `tests/`.
   - Artefato esperado: cobertura >= 80%.

## Comandos executados
```bash
docker compose run --rm train
docker compose up -d api
docker compose run --rm tests
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"features": {}}'
docker compose down
```

## Artefatos gerados
- Evidência de respostas de `/health` e `/predict`
- Relatório de testes com cobertura

## Evidências coletadas
- `GET /health` retornou `{"status":"ok"}`
- `POST /predict` retornou `{"score_risco":0.5990625103596919,"classe_risco":"alto"}`
- Testes: `3 passed`
- Cobertura: `TOTAL 94.39%` (limite mínimo exigido: 80%)

## Resultado da validação binária
- PASSA: API responde localmente em container
- PASSA: schema e contrato de resposta validados
- PASSA: cobertura mínima atingida e superada

## Critério de pronto
- PASSA se API responder localmente e cobertura mínima for atingida.

## Riscos e decisões
- Fora de escopo: novos endpoints além do escopo do edital.
- Decisão: manter interface mínima e estável.

## Aprovação explícita
- Status: `CONCLUÍDA - AGUARDANDO APROVAÇÃO`
- Registro esperado: `APROVADO ETAPA 04`
