/** Independent behavior contracts for the reusable director toolkit.
 * Run: node --test director/test_toolkit.mjs
 * No browser, generated video, toolkit edits, or persistent test artifacts.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {mkdtempSync, readdirSync, readFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {buildMotion, MOTIFS} from './motions.mjs';
import * as components from './components.mjs';
import {CHOICES, recommend, directorPlan} from './decisions.mjs';
import {stateAt, svgMarkup} from '../scripts/engines/common.mjs';

const fpsValues = [24, 25, 30, 60];
const flatten = layers => layers.flatMap(layer => [layer, ...flatten(layer.children ?? [])]);
const framesFor = scene => Math.round(scene.duration * scene.fps);
const find = (scene, id) => flatten(scene.layers).find(layer => layer.id === id);
const scalarText = value => !/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value);
function finiteNumbers(value, path = 'state') {
  if (typeof value === 'number') assert.ok(Number.isFinite(value), `${path} must be finite`);
  else if (Array.isArray(value)) value.forEach((entry, i) => finiteNumbers(entry, `${path}[${i}]`));
  else if (value && typeof value === 'object') for (const [key, entry] of Object.entries(value)) {
    if (key !== 'children' && key !== 'keyframes') finiteNumbers(entry, `${path}.${key}`);
  }
}
function validateScene(result) {
  const {scene, events} = result, layers = flatten(scene.layers);
  assert.equal(scene.width, 960); assert.equal(scene.height, 540);
  assert.ok(layers.length > 0, 'A starter must contain visible-design actors');
  const ids = layers.map(layer => layer.id);
  assert.equal(new Set(ids).size, ids.length, 'Every actor must have a unique ID');
  for (const layer of layers) {
    assert.match(layer.id, /^[-a-zA-Z0-9_]+$/);
    assert.ok(['group', 'text', 'rect', 'path', 'circle', 'image'].includes(layer.type));
    for (const track of Object.values(layer.keyframes ?? {})) {
      assert.ok(Array.isArray(track) && track.length > 0);
      for (const key of track) {
        assert.ok(Number.isFinite(key.t) && key.t >= 0 && key.t <= scene.duration);
        if (typeof key.value === 'number') assert.ok(Number.isFinite(key.value));
      }
    }
  }
  let previous = -1;
  const seen = new Set();
  for (const event of events) {
    assert.ok(Number.isInteger(event.frame) && event.frame >= 0 && event.frame < framesFor(scene));
    assert.equal(event.time, event.frame / scene.fps);
    assert.ok(event.frame >= previous, 'Action export is chronological'); previous = event.frame;
    assert.ok(ids.includes(event.target), `Cue target ${event.target} exists`);
    const key = `${event.frame}:${event.kind}:${event.target}`;
    assert.ok(!seen.has(key), 'No duplicate sound for one actor/action/frame'); seen.add(key);
  }
  for (let frame = 0; frame < framesFor(scene); frame++) {
    for (const layer of layers) {
      const state = stateAt(layer, frame / scene.fps);
      finiteNumbers(state, `${scene.title}/${frame}/${layer.id}`);
      assert.ok(state.opacity >= 0 && state.opacity <= 1);
      for (const dimension of ['width', 'height', 'fontSize']) if (state[dimension] !== undefined) assert.ok(state[dimension] > 0);
      if (state.type === 'text') assert.ok(scalarText(String(state.text ?? '')), `No broken Unicode at ${scene.title}/${frame}/${layer.id}`);
    }
  }
}

test('all nine motifs are distinct, discoverable and routed by matching metadata', () => {
  assert.equal(MOTIFS.length, 9); assert.equal(new Set(MOTIFS).size, 9);
  assert.deepEqual(new Set(CHOICES.map(choice => choice.id)), new Set(MOTIFS));
  assert.equal(components.COMPONENTS.length, 9);
  for (const component of components.COMPONENTS) assert.equal(typeof components[component.name], 'function');
});

for (const motif of MOTIFS) test(`${motif}: unique actors, valid native frames and cue targets across duration/fps boundaries`, () => {
  for (const fps of fpsValues) for (const duration of [2, 4.137, 12]) validateScene(buildMotion(motif, {fps, duration}));
});

for (const motif of MOTIFS) test(`${motif}: scene/SVG/cue exports are deterministic and disclose starter provenance`, () => {
  const options = {fps: 25, duration: 3.4, copy: 'Can we go?', title: 'A real result', color: '#aabbcc', count: 5};
  const originalOptions = structuredClone(options);
  const a = buildMotion(motif, options); const frozenJSON = JSON.stringify(a);
  buildMotion(MOTIFS[(MOTIFS.indexOf(motif) + 1) % MOTIFS.length], {duration: 2});
  const b = buildMotion(motif, options);
  assert.equal(JSON.stringify(b), frozenJSON); assert.deepEqual(options, originalOptions);
  assert.match(a.provenance, /new|authored|adaptable/i);
  assert.match(a.scene.source.notes, /not an exact reference recreation/i);
  assert.match(a.scene.source.notes, /Arial.*replace.*remeasure/i);
  assert.equal(flatten(a.scene.layers).filter(layer => layer.type === 'image').length, 0, 'Generic starters must not silently import reference raster screens');
  for (const event of a.events) assert.match(event.evidence, /authored starter.*not a measured source cue/i);
  const roundTrip = JSON.parse(JSON.stringify(a.scene));
  for (const frame of [0, Math.floor(framesFor(a.scene) / 2), framesFor(a.scene) - 1]) {
    const t = frame / a.scene.fps;
    assert.equal(svgMarkup(a.scene, t), svgMarkup(b.scene, t));
    assert.equal(svgMarkup(a.scene, t), svgMarkup(roundTrip, t));
  }
  a.scene.layers[0].id = 'mutated-by-caller';
  assert.equal(JSON.stringify(buildMotion(motif, options)), frozenJSON, 'One caller cannot mutate future builds');
});

function draftTransitions(result) {
  const input = find(result.scene, 'composer-input'); assert.ok(input);
  const changes = []; let previous = '';
  for (let frame = 0; frame < framesFor(result.scene); frame++) {
    const text = String(stateAt(input, frame / result.scene.fps).text ?? '');
    if (text && text !== previous) changes.push({frame, text, delta: Array.from(text).length - Array.from(previous).length});
    previous = text;
  }
  return changes;
}

const typingCases = [
  {name: 'ordinary request', copy: 'Can you book a table?', duration: 4},
  {name: 'batch changes shorter than one glyph per frame', copy: 'abcdefghijklmnopqrstuvwxyz'.repeat(3), duration: 2},
  {name: 'one-character exact-boundary send', copy: 'Y', duration: 2},
  {name: 'nonintegral duration', copy: 'Friday at seven, please.', duration: 2.031},
  {name: 'repeated characters and spaces', copy: 'Sooo  ready!!', duration: 2.4},
  {name: 'Unicode request', copy: 'Hi 👋 café 🚀, dinner?', duration: 3.7},
  {name: 'Unicode truncation boundary', copy: 'a'.repeat(71) + '🚀Z', duration: 2},
];
for (const spec of typingCases) test(`typing causality: ${spec.name} at every supported fps`, () => {
  for (const fps of fpsValues) {
    const result = buildMotion('conversation-handoff', {fps, duration: spec.duration, copy: spec.copy});
    const input = find(result.scene, 'composer-input');
    const outgoing = find(result.scene, 'sent-copy'); assert.ok(outgoing);
    const expected = Array.from(spec.copy).slice(0, 72).join('');
    assert.equal(outgoing.text, expected);
    const transitions = draftTransitions(result), cues = result.events.filter(event => event.kind === 'typing');
    assert.deepEqual(cues.map(event => event.frame), transitions.map(change => change.frame), 'One cue per actual rendered draft change; no inferred physical key count');
    assert.equal(new Set(cues.map(event => event.frame)).size, cues.length);
    for (let i = 0; i < cues.length; i++) {
      assert.equal(cues[i].target, input.id); assert.equal(cues[i].observed_character_delta, transitions[i].delta);
      assert.ok(transitions[i].delta > 0); assert.ok(expected.startsWith(transitions[i].text)); assert.ok(scalarText(transitions[i].text));
    }
    assert.ok(transitions.some(change => change.text === expected), 'The complete outgoing draft is shown before send');
    if (spec.name.startsWith('batch')) assert.ok(cues.some(event => event.observed_character_delta > 1), 'A low-fps batch is not expanded into fake per-character sounds');
    const send = result.events.filter(event => event.kind === 'message_send'); assert.equal(send.length, 1);
    assert.ok(cues.every(event => event.frame < send[0].frame), 'No typing on or after input clear');
    for (let frame = send[0].frame; frame < framesFor(result.scene); frame++) assert.equal(stateAt(input, frame / fps).text, '', 'Send clears the composer and the old draft never returns');
    const arrival = result.events.filter(event => event.kind === 'message_arrival'); assert.equal(arrival.length, 1); assert.ok(arrival[0].frame > send[0].frame);
    const reply = find(result.scene, 'reply-copy'); assert.ok(reply);
    for (let frame = 0; frame < framesFor(result.scene); frame++) assert.equal(stateAt(reply, frame / fps).text, reply.text, 'AI response arrives whole, without authored keystrokes');
  }
});

test('an empty or whitespace-only composer cannot send an empty message or conjure a reply', () => {
  for (const copy of ['', '   ', '\n\t']) {
    const result = buildMotion('conversation-handoff', {copy});
    assert.equal(result.events.filter(event => ['message_send', 'message_arrival'].includes(event.kind)).length, 0);
    assert.equal(find(result.scene, 'sent'), undefined); assert.equal(find(result.scene, 'reply'), undefined);
    if (!copy) assert.equal(result.events.filter(event => event.kind === 'typing').length, 0);
  }
});

test('no title, AI reply, preexisting montage or static composer acquires typing cues', () => {
  for (const motif of MOTIFS.filter(id => id !== 'conversation-handoff')) {
    const result = buildMotion(motif, {copy: 'New words do not imply typing', title: 'A changing idea'});
    assert.equal(result.events.filter(event => event.kind === 'typing').length, 0, motif);
  }
  assert.deepEqual(buildMotion('message-wall').events, [], 'A montage of existing messages is not new send/arrival events');
});

test('camera focus moves its parent while the local card layout stays stable', () => {
  const {scene} = buildMotion('camera-focus'); const camera = scene.layers[0], card = find(scene, 'focus-card');
  assert.notEqual(stateAt(camera, 0).scaleX, stateAt(camera, 3).scaleX);
  for (const key of ['x', 'y', 'width', 'height']) assert.equal(stateAt(card, 0)[key], stateAt(card, 3)[key]);
  for (const child of flatten(card.children)) assert.deepEqual(child.keyframes ?? {}, {}, 'Camera travel does not reflow local UI');
});

test('morphs preserve one surface identity and keep an actual circle at the beginning', () => {
  for (const [motif, id] of [['identity-morph', 'identity-surface'], ['circle-to-panel', 'morph-surface']]) {
    const {scene} = buildMotion(motif); const surface = find(scene, id), first = stateAt(surface, 0), last = stateAt(surface, 3.9);
    assert.equal(first.width, first.height); assert.equal(first.radius, first.width / 2);
    assert.ok(last.radius < Math.min(last.width, last.height) / 2);
    assert.equal(flatten(scene.layers).filter(layer => layer.id === id).length, 1);
    assert.equal(first.opacity, 1); assert.equal(last.opacity, 1);
  }
});

test('selection changes the existing control instead of duplicating its result actor', () => {
  const {scene, events} = buildMotion('selection-confirm');
  const action = find(scene, 'selection-card-action'); assert.ok(action);
  assert.equal(flatten(scene.layers).filter(layer => layer.id === action.id).length, 1);
  const label = find(scene, 'selection-card-action-label');
  assert.equal(stateAt(label, 0).text, 'Confirm'); assert.equal(stateAt(label, 3.99).text, 'Confirmed');
  assert.equal(events.filter(event => event.kind === 'tap').length, 1); assert.equal(events[0].target, action.id);
});

test('viewport clips belong to phone screen and bottom sheet, preserving nested actor identity', () => {
  const {scene} = buildMotion('app-drawer');
  const screen = find(scene, 'phone-screen'), drawer = find(scene, 'drawer');
  assert.ok(screen.clip && drawer.clip); assert.equal(find(scene, 'phone').clip, undefined);
  assert.ok(flatten(screen.children).some(layer => layer.id === drawer.id));
  assert.equal(flatten(drawer.children).filter(layer => /^app-\d$/.test(layer.id)).length, 6);
});

test('invalid native clock or unknown motif fails explicitly', () => {
  assert.throws(() => buildMotion('unrecognized'));
  for (const duration of [0, -1, 1.99, 12.01, NaN, Infinity, '4']) assert.throws(() => buildMotion('app-drawer', {duration}));
  for (const fps of [0, 23.976, 29.97, 120, NaN, Infinity, '30']) assert.throws(() => buildMotion('app-drawer', {fps}));
});

test('message count cannot silently collapse an otherwise valid wall into an empty stage', () => {
  for (const count of [3, 9, 15, 1, 100]) {
    const result = buildMotion('message-wall', {count});
    const messages = flatten(result.scene.layers).filter(layer => /^wall-message-\d+$/.test(layer.id));
    assert.ok(messages.length >= 3 && messages.length <= 15);
  }
  assert.throws(() => buildMotion('message-wall', {count: NaN}), 'Nonfinite input should fail instead of silently deleting the wall');
});

test('SVG export escapes user copy instead of treating it as markup', () => {
  const result = buildMotion('message-wall', {copy: '<script>alert("x")</script>&🚀'});
  const svg = svgMarkup(result.scene, 1);
  assert.ok(!svg.includes('<script>')); assert.ok(svg.includes('&lt;script&gt;')); assert.ok(svg.includes('&amp;'));
});

test('routing remains explainable and never upgrades a starter into source-measured authority', () => {
  assert.deepEqual(recommend(''), []); assert.deepEqual(recommend('unmatched vocabulary xyzzy'), []);
  const a = directorPlan('Show an assistant request, then send and reply'); const b = directorPlan(a.brief);
  assert.deepEqual(a, b); assert.equal(a.mode, 'original-direction');
  assert.equal(a.suggestions[0].motif, 'conversation-handoff');
  assert.ok(a.suggestions[0].matchedWords.includes('assistant'));
  assert.match(a.authority, /keyword.*judgment.*reference evidence/i);
  assert.match(a.exact_recreation_rule, /measure.*Never substitute.*starter/i);
  assert.equal(directorPlan('').suggestions.length, 0); assert.ok(directorPlan('').unresolved.length);
});

test('CLI list and plan exports are deterministic and require no mutable scene artifacts', () => {
  const cli = fileURLToPath(new URL('./cli.mjs', import.meta.url));
  const invoke = args => {
    const result = spawnSync(process.execPath, [cli, ...args], {encoding: 'utf8'});
    assert.equal(result.status, 0, result.stderr); return result.stdout;
  };
  const listing = JSON.parse(invoke(['list'])); assert.deepEqual(listing.motifs, MOTIFS); assert.equal(listing.components.length, 9);
  const args = ['plan', '--brief', 'A camera should focus on a readable detail'];
  const a = invoke(args), b = invoke(args); assert.equal(a, b); assert.deepEqual(JSON.parse(a), directorPlan(args[2]));
});

test('CLI sampled SVG frames stay inside the same native range as the render engine at fractional durations', () => {
  const cli = fileURLToPath(new URL('./cli.mjs', import.meta.url));
  const scratch = mkdtempSync(path.join(tmpdir(), 'motion-toolkit-contract-'));
  try {
    for (const duration of [2.01, 4.137]) {
      const output = path.join(scratch, String(duration));
      const proc = spawnSync(process.execPath, [cli, 'frames', '--motif', 'camera-focus', '--duration', String(duration), '--out', output], {encoding: 'utf8'});
      assert.equal(proc.status, 0, proc.stderr);
      const {scene} = buildMotion('camera-focus', {duration});
      const names = readdirSync(output).filter(name => name.endsWith('.svg'));
      assert.ok(names.length > 0);
      for (const name of names) {
        const frame = Number(name.slice(0, -4));
        assert.ok(Number.isInteger(frame) && frame >= 0 && frame < framesFor(scene), `${name} must be within native0…${framesFor(scene)-1}`);
        assert.equal(readFileSync(path.join(output, name), 'utf8'), svgMarkup(scene, frame / scene.fps));
      }
      assert.ok(names.includes(String(framesFor(scene) - 1).padStart(6, '0') + '.svg'), 'The settled final native frame is included');
    }
  } finally { rmSync(scratch, {recursive: true, force: true}); }
});
