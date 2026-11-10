// Private diagnostic only: production runtime, scenes and output caches are read-only.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from 'esbuild';
import {chromium} from 'playwright';
import {loadScene} from '../../scene-loader.mjs';
import {sceneForFrames} from '../../runtime-scene.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const out=path.join(root,'verification/final/06-gallery/v23/text-metric-diagnosis/actual');
fs.mkdirSync(out,{recursive:true});
const input=path.join(root,'outputs/06-gallery/final-v23/scene.json');
const raw=JSON.parse(fs.readFileSync(input,'utf8'));
const bundle=path.join(out,'instrument.bundle.js');
await build({entryPoints:[path.join(root,'engines/fixtures/text-top-metrics/instrument.mjs')],bundle:true,format:'iife',platform:'browser',outfile:bundle,loader:{'.svg':'text','.css':'text','.glsl':'text'},define:{'import.meta.env.PROD':'true'}});
let browser;
try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const frame of [1067,1106,552]){
  const pruned=sceneForFrames(raw,[frame]);
  const absolute=layer=>{if(layer.src&&!/^(data:|https?:)/.test(layer.src))layer.src=path.resolve(path.dirname(input),layer.src);for(const child of layer.children??[])absolute(child);};
  pruned.layers.forEach(absolute);
  for(const font of pruned.fonts??[])font.src=path.resolve(path.dirname(input),font.src);
  const filename=path.join(out,`frame-${frame}-scene.json`);
  fs.writeFileSync(filename,JSON.stringify(pruned));
  const scene=loadScene(filename);
  for(const mode of (process.argv.includes('--dom')?['native-dom-prototype']:process.argv.includes('--native-prototype')?['native-prototype']:['off','formula'])){
   const page=await browser.newPage({viewport:{width:raw.width,height:raw.height}});
   page.setDefaultTimeout(120000);
   await page.route('http://font-metrics.local/**',r=>r.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html><head><style>html,body{margin:0}</style></head><body></body></html>'}));
   await page.goto('http://font-metrics.local/');
   await page.addScriptTag({path:bundle});
   await page.evaluate(mode=>{window.metricFixtureMode=mode;},mode);
   await page.evaluate(scene=>window.TextMetricRuntime.setup(scene),scene);
   const png=await page.evaluate(frame=>window.TextMetricRuntime.frame(frame),frame);
   fs.writeFileSync(path.join(out,`${frame}-${mode}.png`),Buffer.from(png.split(',')[1],'base64'));
   const logs=await page.evaluate(()=>({metrics:window.textMetricLogs,diagnostics:window.TextMetricRuntime.diagnostics()}));
   fs.writeFileSync(path.join(out,`${frame}-${mode}.json`),JSON.stringify(logs,null,2));
   await page.close();
   console.log(JSON.stringify({frame,mode,draws:logs.metrics.length,diagnostics:logs.diagnostics}));
  }
 }
}finally{await browser?.close();}
