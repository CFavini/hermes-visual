#!/usr/bin/env python3
"""Hermes v0.4-alpha local server — stdlib only."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
DB_PATH = ROOT / "db" / "private" / "hermes_v04.sqlite"
HOST = "127.0.0.1"
PORT = 8040


def row_to_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


class HermesHandler(BaseHTTPRequestHandler):
    server_version = "HermesV04Alpha/0.1"

    def __init__(self, *args, **kwargs):
        self.web_dir = WEB_DIR
        super().__init__(*args, **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def api_error(self, message: str, status: int = 500) -> None:
        self.send_json({"ok": False, "error": message}, status=status)
    
    def get_debug_identity(self) -> None:
        """GET /api/_debug/identity — Identidade do servidor."""
        import os
        routes_dict = {
            "/api/knowledge": True,
            "/api/knowledge/sources": True,
            "/api/knowledge/claims": True,
        }
        self.send_json({
            "ok": True,
            "server_file": os.path.abspath(__file__),
            "cwd": os.getcwd(),
            "version": "v0.4.2-p0-router-fix",
            "db_path": str(DB_PATH.absolute()),
            "has_knowledge_sources_route": "/api/knowledge/sources" in routes_dict
        })
    
    def serve_file(self, path: str) -> None:
        """Serve um arquivo estático do diretório web."""
        file_path = (self.web_dir / path.lstrip("/")).resolve()
        
        # Segurança: não sair de web_dir
        if not str(file_path).startswith(str(self.web_dir)):
            self.send_error(403, "Forbidden")
            return
        
        if not file_path.exists():
            self.send_error(404, "Not Found")
            return
        
        if file_path.is_dir():
            # Tentar index.html na pasta
            index = file_path / "index.html"
            if index.exists():
                file_path = index
            else:
                self.send_error(403, "Forbidden")
                return
        
        # Servir arquivo
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            
            # Determina content-type
            content_type = "text/plain"
            if file_path.suffix == ".html":
                content_type = "text/html"
            elif file_path.suffix == ".css":
                content_type = "text/css"
            elif file_path.suffix == ".js":
                content_type = "application/javascript"
            elif file_path.suffix == ".json":
                content_type = "application/json"
            
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))

    def do_GET(self) -> None:  # noqa: N802
        import os
        # Saber qual arquivo está sendo executado
        if not hasattr(self, "_debug_server_path"):
            print(f"SERVER RUNNING FROM: {os.path.abspath(__file__)}", file=__import__('sys').stderr)
            self.__class__._debug_server_path = True
        
        parsed = urlparse(self.path)
        path = parsed.path
        
        # PRIORIDADE 1: APIs sempre antes de arquivos estáticos
        if path.startswith("/api/"):
            try:
                self.route_get(path)
                return
            except FileNotFoundError:
                self.api_error("Banco não encontrado. Rode: python3 scripts/init_db.py", 503)
                return
            except Exception as exc:  # defensive local server
                self.api_error(str(exc), 500)
                return
        
        # PRIORIDADE 2: Arquivo estático ou raiz
        if path == "/":
            path = "/index.html"
        
        # Servir arquivo estático
        self.serve_file(path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if not path.startswith("/api/"):
            self.api_error("Endpoint não encontrado", 404)
            return
        try:
            payload = self.read_json()
            self.route_post(path, payload)
        except FileNotFoundError:
            self.api_error("Banco não encontrado. Rode: python3 scripts/init_db.py", 503)
        except json.JSONDecodeError:
            self.api_error("JSON inválido", 400)
        except Exception as exc:
            self.api_error(str(exc), 500)

    def route_get(self, path: str) -> None:
        if path == "/api/_debug/identity":
            return self.get_debug_identity()

        if path == "/api/companies":
            return self.get_companies()

        if path == "/api/rooms":
            return self.get_rooms()

        if path == "/api/agents":
            return self.get_agents()

        if path == "/api/tasks":
            return self.get_tasks()

        if path == "/api/decisions":
            return self.get_decisions()

        if path == "/api/alerts":
            return self.get_alerts()

        if path == "/api/knowledge":
            return self.get_knowledge_index()

        if path == "/api/knowledge/sources":
            return self.get_knowledge_sources()

        if path == "/api/knowledge/claims":
            return self.get_knowledge_claims()

        if path == "/api/knowledge/uncertainties":
            return self.get_knowledge_uncertainties()

        if path == "/api/knowledge/briefings/latest":
            return self.get_briefings_latest()

        if path == "/api/model-usage/summary":
            return self.get_model_usage_summary()

        if path.startswith("/api/knowledge/agents/") and path.endswith("/learning"):
            return self.get_agent_learning(path)

        if path.startswith("/api/knowledge/agents/") and path.endswith("/rules"):
            return self.get_agent_rules(path)

        if path == "/api/simulation/intents":
            return self.get_simulation_intents()

        if path == "/api/ai/budget-policy":
            return self.get_ai_budget_policy()

        return self.api_error("Endpoint não encontrado", 404)

    def route_post(self, path: str, payload: dict) -> None:
        routes = {
            "/api/cycle": self.post_cycle,
            "/api/tasks": self.post_task,
            "/api/decisions": self.post_decision,
            "/api/simulation/tick": self.post_simulation_tick,
        }
        handler = routes.get(path)
        if handler is None:
            self.api_error("Endpoint não encontrado", 404)
            return
        handler(payload)

    def get_companies(self) -> None:
        sql = """
        SELECT vc.*, COUNT(ra.id) AS open_alerts
        FROM virtual_companies vc
        LEFT JOIN risk_alerts ra ON ra.company_id = vc.id AND ra.status = 'open'
        GROUP BY vc.id
        ORDER BY vc.is_blocked DESC, vc.risk_level DESC, vc.id ASC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "companies": rows})

    def get_rooms(self) -> None:
        sql = """
        SELECT r.*, vc.name AS company_name, vc.visual_color AS company_color, vc.risk_level AS company_risk
        FROM rooms r
        LEFT JOIN virtual_companies vc ON vc.id = r.company_id
        ORDER BY r.grid_row ASC, r.grid_col ASC, r.id ASC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "rooms": rows})

    def get_agents(self) -> None:
        sql = """
        SELECT a.*, r.name AS room_name, r.slug AS room_slug
        FROM agents a
        LEFT JOIN rooms r ON r.id = a.current_room_id
        ORDER BY a.id ASC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "agents": rows})

    def get_tasks(self) -> None:
        sql = """
        SELECT t.*, vc.name AS company_name, r.name AS room_name, a.name AS agent_name
        FROM tasks t
        LEFT JOIN virtual_companies vc ON vc.id = t.company_id
        LEFT JOIN rooms r ON r.id = t.room_id
        LEFT JOIN agents a ON a.id = t.assigned_agent_id
        ORDER BY CASE t.priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 ELSE 2 END,
                 CASE t.status WHEN 'blocked' THEN 0 WHEN 'pending' THEN 1 WHEN 'in_progress' THEN 2 ELSE 3 END,
                 t.risk_level DESC, t.id ASC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "tasks": rows})

    def get_decisions(self) -> None:
        sql = """
        SELECT d.*, vc.name AS company_name
        FROM decisions d
        LEFT JOIN virtual_companies vc ON vc.id = d.company_id
        ORDER BY CASE d.priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 ELSE 2 END,
                 CASE d.status WHEN 'pending' THEN 0 ELSE 1 END,
                 d.id ASC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "decisions": rows})

    def get_alerts(self) -> None:
        sql = """
        SELECT ra.*, vc.name AS company_name, a.name AS agent_name
        FROM risk_alerts ra
        LEFT JOIN virtual_companies vc ON vc.id = ra.company_id
        LEFT JOIN agents a ON a.id = ra.agent_id
        ORDER BY ra.blocks_progress DESC, ra.severity DESC, ra.id ASC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "alerts": rows})

    def post_cycle(self, payload: dict | None = None) -> None:
        with connect() as conn:
            critical_company = conn.execute(
                """
                SELECT * FROM virtual_companies
                ORDER BY is_blocked DESC, risk_level DESC, requires_legal_review DESC, phase DESC, id ASC
                LIMIT 1;
                """
            ).fetchone()
            critical_task = conn.execute(
                """
                SELECT * FROM tasks
                WHERE priority = 'P0'
                ORDER BY CASE status WHEN 'blocked' THEN 0 WHEN 'pending' THEN 1 WHEN 'in_progress' THEN 2 ELSE 3 END,
                         risk_level DESC, id ASC
                LIMIT 1;
                """
            ).fetchone()
            critical_alert = conn.execute(
                """
                SELECT * FROM risk_alerts
                WHERE status = 'open'
                ORDER BY blocks_progress DESC, severity DESC, id ASC
                LIMIT 1;
                """
            ).fetchone()
            pending_count = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM decisions
                WHERE status = 'pending' AND requires_favini = 1;
                """
            ).fetchone()["count"]
            blocked_agent = None
            if critical_alert and critical_alert["agent_id"]:
                blocked_agent = conn.execute("SELECT * FROM agents WHERE id = ?", (critical_alert["agent_id"],)).fetchone()
            if blocked_agent is None:
                blocked_agent = conn.execute(
                    """
                    SELECT * FROM agents
                    ORDER BY is_blocked DESC, can_block DESC, id ASC
                    LIMIT 1;
                    """
                ).fetchone()

            summary = (
                f"Ciclo Hermes local concluído. Frente crítica: {critical_company['name'] if critical_company else 'n/d'}. "
                f"Tarefa P0: {critical_task['title'] if critical_task else 'n/d'}. "
                "Nenhuma ação externa executada."
            )
            cur = conn.execute(
                """
                INSERT INTO hermes_cycles
                (critical_company_id, blocked_agent_id, critical_task_id, critical_alert_id,
                 pending_decisions_count, summary, is_simulated, external_action_executed)
                VALUES (?, ?, ?, ?, ?, ?, 1, 0);
                """,
                (
                    critical_company["id"] if critical_company else None,
                    blocked_agent["id"] if blocked_agent else None,
                    critical_task["id"] if critical_task else None,
                    critical_alert["id"] if critical_alert else None,
                    pending_count,
                    summary,
                ),
            )
            cycle_id = cur.lastrowid
            if critical_task:
                conn.execute(
                    """
                    INSERT INTO task_events
                    (task_id, agent_id, event_type, message, is_external_action, data_classification)
                    VALUES (?, ?, 'cycle', ?, 0, ?);
                    """,
                    (
                        critical_task["id"],
                        critical_task["assigned_agent_id"],
                        f"Ciclo Hermes #{cycle_id}: diagnóstico local registrado; nenhuma ação externa executada.",
                        critical_task["data_classification"],
                    ),
                )
            conn.commit()

        self.send_json(
            {
                "ok": True,
                "cycle": {
                    "id": cycle_id,
                    "critical_company": row_to_dict(critical_company) if critical_company else None,
                    "blocked_agent": row_to_dict(blocked_agent) if blocked_agent else None,
                    "critical_task": row_to_dict(critical_task) if critical_task else None,
                    "critical_alert": row_to_dict(critical_alert) if critical_alert else None,
                    "pending_decisions_count": pending_count,
                    "external_action_executed": False,
                    "summary": summary,
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                },
            }
        )

    def post_task(self, payload: dict) -> None:
        title = str(payload.get("title", "")).strip()
        if not title:
            self.api_error("Campo obrigatório: title", 400)
            return
        company_id = payload.get("company_id")
        room_id = payload.get("room_id")
        assigned_agent_id = payload.get("assigned_agent_id")
        description = str(payload.get("description", "Tarefa local criada no Hermes v0.4-alpha."))
        priority = str(payload.get("priority", "P1"))
        risk_level = int(payload.get("risk_level", 2))
        with connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO tasks
                (company_id, room_id, assigned_agent_id, title, description, priority, status,
                 risk_level, requires_favini, requires_legal, external_action_allowed, is_simulated, data_classification)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, 0, 0, 0, 1, 'S0');
                """,
                (company_id, room_id, assigned_agent_id, title, description, priority, risk_level),
            )
            task_id = cur.lastrowid
            conn.execute(
                """
                INSERT INTO task_events
                (task_id, agent_id, event_type, message, is_external_action, data_classification)
                VALUES (?, ?, 'created', 'Tarefa criada localmente pelo protótipo.', 0, 'S0');
                """,
                (task_id, assigned_agent_id),
            )
            conn.commit()
        self.send_json({"ok": True, "task_id": task_id}, 201)

    def post_decision(self, payload: dict) -> None:
        title = str(payload.get("title", "")).strip()
        if not title:
            self.api_error("Campo obrigatório: title", 400)
            return
        code = str(payload.get("decision_code") or f"DEC-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        company_id = payload.get("company_id")
        summary = str(payload.get("summary", "Decisão local pendente de Favini."))
        priority = str(payload.get("priority", "P1"))
        with connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO decisions
                (company_id, title, decision_code, status, priority, summary, required_by,
                 requires_favini, external_effect_allowed, data_classification)
                VALUES (?, ?, ?, 'pending', ?, ?, 'Favini', 1, 0, 'S0');
                """,
                (company_id, title, code, priority, summary),
            )
            conn.commit()
        self.send_json({"ok": True, "decision_id": cur.lastrowid, "decision_code": code}, 201)

    # v0.4.2 — Knowledge Endpoints
    def get_knowledge_index(self) -> None:
        """GET /api/knowledge — Index de endpoints de conhecimento."""
        self.send_json({
            "ok": True,
            "knowledge": {
                "sources": "/api/knowledge/sources",
                "claims": "/api/knowledge/claims",
                "uncertainties": "/api/knowledge/uncertainties",
                "briefings": "/api/knowledge/briefings/latest",
                "model_usage": "/api/model-usage/summary",
                "agent_learning": "/api/knowledge/agents/{agent_id}"
            }
        })
    
    def get_knowledge_sources(self) -> None:
        """GET /api/knowledge/sources — Lista de fontes estudadas."""
        sql = """
        SELECT ks.id, ks.source_id, ks.agent_id, ks.title, ks.institution, ks.year,
               ks.level, ks.status, ks.reliability, a.name AS agent_name
        FROM knowledge_sources ks
        LEFT JOIN agents a ON a.id = ks.agent_id
        ORDER BY ks.agent_id ASC, ks.created_at DESC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "sources": rows})

    def get_knowledge_claims(self) -> None:
        """GET /api/knowledge/claims — Claims extraídos."""
        sql = """
        SELECT ec.id, ec.source_id, ec.agent_id, ec.claim_id, ec.claim_text,
               ec.classification, ec.level, ec.reliability, a.name AS agent_name
        FROM extracted_claims ec
        LEFT JOIN agents a ON a.id = ec.agent_id
        ORDER BY ec.created_at DESC
        LIMIT 100;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "claims": rows})

    def get_agent_learning(self, path: str) -> None:
        """GET /api/knowledge/agents/{id}/learning — Aprendizagem de agente específico."""
        parts = path.split("/")
        try:
            agent_id = int(parts[4])  # /api/knowledge/agents/ID/learning
        except (ValueError, IndexError):
            self.api_error("Agent ID invalido", 400)
            return
        
        with connect() as conn:
            # Fontes estudadas
            sources_sql = """
            SELECT ks.id, ks.source_id, ks.title, ks.status, ks.level
            FROM knowledge_sources ks
            WHERE ks.agent_id = ?
            ORDER BY ks.created_at DESC;
            """
            sources = [row_to_dict(row) for row in conn.execute(sources_sql, (agent_id,))]
            
            # Regras operacionais
            rules_sql = """
            SELECT ar.id, ar.rule_id, ar.rule_name, ar.rule_statement
            FROM agent_rules ar
            WHERE ar.agent_id = ?
            ORDER BY ar.created_at DESC;
            """
            rules = [row_to_dict(row) for row in conn.execute(rules_sql, (agent_id,))]
            
            # Conceitos
            concepts_sql = """
            SELECT ac.id, ac.concept_id, ac.concept_name, ac.definition
            FROM agent_concepts ac
            WHERE ac.agent_id = ?
            ORDER BY ac.created_at DESC;
            """
            concepts = [row_to_dict(row) for row in conn.execute(concepts_sql, (agent_id,))]
            
            # Lacunas abertas
            gaps_sql = """
            SELECT ur.id, ur.uncertainty_text, ur.impact_level, ur.status
            FROM uncertainty_register ur
            WHERE ur.agent_id = ? AND ur.status = 'aberta'
            ORDER BY ur.impact_level DESC;
            """
            gaps = [row_to_dict(row) for row in conn.execute(gaps_sql, (agent_id,))]
            
            # Learning event mais recente
            learning_sql = """
            SELECT ale.id, ale.learning_text, ale.domain, ale.maturity_after, ale.created_at
            FROM agent_learning_events ale
            WHERE ale.agent_id = ?
            ORDER BY ale.created_at DESC
            LIMIT 1;
            """
            latest_learning = row_to_dict(conn.execute(learning_sql, (agent_id,)).fetchone() or {})
        
        self.send_json({
            "ok": True,
            "agent_id": agent_id,
            "sources": sources,
            "rules": rules,
            "concepts": concepts,
            "open_gaps": gaps,
            "latest_learning": latest_learning,
        })
    
    def get_agent_rules(self, path: str) -> None:
        """GET /api/knowledge/agents/{id}/rules — Regras operacionais de agente."""
        try:
            parts = path.split("/")
            agent_id = int(parts[4])
        except (ValueError, IndexError):
            self.api_error("Agent ID invalido", 400)
            return
        
        with connect() as conn:
            sql = """
            SELECT
                id,
                agent_id,
                rule_id,
                rule_name,
                rule_statement AS rule_text,
                data_classification AS classification,
                apply_when,
                skip_when,
                test_criteria,
                'P1' AS priority,
                'active' AS status,
                created_at
            FROM agent_rules
            WHERE agent_id = ?
            ORDER BY created_at DESC;
            """
            rules = [row_to_dict(row) for row in conn.execute(sql, (agent_id,))]
        
        self.send_json({"ok": True, "agent_id": agent_id, "rules": rules})

    def get_knowledge_uncertainties(self) -> None:
        """GET /api/knowledge/uncertainties — Incertezas abertas por agente."""
        sql = """
        SELECT ur.id, ur.agent_id, ur.uncertainty_text, ur.impact_level, ur.status,
               a.name AS agent_name
        FROM uncertainty_register ur
        LEFT JOIN agents a ON a.id = ur.agent_id
        WHERE ur.status = 'aberta'
        ORDER BY ur.impact_level DESC, ur.agent_id ASC;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "uncertainties": rows})

    def get_briefings_latest(self) -> None:
        """GET /api/knowledge/briefings/latest — Ultimos briefings executivos."""
        sql = """
        SELECT eb.id, eb.briefing_type, eb.title, eb.cycle_number,
               eb.created_at, a.name AS agent_name
        FROM executive_briefings eb
        LEFT JOIN agents a ON a.id = eb.related_agent_id
        ORDER BY eb.created_at DESC
        LIMIT 10;
        """
        with connect() as conn:
            rows = [row_to_dict(row) for row in conn.execute(sql)]
        self.send_json({"ok": True, "briefings": rows})

    def get_model_usage_summary(self) -> None:
        """GET /api/model-usage/summary — Resumo de uso de modelos/custo."""
        with connect() as conn:
            # Uso por provider
            provider_sql = """
            SELECT provider, COUNT(*) AS uses, SUM(input_tokens) AS total_input,
                   SUM(output_tokens) AS total_output, SUM(estimated_cost_usd) AS total_cost
            FROM model_usage_log
            GROUP BY provider
            ORDER BY total_cost DESC;
            """
            by_provider = [row_to_dict(row) for row in conn.execute(provider_sql)]
            
            # Budget status
            budget_sql = """
            SELECT budget_period, provider, budget_amount, tokens_used,
                   estimated_cost_usd, status
            FROM token_budget_log
            ORDER BY budget_period DESC
            LIMIT 5;
            """
            budgets = [row_to_dict(row) for row in conn.execute(budget_sql)]
            
            # Total
            total_sql = """
            SELECT COUNT(*) AS total_calls, SUM(input_tokens) AS total_input,
                   SUM(output_tokens) AS total_output, SUM(estimated_cost_usd) AS total_cost
            FROM model_usage_log;
            """
            total_row = conn.execute(total_sql).fetchone()
            total = row_to_dict(total_row) if total_row else {}
        
        self.send_json({
            "ok": True,
            "by_provider": by_provider,
            "budgets": budgets,
            "total": total,
        })

    def get_simulation_intents(self) -> None:
        """GET /api/simulation/intents — Intenções atuais de cada agente baseadas em SQLite."""
        try:
            with connect() as conn:
                # Query simplificada: ler agentes e virtudes
                sql = """
                SELECT 
                  a.id as agent_id,
                  a.name,
                  a.current_room_id,
                  av.virtue_primary,
                  av.main_intention as intention_type,
                  'Operação normal' as reason,
                  a.current_room_id as target_room_id,
                  1 as priority,
                  CASE WHEN av.agent_id IN (1,3,7) THEN 1 ELSE 0 END as requires_favini,
                  0 as external_action_allowed
                FROM agents a
                LEFT JOIN agent_virtues av ON av.agent_id = a.id
                ORDER BY a.id;
                """
                intents = [row_to_dict(row) for row in conn.execute(sql)]
            
            self.send_json({"ok": True, "intents": intents, "source": "SQLite persistent", "count": len(intents)})
        except Exception as e:
            self.api_error(f"Erro em intents: {str(e)}", 500)


    def post_simulation_tick(self) -> None:
        """POST /api/simulation/tick — Registra um tick de simulação."""
        with connect() as conn:
            # Ler intenções atuais
            intents_sql = "SELECT * FROM agent_intentions WHERE expires_at IS NULL OR expires_at > DATETIME('now') LIMIT 12;"
            intents = list(conn.execute(intents_sql))
            
            # Criar novo tick
            tick_sql = "INSERT INTO simulation_ticks (tick_number, start_at, agent_intents_count) VALUES ((SELECT COALESCE(MAX(tick_number), 0) + 1 FROM simulation_ticks), DATETIME('now'), ?);"
            conn.execute(tick_sql, (len(intents),))
            
            # Ler tick criado
            tick_number = conn.execute("SELECT MAX(tick_number) FROM simulation_ticks;").fetchone()[0]
            
            # Criar eventos para movimentos
            for intent in intents:
                event_sql = """
                INSERT INTO world_events (tick_number, event_type, agent_id, target_room_id, description, requires_favini, created_at)
                VALUES (?, 'movement', ?, ?, ?, ?, DATETIME('now'));
                """
                conn.execute(event_sql, (tick_number, intent['agent_id'], intent['target_room_id'], f"Agente {intent['agent_id']} moveu-se para sala.", intent.get('requires_favini', 0)))
            
            conn.commit()
            
            self.send_json({"ok": True, "tick_number": tick_number, "events_created": len(intents), "source": "SQLite persistent"})


    def get_ai_budget_policy(self) -> None:
        """GET /api/ai/budget-policy — Política atual de IA e orçamento."""
        try:
            with connect() as conn:
                sql = "SELECT * FROM ai_budget_policy WHERE id=1 LIMIT 1;"
                row = conn.execute(sql).fetchone()
                policy = row_to_dict(row) if row else {}
            
            # Adicionar metadados calculados
            policy['endpoints_available'] = [
                '/api/simulation/intents',
                '/api/simulation/tick',
                '/api/ai/budget-policy'
            ]
            policy['model_breakdown'] = {
                'local_daily': 'Ollama/Qwen (custo zero)',
                'free_external': 'Gemini/OpenRouter/Groq free tier',
                'cheap_paid': 'DeepSeek/Gemini Flash (uso mínimo)',
                'premium_surgical': 'Claude/OpenAI (somente com autorização)'
            }
            
            self.send_json({"ok": True, "policy": policy})
        except Exception as e:
            self.api_error(f"Erro ao ler política: {str(e)}", 500)


def main() -> None:
    if not DB_PATH.exists():
        print("Banco nao encontrado. Rode primeiro: python3 scripts/init_db_v042.py")
    print(f"Hermes v0.4.2 servindo em http://{HOST}:{PORT}")
    print("Ambiente: SIMULACAO LOCAL — SEM ACAO EXTERNA")
    server = ThreadingHTTPServer((HOST, PORT), HermesHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    main()
