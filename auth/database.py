import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("users.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        password_salt TEXT,
        provider TEXT NOT NULL DEFAULT 'local',
        accepted_terms INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email.lower().strip(),),
    )

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def create_user(email, password_hash, password_salt, provider, accepted_terms):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (email, password_hash, password_salt, provider, accepted_terms, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            email.lower().strip(),
            password_hash,
            password_salt,
            provider,
            1 if accepted_terms else 0,
            datetime.utcnow().isoformat(),
        ),
    )

    conn.commit()
    conn.close()
