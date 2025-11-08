import sqlite3

DB_FILE = "queue.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        command TEXT,
        state TEXT,
        attempts INTEGER,
        max_retries INTEGER,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS dlq (
        id TEXT PRIMARY KEY,
        command TEXT,
        failed_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def execute_query(query, params=(), fetch=False):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data