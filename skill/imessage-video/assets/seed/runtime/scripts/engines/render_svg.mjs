#!/usr/bin/env node
/** Render native-clock scene states to SVG and rasterize them before encoding. */
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {existsSync, mkdirSync, mkdtempSync, readFileSync, renameSync, rmSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import {esc, svgMarkup} from './common.mjs';

const types = {png:'image/png', jpg:'image/jpeg', jpeg:'image/jpeg', webp:'image/webp',
  ttf:'font/ttf', otf:'font/otf', woff:'font/woff', woff2:'font/woff2'};
const layerTypes = new Set(['group', 'rect', 'circle', 'path', 'text', 'image']);
const digest = buffer => createHash('sha256').update(buffer).digest('hex');
const cairoRasterizer = fileURLToPath(new URL('./rasterize_svg.py', import.meta.url));

function asset(src, directory) {
  const embedded = /^data:([^;,]+);base64,([\s\S]+)$/.exec(src);
  if (embedded) return {mime:embedded[1], bytes:Buffer.from(embedded[2], 'base64')};
  if (/^[a-z][a-z0-9+.-]*:/i.test(src)) throw Error('Supply a local or embedded static asset.');
  const mime = types[path.extname(src).slice(1).toLowerCase()];
  if (!mime) throw Error('Unsupported SVG-renderer asset: ' + src);
  return {mime, bytes:readFileSync(path.resolve(directory, src))};
}

function prepare(scene, directory, work) {
  function visit(layer) {
    if (!layerTypes.has(layer.type)) throw Error('Unsupported scene layer: ' + layer.type);
    if (layer.type === 'image') {
      const {mime, bytes} = asset(layer.src, directory);
      layer.src = 'data:' + mime + ';base64,' + bytes.toString('base64');
    }
    for (const child of layer.children ?? []) visit(child);
  }
  for (const layer of scene.layers) visit(layer);
  if (!scene.fonts?.length) return process.env;
  const fonts = path.join(work, 'fonts');
  mkdirSync(fonts);
  const aliases = [];
  for (const [i, font] of scene.fonts.entries()) {
    const {mime, bytes} = asset(font.src, directory);
    const ext = Object.keys(types).find(key => types[key] === mime && types[key].startsWith('font/'));
    if (!ext) throw Error('Expected an sfnt or web font.');
    const file = path.join(fonts, 'face-' + i + '.' + ext);
    writeFileSync(file, bytes);
    font.src = 'data:' + mime + ';base64,' + bytes.toString('base64');
    const identity = spawnSync('fc-scan', ['--format', '%{family[0]}', file], {encoding:'utf8'});
    if (identity.error || identity.status !== 0 || !identity.stdout) throw Error('Fontconfig could not identify ' + font.family);
    aliases.push('<alias binding="strong"><family>' + esc(font.family) + '</family><prefer><family>' +
      esc(identity.stdout) + '</family></prefer></alias>');
  }
  const conf = path.join(work, 'fonts.conf');
  const systemDirs = [...(process.env.FONTCONFIG_PATH ?? '').split(path.delimiter).filter(Boolean),
    '/etc/fonts', '/usr/local/etc/fonts', '/opt/homebrew/etc/fonts'];
  const systemConfig = [process.env.FONTCONFIG_FILE, ...systemDirs.map(dir => path.join(dir,'fonts.conf'))]
    .find(file => file && path.isAbsolute(file) && existsSync(file));
  writeFileSync(conf, '<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig>' +
    (systemConfig ? '<include>' + esc(systemConfig) + '</include>' : '') + '<dir>' + esc(fonts) + '</dir><cachedir>' +
    esc(path.join(work, 'font-cache')) + '</cachedir>' + aliases.join('') + '</fontconfig>');
  return {...process.env, FONTCONFIG_FILE:conf};
}

function clock(scene) {
  if (![scene.width,scene.height].every(x => Number.isSafeInteger(x) && x > 0)) throw Error('Invalid scene dimensions.');
  const picture = scene.timeline?.picture;
  if (picture) {
    const {fpsNum, fpsDen, frameCount} = picture;
    if (![fpsNum, fpsDen, frameCount].every(x => Number.isSafeInteger(x) && x > 0)) throw Error('Invalid declared picture clock.');
    return {count:frameCount, rate:fpsNum + '/' + fpsDen, seconds:n => n * fpsDen / fpsNum};
  }
  if (!(Number.isFinite(scene.fps) && scene.fps > 0 && Number.isFinite(scene.duration) && scene.duration > 0)) {
    throw Error('Supply a positive frame rate and duration.');
  }
  const count = Math.round(scene.fps * scene.duration);
  if (count < 1) throw Error('The scene must contain a frame.');
  return {count, rate:String(scene.fps), seconds:n => n / scene.fps};
}

function main() {
  const {values} = parseArgs({options:{scene:{type:'string'}, out:{type:'string'}, frame:{type:'string'}}});
  if (!values.scene || !values.out) throw Error('Use --scene scene.json --out movie.mp4 or --frame N --out frame.png.');
  const sceneFile = path.resolve(values.scene), out = path.resolve(values.out);
  const sceneBytes = readFileSync(sceneFile), scene = JSON.parse(sceneBytes);
  const timeline = clock(scene);
  const index = values.frame === undefined ? null : Number(values.frame);
  const ext = path.extname(out).toLowerCase();
  if (index !== null && (!Number.isSafeInteger(index) || index < 0 || index >= timeline.count)) throw Error('Invalid frame index.');
  if (index === null ? ext !== '.mp4' : !['.svg', '.png'].includes(ext)) throw Error('Specify .mp4 for a movie or .png/.svg for one frame.');
  mkdirSync(path.dirname(out), {recursive:true});
  const work = mkdtempSync(path.join(path.dirname(out), '.imv-svg-'));
  try {
    const env = prepare(scene, path.dirname(sceneFile), work);
    const frameFile = n => path.join(work, String(n).padStart(8,'0') + '.svg');
    const start = index ?? 0, end = index ?? timeline.count - 1;
    for (let frame = start; frame <= end; frame++) {
      const markup = svgMarkup(scene, timeline.seconds(frame), undefined, ext === '.svg')
        .replaceAll('<image href=', '<image xlink:href=');
      writeFileSync(frameFile(frame), markup);
    }
    if (ext === '.svg') {
      renameSync(frameFile(start), out);
      return;
    }
    const temporary = path.join(work, 'output' + ext);
    const decoders = spawnSync('ffmpeg', ['-hide_banner', '-decoders'], {encoding:'utf8'});
    if (decoders.error) throw decoders.error;
    if (decoders.status !== 0) throw Error('Could not inspect the installed FFmpeg decoders.');
    const directSVG = /\blibrsvg\b/.test(decoders.stdout);
    if (!directSVG) {
      const python = process.env.IMESSAGE_VIDEO_PYTHON || 'python3';
      const cairo = spawnSync(python, ['-I', cairoRasterizer, work, String(start), String(end)],
        {env, stdio:['ignore','ignore','inherit']});
      if (cairo.error) throw cairo.error;
      if (cairo.status !== 0) throw Error('SVG rasterization failed. Install CairoSVG and its Cairo system library.');
    }
    const input = path.join(work, directSVG ? '%08d.svg' : '%08d.png');
    const options = ['-hide_banner','-loglevel','error','-nostdin','-y','-framerate',timeline.rate,
      '-threads','1', ...(directSVG ? ['-c:v','librsvg'] : []),
      '-start_number',String(start),'-i',input,'-frames:v',String(end-start+1),'-an'];
    if (ext === '.png') options.push('-threads','1','-c:v','png','-pix_fmt','rgba');
    else options.push('-c:v','libx264','-threads','2','-filter_threads','1','-vf','scale=out_color_matrix=bt709',
      '-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-crf','16',
      '-pix_fmt',scene.width % 2 || scene.height % 2 ? 'yuv444p' : 'yuv420p','-movflags','+faststart');
    const ffmpeg = spawnSync('ffmpeg',[...options,temporary],{env,stdio:['ignore','ignore','inherit']});
    if (ffmpeg.error) throw ffmpeg.error;
    if (ffmpeg.status !== 0) throw Error('SVG frame sequence encoding failed.');
    renameSync(temporary, out);
    if (ext === '.mp4') {
      const implementation = [fileURLToPath(import.meta.url), fileURLToPath(new URL('./common.mjs',import.meta.url)), cairoRasterizer];
      const report = {method:'svg', rasterizer:directSVG ? 'librsvg' : 'cairosvg', sceneSha256:digest(sceneBytes), rendererFiles:Object.fromEntries(
        implementation.map(file => [path.basename(file),digest(readFileSync(file))])),
        width:scene.width,height:scene.height,frameRate:timeline.rate,frames:timeline.count,out};
      writeFileSync(out + '.render.json', JSON.stringify(report,null,2) + '\n');
      console.log(JSON.stringify(report));
    }
  } finally {
    rmSync(work,{recursive:true,force:true});
  }
}

try { main(); } catch (error) { console.error(error.message); process.exitCode = 1; }
