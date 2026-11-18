import {strict as assert} from 'node:assert';
import {execFileSync} from 'node:child_process';
import {existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, symlinkSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {test} from 'node:test';
import {fileURLToPath} from 'node:url';
import {stateAt} from '../../scripts/engines/common.mjs';
import {buildCatalogScene} from './blocks.mjs';
import {byId, catalog, search} from './search.mjs';

const folder = fileURLToPath(new URL('./', import.meta.url));
const cli = fileURLToPath(new URL('../cli.mjs', import.meta.url));

const queries = [
  ['Slide photos beneath a restaurant name while the buttons stay put', 'place-photo-strip'],
  ['Swipe a carousel of stacked photo attachments in a Messages conversation', 'messages-attachment-stack'],
  ['Images move side by side in a row while the title stays put', 'place-photo-strip'],
  ['Flick the top picture in a text thread to expose the next underneath', 'messages-attachment-stack'],
  ['An inline card opens a sheet over a dimmed conversation', 'inline-card-expand'],
  ['Circular headshots gather around centered copy', 'avatar-ring-assemble']
];

test('retrieval ranks the moving object and fixed context, and defers on ambiguity', () => {
  for (const [query, id] of queries) {
    const result = search(query);
    assert.equal(result.status, 'match', query);
    assert.equal(result.selected, id, query);
    assert.ok(result.candidates[0].matches.length > 0, query);
  }
  assert.equal(search('carousel').selected, null);
  assert.equal(search('carousel').status, 'ambiguous');
  assert.equal(search('Make a rainfall simulation').status, 'no-match');
});

function defaultConfig(id) {
  const location = path.join(folder, byId.get(id).defaults);
  return JSON.parse(readFileSync(location, 'utf8'));
}

function flatten(layers) {
  return layers.flatMap(layer => [layer, ...flatten(layer.children ?? [])]);
}

const layerAt = (scene, id, t) => stateAt(flatten(scene.layers).find(layer => layer.id === id), t);

test('catalog IDs are unique, and each example has an editable and deterministic scene', () => {
  assert.equal(catalog.entries.length, byId.size);
  for (const entry of catalog.entries) {
    const config = defaultConfig(entry.id);
    assert.ok(existsSync(path.join(folder, entry.preview)), entry.preview);
    const scene = buildCatalogScene(entry.id, config);
    assert.deepEqual(scene, buildCatalogScene(entry.id, config));
    const layers = flatten(scene.layers);
    assert.equal(new Set(layers.map(layer => layer.id)).size, layers.length);
    assert.ok(layers.some(layer => layer.type === 'text'));
    assert.ok(layers.some(layer => layer.type === 'image'));
  }
});

test('strip carries all photos in a single horizontal track and fixes the UI above it', () => {
  const id = 'place-photo-strip';
  const scene = buildCatalogScene(id, defaultConfig(id));
  const start = layerAt(scene, 'photo-strip-track', 0);
  const end = layerAt(scene, 'photo-strip-track', scene.duration);
  assert.ok(end.x < start.x);
  assert.equal(end.y, start.y);
  for (const id of ['photo-strip-viewport', 'place-title', 'place-actions']) {
    assert.deepEqual(layerAt(scene, id, 0), layerAt(scene, id, scene.duration));
  }
  const viewport = layerAt(scene, 'photo-strip-viewport', 0);
  assert.ok(viewport.clip);
  assert.ok(layerAt(scene, 'place-actions', 0).y < viewport.y);
  assert.ok(flatten(scene.layers).find(layer => layer.id === 'photo-strip-track').children
    .every(tile => !tile.keyframes && tile.y === 0));
});

test('two swipes promote separate attachments and leave the composer and header in place', () => {
  const id = 'messages-attachment-stack';
  const scene = buildCatalogScene(id, {...defaultConfig(id), swipes: 2});
  const at = (index, t) => layerAt(scene, `attachment-card-${index}`, t);
  const middle = scene.duration * .52;
  assert.notEqual(at(0, 0).x, at(1, 0).x);
  assert.ok(at(0, middle).x < at(0, 0).x);
  assert.ok(at(0, middle).x < -280);
  assert.equal(at(0, middle).opacity, 1);
  assert.equal(at(1, middle).x, 0);
  assert.equal(at(1, middle).opacity, 1);
  assert.ok(at(1, scene.duration).x < -280);
  assert.equal(at(2, scene.duration).x, 0);
  assert.equal(at(2, scene.duration).opacity, 1);
  for (const id of ['conversation-title', 'conversation-copy', 'composer-field', 'attachment-count']) {
    assert.deepEqual(layerAt(scene, id, 0), layerAt(scene, id, scene.duration));
  }
  assert.throws(() => buildCatalogScene(id, {...defaultConfig(id), swipes: 4}), /swipes/);
});

test('sheet rises above the retained card and dims the underlay independently', () => {
  const id = 'inline-card-expand';
  const scene = buildCatalogScene(id, defaultConfig(id));
  const children = flatten(scene.layers).find(layer => layer.id === 'conversation').children;
  const lastLayers = children.slice(-2).map(layer => layer.id);
  assert.deepEqual(lastLayers, ['draft-scrim', 'expanded-draft-sheet']);
  assert.deepEqual(layerAt(scene, 'inline-card', 0), layerAt(scene, 'inline-card', scene.duration));
  assert.equal(layerAt(scene, 'draft-scrim', 0).opacity, 0);
  assert.ok(layerAt(scene, 'draft-scrim', scene.duration).opacity > 0);
  assert.ok(layerAt(scene, 'expanded-draft-sheet', 0).y >
    layerAt(scene, 'expanded-draft-sheet', scene.duration).y);
});

test('portrait routes are independent and the shrinking headline keeps its anchor', () => {
  const id = 'avatar-ring-assemble';
  const scene = buildCatalogScene(id, defaultConfig(id));
  const start = layerAt(scene, 'anchored-headline', 0);
  const end = layerAt(scene, 'anchored-headline', scene.duration);
  assert.deepEqual([end.x, end.y], [start.x, start.y]);
  assert.ok(end.scaleX < start.scaleX);
  const a = layerAt(scene, 'ring-avatar-0', scene.duration);
  const b = layerAt(scene, 'ring-avatar-1', scene.duration);
  assert.notDeepEqual([a.x, a.y], [b.x, b.y]);
});

test('replacements from a different directory remain separate text and image layers through the CLI', () => {
  const temp = mkdtempSync(path.join(tmpdir(), 'motion-catalog-test-'));
  try {
    const input = path.join(temp, 'edit.json');
    const staging = path.join(temp, 'nested');
    const alias = path.join(temp, 'alias');
    mkdirSync(staging);
    symlinkSync(staging, alias, 'dir');
    const output = path.join(alias, 'new.json');
    const artwork = path.join(temp, 'work.svg');
    writeFileSync(artwork, '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"/>');
    writeFileSync(input, JSON.stringify({title: 'Moss & Bark', artwork: ['work.svg', 'work.svg']}));
    const result = JSON.parse(execFileSync(process.execPath, [
      cli, 'motion', 'scene', 'place-photo-strip', '--config', input, '--out', output
    ], {encoding: 'utf8'}));
    assert.equal(result.scene, realpathSync(output));
    const layers = flatten(JSON.parse(readFileSync(output, 'utf8')).layers);
    assert.equal(layers.find(layer => layer.id === 'place-title').text, 'Moss & Bark');
    assert.equal(layers.find(layer => layer.type === 'image').src, '../work.svg');
  } finally {
    rmSync(temp, {recursive: true, force: true});
  }
});
