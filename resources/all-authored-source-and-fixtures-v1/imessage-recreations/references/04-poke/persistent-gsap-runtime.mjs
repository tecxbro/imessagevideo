// Bounded local performance experiment. Same measured scene and actual GSAP tracks.
import {gsap} from '../../engines/node_modules/gsap/index.js';
import {svgMarkup,easeValue,defaults,fontCss,stateAt} from '../../engines/common.mjs';
let scene,timeline,states,rows;
const flatten=layers=>layers.flatMap(l=>[l,...flatten(l.children??[])]);
const unclipped=l=>({...l,start:-1e9,end:1e9,opacity:1,keyframes:Object.fromEntries(Object.entries(l.keyframes??{}).filter(([k])=>k!=='opacity')),children:l.children?.map(unclipped)});
export function setup(input){
 scene=input;states={};timeline=gsap.timeline({paused:true});
 const all=flatten(scene.layers);
 for(const layer of all){
  const target=states[layer.id]={...defaults,...layer};
  for(const [prop,keysRaw] of Object.entries(layer.keyframes??{})){
   const keys=[...keysRaw].sort((a,b)=>a.t-b.t);target[prop]=keys[0].value;
   for(let i=1;i<keys.length;i++){const a=keys[i-1],b=keys[i];if(b.ease==='hold')timeline.set(target,{[prop]:b.value},b.t);else timeline.to(target,{[prop]:b.value,duration:b.t-a.t,ease:p=>easeValue(p,b.ease),immediateRender:false},a.t);}
  }
 }
 timeline.to({x:0},{x:1,duration:scene.duration,ease:'none'},0);
 document.head.insertAdjacentHTML('beforeend',`<style>${fontCss(scene)}</style>`);
 document.getElementById('stage').innerHTML=svgMarkup({...scene,layers:scene.layers.map(unclipped)},0,undefined,false);
 const byId=new Map([...document.querySelectorAll('[data-layer]')].map(el=>[el.getAttribute('data-layer'),el]));
 rows=all.map(l=>({layer:l,element:byId.get(l.id),animated:Object.keys(l.keyframes??{})}));
 seek(0);
}
export function seek(t){
 timeline.seek(t,false);
 for(const {layer,element,animated} of rows){
  const s=stateAt(layer,t,states);
  element.style.display=(t<(s.start??0)||t>=(s.end??scene.duration)||s.opacity<=0)?'none':'';
  element.setAttribute('opacity',s.opacity);
  if(!animated.length)continue;
  element.setAttribute('transform',`translate(${s.x} ${s.y}) translate(${s.originX} ${s.originY}) rotate(${s.rotation}) scale(${s.scaleX} ${s.scaleY}) translate(${-s.originX} ${-s.originY})`);
  element.setAttribute('opacity',s.opacity);
  const shape=element.firstElementChild;
  for(const prop of animated){
   const attr={width:'width',height:'height',radius:'rx',fontSize:'font-size',fontWeight:'font-weight',fill:'fill',stroke:'stroke',strokeWidth:'stroke-width',letterSpacing:'letter-spacing'}[prop];
   if(attr&&shape)shape.setAttribute(attr,s[prop]);
  }
 }
}
