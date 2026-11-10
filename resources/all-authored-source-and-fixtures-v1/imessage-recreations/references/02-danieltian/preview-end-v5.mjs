import fs from 'node:fs';import {createRequire} from 'node:module';
import {loadScene} from '../../engines/scene-loader.mjs';import {svgMarkup,fontCss} from '../../engines/common.mjs';
const require=createRequire('/workspace/imessage-recreations/engines/package.json');const {chromium}=require('playwright');
const scene=loadScene('/workspace/imessage-recreations/references/02-danieltian/scene-v5-ui-endcards.json');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
await page.setContent('<!doctype html><html><head><style>html,body{margin:0;overflow:hidden}svg{display:block}'+fontCss(scene)+'</style></head><body><div id="stage"></div></body></html>');await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>Promise.all([document.fonts.load('600 96px "Photon Sans"'),document.fonts.load('400 48px "Photon Sans"')]));
for(const frame of [30,1050,1080,1134,1155,1170,1182,1194,1206,1224,1290]){const svg=svgMarkup(scene,frame/30,undefined,false);await page.evaluate(svg=>document.getElementById('stage').innerHTML=svg,svg);await page.screenshot({path:`/workspace/imessage-recreations/outputs/02-danieltian/end-v5-${frame}.png`});}
await browser.close();console.log('Captured11 core UI v5 diagnostic frames');
