#!/usr/bin/env node
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import {byId, describe, entries, methods} from './catalog.mjs';
import {buildMotion} from './scene.mjs';
import {composeScenes} from './sequence.mjs';
import {buildUiMotion, uiIds} from './ui-bridge.mjs';

const engines = fileURLToPath(new URL('../scripts/engines/', import.meta.url));
const usage = `node motion/cli.mjs list
node motion/cli.mjs select --brief "What the viewer should see"
node motion/cli.mjs info --id MOTION
node motion/cli.mjs scene --id MOTION --content CONTENT.json --out SCENE.json
node motion/cli.mjs render --id MOTION --out PREVIEW.mp4 [--method pillow]
Use --ui for a Clone iMessage UI variant. Use --ui-root to point to a separate checkout.
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
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw Error('Content must be a JSON object');
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
  const {values: flags} = parseArgs({args, options: {
    ...Object.fromEntries(['id','ids','brief','content','out','method','fps','duration','ui-root'].map(name => [name, {type:'string'}])),
    ui: {type:'boolean'},
  }});
  const print = value => console.log(JSON.stringify(value, null, 2));
  if (command === 'list') { print(entries.map(describe)); return; }
  if (command === 'info') { print(describe(requireEntry(flags.id))); return; }
  if (command === 'select') {
    const result = await choose(flags.brief);
    const matches = result.matches.map(id => {
      const {title, moves, fixed, notice, preview, renderCommand} = describe(requireEntry(id));
      return {id, title, moves, fixed, notice, preview, renderCommand};
    });
    print({...result, entries:matches});
    return;
  }
  if (!['scene', 'render'].includes(command)) throw Error(usage);
  if (!flags.out) throw Error('Supply --out');
  if ([flags.id, flags.ids, flags.brief].filter(Boolean).length !== 1)
    throw Error('Supply exactly one of --id, --ids or --brief');
  const recommendation = flags.brief ? await choose(flags.brief) : null;
  if (recommendation && !recommendation.matches.length)
    throw Error(`${recommendation.action}: ${recommendation.reason}`);
  const ids = recommendation?.matches ?? (flags.ids?.split(',').map(id => id.trim()) ?? [flags.id]);
  if (ids.length > 4) throw Error('Use up to four motions per sequence');
  const content = {...recommendation?.content, ...loadContent(flags.content)};
  const settings = {
    fps: flags.fps === undefined ? undefined : Number(flags.fps),
    duration: flags.duration === undefined ? undefined : Number(flags.duration),
  };
  const beats = recommendation?.sequence?.length
    ? recommendation.sequence.flatMap(beat => beat.action === 'hold'
      ? [null]
      : beat.matches.map(id => ({id, content:beat.content})))
    : ids.map(id => ({id}));
  if (beats.length > 4) throw Error('Use up to four beats per sequence');
  const useUI = Boolean(flags.ui || flags['ui-root']);
  if (useUI && !beats.some(beat => uiIds.includes(beat?.id)))
    throw Error(`Clone iMessage UI covers these motions: ${uiIds.join(', ')}`);
  const scene = composeScenes(beats.map(beat => {
    if (!beat) return null;
    const entry = requireEntry(beat.id);
    const data = {...beat.content, ...content};
    return useUI && uiIds.includes(entry.id)
      ? buildUiMotion(entry, data, {...settings, uiRoot:flags['ui-root']})
      : buildMotion(entry, data, settings);
  }));
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
