from fetch_news import fetch_and_save_news
from sources.arxiv_fetcher import fetch_arxiv_papers
from sources.github import fetch_github_repos
from telegram_bot import build_daily_message, send_telegram_message

def run_daily_pipeline():
    print("Fetching AI news...")
    fetch_and_save_news()

    print("Fetching arXiv papers...")
    fetch_arxiv_papers()

    print("Fetching GitHub repos...")
    fetch_github_repos()

    print("Sending Telegram brief...")
    message = build_daily_message()
    result = send_telegram_message(message)

    print("Telegram message sent successfully.")
    print("Daily pipeline completed.")

if __name__ == "__main__":
    run_daily_pipeline()