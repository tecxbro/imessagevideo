// Bounded real native production check; no completed cache/master is changed.
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {createRequire} from 'node:module';
import {loadScene} from '../../../engines/scene-loader.mjs';import {runtimeChunks,proveRuntimeChunks} from '../../../engines/runtime-scene.mjs';
const root=path.resolve('.'),out=path.join(root,'outputs/alternative-methods/motion-canvas-text-inventory/production-rms');fs.mkdirSync(out,{recursive:true});
const require=createRequire(path.join(root,'engines/package.json')),{chromium}=require('playwright'),{build}=require('esbuild'),targets=[['02-danieltian','final-v19',Array.from({length:15},(_,i)=>80+i)],['04-poke','final-v19',[400]],['06-gallery','final-v23',[1067]],['03-photon-mini','final-v18',[535]]];
const bundle=path.join(out,'runtime.js');await build({entryPoints:[path.join(root,'engines/motion-canvas-runtime.mjs')],bundle:true,format:'iife',globalName:'Runtime',platform:'browser',outfile:bundle,loader:{'.svg':'text','.css':'text','.glsl':'text'},define:{'import.meta.env.PROD':'true'}});
let browser;const records=[];
try{browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const [name,revision,frames]of targets){const input=path.join(root,'outputs',name,revision,'scene.json');let scene=loadScene(input);const chunks=runtimeChunks(scene,frames,8*1024*1024);const proved=proveRuntimeChunks(scene,chunks);const directory=path.join(out,name);fs.mkdirSync(directory,{recursive:true});
  for(const chunk of chunks){const page=await browser.newPage({viewport:{width:scene.width,height:scene.height}});page.setDefaultTimeout(120000);await page.route('http://rms-production.local/**',r=>r.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html><body></body></html>'}));await page.goto('http://rms-production.local/');await page.addScriptTag({path:bundle});await page.evaluate(scene=>window.Runtime.setup(scene),chunk.scene);
   for(const frame of chunk.frames){const png=await page.evaluate(f=>window.Runtime.frame(f),frame);fs.writeFileSync(path.join(directory,String(frame).padStart(6,'0')+'.png'),Buffer.from(png.split(',')[1],'base64'));}
   await page.close();
  }
  records.push({reference:name,sceneSha256:createHash('sha256').update(fs.readFileSync(input)).digest('hex'),frames,pruningProved:proved,directory});console.log(JSON.stringify(records.at(-1)));scene=null;global.gc?.();
 }
}finally{await browser?.close();}
fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify({status:'private native production proof only; no completed output mutation',records},null,2)+'\n');
