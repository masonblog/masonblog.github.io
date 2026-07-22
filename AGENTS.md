# AGENTS.md

本文件为后续在本仓库工作的 AI 代理提供项目约定。修改前请先阅读根目录 `README.md`、`config.yml`，以及与任务相关的内容文件。

## 项目概况

- 本仓库是 Mason's Blog 的 Hugo 静态站点源码，主要地址为 `https://blog.masonhu.cc/`，备用地址为 `https://masonblog.github.io/`。
- 站点使用 Hugo Extended `0.164.0`，主题通过 Hugo Modules 引入 `github.com/adityatelange/hugo-PaperMod`。
- 站点已启用 Hugo 多语言：`zh` 为默认语言并保留根路径，`en` 输出到 `/en/`；语言菜单、首页描述等语言相关配置位于 `config.yml` 的 `languages` 下。
- 主题依赖记录在 `go.mod`。向 `main` 分支推送站点内容、资源、配置或部署文件时，`.github/workflows/deploy.yml` 会自动部署；其他变更可按需通过 `workflow_dispatch` 手动触发。
- 这是个人博客，不是通用内容平台。文字、图片、个人材料默认不授权转载或商用。

## 目录约定

- `content/post/`：博客文章，中文文件名通常为 `blogYYYYMMDD.md`；英文译文使用同 basename 的 `.en.md`，例如 `blog20260514.en.md`；历史私密文章多带 `-private-NN` 后缀。
- `content/about.md`、`content/search.md`、`content/portfolio.md`、`content/archieves.md`：中文独立页面；对应英文页使用 `.en.md` 后缀，例如 `about.en.md`、`search.en.md`。
- `static/images/`：文章和站点图片。新文章图片优先放在 `static/images/blogYYYYMMDD/`。
- `static/favicon/`：站点图标资源。
- `layouts/`：对 PaperMod 的局部覆盖。
- `assets/css/extended/`：站点级 CSS 扩展。
- `.agents/skills/`：仓库级 Codex 技能。用于固化仅适用于本项目的可复用工作流。
- `config.yml`：站点菜单、参数、输出格式、Hugo Module 等全局配置。
- `package.json`、`package-lock.json`：Cloudflare 部署工具依赖；Wrangler 版本必须由二者共同固定。
- `wrangler.jsonc`：Cloudflare Workers 静态资源目录、路由和兼容日期配置。

## 项目级技能

- 新一期《议正言辞》的文稿发布与播客页同步使用 `.agents/skills/publish-podcast-episode/SKILL.md`。
- 当用户提出「按老规矩发布播客文稿」、发布或补发播客单集、生成单集封面、更新中英文播客页，或修复单集与文字稿之间的链接时，必须调用 `publish-podcast-episode` 技能。
- 下一期《议正言辞》的选题策划使用 `.agents/skills/select-podcast-topic/SKILL.md`。
- 当用户询问下一期播客讲什么、要求策划播客选题，或需要生成新单集标题、简介和深度研究报告提示词时，必须调用 `select-podcast-topic` 技能。
- 上述技能是本文件的播客专项扩展。执行技能前仍须遵守本文件；若两者冲突，以本文件和用户的当次明确要求为准。
- 若播客平台 ID、节目定位、内容目录、双语字段、选题输出、封面规则或构建命令发生变化，应同时更新本节与相关技能，避免项目约定分叉。

## 播客维护约定

- 《议正言辞》（英文名 `Reasoned Talk`）是一档聚焦东西方法律史的中文播客。中文入口为 `content/podcast.md`，英文入口为 `content/podcast.en.md`；中文页使用 `layout: podcast` 并声明 `outputs: [HTML, RSS]`，用于生成独立播客页与备份 RSS。
- 播客全局元数据维护在 `config.yml` 的 `params.podcast`，包括标题、简介、作者、邮箱、语言、分类、封面、R2 音频 URL 规则和 explicit/type 等 RSS 字段。平台收听入口目前包括小宇宙和 Apple Podcasts，页面按钮图片位于 `static/images/podcast/`。
- 单集中文文字稿存放在 `content/post/`，文件名沿用 `blogYYYYMMDD.md`；对应英文译文使用同 basename 的 `.en.md`。中文稿 front matter 必须包含 `podcast:` 子字段：`episode`、`title`、`description`、`guid`、`published`、`duration`、`audioType`、`audioLength`，并在正文顶部放置 `{{< podcast-player >}}`。
- `podcast.title`、`podcast.description`、`podcast.guid`、`podcast.published`、`podcast.duration`、`podcast.audioType`、`podcast.audioLength` 应与小宇宙主 RSS 保持一致，不要凭记忆改写。站内播放器与备用 RSS 的音频地址统一由 `params.podcast.audioURLPattern` 按期数生成，当前指向 R2 的 `https://podcast.masonhu.cc/reasoned-talk-NN.m4a`。
- 英文稿通常不携带 `podcast:` 字段，以免重复进入播客 RSS；开头需说明这是《议正言辞》对应单集的英文译文，音频为中文，并链接到英文播客页、小宇宙单集和 Apple Podcasts。
- 每次发布或补录单集，需要同步更新 `content/podcast.md` 与 `content/podcast.en.md` 的列表项，保持编号、标题、日期、时长、摘要、站内链接一致；中文链接指向 `/post/blogYYYYMMDD/`，英文链接指向 `/en/post/blogYYYYMMDD/`。
- 播客 RSS 模板在 `layouts/podcast.rss.xml`，播放器 shortcode 在 `layouts/shortcodes/podcast-player.html`，播放器样式在 `assets/css/extended/podcast.css`。修改这些文件后必须运行生产构建，并检查 `/podcast/index.xml` 是否仍包含 R2 enclosure、与小宇宙一致的单集标题和简介、itunes 字段，以及按集数倒序排列的条目。

## 内容编辑规则

- 保持作者个人写作风格，中文内容以自然、克制、清楚为主，不要改成营销口吻。
- 不要擅自重写历史文章、私密文章或作者观点；除非任务明确要求，只做局部修正。
- 2020 年 1 月 1 日前的历史文章有特殊说明，不要删除或淡化 README 和关于页中的相关免责声明。
- 新文章 front matter 参考现有文章：

```yaml
---
title: "文章标题"
date: YYYY-MM-DD
slug: "blogYYYYMMDD"
description: "一句话摘要"
keywords: ["关键词"]
draft: false
tags: ["标签"]
math: false
ShowToc: true
cover:
  image: "/images/blogYYYYMMDD/cover.png"
---
```

- 普通页面可使用更简洁的 front matter。若页面不应显示授权信息，可沿用 `noLicense: true`。
- 新增英文译文时，优先复制中文原文的 `date`、`slug`、`draft`、`math`、`ShowToc`、`cover` 等结构性字段，只翻译 `title`、`description`、`keywords`、`tags` 和正文；保持同 basename 以便 Hugo/PaperMod 自动建立翻译关系。
- 英文译文应忠实原文但使用自然英语表达，避免机器翻译腔；技术命令、文件路径、代码块和产品名通常不翻译。
- 只翻译公开内容；`draft: true`、明确 `hidden: true` 或历史私密文章暂不翻译，除非任务明确要求。
- 图片路径在 Markdown 和 front matter 中使用站点绝对路径，例如 `/images/blog20260514/cover.png`，对应文件位于 `static/images/blog20260514/cover.png`。
- 文章中如涉及法律、时事、技术版本、工具价格等可能变化的信息，修改前应核实来源和日期，避免制造过期结论。

## 开发与验证

- 本地预览：

```powershell
hugo server --buildDrafts
```

- 生产构建验证：

```powershell
hugo --gc --minify
```

- GitHub Pages 部署构建使用：

```bash
hugo --gc --minify --baseURL "${{ steps.pages.outputs.base_url }}/"
```

- Cloudflare Workers 部署构建使用：

```bash
hugo --gc --minify --baseURL "https://blog.masonhu.cc/"
```

- 修改 `package.json`、`package-lock.json`、`wrangler.jsonc` 或 Cloudflare 部署步骤后，还应验证部署依赖和 Wrangler 配置：

```bash
npm ci --prefer-offline --no-audit --no-fund
npx --no-install wrangler deploy --dry-run
```

- 修改 `config.yml`、`layouts/`、`assets/css/extended/` 或 Hugo Module 版本后，务必至少运行一次生产构建。
- 修改文章内容时，至少确认 front matter 语法有效，图片路径存在，站内链接没有明显拼写错误；新增英文页时还要抽查 `/en/` 路径、语言切换和对应中文页的翻译关系。
- 不要提交 `public/`、`resources/` 等 Hugo 本地构建产物，除非任务明确要求。

## 依赖与部署注意事项

- 不要随意升级 Hugo、PaperMod、GitHub Actions 版本；升级前应说明原因并验证构建。
- `go.mod` 中的 PaperMod 版本是站点主题来源。修改主题行为时，优先通过 `layouts/` 覆盖或 `assets/css/extended/` 扩展，避免直接引入主题源码副本。
- `.github/workflows/deploy.yml` 使用 Hugo Extended Debian 包。GitHub Pages 与 Cloudflare Workers 必须保持为互不依赖的并行任务，并分别使用备份站和主站的 `baseURL`。
- GitHub Pages 需要上传完整 Pages artifact；Cloudflare 应在同一任务中完成 checkout、Hugo 构建和 Wrangler 直接部署，不要重新引入 Cloudflare artifact 上传、下载或第二次 checkout。
- Wrangler 作为 devDependency 固定在 `package.json` 和 `package-lock.json` 中，并通过 `actions/setup-node` 缓存 npm 下载。升级 Wrangler 时必须同步更新 lockfile，运行 `npm ci` 和 `wrangler deploy --dry-run`。
- workflow 的 `paths` 过滤必须覆盖所有站点输入和部署配置；保留按分支划分的 `concurrency` 与 `cancel-in-progress`，避免连续推送部署旧版本。
- `outputs.home` 中的 `JSON` 用于中英文搜索功能，不要移除；多语言构建应同时生成根路径中文搜索索引和 `/en/` 英文搜索索引。
- `markup.goldmark.renderer.unsafe: true` 允许文章中的原始 HTML；删除前需检查历史文章和页面是否依赖该行为。

## Git 工作规范

- 修改前查看当前工作区状态，避免覆盖用户未提交的改动。
- 只改与任务相关的文件；不要顺手格式化大量历史文章或资源。
- 对内容修改，提交说明应能看出影响范围，例如 `Update about page copy`、`Add blog post assets`。
- 若任务涉及敏感个人信息、版权材料或法律结论，完成前再次核对是否确有必要公开。
