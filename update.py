import os
import re
import json
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # например: -1003420069182

CODES = ["USD", "EUR", "PLN", "GBP", "CHF", "CAD", "CZK", "TRY"]

LAST_FILE = "last_update_id.txt"
RATES_FILE = "rates.json"


def load_last_update_id():
    try:
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return None


def save_last_update_id(update_id: int):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(str(update_id))


def load_existing_rates() -> dict:
    try:
        with open(RATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def extract_rates(text: str) -> dict:
    # Понимает:
    # USD🇺🇸/🇺🇦43.10/43.40
    # EUR 🇪🇺 51.10/51.50
    # и т.п. (флаги/эмодзи/пробелы не мешают)
    found = {}
    for cur in CODES:
        m = re.search(rf"{cur}.*?([0-9]+(?:\.[0-9]+)?)/([0-9]+(?:\.[0-9]+)?)", text)
        if m:
            found[cur] = {"buy": float(m.group(1)), "sell": float(m.group(2))}
    return found


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

    newest_update_id = updates[-1]["update_id"]
    save_last_update_id(newest_update_id)

    # Ищем самый свежий пост из нужного канала
    for u in reversed(updates):
        msg = u.get("channel_post") or u.get("message")
        if not msg:
            continue

        chat = msg.get("chat", {})
        if str(chat.get("id")) != str(CHAT_ID):
            continue

        text = msg.get("text") or ""
        new_rates = extract_rates(text)

        # Если в посте нет ни одной валюты — ничего не меняем
        if not new_rates:
            print("No parsable rates in latest channel post.")
            return

        # ✅ Главное: частичное обновление (merge)
        existing = load_existing_rates()
        existing.update(new_rates)

        # (необязательно) гарантируем порядок/наличие ключей
        merged = {}
        for cur in CODES:
            if cur in existing:
                merged[cur] = existing[cur]

        with open(RATES_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        print("Rates merged (partial update).")
        return

    print("No channel posts found in updates.")


if __name__ == "__main__":
    main()
