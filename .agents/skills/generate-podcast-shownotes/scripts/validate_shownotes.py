#!/usr/bin/env python3
"""Validate the ordering, bounds, and useful density of a ShowNotes timeline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TIMELINE_RE = re.compile(
    r"^\s*[-*]\s+(?P<time>(?:\d{1,2}:)?\d{2}:\d{2})\s+(?P<summary>\S.*)\s*$"
)


def parse_clock(value: str) -> int:
    parts = value.split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"invalid timecode: {value}")
    try:
        numbers = [int(part) for part in parts]
    except ValueError as exc:
        raise ValueError(f"invalid timecode: {value}") from exc
    if len(numbers) == 2:
        minutes, seconds = numbers
        hours = 0
    else:
        hours, minutes, seconds = numbers
    if minutes >= 60 and len(numbers) == 3:
        raise ValueError(f"minutes must be below 60: {value}")
    if seconds >= 60:
        raise ValueError(f"seconds must be below 60: {value}")
    return hours * 3600 + minutes * 60 + seconds


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Markdown ShowNotes timeline."
    )
    parser.add_argument(
        "path", type=Path, help="Markdown file containing timeline bullets."
    )
    parser.add_argument(
        "--duration", required=True, help="Audio duration as MM:SS or HH:MM:SS."
    )
    parser.add_argument(
        "--transcript-json",
        type=Path,
        help="Optional transcribe_audio.py JSON used to verify speech boundaries.",
    )
    parser.add_argument(
        "--max-boundary-offset",
        type=float,
        default=2.0,
        help="Maximum seconds from a later timecode to a transcript segment start.",
    )
    parser.add_argument("--min-entries", type=int, default=4)
    parser.add_argument("--max-entries", type=int, default=20)
    args = parser.parse_args()

    if not args.path.is_file():
        parser.error(f"file does not exist: {args.path}")
    try:
        duration = parse_clock(args.duration)
    except ValueError as exc:
        parser.error(str(exc))

    transcript_starts: list[float] | None = None
    if args.transcript_json:
        if not args.transcript_json.is_file():
            parser.error(f"transcript JSON does not exist: {args.transcript_json}")
        try:
            transcript = json.loads(args.transcript_json.read_text(encoding="utf-8"))
            transcript_starts = [
                float(segment["start"])
                for segment in transcript["segments"]
                if segment.get("start") is not None
            ]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            parser.error(f"invalid transcript JSON: {exc}")
        if not transcript_starts:
            parser.error("transcript JSON has no segment starts")

    entries: list[tuple[int, str, int]] = []
    for line_number, line in enumerate(
        args.path.read_text(encoding="utf-8").splitlines(), 1
    ):
        match = TIMELINE_RE.match(line)
        if not match:
            continue
        try:
            seconds = parse_clock(match.group("time"))
        except ValueError as exc:
            print(f"ERROR line {line_number}: {exc}")
            return 1
        entries.append((seconds, match.group("summary"), line_number))

    errors: list[str] = []
    warnings: list[str] = []
    if not args.min_entries <= len(entries) <= args.max_entries:
        errors.append(
            f"found {len(entries)} entries; expected {args.min_entries}–{args.max_entries}"
        )
    if entries and entries[0][0] != 0:
        errors.append("the first entry must begin at 00:00")

    for index, (seconds, summary, line_number) in enumerate(entries):
        if seconds >= duration:
            errors.append(
                f"line {line_number}: timecode is outside duration {args.duration}"
            )
        if len(summary) < 6:
            warnings.append(f"line {line_number}: summary may be too vague or short")
        if index and transcript_starts is not None:
            boundary_offset = min(abs(start - seconds) for start in transcript_starts)
            if boundary_offset > args.max_boundary_offset:
                errors.append(
                    f"line {line_number}: timecode is {boundary_offset:.2f}s from "
                    "the nearest transcript segment start"
                )
        if index:
            previous = entries[index - 1]
            gap = seconds - previous[0]
            if gap <= 0:
                errors.append(f"line {line_number}: timecodes must increase strictly")
            elif gap < 60:
                warnings.append(
                    f"line {line_number}: only {gap}s after the previous chapter; review merging"
                )
            elif gap > 600:
                warnings.append(
                    f"line {line_number}: {gap}s after the previous chapter; review missing transitions"
                )

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(
        f"OK: {len(entries)} entries are strictly increasing and within {args.duration}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
