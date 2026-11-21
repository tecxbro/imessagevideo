const range = [1088 / 30, 1134 / 30];
const film = 'projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4';
// Native frame-to-frame photo translations once the lead-in camera move has settled.
const photoOffsets = [0, 15, 32, 52, 74, 74, 99, 128, 161, 200, 200, 247, 304, 376,
  469, 469, 594, 750, 898, 1008, 1008, 1087, 1146, 1192, 1229, 1229, 1259, 1283,
  1303, 1320, 1320, 1334, 1346, 1356, 1364, 1364, 1370, 1375, 1379, 1382, 1382, 1384, 1385];

function photoRail(ctx, count) {
  const {group, image, rect, colors, stage} = ctx;
  const tiles = Array.from({length: count}, (_, i) =>
    image(`photo-${i + 1}`, i * 308, 0, 296, 197, {photo: i}));
  const rail = group('photo-rail', 0, 0, tiles);
  stage.children.push(
    group('photo-viewport', 30, 33, [
      rect('photo-viewport-field', 0, 0, 440, 197, colors.light),
      rail,
    ], {clip: {x: 0, y: 0, width: 440, height: 197, radius: 14}}),
    rect('photo-rail-divider', 30, 250, 440, 1, colors.line),
  );
  return rail;
}

export const entries = [
  {
    id: 'photos-under-fixed-heading',
    title: 'Slide the photos beneath a fixed heading',
    moves: 'Adjacent photos translate together on one horizontally clipped rail.',
    fixed: 'The heading, viewport, divider and supporting footer stay in place.',
    notice: 'The next photo comes into view while the place and surrounding context remain easy to read.',
    fits: 'Browse pictures inside a place or album surface with persistent labels. Use the separate UI adapter variant for inline conversation paging.',
    avoid: 'A stack that lifts or dismisses only its front photo needs independent layers and depth.',
    intents: [
      'Move the photos beneath a fixed heading',
      'Slide pictures horizontally under a title that stays put',
      'Keep the shop name pinned as the storefront photos glide past',
      'Scroll images without moving the header',
      'Browse ticket options on a card rail while the event name stays visible',
    ],
    editable: ['heading', 'detail', 'photos', 'direction', 'message'],
    example: 'motion/examples/photo-swipe.content.json',
    comparison: 'motion/PHOTO-SWIPE.md',
    photoCount: {min:2, max:12},
    source: {
      kind: 'measured-adaptation',
      ref: film,
      range,
      framesInclusive: [1088, 1134],
      note: 'Native Linq rail displacements after the entrance camera move, including the acceleration, deceleration and final hold. Replanted at a new size with independent imagery and a fixed heading.',
    },
    build(ctx) {
      const rail = photoRail(ctx, ctx.content.photos.length);
      const direction = ctx.content.direction ?? 'left';
      if (!['left', 'right'].includes(direction)) throw Error('The photo rail only supports horizontal travel');
      const travel = (ctx.content.photos.length - 1) * 308 + 296 - 440;
      if (travel === 0) throw Error('photos-under-fixed-heading needs two or more photos');
      const {frameCount, fps} = ctx;
      const lastSample = photoOffsets.length - 1;
      const span = Math.min(Math.round(lastSample * fps / 30), Math.round(frameCount * .75));
      const first = Math.round((frameCount - span) * .4);
      ctx.track(rail, 'x', photoOffsets.map((offset, i) => [
        (first + i * span / lastSample) / frameCount,
        (direction === 'left' ? -offset / photoOffsets[lastSample] : offset / photoOffsets[lastSample] - 1) * travel,
      ]));
      if (ctx.content.message) {
        ctx.stage.children.push(ctx.group('pinned-message', 30, 258, [
          ctx.rect('pinned-message-bg', 0, 0, 440, 34, ctx.colors.light, 13),
          ctx.text('pinned-message-copy', ctx.content.message, 13, 7, 15, {fill: ctx.colors.ink}),
        ], {clip: {x: 0, y: 0, width: 440, height: 34, radius: 13}}));
      }
      ctx.label(ctx.content.detail);
      ctx.event('rail-start', (first + 1) / frameCount, rail.id, 'media.scroll');
      ctx.event('rail-settle', (first + span) / frameCount, rail.id, 'media.settle');
    },
  },
  {
    id: 'heading-over-fixed-photos',
    title: 'Slide a heading over still photos',
    moves: 'The heading text glides within its own clipped band.',
    fixed: 'Photo positions, their crop, the heading backdrop and bottom caption hold still.',
    notice: 'The viewer can compare the same images while the title establishes a new emphasis.',
    fits: 'Reposition an editorial label over stationary evidence or retain a fixed gallery frame.',
    avoid: 'This leaves every picture unchanged. Use a rail when the viewer needs to see a new photo.',
    intents: [
      'Hold the photos still while the heading moves',
      'Slide the heading over stationary pictures',
      'Keep the gallery anchored and let the header drift',
      'Do not move the photos, move the title instead',
    ],
    editable: ['heading', 'detail', 'photos', 'direction'],
    photoCount: {min:1, max:2},
    source: {kind:'authored',ref:'packs/core.mjs#heading-over-fixed-photos',range:[0,2.4]},
    build(ctx) {
      photoRail(ctx, Math.min(ctx.content.photos.length, 2));
      const title = ctx.heading.children[1];
      const direction = ctx.content.direction ?? 'right';
      const vertical = direction === 'up' || direction === 'down';
      const low = vertical ? 4 : 28, high = vertical ? 26 : 150;
      const increasing = direction === 'right' || direction === 'down';
      const [start, end] = increasing ? [low, high] : [high, low];
      title.x = 28;
      ctx.heading.clip = {x: 0, y: 0, width: 500, height: 54};
      ctx.track(title, vertical ? 'y' : 'x', [[0, start], [.25, start], [.70, end, 'easeInOut']]);
      ctx.label(ctx.content.detail);
      ctx.event('heading-start', .27, title.id, 'title.move');
      ctx.event('heading-settle', .70, title.id, 'title.settle');
    },
  },
];
