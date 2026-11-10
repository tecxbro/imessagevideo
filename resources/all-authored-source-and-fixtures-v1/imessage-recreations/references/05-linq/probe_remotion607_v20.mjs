// Run as stdin from engines so documented Remotion packages resolve there.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderFrames} from '@remotion/renderer';
import {loadScene} from './scene-loader.mjs';
import {svgMarkup} from './common.mjs';
import {sceneForFrames,runtimeChunks,proveRuntimeChunks} from './runtime-scene.mjs';
const root=path.resolve('..');
const scenePath=path.join(root,'outputs/05-linq/final-v20/scene.json');
const output=path.join(root,'verification/05-raster-parity-607/fresh-same-process');
fs.mkdirSync(output,{recursive:true});
const scene=loadScene(scenePath);
const metadata=JSON.parse(fs.readFileSync(path.join(root,'verification/05-raster-parity-607/original-r20-render.json'),'utf8'));
const captures=metadata.capturedFrameRanges.flatMap(([a,b])=>Array.from({length:b-a+1},(_,i)=>a+i));
const unique=[];
const hashes=new Set();
for(const frame of captures){
  const hash=createHash('sha256').update(svgMarkup(scene,frame/scene.fps,undefined,false)).digest('hex');
  if(!hashes.has(hash)){hashes.add(hash);unique.push(frame);}
}
const chunks=runtimeChunks(scene,unique);
proveRuntimeChunks(scene,chunks);
const chunk=chunks.find(item=>item.frames.includes(607));
if(!chunk)throw new Error('Original runtime chunk607 was not recovered');
const frames=[606,607,608];
const proofs=frames.map(frame=>{
  const full=createHash('sha256').update(svgMarkup(scene,frame/scene.fps,undefined,false)).digest('hex');
  const transported=createHash('sha256').update(svgMarkup(chunk.scene,frame/scene.fps,undefined,false)).digest('hex');
  if(full!==transported)throw new Error(`SVG mismatch before capture${frame}`);
  return {frame,svgSHA256:full};
});
const browserExecutable=process.env.CHROME_PATH??'/usr/bin/chromium';
const serveUrl=await bundle({entryPoint:path.join(process.cwd(),'remotion-entry.jsx')});
const browser=await openBrowser('chrome',{browserExecutable,chromiumOptions:{disableWebSecurity:true}});
const written=[];
try{
  const composition=await selectComposition({serveUrl,id:'MeasuredScene',inputProps:{scene:sceneForFrames(scene,[captures[0]])},puppeteerInstance:browser,browserExecutable,timeoutInMilliseconds:120000,chromiumOptions:{disableWebSecurity:true}});
  await renderFrames({serveUrl,composition:{...composition,props:{...composition.props,scene:chunk.scene}},inputProps:{scene:chunk.scene},outputDir:null,imageFormat:'png',puppeteerInstance:browser,browserExecutable,concurrency:2,frames,timeoutInMilliseconds:120000,chromiumOptions:{disableWebSecurity:true},onStart:()=>{},onFrameUpdate:()=>{},onFrameBuffer:(buffer,frame)=>{
    const file=path.join(output,`${String(frame).padStart(6,'0')}.png`);
    const temporary=file+'.tmp';
    fs.writeFileSync(temporary,buffer);
    fs.renameSync(temporary,file);
    written.push({frame,sha256:createHash('sha256').update(buffer).digest('hex'),bytes:buffer.length});
  }});
}finally{
  await browser.close({silent:true}).catch(error=>console.error('Probe browser cleanup:',error.message));
}
const report={scene:scenePath,sceneSHA256:createHash('sha256').update(fs.readFileSync(scenePath)).digest('hex'),frames,method:'One documented Remotion renderFrames call, concurrency2, same original broad runtime chunk and same initial selected composition props as the351-frame producer. No encode; production cache remains untouched.',runtimeChunk:{first:chunk.frames[0],last:chunk.frames.at(-1),frames:chunk.frames.length,bytes:chunk.bytes},originalRuntimeChunk:metadata.runtimeTransport.find(item=>item.first<=607&&item.last>=607),proofs,written,rendererVersion:JSON.parse(fs.readFileSync('node_modules/@remotion/renderer/package.json','utf8')).version};
fs.writeFileSync(path.join(output,'probe.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({frames:written.map(item=>item.frame),output,runtimeChunk:report.runtimeChunk}));
