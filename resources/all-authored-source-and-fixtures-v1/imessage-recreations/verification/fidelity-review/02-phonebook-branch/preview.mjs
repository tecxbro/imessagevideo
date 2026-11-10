import fs from 'node:fs';import {createRequire} from 'node:module';
import {loadScene} from '../../../engines/scene-loader.mjs';import {svgMarkup,fontCss} from '../../../engines/common.mjs';
const root='/workspace/imessage-recreations',out=root+'/verification/fidelity-review/02-phonebook-branch';
const require=createRequire(root+'/engines/package.json');const {chromium}=require('playwright');
const inputs=[['patch','scene-v6-phonebook-review.json']];
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
for (const [name,file] of inputs){
const scene=loadScene(root+'/references/02-danieltian/'+file);const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
await page.setContent('<!doctype html><html><head><style>html,body{margin:0;overflow:hidden}svg{display:block}'+fontCss(scene)+'</style></head><body><div id="stage"></div></body></html>');
await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>Promise.all([document.fonts.load('600 96px "Photon Sans"'),document.fonts.load('400 48px "Photon Sans"')]));
for(const frame of [477,480,489,495,499]){
 const svg=svgMarkup(scene,frame/30,undefined,false);await page.evaluate(svg=>document.getElementById('stage').innerHTML=svg,svg);await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))));await page.screenshot({path:out+`/${name}-${frame}.png`});
}
await page.close();}
await browser.close();console.log('Targeted native diagnostic images captured in one browser batch');
const a=loadScene(root+'/references/02-danieltian/scene-v6-phonebook-glyphs.json'),b=loadScene(root+'/references/02-danieltian/scene-v6-phonebook-review.json');
const equality=[0,90,360,389,416,420,450,462,512,525,600,1200].map(frame=>({frame,svgIdentical:svgMarkup(a,frame/30,undefined,false)===svgMarkup(b,frame/30,undefined,false)}));fs.writeFileSync(out+'/outside-ranges.json',JSON.stringify(equality,null,2));console.log(equality);
