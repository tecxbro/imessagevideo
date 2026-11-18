import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import test from 'node:test';
import {stateAt, svgMarkup} from '../../scripts/engines/common.mjs';
import {conversationDemo} from './demo.mjs';
import {buildWithBrowserText, chromiumPath} from './measure-text.mjs';

const require = createRequire(new URL('../../scripts/engines/package.json', import.meta.url));
const [wrapped, short] = await Promise.all([
  buildWithBrowserText(conversationDemo()),
  buildWithBrowserText(conversationDemo({short: true})),
]);

function findPath(layers, id) {
  for (const layer of layers) {
    if (layer.id === id) return [layer];
    const children = findPath(layer.children ?? [], id);
    if (children) return [layer, ...children];
  }
}

function pathTo(scene, id) {
  const path = findPath(scene.layers, id);
  assert.ok(path, `Missing layer ${id}`);
  return path;
}

const find = (scene, id) => pathTo(scene, id).at(-1);

function isVisible(scene, id, time) {
  return pathTo(scene, id).map(layer => stateAt(layer, time)).every(layer =>
    (layer.start ?? 0) <= time && time < (layer.end ?? scene.duration) && layer.opacity > 0);
}

test('preceding copy changes row spacing while the heart stays in message coordinates', () => {
  const {scene} = wrapped;
  const beforeEdit = 1.05;
  const afterEdit = 1.6;
  assert.doesNotMatch(stateAt(find(scene, 'seats-copy'), beforeEdit).text, /\n/);
  assert.match(stateAt(find(scene, 'seats-copy'), afterEdit).text, /\n/);
  assert.doesNotMatch(stateAt(find(short.scene, 'seats-copy'), afterEdit).text, /\n/);
  const rowDistance = (scene, t) => stateAt(find(scene, 'invite'), t).y - stateAt(find(scene, 'seats'), t).y;
  assert.ok(rowDistance(scene, afterEdit) > rowDistance(scene, beforeEdit));
  assert.ok(rowDistance(scene, afterEdit) > rowDistance(short.scene, afterEdit));

  const path = pathTo(scene, 'invite-tapback');
  assert.equal(path.at(-2).id, 'invite');
  assert.equal(isVisible(scene, 'invite-tapback', 0.6), false);
  for (const time of [1.05, 4.2, 5.5, 6.7, 7.98, 8.9]) {
    assert.equal(isVisible(scene, 'invite-tapback', time), true);
    const {x, y} = stateAt(path.at(-1), time);
    const other = stateAt(find(short.scene, 'invite-tapback'), time);
    assert.deepEqual({x, y}, {x: other.x, y: other.y});
  }
  const viewport = path.find(layer => layer.id === 'lantern-viewport');
  const screen = path.find(layer => layer.id === 'lantern-screen');
  assert.ok(viewport?.clip && screen?.clip?.radius > 0);
  const scroll = find(scene, 'lantern-scroll');
  assert.notEqual(stateAt(scroll, 5.65).y, stateAt(scroll, 6.65).y);
  assert.notEqual(stateAt(path[0], 5.65).scaleX, stateAt(path[0], 6.65).scaleX);
});

test('send clears the draft on the first outgoing frame and restores the idle composer', () => {
  const {scene, events} = wrapped;
  const [send, ...duplicates] = events.filter(event => event.kind === 'message_send');
  assert.ok(send?.frame > 0);
  assert.equal(duplicates.length, 0);
  const previous = (send.frame - 1) / scene.fps;
  const first = send.frame / scene.fps;
  const input = find(scene, 'lantern-composer-input');
  const draft = stateAt(input, previous).text;
  const sentCopy = find(scene, 'request-copy').text;
  assert.equal(draft.replace(/\n/g, ' '), sentCopy.replace(/\n/g, ' '));
  assert.equal(isVisible(scene, 'request', previous), false);
  assert.equal(isVisible(scene, 'request', first), true);
  for (let frame = send.frame; frame < scene.duration * scene.fps; frame++) {
    assert.equal(stateAt(input, frame / scene.fps).text, '');
  }
  const placeholder = findPath(scene.layers, 'lantern-composer-placeholder');
  assert.ok(placeholder, 'Composer exposes an idle prompt');
  assert.equal(isVisible(scene, 'lantern-composer-placeholder', previous), false);
  assert.equal(isVisible(scene, 'lantern-composer-placeholder', first), true);
  assert.equal(isVisible(scene, 'reply', first), false);
  assert.equal(isVisible(scene, 'reply', 5.35), true);
  assert.equal(isVisible(scene, 'lantern-composer-active', previous), true);
  assert.equal(isVisible(scene, 'lantern-composer-active', first), false);
  assert.equal(isVisible(scene, 'lantern-composer-idle', first), true);
});

test('rendered SVG clips the scrolling transcript in the transformed phone', async () => {
  const {chromium} = require('playwright');
  const scene = structuredClone(wrapped.scene);
  const viewport = find(scene, 'lantern-viewport');
  const screen = find(scene, 'lantern-screen');
  const scroll = find(scene, 'lantern-scroll');
  // Expose a leak to hit testing if the viewport clip is missing.
  screen.children = screen.children.filter(layer =>
    layer.id !== 'lantern-header' && layer.id !== 'lantern-composer');
  const time = 6.3;
  const scrollY = stateAt(scroll, time).y;
  // A high-contrast shape spans the actual viewport edge at this moving-camera sample.
  scroll.children.push({
    id: 'clip-probe',
    type: 'rect',
    x: viewport.clip.width * 0.5,
    y: viewport.clip.height - scrollY - 12,
    width: 32,
    height: 24,
    fill: '#ff00ff',
  });
  const browser = await chromium.launch({executablePath: chromiumPath(), headless: true});
  try {
    const page = await browser.newPage({viewport: {width: scene.width, height: scene.height}});
    const clipHits = async () => {
      await page.setContent(`<body style="margin:0">${svgMarkup(scene, time)}</body>`);
      return page.evaluate(() => {
        const rect = document.querySelector('[data-layer="clip-probe"] rect');
        const matrix = rect.getScreenCTM();
        const hit = y => {
          const world = new DOMPoint(16, y).matrixTransform(matrix);
          return document.elementFromPoint(world.x, world.y)?.closest('[data-layer]')?.dataset.layer;
        };
        return [hit(6), hit(18)];
      });
    };
    const [inside, outside] = await clipHits();
    assert.equal(inside, 'clip-probe');
    assert.notEqual(outside, 'clip-probe');
    delete viewport.clip;
    assert.deepEqual(await clipHits(), ['clip-probe', 'clip-probe']);
  } finally {
    await browser.close();
  }
});
