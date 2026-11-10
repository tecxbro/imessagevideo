import {makeScene2D,Node,Rect,Circle,Txt,Path,Img} from '@motion-canvas/2d';
import {Renderer,Logger,ValueDispatcher,Vector2} from '@motion-canvas/core';
import {stateAt,fontCss} from './common.mjs';
let renderer,settings,scene,logs=[];
function construct(layer,parent,entries){
 const wrap=new Node({});parent.add(wrap);const content=new Node({});wrap.add(content);let shape;
 const base={offset:[-1,-1],fill:layer.fill??'#000000',stroke:layer.stroke??null,lineWidth:layer.strokeWidth??0};
 if(layer.type==='rect')shape=new Rect({...base,width:layer.width??0,height:layer.height??0,radius:layer.radius??0});
 if(layer.type==='circle')shape=new Circle({...base,width:layer.width??(layer.radius??0)*2,height:layer.height??layer.width??(layer.radius??0)*2});
 if(layer.type==='text')shape=new Txt({...base,text:layer.text??'',fontFamily:layer.fontFamily??'Arial, sans-serif',fontSize:layer.fontSize??32,fontWeight:layer.fontWeight??400,lineHeight:layer.lineHeight??(layer.fontSize??32)*1.2,letterSpacing:layer.letterSpacing??0});
 if(layer.type==='path')shape=new Path({...base,data:layer.d??''});
 if(layer.type==='image')shape=new Img({offset:[-1,-1],src:layer.src,width:layer.width,height:layer.height});
 if(shape)content.add(shape);
 entries.push({layer,wrap,content,shape});
 for(const child of layer.children??[])construct(child,content,entries);
}
function apply(entry,t){const {layer,wrap,content,shape}=entry,s=stateAt(layer,t);wrap.position([s.x+s.originX,s.y+s.originY]);wrap.rotation(s.rotation);wrap.scale([s.scaleX,s.scaleY]);content.position([-s.originX,-s.originY]);wrap.opacity(t<(s.start??0)||t>=(s.end??scene.duration)?0:s.opacity);if(shape){if('fill' in shape)shape.fill(s.fill??'#000000');if('width' in shape&&s.width!==undefined)shape.width(s.width);if('height' in shape&&s.height!==undefined)shape.height(s.height);if(layer.type==='text')shape.text(s.text??'');}}
export async function setup(input){
 scene=input;logs=[];document.head.insertAdjacentHTML('beforeend',`<style>${fontCss(scene)}</style>`);await document.fonts.ready;
 const description=makeScene2D(function*(view){const entries=[];const root=new Node({position:[-scene.width/2,-scene.height/2]});view.add(root);for(const layer of scene.layers)construct(layer,root,entries);for(let frame=0;frame<=Math.ceil(scene.duration*scene.fps);frame++){for(const e of entries)apply(e,frame/scene.fps);yield;}});
 description.name='MeasuredMotionCanvas';description.onReplaced=new ValueDispatcher(description);const logger=new Logger();logger.onLogged.subscribe(log=>logs.push({level:log.level,message:log.message,stack:log.stack,remarks:log.remarks}));renderer=new Renderer({name:'measured',scenes:[description],logger,variables:{},plugins:[],experimentalFeatures:false});
 settings={name:'measured',range:[0,scene.duration],size:new Vector2(scene.width,scene.height),resolutionScale:1,colorSpace:'srgb',background:scene.background??'#ffffff',fps:scene.fps,exporter:{name:'image',options:{}}};
}
export async function frame(frame){await renderer.renderFrame(settings,frame/scene.fps);if(logs.some(x=>x.level==='error'))throw new Error(JSON.stringify(logs));return renderer.stage.finalBuffer.toDataURL('image/png');}
export function diagnostics(){return logs;}
