#!/usr/bin/env python3
"""Inspect local Chinese podcast posts without loading transcript bodies."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


KEY_VALUE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$")
PAGE_EPISODE = re.compile(r"^###\s+\[(\d{1,3})\s+", re.MULTILINE)


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def read_front_matter(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}

    result: dict[str, Any] = {}
    section: str | None = None
    for raw_line in lines[1:end]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        match = KEY_VALUE.match(raw_line.lstrip())
        if not match:
            continue
        key, raw_value = match.groups()
        if indent == 0:
            value = parse_scalar(raw_value)
            result[key] = {} if raw_value.strip() == "" else value
            section = key if isinstance(result[key], dict) else None
        elif section and isinstance(result.get(section), dict):
            result[section][key] = parse_scalar(raw_value)
    return result


def collect_posts(root: Path) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    for path in sorted((root / "content" / "post").glob("*.md")):
        if path.name.endswith(".en.md"):
            continue
        front_matter = read_front_matter(path)
        podcast = front_matter.get("podcast")
        if not isinstance(podcast, dict) or not isinstance(podcast.get("episode"), int):
            continue
        posts.append(
            {
                "episode": podcast["episode"],
                "title": podcast.get("title") or front_matter.get("title"),
                "date": front_matter.get("date"),
                "draft": front_matter.get("draft"),
                "hidden": front_matter.get("hidden"),
                "published": front_matter.get("draft") is False
                and front_matter.get("hidden") is not True,
                "path": path.relative_to(root).as_posix(),
            }
        )
    return posts


def inspect(root: Path) -> dict[str, Any]:
    posts = collect_posts(root)
    published = sorted((post for post in posts if post["published"]), key=lambda item: item["episode"])
    planned = sorted((post for post in posts if not post["published"]), key=lambda item: item["episode"])
    published_episodes = {post["episode"] for post in published}

    podcast_page = root / "content" / "podcast.md"
    page_episodes = []
    if podcast_page.exists():
        page_episodes = sorted(
            {int(value) for value in PAGE_EPISODE.findall(podcast_page.read_text(encoding="utf-8-sig"))}
        )
    page_episode_set = set(page_episodes)

    highest = max(published_episodes, default=0)
    next_episode = highest + 1
    all_counts = Counter(post["episode"] for post in posts)
    warnings: list[str] = []

    duplicates = sorted(episode for episode, count in all_counts.items() if count > 1)
    if duplicates:
        warnings.append(f"Duplicate local episode numbers: {duplicates}")

    missing_from_page = sorted(published_episodes - page_episode_set)
    if missing_from_page:
        warnings.append(f"Published posts missing from content/podcast.md: {missing_from_page}")

    page_only = sorted(page_episode_set - published_episodes)
    if page_only:
        warnings.append(f"Podcast page episodes without published local posts: {page_only}")

    conflicts = [post for post in planned if post["episode"] == next_episode]
    if conflicts:
        warnings.append(
            "The next episode number is already used by an unpublished or hidden post: "
            + ", ".join(post["path"] for post in conflicts)
        )

    return {
        "root": str(root),
        "highest_published": highest or None,
        "next_episode": next_episode,
        "next_episode_padded": f"{next_episode:02d}",
        "latest_five": published[-5:],
        "published_posts": published,
        "planned_or_hidden_posts": planned,
        "podcast_page_episodes": page_episodes,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (default: cwd)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    root = args.root.resolve()
    result = inspect(root)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
