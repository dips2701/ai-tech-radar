import os
import sqlite3
import requests
from dotenv import load_dotenv
from database import DB_PATH
from skill_of_day import get_skill_of_day, parse_skill_output

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=payload)
    return response.json()


def get_top_updates(limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, source, category, url, summary, impact
        FROM updates
        ORDER BY impact DESC, id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def build_daily_message():
    rows = get_top_updates()

    if not rows:
        return "No AI updates found today."

    message = "🚀 <b>AI Tech Radar</b>\n\n"

    for i, row in enumerate(rows, start=1):
        title, source, category, url, summary, impact = row

        short_summary = summary[:250] if summary else "No summary available."

        message += f"<b>{i}. {title}</b>\n"
        message += f"Source: {source} | Category: {category}\n"
        if impact and str(impact).isdigit():
            message += f"Impact: {impact}/10\n"
        else:
            message += "Impact: Not rated\n"
        message += f"{short_summary}...\n"
        message += f"<a href='{url}'>Read more</a>\n\n"

    try:
        message += "\n" + "=" * 40 + "\n\n"
        message += "🎯 <b>Skill of the Day</b>\n\n"
        raw = get_skill_of_day()
        parsed = parse_skill_output(raw)
        
        if parsed["SKILL"]:
            message += f"<b>{parsed['SKILL']}</b>\n"
        if parsed["REASON"]:
            message += f"{parsed['REASON']}\n\n"
        if parsed["EXAMPLES"]:
            message += f"<b>Learn:</b> {parsed['EXAMPLES']}\n"
    except Exception as e:
        print(f"⚠ Skill of the Day failed: {e}")

    return message


if __name__ == "__main__":
    msg = build_daily_message()
    result = send_telegram_message(msg)
    print(result)