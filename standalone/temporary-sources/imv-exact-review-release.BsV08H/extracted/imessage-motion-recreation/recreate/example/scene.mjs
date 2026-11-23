import {readFileSync, writeFileSync} from 'node:fs';
import {sampleTrack} from '../../scripts/engines/common.mjs';
import {
  BottomSheet, Composer, MessageBubble, PhoneFrame, group, rect, text,
} from '../../director/components.mjs';

const fps = 30;
const frameCount = 120;
const toSeconds = frame => frame / fps;
const ink = '#17191d';
const backdrop = '#eeedf3';
const offerCopy = 'Where are we heading?';
const receiptCopy = 'Booked for 18:40.';

function timeline(copy, selectAt) {
  const offer = {id: 'message.offer', senderId: 'account.planner', text: offerCopy};
  const request = {id: 'message.request', senderId: 'account.self', text: copy};
  const receipt = {id: 'message.receipt', senderId: 'account.planner', text: receiptCopy};
  function uiState(messages, surface = 'conversation') {
    return {
      conversationId: 'thread.rail-planner',
      messages,
      composer: {text: '', focused: false},
      viewport: {surface, anchorMessageId: messages.at(-1).id},
    };
  }
  const events = [
    {name: 'conversation', kind: 'conversation.open', target: 'thread.rail-planner', frame: 18,
      layerIds: ['phone'], uiState: uiState([offer])},
    {name: 'request', kind: 'message.send', target: request.id, frame: 30,
      layerIds: ['request'], uiState: uiState([offer, request])},
    {name: 'drawer', kind: 'picker.open', target: 'train-picker', frame: 56,
      layerIds: ['drawer'], uiState: uiState([offer, request], 'train-picker')},
    {name: 'seat-selection', kind: 'picker.select', target: 'train.first', frame: selectAt,
      layerIds: ['seat-selection-checked']},
    {name: 'receipt', kind: 'message.receive', target: receipt.id, frame: 89,
      layerIds: ['receipt'], uiState: uiState([offer, request, receipt])},
  ];
  return {
    version: 1, picture: {fpsNum: fps, fpsDen: 1, frameCount}, initialUI: null,
    events: events.map(({name, ...event}) => ({id: `recreate.train.${name}`, ...event})),
    cues: events.slice(1).map(({name}) => ({
      id: `recreate.train.${name}.cue`, eventId: `recreate.train.${name}`, offsetSamples: 0,
    })),
  };
}

function rise(layer, first, last, distance) {
  return {
    ...layer,
    start: toSeconds(first),
    keyframes: {
      y: [
        {t: toSeconds(first), value: layer.y + distance},
        {t: toSeconds(last), value: layer.y, ease: 'easeOut'},
      ],
    },
  };
}

function selectionControl(selected) {
  const outline = rect('seat-selection-body', 274, 41, 18, 18, '#ffffff', 5, {
    stroke: '#9b99ac', strokeWidth: 1.5, end: toSeconds(selected),
  });
  const check = group('seat-selection-checked', 274, 41, [
    rect('seat-selection-fill', 0, 0, 18, 18, '#5755c6', 5),
    {id: 'seat-selection-mark', type: 'path', d: 'M 4 9 L 7.5 12.5 L 14 5.5',
      fill: 'none', stroke: '#ffffff', strokeWidth: 1.7},
  ], {start: toSeconds(selected)});
  return [outline, check];
}

function buildScene(copy, selectAt) {
  const drawer = rise(BottomSheet({
    id: 'drawer', x: 20, y: 135, width: 324, height: 118, title: 'Pick a train',
    children: [
      rect('first-train-background', 14, 36, 296, 30, '#ffffff', 8),
      text('first-train-time', '18:40', 24, 42, 15, {fontWeight: 600}),
      text('first-train-seats', '2 window seats', 89, 43, 14, {fill: '#777b84'}),
      ...selectionControl(selectAt),
      rect('second-train-background', 14, 72, 296, 30, '#ffffff', 8),
      text('second-train-time', '19:10', 24, 78, 15, {fontWeight: 600}),
      text('second-train-seats', '4 seats', 89, 79, 14, {fill: '#777b84'}),
      rect('second-train-selection', 274, 77, 18, 18, '#ffffff', 5, {
        stroke: '#9b99ac', strokeWidth: 1.5,
      }),
    ],
  }), 56, 66, 29);
  const heading = drawer.children.find(layer => layer.id === 'drawer-heading');
  heading.y = 15;
  heading.fontSize = 16;
  drawer.end = toSeconds(89);

  const phone = PhoneFrame({
    id: 'phone', x: 138, y: 34, width: 364, height: 292, title: 'Rail Planner',
    children: [
      MessageBubble({
        id: 'offer', x: 21, y: 72, width: 186, height: 40, side: 'incoming',
        copy: offerCopy, fontSize: 14,
      }),
      rise(MessageBubble({
        id: 'request', x: 115, y: 116, width: 222, height: 40, copy, fontSize: 14,
      }), 30, 38, 8),
      Composer({id: 'composer', x: 19, y: 236, width: 326, active: false}),
      drawer,
      rise(MessageBubble({
        id: 'receipt', x: 21, y: 194, width: 194, height: 40, side: 'incoming',
        copy: receiptCopy, fontSize: 14,
      }), 89, 96, 7),
    ],
  });
  phone.start = toSeconds(18);
  return {
    width: 640, height: 360, fps, duration: toSeconds(frameCount), background: backdrop,
    timeline: timeline(copy, selectAt),
    layers: [
      group('title-shot', 0, 0, [
        rect('title-background', 0, 0, 640, 360, '#242342'),
        text('title-kicker', 'RAIL PLANNER', 320, 126, 13, {
          fill: '#c2befa', textAnchor: 'middle', letterSpacing: 2.2, fontWeight: 700,
        }),
        text('title-copy', 'Train options', 320, 151, 47, {
          fill: '#ffffff', textAnchor: 'middle', fontWeight: 700,
        }),
      ], {end: toSeconds(18)}),
      phone,
    ],
  };
}

function segment(scene, first, last) {
  if (![first, last].every(Number.isInteger) || first < 0 || last < first || last >= frameCount) {
    throw new Error('Expected an inclusive in-film range such as 70:83.');
  }
  const rebase = time => toSeconds(Math.round(time * fps) - first);
  function shiftLayer(layer) {
    const result = {...layer};
    if (layer.start !== undefined) result.start = rebase(layer.start);
    if (layer.end !== undefined) result.end = rebase(layer.end);
    if (layer.children) result.children = layer.children.map(shiftLayer);
    if (layer.keyframes) {
      result.keyframes = {};
      for (const [key, values] of Object.entries(layer.keyframes)) {
        if (values.at(-1).t <= toSeconds(first)) result[key] = values.at(-1).value;
        else if (values[0].t >= toSeconds(last)) result[key] = values[0].value;
        else {
          // Evaluate the original curves at native frames before shifting the origin.
          result.keyframes[key] = Array.from({length: last - first + 1}, (_, local) => ({
            t: toSeconds(local),
            value: sampleTrack(values, toSeconds(first + local)),
          }));
        }
      }
      if (!Object.keys(result.keyframes).length) delete result.keyframes;
    }
    return result;
  }
  const {events, cues} = scene.timeline;
  const carriedState = events.filter(event => event.frame < first && 'uiState' in event).at(-1);
  const visibleEvents = events.filter(event => first <= event.frame && event.frame <= last)
    .map(event => ({...event, frame: event.frame - first}));
  const visibleIds = new Set(visibleEvents.map(event => event.id));
  const length = last - first + 1;
  return {
    ...scene, duration: toSeconds(length), layers: scene.layers.map(shiftLayer),
    timeline: {
      ...scene.timeline, picture: {fpsNum: fps, fpsDen: 1, frameCount: length},
      initialUI: carriedState ? carriedState.uiState : scene.timeline.initialUI,
      events: visibleEvents, cues: cues.filter(cue => visibleIds.has(cue.eventId)),
    },
  };
}

const [out, ...args] = process.argv.slice(2);
if (!out || args.length % 2) {
  throw new Error('Usage: node scene.mjs OUT [--config JSON] [--segment FIRST:LAST] [--events MAP]');
}
const options = new Map();
for (let index = 0; index < args.length; index += 2) {
  const key = args[index];
  if (!['--config', '--segment', '--events'].includes(key) || options.has(key)) throw new Error(`Unexpected option ${key}`);
  options.set(key, args[index + 1]);
}
const config = options.has('--config')
  ? JSON.parse(readFileSync(options.get('--config'), 'utf8'))
  : {};
const {copy = 'Two seats to Union Station.', selectionFrame = 74} = config;
if (typeof copy !== 'string' || !copy.trim() || !Number.isInteger(selectionFrame)
  || selectionFrame < 66 || selectionFrame >= 89) {
  throw new Error('Provide nonempty message copy and a selection frame from 66 through 88.');
}
const range = options.get('--segment');
if (range && !/^\d+:\d+$/.test(range)) throw new Error('Invalid segment range.');
const fullScene = buildScene(copy, selectionFrame);
const scene = range ? segment(fullScene, ...range.split(':').map(Number)) : fullScene;
writeFileSync(out, JSON.stringify(scene, null, 2) + '\n');
if (options.has('--events')) writeFileSync(options.get('--events'), JSON.stringify(scene.timeline, null, 2) + '\n');
