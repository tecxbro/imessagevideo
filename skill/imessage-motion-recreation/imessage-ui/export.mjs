import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {chromium} from '../scripts/engines/node_modules/playwright/index.mjs';
import {trial} from './trial.mjs';

const args=Object.fromEntries(process.argv.slice(2).reduce((pairs,arg,i,all)=>arg.startsWith('--')?[...pairs,[arg.slice(2),all[i+1]]]:pairs,[]));
if (!args.out) throw new Error('Usage: node export.mjs [--config conversation.json] --out output-directory [--render yes]');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.resolve(args.out), config=args.config ? JSON.parse(fs.readFileSync(args.config,'utf8')) : trial;
const types={'.html':'text/html','.mjs':'text/javascript','.json':'application/json','.css':'text/css'};
const server=http.createServer((request,response)=>{
  const filename=path.resolve(root,'.'+decodeURIComponent(new URL(request.url,'http://localhost').pathname));
  if (!filename.startsWith(root+path.sep)) {response.writeHead(403).end();return;}
  try {response.setHeader('Content-Type',types[path.extname(filename)] ?? 'application/octet-stream');response.end(fs.readFileSync(filename));}
  catch {response.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const executablePath=process.env.CHROME_PATH ?? (process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':'/usr/bin/chromium');
let browser;
try {
  browser=await chromium.launch({executablePath,headless:true});
  const page=await browser.newPage();
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/imessage-ui/index.html`);
  await page.waitForFunction(()=>Boolean(window.conversationLab));
  const result=await page.evaluate(config=>window.conversationLab.apply(config),config);
  if(errors.length)throw new Error(errors.join('\n'));
  fs.mkdirSync(out,{recursive:true});
  for (const [name,value] of Object.entries({'conversation.config.json':config,'conversation.scene.json':result.scene,'layout-audit.json':result.audit}))fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2)+'\n');
  console.log(`Exported editable scene and measured layout to ${out}`);
} finally {await browser?.close();await new Promise(resolve=>server.close(resolve));}
if (args.render==='yes') {
  const result=spawnSync(process.execPath,[path.join(root,'scripts/engines/render.mjs'),'--method','html','--scene',path.join(out,'conversation.scene.json'),'--out',path.join(out,'conversation.mp4')],{stdio:'inherit',env:{...process.env,CHROME_PATH:executablePath}});
  if(result.status!==0)process.exit(result.status ?? 1);
}
