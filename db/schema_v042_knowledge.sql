-- Hermes v0.4.2 — Extensão de schema para memória persistente dos agentes
-- Adiciona tabelas para armazenar conhecimento, learning e custos operacionais

PRAGMA foreign_keys = ON;

-- Tabela de fontes de conhecimento estudadas
CREATE TABLE IF NOT EXISTS knowledge_sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL UNIQUE,
  agent_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  institution TEXT NOT NULL,
  year INTEGER NOT NULL,
  url TEXT NOT NULL,
  access_tool TEXT NOT NULL DEFAULT 'web_extract',
  access_date TEXT NOT NULL,
  level TEXT NOT NULL CHECK(level IN ('N1', 'N2', 'N3')),
  language TEXT NOT NULL DEFAULT 'English',
  sections_read TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'parcialmente_lida' CHECK(status IN ('nao_lida', 'parcialmente_lida', 'lida_parcialmente', 'lida_completa', 'quarentena', 'descartada')),
  reliability TEXT NOT NULL DEFAULT 'media' CHECK(reliability IN ('alta', 'media-alta', 'media', 'baixa')),
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- Tabela de leituras/digestões de fontes
CREATE TABLE IF NOT EXISTS source_readings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  reading_date TEXT NOT NULL,
  sections_count INTEGER NOT NULL DEFAULT 1,
  proof_extracted TEXT NOT NULL DEFAULT '',
  limitations TEXT NOT NULL DEFAULT '',
  misinterpretation_risks TEXT NOT NULL DEFAULT '',
  internal_notes TEXT NOT NULL DEFAULT '',
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- Tabela de claims extraídos de fontes
CREATE TABLE IF NOT EXISTS extracted_claims (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  claim_id TEXT NOT NULL UNIQUE,
  claim_text TEXT NOT NULL,
  classification TEXT NOT NULL CHECK(classification IN ('afirmacao', 'fato', 'principio', 'princípio', 'recomendacao', 'risco', 'lacuna', 'cenario')),
  source_location TEXT NOT NULL DEFAULT '',
  level TEXT NOT NULL DEFAULT 'N1',
  reliability TEXT NOT NULL DEFAULT 'media',
  implication_hermes TEXT NOT NULL DEFAULT '',
  implication_agent TEXT NOT NULL DEFAULT '',
  implication_favini TEXT NOT NULL DEFAULT '',
  contestor_agent_id INTEGER,
  is_contested INTEGER NOT NULL DEFAULT 0 CHECK(is_contested IN (0, 1)),
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
  FOREIGN KEY (contestor_agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- Tabela de conceitos novos incorporados por agente
CREATE TABLE IF NOT EXISTS agent_concepts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  concept_id TEXT NOT NULL UNIQUE,
  concept_name TEXT NOT NULL,
  definition TEXT NOT NULL,
  use_in_agent TEXT NOT NULL DEFAULT '',
  risk_mitigation TEXT NOT NULL DEFAULT '',
  contestor_agent_id INTEGER,
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
  FOREIGN KEY (contestor_agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- Tabela de regras operacionais novas por agente
CREATE TABLE IF NOT EXISTS agent_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  rule_id TEXT NOT NULL UNIQUE,
  rule_name TEXT NOT NULL,
  rule_statement TEXT NOT NULL,
  apply_when TEXT NOT NULL DEFAULT '',
  skip_when TEXT NOT NULL DEFAULT '',
  enforcer_agent_id INTEGER,
  test_criteria TEXT NOT NULL DEFAULT '',
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
  FOREIGN KEY (enforcer_agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- Tabela de eventos de aprendizagem por agente
CREATE TABLE IF NOT EXISTS agent_learning_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id INTEGER NOT NULL,
  source_id INTEGER NOT NULL,
  learning_text TEXT NOT NULL,
  domain TEXT NOT NULL DEFAULT '',
  start_behavior TEXT NOT NULL DEFAULT '',
  stop_behavior TEXT NOT NULL DEFAULT '',
  error_not_repeat TEXT NOT NULL DEFAULT '',
  remaining_gap TEXT NOT NULL DEFAULT '',
  next_reading TEXT NOT NULL DEFAULT '',
  maturity_before REAL NOT NULL DEFAULT 0.0,
  maturity_after REAL NOT NULL DEFAULT 0.0,
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE
);

-- Tabela de exames/exercícios de maturidade
CREATE TABLE IF NOT EXISTS agent_exams (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id INTEGER NOT NULL,
  source_id INTEGER NOT NULL,
  exercise_scenario TEXT NOT NULL,
  contestor_agent_id INTEGER,
  generic_critique TEXT NOT NULL DEFAULT '',
  evidence_gap TEXT NOT NULL DEFAULT '',
  theater_risk TEXT NOT NULL DEFAULT '',
  excess_risk TEXT NOT NULL DEFAULT '',
  maturity_study REAL NOT NULL DEFAULT 0.0,
  maturity_application REAL NOT NULL DEFAULT 0.0,
  maturity_executive REAL NOT NULL DEFAULT 0.0,
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  FOREIGN KEY (contestor_agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- Tabela de incertezas/lacunas abertas
CREATE TABLE IF NOT EXISTS uncertainty_register (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  uncertainty_text TEXT NOT NULL,
  impact_level TEXT NOT NULL DEFAULT 'medio' CHECK(impact_level IN ('baixo', 'medio', 'alto', 'critico')),
  status TEXT NOT NULL DEFAULT 'aberta' CHECK(status IN ('aberta', 'parcialmente_resolvida', 'resolvida', 'descartada')),
  requires_favini INTEGER NOT NULL DEFAULT 0 CHECK(requires_favini IN (0, 1)),
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  resolved_at TEXT,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- Tabela de contradições/limitações por fonte
CREATE TABLE IF NOT EXISTS contradictions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL,
  agent_id INTEGER NOT NULL,
  limitation_text TEXT NOT NULL,
  misinterpretation_text TEXT NOT NULL DEFAULT '',
  contestor_agent_id INTEGER,
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
  FOREIGN KEY (contestor_agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- Tabela de briefings/relatórios executivos
CREATE TABLE IF NOT EXISTS executive_briefings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  briefing_type TEXT NOT NULL CHECK(briefing_type IN ('ciclo_completo', 'agente_update', 'risco', 'decisao')),
  title TEXT NOT NULL,
  content_markdown TEXT NOT NULL,
  cycle_number INTEGER,
  related_agent_id INTEGER,
  requires_favini INTEGER NOT NULL DEFAULT 0 CHECK(requires_favini IN (0, 1)),
  is_exported INTEGER NOT NULL DEFAULT 0 CHECK(is_exported IN (0, 1)),
  exported_to TEXT DEFAULT '',
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (related_agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- Tabela de uso de modelos (para tracking de custos operacionais)
CREATE TABLE IF NOT EXISTS model_usage_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_name TEXT NOT NULL,
  provider TEXT NOT NULL,
  task_type TEXT NOT NULL,
  input_tokens INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  estimated_cost_usd REAL NOT NULL DEFAULT 0.0,
  agent_id INTEGER,
  related_source_id INTEGER,
  result_summary TEXT DEFAULT '',
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL,
  FOREIGN KEY (related_source_id) REFERENCES knowledge_sources(id) ON DELETE SET NULL
);

-- Tabela de budget de tokens (para rastrear consumo)
CREATE TABLE IF NOT EXISTS token_budget_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  budget_period TEXT NOT NULL,
  provider TEXT NOT NULL,
  budget_amount INTEGER NOT NULL,
  tokens_used INTEGER NOT NULL DEFAULT 0,
  estimated_cost_usd REAL NOT NULL DEFAULT 0.0,
  status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'exhausted', 'paused')),
  notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_agent ON knowledge_sources(agent_id, status);
CREATE INDEX IF NOT EXISTS idx_source_readings_source ON source_readings(source_id);
CREATE INDEX IF NOT EXISTS idx_extracted_claims_agent ON extracted_claims(agent_id, classification);
CREATE INDEX IF NOT EXISTS idx_extracted_claims_contested ON extracted_claims(is_contested);
CREATE INDEX IF NOT EXISTS idx_agent_concepts_agent ON agent_concepts(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_rules_agent ON agent_rules(agent_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_agent ON agent_learning_events(agent_id, created_at);
CREATE INDEX IF NOT EXISTS idx_uncertainty_status ON uncertainty_register(agent_id, status);
CREATE INDEX IF NOT EXISTS idx_executive_briefings_type ON executive_briefings(briefing_type, created_at);
CREATE INDEX IF NOT EXISTS idx_model_usage_provider ON model_usage_log(provider, created_at);
