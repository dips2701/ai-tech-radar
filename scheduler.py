import schedule
import time
from fetch_news import fetch_news
from database import initialize_database


def refresh_news():
    initialize_database()
    articles = fetch_news()
    print(f"Fetched {len(articles)} articles")


def start_scheduler():
    schedule.every(1).hours.do(refresh_news)
    refresh_news()
    while True:
        schedule.run_pending()
        time.sleep(1)
