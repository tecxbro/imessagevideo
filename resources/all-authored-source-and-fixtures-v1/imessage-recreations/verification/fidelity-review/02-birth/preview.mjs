import fs from 'node:fs';import {createRequire} from 'node:module';import {loadScene} from '../../../engines/scene-loader.mjs';import {svgMarkup,fontCss} from '../../../engines/common.mjs';
const root='/workspace/imessage-recreations',out=root+'/verification/fidelity-review/02-birth';const require=createRequire(root+'/engines/package.json');const {chromium}=require('playwright');const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
for (const [name,file] of [['base','scene-birth-base-v8.json'],['patch','scene-birth-review-v8.json']]){
 const scene=loadScene(root+'/references/02-danieltian/'+file);const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});await page.setContent('<!doctype html><html><head><style>html,body{margin:0;overflow:hidden}svg{display:block}'+fontCss(scene)+'</style></head><body><div id="stage"></div></body></html>');await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>Promise.all([document.fonts.load('600 96px "Photon Sans"'),document.fonts.load('400 48px "Photon Sans"')]));
 for(const f of [414,415,416,417,418,419,420]){const svg=svgMarkup(scene,f/30,undefined,false);await page.evaluate(svg=>document.getElementById('stage').innerHTML=svg,svg);await page.screenshot({path:out+`/${name}-${f}.png`});}
 await page.close();
}
await browser.close();console.log('14 native checkpoints complete');
