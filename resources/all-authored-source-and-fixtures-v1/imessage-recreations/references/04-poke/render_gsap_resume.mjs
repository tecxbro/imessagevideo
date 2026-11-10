// Resume a validated GSAP prefix without discarding completed native frames.
import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import {spawnSync} from 'node:child_process';
import {loadScene} from '../../engines/scene-loader.mjs';import {build} from '../../engines/node_modules/esbuild/lib/main.js';import {chromium} from '../../engines/node_modules/playwright/index.mjs';
const base='/workspace/imessage-recreations',scenePath=base+'/references/04-poke/scene.json',scene=loadScene(scenePath),dir=base+'/outputs/retained-frames/measured-frames-jRBOzF',out=base+'/outputs/04-poke/gsap.mp4';
const firstFrame=617,count=Math.round(scene.fps*scene.duration),started=Date.now();for(let i=0;i<firstFrame;i++)if(!fs.existsSync(`${dir}/${String(i).padStart(6,'0')}.png`))throw new Error(`Missing retained prefix ${i}`);
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'poke-gsap-resume-'));let browser;
function atomic(filename,buf){const tmp=filename+`.tmp-${process.pid}`;fs.writeFileSync(tmp,buf);fs.renameSync(tmp,filename);}
try{
 await build({entryPoints:[base+'/engines/web-runtime.mjs'],bundle:true,format:'iife',globalName:'MeasuredRuntime',platform:'browser',outfile:temp+'/runtime.js'});
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:scene.width,height:scene.height},deviceScaleFactor:1});page.setDefaultTimeout(120000);
 await page.setContent('<!doctype html><style>body{margin:0;overflow:hidden}svg{display:block}</style><div id="stage"></div>');await page.addScriptTag({path:temp+'/runtime.js'});await page.evaluate(scene=>window.MeasuredRuntime.setup(scene,'gsap'),scene);await page.evaluate(()=>document.fonts.ready);
 let previous=null,unique=0;
 for(let frame=firstFrame;frame<count;frame++){
  const changed=await page.evaluate(t=>window.MeasuredRuntime.seek(t),frame/scene.fps),destination=`${dir}/${String(frame).padStart(6,'0')}.png`;
  if(!changed&&previous){fs.rmSync(destination,{force:true});fs.linkSync(previous,destination);}else{atomic(destination,await page.screenshot({animations:'disabled',timeout:120000}));unique++;}
  previous=destination;if(frame%100===0)console.log(JSON.stringify({frame,total:count,seconds:(Date.now()-started)/1000}));
 }
 await browser.close();browser=null;
 for(let i=0;i<count;i++)if(!fs.existsSync(`${dir}/${String(i).padStart(6,'0')}.png`))throw new Error(`Incomplete cache ${i}`);
 const enc=spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate',String(scene.fps),'-i',dir+'/%06d.png','-frames:v',String(count),'-c:v','libx264','-vf','scale=out_color_matrix=bt709','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',out],{stdio:'inherit'});if(enc.status!==0)throw new Error('FFmpeg encode failed');
 const meta={method:'gsap',scene:scenePath,out,width:scene.width,height:scene.height,fps:scene.fps,frames:count,duration:count/scene.fps,source:scene.source,frameDirectory:dir,capturedFrameRange:[firstFrame,count-1],preservedFrameRange:[0,firstFrame-1],uniqueFramesCaptured:unique,screenshotTimeoutMs:120000,seconds:(Date.now()-started)/1000};fs.writeFileSync(out+'.render.json',JSON.stringify(meta,null,2));console.log(JSON.stringify(meta));
}finally{if(browser)await browser.close();fs.rmSync(temp,{recursive:true,force:true});}
