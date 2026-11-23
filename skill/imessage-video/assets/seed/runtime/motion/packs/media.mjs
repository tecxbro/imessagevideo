const entry = (id, title, brief, build) => ({
  id,
  title,
  source: {
    kind: 'authored', ref: `packs/media.mjs#${id}`, range: [0, 2.4],
    note: 'Motion-authored shot. Gesture and timing are illustrative.',
  },
  editable: ['heading', 'photos'],
  ...brief,
  build,
});

function photoWindow(ctx, id, x, y, width, height, photo = 0, radius = 14) {
  return ctx.group(id, x, y, [
    ctx.image(`${id}-image`, 0, 0, width, height, {photo}),
  ], {clip: {x: 0, y: 0, width, height, radius}});
}

function photoTile(ctx, id, x, y, width, height, photo = 0) {
  return ctx.group(id, x, y, [
    ctx.rect(`${id}-surface`, 0, 0, width + 8, height + 8, '#ffffff', 12, {
      stroke: ctx.colors.light, strokeWidth: 1,
    }),
    photoWindow(ctx, `${id}-photo`, 4, 4, width, height, photo, 8),
  ], {originX: (width + 8) / 2, originY: (height + 8) / 2});
}

function scale(ctx, layer, keys) {
  ctx.track(layer, 'scaleX', keys);
  ctx.track(layer, 'scaleY', keys);
}

function add(ctx, ...layers) {
  ctx.stage.children.push(...layers);
}

function stageCard(ctx, id, x, y, width, height) {
  return ctx.rect(id, x, y, width, height, '#ffffff', 17, {
    stroke: ctx.colors.light, strokeWidth: 1,
  });
}

function fitCaption(value) {
  const lines = [''];
  for (const word of value.split(/\s+/)) {
    const candidate = `${lines.at(-1)} ${word}`.trim();
    if (candidate.length <= 31) {
      lines[lines.length - 1] = candidate;
    } else if (lines.length < 3 && word.length <= 31) {
      lines.push(word);
    } else {
      lines[lines.length - 1] = (lines.at(-1) || word).slice(0, 30) + '…';
      break;
    }
  }
  return lines.join('\n');
}

export const entries = [
  entry('photo-open-continuity', 'Thumbnail opens into a viewer', {
    moves: 'The chosen thumbnail grows and moves into a raised preview while its neighbors dim.',
    fixed: 'The other thumbnail boxes, heading, footer, and viewport hold position.',
    notice: 'The same selected image is now large enough to inspect.',
    fits: 'Open one attachment while preserving its identity and origin in the row.',
    avoid: 'For a pinch in a fixed frame, use photo-pinch-detail. For a temporary long-press preview, use attachment-peek-release.',
    intents: [
      'Tap one thumbnail to expand it into a big photo viewer',
      'Show where the larger attachment came from by opening the selected tile in place',
    ],
  }, ctx => {
    const neighbors = ctx.group('thumbnail-neighbors', 0, 0, [
      photoTile(ctx, 'neighbor-left', 57, 104, 102, 65, 1),
      photoTile(ctx, 'neighbor-right', 333, 104, 102, 65, 2),
    ]);
    const chosen = photoTile(ctx, 'chosen-thumbnail', 195, 97, 102, 65);
    scale(ctx, chosen, [[0, 1], [.24, 1], [.65, 3.03, 'easeInOut']]);
    ctx.track(chosen, 'y', [[0, 97], [.24, 97], [.65, 112, 'easeInOut']]);
    ctx.track(neighbors, 'opacity', [[0, 1], [.24, 1], [.55, .22, 'easeOut']]);
    add(ctx, neighbors, chosen);
    ctx.event('thumbnail-open', .24, chosen.id, 'tap');
    ctx.event('preview-settle', .65, chosen.id, 'viewer_open');
  }),

  entry('photo-pinch-detail', 'Pinch into a detail inside the photo', {
    moves: 'The picture scales around a focal point inside a clipped viewer as the gesture markers spread.',
    fixed: 'The image window, control below it, heading, and footer hold position.',
    notice: 'The viewer is magnifying the picture inside an existing viewport.',
    fits: 'Give a viewer a closer look while preserving interface context.',
    avoid: 'For a whole-screen camera push or a thumbnail opening into a viewer, choose the corresponding camera or open motion.',
    intents: [
      'Pinch in on the photo detail but keep the frame and UI fixed',
      'Show two fingers spread apart to enlarge part of an image in place',
    ],
  }, ctx => {
    const frame = photoWindow(ctx, 'pinch-frame', 65, 23, 370, 216);
    const picture = frame.children[0];
    picture.originX = 225;
    picture.originY = 103;
    scale(ctx, picture, [[0, 1], [.26, 1], [.66, 1.82, 'easeInOut']]);
    const left = ctx.rect('pinch-left-finger', 267, 104, 24, 24, '#ffffff', 12, {
      stroke: ctx.colors.blue, strokeWidth: 2,
    });
    const right = ctx.rect('pinch-right-finger', 306, 133, 24, 24, '#ffffff', 12, {
      stroke: ctx.colors.blue, strokeWidth: 2,
    });
    ctx.track(left, 'x', [[0, 267], [.26, 267], [.66, 195, 'easeInOut']]);
    ctx.track(left, 'y', [[0, 104], [.26, 104], [.66, 68, 'easeInOut']]);
    ctx.track(right, 'x', [[0, 306], [.26, 306], [.66, 376, 'easeInOut']]);
    ctx.track(right, 'y', [[0, 133], [.26, 133], [.66, 169, 'easeInOut']]);
    for (const marker of [left, right]) {
      ctx.track(marker, 'opacity', [[0, 0], [.18, 0], [.22, .83], [.66, .83], [.75, 0]]);
    }
    add(ctx, frame, left, right, ctx.text('pinch-caption', 'Zoom', 250, 251, 16, {textAnchor: 'middle'}));
    ctx.event('pinch-start', .26, frame.id, 'pinch');
    ctx.event('pinch-end', .66, frame.id, 'gesture_end');
  }),

  entry('photo-crop-reframe', 'Reframe a photo inside a fixed crop', {
    moves: 'An oversized picture eases sideways underneath a stationary portrait crop frame.',
    fixed: 'The crop bounds, grid lines, heading, and footer hold position.',
    notice: 'The same image is composed around a different focal point at the same magnification.',
    fits: 'Demonstrate shifting a subject within a thumbnail crop or portrait frame.',
    avoid: 'For a series of different photos sliding by, choose a gallery strip. For changing magnification choose photo-pinch-detail.',
    intents: [
      'Slide the same large image behind the crop frame until the subject is centered',
      'Adjust the focal point of the thumbnail without moving or scaling its frame',
    ],
  }, ctx => {
    const w = 136;
    const h = 242;
    const picture = ctx.image('crop-photo', -85, 0, 363, h);
    ctx.track(picture, 'x', [[0, -85], [.24, -85], [.65, 0, 'easeInOut']]);
    const grid = [1, 2].flatMap(i => [
      ctx.rect(`crop-vertical-${i}`, w * i / 3, 0, 1, h, '#ffffff', 0, {opacity: .73}),
      ctx.rect(`crop-horizontal-${i}`, 0, h * i / 3, w, 1, '#ffffff', 0, {opacity: .73}),
    ]);
    const frame = ctx.group('crop-frame', 182, 20, [picture, ...grid], {
      clip: {x: 0, y: 0, width: w, height: h, radius: 10},
    });
    add(ctx, frame);
    ctx.event('crop-drag', .24, picture.id, 'drag');
    ctx.event('crop-settle', .65, picture.id, 'gesture_end');
  }),

  entry('photo-compare-wipe', 'Wipe across a registered before/after photo', {
    moves: 'A divider increases the visible fraction of the second image from the same crop origin.',
    fixed: 'Both photo grids, the surrounding crop frame, and the outside controls hold position.',
    notice: 'The viewer can compare the two conditions at the same coordinate.',
    fits: 'Compare two versions of the same asset. Supply equally sized and registered before and after images.',
    avoid: 'For paging to a different photo or repositioning an image inside the crop, choose a gallery or crop reframe.',
    intents: [
      'Drag a before and after slider across two aligned versions of the photo',
      'Use a comparison wipe with both images staying in registration',
      'Compare a retouch to the unedited original using a draggable divider',
    ],
  }, ctx => {
    const w = 370;
    const h = 204;
    const before = ctx.image('comparison-before', 0, 0, w, h, {photo: 0});
    const after = ctx.image('comparison-after', 0, 0, w, h, {photo: 1});
    // Counter-translate the pixels while the fixed-width clip moves over them.
    const mask = ctx.group('comparison-mask', 0, 0, [after], {
      clip: {x: 0, y: 0, width: w, height: h},
    });
    const fraction = [[0, .14], [.23, .14], [.70, .85, 'easeInOut']];
    const positions = map => fraction.map(([t, f, ease]) => [t, map(f), ease]);
    ctx.track(mask, 'x', positions(f => w * (f - 1)));
    ctx.track(after, 'x', positions(f => w * (1 - f)));
    const divider = ctx.group('comparison-divider', 0, 0, [
      ctx.rect('comparison-line', -1, 0, 2, h, '#ffffff'),
      ctx.rect('comparison-thumb', -12, 90, 24, 24, '#ffffff', 12, {
        stroke: ctx.colors.light, strokeWidth: 1,
      }),
    ]);
    ctx.track(divider, 'x', positions(f => w * f));
    const frame = ctx.group('comparison-frame', 65, 35, [before, mask, divider], {
      clip: {x: 0, y: 0, width: w, height: h, radius: 12},
    });
    add(ctx, frame, ctx.text('comparison-after-label', 'After', 65, 249, 15),
      ctx.text('comparison-before-label', 'Before', 435, 249, 15, {textAnchor: 'end'}));
    ctx.event('divider-drag', .23, divider.id, 'drag');
    ctx.event('divider-stop', .70, divider.id, 'gesture_end');
  }),

  entry('photo-album-deal', 'Deal photos from one album stack', {
    moves: 'The three already stacked thumbnails separate on staggered paths and straighten into a row.',
    fixed: 'Heading, footer, and the album label hold position.',
    notice: 'The individual images belong to the same combined attachment.',
    fits: 'Unpack a small set of photos from a single visible stack.',
    avoid: 'For navigating a photo rail beyond the visible area or changing an album grid density, use the respective rail or density move.',
    intents: [
      'Deal the photo pile out into separate cards from the same album',
      'Spread a stack of three attached pictures into a row so I can see each one',
    ],
    editable: ['heading', 'photos', 'title'],
  }, ctx => {
    const positions = [43, 194, 345];
    // Add topmost tile last so it stays on top as the other tiles emerge.
    for (const i of [2, 1, 0]) {
      const tile = photoTile(ctx, `album-tile-${i}`, 194 + i * 5, 76 - i * 4, 104, 81, i);
      const start = .23 + i * .075;
      ctx.track(tile, 'x', [[0, tile.x], [start, tile.x], [start + .27, positions[i], 'easeInOut']]);
      ctx.track(tile, 'y', [[0, tile.y], [start, tile.y], [start + .27, 93, 'easeOut']]);
      const angle = (i - 1) * 8;
      ctx.track(tile, 'rotation', [[0, angle], [start, angle], [start + .27, 0, 'easeOut']]);
      add(ctx, tile);
    }
    add(ctx, ctx.text('album-deal-label', ctx.content.title, 250, 209, 17, {textAnchor: 'middle'}));
    ctx.event('album-open', .23, 'album-tile-0', 'tap');
    ctx.event('album-dealt', .65, 'album-tile-2', 'layout_settle');
  }),

  entry('media-video-scrub', 'Scrub to specific points in a media preview', {
    moves: 'The playhead drags forward, pauses, and backtracks; the sample shown in the fixed viewer follows its position.',
    fixed: 'The preview frame, timeline baseline, and interface chrome hold position.',
    notice: 'Moving through time changes the viewer while the rest of the UI remains stable.',
    fits: 'Show seeking instead of playback. Supply ordered stills from the same video as sample frames.',
    avoid: 'For selecting start and end boundaries, choose media-trim-range. The example samples are discrete images.',
    intents: [
      'Drag a video playhead through the timeline and scrub back to a frame',
      'Seek through the clip and have the preview update when the thumb moves',
    ],
  }, ctx => {
    const w = 318;
    const h = 171;
    const samples = [0, 1, 2, 3].map(i => ctx.image(`scrub-sample-${i}`, 0, 0, w, h, {photo: i}));
    const selection = [[0, 0], [.30, 1], [.44, 2], [.57, 3], [.77, 2]];
    for (const [i, sample] of samples.entries()) {
      ctx.track(sample, 'opacity', selection.map(([t, current]) => [t, Number(current === i), 'hold']));
    }
    add(ctx, ctx.group('scrub-viewer', 91, 23, samples, {
      clip: {x: 0, y: 0, width: w, height: h, radius: 12},
    }));
    const thumb = ctx.rect('scrub-thumb', 91, 215, 18, 18, ctx.colors.blue, 9);
    ctx.track(thumb, 'x', [[0, 91], [.21, 91], [.30, 165], [.44, 241], [.57, 371], [.67, 371],
      [.77, 261, 'easeOut']]);
    add(ctx, ctx.rect('scrub-rail', 100, 222, 292, 4, ctx.colors.light, 2), thumb,
      ctx.text('scrub-start', '0:00', 92, 247, 14), ctx.text('scrub-end', '0:18', 408, 247, 14, {textAnchor: 'end'}));
    ctx.event('seek-start', .21, thumb.id, 'drag');
    ctx.event('seek-stop', .77, thumb.id, 'gesture_end');
  }),

  entry('media-trim-range', 'Trim the in and out points independently', {
    moves: 'The two range handles advance inward in separate gestures around a fixed filmstrip.',
    fixed: 'The filmstrip image positions, heading, footer, and time axis hold position.',
    notice: 'Only the section between the handles will be kept.',
    fits: 'Set in and out points, with excluded time still visible for orientation.',
    avoid: 'For jumping to a playhead location without changing the committed range, use media-video-scrub.',
    intents: [
      'Move the two trim handles in to select the part of a video to keep',
      'Set a new start point and end point around the same filmstrip',
    ],
  }, ctx => {
    add(ctx, stageCard(ctx, 'trim-card', 50, 53, 400, 165));
    const w = 344;
    const leftStart = 78;
    const right = leftStart + w;
    const y = 101;
    const h = 62;
    const filmstrip = ctx.group('trim-filmstrip', leftStart, y,
      [0, 1, 2, 3].map(i => ctx.image(`trim-sample-${i}`, 86 * i, 0, 86, h, {photo: i})),
      {clip: {x: 0, y: 0, width: w, height: h, radius: 8}});
    const leftShade = ctx.rect('trim-excluded-left', leftStart, y, 10, h, '#101723', 0, {opacity: .68});
    const rightShade = ctx.rect('trim-excluded-right', right - 12, y, 12, h, '#101723', 0, {opacity: .68});
    const leftHandle = ctx.rect('trim-in-handle', leftStart + 7, y - 8, 6, h + 16, ctx.colors.blue, 3);
    const rightHandle = ctx.rect('trim-out-handle', right - 15, y - 8, 6, h + 16, ctx.colors.blue, 3);
    const a = [[0, 10], [.24, 10], [.43, 72, 'easeOut']];
    const b = [[0, 12], [.52, 12], [.73, 83, 'easeOut']];
    const transform = (keys, map) => keys.map(([t, f, ease]) => [t, map(f), ease]);
    ctx.track(leftShade, 'width', a);
    ctx.track(rightShade, 'width', b);
    ctx.track(rightShade, 'x', transform(b, width => right - width));
    ctx.track(leftHandle, 'x', transform(a, width => leftStart + width - 3));
    ctx.track(rightHandle, 'x', transform(b, width => right - width - 3));
    add(ctx, filmstrip, leftShade, rightShade, leftHandle, rightHandle,
      ctx.text('trim-label', 'Selected range', 250, 181, 15, {textAnchor: 'middle'}));
    ctx.event('trim-in-drag', .24, leftHandle.id, 'drag');
    ctx.event('trim-out-drag', .52, rightHandle.id, 'drag');
    ctx.event('trim-range-settle', .73, rightHandle.id, 'selection_change');
  }),

  entry('attachment-peek-release', 'Lift an attachment briefly and return it', {
    moves: 'One attachment rises and grows a little during a hold, then settles into exactly the original grid slot.',
    fixed: 'Neighboring thumbnails and interface chrome hold position.',
    notice: 'The viewer is temporarily inspecting an item before letting go, with no navigation or selection committed.',
    fits: 'Show a transient peek and return to the same spatial context.',
    avoid: 'For a committed large viewer, use photo-open-continuity. For moving an item to a new slot, use card-reorder-insert.',
    intents: [
      'Long press a photo to peek and let it fall back when released',
      'Temporarily lift the attachment for a closer look while its grid neighbors stay put',
    ],
  }, ctx => {
    add(ctx, photoTile(ctx, 'peek-left-neighbor', 31, 103, 121, 76, 1),
      photoTile(ctx, 'peek-right-neighbor', 339, 103, 121, 76, 2));
    const shadow = ctx.rect('peek-shadow', 178, 116, 145, 85, '#252d3c', 13, {blur: 12, opacity: 0});
    const item = photoTile(ctx, 'peek-attachment', 185, 103, 121, 76);
    const lift = [[0, 103], [.23, 103], [.40, 75, 'easeOut'], [.65, 75], [.84, 103, 'easeInOut']];
    ctx.track(item, 'y', lift);
    scale(ctx, item, [[0, 1], [.23, 1], [.40, 1.20, 'easeOut'], [.65, 1.20], [.84, 1, 'easeInOut']]);
    ctx.track(shadow, 'opacity', [[0, 0], [.23, 0], [.40, .22], [.65, .22], [.84, 0]]);
    add(ctx, shadow, item);
    ctx.event('peek-lift', .23, item.id, 'long_press');
    ctx.event('peek-release', .65, item.id, 'gesture_end');
    ctx.event('peek-return', .84, item.id, 'layout_settle');
  }),

  entry('card-reorder-insert', 'Drag a photo into a new grid position', {
    moves: 'The lifted tile follows a path over the row, its neighbors shift into the vacated space, and it docks in the new order.',
    fixed: 'The thumbnail row bounds, heading, and footer hold position.',
    notice: 'The dragged item is now third and the displaced items keep their relative order.',
    fits: 'Demonstrate a persistent order change in a set of editable media.',
    avoid: 'For a temporary lift with no order change, use attachment-peek-release. For bulk layout changes, use photo-grid-density.',
    intents: [
      'Drag the first photo to the third slot and slide the other two into the open space',
      'Show the neighboring tiles shifting out of the way of a drag-to-reorder gesture',
    ],
  }, ctx => {
    const first = photoTile(ctx, 'reorder-first', 47, 112, 103, 73);
    const second = photoTile(ctx, 'reorder-second', 195, 112, 103, 73, 1);
    const third = photoTile(ctx, 'reorder-third', 343, 112, 103, 73, 2);
    const slot = ctx.rect('reorder-destination', 341, 110, 115, 85, '#e4efff', 14, {
      stroke: ctx.colors.blue, strokeWidth: 2, opacity: 0,
    });
    ctx.track(slot, 'opacity', [[0, 0], [.47, 0], [.60, 1], [.74, 1], [.81, 0]]);
    ctx.track(first, 'x', [[0, 47], [.30, 47], [.51, 216, 'easeInOut'], [.66, 343, 'easeOut']]);
    ctx.track(first, 'y', [[0, 112], [.23, 112], [.34, 46, 'easeOut'], [.64, 46], [.80, 112, 'easeIn']]);
    scale(ctx, first, [[0, 1], [.23, 1], [.35, 1.10, 'easeOut'], [.65, 1.10], [.80, 1]]);
    ctx.track(second, 'x', [[0, 195], [.44, 195], [.60, 47, 'easeOut']]);
    ctx.track(third, 'x', [[0, 343], [.50, 343], [.66, 195, 'easeOut']]);
    add(ctx, slot, second, third, first);
    ctx.event('reorder-pickup', .23, first.id, 'drag');
    ctx.event('reorder-drop', .80, first.id, 'drop');
  }),

  entry('media-progressive-sharpen', 'Resolve a soft preview in successive regions', {
    moves: 'Successive bands sharpen over a soft version of the same photo.',
    fixed: 'The picture geometry, window, heading, and footer hold position.',
    notice: 'The visible asset is gaining detail rather than being replaced.',
    fits: 'Show a deliberately staged placeholder-to-full-resolution transition.',
    avoid: 'For a loading bar without pixel changes, use attachment-download-progress. For a reveal across previously empty space, use photo-iris-reveal.',
    intents: [
      'Keep the blurry preview still while the full resolution photo sharpens in bands',
      'Resolve a soft photo placeholder progressively without shifting the crop',
    ],
  }, ctx => {
    const w = 350;
    const h = 211;
    const soft = ctx.image('decode-placeholder', 0, 0, w, h, {blur: 13});
    const bands = Array.from({length: 4}, (_, i) => {
      const top = h * i / 4;
      const band = ctx.group(`decode-band-${i}`, 0, top, [
        ctx.image(`decode-crisp-${i}`, 0, -top, w, h),
      ], {clip: {x: 0, y: 0, width: w, height: h / 4 + .3}, opacity: 0});
      const start = .25 + i * .12;
      ctx.track(band, 'opacity', [[0, 0], [start, 0], [start + .13, 1, 'easeOut']]);
      return band;
    });
    const frame = ctx.group('decode-photo', 75, 38, [soft, ...bands], {
      clip: {x: 0, y: 0, width: w, height: h, radius: 13},
    });
    add(ctx, ctx.rect('decode-backing', 75, 38, w, h, '#d8e0e9', 13), frame);
    ctx.event('first-region-resolves', .25, bands[0].id, 'load_visible');
    ctx.event('full-resolution', .74, frame.id, 'load_complete');
  }),

  entry('media-caption-disclosure', 'Unfold a caption below a stationary photo', {
    moves: 'The caption window gains height, the full caption appears, and the neighboring row below is pushed down.',
    fixed: 'The photo bounds, disclosure control, heading, and footer hold position.',
    notice: 'The caption is part of the photo’s layout and takes up real space.',
    fits: 'Expose longer notes while keeping the photo visible and preserving a coherent layout.',
    avoid: 'For an overlay that should leave the rows underneath alone, use a modal or peek motif.',
    intents: [
      'Expand the caption under the photo and push the next row down',
      'Reveal the full photo notes while keeping the image fixed at the top',
    ],
    editable: ['heading', 'photos', 'detail', 'action', 'reply'],
  }, ctx => {
    const w = 275;
    const x = 112;
    const panel = stageCard(ctx, 'caption-card', x, 9, w, 163);
    const caption = ctx.text('caption-detail', fitCaption(ctx.content.detail), 14, 4, 14, {
      fontWeight: 500, lineHeight: 15,
    });
    ctx.track(caption, 'opacity', [[0, 0], [.30, 0], [.54, 1, 'easeOut']]);
    const captionWindow = ctx.group('caption-content', x, 160, [caption], {
      clip: {x: 0, y: 0, width: w, height: 53},
    });
    const lower = ctx.group('caption-next-row', x, 185, [
      ctx.rect('caption-next-row-body', 0, 0, w, 34, ctx.colors.light, 9),
      ctx.text('caption-next-row-text', ctx.content.reply, 14, 7, 13),
    ], {clip: {x: 0, y: 0, width: w, height: 34, radius: 9}});
    ctx.track(panel, 'height', [[0, 163], [.23, 163], [.58, 216, 'easeOut']]);
    ctx.track(lower, 'y', [[0, 185], [.23, 185], [.58, 238, 'easeOut']]);
    add(ctx, panel, photoWindow(ctx, 'caption-photo', x + 12, 20, w - 24, 105),
      ctx.text('caption-control', ctx.content.action, x + 14, 134, 16, {fill: ctx.colors.blue, fontWeight: 600}),
      captionWindow, lower);
    ctx.event('caption-toggle', .23, 'caption-control', 'tap');
    ctx.event('caption-settle', .58, panel.id, 'layout_settle');
  }),

  entry('photo-iris-reveal', 'Reveal a photograph through an expanding aperture', {
    moves: 'A circular mask expands from a chosen point and opens to all four corners of the frame.',
    fixed: 'The underlying picture geometry, reveal origin, crop frame, and interface chrome hold position.',
    notice: 'The first detail appears at the chosen point; its surroundings are revealed from the same unmoving image.',
    fits: 'Reveal one image outward from an editorial focal point after a hold.',
    avoid: 'For a centered zoom where the photo itself changes size, choose photo-pinch-detail.',
    intents: [
      'Reveal a photo outward from a circular hole while the image itself stays still',
      'Start on one detail and open an iris mask out to the edges of the photo',
    ],
  }, ctx => {
    const w = 360;
    const h = 206;
    const origin = {x: 141, y: 105};
    const r = 83;
    const pixels = ctx.image('iris-image', r - origin.x, r - origin.y, w, h, {
      originX: origin.x, originY: origin.y,
    });
    const mask = ctx.group('iris-mask', origin.x - r, origin.y - r, [pixels], {
      originX: r, originY: r,
      clip: {x: 0, y: 0, width: 2 * r, height: 2 * r, radius: r},
    });
    // Sample the inverse transform so the photo stays registered between keys.
    const aperture = [[0, .08], [.23, .08]];
    for (let step = 1; step <= 26; step++) {
      const p = step / 26;
      const eased = p * p * (3 - 2 * p);
      aperture.push([.23 + .46 * p, .08 + 2.98 * eased]);
    }
    scale(ctx, mask, aperture);
    scale(ctx, pixels, aperture.map(([t, value]) => [t, 1 / value]));
    // Once the aperture covers the frame, use the full-size pixels to avoid
    // retaining intermediate raster resampling through the rest of the hold.
    const revealed = ctx.image('iris-image-settled', 0, 0, w, h);
    ctx.track(revealed, 'opacity', [[0, 0], [.64, 0], [.69, 1]]);
    const viewport = ctx.group('iris-viewport', 70, 38, [
      ctx.rect('iris-underlay', 0, 0, w, h, '#1e2b38'),
      mask, revealed,
    ], {clip: {x: 0, y: 0, width: w, height: h, radius: 14}});
    add(ctx, viewport);
    ctx.event('iris-opens', .23, mask.id, 'reveal_start');
    ctx.event('iris-clears-frame', .69, viewport.id, 'reveal_complete');
  }),

  entry('album-page-turn', 'Turn one album leaf across a visible spine', {
    moves: 'The departing right leaf compresses toward the seam; its reverse side opens over the left page.',
    fixed: 'The album cover and center seam hold position, and content on resting pages has no free translation.',
    notice: 'The viewer advances to the next spread by turning one physical leaf.',
    fits: 'Present an album as a book; this is a flat hinge projection with shadow, without a rolling paper deformation.',
    avoid: 'For side-scrolling loose photos, choose a rail or a photo stack. For a whole card flipping independently, use a card flip.',
    intents: [
      'Flip the right-hand album page over the spine to reveal the next spread',
      'Show a book leaf turning with its outer edge closing in on the hinge',
    ],
  }, ctx => {
    const w = 158;
    const h = 178;
    add(ctx, ctx.rect('page-cover', 81, 48, 338, 196, '#243344', 17),
      photoWindow(ctx, 'static-old-left', 92, 57, w, h, 0, 5),
      photoWindow(ctx, 'static-new-right', 250, 57, w, h, 1, 5));
    const face = photoWindow(ctx, 'turning-front', 250, 57, w, h, 2, 5);
    ctx.track(face, 'scaleX', [[0, 1], [.23, 1], [.48, .008, 'easeIn']]);
    ctx.track(face, 'opacity', [[0, 1], [.48, 1], [.49, 0, 'hold']]);
    const reverse = photoWindow(ctx, 'turning-back', 92, 57, w, h, 3, 5);
    reverse.originX = w;
    ctx.track(reverse, 'scaleX', [[0, .008], [.49, .008], [.75, 1, 'easeOut']]);
    ctx.track(reverse, 'opacity', [[0, 0], [.49, 1, 'hold']]);
    const crease = ctx.rect('album-crease', 247, 56, 6, h + 2, '#142031', 2, {opacity: .60});
    add(ctx, face, reverse, crease);
    ctx.event('page-edge-lift', .23, face.id, 'drag');
    ctx.event('page-spine-cross', .49, reverse.id, 'gesture_change');
    ctx.event('page-settle', .75, reverse.id, 'gesture_end');
  }),

  entry('photo-grid-density', 'Reflow the same photo tiles into a denser grid', {
    moves: 'Existing images shrink and converge to new rows and columns while secondary tiles appear in the now reachable cells.',
    fixed: 'The grid region, headings, and footer hold position.',
    notice: 'The same album now shows more thumbnails per row while preserving item identity and order.',
    fits: 'Preview a grid density change, keeping the first four image identities across both states.',
    avoid: 'For a single dragged tile changing order, choose card-reorder-insert. For scaling a single picture without relayout, choose photo-pinch-detail.',
    intents: [
      'Switch the album from two big thumbnails per row to three smaller ones but keep each photo in order',
      'Change the thumbnail density by shrinking and reflowing the same photos',
    ],
  }, ctx => {
    const columns = [77, 209, 341];
    const rows = [43, 155];
    for (let i = 0; i < 6; i++) {
      const tile = photoTile(ctx, `density-tile-${i}`, 96 + i % 2 * 152, 30 + Math.floor(i / 2) * 114, 147, 102, i);
      tile.originX = 0;
      tile.originY = 0;
      if (i < 4) {
        ctx.track(tile, 'x', [[0, tile.x], [.23, tile.x], [.61, columns[i % 3], 'easeInOut']]);
        ctx.track(tile, 'y', [[0, tile.y], [.23, tile.y], [.61, rows[Math.floor(i / 3)], 'easeInOut']]);
        scale(ctx, tile, [[0, 1], [.23, 1], [.61, .72, 'easeInOut']]);
      } else {
        tile.x = columns[i % 3];
        tile.y = rows[Math.floor(i / 3)];
        tile.scaleX = tile.scaleY = .72;
        ctx.track(tile, 'opacity', [[0, 0], [.61, 0], [.73, 1, 'easeOut']]);
      }
      add(ctx, tile);
    }
    ctx.event('density-change', .23, 'density-tile-0', 'layout_change');
    ctx.event('density-settle', .73, 'density-tile-5', 'layout_settle');
  }),

  entry('attachment-download-progress', 'Track transfer progress to a usable attachment', {
    moves: 'A determinate progress bar fills with two pauses; the status becomes available only at completion.',
    fixed: 'The attachment thumbnail, filename, card geometry, and interface chrome hold position.',
    notice: 'The item is still transferring until it reaches completion.',
    fits: 'Show a measured percentage advancing toward an openable attachment.',
    avoid: 'For waiting with unknown progress, choose an indeterminate indicator. For a progressively sharpening image, use media-progressive-sharpen.',
    intents: [
      'Show a download bar filling on the same attachment and enable opening when complete',
      'Represent attachment transfer progress as a percentage until the file is ready',
    ],
    editable: ['heading', 'photos', 'title'],
  }, ctx => {
    add(ctx, stageCard(ctx, 'download-card', 51, 76, 398, 132),
      photoWindow(ctx, 'download-icon', 67, 93, 88, 96, 0, 9),
      ctx.text('download-title', ctx.content.title, 173, 101, 19, {fontWeight: 600}),
      ctx.rect('download-rail', 173, 149, 253, 5, ctx.colors.light, 2.5));
    const progress = ctx.rect('download-progress', 173, 149, 0, 5, ctx.colors.blue, 2.5);
    const status = ctx.text('download-status', 'Download', 173, 167, 15, {fill: ctx.colors.muted});
    const checkpoints = [[0, 0], [.20, 0], [.35, .27], [.42, .27], [.57, .67], [.63, .67], [.79, 1]];
    ctx.track(progress, 'width', checkpoints.map(([t, value]) => [t, 253 * value]));
    ctx.track(progress, 'fill', [[0, ctx.colors.blue], [.79, ctx.colors.green, 'hold']]);
    const readouts = [[0, 'Download'], [.20, '0%']];
    for (let i = 2; i < checkpoints.length; i++) {
      const [start, from] = checkpoints[i - 1];
      const [end, to] = checkpoints[i];
      if (to === from) continue;
      for (let step = 5; step < 100 * (to - from); step += 5) {
        const at = start + (end - start) * step / (100 * (to - from));
        readouts.push([at, `${Math.round(100 * from + step)}%`]);
      }
      readouts.push([end, to === 1 ? 'Available to open' : `${Math.round(100 * to)}%`]);
    }
    ctx.track(status, 'text', readouts.map(([t, value]) => [t, value, 'hold']));
    add(ctx, progress, status);
    ctx.event('transfer-start', .20, progress.id, 'download_start');
    ctx.event('transfer-complete', .79, progress.id, 'download_complete');
  }),

  entry('photo-markup-stroke', 'Draw a markup stroke over a stationary photo', {
    moves: 'A curved annotation accumulates in drawing order with the pen tip moving along the growing stroke.',
    fixed: 'The photograph, viewport, heading, and footer hold position.',
    notice: 'The markup singles out a region while keeping the underlying photo visible.',
    fits: 'Direct attention with a hand-drawn path that remains at the end of the move.',
    avoid: 'For gradually exposing the photo itself, choose a reveal. For following a real contour, replace the editable markup coordinates to match that subject.',
    intents: [
      'Draw a hand-marked curved line on top of the still photo to point out a detail',
      'Add a visible pen stroke around part of the attachment while keeping the picture fixed',
    ],
  }, ctx => {
    add(ctx, photoWindow(ctx, 'markup-photo', 60, 26, 380, 229));
    const points = [
      [139, 151], [144, 131], [155, 113], [171, 98], [190, 86],
      [212, 78], [236, 75], [260, 78], [281, 87], [299, 100],
      [313, 116], [319, 134], [318, 152], [309, 167], [294, 181],
      [273, 192], [249, 199], [224, 202], [199, 199], [178, 192], [161, 183],
    ];
    const time = i => .23 + .44 * i / (points.length - 1);
    const tip = ctx.rect('markup-pen-tip', points[0][0] - 7, points[0][1] - 7, 14, 14, '#ffffff', 7, {
      stroke: ctx.colors.blue, strokeWidth: 2,
    });
    ctx.track(tip, 'x', points.map(([x], i) => [time(i), x - 7]));
    ctx.track(tip, 'y', points.map(([, y], i) => [time(i), y - 7]));
    ctx.track(tip, 'opacity', [[0, 0], [.19, 0], [.23, 1], [.67, 1], [.74, 0]]);
    // One segment grows at a time along the same track as the tip.
    for (let i = 1; i < points.length; i++) {
      const [x0, y0] = points[i - 1];
      const [x1, y1] = points[i];
      const angle = Math.atan2(y1 - y0, x1 - x0);
      const length = Math.hypot(x1 - x0, y1 - y0);
      const segment = ctx.rect(`markup-segment-${i}`, x0 - 3, y0 - 3, 6, 6, '#f8de66', 3, {
        originX: 3, originY: 3, rotation: angle * 180 / Math.PI,
      });
      ctx.track(segment, 'width', [[0, 6], [time(i - 1), 6], [time(i), length + 6]]);
      ctx.track(segment, 'opacity', [[0, 0], [time(i - 1), 1, 'hold']]);
      add(ctx, segment);
    }
    add(ctx, tip);
    ctx.event('pen-down', .23, tip.id, 'stroke_start');
    ctx.event('pen-up', .67, tip.id, 'stroke_end');
  }),
];
