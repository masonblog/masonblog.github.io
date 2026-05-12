# <img src="static/images/mason.png" alt="Mason's Blog Logo" width="36" height="36" /> Mason's Blog

知识分享与微小叙事。

[![Hugo](https://img.shields.io/badge/Hugo-0.161.1-FF4088?logo=hugo&logoColor=white)](https://gohugo.io/) [![PaperMod](https://img.shields.io/badge/Theme-PaperMod-2ea44f)](https://github.com/adityatelange/hugo-PaperMod) [![GitHub Pages](https://img.shields.io/badge/Hosted_on-GitHub_Pages-222222?logo=github&logoColor=white)](https://pages.github.com/) [![GitHub Actions](https://img.shields.io/badge/Deploy-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)

这里是 [Mason's Blog](https://masonblog.github.io/) 的源码仓库。它是一个用 Hugo 搭建的个人博客，用来记录一些零碎的新知识，也存放偶有的牢骚、絮叨和个人经历。

- 博客地址：[https://masonblog.github.io/](https://masonblog.github.io/)
- 备用地址：[https://blog.masonhu.xyz/](https://blog.masonhu.xyz/)

## 关于作者

作者 Mason，法律硕士毕业，一个为了自己与家庭的未来努力谋生的 90 后，稍微带点理想主义。

我热爱历史与文学，对 IT 也颇有兴趣，曾利用业余时间参与制作《东亚观察局》，目前在小宇宙更新个人播客《议正言辞》，聚焦东西方法制历史，试图将古罗马和 21 世纪的中国串联起来，探寻正义的漫长旅程。

联系邮箱：me@masonhu.xyz

## 关于这个博客

这个博客不追求传播学意义上的价值，更像一个长期保存个人经验和思考的树洞。内容主题比较杂，包括但不限于：

- 科技工具与建站记录
- 个人生活和日记
- 历史、法学与读书笔记
- 时事评论和社会观察
- AI 工具与个人项目实践

全部文章均为本人原创。如无特别说明，均禁止转载。

本博客建立于 2020 年新冠疫情期间。凡 2020 年 1 月 1 日前的文章，均为博客创建以前撰写的个人历史文章。受限于年龄和视野，该部分文章的可读性不高，且部分态度和观点已不被当前的作者所坚持或接受。

本博客不接受针对文章的打赏与资助，也不希望被推荐给更多的人。若你偶然来到这里，安静阅读就很好。

## 目录结构

- `content/post/`：博客文章
- `content/about.md`：关于页
- `static/images/`：图片资源
- `layouts/`：站点级布局覆盖
- `assets/css/extended/`：站点级 CSS 扩展

## 自动部署

推送到 `main` 分支后，`.github/workflows/hugo.yml` 会自动：

1. 安装指定版本的 Hugo/Go/Hugo Modules。
2. 构建静态站点。
3. 上传 Pages artifact。
4. 部署到 GitHub Pages。

## 版权说明

除非文章内另有说明，本博客文字内容均为作者原创，禁止未经许可转载、摘编或用于商业用途。

仓库中的主题代码遵循其原项目许可证；博客文章、图片和个人内容不因仓库公开而自动授权复用。
