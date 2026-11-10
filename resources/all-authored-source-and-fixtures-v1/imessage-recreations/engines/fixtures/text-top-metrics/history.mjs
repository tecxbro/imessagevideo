// Isolate the one actual omitted-lineHeight/fontSize animation, without source art.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {build} from 'esbuild';
import {loadScene} from '../../scene-loader.mjs';
import {svgMarkup,stateAt} from '../../common.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const dom=process.argv.includes('--dom');const out=path.join(root,'verification/final/06-gallery/v23/text-metric-diagnosis',dom?'history-dom':'history');fs.mkdirSync(out,{recursive:true});
const input=path.join(root,'outputs/04-poke/final-v19/scene.json');
const raw=JSON.parse(fs.readFileSync(input,'utf8'));
const find=nodes=>{for(const node of nodes){if(node.id==='p0015')return node;const child=find(node.children??[]);if(child)return child;}};
const node=find(raw.layers);
const text={id:'p0015-history',type:'text',text:'Poke',x:80,y:40,start:node.start,end:node.end,fontFamily:node.fontFamily,fontWeight:node.fontWeight,fontSize:node.fontSize,fill:'#ffffff',keyframes:{fontSize:node.keyframes.fontSize}};
const fixture={width:800,height:250,duration:5,fps:raw.fps,background:'#090909',fonts:raw.fonts.map(font=>({...font,src:path.resolve(path.dirname(input),font.src)})),layers:[text]};
const file=path.join(out,'scene.json');fs.writeFileSync(file,JSON.stringify(fixture));const scene=loadScene(file);
const bundle=path.join(out,'instrument.bundle.js');await build({entryPoints:[path.join(root,'engines/fixtures/text-top-metrics/instrument.mjs')],bundle:true,format:'iife',platform:'browser',outfile:bundle,loader:{'.svg':'text','.css':'text','.glsl':'text'},define:{'import.meta.env.PROD':'true'}});
let browser;
try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const mode of ['off',dom?'native-dom-prototype':'native-prototype']){
  const page=await browser.newPage({viewport:{width:800,height:250}});
  await page.route('http://font-metrics.local/**',r=>r.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html><head><style>html,body{margin:0}</style></head><body><div id="stage"></div></body></html>'}));
  await page.goto('http://font-metrics.local/');await page.addScriptTag({path:bundle});
  await page.evaluate(mode=>window.metricFixtureMode=mode,mode);
  await page.evaluate(scene=>window.TextMetricRuntime.setup(scene),scene);
  await page.evaluate(()=>window.TextMetricRuntime.frame(6));
  await page.evaluate(()=>window.textMetricLogs=[]);
  const png=await page.evaluate(()=>window.TextMetricRuntime.frame(40));
  fs.writeFileSync(path.join(out,`${mode}.png`),Buffer.from(png.split(',')[1],'base64'));
  const logs=await page.evaluate(()=>window.textMetricLogs);fs.writeFileSync(path.join(out,`${mode}.json`),JSON.stringify(logs,null,2));
  await page.evaluate(markup=>document.getElementById('stage').innerHTML=markup,svgMarkup(scene,40/scene.fps,undefined,false));await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(out,'svg.png')});
  console.log(JSON.stringify({mode,initialSize:stateAt(text,6/scene.fps).fontSize,finalSize:stateAt(text,40/scene.fps).fontSize,logs}));
  await page.close();
 }
}finally{await browser?.close();}
