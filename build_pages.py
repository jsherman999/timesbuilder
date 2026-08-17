"""Build the static shell and assets into docs/ for GitHub Pages.

Run: `.venv/bin/python build_pages.py`
The generated page fetches the NYT HomePage RSS feed in the visitor's browser,
so the page can update on every load instead of committing an article snapshot.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from flask import render_template

from app import app, _archive_url

DOCS = Path(__file__).parent / "docs"


def main() -> None:
    with app.test_request_context():
        html = render_template(
            "index.html",
            articles=[],
            archive_url=_archive_url,
            fetched_at="",
            client_render=True,
        )

    # url_for emits /static/... (absolute); Pages serves under a subpath.
    html = html.replace('href="/static/', 'href="static/')
    html = html.replace('src="/static/', 'src="static/')
    html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"

    DOCS.mkdir(exist_ok=True)
    (DOCS / "static").mkdir(exist_ok=True)
    shutil.copy(Path(__file__).parent / "static" / "style.css", DOCS / "static" / "style.css")
    shutil.copy(Path(__file__).parent / "static" / "app.js", DOCS / "static" / "app.js")
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote {DOCS / 'index.html'} (live RSS shell)")


if __name__ == "__main__":
    main()
