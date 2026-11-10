// Read-only loaded-font impact proof. No Motion Canvas setup/capture or cache writes.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const root=path.resolve('.'),out=path.join(root,'outputs/alternative-methods/motion-canvas-text-inventory');
const require=createRequire(path.join(root,'engines/package.json'));
const {chromium}=require('playwright');
const sha=b=>createHash('sha256').update(b).digest('hex');
const ranges=values=>{const r=[];for(const f of [...new Set(values)].sort((a,b)=>a-b)){if(r.length&&r.at(-1)[1]===f-1)r.at(-1)[1]=f;else r.push([f,f]);}return r;};
const summary=JSON.parse(fs.readFileSync(path.join(out,'summary.json'),'utf8'));
const results=[];let browser;
try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const entry of summary.scenes){
  const inventoryFile=path.join(out,entry.reference+'.json'),bytes=fs.readFileSync(inventoryFile),inventory=JSON.parse(bytes);
  let measurements=[],loadedFonts=[];
  if(inventory.styles.length){
   const context=await browser.newContext();const page=await context.newPage();
   const faces=inventory.fonts.map(font=>{if(font.source==='embedded:data')throw new Error('Inventory font needs explicit asset: '+font.family);const b=fs.readFileSync(font.source);if(sha(b)!==font.sha256)throw new Error('Font changed: '+font.source);return {...font,url:'data:application/octet-stream;base64,'+b.toString('base64')};});
   await page.setContent('<!doctype html><html><head><style>html,body{margin:0;padding:0}</style></head><body></body></html>');
   loadedFonts=await page.evaluate(async faces=>{
    for(const f of faces){const face=new FontFace(f.family,`url(${f.url})`,{weight:String(f.weight),style:f.style});await face.load();document.fonts.add(face);}
    await document.fonts.ready;return [...document.fonts].map(f=>({family:f.family,weight:f.weight,style:f.style,status:f.status}));
   },faces);
   measurements=await page.evaluate(styles=>styles.map(s=>{
    const box=document.createElement('div');Object.assign(box.style,{display:'block',position:'relative',padding:'0',margin:'0',border:'0',whiteSpace:'pre',fontFamily:s.fontFamily,fontWeight:String(s.fontWeight),fontSize:s.fontSize+'px',lineHeight:s.effectiveLineHeightPx+'px'});
    const span=document.createElement('span');span.textContent=(s.examples.find(x=>x.trim())??'Metrics').split('\n')[0];box.append(span);document.body.append(box);
    const css=getComputedStyle(span),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=css.font;ctx.textBaseline='bottom';
    const m=ctx.measureText(''),height=m.fontBoundingBoxAscent+m.fontBoundingBoxDescent,lineHeight=parseFloat(css.lineHeight),range=document.createRange();range.selectNodeContents(span);
    const leading=range.getBoundingClientRect().top-box.getBoundingClientRect().top,delta=-Math.floor((lineHeight-height)/2);
    const result={styleId:s.id,fontCSS:css.font,fontFamily:css.fontFamily,fontWeight:css.fontWeight,fontSize:css.fontSize,actualLineHeightPx:lineHeight,fontBoundingBoxAscent:m.fontBoundingBoxAscent,fontBoundingBoxDescent:m.fontBoundingBoxDescent,naturalFontBoxHeight:height,domLeading:leading,formulaDelta:delta,formulaMatchesDOM:Math.abs(delta+leading)<1e-6,example:span.textContent};
    box.remove();return result;
   }),inventory.styles);
   await context.close();
  }
  const byId=new Map(measurements.map(m=>[m.styleId,m])),nodes=[];
  for(const n of inventory.nodes){const selected=[],usedStyles=new Set();for(const run of n.runs){if(!inventory.texts[run.textId].hasInk)continue;const m=byId.get(run.styleId);if(m?.domLeading!==0||n.defaultLineHeightWithAnimatedFontSize){usedStyles.add(run.styleId);for(let f=run.start;f<=run.end;f++)selected.push(f);}}
   if(selected.length)nodes.push({id:n.id,frameRanges:ranges(selected),frameCount:new Set(selected).size,styleIds:[...usedStyles],historyDependent:n.defaultLineHeightWithAnimatedFontSize,reason:n.defaultLineHeightWithAnimatedFontSize?'Conservative full active node: omitted lineHeight with animated fontSize; actual CSS lineHeight depends on first activation/capture history. Private actual6→40 control proves mapping using actual DOM value.':'Nonzero measured DOM inline-font-box correction on exact active ink runs.'});
  }
  const allFrames=nodes.flatMap(n=>n.frameRanges.flatMap(([a,b])=>Array.from({length:b-a+1},(_,i)=>a+i)));
  const result={reference:inventory.reference,input:inventory.input,sceneSha256:inventory.sceneSha256,inventorySha256:sha(bytes),fontSha256:inventory.fonts.map(f=>({family:f.family,weight:f.weight,sha256:f.sha256})),loadedFonts,measurements,candidateNodes:nodes,candidateFrameRanges:ranges(allFrames),candidateFrameCount:new Set(allFrames).size,formulaMismatches:measurements.filter(m=>!m.formulaMatchesDOM),note:'Candidate actor visibility is exact lifecycle/positive opacity, conservatively includes offscreen/occluded actors. No production runtime or native PNG changed.'};
  fs.writeFileSync(path.join(out,inventory.reference+'.font-metrics.json'),JSON.stringify(result,null,2)+'\n');results.push({reference:result.reference,sceneSha256:result.sceneSha256,styles:measurements.length,nonzeroStyles:measurements.filter(m=>m.domLeading!==0).length,formulaNonzeroStyles:measurements.filter(m=>m.formulaDelta!==0).length,candidateNodes:nodes.length,candidateFrameRanges:result.candidateFrameRanges,candidateFrameCount:result.candidateFrameCount,formulaMismatches:result.formulaMismatches.length});console.log(JSON.stringify(results.at(-1)));
 }
}finally{await browser?.close();}
fs.writeFileSync(path.join(out,'font-impact-summary.json'),JSON.stringify({status:'Read-only loaded-font metrics and conservative actor/frame impact proof; not capture authority.',inventorySummarySha256:sha(fs.readFileSync(path.join(out,'summary.json'))),scenes:results},null,2)+'\n');
