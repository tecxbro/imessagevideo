import fs from 'node:fs';
import {loadScene} from '../../engines/scene-loader.mjs';
import {svgMarkup,fontCss} from '../../engines/common.mjs';
const base=loadScene('outputs/03-photon-mini/final-v14/scene.json'),target=loadScene('references/03-photon-mini/collage-v15-measure/combined-prototype.scene.json');
const changed=[],outside=[];let total=0;
if(fontCss(base)!==fontCss(target))throw Error('Font CSS changed');
for(let f=0;f<1260;f++){
 const different=svgMarkup(base,f/30,undefined,false)!==svgMarkup(target,f/30,undefined,false);if(different){changed.push(f);if(f<903||f>974)outside.push(f);}total++;
 if(f%150===0)console.log(JSON.stringify({checked:f,changed:changed.length,outside:outside.length}));
}
let ranges=[];for(const f of changed){if(ranges.length&&ranges.at(-1)[1]===f-1)ranges.at(-1)[1]=f;else ranges.push([f,f]);}
const ids=new Set(),duplicates=[];function walk(n){if(ids.has(n.id))duplicates.push(n.id);ids.add(n.id);for(const c of n.children??[])walk(c);}target.layers.forEach(walk);
const report={base:'outputs/03-photon-mini/final-v14/scene.json',target:'collage-v15-measure/combined-prototype.scene.json',checkedFrames:total,changedFrames:changed.length,exactChangedRanges:ranges,outsideFrames:outside,duplicateIds:duplicates,fontCssIdentical:true,definition:'All1260 resolved SVG states with embedded actual asset bytes, including complete referenced definitions. Full fonts are compared separately.'};
fs.writeFileSync('references/03-photon-mini/collage-v15-measure/scope-proof.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(outside.length||duplicates.length)process.exit(1);
