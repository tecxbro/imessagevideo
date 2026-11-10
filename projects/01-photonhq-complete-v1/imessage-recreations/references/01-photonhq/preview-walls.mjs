import fs from 'node:fs';import {createRequire} from 'node:module';
import {loadScene} from '../../engines/scene-loader.mjs';import {svgMarkup,fontCss} from '../../engines/common.mjs';
const require=createRequire('/workspace/imessage-recreations/engines/package.json');const {chromium}=require('playwright');
const scene=loadScene('/workspace/imessage-recreations/references/01-photonhq/scene-wall-v4.json');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
await page.setContent('<!doctype html><html><head><style>html,body{margin:0;overflow:hidden}svg{display:block}'+fontCss(scene)+'</style></head><body><div id="stage"></div></body></html>');await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>Promise.all([document.fonts.load('600 96px "Photon Sans"'),document.fonts.load('400 48px "Photon Sans"')]));
for(const frame of [246,252,258,264,270,276,282,288,294,318,324,330,336,342,348,351,354,360,366,372,378,384,387,390,393,396,402,408,414,420,423,426,429,432,438,444,450,456,462,465,468,471]){const svg=svgMarkup(scene,frame/30,undefined,false);await page.evaluate(svg=>document.getElementById('stage').innerHTML=svg,svg);await page.screenshot({path:`/workspace/imessage-recreations/outputs/01-photonhq/wall-v4-${frame}.png`});}
await browser.close();console.log('Captured 42 wall diagnostic frames including phase boundaries');
