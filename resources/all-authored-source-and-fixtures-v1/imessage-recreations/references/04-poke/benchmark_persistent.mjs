import fs from 'node:fs';
import {loadScene} from '../../engines/scene-loader.mjs';
import {build} from '../../engines/node_modules/esbuild/lib/main.js';
import {chromium} from '../../engines/node_modules/playwright/index.mjs';
const base='/workspace/imessage-recreations';const local=base+'/references/04-poke';const dir=base+'/outputs/04-poke/persistent-experiment';fs.mkdirSync(dir,{recursive:true});
const scene=loadScene(local+'/scene.json');const times=[0,.5,2,5,8,12,22,27,34,37,39,41];
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const result={times,methods:{}};
for(const mode of ['baseline','persistent']){
 await build({entryPoints:[mode==='baseline'?base+'/engines/web-runtime.mjs':local+'/persistent-gsap-runtime.mjs'],bundle:true,format:'iife',globalName:'Runtime',platform:'browser',outfile:dir+'/'+mode+'.js'});
 const page=await browser.newPage({viewport:{width:1440,height:1080},deviceScaleFactor:1});await page.setContent('<!doctype html><style>body{margin:0;overflow:hidden;}svg{display:block;}</style><div id="stage"></div>');await page.addScriptTag({path:dir+'/'+mode+'.js'});
 await page.evaluate(({scene,mode})=>window.Runtime.setup(scene,mode==='baseline'?'gsap':undefined),{scene,mode});await page.evaluate(()=>document.fonts.ready);
 const started=Date.now();
 for(const t of times){await page.evaluate(t=>window.Runtime.seek(t),t);await page.screenshot({path:dir+'/'+mode+'-'+t+'.png',animations:'disabled'});}
 result.methods[mode]={seconds:(Date.now()-started)/1000,screenshots:times.length};await page.close();
}
await browser.close();fs.writeFileSync(dir+'/timing.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
