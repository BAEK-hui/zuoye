// 点击工具栏图标，在新标签页打开练习。
chrome.action.onClicked.addListener(() => { chrome.tabs.create({url:chrome.runtime.getURL('practice.html')}); });

