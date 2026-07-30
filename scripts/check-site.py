#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
MAX_PUBLIC_ASSET_BYTES = 5 * 1024 * 1024

PUBLIC_PAGES = [
    ROOT / "index.html",
    ROOT / "artifacts" / "index.html",
    ROOT / "licensing" / "index.html",
    ROOT / "listen" / "index.html",
    ROOT / "lore" / "index.html",
    ROOT / "nine-sisters" / "index.html",
    ROOT / "press" / "index.html",
    ROOT / "salt" / "index.html",
    ROOT / "shop" / "index.html",
    ROOT / "threshold" / "index.html",
    ROOT / "updates" / "index.html",
    *sorted((ROOT / "sisters").glob("*.html")),
]

DRAFT_PAGES: list[Path] = []
SITE_PAGES = [
    *PUBLIC_PAGES,
    ROOT / "404.html",
]
LINK_CHECK_PAGES = SITE_PAGES
SOCIAL_PREVIEW_PAGES = SITE_PAGES
SAME_SITE_HOSTS = {"unholyghost.org", "www.unholyghost.org"}

REQUIRED_PATTERNS = [
    ("<title>", re.compile(r"<title>.*?</title>", re.IGNORECASE | re.DOTALL)),
    ('meta name="description"', re.compile(r'<meta[^>]+name=["\']description["\']', re.IGNORECASE)),
    ('link rel="canonical"', re.compile(r'<link[^>]+rel=["\']canonical["\']', re.IGNORECASE)),
    ('link rel="manifest"', re.compile(r'<link[^>]+rel=["\']manifest["\']', re.IGNORECASE)),
    ('meta property="og:title"', re.compile(r'<meta[^>]+property=["\']og:title["\']', re.IGNORECASE)),
    ('meta property="og:description"', re.compile(r'<meta[^>]+property=["\']og:description["\']', re.IGNORECASE)),
    ('meta name="twitter:card"', re.compile(r'<meta[^>]+name=["\']twitter:card["\']', re.IGNORECASE)),
]
REQUIRED_SOCIAL_PREVIEW_FIELDS = [
    "og:image",
    "og:image:alt",
    "twitter:image",
    "twitter:image:alt",
]

DISALLOWED_METADATA_PATTERNS = [
    (
        "generic location-and-genre boilerplate",
        re.compile(r"\bPhoenix(?:-based)?\s+experimental post-hardcore\b", re.IGNORECASE),
    ),
]

PUBLIC_PDF_FILES = [
    ROOT / "press" / "assets" / "ghost-orgy-one-sheet.pdf",
]

DISALLOWED_NON_HTML_COPY_PATTERNS = [
    (
        "editorial governance language",
        re.compile(r"\bcanon(?:ical|ically)?\b", re.IGNORECASE),
    ),
    (
        "retired genre language",
        re.compile(r"\b(?:horrorcore|experimental post-rock)\b", re.IGNORECASE),
    ),
    (
        "generic location-and-genre boilerplate",
        re.compile(r"\bPhoenix(?:-based)?\s+experimental post-hardcore\b", re.IGNORECASE),
    ),
    (
        "internal instruction scaffolding",
        re.compile(
            r"\b(?:routing guidance|source order|guardrails?)\b|"
            r"agent-service|agent-skills|Fourthwall dashboard|source-assets/",
            re.IGNORECASE,
        ),
    ),
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

RETIRED_INTEGRATION_SNIPPETS = [
    "googletagmanager.com",
    "GTM-KQVXQND4",
]

DISALLOWED_COPY_SNIPPETS = [
    "Textural Orbit",
    "Lingua Ignota",
    "Godspeed You! Black Emperor",
    "Sunn O)))",
    "The Caretaker",
    "Burial",
    "horrorcore",
    "experimental post-rock",
    "Pre-save",
]

DISALLOWED_PUBLIC_COPY_PATTERNS = [
    (
        "retired pre-v1.1 Orchard origin",
        re.compile(r"\bsalt opened the orchard\b", re.IGNORECASE),
    ),
    (
        "human-like Orchard agency forbidden by Canon Lock v2.0",
        re.compile(
            r"\bthe orchard\s+(?:prefers|preferred|chooses|chose|sends|sent|plans|planned|"
            r"bargains|resented|resents|celebrates|wants(?!\s+for\s+nothing\s+but\s+souls\b))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "retired Orchard preference language",
        re.compile(r"\bthe orchard's preferred\b", re.IGNORECASE),
    ),
    (
        "retired non-soul fuel language",
        re.compile(
            r"\bprayer becomes fuel\b|\bprayer[^.?!<]*becomes fuel\b|"
            r"\bfear of loss becomes (?:raw fuel|(?:its|the orchard's) nourishment)\b|"
            r"\b(?:residual )?ache[^.?!<]*roots can drink\b|"
            r"\bharvest(?:s|ed|ing)? the energy of broken trust\b|"
            r"\b(?:desire|belief|guilt|betrayal)[^.?!<]{0,80}"
            r"(?:feeds?|fuels?|nourishes?) the orchard\b",
            re.IGNORECASE,
        ),
    ),
    (
        "retired Orchard office or growth language",
        re.compile(
            r"\baccountant of the orchard\b|\baccelerator of orchard expansion\b|"
            r"\bforce rapid growth\b|\bthe orchard stirs\b",
            re.IGNORECASE,
        ),
    ),
    (
        "retired Wrath-as-selective-judgment language",
        re.compile(
            r"\bwrath is the sister of judgment\b|\bselective thermal execution\b|"
            r"\bshe only burns what she means to burn\b|\bguilt made physical\b",
            re.IGNORECASE,
        ),
    ),
    (
        "retired non-human origin language for the Nine",
        re.compile(r"\bnine bodies grown around nine failures of the self\b", re.IGNORECASE),
    ),
    (
        "retired Hell-claim language",
        re.compile(r"\bhuman once,\s*taken by hell\b", re.IGNORECASE),
    ),
    (
        "retired dormant-Orchard model",
        re.compile(r"\bdormant\s+(?:primordial\s+|theological\s+)*orchard\b", re.IGNORECASE),
    ),
    (
        "retired Orchard-awakening model",
        re.compile(
            r"\b(?:their|the nine(?:'s)?)\s+passage\s+awakened\s+the\s+orchard\b|"
            r"\bfirst\s+soul[^.?!<]*\bawakened\s+(?:its|the orchard's)\s+(?:appetite|growth)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "retired Orchard-consciousness model",
        re.compile(r"\bthe orchard is a consciousness\b|\bconsciousness-of-will\b", re.IGNORECASE),
    ),
    (
        "internal storefront directive",
        re.compile(r"\bthe storefront should orbit the album\b", re.IGNORECASE),
    ),
    (
        "internal merch/music directive",
        re.compile(r"\bevery object should send people back to the music\b", re.IGNORECASE),
    ),
    (
        "internal artifact directive",
        re.compile(r"\bartifacts should send people back to the music\b", re.IGNORECASE),
    ),
    (
        "internal shop-object directive",
        re.compile(r"\bshop objects\b[^.?!<]*\bshould read\b", re.IGNORECASE),
    ),
    (
        "repo-approved public copy leak",
        re.compile(r"\brepo-approved\b", re.IGNORECASE),
    ),
    (
        "approved-object public copy leak",
        re.compile(r"\bapproved objects\b", re.IGNORECASE),
    ),
    (
        "public-facing/internal framing leak",
        re.compile(r"\bpublic-facing breach\b|\boperating principle\b", re.IGNORECASE),
    ),
    (
        "internal routing instruction",
        re.compile(
            r"\buse this page as\b|\buse these as\b|\buse the updates route\b|\bshop now routes\b",
            re.IGNORECASE,
        ),
    ),
    (
        "internal handoff/copy-ready language",
        re.compile(
            r"\bcopy-ready\b|\bhandoff\b|\bclean album destination\b|\bsocial verification\b|"
            r"\bpress kit first\b|\bworld second\b",
            re.IGNORECASE,
        ),
    ),
    (
        "internal product-world framing",
        re.compile(r"\bproduct world\b|\bdisconnected storefront\b", re.IGNORECASE),
    ),
]

REQUIRED_DOWNLOADS = [
    ROOT / "press" / "assets" / "ghost-orgy-one-sheet.pdf",
    ROOT / "press" / "assets" / "ghost-orgy-salt-cover-3000.jpg",
    ROOT / "press" / "assets" / "ghost-orgy-wordmark.svg",
    ROOT / "press" / "assets" / "ghost-orgy-short-bio.txt",
    ROOT / "press" / "assets" / "ghost-orgy-long-bio.txt",
    ROOT / "press" / "assets" / "ghost-orgy-bios.txt",
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
SRCSET_SPLIT_PATTERN = re.compile(r"\s*,\s*")


class PageReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str, str]] = []
        self.meta: dict[str, str] = {}
        self.anchors: set[str] = set()
        self.title_parts: list[str] = []
        self.json_ld_blocks: list[str] = []
        self._in_title = False
        self._in_json_ld = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value for name, value in attrs if value is not None}

        for attr in ("id", "name"):
            value = attr_map.get(attr)
            if value:
                self.anchors.add(value)

        for attr in ("href", "src", "poster"):
            value = attr_map.get(attr)
            if value:
                self.references.append((tag, attr, value))

        for attr in ("srcset", "imagesrcset"):
            value = attr_map.get(attr)
            if not value:
                continue
            for item in SRCSET_SPLIT_PATTERN.split(value.strip()):
                candidate = item.strip().split()[0] if item.strip() else ""
                if candidate:
                    self.references.append((tag, attr, candidate))

        if tag == "title":
            self._in_title = True

        if tag == "script" and attr_map.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_parts = []

        if tag != "meta":
            return

        key = attr_map.get("property") or attr_map.get("name")
        content = attr_map.get("content")
        if key and content:
            self.meta[key.lower()] = content

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_parts))
            self._in_json_ld = False
            self._json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self._json_ld_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_page(path: Path) -> PageReferenceParser:
    parser = PageReferenceParser()
    parser.feed(read_text(path))
    return parser


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


def is_skipped_reference(raw_url: str) -> bool:
    if not raw_url or raw_url.startswith("{"):
        return True

    parsed = urlparse(raw_url)
    if parsed.scheme in {"mailto", "tel", "javascript", "data"}:
        return True
    if parsed.scheme in {"http", "https"} and parsed.netloc not in SAME_SITE_HOSTS:
        return True
    if parsed.netloc and parsed.netloc not in SAME_SITE_HOSTS:
        return True
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return True
    return False


def resolve_site_reference(page: Path, raw_url: str) -> tuple[Path, str, str] | None:
    if is_skipped_reference(raw_url):
        return None

    parsed = urlparse(raw_url)
    path_part = unquote(parsed.path)
    fragment = unquote(parsed.fragment)

    if not path_part and not fragment:
        return None
    if not path_part and fragment:
        return page, "", fragment

    if parsed.scheme in {"http", "https"} or parsed.netloc in SAME_SITE_HOSTS or path_part.startswith("/"):
        target = ROOT / path_part.lstrip("/")
    else:
        target = page.parent / path_part

    if target.is_dir() or path_part.endswith("/"):
        target = target / "index.html"

    return target.resolve(), path_part, fragment


def check_links_and_anchors(errors: list[str]) -> None:
    parsed_pages = {page: parse_page(page) for page in LINK_CHECK_PAGES}
    anchors_by_page = {page.resolve(): parser.anchors for page, parser in parsed_pages.items()}

    for page, parser in parsed_pages.items():
        for tag, attr, raw_url in parser.references:
            resolved = resolve_site_reference(page, raw_url)
            if not resolved:
                continue

            target, path_part, fragment = resolved
            if path_part and not target.exists():
                errors.append(
                    f"{page.relative_to(ROOT)} references missing local target `{raw_url}` "
                    f"from `{tag} {attr}`."
                )
                continue

            if not fragment or target.suffix.lower() != ".html":
                continue

            anchors = anchors_by_page.get(target)
            if anchors is None and target.is_file():
                anchors = parse_page(target).anchors
                anchors_by_page[target] = anchors

            if anchors is not None and fragment not in anchors:
                errors.append(
                    f"{page.relative_to(ROOT)} references missing anchor `#{fragment}` in "
                    f"`{target.relative_to(ROOT)}` via `{raw_url}`."
                )


def check_social_previews(errors: list[str]) -> None:
    for page in SOCIAL_PREVIEW_PAGES:
        parser = parse_page(page)
        for field in REQUIRED_SOCIAL_PREVIEW_FIELDS:
            value = parser.meta.get(field)
            if not value:
                errors.append(f"{page.relative_to(ROOT)} is missing social preview field `{field}`.")
                continue

            if field.endswith(":alt"):
                if not value.strip():
                    errors.append(f"{page.relative_to(ROOT)} has an empty social preview field `{field}`.")
                continue

            parsed = urlparse(value)
            if parsed.scheme != "https" or parsed.netloc not in SAME_SITE_HOSTS:
                errors.append(f"{page.relative_to(ROOT)} uses non-site HTTPS social image `{value}` for `{field}`.")
                continue

            image_path = (ROOT / unquote(parsed.path).lstrip("/")).resolve()
            try:
                image_path.relative_to(ROOT)
            except ValueError:
                errors.append(f"{page.relative_to(ROOT)} points `{field}` outside the repo: `{value}`.")
                continue

            if not image_path.is_file():
                errors.append(f"{page.relative_to(ROOT)} points `{field}` to missing image `{value}`.")
                continue

            if image_path.suffix.lower() not in PUBLIC_MEDIA_EXTENSIONS:
                errors.append(f"{page.relative_to(ROOT)} points `{field}` to non-image media `{value}`.")


def iter_json_objects(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_json_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_json_objects(child)


def check_metadata_contracts(errors: list[str]) -> None:
    for page in SITE_PAGES:
        parser = parse_page(page)
        relative = page.relative_to(ROOT)
        title = parser.title
        description = parser.meta.get("description", "")

        for field in ("og:title", "twitter:title"):
            value = parser.meta.get(field, "")
            if value != title:
                errors.append(f"{relative} metadata `{field}` does not match the document title.")

        for field in ("og:description", "twitter:description"):
            value = parser.meta.get(field, "")
            if value != description:
                errors.append(f"{relative} metadata `{field}` does not match the meta description.")

        metadata_text = " ".join(
            value
            for value in (
                title,
                description,
                parser.meta.get("og:title", ""),
                parser.meta.get("og:description", ""),
                parser.meta.get("twitter:title", ""),
                parser.meta.get("twitter:description", ""),
            )
            if value
        )
        for label, pattern in DISALLOWED_METADATA_PATTERNS:
            if pattern.search(metadata_text):
                errors.append(f"{relative} contains {label} in indexed metadata.")

        for raw_block in parser.json_ld_blocks:
            try:
                block = json.loads(raw_block)
            except json.JSONDecodeError:
                continue
            for item in iter_json_objects(block):
                if item.get("@type") not in {"WebPage", "ContactPage", "CollectionPage"}:
                    continue
                schema_name = item.get("name")
                if schema_name and schema_name != title:
                    errors.append(
                        f"{relative} structured-data name `{schema_name}` does not match the document title."
                    )


def check_pdf_copy(errors: list[str]) -> None:
    for pdf_path in PUBLIC_PDF_FILES:
        if not pdf_path.is_file():
            errors.append(f"Required public PDF is missing: {pdf_path.relative_to(ROOT)}.")
            continue
        try:
            reader = PdfReader(pdf_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            errors.append(f"Could not extract copy from {pdf_path.relative_to(ROOT)}: {exc}.")
            continue
        if not text.strip():
            errors.append(f"{pdf_path.relative_to(ROOT)} has no extractable copy.")
            continue
        for label, pattern in DISALLOWED_NON_HTML_COPY_PATTERNS:
            if pattern.search(text):
                errors.append(f"{pdf_path.relative_to(ROOT)} contains {label}.")


def main() -> int:
    errors: list[str] = []
    referenced_assets: set[Path] = set()

    for page in SITE_PAGES:
        text = read_text(page)
        for snippet in RETIRED_INTEGRATION_SNIPPETS:
            if snippet in text:
                errors.append(
                    f"{page.relative_to(ROOT)} still references retired integration `{snippet}`."
                )

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
        for snippet in DISALLOWED_COPY_SNIPPETS:
            if snippet in text:
                errors.append(f"{page.relative_to(ROOT)} contains disallowed copy/reference `{snippet}`.")
        for label, pattern in DISALLOWED_PUBLIC_COPY_PATTERNS:
            if pattern.search(text):
                errors.append(f"{page.relative_to(ROOT)} contains {label}; rewrite it as visitor-facing copy.")

    for draft in DRAFT_PAGES:
        if not draft.is_file():
            continue
        text = read_text(draft)
        if 'meta name="robots" content="noindex, nofollow, noarchive"' not in text:
            errors.append(f"{draft.relative_to(ROOT)} should be marked `noindex, nofollow, noarchive`.")

    check_links_and_anchors(errors)
    check_social_previews(errors)
    check_metadata_contracts(errors)
    check_pdf_copy(errors)

    if not (ROOT / "404.html").is_file():
        errors.append("404.html is missing.")

    if not (ROOT / "site.webmanifest").is_file():
        errors.append("site.webmanifest is missing.")

    for download in REQUIRED_DOWNLOADS:
        if not download.is_file():
            errors.append(f"Required press download is missing: {download.relative_to(ROOT)}.")

    if not (ROOT / ".nojekyll").is_file():
        errors.append(".nojekyll is missing; GitHub Pages processing should remain disabled.")

    robots = read_text(ROOT / "robots.txt")
    if "Content-Signal:" not in robots:
        errors.append("robots.txt is missing a `Content-Signal:` directive.")

    homepage = read_text(ROOT / "index.html")
    for rel_name in ("service-doc", "describedby"):
        if f'rel="{rel_name}"' not in homepage:
            errors.append(f'index.html is missing a `<link rel="{rel_name}">` discovery hint.')

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
