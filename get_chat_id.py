import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(url)
print(response.json())