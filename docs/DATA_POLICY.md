# Hermes v0.4-alpha — Data Policy

## Dados permitidos

- Dados mockados.
- Dados sanitizados.
- Nomes simbólicos de empresas/frentes virtuais autorizadas.
- Estados visuais de agentes.
- Tarefas simuladas.
- Alertas fictícios ou genéricos.
- Decisões internas sem efeito externo.

## Dados proibidos

- Dados reais de clientes.
- Dados reais de sinistros.
- Credenciais, tokens, chaves e certificados.
- Contratos reais.
- Dados financeiros reais.
- Dados pessoais.
- Documentos S3/S4.
- Genoma Digital bruto.
- Conteúdo sensível de PI.

## Classificação S0-S4

- **S0:** público, mockado ou demonstrativo.
- **S1:** interno leve, sem sensibilidade crítica.
- **S2:** estratégico controlado, apenas metadados/resumos sanitizados.
- **S3:** sensível/confidencial; não renderizar conteúdo bruto.
- **S4:** quarentena crítica; apenas entidade visual, sem conteúdo.

## Regras permanentes

- Nenhum documento S3/S4 aparece na interface.
- Nenhum Genoma Digital bruto entra no app.
- Nenhuma ação externa é executada.
- Nenhuma empresa virtual é pessoa jurídica.
- O Ciclo Hermes é diagnóstico local e simulado.
