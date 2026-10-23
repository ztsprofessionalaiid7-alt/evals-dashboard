import sqlite3
from datetime import datetime, timezone

DB = "logs.db"

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS llm_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, model TEXT, prompt_version TEXT,
            input_text TEXT, output_text TEXT,
            prompt_tokens INTEGER, completion_tokens INTEGER,
            latency_ms INTEGER, error TEXT
        )""")

def log_call(model, prompt_version, input_text, output_text,
             prompt_tokens, completion_tokens, latency_ms, error=None):
    with sqlite3.connect(DB) as c:
        c.execute("""INSERT INTO llm_logs
            (ts, model, prompt_version, input_text, output_text,
             prompt_tokens, completion_tokens, latency_ms, error)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (datetime.now(timezone.utc).isoformat(), model, prompt_version,
             input_text, output_text, prompt_tokens, completion_tokens,
             latency_ms, error))