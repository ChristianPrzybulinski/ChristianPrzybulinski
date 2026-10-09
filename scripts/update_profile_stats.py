#!/usr/bin/env python3
"""Refresh GitHub activity cards with a token supplied by the workflow secret."""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

OWNER = "ChristianPrzybulinski"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
TOKEN = os.environ["PROFILE_STATS_TOKEN"]
YEAR = dt.date.today().year

def get_json(url):
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def search(query):
    url = "https://api.github.com/search/issues?" + urllib.parse.urlencode({"q": query, "per_page": 1})
    return int(get_json(url)["total_count"])

def owned_projects():
    repos = get_json("https://api.github.com/user/repos?affiliation=owner&visibility=all&per_page=100")
    return sum(1 for repo in repos if not repo["fork"])

def card(filename, label, value):
    today = dt.date.today().isoformat()
    title = f"{value} {label.lower()}. Snapshot {today}."
    text = f'''<svg xmlns="http://www.w3.org/2000/svg" width="230" height="108" viewBox="0 0 230 108" role="img" aria-labelledby="title"><title id="title">{title}</title><defs><radialGradient id="bg"><stop stop-color="#111e32"/><stop offset="1" stop-color="#080d18"/></radialGradient></defs><rect width="230" height="108" rx="3" fill="url(#bg)"/><path d="M20 10H210l10 10V88l-10 10H20l-10-10V20Z" fill="none" stroke="#52647b" stroke-width=".8"/><text x="115" y="36" text-anchor="middle" font-family="Georgia, Times New Roman, serif" font-size="17" fill="#9eafc3">{label}</text><text x="115" y="77" text-anchor="middle" font-family="Georgia, Times New Roman, serif" font-size="40" fill="#e6e8e5">{value}</text><path d="M84 90h62" stroke="#52647b"/></svg>\n'''
    (ASSETS / filename).write_text(text)

def main():
    commits = search(f"author:{OWNER} author-date:{YEAR}-01-01..{YEAR}-12-31")
    prs = search(f"author:{OWNER} is:pr created:{YEAR}-01-01..{YEAR}-12-31")
    projects = owned_projects()
    card("github-commits.svg", "Indexed commits", commits)
    card("github-prs.svg", "PRs opened", prs)
    card("github-projects.svg", "Owned projects", projects)

if __name__ == "__main__":
    main()
