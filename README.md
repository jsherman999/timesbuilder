# timesbuilder

A tiny Flask app that rebuilds the New York Times homepage as a reader-style
grid where every article links to its **archive.ph** snapshot instead of
nytimes.com. A small "NYT original" link is included as a fallback for
articles that haven't been archived.

## Why

If you want to read NYT content via archive.ph but don't want to copy/paste
URLs one by one, point your browser here and click.

## GitHub Pages

The page is published at
**https://jsherman999.github.io/timesbuilder/**

GitHub Pages serves a small static shell from `docs/`. On each page load,
`static/app.js` fetches the current NYT HomePage RSS feed in the browser and
builds the article grid. The RSS service may itself cache responses briefly,
so "current" means the latest feed version available when the page loads.
Rebuild the shell/assets with `.venv/bin/python build_pages.py` if the template
or styles change; no NYT article snapshot is committed.

## How it works

1. Fetches the NYT HomePage RSS feed (`rss.nytimes.com/.../HomePage.xml`),
   server-side for Flask or client-side for GitHub Pages.
2. Renders each item as a card in a responsive grid (hero + secondary).
3. Each card's primary link is `https://archive.ph/<nyt-url>` — archive.ph
   redirects to the snapshot if one exists, or shows its search page if not.
4. A small "NYT original ›" link on each card goes straight to nytimes.com.
5. The assembled page is cached server-side for 5 minutes; reloads within
   that window are instant.

### What it does *not* do

It does **not** check archive.ph from the server to detect which articles are
archived. archive.ph blocks non-browser clients with a Cloudflare reCAPTCHA
challenge, so per-article "archived vs not archived" badges aren't reliable
from a script. Your browser handles the CF challenge once on first click and
the clearance cookie persists.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then open one of:

- `http://localhost:8999` on this machine
- `http://<this-host-lan-ip>:8999` from anywhere on your LAN

The server binds to `0.0.0.0:8999` with no authentication.

## Files

```
app.py                Flask server, 5-minute page cache, archive.ph URL builder
scraper.py            NYT HomePage RSS → list[Article] with image URLs
build_pages.py        Builds the live RSS shell and assets into docs/
static/app.js         Browser-side RSS fetcher and article-grid renderer
templates/index.html  Reader-style grid template
static/style.css      Typography + responsive 3/2/1-column layout
requirements.txt      Flask, feedparser
```
