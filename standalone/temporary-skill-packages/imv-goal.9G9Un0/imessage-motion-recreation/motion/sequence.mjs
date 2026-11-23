import {stateAt} from '../scripts/engines/common.mjs';

const freezeLayer = (layer, t, duration) => {
  const {start = 0, end = duration, keyframes, children, ...state} = stateAt(layer, t);
  if (t < start || t >= end) return null;
  return children ? {...state, children: children.map(child => freezeLayer(child, t, duration)).filter(Boolean)} : state;
};

function hold(scene, after) {
  const {fps, duration, timeline} = scene;
  const time = after ? (timeline.picture.frameCount - 1) / fps : 0;
  let initialUI = timeline.initialUI;
  for (const event of timeline.events) {
    if (event.frame / fps > time) break;
    if (Object.hasOwn(event, 'uiState')) initialUI = event.uiState;
  }
  return {
    ...scene,
    title: 'Reading hold',
    source: {notes: 'Snapshot of the adjacent editable scene.'},
    duration: 1,
    layers: scene.layers.map(layer => freezeLayer(layer, time, duration)).filter(Boolean),
    timeline: {...timeline, picture: {...timeline.picture, frameCount: fps}, initialUI, events: [], cues: []},
  };
}

/** A null part requests a one-second hold on the adjoining shot.
 * Every boundary resets semantic UI and all action/cue IDs remain resolvable.
 */
export function composeScenes(input) {
  const firstMotion = input.find(Boolean);
  if (!firstMotion) throw Error('A reading hold needs a scene to hold');
  if (input.length === 1) return firstMotion;
  let previous;
  const parts = input.map(part => {
    if (part) { previous = part; return part; }
    return hold(previous ?? firstMotion, Boolean(previous));
  });
  const first = parts[0];
  let frames = 0;
  const layers = [];
  const events = [];
  const cues = [];
  const fonts = new Map();
  for (const [index, part] of parts.entries()) {
    if (part.width !== first.width || part.height !== first.height || part.fps !== first.fps)
      throw Error('Sequence parts need one canvas and picture rate');
    const beat = `beat-${index + 1}`;
    const prefix = beat + '.';
    const start = frames / first.fps;
    const beatFrames = part.timeline.picture.frameCount;
    const end = (frames + beatFrames) / first.fps;
    const offset = layer => ({
      ...layer, id: prefix + layer.id,
      ...(layer.start === undefined ? {} : {start: start + layer.start}),
      ...(layer.end === undefined ? {} : {end: start + layer.end}),
      ...(layer.children ? {children: layer.children.map(offset)} : {}),
      ...(layer.keyframes ? {keyframes: Object.fromEntries(
        Object.entries(layer.keyframes).map(([key, track]) => [key, track.map(k => ({...k, t: k.t + start}))]),
      )} : {}),
    });
    const backdrop = {id: prefix + 'scene-background', type:'rect', width:first.width, height:first.height, fill:part.background};
    layers.push({id:beat, type:'group', start, end, children:[backdrop, ...part.layers.map(offset)]});
    const frameZeroChange = part.timeline.events.some(event => event.frame === 0 && Object.hasOwn(event, 'uiState'));
    if (index > 0 && !frameZeroChange) events.push({
      id:prefix + 'cut', kind:'shot.cut', target:beat, frame:frames, layerIds:[beat], uiState:part.timeline.initialUI,
    });
    for (const event of part.timeline.events) {
      const layerIds = event.layerIds ?? [];
      events.push({
        ...event, id:prefix + event.id, frame:event.frame + frames,
        target:layerIds.includes(event.target) ? prefix + event.target : event.target,
        layerIds:layerIds.map(id => prefix + id),
      });
    }
    for (const cue of part.timeline.cues)
      cues.push({...cue, id:prefix + cue.id, eventId:prefix + cue.eventId});
    for (const font of part.fonts ?? []) fonts.set(JSON.stringify(font), font);
    frames += beatFrames;
  }
  return {
    ...first,
    duration: frames / first.fps,
    title: parts.map(part => part.title).join(' / '),
    source: {notes: parts.map(part => part.source.path
      ? `${part.source.path} [${part.source.sourceStart}, ${part.source.sourceEnd})`
      : part.source.notes).join(' then ')},
    layers,
    ...(fonts.size ? {fonts:[...fonts.values()]} : {}),
    timeline: {...first.timeline, picture:{...first.timeline.picture, frameCount:frames}, events, cues},
  };
}
