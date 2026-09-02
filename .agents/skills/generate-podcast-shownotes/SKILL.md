---
name: generate-podcast-shownotes
description: "Generate an accurate Markdown ShowNotes timeline from a local podcast audio file or the latest episode in an RSS feed by producing timestamped speech transcription, locating semantic topic changes, writing concise section summaries, and validating the final timecodes. Use when the user asks to 为播客音频生成时间轴、章节时间码、音频章节、shownotes timestamps, or test the latest 议正言辞 episode from Xiaoyuzhou RSS."
---

# Generate Podcast ShowNotes

## Respect project scope

Read the repository-root `AGENTS.md`, `README.md`, and `config.yml` before acting. Preserve unrelated worktree changes. This skill generates draft editorial material; it does not publish an episode, change podcast pages, upload audio, or edit an existing transcript unless the user separately requests that work.

The default Xiaoyuzhou RSS for 《议正言辞》 is `https://feed.xyzfm.space/fnejgl98kbk6`. Parse RSS as XML and use the newest item by `pubDate`; do not scrape the show page or infer the enclosure URL from a naming convention.

## Choose the source

- For a user-supplied MP3, M4A, WAV, or other supported audio file, use the local path exactly as supplied.
- When the user asks for the latest 《议正言辞》 episode, use the RSS URL above.
- For another feed, use the RSS URL the user supplies.
- Download remote audio only to a system temporary directory. Never add source audio, model files, or raw transcription artifacts to the repository.

If a matching public transcript exists in `content/post/`, use it to correct names, case citations, and other proper nouns after transcription. Never derive timecodes from the written transcript: edited prose can omit, reorder, or rewrite the recording.

## Produce the timestamped transcript

Run the bundled transcriber from the repository root. `uv` keeps the speech-to-text dependency outside this repository:

```powershell
uv run --python 3.12 --with faster-whisper .agents/skills/generate-podcast-shownotes/scripts/transcribe_audio.py `
  --rss-url "https://feed.xyzfm.space/fnejgl98kbk6" `
  --output "$env:TEMP/podcast-transcript.json" `
  --text-output "$env:TEMP/podcast-transcript.md" `
  --model small
```

For local audio, replace `--rss-url URL` with `--audio PATH`. Use `small` as the portable default. A larger model may improve names and uncommon vocabulary when suitable hardware and time are available; do not imply that model size removes the need for editorial checking. The script defaults to CPU `int8`; use its `--device` and `--compute-type` options only when the available runtime supports them.

The JSON output is the timing authority. The Markdown output is a readable view for semantic review. Record the detected duration, language, selected RSS item, model, and transcription warnings in the handoff.

## Build semantic chapters

Read the full timestamped transcript before selecting chapter boundaries. Identify changes in the episode's actual function: opening question, necessary background, a new person or event, a legal mechanism, a major turn, evaluation, or conclusion. Do not create chapters at uniform intervals.

Use these editorial defaults unless the user requests a different density:

- Start with `00:00`, describing the opening rather than the first transcribed word after music or silence.
- For a 25–40 minute narrative episode, prefer 7–12 entries. Scale the count to the amount of substantive topic change, not duration alone.
- Put each later timecode at the beginning of the first sentence that establishes the new section. Use word or segment timestamps from the JSON and record whole seconds.
- Keep adjacent chapters far enough apart to represent meaningful listening sections; merge entries that merely restate or illustrate the same point.
- Write one concrete, neutral summary per entry. Prefer names, events, institutions, or legal questions over generic labels such as “背景介绍” or “进一步讨论”.
- Keep the summaries faithful to what is spoken after that timecode. A written transcript may correct spelling, but must not add an unrecorded topic.
- Omit promotional boilerplate and routine closing requests unless they form a distinct, useful chapter.

For uncertain boundaries, inspect the transcript from roughly 20 seconds before to 20 seconds after the candidate time. Prefer the start of the transition sentence over the moment at which the new topic is already underway. Note any boundary that could not be confidently resolved; do not silently claim frame-level precision.

## Write and validate the result

Unless the user names another path, save repository-specific drafts as `podcast-drafts/episode-NN-shownotes.md`. For unrelated audio, save beside the user-designated output or return the timeline in chat. Use this exact copy-ready shape:

```markdown
## ShowNotes 时间轴

- 00:00 开场提出本期问题
- 03:42 第一个实质章节的具体内容
```

Validate the saved timeline against the transcription or RSS duration:

```powershell
python .agents/skills/generate-podcast-shownotes/scripts/validate_shownotes.py `
  podcast-drafts/episode-NN-shownotes.md `
  --duration HH:MM:SS `
  --transcript-json "$env:TEMP/podcast-transcript.json"
```

Fix every error before delivery. Treat validator warnings as prompts for editorial review rather than automatic failure. Finally sample at least three boundaries—an early, middle, and late entry—against the timestamped transcript. Report the source episode, duration, model, output path, entry count, validation result, and any material uncertainty.

## Completion criteria

- RSS metadata and enclosure came from the selected XML item, and a downloaded enclosure matched its declared byte length when one was provided.
- Every timecode is backed by a nearby audio-transcription boundary, begins at `00:00`, increases strictly, and falls inside the episode duration.
- Chapters reflect semantic transitions and their summaries match the following audio.
- Proper nouns were checked against an available canonical transcript without substituting prose-derived timings.
- Raw audio, speech-model files, and intermediate transcripts remain outside the repository.
- The Markdown timeline passes `validate_shownotes.py` and is ready to paste into episode ShowNotes.
