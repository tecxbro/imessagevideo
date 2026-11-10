// Read-only sampling probe: a11 before / DOM mapping / explicit Canvas baselines.
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath}from'node:url';
import{build}from'esbuild';import{chromium}from'playwright';
import{loadScene}from'../../scene-loader.mjs';import{svgMarkup,stateAt}from'../../common.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const out=path.join(root,'verification/final/motion-canvas-text-baseline52');fs.mkdirSync(out,{recursive:true});
const source=path.join(root,'outputs/04-poke/final-v19/scene.json');const raw=JSON.parse(fs.readFileSync(source,'utf8'));
const find=(nodes,id)=>{for(const n of nodes){if(n.id===id)return n;const r=find(n.children??[],id);if(r)return r;}};
const p=stateAt(find(raw.layers,'p0135'),400/raw.fps),n=stateAt(find(raw.layers,'p0138'),400/raw.fps);
const x=p.x+p.scaleX*n.x,y=p.y+p.scaleY*n.y,sx=p.scaleX*n.scaleX,sy=p.scaleY*n.scaleY;
const cases=[{id:'unscaled52',x,y:y-200,scaleX:1,scaleY:1},{id:'actual400-world52',x,y,scaleX:sx,scaleY:sy},{id:'uniform52',x,y:y+200,scaleX:sy,scaleY:sy},{id:'vertical52',x,y:y+400,scaleX:1,scaleY:sy}].map(c=>({...c,type:'text',fontFamily:'SF Pro Display',fontWeight:400,fontSize:52,text:'Selected option',fill:'#777777'}));
const fixture={width:1200,height:900,fps:30,duration:1,background:'#e6e6e6',fonts:raw.fonts.filter(f=>f.family==='SF Pro Display'&&f.weight===400).map(f=>({...f,src:path.resolve(path.dirname(source),f.src)})),layers:cases};
const input=path.join(out,'scene.json');fs.writeFileSync(input,JSON.stringify(fixture,null,2));const scene=loadScene(input);
const bundle=path.join(out,'instrument.bundle.js');await build({entryPoints:[path.join(root,'engines/fixtures/text-top-metrics/instrument.mjs')],bundle:true,format:'iife',platform:'browser',outfile:bundle,loader:{'.svg':'text','.css':'text','.glsl':'text'},define:{'import.meta.env.PROD':'true'}});
let browser;try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const mode of ['off','native-dom-prototype']){
  const page=await browser.newPage({viewport:{width:1200,height:900}});
  await page.route('http://font-metrics.local/**',r=>r.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html><head><style>html,body{margin:0}</style></head><body><div id="stage"></div></body></html>'}));
  await page.goto('http://font-metrics.local/');await page.addScriptTag({path:bundle});
  await page.evaluate(({mode,cases})=>{window.metricFixtureMode=mode;window.metricFixtureSequence=cases.map(c=>({id:c.id,text:c.text}));},{mode,cases});
  await page.evaluate(s=>window.TextMetricRuntime.setup(s),scene);const png=await page.evaluate(()=>window.TextMetricRuntime.frame(0));fs.writeFileSync(path.join(out,`${mode}.png`),Buffer.from(png.split(',')[1],'base64'));fs.writeFileSync(path.join(out,`${mode}.json`),JSON.stringify(await page.evaluate(()=>window.textMetricLogs),null,2));
  if(mode==='native-dom-prototype'){
   await page.evaluate(markup=>document.getElementById('stage').innerHTML=markup,svgMarkup(scene,0,undefined,false));await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(out,'svg.png')});
   const svg=await page.evaluate(()=>Array.from(document.querySelectorAll('text')).map(t=>({text:t.textContent,start:{x:t.getStartPositionOfChar(0).x,y:t.getStartPositionOfChar(0).y},bbox:{x:t.getBBox().x,y:t.getBBox().y,width:t.getBBox().width,height:t.getBBox().height}})));fs.writeFileSync(path.join(out,'svg-metrics.json'),JSON.stringify(svg,null,2));
   for(const baseline of ['bottom-fontbox','alphabetic-fontbox','top','effective-ascent']){
    const result=await page.evaluate(({cases,baseline})=>{
     const canvas=document.createElement('canvas');canvas.width=1200;canvas.height=900;const ctx=canvas.getContext('2d');ctx.fillStyle='#e6e6e6';ctx.fillRect(0,0,1200,900);const metrics=[];
     for(const c of cases){ctx.save();ctx.setTransform(c.scaleX,0,0,c.scaleY,c.x,c.y);ctx.font='400 52px "SF Pro Display"';ctx.fillStyle='#777777';ctx.letterSpacing='0px';ctx.textBaseline=baseline==='bottom-fontbox'?'bottom':baseline==='top'?'top':'alphabetic';const m=ctx.measureText(''),before={ascent:m.fontBoundingBoxAscent,descent:m.fontBoundingBoxDescent};let drawY=baseline==='top'?0:m.fontBoundingBoxAscent;let effective=null;
      if(baseline==='effective-ascent'){ctx.font=`400 ${52*c.scaleY}px "SF Pro Display"`;effective=ctx.measureText('').fontBoundingBoxAscent;ctx.font='400 52px "SF Pro Display"';drawY=effective/c.scaleY;}
      ctx.fillText(c.text,0,drawY);metrics.push({id:c.id,baseline,metrics:before,effectiveAscent:effective,drawY});ctx.restore();
     }return{png:canvas.toDataURL('image/png'),metrics};
    },{cases,baseline});fs.writeFileSync(path.join(out,`${baseline}.png`),Buffer.from(result.png.split(',')[1],'base64'));fs.writeFileSync(path.join(out,`${baseline}.json`),JSON.stringify(result.metrics,null,2));
   }
  }
  await page.close();console.log(JSON.stringify({mode,cases:cases.length}));
 }
}finally{await browser?.close();}
