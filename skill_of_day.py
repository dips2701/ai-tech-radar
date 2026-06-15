import ollama
import sqlite3
from database import DB_PATH
from datetime import date

def get_skill_of_day():
    """Analyze today's updates and suggest the most important skill to learn."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, summary, ai_summary
        FROM updates
        ORDER BY id DESC
        LIMIT 20
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No updates available to analyze."
    
    context = "\n\n".join([
        f"Title: {row[0]}\nSummary: {row[2] or row[1]}"
        for row in rows
    ])
    
    prompt = f"""You are an AI industry advisor.

Today's AI Updates:
{context}

Based on these updates, what is the SINGLE most important skill 
an AI engineer should learn today to stay competitive?

Format your response as:

SKILL:
[skill name]

REASON:
[2-3 sentences explaining why]

EXAMPLES:
[1-2 specific tools or techniques to learn]
"""

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response["message"]["content"]


def parse_skill_output(raw_output):
    """Parse skill output into a dict."""
    sections = {"SKILL": "", "REASON": "", "EXAMPLES": ""}
    current = None

    for line in raw_output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        upper = stripped.upper()
        for key in sections:
            if upper.startswith(key + ":"):
                current = key
                sections[key] = stripped.split(":", 1)[1].strip()
                break
        else:
            if current:
                if sections[current]:
                    sections[current] += "\n" + stripped
                else:
                    sections[current] = stripped

    return sections


if __name__ == "__main__":
    print("Analyzing today's updates...")
    raw = get_skill_of_day()
    print("\n" + "=" * 60)
    print("SKILL OF THE DAY (RAW):")
    print("=" * 60)
    print(raw)
    
    print("\n" + "=" * 60)
    print("PARSED:")
    print("=" * 60)
    parsed = parse_skill_output(raw)
    for key, value in parsed.items():
        print(f"\n{key}:")
        print(value)
