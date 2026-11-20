import {statSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as ui from '../director/components.mjs';

export const colors = Object.freeze({
  ink: '#182737', paper: '#ffffff', blue: '#1478e9', muted: '#516277',
  light: '#e8eef5', green: '#16815f', red: '#ba394b', line: '#d4dfe9',
});

const width = 720;
const height = 480;
const samplePhotos = Array.from({length: 4}, (_, i) =>
  fileURLToPath(new URL(`./assets/landscape-${i + 1}.png`, import.meta.url)));

export const defaults = Object.freeze({
  heading: 'Alpine field notes', copy: 'Can you send the trail map?',
  reply: 'Here it is. Meet at the north gate.', title: 'The north ridge',
  detail: 'Field guide · Autumn', action: 'Open', photos: samplePhotos,
});

const numberInRange = (value, min, max) => Number.isFinite(value) && value >= min && value <= max;
const idPattern = /^[a-z0-9][a-z0-9._:-]*$/;
const easePattern = /^(linear|hold|easeIn|easeOut|easeInOut|cubic-bezier\([^)]+\))$/;

function configuration(content) {
  if (!content || typeof content !== 'object' || Array.isArray(content))
    throw Error('Content must be a JSON object');
  for (const [key, value] of Object.entries(content)) {
    if (key === 'values') {
      if (!Array.isArray(value) || value.length < 1 || value.length > 24 || !value.every(Number.isFinite))
        throw Error('values must contain 1–24 finite numbers');
      continue;
    }
    if (key === 'swipes') {
      if (![1, 2].includes(value)) throw Error('swipes must be 1 or 2');
      continue;
    }
    if (key === 'direction') {
      if (!['up', 'down', 'left', 'right'].includes(value)) throw Error('direction must be up, down, left or right');
      continue;
    }
    if (!Object.hasOwn(defaults, key)) throw Error(`Unknown content field: ${key}`);
    if (key !== 'photos' && (typeof value !== 'string' || value.length > 250))
      throw Error(`Content ${key} must be a string up to 250 characters`);
  }
  const config = {...defaults, ...content};
  if (!Array.isArray(config.photos) || !config.photos.length || config.photos.length > 12)
    throw Error('Provide 1–12 local image paths in photos');
  config.photos = config.photos.map(src => {
    if (typeof src !== 'string' || !/\.(png|jpe?g|webp)$/i.test(src))
      throw Error('Each photo must be a local PNG, JPG or WebP path');
    const full = path.resolve(src);
    if (!statSync(full, {throwIfNoEntry: false})?.isFile()) throw Error(`Photo file not found: ${full}`);
    return full;
  });
  return config;
}

export function buildMotion(entry, content = {}, options = {}) {
  if (!entry || typeof entry.build !== 'function') throw Error('Unknown motion entry');
  const data = configuration({...entry.defaults, ...content});
  if (entry.photoCount && content.photos !== undefined) {
    const {min, max} = entry.photoCount;
    if (!numberInRange(data.photos.length, min, max))
      throw Error(`${entry.id} needs ${min}–${max} photos`);
  }
  const fps = options.fps ?? 30;
  const seconds = options.duration ?? 2.4;
  if (data.direction && !entry.editable.includes('direction'))
    delete data.direction;
  if (![24, 25, 30, 60].includes(fps)) throw Error('Use an fps of 24, 25, 30 or 60');
  if (!numberInRange(seconds, 1.6, 12)) throw Error('Duration must be 1.6–12 seconds');
  const frameCount = Math.round(seconds * fps);
  const duration = frameCount / fps;
  const {rect, text, group} = ui;
  const heading = group('heading', 110, 44, [
    rect('heading-background', 0, 0, 500, 54, '#f2f6fb', 13),
    text('heading-copy', data.heading, 26, 13, 23, {fill: colors.ink, fontWeight: 700}),
  ]);
  const stage = group('stage', 110, 98, [], {clip: {x: 0, y: 0, width: 500, height: 298}});
  const footer = group('footer', 110, 396, [rect('footer-background', 0, 0, 500, 40, '#f2f6fb', 12)]);
  const frame = rect('surface', 110, 44, 500, 392, colors.paper, 18);
  const layers = [frame, stage, footer, heading];
  const events = [];
  let initialUI = null;

  entry.build({
    heading, stage, footer, colors, rect, text, group, content: data, ui, fps, frameCount, duration,
    label(value) {
      footer.children.push(text('footer-label', value, 26, 11, 15, {fill: colors.muted}));
    },
    image(id, x, y, width, height, {photo = 0, ...extra} = {}) {
      if (!Number.isInteger(photo) || photo < 0) throw Error(`Invalid photo index for ${id}`);
      return {id, type: 'image', src: data.photos[photo % data.photos.length], x, y, width, height, ...extra};
    },
    track(layer, property, points) {
      let previous = -1;
      const keys = points.map(([fraction, value, ease = 'linear']) => {
        if (!numberInRange(fraction, 0, 1) || fraction <= previous || !easePattern.test(ease))
          throw Error(`Invalid or out-of-order key for ${layer.id}.${property}`);
        previous = fraction;
        return {t: fraction * duration, value, ease};
      });
      layer.keyframes ??= {};
      if (Object.hasOwn(layer.keyframes, property)) throw Error(`Duplicate track: ${layer.id}.${property}`);
      layer.keyframes[property] = keys;
    },
    event(name, fraction, target, kind = name, uiState) {
      if (!idPattern.test(name) || !idPattern.test(kind) || !numberInRange(fraction, 0, 1))
        throw Error(`Invalid event: ${name}`);
      const frame = Math.max(0, Math.min(frameCount - 1, Math.ceil(fraction * frameCount - 1e-8)));
      const event = {id: `motion.${entry.id}.${name}`, kind, target, frame, layerIds: [target]};
      if (uiState !== undefined) event.uiState = uiState;
      events.push(event);
    },
    setInitialUI(state) { initialUI = state; },
  });

  return {
    width, height, fps, duration, background: '#dce7f1', title: entry.title,
    source: {
      path: entry.source.ref,
      sourceStart: entry.source.range[0],
      sourceEnd: entry.source.range[1],
      notes: entry.source.note ?? 'Original editable Motion demonstration.',
    },
    layers,
    timeline: {
      version: 1, picture: {fpsNum: fps, fpsDen: 1, frameCount}, initialUI,
      events: events.sort((a, b) => a.frame - b.frame), cues: [],
    },
  };
}
