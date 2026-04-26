#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MAX_PUBLIC_ASSET_BYTES = 5 * 1024 * 1024

PUBLIC_PAGES = [
    ROOT / "index.html",
    ROOT / "artifacts" / "index.html",
    ROOT / "lore" / "index.html",
    ROOT / "press" / "index.html",
    ROOT / "threshold" / "index.html",
    *sorted((ROOT / "sisters").glob("*.html")),
]

DRAFT_PAGES = [
    ROOT / "ghost_orgy_cinematic_sequence.html",
    ROOT / "ghost_orgy_hero_rewrite.html",
    ROOT / "ghost_orgy_orchard_reentry.html",
]

REQUIRED_PATTERNS = [
    ("<title>", re.compile(r"<title>.*?</title>", re.IGNORECASE | re.DOTALL)),
    ('meta name="description"', re.compile(r'<meta[^>]+name=["\']description["\']', re.IGNORECASE)),
    ('link rel="canonical"', re.compile(r'<link[^>]+rel=["\']canonical["\']', re.IGNORECASE)),
    ('link rel="manifest"', re.compile(r'<link[^>]+rel=["\']manifest["\']', re.IGNORECASE)),
    ('meta property="og:title"', re.compile(r'<meta[^>]+property=["\']og:title["\']', re.IGNORECASE)),
    ('meta property="og:description"', re.compile(r'<meta[^>]+property=["\']og:description["\']', re.IGNORECASE)),
    ('meta name="twitter:card"', re.compile(r'<meta[^>]+name=["\']twitter:card["\']', re.IGNORECASE)),
]

PLACEHOLDER_SNIPPETS = [
    "YOUR_SOUNDCLOUD_TRACK_URL",
    "TODO",
    "FIXME",
    "Replace the src with your actual",
]

DISALLOWED_PAGE_SNIPPETS = [
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "db.onlinewebfonts.com",
]

PUBLIC_MEDIA_EXTENSIONS = {
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mp4",
    ".png",
    ".webm",
    ".webp",
}

LOCAL_MEDIA_PATTERN = re.compile(
    r"""["']([^"']+\.(?:avif|gif|jpe?g|mp4|png|webm|webp))(?:\?[^"']*)?["']""",
    re.IGNORECASE,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_referenced_assets(page: Path, text: str) -> set[Path]:
    assets: set[Path] = set()

    for match in LOCAL_MEDIA_PATTERN.finditer(text):
        raw_path = match.group(1)
        if "://" in raw_path or raw_path.startswith("data:"):
            continue
        candidate = (page.parent / raw_path).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            continue
        if candidate.is_file():
            assets.add(candidate)

    return assets


def main() -> int:
    errors: list[str] = []
    referenced_assets: set[Path] = set()

    for page in PUBLIC_PAGES:
        text = read_text(page)
        referenced_assets.update(collect_referenced_assets(page, text))
        for label, pattern in REQUIRED_PATTERNS:
            if not pattern.search(text):
                errors.append(f"{page.relative_to(ROOT)} is missing `{label}`.")
        for placeholder in PLACEHOLDER_SNIPPETS:
            if placeholder in text:
                errors.append(f"{page.relative_to(ROOT)} still contains placeholder text `{placeholder}`.")
        for snippet in DISALLOWED_PAGE_SNIPPETS:
            if snippet in text:
                errors.append(f"{page.relative_to(ROOT)} still references external font host `{snippet}`.")

    for draft in DRAFT_PAGES:
        text = read_text(draft)
        if 'meta name="robots" content="noindex, nofollow, noarchive"' not in text:
            errors.append(f"{draft.relative_to(ROOT)} should be marked `noindex, nofollow, noarchive`.")

    if not (ROOT / "404.html").is_file():
        errors.append("404.html is missing.")

    if not (ROOT / "site.webmanifest").is_file():
        errors.append("site.webmanifest is missing.")

    for asset in referenced_assets:
        if asset.suffix.lower() not in PUBLIC_MEDIA_EXTENSIONS:
            continue
        if asset.stat().st_size > MAX_PUBLIC_ASSET_BYTES:
            errors.append(
                f"{asset.relative_to(ROOT)} is larger than {MAX_PUBLIC_ASSET_BYTES // (1024 * 1024)} MiB; optimize it before shipping."
            )

    if errors:
        print("Site QA failed:\n")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Site QA passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
