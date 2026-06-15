import os
import sqlite3

DB_PATH = "data/ai_news.db"

def create_table():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        source TEXT,
        category TEXT,
        url TEXT UNIQUE,
        summary TEXT,
        published TEXT,
        impact_score INTEGER,
        ai_summary TEXT,
        why_it_matters TEXT,
        action_item TEXT
    )
    """)

    conn.commit()
    conn.close()

def update_summary_fields(url, ai_summary, why_it_matters, action_item, impact_score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE updates
        SET ai_summary = ?,
            why_it_matters = ?,
            action_item = ?,
            impact_score = ?
        WHERE url = ?
    """, (
        ai_summary,
        why_it_matters,
        action_item,
        impact_score,
        url
    ))

    conn.commit()
    conn.close()