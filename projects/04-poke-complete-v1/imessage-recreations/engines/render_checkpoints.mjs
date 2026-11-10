import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {build} from 'esbuild';
import {loadScene} from './scene-loader.mjs';
import {sceneForTimes} from './runtime-scene.mjs';
import {svgMarkup} from './common.mjs';
import {createHash} from 'node:crypto';
const args=Object.fromEntries(process.argv.slice(2).reduce((p,v,i,a)=>v.startsWith('--')?[...p,[v.slice(2),a[i+1]]]:p,[]));
if(!args.scene||(!args.times&&!args.frames)||!args.out)throw new Error('Use --scene FILE --frames INDEX,INDEX (or --times SECONDS,SECONDS) --out DIRECTORY [--method html|gsap]');
const scene=loadScene(args.scene),method=args.method??'html';
if(!['html','gsap'].includes(method))throw new Error('Checkpoint batch supports html and gsap');
const out=path.resolve(args.out);fs.mkdirSync(out,{recursive:true});const temp=fs.mkdtempSync(path.join(os.tmpdir(),'measured-checkpoints-'));
let browser;
try{
 const root=path.dirname(fileURLToPath(import.meta.url));await build({entryPoints:[path.join(root,'web-runtime.mjs')],bundle:true,format:'iife',globalName:'MeasuredRuntime',platform:'browser',outfile:path.join(temp,'runtime.js')});
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH??'/usr/bin/chromium',headless:true,args:['--no-sandbox'],timeout:120000});
 const page=await browser.newPage({viewport:{width:scene.width,height:scene.height},deviceScaleFactor:1});page.setDefaultTimeout(120000);
 await page.setContent('<style>html,body{margin:0;padding:0;overflow:hidden}svg{display:block}</style><div id="stage"></div>');await page.addScriptTag({path:path.join(temp,'runtime.js')});

 const frameIndices=args.frames?args.frames.split(',').map(Number):null;
 if(frameIndices?.some(n=>!Number.isInteger(n)||n<0||n>=Math.round(scene.duration*scene.fps)))throw new Error('Invalid frame index');
 const times=frameIndices?frameIndices.map(n=>n/scene.fps):args.times.split(',').map(Number);
 for(const t of times){if(!Number.isFinite(t))throw new Error('Invalid time');const runtime=sceneForTimes(scene,[t]);if(svgMarkup(scene,t,undefined,false)!==svgMarkup(runtime,t,undefined,false))throw new Error('Checkpoint pruning changed SVG at '+t);await page.evaluate(({scene,method})=>window.MeasuredRuntime.setup(scene,method),{scene:runtime,method});await page.evaluate(()=>document.fonts.ready);await page.evaluate(t=>window.MeasuredRuntime.seek(t),t);const file=path.join(out,t.toFixed(3)+'.png');await page.screenshot({path:file,animations:'disabled',timeout:120000});console.log(JSON.stringify({t,file}));}
 fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify({scene:path.resolve(args.scene),sceneSHA256:createHash('sha256').update(fs.readFileSync(args.scene)).digest('hex'),method,times,frameIndices,width:scene.width,height:scene.height},null,2));
}finally{if(browser)await browser.close();fs.rmSync(temp,{recursive:true,force:true});}
