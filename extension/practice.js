
// 本练习按 Unicode 字符逐位比对，速度按正确字符数 / 分钟计算。
const original='清晨的阳光穿过树叶，落在安静的小路上。放慢脚步，感受微风，也给自己一点耐心。每一次专注的练习，都会让明天的你更加从容。';
// 不同难度提供不同篇幅、用词与标点；哈希路由支持浏览器前进、后退。
const lessons=[
 {id:'morning',title:'清晨小路',level:'简单',description:'日常短句，轻松热身。',text:original},
 {id:'weekend',title:'周末时光',level:'简单',description:'熟悉的生活词语，找到节奏。',text:'周末的午后，我坐在窗边读书。桌上放着一杯温水，窗外传来小鸟的叫声。读累了，就抬头看看蓝天。平凡的日子，也有许多值得珍惜的小事。'},
 {id:'journey',title:'山间来信',level:'中等',description:'更长的句子，练习连续输入。',text:'沿着山间的小径向前走，城市的喧闹渐渐远去。溪水绕过石头，在树影之间闪着细碎的光。我们停在一座木桥旁，打开地图，商量接下来的路线。旅行的意义，也许就在这些没有预先安排的片刻里：一次停留、一场交谈，以及重新出发时的期待。'},
 {id:'library',title:'城市书房',level:'中等',description:'练习引号、顿号与问号。',text:'傍晚，街角的书店亮起了灯。书架上摆着小说、散文和旅行笔记，空气里有淡淡的纸张气息。“你在寻找什么样的故事？”店员轻声问。我想了想，回答：“一段能让我慢下来的文字。”于是，我们聊起读过的书，也聊起那些尚未抵达的远方。离开时，雨已经停了，路面的灯影清晰而温柔。'},
 {id:'harbor',title:'港口观察',level:'困难',description:'专业用词、数字与复杂标点。',text:'清晨08:30，港区调度中心开始核对当日作业计划。记录显示：3号泊位预计接靠2艘货轮，装卸设备须提前完成检查；风速超过12米/秒时，应重新评估作业条件。“效率”与“安全”如何兼顾？答案藏在每一项细致的准备中——从航道信息的确认，到人员、设备及货物的协调，任何环节都不能疏忽。值班员在日志中写道：“数据需要复核，指令必须清晰。”'},
 {id:'thinking',title:'思考的尺度',level:'困难',description:'长篇抽象表达，挑战耐心与准确度。',text:'当信息不断涌入，我们是否仍能保留独立思考的空间？快速判断固然方便，却也可能掩盖细节：一个看似明确的结论，往往建立在若干未经检验的前提之上。因此，阅读时不妨追问：“证据来自哪里？条件发生变化后，结论是否依然成立？”这种审慎并非犹豫，而是对复杂现实的尊重。真正有效的学习，需要在理解、实践与反思之间反复往返；既愿意承认暂时的未知，也愿意用耐心逐步缩小未知的范围。'}
];
let chars=Array.from(original);
const input=document.querySelector('#input');
const reference=document.querySelector('#reference'), status=document.querySelector('#status');
let start=null, finished=null, composing=false;
const choices=document.querySelector('#choices');
lessons.forEach(lesson=>{const button=document.createElement('button');button.className='lesson';button.type='button';const badge=document.createElement('span');badge.className='badge';badge.textContent=lesson.level;const title=document.createElement('h2');title.textContent=lesson.title;const description=document.createElement('p');description.textContent=lesson.description;const count=document.createElement('small');count.textContent=Array.from(lesson.text).length+' 字 · 点击开始 →';button.append(badge,title,description,count);button.addEventListener('click',()=>{location.hash=lesson.id});choices.appendChild(button)});
function route(){
 const lesson=lessons.find(item=>'#'+item.id===location.hash);
 document.querySelector('#selection').hidden=!!lesson;
 document.querySelector('#practice').hidden=!lesson;
 input.value='';start=null;finished=null;composing=false;
 if(lesson){chars=Array.from(lesson.text);document.querySelector('#lesson-title').textContent=lesson.level+' · '+lesson.title;reference.replaceChildren();chars.forEach(char=>{const span=document.createElement('span');span.textContent=char;reference.appendChild(span)});update();input.focus()}
 else{choices.querySelector('button').focus()}
}
document.querySelector('#back').addEventListener('click',()=>{location.hash=''});
window.addEventListener('hashchange',route);
// 将光标固定在末尾，仅允许依序追加或退格，避免跳到中间输入。
function moveEnd(){input.setSelectionRange(input.value.length,input.value.length)}
input.addEventListener('click',moveEnd);
input.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End','Delete'].includes(event.key)){event.preventDefault();moveEnd()}});
input.addEventListener('beforeinput',event=>{if(!composing)moveEnd();if(event.inputType==='insertFromPaste'||event.inputType==='insertFromDrop')event.preventDefault()});
input.addEventListener('paste',event=>event.preventDefault());
input.addEventListener('drop',event=>event.preventDefault());
// 中文输入法组词期间不截断内容，确认文字后再更新统计。
input.addEventListener('compositionstart',()=>{composing=true});
input.addEventListener('compositionend',()=>{composing=false;update()});
input.addEventListener('input',()=>{if(!composing)update()});
function update(){
 let typed=Array.from(input.value);
 if(typed.length>chars.length){typed=typed.slice(0,chars.length);input.value=typed.join('')}
 if(!typed.length){start=null;finished=null}else if(start===null){start=performance.now()}
 let errors=0;
 Array.from(reference.children).forEach((span,index)=>{span.className=index<typed.length?(typed[index]===chars[index]?'correct':'wrong'):(index===typed.length?'current':'');if(index<typed.length&&typed[index]!==chars[index])errors++});
 // 只有整篇正确才结束计时，用户仍可退格修正错误。
 if(typed.length===chars.length&&errors===0){if(finished===null)finished=performance.now()}else{finished=null}
 document.querySelector('#total').textContent=typed.length;
 document.querySelector('#errors').textContent=errors;
 document.querySelector('#accuracy').textContent=typed.length?((typed.length-errors)/typed.length*100).toFixed(1)+'%':'100%';
 renderTime();
}
function renderTime(){const elapsed=start===null?0:((finished??performance.now())-start)/1000;const seconds=Math.floor(elapsed);const typed=Array.from(input.value);const correct=typed.filter((char,index)=>char===chars[index]).length;document.querySelector('#speed').textContent=elapsed>=1?Math.round(correct/elapsed*60):0;status.textContent=(finished!==null?'练习完成，做得不错！':start===null?'准备好了，就开始吧':'专注输入中')+' · '+String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0')}
document.querySelector('#reset').addEventListener('click',()=>{input.value='';update();input.focus()});
setInterval(renderTime,250);route();

