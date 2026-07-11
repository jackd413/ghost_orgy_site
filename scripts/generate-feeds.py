#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
RSS_PATH = ROOT / "feed.xml"
JSON_FEED_PATH = ROOT / "feed.json"
SITE_URL = "https://unholyghost.org"


@dataclass(frozen=True)
class FeedItem:
    title: str
    url: str
    date: str
    summary: str


ITEMS = [
    FeedItem(
        "Salt is available",
        f"{SITE_URL}/salt/",
        "2026-05-29",
        "Salt is the debut album by Ghost Orgy, a Phoenix-based experimental post-hardcore project by Jack Dyer.",
    ),
    FeedItem(
        "Ghost Orgy press kit",
        f"{SITE_URL}/press/",
        "2026-07-05",
        "Press assets, bios, artwork, links, and licensing contact for Ghost Orgy.",
    ),
    FeedItem(
        "Listen to Ghost Orgy",
        f"{SITE_URL}/listen/",
        "2026-07-05",
        "Start with Salt and The Sky That Fears Us, then follow Ghost Orgy on the main listening platforms.",
    ),
]


def rfc_2822(date: str) -> str:
    year, month, day = (int(part) for part in date.split("-"))
    return formatdate(datetime(year, month, day, tzinfo=timezone.utc).timestamp())


def render_rss() -> str:
    latest = max(item.date for item in ITEMS)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        "  <channel>",
        "    <title>Ghost Orgy Updates</title>",
        f"    <link>{SITE_URL}/updates/</link>",
        "    <description>Release notes, press notes, and site updates from Ghost Orgy.</description>",
        "    <language>en-us</language>",
        f"    <lastBuildDate>{rfc_2822(latest)}</lastBuildDate>",
    ]
    for item in sorted(ITEMS, key=lambda entry: entry.date, reverse=True):
        lines.extend(
            [
                "    <item>",
                f"      <title>{escape(item.title)}</title>",
                f"      <link>{escape(item.url)}</link>",
                f"      <guid isPermaLink=\"true\">{escape(item.url)}</guid>",
                f"      <pubDate>{rfc_2822(item.date)}</pubDate>",
                f"      <description>{escape(item.summary)}</description>",
                "    </item>",
            ]
        )
    lines.extend(["  </channel>", "</rss>"])
    return "\n".join(lines) + "\n"


def render_json_feed() -> str:
    payload = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Ghost Orgy Updates",
        "home_page_url": f"{SITE_URL}/",
        "feed_url": f"{SITE_URL}/feed.json",
        "description": "Release notes, press notes, and site updates from Ghost Orgy.",
        "language": "en-US",
        "items": [
            {
                "id": item.url,
                "url": item.url,
                "title": item.title,
                "content_text": item.summary,
                "date_published": f"{item.date}T00:00:00Z",
            }
            for item in sorted(ITEMS, key=lambda entry: entry.date, reverse=True)
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or check Ghost Orgy first-party feeds.")
    parser.add_argument("--check", action="store_true", help="Fail if generated feed files are stale.")
    args = parser.parse_args()

    rss = render_rss()
    json_feed = render_json_feed()
    if args.check:
        stale = []
        if not RSS_PATH.exists() or RSS_PATH.read_text(encoding="utf-8") != rss:
            stale.append("feed.xml")
        if not JSON_FEED_PATH.exists() or JSON_FEED_PATH.read_text(encoding="utf-8") != json_feed:
            stale.append("feed.json")
        if stale:
            print(f"{', '.join(stale)} stale. Run `python scripts/generate-feeds.py`.", file=sys.stderr)
            return 1
        print("Feed check passed.")
        return 0

    RSS_PATH.write_text(rss, encoding="utf-8", newline="\n")
    JSON_FEED_PATH.write_text(json_feed, encoding="utf-8", newline="\n")
    print("feed.xml and feed.json updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
