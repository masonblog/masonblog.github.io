# AGENTS.MD

本文件为后续在本仓库工作的 AI 代理提供项目约定。修改前请先阅读根目录 `README.md`、`config.yml`，以及与任务相关的内容文件。

## 项目概况

- 本仓库是 Mason's Blog 的 Hugo 静态站点源码，线上地址为 `https://masonblog.github.io/`，备用地址为 `https://blog.masonhu.xyz/`。
- 站点使用 Hugo Extended `0.161.1`，主题通过 Hugo Modules 引入 `github.com/adityatelange/hugo-PaperMod`。
- 站点已启用 Hugo 多语言：`zh` 为默认语言并保留根路径，`en` 输出到 `/en/`；语言菜单、首页描述等语言相关配置位于 `config.yml` 的 `languages` 下。
- 主题依赖记录在 `go.mod`，部署由 `.github/workflows/deploy.yml` 在 `main` 分支推送后自动完成。
- 这是个人博客，不是通用内容平台。文字、图片、个人材料默认不授权转载或商用。

## 目录约定

- `content/post/`：博客文章，中文文件名通常为 `blogYYYYMMDD.md`；英文译文使用同 basename 的 `.en.md`，例如 `blog20260514.en.md`；历史私密文章多带 `-private-NN` 后缀。
- `content/about.md`、`content/search.md`、`content/portfolio.md`、`content/archieves.md`：中文独立页面；对应英文页使用 `.en.md` 后缀，例如 `about.en.md`、`search.en.md`。
- `static/images/`：文章和站点图片。新文章图片优先放在 `static/images/blogYYYYMMDD/`。
- `static/favicon/`：站点图标资源。
- `layouts/`：对 PaperMod 的局部覆盖。
- `assets/css/extended/`：站点级 CSS 扩展。
- `config.yml`：站点菜单、参数、输出格式、Hugo Module 等全局配置。

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

- 修改 `config.yml`、`layouts/`、`assets/css/extended/` 或 Hugo Module 版本后，务必至少运行一次生产构建。
- 修改文章内容时，至少确认 front matter 语法有效，图片路径存在，站内链接没有明显拼写错误；新增英文页时还要抽查 `/en/` 路径、语言切换和对应中文页的翻译关系。
- 不要提交 `public/`、`resources/` 等 Hugo 本地构建产物，除非任务明确要求。

## 依赖与部署注意事项

- 不要随意升级 Hugo、PaperMod、GitHub Actions 版本；升级前应说明原因并验证构建。
- `go.mod` 中的 PaperMod 版本是站点主题来源。修改主题行为时，优先通过 `layouts/` 覆盖或 `assets/css/extended/` 扩展，避免直接引入主题源码副本。
- `.github/workflows/deploy.yml` 使用 Hugo Extended Debian 包，部署目标是 GitHub Pages 和 Cloudflare Workers。保持 workflow 的 Pages 权限、artifact 上传和 Workers 部署步骤完整。
- `outputs.home` 中的 `JSON` 用于中英文搜索功能，不要移除；多语言构建应同时生成根路径中文搜索索引和 `/en/` 英文搜索索引。
- `markup.goldmark.renderer.unsafe: true` 允许文章中的原始 HTML；删除前需检查历史文章和页面是否依赖该行为。

## Git 工作规范

- 修改前查看当前工作区状态，避免覆盖用户未提交的改动。
- 只改与任务相关的文件；不要顺手格式化大量历史文章或资源。
- 对内容修改，提交说明应能看出影响范围，例如 `Update about page copy`、`Add blog post assets`。
- 若任务涉及敏感个人信息、版权材料或法律结论，完成前再次核对是否确有必要公开。
