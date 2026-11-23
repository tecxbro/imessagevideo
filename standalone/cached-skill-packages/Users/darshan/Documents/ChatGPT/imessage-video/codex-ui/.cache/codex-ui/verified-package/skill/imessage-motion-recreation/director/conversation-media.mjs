/** Distinct authored media surfaces for the plain scene contract. */
import {group, rect, text} from './components.mjs';

const key = (t, value, ease = 'linear') => ({t, value, ease});
const clip = (width, height, radius = 0) => ({x: 0, y: 0, width, height, radius});
const font = 'Arial, sans-serif';

function image(id, asset, x, y, width, height, radius) {
  if (typeof asset?.src !== 'string' || !asset.src.trim()) {
    throw new Error(`Provide a local image src for ${id}`);
  }
  return group(id, x, y, [{
    id: id + '-image', type: 'image', src: asset.src, width, height,
    preserveAspectRatio: 'xMidYMid slice',
  }], {clip: clip(width, height, radius)});
}

function imageSet(images, minimum, maximum, surface) {
  if (!Array.isArray(images) || images.length < minimum || images.length > maximum) {
    throw new Error(`${surface} needs ${minimum === maximum ? minimum : `${minimum}–${maximum}`} images`);
  }
  return images;
}

function dimensions(width, height) {
  if (!Number.isFinite(width) || !Number.isFinite(height) || width < 100 || height < 48) {
    throw new Error('Media needs a width of at least 100 and a height of at least 48 design pixels');
  }
}

function swipeWindows(swipes, max) {
  if (!Array.isArray(swipes) || swipes.length > max) throw new Error('Too many swipes for this image set');
  let previousEnd = 0;
  return swipes.map(({at, duration = .42}) => {
    if (!Number.isFinite(at) || !Number.isFinite(duration) || at < previousEnd || duration <= 0) {
      throw new Error('Swipes must have finite, non-overlapping time windows');
    }
    previousEnd = at + duration;
    return {at, end: previousEnd};
  });
}

/** A horizontally scrolling rail that can be nested in a document or app surface. */
export function PhotoStrip({id, x = 0, y = 0, width = 214, height = 98, images, swipes = []}) {
  dimensions(width, height);
  imageSet(images, 2, Infinity, 'PhotoStrip');
  const gap = 5;
  const tileWidth = Math.round(width * .77);
  const stride = tileWidth + gap;
  const maxOffset = (images.length - 1) * stride + tileWidth - width;
  const track = [key(0, 0)];
  let offset = 0;
  for (const [index, {at, end}] of swipeWindows(swipes, images.length - 1).entries()) {
    if (at !== track.at(-1).t) track.push(key(at, -offset));
    offset = Math.min((index + 1) * stride, maxOffset);
    track.push(key(end, -offset, 'easeInOut'));
  }
  const tiles = images.map((asset, index) => image(
    `${id}-tile-${index + 1}`, asset, index * stride, 0, tileWidth, height, 9,
  ));
  return group(id, x, y, [
    rect(id + '-backing', 0, 0, width, height, '#f1f1f4', 13),
    group(id + '-rail', 0, 0, tiles, {keyframes: {x: track}}),
  ], {width, height, clip: clip(width, height, 13)});
}

/** Compact preview for a grouped message with two or three photos. */
export function NativePhotoCollage({id, x = 0, y = 0, width = 214, height = 114, images}) {
  dimensions(width, height);
  imageSet(images, 2, 3, 'NativePhotoCollage');
  const gap = 3;
  const halfWidth = (width - gap) / 2;
  const halfHeight = (height - gap) / 2;
  const tiles = images.map((asset, index) => {
    const left = index === 0;
    return image(`${id}-tile-${index + 1}`, asset, left ? 0 : halfWidth + gap,
      index === 2 ? halfHeight + gap : 0, halfWidth,
      left || images.length === 2 ? height : halfHeight, 0);
  });
  return group(id, x, y, tiles, {width, height, clip: clip(width, height, 15)});
}

/** A grouped four-plus preview. Any configured inline sweep is authored choreography. */
export function NativeAttachmentStack({id, x = 0, y = 0, width = 214, height = 126, images, swipes = []}) {
  dimensions(width, height);
  imageSet(images, 4, Infinity, 'NativeAttachmentStack');
  const windows = swipeWindows(swipes, images.length - 1);
  const cardWidth = width - 23;
  const cardHeight = height - 15;
  const cards = images.map((asset, index) => {
    const card = image(`${id}-card-${index + 1}`, asset, 10, 7, cardWidth, cardHeight, 13);
    const pose = depth => {
      const visibleDepth = Math.min(2, depth);
      return {x: 10 + 5 * visibleDepth, y: 7 + 3 * visibleDepth, rotation: 5 * visibleDepth};
    };
    const initial = pose(index);
    const tracks = Object.fromEntries(Object.entries(initial).map(([property, value]) => [property, [key(0, value)]]));
    for (const [frontIndex, {at, end}] of windows.entries()) {
      const depth = index - frontIndex;
      if (depth < 0) break;
      const from = pose(depth);
      const to = depth === 0 ? {x: -cardWidth - 20, y: -8, rotation: -10} : pose(depth - 1);
      for (const property of Object.keys(tracks)) {
        if (at !== tracks[property].at(-1).t) tracks[property].push(key(at, from[property]));
        tracks[property].push(key(end, to[property], 'easeInOut'));
      }
      if (depth === 0) card.end = end;
    }
    return Object.assign(card, initial, {
      originX: cardWidth / 2, originY: cardHeight / 2, keyframes: tracks,
    });
  });
  return group(id, x, y, cards.reverse(), {width, height, clip: clip(width, height, 15)});
}

/** Inline launch preview. Any expanded app sheet has independent content and timing. */
export function InlineAppCard({
  id, x = 0, y = 0, width = 214, height = 130, title, detail = '', action = '',
  image: artwork, color = '#e3ecf8', fontFamily = font,
}) {
  dimensions(width, height);
  if (height < 100 || typeof title !== 'string' || !title.trim()) {
    throw new Error('InlineAppCard needs a title and a height of at least 100 design pixels');
  }
  const footerHeight = (detail ? 50 : 32) + (action ? 23 : 0);
  const artHeight = height - footerHeight;
  const label = (name, value, lineY, size, extra) =>
    text(id + '-' + name, value, 0, lineY, size, {fontFamily, ...extra});
  const labels = [label('title', title, 0, 14, {fontWeight: 650})];
  if (detail) labels.push(label('detail', detail, 20, 11, {fill: '#565e6b'}));
  if (action) labels.push(label('action', action, footerHeight - 29, 11, {fill: '#0869c7', fontWeight: 650}));
  return group(id, x, y, [
    rect(id + '-surface', 0, 0, width, height, '#eef1f5', 15),
    artwork ? image(id + '-artwork', artwork, 0, 0, width, artHeight, 0)
      : rect(id + '-art', 0, 0, width, artHeight, color),
    group(id + '-labels', 11, artHeight + 8, labels, {clip: clip(width - 22, footerHeight - 9)}),
  ], {width, height, clip: clip(width, height, 15)});
}
