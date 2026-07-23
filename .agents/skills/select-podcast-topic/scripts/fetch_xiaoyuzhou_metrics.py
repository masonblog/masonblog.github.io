#!/usr/bin/env python3
"""Fetch public episode metrics from Xiaoyuzhou's official web pages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_PODCAST_URL = (
    "https://www.xiaoyuzhoufm.com/podcast/68453dda5d66f3ec9a7aa1b4"
)
EPISODE_URL_RE = re.compile(
    r"https://www\.xiaoyuzhoufm\.com/episode/([0-9a-f]+)",
    re.IGNORECASE,
)
PODCAST_URL_RE = re.compile(
    r"https://www\.xiaoyuzhoufm\.com/podcast/([0-9a-f]+)",
    re.IGNORECASE,
)
NEXT_DATA_RE = re.compile(
    r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>([\s\S]*?)</script>',
    re.IGNORECASE,
)


def fetch_page_props(url: str, timeout: float) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; select-podcast-topic/1.0; "
                "+https://blog.masonhu.cc/)"
            )
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            html = response.read().decode(charset, errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"cannot fetch {url}: {exc}") from exc

    match = NEXT_DATA_RE.search(html)
    if not match:
        raise RuntimeError(f"official page has no __NEXT_DATA__: {url}")

    try:
        payload = json.loads(match.group(1))
        page_props = payload["props"]["pageProps"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError(f"cannot parse official page data: {url}") from exc

    if not isinstance(page_props, dict) or not page_props:
        raise RuntimeError(f"official page returned empty pageProps: {url}")
    return page_props


def episode_urls_from_local_page(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [
        f"https://www.xiaoyuzhoufm.com/episode/{episode_id}"
        for episode_id in EPISODE_URL_RE.findall(text)
    ]


def episode_urls_from_podcast(
    podcast_url: str, timeout: float
) -> tuple[list[str], dict[str, Any]]:
    page_props = fetch_page_props(podcast_url, timeout)
    podcast = page_props.get("podcast")
    if not isinstance(podcast, dict):
        raise RuntimeError(f"official podcast data is missing: {podcast_url}")

    urls: list[str] = []
    for episode in podcast.get("episodes") or []:
        if isinstance(episode, dict) and episode.get("eid"):
            urls.append(
                f"https://www.xiaoyuzhoufm.com/episode/{episode['eid']}"
            )
    return urls, podcast


def int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def parse_published_at(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except ValueError:
        return None


def parse_episode(
    url: str,
    episode: dict[str, Any],
    expected_podcast_id: str,
    observed_at: datetime,
) -> dict[str, Any]:
    actual_podcast_id = episode.get("pid")
    if actual_podcast_id != expected_podcast_id:
        raise RuntimeError(
            f"episode belongs to podcast {actual_podcast_id!r}, "
            f"expected {expected_podcast_id!r}: {url}"
        )

    published_at = parse_published_at(episode.get("pubDate"))
    age_days = None
    if published_at is not None:
        age_days = round(
            max((observed_at - published_at).total_seconds(), 0) / 86400,
            3,
        )

    play_count = int_or_none(episode.get("playCount"))
    clap_count = int_or_none(episode.get("clapCount"))
    favorite_count = int_or_none(episode.get("favoriteCount"))
    comment_count = int_or_none(episode.get("commentCount"))

    rates: dict[str, float | None] = {
        "claps_per_100_plays": None,
        "favorites_per_100_plays": None,
        "comments_per_100_plays": None,
    }
    if play_count is not None and play_count > 0:
        rates = {
            "claps_per_100_plays": round(clap_count * 100 / play_count, 3)
            if clap_count is not None
            else None,
            "favorites_per_100_plays": round(
                favorite_count * 100 / play_count, 3
            )
            if favorite_count is not None
            else None,
            "comments_per_100_plays": round(
                comment_count * 100 / play_count, 3
            )
            if comment_count is not None
            else None,
        }

    title = episode.get("title")
    episode_number = None
    if isinstance(title, str):
        number_match = re.match(r"^\s*(\d{1,3})\b", title)
        if number_match:
            episode_number = int(number_match.group(1))

    return {
        "episode_number": episode_number,
        "episode_id": episode.get("eid"),
        "title": title,
        "canonical_url": url,
        "published_at": episode.get("pubDate"),
        "age_days_at_observation": age_days,
        "duration_seconds": int_or_none(episode.get("duration")),
        "play_count": play_count,
        "clap_count": clap_count,
        "favorite_count": favorite_count,
        "comment_count": comment_count,
        "rates": rates,
    }


def deduplicate(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read public play, clap, favorite, and comment counts from "
            "Xiaoyuzhou's official podcast and episode pages."
        )
    )
    parser.add_argument(
        "--podcast-url",
        default=DEFAULT_PODCAST_URL,
        help="Official Xiaoyuzhou podcast URL.",
    )
    parser.add_argument(
        "--podcast-page",
        default="content/podcast.md",
        help=(
            "Local Markdown page containing official episode URLs. "
            "It supplies older links beyond the official show's recent list."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    args = parser.parse_args()

    podcast_match = PODCAST_URL_RE.fullmatch(args.podcast_url.rstrip("/"))
    if not podcast_match:
        parser.error("--podcast-url must be an official Xiaoyuzhou podcast URL")
    podcast_id = podcast_match.group(1)
    observed_at = datetime.now(timezone.utc)

    errors: list[dict[str, str]] = []
    try:
        recent_urls, podcast = episode_urls_from_podcast(
            args.podcast_url.rstrip("/"), args.timeout
        )
    except RuntimeError as exc:
        recent_urls = []
        podcast = {}
        errors.append({"url": args.podcast_url, "error": str(exc)})

    local_urls = episode_urls_from_local_page(Path(args.podcast_page))
    episode_urls = deduplicate(local_urls + recent_urls)
    episodes: list[dict[str, Any]] = []

    for url in episode_urls:
        try:
            page_props = fetch_page_props(url, args.timeout)
            episode = page_props.get("episode")
            if not isinstance(episode, dict):
                raise RuntimeError(f"official episode data is missing: {url}")
            episodes.append(
                parse_episode(url, episode, podcast_id, observed_at)
            )
        except RuntimeError as exc:
            errors.append({"url": url, "error": str(exc)})

    episodes.sort(
        key=lambda item: item.get("published_at") or "",
        reverse=True,
    )
    output = {
        "schema_version": 1,
        "source": {
            "provider": "小宇宙",
            "podcast_url": args.podcast_url.rstrip("/"),
            "podcast_id": podcast_id,
            "podcast_title": podcast.get("title"),
            "local_episode_link_source": str(Path(args.podcast_page)),
        },
        "observed_at": observed_at.isoformat().replace("+00:00", "Z"),
        "episode_count": len(episodes),
        "episodes": episodes,
        "errors": errors,
    }
    json.dump(
        output,
        sys.stdout,
        ensure_ascii=False,
        indent=2 if args.pretty else None,
    )
    sys.stdout.write("\n")

    if not episode_urls:
        print("no official episode URLs found", file=sys.stderr)
        return 1
    if errors:
        print(
            f"failed to read {len(errors)} official page(s); see errors in JSON",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
