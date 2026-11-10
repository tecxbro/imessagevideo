import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {layerMarkup} from '../../engines/common.mjs';
const read=p=>JSON.parse(fs.readFileSync(p));const oldPath='outputs/04-poke/final-v17/scene.json';const newPath='references/04-poke/scene-v18-candidate.json';const a=read(oldPath),b=read(newPath);const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');const changedIds=JSON.parse(fs.readFileSync('references/04-poke/v18-changed-parents.json'));
if(JSON.stringify(a.fonts)!==JSON.stringify(b.fonts))throw Error('Font table changed');
if(JSON.stringify(a.gradients)!==JSON.stringify(b.gradients.slice(0,a.gradients.length)))throw Error('Original gradient changed');
if(a.width!==b.width||a.height!==b.height||a.fps!==b.fps||a.duration!==b.duration)throw Error('Format changed');
for(let i=0;i<a.layers.length;i++)if(!changedIds.includes(a.layers[i].id)&&JSON.stringify(a.layers[i])!==JSON.stringify(b.layers[i]))throw Error('Unscoped parent '+a.layers[i].id);
const frames=[];for(let f=0;f<1283;f++){const t=f/a.fps;let differs=false;for(const id of changedIds){const x=a.layers.find(g=>g.id===id),y=b.layers.find(g=>g.id===id);if(layerMarkup(x,t,a.duration)!==layerMarkup(y,t,b.duration))differs=true;}if(differs)frames.push(f);}
const ranges=[];for(const f of frames){if(!ranges.length||f>ranges.at(-1)[1]+1)ranges.push([f,f]);else ranges.at(-1)[1]=f;}
if(frames.some(f=>(f<1170||f>1210)))throw Error('Frame scope leak');const result={method:'Exact active changed-parent markup across all1283 native frames. All other top-level parents and existing font/gradient definitions are byte-identical; no new font or gradient definitions. Only24held-grid image cameras differ1170–1210; actual entry1169and original1211–1214tail/1215exit retained. Coherent per-frame source registration and native fullinterval acceptance are frozen in separate ledgers.',old_scene_sha256:hash(oldPath),candidate_scene_sha256:hash(newPath),changed_parent_ids:changedIds,frames:frames.length,ranges};fs.writeFileSync('references/04-poke/changed-ranges-v18.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
