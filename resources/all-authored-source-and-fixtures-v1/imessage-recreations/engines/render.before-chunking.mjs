import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {loadScene} from './scene-loader.mjs';
import {svgMarkup} from './common.mjs';
import {createHash} from 'node:crypto';
const args=Object.fromEntries(process.argv.slice(2).reduce((pairs,arg,i,all)=>arg.startsWith('--')?[...pairs,[arg.slice(2),all[i+1]]]:pairs,[]));
if(!args.scene||!args.out||!['remotion','gsap','html'].includes(args.method)){console.error('Usage: node render.mjs --method remotion|gsap|html --scene scene.json --out out.mp4 [--frame frameIndex]');process.exit(2);}
const root=path.dirname(fileURLToPath(import.meta.url));const scene=loadScene(args.scene);const out=path.resolve(args.out);fs.mkdirSync(path.dirname(out),{recursive:true});
// A completion sidecar certifies only a finished render, never an in-flight replacement.
fs.rmSync(out+'.render.json',{force:true});
const browserExecutable=process.env.CHROME_PATH??(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':'/home/agent/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome');
const started=Date.now();
const pixelFormat=scene.width%2||scene.height%2?'yuv444p':'yuv420p';
const frameCount=Math.round(scene.duration*scene.fps);
const explicitRanges=args.ranges?args.ranges.split(',').map(r=>r.split(':').map(Number)):null;
const ranges=explicitRanges??[[Number(args['start-frame']??0),Number(args['end-frame']??(frameCount-1))]];
for(const range of ranges)if(range.length!==2||!range.every(Number.isInteger)||range[0]<0||range[1]>=frameCount||range[1]<range[0])throw new Error('Invalid inclusive frame range');
const captureFrames=[...new Set(ranges.flatMap(([first,last])=>Array.from({length:last-first+1},(_,i)=>i+first)))].sort((a,b)=>a-b);
const firstFrame=captureFrames[0],lastFrame=captureFrames.at(-1);
const frameDirectory=args['frames-dir']?path.resolve(args['frames-dir']):null;
if(!Number.isInteger(firstFrame)||!Number.isInteger(lastFrame)||firstFrame<0||lastFrame>=frameCount||lastFrame<firstFrame)throw new Error('Invalid inclusive frame range');
if(captureFrames.length!==frameCount&&!frameDirectory)throw new Error('Partial capture requires --frames-dir with the complete retained frame sequence');
if(frameDirectory)fs.mkdirSync(frameDirectory,{recursive:true});
let uniqueFramesCaptured=0;
function atomicWrite(filename,buffer){const temporary=filename+`.tmp-${process.pid}`;fs.writeFileSync(temporary,buffer);fs.renameSync(temporary,filename);}
function cloneFrame(source,destination){if(source===destination)return;fs.rmSync(destination,{force:true});fs.linkSync(source,destination);}
function encodeFrames(directory){
 for(let frame=0;frame<frameCount;frame++)if(!fs.existsSync(path.join(directory,`${String(frame).padStart(6,'0')}.png`)))throw new Error(`Cannot encode incomplete frame cache: missing frame ${frame}`);
 const partial=out+`.rendering-${process.pid}.mp4`;
 const proc=spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-framerate',String(scene.fps),'-i',path.join(directory,'%06d.png'),'-frames:v',String(frameCount),'-c:v','libx264','-threads','2','-vf','scale=out_color_matrix=bt709','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-crf','16','-pix_fmt',pixelFormat,'-movflags','+faststart',partial],{stdio:'inherit'});if(proc.status!==0){fs.rmSync(partial,{force:true});throw new Error(`ffmpeg failed: ${proc.status}`);}fs.renameSync(partial,out);
}
if(args.method==='remotion'){
 const {bundle}=await import('@remotion/bundler');const {selectComposition,renderFrames,renderStill}=await import('@remotion/renderer');
 const serveUrl=await bundle({entryPoint:path.join(root,'remotion-entry.jsx')});
 const composition=await selectComposition({serveUrl,id:'MeasuredScene',inputProps:{scene},browserExecutable,timeoutInMilliseconds:120000,chromiumOptions:{disableWebSecurity:true}});
 if(args.frame!==undefined)await renderStill({serveUrl,composition,inputProps:{scene},output:out,frame:Number(args.frame),browserExecutable,imageFormat:'png',timeoutInMilliseconds:120000});
 else {
  const temp=frameDirectory??fs.mkdtempSync(path.join(os.tmpdir(),'remotion-measured-frames-'));
  try{
   const byHash=new Map(),unique=[],duplicates=[];
   for(const frame of captureFrames){const hash=createHash('sha256').update(svgMarkup(scene,frame/scene.fps,undefined,false)).digest('hex');if(byHash.has(hash))duplicates.push([frame,byHash.get(hash)]);else{byHash.set(hash,frame);unique.push(frame);}}
   uniqueFramesCaptured=unique.length;
   await renderFrames({serveUrl,composition,inputProps:{scene},outputDir:null,imageFormat:'png',browserExecutable,concurrency:2,frames:unique,timeoutInMilliseconds:120000,chromiumOptions:{disableWebSecurity:true},onStart:()=>{},onFrameUpdate:()=>{},onFrameBuffer:(buffer,frame)=>atomicWrite(path.join(temp,`${String(frame).padStart(6,'0')}.png`),buffer)});
   for(const [frame,original] of duplicates)cloneFrame(path.join(temp,`${String(original).padStart(6,'0')}.png`),path.join(temp,`${String(frame).padStart(6,'0')}.png`));
   encodeFrames(temp);
  }finally{if(!frameDirectory)fs.rmSync(temp,{recursive:true,force:true});}
 }
}else{
 const {chromium}=await import('playwright');const {build}=await import('esbuild');
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'measured-frames-'));
 try{
  await build({entryPoints:[path.join(root,'web-runtime.mjs')],bundle:true,format:'iife',globalName:'MeasuredRuntime',platform:'browser',outfile:path.join(temp,'runtime.js')});
  const browser=await chromium.launch({executablePath:browserExecutable,headless:true,args:['--no-sandbox'],timeout:120000});const page=await browser.newPage({viewport:{width:scene.width,height:scene.height},deviceScaleFactor:1});page.setDefaultTimeout(120000);
  await page.setContent('<!doctype html><html><head><style>html,body{margin:0;padding:0;overflow:hidden;}svg{display:block;}</style></head><body><div id="stage"></div></body></html>');
  await page.addScriptTag({path:path.join(temp,'runtime.js')});await page.evaluate(({scene,method})=>window.MeasuredRuntime.setup(scene,method),{scene,method:args.method});await page.evaluate(()=>document.fonts.ready);
  const frames=args.frame!==undefined?[Number(args.frame)]:captureFrames;
  let previousFramePath=null;
  for(const frame of frames){const changed=await page.evaluate(t=>window.MeasuredRuntime.seek(t),frame/scene.fps);const destination=args.frame!==undefined?out:path.join(frameDirectory??temp,`${String(frame).padStart(6,'0')}.png`);if(!changed&&previousFramePath&&args.frame===undefined)cloneFrame(previousFramePath,destination);else{atomicWrite(destination,await page.screenshot({animations:'disabled'}));uniqueFramesCaptured++;}previousFramePath=destination;}
  await browser.close();
  if(args.frame===undefined)encodeFrames(frameDirectory??temp);
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
}
const metadata={method:args.method,scene:path.resolve(args.scene),sceneSHA256:createHash('sha256').update(fs.readFileSync(args.scene)).digest('hex'),out,width:scene.width,height:scene.height,fps:scene.fps,frames:frameCount,duration:frameCount/scene.fps,source:scene.source??null,frame:args.frame===undefined?null:Number(args.frame),frameDirectory,capturedFrameRange:[firstFrame,lastFrame],capturedFrameRanges:ranges,uniqueFramesCaptured,pixelFormat,seconds:(Date.now()-started)/1000};atomicWrite(out+'.render.json',JSON.stringify(metadata,null,2)+'\n');
console.log(JSON.stringify({method:args.method,out,width:scene.width,height:scene.height,fps:scene.fps,frames:Math.round(scene.duration*scene.fps),seconds:(Date.now()-started)/1000}));
