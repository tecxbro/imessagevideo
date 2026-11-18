import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { once } from 'node:events';
import { picture } from './picture.mjs';
import { edits, FPS, width, height } from './edit.mjs';

const [name = 'early', arg = `films/${name}.mp4`, frameArg] = process.argv.slice(2);
const edit = edits[name];
if (!edit) throw new Error('Usage: node render.mjs early|alternate|final [output.mp4] [snapshot-frame]');
const output = resolve(arg);
const draw = await picture(name);
await mkdir(dirname(output), { recursive: true });
if (frameArg !== undefined) {
  const frame = Number(frameArg);
  if (!Number.isInteger(frame) || frame < 0 || frame >= edit.end) throw new Error('Frame is outside edit');
  await writeFile(output, draw(frame).toBuffer('image/png'));
} else {
  const encoder = spawn('ffmpeg', [
    '-hide_banner', '-loglevel', 'error', '-y',
    '-f', 'rawvideo', '-pixel_format', 'rgba', '-video_size', `${width}x${height}`,
    '-framerate', String(FPS), '-i', 'pipe:0', '-an',
    '-c:v', 'libx264', '-crf', '17', '-preset', 'fast',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  const closed = once(encoder, 'close');
  for (let frame = 0; frame < edit.end; frame++) {
    if (!encoder.stdin.write(draw(frame).data())) await once(encoder.stdin, 'drain');
  }
  encoder.stdin.end();
  const [code] = await closed;
  if (code !== 0) throw new Error(`ffmpeg exited with status ${code}`);
  process.stdout.write(`${name}: ${edit.end} frames at ${FPS} fps → ${output}\n`);
}
