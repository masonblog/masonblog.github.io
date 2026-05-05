# AGENTS.md

## Project Overview

This repository is a Hugo static site for Mason's Blog, a Chinese-language personal blog using the PaperMod theme.

- Site config lives in `config.yml`.
- Source content lives in `content/`.
- Blog posts live in `content/post/`.
- Static assets live in `static/`.
- The active theme is the vendored `themes/PaperMod` directory.
- `public/` is generated build output and is ignored by Git.
- GitHub Pages deployment is automated through `.github/workflows/hugo.yml`.

The site is configured for `https://masonblog.github.io/`, uses PaperMod, enables emoji, raw HTML rendering, robots.txt, Google Analytics, and JSON output for search.

## Directory Guide

- `content/post/`: Markdown blog posts. Filenames generally follow `blogYYYYMMDD.md`.
- `content/about.md`: About page. This file currently uses TOML front matter.
- `content/search.md`: Search page using PaperMod's `search` layout.
- `content/archieves.md`: Archive page. Keep the existing filename unless intentionally migrating URLs/content.
- `static/images/`: Images served from `/images/...`. Post-specific images usually live in `static/images/<slug>/`.
- `static/favicon/`: Favicon files referenced by `config.yml`.
- `static/Ads.txt`: Ads.txt served as a static file.
- `layouts/partials/extend_head.html`: Site-level head extension. Currently loads Google AdSense.
- `assets/css/extended/tag-cover.css`: Site-level PaperMod CSS override for tag/list cover display.
- `themes/PaperMod/`: Active vendored theme. Avoid broad theme edits when a site-level override can solve the problem.
- `themes/PaperMod - backup/`: Backup copy of the theme. Do not edit unless explicitly asked.
- `.claude/settings.json`: Claude-specific local permission settings.
- `.github/workflows/hugo.yml`: Builds the Hugo site and deploys it to GitHub Pages with GitHub Actions.

## Content Conventions

New posts should normally use YAML front matter like:

```yaml
---
title: "文章标题"
date: 2026-05-05
slug: "blog20260505"
description: "文章摘要"
keywords: ["关键词1", "关键词2"]
draft: false
tags: ["科技分享"]
math: false
ShowToc: true
cover:
  image: "/images/blog20260505/cover.png"
---
```

Guidelines:

- Keep post filenames, slugs, and image folders aligned: `content/post/blogYYYYMMDD.md`, `slug: "blogYYYYMMDD"`, and `static/images/blogYYYYMMDD/`.
- Use absolute site paths for images in content and front matter, for example `/images/blog20260426/cover.png`.
- Prefer existing tag names unless introducing a deliberate new category. Common tags include `科技分享`, `时事评论`, `日记`, `读书笔记`, `教程`, `AI`, `财经`, and `人物`.
- Preserve the author's Chinese prose style. Edits should be light-touch unless the user asks for rewriting.
- Keep `draft: false` for published posts and `draft: true` for unpublished drafts.
- Use `ShowToc: true` on long structured posts; it is common in recent posts.
- Do not add licensing, sharing, donation, or promotional text that conflicts with the about page's stated preference: original content, no unauthorized republication, no tipping/sponsorship.

## Theme And Layout Notes

- Prefer site-level overrides in `layouts/`, `assets/`, or `static/` before modifying `themes/PaperMod/`.
- The active `extend_head.html` injects AdSense. Be careful not to duplicate script tags.
- `config.yml` has `markup.goldmark.renderer.unsafe: true`, so raw HTML can render in Markdown. Use this intentionally and sparingly.
- Search depends on `outputs.home` including `JSON` and `content/search.md` using `layout: "search"`.
- External link behavior may be customized in the theme's `_markup/render-link.html`; check before changing link rendering.

## Build And Verification

Use Hugo commands from the project root:

```powershell
hugo server -D
hugo --cleanDestinationDir
```

Notes:

- `hugo server -D` is for local preview, including drafts.
- `hugo --cleanDestinationDir` builds the static site into `public/`.
- In this environment, `hugo` may not be installed or available on `PATH`; if so, report that clearly instead of inventing a successful build.
- After content or config changes, verify at least that front matter is valid YAML/TOML and image paths point to files under `static/`.

## Editing Rules

- Do not hand-edit generated files in `public/` unless the user explicitly asks.
- Do not modify both `themes/PaperMod/` and `themes/PaperMod - backup/` in a routine change.
- Avoid sweeping formatting changes across old posts; many posts are archival and should remain stable.
- Be careful with YAML indentation in `config.yml` and post front matter.
- Keep file encodings compatible with existing Chinese content.
- If adding images, place source assets under `static/images/...`; generated copies under `public/images/...` are produced by Hugo.

## Useful Checks

When analyzing changes, these commands are helpful:

```powershell
rg --files
rg "draft: true|draft = true" content
rg "/images/" content
```

For structure checks, inspect:

```powershell
Get-Content -Raw config.yml
Get-Content -Raw content\search.md
Get-ChildItem static\images
```

## Deployment Assumptions

The deployment model is source-based and already active on GitHub:

- The repository `masonblog/masonblog.github.io` now stores Hugo source on `main`, not prebuilt HTML.
- GitHub Pages is configured with `build_type: workflow`, not legacy branch publishing.
- On push to `main`, `.github/workflows/hugo.yml` installs Hugo `0.161.1`, builds the site, uploads the generated `public/` artifact, and deploys it with GitHub Pages.
- The last verified migration commit was `4de52a7 Migrate site to Hugo source deployment`.
- A manual workflow dispatch after switching Pages to workflow mode completed successfully and restored `https://masonblog.github.io/`.

Local workspace note:

- In the outer local folder `C:\Users\huyun\Documents\GitHub\hugo\Mason's Blog`, the sibling/top-level `public/` path is this Git checkout.
- When working inside this repository checkout, local Hugo builds write generated files to `public/`; those files are ignored and should not be committed.
- Avoid returning to the old manual pattern of committing generated HTML to the root of `masonblog.github.io`.
