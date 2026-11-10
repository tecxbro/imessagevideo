import fs from 'node:fs';
import {loadScene} from '../../../engines/scene-loader.mjs';
import {stateAt} from '../../../engines/common.mjs';
import {runtimeChunks,sceneForFrames} from '../../../engines/runtime-scene.mjs';
const scene=loadScene('outputs/03-photon-mini/final-v17/scene.json');
const frames=[[211,309],[335,344],[497,516],[541,617],[735,799],[813,849],[1185,1198]].flatMap(([a,b])=>Array.from({length:b-a+1},(_,i)=>a+i));
const chunks=runtimeChunks(scene,frames,8*1024*1024);
const rows=[];
for(const f of [831,832,833,834,835,840]){
 const all=[];
 function walk(ls,t,ancestors=[]){for(const n of ls){const s=stateAt(n,t);if(t<(s.start??0)||t>=(s.end??scene.duration)||s.opacity===0)continue;
  if(s.type==='path')all.push({id:s.id,bytes:s.d?.length??0,commands:(s.d?.match(/[a-zA-Z]/g)??[]).length,transform:{x:s.x,y:s.y,scale:s.scale,scaleX:s.scaleX,scaleY:s.scaleY,rotation:s.rotation},blur:s.blur,ancestors});
  walk(n.children??[],t,[...ancestors,{id:n.id,scale:s.scale,scaleX:s.scaleX,scaleY:s.scaleY,blur:s.blur,rotation:s.rotation}]);
 }}
 walk(scene.layers,f/scene.fps);
 const c=chunks.find(c=>c.frames.includes(f));rows.push({frame:f,chunk:{first:c.frames[0],last:c.frames.at(-1),frames:c.frames.length,bytes:c.bytes},paths:all.length,pathBytes:all.reduce((s,n)=>s+n.bytes,0),largest:all.sort((a,b)=>b.bytes-a.bytes).slice(0,5)});
}
const report={fullSceneBytes:Buffer.byteLength(JSON.stringify(scene)),chunks:chunks.length,rows};fs.writeFileSync('outputs/alternative-methods/03-v17-runtime-diagnosis/scene-complexity.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
