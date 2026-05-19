"""Tiny Flask server that renders the NYT homepage with archive.ph links.

Run: `.venv/bin/python app.py` then open http://localhost:8999
Bound to 0.0.0.0 — reachable on the LAN at http://<this-host-ip>:8999

Each card links to https://archive.ph/<nyt-url>. If archive.ph has a snapshot
it shows it; otherwise it shows its search/save page. A small "NYT original"
link is provided as a fallback.
"""
from __future__ import annotations

import time
from urllib.parse import quote

from flask import Flask, render_template

from scraper import fetch_homepage_articles

PAGE_CACHE_TTL_SECONDS = 5 * 60

app = Flask(__name__)

_cache: dict = {"ts": 0.0, "articles": []}


def _archive_url(nyt_url: str) -> str:
    return f"https://archive.ph/{quote(nyt_url, safe=':/?&=')}"


@app.route("/")
def index():
    now = time.time()
    if now - _cache["ts"] > PAGE_CACHE_TTL_SECONDS or not _cache["articles"]:
        articles = fetch_homepage_articles()
        _cache["ts"] = now
        _cache["articles"] = articles
        fetched_at = now
    else:
        articles = _cache["articles"]
        fetched_at = _cache["ts"]

    return render_template(
        "index.html",
        articles=articles,
        archive_url=_archive_url,
        fetched_at=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(fetched_at)),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8999, debug=False)
