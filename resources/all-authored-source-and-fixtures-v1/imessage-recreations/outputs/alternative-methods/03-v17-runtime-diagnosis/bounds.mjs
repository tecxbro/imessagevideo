import fs from 'node:fs';
import {stateAt} from '../../../engines/common.mjs';
const scene=JSON.parse(fs.readFileSync('outputs/03-photon-mini/final-v17/scene.json'));
const rows=[];
for(const frame of [832,833,834]){
 const nodes=[];
 function walk(ls,ancestors=[]){for(const n of ls){const s=stateAt(n,frame/scene.fps);if(frame/scene.fps<(s.start??0)||frame/scene.fps>=(s.end??scene.duration)||s.opacity===0)continue;
 const v={id:s.id,type:s.type,x:s.x,y:s.y,width:s.width,height:s.height,scaleX:s.scaleX,scaleY:s.scaleY,rotation:s.rotation,opacity:s.opacity,blur:s.blur,shadow:s.shadow,clip:s.clip,ancestors};if(s.type==='path'){const ns=(s.d?.match(/[-+]?(?:\d*\.)?\d+(?:e[-+]?\d+)?/gi)??[]).map(Number);v.maxPathNumber=Math.max(...ns.map(Math.abs));}nodes.push(v);walk(n.children??[],[...ancestors,s.id]);}}
 walk(scene.layers);rows.push({frame,nodes});
}
fs.writeFileSync('outputs/alternative-methods/03-v17-runtime-diagnosis/active-geometry.json',JSON.stringify(rows,null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({frame:r.frame,nodes:r.nodes.length,filters:r.nodes.filter(n=>n.blur||n.shadow),largeGeometry:r.nodes.filter(n=>Math.max(n.width??0,n.height??0,n.maxPathNumber??0)>5000),largeTransforms:r.nodes.filter(n=>Math.max(Math.abs(n.x),Math.abs(n.y),Math.abs(n.scaleX),Math.abs(n.scaleY))>10000)}))));
