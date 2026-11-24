"""Fetch a user's contribution calendar for the last year.

    python scripts/fetch_contributions.py Ivanok1990 data/contributions.json

Tries the public calendar page first (no token; includes private counts when
"Private contributions" is enabled on the profile). Falls back to the GraphQL
API when GITHUB_TOKEN is set.
"""
import json
import os
import re
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (profile-readme-updater)"}
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def from_page(login):
    req = urllib.request.Request(f"https://github.com/users/{login}/contributions", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    tips = {}
    for m in re.finditer(r"<tool-tip\b([^>]*)>([^<]*)</tool-tip>", html):
        target = attr(m.group(1), "for")
        if target:
            tips[target] = m.group(2).strip()
    days = []
    for m in re.finditer(r"<td\b[^>]*\bdata-date=[^>]*>", html):
        tag = m.group(0)
        tip = tips.get(attr(tag, "id") or "", "")
        n = re.match(r"(\d+)\s+contribution", tip)
        days.append({"date": attr(tag, "data-date"), "level": int(attr(tag, "data-level") or 0),
                     "count": int(n.group(1)) if n else 0})
    return days


def from_graphql(login, token):
    query = ('query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{'
             'weeks{contributionDays{date contributionCount contributionLevel}}}}}}')
    body = json.dumps({"query": query, "variables": {"l": login}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body,
                                 headers={**UA, "Authorization": f"bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [{"date": d["date"], "count": d["contributionCount"], "level": LEVELS.get(d["contributionLevel"], 0)}
            for w in weeks for d in w["contributionDays"]]


def main(login, out):
    days = []
    try:
        days = from_page(login)
    except Exception as e:  # noqa: BLE001
        print("calendar page failed:", e)
    if len(days) < 300 and os.environ.get("GITHUB_TOKEN"):
        print("falling back to GraphQL")
        days = from_graphql(login, os.environ["GITHUB_TOKEN"])
    if len(days) < 300:
        raise SystemExit(f"unexpected calendar size: {len(days)} days")
    days.sort(key=lambda d: d["date"])
    total = sum(d["count"] for d in days)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"login": login, "total": total, "days": days}, f, indent=1)
    print(f"{login}: {len(days)} days, {total} contributions")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
