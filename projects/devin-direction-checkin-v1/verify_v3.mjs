import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {stateAt} from '../../skill/imessage-motion-recreation/scripts/engines/common.mjs';
import {flatten, frameMapping, retimeScene, visibleEvents} from './timeline_v3.mjs';

const read=name=>JSON.parse(fs.readFileSync(new URL(name,import.meta.url)));
const scene=read('scene.json'),v2=read('scene.v2.json'),map=read('frame-map.json');
const layers=new Map(flatten(scene.layers).map(l=>[l.id,l]));
const old=new Map(flatten(v2.layers).map(l=>[l.id,l]));
const state=(id,f)=>stateAt(layers.get(id),f/scene.fps);
assert.equal(scene.duration*scene.fps,720);
assert.equal(layers.size,flatten(scene.layers).length);
assert.deepEqual(map.range,{v2:[210,419],v3:[210,299]});
assert.equal(map.v2ToV3[420].v3Frame,300);
assert.equal(map.v2ToV3[839].v3Frame,719);
for(const {v3Frame,v2Frame} of map.v3ToV2){
  for(const [id,layer] of layers){
    if(id==='camera'&&v2Frame<120)continue;
    const a=stateAt(layer,v3Frame/30),b=stateAt(old.get(id),v2Frame/30);
    for(const property of Object.keys(old.get(id).keyframes??{})){
      if(typeof a[property]==='number')assert(Math.abs(a[property]-b[property])<1e-8,`${v3Frame} ${id}.${property}`);
      else if(/^#[0-9a-f]{6}$/i.test(a[property]))assert.equal(a[property].toLowerCase(),b[property].toLowerCase());
      else assert.deepEqual(a[property],b[property]);
    }
  }
  const camera=state('camera',v3Frame);
  for(const id of ['phoneMaya','phoneSam']){
    const phone=state(id,v3Frame);
    if(phone.opacity<=0)continue;
    const left=camera.x+camera.scaleX*(phone.x-14),right=left+540*camera.scaleX;
    assert(left>=0&&right<=scene.width,`Edge sliver: ${id} at ${v3Frame}`);
  }
  if(v3Frame>=210&&v3Frame<=299)assert(camera.scaleY*944>=scene.height*.45);
  for(const id of ['cardMaya','cardSam']){
    const eta=state(id+'-eta',v3Frame).text,clock=state(id==='cardMaya'?'clockMaya':'clockSam',v3Frame).text;
    if(v3Frame<460&&v3Frame>=204){
      const [hour,minute]=clock.split(':').map(Number),remaining=720-(hour*60+minute);
      assert.equal(Number(eta.match(/\d+/)[0]),Math.max(1,remaining));
    }
  }
}
const events=Object.values(read('events.json').events).flat();
assert.deepEqual(events,visibleEvents(scene));
assert.equal(events.length,35);
assert.equal(events.filter(e=>e.action==='arrival').length,1);
assert.equal(events.find(e=>e.action==='arrival').frame,460);
assert.equal(events.find(e=>e.target==='bubbleAsk').frame,13);
assert(!events.some(e=>e.target==='homePin'||e.target==='tapSend'||e.target==='tapHeartSend'));
assert(!events.some(e=>e.action==='receive'&&e.target==='cardSam'));
for(const action of ['type char','backspace']){
  const chars=events.filter(e=>e.action===action);
  assert.equal(chars.length,14);
  assert(chars.every(e=>e.char.trim().length>0));
  for(const e of chars)assert.notEqual(state('draftSam',e.frame-1).text.trimEnd(),state('draftSam',e.frame).text.trimEnd());
}
assert.equal(state('draftSam',460).text,'are you home yet?');
assert.equal(state('draftSam',487).text,'are you home yet?');
assert.equal(state('draftSam',541).text,'');
for(const e of events.filter(e=>e.action==='tap')){
  const c=state('camera',e.frame),p=state('phoneMaya',e.frame),t=state(e.target,e.frame);
  const x=c.x+c.scaleX*(p.x+t.x),y=c.y+c.scaleY*(p.y+t.y);
  assert(x>40&&x<1880&&y>40&&y<1040);
}
assert.throws(()=>frameMapping({start:210,end:209,frames:90}),/Invalid/);
assert.deepEqual(visibleEvents(scene).filter(e=>e.frame>=210&&e.frame<300),[]);
const empty={fps:30,duration:2,layers:[]};
assert.equal(retimeScene(empty,{start:10,end:39,frames:10}).scene.layers.length,0);
for(const [version,hash] of [['v1','47a3cd6678980f33788726fd5784d23d20317ce8df7b75c0a28a7f0642e49c81'],['v2','22f306c8151be6aea3e51e474063904c7ba3deb780bf9cb871fc16dc00488b3c']]){
  const name=version==='v1'?'v1-first-export':'v2-revised';
  const digest=file=>createHash('sha256').update(fs.readFileSync(new URL(file,import.meta.url))).digest('hex');
  assert.equal(digest(`renders/${name}.mp4`),hash);
  assert.equal(digest(`scene.${version}.json`),read(`renders/${name}.mp4.render.json`).sceneSHA256);
}
console.log('PASS: 720 frames; endpoint-preserving 210–419 → 210–299; all other scene states retain native timing (opening camera exception).');
console.log('PASS: 35 visible soundable events, no reveal receives or space-only keys, one shared arrival; plus tap on-screen; ETA/clock agree.');
console.log('PASS: no edge-phone slivers in 720 frames; readable walk scale; arrival/draft/heart order; v1/v2 movies and scene hashes preserved; empty/error retime cases.');
