"""Build a static snapshot of the page into docs/ for GitHub Pages.

Run: `.venv/bin/python build_pages.py`
Fetches the NYT HomePage RSS feed once and renders the same template the
Flask app serves, with relative asset paths so it works under a project
Pages URL (https://<user>.github.io/timesbuilder/).
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

from flask import render_template

from app import app, _archive_url
from scraper import fetch_homepage_articles

DOCS = Path(__file__).parent / "docs"


def main() -> None:
    articles = fetch_homepage_articles()
    fetched_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with app.test_request_context():
        html = render_template(
            "index.html",
            articles=articles,
            archive_url=_archive_url,
            fetched_at=fetched_at,
        )

    # url_for emits /static/... (absolute); Pages serves under a subpath.
    html = html.replace('href="/static/', 'href="static/')

    DOCS.mkdir(exist_ok=True)
    (DOCS / "static").mkdir(exist_ok=True)
    shutil.copy(Path(__file__).parent / "static" / "style.css", DOCS / "static" / "style.css")
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote {DOCS / 'index.html'} ({len(articles)} articles, fetched {fetched_at})")


if __name__ == "__main__":
    main()
