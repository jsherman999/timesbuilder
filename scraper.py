"""Fetch and parse the NYT HomePage RSS feed."""
from __future__ import annotations

from dataclasses import dataclass

import feedparser

NYT_HOMEPAGE_FEED = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"


@dataclass
class Article:
    title: str
    url: str
    summary: str
    image_url: str | None
    image_credit: str | None
    published: str | None


def _pick_image(entry) -> tuple[str | None, str | None]:
    # feedparser exposes media:content as `media_content` and media:thumbnail as
    # `media_thumbnail`. Prefer the largest media_content image.
    media = getattr(entry, "media_content", None) or []
    best = None
    best_w = -1
    for m in media:
        try:
            w = int(m.get("width", 0))
        except (TypeError, ValueError):
            w = 0
        if m.get("url") and w > best_w:
            best = m["url"]
            best_w = w
    if not best:
        thumbs = getattr(entry, "media_thumbnail", None) or []
        if thumbs:
            best = thumbs[0].get("url")

    credit = None
    credits = getattr(entry, "media_credit", None) or []
    if credits and isinstance(credits, list):
        c = credits[0]
        credit = c.get("content") if isinstance(c, dict) else str(c)

    return best, credit


def fetch_homepage_articles() -> list[Article]:
    parsed = feedparser.parse(NYT_HOMEPAGE_FEED)
    out: list[Article] = []
    for entry in parsed.entries:
        url = entry.get("link")
        title = entry.get("title")
        if not url or not title:
            continue
        image_url, image_credit = _pick_image(entry)
        out.append(
            Article(
                title=title,
                url=url,
                summary=entry.get("summary", ""),
                image_url=image_url,
                image_credit=image_credit,
                published=entry.get("published"),
            )
        )
    return out


if __name__ == "__main__":
    articles = fetch_homepage_articles()
    print(f"Got {len(articles)} articles")
    for a in articles[:3]:
        print(f"- {a.title}\n    {a.url}\n    image={a.image_url}")
