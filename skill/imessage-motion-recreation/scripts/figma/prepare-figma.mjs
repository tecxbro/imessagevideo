#!/usr/bin/env node
// Local preparation only. This module never calls the Figma connector.
import fs from 'node:fs/promises';
import path from 'node:path';
import {sampleTrack} from '../engines/common.mjs';

const args = Object.fromEntries(process.argv.slice(2).reduce((out,v,i,a)=>v.startsWith('--')?[...out,[v.slice(2),a[i+1]]]:out,[]));
if (!args.scene || !args.out) throw new Error('Usage: node figma/prepare-figma.mjs --scene SCENE.json --out OUTPUT_DIRECTORY');
const scenePath=path.resolve(args.scene), scene=JSON.parse(await fs.readFile(scenePath,'utf8'));
const out=path.resolve(args.out), blockers=[], warnings=[
  'UNEXECUTED: no Figma account, file, Motion capability, rasterization, or export was established in this run.',
  'Native text metrics, SVG origin/pivot wrapping, clipping, and fractional frame cadence require exported-frame validation.',
  'Generated absolute layer placement preserves a measured graphic composition; it is not a responsive UI layout.'
];
const allowedKeys=new Set(['x','y','opacity','rotation','scaleX','scaleY','width','height','radius','strokeWidth','fill','stroke']);
const layers=[];
const imageAssets={};
async function inspect(layer,location){
  layers.push({id:layer.id,type:layer.type,location});
  if(!['rect','circle','text','image','path','group'].includes(layer.type)) blockers.push(`${location}: unsupported layer type ${layer.type}`);
  if(layer.clip) blockers.push(`${location}: group clipping needs a native Figma mask adapter`);
  if(layer.shadow) blockers.push(`${location}: shadow conversion needs matching Figma effect semantics`);
  if(layer.blur) blockers.push(`${location}: layer blur conversion is not implemented`);
  for(const p of ['fill','stroke'])if(layer[p] && !/^(#[0-9a-f]{3,8}|none)$/i.test(layer[p]))blockers.push(`${location}: unsupported ${p} paint ${layer[p]}`);
  for(const [key,track] of Object.entries(layer.keyframes??{})){
    if(!allowedKeys.has(key))blockers.push(`${location}: unsupported keyframe property ${key}`);
    if(['width','height'].includes(key)&&['path','group','text'].includes(layer.type))blockers.push(`${location}: ${key} cannot be mapped safely for ${layer.type}`);
    for(const k of track)if(typeof k.t!=='number'||!Number.isFinite(k.t))blockers.push(`${location}: invalid keyframe timestamp`);
  }
  if(layer.type==='image'){
    try{
      let bytes;
      if(layer.src?.startsWith('data:image/'))bytes=Buffer.from(layer.src.split(',')[1],'base64');
      else if(/^[a-z]+:/i.test(layer.src??''))throw new Error('remote images must be downloaded and declared as local static image assets');
      else bytes=await fs.readFile(path.resolve(path.dirname(scenePath),layer.src));
      imageAssets[layer.id]=[...bytes];
    }catch(e){blockers.push(`${location}: image unavailable: ${e.message}`);}
  }
  if(layer.type==='text'){
    if(String(layer.fontFamily??'').includes(','))warnings.push(`${location}: family list must resolve to one exact available Figma font family`);
    if(layer.textAnchor && !['start','middle','end'].includes(layer.textAnchor))blockers.push(`${location}: unknown text anchor`);
  }
  for(const [i,c] of (layer.children??[]).entries())await inspect(c,`${location}.children[${i}]`);
}
for(const [i,l] of scene.layers.entries())await inspect(l,`layers[${i}]`);
if(scene.gradients?.length)blockers.push('Scene uses SVG gradients; native gradient transform conversion must be implemented and validated before import.');
if(scene.fonts?.length)warnings.push('Scene embeds font files for browsers. Those files must be independently available to the Figma account; they are not imported by this script.');
const audit={scene:scenePath,width:scene.width,height:scene.height,fps:scene.fps,duration:scene.duration,layer_count:layers.length,image_count:Object.keys(imageAssets).length,blockers,warnings,execution_status:'unexecuted',layers};
await fs.mkdir(out,{recursive:true});
await fs.writeFile(path.join(out,'audit.json'),JSON.stringify(audit,null,2)+'\n');
await fs.writeFile(path.join(out,'scene-data.json'),JSON.stringify(scene,null,2)+'\n');

// Common evaluator is included as source text so generated Plugin API code is self-contained.
const common=await fs.readFile(new URL('../engines/common.mjs',import.meta.url),'utf8');
const evaluator=common.slice(common.indexOf('function cubic'),common.indexOf('export function stateAt')).replaceAll('export ','');
const code=`// UNEXECUTED conversion prototype. Read audit.json and required Figma skills first.
// Submit only after a known file/session, read-only canvas inspection, and Motion capability probe.
const scene=${JSON.stringify(scene)};
const imageAssets=${JSON.stringify(imageAssets)};
const blockers=${JSON.stringify(blockers)};
if(blockers.length)throw new Error('Preparation has blocking features: '+blockers.join('; '));
${evaluator}
const createdNodeIds=[], mutatedNodeIds=[], nativeFonts=await figma.listAvailableFontsAsync();
const available=nativeFonts.map(x=>x.fontName);
const record=n=>{createdNodeIds.push(n.id);return n;};
const color=s=>{if(!s||s==='none')return null;let v=s.slice(1);if(v.length===3)v=v.split('').map(c=>c+c).join('');return {r:parseInt(v.slice(0,2),16)/255,g:parseInt(v.slice(2,4),16)/255,b:parseInt(v.slice(4,6),16)/255,a:v.length===8?parseInt(v.slice(6,8),16)/255:1};};
const paint=s=>{const c=color(s);return c?[{type:'SOLID',color:{r:c.r,g:c.g,b:c.b},opacity:c.a}]:[];};
const easing=s=>{if(!s||s==='linear')return {type:'LINEAR'};if(s==='hold')return {type:'HOLD'};const named={easeIn:'EASE_IN',easeOut:'EASE_OUT',easeInOut:'EASE_IN_AND_OUT'};if(named[s])return {type:named[s]};const m=s.match(/^cubic-bezier\\(([^)]+)\\)$/);if(m){const [x1,y1,x2,y2]=m[1].split(',').map(Number);return {type:'CUSTOM_CUBIC_BEZIER',easingFunctionCubicBezier:{x1,y1,x2,y2}};}throw new Error('Unknown easing '+s);};
const kf=(k,value)=>({timelinePosition:k.t,value:{type:'FLOAT',value},easing:easing(k.ease)});
const opacityKeys=l=>{const a=l.start??0,b=l.end??scene.duration,track=l.keyframes?.opacity;const at=t=>track?sampleTrack(track,t):(l.opacity??1);const keys=[{t:0,value:a>0?0:at(0)}];if(a>0)keys.push({t:a,value:at(a),ease:'hold'});for(const k of (track??[]))if(k.t>a&&k.t<b)keys.push(k);if(b<scene.duration)keys.push({t:b,value:0,ease:'hold'});return keys;};
function fontFor(l){const family=String(l.fontFamily??'Arial').split(',')[0].trim().replace(/^['\"]|['\"]$/g,'');const fonts=available.filter(f=>f.family===family);if(!fonts.length)throw new Error('Font family unavailable: '+family);const w=Number(l.fontWeight??400),target=w>=800?['Extra Bold','ExtraBold','Black']:w>=700?['Bold']:w>=600?['Semi Bold','SemiBold','Semibold']:w>=500?['Medium']:w<=300?['Light']:['Regular','Normal','Book'];const found=fonts.find(f=>target.some(x=>x.toLowerCase()===f.style.toLowerCase()));if(!found)throw new Error('Exact font style unavailable for '+family+' weight '+w);return found;}
// Validate all declared font families/styles before creating any nodes.
const verifyFonts=async ls=>{for(const l of ls){if(l.type==='text')await figma.loadFontAsync(fontFor(l));await verifyFonts(l.children??[]);}};
await verifyFonts(scene.layers);
const existing=figma.currentPage.children;
const right=existing.reduce((m,n)=>Math.max(m,n.x+n.width),0);
const stage=record(figma.createFrame());stage.name=scene.title??'Measured recreation';stage.resize(scene.width,scene.height);stage.x=right+160;stage.y=80;stage.fills=paint(scene.background??'#ffffff');stage.clipsContent=true;
async function create(l,parent){
  const originX=l.originX??0,originY=l.originY??0;
  const wrapper=record(figma.createFrame());wrapper.name=l.id+' / motion';wrapper.resize(1,1);wrapper.fills=[];wrapper.clipsContent=false;parent.appendChild(wrapper);wrapper.x=(l.x??0)+originX-.5;wrapper.y=(l.y??0)+originY-.5;
  let n;
  if(l.type==='group'){
    n=record(figma.createFrame());n.name=l.id+' / content';n.resize(Math.max(1,l.width??1),Math.max(1,l.height??1));n.fills=[];n.clipsContent=false;
  }else if(l.type==='rect'){n=record(figma.createRectangle());n.resize(Math.max(.01,l.width??1),Math.max(.01,l.height??1));n.cornerRadius=l.radius??0;}
  else if(l.type==='circle'){n=record(figma.createEllipse());const w=l.width??(l.radius??1)*2;n.resize(w,l.height??w);}
  else if(l.type==='text'){
    n=record(figma.createText());n.fontName=fontFor(l);n.fontSize=l.fontSize??32;n.characters=String(l.text??'');n.textAutoResize='WIDTH_AND_HEIGHT';n.lineHeight={unit:'PIXELS',value:l.lineHeight??(l.fontSize??32)*1.2};n.letterSpacing={unit:'PIXELS',value:l.letterSpacing??0};if(l.textDecoration==='underline')n.textDecoration='UNDERLINE';
  }else if(l.type==='image'){
    n=record(figma.createRectangle());n.resize(l.width,l.height);n.fills=[{type:'IMAGE',imageHash:figma.createImage(new Uint8Array(imageAssets[l.id])).hash,scaleMode:'FILL'}];
  }else if(l.type==='path'){n=record(figma.createVector());n.vectorPaths=[{windingRule:'NONZERO',data:l.d}];}
  wrapper.appendChild(n);n.name=l.id;n.x=.5-originX;n.y=.5-originY;
  if(l.type==='text'&&l.textAnchor==='middle')n.x-=n.width/2;if(l.type==='text'&&l.textAnchor==='end')n.x-=n.width;
  if(l.type!=='image'&&l.type!=='group')n.fills=paint(l.fill??'#000000');
  if(l.stroke){n.strokes=paint(l.stroke);n.strokeWeight=l.strokeWidth??0;}
  for(const c of l.children??[])await create(c,n);
  const transformFields={x:'TRANSLATION_X',y:'TRANSLATION_Y',rotation:'ROTATION',scaleX:'SCALE_X',scaleY:'SCALE_Y'};
  const tracks={OPACITY:{keyframes:opacityKeys(l).map(k=>kf(k,k.value))}};
  for(const [p,field] of Object.entries(transformFields)){
    const keys=l.keyframes?.[p]??([{t:0,value:l[p]??(['scaleX','scaleY'].includes(p)?1:0)}]);
    tracks[field]={keyframes:keys.map(k=>kf(k,p==='x'?k.value-(l.x??0):p==='y'?k.value-(l.y??0):p==='rotation'?-k.value:k.value))};
  }
  wrapper.manualKeyframeTracks=tracks;
  const shapeTracks={};
  for(const [p,field]of Object.entries({width:'WIDTH',height:'HEIGHT',radius:'CORNER_RADIUS',strokeWidth:'STROKE_WEIGHT'}))if(l.keyframes?.[p])shapeTracks[field]={keyframes:l.keyframes[p].map(k=>kf(k,k.value))};
  for(const [p,indexed]of Object.entries({fill:'fills',stroke:'strokes'}))if(l.keyframes?.[p])shapeTracks[indexed]={0:{keyframes:l.keyframes[p].map(k=>({timelinePosition:k.t,value:{type:'COLOR',value:color(k.value)},easing:easing(k.ease)}))}};
  if(Object.keys(shapeTracks).length)n.manualKeyframeTracks=shapeTracks;
  return wrapper;
}
const roots=[];for(const l of scene.layers)roots.push(await create(l,stage));
if(roots.length){const [timeline]=roots[0].timelines;if(!timeline)throw new Error('No native Motion timeline was created');if(timeline.duration<scene.duration){roots[0].setTimelineDuration(timeline.id,scene.duration);mutatedNodeIds.push(timeline.id);}}
stage.placeholder=false;
return {createdNodeIds,mutatedNodeIds,stageId:stage.id,width:stage.width,height:stage.height,timeline:roots[0]?.timelines,warning:'Generated conversion was unverified before this write. Export and compare before claiming fidelity.'};
`;
// Parse the body using AsyncFunction to catch generated-JS syntax errors without running Figma APIs.
new (Object.getPrototypeOf(async function(){}).constructor)(code);
await fs.writeFile(path.join(out,'import-native-motion.js'),code);
console.log(JSON.stringify({out,layer_count:layers.length,blockers:blockers.length,warnings:warnings.length,status:'prepared_unexecuted'}));
