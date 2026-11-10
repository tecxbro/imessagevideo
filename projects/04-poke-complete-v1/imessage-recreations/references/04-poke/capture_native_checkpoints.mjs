// Same GSAP runtime and screenshot settings as the production renderer, without a
// redundant full encode while evaluating a measured scene candidate.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {loadScene} from '../../engines/scene-loader.mjs';
import {build} from '../../engines/node_modules/esbuild/lib/main.js';
import {chromium} from '../../engines/node_modules/playwright/index.mjs';
const args=Object.fromEntries(process.argv.slice(2).reduce((pairs,arg,i,all)=>arg.startsWith('--')?[...pairs,[arg.slice(2),all[i+1]]]:pairs,[]));
if(!args.scene||!args['out-dir']||!args.frames)throw new Error('Required: --scene path --out-dir path --frames comma-separated-native-indices');
const inputSceneSHA256=createHash('sha256').update(fs.readFileSync(args.scene)).digest('hex');
const here=path.dirname(fileURLToPath(import.meta.url));const root=path.resolve(here,'../..');const scene=loadScene(args.scene);const frames=args.frames.split(',').map(Number);const out=path.resolve(args['out-dir']);fs.mkdirSync(out,{recursive:true});
const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'poke-native-check-'));
try{
 await build({entryPoints:[path.join(root,'engines/web-runtime.mjs')],bundle:true,format:'iife',globalName:'MeasuredRuntime',platform:'browser',outfile:path.join(temporary,'runtime.js')});
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox'],timeout:120000});
 try{
  const page=await browser.newPage({viewport:{width:scene.width,height:scene.height},deviceScaleFactor:1});page.setDefaultTimeout(120000);
  await page.setContent('<!doctype html><html><head><style>html,body{margin:0;padding:0;overflow:hidden;}svg{display:block;}</style></head><body><div id="stage"></div></body></html>');
  await page.addScriptTag({path:path.join(temporary,'runtime.js')});await page.evaluate(scene=>window.MeasuredRuntime.setup(scene,'gsap'),scene);await page.evaluate(()=>document.fonts.ready);
  for(const frame of frames){if(!Number.isInteger(frame)||frame<0||frame>=Math.round(scene.duration*scene.fps))throw new Error('Invalid native frame');await page.evaluate(t=>window.MeasuredRuntime.seek(t),frame/scene.fps);await page.screenshot({path:path.join(out,`${String(frame).padStart(6,'0')}.png`),animations:'disabled'});}
 }finally{await browser.close();}
 fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify({method:'actual production GSAP runtime, native checkpoints only',scene:path.resolve(args.scene),sceneSHA256:inputSceneSHA256,frames,width:scene.width,height:scene.height,fps:scene.fps},null,2));
}finally{fs.rmSync(temporary,{recursive:true,force:true});}
