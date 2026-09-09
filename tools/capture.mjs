// Optional browser evidence helper. Node 22+; an installed Chromium/Chrome executable.
import {spawn} from 'node:child_process';
import {mkdtemp,readFile,writeFile,rm,mkdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
const [url,output]=process.argv.slice(2);
if(!url||!output)throw Error('Usage: node tools/capture.mjs http://127.0.0.1:8770/ OUTPUT_DIRECTORY');
const parsed=new URL(url);
if(!['127.0.0.1','localhost','[::1]'].includes(parsed.hostname))throw Error('This helper only opens loopback review pages.');
const chrome=process.env.CHROME || (process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':'chromium');
const profile=await mkdtemp(join(tmpdir(),'placecraft-browser-'));
const folder=resolve(output);await mkdir(folder,{recursive:true});
const child=spawn(chrome,['--headless=new','--remote-debugging-port=0',`--user-data-dir=${profile}`,'--no-first-run','--window-size=1280,960','about:blank'],{stdio:'ignore'});
let startError;child.on('error',e=>startError=e);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let socket;let sequence=0;const pending=new Map();const errors=[];
try{
 let port;
 for(let i=0;i<100;i++){if(startError)throw startError;try{port=(await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{}await sleep(100);}
 if(!port)throw Error('Chrome did not start. Set CHROME to its executable.');
 const targets=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();
 socket=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
 socket.onmessage=({data})=>{const m=JSON.parse(data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);clearTimeout(p.timer);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value??a.description).join(' '));};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++sequence;const timer=setTimeout(()=>{pending.delete(id);reject(Error(`CDP timeout: ${method}`));},20000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}));});
 await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url});
 let ready=false;
 for(let i=0;i<150;i++){const r=await send('Runtime.evaluate',{expression:'window.placecraft?.ready',returnByValue:true});if(r.result.value){ready=true;break;}if(errors.length)break;await sleep(200);}
 if(!ready)throw Error('Viewer failed to load: '+JSON.stringify(errors));
 const views=['overview','front','rear','left','right','roof'];
 for(const view of views){
  const result=await send('Runtime.evaluate',{expression:`window.placecraft.setView(${JSON.stringify(view)})`,returnByValue:true});
  if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));
  await sleep(150);
  const png=await send('Page.captureScreenshot',{format:'png'});
  await writeFile(join(folder,`${view}.png`),Buffer.from(png.data,'base64'));
 }
 const rotate=await send('Runtime.evaluate',{expression:`(()=>{const b=document.querySelector('#rotate');b.click();const on=b.getAttribute('aria-pressed')==='true';b.click();return on&&b.getAttribute('aria-pressed')==='false';})()`,returnByValue:true});
 if(!rotate.result.value||errors.length)throw Error('Controls/errors check failed: '+JSON.stringify(errors));
 await writeFile(join(folder,'browser-check.json'),JSON.stringify({views,loaded:true,rotation_control:true,console_errors:errors,visual_judgment:'Screenshots require human/agent inspection; capture alone is not approval.'},null,2)+'\n');
 console.log('Captured six review views; model loaded and controls passed.');
}finally{
 for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('Browser closing'));}pending.clear();
 socket?.close();child.kill();await sleep(400);await rm(profile,{recursive:true,force:true,maxRetries:3,retryDelay:200});
}
