import fs from'node:fs';import path from'node:path';import{fileURLToPath}from'node:url';import{loadScene}from'../../../engines/scene-loader.mjs';import{sceneForFrames}from'../../../engines/runtime-scene.mjs';import{svgMarkup,layerMarkup}from'../../../engines/common.mjs';
const D=path.dirname(fileURLToPath(import.meta.url)),ROOT=path.resolve(D,'../../..');
const specFile=process.argv[2]??path.join(D,'reasoning-neutral-candidate.json'),out=process.argv[3]??path.join(D,'reasoning-neutral-probe.scene.json');
const frames=(process.argv[4]??'271,272,275,280,293,300,320,350,360,361,363,364,367,370,374,375').split(',').map(Number);
const scene=loadScene(path.join(ROOT,'outputs/02-danieltian/final-v16/scene.json')),spec=JSON.parse(fs.readFileSync(specFile)),replacement=structuredClone(spec.replacement);
if(process.argv[5]==='--house'){const house=JSON.parse(fs.readFileSync(path.join(D,'house-preview-element.json')));const find=n=>n.id==='early-reason-emoji-full-3-0'?n:(n.children??[]).map(find).find(Boolean);const oldHouse=find(replacement);oldHouse.start=291/30;oldHouse.end=292/30;replacement.children.push(house);}
const embed=n=>{if(n.src&&!n.src.startsWith('data:'))n.src='data:image/png;base64,'+fs.readFileSync(n.src).toString('base64');for(const child of n.children??[])embed(child)};embed(replacement);
const index=scene.layers.findIndex(n=>n.id===spec.id);if(index<0)throw Error('Missing reason root');const original=scene.layers[index];scene.layers[index]=replacement;
const changed=[];for(let f=0;f<1360;f++)if(layerMarkup(original,f/30,scene.duration)!==layerMarkup(replacement,f/30,scene.duration))changed.push(f);
if(changed.some(f=>f<272||f>374))throw Error('Outside reasoning scope changed');
const probe=sceneForFrames(scene,frames);for(const f of frames)if(svgMarkup(scene,f/30,undefined,false)!==svgMarkup(probe,f/30,undefined,false))throw Error('Prune mismatch');
fs.writeFileSync(out,JSON.stringify(probe));fs.writeFileSync(out+'.scope.json',JSON.stringify({frames:1360,changedFrames:changed,unchangedFrames:1360-changed.length,probeFrames:frames,pruningExact:true},null,2));console.log(JSON.stringify({out,changed:changed.length,bytes:fs.statSync(out).size}));
