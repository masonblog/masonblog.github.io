# AGENTS.md

## Project Overview

This repository is a Hugo static site for Mason's Blog, a Chinese-language personal blog using the PaperMod theme.

- Site config lives in `config.yml`.
- Source content lives in `content/`.
- Blog posts live in `content/post/`.
- Static assets live in `static/`.
- The active theme is the vendored `themes/PaperMod` directory.
- `public/` and `resources/` are generated build outputs and should usually not be edited by hand.
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

- Do not hand-edit generated files in `public/` or `resources/` unless the user explicitly asks.
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

The preferred deployment model is now source-based:

- Commit the Hugo source project, including `content/`, `config.yml`, `layouts/`, `assets/`, `static/`, `themes/PaperMod/`, `.gitignore`, and `.github/workflows/hugo.yml`.
- Do not commit `public/` from the source repository; it is ignored and generated by the workflow.
- Configure GitHub Pages to use `GitHub Actions` as the publishing source.
- On push to `main`, `.github/workflows/hugo.yml` builds the site and deploys the generated `public/` artifact.

This workspace also contains a legacy nested Git repository under `public/` pointing to `masonblog/masonblog.github.io`. Treat that as the old manual publishing path and avoid changing it unless the user explicitly asks to keep or remove the legacy setup.
