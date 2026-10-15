const fs = require('fs');
const base = 'typing-extension/';
const html = fs.readFileSync(base+'extension/practice.html','utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/);
fs.writeFileSync(base+'extension/practice.js',match[1]);
fs.writeFileSync(base+'extension/practice.html',html.replace(match[0],'<script src="practice.js"></script>'));
fs.writeFileSync(base+'extension/manifest.json',JSON.stringify({manifest_version:3,name:'轻敲 · 打字练习',version:'1.0.0',description:'六篇分级文章，实时速度、准确率与逐字反馈。离线可用。',action:{default_title:'打开轻敲打字练习'},background:{service_worker:'background.js'}},null,2));
fs.writeFileSync(base+'extension/background.js',"// 点击工具栏图标，在新标签页打开练习。\nchrome.action.onClicked.addListener(() => { chrome.tabs.create({url:chrome.runtime.getURL('practice.html')}); });\n");

