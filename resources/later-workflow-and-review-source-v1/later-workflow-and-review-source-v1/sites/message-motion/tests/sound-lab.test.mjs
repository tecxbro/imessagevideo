import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {MEDIA_ORIGIN, FILM_IDS, validateSoundData, bridgeReply, RecreatedBridge, BlobSession, ExclusivePlayback, fetchMediaBlob, isMP4Bytes, formatTime, clampTime, playbackMessage, playbackGain, matchedPlaybackLevels, nextPlaybackLevel} from '../dist/sound-lab.js';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'https://message-studies.example/sound.html';
const records = JSON.parse(readFileSync(resolve(root, 'dist/sound-data.json'), 'utf8'));
const mp4 = () => new Uint8Array([0, 0, 0, 24, 102, 116, 121, 112, 105, 115, 111, 109, 0, 0, 0, 0]).buffer;
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return {promise, resolve, reject}; };

// Controller message transport only: no DOM, browser, renderer or network emulation.
function bridgeHarness(options = {}) {
  const sent = []; let activeFilm = FILM_IDS[0], removed = false, frameURL;
  const endpoint = {postMessage: (data, origin) => sent.push({data, origin})};
  const hostWindow = {addEventListener() {}, removeEventListener() {}};
  const bridge = new RecreatedBridge({hostWindow, createFrame: url => { frameURL = url; return {contentWindow: endpoint, remove: () => { removed = true; }}; }, currentFilm: () => activeFilm, ...options});
  const message = data => bridge.handle({origin: MEDIA_ORIGIN, source: endpoint, data});
  return {bridge, sent, endpoint, message, setFilm: film => { activeFilm = film; }, get frameURL() { return frameURL; }, get removed() { return removed; }};
}

test('the six real records retain descriptions and use GSAP picture paths for both sound modes', () => {
  const films = validateSoundData(records, base);
  assert.deepEqual(films.map(f => f.id), FILM_IDS);
  for (const film of films) {
    const original = records.find(f => f.id === film.id);
    assert.equal(film.description, original.description); assert.equal(film.audio_status, original.audio_status);
    assert.equal(new URL(film.reference_audio_video).origin, new URL(base).origin);
    assert.equal(new URL(film.recreated_video).pathname, `/audio-previews/${film.id}/recreated.mp4`);
    assert.ok(existsSync(resolve(root, 'dist', original.poster)));
    assert.equal(original.source_samples_reused, false);
  }
});
test('incomplete, duplicate, wrong-film and cross-origin metadata is rejected', () => {
  assert.throws(() => validateSoundData(records.slice(1), base), /six/);
  assert.throws(() => validateSoundData([records[0], records[0], ...records.slice(2)], base), /duplicate/);
  assert.throws(() => validateSoundData(records.map((f, i) => i ? f : {...f, reference_audio_video: 'https://elsewhere.example/a.mp4'}), base), /location/);
  assert.throws(() => validateSoundData(records.map((f, i) => i ? f : {...f, recreated_video: MEDIA_ORIGIN + '/audio-previews/02-danieltian/recreated.mp4'}), base), /path/);
  assert.throws(() => validateSoundData(records.map((f, i) => i ? f : {...f, poster: 'javascript:alert(1)'}), base), /location/);
});
test('optional stems and gains can be absent while the six-film comparison remains available', () => {
  const films = validateSoundData(records.map(f => ({...f, music_stem: null, sfx_stem: null, mix_audio: null})), base);
  assert.equal(films[0].mix_audio, null); assert.equal(playbackGain({}, 'reference'), 1); assert.equal(matchedPlaybackLevels({}), false);
});
test('bridge replies require both the exact origin and source, pending ID and current film', () => {
  const source = {}, pending = {id: 'sound-lab-1', film: FILM_IDS[0]};
  const context = {origin: MEDIA_ORIGIN, source, pending, currentFilm: FILM_IDS[0]};
  const event = {origin: MEDIA_ORIGIN, source, data: {type: 'loaded', id: pending.id, bytes: mp4()}};
  assert.equal(bridgeReply(event, context), event.data);
  for (const changed of [{origin: 'https://wrong.example'}, {source: {}}, {data: {...event.data, id: 'reference-old'}}, {data: {...event.data, film: FILM_IDS[1]}}, {data: {...event.data, variant: 'reference'}}]) assert.equal(bridgeReply({...event, ...changed}, context), null);
  assert.equal(bridgeReply(event, {...context, currentFilm: FILM_IDS[1]}), null);
  assert.equal(bridgeReply({origin: MEDIA_ORIGIN, data: {type: 'ready'}}, {...context, source: undefined}), null);
});
test('recreated loading explicitly selects its variant and transfers unchanged MP4 bytes only after ready', async () => {
  const h = bridgeHarness(); const pending = h.bridge.load(FILM_IDS[0], new AbortController().signal);
  assert.equal(h.frameURL, MEDIA_ORIGIN + '/bridge.html'); assert.equal(h.sent.length, 0);
  h.message({type: 'ready'}); assert.equal(h.sent.length, 1);
  const request = h.sent[0]; assert.equal(request.origin, MEDIA_ORIGIN); assert.equal(request.data.variant, 'recreated'); assert.match(request.data.id, /^sound-lab-recreated-/);
  h.message({type: 'ready'}); assert.equal(h.sent.length, 1);
  h.message({type: 'loaded', id: 'unknown-id', bytes: mp4()}); assert.equal(h.bridge.pending.size, 1);
  const bytes = mp4(); h.message({type: 'loaded', id: request.data.id, bytes});
  const blob = await pending; assert.deepEqual(await blob.arrayBuffer(), bytes); assert.equal(h.bridge.pending.size, 0); h.bridge.dispose();
});
test('bridge abort sends cancel and ignores late replies', async () => {
  const h = bridgeHarness(), controller = new AbortController(); const pending = h.bridge.load(FILM_IDS[0], controller.signal);
  h.message({type: 'ready'}); const id = h.sent[0].data.id;
  const rejected = assert.rejects(pending, {name: 'AbortError'}); controller.abort(); await rejected;
  assert.deepEqual(h.sent.at(-1).data, {type: 'cancel', id}); assert.equal(h.bridge.pending.size, 0);
  h.message({type: 'loaded', id, bytes: mp4()}); assert.equal(h.bridge.pending.size, 0); h.bridge.dispose();
});
test('bridge rejects invalid/oversized media, times out, and cleans every pending request on disposal', async () => {
  const h = bridgeHarness({maxBytes: 12}); const pending = h.bridge.load(FILM_IDS[0]); h.message({type: 'ready'});
  h.message({type: 'loaded', id: h.sent[0].data.id, bytes: mp4()}); await assert.rejects(pending, /valid MP4/); h.bridge.dispose();
  const slow = bridgeHarness({timeoutMs: 5}); await assert.rejects(slow.bridge.load(FILM_IDS[0]), /too long/); slow.bridge.dispose();
  const closing = bridgeHarness(); const open = assert.rejects(closing.bridge.load(FILM_IDS[0]), {name: 'AbortError'}); closing.bridge.dispose(); await open; assert.equal(closing.removed, true);
});
test('full same-origin media loading has no Range request and preserves exact container bytes', async () => {
  const bytes = mp4(); const controller = new AbortController(); let options;
  const blob = await fetchMediaBlob('https://message-studies.example/file.mp4', controller.signal, {fetchImpl: async (url, init) => { options = init; return new Response(bytes, {headers: {'content-type': 'application/octet-stream'}}); }});
  assert.equal(options.credentials, 'omit'); assert.equal(options.signal, controller.signal); assert.equal(options.headers, undefined); assert.deepEqual(await blob.arrayBuffer(), bytes);
});
test('HTML errors, truncated containers and oversized response streams cannot become playback blobs', async () => {
  await assert.rejects(fetchMediaBlob('/bad', undefined, {fetchImpl: async () => new Response('<html>', {headers: {'content-type': 'text/html'}})}), /media file/);
  await assert.rejects(fetchMediaBlob('/bad', undefined, {fetchImpl: async () => new Response(new Uint8Array([1, 2, 3]))}), /container/);
  let cancelled = false;
  const stream = new ReadableStream({start(c) { c.enqueue(new Uint8Array(40)); }, cancel() { cancelled = true; }});
  await assert.rejects(fetchMediaBlob('/big', undefined, {maxBytes: 20, fetchImpl: async () => new Response(stream)}), /too large/); assert.equal(cancelled, true);
  assert.equal(isMP4Bytes(new Uint8Array(mp4())), false); assert.equal(isMP4Bytes(mp4()), true);
});
test('a late previous load never creates a URL or replaces the latest selection', async () => {
  const a = deferred(), b = deferred(), ready = [], created = [], signals = [];
  const session = new BlobSession({load: (r, signal) => { signals.push(signal); return r.id === 'a' ? a.promise : b.promise; }, createURL: blob => { created.push(blob); return 'blob:test-' + created.length; }, revokeURL() {}, onReady: (url, r) => ready.push(r.id)});
  const first = session.start({id: 'a'}), second = session.start({id: 'b'}); assert.equal(signals[0].aborted, true);
  a.resolve(new Blob(['old'])); assert.equal(await first, false); assert.deepEqual(ready, []);
  b.resolve(new Blob(['new'])); assert.equal(await second, true); assert.deepEqual(ready, ['b']); assert.equal(created.length, 1); session.dispose();
});
test('replacement, cancellation and disposal revoke object URLs and stop pending work', async () => {
  const revoked = []; let count = 0; const waiting = deferred(); let pendingSignal;
  const session = new BlobSession({load: (r, signal) => { pendingSignal = signal; return r.wait ? waiting.promise : Promise.resolve(new Blob(['media'])); }, createURL: () => 'blob:' + ++count, revokeURL: url => revoked.push(url)});
  await session.start({}); const pending = session.start({wait: true}); assert.deepEqual(revoked, ['blob:1']);
  session.cancelPending(); assert.equal(pendingSignal.aborted, true); waiting.resolve(new Blob(['late'])); assert.equal(await pending, false); assert.equal(session.url, null);
  await session.start({}); session.dispose(); assert.deepEqual(revoked, ['blob:1', 'blob:2']); assert.equal(await session.start({}), false);
});
test('failed attachment releases its newly created Blob lease and reports an actionable error', async () => {
  const revoked = [], states = [];
  const session = new BlobSession({load: async () => new Blob(['bytes']), createURL: () => 'blob:bad', revokeURL: url => revoked.push(url), onReady() { throw new Error('attachment failed'); }, onState: phase => states.push(phase)});
  assert.equal(await session.start({}), false); assert.equal(session.url, null); assert.equal(session.loading, false); assert.deepEqual(revoked, ['blob:bad']); assert.equal(states.at(-1), 'error');
});
test('exclusive playback invalidates pending autoplay and stops every other audition', () => {
  const focus = new ExclusivePlayback(), stopped = [];
  for (const name of ['video', 'mix', 'music', 'sfx']) focus.register(name, () => stopped.push(name));
  const videoEpoch = focus.claim('video'); assert.deepEqual(stopped, ['mix', 'music', 'sfx']);
  stopped.length = 0; const musicEpoch = focus.claim('music'); assert.deepEqual(stopped, ['video', 'mix', 'sfx']); assert.equal(focus.owns('video', videoEpoch), false); assert.equal(focus.owns('music', musicEpoch), true);
  focus.stopAll(); assert.equal(focus.owns('music', musicEpoch), false);
});
test('matched playback attenuation preserves a manually changed base volume and mute-independent zero', () => {
  const film = {reference_gain: .6, recreated_gain: 1}; assert.equal(matchedPlaybackLevels(film), true);
  let level = nextPlaybackLevel({baseVolume: 1, gain: 1, volume: 1}, 1, playbackGain(film, 'reference')); assert.equal(level.volume, .6);
  level = nextPlaybackLevel(level, .3, playbackGain(film, 'recreated')); assert.ok(Math.abs(level.baseVolume - .5) < 1e-9); assert.ok(Math.abs(level.volume - .5) < 1e-9);
  level = nextPlaybackLevel(level, 0, .6); assert.equal(level.volume, 0); assert.equal(level.baseVolume, 0);
  let loud = nextPlaybackLevel({baseVolume: 1, gain: .6, volume: .6}, 1, 1); assert.equal(loud.volume, 1); assert.ok(loud.baseVolume > 1);
  loud = nextPlaybackLevel(loud, 1, .6); assert.equal(loud.volume, 1);
  assert.equal(playbackGain({reference_gain: 5}, 'reference'), 1);
});
test('seek/time display and native policy errors are explicit', () => {
  assert.equal(clampTime(10, 8), 8); assert.equal(clampTime(NaN, 8), 0); assert.equal(formatTime(65), '1:05'); assert.equal(formatTime(NaN), '0:00');
  assert.match(playbackMessage({name: 'NotAllowedError'}), /Press play/); assert.match(playbackMessage({name: 'NotSupportedError'}), /download/);
});
test('the page exposes one native inline video, three native audio controls and honest draft labels', () => {
  const html = readFileSync(resolve(root, 'dist/sound.html'), 'utf8'); const videos = html.match(/<video\b[^>]*>/g);
  assert.equal(videos.length, 1); assert.match(videos[0], /\bcontrols\b/); assert.match(videos[0], /\bplaysinline\b/); assert.doesNotMatch(videos[0], /\bautoplay\b/);
  assert.equal((html.match(/<audio\b[^>]*controls/g) || []).length, 3);
  assert.match(html, /No reference audio in this mix/); assert.match(html, /not identical reproductions/); assert.match(html, /role="status"/); assert.match(html, /sound-lab.js/);
});


test('UI-only metadata allows credited stock effects but rejects a wrong-film UI path or borrowed reference audio', () => {
  const rows=records.map(row=>({...row,library_samples_used:true,reference_samples_reused:false,ui_video:MEDIA_ORIGIN+'/audio-previews/'+row.id+'/ui.mp4',ui_gain:1}));
  assert.equal(validateSoundData(rows,base)[0].ui_video,rows[0].ui_video);
  const wrong=structuredClone(rows);wrong[0].ui_video=MEDIA_ORIGIN+'/audio-previews/02-danieltian/ui.mp4';assert.throws(()=>validateSoundData(wrong,base));
  const borrowed=structuredClone(rows);borrowed[0].reference_samples_reused=true;assert.throws(()=>validateSoundData(borrowed,base));
});
test('UI-only transport selects only its fixed variant and rejects a cross-variant response', async () => {
  const h=bridgeHarness();const pending=h.bridge.load(FILM_IDS[0],new AbortController().signal,'ui');h.message({type:'ready'});
  const request=h.sent[0].data;assert.equal(request.variant,'ui');assert.match(request.id,/^sound-lab-ui-/);
  h.message({type:'loaded',id:request.id,variant:'recreated',bytes:mp4()});assert.equal(h.bridge.pending.size,1);
  h.message({type:'loaded',id:request.id,variant:'ui',bytes:mp4()});await pending;h.bridge.dispose();
});
