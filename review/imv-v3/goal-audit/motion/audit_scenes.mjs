import {createHash} from 'node:crypto';
import {existsSync, readFileSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [skillPath, freshPath, outPath] = process.argv.slice(2);
if (!outPath) throw Error('Usage: node audit_scenes.mjs SKILL_DIRECTORY FRESH_PREVIEWS OUTPUT.json');
const skill = path.resolve(skillPath);
const motion = path.join(skill, 'motion');
const imp = name => import(pathToFileURL(path.join(motion, name)).href);
const {entries, metadata} = await imp('catalog.mjs');
const {buildMotion, defaults} = await imp('scene.mjs');
const {buildUiMotion, uiIds} = await imp('ui-bridge.mjs');
const jsonFile = name => JSON.parse(readFileSync(name, 'utf8'));
const pathShort = value => value.startsWith(skill + path.sep) ? path.relative(skill, value) : path.basename(value);
const hash = value => createHash('sha256').update(value).digest('hex');
const linesByModule = new Map(entries.map(({implementation}) => implementation).map(file => [
  file, readFileSync(path.join(motion, file), 'utf8').split('\n'),
]));

function filePointer(entry) {
  const lines = linesByModule.get(entry.implementation);
  const quoted = new RegExp(`(['"\x60])${entry.id}\\1`);
  const found = lines.findIndex(line => quoted.test(line));
  return {path: `motion/${entry.implementation}`, line: found < 0 ? null : found + 1,
    builder: entry.build.name || 'inline builder'};
}

function assetInfo(name) {
  const exists = existsSync(name);
  return {path: pathShort(name), present: exists, sha256: exists ? hash(readFileSync(name)) : null};
}

function normalizeTrack(keys) {
  return keys.map(({t, value, ease}) => [
    Number(t.toFixed(8)), typeof value === 'string' ? '<changed text or color>' : value, ease,
  ]);
}

function sceneEvidence(scene) {
  const layerIds = new Set();
  const duplicates = [];
  const movingLayers = [];
  const assetNames = new Set();
  const channelsFingerprint = [];
  function visit(layers, parent, parentType) {
    for (const layer of layers) {
      if (layerIds.has(layer.id)) duplicates.push(layer.id);
      layerIds.add(layer.id);
      if (layer.src) assetNames.add(layer.src);
      if (layer.keyframes) {
        const channels = Object.fromEntries(Object.entries(layer.keyframes)
          .filter(([, keys]) => new Set(keys.map(({value}) => JSON.stringify(value))).size > 1));
        if (Object.keys(channels).length) {
          movingLayers.push({layer: layer.id, parent, type: layer.type, channels: Object.keys(channels)});
          channelsFingerprint.push([layer.type, parentType, Object.entries(channels)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([channel, keys]) => [channel, normalizeTrack(keys)])]);
        }
      }
      visit(layer.children ?? [], layer.id, layer.type);
    }
  }
  visit(scene.layers, null, null);
  for (const font of scene.fonts ?? []) if (font.src) assetNames.add(font.src);
  const events = scene.timeline.events.map(({id, kind, target, frame, layerIds: refs, uiState}) => ({
    id, kind, target, frame, hasState: Boolean(uiState),
    unresolvedLayerIds: (refs ?? []).filter(ref => !layerIds.has(ref)),
  }));
  return {
    topLevel: scene.layers.map(layer => layer.id),
    layerCount: layerIds.size,
    assets: [...assetNames].sort().map(assetInfo),
    eventMap: events,
    initialUI: Boolean(scene.timeline.initialUI),
    animatedLayers: movingLayers,
    duplicateLayerIds: duplicates,
    trackSignature: hash(JSON.stringify(channelsFingerprint.map(track => JSON.stringify(track)).sort())),
  };
}

function testEdit(entry, field, build, ui = false) {
  const samples = {
    direction: ['left', 'right'],
    swipes: [1, 2],
    values: [[9, 25], [17, 79]],
    photos: [
      Array.from({length: entry.photoCount?.min ?? 2}, (_, i) => defaults.photos[i % defaults.photos.length]),
      Array.from({length: entry.photoCount?.min ?? 2}, (_, i) => defaults.photos[(i + 1) % defaults.photos.length]),
    ],
  };
  const values = ui && entry.id === 'delivery-receipt-handoff' && field === 'detail'
    ? ['Delivered', 'Read'] : samples[field] ?? ['North access', 'West gate'];
  try {
    const scenes = values.map(value => build({[field]: value}));
    return JSON.stringify(scenes[0].layers) === JSON.stringify(scenes[1].layers)
      ? 'unchanged layer tree' : 'changes layer tree';
  } catch (error) {
    return error.message;
  }
}

const catalog = jsonFile(path.join(motion, 'catalog.json'));
const catalogRows = new Map(catalog.entries.map(row => [row.id, row]));
const rows = entries.map(entry => {
  const row = catalogRows.get(entry.id);
  const build = content => buildMotion(entry, content);
  const data = sceneEvidence(build({}));
  const recipeMetadata = metadata(entry);
  const hasUi = uiIds.includes(entry.id);
  const buildUI = content => buildUiMotion(entry, content);
  const uiPicture = hasUi ? jsonFile(path.join(freshPath, `ui.${row.id}.scene.json`)) : null;
  return {
    id: row.id, code: filePointer(entry),
    sourceKind: row.source.kind, source: row.source.ref, sourceRange: row.source.range,
    framesInclusive: row.source.framesInclusive ?? row.source.frames ?? null,
    composite: row.composite ?? null, variantOf: row.variantOf ?? null,
    liveMetadataMatchesCatalog: Object.entries(recipeMetadata).every(([key, value]) =>
      JSON.stringify(value) === JSON.stringify(row[key])),
    catalogPreview: row.preview,
    hasUiCatalogEntry: Boolean(row.ui),
    hasUiRecipe: hasUi,
    editProbes: Object.fromEntries(row.editable.map(field => [field, testEdit(entry, field, build)])),
    ...data,
    ui: uiPicture ? {
      ...sceneEvidence(uiPicture),
      editProbes: Object.fromEntries(row.editable.map(field => [field, testEdit(entry, field, buildUI, true)])),
    } : null,
  };
});
writeFileSync(outPath, JSON.stringify(rows, null, 2) + '\n');
const distinct = new Set(rows.filter(row => !row.composite && !row.variantOf).map(row => row.trackSignature));
console.log(JSON.stringify({catalogRows: catalog.entries.length, liveRows: rows.length,
  rootTrackSignatures: distinct.size, ui: rows.filter(row => row.ui).length}));
