import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { group, rect, text } from '../components.mjs';

const FPS = 30;
const WIDTH = 960;
const HEIGHT = 540;
const PAPER = '#ffffff';
const INK = '#1c2728';
const MUTED = '#566367';
const clip = (width, height, radius) => ({ x: 0, y: 0, width, height, radius });
const key = (t, value, ease = 'linear') => ({ t, value, ease });
const image = (id, src, x, y, width, height) => ({ id, type: 'image', src, x, y, width, height });
const circle = (id, x, y, diameter, fill) => ({ id, type: 'circle', x, y, width: diameter, height: diameter, fill });

function configText(value, fallback, field) {
  const result = value ?? fallback;
  if (typeof result !== 'string') throw new TypeError(`${field} must be text.`);
  return result;
}

function configList(value, fallback, field, min, max) {
  const result = value ?? fallback;
  if (!Array.isArray(result) || result.length < min || result.length > max ||
      !result.every(item => typeof item === 'string' && item.trim().length > 0)) {
    throw new TypeError(`${field} must have ${min}–${max} nonempty strings.`);
  }
  return result;
}

function configuration(id, config, minimumArtwork = 2, maximumArtwork = 5) {
  const defaultsFile = new URL(`./defaults/${id}.json`, import.meta.url);
  const defaults = JSON.parse(readFileSync(defaultsFile, 'utf8'));
  const defaultArtwork = defaults.artwork.map(src => fileURLToPath(new URL(src, defaultsFile)));
  const duration = config.duration ?? defaults.duration;
  if (!Number.isFinite(duration) || duration < 2 || duration > 12) {
    throw new RangeError('duration must be 2–12 seconds.');
  }
  const accent = config.accent ?? defaults.accent;
  if (!/^#[a-f0-9]{6}$/i.test(accent)) throw new TypeError('accent must be a six-digit hex color.');
  return {
    duration: Math.round(duration * FPS) / FPS,
    accent,
    title: configText(config.title, defaults.title, 'title'),
    copy: configText(config.copy, defaults.copy, 'copy'),
    detail: configText(config.detail, defaults.detail ?? '', 'detail'),
    sceneTitle: configText(config.sceneTitle, defaults.sceneTitle ?? '', 'sceneTitle'),
    artwork: configList(config.artwork, defaultArtwork, 'artwork', minimumArtwork, maximumArtwork),
    actions: defaults.actions ? configList(config.actions, defaults.actions, 'actions', 1, 3) : undefined,
  };
}

function makeScene(id, duration, background, notes, layers) {
  return {
    width: WIDTH, height: HEIGHT, fps: FPS, duration, background, title: id,
    source: { notes },
    layers,
  };
}

function headline(title, accent) {
  return group('presentation-headline', 66, 156, [
    rect('presentation-rule', 0, 0, 60, 4, accent, 2),
    text('presentation-title', title, 0, 27, 51, {
      fill: '#f7f6ef', fontWeight: 700, lineHeight: 55, letterSpacing: -1.5,
    }),
  ]);
}

function chip(id, label, x, y, width, fill, ink) {
  return group(id, x, y, [
    rect(`${id}-surface`, 0, 0, width, 39, fill, 11),
    text(`${id}-label`, label, width / 2, 10, 14, { fill: ink, textAnchor: 'middle', fontWeight: 700 }),
  ]);
}

function artworkTile(id, src, x, y, width, height, radius, aspect = 1.6) {
  const artWidth = Math.max(width, height * aspect);
  const artHeight = Math.max(height, width / aspect);
  return group(id, x, y, [
    image(`${id}-artwork`, src, (width - artWidth) / 2, (height - artHeight) / 2, artWidth, artHeight),
  ], { clip: clip(width, height, radius) });
}

function placePhotoStrip(config) {
  const values = configuration('place-photo-strip', config);
  const width = 344;
  const height = 201;
  const tileWidth = 320;
  const stride = 331;
  const travel = (values.artwork.length - 1) * stride + tileWidth - width;
  // Original 30 fps film samples, mapped onto the distance of the replacement strip.
  const sourceTravel = [0, 22, 22, 47, 76, 109, 148, 148, 195, 252, 324, 417, 417, 542, 698, 846, 956, 956, 1035, 1094, 1140];
  const firstFrame = Math.round(values.duration * FPS * 0.34);
  const photoTrack = group('photo-strip-track', 0, 0,
    values.artwork.map((src, index) =>
      artworkTile(`place-photo-${index}`, src, stride * index, 0, tileWidth, height, 12),
    ),
    { keyframes: { x: sourceTravel.map((distance, index) =>
      key((firstFrame + index) / FPS, distance === 0 ? 0 : -travel * distance / 1140),
    ) } },
  );
  const photoViewport = group('photo-strip-viewport', 14, 152, [
    rect('photo-strip-backdrop', 0, 0, width, height, '#e8ede3', 12),
    photoTrack,
  ], { clip: clip(width, height, 12) });

  const buttonWidth = (width - 8 * (values.actions.length - 1)) / values.actions.length;
  const actions = values.actions.map((action, index) =>
    chip(`place-action-${index}`, action, (buttonWidth + 8) * index, 0, buttonWidth,
      index === values.actions.length - 1 ? values.accent : '#e9eee7', INK),
  );
  const place = group('place-card', 525, 60, [
    rect('place-surface', 0, 0, 372, 420, PAPER, 24),
    text('place-title', values.title, 16, 21, 28, { fontWeight: 700, fill: INK }),
    text('place-copy', values.copy, 16, 62, 17, { fill: INK }),
    group('place-actions', 14, 98, actions),
    photoViewport,
    rect('place-divider', 14, 371, 344, 1, '#e4e9e5'),
    text('place-detail', values.detail, 16, 383, 15, { fill: MUTED }),
  ]);
  return makeScene('place-photo-strip', values.duration, '#163633',
    'New place-card scene. The shared photo track adapts Linq frames 1091–1111; stationary UI geometry and artwork are authored.',
    [headline(values.sceneTitle, values.accent), place]);
}

function chatPanel(title, copy, child, detail, overlays = []) {
  return group('conversation', 513, 38, [
    rect('conversation-surface', 0, 0, 384, 464, '#f6f7fc', 30),
    circle('conversation-contact-glyph', 20, 19, 31, '#b8bddf'),
    text('conversation-title', title, 63, 20, 17, { fontWeight: 700, fill: INK }),
    text('conversation-detail', detail, 63, 42, 12, { fill: MUTED }),
    rect('conversation-divider', 0, 68, 384, 1, '#dcdfee'),
    group('conversation-request', 21, 89, [
      rect('conversation-request-surface', 0, 0, 342, 56, '#e8e9f5', 14),
      text('conversation-copy', copy, 12, 12, 15, { fill: INK, lineHeight: 19 }),
    ]),
    child,
    rect('composer-field', 21, 412, 342, 35, PAPER, 12, { stroke: '#dcdfee', strokeWidth: 1 }),
    text('composer-placeholder', 'Message', 34, 420, 14, { fill: MUTED }),
    ...overlays,
  ], { clip: clip(384, 464, 30) });
}

function stackedAttachmentCard(src, index, width, height, keyframes) {
  const id = `attachment-card-${index}`;
  return group(id, 0, 0, [
    rect(`${id}-rim`, 0, 0, width, height, '#ffffff', 17, {
      shadow: { x: 0, y: 3, blur: 9, color: 'rgba(27,33,60,0.19)' },
    }),
    artworkTile(id + '-image', src, 4, 4, width - 8, height - 8, 13),
  ], { originX: width / 2, originY: height / 2, keyframes });
}

function restingCard(rank) {
  const scale = 1 - rank * .036;
  return { x: rank * 14, y: rank * -6, rotation: rank * -3.8, scaleX: scale, scaleY: scale };
}

function attachmentTracks(index, swipes, duration) {
  const initial = restingCard(index);
  const tracks = Object.fromEntries(Object.entries(initial).map(([prop, value]) => [prop, [key(0, value)]]));
  const addPose = (time, pose, ease) => {
    for (const [prop, value] of Object.entries(pose)) tracks[prop].push(key(time, value, ease));
  };

  // Recompute depth from rank for each gesture. Back-to-front paint order stays
  // stable while the front card departs and its nearest neighbor takes its place.
  const slot = duration * .58 / swipes;
  for (let swipe = 0; swipe < swipes && swipe <= index; swipe += 1) {
    const start = duration * .28 + swipe * slot;
    const pickup = start + slot * .29;
    const finish = start + slot * .77;
    const rank = index - swipe;
    const rest = restingCard(rank);
    addPose(start, rest, 'hold');
    if (rank === 0) {
      addPose(pickup, { ...rest, x: -65, y: 4, rotation: -6 }, 'easeIn');
      addPose(finish, { ...rest, x: -303, y: 24, rotation: -15 }, 'easeOut');
    } else {
      addPose(pickup, rest, 'hold');
      addPose(finish, restingCard(rank - 1), 'easeOut');
    }
  }
  return tracks;
}

function attachmentStack(config) {
  const values = configuration('messages-attachment-stack', config);
  const swipes = config.swipes ?? Math.min(2, values.artwork.length - 1);
  if (!Number.isInteger(swipes) || swipes < 1 || swipes >= values.artwork.length) {
    throw new RangeError('swipes must be 1 through artwork.length − 1.');
  }
  const width = 246;
  const height = 158;
  const cards = values.artwork.map((src, index) =>
    stackedAttachmentCard(src, index, width, height, attachmentTracks(index, swipes, values.duration)),
  ).reverse();
  const stack = group('attachment-gallery', 20, 157, [
    group('attachment-viewport', 0, 0, [
      group('attachment-deck', 31, 31, cards),
    ], { clip: clip(344, 202, 13) }),
    text('attachment-count', `${cards.length} attachments`, 32, 208, 14, { fill: MUTED, fontWeight: 700 }),
  ]);
  return makeScene('messages-attachment-stack', values.duration, '#2c3157',
    'Authored conversation and separate stack layers. Swipe timing, rotations, travel and exits are editable illustrative values.',
    [headline(values.sceneTitle, values.accent), chatPanel(values.title, values.copy, stack, values.detail)]);
}


function inlineCardExpand(config) {
  const values = configuration('inline-card-expand', config, 1, 1);
  const inline = group('inline-card', 21, 170, [
    rect('inline-card-surface', 0, 0, 290, 128, '#dbe8f1', 15),
    artworkTile('inline-card-artwork', values.artwork[0], 12, 14, 90, 99, 9),
    text('inline-card-title', values.title, 116, 25, 17, { fontWeight: 700 }),
    text('inline-card-detail', values.detail, 116, 55, 13, { fill: MUTED }),
    text('inline-card-hint', 'View draft', 116, 91, 13, { fontWeight: 700, fill: '#36516a' }),
  ]);
  const onset = Math.round(values.duration * FPS * .31);
  const scrim = rect('draft-scrim', 0, 0, 384, 464, '#132333', 0, {
    keyframes: { opacity: [key(onset / FPS, 0), key((onset + 10) / FPS, .46, 'easeOut')] },
  });

  // Grabber y from Photon Mini f214–240, mapped from the 1080px source to the chat panel.
  const grabberY = [879, 640, 482, 374, 294, 232, 183, 144, 113, 89, 69, 54, 43, 36, 31, 29, 30, 31, 33, 34, 35, 36, 36, 37, 38, 38, 39];
  const sheetTop = 117;
  const sheetTrack = [
    key((onset + 2) / FPS, 464),
    ...grabberY.map((y, index) =>
      key((onset + 3 + index) / FPS, sheetTop + (y - 39) * (464 - sheetTop) / (1080 - 39)),
    ),
  ];
  const buttonWidth = (344 - 8 * (values.actions.length - 1)) / values.actions.length;
  const buttons = values.actions.map((label, index) =>
    chip(`draft-action-${index}`, label, (buttonWidth + 8) * index, 0, buttonWidth,
      index === values.actions.length - 1 ? values.accent : '#f0f2f2', INK),
  );
  const sheet = group('expanded-draft-sheet', 0, 464, [
    rect('draft-sheet-surface', 0, 0, 384, 385, '#ffffff', 26),
    rect('draft-grabber', 171, 10, 42, 4, '#a5adb6', 2),
    text('draft-title', values.title, 20, 34, 24, { fontWeight: 700 }),
    text('draft-detail', values.detail, 20, 67, 14, { fill: MUTED }),
    artworkTile('draft-cover', values.artwork[0], 20, 96, 344, 110, 9),
    text('draft-copy', values.copy, 20, 217, 16, { lineHeight: 20 }),
    group('draft-actions', 20, 288, buttons),
  ], { keyframes: { y: sheetTrack } });

  return makeScene('inline-card-expand', values.duration, '#2f394b',
    'New draft scene. A distinct sheet adapts the measured grabber path from Photon Mini frames 214–240 above an independently dimmed thread.',
    [headline(values.sceneTitle, values.accent), chatPanel('Location scouting', 'Could you check the call time?', inline, 'Drafts', [scrim, sheet])]);
}

const PORTRAIT_POSES = [
  { from: [-34, -46], via: [246, 124], to: [196, 148], scale: 2.2 },
  { from: [459, -125], via: [438, 97], to: [453, 119], scale: 1.55 },
  { from: [937, -21], via: [696, 156], to: [747, 154], scale: 2.06 },
  { from: [1016, 492], via: [734, 343], to: [765, 405], scale: 2.36 },
  { from: [-57, 512], via: [284, 393], to: [250, 415], scale: 1.8 },
];

function avatarRingAssemble(config) {
  const values = configuration('avatar-ring-assemble', config);
  const onset = Math.round(values.duration * FPS * .26);
  const cadence = Math.min(1, (values.duration * FPS - onset - 5) / 50);
  const atOffset = offset => (onset + offset * cadence) / FPS;
  const headlineScale = [[1, 1], [7, .94], [13, .73], [17, .65], [21, .61], [27, .58], [37, .56], [49, .56]];
  const scale = headlineScale.map(([offset, amount]) => key(atOffset(offset), amount));
  const center = group('anchored-headline', WIDTH / 2, HEIGHT / 2, [
    text('ring-title', values.title, 0, -50, 70, {
      textAnchor: 'middle', fontWeight: 700, fill: '#f5efe4', letterSpacing: -2,
    }),
    text('ring-copy', values.copy, 0, 37, 28, {
      textAnchor: 'middle', fontWeight: 700, fill: values.accent,
    }),
  ], { keyframes: { scaleX: scale, scaleY: scale } });
  const diameter = 126;
  const portraits = values.artwork.map((src, index) => {
    const pose = PORTRAIT_POSES[index];
    const enter = atOffset(3 + (index % 3) * 3);
    const crossing = atOffset(19 + (index % 2) * 3);
    const driftEnd = atOffset(47 + (index % 3));
    const coord = axis => [
      key(enter, pose.from[axis] - diameter / 2),
      key(crossing, pose.via[axis] - diameter / 2, 'easeOut'),
      key(driftEnd, pose.to[axis] - diameter / 2, 'easeOut'),
    ];
    const size = [key(enter, pose.scale), key(crossing, 1.11, 'easeOut'), key(driftEnd, 1, 'easeOut')];
    return group(`ring-avatar-${index}`, 0, 0, [
      circle(`ring-avatar-${index}-rim`, 0, 0, diameter, '#f2e7d3'),
      artworkTile(`ring-avatar-${index}-picture`, src, 4, 4, diameter - 8, diameter - 8, (diameter - 8) / 2, 1),
    ], {
      originX: diameter / 2, originY: diameter / 2,
      keyframes: {
        x: coord(0), y: coord(1), scaleX: size, scaleY: size,
        opacity: [key(enter, 0), key(enter + .19, 1, 'easeOut')],
        blur: [key(enter, 16 + index * 3), key(crossing, 3), key(driftEnd, 0, 'easeOut')],
      },
    });
  });
  return makeScene('avatar-ring-assemble', values.duration, '#222c34',
    'New portrait composition. The anchored headline scales close to sampled Gallery f603–653 proportions; portrait routes and focus are illustrative.',
    [center, ...portraits]);
}

const BUILDERS = {
  'place-photo-strip': placePhotoStrip,
  'messages-attachment-stack': attachmentStack,
  'inline-card-expand': inlineCardExpand,
  'avatar-ring-assemble': avatarRingAssemble,
};

export function buildCatalogScene(id, config = {}) {
  if (!Object.hasOwn(BUILDERS, id)) throw new RangeError(`Unknown editable motion: ${id}`);
  if (!config || typeof config !== 'object' || Array.isArray(config)) {
    throw new TypeError('Motion configuration must be an object.');
  }
  return BUILDERS[id](config);
}
