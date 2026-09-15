#!/usr/bin/env python3
"""Generate a self-hosted GitHub stats card for the profile README."""

import html
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen


USERNAME = os.environ.get("GITHUB_USERNAME", "chenbin98")
OUTPUT = Path(os.environ.get("STATS_OUTPUT", "stats.svg"))


def github_json(path: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com{path}", headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def compact(value: int) -> str:
    return f"{value:,}"


def card(profile: dict, repos: list[dict]) -> str:
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    values = [
        ("PUBLIC REPOSITORIES", compact(profile.get("public_repos", 0))),
        ("TOTAL STARS", compact(stars)),
        ("FOLLOWERS", compact(profile.get("followers", 0))),
        ("FOLLOWING", compact(profile.get("following", 0))),
    ]
    cells = []
    for index, (label, value) in enumerate(values):
        x = 28 + (index % 2) * 214
        y = 86 + (index // 2) * 62
        cells.append(
            f'<text x="{x}" y="{y}" class="value">{html.escape(value)}</text>'
            f'<text x="{x}" y="{y + 20}" class="label">{html.escape(label)}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="450" height="220" viewBox="0 0 450 220" role="img" aria-labelledby="title desc">
  <title id="title">{html.escape(USERNAME)}'s GitHub stats</title>
  <desc id="desc">A summary of public repositories, stars, followers, and following.</desc>
  <style>
    .card {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
    .title {{ fill: #58a6ff; font: 600 21px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .value {{ fill: #f0f6fc; font: 700 24px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .label {{ fill: #8b949e; font: 10px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; letter-spacing: .7px; }}
  </style>
  <rect class="card" x=".5" y=".5" width="449" height="219" rx="8" />
  <text x="28" y="42" class="title">{html.escape(USERNAME)}'s GitHub Stats</text>
  <line x1="28" y1="58" x2="422" y2="58" stroke="#30363d" />
  {"".join(cells)}
</svg>
'''


def main() -> None:
    profile = github_json(f"/users/{USERNAME}")
    repos = github_json(f"/users/{USERNAME}/repos?per_page=100&type=owner")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(card(profile, repos), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"stats generation failed: {exc}", file=sys.stderr)
        raise
