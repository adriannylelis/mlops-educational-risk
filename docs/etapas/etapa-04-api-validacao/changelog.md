## Etapa 04 – API de inferência pronta para validação

### Adicionado
- Endpoint `POST /predict` com schema de entrada e resposta tipada.
- Testes de API em `tests/test_api.py` cobrindo `/health` e `/predict`.
- Serviço `api` no `docker-compose.yml` com execução via Uvicorn.

### Alterado
- `app/main.py` evoluído para carregar modelo, validar payload e retornar score/classe.
- `docker-compose.yml` com comando de testes incluindo cobertura mínima (`--cov-fail-under=80`).

### Removido
- N/A.

### Decisões Técnicas
- Escopo restrito a `/health` e `/predict`.
- Contrato mínimo de inferência mantido com `features` genérico para evitar overengineering de schema.

### Impacto
- API validada localmente via container e pronta para integração nas próximas etapas.
- Cobertura de testes consolidada acima do mínimo exigido.

### Riscos Conhecidos
- Payload genérico pode exigir endurecimento de schema em produção dependendo da governança de dados.
