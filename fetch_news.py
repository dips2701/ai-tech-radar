import feedparser
import sqlite3
from database import DB_PATH, create_table, update_summary_fields
from sources.arxiv_fetcher import fetch_arxiv_papers
from ai_enrichment import enrich_update, parse_enrichment

RSS_FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml"
}

CATEGORY_MAP = {
    "OpenAI": "News",
    "Google AI": "Research",
    "Hugging Face": "Tools",
}


def get_summary(entry):
    summary = entry.get("summary", "")
    description = entry.get("description", "")
    content = ""

    if "content" in entry:
        content = entry.content[0].value

    return (summary or description or content or entry.title)[:500]


def get_reason(title):
    title_lower = title.lower()
    if "agent" in title_lower:
        return "Useful for building AI agents."
    elif "llm" in title_lower:
        return "Relevant for LLM applications."
    else:
        return "General AI industry update."


def insert_update(cursor, title, source, category, url, summary, published, why_it_matters):
    cursor.execute(
        "SELECT id FROM updates WHERE url = ?",
        (url,)
    )
    if cursor.fetchone():
        return None

    cursor.execute("""
    INSERT INTO updates 
    (title, source, category, url, summary, published, why_it_matters)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, source, category, url, summary, published, why_it_matters))
    
    article_id = cursor.lastrowid
    return article_id


def fetch_and_save_news():
    create_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for source, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title = entry.title
            url = entry.link
            published = entry.get("published", "")
            category = CATEGORY_MAP.get(source, "News")
            why_it_matters = get_reason(title)

            summary = get_summary(entry)
            article_id = insert_update(cursor, title, source, category, url, summary, published, why_it_matters)
            
            if article_id:
                conn.commit()
                conn.close()
                
                try:
                    raw = enrich_update(title, summary)
                    fields = parse_enrichment(raw)
                    update_summary_fields(
                        article_id,
                        fields["SUMMARY"],
                        fields["WHY_IT_MATTERS"],
                        fields["ACTION"],
                        fields["IMPACT"]
                    )
                    print(f"Enriched: {title}")
                except Exception as e:
                    print(f"Enrichment failed for {title}: {e}")
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()

    for paper in fetch_arxiv_papers():
        article_id = insert_update(
            cursor,
            paper["title"],
            paper["source"],
            paper["category"],
            paper["url"],
            paper["summary"],
            paper["published"],
            paper.get("why_it_matters", get_reason(paper["title"]))
        )
        
        if article_id:
            conn.commit()
            conn.close()
            
            try:
                raw = enrich_update(paper["title"], paper["summary"])
                fields = parse_enrichment(raw)
                update_summary_fields(
                    article_id,
                    fields["SUMMARY"],
                    fields["WHY_IT_MATTERS"],
                    fields["ACTION"],
                    fields["IMPACT"]
                )
                print(f"Enriched: {paper['title']}")
            except Exception as e:
                print(f"Enrichment failed for {paper['title']}: {e}")
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fetch_and_save_news()
    print("News saved successfully.")