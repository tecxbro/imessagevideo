export const MEDIA_ORIGIN = 'https://message-motion-originals.orchidhq.chatgpt.site';
export const FILM_IDS = Object.freeze(['01-photonhq', '02-danieltian', '03-photon-mini', '04-poke', '05-linq', '06-gallery']);
const VIDEO_LIMIT = 128 * 1024 * 1024;
const AUDIO_LIMIT = 32 * 1024 * 1024;
let messageSequence = 0;

export function formatTime(value) {
  const seconds = Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}
export function clampTime(value, duration) {
  return Number.isFinite(value) ? Math.max(0, Math.min(value, Number.isFinite(duration) ? Math.max(0, duration) : 0)) : 0;
}
export function abortError() { return new DOMException('This load was cancelled.', 'AbortError'); }
export function playbackMessage(error) {
  return error?.name === 'NotAllowedError' ? 'Ready. Press play to hear this soundtrack.' : 'Playback could not start. Try the native play control, or download the file.';
}
function validGain(value) { return Number.isFinite(value) && value >= 0 && value <= 1; }
export function playbackGain(film, mode) {
  const value = mode === 'ui' ? film.ui_gain : mode === 'reference' ? film.reference_gain : film.recreated_gain;
  return validGain(value) ? value : 1;
}
export function matchedPlaybackLevels(film) { return validGain(film.reference_gain) && validGain(film.recreated_gain); }
export function nextPlaybackLevel(previous, observedVolume, gain) {
  const volume = Math.max(0, Math.min(1, Number.isFinite(observedVolume) ? observedVolume : 1));
  let baseVolume = Number.isFinite(previous.baseVolume) ? Math.max(0, previous.baseVolume) : 1;
  if (Math.abs(volume - previous.volume) > .0001) baseVolume = previous.gain > 0 ? volume / previous.gain : volume;
  const nextGain = validGain(gain) ? gain : 1;
  return {baseVolume, gain: nextGain, volume: Math.max(0, Math.min(1, baseVolume * nextGain))};
}
function assetURL(value, base, allowedOrigins) {
  if (typeof value !== 'string' || !value.trim()) throw new Error('Missing media path.');
  const url = new URL(value, base);
  if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password || !allowedOrigins.includes(url.origin)) throw new Error('Unexpected media location.');
  return url;
}
export function validateSoundData(input, baseURL) {
  const records = Array.isArray(input) ? input : input?.films;
  if (!Array.isArray(records) || records.length !== 6) throw new Error('The sound collection needs six films.');
  const base = new URL(baseURL), seen = new Set();
  const films = records.map(record => {
    if (!record || !FILM_IDS.includes(record.id) || seen.has(record.id)) throw new Error('Unknown or duplicate film.');
    seen.add(record.id);
    if (typeof record.title !== 'string' || !record.title.trim() || !Number.isFinite(record.duration) || record.duration <= 0 || record.duration > 3600) throw new Error('Incomplete film metadata.');
    if (record.source_samples_reused === true || record.reference_samples_reused === true) throw new Error('This collection requires newly produced mixes without reference samples.');
    const reference = assetURL(record.reference_audio_video, base, [base.origin]);
    if (!reference.pathname.endsWith(`/deliverables/${record.id}/gsap.mp4`)) throw new Error('Reference sound must use this film’s GSAP recreation.');
    const recreated = assetURL(record.recreated_video, base, [MEDIA_ORIGIN]);
    if (recreated.pathname !== `/audio-previews/${record.id}/recreated.mp4`) throw new Error('Unexpected recreated preview path.');
    const ui = record.ui_video ? assetURL(record.ui_video, base, [MEDIA_ORIGIN]) : null;
    if (ui && ui.pathname !== `/audio-previews/${record.id}/ui.mp4`) throw new Error('Unexpected UI preview path.');
    const poster = assetURL(record.poster, base, [base.origin]);
    const result = {...record, title: record.title.trim(), poster: poster.href, reference_audio_video: reference.href, recreated_video: recreated.href, ui_video: ui?.href || null};
    for (const field of ['mix_audio', 'music_stem', 'sfx_stem']) {
      result[field] = record[field] ? assetURL(record[field], base, [base.origin, MEDIA_ORIGIN]).href : null;
    }
    return Object.freeze(result);
  });
  return FILM_IDS.map(id => films.find(film => film.id === id));
}
export function isMP4Bytes(bytes) {
  if (!(bytes instanceof ArrayBuffer) || bytes.byteLength < 12) return false;
  const header = new Uint8Array(bytes, 4, 4);
  return String.fromCharCode(...header) === 'ftyp';
}
export function bridgeReply(event, {origin, source, pending, currentFilm}) {
  if (!source || event.origin !== origin || event.source !== source || !event.data || typeof event.data !== 'object') return null;
  const data = event.data;
  if (data.type === 'ready') return data;
  if (!pending || data.id !== pending.id || pending.film !== currentFilm || pending.signal?.aborted) return null;
  if (data.film !== undefined && data.film !== pending.film) return null;
  if (data.variant !== undefined && data.variant !== (pending.variant || 'recreated')) return null;
  return data.type === 'loaded' || data.type === 'error' ? data : null;
}

export class RecreatedBridge {
  constructor({hostWindow, createFrame, currentFilm, timeoutMs = 120000, maxBytes = VIDEO_LIMIT}) {
    this.host = hostWindow; this.createFrame = createFrame; this.currentFilm = currentFilm;
    this.timeoutMs = timeoutMs; this.maxBytes = maxBytes; this.pending = new Map(); this.frame = null; this.ready = false; this.disposed = false;
    this.receive = event => this.handle(event);
    this.host.addEventListener('message', this.receive);
  }
  ensureFrame() { if (!this.frame) this.frame = this.createFrame(MEDIA_ORIGIN + '/bridge.html'); }
  send(item) {
    if (!this.ready || item.sent || !this.pending.has(item.id)) return;
    if (item.film !== this.currentFilm()) { this.finish(item.id, abortError(), true); return; }
    item.sent = true;
    this.frame.contentWindow.postMessage({type: 'load', id: item.id, film: item.film, variant: item.variant}, MEDIA_ORIGIN);
  }
  finish(id, value, failed = false, cancel = false) {
    const item = this.pending.get(id);
    if (!item) return;
    this.pending.delete(id); clearTimeout(item.timer);
    item.signal?.removeEventListener('abort', item.abort);
    if (cancel && item.sent) this.frame?.contentWindow?.postMessage({type: 'cancel', id}, MEDIA_ORIGIN);
    if (failed) item.reject(value); else item.resolve(value);
  }
  load(film, signal, variant = 'recreated') {
    if (!['recreated','ui'].includes(variant)) return Promise.reject(new Error('Unexpected sound variant.'));
    if (this.disposed || !FILM_IDS.includes(film) || film !== this.currentFilm() || signal?.aborted) return Promise.reject(abortError());
    return new Promise((resolve, reject) => {
      const id = `sound-lab-${variant}-${Date.now()}-${++messageSequence}`;
      const item = {id, film, variant, signal, resolve, reject, sent: false};
      item.abort = () => this.finish(id, abortError(), true, true);
      item.timer = setTimeout(() => this.finish(id, new Error('The soundtrack took too long to load.'), true, true), this.timeoutMs);
      this.pending.set(id, item); signal?.addEventListener('abort', item.abort, {once: true});
      try { this.ensureFrame(); this.send(item); } catch (error) { this.finish(id, error, true); }
    });
  }
  handle(event) {
    const item = this.pending.get(event.data?.id);
    const data = bridgeReply(event, {origin: MEDIA_ORIGIN, source: this.frame?.contentWindow, pending: item, currentFilm: this.currentFilm()});
    if (!data) return;
    if (data.type === 'ready') { this.ready = true; for (const pending of [...this.pending.values()]) this.send(pending); return; }
    if (data.type === 'error') { this.finish(item.id, new Error('This soundtrack could not be loaded.'), true); return; }
    if (!(data.bytes instanceof ArrayBuffer) || data.bytes.byteLength > this.maxBytes || !isMP4Bytes(data.bytes)) {
      this.finish(item.id, new Error('The preview did not contain a valid MP4 file.'), true); return;
    }
    this.finish(item.id, new Blob([data.bytes], {type: 'video/mp4'}));
  }
  dispose() {
    if (this.disposed) return;
    this.disposed = true;
    for (const id of [...this.pending.keys()]) this.finish(id, abortError(), true, true);
    this.host.removeEventListener('message', this.receive); this.frame?.remove(); this.frame = null; this.ready = false;
  }
}

export async function fetchMediaBlob(url, signal, {kind = 'video', fetchImpl = globalThis.fetch, maxBytes = kind === 'audio' ? AUDIO_LIMIT : VIDEO_LIMIT} = {}) {
  const response = await fetchImpl(url, {signal, credentials: 'omit'});
  if (!response.ok) throw new Error('This file is not available yet.');
  const type = response.headers.get('content-type') || '';
  if (type.includes('text/') || type.includes('json')) throw new Error('The server did not return a media file.');
  const size = Number(response.headers.get('content-length'));
  if (Number.isFinite(size) && size > maxBytes) throw new Error('The media file is too large.');
  const parts = []; let total = 0;
  if (response.body?.getReader) {
    const reader = response.body.getReader();
    try {
      while (true) {
        const {done, value} = await reader.read(); if (done) break;
        if (signal?.aborted) throw abortError();
        total += value.byteLength;
        if (total > maxBytes) throw new Error('The media file is too large.');
        parts.push(value);
      }
    } catch (error) { await reader.cancel().catch(() => {}); throw error; }
    finally { reader.releaseLock(); }
  } else { const bytes = await response.arrayBuffer(); total = bytes.byteLength; parts.push(bytes); }
  if (signal?.aborted) throw abortError();
  if (!total || total > maxBytes) throw new Error('The media file is empty or too large.');
  const blob = new Blob(parts, {type: kind === 'audio' ? 'audio/mp4' : 'video/mp4'});
  if (!isMP4Bytes(await blob.slice(0, 16).arrayBuffer())) throw new Error('The file is not a playable MP4/M4A container.');
  return blob;
}

export class BlobSession {
  constructor({load, onReady = () => {}, onClear = () => {}, onState = () => {}, createURL = blob => URL.createObjectURL(blob), revokeURL = url => URL.revokeObjectURL(url)}) {
    this.load = load; this.onReady = onReady; this.onClear = onClear; this.onState = onState; this.createURL = createURL; this.revokeURL = revokeURL;
    this.generation = 0; this.url = null; this.controller = null; this.loading = false; this.disposed = false;
  }
  async start(request) {
    if (this.disposed) return false;
    this.reset(false); const generation = ++this.generation;
    this.controller = new AbortController(); const signal = this.controller.signal; this.loading = true; this.onState('loading', null, request);
    try {
      const blob = await this.load(request, signal);
      if (signal.aborted || generation !== this.generation || this.disposed) return false;
      if (!(blob instanceof Blob) || !blob.size) throw new Error('Empty media file.');
      this.url = this.createURL(blob); this.loading = false; this.controller = null;
      this.onReady(this.url, request);
      if (generation !== this.generation || this.disposed) return false;
      this.onState('ready', null, request); return true;
    } catch (error) {
      if (generation !== this.generation || this.disposed) return false;
      this.loading = false; this.controller = null;
      if (this.url) { this.onClear(); this.revokeURL(this.url); this.url = null; }
      this.onState('error', error, request); return false;
    }
  }
  cancelPending() {
    if (!this.loading) return;
    ++this.generation; this.controller?.abort(); this.controller = null; this.loading = false;
    this.onState(this.url ? 'ready' : 'idle');
  }
  reset(notify = true) {
    ++this.generation; this.controller?.abort(); this.controller = null; this.loading = false;
    this.onClear(); if (this.url) this.revokeURL(this.url); this.url = null;
    if (notify) this.onState('idle');
  }
  dispose() { this.disposed = true; this.reset(); }
}

export class ExclusivePlayback {
  constructor() { this.players = new Map(); this.active = null; this.epoch = 0; }
  register(name, stop) { this.players.set(name, stop); }
  claim(name) { this.active = name; const epoch = ++this.epoch; for (const [other, stop] of this.players) if (other !== name) stop(); return epoch; }
  owns(name, epoch) { return this.active === name && this.epoch === epoch; }
  stopAll() { this.active = null; ++this.epoch; for (const stop of this.players.values()) stop(); }
}

function startSoundLab(document, host) {
  const $ = id => document.getElementById(id);
  const video = $('sound-video'), selector = $('film-selector'), status = $('sound-status');
  const focus = new ExclusivePlayback();
  const state = {films: [], film: null, mode: 'ui', request: null, preparing: false, pendingTime: 0, pendingPlay: false, timer: null, metadataHandler: null, level: {baseVolume: video.volume, gain: 1, volume: video.volume}};
  let bridge, dataAbort, suspendedTime = 0;
  const makeBridge = () => new RecreatedBridge({hostWindow: host, currentFilm: () => state.film?.id, createFrame: src => {
    const frame = document.createElement('iframe'); frame.hidden = true; frame.title = 'Recreated soundtrack media loader'; frame.src = src; document.body.append(frame); return frame;
  }});
  bridge = makeBridge();
  const element = (tag, className, text) => { const node = document.createElement(tag); if (className) node.className = className; if (text) node.textContent = text; return node; };
  function setStatus(text, error = false) { status.textContent = text; status.classList.toggle('error', error); }
  function busy(value) { $('sound-video-frame').setAttribute('aria-busy', String(value)); $('video-loading').hidden = !value; }
  function updateTime() { $('sound-time').textContent = `${formatTime(state.preparing ? state.pendingTime : video.currentTime)} / ${formatTime(state.film?.duration)}`; }
  function clearVideo() {
    clearTimeout(state.timer); video.pause();
    if (state.metadataHandler) video.removeEventListener('loadedmetadata', state.metadataHandler);
    state.metadataHandler = null; video.removeAttribute('src'); video.load();
    $('download-sound-video').removeAttribute('href'); $('download-sound-video').setAttribute('aria-disabled', 'true'); $('download-sound-video').tabIndex = -1;
  }
  function currentRequest(request) { return state.request === request && state.film?.id === request.film && state.mode === request.mode; }
  function tryPlay(media, isCurrent, note) {
    try { const attempt = media.play(); if (attempt?.catch) attempt.catch(error => { if (isCurrent() && error?.name !== 'AbortError') note(playbackMessage(error)); }); }
    catch (error) { if (isCurrent() && error?.name !== 'AbortError') note(playbackMessage(error)); }
  }
  const videoSession = new BlobSession({
    load: (request, signal) => request.mode === 'reference' ? fetchMediaBlob(request.url, signal) : bridge.load(request.film, signal, request.mode === 'ui' ? 'ui' : 'recreated'),
    onClear: clearVideo,
    onReady: (url, request) => {
      if (!currentRequest(request)) return;
      state.metadataHandler = () => {
        if (!currentRequest(request) || videoSession.url !== url) return;
        state.preparing = false; clearTimeout(state.timer); busy(false);
        video.currentTime = clampTime(request.time, video.duration); updateTime(); setStatus('Ready when you are. Press play.');
        if (request.autoplay && focus.owns('video', request.focusEpoch)) tryPlay(video, () => currentRequest(request), setStatus);
      };
      video.addEventListener('loadedmetadata', state.metadataHandler, {once: true}); video.src = url; video.load();
      const download = $('download-sound-video'); download.href = url; download.download = `${request.film}-${request.mode}-sound.mp4`; download.removeAttribute('aria-disabled'); download.tabIndex = 0;
    },
    onState: (phase, error, request) => {
      if (request && !currentRequest(request)) return;
      if (phase === 'loading') { state.preparing = true; busy(true); setStatus('Preparing this soundtrack…'); $('retry-video').hidden = true; $('open-video-file').hidden = true; }
      if (phase === 'error') { state.preparing = false; clearTimeout(state.timer); busy(false); setStatus('This soundtrack could not finish loading. Try again, or open the MP4 separately.', true); $('retry-video').hidden = false; $('open-video-file').hidden = false; }
    }
  });
  focus.register('video', () => { video.pause(); state.pendingPlay = false; });
  const stemFields = {mix: 'mix_audio', music: 'music_stem', sfx: 'sfx_stem'};
  const stems = [...document.querySelectorAll('[data-stem]')].map(card => {
    const key = card.dataset.stem, media = card.querySelector('audio'), button = card.querySelector('[data-stem-listen]'), note = card.querySelector('.sound-stem-status'), download = card.querySelector('[data-stem-download]');
    const originalLabel = button.textContent; const item = {key, card, media, button, note, download, url: null, session: null};
    const message = (text, error = false) => { note.textContent = text; note.classList.toggle('error', error); };
    item.session = new BlobSession({load: (request, signal) => fetchMediaBlob(request.url, signal, {kind: 'audio'}),
      onClear: () => { media.pause(); media.removeAttribute('src'); media.load(); media.hidden = true; },
      onReady: (url, request) => {
        media.src = url; media.load(); media.hidden = false; button.hidden = true; message('');
        if (focus.owns(key, request.focusEpoch) && request.film === state.film?.id) tryPlay(media, () => request.film === state.film?.id && item.session.url === url, message);
      },
      onState: (phase) => {
        button.disabled = phase === 'loading';
        if (phase === 'loading') { button.textContent = 'preparing audio…'; message(''); }
        if (phase === 'error') { button.hidden = false; button.textContent = 'try listening again ↺'; message('This layer is not available yet. Try again shortly.', true); }
        if (phase === 'idle') { button.hidden = false; button.textContent = originalLabel; }
      }
    });
    focus.register(key, () => { media.pause(); item.session.cancelPending(); });
    button.addEventListener('click', () => { if (!item.url) return; const epoch = focus.claim(key); item.session.start({url: item.url, film: state.film.id, focusEpoch: epoch}); });
    media.addEventListener('play', () => focus.claim(key));
    media.addEventListener('error', () => { if (media.getAttribute('src')) { message('This audio could not play. Try its download link.', true); button.hidden = false; button.textContent = 'load this layer again ↺'; } });
    return item;
  });
  function releaseAuditions() { for (const item of stems) item.session.reset(); }
  function loadVariant({time = state.preparing ? state.pendingTime : video.currentTime || 0, autoplay = state.preparing ? state.pendingPlay : !video.paused} = {}) {
    if (!state.film) return;
    const focusEpoch = focus.claim('video'); releaseAuditions();
    state.pendingTime = time; state.pendingPlay = autoplay;
    const request = {film: state.film.id, mode: state.mode, url: state.mode === 'ui' ? state.film.ui_video : state.mode === 'recreated' ? state.film.recreated_video : state.film.reference_audio_video, time, autoplay, focusEpoch};
    state.request = request;
    const level = nextPlaybackLevel(state.level, video.volume, playbackGain(state.film, state.mode));
    let levelApplied = false;
    try { video.volume = level.volume; levelApplied = Math.abs(video.volume - level.volume) <= .001; } catch { /* Native volume can be hardware-controlled. */ }
    state.level = {...level, gain: levelApplied ? level.gain : 1, volume: video.volume};
    $('levels-note').hidden = state.mode === 'ui' || !matchedPlaybackLevels(state.film) || !levelApplied || level.baseVolume > 1.0001;
    for (const button of document.querySelectorAll('[data-sound-mode]')) button.setAttribute('aria-pressed', String(button.dataset.soundMode === state.mode));
    $('video-mode-label').textContent = state.mode === 'ui' ? 'UI sounds only / timing study' : state.mode === 'recreated' ? 'UI sounds with quiet music' : 'reference sound / supplied soundtrack';
    $('sound-provenance').textContent = state.mode === 'ui' ? 'Downloaded UI and real keyboard sounds, aligned to visible actions. Custom synthesized accents fill the gaps. No reference audio in this mix.' : state.mode === 'recreated' ? 'The same UI effects with a quiet music bed. No reference audio in this mix.' : 'The supplied soundtrack, on the same recreated picture. Switch to UI sounds only to hear the new layer.';
    $('audio-status-note').textContent = state.mode === 'ui' ? state.film.ui_status || 'UI-only audition brings the effects forward for timing review.' : state.mode === 'recreated' ? state.film.audio_status || 'A new UI sound study with optional background music.' : 'Reference sound is included for comparison. It is not part of the new UI layer.';
    $('open-video-file').href = request.url; video.setAttribute('aria-label', `${state.film.title} — ${state.mode === 'ui' ? 'UI sounds only' : state.mode === 'recreated' ? 'UI sounds with music' : 'reference sound'}`);
    videoSession.start(request); updateTime();
    state.timer = setTimeout(() => { if (currentRequest(request) && state.preparing) { setStatus('Still preparing this soundtrack. You can try loading it again.'); $('retry-video').hidden = false; } }, 15000);
  }
  function selectFilm(index, writeHash = false) {
    const film = state.films[index]; if (!film) return;
    focus.stopAll(); videoSession.reset(); releaseAuditions(); state.film = film; state.pendingTime = 0; state.pendingPlay = false;
    $('selected-film-title').textContent = film.title; $('selected-film-number').textContent = `film ${String(index + 1).padStart(2, '0')} / 06`; $('sound-description').textContent = film.description || '';
    $('listening-panel').hidden = false; $('listening-panel').setAttribute('aria-labelledby', 'film-tab-' + film.id); video.poster = film.poster;
    for (const tab of selector.children) { const chosen = tab.dataset.film === film.id; tab.setAttribute('aria-selected', String(chosen)); tab.tabIndex = chosen ? 0 : -1; }
    for (const item of stems) { item.url = film[stemFields[item.key]]; item.card.hidden = !item.url; item.note.textContent = ''; item.note.classList.remove('error'); if (item.url) { item.download.href = item.url; item.download.download = `${film.id}-${item.key}.m4a`; item.media.setAttribute('aria-label', `${film.title} — ${item.key === 'sfx' ? 'UI effects layer' : item.key === 'music' ? 'instrumental music' : 'new full audio mix'}`); } }
    $('stems').hidden = !stems.some(item => item.url); if (writeHash) host.history.replaceState(null, '', `#${film.id}/${state.mode}`);
    loadVariant({time: 0, autoplay: false});
  }
  for (const button of document.querySelectorAll('[data-sound-mode]')) button.addEventListener('click', () => {
    if (button.dataset.soundMode === state.mode || !state.film) return;
    state.mode = button.dataset.soundMode; host.history.replaceState(null, '', `#${state.film.id}/${state.mode}`); loadVariant();
  });
  $('retry-video').addEventListener('click', () => loadVariant({autoplay: false}));
  video.addEventListener('play', () => focus.claim('video'));
  video.addEventListener('timeupdate', updateTime); video.addEventListener('loadedmetadata', updateTime);
  video.addEventListener('error', () => { if (video.getAttribute('src')) { state.preparing = false; clearTimeout(state.timer); busy(false); setStatus('The file loaded, but the video could not play. Try again or download this MP4.', true); $('retry-video').hidden = false; } });
  selector.addEventListener('keydown', event => {
    const tabs = [...selector.children], index = tabs.indexOf(document.activeElement); if (index < 0) return;
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); tabs.forEach((tab, i) => { tab.tabIndex = i === next ? 0 : -1; }); tabs[next].focus(); }
  });
  async function loadCollection() {
    dataAbort?.abort(); const controller = new AbortController(); dataAbort = controller;
    $('retry-data').hidden = true; $('sound-data-status').hidden = false; $('sound-data-status').textContent = 'Getting the collection ready…';
    try {
      const inline = $('sound-data')?.textContent.trim(); let raw;
      if (inline) raw = JSON.parse(inline);
      else { const response = await fetch('sound-data.json', {signal: controller.signal, credentials: 'omit'}); if (!response.ok) throw new Error('Collection unavailable.'); raw = await response.json(); }
      if (controller.signal.aborted || dataAbort !== controller) return;
      state.films = validateSoundData(raw, host.location.href); selector.replaceChildren();
      state.films.forEach((film, index) => {
        const button = element('button', 'sound-film'); button.type = 'button'; button.id = 'film-tab-' + film.id; button.dataset.film = film.id; button.setAttribute('role', 'tab'); button.setAttribute('aria-controls', 'listening-panel'); button.setAttribute('aria-selected', 'false'); button.tabIndex = -1;
        const picture = element('span', 'sound-film-picture'), image = element('img'); image.src = film.poster; image.alt = ''; image.width = 320; image.height = 200; image.loading = 'lazy'; image.decoding = 'async'; picture.append(image, element('span', 'sound-film-number mono', String(index + 1).padStart(2, '0')));
        button.append(picture, element('strong', '', film.title), element('span', 'mono', formatTime(film.duration))); button.addEventListener('click', () => { if (state.film?.id !== film.id) selectFilm(index, true); }); selector.append(button);
      });
      $('sound-data-status').hidden = true;
      const [wanted, mode] = host.location.hash.slice(1).split('/'); state.mode = ['ui','recreated','reference'].includes(mode) ? mode : 'ui'; const index = state.films.findIndex(film => film.id === wanted); selectFilm(index < 0 ? 4 : index);
    } catch (error) { if (error.name === 'AbortError' || controller.signal.aborted || dataAbort !== controller) return; $('sound-data-status').textContent = 'The listening room could not load. Try again in a moment.'; $('retry-data').hidden = false; }
  }
  $('retry-data').addEventListener('click', loadCollection);
  host.addEventListener('pagehide', () => { suspendedTime = state.preparing ? state.pendingTime : video.currentTime || 0; focus.stopAll(); videoSession.reset(); releaseAuditions(); bridge.dispose(); dataAbort?.abort(); });
  host.addEventListener('pageshow', event => { if (event.persisted) { bridge = makeBridge(); if (state.film) loadVariant({time: suspendedTime, autoplay: false}); else loadCollection(); } });
  loadCollection();
}

if (typeof document !== 'undefined' && typeof window !== 'undefined' && document.getElementById('sound-lab')) startSoundLab(document, window);
