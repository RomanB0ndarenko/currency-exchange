import os
import re
import json
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # -1003420069182

CODES = ["USD", "EUR", "PLN", "GBP", "CHF", "CAD", "CZK", "TRY"]

LAST_FILE = "last_update_id.txt"

def load_last_update_id():
    try:
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return None

def save_last_update_id(update_id: int):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(str(update_id))

def extract_rates(text: str) -> dict:
    rates = {}
    for cur in CODES:
        # ловит:
        # USD🇺🇸/🇺🇦43.10/43.40
        # USD 🇺🇸 43.10/43.40
        m = re.search(rf"{cur}.*?([0-9]+(?:\.[0-9]+)?)/([0-9]+(?:\.[0-9]+)?)", text)
        if m:
            rates[cur] = {"buy": float(m.group(1)), "sell": float(m.group(2))}
    return rates

def main():
    if not TOKEN:
        raise SystemExit("Missing TELEGRAM_TOKEN")
    if not CHAT_ID:
        raise SystemExit("Missing TELEGRAM_CHAT_ID")

    last_id = load_last_update_id()
    params = {"timeout": 0}
    if last_id is not None:
        params["offset"] = last_id + 1

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    resp = requests.get(url, params=params, timeout=30).json()
    if not resp.get("ok"):
        raise SystemExit(f"Telegram error: {resp}")

    updates = resp.get("result", [])
    if not updates:
        print("No updates yet.")
        return

    # сохраняем newest update_id, чтобы не парсить одно и то же
    newest_update_id = updates[-1]["update_id"]
    save_last_update_id(newest_update_id)

    # ищем самый свежий пост из нужного канала, где есть курсы
    for u in reversed(updates):
        msg = u.get("channel_post") or u.get("message")
        if not msg:
            continue

        chat = msg.get("chat", {})
        if str(chat.get("id")) != str(CHAT_ID):
            continue

        text = msg.get("text") or ""
        rates = extract_rates(text)
        if rates:
            with open("rates.json", "w", encoding="utf-8") as f:
                json.dump(rates, f, ensure_ascii=False, indent=2)
            print("Rates updated.")
            return

    print("Updates received, but no parsable rates found.")

if __name__ == "__main__":
    main()
