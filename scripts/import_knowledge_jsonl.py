#!/usr/bin/env python3
"""
Hermes v0.4.2 — Import Knowledge JSONL to SQLite

Lê arquivos JSONL de ~/.hermes/knowledge/ e insere no SQLite,
substituindo JSONL com SQLite como fonte canônica de memória.

Uso:
  python3 scripts/import_knowledge_jsonl.py

Precisa:
  - Banco SQLite já inicializado (rodou schema_v042_knowledge.sql)
  - Agentes já existem na tabela agents
  - ~/.hermes/knowledge/*.jsonl existem

Estratégia:
  - Valida cada linha JSON
  - Ignora linhas inválidas com log (não falha)
  - Detecta duplicatas por source_id / claim_id / rule_id, não insere
  - Gera resumo final

"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Caminhos
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "private" / "hermes_v04.sqlite"
KNOWLEDGE_DIR = Path.home() / ".hermes" / "knowledge"

# Arquivos JSONL esperados
JSONL_FILES = {
    "sources_ledger.jsonl": "knowledge_sources",
    "claims_ledger.jsonl": "extracted_claims",
    "concepts_ledger.jsonl": "agent_concepts",
    "contradictions_ledger.jsonl": "contradictions",
    "agent_learning_log.jsonl": "agent_learning_events",
    "agent_exams.jsonl": "agent_exams",
    "uncertainty_register.jsonl": "uncertainty_register",
    "rejected_sources.jsonl": None,  # Log apenas, não insere
}


def get_agent_id_by_name(conn: sqlite3.Connection, agent_name: str) -> int | None:
    """Busca ID do agente pelo nome."""
    cur = conn.execute("SELECT id FROM agents WHERE name = ?", (agent_name,))
    row = cur.fetchone()
    return row[0] if row else None


def normalize_enum_value(field: str, value: str) -> str:
    """Normaliza valores de enum para aceitar variações com/sem acento."""
    if field == "classification":
        # princípio -> principio, recomendação -> recomendacao, etc.
        return (value.lower()
                .replace("princípio", "principio")
                .replace("recomendação", "recomendacao")
                .replace("média", "media")
                .replace("alta", "alta")
                .replace("baixa", "baixa"))
    elif field == "status":
        # lida_parcialmente -> parcialmente_lida
        return (value.lower()
                .replace("lida_parcialmente", "parcialmente_lida")
                .replace("lida_completa", "lida_completa")
                .replace("parcialmente_lida", "parcialmente_lida"))
    elif field == "reliability":
        return (value.lower()
                .replace("média", "media")
                .replace("media-alta", "media-alta")
                .replace("media-alta", "media-alta"))
    return value.lower() if isinstance(value, str) else str(value)


def get_source_id(conn: sqlite3.Connection, source_id_text: str) -> int | None:
    """Busca ID da fonte pelo source_id."""
    cur = conn.execute("SELECT id FROM knowledge_sources WHERE source_id = ?", (source_id_text,))
    row = cur.fetchone()
    return row[0] if row else None


def import_sources_ledger(conn: sqlite3.Connection, path: Path) -> dict[str, Any]:
    """Importa sources_ledger.jsonl → knowledge_sources."""
    stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
    
    if not path.exists():
        print(f"⚠ {path.name} não encontrado")
        return stats
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["read"] += 1
                    
                    agent_name = record.get("agent")
                    agent_id = get_agent_id_by_name(conn, agent_name)
                    
                    if not agent_id:
                        print(f"  ⚠ Linha {line_no}: agente '{agent_name}' não encontrado, pulando")
                        stats["skipped"] += 1
                        continue
                    
                    # Verifica duplicação
                    source_id_text = record.get("source_id")
                    existing = get_source_id(conn, source_id_text)
                    if existing:
                        stats["skipped"] += 1
                        continue
                    
                    conn.execute("""
                        INSERT INTO knowledge_sources (
                            source_id, agent_id, title, institution, year, url, access_tool,
                            access_date, level, language, sections_read, status, reliability
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        source_id_text,
                        agent_id,
                        record.get("title", ""),
                        record.get("institution", ""),
                        record.get("year", 0),
                        record.get("url", ""),
                        record.get("access_tool", "web_extract"),
                        record.get("access_date", datetime.utcnow().isoformat()),
                        record.get("level", "N1"),
                        record.get("language", "English"),
                        record.get("sections_read", ""),
                        normalize_enum_value("status", record.get("status", "parcialmente_lida")),
                        normalize_enum_value("reliability", record.get("reliability", "media")),
                    ))
                    stats["imported"] += 1
                
                except json.JSONDecodeError as e:
                    stats["errors"] += 1
                    print(f"  ✗ Linha {line_no}: JSON inválido — {e}")
                except Exception as e:
                    stats["errors"] += 1
                    print(f"  ✗ Linha {line_no}: {type(e).__name__} — {e}")
    
    except IOError as e:
        print(f"✗ Erro ao ler {path.name}: {e}")
    
    return stats


def import_claims_ledger(conn: sqlite3.Connection, path: Path) -> dict[str, Any]:
    """Importa claims_ledger.jsonl → extracted_claims."""
    stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
    
    if not path.exists():
        print(f"⚠ {path.name} não encontrado")
        return stats
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["read"] += 1
                    
                    agent_name = record.get("agent")
                    agent_id = get_agent_id_by_name(conn, agent_name)
                    
                    if not agent_id:
                        print(f"  ⚠ Linha {line_no}: agente '{agent_name}' não encontrado")
                        stats["skipped"] += 1
                        continue
                    
                    source_id_text = record.get("source_id")
                    source_db_id = get_source_id(conn, source_id_text)
                    
                    if not source_db_id:
                        print(f"  ⚠ Linha {line_no}: fonte '{source_id_text}' não importada ainda")
                        stats["skipped"] += 1
                        continue
                    
                    # Verifica duplicação por claim_id
                    claim_id = record.get("claim_id")
                    cur = conn.execute("SELECT id FROM extracted_claims WHERE claim_id = ?", (claim_id,))
                    if cur.fetchone():
                        stats["skipped"] += 1
                        continue
                    
                    conn.execute("""
                        INSERT INTO extracted_claims (
                            source_id, agent_id, claim_id, claim_text, classification,
                            source_location, level, reliability, implication_hermes,
                            implication_agent, implication_favini
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        source_db_id,
                        agent_id,
                        claim_id,
                        record.get("claim", ""),
                        normalize_enum_value("classification", record.get("classification", "fato")),
                        record.get("source_location", ""),
                        record.get("level", "N1"),
                        normalize_enum_value("reliability", record.get("reliability", "media")),
                        record.get("implication_hermes", ""),
                        record.get("implication_agent", ""),
                        record.get("implication_favini", ""),
                    ))
                    stats["imported"] += 1
                
                except json.JSONDecodeError as e:
                    stats["errors"] += 1
                    print(f"  ✗ Linha {line_no}: JSON inválido — {e}")
                except Exception as e:
                    stats["errors"] += 1
                    print(f"  ✗ Linha {line_no}: {type(e).__name__} — {e}")
    
    except IOError as e:
        print(f"✗ Erro ao ler {path.name}: {e}")
    
    return stats


def import_concepts_ledger(conn: sqlite3.Connection, path: Path) -> dict[str, Any]:
    """Importa concepts_ledger.jsonl → agent_concepts."""
    stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
    
    if not path.exists():
        print(f"⚠ {path.name} não encontrado")
        return stats
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["read"] += 1
                    
                    agent_name = record.get("agent")
                    agent_id = get_agent_id_by_name(conn, agent_name)
                    
                    if not agent_id:
                        stats["skipped"] += 1
                        continue
                    
                    source_id_text = record.get("source_id")
                    source_db_id = get_source_id(conn, source_id_text)
                    
                    if not source_db_id:
                        stats["skipped"] += 1
                        continue
                    
                    concept_id = record.get("concept_id")
                    cur = conn.execute("SELECT id FROM agent_concepts WHERE concept_id = ?", (concept_id,))
                    if cur.fetchone():
                        stats["skipped"] += 1
                        continue
                    
                    conn.execute("""
                        INSERT INTO agent_concepts (
                            source_id, agent_id, concept_id, concept_name, definition,
                            use_in_agent, risk_mitigation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        source_db_id,
                        agent_id,
                        concept_id,
                        record.get("concept", ""),
                        record.get("definition", ""),
                        record.get("use_in_agent", ""),
                        record.get("risk", ""),
                    ))
                    stats["imported"] += 1
                
                except (json.JSONDecodeError, Exception) as e:
                    stats["errors"] += 1
    
    except IOError as e:
        print(f"✗ Erro ao ler {path.name}: {e}")
    
    return stats


def import_contradictions_ledger(conn: sqlite3.Connection, path: Path) -> dict[str, Any]:
    """Importa contradictions_ledger.jsonl → contradictions."""
    stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
    
    if not path.exists():
        print(f"⚠ {path.name} não encontrado")
        return stats
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["read"] += 1
                    
                    agent_name = record.get("agent")
                    agent_id = get_agent_id_by_name(conn, agent_name)
                    
                    if not agent_id:
                        stats["skipped"] += 1
                        continue
                    
                    source_id_text = record.get("source_id")
                    source_db_id = get_source_id(conn, source_id_text)
                    
                    if not source_db_id:
                        stats["skipped"] += 1
                        continue
                    
                    # Cada source tem 1 contradiction record
                    cur = conn.execute(
                        "SELECT id FROM contradictions WHERE source_id = ? AND agent_id = ?",
                        (source_db_id, agent_id)
                    )
                    if cur.fetchone():
                        stats["skipped"] += 1
                        continue
                    
                    conn.execute("""
                        INSERT INTO contradictions (
                            source_id, agent_id, limitation_text, misinterpretation_text
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        source_db_id,
                        agent_id,
                        record.get("contradiction", ""),
                        record.get("limitations", "") + "; " + record.get("misrisks", ""),
                    ))
                    stats["imported"] += 1
                
                except (json.JSONDecodeError, Exception) as e:
                    stats["errors"] += 1
    
    except IOError as e:
        print(f"✗ Erro ao ler {path.name}: {e}")
    
    return stats


def import_learning_log(conn: sqlite3.Connection, path: Path) -> dict[str, Any]:
    """Importa agent_learning_log.jsonl → agent_learning_events."""
    stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
    
    if not path.exists():
        print(f"⚠ {path.name} não encontrado")
        return stats
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["read"] += 1
                    
                    agent_name = record.get("agent")
                    agent_id = get_agent_id_by_name(conn, agent_name)
                    
                    if not agent_id:
                        stats["skipped"] += 1
                        continue
                    
                    source_id_text = record.get("source_id")
                    source_db_id = get_source_id(conn, source_id_text)
                    
                    if not source_db_id:
                        stats["skipped"] += 1
                        continue
                    
                    conn.execute("""
                        INSERT INTO agent_learning_events (
                            agent_id, source_id, learning_text, domain,
                            start_behavior, stop_behavior, error_not_repeat, remaining_gap,
                            next_reading
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        agent_id,
                        source_db_id,
                        record.get("learned", ""),
                        record.get("domain", ""),
                        record.get("start_behavior", ""),
                        record.get("stop_behavior", ""),
                        record.get("error_not_repeat", ""),
                        record.get("remaining_gap", ""),
                        record.get("next_reading", ""),
                    ))
                    stats["imported"] += 1
                
                except (json.JSONDecodeError, Exception) as e:
                    stats["errors"] += 1
    
    except IOError as e:
        print(f"✗ Erro ao ler {path.name}: {e}")
    
    return stats


def import_exams(conn: sqlite3.Connection, path: Path) -> dict[str, Any]:
    """Importa agent_exams.jsonl → agent_exams."""
    stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
    
    if not path.exists():
        print(f"⚠ {path.name} não encontrado")
        return stats
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["read"] += 1
                    
                    agent_name = record.get("agent")
                    agent_id = get_agent_id_by_name(conn, agent_name)
                    
                    if not agent_id:
                        stats["skipped"] += 1
                        continue
                    
                    source_id_text = record.get("source_id")
                    source_db_id = get_source_id(conn, source_id_text)
                    
                    if not source_db_id:
                        stats["skipped"] += 1
                        continue
                    
                    metrics = record.get("maturity_metric", {})
                    
                    conn.execute("""
                        INSERT INTO agent_exams (
                            agent_id, source_id, exercise_scenario,
                            generic_critique, evidence_gap, theater_risk, excess_risk,
                            maturity_study, maturity_application, maturity_executive
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        agent_id,
                        source_db_id,
                        record.get("exercise", ""),
                        record.get("contestator_critique", {}).get("generic", ""),
                        record.get("contestator_critique", {}).get("evidence_gap", ""),
                        record.get("contestator_critique", {}).get("theater_risk", ""),
                        record.get("contestator_critique", {}).get("excess_risk", ""),
                        metrics.get("study", 0.0),
                        metrics.get("application", 0.0),
                        metrics.get("executive_usefulness", 0.0),
                    ))
                    stats["imported"] += 1
                
                except (json.JSONDecodeError, Exception) as e:
                    stats["errors"] += 1
    
    except IOError as e:
        print(f"✗ Erro ao ler {path.name}: {e}")
    
    return stats


def import_uncertainty_register(conn: sqlite3.Connection, path: Path) -> dict[str, Any]:
    """Importa uncertainty_register.jsonl → uncertainty_register."""
    stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
    
    if not path.exists():
        print(f"⚠ {path.name} não encontrado")
        return stats
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    stats["read"] += 1
                    
                    agent_name = record.get("agent")
                    agent_id = get_agent_id_by_name(conn, agent_name)
                    
                    if not agent_id:
                        stats["skipped"] += 1
                        continue
                    
                    source_id_text = record.get("source_id")
                    source_db_id = get_source_id(conn, source_id_text)
                    
                    if not source_db_id:
                        stats["skipped"] += 1
                        continue
                    
                    conn.execute("""
                        INSERT INTO uncertainty_register (
                            source_id, agent_id, uncertainty_text, impact_level, status
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        source_db_id,
                        agent_id,
                        record.get("uncertainty", ""),
                        record.get("impact", "medio"),
                        record.get("status", "aberta"),
                    ))
                    stats["imported"] += 1
                
                except (json.JSONDecodeError, Exception) as e:
                    stats["errors"] += 1
    
    except IOError as e:
        print(f"✗ Erro ao ler {path.name}: {e}")
    
    return stats


def main() -> int:
    """Executa importação."""
    print("=" * 70)
    print("Hermes v0.4.2 — Importação de JSONL para SQLite")
    print("=" * 70)
    print()
    
    # Verifica arquivo
    if not DB_PATH.exists():
        print(f"✗ Banco SQLite não encontrado: {DB_PATH}")
        print("  Execute primeiro: python3 scripts/init_db.py")
        return 1
    
    if not KNOWLEDGE_DIR.exists():
        print(f"⚠ Diretório ~/.hermes/knowledge não encontrado")
        print("  Ciclo 001 não foi executado?")
        return 1
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Valida que agentes existem
        cur = conn.execute("SELECT COUNT(*) FROM agents")
        agent_count = cur.fetchone()[0]
        if agent_count == 0:
            print("✗ Nenhum agente encontrado no banco")
            return 1
        
        print(f"✓ Banco aberto, {agent_count} agentes encontrados")
        print()
        
        # Importa cada arquivo
        total_stats = {"read": 0, "imported": 0, "skipped": 0, "errors": 0}
        
        print("1. Importando sources...")
        stats = import_sources_ledger(conn, KNOWLEDGE_DIR / "sources_ledger.jsonl")
        print(f"   Lidas: {stats['read']}, importadas: {stats['imported']}, "
              f"puladas: {stats['skipped']}, erros: {stats['errors']}")
        for k in total_stats:
            total_stats[k] += stats[k]
        print()
        
        print("2. Importando claims...")
        stats = import_claims_ledger(conn, KNOWLEDGE_DIR / "claims_ledger.jsonl")
        print(f"   Lidas: {stats['read']}, importadas: {stats['imported']}, "
              f"puladas: {stats['skipped']}, erros: {stats['errors']}")
        for k in total_stats:
            total_stats[k] += stats[k]
        print()
        
        print("3. Importando conceitos...")
        stats = import_concepts_ledger(conn, KNOWLEDGE_DIR / "concepts_ledger.jsonl")
        print(f"   Lidas: {stats['read']}, importadas: {stats['imported']}, "
              f"puladas: {stats['skipped']}, erros: {stats['errors']}")
        for k in total_stats:
            total_stats[k] += stats[k]
        print()
        
        print("4. Importando contradições...")
        stats = import_contradictions_ledger(conn, KNOWLEDGE_DIR / "contradictions_ledger.jsonl")
        print(f"   Lidas: {stats['read']}, importadas: {stats['imported']}, "
              f"puladas: {stats['skipped']}, erros: {stats['errors']}")
        for k in total_stats:
            total_stats[k] += stats[k]
        print()
        
        print("5. Importando learning events...")
        stats = import_learning_log(conn, KNOWLEDGE_DIR / "agent_learning_log.jsonl")
        print(f"   Lidas: {stats['read']}, importadas: {stats['imported']}, "
              f"puladas: {stats['skipped']}, erros: {stats['errors']}")
        for k in total_stats:
            total_stats[k] += stats[k]
        print()
        
        print("6. Importando exames...")
        stats = import_exams(conn, KNOWLEDGE_DIR / "agent_exams.jsonl")
        print(f"   Lidas: {stats['read']}, importadas: {stats['imported']}, "
              f"puladas: {stats['skipped']}, erros: {stats['errors']}")
        for k in total_stats:
            total_stats[k] += stats[k]
        print()
        
        print("7. Importando incertezas...")
        stats = import_uncertainty_register(conn, KNOWLEDGE_DIR / "uncertainty_register.jsonl")
        print(f"   Lidas: {stats['read']}, importadas: {stats['imported']}, "
              f"puladas: {stats['skipped']}, erros: {stats['errors']}")
        for k in total_stats:
            total_stats[k] += stats[k]
        print()
        
        # Commit
        conn.commit()
        
        print("=" * 70)
        print(f"Resumo: {total_stats['imported']} registros importados, "
              f"{total_stats['skipped']} pulados, {total_stats['errors']} erros")
        print("=" * 70)
        
        conn.close()
        return 0
    
    except Exception as e:
        print(f"✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
