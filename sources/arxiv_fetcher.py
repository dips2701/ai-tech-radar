import feedparser
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database import DB_PATH, create_table

ARXIV_FEEDS = {
    "cs.AI": "https://export.arxiv.org/rss/cs.AI",
    "cs.LG": "https://export.arxiv.org/rss/cs.LG",
    "cs.CL": "https://export.arxiv.org/rss/cs.CL",
}


def get_summary(entry):
    summary = entry.get("summary", "")
    description = entry.get("description", "")
    content = ""

    if "content" in entry:
        content = entry.content[0].value

    return (summary or description or content or entry.title)[:700]


def fetch_arxiv_papers(limit=5):
    papers = []

    for category in ARXIV_FEEDS:
        feed = feedparser.parse(ARXIV_FEEDS[category])

        for entry in feed.entries[:limit]:
            published = entry.get("published", "") or entry.get("updated", "")
            papers.append(
                {
                    "title": entry.title,
                    "url": entry.link,
                    "summary": get_summary(entry),
                    "source": "arXiv",
                    "category": "Research",
                    "published": published,
                    "why_it_matters": (
                        "Useful for building AI agents." if "agent" in entry.title.lower()
                        else "Relevant for LLM applications." if "llm" in entry.title.lower()
                        else "General AI industry update."
                    ),
                }
            )

    return papers


if __name__ == "__main__":
    create_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    papers = fetch_arxiv_papers()

    saved = 0
    for paper in papers:
        cursor.execute("SELECT id FROM updates WHERE url=?", (paper["url"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO updates
                (title, source, category, url, summary, published, why_it_matters)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                paper["title"],
                paper["source"],
                paper["category"],
                paper["url"],
                paper["summary"],
                paper["published"],
                paper["why_it_matters"],
            ))
            saved += 1

    conn.commit()
    conn.close()
    print(f"Saved {saved} new arXiv papers.")