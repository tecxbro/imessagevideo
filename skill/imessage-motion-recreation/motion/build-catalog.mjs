#!/usr/bin/env node
import {createHash} from 'node:crypto';
import {existsSync, readFileSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {entries, metadata} from './catalog.mjs';

const catalogURL = new URL('./catalog.json', import.meta.url);
const repo = fileURLToPath(new URL('../../../', import.meta.url));
const review = 'review/imv-v3/motion';
const json = filename => JSON.parse(readFileSync(filename, 'utf8'));
const observed = json(new URL('./observed.json', import.meta.url));
const samples = json(path.join(repo, review, 'samples/renderer-samples.json'));
const reuse = json(path.join(repo, review, 'reuse/index.json'));

const contentTypes = {
  heading:'text', copy:'text', reply:'text', title:'text', detail:'text', action:'text',
  photos:'array of local PNG, JPEG or WebP paths, relative to the content JSON',
  values:'array of 1–24 finite numbers; use the entry notes for meaning and bounds',
  direction:'left, right, up or down; the photo rail supports left/right only',
  swipes:'integer 1 or 2; requires at least one more photo than swipes',
};
const renderCommand = id => `node motion/cli.mjs render --id ${id} --method pillow --out /tmp/${id}.mp4`;

function capture(stem) {
  const preview = `${review}/${stem}.mp4`;
  const eventMap = `${review}/${stem}.events.json`;
  const timeline = json(path.join(repo,eventMap));
  const sha256 = createHash('sha256').update(readFileSync(path.join(repo,preview))).digest('hex');
  return {preview, sha256, eventMap, picture:timeline.picture,
    events:timeline.events.map(({id,kind,frame})=>({id,kind,frame}))};
}

const rows = entries.map(entry => {
  const assets = capture(entry.id);
  const renderers = [
    {method:'pillow', evidence:'full-preview', frames:assets.picture.frameCount},
    ...Object.entries(samples).flatMap(([method, ids]) => ids[entry.id] >= 2
      ? [{method, evidence:'retimed-nine-frame-probe', distinctFrames:ids[entry.id]}]
      : []),
  ];
  const ui = existsSync(path.join(repo,review,'ui',entry.id+'.mp4')) ? {
    ...capture(`ui/${entry.id}`),
    adapter:'Clone iMessage UI at 5e2ff5a',
    renderCommand:`${renderCommand(entry.id)} --ui`,
  } : undefined;
  return {...metadata(entry), ...assets, renderers, ui,
    editableFields:Object.fromEntries(entry.editable.map(field=>[field,contentTypes[field]??'see recipe'])),
    renderCommand:renderCommand(entry.id)};
});
const counts = {
  observedOnly:observed.length,
  playableEntries:rows.length,
  reusedEntries:new Set(reuse.map(row=>row.id)).size,
  distinctPlayableMotions:rows.filter(row=>!row.composite && !row.variantOf).length,
};
writeFileSync(catalogURL,JSON.stringify({
  version:1, counts, frameConvention:'Output event frame zero is the first decoded frame. Source ranges in seconds are half-open.',
  entries:rows, observedOnly:observed, independentReuse:reuse,
},null,2)+'\n');
console.log(JSON.stringify(counts));
