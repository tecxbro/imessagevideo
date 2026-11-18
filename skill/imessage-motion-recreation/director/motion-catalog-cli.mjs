#!/usr/bin/env node
import {createHash} from 'node:crypto';
import {createReadStream, mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {dirname, extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import {buildCatalogScene, describeMotion, getMotion, searchMotions} from './motion-catalog.mjs';

const usage = `search BRIEF
show ID
scene ID [--config options.json] --out scene.json
source ID --out reference.mp4`;
const json = value => JSON.stringify(value, null, 2)+'\n';

async function main(args) {
  const [command, ...rest] = args;
  if (!command || command === '--help') {
    console.log(usage);
    return;
  }
  if (command === 'search') {
    if (!rest.join(' ').trim()) throw Error('Supply a motion brief');
    console.log(json(searchMotions(rest.join(' '))).trimEnd());
    return;
  }

  const {values, positionals} = parseArgs({
    args: rest, allowPositionals: true,
    options:{out:{type:'string'}, config:{type:'string'}},
  });
  if (positionals.length !== 1) throw Error('Supply one motion ID');
  const [id] = positionals;
  const description = describeMotion(getMotion(id));
  if (command === 'show' && !values.out && !values.config) {
    console.log(json(description).trimEnd());
  } else if (command === 'scene' && extname(values.out ?? '') === '.json') {
    const config = values.config ? JSON.parse(readFileSync(values.config, 'utf8')) : {};
    const scene = buildCatalogScene(id, config);
    mkdirSync(dirname(values.out), {recursive:true});
    writeFileSync(values.out, json(scene), {flag:'wx'});
  } else if (command === 'source' && extname(values.out ?? '') === '.mp4' && !values.config) {
    if (!description.source) throw Error(description.avoid);
    const {file, frames:[first,last], sha256} = description.source;
    const filePath = fileURLToPath(new URL('../../../'+file, import.meta.url));
    const hash = createHash('sha256');
    for await (const chunk of createReadStream(filePath)) hash.update(chunk);
    if (hash.digest('hex') !== sha256) throw Error('Local film does not match the catalog source SHA-256');
    mkdirSync(dirname(values.out), {recursive:true});
    const result = spawnSync('ffmpeg', [
      '-nostdin', '-n', '-v', 'error', '-i', filePath, '-map', '0:v:0', '-an',
      '-vf', `trim=start_frame=${first}:end_frame=${last+1},setpts=PTS-STARTPTS`,
      '-fps_mode', 'passthrough', '-c:v', 'libx264', '-crf', '16',
      '-pix_fmt', 'yuv420p', '-movflags', '+faststart', values.out,
    ], {stdio:'inherit'});
    if (result.error) throw result.error;
    if (result.status !== 0) throw Error('FFmpeg could not write the source clip');
  } else {
    throw Error(usage);
  }
}

main(process.argv.slice(2)).catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
