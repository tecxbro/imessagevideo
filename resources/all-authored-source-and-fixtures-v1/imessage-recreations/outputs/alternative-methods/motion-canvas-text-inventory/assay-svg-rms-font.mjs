// Private causal glyph assay: SVG's measured RMS font scale, never source pixels.
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {loadScene} from '../../../engines/scene-loader.mjs';
const root=path.resolve('.'),base=path.join(root,'verification/final/motion-canvas-text-baseline52'),out=path.join(base,'rms-assay');fs.mkdirSync(out,{recursive:true});
const scene=loadScene(path.join(base,'dense/scene.json')),{chromium}=createRequire(path.join(root,'engines/package.json'))('playwright');let browser;
try{browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await browser.newPage();await page.setContent('<!doctype html><html><body></body></html>');await page.evaluate(async fonts=>{for(const f of fonts){const face=new FontFace(f.family,`url(${f.src})`,{weight:String(f.weight)});await face.load();document.fonts.add(face);}await document.fonts.ready;},scene.fonts);
 for(const mode of ['rms-ascent','rms-font']){
  const result=await page.evaluate(({cases,mode,width,height})=>{const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;const ctx=canvas.getContext('2d');ctx.fillStyle='#e6e6e6';ctx.fillRect(0,0,width,height);const metrics=[];
   for(const n of cases){ctx.save();const rms=Math.hypot(n.scaleX,n.scaleY)/Math.SQRT2;ctx.textBaseline='alphabetic';ctx.fillStyle=n.fill;ctx.letterSpacing='0px';ctx.font=`400 ${52*rms}px "SF Pro Display"`;const m=ctx.measureText(n.text);let y=m.fontBoundingBoxAscent;
    if(mode==='rms-ascent'){ctx.font='400 52px "SF Pro Display"';ctx.setTransform(n.scaleX,0,0,n.scaleY,n.x,n.y);y/=rms;}else ctx.setTransform(n.scaleX/rms,0,0,n.scaleY/rms,n.x,n.y);
    ctx.fillText(n.text,0,y);ctx.restore();metrics.push({frame:n.frame,rms,scaledFontAscent:m.fontBoundingBoxAscent,scaledTextWidth:m.width,drawY:y});}
   return {png:canvas.toDataURL('image/png'),metrics};},{cases:scene.layers,mode,width:scene.width,height:scene.height});
  fs.writeFileSync(path.join(out,mode+'.png'),Buffer.from(result.png.split(',')[1],'base64'));fs.writeFileSync(path.join(out,mode+'.json'),JSON.stringify(result.metrics,null,2)+'\n');console.log(mode);
 }
}finally{await browser?.close();}
