PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS virtual_companies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  entity_type TEXT NOT NULL,
  phase INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'simulada',
  legal_status TEXT NOT NULL DEFAULT 'sem_personalidade_juridica',
  labels TEXT NOT NULL DEFAULT '',
  risk_level INTEGER NOT NULL DEFAULT 1 CHECK (risk_level BETWEEN 1 AND 5),
  visual_color TEXT NOT NULL DEFAULT '#2f6fed',
  data_classification TEXT NOT NULL DEFAULT 'S0',
  is_simulated INTEGER NOT NULL DEFAULT 1 CHECK (is_simulated IN (0, 1)),
  external_interaction_allowed INTEGER NOT NULL DEFAULT 0 CHECK (external_interaction_allowed IN (0, 1)),
  requires_human_responsible INTEGER NOT NULL DEFAULT 0 CHECK (requires_human_responsible IN (0, 1)),
  requires_legal_review INTEGER NOT NULL DEFAULT 0 CHECK (requires_legal_review IN (0, 1)),
  is_blocked INTEGER NOT NULL DEFAULT 0 CHECK (is_blocked IN (0, 1)),
  public_summary TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rooms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  room_type TEXT NOT NULL DEFAULT 'operational',
  status TEXT NOT NULL DEFAULT 'active',
  grid_col INTEGER NOT NULL DEFAULT 1,
  grid_row INTEGER NOT NULL DEFAULT 1,
  grid_w INTEGER NOT NULL DEFAULT 2,
  grid_h INTEGER NOT NULL DEFAULT 2,
  security_level TEXT NOT NULL DEFAULT 'S0',
  is_quarantine INTEGER NOT NULL DEFAULT 0 CHECK (is_quarantine IN (0, 1)),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (company_id) REFERENCES virtual_companies(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS agents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL,
  avatar_symbol TEXT NOT NULL DEFAULT '●',
  home_room_id INTEGER,
  current_room_id INTEGER,
  state TEXT NOT NULL DEFAULT 'idle',
  status TEXT NOT NULL DEFAULT 'available',
  alert_type TEXT NOT NULL DEFAULT '',
  can_block INTEGER NOT NULL DEFAULT 0 CHECK (can_block IN (0, 1)),
  is_blocked INTEGER NOT NULL DEFAULT 0 CHECK (is_blocked IN (0, 1)),
  data_access_level TEXT NOT NULL DEFAULT 'S0',
  external_interaction_allowed INTEGER NOT NULL DEFAULT 0 CHECK (external_interaction_allowed IN (0, 1)),
  visual_color TEXT NOT NULL DEFAULT '#7aa2ff',
  xp INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (home_room_id) REFERENCES rooms(id) ON DELETE SET NULL,
  FOREIGN KEY (current_room_id) REFERENCES rooms(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  room_id INTEGER,
  assigned_agent_id INTEGER,
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  priority TEXT NOT NULL DEFAULT 'P1',
  status TEXT NOT NULL DEFAULT 'pending',
  risk_level INTEGER NOT NULL DEFAULT 1 CHECK (risk_level BETWEEN 1 AND 5),
  requires_favini INTEGER NOT NULL DEFAULT 0 CHECK (requires_favini IN (0, 1)),
  requires_legal INTEGER NOT NULL DEFAULT 0 CHECK (requires_legal IN (0, 1)),
  external_action_allowed INTEGER NOT NULL DEFAULT 0 CHECK (external_action_allowed IN (0, 1)),
  is_simulated INTEGER NOT NULL DEFAULT 1 CHECK (is_simulated IN (0, 1)),
  data_classification TEXT NOT NULL DEFAULT 'S0',
  due_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at TEXT,
  FOREIGN KEY (company_id) REFERENCES virtual_companies(id) ON DELETE SET NULL,
  FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL,
  FOREIGN KEY (assigned_agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS task_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  agent_id INTEGER,
  event_type TEXT NOT NULL,
  message TEXT NOT NULL,
  is_external_action INTEGER NOT NULL DEFAULT 0 CHECK (is_external_action IN (0, 1)),
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  title TEXT NOT NULL,
  decision_code TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending',
  priority TEXT NOT NULL DEFAULT 'P1',
  summary TEXT NOT NULL DEFAULT '',
  required_by TEXT NOT NULL DEFAULT 'Favini',
  requires_favini INTEGER NOT NULL DEFAULT 1 CHECK (requires_favini IN (0, 1)),
  external_effect_allowed INTEGER NOT NULL DEFAULT 0 CHECK (external_effect_allowed IN (0, 1)),
  data_classification TEXT NOT NULL DEFAULT 'S0',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  decided_at TEXT,
  FOREIGN KEY (company_id) REFERENCES virtual_companies(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS risk_alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER,
  task_id INTEGER,
  agent_id INTEGER,
  title TEXT NOT NULL,
  risk_type TEXT NOT NULL,
  severity INTEGER NOT NULL DEFAULT 1 CHECK (severity BETWEEN 1 AND 5),
  status TEXT NOT NULL DEFAULT 'open',
  blocks_progress INTEGER NOT NULL DEFAULT 0 CHECK (blocks_progress IN (0, 1)),
  requires_favini INTEGER NOT NULL DEFAULT 0 CHECK (requires_favini IN (0, 1)),
  data_classification TEXT NOT NULL DEFAULT 'S0',
  message TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  resolved_at TEXT,
  FOREIGN KEY (company_id) REFERENCES virtual_companies(id) ON DELETE SET NULL,
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS hermes_cycles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  critical_company_id INTEGER,
  blocked_agent_id INTEGER,
  critical_task_id INTEGER,
  critical_alert_id INTEGER,
  pending_decisions_count INTEGER NOT NULL DEFAULT 0,
  summary TEXT NOT NULL DEFAULT '',
  is_simulated INTEGER NOT NULL DEFAULT 1 CHECK (is_simulated IN (0, 1)),
  external_action_executed INTEGER NOT NULL DEFAULT 0 CHECK (external_action_executed IN (0, 1)),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (critical_company_id) REFERENCES virtual_companies(id) ON DELETE SET NULL,
  FOREIGN KEY (blocked_agent_id) REFERENCES agents(id) ON DELETE SET NULL,
  FOREIGN KEY (critical_task_id) REFERENCES tasks(id) ON DELETE SET NULL,
  FOREIGN KEY (critical_alert_id) REFERENCES risk_alerts(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_virtual_companies_risk ON virtual_companies(is_blocked, risk_level);
CREATE INDEX IF NOT EXISTS idx_rooms_company ON rooms(company_id);
CREATE INDEX IF NOT EXISTS idx_agents_room ON agents(current_room_id);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority, status, risk_level);
CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status, requires_favini);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON risk_alerts(status, blocks_progress, severity);
