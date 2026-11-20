import assert from 'node:assert/strict';
import test from 'node:test';
import {byId, entries} from '../catalog.mjs';
import {select} from '../select.mjs';
import {buildMotion} from '../scene.mjs';
import {composeScenes} from '../sequence.mjs';

test('a second shot resets conversation state and remaps cue links', () => {
  const chat = buildMotion(byId.get('conversation-handoff'));
  const photos = buildMotion(byId.get('heading-over-fixed-photos'));
  chat.timeline.cues.push({id:'send.click',eventId:'motion.conversation-handoff.send',offsetSamples:120});
  photos.timeline.cues.push({id:'title.swish',eventId:'motion.heading-over-fixed-photos.heading-start',offsetSamples:0});
  const result = composeScenes([chat, photos]);
  const {events,cues,picture} = result.timeline;
  const cut = events.find(event => event.id === 'beat-2.cut');
  assert.equal(picture.frameCount, 144);
  assert.equal(cut.frame, 72);
  assert.equal(cut.uiState, null);
  assert.equal(events.find(event => event.kind === 'title.move').frame, 92);
  assert.deepEqual(cues.map(cue => cue.eventId),
    ['beat-1.motion.conversation-handoff.send','beat-2.motion.heading-over-fixed-photos.heading-start']);
  assert.equal(chat.layers[0].id, 'surface');
});

test('a reading hold freezes the adjacent editable scene after its motion', () => {
  const move = buildMotion(byId.get('heading-over-fixed-photos'));
  const result = composeScenes([move,null]);
  assert.equal(result.timeline.picture.frameCount, 102);
  const title = result.layers[1].children.find(node => node.id === 'beat-2.heading').children[1];
  assert.equal(title.x, 150);
  assert.equal(title.keyframes,undefined);
});

test('photos and heading have genuinely different moving scopes', () => {
  const rail = buildMotion(byId.get('photos-under-fixed-heading'));
  const heading = buildMotion(byId.get('heading-over-fixed-photos'), {direction:'up'});
  const card = scene => scene.layers.find(node => node.id === 'stage').children[0];
  const label = scene => scene.layers.find(node => node.id === 'heading').children[1];
  assert.ok(card(rail).children[1].keyframes.x);
  assert.equal(label(rail).keyframes,undefined);
  assert.equal(card(heading).children[1].keyframes,undefined);
  assert.ok(label(heading).keyframes.y[0].value > label(heading).keyframes.y.at(-1).value);
});

test('an ordinary request combines a move with an explicit reading hold', () => {
  const result = select(entries, 'Slide the heading over stationary pictures, then hold still so the viewer can read');
  assert.equal(result.action,'combine');
  assert.deepEqual(result.matches,['heading-over-fixed-photos']);
  assert.deepEqual(result.sequence.map(beat=>beat.action),['retrieve','hold']);
});
