from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

import os
from dotenv import load_dotenv
import sqlite3
from database import DB_PATH
from telegram.ext import MessageHandler, filters
import ollama

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        """
🚀 AI Tech Radar

Available commands:

/today
/papers
/repos
"""
    )

async def today(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, impact
        FROM updates
        ORDER BY impact DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()

    conn.close()

    message = "🚀 Today's Top AI Updates\n\n"

    for idx, row in enumerate(rows, start=1):

        title = row[0]
        impact = row[1]

        message += (
            f"{idx}. {title}\n"
            f"Impact: {impact}/10\n\n"
        )

    await update.message.reply_text(message)

async def papers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, url, summary
        FROM updates
        WHERE category = 'Research'
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("No research papers found.")
        return

    message = "📄 Latest AI Research Papers\n\n"

    for idx, row in enumerate(rows, start=1):
        title, url, summary = row
        short_summary = summary[:200] if summary else "No summary available."

        message += (
            f"{idx}. {title}\n"
            f"{short_summary}...\n"
            f"{url}\n\n"
        )

    await update.message.reply_text(message)

async def repos(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, url, summary
        FROM updates
        WHERE category = 'GitHub'
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("No GitHub repos found.")
        return

    message = "💻 Trending AI GitHub Repos\n\n"

    for idx, row in enumerate(rows, start=1):
        title, url, summary = row
        short_summary = summary[:200] if summary else "No description available."

        message += (
            f"{idx}. {title}\n"
            f"{short_summary}...\n"
            f"{url}\n\n"
        )

    await update.message.reply_text(message)


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        question = " ".join(context.args)

        if not question:
            await update.message.reply_text("Usage: /ask your question")
            return

        await update.message.reply_text("Thinking...")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, category, summary
            FROM updates
            ORDER BY id DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()
        conn.close()

        context_text = "\n\n".join(
            [
                f"Title: {title}\nCategory: {category}\nSummary: {summary}"
                for title, category, summary in rows
            ]
        )

        prompt = f"""
You are an AI career and technology analyst.

Use the latest updates below to answer the user's question.

LATEST AI UPDATES:
{context_text}

USER QUESTION:
{question}

Answer clearly and practically.
If the user asks what to learn, suggest 3-5 skills.
Keep it concise.
"""

        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response["message"]["content"]
        await update.message.reply_text(answer[:4000])

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


app = Application.builder().token(
    BOT_TOKEN
).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("today", today)
)

app.add_handler(CommandHandler("papers", papers))
app.add_handler(CommandHandler("repos", repos))
app.add_handler(
    CommandHandler("ask", ask)
)

print("Bot running...")

app.run_polling()
