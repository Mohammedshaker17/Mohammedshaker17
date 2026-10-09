"""Scrape the public contribution calendar and save it to data/contributions.json."""
import json
import re
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Mohammedshaker17"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def main():
    html = requests.get(
        f"https://github.com/users/{USERNAME}/contributions",
        headers={"User-Agent": "profile-readme-bot"},
        timeout=30,
    ).text
    soup = BeautifulSoup(html, "html.parser")

    # Each day's count lives in a <tool-tip for="day-id"> element.
    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"(\d+|No) contribution", tip.get_text(strip=True))
        if m:
            counts[tip.get("for")] = 0 if m.group(1) == "No" else int(m.group(1))

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": counts.get(td.get("id"), 0),
        })
    days.sort(key=lambda d: d["date"])

    # Streaks
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        elif current == 0 and d["date"] == date.today().isoformat():
            continue  # today not done yet doesn't break the streak
        else:
            break

    best = max(days, key=lambda d: d["count"]) if days else None
    stats = {
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"stats": stats, "days": days}, indent=1))
    print(f"saved {len(days)} days, {stats['total']} contributions")


if __name__ == "__main__":
    main()
