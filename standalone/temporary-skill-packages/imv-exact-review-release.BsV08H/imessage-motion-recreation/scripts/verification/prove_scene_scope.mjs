/** Verify that a scoped refinement changes no evaluated native frame outside its ranges. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {parseArgs} from 'node:util';
import {loadScene} from '../engines/scene-loader.mjs';
import {svgMarkup} from '../engines/common.mjs';
const {values:v}=parseArgs({options:{input:{type:'string'},candidate:{type:'string'},ranges:{type:'string'},out:{type:'string'}}});
for(const k of ['input','candidate','ranges','out'])if(!v[k])throw Error('Required --'+k);
const ranges=v.ranges.split(',').map(s=>s.split(':').map(Number));
const a=loadScene(v.input),b=loadScene(v.candidate);if(a.fps!==b.fps||a.duration!==b.duration)throw Error('Cadence/duration changed');
const count=a.frameCount??Math.round(a.duration*a.fps),changed=[],failures=[];let checked=0;
for(let f=0;f<count;f++){
 const permitted=ranges.some(([lo,hi])=>f>=lo&&f<=hi);if(!permitted)checked++;
 const diff=svgMarkup(a,f/a.fps,undefined,false)!==svgMarkup(b,f/a.fps,undefined,false);
 if(diff){changed.push(f);if(!permitted)failures.push(f);}
}
const intervals=[];for(const f of changed){if(!intervals.length||f>intervals.at(-1)[1]+1)intervals.push([f,f]);else intervals.at(-1)[1]=f;}
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const result={input:v.input,inputSHA256:hash(v.input),candidate:v.candidate,candidateSHA256:hash(v.candidate),frameCount:count,declaredRanges:ranges,outsideFramesChecked:checked,allOutsideMarkupIdentical:failures.length===0,failedFrames:failures,exactMarkupChangedRanges:intervals};fs.writeFileSync(v.out,JSON.stringify(result,null,2));console.log(JSON.stringify(result));if(failures.length)process.exitCode=1;
