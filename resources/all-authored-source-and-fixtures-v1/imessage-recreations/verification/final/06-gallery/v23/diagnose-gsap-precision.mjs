import fs from 'node:fs';
import {createRequire} from 'node:module';
import {defaults,easeValue,stateAt} from '../../../../engines/common.mjs';
const require=createRequire(import.meta.url);const {gsap}=require('../../../../engines/node_modules/gsap/dist/gsap.js');
const scene=JSON.parse(fs.readFileSync('outputs/06-gallery/final-v23/scene.json','utf8'));
const flatten=ns=>ns.flatMap(n=>[n,...flatten(n.children??[])]);
const nodes=flatten(scene.layers).filter(n=>['rene-final11-group-37','rene-final11-image-107'].includes(n.id));
const states={};const timeline=gsap.timeline({paused:true});
for(const n of nodes){const target=states[n.id]={...defaults,...n};for(const [prop,raw] of Object.entries(n.keyframes??{})){const keys=[...raw].sort((a,b)=>a.t-b.t);target[prop]=keys[0].value;for(let i=1;i<keys.length;i++){const a=keys[i-1],b=keys[i];if(b.ease==='hold')timeline.set(target,{[prop]:b.value},b.t);else timeline.to(target,{[prop]:b.value,duration:b.t-a.t,ease:p=>easeValue(p,b.ease),immediateRender:false},a.t);}}}
timeline.to({x:0},{x:1,duration:scene.duration,ease:'none'},0);timeline.seek(0,false);
const rows=[];
for(const frame of [208,1257,1258,1259,1260,1261,1263,1264]){timeline.seek(frame/30,false);const n=nodes.find(n=>n.id===(frame===208?'rene-final11-group-37':'rene-final11-image-107'));const exact=stateAt(n,frame/30);const gs=states[n.id];const props=Object.fromEntries((frame===208?['opacity']:['x','y','scaleX','scaleY']).map(k=>[k,{exact:exact[k],gsap:gs[k],delta:gs[k]-exact[k]}]));rows.push({frame,id:n.id,properties:props});}
fs.writeFileSync('verification/final/06-gallery/v23/gsap-precision-fixture.json',JSON.stringify({method:'Same numeric tween construction as web-runtime, pure-JS fixture, no source/renderer mutation',rows},null,2));console.log(JSON.stringify(rows));timeline.kill();gsap.ticker.sleep();
