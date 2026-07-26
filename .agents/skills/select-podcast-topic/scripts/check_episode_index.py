#!/usr/bin/env python3
"""Compare podcast transcripts with the persistent semantic coverage index."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import textwrap
from datetime import date, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
AUDIT_INTERVAL_EPISODES = 5
AUDIT_INTERVAL_DAYS = 180
REQUIRED_COVERAGE_STRINGS = (
    "summary",
    "core_question",
    "narrative_hook",
    "expected_conclusion",
)
REQUIRED_COVERAGE_LISTS = (
    "eras",
    "jurisdictions",
    "people_or_cases",
    "legal_fields",
    "mechanisms",
    "central_claims",
    "source_types",
    "overlap_notes",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def front_matter(text: str) -> str | None:
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|\Z)", text, re.S)
    return match.group(1) if match else None


def scalar(metadata: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", metadata)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value


def podcast_block(metadata: str) -> str | None:
    lines = metadata.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if re.fullmatch(r"podcast:\s*", line):
            start = index + 1
            break
    if start is None:
        return None

    block: list[str] = []
    for line in lines[start:]:
        if line and not line[0].isspace():
            break
        block.append(line)
    return textwrap.dedent("\n".join(block))


def inventory(repo: Path) -> tuple[list[dict[str, Any]], list[str]]:
    posts = repo / "content" / "post"
    episodes: list[dict[str, Any]] = []
    indexed_paths: set[str] = set()

    for path in sorted(posts.glob("*.md")):
        if path.name.endswith(".en.md"):
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        metadata = front_matter(text)
        if metadata is None:
            continue
        block = podcast_block(metadata)
        if block is None:
            continue
        episode_value = scalar(block, "episode")
        if episode_value is None or not episode_value.isdigit():
            continue

        relative_path = path.relative_to(repo).as_posix()
        draft = (scalar(metadata, "draft") or "").lower()
        hidden = (scalar(metadata, "hidden") or "").lower()
        publication_state = (
            "published" if draft == "false" and hidden != "true" else "planned"
        )
        item = {
            "episode": int(episode_value),
            "path": relative_path,
            "publication_state": publication_state,
            "title": scalar(block, "title") or scalar(metadata, "title"),
            "date": scalar(metadata, "date"),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
        }
        episodes.append(item)
        indexed_paths.add(relative_path)

    podcast_page_only: list[str] = []
    podcast_page = repo / "content" / "podcast.md"
    if podcast_page.exists():
        page_text = podcast_page.read_text(encoding="utf-8")
        for slug in sorted(set(re.findall(r"/post/(blog\d{8})/", page_text))):
            relative_path = f"content/post/{slug}.md"
            if relative_path not in indexed_paths:
                podcast_page_only.append(relative_path)

    episodes.sort(key=lambda item: (item["episode"], item["path"]))
    return episodes, podcast_page_only


def load_index(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "index file does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"cannot read index: {exc}"
    if not isinstance(data, dict):
        return None, "index root must be an object"
    if data.get("schema_version") != SCHEMA_VERSION:
        return None, (
            f"schema_version must be {SCHEMA_VERSION}, "
            f"got {data.get('schema_version')!r}"
        )
    if not isinstance(data.get("episodes"), list):
        return None, "episodes must be an array"
    return data, None


def entry_problems(entry: Any, item: dict[str, Any]) -> list[str]:
    if not isinstance(entry, dict):
        return ["entry must be an object"]

    problems: list[str] = []
    if entry.get("episode") != item["episode"]:
        problems.append("episode does not match source")
    if entry.get("publication_state") != item["publication_state"]:
        problems.append("publication_state does not match source")
    if not isinstance(entry.get("indexed_at"), str) or not entry["indexed_at"].strip():
        problems.append("indexed_at is missing")

    coverage = entry.get("coverage")
    if not isinstance(coverage, dict):
        return problems + ["coverage must be an object"]
    for key in REQUIRED_COVERAGE_STRINGS:
        if not isinstance(coverage.get(key), str) or not coverage[key].strip():
            problems.append(f"coverage.{key} must be a non-empty string")
    for key in REQUIRED_COVERAGE_LISTS:
        value = coverage.get(key)
        if not isinstance(value, list) or not all(
            isinstance(element, str) and element.strip() for element in value
        ):
            problems.append(f"coverage.{key} must be an array of non-empty strings")
    present_connection = coverage.get("present_connection")
    if not isinstance(present_connection, str):
        problems.append("coverage.present_connection must be a string")
    return problems


def parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def audit_status(index: dict[str, Any] | None, items: list[dict[str, Any]]) -> dict[str, Any]:
    if index is None:
        return {"due": True, "reasons": ["coverage index is unavailable"]}

    audit = index.get("full_audit")
    if not isinstance(audit, dict):
        return {"due": True, "reasons": ["full_audit metadata is missing"]}

    reasons: list[str] = []
    completed_at = parse_iso_date(audit.get("completed_at"))
    through_episode = audit.get("through_episode")
    highest_episode = max((item["episode"] for item in items), default=0)

    if completed_at is None:
        reasons.append("no completed full audit is recorded")
    elif (date.today() - completed_at).days >= AUDIT_INTERVAL_DAYS:
        reasons.append(
            f"last full audit is at least {AUDIT_INTERVAL_DAYS} days old"
        )

    if not isinstance(through_episode, int):
        reasons.append("full_audit.through_episode is invalid")
    elif highest_episode - through_episode >= AUDIT_INTERVAL_EPISODES:
        reasons.append(
            f"{highest_episode - through_episode} episodes were added "
            "after the last full audit"
        )

    return {
        "due": bool(reasons),
        "reasons": reasons,
        "completed_at": audit.get("completed_at"),
        "through_episode": through_episode,
    }


def compare(
    items: list[dict[str, Any]],
    index: dict[str, Any] | None,
    index_error: str | None,
    podcast_page_only: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "index_error": index_error,
        "current": [],
        "missing": [],
        "changed": [],
        "incomplete": [],
        "orphaned": [],
        "podcast_page_only": podcast_page_only,
        "duplicate_episodes": [],
    }
    indexed_by_path: dict[str, Any] = {}
    duplicate_paths: set[str] = set()

    if index is not None:
        for entry in index["episodes"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                result["incomplete"].append(
                    {"path": None, "problems": ["entry path is missing"]}
                )
                continue
            path = entry["path"]
            if path in indexed_by_path:
                duplicate_paths.add(path)
            indexed_by_path[path] = entry

    for path in sorted(duplicate_paths):
        result["incomplete"].append(
            {"path": path, "problems": ["duplicate index entries"]}
        )

    inventory_paths = {item["path"] for item in items}
    paths_by_episode: dict[int, list[str]] = {}
    for item in items:
        paths_by_episode.setdefault(item["episode"], []).append(item["path"])
    for episode, paths in sorted(paths_by_episode.items()):
        if len(paths) > 1:
            result["duplicate_episodes"].append(
                {"episode": episode, "paths": sorted(paths)}
            )

    for item in items:
        entry = indexed_by_path.get(item["path"])
        identity = {
            "episode": item["episode"],
            "path": item["path"],
            "publication_state": item["publication_state"],
            "title": item["title"],
        }
        if entry is None:
            result["missing"].append(identity)
            continue
        if entry.get("source_sha256") != item["source_sha256"]:
            result["changed"].append(
                {
                    **identity,
                    "indexed_sha256": entry.get("source_sha256"),
                    "source_sha256": item["source_sha256"],
                }
            )
            continue
        problems = entry_problems(entry, item)
        if problems:
            result["incomplete"].append({**identity, "problems": problems})
            continue
        result["current"].append(identity)

    for path in sorted(set(indexed_by_path) - inventory_paths):
        result["orphaned"].append(
            {
                "path": path,
                "episode": indexed_by_path[path].get("episode"),
            }
        )

    result["audit"] = audit_status(index, items)
    result["summary"] = {
        "transcript_count": len(items),
        "current": len(result["current"]),
        "missing": len(result["missing"]),
        "changed": len(result["changed"]),
        "incomplete": len(result["incomplete"]),
        "orphaned": len(result["orphaned"]),
        "podcast_page_only": len(result["podcast_page_only"]),
        "duplicate_episodes": len(result["duplicate_episodes"]),
        "full_audit_due": result["audit"]["due"],
    }
    return result


def main() -> int:
    repo = repository_root()
    parser = argparse.ArgumentParser(
        description="Report missing, changed, or invalid podcast coverage-index entries."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo,
        help="Repository root. Defaults to the root containing this skill.",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="Coverage index JSON path.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero unless the index is current and no audit is due.",
    )
    args = parser.parse_args()

    repo_path = args.repo_root.resolve()
    index_path = args.index
    if index_path is None:
        index_path = (
            repo_path
            / ".agents"
            / "skills"
            / "select-podcast-topic"
            / "references"
            / "episode-coverage.json"
        )
    elif not index_path.is_absolute():
        index_path = repo_path / index_path

    items, podcast_page_only = inventory(repo_path)
    index, index_error = load_index(index_path)
    result = compare(items, index, index_error, podcast_page_only)
    try:
        result["index_path"] = index_path.relative_to(repo_path).as_posix()
    except ValueError:
        result["index_path"] = str(index_path)
    json.dump(
        result,
        sys.stdout,
        ensure_ascii=False,
        indent=2 if args.pretty else None,
    )
    sys.stdout.write("\n")

    if args.strict:
        summary = result["summary"]
        blocked = (
            index_error is not None
            or summary["missing"]
            or summary["changed"]
            or summary["incomplete"]
            or summary["orphaned"]
            or summary["podcast_page_only"]
            or summary["duplicate_episodes"]
            or summary["full_audit_due"]
        )
        return 1 if blocked else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
