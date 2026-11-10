import {gsap} from 'gsap';
import {svgMarkup,easeValue,defaults,fontCss} from './common.mjs';
let scene,method,timeline,states,lastMarkup;
const flatten=layers=>layers.flatMap(l=>[l,...flatten(l.children??[])]);
export function setup(input,engine){scene=input;method=engine;states={};lastMarkup=undefined;
 if(method==='gsap'){
  timeline=gsap.timeline({paused:true});
  for(const layer of flatten(scene.layers)){
   const target=states[layer.id]={...defaults,...layer};
   for(const [prop,keysRaw] of Object.entries(layer.keyframes??{})){
    const keys=[...keysRaw].sort((a,b)=>a.t-b.t);target[prop]=keys[0].value;
    for(let i=1;i<keys.length;i++){const a=keys[i-1],b=keys[i];if(b.ease==='hold')timeline.set(target,{[prop]:b.value},b.t);else timeline.to(target,{[prop]:b.value,duration:b.t-a.t,ease:p=>easeValue(p,b.ease),immediateRender:false},a.t);}
   }
  }
  // Keep scene-length tail so seek doesn't clamp at the last animated key.
  timeline.to({x:0},{x:1,duration:scene.duration,ease:'none'},0);
 }
 document.head.insertAdjacentHTML('beforeend',`<style>${fontCss(scene)}</style>`);
 seek(0);
}
export function seek(t){if(method==='gsap')timeline.seek(t,false);const markup=svgMarkup(scene,t,method==='gsap'?states:undefined,false);const changed=markup!==lastMarkup;if(changed){document.getElementById('stage').innerHTML=markup;lastMarkup=markup;}return changed;}
