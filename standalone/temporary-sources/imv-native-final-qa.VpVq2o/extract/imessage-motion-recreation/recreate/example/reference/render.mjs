import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {linkSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname, join, resolve} from 'node:path';

const require = createRequire(new URL('../../../scripts/engines/package.json', import.meta.url));
const {chromium} = require('playwright');
const out = process.argv[2] && resolve(process.argv[2]);
if (!out) throw new Error('Usage: node reference/render.mjs OUT.mp4');

const fps = 30;
const frames = 120;
const cues = [
  {frame: 30, hz: 640, duration: 0.095},
  {frame: 56, hz: 460, duration: 0.125},
  {frame: 74, hz: 890, duration: 0.057},
  {frame: 89, hz: 560, duration: 0.13},
];

function originalWave(file) {
  const rate = 48000;
  const samples = frames * rate / fps;
  const wav = Buffer.alloc(44 + samples * 2);
  wav.write('RIFF', 0);
  wav.writeUInt32LE(wav.length - 8, 4);
  wav.write('WAVEfmt ', 8);
  wav.writeUInt32LE(16, 16);
  wav.writeUInt16LE(1, 20);
  wav.writeUInt16LE(1, 22);
  wav.writeUInt32LE(rate, 24);
  wav.writeUInt32LE(rate * 2, 28);
  wav.writeUInt16LE(2, 32);
  wav.writeUInt16LE(16, 34);
  wav.write('data', 36);
  wav.writeUInt32LE(samples * 2, 40);
  for (const {frame, hz, duration} of cues) {
    const first = frame * rate / fps;
    for (let offset = 0; offset < duration * rate; offset++) {
      const t = offset / rate;
      const envelope = Math.min(t / 0.004, 1) * (1 - t / duration) ** 3;
      const wave = 0.35 * envelope * (Math.sin(2 * Math.PI * hz * t) + 0.2 * Math.sin(2 * Math.PI * 2.2 * hz * t));
      wav.writeInt16LE(Math.round(wave * 32767), 44 + 2 * (first + offset));
    }
  }
  writeFileSync(file, wav);
}

mkdirSync(dirname(out), {recursive: true});
const temp = mkdtempSync(join(tmpdir(), 'train-reference-'));
const filename = frame => join(temp, `${String(frame).padStart(6, '0')}.png`);
try {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH ?? '/usr/bin/chromium',
    args: ['--no-sandbox'],
  });
  try {
    const page = await browser.newPage({viewport: {width: 640, height: 360}, deviceScaleFactor: 1});
    await page.setContent(readFileSync(new URL('./film.html', import.meta.url), 'utf8'));
    await page.evaluate(() => document.fonts.ready);
    let previous;
    let capture;
    for (let frame = 0; frame < frames; frame++) {
      const svg = await page.evaluate(frame => window.paint(frame), frame);
      if (svg !== previous) {
        capture = filename(frame);
        await page.screenshot({path: capture, animations: 'disabled'});
        previous = svg;
      } else {
        linkSync(capture, filename(frame));
      }
    }
  } finally {
    await browser.close();
  }
  const audio = join(temp, 'authored-cues.wav');
  originalWave(audio);
  const encode = spawnSync('ffmpeg', [
    '-hide_banner', '-loglevel', 'error', '-y', '-threads', '1', '-filter_threads', '1',
    '-framerate', String(fps), '-i', join(temp, '%06d.png'), '-i', audio, '-frames:v', String(frames),
    '-c:v', 'libx264', '-threads', '2', '-vf', 'scale=out_color_matrix=bt709',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-color_range', 'tv', '-crf', '16', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out,
  ], {stdio: 'inherit'});
  if (encode.error) throw encode.error;
  if (encode.status !== 0) throw new Error(`FFmpeg exit ${encode.status}`);
} finally {
  rmSync(temp, {recursive: true, force: true});
}
