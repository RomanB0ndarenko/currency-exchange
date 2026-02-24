import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()

print(response)
