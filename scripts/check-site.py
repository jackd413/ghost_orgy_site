#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
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

DRAFT_PAGES: list[Path] = []

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


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


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
        if not draft.is_file():
            continue
        text = read_text(draft)
        if 'meta name="robots" content="noindex, nofollow, noarchive"' not in text:
            errors.append(f"{draft.relative_to(ROOT)} should be marked `noindex, nofollow, noarchive`.")

    if not (ROOT / "404.html").is_file():
        errors.append("404.html is missing.")

    if not (ROOT / "site.webmanifest").is_file():
        errors.append("site.webmanifest is missing.")

    if not (ROOT / ".nojekyll").is_file():
        errors.append(".nojekyll is missing; GitHub Pages may skip dot-directories like /.well-known/.")

    if not (ROOT / ".well-known" / "agent-service.json").is_file():
        errors.append(".well-known/agent-service.json is missing.")

    robots = read_text(ROOT / "robots.txt")
    if "Content-Signal:" not in robots:
        errors.append("robots.txt is missing a `Content-Signal:` directive.")

    agent_skills_index = ROOT / ".well-known" / "agent-skills" / "index.json"
    if not agent_skills_index.is_file():
        errors.append(".well-known/agent-skills/index.json is missing.")
    else:
        try:
            index_data = read_json(agent_skills_index)
        except json.JSONDecodeError as exc:
            errors.append(f".well-known/agent-skills/index.json is not valid JSON: {exc}.")
        else:
            expected_schema = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
            if index_data.get("$schema") != expected_schema:
                errors.append(
                    ".well-known/agent-skills/index.json should use "
                    f"`{expected_schema}` as its `$schema`."
                )

            skills = index_data.get("skills")
            if not isinstance(skills, list) or not skills:
                errors.append(".well-known/agent-skills/index.json should contain a non-empty `skills` array.")
            else:
                for idx, skill in enumerate(skills, start=1):
                    if not isinstance(skill, dict):
                        errors.append(f"Skill entry #{idx} in agent-skills index is not an object.")
                        continue

                    for field in ("name", "type", "description", "url", "digest"):
                        if field not in skill:
                            errors.append(f"Skill entry #{idx} is missing `{field}`.")

                    if skill.get("type") != "skill-md":
                        errors.append(
                            f"Skill `{skill.get('name', f'#{idx}')}` should use `type: \"skill-md\"` for a standalone SKILL.md file."
                        )
                        continue

                    raw_url = skill.get("url")
                    if not isinstance(raw_url, str) or not raw_url.startswith("/"):
                        errors.append(f"Skill `{skill.get('name', f'#{idx}')}` should use a path-absolute `url`.")
                        continue

                    artifact = (ROOT / raw_url.lstrip("/")).resolve()
                    try:
                        artifact.relative_to(ROOT)
                    except ValueError:
                        errors.append(f"Skill `{skill.get('name', f'#{idx}')}` points outside the repo: `{raw_url}`.")
                        continue

                    if not artifact.is_file():
                        errors.append(f"Skill `{skill.get('name', f'#{idx}')}` points to a missing artifact: `{raw_url}`.")
                        continue

                    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
                    expected_digest = f"sha256:{digest}"
                    if skill.get("digest") != expected_digest:
                        errors.append(
                            f"Skill `{skill.get('name', f'#{idx}')}` has digest `{skill.get('digest')}`, "
                            f"expected `{expected_digest}`."
                        )

    homepage = read_text(ROOT / "index.html")
    for rel_name in ("service-desc", "service-doc", "describedby"):
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
