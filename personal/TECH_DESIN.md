# TECH_DESIN
采用原生 HTML、CSS、JavaScript，无构建依赖。index.html 展示，admin.html 管理，app.js 负责校验、渲染及持久化，style.css 提供响应式样式。
存储键 personal.portfolio.v1。JSON 包含 name/title/bio/about/email/location/skills/projects/avatar/resume；文件转为 Data URL。头像限制 PNG/JPEG/WebP 1MB，PDF 2MB；存储配额错误显示在状态栏。
所有文本通过 textContent 渲染；项目外链仅允许 HTTP(S)，新窗口设置 noopener noreferrer；导入执行结构及文件类型校验。管理页无密码，因为纯前端无法提供可信鉴权。
运行：在本目录运行 python -m http.server 8080，访问 http://localhost:8080。也可使用任意静态服务器。
Cloudflare Pages：连接 GitHub 仓库，构建命令留空，输出目录设为 /（仓库根目录为 personal 时）。直接上传可用 npx wrangler pages deploy . --project-name personal-portfolio，需先登录 Cloudflare。不要上传凭据。
公开初始内容在 app.js 的 defaults 中维护。浏览器备份可用于迁移本地修改，不会自动写入静态服务器文件。
