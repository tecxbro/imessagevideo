// Read-only all-active-Txt/world-transform metric audit. No native scene capture.
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';
const root=path.resolve('.'),out=path.join(root,'outputs/alternative-methods/motion-canvas-text-inventory'),{chromium}=createRequire(path.join(root,'engines/package.json'))('playwright');
const ranges=values=>{const r=[];for(const f of [...new Set(values)].sort((a,b)=>a-b)){if(r.length&&r.at(-1)[1]===f-1)r.at(-1)[1]=f;else r.push([f,f]);}return r;};
const references=['01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery'],summary=[];let browser;
try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const name of references){
  const inv=JSON.parse(fs.readFileSync(path.join(out,name+'.json'),'utf8')),pairs=[],byKey=new Map(),nodeRuns=[];
  for(const node of inv.nodes)for(const run of node.runs){if(!inv.texts[run.textId].hasInk)continue;const style=inv.styles[run.styleId],transform=inv.transforms[run.transformId],sy=transform.worldYGain,key=JSON.stringify([run.styleId,sy]);let id=byKey.get(key);if(id===undefined){id=pairs.length;byKey.set(key,id);pairs.push({id,styleId:run.styleId,worldSY:sy,style});}nodeRuns.push({id:node.id,...run,pairId:id});}
  let measurements=[];
  if(pairs.length){const context=await browser.newContext(),page=await context.newPage();await page.setContent('<!doctype html><html><body style="margin:0"></body></html>');
   await page.evaluate(async fonts=>{for(const f of fonts){const face=new FontFace(f.family,`url(data:application/octet-stream;base64,${f.data})`,{weight:String(f.weight),style:f.style});await face.load();document.fonts.add(face);}await document.fonts.ready;},inv.fonts.map(f=>({...f,data:fs.readFileSync(f.source).toString('base64')})));
   measurements=await page.evaluate(pairs=>{const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),styleFonts=new Map();return pairs.map(p=>{
    let font=styleFonts.get(p.styleId);if(!font){const span=document.createElement('span');Object.assign(span.style,{fontFamily:p.style.fontFamily,fontSize:p.style.fontSize+'px',fontWeight:String(p.style.fontWeight),lineHeight:p.style.effectiveLineHeightPx+'px'});span.textContent='x';document.body.append(span);const css=getComputedStyle(span);ctx.font=css.font;font={fontCSS:ctx.font,computedFontSize:parseFloat(css.fontSize)};styleFonts.set(p.styleId,font);span.remove();}
    ctx.font=font.fontCSS;ctx.textBaseline='alphabetic';const localAscent=ctx.measureText('').fontBoundingBoxAscent;const effectiveFontSize=font.computedFontSize*p.worldSY;let effectiveAscent=null,extra=0;
    if(p.worldSY>1e-12){ctx.font=font.fontCSS.replace(/[0-9]*\.?[0-9]+px/,effectiveFontSize+'px');effectiveAscent=ctx.measureText('').fontBoundingBoxAscent;extra=effectiveAscent/p.worldSY-localAscent;}
    return {pairId:p.id,styleId:p.styleId,worldSY:p.worldSY,...font,localAscent,effectiveFontSize,effectiveAscent,rawExtraLocalY:extra,extraLocalY:Math.abs(extra)<1e-9?0:extra};
   });},pairs);await context.close();
  }
  const affected=new Map();for(const r of nodeRuns)if(measurements[r.pairId].extraLocalY!==0){if(!affected.has(r.id))affected.set(r.id,[]);for(let f=r.start;f<=r.end;f++)affected.get(r.id).push(f);}
  const nodes=[...affected].map(([id,frames])=>({id,frameRanges:ranges(frames),frames:new Set(frames).size})),all=nodes.flatMap(n=>n.frameRanges.flatMap(([a,b])=>Array.from({length:b-a+1},(_,i)=>a+i))),previous=JSON.parse(fs.readFileSync(path.join(out,name+'.font-metrics.json'),'utf8'));
  let sceneSha256=inv.sceneSha256;if(name==='05-linq')sceneSha256=JSON.parse(fs.readFileSync(path.join(out,'05-target20-text-audit.json'),'utf8')).sceneSha256;
  const result={reference:name,sceneSha256,status:'Metric candidates only. No runtime promotion; private native/blur/rotation controls still required.',rule:'extra=(Canvas alphabetic ascent at computedFontSize*worldSY)/worldSY − localCanvas alphabetic ascent. WorldSY is authored world-space Y gain, not offscreen cache density. Abs<1e-9 numerical noise is zero.',allActiveInkNodeRuns:nodeRuns.length,measurements,candidateNodes:nodes,extraCandidateRanges:ranges(all),extraCandidateFrames:new Set(all).size,previousDOMCandidateRanges:previous.candidateFrameRanges};
  if(name==='03-photon-mini'){const combined=[...all,...previous.candidateFrameRanges.flatMap(([a,b])=>Array.from({length:b-a+1},(_,i)=>a+i))];result.directA11CombinedCandidateRanges=ranges(combined);result.directA11CombinedCandidateFrames=new Set(combined).size;}
  fs.writeFileSync(path.join(out,name+'.effective-ascent.json'),JSON.stringify(result,null,2)+'\n');const {measurements:_,candidateNodes:__,...short}=result;summary.push(short);console.log(JSON.stringify(short));
 }
}finally{await browser?.close();}
fs.writeFileSync(path.join(out,'effective-ascent-impact-summary.json'),JSON.stringify({status:'read-only all-active-frame/worldSY audit, not capture authority',scenes:summary},null,2)+'\n');
