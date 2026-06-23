#!/usr/bin/env python3
"""Create a local timestamped backup of the Hermes SQLite database."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "private" / "hermes_v04.sqlite"
BACKUP_DIR = ROOT / "backups"


def main() -> None:
    if not DB_PATH.exists():
        print(f"BLOQUEADO: banco não encontrado em {DB_PATH}")
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = BACKUP_DIR / f"hermes_v04-{stamp}.sqlite"
    shutil.copy2(DB_PATH, target)
    print(f"Backup local criado: {target}")


if __name__ == "__main__":
    main()
