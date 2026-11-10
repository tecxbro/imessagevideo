import {makeScene2D,Node,Rect,Circle,Txt,Path,Img,Gradient,blur} from '@motion-canvas/2d';
import {Renderer,Logger,ValueDispatcher,Vector2} from '@motion-canvas/core';
import {stateAt,fontCss} from '../../common.mjs';
import {TxtLeaf} from '../../node_modules/@motion-canvas/2d/lib/components/TxtLeaf.js';

// Match SVG's font-box origin and transform-dependent glyph shaping without
// changing native actors/layout. Browser SVG shapes fonts at the RMS world scale
// and compensates its paint transform. Canvas otherwise shapes at local size,
// which can move hinted glyphs by a pixel even with identical logical origins.
const nativeDrawText=TxtLeaf.prototype.drawText;
TxtLeaf.prototype.drawText=function(context,text,box){
 if(!text)return nativeDrawText.call(this,context,text,box);
 const range=document.createRange();range.selectNodeContents(this.element);
 const parent=this.parent()?.element;
 const delta=parent?-(range.getBoundingClientRect().top-parent.getBoundingClientRect().top):0;
 const aligned=delta&&Number.isFinite(delta)?{x:box.x,y:box.y+delta}:box;
 const world=this.localToWorld(),rms=Math.hypot(world.a,world.b,world.c,world.d)/Math.SQRT2;
 // Preserve the established native branch literally when no shaping scale is
 // needed. World scale, not the density of an offscreen blur cache, is relevant.
 if(!text.trim()||!Number.isFinite(rms)||rms<=0||Math.abs(rms-1)<1e-9)return nativeDrawText.call(this,context,text,aligned);
 const normalized=text.replace(/\s+/g,' '),oldMetrics=context.measureText(''),oldWidth=context.measureText(normalized).width;
 const font=context.font.replace(/([\d.]+)px/,(_,size)=>`${Number(size)*rms}px`);
 context.save();
 try{
  context.font=font;context.textBaseline='alphabetic';
  if('letterSpacing'in context)context.letterSpacing=`${this.letterSpacing()*rms}px`;
  const metrics=context.measureText(''),width=context.measureText(normalized).width;
  const anchor=(this.parent().offset().x+1)/2,xCorrection=(oldWidth-width/rms)*anchor;
  const x=(aligned.x+xCorrection)*rms,y=(aligned.y-oldMetrics.fontBoundingBoxAscent)*rms+metrics.fontBoundingBoxAscent;
  context.scale(1/rms,1/rms);context.lineWidth*=rms;
  return nativeDrawText.call(this,context,text,{x,y});
 }finally{context.restore();}
};

// Local-space native component compositor: children remain Scene2D nodes.
class LocalSpaceBlurNode extends Node {
 constructor(){super({});this.amount=0;this.localShadow=null;this.sourceCanvas=null;this.filteredCanvas=null;}
 setAmount(value){if(value===this.amount)return false;this.amount=value;this.updatePadding();return true;}
 setShadow(value){if(value===this.localShadow)return false;this.localShadow=value;this.updatePadding();return true;}
 updatePadding(){const s=this.localShadow;this.cachePadding(this.amount||s?this.amount*3+(s?(s.blur??0)*3+Math.max(Math.abs(s.x??0),Math.abs(s.y??0)):0)+2:0);}
 draw(context){
  if(!this.amount&&!this.localShadow){super.draw(context);return;}
  const bbox=this.cacheBBox(),x=Math.floor(bbox.x),y=Math.floor(bbox.y),width=Math.ceil(bbox.x+bbox.width)-x,height=Math.ceil(bbox.y+bbox.height)-y;
  if(width<=0||height<=0)return;
  this.sourceCanvas??=document.createElement('canvas');this.filteredCanvas??=document.createElement('canvas');
  const density=Math.min(2,16380/Math.max(width,height),Math.sqrt(8000000/(width*height))),w=Math.max(1,Math.ceil(width*density)),h=Math.max(1,Math.ceil(height*density));
  for(const canvas of [this.sourceCanvas,this.filteredCanvas]){if(canvas.width!==w)canvas.width=w;if(canvas.height!==h)canvas.height=h;}
  const source=this.sourceCanvas.getContext('2d'),filtered=this.filteredCanvas.getContext('2d');
  source.setTransform(1,0,0,1,0,0);source.clearRect(0,0,w,h);source.setTransform(density,0,0,density,-x*density,-y*density);this.drawChildren(source);
  filtered.setTransform(1,0,0,1,0,0);filtered.clearRect(0,0,w,h);const filters=[];if(this.localShadow){const s=this.localShadow;filters.push(`drop-shadow(${(s.x??0)*density}px ${(s.y??0)*density}px ${(s.blur??0)*density}px ${s.color??'#000000'})`);}if(this.amount)filters.push(`blur(${this.amount*density}px)`);filtered.filter=filters.join(' ')||'none';filtered.drawImage(this.sourceCanvas,0,0);filtered.filter='none';
  context.drawImage(this.filteredCanvas,x,y,w/density,h/density);
 }
}

let renderer,settings,scene,logs=[],liveEntries=[],initialized=false,lastPng=null;
const colorValue=v=>v===undefined||v===null||v==='none'||v==='transparent'?null:v;
const percent=(v,size,def=0)=>v===undefined?def:typeof v==='string'&&v.endsWith('%')?parseFloat(v)*size/100:Number(v);
function fillFor(value,shape){
 if(!String(value??'').startsWith('url('))return colorValue(value??'#000000');
 const id=String(value).match(/^url\(#([^)]*)\)$/)?.[1],g=scene.gradients?.find(g=>g.id===id);if(!g)throw new Error('Unknown gradient '+id);
 const w=shape.width(),h=shape.height(),bbox=shape instanceof Path?shape.childrenBBox():{x:-w/2,y:-h/2},stops=g.stops.map(s=>({offset:percent(s.offset,1),color:s.opacity===undefined?s.color:withAlpha(s.color,s.opacity)}));
 if(g.type==='radial'){const center=[percent(g.cx,w,w/2)+bbox.x,percent(g.cy,h,h/2)+bbox.y];return new Gradient({type:'radial',from:center,to:center,fromRadius:0,toRadius:percent(g.r,Math.hypot(w,h)/Math.SQRT2,Math.hypot(w,h)/Math.SQRT2/2),stops});}
 return new Gradient({type:'linear',from:[percent(g.x1,w,0)+bbox.x,percent(g.y1,h,0)+bbox.y],to:[percent(g.x2,w,0)+bbox.x,percent(g.y2,h,h)+bbox.y],stops});
}
function withAlpha(color,alpha){if(/^#[0-9a-f]{6}$/i.test(color))return color+Math.round(alpha*255).toString(16).padStart(2,'0');return color;}
function construct(layer,parent,entries,ancestor=null){
 if(!['group','rect','circle','text','path','image'].includes(layer.type))throw new Error('Unsupported native Motion Canvas layer type: '+layer.type);
 const wrap=new Node({composite:true});parent.add(wrap);const effect=new LocalSpaceBlurNode();const shadowNode=layer.shadow?new Node({}):null;if(shadowNode){wrap.add(shadowNode);shadowNode.add(effect);}else wrap.add(effect);const content=new Node({});effect.add(content);let target=content,shape,underline;
 if(layer.clip){const c=layer.clip,cx=(c.x??0)+c.width/2,cy=(c.y??0)+c.height/2,mask=new Rect({position:[cx,cy],width:c.width,height:c.height,radius:c.radius??0,fill:null,clip:true});content.add(mask);target=new Node({position:[-cx,-cy]});mask.add(target);}
 const base={offset:[-1,-1],fill:String(layer.fill??'').startsWith('url(')?'#000000':colorValue(layer.fill??'#000000'),stroke:colorValue(layer.stroke),lineWidth:layer.strokeWidth??0};
 if(layer.type==='rect')shape=new Rect({...base,width:layer.width??0,height:layer.height??0,radius:layer.radius??0});
 if(layer.type==='circle')shape=new Circle({...base,width:layer.width??(layer.radius??0)*2,height:layer.height??layer.width??(layer.radius??0)*2});
 if(layer.type==='text'){shape=new Txt({...base,offset:[({start:-1,middle:0,end:1})[layer.textAnchor??'start'],-1],text:layer.text??'',fontFamily:layer.fontFamily??'Arial, sans-serif',fontSize:layer.fontSize??32,fontWeight:layer.fontWeight??400,lineHeight:layer.lineHeight??(layer.fontSize??32)*1.2,letterSpacing:layer.letterSpacing??0,textAlign:({start:'left',middle:'center',end:'right'})[layer.textAnchor??'start']});if(layer.textDecoration==='underline'){underline=new Rect({offset:[-1,-1],height:Math.max(1,(layer.fontSize??32)/20),fill:layer.fill??'#000000'});target.add(underline);}}
 if(layer.type==='path')shape=new Path({...base,offset:[0,0],data:layer.d??''});
 if(layer.type==='image')shape=new Img({offset:[-1,-1],src:layer.src,width:layer.width,height:layer.height});
 if(shape)target.add(shape);const entry={layer,wrap,effect,shadowNode,content,shape,underline,ancestor,active:false,last:null};entries.push(entry);
 for(const child of layer.children??[])construct(child,target,entries,entry);
}
function apply(entry,t){
 const {layer,wrap,effect,shadowNode,content,shape,underline,ancestor}=entry;
 if(ancestor&&!ancestor.active){const dirty=entry.active;if(dirty)wrap.opacity(0);entry.active=false;return dirty;}
 const s=stateAt(layer,t),last=entry.last??{},visible=t>=(s.start??0)&&t<(s.end??scene.duration)&&s.opacity>0;
 if(!visible){const dirty=entry.active;if(dirty||!entry.last)wrap.opacity(0);entry.active=false;return dirty;}
 const first=!entry.active||!entry.last;entry.active=true;const dirty=first||['x','y','rotation','scaleX','scaleY','originX','originY','opacity','blur','width','height','text','d','fill','stroke','strokeWidth','fontSize','fontWeight','lineHeight','letterSpacing','radius'].some(k=>s[k]!==last[k]);
 if(first||s.x!==last.x||s.y!==last.y||s.originX!==last.originX||s.originY!==last.originY)wrap.position([s.x+s.originX,s.y+s.originY]);
 if(first||s.rotation!==last.rotation)wrap.rotation(s.rotation);
 if(first||s.scaleX!==last.scaleX||s.scaleY!==last.scaleY)wrap.scale([s.scaleX,s.scaleY]);
 if(first||s.originX!==last.originX||s.originY!==last.originY)content.position([-s.originX,-s.originY]);
 if(first||s.opacity!==last.opacity)wrap.opacity(s.opacity);
 const world=wrap.localToWorld(),sx=Math.hypot(world.a,world.b),sy=Math.hypot(world.c,world.d),anisotropic=Math.abs(sx-sy)>1e-6*Math.max(sx,sy)||Math.abs(world.a*world.c+world.b*world.d)>1e-6*sx*sy;const local=!!s.blur&&anisotropic,combined=!!(local&&s.shadow&&s.opacity<1);const blurDirty=effect.setAmount(local?s.blur:0),shadowDirty=effect.setShadow(combined?s.shadow:null),effectDirty=blurDirty||shadowDirty;if(first||s.blur!==last.blur||entry.localBlur!==local)wrap.filters(s.blur&&!local?[blur(s.blur)]:[]);entry.localBlur=local;
 // Canvas globalAlpha is applied separately to shadow and ink. At partial
 // opacity that exposes a shadow through an otherwise opaque component. Keep
 // its native shadow on an inner opacity1 node, then fade the complete result.
 if(s.shadow&&(first||s.shadow!==last.shadow||s.opacity!==last.opacity||entry.combinedShadow!==combined)){
  if(combined){wrap.shadowColor('#00000000');shadowNode.shadowColor('#00000000');}
  else{const separate=s.opacity<1,target=separate?shadowNode:wrap,clear=separate?wrap:shadowNode;clear?.shadowColor('#00000000');target.shadowColor(s.shadow.color??'#000000');target.shadowBlur((s.shadow.blur??0)*2);target.shadowOffset([s.shadow.x??0,s.shadow.y??0]);}
 }entry.combinedShadow=combined;
 if(shape){
  if(layer.type==='path'&&(first||s.d!==last.d))shape.data(s.d??'');
  if('width' in shape&&s.width!==undefined&&(first||s.width!==last.width))shape.width(s.width);
  if('height' in shape&&s.height!==undefined&&(first||s.height!==last.height))shape.height(s.height);
  if(layer.type==='text'){
   if(first||s.text!==last.text)shape.text(s.text??'');
   if(first||s.fontSize!==last.fontSize)shape.fontSize(s.fontSize??32);
   if(first||s.letterSpacing!==last.letterSpacing)shape.letterSpacing(s.letterSpacing??0);
  }
  if('stroke' in shape&&(first||s.stroke!==last.stroke))shape.stroke(colorValue(s.stroke));
  if('lineWidth' in shape&&(first||s.strokeWidth!==last.strokeWidth))shape.lineWidth(s.strokeWidth??0);
  if('radius' in shape&&layer.type==='rect'&&(first||s.radius!==last.radius))shape.radius(s.radius??0);
  if(layer.type==='text'){if(first||s.fontWeight!==last.fontWeight)shape.fontWeight(s.fontWeight??400);if(first||s.lineHeight!==last.lineHeight)shape.lineHeight(s.lineHeight??(s.fontSize??32)*1.2);}
  if(layer.type==='image'){if(first)shape.fill(null);}else if('fill' in shape&&(first||s.fill!==last.fill||s.width!==last.width||s.height!==last.height||s.text!==last.text||s.d!==last.d))shape.fill(fillFor(s.fill,shape));
  if(underline&&(first||s.text!==last.text||s.fontSize!==last.fontSize)){const width=shape.width(),anchor=s.textAnchor??'start';underline.position([anchor==='middle'?-width/2:anchor==='end'?-width:0,(s.fontSize??32)*.95]);underline.width(width);}
 }
 entry.last=s;return dirty||effectDirty;
}
export async function setup(input){
 scene=input;logs=[];initialized=false;lastPng=null;liveEntries=[];document.head.insertAdjacentHTML('beforeend',`<style>${fontCss(scene)}</style>`);for(const f of scene.fonts??[])await document.fonts.load(`${f.weight??400} 32px '${f.family.replaceAll("'",'')}'`);await document.fonts.ready;
 const description=makeScene2D(function*(view){const entries=[];liveEntries=entries;const root=new Node({position:[-scene.width/2,-scene.height/2]});view.add(root);for(const layer of scene.layers)construct(layer,root,entries);yield root;for(let frame=0;frame<=Math.ceil(scene.duration*scene.fps);frame++){for(const e of entries)apply(e,frame/scene.fps);yield;}});
 description.name='MeasuredMotionCanvas';description.onReplaced=new ValueDispatcher(description);const logger=new Logger();logger.onLogged.subscribe(log=>logs.push({level:log.level,message:log.message,stack:log.stack,remarks:log.remarks}));renderer=new Renderer({name:'measured',scenes:[description],logger,variables:{},plugins:[],experimentalFeatures:false});
 settings={name:'measured',range:[0,scene.duration],size:new Vector2(scene.width,scene.height),resolutionScale:1,colorSpace:'srgb',background:scene.background??'#ffffff',fps:scene.fps,exporter:{name:'image',options:{}}};
}
export async function frame(frame){if(!initialized){await renderer.renderFrame(settings,0);initialized=true;}const current=renderer.playback.currentScene;let dirty=false;current.execute(()=>{for(const e of liveEntries)dirty=apply(e,frame/scene.fps)||dirty;});if(dirty||!lastPng){await renderer.stage.render(current,null);lastPng=renderer.stage.finalBuffer.toDataURL('image/png');}if(logs.some(x=>x.level==='error'))throw new Error(JSON.stringify(logs));return lastPng;}
export function diagnostics(){return logs;}
