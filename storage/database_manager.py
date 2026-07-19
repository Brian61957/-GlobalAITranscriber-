import sqlite3

DB_NAME = "global_ai_transcriber.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        date TEXT,
        notes TEXT,
        status TEXT,
        language TEXT,
        confidence REAL
    )
    """)

    conn.commit()
    conn.close()