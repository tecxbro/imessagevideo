import fs from 'node:fs';import {createRequire} from 'node:module';import {execFileSync} from 'node:child_process';
import {loadScene} from '../../engines/scene-loader.mjs';import {svgMarkup,fontCss} from '../../engines/common.mjs';
const root='/workspace/imessage-recreations/references/01-photonhq';const out='/workspace/imessage-recreations/outputs/01-photonhq';const fits=JSON.parse(fs.readFileSync(root+'/wall-title-fit.json','utf8'));let raw=JSON.parse(fs.readFileSync(root+'/scene-wall-v4.json','utf8'));
for(const [name,f] of Object.entries(fits))raw.fonts.push({family:f.family,src:f.font_asset,weight:400});
fs.writeFileSync(root+'/scene-wall-v4.json',JSON.stringify(raw,null,2));let scene=loadScene(root+'/scene-wall-v4.json');
const require=createRequire('/workspace/imessage-recreations/engines/package.json');const {chromium}=require('playwright');const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
await page.setContent('<!doctype html><html><head><style>html,body{margin:0;overflow:hidden}svg{display:block}'+fontCss(scene)+'</style></head><body><div id="stage"></div></body></html>');await page.evaluate(()=>document.fonts.ready);
const metrics={};
for(const [name,f] of Object.entries(fits)){
 const size=f.selected.size;await page.evaluate(async({family,size})=>{await document.fonts.load(`400 ${size}px "${family}"`)},{family:f.family,size});
 const m=await page.evaluate(({family,size,copy})=>{const c=document.createElement('canvas').getContext('2d');c.font=`400 ${size}px "${family}"`;const m=c.measureText(copy);return Object.fromEntries(['actualBoundingBoxLeft','actualBoundingBoxRight','actualBoundingBoxAscent','actualBoundingBoxDescent','fontBoundingBoxAscent','fontBoundingBoxDescent'].map(k=>[k,m[k]]));},{family:f.family,size,copy:f.copy});
 const [x0,y0,x1,y1]=f.source_bbox,sx=(x1-x0)/(m.actualBoundingBoxLeft+m.actualBoundingBoxRight),sy=(y1-y0)/(m.actualBoundingBoxAscent+m.actualBoundingBoxDescent);const layer=raw.layers.find(l=>l.type==='text'&&l.text===f.copy);
 if(!layer)throw new Error('Missing native heading '+name);
 Object.assign(layer,{fontFamily:f.family,fontWeight:400,fontSize:size,x:x0+m.actualBoundingBoxLeft*sx,y:y0-(m.fontBoundingBoxAscent-m.actualBoundingBoxAscent)*sy,scaleX:sx,scaleY:sy});metrics[name]={canvas:m,source_bbox:f.source_bbox,font_family:f.family,font_source:f.selected.name,layer_before_pixel_fit:{...layer}};
}
fs.writeFileSync(root+'/scene-wall-v4.json',JSON.stringify(raw,null,2));scene=loadScene(root+'/scene-wall-v4.json');
const bboxPy=`from PIL import Image\nimport numpy as np,json,sys\na=np.array(Image.open(sys.argv[1]).convert('RGB'));m=(a[470:620,200:1720,:].max(2)<128);y,x=np.where(m);print(json.dumps([int(x.min()+200),int(y.min()+470),int(x.max()+201),int(y.max()+471)]))`;
for(const [name,f] of Object.entries(fits)){
 const file=out+'/wall-v4-'+f.source_frame+'.png';await page.evaluate(svg=>document.getElementById('stage').innerHTML=svg,svgMarkup(scene,f.source_frame/30,undefined,false));await page.screenshot({path:file});
 const bb=JSON.parse(execFileSync('python3',['-c',bboxPy,file],{encoding:'utf8'}));const target=f.source_bbox;const layer=raw.layers.find(l=>l.type==='text'&&l.text===f.copy);const rx=(target[2]-target[0])/(bb[2]-bb[0]),ry=(target[3]-target[1])/(bb[3]-bb[1]);layer.x=target[0]-(bb[0]-layer.x)*rx;layer.y=target[1]-(bb[1]-layer.y)*ry;layer.scaleX*=rx;layer.scaleY*=ry;metrics[name].first_render_bbox=bb;metrics[name].pixel_fit_layer={...layer};
}
fs.writeFileSync(root+'/scene-wall-v4.json',JSON.stringify(raw,null,2));scene=loadScene(root+'/scene-wall-v4.json');
for(const frame of [258,264,270,276,282,324,330,336,342,360,366,372,378,384,396,402,408,414,420,432,438,444,450,456,462]){await page.evaluate(svg=>document.getElementById('stage').innerHTML=svg,svgMarkup(scene,frame/30,undefined,false));await page.screenshot({path:out+'/wall-v4-'+frame+'.png'});}
await browser.close();fs.writeFileSync(root+'/wall-title-native-fit.json',JSON.stringify(metrics,null,2));console.log('Applied phase-specific native font and exact ink-bounds fitting; captured25 wall samples');
