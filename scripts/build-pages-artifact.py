#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_PATHS = [
    ".nojekyll",
    ".well-known",
    "404.html",
    "CNAME",
    "artifacts",
    "fonts",
    "icons",
    "images",
    "index.html",
    "licensing",
    "listen",
    "lore",
    "nine-sisters",
    "press",
    "robots.txt",
    "salt",
    "shop",
    "sisters",
    "site.webmanifest",
    "sitemap.xml",
    "styles",
    "threshold",
    "updates",
]

SCRIPT_PATHS = [
    "scripts/site.js",
]

EXPECTED_TOP_LEVEL = {Path(path).parts[0] for path in PUBLIC_PATHS}
EXPECTED_TOP_LEVEL.add("scripts")


def resolve_inside_root(path: Path) -> Path:
    resolved = path.resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        raise ValueError(f"Refusing to write outside repo root: {resolved}")
    return resolved


def remove_existing(path: Path, *, require_inside_root: bool) -> None:
    resolved = resolve_inside_root(path) if require_inside_root else path.resolve()
    if resolved.exists():
        shutil.rmtree(resolved)


def copy_entry(relative_path: str, destination_root: Path) -> None:
    source = ROOT / relative_path
    if not source.exists():
        raise FileNotFoundError(f"Public artifact source is missing: {relative_path}")

    target = destination_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
    else:
        shutil.copy2(source, target)


def validate_artifact(destination_root: Path) -> list[str]:
    errors: list[str] = []

    for relative_path in [*PUBLIC_PATHS, *SCRIPT_PATHS]:
        if not (destination_root / relative_path).exists():
            errors.append(f"Artifact is missing `{relative_path}`.")

    for entry in destination_root.iterdir():
        if entry.name not in EXPECTED_TOP_LEVEL:
            errors.append(f"Artifact contains non-public top-level entry `{entry.name}`.")

    for forbidden in [
        ".git",
        ".github",
        ".claude",
        ".wrangler",
        "cloudflare",
        "node_modules",
        "source-assets",
        "staging",
        "canon-sync.local.json",
        "package.json",
        "package-lock.json",
        "HOSTING.md",
        "LOCAL_ASSETS.md",
        "REPO_RULES.md",
    ]:
        if (destination_root / forbidden).exists():
            errors.append(f"Artifact includes forbidden repo-only path `{forbidden}`.")

    return errors


def build_artifact(destination_root: Path, *, require_inside_root: bool = True) -> None:
    remove_existing(destination_root, require_inside_root=require_inside_root)
    destination_root.mkdir(parents=True, exist_ok=True)

    for relative_path in PUBLIC_PATHS:
        copy_entry(relative_path, destination_root)

    for relative_path in SCRIPT_PATHS:
        copy_entry(relative_path, destination_root)

    errors = validate_artifact(destination_root)
    if errors:
        raise RuntimeError("Pages artifact validation failed:\n- " + "\n- ".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate the GitHub Pages artifact.")
    parser.add_argument("destination", nargs="?", default="_site", help="Artifact output directory.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Build into a temporary directory and validate without writing the destination.",
    )
    args = parser.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory(prefix="ghost-orgy-pages-artifact-") as tmp:
            destination = Path(tmp) / "_site"
            build_artifact(destination, require_inside_root=False)
        print("Pages artifact check passed.")
        return 0

    destination = resolve_inside_root(ROOT / args.destination)
    build_artifact(destination)
    print(f"Pages artifact built at {destination.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
