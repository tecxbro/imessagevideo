import {spawnSync} from 'node:child_process';
import {existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {defaults} from './scene.mjs';

const SELF = 'account.self';
const REMOTE = 'account.remote';
const root = fileURLToPath(new URL('../', import.meta.url));
const preview = {width: 720, height: 480, padding: 16};
const graphemes = new Intl.Segmenter(undefined, {granularity: 'grapheme'});
const message = (id, senderId, text, extra = {}) => ({id, senderId, text, ...extra});

function draftEvents(copy, first, last) {
  const characters = Array.from(graphemes.segment(copy), ({segment}) => segment);
  const stepCount = Math.min(last - first + 1, characters.length);
  return Array.from({length: stepCount}, (_, i) => ({
    name: `draft-${i + 1}`, kind: 'draft', frame: first + (stepCount === 1 ? 0 : Math.floor(i * (last - first) / (stepCount - 1))),
    text: characters.slice(0, Math.ceil((i + 1) * characters.length / stepCount)).join(''), durationFrames: 0,
  }));
}

const recipes = {
  'conversation-handoff': {
    note: 'The adapter keeps the Motion send and receive frame anchors and renders its own draft, clearing, and message entry.',
    build({data, at}) {
      const draft = draftEvents(data.copy, at(.114), at(.365));
      return {events: [
        ...draft,
        {name: 'send', kind: 'send', outputKind: 'message.send', frame: at(.44), message: {id: 'message.sent'}},
        {name: 'receive', kind: 'receive', outputKind: 'message.receive', frame: at(.70), message: message('message.reply', REMOTE, data.reply)},
      ]};
    },
  },
  'photos-under-fixed-heading': {
    note: 'The attachment rail shows one adjacent page per swipe and holds the conversation header. Its easing comes from the adapter.',
    build({data, frameCount}) {
      const direction = data.direction ?? 'left';
      if (!['left','right'].includes(direction)) throw Error('The photo rail only supports horizontal travel');
      if (!Array.isArray(data.photos) || data.photos.length < 2 || data.photos.length > 12)
        throw Error('photos-under-fixed-heading needs 2–12 photos');
      const attachmentIds = data.photos.map((_, index) => `photo-${index + 1}`);
      const from = direction === 'right' ? 1 : 0;
      const railStart = Math.round(frameCount * .27) + 1;
      const railSpan = Math.min(20, Math.round(frameCount * .47));
      return {
        assets: Object.fromEntries(attachmentIds.map((id, index) => [id, path.resolve(data.photos[index])])),
        initial: {messages: [message('message.photos', REMOTE, '', {attachmentIds})]},
        events: [
          ...(from ? [{name: 'rail-initial-page', kind: 'media.page', frame: 0, messageId: 'message.photos', index: from, durationFrames: 0}] : []),
          {name: 'rail-start', kind: 'media.page', outputKind: 'media.scroll', frame: railStart, messageId: 'message.photos', index: 1 - from, durationFrames: railSpan},
        ],
        markers: [{name: 'rail-settle', from: 'rail-start', kind: 'media.settle', frame: railStart + railSpan - 1}],
      };
    },
  },
  'composer-type': {
    note: 'The typing beat uses frame-addressed draft revisions and the adapter’s composer. Longer input wraps in the field.',
    build({data, content, at}) {
      const events = draftEvents(data.copy, at(.16), at(.82));
      const initial = Object.hasOwn(content, 'reply')
        ? {messages: [message('message.prior', REMOTE, data.reply)]}
        : undefined;
      if (!events.length) return {initial, events};
      Object.assign(events[0], {name: 'first-character', outputKind: 'typing'});
      return {initial, events, markers: [{name: 'draft-complete', from: 'first-character', kind: 'typing_end', frame: events.at(-1).frame}]};
    },
  },
  'draft-send-flight': {
    note: 'The source event IDs carry through the adapter’s authored row entrance and composer clearing. The source spring and collapsing field shape belong to the measured Motion preview.',
    build({data, at, fps, frameCount}) {
      const start = at(.19);
      const finish = at(.19 + .69 * fps / frameCount);
      return {
        initial: {draft: data.copy, messages: [message('message.prior', REMOTE, data.reply)]},
        events: [{name: 'send', kind: 'send', outputKind: 'message_send', frame: start,
          durationFrames: finish - start + 1, message: {id: 'message.sent'}}],
        markers: [{name: 'settle', from: 'send', kind: 'message_settle', frame: finish}],
      };
    },
  },
  'typing-indicator-cycle': {
    note: 'The adapter reveals a named typing indicator and holds it. The three-dot cycle is available in the Motion preview.',
    build({data, at}) {
      return {initial: {messages: [message('message.sent', SELF, data.copy)]}, events: [
        {name: 'thinking-visible', kind: 'typing', outputKind: 'typing_indicator', frame: at(.11), senderId: REMOTE, active: true},
      ]};
    },
  },
  'reply-makes-room': {
    note: 'The reply arrives whole. The adapter scrolls its transcript when the new message would exceed the pane.',
    build({data, at}) {
      return {
        initial: {messages: [
          message('message.opening', REMOTE, 'Do you have a minute?'),
          message('message.acknowledged', SELF, 'Yes, go ahead.'),
          message('message.prior', REMOTE, 'I can check the details.'),
          message('message.context', SELF, 'Could you confirm what you found?'),
          message('message.detail', REMOTE, 'I have the first part.'),
          message('message.request', SELF, data.copy),
        ]},
        events: [{name: 'reply-arrival', kind: 'receive', outputKind: 'message_arrival', frame: at(.48),
          message: message('message.reply', REMOTE, data.reply)}],
      };
    },
  },
  'delivery-receipt-handoff': {
    note: 'The adapter adds a second send before applying its status to the latest outgoing row.',
    build({data, at}) {
      const status = ['Delivered', 'Read', 'Failed'].find(value => value.toLowerCase() === data.detail.trim().toLowerCase());
      if (!status) throw Error('Use Delivered, Read, or Failed for receipt detail in Clone iMessage UI');
      return {
        initial: {messages: [message('message.first', SELF, data.copy, {receipt: 'Delivered'})]},
        events: [
          {name: 'outgoing-arrives', kind: 'send', frame: at(.28), durationFrames: at(.41) - at(.28) + 1,
            message: {id: 'message.latest', text: data.reply}},
          {name: 'receipt-reassigned', kind: 'receipt', outputKind: 'delivery_status', frame: at(.46), messageId: 'message.latest', status},
        ],
      };
    },
  },
  'edit-message-reflow': {
    note: 'The adapter revises the same message at commit and recomputes the layout. Editable text revisions mark the change.',
    build({data, at}) {
      return {
        initial: {messages: [message('message.original', SELF, data.copy), message('message.reply', REMOTE, data.reply)]},
        events: [{name: 'edit-commit', kind: 'edit', outputKind: 'edit_commit', frame: at(.64),
          messageId: 'message.original', text: [data.copy, data.detail].filter(Boolean).join('\n')}],
      };
    },
  },
  'undo-send-remove': {
    note: 'The adapter replaces the row with a removal line and updates the transcript. The Motion preview gives the outgoing bubble a separate retraction path.',
    build({data, at}) {
      return {
        initial: {messages: [message('message.prior', REMOTE, data.reply), message('message.sent', SELF, data.copy)]},
        events: [{name: 'undo-send', kind: 'unsend', frame: at(.36), messageId: 'message.sent'}],
      };
    },
  },
  'reaction-attach': {
    note: 'The adapter opens context, then attaches the chosen reaction to the targeted row. The Motion preview animates a separate badge flight.',
    build({data, at}) {
      return {
        initial: {messages: [message('message.prior', SELF, data.reply), message('message.target', REMOTE, data.copy)]},
        events: [
          {name: 'reaction-choices', kind: 'overlay', frame: at(.12), surface: 'context', messageId: 'message.target',
            durationFrames: at(.31) - at(.12) + 1},
          {name: 'reaction-choice', kind: 'reaction', outputKind: 'reaction_select', frame: at(.35), messageId: 'message.target',
            mark: data.action, durationFrames: at(.67) - at(.35) + 1},
        ],
        markers: [{name: 'reaction-attached', from: 'reaction-choice', kind: 'reaction_attached', frame: at(.67)}],
      };
    },
  },
  'long-press-actions': {
    note: 'The adapter anchors a single context popup to the selected row. The native-source staging of dimming, tray and reaction rail is in the Motion preview.',
    build({data, at, fps, frameCount}) {
      const start = at(.27);
      const finish = at(.27 + .38 * fps / frameCount);
      return {
        initial: {messages: [message('message.prior', REMOTE, data.reply), message('message.target', SELF, data.copy)]},
        events: [{name: 'hold-threshold', kind: 'overlay', outputKind: 'long_press', frame: start,
          surface: 'context', messageId: 'message.target', durationFrames: finish - start + 1}],
        markers: [{name: 'actions-ready', from: 'hold-threshold', kind: 'menu_open', frame: finish}],
      };
    },
  },
  'keyboard-focus-reflow': {
    note: 'The adapter raises its own keyboard and composer. Existing rows reflow when they exceed the reduced pane.',
    build({data, at}) {
      const start = at(.34);
      const finish = at(.60);
      return {
        initial: {draft: data.copy, messages: [
          message('message.start', REMOTE, 'Do you have a minute?'),
          message('message.local', SELF, 'Yes, go ahead.'),
          message('message.reply', REMOTE, data.reply),
        ]},
        events: [{name: 'composer-focus', kind: 'focus', outputKind: 'tap', frame: start, focused: true,
          durationFrames: finish - start + 1}],
        markers: [{name: 'keyboard-ready', from: 'composer-focus', kind: 'keyboard_show', frame: finish}],
      };
    },
  },
  'app-drawer': {
    note: 'The adapter brings its app tray into view within the current conversation with a short rise.',
    build({data, at}) {
      return {initial: {messages: [message('message.context', REMOTE, data.copy)]}, events: [
        {name: 'drawer-open', kind: 'overlay', outputKind: 'drawer-open', frame: at(.42), surface: 'tray'},
      ]};
    },
  },
};

export const uiIds = Object.freeze(Object.keys(recipes));

function rebaseAssets(scene, directory) {
  // The adapter emits data URIs for artwork normalized from EXIF orientation.
  const rebase = src => src.startsWith('data:') ? src : path.resolve(directory, src);
  function visit(layer) {
    if (layer.type === 'image') layer.src = rebase(layer.src);
    for (const child of layer.children ?? []) visit(child);
  }
  for (const layer of scene.layers) visit(layer);
  for (const font of scene.fonts ?? []) font.src = rebase(font.src);
}

export function buildUiMotion(entry, content = {}, {
  fps = 30, duration = 2.4, uiRoot = root, python = process.env.MOTION_PYTHON ?? 'python3',
} = {}) {
  const recipe = entry && Object.hasOwn(recipes, entry.id) ? recipes[entry.id] : null;
  if (!recipe) throw Error(`Clone iMessage UI does not cover ${entry?.id ?? 'this entry'}. Choose ${uiIds.join(', ')}`);
  if (![24,25,30,60].includes(fps)) throw Error('Use an fps of 24, 25, 30 or 60');
  if (!Number.isFinite(duration) || duration < 1.6 || duration > 12) throw Error('Duration must be 1.6–12 seconds');
  if (!content || typeof content !== 'object' || Array.isArray(content)) throw Error('Content must be a JSON object');
  const data = {...defaults, ...entry.defaults, ...content};
  for (const key of ['heading','copy','reply','title','detail','action']) {
    if (typeof data[key] !== 'string' || data[key].length > 250)
      throw Error(`Content ${key} must be a string up to 250 characters`);
  }
  const frameCount = Math.round(fps * duration);
  const at = fraction => Math.min(frameCount - 1, Math.ceil(fraction * frameCount - 1e-8));
  const {initial, events, markers = [], assets} = recipe.build({data, content, at, fps, frameCount});
  const prefix = `motion.${entry.id}.`;
  const conversation = {
    version: 1, conversationId: 'thread.motion', title: data.heading, service: data.detail,
    participants: {[SELF]: 'You', [REMOTE]: 'Recipient'}, localSenderId: SELF,
    display: {width: 490, height: 480, textSize: 19}, fps, frameCount, initial, assets,
    events: events.map(({name, outputKind, ...event}) => ({...event, id: prefix + name})),
  };
  const cwd = path.resolve(uiRoot);
  if (!existsSync(path.join(cwd, 'ui', 'adapter.py')))
    throw Error(`Clone iMessage UI adapter is unavailable at ${cwd}. Use the skill directory containing ui/adapter.py.`);
  const directory = mkdtempSync(path.join(tmpdir(), 'motion-ui-'));
  try {
    const input = path.join(directory, 'conversation.json');
    const output = path.join(directory, 'scene.json');
    writeFileSync(input, JSON.stringify(conversation));
    const result = spawnSync(python, ['-m', 'ui.adapter', input, '--out', output], {cwd, encoding: 'utf8'});
    if (result.error) throw result.error;
    if (result.status !== 0) throw Error(`Clone iMessage UI adapter failed: ${result.stderr?.trim() || result.signal || result.status}`);
    const scene = JSON.parse(readFileSync(output, 'utf8'));
    rebaseAssets(scene, directory);
    const scale = Math.min((preview.width - 2 * preview.padding) / scene.width,
      (preview.height - 2 * preview.padding) / scene.height);
    const layers = [{id: 'motion.ui-fit', type: 'group', x: (preview.width - scene.width * scale) / 2,
      y: (preview.height - scene.height * scale) / 2, scaleX: scale, scaleY: scale,
      clip: {x: 0, y: 0, width: scene.width, height: scene.height}, children: scene.layers}];
    const outputKinds = new Map(events.filter(event => event.outputKind).map(event => [prefix + event.name, event.outputKind]));
    for (const event of scene.timeline.events) event.kind = outputKinds.get(event.id) ?? event.kind;
    for (const {name, from, kind, frame} of markers) {
      const base = scene.timeline.events.find(event => event.id === prefix + from);
      scene.timeline.events.push({id: prefix + name, kind, target: base.target, layerIds: base.layerIds, frame});
    }
    scene.timeline.events.sort((a, b) => a.frame - b.frame);
    return {...scene, width: preview.width, height: preview.height, layers, title: entry.title,
      source: {path: entry.source.ref, sourceStart: entry.source.range[0], sourceEnd: entry.source.range[1],
        notes: `Clone iMessage UI film-paper adaptation. ${recipe.note}`}};
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
}
