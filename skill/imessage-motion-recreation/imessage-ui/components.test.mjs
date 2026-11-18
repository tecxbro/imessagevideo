import test from 'node:test';
import assert from 'node:assert/strict';
import {buildConversation,wrapText,validateConversation,Message,ComposerState,PhotoStack} from './components.mjs';
import {trial} from './trial.mjs';
import {svgMarkup,stateAt} from '../scripts/engines/common.mjs';

const clusters=value=>[...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(value)];
const measure=(value,size=17)=>clusters(value).length*size*.54;
const flatten=layers=>layers.flatMap(layer=>[layer,...flatten(layer.children ?? [])]);
const clone=()=>structuredClone(trial);
test('wrapping preserves explicit paragraphs, long tokens and whole emoji clusters',()=>{
  const copy='Supercalifragilisticexpialidociouslyunderfiredbisqueware\n👩🏽‍🔬🧑🏿‍🎨🏳️‍🌈';
  const lines=wrapText(copy,90,measure);
  assert.equal(lines.join(''),copy.replaceAll('\n',''));
  for(const line of lines)assert.ok(measure(line)<=90);
  assert.ok(lines.some(line=>line.includes('👩🏽‍🔬')));
  assert.ok(lines.some(line=>line.includes('🧑🏿‍🎨')));
});
test('emoji-only messages are large text without a bubble surface',()=>{
  const message=Message({id:'emoji',copy:'👩🏽‍🔬🧑🏿‍🎨🏳️‍🌈',measure});
  assert.equal(message.layer.children.length,1);assert.equal(message.layer.children[0].fontSize,48);
});
test('reactions retain explicit owner and message independently from message side',()=>{
  const {scene,audit}=buildConversation(trial,measure);
  assert.deepEqual(audit.messages[0].reactions.map(r=>r.ownerId),['jo','self']);
  const layers=flatten(scene.layers);
  assert.equal(layers.find(layer=>layer.id==='msg-invite-reaction-0').ownerId,'jo');
  assert.equal(layers.find(layer=>layer.id==='msg-invite-reaction-1').ownerId,'self');
  assert.equal(layers.find(layer=>layer.id==='msg-invite-reaction-0-owner').text,'JR');
  assert.equal(layers.find(layer=>layer.id==='msg-invite-reaction-1-emoji').text,'👍');
  for(const reaction of layers.filter(layer=>/^msg-invite-reaction-\d$/.test(layer.id))){
    assert.equal(reaction.y,-24);assert.ok(reaction.y+34>0,'Badge touches its bubble, not a floating sender-label row');
  }
});
test('link URL is retained in input but displayed once as a preview',()=>{
  const config=clone();const url='https://example.com/a-very-long-link';
  config.messages[0].copy='read this → '+url;
  config.messages[0].link={url,title:'Read this',color:'#c4a484'};
  const {scene}=buildConversation(config,measure),layers=flatten(scene.layers);
  assert.equal(config.messages[0].copy,'read this → '+url);
  assert.equal(layers.find(layer=>layer.id==='msg-invite-copy').text,'read this →');
  assert.equal(layers.find(layer=>layer.id==='msg-invite-link-domain').text,'example.com');
});
test('composer grows, transfers once, clears and disables empty send',()=>{
  const {scene,audit}=buildConversation(trial,measure);
  assert.equal(audit.composer[0].enabled,false);
  assert.ok(audit.composer.at(-2).height>audit.composer[0].height);
  assert.equal(audit.composer.at(-1).copy,'');assert.equal(audit.composer.at(-1).enabled,false);
  const before=svgMarkup(scene,11.9), after=svgMarkup(scene,12.3);
  assert.match(before,/draft-3-input/);assert.doesNotMatch(before,/data-layer="msg-send-row"/);
  assert.doesNotMatch(after,/draft-3-input/);assert.match(after,/data-layer="msg-send-row"/);
});
test('attachment-only composer enables send and reserves attachment height',()=>{
  const draft=ComposerState({id:'draft',copy:'',attachment:'1 photo',measure,start:0,end:1});
  assert.equal(draft.enabled,true);assert.ok(draft.height>44);
});
test('photo geometry retains different original aspect ratios',()=>{
  const photos=[{color:'#6B8F71',aspectRatio:4/5},{color:'#D9A5B3',aspectRatio:1},{color:'#3E4A61',aspectRatio:16/9}];
  const built=PhotoStack({id:'photos',photos,caption:'kiln 2 shelf layout v3',measure});
  const images=flatten([built.layer]).filter(layer=>layer.id.endsWith('-image'));
  assert.deepEqual(images.map(layer=>layer.width/layer.height),photos.map(photo=>photo.aspectRatio));
  assert.equal(built.reactionAnchor.x,7+images[0].width);
  assert.equal(built.reactionAnchor.y,12);
});
test('camera moves one clipped hierarchy, not local message geometry',()=>{
  const first=buildConversation(trial,measure);const changed=clone();changed.camera[1].scale=1.6;
  const second=buildConversation(changed,measure);
  assert.deepEqual(first.audit,second.audit);
  const layers=flatten(second.scene.layers);
  assert.ok(layers.find(layer=>layer.id==='transcript-viewport').clip);
  assert.ok(layers.find(layer=>layer.id==='phone-screen').clip);
  assert.equal(stateAt(layers.find(layer=>layer.id==='conversation-camera'),4.8).scaleX,1.6);
});
test('scene IDs are unique, finite at every native frame, deterministic and escaped',()=>{
  const input=clone();input.messages[0].copy='<script>hello & goodbye</script>';
  const original=structuredClone(input), {scene}=buildConversation(input,measure), layers=flatten(scene.layers);
  assert.deepEqual(input,original);assert.deepEqual(buildConversation(input,measure).scene,scene);
  assert.equal(new Set(layers.map(layer=>layer.id)).size,layers.length);
  for(let frame=0;frame<scene.duration*scene.fps;frame++)for(const layer of layers){
    const state=stateAt(layer,frame/scene.fps);
    for(const key of ['x','y','scaleX','scaleY','opacity'])assert.ok(Number.isFinite(state[key]));
  }
  assert.match(svgMarkup(scene,.4),/&lt;script&gt;/);assert.doesNotMatch(svgMarkup(scene,.4),/<script>/);
});
for(const [name,mutate,pattern] of [
  ['unknown reaction owner',c=>c.messages[0].reactions[0].ownerId='ghost',/reaction owner/],
  ['early reaction',c=>c.messages[1].reactions[0].at=0,/follow its message/],
  ['duplicate participant',c=>c.participants.push({...c.participants[0]}),/unique/],
  ['duplicate message',c=>c.messages[1].id=c.messages[0].id,/unique/],
  ['uncleared send',c=>c.composer.at(-1).copy='duplicate',/transfer/],
  ['wrong draft',c=>c.messages[3].copy='not the draft',/transfer/],
  ['bad camera',c=>c.camera[0].scale=NaN,/Camera/],
  ['non-monotonic composer',c=>c.composer[2].at=1,/increase/]
])test('rejects '+name,()=>{const config=clone();mutate(config);assert.throws(()=>validateConversation(config),pattern);});
