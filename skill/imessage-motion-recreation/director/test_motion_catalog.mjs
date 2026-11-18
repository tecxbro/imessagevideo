import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import test from 'node:test';
import {fileURLToPath} from 'node:url';
import {buildCatalogScene, describeMotion, getMotion, searchMotions} from './motion-catalog.mjs';
import {stateAt, svgMarkup} from '../scripts/engines/common.mjs';

const photo = 'linq-fixed-chrome-photo-rail';
const fare = 'linq-flight-fare-rail';
const amount = 'linq-amount-units-roll';
const stack = 'messages-attachment-stack';
const cli = fileURLToPath(new URL('./motion-catalog-cli.mjs', import.meta.url));
const walk = layers => layers.flatMap(layer => [layer, ...walk(layer.children ?? [])]);

test('retrieves mechanics rather than generic shared words like swipe, photo, or card', () => {
  const prompts = [
    [photo, 'The row of thumbnails moves left while the toolbar buttons stay put'],
    [photo, 'Slide pictures under an unmoving header, rather than a Messages attachment stack'],
    [photo, 'Linq frames 1091–1111'],
    [stack, 'In a chat thread, I want to swipe through an overlapping deck of photos and show the next attachment at the front'],
    [stack, 'Move the top photo behind the others in our iMessage bubble'],
    [fare, 'Slide the ticket tier cards horizontally so I can compare baggage limits and flight options'],
    [amount, 'Show the ones digit increment as the plus button pulses'],
  ];
  for (const [expected, query] of prompts) {
    const result = searchMotions(query);
    assert.equal(result.status, 'matched', query);
    assert.equal(result.selection, expected, query);
    assert.equal(result.results[0].id, expected, query);
  }
  assert.deepEqual(searchMotions('a photo swipe').status, 'ambiguous');
  assert.equal(searchMotions('shatter into confetti').status, 'no-match');
  assert.equal(describeMotion(getMotion(stack)).source, null);
  assert.throws(() => buildCatalogScene(stack), /No verified/);
});

test('each source window and fitted sample matches the accepted Linq scene', () => {
  const path = new URL('../../../'+describeMotion(getMotion(photo)).source.fit_scene, import.meta.url);
  const canonical = walk(JSON.parse(readFileSync(path, 'utf8')).layers);
  for (const id of [photo, fare, amount]) {
    const {frames:[first,last], fit, beats} = getMotion(id);
    assert.equal(fit.samples_start, first);
    assert.ok(fit.samples.length >= last-first+1);
    assert.ok(beats.every(([frame]) => frame >= first && frame <= last));
    const node = canonical.find(layer => layer.id === fit.layer);
    assert.ok(node, fit.layer);
    fit.samples.forEach((sample, i) => {
      assert.ok(Math.abs(stateAt(node, (first+i)/30)[fit.property]-sample) < .051, `${id} frame ${first+i}`);
    });
  }
});

test('artwork edits preserve photo choreography, clip and chrome for every output frame', () => {
  const original = buildCatalogScene(photo);
  const options = JSON.parse(readFileSync(new URL('./examples/solar-lab-artwork.json', import.meta.url), 'utf8'));
  const variant = buildCatalogScene(photo, options);
  const source = variant.source.evidence;
  assert.deepEqual(source.citedFrames, [1091,1111]);
  assert.deepEqual(source.fittedFrames, [1091,1122]);
  assert.equal(variant.layers.find(layer => layer.id === 'gallery-title').text, options.title);
  const container = variant.layers.find(layer => layer.id === 'photo-rail-viewport');
  const [rail] = container.children;
  assert.deepEqual(container.clip, {width:578, height:334});
  assert.deepEqual(rail.keyframes, original.layers.find(layer => layer.id === container.id).children[0].keyframes);
  assert.deepEqual(variant.layers.flatMap(layer => Object.keys(layer.keyframes ?? {})), []);
  assert.ok(rail.children.every(layer => !layer.keyframes));
  const first = stateAt(rail, source.outputLeadFrames/30).x;
  const last = stateAt(rail, (source.outputLeadFrames+20)/30).x;
  assert.ok(first-last > 1150);
  assert.notEqual(svgMarkup(variant, 0), svgMarkup(original, 0));
  assert.throws(() => buildCatalogScene(photo,{cards:[{}]}), /exactly five/);
});

test('fare CTAs ride the clipped rail; amount moves only a masked lane and a separate plus', () => {
  const rail = buildCatalogScene(fare).layers.find(layer => layer.id === 'fare-rail-viewport').children[0];
  assert.ok(rail.children.every(layer => layer.children.some(child => child.id.endsWith('-action'))));
  const scene = buildCatalogScene(amount, {startDigit:4});
  const byId = Object.fromEntries(walk(scene.layers).map(layer => [layer.id, layer]));
  assert.equal(byId['units-viewport'].clip.height, 94);
  assert.deepEqual(byId['units-rail'].children.map(layer => layer.text), ['4','5','6','7','8']);
  assert.deepEqual(Object.keys(byId['units-rail'].keyframes), ['y']);
  assert.deepEqual(Object.keys(byId['amount-plus'].keyframes), ['scaleX','scaleY']);
  assert.equal(byId['amount-prefix'].keyframes, undefined);
  assert.throws(() => buildCatalogScene(amount,{startDigit:6}), /no carry/);
});

test('CLI keeps outputs editable and refuses to overwrite a scene', () => {
  const dir = mkdtempSync(join(tmpdir(), 'catalog-test-'));
  try {
    const run = (...args) => spawnSync(process.execPath, [cli, ...args], {cwd:dir, encoding:'utf8'});
    const search = run('search', 'Pictures glide under fixed navigation buttons');
    assert.equal(search.status, 0, search.stderr);
    assert.equal(JSON.parse(search.stdout).selection, photo);
    const build = run('scene', photo, '--out', 'output/scene.json');
    assert.equal(build.status, 0, build.stderr);
    assert.equal(JSON.parse(readFileSync(join(dir,'output/scene.json'))).fps, 30);
    assert.notEqual(run('scene', photo, '--out', 'output/scene.json').status, 0);
    assert.notEqual(run('source', stack, '--out', 'not-a-source.mp4').status, 0);
  } finally {
    rmSync(dir, {recursive:true, force:true});
  }
});
