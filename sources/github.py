import requests
from bs4 import BeautifulSoup
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database import DB_PATH, create_table

AI_KEYWORDS = [
    "llm",
    "ai",
    "agent",
    "rag",
    "transformer",
    "gpt",
    "claude",
    "gemini",
    "vision",
    "embedding",
    "langchain",
    "llama"
]

def fetch_github_repos():
    create_table()

    url = "https://github.com/trending/python?since=daily"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    repos = soup.find_all("article", class_="Box-row")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for repo in repos[:10]:
        repo_name = repo.h2.text.strip().replace("\n", "").replace(" ", "")
        repo_url = "https://github.com/" + repo_name

        description_tag = repo.find("p")
        summary = description_tag.text.strip() if description_tag else "No description available."

        title = repo_name
        source = "GitHub Trending"
        category = "GitHub"
        published = "Daily Trending"
        impact_score = 6
        why_it_matters = "General AI industry update."
        if "agent" in title.lower():
            why_it_matters = "Useful for building AI agents."
        elif "llm" in title.lower():
            why_it_matters = "Relevant for LLM applications."

        text = f"{title} {summary}".lower()
        if not any(keyword in text for keyword in AI_KEYWORDS):
            continue

        cursor.execute("SELECT id FROM updates WHERE url=?", (repo_url,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("""
                INSERT INTO updates
                (title, source, category, url, summary, published, why_it_matters)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                source,
                category,
                repo_url,
                summary,
                published,
                why_it_matters
            ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fetch_github_repos()
    print("GitHub repos saved successfully.")
    