# Hermes v0.4-alpha — Pixel Office Executável

Cockpit visual local-first para Empresas Virtuais Favini, com estilo **Pixel Office / The Sims corporativo 2D**.

## Objetivo

Abrir no navegador um escritório visual vivo com:

- mapa multiempresa;
- salas separadas;
- agentes dentro das salas;
- tarefas P0/P1;
- decisões pendentes;
- alertas críticos;
- botão **Rodar Ciclo Hermes**;
- SQLite local como estado inicial.

## Requisitos

- Python 3.11+.
- Navegador moderno.
- Nenhum Node/npm.
- Nenhum Docker.
- Nenhuma API externa.
- Nenhum banco externo.
- Nenhum serviço pago.

## Inicializar banco

Na pasta `hermes-visual/`:

```bash
python3 scripts/init_db.py
```

Isso cria:

```text
db/private/hermes_v04.sqlite
```

O script não sobrescreve banco existente sem confirmação explícita por flag:

```bash
python3 scripts/init_db.py --force
```

## Rodar servidor

```bash
python3 app/server.py
```

Servidor padrão:

```text
http://127.0.0.1:8040
```

## Abrir no navegador

Abra:

```text
http://127.0.0.1:8040/
```

## Política de dados

Este protótipo usa dados mockados/sanitizados.

Permitido:

- nomes de frentes simuladas;
- nomes dos agentes simbólicos;
- tarefas fictícias;
- alertas fictícios;
- decisões internas mockadas;
- estados visuais locais.

Proibido:

- dados reais de clientes;
- documentos S3/S4;
- Genoma Digital bruto;
- credenciais;
- contratos reais;
- dados financeiros reais;
- dados reais de sinistros;
- qualquer ação externa automática.

## O que é simulado

- Empresas Virtuais Favini.
- Conselho do Arconte.
- Ciclo Hermes.
- Riscos, tarefas, decisões e agentes.
- Movimentação visual dos agentes.

## O que é proibido

- Tratar empresa virtual como pessoa jurídica.
- Interagir com terceiros.
- Enviar dados para IA externa.
- Publicar `db/private/`.
- Usar dados sensíveis reais na interface.

## Segurança e GitHub Pro

Use GitHub Pro apenas como repositório privado/versionamento.

Nunca versionar:

- `db/private/`;
- `*.sqlite`;
- `backups/`;
- `exports/private/`;
- documentos S3/S4;
- arquivos `.env`;
- chaves ou certificados.

Antes de `git add`, confira:

```bash
git status --ignored
```
