#!/usr/bin/env python3
"""Initialize Hermes v0.4-alpha SQLite database using stdlib only."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "db" / "private"
DB_PATH = DB_DIR / "hermes_v04.sqlite"
SCHEMA_PATH = ROOT / "db" / "schema.sql"
SEED_PATH = ROOT / "db" / "seeds" / "001_initial_seed.sql"

REQUIRED_DIRS = [
    ROOT / "app",
    ROOT / "web",
    ROOT / "db",
    DB_DIR,
    ROOT / "db" / "seeds",
    ROOT / "assets" / "logo",
    ROOT / "assets" / "avatars",
    ROOT / "assets" / "icons",
    ROOT / "docs",
    ROOT / "exports" / "public",
    ROOT / "exports" / "private",
    ROOT / "scripts",
    ROOT / "backups",
]


def ensure_dirs() -> None:
    for path in REQUIRED_DIRS:
        path.mkdir(parents=True, exist_ok=True)


def read_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {path}")
    return path.read_text(encoding="utf-8")


def init_db(force: bool = False) -> None:
    ensure_dirs()

    if DB_PATH.exists() and not force:
        print(f"BLOQUEADO: banco já existe em {DB_PATH}")
        print("Use --force para recriar conscientemente.")
        return

    if DB_PATH.exists() and force:
        DB_PATH.unlink()

    schema_sql = read_sql(SCHEMA_PATH)
    seed_sql = read_sql(SEED_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)
        conn.executescript(seed_sql)
        conn.commit()

    print("Hermes v0.4-alpha SQLite inicializado com sucesso.")
    print(f"Banco: {DB_PATH}")
    print("Dados: mockados/sanitizados. Nenhuma ação externa executada.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializa o banco SQLite do Hermes v0.4-alpha.")
    parser.add_argument("--force", action="store_true", help="Recria o banco se ele já existir.")
    args = parser.parse_args()
    init_db(force=args.force)


if __name__ == "__main__":
    main()
