const range = [36.366667, 37.066667];
const film = 'projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4';
const photoOffsets = [0, 22, 22, 47, 76, 109, 148, 148, 195, 252, 324, 417, 417, 542, 698, 846, 956, 956, 1035, 1094, 1140];

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
    fits: 'Browse pictures within a single place, album or message surface with persistent labels.',
    avoid: 'A stack that lifts or dismisses only its front photo needs independent layers and depth.',
    intents: [
      'Move the photos beneath a fixed heading',
      'Slide pictures horizontally under a title that stays put',
      'Keep the shop name pinned as the storefront photos glide past',
      'Scroll images without moving the header',
    ],
    editable: ['heading', 'detail', 'photos', 'direction'],
    photoCount: {min:2, max:12},
    source: {
      kind: 'measured-adaptation',
      ref: film,
      range,
      framesInclusive: [1091, 1111],
      note: 'Normalized Linq rail shift sampled by the earlier motion library at a23bfb2. Reproduced at a new size with authored artwork and a held header.',
    },
    build(ctx) {
      const rail = photoRail(ctx, ctx.content.photos.length);
      const direction = ctx.content.direction ?? 'left';
      if (!['left', 'right'].includes(direction)) throw Error('The photo rail only supports horizontal travel');
      const travel = (ctx.content.photos.length - 1) * 308 + 296 - 440;
      if (travel === 0) throw Error('photos-under-fixed-heading needs two or more photos');
      const {frameCount} = ctx;
      const first = Math.round(frameCount * .27);
      const span = Math.min(20, Math.round(frameCount * .47));
      ctx.track(rail, 'x', photoOffsets.map((offset, i) => [
        (first + i * span / 20) / frameCount, (direction === 'left' ? -offset / 1140 : offset / 1140 - 1) * travel,
      ]));
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
