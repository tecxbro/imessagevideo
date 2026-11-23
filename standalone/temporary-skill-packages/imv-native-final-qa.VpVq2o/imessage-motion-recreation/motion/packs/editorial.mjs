// Original Motion demonstrations. The source ranges refer to the authored
// 2.4-second previews. These entries are suggestions for editorial use.

const label = (ctx, id, value, x, y, size, extra = {}) => ctx.text(id, value, x, y, size, {
  fill: ctx.colors.ink, fontWeight: 600, ...extra,
});

function caption(ctx, value) {
  ctx.footer.children.push(label(ctx, 'editorial-caption', value, 22, 9, 15, {fill: ctx.colors.muted}));
}

function tile(ctx, id, x, y, width, height, title, fill = ctx.colors.paper) {
  const {rect, group, colors} = ctx;
  return group(id, x, y, [
    rect(id + '-surface', 0, 0, width, height, fill, 16, {stroke: colors.light, strokeWidth: 1}),
    label(ctx, id + '-label', title, 16, 14, 18),
    rect(id + '-detail', 16, 45, Math.max(16, width - 44), 5, colors.light, 2),
  ]);
}

function lineBetween(ctx, id, from, to, fill = ctx.colors.blue, size = 4) {
  const dx = to[0] - from[0];
  const dy = to[1] - from[1];
  return ctx.rect(id, from[0], from[1] - size / 2, Math.hypot(dx, dy), size, fill, size / 2, {
    originY: size / 2, rotation: Math.atan2(dy, dx) * 180 / Math.PI,
  });
}

function marker(ctx, id, x, y, diameter, fill = ctx.colors.blue) {
  return {id, type: 'circle', x: x - diameter / 2, y: y - diameter / 2, width: diameter, height: diameter, fill};
}

function pushIn(ctx) {
  const {stage, group, rect, track, event, content, colors} = ctx;
  const detail = tile(ctx, 'detail', 174, 100, 154, 90, content.title);
  const cameraPlane = group('camera-plane', 0, 0, [
    rect('workspace', 26, 29, 448, 242, colors.light, 24),
    tile(ctx, 'neighbor-left', 42, 100, 111, 80, 'Overview'),
    detail,
    tile(ctx, 'neighbor-right', 348, 100, 110, 80, 'History'),
    rect('detail-focus', 187, 162, 110, 8, colors.blue, 4),
  ], {originX: 251, originY: 145});
  for (const property of ['scaleX', 'scaleY']) {
    track(cameraPlane, property, [[0, .91], [.16, .91], [.68, 1.68, 'easeInOut']]);
  }
  stage.children.push(cameraPlane);
  caption(ctx, content.detail);
  event('push-start', .16, cameraPlane.id);
  event('detail-in-frame', .68, detail.id);
}

function truckBetween(ctx) {
  const {stage, group, track, event, content, colors} = ctx;
  const cards = group('lateral-camera', 0, 0, [
    tile(ctx, 'left-destination', 99, 91, 302, 109, content.copy),
    tile(ctx, 'right-destination', 425, 91, 302, 109, content.title),
  ]);
  const index = marker(ctx, 'position-index', 236, 235, 8);
  stage.children.push(cards, marker(ctx, 'index-track', 264, 235, 8, colors.light), index);
  track(cards, 'x', [[0, 0], [.19, 0], [.69, -326, 'easeInOut']]);
  track(index, 'x', [[0, 232], [.19, 232], [.69, 260, 'easeInOut']]);
  caption(ctx, content.detail);
  event('truck-start', .19, cards.id);
  event('next-region-framed', .69, 'right-destination');
}

function parallax(ctx) {
  const {stage, group, rect, track, event, content, colors} = ctx;
  const background = group('far-grid', 0, 0, Array.from({length: 10}, (_, i) =>
    rect('grid-line-' + i, 24 + i * 51, 30, 1, 238, colors.light)));
  const cards = group('middle-cards', 0, 0, [
    tile(ctx, 'far-card', 75, 78, 180, 108, 'Workspace'),
    tile(ctx, 'mid-card', 236, 108, 180, 107, content.title),
  ]);
  const foreground = group('near-frame', 0, 0, [
    rect('foreground-edge', 12, 49, 44, 205, colors.blue, 16),
    rect('foreground-dot', 26, 67, 16, 16, colors.paper, 8),
  ]);
  for (const [plane, distance] of [[background, -11], [cards, -41], [foreground, -94]]) {
    track(plane, 'x', [[0, 0], [.1, 0], [.74, distance, 'easeInOut']]);
  }
  stage.children.push(background, cards, foreground);
  caption(ctx, content.detail);
  event('depth-shift-start', .1, foreground.id);
  event('planes-settle', .74, cards.id);
}

function rackFocus(ctx) {
  const {stage, track, event, content} = ctx;
  const far = tile(ctx, 'far-object', 198, 53, 236, 124, content.title);
  const near = tile(ctx, 'near-object', 58, 128, 242, 122, content.copy);
  track(far, 'blur', [[0, 6], [.32, 6], [.59, 0, 'easeInOut']]);
  track(near, 'blur', [[0, 0], [.32, 0], [.59, 6, 'easeInOut']]);
  track(near, 'opacity', [[0, 1], [.32, 1], [.59, .58, 'easeInOut']]);
  stage.children.push(far, near);
  caption(ctx, content.detail);
  event('focus-shift-start', .32, near.id);
  event('far-object-sharp', .59, far.id);
}

function consolidateTracking(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const headline = label(ctx, 'tracking-title', content.title, 250, 109, 44, {textAnchor: 'middle'});
  const baseline = rect('center-axis', 249, 170, 2, 32, colors.light);
  track(headline, 'letterSpacing', [[0, 14], [.16, 14], [.57, 0, 'easeOut']]);
  stage.children.push(headline, baseline);
  caption(ctx, content.detail);
  event('tracking-contracts', .16, headline.id);
  event('title-readable', .57, headline.id);
}

function stepIndicator(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const centers = [96, 250, 404];
  const positions = [56, 210, 364];
  const steps = [content.copy, content.title, content.action];
  stage.children.push(rect('progress-rail', 55, 104, 390, 4, colors.light, 2));
  const active = rect('active-step', positions[0], 103, 80, 6, colors.blue, 3);
  track(active, 'x', [[0, positions[0]], [.22, positions[0]], [.36, positions[1], 'easeOut'], [.57, positions[1]], [.73, positions[2], 'easeOut']]);
  stage.children.push(active);
  for (const [i, value] of steps.entries()) {
    stage.children.push(label(ctx, 'step-label-' + i, value, centers[i], 132, 18, {textAnchor: 'middle'}));
    const dot = marker(ctx, 'step-dot-' + i, centers[i], 105, 11, colors.paper);
    dot.stroke = colors.blue;
    dot.strokeWidth = 2;
    stage.children.push(dot);
  }
  stage.children.push(label(ctx, 'sequence-purpose', content.detail, 250, 193, 24, {textAnchor: 'middle'}));
  event('middle-step', .36, 'step-dot-1');
  event('final-step', .73, 'step-dot-2');
}

function rollValue(ctx) {
  const {stage, rect, group, track, event, content, colors} = ctx;
  const glyphs = group('value-wheel', 0, 0, [content.copy, content.title, content.reply].map((value, i) =>
    label(ctx, 'wheel-value-' + i, value, 135, i * 66 + 7, 43, {textAnchor: 'middle'})));
  track(glyphs, 'y', [[0, 0], [.18, 0], [.33, -66, 'easeOut'], [.45, -66], [.65, -132, 'easeOut']]);
  stage.children.push(
    label(ctx, 'metric-label', content.heading, 250, 60, 20, {textAnchor: 'middle'}),
    rect('metric-window-bg', 115, 103, 270, 66, colors.light, 12),
    group('metric-window', 115, 103, [glyphs], {clip: {width: 270, height: 66, radius: 12}}),
    rect('metric-baseline', 115, 179, 270, 2, colors.blue, 1),
  );
  caption(ctx, content.detail);
  event('value-turned', .33, 'wheel-value-1');
  event('value-lands', .65, 'wheel-value-2');
}

function compareBars(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const barHeight = (index, fallback) => {
    const value = content.values?.[index];
    return Math.max(0, Math.min(100, Number.isFinite(value) ? value : fallback)) * 1.54;
  };
  const values = [
    {id: 'earlier-bar', x: 120, height: barHeight(0, 55), fill: colors.muted, time: .48, name: content.copy},
    {id: 'later-bar', x: 285, height: barHeight(1, 99), fill: colors.blue, time: .66, name: content.title},
  ];
  for (const data of values) {
    const bar = rect(data.id, data.x, 219, 95, 1, data.fill, 4, {originY: 0});
    const endY = 220 - data.height;
    track(bar, 'y', [[0, 219], [.18, 219], [data.time, endY, 'easeOut']]);
    track(bar, 'height', [[0, 1], [.18, 1], [data.time, data.height, 'easeOut']]);
    stage.children.push(bar, label(ctx, data.id + '-label', data.name, data.x + 47, 232, 17, {textAnchor: 'middle'}));
  }
  stage.children.push(
    rect('baseline', 70, 220, 362, 2, colors.ink),
    rect('benchmark', 70, 114, 362, 1, colors.red),
    label(ctx, 'benchmark-label', 'Target', 435, 105, 13, {fill: colors.red}),
  );
  caption(ctx, content.detail);
  event('first-value-settled', .48, 'earlier-bar');
  event('second-value-settled', .66, 'later-bar');
}

function tracePlot(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const points = [[53, 222], [149, 166], [239, 179], [336, 107], [447, 65]].map(([x, y], i) => {
    const value = content.values?.[i];
    return [x, Number.isFinite(value) ? 222 - Math.max(0, Math.min(100, value)) * 1.57 : y];
  });
  const times = [.14, .29, .41, .55, .69];
  for (const y of [65, 118, 171, 224]) {
    stage.children.push(rect('reference-grid-' + y, 50, y, 398, 1, colors.light));
  }
  stage.children.push(rect('vertical-axis', 50, 60, 2, 168, colors.muted));
  for (let i = 1; i < points.length; i++) {
    const segment = lineBetween(ctx, 'trend-segment-' + i, points[i - 1], points[i]);
    track(segment, 'scaleX', [[0, 0], [times[i - 1], 0], [times[i], 1]]);
    stage.children.push(segment);
  }
  const tip = marker(ctx, 'active-plot-point', ...points[0], 13);
  for (const [axis, origin] of [['x', 0], ['y', 1]]) {
    track(tip, axis, times.map((time, i) => [time, points[i][origin] - 6.5]));
  }
  stage.children.push(tip, label(ctx, 'trend-result', content.title, 437, 30, 18, {textAnchor: 'end'}));
  caption(ctx, content.detail);
  event('plot-trace-start', .14, 'trend-segment-1');
  event('plot-final-point', .69, tip.id);
}

function gridReflow(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const start = [[44, 57], [255, 57], [44, 154], [255, 154]];
  // Every card owns its continuous path, so a reordered card keeps its identity.
  const end = [[38, 189], [38, 41], [264, 41], [264, 137]];
  const names = [content.copy, content.title, content.action, content.reply];
  const board = rect('reflow-board', 22, 27, 456, 244, colors.light, 22);
  stage.children.push(board);
  for (const [i, name] of names.entries()) {
    const card = tile(ctx, 'reflow-card-' + i, ...start[i], 196, 70, name);
    const onset = .13 + i * .04;
    const lane = i === 0 ? 15 : end[i][0];
    track(card, 'x', [[0, start[i][0]], [onset, start[i][0]], [.40, lane, 'easeInOut'], [.67, end[i][0], 'easeOut']]);
    track(card, 'y', [[0, start[i][1]], [onset, start[i][1]], [.67, end[i][1], 'easeInOut']]);
    stage.children.push(card);
  }
  caption(ctx, content.detail);
  event('layout-reflow-start', .13, 'reflow-card-0');
  event('grid-reordered', .67, board.id);
}

function expandAccordion(ctx) {
  const {stage, rect, group, track, event, content, colors} = ctx;
  const panel = rect('accordion-surface', 63, 70, 374, 48, colors.light, 14);
  const body = label(ctx, 'expanded-copy', content.detail, 85, 125, 18);
  const following = group('following-row', 63, 128, [
    rect('following-surface', 0, 0, 374, 48, colors.paper, 14, {stroke: colors.light, strokeWidth: 1}),
    label(ctx, 'following-label', content.reply, 22, 12, 18),
  ]);
  const caret = lineBetween(ctx, 'disclosure-caret', [391, 95], [410, 95], colors.blue, 4);
  caret.originX = 9.5;
  track(panel, 'height', [[0, 48], [.18, 48], [.57, 122, 'easeInOut']]);
  track(following, 'y', [[0, 128], [.18, 128], [.57, 202, 'easeInOut']]);
  track(body, 'opacity', [[0, 0], [.36, 0], [.61, 1, 'easeOut']]);
  track(caret, 'rotation', [[0, 90], [.18, 90], [.57, 0, 'easeInOut']]);
  stage.children.push(panel, label(ctx, 'accordion-title', content.title, 85, 82, 18), following, body, caret);
  event('accordion-opens', .18, panel.id);
  event('detail-exposed', .61, body.id);
}

function separateLayers(ctx) {
  const {stage, rect, group, track, event, content, colors} = ctx;
  const panels = [content.reply, content.action, content.title];
  for (const [i, value] of panels.entries()) {
    const plane = group('layer-plane-' + i, 104 + i * 7, 93 + i * 7, [
      rect('layer-surface-' + i, 0, 0, 236, 92, i === 2 ? colors.blue : colors.paper, 18, {
        stroke: colors.blue, strokeWidth: 2,
      }),
      label(ctx, 'layer-caption-' + i, value, 14, 35, 17, {
        fill: i === 2 ? colors.paper : colors.ink,
      }),
    ]);
    track(plane, 'x', [[0, plane.x], [.17, plane.x], [.64, 45 + i * 87, 'easeInOut']]);
    track(plane, 'y', [[0, plane.y], [.17, plane.y], [.64, 153 - i * 41, 'easeInOut']]);
    track(plane, 'rotation', [[0, 0], [.17, 0], [.64, -8, 'easeInOut']]);
    stage.children.push(plane);
  }
  caption(ctx, content.detail);
  event('assembly-separates', .17, 'layer-plane-2');
  event('layers-separated', .64, 'layer-plane-0');
}

function spotlightText(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const width = 186;
  const lefts = [32, 282];
  const labels = [content.copy, content.title, content.reply];
  stage.children.push(
    label(ctx, 'target-left', labels[0], 128, 122, 25, {textAnchor: 'middle'}),
    label(ctx, 'target-right', labels[1], 375, 122, 25, {textAnchor: 'middle'}),
    label(ctx, 'context-top', labels[2], 250, 63, 18, {textAnchor: 'middle'}),
    rect('shade-above', 0, 0, 500, 108, colors.light, 0, {opacity: .88}),
    rect('shade-below', 0, 167, 500, 131, colors.light, 0, {opacity: .88}),
  );
  const left = rect('shade-left', 0, 108, lefts[0], 59, colors.light, 0, {opacity: .88});
  const right = rect('shade-right', lefts[0] + width, 108, 500 - width - lefts[0], 59, colors.light, 0, {opacity: .88});
  const rim = rect('spotlight-edge', lefts[0], 108, width, 59, 'none', 0, {stroke: colors.blue, strokeWidth: 2});
  const sweep = (from, to) => [[0, from], [.23, from], [.61, to, 'easeInOut']];
  track(left, 'width', sweep(...lefts));
  track(right, 'x', sweep(...lefts.map(x => x + width)));
  track(right, 'width', sweep(...lefts.map(x => 500 - width - x)));
  track(rim, 'x', sweep(...lefts));
  stage.children.push(left, right, rim);
  caption(ctx, content.detail);
  event('spotlight-start', .23, rim.id);
  event('phrase-in-spotlight', .61, 'target-right');
}

function mergeRoutes(ctx) {
  const {stage, track, event, content, colors} = ctx;
  const sources = [[77, 79], [77, 220]];
  const junction = [255, 150];
  const destination = [421, 150];
  for (const [i, point] of sources.entries()) {
    stage.children.push(lineBetween(ctx, 'branch-' + i, point, junction, colors.muted, 2));
  }
  stage.children.push(lineBetween(ctx, 'shared-route', junction, destination, colors.muted, 2));
  const branches = sources.map(([x, y], i) => {
    const pulse = marker(ctx, 'input-' + i, x, y, 19, i === 0 ? colors.blue : colors.green);
    const onset = .15 + i * .08;
    for (const [property, value, end] of [['x', x, junction[0]], ['y', y, junction[1]]]) {
      track(pulse, property, [[0, value - 9.5], [onset, value - 9.5], [.52, end - 9.5, 'easeInOut']]);
    }
    track(pulse, 'opacity', [[0, 1], [.52, 0, 'hold']]);
    return pulse;
  });
  const joined = marker(ctx, 'joined-pulse', ...junction, 21, colors.blue);
  track(joined, 'opacity', [[0, 0], [.52, 1, 'hold']]);
  track(joined, 'x', [[.52, junction[0] - 10.5], [.79, destination[0] - 10.5, 'easeInOut']]);
  stage.children.push(...branches, joined,
    label(ctx, 'input-upper', content.copy, 33, 37, 17),
    label(ctx, 'input-lower', content.reply, 33, 245, 17),
    label(ctx, 'output', content.title, 418, 103, 18, {textAnchor: 'middle'}),
  );
  caption(ctx, content.detail);
  event('inputs-merge', .52, joined.id);
  event('result-arrives', .79, joined.id);
}

function radiate(ctx) {
  const {stage, track, event, content, colors} = ctx;
  const source = marker(ctx, 'signal-source', 250, 147, 43);
  for (let i = 0; i < 3; i++) {
    const ring = marker(ctx, 'signal-ring-' + i, 250, 147, 44, 'none');
    Object.assign(ring, {originX: 22, originY: 22, stroke: colors.blue, strokeWidth: 2});
    const onset = .14 + i * .10;
    const end = onset + .39;
    for (const property of ['scaleX', 'scaleY']) {
      track(ring, property, [[0, 1], [onset, 1], [end, 4.3, 'easeOut']]);
    }
    track(ring, 'opacity', [[0, 0], [onset, .61, 'hold'], [end, 0, 'easeIn']]);
    stage.children.push(ring);
  }
  stage.children.push(source,
    label(ctx, 'signal-top', content.title, 250, 22, 21, {textAnchor: 'middle'}),
    label(ctx, 'signal-bottom', content.action, 250, 237, 18, {textAnchor: 'middle'}),
  );
  caption(ctx, content.detail);
  event('signal-emitted', .14, source.id);
  event('last-wave-clears', .73, 'signal-ring-2');
}

function freezeSurroundings(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  stage.children.push(
    rect('top-flow-lane', 28, 55, 442, 34, colors.light, 17),
    rect('bottom-flow-lane', 28, 210, 442, 34, colors.light, 17),
    rect('active-lane', 28, 122, 442, 55, colors.paper, 20, {stroke: colors.blue, strokeWidth: 1}),
  );
  for (let i = 0; i < 6; i++) {
    const lo = i % 2 === 0 ? 72 : 227;
    const flow = marker(ctx, 'ambient-point-' + i, 55 + Math.floor(i / 2) * 89, lo, 13, colors.muted);
    track(flow, 'x', [[0, flow.x], [.33, flow.x + 119], [.82, flow.x + 119, 'hold']]);
    stage.children.push(flow);
  }
  const cursor = marker(ctx, 'live-point', 71, 149, 20);
  track(cursor, 'x', [[0, cursor.x], [.33, cursor.x + 119], [.73, cursor.x + 358, 'easeOut']]);
  stage.children.push(
    cursor,
    label(ctx, 'focus-lane-title', content.title, 250, 179, 19, {textAnchor: 'middle'}),
    label(ctx, 'freeze-status', content.action, 34, 25, 16, {fill: colors.muted}),
  );
  caption(ctx, content.detail);
  event('surroundings-freeze', .33, 'ambient-point-0');
  event('live-point-arrives', .73, cursor.id);
}

function collapseToTally(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const count = label(ctx, 'total-value', '0', 395, 108, 48, {textAnchor: 'middle', fill: colors.blue});
  const arrivals = [.43, .56, .69];
  stage.children.push(
    rect('tally-surface', 339, 82, 112, 142, colors.light, 22),
    count,
    label(ctx, 'tally-label', content.title, 395, 177, 15, {textAnchor: 'middle'}),
  );
  for (const [i, name] of [content.copy, content.reply, content.action].entries()) {
    const arrival = arrivals[i];
    const start = .15 + i * .09;
    const card = tile(ctx, 'counted-item-' + i, 42 + i * 74, 145, 115, 72, name);
    card.originX = 57.5;
    card.originY = 36;
    track(card, 'x', [[0, card.x], [start, card.x], [arrival, 337.5, 'easeInOut']]);
    track(card, 'y', [[0, card.y], [start, card.y], [(start + arrival) / 2, 75, 'easeOut'], [arrival, 112, 'easeIn']]);
    for (const property of ['scaleX', 'scaleY']) {
      track(card, property, [[0, 1], [start, 1], [arrival, .12, 'easeIn']]);
    }
    track(card, 'opacity', [[0, 1], [arrival - .04, 1], [arrival, 0, 'easeIn']]);
    stage.children.push(card);
    event('item-' + (i + 1) + '-counted', arrival, count.id);
  }
  track(count, 'text', [[0, '0'], ...arrivals.map((time, i) => [time, String(i + 1), 'hold'])]);
  caption(ctx, content.detail);
}

function cutOnShape(ctx) {
  const {stage, rect, group, track, event, content, colors} = ctx;
  const cut = .49;
  const left = group('from-scene', 0, 0, [
    rect('project-window', 41, 45, 418, 211, colors.light, 26),
    label(ctx, 'old-surface-title', content.copy, 69, 69, 21),
    rect('app-glyph', 185, 119, 130, 60, colors.blue, 29),
    label(ctx, 'app-glyph-label', content.action, 250, 135, 18, {textAnchor: 'middle', fill: colors.paper}),
  ]);
  const right = group('to-scene', 0, 0, [
    rect('next-scene-window', 41, 45, 418, 211, colors.ink, 26),
    label(ctx, 'next-surface-title', content.title, 69, 69, 21, {fill: colors.paper}),
    rect('matched-feature-button', 185, 119, 130, 60, colors.blue, 29),
    label(ctx, 'matched-action-label', content.action, 250, 135, 18, {textAnchor: 'middle', fill: colors.paper}),
  ]);
  track(left, 'opacity', [[0, 1], [cut, 0, 'hold']]);
  track(right, 'opacity', [[0, 0], [cut, 1, 'hold']]);
  const feature = label(ctx, 'new-context-description', content.detail, 250, 197, 18, {
    textAnchor: 'middle', fill: colors.paper,
  });
  track(feature, 'opacity', [[0, 0], [.55, 0], [.71, 1, 'easeOut']]);
  right.children.push(feature);
  stage.children.push(left, right);
  event('registered-cut', cut, 'matched-feature-button');
  event('new-context-readable', .71, feature.id);
}

function passBehind(ctx) {
  const {stage, rect, track, event, content, colors} = ctx;
  const left = tile(ctx, 'left-payload', 22, 114, 144, 76, content.copy, colors.light);
  const right = tile(ctx, 'right-payload', 334, 116, 144, 72, content.title);
  track(left, 'x', [[0, 22], [.17, 22], [.72, 334, 'easeInOut']]);
  track(right, 'x', [[0, 334], [.17, 334], [.72, 22, 'easeInOut']]);
  // The fixed bridge is above both payloads, so neither can cross in front.
  stage.children.push(left, right,
    rect('bridge', 172, 79, 156, 140, colors.ink, 18),
    label(ctx, 'bridge-label', content.action, 250, 130, 21, {textAnchor: 'middle', fill: colors.paper}),
  );
  caption(ctx, content.detail);
  // At these crossings, the moving edge first intersects each side of the cover.
  event('payloads-enter-occlusion', .263, 'bridge');
  event('payloads-emerge', .449, 'left-payload');
}

function sweepGauge(ctx) {
  const {stage, track, event, content, colors} = ctx;
  const pivot = [246, 181];
  const polar = (degrees, radius) => [
    pivot[0] + Math.cos(degrees * Math.PI / 180) * radius,
    pivot[1] + Math.sin(degrees * Math.PI / 180) * radius,
  ];
  const angles = [-165, -140, -115, -90, -65, -40, -15];
  const rawTarget = content.values?.[0];
  const value = Number.isFinite(rawTarget) ? Math.max(0, Math.min(100, rawTarget)) : 84;
  const target = -165 + 1.5 * value;
  for (const [i, angle] of angles.entries()) {
    stage.children.push(lineBetween(ctx, 'gauge-tick-' + i, polar(angle, 99), polar(angle, 119),
      i >= 4 ? colors.green : colors.muted, 5));
  }
  const needle = lineBetween(ctx, 'gauge-needle', pivot, polar(-154, 104), colors.blue, 6);
  const overshoot = Math.max(-165, Math.min(-15, target + Math.sign(target + 154) * 5));
  track(needle, 'rotation', [[0, -154], [.18, -154], [.62, overshoot, 'easeOut'], [.71, target, 'easeInOut']]);
  stage.children.push(needle, marker(ctx, 'needle-pivot', ...pivot, 17, colors.ink),
    label(ctx, 'gauge-label', content.title, 250, 211, 24, {textAnchor: 'middle'}),
    label(ctx, 'gauge-min', content.copy, 73, 190, 16),
    label(ctx, 'gauge-max', content.action, 421, 190, 16, {textAnchor: 'end'}),
  );
  caption(ctx, content.detail);
  event('needle-start', .18, needle.id);
  event('needle-settled', .71, needle.id);
}

export const entries = [
  {
    id: 'camera-push-in',
    title: 'Push the camera toward a detail',
    moves: 'The camera plane scales around a chosen detail, taking its neighboring cards toward the edges.',
    fixed: 'The focal point, the cards’ arrangement within the camera plane, and the surrounding frame.',
    notice: 'The detail belongs to the same workspace established at the start.',
    fits: 'Lead into an important control or small result that was hard to read in the overview.',
    avoid: 'A push implies looking closer. Use a state change if the product itself opens or grows.',
    intents: ['zoom into the booking detail', 'move the camera closer to one detail', 'focus in on a card without changing its layout'],
    editable: ['heading', 'title', 'detail'],
    defaults: {heading: 'Trip planner', title: 'Reservation', detail: 'The booking stays in the same workspace.'},
    build: pushIn,
  },
  {
    id: 'camera-truck-between',
    title: 'Pan the camera across neighboring workspaces',
    moves: 'A horizontal camera pan moves the view between adjacent panels. A small index marks the next destination.',
    fixed: 'Magnification, destination sizes and spacing, the viewing window, and the surrounding heading.',
    notice: 'The second view is next to the first on the same plane.',
    fits: 'Show a connection between adjacent panels or identify the next stop in an established horizontal layout.',
    avoid: 'A lateral camera move implies adjacency. A distant location needs a different transition.',
    intents: ['pan across to the neighboring destination', 'move the camera sideways between two product areas', 'displace the camera horizontally to reach the panel beside this one'],
    editable: ['heading', 'copy', 'title', 'detail'],
    defaults: {heading: 'One workspace', copy: 'Plan', title: 'Check out', detail: 'The next destination sits on the same surface.'},
    build: truckBetween,
  },
  {
    id: 'depth-parallax',
    title: 'Shift foreground, middle and background at different rates',
    moves: 'The foreground crosses quickly, the middle cards move a shorter distance, and the grid barely shifts.',
    fixed: 'The drawing window and the relative arrangement of objects on each plane.',
    notice: 'Different rates disclose depth between established planes.',
    fits: 'Reveal spatial layers or give a lateral product view a credible sense of depth.',
    avoid: 'Differential speed implies depth or independent planes. It can misstate a flat, rigid interface.',
    intents: ['make the foreground travel faster than the background', 'use parallax across the feature', 'show three planes shifting at different rates'],
    editable: ['heading', 'title', 'detail'],
    defaults: {heading: 'Layered workspace', title: 'Controls', detail: 'Near objects cover more distance.'},
    build: parallax,
  },
  {
    id: 'rack-focus',
    title: 'Transfer focus between two stationary planes',
    moves: 'Sharpness shifts from the near card to the far card. The near card softens in place.',
    fixed: 'Both cards’ positions and silhouettes, the frame, and the heading.',
    notice: 'The subject in the back becomes the point of attention even though its position never changes.',
    fits: 'Pass attention between subjects while preserving their positions and sense of depth.',
    avoid: 'Blur makes wording temporarily unreadable. Keep both clear for simultaneous comparisons.',
    intents: ['pull focus from the front object to the one behind it', 'keep both cards in place and rack focus to the far card', 'blur the foreground as the background sharpens'],
    editable: ['heading', 'copy', 'title', 'detail'],
    defaults: {heading: 'Two planes', copy: 'Overview', title: 'Specific result', detail: 'Focus moves toward the result behind the overview.'},
    build: rackFocus,
  },
  {
    id: 'typographic-tracking-contract',
    title: 'Draw the letters of a title into reading position',
    moves: 'Letter spacing contracts toward the center without changing the word or type size.',
    fixed: 'The title’s center and baseline, its wording, and the axis underneath.',
    notice: 'Dispersed characters resolve into one readable phrase.',
    fits: 'Settle a short title at the end of a reveal, especially when the idea is convergence or agreement.',
    avoid: 'The initial tracking slows reading. Keep the spacing stable for long or urgent copy.',
    intents: ['pull the spread-out letters together into a readable word', 'tighten the title tracking around its center', 'bring the spaced-out characters together without moving the title block'],
    editable: ['heading', 'title', 'detail'],
    defaults: {heading: 'Title treatment', title: 'Together', detail: 'The text reaches normal tracking and holds.'},
    build: consolidateTracking,
  },
  {
    id: 'step-indicator-travel',
    title: 'Move the active indicator through three fixed steps',
    moves: 'An underline travels to the second step, holds, then travels to the third.',
    fixed: 'All step labels, the rail, and the explanatory line.',
    notice: 'The movement represents progression through an ordered set of stages.',
    fits: 'Show a workflow reaching successive checkpoints without moving the actual controls.',
    avoid: 'The indicator implies active progression. A set of unrelated options needs a different cue.',
    intents: ['advance the active underline across three fixed steps', 'show progress through stages with a moving tab marker', 'move a progress indicator from one fixed label to the next'],
    editable: ['heading', 'copy', 'title', 'action', 'detail'],
    defaults: {heading: 'Guided booking', copy: 'Choose', title: 'Review', action: 'Reserve', detail: 'Three steps to a reservation'},
    build: stepIndicator,
  },
  {
    id: 'metric-wheel-roll',
    title: 'Roll a value through a fixed readout window',
    moves: 'Three values roll upward through a narrow clipped readout and stop at the final value.',
    fixed: 'Width and position of the readout, its baseline, and the metric label.',
    notice: 'One metric changes over time, with a marked starting value and a readable final value.',
    fits: 'Represent an increasing count or visibly changing ordinal state in an instrument-like readout.',
    avoid: 'A rolling readout suggests ordered progression. Keep unrelated labels out of a numeric roll.',
    intents: ['roll the number like an odometer', 'bring each new metric value up through a fixed window', 'change the count with a vertical number wheel'],
    editable: ['heading', 'copy', 'title', 'reply', 'detail'],
    defaults: {heading: 'Completed bookings', copy: '28', title: '39', reply: '42', detail: 'The final count remains visible.'},
    build: rollValue,
  },
  {
    id: 'comparison-bars-grow',
    title: 'Grow two comparison bars from a shared baseline',
    moves: 'Both bars grow upward from the same baseline and stop at their own value.',
    fixed: 'The baseline, the target line, and the two category labels.',
    notice: 'The second bar clears the target line while the first falls short in the default example.',
    fits: 'Compare quantitative magnitudes with a shared reference and readable final state.',
    avoid: 'Bar growth emphasizes size. Unordered categories or different units should use a different treatment.',
    intents: ['grow two bars from a common baseline and compare them to a target', 'animate a before and after bar chart', 'show which column crosses the fixed benchmark line'],
    editable: ['heading', 'copy', 'title', 'detail', 'values'],
    defaults: {heading: 'Bookings per week', copy: 'Earlier', title: 'Now', detail: 'Two values share one scale.'},
    editNotes: 'Provide two values on a 0–100 scale. The first controls the earlier bar and the second controls the later bar.',
    build: compareBars,
  },
  {
    id: 'trend-line-trace',
    title: 'Trace a trend through the points of a chart',
    moves: 'A leading point traverses the chart and leaves the completed segments behind.',
    fixed: 'Grid lines, axes, and the endpoints of the plotted values.',
    notice: 'Ordering matters. The retained path makes the direction and reversals legible.',
    fits: 'Reveal how a trend developed across a series of points.',
    avoid: 'A traced path implies an ordered series. Use independent bars for unrelated categories.',
    intents: ['draw the trend across a chart over time', 'follow a data point along a growing line graph', 'trace the trend through five points and leave the line behind'],
    editable: ['heading', 'title', 'detail', 'values'],
    defaults: {heading: 'Booking activity', title: 'Weekly trend', detail: 'The trace keeps the earlier changes visible.'},
    editNotes: 'Provide five values on a 0–100 scale, one per point from left to right.',
    build: tracePlot,
  },
  {
    id: 'grid-reflow',
    title: 'Reflow four cards while keeping them recognizable',
    moves: 'Each card follows an individual path into a changed grid order.',
    fixed: 'Card copy and proportions, the board, and the heading.',
    notice: 'The same cards survive the layout change, even as reading order shifts.',
    fits: 'Make a changed sort or rearranged layout clear without losing track of the items.',
    avoid: 'A reflow suggests continuity of the existing set. If new items replace old ones, show that replacement.',
    intents: ['rearrange four cards and keep the same items visible', 'reflow a dashboard grid after changing the sort', 'show the same tiles moving into a new layout'],
    editable: ['heading', 'copy', 'title', 'action', 'reply', 'detail'],
    defaults: {heading: 'Sort by priority', copy: 'Archive', title: 'Due today', action: 'Next', reply: 'Waiting', detail: 'The same cards land in a different order.'},
    build: gridReflow,
  },
  {
    id: 'accordion-displaces-row',
    title: 'Expand a disclosure and make room for its details',
    moves: 'The first row grows down, its indicator rotates, and the following row makes space below it.',
    fixed: 'The top edge of the first row, the row titles, and the surrounding viewport.',
    notice: 'The details belong to the opening row, and the lower row remains part of the layout.',
    fits: 'Show details disclosed inside a vertically stacked list with physical reflow.',
    avoid: 'The push down implies that the content occupies layout space. Use an overlay for temporary detail.',
    intents: ['open an accordion section and push the row beneath it down', 'reveal details inline within a list', 'expand the disclosure without overlaying the next row'],
    editable: ['heading', 'title', 'detail', 'reply'],
    defaults: {heading: 'Reservation details', title: 'Timing', detail: 'Hold expires after fifteen minutes.', reply: 'Travel information'},
    build: expandAccordion,
  },
  {
    id: 'exploded-layer-view',
    title: 'Separate a compact assembly into visible layers',
    moves: 'Three stacked planes spread diagonally, keeping a shared orientation as their edges separate.',
    fixed: 'Each layer’s own geometry, border, and label.',
    notice: 'The assembly contains separate working surfaces that belong together.',
    fits: 'Explain how a view is composed or which layer handles each responsibility.',
    avoid: 'The offset stack implies an assembly. Independent products should not look like layers of one interface.',
    intents: ['show the parts by pulling apart an exploded stack', 'separate the overlapping UI layers to explain their anatomy', 'break the assembled product view into three depth planes'],
    editable: ['heading', 'reply', 'action', 'title', 'detail'],
    defaults: {heading: 'Layer anatomy', reply: 'Surface', action: 'Tools', title: 'Content', detail: 'Three editable planes make one assembly.'},
    build: separateLayers,
  },
  {
    id: 'spotlight-cross-text',
    title: 'Move a spotlight across fixed phrases',
    moves: 'A bounded opening in a dim overlay travels from one phrase to the next.',
    fixed: 'All the text, its position, type, and spacing. The overlay keeps its height.',
    notice: 'The next phrase becomes current while earlier context stays visible in low contrast.',
    fits: 'Direct the eye to different phrases in a fixed diagram or copy layout.',
    avoid: 'Moving a spotlight reduces contrast outside the window. Use uniform contrast when the viewer must read all content at once.',
    intents: ['highlight the next phrase without moving the words', 'sweep a spotlight over fixed text', 'use an aperture to pick out one phrase at a time'],
    editable: ['heading', 'copy', 'title', 'reply', 'detail'],
    defaults: {heading: 'Two ways to book', copy: 'Pick a time', title: 'Reserve now', reply: 'Choose one action', detail: 'The words stay in place as the highlight moves.'},
    build: spotlightText,
  },
  {
    id: 'signals-merge-routes',
    title: 'Merge two incoming routes into one outgoing result',
    moves: 'Two signals travel along separate pathways and combine at the junction. One outgoing packet continues along the shared route.',
    fixed: 'The branch geometry, junction, endpoints and labels.',
    notice: 'Independent inputs are combined before the result is delivered.',
    fits: 'Explain joins, aggregation, or collaboration with a clear point of convergence.',
    avoid: 'A single outgoing marker implies a real merge. Use separate paths if the inputs reach distinct results.',
    intents: ['merge two input signals into one output at a junction', 'animate data coming down two branches and joining a shared route', 'show a workflow combining two sources into one result'],
    editable: ['heading', 'copy', 'reply', 'title', 'detail'],
    defaults: {heading: 'Booking workflow', copy: 'Availability', reply: 'Preferences', title: 'Reservation', detail: 'The inputs meet before the result moves on.'},
    build: mergeRoutes,
  },
  {
    id: 'signal-radiation',
    title: 'Send concentric signal waves from one point',
    moves: 'Thin rings grow out from one source and fade at successive distances.',
    fixed: 'The source itself, heading, and explanatory text.',
    notice: 'A single originating action propagates outward to its surroundings.',
    fits: 'Show broadcasting, discovery, or a ripple of system activity from one source.',
    avoid: 'Radial expansion implies broad propagation. Use a routed movement for a directed delivery.',
    intents: ['send waves outward from a single source', 'broadcast from one point with expanding rings', 'make the signal radiate while the central node stays put'],
    editable: ['heading', 'title', 'action', 'detail'],
    defaults: {heading: 'Discovery', title: 'Source online', action: 'Broadcast', detail: 'Successive waves indicate propagation from one source.'},
    build: radiate,
  },
  {
    id: 'freeze-around-live-detail',
    title: 'Freeze surrounding movement while one detail keeps going',
    moves: 'Peripheral activity stops mid-travel. One point in the center keeps moving to its destination.',
    fixed: 'The tracks stay fixed throughout. After the stop, all peripheral points hold their exact positions.',
    notice: 'One process remains relevant while competing activity pauses.',
    fits: 'Isolate a still-running process in a dense animated wash of other activity.',
    avoid: 'Arresting activity changes the perceived system state. If all processes are running, use a highlight that preserves them.',
    intents: ['freeze the surrounding activity while the central process keeps moving', 'arrest background motion and keep the important point moving', 'pause competing lanes and leave one live'],
    editable: ['heading', 'action', 'title', 'detail'],
    defaults: {heading: 'Activity feed', action: 'Background paused', title: 'Priority task', detail: 'Only the priority lane continues.'},
    build: freezeSurroundings,
  },
  {
    id: 'items-collapse-into-count',
    title: 'Convert individual items into a tally',
    moves: 'Each item takes a short arc into a counter, shrinks away at arrival, and advances the count.',
    fixed: 'The count surface, the label underneath it, and the overall framing.',
    notice: 'Every count increase corresponds to one specific arriving item.',
    fits: 'Show completion, aggregation, or the number of processed items.',
    avoid: 'A disappearing item implies conversion into a summary. Keep entities in separate cards when they still matter individually.',
    intents: ['collect each item into a count and increment the tally on arrival', 'make completed cards collapse into a counter', 'show that three distinct objects add up to a total'],
    editable: ['heading', 'title', 'copy', 'reply', 'action', 'detail'],
    defaults: {heading: 'Processed tasks', title: 'Completed', copy: 'Verify', reply: 'Route', action: 'Send', detail: 'One arrival produces one count increase.'},
    build: collapseToTally,
  },
  {
    id: 'registered-shape-cut',
    title: 'Cut between two contexts on a matched shape',
    moves: 'An abrupt cut changes the surrounding shot in one frame. The supporting line appears after the cut.',
    fixed: 'The matched action shape, its position and size, and the action wording.',
    notice: 'A corresponding action connects two different contexts.',
    fits: 'Jump between two contexts while keeping a strong visual point of correspondence.',
    avoid: 'The cut implies editorial correspondence. Use a continuous transition when physical continuity matters.',
    intents: ['match cut around the same button', 'hard cut to a new context while keeping the action in the exact spot', 'use a graphic match to connect two shots'],
    editable: ['heading', 'copy', 'title', 'action', 'detail'],
    defaults: {heading: 'One familiar action', copy: 'In a message', title: 'In the workspace', action: 'Approve', detail: 'The same action is available here.'},
    build: cutOnShape,
  },
  {
    id: 'objects-pass-behind',
    title: 'Move two objects behind a fixed foreground cover',
    moves: 'The objects travel toward each other, disappear behind a central cover, and emerge on opposite sides.',
    fixed: 'The central cover, both travel lanes, and the heading.',
    notice: 'The objects continue behind the cover and keep their identities as they reappear.',
    fits: 'Demonstrate a handoff through an occluded region or passage on the same plane.',
    avoid: 'A temporary disappearance can imply travel through a real intervening space. Use a dissolve for unrelated replacements.',
    intents: ['make two objects pass behind a stationary cover', 'send cards through the middle behind a foreground obstruction', 'swap sides by passing behind the same bridge'],
    editable: ['heading', 'copy', 'title', 'action', 'detail'],
    defaults: {heading: 'Transfer route', copy: 'Intake', title: 'Output', action: 'Relay', detail: 'Both objects reappear after passing behind the relay.'},
    build: passBehind,
  },
  {
    id: 'needle-sweeps-threshold',
    title: 'Sweep a gauge needle to its measured reading',
    moves: 'A single meter pointer rotates about its pivot, overshoots briefly, and settles at the desired reading.',
    fixed: 'Gauge ticks, the threshold region, the pivot and the labels.',
    notice: 'The shown value falls at a specific point on a bounded scale.',
    fits: 'Show one metric crossing a threshold or resolving into a stable reading.',
    avoid: 'A gauge implies a meaningful range. Use a cycle or spinner for activity that has no bounded reading.',
    intents: ['sweep a needle across fixed gauge ticks', 'show the dial needle crossing the green threshold', 'swing the pointer across a static meter scale'],
    editable: ['heading', 'copy', 'title', 'action', 'detail', 'values'],
    defaults: {heading: 'System health', copy: 'Low', title: 'Capacity', action: 'High', detail: 'The pointer settles in the target range.'},
    editNotes: 'The first value sets the needle reading on a 0–100 scale.',
    build: sweepGauge,
  },
].map(entry => ({
  ...entry,
  source: {kind: 'authored', ref: 'packs/editorial.mjs#' + entry.id, range: [0, 2.4]},
}));
