import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {stateAt} from '../../skill/imessage-motion-recreation/scripts/engines/common.mjs';

const root=path.dirname(fileURLToPath(import.meta.url));
const read=name=>JSON.parse(fs.readFileSync(path.join(root,name)));
const scene=read('scene.json');
const flatten=layers=>layers.flatMap(l=>[l,...flatten(l.children??[])]);
const all=flatten(scene.layers),layers=new Map(all.map(l=>[l.id,l]));
assert.equal(all.length,layers.size);
const state=(id,frame)=>stateAt(layers.get(id),frame/scene.fps);
const ledger=Object.values(read('events.json').events).flat();
const typed=ledger.filter(e=>e.action==='type char'),deleted=ledger.filter(e=>e.action==='backspace');
assert.equal(typed.map(e=>e.char).join(''),'are you home yet?');
assert.equal(typed.length,17);
assert.equal(deleted.length,17);
assert(new Set(typed.slice(1).map((e,i)=>e.frame-typed[i].frame)).size>3);
assert.equal(state('draftSam',560).text,'are you home yet?');
assert.equal(state('draftSam',580).text,'are you home yet?');
assert.equal(state('draftSam',607).text,'are you home yet?');
assert.equal(state('draftSam',661).text,'');
for(const [id,frame] of [['bubbleHeartSam',690],['bubbleHeart',735]])assert(state(id,frame).y+116<=846);
for(const id of ['cardMaya','cardSam']){
  assert.equal(state(id+'-mode',579).text,'When I Arrive');
  assert.equal(state(id+'-mode',580).text,'Arrived');
}
for(const frame of [204,300,580,839]){
  assert.equal(state('cardMaya',frame).x+state('cardMaya-surface',frame).width,484);
  assert.equal(state('cardSam',frame).x,32);
}
assert.equal(all.filter(l=>l.id==='cardMaya').length,1);
for(let frame=0;frame<scene.duration*scene.fps;frame++){
  const camera=state('camera',frame);
  if(frame>=210&&frame<=419)assert(camera.scaleY*944>=scene.height*.45);
  for(const id of ['phoneMaya','phoneSam']){
    const phone=state(id,frame);
    if(phone.opacity<=0)continue;
    const left=camera.x+camera.scaleX*(phone.x-14);
    const right=left+540*camera.scaleX;
    assert(left>=0&&right<=scene.width,`Cropped shell at ${frame}: ${id}`);
  }
}
assert(ledger.every(e=>Number.isInteger(e.frame)&&e.frame>=0&&e.frame<840));
for(const layer of all)for(const keys of Object.values(layer.keyframes??{}))assert(keys.every((k,i)=>Number.isFinite(k.t)&&(!i||k.t>=keys[i-1].t)));
const v1=read('renders/v1-first-export.mp4.render.json');
assert.equal(createHash('sha256').update(fs.readFileSync(path.join(root,'scene.v1.json'))).digest('hex'),v1.sceneSHA256);
assert.equal(createHash('sha256').update(fs.readFileSync(path.join(root,'renders/v1-first-export.mp4'))).digest('hex'),'47a3cd6678980f33788726fd5784d23d20317ce8df7b75c0a28a7f0642e49c81');
console.log('PASS: 17 uneven typed characters, arrival-with-draft hold, 17 backspaces to empty, correct card sides, one outgoing actor, sorted tracks and scene-derived events.');
console.log('PASS: no horizontal phone-shell clipping at any of 840 frames; walk phone height >=45%; v1 movie and scene hashes preserved.');
