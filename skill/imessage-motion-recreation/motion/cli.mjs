#!/usr/bin/env node
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import {byId, entries, metadata, methods} from './catalog.mjs';
import {buildMotion} from './scene.mjs';

const engines = fileURLToPath(new URL('../scripts/engines/', import.meta.url));
const usage = `node motion/cli.mjs list
node motion/cli.mjs select --brief "What the viewer should see"
node motion/cli.mjs info --id MOTION
node motion/cli.mjs scene --id MOTION --content CONTENT.json --out SCENE.json
node motion/cli.mjs render --id MOTION --out PREVIEW.mp4 [--method pillow]
Use --ids ID1,ID2 for a sequence. Use --brief in place of --id for selection.
Render also writes editable .scene.json and frame-addressed .events.json files.`;

function save(filename, value) {
  const absolute = path.resolve(filename);
  mkdirSync(path.dirname(absolute), {recursive: true});
  writeFileSync(absolute, JSON.stringify(value, null, 2) + '\n');
  return absolute;
}

function loadContent(filename) {
  if (!filename) return {};
  const absolute = path.resolve(filename);
  const data = JSON.parse(readFileSync(absolute, 'utf8'));
  if (Array.isArray(data?.photos)) {
    data.photos = data.photos.map(src => typeof src === 'string' ? path.resolve(path.dirname(absolute), src) : src);
  }
  return data;
}

async function choose(brief) {
  const {select} = await import('./select.mjs');
  return select(entries, brief);
}

function requireEntry(id) {
  const entry = byId.get(id);
  if (!entry) throw Error(`Unknown motion ID: ${id}`);
  return entry;
}

function sequence(parts) {
  if (parts.length === 1) return parts[0];
  const first = parts[0];
  let frames = 0;
  const layers = [];
  const events = [];
  const cues = [];
  for (const [index, part] of parts.entries()) {
    if (part.fps !== first.fps || part.width !== first.width || part.height !== first.height)
      throw Error('Sequence beats must share picture dimensions and frame rate');
    const groupId = `beat-${index + 1}`;
    const prefix = groupId + '.';
    const start = frames / first.fps;
    const beatFrames = part.timeline.picture.frameCount;
    const end = (frames + beatFrames) / first.fps;
    const offset = layer => {
      layer.id = prefix + layer.id;
      if (layer.start !== undefined) layer.start += start;
      if (layer.end !== undefined) layer.end += start;
      for (const track of Object.values(layer.keyframes ?? {}))
        for (const key of track) key.t += start;
      for (const child of layer.children ?? []) offset(child);
    };
    const background = {
      id: prefix + 'background', type: 'rect', x: 0, y: 0,
      width: part.width, height: part.height, fill: part.background,
    };
    for (const layer of part.layers) offset(layer);
    layers.push({id: groupId, type: 'group', start, end, children: [background, ...part.layers]});
    if (index && !part.timeline.events.some(event => event.frame === 0 && Object.hasOwn(event, 'uiState'))) {
      events.push({id: prefix + 'cut', kind: 'shot.cut', target: groupId,
        frame: frames, layerIds: [groupId], uiState: part.timeline.initialUI});
    }
    for (const event of part.timeline.events) {
      const remapped = {...event, id: prefix + event.id, frame: event.frame + frames};
      if (event.layerIds) remapped.layerIds = event.layerIds.map(id => prefix + id);
      events.push(remapped);
    }
    for (const cue of part.timeline.cues)
      cues.push({...cue, id: prefix + cue.id, eventId: prefix + cue.eventId});
    frames += beatFrames;
  }
  return {...first, duration: frames / first.fps, title: parts.map(part => part.title).join(' / '),
    source: {notes: parts.map(part => `${part.source.path} [${part.source.sourceStart}, ${part.source.sourceEnd})`).join(' then ')},
    layers, timeline: {...first.timeline, picture: {...first.timeline.picture, frameCount: frames}, events, cues},
  };
}

function render(scenePath, out, method) {
  if (!methods.includes(method)) throw Error(`Unknown method ${method}. Choose ${methods.join(', ')}`);
  const args = ['--scene', scenePath, '--out', out];
  let command = process.execPath;
  if (method === 'pillow') {
    command = process.env.MOTION_PYTHON ?? 'python3';
    args.unshift(path.join(engines, 'render_pillow.py'));
  } else if (method === 'motion-canvas') {
    args.unshift(path.join(engines, 'render_motion_canvas.mjs'));
  } else {
    args.unshift(path.join(engines, 'render.mjs'), '--method', method);
  }
  const result = spawnSync(command, args, {stdio: ['ignore', 'inherit', 'inherit']});
  if (result.error) throw result.error;
  if (result.status !== 0) throw Error(`${method} render failed: ${result.signal ?? result.status}`);
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  if (!command || command === '--help') { console.log(usage); return; }
  const {values: flags} = parseArgs({args, options: Object.fromEntries(
    ['id','ids','brief','content','out','method','fps','duration'].map(name => [name, {type:'string'}]),
  )});
  const print = value => console.log(JSON.stringify(value, null, 2));
  if (command === 'list') { print(entries.map(metadata)); return; }
  if (command === 'info') { print(metadata(requireEntry(flags.id))); return; }
  if (command === 'select') { print(await choose(flags.brief)); return; }
  if (!['scene', 'render'].includes(command)) throw Error(usage);
  if (!flags.out) throw Error('Supply --out');
  if ([flags.id, flags.ids, flags.brief].filter(Boolean).length !== 1)
    throw Error('Supply exactly one of --id, --ids or --brief');
  const recommendation = flags.brief ? await choose(flags.brief) : null;
  if (recommendation && !recommendation.matches.length)
    throw Error(`${recommendation.action}: ${recommendation.reason}`);
  const ids = recommendation?.matches ?? (flags.ids?.split(',').map(id => id.trim()) ?? [flags.id]);
  if (ids.length > 4) throw Error('Use up to four motions per sequence');
  const content = loadContent(flags.content);
  const settings = {
    fps: flags.fps === undefined ? undefined : Number(flags.fps),
    duration: flags.duration === undefined ? undefined : Number(flags.duration),
  };
  const scene = sequence(ids.map(id => buildMotion(requireEntry(id), content, settings)));
  const out = path.resolve(flags.out);
  if (path.extname(out) !== (command === 'scene' ? '.json' : '.mp4'))
    throw Error(command === 'scene' ? 'Scene output must end in .json' : 'Render output must end in .mp4');
  const stem = out.slice(0, -path.extname(out).length);
  const scenePath = save(command === 'scene' ? out : stem + '.scene.json', scene);
  const eventMap = save(stem + '.events.json', scene.timeline);
  if (command === 'render') render(scenePath, out, flags.method ?? 'pillow');
  print({ids, scene: scenePath, events: eventMap, ...(command === 'render' ? {video: out} : {}), ...(recommendation ? {recommendation} : {})});
}

try { await main(); } catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
