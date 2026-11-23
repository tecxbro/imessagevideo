#!/usr/bin/env node
import {createHash} from 'node:crypto';
import {copyFileSync, mkdirSync, mkdtempSync, readFileSync, statSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import {byId, describe, entries, methods} from './catalog.mjs';
import {describeMotionComponents} from './components.mjs';
import {buildMotion} from './scene.mjs';
import {composeScenes} from './sequence.mjs';
import {buildUiMotion, uiIds} from './ui-bridge.mjs';

const engines = fileURLToPath(new URL('../scripts/engines/', import.meta.url));
const repo = fileURLToPath(new URL('../../../', import.meta.url));
const python = process.env.MOTION_PYTHON ?? 'python3';
const usage = `node motion/cli.mjs list
node motion/cli.mjs select --brief "What the viewer should see"
node motion/cli.mjs info --id MOTION
node motion/cli.mjs preview --id MOTION [--out PREVIEW.mp4]
node motion/cli.mjs preview --id MOTION --frame INDEX --out FRAME.png
node motion/cli.mjs apply --id MOTION --project CONVERSATION.json --binding BINDING.json --out PROJECT_DIR
node motion/cli.mjs extract --source REFERENCE.mp4 --plan TRACKS.json --out REVIEW_DIR
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
    command = python;
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
    ...Object.fromEntries(['id','ids','brief','content','out','method','fps','duration','ui-root','frame',
      'project','binding','source','plan','measurements'].map(name => [name, {type:'string'}])),
    ui: {type:'boolean'},
  }});
  const print = value => console.log(JSON.stringify(value, null, 2));
  if (command === 'apply' || command === 'extract') {
    const binding = command === 'apply';
    const required = binding ? ['id', 'project', 'binding', 'out'] : ['source', 'plan', 'out'];
    if (!required.every(name => flags[name])) throw Error(usage);
    const script = fileURLToPath(new URL(binding ? './bind.py' : './extract.py', import.meta.url));
    const args = binding
      ? [requireEntry(flags.id).id, flags.project, '--binding', flags.binding]
      : [flags.source, '--plan', flags.plan, ...(flags.measurements ? ['--measurements', flags.measurements] : [])];
    const result = spawnSync(python, [script, ...args, '--out', flags.out], {stdio: 'inherit'});
    if (result.error) throw result.error;
    process.exitCode = result.status ?? 1;
    return;
  }
  if (command === 'list') { print(entries.map(describe)); return; }
  if (command === 'info') {
    const entry = requireEntry(flags.id);
    print({...describe(entry), components: describeMotionComponents(entry.id)});
    return;
  }
  if (command === 'preview') {
    const entry = describe(requireEntry(flags.id));
    const useUI = Boolean(flags.ui || flags['ui-root']);
    const variant = useUI ? entry.ui : entry;
    if (!variant?.preview) throw Error('No published preview for this motion and variant');
    let source = path.resolve(repo, variant.preview);
    const published = !flags['ui-root'] && statSync(source, {throwIfNoEntry: false})?.isFile() === true;
    let generated;
    if (!published) {
      const directory = mkdtempSync(path.join(tmpdir(), 'imv-motion-preview-'));
      const recipe = requireEntry(flags.id);
      const scene = useUI ? buildUiMotion(recipe, {}, {uiRoot: flags['ui-root']}) : buildMotion(recipe);
      generated = {
        scene: save(path.join(directory, 'preview.scene.json'), scene),
        events: save(path.join(directory, 'preview.events.json'), scene.timeline),
      };
      source = path.join(directory, 'preview.mp4');
      render(generated.scene, source, flags.method ?? 'pillow');
    }
    const digest = createHash('sha256').update(readFileSync(source)).digest('hex');
    if (published && digest !== variant.sha256) throw Error('Preview bytes differ from the published catalog hash');
    const evidence = {sha256: digest, provenance: published ? 'published' : 'local render', ...generated};
    if (flags.frame !== undefined) {
      const index = Number(flags.frame);
      if (!/^\d+$/.test(flags.frame) || !Number.isSafeInteger(index) || index >= variant.picture.frameCount)
        throw Error(`Frame must be in 0–${variant.picture.frameCount - 1}`);
      if (!flags.out || path.extname(flags.out) !== '.png') throw Error('Supply --out FRAME.png');
      const out = path.resolve(flags.out);
      mkdirSync(path.dirname(out), {recursive: true});
      const extractor = spawnSync('ffmpeg', ['-v', 'error', '-xerror', '-nostdin', '-n', '-i', source, '-an',
        '-vf', `select=eq(n\\,${index})`, '-frames:v', '1', '-threads', '1', '-update', '1', out],
      {encoding: 'utf8'});
      if (extractor.error) throw extractor.error;
      if (extractor.status !== 0 || !statSync(out, {throwIfNoEntry: false})?.isFile())
        throw Error(extractor.stderr?.trim() || 'Could not decode the selected frame');
      print({id: entry.id, preview: source, ...evidence, frame: index, image: out});
      return;
    }
    const out = flags.out ? path.resolve(flags.out) : source;
    if (out !== source) {
      if (path.extname(out) !== '.mp4') throw Error('Preview output must end in .mp4');
      mkdirSync(path.dirname(out), {recursive: true});
      copyFileSync(source, out);
    }
    print({id: entry.id, preview: out, ...evidence});
    return;
  }
  if (command === 'select') {
    const result = await choose(flags.brief);
    const matches = result.matches.map(id => {
      const {title, fits, avoid, moves, fixed, notice, implementation, preview, renderCommand} = describe(requireEntry(id));
      return {id, title, fits, avoid, moves, fixed, notice, implementation, preview, renderCommand,
        components: describeMotionComponents(id).production};
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
  const unsupported = useUI ? ids.filter(id => !uiIds.includes(id)) : [];
  if (unsupported.length)
    throw Error(`No Messages adapter variant for ${unsupported.join(', ')}. Available variants: ${uiIds.join(', ')}`);
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
