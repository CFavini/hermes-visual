#!/usr/bin/env python3
"""
Hermes v0.4.2 — Initialize SQLite with v0.4.2 schema

Executa schema original + schema_v042_knowledge.sql.
Seguro para rodar múltiplas vezes (usa CREATE IF NOT EXISTS).

Uso:
  python3 scripts/init_db_v042.py

"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "private" / "hermes_v04.sqlite"
SCHEMA_V1 = PROJECT_ROOT / "db" / "schema.sql"
SCHEMA_V042 = PROJECT_ROOT / "db" / "schema_v042_knowledge.sql"


def main() -> int:
    """Inicializa banco."""
    print("Hermes v0.4.2 — Inicialização do banco de dados")
    print()
    
    # Verifica schema v1
    if not SCHEMA_V1.exists():
        print(f"✗ Schema original não encontrado: {SCHEMA_V1}")
        return 1
    
    if not SCHEMA_V042.exists():
        print(f"✗ Schema v0.4.2 não encontrado: {SCHEMA_V042}")
        return 1
    
    # Cria diretório db/private se não existir
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Executa schema v1
        print(f"Executando {SCHEMA_V1.name}...")
        with SCHEMA_V1.open("r", encoding="utf-8") as f:
            schema_v1 = f.read()
        conn.executescript(schema_v1)
        print("  ✓ Schema v0.4 OK")
        
        # Executa schema v0.4.2
        print(f"Executando {SCHEMA_V042.name}...")
        with SCHEMA_V042.open("r", encoding="utf-8") as f:
            schema_v042 = f.read()
        conn.executescript(schema_v042)
        print("  ✓ Schema v0.4.2 OK")
        
        conn.commit()
        conn.close()
        
        print()
        print(f"✓ Banco inicializado: {DB_PATH}")
        return 0
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
