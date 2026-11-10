import path from 'node:path';import fs from 'node:fs';import crypto from 'node:crypto';
import {loadScene} from '../../engines/scene-loader.mjs';import {svgMarkup} from '../../engines/common.mjs';
const dir=path.resolve('references/03-photon-mini');const a=loadScene(path.join(dir,'final-v12.scene.json'));const b=loadScene(path.join(dir,'final-v13.scene.json'));const ranges=[[0,413],[436,494],[618,890],[901,974]];const changed=[],outside=[];
// A dormant global gradient definition cannot change a pixel. Preserve active
// clip/filter definitions, remove only unused linear/radial gradient definitions.
function canonical(markup){const body=markup.replace(/<(linearGradient|radialGradient)\b[\s\S]*?<\/\1>/g,'');const refs=new Set([...body.matchAll(/url\(#([^)]*)\)/g)].map(x=>x[1]));return markup.replace(/<(linearGradient|radialGradient)\b[^>]*id="([^"]+)"[\s\S]*?<\/\1>/g,(all,type,id)=>refs.has(id)?all:'');}
for(let f=0;f<1260;f++){const aa=canonical(svgMarkup(a,f/30,undefined,false));const bb=canonical(svgMarkup(b,f/30,undefined,false));if(aa!==bb){changed.push(f);if(!ranges.some(([lo,hi])=>f>=lo&&f<=hi))outside.push(f);}if(f%300===0)console.log('checked',f);}
let intervals=[];for(const f of changed){const p=intervals.at(-1);if(p&&f===p[1]+1)p[1]=f;else intervals.push([f,f]);}
const result={baseline:'final-v12.scene.json',candidate:'final-v13.scene.json',total_frames:1260,changed_frames:changed.length,observed_intervals:intervals,declared_patch:ranges,outside_declared:outside,normalization:'Unused global linear/radial gradients removed; active clips, filters, geometry, text and image data retained.'};fs.writeFileSync(path.join(dir,'final-v13-scope-verification.json'),JSON.stringify(result,null,2));console.log(result);if(outside.length)process.exit(1);
