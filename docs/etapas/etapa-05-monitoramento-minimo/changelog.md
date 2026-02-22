## Etapa 05 – Monitoramento mínimo auditável

### Adicionado
- Logging estruturado na API com campos de latência, status, score e erro.
- Geração de relatório de drift PSI em `monitoring/drift_report.py`.
- Dashboard mínimo em `monitoring/dashboard.html`.
- Serviço `monitor` e `dashboard` no `docker-compose.yml`.
- Teste de monitoramento em `tests/test_monitoring.py`.

### Alterado
- `app/main.py` para emitir logs estruturados de requisição e predição.

### Removido
- N/A.

### Decisões Técnicas
- Monitoramento por lote para reduzir complexidade operacional.
- Uso de PSI por feature com thresholds simples (`stable`, `warning`, `drift`).
- Dashboard estático servindo JSON de artefatos para manter escopo MVP.

### Impacto
- Entrega evidência auditável mínima de monitoramento contínuo.
- Mantém conformidade com requisito do datathon sem overengineering.

### Riscos Conhecidos
- Sensibilidade do drift depende da qualidade das amostras monitoradas.
- Thresholds de PSI podem requerer calibração com dados de produção reais.
