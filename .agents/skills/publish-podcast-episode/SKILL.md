---
name: publish-podcast-episode
description: "Publish a new episode of the 议正言辞 podcast from a Markdown transcript into this Hugo repository by verifying current Xiaoyuzhou and Apple episode metadata, freezing the Xiaoyuzhou RSS fields for the backup feed, creating paired Chinese and English blog posts, embedding the Chinese audio player, generating and saving a GPT cover, updating both podcast pages, connecting episode and transcript links, and validating the multilingual build and podcast RSS. Use when the user asks to 按老规矩发布播客文稿, publish or backfill a new 议正言辞 episode, update the bilingual podcast pages, generate an episode cover, repair links between an episode and its transcript, or synchronize the blog backup podcast feed."
---

# Publish Podcast Episode

## Respect project authority

Read the repository-root `AGENTS.MD`, `README.md`, and `config.yml` before editing. Treat `AGENTS.MD` as authoritative; use this skill as the podcast-specific extension of those rules. Preserve unrelated worktree changes.

## Inspect the current pattern

Read these files before choosing names or copy:

- `content/podcast.md`
- `content/podcast.en.md`
- The newest public podcast transcript pair in `content/post/`
- The supplied source transcript

Run `git status --short`. Do not overwrite an existing `blogYYYYMMDD` pair or image directory. If the episode date collides with an unrelated post basename, stop and ask the user to choose an alternate slug/date.

## Verify the public episode

Use the latest public episode metadata, not a related-episode link found inside the transcript.

1. Read the Xiaoyuzhou main RSS at `https://feed.xyzfm.space/fnejgl98kbk6` with an XML parser. Do not parse XML with regular expressions.
2. Check the Xiaoyuzhou show page at `https://www.xiaoyuzhoufm.com/podcast/68453dda5d66f3ec9a7aa1b4`. Resolve the Apple RSS feed, when needed, through `https://itunes.apple.com/lookup?id=6787849374&entity=podcast`, then inspect its `feedUrl`.
3. Match the episode by its exact title and capture:
   - Canonical Xiaoyuzhou episode URL without tracking parameters
   - RSS `guid` without modification
   - Full RSS `pubDate` string
   - Enclosure `url`, `type`, and integer `length`
   - Exact `itunes:duration`
   - Displayed duration in rounded minutes
   - Public episode description
4. Convert UTC timestamps to `Asia/Shanghai` before choosing `YYYY-MM-DD`.

If the episode is not publicly available or its identity is ambiguous, do not invent an ID, date, duration, or enclosure field. Report the missing fact and request the episode link.

## Create the Chinese post

Create `content/post/blogYYYYMMDD.md` with:

```yaml
---
title: "不含期数前缀的标题"
date: YYYY-MM-DD
slug: "blogYYYYMMDD"
description: "自然摘要，并注明这是《议正言辞》第 NN 期文字稿。"
keywords: ["关键词"]
draft: false
tags: ["读书笔记"]
math: false
ShowToc: true
cover:
  image: "/images/blogYYYYMMDD/cover.png"
podcast:
  episode: NN
  guid: "RSS guid"
  published: "Full RSS pubDate"
  duration: "Exact itunes:duration"
  audioURL: "Full enclosure URL"
  audioType: "Enclosure MIME type"
  audioLength: 12345678
---
```

Use integers for `episode` and `audioLength`; quote all other podcast fields. Preserve the enclosure URL exactly as published by Xiaoyuzhou. Do not copy the `podcast` block to the English post.

Immediately after the front matter, link the podcast hub, the canonical Xiaoyuzhou episode, and Apple Podcasts. Follow the wording used by the newest transcript, then insert `{{< podcast-player >}}` before the article body.

Turn the spoken transcript into a readable post without changing the author’s position:

- Remove source-only wrappers such as the top-level episode title, `节目简介`, and `逐字稿` headings.
- Normally omit routine spoken greetings and farewells.
- Add restrained `##` headings where the argument or narrative changes.
- Preserve substantive examples, quotations, and Shownotes.
- Convert Shownotes into article sections when the recent post pattern does so.
- Correct only clear typos, dates, names, case roles, or legal citations; disclose material corrections in the handoff.
- Do not turn the prose into promotional copy or silently shorten the argument.

## Create the English translation

Create `content/post/blogYYYYMMDD.en.md` with the same basename and the same structural fields: `date`, `slug`, `draft`, `math`, `ShowToc`, and `cover`.

- Translate `title`, `description`, `keywords`, `tags`, headings, body, and Shownotes into natural English.
- Preserve the Chinese post’s structure and substance.
- Do not add podcast front matter or the podcast player shortcode; the English translation must not become a duplicate RSS episode.
- Use the podcast name and capitalization already established in the repository.
- State that the episode audio is in Chinese and the transcript is translated.
- Link the English podcast hub at `/en/podcast/`.
- Keep case names, citations, product names, and URLs technically accurate.

## Generate and save the cover

Use the installed `imagegen` skill and its built-in image generation path unless the user explicitly requests another method.

1. Inspect the newest podcast covers to match the site’s visual language.
2. Generate one polished 16:9 landscape image suitable for a Hugo cover, normally without embedded text, logos, or watermarks.
3. Base the scene on the episode’s central historical or legal conflict. Avoid sensationalism and avoid presenting a generated face as an exact historical likeness unless requested.
4. Inspect the result and iterate only when a specific defect matters.
5. Save the final file as `static/images/blogYYYYMMDD/cover.png` and reference it with `/images/blogYYYYMMDD/cover.png` in both posts.

Never leave a project-referenced image only in the generator’s cache directory.

## Update both podcast pages

Insert the new episode first under the episode-list heading in both `content/podcast.md` and `content/podcast.en.md`.

Use this structure:

```markdown
### [NN Episode title](CANONICAL_XIAOYUZHOU_URL)

YYYY-MM-DD · NN 分钟 · [文字稿](/post/blogYYYYMMDD/)

Concise description based on the public episode description.
```

For English, use `NN min`, `[Transcript](/en/post/blogYYYYMMDD/)`, and a natural English title and summary. Keep the episode title linked to Xiaoyuzhou and the transcript link pointed to the new local post.

## Validate the release

Check all of the following:

- Chinese and English front matter parses.
- Cover file exists and both posts reference it.
- Both posts link to the canonical episode.
- Both podcast pages link back to the correct language transcript.
- The Chinese post contains one `podcast` block and one `podcast-player` shortcode; the English post contains neither.
- Hugo recognizes the two posts as translations and renders language switching.
- `/post/blogYYYYMMDD/`, `/en/post/blogYYYYMMDD/`, `/podcast/`, and `/en/podcast/` render.
- `/podcast/index.xml` parses as RSS 2.0 and contains the new episode exactly once.
- The backup item’s GUID, `pubDate`, enclosure URL/type/length, and duration exactly match the Xiaoyuzhou main RSS.
- `/index.xml` remains the blog RSS, and `/en/podcast/index.xml` does not exist.
- The local Hugo Extended binary exactly matches `.github/workflows/deploy.yml` → `env.HUGO_VERSION`.
- `git diff --check` passes and `git status --short` contains only intended changes.

Read the required Hugo version from the deployment workflow; do not duplicate a version number in this skill. Resolve the intended Hugo executable, compare its reported version, and only then run the production build:

```powershell
$workflow = Get-Content -Raw ".github/workflows/deploy.yml"
$match = [regex]::Match(
  $workflow,
  '(?m)^\s*HUGO_VERSION:\s*["'']?([0-9]+\.[0-9]+\.[0-9]+)["'']?\s*$'
)
if (-not $match.Success) {
  throw "Cannot determine env.HUGO_VERSION from .github/workflows/deploy.yml"
}
$requiredHugoVersion = $match.Groups[1].Value

$hugo = (Get-Command hugo -ErrorAction SilentlyContinue).Source
if (-not $hugo) {
  throw "Hugo Extended $requiredHugoVersion is not on PATH; locate or install that exact version before building"
}

$actualHugoVersion = & $hugo version
if ($actualHugoVersion -notmatch "^hugo v$([regex]::Escape($requiredHugoVersion))\b") {
  throw "Hugo version mismatch: project requires $requiredHugoVersion; found $actualHugoVersion"
}
if ($actualHugoVersion -notmatch "\+extended\b") {
  throw "The project requires Hugo Extended; found $actualHugoVersion"
}

& $hugo --gc --minify
```

Treat `.github/workflows/deploy.yml` as the executable source of truth for the build version. If Hugo is not on `PATH`, locate an exact-version local binary before downloading anything, set `$hugo` to that executable, and run the same comparison. Do not validate with a different Hugo version or upgrade project dependencies. If README or `AGENTS.MD` names a different version, report the documentation drift instead of silently choosing it for the build. Prefer an output/cache directory outside the repository when the environment permits. Remove only verification artifacts created during this run; never delete pre-existing `public/`, `resources/`, or `go.sum` blindly.

## Finish safely

Report:

- Created and updated file paths
- Verified episode date, duration, canonical URL, GUID, and enclosure metadata
- Cover generation method, final prompt, and saved path
- Build, rendered-link, player, and backup RSS results
- Any source corrections or unresolved factual caveats

Do not commit, push, or trigger deployment unless the user explicitly asks. A live release occurs only after the resulting changes reach `main` through the repository’s normal Git workflow.
