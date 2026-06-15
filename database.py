import sqlite3

DB_PATH = "data/ai_news.db"

def create_table():
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
        saved INTEGER DEFAULT 0,
        why_it_matters TEXT,
        ai_summary TEXT,
        action_item TEXT,
        impact TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(updates)")
    columns = [row[1] for row in cursor.fetchall()]
    if "saved" not in columns:
        cursor.execute("ALTER TABLE updates ADD COLUMN saved INTEGER DEFAULT 0")
    if "why_it_matters" not in columns:
        cursor.execute("ALTER TABLE updates ADD COLUMN why_it_matters TEXT")
    if "ai_summary" not in columns:
        cursor.execute("ALTER TABLE updates ADD COLUMN ai_summary TEXT")
    if "action_item" not in columns:
        cursor.execute("ALTER TABLE updates ADD COLUMN action_item TEXT")
    if "impact" not in columns:
        cursor.execute("ALTER TABLE updates ADD COLUMN impact TEXT")

    conn.commit()
    conn.close()


def update_summary_fields(article_id, ai_summary, why_it_matters, action_item, impact):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE updates
        SET ai_summary = ?, why_it_matters = ?, action_item = ?, impact = ?
        WHERE id = ?
        """,
        (ai_summary, why_it_matters, action_item, impact, article_id)
    )
    conn.commit()
    conn.close()
