#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"


@dataclass(frozen=True)
class SitemapEntry:
    loc: str
    paths: tuple[str, ...]


ENTRIES = [
    SitemapEntry("https://unholyghost.org/", ("index.html",)),
    SitemapEntry("https://shop.unholyghost.org/", ("shop/index.html",)),
    SitemapEntry("https://unholyghost.org/artifacts/", ("artifacts/index.html",)),
    SitemapEntry("https://unholyghost.org/listen/", ("listen/index.html",)),
    SitemapEntry("https://unholyghost.org/licensing/", ("licensing/index.html",)),
    SitemapEntry("https://unholyghost.org/lore/", ("lore/index.html",)),
    SitemapEntry("https://unholyghost.org/nine-sisters/", ("nine-sisters/index.html",)),
    SitemapEntry("https://unholyghost.org/press/", ("press/index.html",)),
    SitemapEntry("https://unholyghost.org/salt/", ("salt/index.html",)),
    SitemapEntry("https://unholyghost.org/shop/", ("shop/index.html",)),
    SitemapEntry("https://unholyghost.org/threshold/", ("threshold/index.html",)),
    SitemapEntry("https://unholyghost.org/updates/", ("updates/index.html",)),
    SitemapEntry("https://unholyghost.org/sisters/limbo.html", ("sisters/limbo.html",)),
    SitemapEntry("https://unholyghost.org/sisters/lust.html", ("sisters/lust.html",)),
    SitemapEntry("https://unholyghost.org/sisters/gluttony.html", ("sisters/gluttony.html",)),
    SitemapEntry("https://unholyghost.org/sisters/greed.html", ("sisters/greed.html",)),
    SitemapEntry("https://unholyghost.org/sisters/wrath.html", ("sisters/wrath.html",)),
    SitemapEntry("https://unholyghost.org/sisters/heresy.html", ("sisters/heresy.html",)),
    SitemapEntry("https://unholyghost.org/sisters/violence.html", ("sisters/violence.html",)),
    SitemapEntry("https://unholyghost.org/sisters/fraud.html", ("sisters/fraud.html",)),
    SitemapEntry("https://unholyghost.org/sisters/treachery.html", ("sisters/treachery.html",)),
]


def git_lastmod(paths: tuple[str, ...]) -> str:
    existing_paths = [path for path in paths if (ROOT / path).exists()]
    if not existing_paths:
        raise FileNotFoundError(f"No sitemap source paths exist for {paths!r}")

    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", *existing_paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git log failed for {existing_paths!r}")

    lastmod = result.stdout.strip().splitlines()
    if not lastmod:
        raise RuntimeError(f"No git history found for sitemap paths {existing_paths!r}")
    return lastmod[0]


def render_sitemap() -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for entry in ENTRIES:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{escape(entry.loc)}</loc>",
                f"    <lastmod>{git_lastmod(entry.paths)}</lastmod>",
                "  </url>",
            ],
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or check sitemap.xml from tracked public pages.")
    parser.add_argument("--check", action="store_true", help="Fail if sitemap.xml is not up to date.")
    args = parser.parse_args()

    generated = render_sitemap()
    if args.check:
        current = SITEMAP.read_text(encoding="utf-8")
        if current != generated:
            print("sitemap.xml is stale. Run `python scripts/generate-sitemap.py`.", file=sys.stderr)
            return 1
        print("Sitemap check passed.")
        return 0

    SITEMAP.write_text(generated, encoding="utf-8", newline="\n")
    print("sitemap.xml updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
