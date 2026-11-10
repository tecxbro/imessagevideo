import fs from 'node:fs';
import {loadScene} from '../../engines/scene-loader.mjs';
import {build} from '../../engines/node_modules/esbuild/lib/main.js';
import {chromium} from '../../engines/node_modules/playwright/index.mjs';
const root='/workspace/imessage-recreations',out=root+'/verification/fidelity-review';
await build({entryPoints:[root+'/engines/web-runtime.mjs'],bundle:true,format:'iife',globalName:'MeasuredRuntime',platform:'browser',outfile:out+'/runtime.js'});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
for(const [id,times] of [['05-linq',[9.2,13.3]],['06-gallery',[12.4,26.5,29.4,29.7]]]){
 const scene=loadScene(root+'/outputs/'+id+'/final-v4/scene.json');const dir=out+'/'+id+'/final-v4';fs.mkdirSync(dir,{recursive:true});const page=await browser.newPage({viewport:{width:scene.width,height:scene.height},deviceScaleFactor:1});
 await page.setContent('<!doctype html><style>body{margin:0;overflow:hidden}svg{display:block}</style><div id="stage"></div>');await page.addScriptTag({path:out+'/runtime.js'});await page.evaluate(scene=>window.MeasuredRuntime.setup(scene,'html'),scene);await page.evaluate(async fs=>{await Promise.all(fs.map(f=>document.fonts.load(`${f.weight??400} 24px "${f.family}"`)));await document.fonts.ready},scene.fonts??[]);
 for(const t of times){await page.evaluate(t=>window.MeasuredRuntime.seek(t),t);await page.screenshot({path:dir+'/'+t.toFixed(2)+'.png'});}await page.close();
}
await browser.close();
