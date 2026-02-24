import requests
import re
import json
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = "@kursvalutobmin"

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()

if not response["result"]:
    exit()

text = response["result"][-1]["message"]["text"]

patterns = {
    "USD": r"USD.*?([\d.]+)/([\d.]+)",
    "EUR": r"EUR.*?([\d.]+)/([\d.]+)",
    "PLN": r"PLN.*?([\d.]+)/([\d.]+)",
    "GBP": r"GBP.*?([\d.]+)/([\d.]+)",
    "CHF": r"CHF.*?([\d.]+)/([\d.]+)",
    "CAD": r"CAD.*?([\d.]+)/([\d.]+)",
    "CZK": r"CZK.*?([\d.]+)/([\d.]+)",
    "TRY": r"TRY.*?([\d.]+)/([\d.]+)"
}

rates = {}

for currency, pattern in patterns.items():
    match = re.search(pattern, text)
    if match:
        rates[currency] = {
            "buy": float(match.group(1)),
            "sell": float(match.group(2))
        }

with open("rates.json", "w") as f:
    json.dump(rates, f, indent=4)
