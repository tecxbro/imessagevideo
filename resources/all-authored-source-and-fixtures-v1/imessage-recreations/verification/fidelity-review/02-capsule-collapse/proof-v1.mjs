import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {loadScene} from '../../../engines/scene-loader.mjs';
import {svgMarkup} from '../../../engines/common.mjs';
const root='/workspace/imessage-recreations';
const input=root+'/outputs/02-danieltian/final-v12/scene.json';
const output=root+'/references/02-danieltian/scene-capsule-collapse-review.json';
const a=loadScene(input),b=loadScene(output),changed=[],outside=[];
for(let frame=0;frame<1360;frame++){
    if(svgMarkup(a,frame/30,undefined,false)!==svgMarkup(b,frame/30,undefined,false)){
        changed.push(frame);
        if(frame<526||frame>550)outside.push(frame);
    }
}
const ranges=[];
for(const frame of changed){if(!ranges.length||frame>ranges.at(-1)[1]+1)ranges.push([frame,frame]);else ranges.at(-1)[1]=frame;}
const result={input,inputSHA256:createHash('sha256').update(fs.readFileSync(input)).digest('hex'),output,outputSHA256:createHash('sha256').update(fs.readFileSync(output)).digest('hex'),frames:1360,declaredRanges:[[526,550]],outsideFramesChecked:1335,allOutsideMarkupIdentical:outside.length===0,outsideFailures:outside,exactChangedRanges:ranges,changedCount:changed.length};
fs.writeFileSync(root+'/verification/fidelity-review/02-capsule-collapse/all-frame-scope-proof-v1.json',JSON.stringify(result,null,2));console.log(result);
