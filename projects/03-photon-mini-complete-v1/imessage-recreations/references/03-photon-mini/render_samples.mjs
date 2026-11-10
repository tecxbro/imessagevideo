import {chromium} from '../../engines/node_modules/playwright/index.mjs';
import {svgMarkup,fontCss} from '../../engines/common.mjs';
import {loadScene} from '../../engines/scene-loader.mjs';
import path from 'node:path';import fs from 'node:fs';import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));let scene=loadScene(path.join(dir,process.argv[2]??'scene.json'));const sampleFolder=process.argv[3]??'sample-rebuild';const sampleTimes=process.argv[4]?process.argv[4].split(',').map(value=>value.startsWith('f:')?Number(value.slice(2))/scene.fps:Number(value)):[0.8,2.5,4,6,8,9.5,11,12.5,14.5,16.5,18.5,20,21.5,22.5,24.5,27,28,29,30,31,32,33.5,35.5,37.5,40.5];
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1920,height:1080}});fs.mkdirSync(path.join(dir,sampleFolder),{recursive:true});
await page.setContent('<head><style>html,body{margin:0;padding:0;}'+fontCss(scene)+'</style></head><body></body>');await page.evaluate(()=>document.fonts.ready);
for(const t of sampleTimes){await page.evaluate(markup=>{document.body.innerHTML=markup},svgMarkup(scene,t,undefined,false));await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))));await page.screenshot({path:path.join(dir,sampleFolder,t+'.png')});}
await browser.close();
