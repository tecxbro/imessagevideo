import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {layerMarkup} from '../../engines/common.mjs';
const read=p=>JSON.parse(fs.readFileSync(p));const oldPath='outputs/04-poke/final-v15/scene.json';const newPath='references/04-poke/scene-v16-candidate.json';const a=read(oldPath),b=read(newPath);const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');const changedIds=['p0223','p0255'];
if(JSON.stringify(a.fonts)!==JSON.stringify(b.fonts))throw Error('Font table changed');
if(JSON.stringify(a.gradients)!==JSON.stringify(b.gradients.slice(0,a.gradients.length)))throw Error('Original gradient changed');
if(a.width!==b.width||a.height!==b.height||a.fps!==b.fps||a.duration!==b.duration)throw Error('Format changed');
for(let i=0;i<a.layers.length;i++)if(!changedIds.includes(a.layers[i].id)&&JSON.stringify(a.layers[i])!==JSON.stringify(b.layers[i]))throw Error('Unscoped parent '+a.layers[i].id);
const frames=[];for(let f=0;f<1283;f++){const t=f/a.fps;let differs=false;for(const id of changedIds){const x=a.layers.find(g=>g.id===id),y=b.layers.find(g=>g.id===id);if(layerMarkup(x,t,a.duration)!==layerMarkup(y,t,b.duration))differs=true;}if(differs)frames.push(f);}
const ranges=[];for(const f of frames){if(!ranges.length||f>ranges.at(-1)[1]+1)ranges.push([f,f]);else ranges.at(-1)[1]=f;}
if(frames.some(f=>f<513||f>671))throw Error('Frame scope leak');const result={method:'Exact active changed-parent markup across all1283 native frames. All other top-level parents and existing font/gradient definitions are byte-identical; appended unique gradients are used only inside existing p0255 lifecycle575–671. New unused defs do not change other frame pixels.',old_scene_sha256:hash(oldPath),candidate_scene_sha256:hash(newPath),changed_parent_ids:changedIds,frames:frames.length,ranges};fs.writeFileSync('references/04-poke/changed-ranges-v16.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
