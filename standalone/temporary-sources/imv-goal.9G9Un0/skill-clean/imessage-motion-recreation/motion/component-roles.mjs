const adapterRecipes = {
  'photos-under-fixed-heading': {
    moving: ['carousel'], fixed: ['screen', 'header', 'composer', 'transcript', 'attachmentViewport'],
    required: ['viewport', 'message', 'attachment'], transitionKinds: ['media.page'],
  },
  'conversation-handoff': {
    moving: ['draft', 'sendButton', 'message', 'reply'], fixed: ['screen', 'header'],
    required: ['viewport', 'composer', 'transcript'], transitionKinds: ['draft', 'send', 'receive'],
  },
  'composer-type': {
    moving: ['draft', 'sendButton'], fixed: ['screen', 'header', 'transcript'],
    required: ['viewport', 'composer'], transitionKinds: ['draft'],
  },
  'draft-send-flight': {
    moving: ['draft', 'sendButton', 'message'], fixed: ['screen', 'header'],
    required: ['viewport', 'composer', 'transcript'], transitionKinds: ['send'],
  },
  'typing-indicator-cycle': {
    moving: ['typing'], fixed: ['screen', 'header', 'composer'],
    required: ['viewport', 'transcript'], transitionKinds: ['typing'],
  },
  'reply-makes-room': {
    moving: ['reply', 'transcript'], fixed: ['screen', 'header', 'viewport', 'composer'],
    required: [], transitionKinds: ['receive'],
  },
  'delivery-receipt-handoff': {
    moving: ['message', 'receipt'], fixed: ['screen', 'header'],
    required: ['viewport', 'composer', 'transcript'], transitionKinds: ['send', 'receipt'],
  },
  'long-press-actions': {
    moving: ['contextMenu'], fixed: ['screen', 'header', 'composer'],
    required: ['viewport', 'transcript', 'message'], transitionKinds: ['overlay'],
  },
  'reaction-attach': {
    moving: ['contextMenu', 'reaction'], fixed: ['screen', 'header', 'composer'],
    required: ['viewport', 'transcript', 'message'], transitionKinds: ['overlay', 'reaction'],
  },
  'edit-message-reflow': {
    moving: ['message'], fixed: ['screen', 'header', 'composer'],
    required: ['viewport', 'transcript'], transitionKinds: ['edit'],
  },
  'undo-send-remove': {
    moving: ['message'], fixed: ['screen', 'header', 'composer'],
    required: ['viewport', 'transcript'], transitionKinds: ['unsend'],
  },
  'keyboard-focus-reflow': {
    moving: ['keyboard', 'composer', 'transcript'], fixed: ['screen', 'header'],
    required: ['viewport'], transitionKinds: ['focus'],
  },
  'app-drawer': {
    moving: ['appDrawer'], fixed: ['screen', 'header', 'composer'],
    required: ['viewport', 'transcript'], transitionKinds: ['overlay'],
  },
};

// Each study names its primary moving role and the local component anchors it
// demonstrates. Remaining moving layers are returned separately as supporting actors.
const studies = {
  'photos-under-fixed-heading': ['carousel', 'photo-rail', {header: 'heading', attachmentViewport: 'photo-viewport',
    divider: 'photo-rail-divider', caption: 'footer-label'}],
  'heading-over-fixed-photos': ['heading', 'heading-copy', {carousel: 'photo-rail', attachmentViewport: 'photo-viewport',
    headingBand: 'heading', caption: 'footer-label'}],
  'conversation-handoff': ['message', /^(sent|reply|composer-input)$/, {composer: 'composer', phone: 'phone', header: 'contact'}],
  'composer-type': ['draft', 'type-draft-input', {composer: 'type-draft', header: 'heading'}],
  'draft-send-flight': ['message', 'send-outgoing', {composer: 'send-draft', header: 'heading'}],
  'typing-indicator-cycle': ['typing', /^waiting-(indicator|dot-)/, {composer: 'waiting-composer', header: 'heading'}],
  'reply-makes-room': ['reply', 'arrival-new-reply', {composer: 'arrival-composer', priorMessage: 'arrival-outgoing'}],
  'delivery-receipt-handoff': ['receipt', /^receipt-(old|new)-status$/, {composer: 'receipt-composer', header: 'heading'}],
  'long-press-actions': ['contextMenu', 'actions-context-menu', {message: 'actions-selected', composer: 'actions-composer'}],
  'reaction-attach': ['reaction', 'reaction-badge', {composer: 'reaction-composer', header: 'heading'}],
  'transcript-timestamp-peek': ['transcript', 'peek-bubble-column', {composer: 'peek-composer', header: 'heading'}],
  'swipe-to-quote': ['message', 'quote-message', {composer: 'quote-composer', header: 'heading'}],
  'inline-thread-open': ['reply', /^thread-reply-/, {composer: 'thread-composer', header: 'heading'}],
  'edit-message-reflow': ['message', /^edit-original-/, {composer: 'edit-composer', header: 'heading'}],
  'undo-send-remove': ['message', 'undo-outgoing', {composer: 'undo-composer', header: 'heading'}],
  'history-prepend-anchor': ['transcript', 'prepend-transcript', {composer: 'prepend-composer', header: 'heading'}],
  'jump-to-unread': ['transcript', 'unread-transcript', {composer: 'unread-composer', header: 'heading'}],
  'keyboard-focus-reflow': ['keyboard', 'focus-keyboard', {header: 'heading'}],
  'link-preview-upgrade': ['attachment', 'link-preview-surface', {composer: 'link-composer', attachmentViewport: 'link-metadata-window'}],
  'send-failure-retry': ['message', 'failed-outgoing', {composer: 'failed-composer', header: 'heading'}],
  'schedule-send-wheel': ['scheduleWheel', 'schedule-wheel', {composer: 'schedule-draft', wheelViewport: 'schedule-wheel-window'}],
  'batch-select-messages': ['transcript', 'batch-transcript', {header: 'heading'}],
  'pin-conversation-avatar': ['avatar', 'pin-traveling-avatar', {header: 'heading'}],
  'camera-push-in': ['camera', 'camera-plane', {cameraViewport: 'stage'}],
  'camera-truck-between': ['camera', 'lateral-camera', {cameraViewport: 'stage'}],
  'depth-parallax': ['depthPlanes', /^(far-grid|middle-cards|near-frame)$/, {cameraViewport: 'stage'}],
  'rack-focus': ['focusPlanes', /^(far|near)-object$/, {cameraViewport: 'stage'}],
  'typographic-tracking-contract': ['type', 'tracking-title', {baseline: 'center-axis'}],
  'step-indicator-travel': ['stepIndicator', 'active-step', {rail: 'progress-rail'}],
  'metric-wheel-roll': ['valueWheel', 'value-wheel', {wheelViewport: 'metric-window', baseline: 'metric-baseline'}],
  'comparison-bars-grow': ['comparisonBars', /^(earlier|later)-bar$/, {baseline: 'baseline', benchmark: 'benchmark'}],
  'trend-line-trace': ['plotTrace', /^(trend-segment|active-plot-point)/, {axis: 'vertical-axis'}],
  'grid-reflow': ['gridCards', /^reflow-card-/, {board: 'reflow-board'}],
  'accordion-displaces-row': ['accordion', 'accordion-surface', {header: 'accordion-title'}],
  'exploded-layer-view': ['assembly', /^layer-plane-/, {viewport: 'stage'}],
  'spotlight-cross-text': ['spotlight', /^(shade-left|shade-right|spotlight-edge)$/, {labelLeft: 'target-left', labelRight: 'target-right'}],
  'signals-merge-routes': ['routeSignals', /^(input-\d+|joined-pulse)$/, {route: 'shared-route'}],
  'signal-radiation': ['radioWaves', /^signal-ring-/, {origin: 'signal-source'}],
  'freeze-around-live-detail': ['activeDetail', 'live-point', {rail: 'active-lane'}],
  'items-collapse-into-count': ['countedItems', /^counted-item-/, {counterSurface: 'tally-surface'}],
  'registered-shape-cut': ['matchedScenes', /^(from|to)-scene$/, {viewport: 'stage',
    previousShape: 'app-glyph', resultingShape: 'matched-feature-button'}],
  'objects-pass-behind': ['passingObjects', /^(left|right)-payload$/, {occluder: 'bridge'}],
  'needle-sweeps-threshold': ['gaugeNeedle', 'gauge-needle', {pivot: 'needle-pivot', viewport: 'stage'}],
  'message-wall': ['message', /^wall-message-/, {header: 'heading'}],
  'app-drawer': ['appDrawer', 'drawer', {priorMessage: 'message', phone: 'phone'}],
  'identity-morph': ['identity', 'identity-surface', {viewport: 'stage'}],
  'circle-to-panel': ['panel', 'morph-surface', {viewport: 'stage'}],
  'mini-app-expand': ['attachment', 'mini-app', {priorMessage: 'request', composer: 'composer', phone: 'phone'}],
  'selection-confirm': ['selection', /^selection-card-action-/, {selectionCard: 'selection-card'}],
  'card-orbit': ['orbitalCards', /^orbit-card-\d$/, {viewport: 'stage'}],
  'messages-attachment-stack': ['attachment', /^attachment-\d$/, {composer: 'stack-composer', header: 'heading'}],
  'inline-card-expand': ['appDrawer', 'detail-sheet', {attachment: 'inline-preview', header: 'heading'}],
  'avatar-ring-assemble': ['avatar', /^portrait-\d$/, {viewport: 'stage'}],
  'tear-perforated-ticket': ['ticket', 'ticket-stub', {ticketBody: 'main-ticket'}],
  'message-pin-landing': ['locationPin', 'mapped-cue', {priorMessage: 'location-query', map: 'map-area'}],
  'photo-open-continuity': ['attachment', 'chosen-thumbnail', {viewport: 'stage'}],
  'photo-pinch-detail': ['attachment', 'pinch-frame-image', {attachmentViewport: 'pinch-frame'}],
  'photo-crop-reframe': ['attachment', 'crop-photo', {attachmentViewport: 'crop-frame'}],
  'photo-compare-wipe': ['comparisonDivider', 'comparison-divider', {attachmentViewport: 'comparison-frame', beforeImage: 'comparison-before'}],
  'photo-album-deal': ['attachment', /^album-tile-\d$/, {label: 'album-deal-label'}],
  'media-video-scrub': ['playhead', 'scrub-thumb', {attachmentViewport: 'scrub-viewer', timelineRail: 'scrub-rail'}],
  'media-trim-range': ['trimHandles', /^trim-(in|out)-handle$/, {timelineFilmstrip: 'trim-filmstrip'}],
  'attachment-peek-release': ['attachment', 'peek-attachment', {
    leftNeighbor: 'peek-left-neighbor', rightNeighbor: 'peek-right-neighbor', viewport: 'stage'}],
  'card-reorder-insert': ['attachment', 'reorder-first', {viewport: 'stage'}],
  'media-progressive-sharpen': ['attachment', /^decode-band-/, {attachmentViewport: 'decode-photo'}],
  'media-caption-disclosure': ['caption', 'caption-detail', {attachment: 'caption-photo', control: 'caption-control'}],
  'photo-iris-reveal': ['attachmentMask', 'iris-mask', {attachmentViewport: 'iris-viewport'}],
  'album-page-turn': ['albumPage', /^turning-(front|back)$/, {cover: 'page-cover', spine: 'album-crease'}],
  'photo-grid-density': ['attachment', /^density-tile-\d$/, {viewport: 'stage'}],
  'attachment-download-progress': ['downloadProgress', 'download-progress', {attachment: 'download-icon',
    filename: 'download-title', rail: 'download-rail'}],
  'photo-markup-stroke': ['annotation', /^markup-segment-/, {attachment: 'markup-photo'}],
  'location-question-bridge': ['attachment', 'shared-location-map', {header: 'heading'}],
  'screen-to-physical-prop': ['phone', 'prop-handset', {screen: 'editable-handset-screen'}],
  'metric-count': ['metric', 'metric-value', {header: 'heading'}],
  'text-scramble-resolve': ['type', /^decoded-glyph-/, {header: 'heading'}],
  'center-gutter-open': ['panels', /^(left|right)-panel$/, {header: 'heading'}],
  'hinged-swatch-fan': ['swatches', /^leaf-(left|right)$/, {centerSwatch: 'leaf-center'}],
};

export function roleSpecification(entry) {
  const study = studies[entry.id];
  if (!study) throw Error(`Missing component study for ${entry.id}`);
  const adapter = adapterRecipes[entry.id];
  if (adapter) {
    const {moving, fixed, transitionKinds} = adapter;
    return {study, production: {mode: 'adapter-recipe', moving, fixed,
      required: [...new Set([...adapter.required, ...moving, ...fixed])], transitionKinds,
      verification: 'Validate explicit bindings on the compiled scene and review decoded frames from that candidate.'}};
  }
  const primitive = entry.implementation === 'packs/editorial.mjs' || entry.implementation === 'packs/attention.mjs'
    || ['heading-over-fixed-photos', 'identity-morph', 'circle-to-panel', 'card-orbit', 'avatar-ring-assemble',
      'tear-perforated-ticket'].includes(entry.id);
  const fixed = Object.keys(study[2]);
  const required = entry.id === 'media-video-scrub'
    ? ['screen', 'composer', 'attachmentViewport', 'videoSource', 'timelineRail', 'playhead']
    : [study[0], ...fixed];
  return {study, production: {
    mode: primitive ? 'primitive-only' : entry.id === 'media-video-scrub' ? 'depiction-only' : 'needs-authoring',
    moving: [study[0]], fixed, required, transitionKinds: [],
    verification: 'Requires a separately authored binding and visual proof on a Messages scene.',
  }};
}
