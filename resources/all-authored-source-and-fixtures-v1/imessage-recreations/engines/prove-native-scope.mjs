/** Compare actual resolved visual states, excluding only unreferenced gradients. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {loadScene} from './scene-loader.mjs';
import {layerMarkup,gradientDefs,fontCss} from './common.mjs';
const [basePath,targetPath,outputPath,rangeText]=process.argv.slice(2);if(!outputPath)throw Error('Usage: node prove-native-scope.mjs base.json target.json proof.json [first:last,...]');
const a=loadScene(basePath),b=loadScene(targetPath),frames=Math.round(a.duration*a.fps);if(a.width!==b.width||a.height!==b.height||a.fps!==b.fps||frames!==Math.round(b.duration*b.fps))throw Error('Incompatible scene cadence/dimensions');
const ranges=rangeText?.split(',').map(x=>x.split(':').map(Number)),allowed=f=>!ranges||ranges.some(([x,y])=>f>=x&&f<=y);const fontsEqual=fontCss(a)===fontCss(b);const changed=[],outside=[];
function visual(s,t){const body=s.layers.map(l=>layerMarkup(l,t,s.duration)).join(''),ids=new Set([...body.matchAll(/url\(#([^\)]+)\)/g)].map(m=>m[1]));return JSON.stringify([s.background,body,gradientDefs({...s,gradients:(s.gradients??[]).filter(g=>ids.has(g.id))})]);}
for(let f=0;f<frames;f++){if(!fontsEqual||visual(a,f/a.fps)!==visual(b,f/b.fps)){changed.push(f);if(!allowed(f))outside.push(f);}if(f%150===0)console.log(JSON.stringify({checked:f,changed:changed.length,outside:outside.length}));}
let exact=[];for(const f of changed){if(exact.length&&exact.at(-1)[1]===f-1)exact.at(-1)[1]=f;else exact.push([f,f]);}
const sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex'),report={base:basePath,target:targetPath,baseSha256:sha(basePath),targetSha256:sha(targetPath),checkedFrames:frames,changedFrames:changed.length,exactChangedRanges:exact,conservativeCaptureRanges:ranges??exact,changedOutsideCaptureUnion:outside,fontCssIdentical:fontsEqual,definition:'Embedded active layer markup plus referenced gradient definitions, background and font CSS. Unused gradients cannot change inactive pixels.'};fs.writeFileSync(outputPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(outside.length)process.exit(1);
