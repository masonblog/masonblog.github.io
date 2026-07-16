# <img src="static/images/mason.png" alt="Mason's Blog Logo" width="36" height="36" /> Mason's Blog｜分享知识与个人叙事

[![Hugo](https://img.shields.io/badge/Hugo-0.164.0-FF4088?logo=hugo&logoColor=white)](https://gohugo.io/) [![PaperMod](https://img.shields.io/badge/Theme-PaperMod-2ea44f)](https://github.com/adityatelange/hugo-PaperMod) [![Cloudflare Workers](https://img.shields.io/badge/Hosted_on-Cloudflare_Workers-F38020?logo=cloudflareworkers&logoColor=white)](https://workers.cloudflare.com/) [![GitHub Actions](https://img.shields.io/badge/Deploy-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions) [![GitHub Pages](https://img.shields.io/badge/Mirror-GitHub_Pages-222222?logo=github&logoColor=white)](https://pages.github.com/)

这里是 [Mason's Blog](https://blog.masonhu.cc/) 的源码仓库。它是一个用 Hugo 搭建的双语个人博客，用来记录一些零碎的经历和想法，也存放个人作品集和播客文稿。中文站保留在根路径，英文站输出到 `/en/`。

[博客地址](https://blog.masonhu.cc/)｜[英文版](https://blog.masonhu.cc/en/)｜[备份地址](https://masonblog.github.io/)

## 关于作者

作者 Mason，法律硕士毕业，一个为了自己与家庭的未来努力谋生的 90 后，稍微带点理想主义。

我热爱历史与文学，对 IT 也颇有兴趣，曾利用业余时间参与制作 [《东亚观察局》](https://podcasts.apple.com/us/podcast/%E4%B8%9C%E4%BA%9A%E8%A7%82%E5%AF%9F%E5%B1%80/id1508293790)，以选出令人惊艳的片尾曲为乐。目前在运营不温不火的个人播客 [《议正言辞》](https://www.xiaoyuzhoufm.com/podcast/68453dda5d66f3ec9a7aa1b4)和 Bilibili 频道 [MasonTV](https://space.bilibili.com/492153853)。

联系邮箱：me@masonhu.cc

## 关于博客

本博客用于记录一些零碎的经历和想法，以及偶有的牢骚和絮叨。同时，这里还会存放我自己开发的技能和小工具，以及个人播客《议正言辞》的文稿等。它不追求传播学意义上的价值，更像一个长期保存个人经验和思考的树洞。

本博客建立于 2020 年新冠疫情期间。凡 2020 年 1 月 1 日前的文章，均为博客创建以前撰写的个人历史文章。 **受限于年龄和视野，该部分文章的可读性不高，且部分态度和观点已不被当前的作者所坚持或接受**。本博客不接受针对文章的打赏与资助，也不希望被推荐给更多的人。若你偶然来到这里，安静阅读就很好。

## 多语言结构

站点使用 Hugo 原生多语言能力：`zh` 是默认语言并保留根路径，`en` 输出到 `/en/`。语言相关菜单和首页文案配置在 `config.yml` 的 `languages` 下；PaperMod 会根据同 basename 的内容文件识别对应翻译。英文译文保留原文的日期、slug、封面和结构性 front matter，以便中英文页面保持稳定的一一对应关系。

## 目录结构

- `content/post/`：博客文章及对应英文译文
- `content/about.md` / `content/about.en.md`：关于页
- `content/portfolio.md` / `content/portfolio.en.md`：作品集页
- `static/images/`：图片资源，中英文内容共用同一套图片路径
- `layouts/`：站点级布局覆盖
- `assets/css/extended/`：站点级 CSS 扩展

## 自动部署

推送到 `main` 分支后，`.github/workflows/deploy.yml` 会自动：

1. 安装指定版本的 Hugo。
2. 通过 Hugo Modules 拉取 `go.mod` 中固定版本的 PaperMod 主题。
3. 构建静态站点，并同时生成根路径中文页面与 `/en/` 英文页面。
4. 上传 Pages artifact。
5. 将主站部署到 Cloudflare Workers，并部署 GitHub Pages 备份站。

## 版权说明

除非文章内另有说明，本博客文字内容均为作者原创，禁止未经许可转载、摘编或用于商业用途。

仓库中的主题代码遵循其原项目许可证；博客文章、图片和个人内容不因仓库公开而自动授权复用。
