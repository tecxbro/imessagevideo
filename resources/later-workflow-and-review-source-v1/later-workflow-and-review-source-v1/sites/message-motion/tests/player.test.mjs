import {readFileSync, existsSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sandbox = {};
vm.runInNewContext(readFileSync(resolve(root, 'dist/player-core.js'), 'utf8'), sandbox);
const {sourceTime, clampTime, formatTime, validateFilm, playbackMessage} = sandbox.MotionReview;
const films = JSON.parse(readFileSync(resolve(root, 'dist/videos.json'), 'utf8'));
const rene = films.find(f => f.id === '06-gallery');
test('normal films keep source and recreation aligned through the final frame', () => {
  for (const film of films.filter(f => !f.segments.length)) for (const time of [0, .033333, 10, film.duration - .033333, film.duration]) assert.equal(sourceTime(time, film.segments), time);
});
test('Rene jumps the excluded live action at the exact cut and keeps the rest aligned', () => {
  const cut = 34.96666666666667;
  assert.ok(Math.abs(sourceTime(cut - 1 / 30, rene.segments) - (cut - 1 / 30)) < 1e-10);
  assert.equal(sourceTime(cut, rene.segments), 41);
  assert.ok(Math.abs(sourceTime(cut + 1 / 30, rene.segments) - (41 + 1 / 30)) < 1e-10);
  assert.ok(Math.abs(sourceTime(rene.duration - 1 / 30, rene.segments) - (rene.duration - 1 / 30 + 181 / 30)) < 1e-8);
  assert.ok(Math.abs(sourceTime(1000, rene.segments) - (41 + 14.466666666666667)) < 1e-8);
});
test('invalid and out-of-range seeks are clamped', () => {
  assert.equal(clampTime(-1, 50), 0); assert.equal(clampTime(Infinity, 50), 0); assert.equal(clampTime('bad', 50), 0); assert.equal(clampTime(80, 50), 50);
  assert.equal(sourceTime(-1, rene.segments), 0);
});
test('all methods and gallery paths resolve, with six original URLs on the companion origin', () => {
  assert.equal(films.length, 6);
  const urls = [];
  for (const film of films) {
    validateFilm(film);
    for (const path of [film.source, film.poster, ...Object.values(film.methods)]) {
      if (path.startsWith('https://')) { const u=new URL(path);assert.equal(u.origin,'https://message-motion-originals.orchidhq.chatgpt.site');assert.ok(u.pathname.endsWith('/source.mp4')); } else { assert.ok(!path.includes('..') && !path.startsWith('/') && !path.includes('://'), path);assert.ok(existsSync(resolve(root, 'dist', path)), path); } urls.push(path);
    }
  }
  assert.equal(urls.length, 42); assert.equal(new Set(urls).size, 42);
});
test('incomplete datasets fail visibly instead of creating broken method buttons', () => {
  assert.throws(() => validateFilm({...films[0], methods:{gsap:'x.mp4'}}), /Missing/);
});
test('browser policy rejection and missing-media errors produce actionable messages', () => {
  assert.match(playbackMessage({name:'NotAllowedError'}), /tap/);
  assert.match(playbackMessage({code:2}), /connection/);
  assert.match(playbackMessage({code:3}), /decode/);
  assert.match(playbackMessage({code:4}), /MP4/);
});
test('time display is stable for loading, negative, and minute-long films', () => {
  assert.equal(formatTime(NaN), '0:00');assert.equal(formatTime(-10), '0:00');assert.equal(formatTime(49.433), '0:49');assert.equal(formatTime(65), '1:05');
});
test('both media elements support native controls and inline playback, with no page-load autoplay', () => {
  const html = readFileSync(resolve(root, 'dist/index.html'), 'utf8');
  const videos = html.match(/<video\b[^>]*>/g);
  assert.equal(videos.length, 2);
  for (const video of videos) { assert.match(video, /\bcontrols\b/);assert.match(video, /\bplaysinline\b/);assert.ok(!/\bautoplay\b/.test(video)); }
  assert.ok(!html.includes('__VIDEO_DATA__'));
  assert.match(html, /role="status"/);
});
