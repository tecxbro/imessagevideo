import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {loadScene} from '../engines/scene-loader.mjs';
import {svgMarkup} from '../engines/common.mjs';
const input='outputs/05-linq/final-v11/scene.json',candidate='references/05-linq/scene-merged-v12.json';
const a=loadScene(input),b=loadScene(candidate),ranges=[[340,351],[860,946],[1185,1189],[1191,1194],[1196,1199]],bad=[],changed=[];let outside=0;
const normalize=(s)=>s.replace(/<radialGradient id="v12-ai-victory-emission"[\s\S]*?<\/radialGradient>/g,'');
for(let f=0;f<1458;f++){
 const allowed=ranges.some(([lo,hi])=>f>=lo&&f<=hi);let aa=svgMarkup(a,f/30,undefined,false),bb=svgMarkup(b,f/30,undefined,false);
 if(!allowed){outside++;if(bb.includes('url(#v12-ai-victory-emission)'))bad.push({frame:f,reason:'New gradient unexpectedly active outside scope'});}
 if(normalize(aa)!==normalize(bb)){changed.push(f);if(!allowed)bad.push({frame:f,reason:'Active evaluated markup differs'});}
}
const intervals=[];for(const f of changed){if(!intervals.length||f>intervals.at(-1)[1]+1)intervals.push([f,f]);else intervals.at(-1)[1]=f;}
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const r={input,inputSHA256:hash(input),candidate,candidateSHA256:hash(candidate),declaredRanges:ranges,outsideFramesChecked:outside,allOutsideActiveMarkupIdentical:bad.length===0,normalization:'Only the new unused radialGradient definition is omitted when comparing markup. Its URL is explicitly proved absent from every outside-frame active layer. This does not omit any active shape/filter/asset.',exactActiveMarkupChangedRanges:intervals,failures:bad};fs.writeFileSync('verification/05-merged-v12-outside.json',JSON.stringify(r,null,2));console.log(JSON.stringify(r));if(bad.length)process.exitCode=1;
