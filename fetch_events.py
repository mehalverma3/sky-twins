import csv
import time
from datetime import date, timedelta

import requests

# Wikimedia asks API users to identify themselves; put your GitHub name here
HEADERS = {"User-Agent": "sky-twins-hackathon/0.1 (github.com/mehalverma3)"}
URL = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/{m:02d}/{d:02d}"
MIN_YEAR, MAX_YEAR = 1900, 2025


def fetch_day(month: int, day: int) -> list[dict]:
    for attempt in range(3):
        try:
            r = requests.get(URL.format(m=month, d=day), headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r.json().get("events", [])
        except requests.RequestException as e:
            print(f"  retry {attempt + 1} for {month}/{day}: {e}")
            time.sleep(2)
    return []


def main():
    rows, seen = [], set()
    # 2000 is a leap year, so this covers all 366 month/day combos
    day = date(2000, 1, 1)
    while day.year == 2000:
        events = fetch_day(day.month, day.day)
        for ev in events:
            year = ev.get("year")
            text = (ev.get("text") or "").strip()
            if not year or not text or not (MIN_YEAR <= year <= MAX_YEAR):
                continue
            iso = f"{year:04d}-{day.month:02d}-{day.day:02d}"
            if (iso, text) in seen:
                continue
            seen.add((iso, text))
            pages = ev.get("pages") or []
            page = pages[0] if pages else {}
            rows.append({
                "date": iso,
                "text": text,
                "page_title": page.get("normalizedtitle", ""),
                "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
            })
        print(f"{day.month:02d}-{day.day:02d}: {len(events)} raw, {len(rows)} kept so far")
        time.sleep(0.5)  # be polite to the API
        day += timedelta(days=1)

    with open("events.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "text", "page_title", "url"])
        w.writeheader()
        w.writerows(rows)
    print(f"Done: {len(rows)} events saved to events.csv")


if __name__ == "__main__":
    main()