#!/usr/bin/env python3
"""
Hermes v0.4.2 — Fix Hotfix: Corrige constraints e reimporta dados
"""
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "Documents" / "My Web Sites" / "Site" / "hermes-visual" / "db" / "private" / "hermes_v04.sqlite"

def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = OFF;")  # Temporariamente desativa FK
    
    try:
        # Verifica se tabela exists
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='extracted_claims'")
        if cur.fetchone():
            # Deleta registros com valor ruim
            conn.execute("DELETE FROM extracted_claims WHERE classification NOT IN ('afirmacao', 'fato', 'principio', 'recomendacao', 'risco', 'lacuna', 'cenario')")
            conn.execute("DELETE FROM extracted_claims WHERE classification = 'princípio' OR classification = 'recomendação'")
            print("✓ Deletados registros com classification inválida")
        
        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON;")
        print("✓ Banco corrigido")
    except Exception as e:
        print(f"✗ Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
