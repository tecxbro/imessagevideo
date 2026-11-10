import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';import {chromium} from 'playwright';import {build} from 'esbuild';import {loadScene} from './scene-loader.mjs';import {runtimeChunks,proveRuntimeChunks} from './runtime-scene.mjs';
const args=Object.fromEntries(process.argv.slice(2).reduce((p,a,i,all)=>a.startsWith('--')?[...p,[a.slice(2),all[i+1]]]:p,[]));if(!args.scene||!args.out){console.error('Usage: node render_motion_canvas.mjs --scene scene.json --out output.mp4 [--frame N] [--frames-dir DIR] [--ranges first:last,...]');process.exit(2);}
const scene=loadScene(args.scene),out=path.resolve(args.out),frameCount=Math.round(scene.duration*scene.fps),root=path.dirname(fileURLToPath(import.meta.url));fs.mkdirSync(path.dirname(out),{recursive:true});
const engineSha256=createHash('sha256').update(Buffer.concat(['render_motion_canvas-local-blur-experiment.mjs','motion-canvas-runtime-local-blur-experiment.mjs','common.mjs','scene-loader.mjs','runtime-scene.mjs'].map(n=>fs.readFileSync(path.join(root,n))))).digest('hex');
const frameDirectory=args['frames-dir']?path.resolve(args['frames-dir']):null,ranges=args.ranges?args.ranges.split(',').map(r=>r.split(':').map(Number)):[[Number(args['start-frame']??0),Number(args['end-frame']??frameCount-1)]];
for(const r of ranges)if(r.length!==2||!r.every(Number.isInteger)||r[0]<0||r[1]>=frameCount||r[1]<r[0])throw new Error('Invalid inclusive frame range');
const captureFrames=[...new Set(ranges.flatMap(([a,b])=>Array.from({length:b-a+1},(_,i)=>a+i)))].sort((a,b)=>a-b);
if(args.frame===undefined&&captureFrames.length!==frameCount&&!frameDirectory)throw new Error('Partial capture requires --frames-dir with complete retained native PNG sequence');
if(frameDirectory)fs.mkdirSync(frameDirectory,{recursive:true});
if(args.frame!==undefined&&(!Number.isInteger(Number(args.frame))||Number(args.frame)<0||Number(args.frame)>=frameCount))throw new Error('Invalid frame index');
if(frameDirectory&&(captureFrames.length!==frameCount||args['encode-only']==='true')){const metadata=path.join(frameDirectory,'native-cache.json');if(fs.existsSync(metadata)){const old=JSON.parse(fs.readFileSync(metadata,'utf8'));if(old.width!==scene.width||old.height!==scene.height||old.frames!==frameCount||Math.abs(old.fps-scene.fps)>1e-8)throw new Error('Native cache dimensions/cadence/frame count mismatch');}const selected=new Set(captureFrames);for(let f=0;f<frameCount;f++)if((args['encode-only']==='true'||!selected.has(f))&&!fs.existsSync(path.join(frameDirectory,`${String(f).padStart(6,'0')}.png`)))throw new Error(`Missing unchanged cached frame ${f}`);}
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'motioncanvas-')),directory=frameDirectory??tmp,started=Date.now(),encoding=out+`.encoding-${process.pid}.mp4`;let browser,uniqueFramesCaptured=0,runtimeTransport=[],runtimePruningVerifiedFrames=0;
const transportByteLimit=8*1024*1024,transportPruningThreshold=32*1024*1024;let transportMode=args['encode-only']==='true'?'encode-only':null;
const pngPath=f=>path.join(directory,`${String(f).padStart(6,'0')}.png`);
function atomicWrite(file,data){const temporary=file+`.tmp-${process.pid}`;fs.writeFileSync(temporary,data);fs.renameSync(temporary,file);}
function cloneFrame(source,target){if(source===target)return;fs.rmSync(target,{force:true});fs.linkSync(source,target);}
function encode(){for(let f=0;f<frameCount;f++)if(!fs.existsSync(pngPath(f)))throw new Error(`Incomplete native frame cache: ${f}`);const p=spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-framerate',String(scene.fps),'-i',path.join(directory,'%06d.png'),'-frames:v',String(frameCount),'-c:v','libx264','-threads','2','-vf','scale=out_color_matrix=bt709','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-crf','16','-pix_fmt',scene.width%2||scene.height%2?'yuv444p':'yuv420p','-movflags','+faststart',encoding],{stdio:'inherit'});if(p.status)throw new Error('FFmpeg '+p.status);fs.renameSync(encoding,out);}
try{
 if(args['encode-only']!=='true'){
  await build({entryPoints:[path.join(root,'motion-canvas-runtime-local-blur-experiment.mjs')],bundle:true,format:'iife',globalName:'MotionCanvasRuntime',platform:'browser',outfile:path.join(tmp,'runtime.js'),loader:{'.svg':'text','.css':'text','.glsl':'text'},define:{'import.meta.env.PROD':'true'}});
  const frames=args.frame!==undefined?[Number(args.frame)]:captureFrames;
  const fullSceneBytes=Buffer.byteLength(JSON.stringify(scene));
  // Preserve the established native setup for small scenes. Large scenes keep
  // absolute source times and only remove nodes outside requested lifetimes.
  transportMode=fullSceneBytes>transportPruningThreshold?'active-lifecycle-chunks':'full-scene';
  const chunks=transportMode==='full-scene'?[{frames,scene,bytes:fullSceneBytes}]:runtimeChunks(scene,frames,transportByteLimit);
  if(transportMode==='active-lifecycle-chunks')runtimePruningVerifiedFrames=proveRuntimeChunks(scene,chunks);
  runtimeTransport=chunks.map(c=>({first:c.frames[0],last:c.frames.at(-1),frames:c.frames.length,bytes:c.bytes}));
  browser=await chromium.launch({executablePath:process.env.CHROME_PATH??'/usr/bin/chromium',headless:true,args:['--no-sandbox'],timeout:120000});
  let previousData=null,previousPath=null;
  for(const chunk of chunks){
   // A fresh page gives each native Scene2D renderer a clean resource lifetime.
   // No renderer/global state from an earlier chunk can retain its first props.
   const page=await browser.newPage({viewport:{width:scene.width,height:scene.height}});
   try{
    page.setDefaultTimeout(120000);page.on('console',msg=>{if(msg.type()==='error')console.error('browser:',msg.text())});await page.route('http://motion-canvas.local/**',route=>route.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html><body></body></html>'}));await page.goto('http://motion-canvas.local/');await page.addScriptTag({path:path.join(tmp,'runtime.js')});await page.evaluate(s=>window.MotionCanvasRuntime.setup(s),chunk.scene);
    for(const frame of chunk.frames){if(args.frame===undefined&&frame%150===0)console.error(JSON.stringify({method:'motion-canvas',frame,total:frameCount}));const data=await page.evaluate(f=>window.MotionCanvasRuntime.frame(f),frame),destination=args.frame!==undefined?out:pngPath(frame);if(args.frame===undefined&&data===previousData&&previousPath)cloneFrame(previousPath,destination);else{atomicWrite(destination,Buffer.from(data.split(',')[1],'base64'));uniqueFramesCaptured++;}previousData=data;previousPath=destination;}
   }finally{await page.close();}
  }
  await browser.close();browser=null;
 }
 if(args.frame===undefined)encode();
 const previous=fs.existsSync(out+'.render.json')?JSON.parse(fs.readFileSync(out+'.render.json','utf8')):null;const captureHistory=previous?[...(previous.captureHistory??[]),{scene:previous.scene,sceneSha256:previous.sceneSha256??null,engineSha256:previous.engineSha256??null,capturedFrameRanges:previous.capturedFrameRanges??null,knownIssues:previous.knownIssues??null}]:[];const meta={captureHistory,method:'motion-canvas',engineSha256,scene:path.resolve(args.scene),sceneSha256:createHash('sha256').update(fs.readFileSync(args.scene)).digest('hex'),out,width:scene.width,height:scene.height,fps:scene.fps,frames:frameCount,duration:frameCount/scene.fps,source:scene.source??null,frameDirectory,capturedFrameRanges:args['encode-only']==='true'?[]:ranges,uniqueFramesCaptured,transportMode,transportByteLimit,transportPruningThreshold,runtimeTransport,runtimePruningVerifiedFrames,seconds:(Date.now()-started)/1000};atomicWrite(out+'.render.json',Buffer.from(JSON.stringify(meta,null,2)+'\n'));if(frameDirectory)atomicWrite(path.join(frameDirectory,'native-cache.json'),Buffer.from(JSON.stringify(meta,null,2)+'\n'));console.log(JSON.stringify(meta));
}finally{await browser?.close();fs.rmSync(tmp,{recursive:true,force:true});fs.rmSync(encoding,{force:true});}
