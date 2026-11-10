import fs from 'node:fs';
import {sceneForFrames} from '../../../engines/runtime-scene.mjs';
import {stateAt} from '../../../engines/common.mjs';
const s=JSON.parse(fs.readFileSync('outputs/03-photon-mini/final-v17/scene.json'));
const rows=[];
for(const [a,b] of [[823,832],[833,842]]){
 const frames=Array.from({length:b-a+1},(_,i)=>a+i),scene=sceneForFrames(s,frames);let total=0,zeroAtAllTimes=0;const types={};
 function walk(ls){for(const n of ls){total++;types[n.type]=(types[n.type]??0)+1;if(frames.every(f=>stateAt(n,f/s.fps).opacity<=0))zeroAtAllTimes++;walk(n.children??[]);}}
 walk(scene.layers);rows.push({a,b,authoredNodes:total,estimatedNativeNodes:'at least '+total*3,types,zeroAtAllSelectedTimes:zeroAtAllTimes});
}
fs.writeFileSync('outputs/alternative-methods/03-v17-runtime-diagnosis/node-cost.json',JSON.stringify(rows,null,2)+'\n');console.log(JSON.stringify(rows));
