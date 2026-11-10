// Read-only actual-font/text/prefix shaping audit, including unit-RMS text.
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';
const root=path.resolve('.'),out=path.join(root,'outputs/alternative-methods/motion-canvas-kerning-inventory'),{chromium}=createRequire(path.join(root,'engines/package.json'))('playwright');
const refs=['01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery'];
const ranges=values=>{const r=[];for(const f of [...new Set(values)].sort((a,b)=>a-b)){if(r.length&&r.at(-1)[1]===f-1)r.at(-1)[1]=f;else r.push([f,f]);}return r;};
let browser;const summary=[];
try{browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const name of refs){const inv=JSON.parse(fs.readFileSync(path.join(out,name+'.json'),'utf8')),pairs=[],pairIds=new Map(),runs=[];
  for(const node of inv.nodes)for(const run of node.runs){const raw=inv.texts[run.textId];if(!raw.hasInk)continue;const matrix=inv.transforms[run.transformId].worldLinear,rms=Math.hypot(...matrix)/Math.SQRT2;const key=JSON.stringify([run.styleId,run.textId,rms]);let id=pairIds.get(key);if(id===undefined){id=pairs.length;pairIds.set(key,id);pairs.push({id,style:inv.styles[run.styleId],text:raw.text,rms});}runs.push({nodeId:node.id,...run,pairId:id});}
  let measurements=[];
  if(pairs.length){const context=await browser.newContext(),page=await context.newPage();page.setDefaultTimeout(120000);await page.setContent('<!doctype html><html><body></body></html>');
   await page.evaluate(async fonts=>{for(const f of fonts){const face=new FontFace(f.family,`url(data:application/octet-stream;base64,${f.data})`,{weight:String(f.weight),style:f.style});await face.load();document.fonts.add(face);}await document.fonts.ready;},inv.fonts.map(f=>({...f,data:fs.readFileSync(f.source).toString('base64')})));
   measurements=await page.evaluate(pairs=>{
    const ctx=document.createElement('canvas').getContext('2d'),fontByStyle=new Map(),keys=['width','actualBoundingBoxLeft','actualBoundingBoxRight','actualBoundingBoxAscent','actualBoundingBoxDescent'];ctx.textBaseline='alphabetic';ctx.textRendering='auto';
    const metric=t=>{const m=ctx.measureText(t);return keys.map(k=>m[k]);};
    const differs=(a,b)=>a.some((x,i)=>Math.abs(x-b[i])>1e-9);
    function compareLine(text,font,spacing){ctx.font=font;ctx.letterSpacing=spacing+'px';let prefix='',prefixChanged=false,maxMetricDifference=0,fullAuto,fullNormal;for(const c of [...text]){prefix+=c;ctx.fontKerning='auto';const a=metric(prefix);ctx.fontKerning='normal';const b=metric(prefix);prefixChanged||=differs(a,b);maxMetricDifference=Math.max(maxMetricDifference,...a.map((x,i)=>Math.abs(x-b[i])));fullAuto=a;fullNormal=b;}return {prefixChanged,maxMetricDifference,autoAdvance:fullAuto?.[0]??0,normalAdvance:fullNormal?.[0]??0,totalAdvanceChanged:Math.abs((fullAuto?.[0]??0)-(fullNormal?.[0]??0))>1e-9};}
    return pairs.map(p=>{let font=fontByStyle.get(p.style.id);if(!font){const span=document.createElement('span');Object.assign(span.style,{fontFamily:p.style.fontFamily,fontWeight:String(p.style.fontWeight),fontSize:p.style.fontSize+'px',lineHeight:p.style.effectiveLineHeightPx+'px'});span.textContent='x';document.body.append(span);ctx.font=getComputedStyle(span).font;font=ctx.font;fontByStyle.set(p.style.id,font);span.remove();}
     const scaled=font.replace(/([\d.]+)px/,(_,size)=>`${Number(size)*p.rms}px`),anchor=({start:0,middle:.5,end:1})[p.style.textAnchor??'start'],lines=[];
     for(const raw of p.text.split('\n'))for(const trailing of [false,true]){const text=(raw+(trailing?'\n':'')).replace(/\s+/g,' ');if(!text.trim())continue;const local=compareLine(text,font,p.style.letterSpacing??0),paint=compareLine(text,scaled,(p.style.letterSpacing??0)*p.rms);lines.push({text,trailingNewlineVariant:trailing,local,paint});}
     return {pairId:p.id,styleId:p.style.id,rms:p.rms,fontCSS:font,paintFontCSS:scaled,letterSpacing:p.style.letterSpacing??0,anchor,text:p.text,lines,paintPrefixOrInkChanged:lines.some(l=>l.paint.prefixChanged),anchorOldWidthChanged:anchor!==0&&lines.some(l=>l.local.totalAdvanceChanged),candidate:lines.some(l=>l.paint.prefixChanged)||(anchor!==0&&lines.some(l=>l.local.totalAdvanceChanged))};
    });
   },pairs);await context.close();
  }
  const nodes=new Map();for(const r of runs)if(measurements[r.pairId].candidate){if(!nodes.has(r.nodeId))nodes.set(r.nodeId,[]);for(let f=r.start;f<=r.end;f++)nodes.get(r.nodeId).push(f);}
  const nodeRows=[...nodes].map(([id,frames])=>({id,ranges:ranges(frames),frames:new Set(frames).size})),all=nodeRows.flatMap(n=>n.ranges.flatMap(([a,b])=>Array.from({length:b-a+1},(_,i)=>a+i)));
  const result={reference:name,sceneSha256:inv.sceneSha256,status:'Read-only metric candidate scope; not production authority. Both local old-width and RMS paint policy changes covered; multiline newline variants are conservative.',metricPolicy:'Compare auto/normal width+ink metrics for every actual text prefix at local and RMS font sizes/spacing. Include painted differences and anchored local advance changes, including RMS1.',pairCount:pairs.length,candidatePairCount:measurements.filter(m=>m.candidate).length,candidateRanges:ranges(all),candidateFrames:new Set(all).size,candidateNodes:nodeRows,measurements};
  fs.writeFileSync(path.join(out,name+'.kerning.json'),JSON.stringify(result,null,2)+'\n');summary.push({...result,measurements:undefined,candidateNodes:undefined});console.log(JSON.stringify(summary.at(-1)));global.gc?.();
 }
}finally{await browser?.close();}
fs.writeFileSync(path.join(out,'impact-summary.json'),JSON.stringify({status:'All-six read-only actual font/text/prefix impact audit, pending private safety gate',scenes:summary},null,2)+'\n');
