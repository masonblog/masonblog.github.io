#!/usr/bin/env python3
"""Transcribe local audio or the newest RSS enclosure with word timestamps."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

USER_AGENT = "generate-podcast-shownotes/1.0 (+https://masonhu.cc/)"


def request_bytes(url: str, timeout: float) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"cannot fetch {url}: {exc}") from exc


def child_text(element: ET.Element, local_name: str) -> str | None:
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == local_name:
            value = (child.text or "").strip()
            return value or None
    return None


def parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def latest_rss_item(xml_bytes: bytes, rss_url: str) -> dict[str, Any]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise RuntimeError(f"invalid RSS XML from {rss_url}: {exc}") from exc

    channel = root.find("channel")
    if channel is None:
        raise RuntimeError(f"RSS channel is missing: {rss_url}")
    items = channel.findall("item")
    if not items:
        raise RuntimeError(f"RSS has no episode items: {rss_url}")
    item = max(items, key=lambda value: parse_date(child_text(value, "pubDate")))

    enclosure = next(
        (child for child in item if child.tag.rsplit("}", 1)[-1] == "enclosure"),
        None,
    )
    if enclosure is None or not enclosure.attrib.get("url"):
        raise RuntimeError("newest RSS item has no audio enclosure URL")

    length_text = enclosure.attrib.get("length")
    try:
        length = int(length_text) if length_text else None
    except ValueError as exc:
        raise RuntimeError(f"invalid RSS enclosure length: {length_text!r}") from exc

    return {
        "rss_url": rss_url,
        "podcast_title": child_text(channel, "title"),
        "episode_title": child_text(item, "title"),
        "published": child_text(item, "pubDate"),
        "guid": child_text(item, "guid"),
        "episode_url": child_text(item, "link"),
        "audio_url": enclosure.attrib["url"],
        "audio_type": enclosure.attrib.get("type"),
        "audio_length": length,
        "rss_duration": child_text(item, "duration"),
    }


def download_audio(
    url: str,
    destination: Path,
    expected_length: int | None,
    timeout: float,
) -> int:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with (
            urlopen(request, timeout=timeout) as response,
            destination.open("wb") as handle,
        ):
            shutil.copyfileobj(response, handle)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"cannot download audio enclosure {url}: {exc}") from exc

    actual_length = destination.stat().st_size
    if expected_length is not None and actual_length != expected_length:
        raise RuntimeError(
            "downloaded enclosure length does not match RSS: "
            f"expected {expected_length}, got {actual_length}"
        )
    return actual_length


def clock(seconds: float, milliseconds: bool = False) -> str:
    seconds = max(seconds, 0.0)
    whole = int(seconds)
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    base = f"{hours:02d}:{minutes:02d}:{secs:02d}"
    if milliseconds:
        return f"{base}.{int((seconds - whole) * 1000):03d}"
    return base


def transcribe(
    audio_path: Path,
    model_name: str,
    language: str | None,
    device: str,
    compute_type: str,
    initial_prompt: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is required; run this script with "
            "`uv run --python 3.12 --with faster-whisper ...`"
        ) from exc

    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segment_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
        word_timestamps=True,
        initial_prompt=initial_prompt,
    )

    segments: list[dict[str, Any]] = []
    next_progress_second = 60
    for segment in segment_iter:
        words = [
            {
                "start": word.start,
                "end": word.end,
                "text": word.word,
                "probability": word.probability,
            }
            for word in segment.words or []
        ]
        segments.append(
            {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": words,
            }
        )
        while segment.end >= next_progress_second:
            print(
                f"transcribed through {clock(next_progress_second)}",
                file=sys.stderr,
                flush=True,
            )
            next_progress_second += 60

    info_data = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration_seconds": info.duration,
        "duration_after_vad_seconds": info.duration_after_vad,
    }
    return info_data, segments


def write_readable_transcript(path: Path, payload: dict[str, Any]) -> None:
    source = payload["source"]
    transcription = payload["transcription"]
    lines = [
        "# Timestamped transcript",
        "",
        f"- Source: {source.get('episode_title') or source.get('audio_path')}",
        f"- Duration: {clock(transcription['duration_seconds'])}",
        f"- Language: {transcription['language']}",
        f"- Model: {transcription['model']}",
        "",
    ]
    lines.extend(
        f"[{clock(segment['start'], True)} --> {clock(segment['end'], True)}] {segment['text']}"
        for segment in payload["segments"]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Transcribe local audio or the newest RSS enclosure with timestamps."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--audio", type=Path, help="Local audio file.")
    source.add_argument(
        "--rss-url", help="RSS feed; selects the newest item by pubDate."
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Transcript JSON path."
    )
    parser.add_argument(
        "--text-output", type=Path, help="Readable timestamped Markdown path."
    )
    parser.add_argument("--model", default="small", help="faster-whisper model name.")
    parser.add_argument(
        "--language", default="zh", help="Language code; use auto to detect."
    )
    parser.add_argument("--device", default="cpu", help="faster-whisper device.")
    parser.add_argument(
        "--compute-type", default="int8", help="faster-whisper compute type."
    )
    parser.add_argument(
        "--timeout", type=float, default=120, help="Network timeout in seconds."
    )
    parser.add_argument(
        "--initial-prompt",
        default="以下是中文播客《议正言辞》，涉及法律史、人名、案件和法条。",
        help="Prompt supplied to the speech recognizer.",
    )
    args = parser.parse_args()

    if args.audio is not None and not args.audio.is_file():
        parser.error(f"audio file does not exist: {args.audio}")

    source_data: dict[str, Any]
    temp_context = tempfile.TemporaryDirectory(prefix="podcast-shownotes-")
    try:
        if args.rss_url:
            source_data = latest_rss_item(
                request_bytes(args.rss_url, args.timeout),
                args.rss_url,
            )
            suffix = Path(urlparse(source_data["audio_url"]).path).suffix or ".audio"
            audio_path = Path(temp_context.name) / f"episode{suffix}"
            source_data["downloaded_length"] = download_audio(
                source_data["audio_url"],
                audio_path,
                source_data["audio_length"],
                args.timeout,
            )
        else:
            audio_path = args.audio.resolve()
            source_data = {
                "audio_path": str(audio_path),
                "audio_length": audio_path.stat().st_size,
            }

        language = None if args.language.lower() == "auto" else args.language
        info, segments = transcribe(
            audio_path,
            args.model,
            language,
            args.device,
            args.compute_type,
            args.initial_prompt,
        )
        payload = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "source": source_data,
            "transcription": {
                **info,
                "model": args.model,
                "device": args.device,
                "compute_type": args.compute_type,
                "requested_language": language,
            },
            "segments": segments,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if args.text_output:
            write_readable_transcript(args.text_output, payload)

        print(
            json.dumps(
                {
                    "episode_title": source_data.get("episode_title"),
                    "duration": clock(info["duration_seconds"]),
                    "language": info["language"],
                    "segments": len(segments),
                    "output": str(args.output),
                    "text_output": str(args.text_output) if args.text_output else None,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        temp_context.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
