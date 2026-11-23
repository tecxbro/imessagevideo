import assert from 'node:assert/strict';
import test from 'node:test';
import {entries} from '../catalog.mjs';
import {describeMotionComponents, inferAdapterBindings, validateMotionBinding} from '../components.mjs';

const clip = {x: 0, y: 0, width: 390, height: 600};
const group = (id, children = [], properties = {}) => ({id, type: 'group', children, ...properties});
const media = message => {
  const owner = `ui.message/${message}`;
  return group(owner, [group(`${owner}/media`, [
    group(`${owner}/media-window`, [group(`${owner}/rail`)], {clip}),
  ])]);
};

function gallery() {
  const transcript = group('ui.transcript', [media('message.first'), media('message.chosen')]);
  const viewport = group('ui.viewport', [transcript], {clip});
  const screen = group('ui.screen', [viewport, group('ui.header'), group('ui.composer')], {clip});
  const event = {id: 'page-selected', kind: 'media.page', target: 'message.chosen', frame: 8};
  return {scene: {fps: 24, duration: 2, layers: [group('ui.camera', [screen])], timeline: {
    picture: {fpsNum: 24, fpsDen: 1, frameCount: 48}, initialUI: {conversationId: 'thread.demo'}, events: [event],
  }}, screen, transcript};
}

test('every catalog recipe resolves primary actors, anchors, event IDs and preview evidence', () => {
  const rows = entries.map(entry => describeMotionComponents(entry.id));
  assert.equal(rows.length, 77);
  assert.equal(rows.filter(row => row.production.mode === 'adapter-recipe').length, 13);
  for (const row of rows) {
    assert.ok(row.implementation.startsWith('motion/packs/'));
    assert.ok(row.whenToUse && row.avoidWhen && row.source.ref);
    assert.ok(row.demo.moving.some(actor => actor.role !== 'supportingActor'));
    assert.ok(row.demo.fixed.length > 0);
    assert.ok(row.demo.events.every(event => event.layerIds.length > 0));
    assert.match(row.preview.sha256, /^[a-f0-9]{64}$/);
    assert.equal(row.preview.evidence, 'published-demo');
    assert.ok(row.production.verification);
  }
});

test('gallery and title studies use opposite moving and fixed components', () => {
  const gallery = describeMotionComponents('photos-under-fixed-heading');
  assert.deepEqual(gallery.demo.moving.map(({id, role}) => [id, role]), [['photo-rail', 'carousel']]);
  assert.equal(gallery.demo.fixed.find(({role}) => role === 'header').id, 'heading');
  const title = describeMotionComponents('heading-over-fixed-photos');
  assert.deepEqual(title.demo.moving.map(({id, role}) => [id, role]), [['heading-copy', 'heading']]);
  assert.equal(title.demo.fixed.find(({role}) => role === 'carousel').id, 'photo-rail');
  assert.equal(title.production.mode, 'primitive-only');
});

test('gallery actor binds to the selected message, even when another row has the same components', () => {
  const {scene} = gallery();
  const id = 'photos-under-fixed-heading';
  const eventIds = ['page-selected'];
  const bindings = inferAdapterBindings(id, scene, eventIds);
  assert.equal(bindings.message, 'ui.message/message.chosen');
  assert.equal(bindings.carousel, 'ui.message/message.chosen/rail');
  assert.equal(validateMotionBinding(id, {scene, bindings, eventIds, window: [7, 24]}).ok, true);

  const different = {...bindings, message: 'ui.message/message.first', attachment: 'ui.message/message.first/media',
    attachmentViewport: 'ui.message/message.first/media-window', carousel: 'ui.message/message.first/rail'};
  const result = validateMotionBinding(id, {scene, bindings: different, eventIds});
  assert.equal(result.ok, false);
  assert.ok(result.issues.some(issue => issue.code === 'wrong-event-component' && issue.role === 'message'));
});

test('missing composer fails and a same-type layer cannot substitute for it', () => {
  const {scene, screen} = gallery();
  const id = 'photos-under-fixed-heading';
  screen.children.pop();
  screen.children.push(group('demo.footer'));
  const bindings = inferAdapterBindings(id, scene, ['page-selected']);
  const missing = validateMotionBinding(id, {scene, bindings});
  assert.ok(missing.issues.some(issue => issue.code === 'missing-component' && issue.role === 'composer'));
  const substitute = validateMotionBinding(id, {scene, bindings: {...bindings, composer: 'demo.footer'}});
  assert.ok(substitute.issues.some(issue => issue.code === 'wrong-component' && issue.role === 'composer'));
});

test('component ancestry, clipping and fixed world geometry are checked over native frames', () => {
  const {scene, screen, transcript} = gallery();
  const id = 'photos-under-fixed-heading';
  const bindings = inferAdapterBindings(id, scene, ['page-selected']);
  const viewport = screen.children[0];
  screen.children.push(viewport.children.pop());
  delete viewport.clip;
  scene.layers[0].keyframes = {x: [{t: 0, value: 0}, {t: 1, value: 15}]};
  const result = validateMotionBinding(id, {scene, bindings, window: [7, 24]});
  assert.ok(result.issues.some(issue => issue.code === 'wrong-component-parent' && issue.role === 'transcript'));
  assert.ok(result.issues.some(issue => issue.code === 'wrong-component' && issue.role === 'viewport'));
  assert.ok(result.issues.some(issue => issue.code === 'moves-fixed-component' && issue.role === 'composer'));
  transcript.children[1].children[0].children[0].clip = undefined;
  assert.ok(validateMotionBinding(id, {scene, bindings}).issues
    .some(issue => issue.code === 'wrong-component' && issue.role === 'attachmentViewport'));
});

test('fixed components use the adjacent frame before onset and must stay visible', () => {
  const {scene, screen} = gallery();
  const id = 'photos-under-fixed-heading';
  const eventIds = ['page-selected'];
  const bindings = inferAdapterBindings(id, scene, eventIds);
  scene.layers[0].keyframes = {x: [{t: 0, value: 0}, {t: 8 / 24, value: 15, ease: 'hold'}]};
  screen.children[2].start = 8 / 24;
  const result = validateMotionBinding(id, {scene, bindings, eventIds, window: [8, 24]});
  assert.ok(result.issues.some(issue => issue.code === 'moves-fixed-component' && issue.role === 'header'));
  assert.ok(result.issues.some(issue => issue.code === 'inactive-fixed-component' && issue.frame === 7
    && issue.role === 'composer'));
});

test('a fixed header preserves the title position inside it', () => {
  const {scene, screen} = gallery();
  const id = 'photos-under-fixed-heading';
  const eventIds = ['page-selected'];
  const bindings = inferAdapterBindings(id, scene, eventIds);
  screen.children[1].children.push({
    id: 'ui.header.title', type: 'text',
    keyframes: {x: [{t: 7 / 24, value: 0}, {t: 14 / 24, value: 50}]},
  });
  const result = validateMotionBinding(id, {scene, bindings, eventIds, window: [7, 24]});
  assert.ok(result.issues.some(issue => issue.code === 'moves-fixed-component' && issue.role === 'header'));
});

test('send binding chooses the visible draft revision before the selected send', () => {
  const {scene, screen} = gallery();
  const composer = screen.children[2];
  composer.children = [
    group('ui.composer@0', [
      {id: 'ui.composer.draft', type: 'text'}, {id: 'ui.composer.send', type: 'rect'},
    ], {end: 4 / 24}),
    group('ui.composer@4', [
      group('ui.composer.draft@4'), group('ui.composer.send@4'),
    ], {start: 4 / 24, end: 8 / 24}),
    group('ui.composer@8', [
      group('ui.composer.draft@8'), group('ui.composer.send@8'),
    ], {start: 8 / 24}),
  ];
  scene.timeline.events = [
    {id: 'send', kind: 'send', target: 'message.chosen', frame: 8},
  ];
  const eventIds = ['send'];
  const bindings = inferAdapterBindings('draft-send-flight', scene, eventIds);
  assert.equal(bindings.draft, 'ui.composer.draft@4');
  assert.equal(bindings.sendButton, 'ui.composer.send@4');
  assert.equal(validateMotionBinding('draft-send-flight', {scene, bindings, eventIds}).ok, true);
});

test('a preview depiction of seeking has no production adapter binding', () => {
  const id = 'media-video-scrub';
  const description = describeMotionComponents(id);
  assert.equal(description.production.mode, 'depiction-only');
  assert.equal(description.demo.moving.find(({role}) => role === 'playhead').id, 'scrub-thumb');
  assert.equal(validateMotionBinding(id).ok, false);
});
