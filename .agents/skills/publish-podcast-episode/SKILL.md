---
name: publish-podcast-episode
description: "Publish a new episode of the 议正言辞 podcast from a Markdown transcript into this Hugo repository by verifying current Xiaoyuzhou and Apple episode metadata, mirroring the Xiaoyuzhou RSS audio enclosure to the masonhu Cloudflare R2 bucket, freezing the Xiaoyuzhou RSS fields for the backup feed, creating paired Chinese and English blog posts, embedding the Chinese audio player, generating and saving a GPT cover, updating both podcast pages, connecting episode and transcript links, and validating the multilingual build and podcast RSS. Use when the user asks to 按老规矩发布播客文稿, publish or backfill a new 议正言辞 episode, update the bilingual podcast pages, generate an episode cover, repair links between an episode and its transcript, or synchronize the blog backup podcast feed."
---

# Publish Podcast Episode

## Respect project authority

Read the repository-root `AGENTS.MD`, `README.md`, and `config.yml` before editing. Treat `AGENTS.MD` as authoritative; use this skill as the podcast-specific extension of those rules. Preserve unrelated worktree changes.

## Inspect the current pattern

Read these files before choosing names or copy:

- `content/podcast.md`
- `content/podcast.en.md`
- `content/post/blog20260722.md` and `content/post/blog20260722.en.md` as the canonical episode-page shell
- The newest public podcast transcript pair in `content/post/` for current editorial and body-structure conventions
- The supplied source transcript

When a newer draft or episode conflicts with episode 11 on title prefixes, page preambles, player placement, or podcast-list entry structure, follow episode 11 unless the user explicitly adopts a newer convention.

Run `git status --short`. Do not overwrite an existing `blogYYYYMMDD` pair or image directory. If the episode date collides with an unrelated post basename, stop and ask the user to choose an alternate slug/date.

## Verify the public episode

Use the latest public episode metadata, not a related-episode link found inside the transcript.

1. Read the Xiaoyuzhou main RSS at `https://feed.xyzfm.space/fnejgl98kbk6` with an XML parser. Do not parse XML with regular expressions.
2. Check the Xiaoyuzhou show page at `https://www.xiaoyuzhoufm.com/podcast/68453dda5d66f3ec9a7aa1b4`. Resolve the Apple RSS feed, when needed, through `https://itunes.apple.com/lookup?id=6787849374&entity=podcast`, then inspect its `feedUrl`. Query `https://itunes.apple.com/lookup?id=6787849374&entity=podcastEpisode&limit=200`, match the exact episode title, and confirm that the result belongs to collection ID `6787849374`. Check the Spotify show page at `https://open.spotify.com/show/033N8EeYaxKaf8Xdd7yHSF`, match the exact episode title, and confirm that its link is an independent `/episode/` URL.
3. Match the episode by its exact title and capture:
   - Canonical Xiaoyuzhou episode URL without tracking parameters
   - Apple Podcasts episode `trackId` and `trackViewUrl`; preserve the `i=TRACK_ID` parameter when creating the Chinese `/cn/` and English `/us/` links
   - Canonical Spotify episode URL in the form `https://open.spotify.com/episode/EPISODE_ID`
   - RSS `guid` without modification
   - Full RSS `pubDate` string
   - Enclosure `url`, `type`, and integer `length`
   - Exact `itunes:duration`
   - Displayed duration in rounded minutes
   - Public episode description
4. Convert UTC timestamps to `Asia/Shanghai` before choosing `YYYY-MM-DD`.

If the episode is not publicly available or its identity is ambiguous, do not invent an ID, date, duration, or enclosure field. Report the missing fact and request the episode link.

## Mirror the episode audio to Cloudflare R2

After verifying the episode, download its RSS enclosure to a temporary file outside the repository and upload it to the `masonhu` R2 bucket. This is a required release step.

1. Format `site.Params.podcast.audioURLPattern` with the episode number to obtain the public R2 URL. Use that URL path without the leading slash as the object key; with the current configuration, episode `NN` maps to `reasoned-talk-NN.m4a`.
2. Download the exact Xiaoyuzhou RSS enclosure URL. Confirm the temporary file length exactly equals the enclosure `length` before uploading.
3. If project dependencies are absent, run `npm ci --prefer-offline --no-audit --no-fund`. Use the repository-locked Wrangler and explicitly target remote storage:

```powershell
npx --no-install wrangler r2 object put "masonhu/$objectKey" `
  --file $audioFile `
  --content-type $audioType `
  --remote
if ($LASTEXITCODE -ne 0) {
  throw "R2 audio upload failed"
}
```

Here `$objectKey` comes from the configured public R2 URL, `$audioFile` is the temporary download, and `$audioType` is the enclosure MIME type. Do not substitute a related-episode asset, commit the audio file, omit `--remote`, expose Cloudflare credentials, or change the object naming convention independently of `audioURLPattern`.

4. Request the public R2 URL and confirm success, the expected MIME type, and a `Content-Length` equal to the enclosure `length`. Only then remove the temporary file. Treat download, authentication, upload, or verification failure as a release blocker; never report the episode as fully published while the R2 object is missing or mismatched.

## Create the Chinese post

Create `content/post/blogYYYYMMDD.md` with:

```yaml
---
title: "议正言辞 NN｜不含期数前缀的标题"
date: YYYY-MM-DD
slug: "blogYYYYMMDD"
description: "与 content/podcast.md 对应列表项完全一致的纯文本单集简介。"
keywords: ["关键词"]
draft: false
tags: ["读书笔记", "播客"]
math: false
ShowToc: true
cover:
  image: "/images/blogYYYYMMDD/cover.png"
podcast:
  episode: NN
  title: "小宇宙 RSS 中的完整单集标题"
  description: >-
    本站播客页中的单集简介，并附本站文字稿链接
  guid: "RSS guid"
  published: "Full RSS pubDate"
  duration: "Exact itunes:duration"
  audioType: "Enclosure MIME type"
  audioLength: 12345678
---
```

Use integers for `episode` and `audioLength`; quote the scalar podcast fields and use a folded scalar for `description`. Preserve the Xiaoyuzhou RSS title exactly. The top-level `description` must exactly match the corresponding summary in `content/podcast.md`. Use that same local podcast page summary for `podcast.description`, followed by `本期文字稿` and the absolute local transcript URL. The on-page player and backup RSS enclosure URL are both generated from `site.Params.podcast.audioURLPattern`. Do not copy the `podcast` block to the English post.

Immediately after the front matter, insert exactly one `{{< podcast-player >}}`, followed by any episode-specific correction note and then the article body. Do not add a podcast-hub or external-listening preamble to the Chinese post; episode 11 establishes the player-first Chinese layout.

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

- Use the title pattern `Podcast NN｜Natural English episode title`.
- Make the front-matter `description` exactly match the corresponding plain-text summary in `content/podcast.en.md`. Do not append transcript boilerplate there; the fixed body preamble supplies that context.
- Translate `title`, `description`, `keywords`, `tags`, headings, body, and Shownotes into natural English.
- Preserve the Chinese post’s structure and substance.
- Do not add podcast front matter or the podcast player shortcode; the English translation must not become a duplicate RSS episode.
- Use `Reasoned Talk` with exactly this capitalization as the established English podcast name.
- Immediately after the front matter, use this fixed preamble:

```markdown
> This is the transcript of episode NN of my podcast [*Reasoned Talk*](/en/podcast/) (议正言辞). Listen on [Xiaoyuzhou](CANONICAL_XIAOYUZHOU_URL) or [Apple Podcasts](APPLE_PODCASTS_EPISODE_URL_US). The episode is in Chinese; this transcript has been translated into English.
```

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

Keep the existing `.episode-listen` CSS and use these exact entry shells. For Chinese:

```markdown
### [NN 中文单集标题](/post/blogYYYYMMDD/)

YYYY-MM-DD · NN 分钟 · <span class="episode-listen"><a href="CANONICAL_XIAOYUZHOU_URL" target="_blank" rel="noopener" aria-label="小宇宙"><img src="/images/podcast/Xiaoyuzhou_Icon.png" alt="小宇宙"></a><a href="APPLE_PODCASTS_EPISODE_URL_CN" target="_blank" rel="noopener" aria-label="Apple Podcasts"><img src="/images/podcast/Apple_Podcasts_Icon.png" alt="Apple Podcasts"></a><a href="SPOTIFY_EPISODE_URL" target="_blank" rel="noopener" aria-label="Spotify"><img src="/images/podcast/Spotify_Icon.png" alt="Spotify"></a></span>

简洁的中文单集简介。
```

For English:

```markdown
### [NN Natural English episode title](/en/post/blogYYYYMMDD/)

YYYY-MM-DD · NN min · <span class="episode-listen"><a href="CANONICAL_XIAOYUZHOU_URL" target="_blank" rel="noopener" aria-label="Xiaoyuzhou"><img src="/images/podcast/Xiaoyuzhou_Icon.png" alt="Xiaoyuzhou"></a><a href="APPLE_PODCASTS_EPISODE_URL_US" target="_blank" rel="noopener" aria-label="Apple Podcasts"><img src="/images/podcast/Apple_Podcasts_Icon.png" alt="Apple Podcasts"></a><a href="SPOTIFY_EPISODE_URL" target="_blank" rel="noopener" aria-label="Spotify"><img src="/images/podcast/Spotify_Icon.png" alt="Spotify"></a></span>

Concise natural-English episode summary, exactly matching the English post's top-level `description`.
```

Keep both language summaries in plain text without Markdown emphasis so the same text renders cleanly in post-header descriptions.

The heading link is the transcript link. Put Xiaoyuzhou, Apple, and Spotify listening links only in the icon row; do not link the heading to a listening platform or add a separate text transcript link.

## Validate the release

Check all of the following:

- Chinese and English front matter parses.
- Each post's top-level `description` exactly matches the corresponding summary on its language's podcast page.
- Cover file exists and both posts reference it.
- The Chinese post title begins `议正言辞 NN｜`; the English title begins `Podcast NN｜`.
- The Chinese post begins with the player and does not add an external-listening preamble.
- The English post contains the fixed `Reasoned Talk` preamble linking the English podcast hub, canonical Xiaoyuzhou episode, and Apple Podcasts.
- Each podcast-page heading links to the correct-language local transcript.
- Each podcast-page metadata row contains the canonical Xiaoyuzhou link, the language-appropriate Apple Podcasts episode link with the matched `i=TRACK_ID` parameter, and the canonical Spotify `/episode/` link in the existing inline icon shell; no platform may fall back to its show page.
- The Chinese post contains one `podcast` block and one `podcast-player` shortcode; the English post contains neither.
- Hugo recognizes the two posts as translations and renders language switching.
- `/post/blogYYYYMMDD/`, `/en/post/blogYYYYMMDD/`, `/podcast/`, and `/en/podcast/` render.
- `/podcast/index.xml` parses as RSS 2.0 and contains the new episode exactly once.
- The backup item’s title, GUID, `pubDate`, enclosure type/length, and duration exactly match the Xiaoyuzhou main RSS; its description matches the local podcast page summary and links to the local transcript.
- The Xiaoyuzhou enclosure download and the uploaded `masonhu` R2 object both have the RSS enclosure’s exact byte length.
- The on-page player and backup enclosure URLs match `site.Params.podcast.audioURLPattern`; requesting that public R2 object succeeds and returns the expected MIME type and content length.
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
- R2 bucket, object key, public URL, MIME type, and verified byte length
- Cover generation method, final prompt, and saved path
- Build, rendered-link (including Spotify show and episode links), player, and backup RSS results
- Any source corrections or unresolved factual caveats

Do not commit, push, or trigger deployment unless the user explicitly asks. A live release occurs only after the resulting changes reach `main` through the repository’s normal Git workflow.
