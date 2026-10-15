# 轻敲 · 打字练习

Chrome / Edge Manifest V3 扩展。六篇分级文章、逐字符反馈、实时速度及准确率；无需网络或额外权限。

## 安装

下载 docs/qingqiao-v1.0.0.zip 并解压。在 chrome://extensions 或 edge://extensions 开启开发者模式，加载包含 manifest.json 的文件夹。点击扩展工具栏图标开始练习。

## 发布介绍页

将本目录内容上传 GitHub 仓库，在 Settings → Pages 选择 Deploy from a branch，选择 main 分支的 /docs 文件夹并保存。介绍页下载按钮使用同目录真实 ZIP 文件。

extension/ 为插件源码；docs/ 为介绍页和安装包。插件脚本使用独立文件，兼容扩展的内容安全策略。

