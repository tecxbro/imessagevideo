// Font metrics only; never renders a scene or replaces native capture pixels.
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';
const root=path.resolve('.'),out=path.join(root,'outputs/alternative-methods/motion-canvas-text-inventory'),{chromium}=createRequire(path.join(root,'engines/package.json'))('playwright');
let browser;
try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for(const name of ['02-danieltian','03-photon-mini','04-poke','06-gallery']){
  const inventory=JSON.parse(fs.readFileSync(path.join(out,name+'.json'),'utf8'));const context=await browser.newContext(),page=await context.newPage();await page.setContent('<!doctype html><html><body style="margin:0"></body></html>');
  await page.evaluate(async fonts=>{for(const f of fonts){const face=new FontFace(f.family,`url(data:application/octet-stream;base64,${f.data})`,{weight:String(f.weight),style:f.style});await face.load();document.fonts.add(face);}await document.fonts.ready;},inventory.fonts.map(f=>({...f,data:fs.readFileSync(f.source).toString('base64')})));
  const rows=await page.evaluate(styles=>styles.map(s=>{
   const text=(s.examples.find(x=>x.trim())??'M').split('\n')[0],canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=`${s.fontWeight} ${s.fontSize}px ${s.fontFamily}`;ctx.textBaseline='alphabetic';const m=ctx.measureText('');
   const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('width','4000');svg.setAttribute('height','400');document.body.append(svg);
   const texts=['alphabetic','text-before-edge'].map(baseline=>{const t=document.createElementNS(svg.namespaceURI,'text');t.setAttribute('font-family',s.fontFamily);t.setAttribute('font-weight',String(s.fontWeight));t.setAttribute('font-size',String(s.fontSize));t.setAttribute('dominant-baseline',baseline);t.textContent=text;svg.append(t);return t;});
   const result={styleId:s.id,fontFamily:s.fontFamily,fontWeight:s.fontWeight,fontSize:s.fontSize,canvasAlphabeticFontAscent:m.fontBoundingBoxAscent,canvasAlphabeticFontDescent:m.fontBoundingBoxDescent,text};
   for(let i=0;i<2;i++){const t=texts[i],b=t.getBBox(),p=t.getStartPositionOfChar(0);result[i?'svgBeforeEdge':'svgAlphabetic']={bbox:{x:b.x,y:b.y,width:b.width,height:b.height},start:{x:p.x,y:p.y}};}
   result.svgBaselineTranslation=result.svgBeforeEdge.start.y-result.svgAlphabetic.start.y;result.bboxTranslation=result.svgBeforeEdge.bbox.y-result.svgAlphabetic.bbox.y;result.extraVsCanvasFontAscent=result.svgBaselineTranslation-m.fontBoundingBoxAscent;svg.remove();return result;
  }),inventory.styles);
  await context.close();fs.writeFileSync(path.join(out,name+'.svg-font-metrics.json'),JSON.stringify({reference:name,sceneSha256:inventory.sceneSha256,status:'read-only font-metric diagnosis; no production runtime/capture changed',styles:rows},null,2)+'\n');console.log(JSON.stringify({reference:name,nonzeroExtra:rows.filter(r=>r.extraVsCanvasFontAscent!==0).map(r=>({style:r.styleId,size:r.fontSize,extra:r.extraVsCanvasFontAscent,svgBaseline:r.svgBaselineTranslation,canvasAscent:r.canvasAlphabeticFontAscent}))}));
 }
}finally{await browser?.close();}
