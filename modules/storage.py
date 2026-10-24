import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "resumeframer.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL, role TEXT NOT NULL, created_at TEXT NOT NULL,
            analysis_json TEXT, tailored_resume TEXT, learning_plan TEXT
        )""")
        conn.commit()

def save_application(company, role, analysis_json, tailored_resume, learning_plan):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO applications (company, role, created_at, analysis_json, tailored_resume, learning_plan) VALUES (?, ?, ?, ?, ?, ?)",
            (company, role, datetime.now().isoformat(timespec="seconds"), analysis_json, tailored_resume, learning_plan)
        )
        conn.commit()

def list_applications():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT id, company, role, created_at FROM applications ORDER BY id DESC").fetchall()
    return [{"ID": r[0], "Company": r[1], "Role": r[2], "Created": r[3]} for r in rows]
