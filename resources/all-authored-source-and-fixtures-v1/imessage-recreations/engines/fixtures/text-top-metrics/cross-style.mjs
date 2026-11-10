// Actual eight multiline styles plus the only current fallback-symbol Txt.
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';import {build} from 'esbuild';
import {loadScene} from '../../scene-loader.mjs';import {svgMarkup} from '../../common.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const dom=process.argv.includes('--dom');const out=path.join(root,'verification/final/06-gallery/v23/text-metric-diagnosis',dom?'cross-style-dom':'cross-style');fs.mkdirSync(out,{recursive:true});
const inventories=['03-photon-mini','04-poke'].map(name=>JSON.parse(fs.readFileSync(path.join(root,'outputs/alternative-methods/motion-canvas-text-inventory',name+'.json'),'utf8')));
const fonts=inventories.flatMap(s=>s.fonts.map(f=>({family:f.family,weight:f.weight,src:f.source})));
const cases=[];
for(const inventory of inventories)for(const node of inventory.nodes)if(node.flags.multiline||node.flags.emoji){
 const run=node.runs[0],style=inventory.styles[run.styleId],text=inventory.texts[run.textId].text;
 cases.push({id:node.id,text,type:'text',x:80,y:20+cases.length*180,fontFamily:style.fontFamily,fontSize:style.fontSize,fontWeight:style.fontWeight,lineHeight:style.effectiveLineHeightPx,fill:'#ffffff'});
}
if(dom){const style=inventories[1].styles.find(s=>s.id===51);cases.push({id:'04-p0015-fractional-style51',type:'text',text:'Poke',x:80,y:20+cases.length*180,fontFamily:style.fontFamily,fontWeight:style.fontWeight,fontSize:style.fontSize,lineHeight:style.effectiveLineHeightPx,fill:'#ffffff'});}
const fixture={width:1600,height:180*cases.length,fps:30,duration:1,background:'#090909',fonts,layers:cases};
const input=path.join(out,'scene.json');fs.writeFileSync(input,JSON.stringify(fixture,null,2));const scene=loadScene(input);
const bundle=path.join(out,'instrument.bundle.js');await build({entryPoints:[path.join(root,'engines/fixtures/text-top-metrics/instrument.mjs')],bundle:true,format:'iife',platform:'browser',outfile:bundle,loader:{'.svg':'text','.css':'text','.glsl':'text'},define:{'import.meta.env.PROD':'true'}});
let browser;try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const mode of (dom?['off','native-prototype','native-dom-prototype']:['off','native-prototype'])){
  const page=await browser.newPage({viewport:{width:fixture.width,height:fixture.height}});
  await page.route('http://font-metrics.local/**',r=>r.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html><head><style>html,body{margin:0}</style></head><body><div id="stage"></div></body></html>'}));
  await page.goto('http://font-metrics.local/');await page.addScriptTag({path:bundle});
  await page.evaluate(({mode,sequence})=>{window.metricFixtureMode=mode;window.metricFixtureSequence=sequence;},{mode,sequence:cases.flatMap(c=>c.text.split('\n').map(text=>({id:c.id,text})))});
  await page.evaluate(scene=>window.TextMetricRuntime.setup(scene),scene);
  const png=await page.evaluate(()=>window.TextMetricRuntime.frame(0));fs.writeFileSync(path.join(out,`${mode}.png`),Buffer.from(png.split(',')[1],'base64'));
  fs.writeFileSync(path.join(out,`${mode}.json`),JSON.stringify(await page.evaluate(()=>window.textMetricLogs),null,2));
  await page.evaluate(markup=>document.getElementById('stage').innerHTML=markup,svgMarkup(scene,0,undefined,false));await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(out,'svg.png')});
  await page.close();console.log(JSON.stringify({mode,cases:cases.length}));
 }
}finally{await browser?.close();}
