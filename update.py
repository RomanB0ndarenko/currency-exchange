import requests
import re
import json
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()

if not response.get("result"):
    exit()

text = response["result"][-1]["message"]["text"]

patterns = {
    "USD": r"USD.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)",
    "EUR": r"EUR.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)",
    "PLN": r"PLN.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)",
    "GBP": r"GBP.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)",
    "CHF": r"CHF.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)",
    "CAD": r"CAD.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)",
    "CZK": r"CZK.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)",
    "TRY": r"TRY.*?([\d]+(?:\.[\d]+)?)/([\d]+(?:\.[\d]+)?)"
}

rates = {}

for currency, pattern in patterns.items():
    match = re.search(pattern, text)
    if match:
        rates[currency] = {
            "buy": float(match.group(1)),
            "sell": float(match.group(2))
        }

if rates:
    with open("rates.json", "w") as f:
        json.dump(rates, f, indent=4)
