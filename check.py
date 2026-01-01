import os
import requests

# Load .env for local testing (ignored in CI if missing)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


API_URL = "https://api.deerpark.fredbooking.com/api/quote"
DATES = ["2026-01-03"]
TIME_HHMM = "09:50"


def send_telegram(message: str):
    bot = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{bot}/sendMessage"
    r = requests.post(
        url,
        json={"chat_id": chat_id, "text": message},
        timeout=20,
    )
    r.raise_for_status()


def fetch_available(date_yyyy_mm_dd: str) -> bool | None:
    token = os.environ["DEERPARK_BEARER_TOKEN"]

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json; charset=utf-8",
        "origin": "https://booking.deerparkheights.co.nz",
        "referer": "https://booking.deerparkheights.co.nz/",
        "user-agent": "Mozilla/5.0 (monitor)",
    }

    # If API requires "YYYY-MM-DDHH:MM", change this line accordingly
    payload = {"from": f"{date_yyyy_mm_dd}{TIME_HHMM}"}

    r = requests.post(API_URL, headers=headers, json=payload, timeout=25)

    # Ignore transient errors
    if r.status_code in (429, 500, 502, 503, 504):
        return None

    r.raise_for_status()
    data = r.json()

    quotes = data.get("quotes") or []
    if not quotes:
        return None

    return bool(quotes[0].get("available"))


def main():
    availabilities = []

    for d in DATES:
        avail = fetch_available(d)
        res = f"{d}: available={avail}"
        print(res)

        if avail:
            availabilities.append(res)


    if availabilities:
        joined = "\n".join(availabilities)
        send_telegram(
            f"✅ Deerpark available!\nDate: {joined}"
        )


if __name__ == "__main__":
    main()
