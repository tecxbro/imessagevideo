/** Diagnostic-only exact lifetime pruning with a native-node budget. */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
import {build} from 'esbuild';
import {loadScene} from '../../scene-loader.mjs';
import {sceneForFrames,proveRuntimeChunks} from '../../runtime-scene.mjs';
const args=Object.fromEntries(process.argv.slice(2).reduce((r,x,i,all)=>x.startsWith('--')?[...r,[x.slice(2),all[i+1]]]:r,[]));
const input=path.resolve(args.scene),out=path.resolve(args.out),runtime=path.resolve('engines/motion-canvas-runtime.mjs');
const scene=loadScene(input),frames=args.frames.split(',').map(Number),maxNodes=Number(args['max-nodes']??512),started=performance.now();
const count=ls=>ls.reduce((n,l)=>n+1+count(l.children??[]),0);
function split(indices){
 const active=sceneForFrames(scene,indices),bytes=Buffer.byteLength(JSON.stringify(active)),nodes=count(active.layers);
 if((bytes<=8*1024*1024&&nodes<=maxNodes)||indices.length===1)return [{scene:active,frames:indices,bytes,nodes}];
 const m=Math.floor(indices.length/2);return [...split(indices.slice(0,m)),...split(indices.slice(m))];
}
const chunks=split(frames);proveRuntimeChunks(scene,chunks);fs.mkdirSync(out,{recursive:true});
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'native-node-budget-'));let browser;const timings=[];
try{
 await build({entryPoints:[runtime],bundle:true,format:'iife',globalName:'MotionCanvasRuntime',platform:'browser',outfile:path.join(tmp,'runtime.js'),loader:{'.svg':'text','.css':'text','.glsl':'text'},define:{'import.meta.env.PROD':'true'}});
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox'],timeout:120000});
 for(const chunk of chunks){
  const start=performance.now(),page=await browser.newPage({viewport:{width:scene.width,height:scene.height}});
  try{
   await page.route('http://motion-canvas.local/**',r=>r.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html><body></body></html>'}));
   await page.goto('http://motion-canvas.local/');await page.addScriptTag({path:path.join(tmp,'runtime.js')});await page.evaluate(s=>window.MotionCanvasRuntime.setup(s),chunk.scene);
   const setupDone=performance.now(),frameTimes=[];
   for(const f of chunk.frames){const t=performance.now(),data=await page.evaluate(f=>window.MotionCanvasRuntime.frame(f),f);fs.writeFileSync(path.join(out,`${String(f).padStart(6,'0')}.png`),Buffer.from(data.split(',')[1],'base64'));frameTimes.push({frame:f,milliseconds:performance.now()-t});}
   const cdp=await page.context().newCDPSession(page),heap=await cdp.send('Runtime.getHeapUsage');
   const timing={first:chunk.frames[0],last:chunk.frames.at(-1),frames:chunk.frames.length,nodes:chunk.nodes,bytes:chunk.bytes,setupMilliseconds:setupDone-start,frameTimes,heap};timings.push(timing);console.log(JSON.stringify(timing));
  }finally{await page.close();}
 }
 const sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({input,inputSha256:sha(input),runtimeSha256:sha(runtime),maxNodes,frames,pruningVerifiedFrames:frames.length,seconds:(performance.now()-started)/1000,chunks:timings},null,2)+'\n');
}finally{await browser?.close();fs.rmSync(tmp,{recursive:true,force:true});}
