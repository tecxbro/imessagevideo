import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {stateAt} from '../scripts/engines/common.mjs';
import {byId, describe} from './catalog.mjs';
import {roleSpecification} from './component-roles.mjs';
import {buildMotion} from './scene.mjs';

const assetRoot = fileURLToPath(new URL('./assets/', import.meta.url));
const catalogRoot = fileURLToPath(new URL('../../../', import.meta.url));
const fixedChannels = ['x', 'y', 'scaleX', 'scaleY', 'rotation', 'originX', 'originY', 'width', 'height', 'clip'];
const adapterMessage = /^ui\.message\/[^/@]+$/;

const adapterRoles = {
  screen: {id: 'ui.screen', type: 'group', clip: true},
  viewport: {id: 'ui.viewport', type: 'group', parent: 'screen', clip: true},
  header: {id: 'ui.header', type: 'group', parent: 'screen'},
  composer: {id: 'ui.composer', type: 'group', parent: 'screen'},
  draft: {pattern: /^ui\.composer\.draft(?:@\d+)?$/, types: ['text', 'group'], parent: 'composer', revision: true},
  sendButton: {pattern: /^ui\.composer\.send(?:@\d+)?$/, types: ['rect', 'group'], parent: 'composer', revision: true},
  transcript: {id: 'ui.transcript', type: 'group', parent: 'viewport'},
  message: {pattern: adapterMessage, type: 'group', parent: 'transcript'},
  reply: {pattern: adapterMessage, type: 'group', parent: 'transcript'},
  typing: {id: 'ui.typing', type: 'group', parent: 'transcript'},
  keyboard: {id: 'ui.keyboard', type: 'group', parent: 'screen'},
  receipt: {suffix: 'receipt', type: 'group', parent: 'message'},
  reaction: {suffix: 'reaction', type: 'group', parent: 'message'},
  contextMenu: {id: 'ui.overlay', type: 'group', parent: 'screen'},
  appDrawer: {id: 'ui.overlay', type: 'group', parent: 'screen'},
  attachment: {suffix: 'media', type: 'group', parent: 'message'},
  attachmentViewport: {suffix: 'media-window', type: 'group', parent: 'attachment', clip: true},
  carousel: {suffix: 'rail', type: 'group', parent: 'attachmentViewport'},
};

function indexScene(scene) {
  if (!Array.isArray(scene?.layers)) throw Error('Motion bindings require an editable scene with layers');
  const nodes = new Map();
  function visit(layers, parent) {
    for (const node of layers) {
      if (typeof node.id !== 'string' || !node.id || nodes.has(node.id)) {
        throw Error(`Invalid or duplicate layer ID: ${node.id}`);
      }
      nodes.set(node.id, {node, parent});
      visit(node.children ?? [], node.id);
    }
  }
  visit(scene.layers, null);
  return nodes;
}

function changes(keys) {
  return new Set(keys.map(key => JSON.stringify(key.value))).size > 1;
}

function localAsset(src) {
  if (typeof src !== 'string' || !path.isAbsolute(src) || !src.startsWith(assetRoot)) {
    throw Error(`Expected bundled Motion demo artwork: ${src}`);
  }
  return {
    path: path.relative(catalogRoot, src),
    sha256: createHash('sha256').update(readFileSync(src)).digest('hex'),
  };
}

/** Generate inspection metadata from a recipe's current editable demo scene. */
export function describeMotionComponents(id) {
  const entry = byId.get(id);
  if (!entry) throw Error(`Unknown motion ID: ${id}`);
  const {study: [primaryRole, primaryLayers, anchors], production} = roleSpecification(entry);
  const scene = buildMotion(entry);
  const nodes = indexScene(scene);
  const isPrimary = typeof primaryLayers === 'string'
    ? candidate => candidate === primaryLayers : candidate => primaryLayers.test(candidate);
  const moving = [];
  const assetPaths = new Set();
  for (const [layerId, {node, parent}] of nodes) {
    if (node.src) assetPaths.add(node.src);
    const channels = Object.entries(node.keyframes ?? {}).filter(([, keys]) => changes(keys)).map(([key]) => key);
    if ((node.start ?? 0) > 0 || (node.end ?? scene.duration) < scene.duration) {
      channels.push('visibilityInterval');
    }
    if (channels.length) moving.push({
      id: layerId, parent, type: node.type, channels, role: isPrimary(layerId) ? primaryRole : 'supportingActor',
    });
  }
  if (!moving.some(layer => layer.role === primaryRole)) {
    throw Error(`Motion ${id} is missing its primary demo actor: ${primaryLayers}`);
  }
  const fixed = Object.entries(anchors).map(([role, layerId]) => {
    const actor = nodes.get(layerId);
    if (!actor) throw Error(`Motion ${id} is missing its demo anchor: ${layerId}`);
    const varying = moving.find(layer => layer.id === layerId);
    if (varying?.channels.some(channel => fixedChannels.includes(channel) || channel === 'visibilityInterval')) {
      throw Error(`Motion ${id} moves its fixed-position demo anchor: ${layerId}`);
    }
    return {id: layerId, parent: actor.parent, type: actor.node.type, role, scope: 'local-position'};
  });
  const verified = describe(entry);
  const events = scene.timeline.events.map(({id: eventId, kind, frame, target, layerIds}) => {
    if (layerIds.some(layerId => !nodes.has(layerId))) throw Error(`Unknown layer in event ${eventId}`);
    return {id: eventId, kind, frame, target, layerIds};
  });
  return {
    id, implementation: `motion/${entry.implementation}`,
    whenToUse: entry.fits, avoidWhen: entry.avoid, source: entry.source,
    preview: verified.preview ? {path: verified.preview, sha256: verified.sha256, evidence: 'published-demo'} : null,
    adapterPreview: verified.ui ? {path: verified.ui.preview, sha256: verified.ui.sha256, evidence: 'published-adapter-demo'} : null,
    demo: {moving, fixed, events, assets: [...assetPaths].map(localAsset)},
    production: {
      ...production,
      bindings: production.mode === 'adapter-recipe' ? Object.fromEntries(production.required.map(role => {
        const spec = adapterRoles[role];
        return [role, {...spec, ...(spec.pattern ? {pattern: spec.pattern.source} : {})}];
      })) : null,
    },
  };
}

function descendsFrom(nodes, id, ancestor) {
  for (let current = nodes.get(id)?.parent; current; current = nodes.get(current).parent) {
    if (current === ancestor) return true;
  }
  return false;
}

function activeAt(nodes, id, scene, frame) {
  const t = frame / scene.fps;
  for (let current = id; current; current = nodes.get(current).parent) {
    const state = stateAt(nodes.get(current).node, t);
    if (t < (state.start ?? 0) || t >= (state.end ?? scene.duration) || state.opacity <= 0) return false;
  }
  return true;
}

function fixedDuring(nodes, id, scene, first, last) {
  for (let current = id; current; current = nodes.get(current).parent) {
    const {node} = nodes.get(current);
    const relevant = fixedChannels.filter(channel => node.keyframes?.[channel] && changes(node.keyframes[channel]));
    if (relevant.length === 0) continue;
    const before = stateAt(node, first / scene.fps);
    for (let frame = first + 1; frame <= last; frame += 1) {
      const currentState = stateAt(node, frame / scene.fps);
      if (relevant.some(channel => JSON.stringify(before[channel]) !== JSON.stringify(currentState[channel]))) {
        return false;
      }
    }
  }
  return true;
}

/** Resolve adapter component IDs against the actual selected conversation actions. */
export function inferAdapterBindings(id, scene, eventIds) {
  const entry = byId.get(id);
  if (!entry) throw Error(`Unknown motion ID: ${id}`);
  const {production} = roleSpecification(entry);
  if (production.mode !== 'adapter-recipe') throw Error(`${id} has no adapter recipe`);
  if (!Array.isArray(eventIds) || eventIds.length === 0 || new Set(eventIds).size !== eventIds.length) {
    throw Error('Name the selected conversation event IDs');
  }
  const timeline = scene?.timeline;
  if (!timeline?.initialUI || !Array.isArray(timeline.events)) throw Error('Missing editable conversation timeline');
  const byEvent = new Map(timeline.events.map(event => [event.id, event]));
  if (byEvent.size !== timeline.events.length) throw Error('Duplicate conversation event ID');
  const selected = eventIds.map(eventId => {
    const event = byEvent.get(eventId);
    if (!event) throw Error(`Conversation event is absent: ${eventId}`);
    return event;
  });
  const expected = production.transitionKinds;
  const correctKinds = id === 'composer-type'
    ? selected.length >= 2 && selected.every(event => event.kind === 'draft')
    : expected.length === selected.length && selected.every((event, index) => event.kind === expected[index]);
  if (!correctKinds || selected.some((event, index) => index > 0 && event.frame <= selected[index - 1].frame)) {
    throw Error(`${id} needs these ordered conversation actions: ${expected.join(', ')}`);
  }

  const overlay = selected.find(event => event.kind === 'overlay');
  if (overlay) {
    const surface = id === 'app-drawer' ? 'tray' : 'context';
    if (overlay.uiState?.viewport?.surface !== surface) throw Error(`Expected the ${surface} overlay`);
  }
  const outgoing = selected.find(event => event.kind === 'send');
  const incoming = selected.find(event => event.kind === 'receive');
  const target = selected.find(event => ['reaction', 'receipt', 'media.page', 'edit', 'unsend'].includes(event.kind));
  const messageId = outgoing?.target ?? target?.target ?? overlay?.target;
  if (outgoing && target && outgoing.target !== target.target) throw Error('Receipt target differs from the selected send');
  if (overlay && target && overlay.target !== target.target) throw Error('Reaction target differs from the selected context');
  if (id === 'typing-indicator-cycle' && !selected[0].uiState?.typingSenderIds?.includes(selected[0].target)) {
    throw Error('Expected the selected remote participant to begin typing');
  }
  if (id === 'keyboard-focus-reflow' && !selected[0].uiState?.composer?.keyboardVisible) {
    throw Error('Expected the selected focus action to show the keyboard');
  }

  const bindings = {};
  const composerFrame = outgoing ? Math.max(0, outgoing.frame - 1) : selected.at(-1).frame;
  const nodes = indexScene(scene);
  for (const role of production.required) {
    const spec = adapterRoles[role];
    if (spec.id) bindings[role] = spec.id;
    else if (role === 'message' && messageId) bindings.message = `ui.message/${messageId}`;
    else if (role === 'reply' && incoming?.target) bindings.reply = `ui.message/${incoming.target}`;
    else if (spec.suffix && messageId) bindings[role] = `ui.message/${messageId}/${spec.suffix}`;
    else if (spec.revision) {
      const active = [...nodes.keys()].filter(layerId => spec.pattern.test(layerId) &&
        activeAt(nodes, layerId, scene, composerFrame));
      if (active.length !== 1) throw Error(`Expected one visible ${role} on native frame ${composerFrame}`);
      bindings[role] = active[0];
    }
  }
  return bindings;
}

/** Validate a binding on an adapter scene. Pixel fidelity and effect coverage need decoded evidence. */
export function validateMotionBinding(id, {scene, bindings = {}, eventIds, window} = {}) {
  const entry = byId.get(id);
  if (!entry) throw Error(`Unknown motion ID: ${id}`);
  const {production} = roleSpecification(entry);
  const issues = [];
  let checkedWindow;
  const done = () => ({ok: issues.length === 0, mode: production.mode, issues, evidence: 'structural-only',
    ...(checkedWindow ? {checkedWindow} : {})});
  if (production.mode !== 'adapter-recipe') {
    issues.push({code: 'production-application-unavailable', motion: id});
    return done();
  }
  if (!scene?.timeline?.initialUI) issues.push({code: 'missing-conversation-state'});
  const nodes = indexScene(scene);
  const inferred = eventIds === undefined ? {} : inferAdapterBindings(id, scene, eventIds);
  const used = new Set();
  for (const role of production.required) {
    const layerId = bindings[role];
    const actor = nodes.get(layerId);
    if (!actor) {
      issues.push({code: 'missing-component', role, layerId});
      continue;
    }
    const expected = adapterRoles[role];
    const wrongId = expected.id && layerId !== expected.id || expected.pattern && !expected.pattern.test(layerId)
      || expected.suffix && !layerId.endsWith(`/${expected.suffix}`);
    const {width, height} = actor.node.clip ?? {};
    const wrongClip = expected.clip && ![width, height].every(size => Number.isFinite(size) && size > 0);
    if (wrongId || !(expected.types ?? [expected.type]).includes(actor.node.type) || wrongClip) {
      issues.push({code: 'wrong-component', role, layerId});
    }
    if (expected.parent && !descendsFrom(nodes, layerId, bindings[expected.parent])) {
      issues.push({code: 'wrong-component-parent', role, layerId, parent: expected.parent});
    }
    if (inferred[role] && inferred[role] !== layerId) {
      issues.push({code: 'wrong-event-component', role, layerId, expected: inferred[role]});
    }
    if (used.has(layerId)) issues.push({code: 'duplicate-component', role, layerId});
    used.add(layerId);
  }
  if (!window) return done();
  const [start, last] = window;
  const firstEvent = scene.timeline?.events?.find(event => event.id === eventIds?.[0]);
  const first = firstEvent?.frame === start ? Math.max(0, start - 1) : start;
  const total = scene.timeline?.picture?.frameCount;
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(last) || start < 0 || first >= last || last >= total
      || !Number.isFinite(scene.fps) || scene.fps <= 0) {
    throw Error('Validation window must contain at least two native frames within the scene');
  }
  checkedWindow = [first, last];
  for (const role of production.fixed) {
    const layerId = bindings[role];
    if (!nodes.has(layerId)) continue;
    for (let frame = first; frame <= last; frame += 1) {
      if (activeAt(nodes, layerId, scene, frame)) continue;
      issues.push({code: 'inactive-fixed-component', role, layerId, frame});
      break;
    }
    const targets = role === 'header'
      ? [layerId, ...[...nodes.keys()].filter(id => descendsFrom(nodes, id, layerId))]
      : [layerId];
    if (targets.some(id => !fixedDuring(nodes, id, scene, first, last))) {
      issues.push({code: 'moves-fixed-component', role, layerId, window: checkedWindow});
    }
  }
  return done();
}
