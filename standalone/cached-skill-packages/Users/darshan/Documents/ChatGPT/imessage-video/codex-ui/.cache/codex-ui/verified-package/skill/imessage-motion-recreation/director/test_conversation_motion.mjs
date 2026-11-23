import assert from 'node:assert/strict';
import test from 'node:test';
import { AttachmentCollage, AttachmentStack, Conversation, PhotoAttachment, PhotoStrip } from './components.mjs';
import { conversationMotion } from './examples/conversation-motion.mjs';
import { stateAt, svgMarkup } from '../scripts/engines/common.mjs';

function layerIndex(layers, parent = null, entries = new Map()) {
  for (const layer of layers) {
    assert.ok(!entries.has(layer.id), `Duplicate layer ${layer.id}`);
    entries.set(layer.id, { layer, parent });
    layerIndex(layer.children ?? [], layer.id, entries);
  }
  return entries;
}

function sampled(scene, t) {
  const entries = layerIndex(scene.layers);
  return id => stateAt(entries.get(id).layer, t);
}

test('edited previous copy reflows the target row and keeps its reaction attached', () => {
  const long = conversationMotion();
  const compact = conversationMotion({ compact: true });
  const body = 'thread-message-detour-body';
  const row = 'thread-message-awning';
  const badge = `${row}-reaction`;
  assert.ok(sampled(long, 0)(body).height > sampled(compact, 0)(body).height);
  assert.ok(sampled(long, 0)(row).y > sampled(compact, 0)(row).y);
  assert.ok(!svgMarkup(long, .90).includes(`data-layer="${badge}"`));
  for (const scene of [long, compact]) {
    assert.equal(layerIndex(scene.layers).get(badge).parent, row);
    for (const t of [1.2, 2.8, 4.5, 5.13, 6.42]) {
      const at = sampled(scene, t);
      assert.equal(at(badge).y, sampled(scene, 1.2)(badge).y);
      assert.equal(at(badge).x, sampled(scene, 1.2)(badge).x);
      assert.ok(svgMarkup(scene, t).includes(`data-layer="${badge}"`));
    }
  }
});

test('the send frame clears the draft, hides the send icon and reveals exactly one outgoing row', () => {
  const scene = conversationMotion();
  const input = 'thread-composer-input';
  const send = 'thread-composer-send';
  const row = 'thread-message-sent';
  const before = sampled(scene, 77 / 30);
  const after = sampled(scene, 78 / 30);
  assert.equal(before(input).text, 'On my way 🌙');
  assert.equal(before(send).opacity, 1);
  assert.ok(!svgMarkup(scene, 77 / 30).includes(`data-layer="${row}"`));
  assert.equal(after(input).text, '');
  assert.equal(after(send).opacity, 0);
  assert.equal(after('thread-composer-placeholder').opacity, 1);
  assert.equal(after(`${row}-copy`).text, before(input).text);
  assert.equal(svgMarkup(scene, 78 / 30).split(`data-layer="${row}"`).length, 2);
  assert.equal(sampled(scene, 7.4)(input).text, '');
});

test('scroll and camera both move while the transcript clip stays phone-local', () => {
  const scene = conversationMotion();
  const entries = layerIndex(scene.layers);
  const at = sampled(scene, 5.13);
  assert.equal(entries.get('thread').parent, 'camera');
  assert.equal(entries.get('thread-transcript').parent, 'thread-screen');
  assert.equal(entries.get('thread-composer').parent, 'thread-screen');
  assert.equal(entries.get('thread-message-awning').parent, 'thread-history-offset');
  assert.equal(entries.get('thread-history-offset').parent, 'thread-scroll');
  assert.equal(entries.get('thread-scroll').parent, 'thread-transcript');
  assert.notEqual(at('thread-history-offset').y, sampled(scene, 4.12)('thread-history-offset').y);
  assert.notEqual(at('camera').scaleX, sampled(scene, 4.12)('camera').scaleX);
  assert.notEqual(at('camera').rotation, sampled(scene, 4.12)('camera').rotation);
  const transcript = at('thread-transcript');
  assert.ok(transcript.y + transcript.clip.y + transcript.clip.height < at('thread-composer').y);
  const markup = svgMarkup(scene, 5.13);
  assert.match(markup, /clip-path="url\(#clip-thread-transcript\)"/);
  assert.match(markup, /clip-path="url\(#clip-thread-screen\)"/);
});

test('a multiline draft stays clipped and sends the full string when copy is omitted', () => {
  const full = 'First line\nThe final line includes a family emoji 👨‍👩‍👧‍👦';
  const phone = Conversation({
    id: 'test',
    messages: [{id: 'sent', person: 'you', at: 1, send: true}],
    draft: [{at: .5, copy: full}],
  });
  const scene = {width: 960, height: 540, duration: 2, fps: 30, layers: [phone]};
  const before = sampled(scene, 29 / 30);
  assert.equal(before('test-composer-input').text, full.split('\n')[1]);
  assert.equal(before('test-composer-draft-window').clip.height, before('test-composer-field').height);
  const after = sampled(scene, 1);
  assert.equal(after('test-composer-input').text, '');
  assert.equal(after('test-message-sent-copy').text.replace(/\n/g, ' '), full.replace(/\n/g, ' '));
});

test('attachment surfaces keep distinct moving parts and explicit presentation choices', () => {
  const images = ['one.jpg', 'two.jpg', 'three.jpg', 'four.jpg'].map(src => ({src, alt: src}));
  const photo = PhotoAttachment({id: 'single', image: images[0], fit: 'contain'});
  const collage = AttachmentCollage({id: 'collage', images: images.slice(0, 3)});
  const strip = PhotoStrip({id: 'strip', images, position: [{t: 1, value: 145}]});
  const stack = AttachmentStack({id: 'stack', images, swipes: [{at: 1, index: 1, duration: .4}]});
  const phone = Conversation({
    id: 'test',
    messages: [{id: 'pass', person: 'you', attachment: {type: 'app-card', image: images[0], title: 'Your pass'}}],
  });
  const layers = layerIndex([photo, collage, strip, stack, phone]);
  const get = id => layers.get(id).layer;
  assert.ok(photo.clip && collage.clip);
  const imageLayers = id => [...layers.values()].map(({layer}) => layer).filter(layer => layer.type === 'image' && layer.id.startsWith(id));
  assert.equal(imageLayers('single-').length, 1);
  assert.equal(imageLayers('single-')[0].preserveAspectRatio, 'xMidYMid meet');
  assert.equal(imageLayers('collage-').length, 3);
  assert.throws(() => AttachmentCollage({id: 'invalid', images}), /two or three/i);
  assert.ok(get('strip').clip && get('stack').clip);
  assert.equal(stateAt(get('strip-rail'), 1).x, -145);
  assert.equal(stateAt(get('stack-photo-0'), .9).opacity, 1);
  assert.equal(stateAt(get('stack-photo-0'), 1.4).opacity, 0);
  assert.equal(stateAt(get('stack-photo-1'), 1.4).opacity, 1);
  assert.equal(get('test-message-pass-attachment-art-image').src, 'one.jpg');
  assert.equal(get('test-message-pass-attachment-action-label').type, 'text');
  assert.ok(![...layers.keys()].some(id => id.startsWith('test-message-pass-attachment-rail')));
});
