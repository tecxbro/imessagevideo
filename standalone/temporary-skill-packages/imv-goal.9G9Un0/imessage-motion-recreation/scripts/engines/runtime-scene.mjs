/** Exact lifecycle pruning for transport; the authored scene/hash stays intact. */
import {stateAt,svgMarkup} from './common.mjs';
export function sceneForTimes(scene,times){
 const walk=(layers,requestedTimes)=>layers.flatMap(layer=>{
  const active=requestedTimes.filter(t=>{const dynamic=layer.keyframes?.start||layer.keyframes?.end;const state=dynamic?stateAt(layer,t):layer;return t>=(state.start??0)&&t<(state.end??scene.duration);});
  if(!active.length)return [];
  // Preserve active empty group wrappers; this keeps evaluated SVG exact too.
  return [{...layer,...(layer.children?{children:walk(layer.children,active)}:{})}];
 });
 return {width:scene.width,height:scene.height,fps:scene.fps,duration:scene.duration,background:scene.background,fonts:scene.fonts,gradients:scene.gradients,layers:walk(scene.layers,times)};
}
export function sceneForFrames(scene,frames){return sceneForTimes(scene,frames.map(frame=>frame/scene.fps));}
export function runtimeChunks(scene,frames,maxBytes=8*1024*1024){
 const split=indices=>{const runtime=sceneForFrames(scene,indices);const bytes=Buffer.byteLength(JSON.stringify(runtime));if(bytes<=maxBytes||indices.length===1)return [{frames:indices,scene:runtime,bytes}];const middle=Math.floor(indices.length/2);return [...split(indices.slice(0,middle)),...split(indices.slice(middle))];};
 return split(frames);
}
export function proveRuntimeChunks(scene,chunks){
 let checked=0;for(const chunk of chunks)for(const frame of chunk.frames){if(svgMarkup(scene,frame/scene.fps,undefined,false)!==svgMarkup(chunk.scene,frame/scene.fps,undefined,false))throw new Error(`Runtime pruning changed frame ${frame}`);checked++;}return checked;
}
