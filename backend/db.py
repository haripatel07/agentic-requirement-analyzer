"""Simple SQLite persistence for runs."""
import sqlite3
import json
from datetime import datetime
from typing import Optional

DB_PATH = "./runs.db"


def init_db(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            created_at TEXT,
            report_json TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_run(filename: str, report: dict, path: str = DB_PATH) -> int:
    conn = sqlite3.connect(path)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO runs (filename, created_at, report_json) VALUES (?, ?, ?)", (filename, now, json.dumps(report)))
    conn.commit()
    run_id = c.lastrowid
    conn.close()
    return run_id


def list_runs(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT id, filename, created_at FROM runs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "filename": r[1], "created_at": r[2]} for r in rows]


def get_run(run_id: int, path: str = DB_PATH) -> Optional[dict]:
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT id, filename, created_at, report_json FROM runs WHERE id = ?", (run_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "filename": row[1], "created_at": row[2], "report": json.loads(row[3])}


if __name__ == "__main__":
    init_db()
    print(list_runs())
