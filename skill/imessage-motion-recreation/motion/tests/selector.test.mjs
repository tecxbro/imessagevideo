import assert from 'node:assert/strict';
import test from 'node:test';
import {select} from '../select.mjs';
import {entries as catalog} from '../catalog.mjs';

const entries = [
  {
    id: 'photos-under-fixed-heading',
    title: 'Photo strip slides under a fixed heading',
    moves: 'The horizontal photo strip slides left through one clipped viewport.',
    fixed: 'Heading, actions and clip viewport stay in place.',
    notice: 'A new set of places in the same card.',
    fits: 'Use this when the photos change and the venue identity stays in view.',
    intents: ['Move the photos beneath a fixed heading', 'pan a photo rail underneath the title and buttons', 'browse night market photos while the place name stays put'],
  },
  {
    id: 'heading-over-fixed-photos',
    title: 'A heading slides over fixed photos',
    moves: 'A heading slides over a still row of photos.',
    fixed: 'All photos and controls are fixed throughout.',
    notice: 'The new overlay heading and unchanged artwork.',
    fits: 'Use this when a new caption frames the same artwork.',
    intents: ['hold the photos still while the heading moves', 'slide a headline over the static photographs'],
  },
  {
    id: 'messages-attachment-stack',
    title: 'Swipe attached photos off a stacked message',
    moves: 'The top attachment moves left and promotes the next photo behind it.',
    fixed: 'The composer, attachment counter and conversation header stay in place.',
    notice: 'The next photo is revealed behind the first.',
    fits: 'Use this to browse stacked photos sent in an existing chat.',
    intents: ['swipe the front photo away to see the one behind it', 'swipe twice through a stack of message attachments', 'photo stack inside a group thread'],
    editable: ['swipes'],
  },
  {
    id: 'inline-card-expand',
    title: 'Open a full-size panel from an inline preview',
    moves: 'The panel rises from below while the conversation dims.',
    fixed: 'The conversation layout and composer remain fixed.',
    notice: 'The conversation stays visible behind the open panel.',
    fits: 'Useful when a compact preview opens a working surface in the same conversation.',
    intents: ['tap the inline preview and bring a full-size control panel up from below', 'open the full-screen panel while the chat underneath dims'],
  },
  {
    id: 'avatar-ring-assemble',
    title: 'Headshots assemble around a centered headline',
    moves: 'Portraits travel from outer edges into a ring. The headline shrinks around its middle.',
    fixed: 'The headline center stays fixed.',
    notice: 'Every person is part of the same group.',
    fits: 'Use this for showing a group assembling around a central claim.',
    intents: ['headshots assemble around the words as the text gets smaller', 'portraits gather around a centered headline'],
  },
  {
    id: 'camera-focus',
    title: 'Push in toward the booking detail',
    moves: 'Camera zoom makes a booking result stand out.',
    fixed: 'The card and its content retain local size and spacing.',
    notice: 'The result gains room for reading.',
    fits: 'Use for zooming into one booking detail on a dense screen.',
    intents: ['zoom into the booking detail', 'push the camera in on the appointment result'],
  },
];

const photos = ['photos-under-fixed-heading'];
const heading = ['heading-over-fixed-photos'];
const examples = [
  ['Move the photos beneath a fixed heading', 'retrieve', photos],
  ['Hold the photos still while the heading moves', 'retrieve', heading],
  ['Keep the masthead pinned while the thumbnails drift left.', 'retrieve', photos],
  ['Let the top label travel over motionless imagery.', 'retrieve', heading],
  ['Photos shouldn’t move, just slide the headline across.', 'retrieve', heading],
  ['Don’t move the header. Pan the pictures.', 'retrieve', photos],
  ['While the photos stay put, sweep the top title right.', 'retrieve', heading],
  ['Pan the photo strip beneath the fixed heading more slowly with different images.', 'adapt', photos],
  ['Slide the photos below the fixed heading, then zoom into the booking detail.', 'combine', [...photos, 'camera-focus']],
  ['Swipe the front photo off to see the attachment behind it, then swipe again.', 'adapt', ['messages-attachment-stack']],
  ['Swipe the top photo off the stack three times.', 'missing', []],
  ['Keep everything still while viewers read the confirmation.', 'hold', []],
  ['No animation. Leave everything on the screen for reading.', 'hold', []],
  ['Keep the screen still, then zoom into the booking detail.', 'combine', ['camera-focus']],
  ['Carousel', 'missing', []],
  ['Slide the photos underneath a fixed heading with a 3D page curl', 'missing', []],
  ['Zoom into the booking detail without zoom', 'missing', []],
  ['Rotate the photos beneath the fixed heading', 'missing', []],
  ['Slide the photo strip downward below the fixed heading', 'missing', []],
  ['Move the heading and keep the same heading fixed while the photos move', 'missing', []],
  ['Photos slide beneath the fixed heading, then simulate cloth physics.', 'missing', []],
  ['A lot of headshots gather around a headline that gets smaller without leaving the middle', 'retrieve', ['avatar-ring-assemble']],
  ['Tap the preview; bring a full-size control panel up, darkening the conversation behind it.', 'retrieve', ['inline-card-expand']],
];

for (const [brief, action, matches] of examples) {
  test(brief, () => {
    const result = select(entries, brief);
    assert.deepEqual([result.action, result.matches], [action, matches], JSON.stringify(result));
    assert.ok(result.reason.length > 0);
  });
}

test('a missing technique identifies why near matches were excluded', () => {
  const result = select(entries, 'Slide the photos beneath the fixed heading with a 3D page curl');
  assert.ok(result.candidates[0].issues.includes('requires 3d'));
});

test('the combine response retains each beat and its selected IDs', () => {
  const result = select(entries, 'Photos slide beneath fixed heading, then push in toward the booking detail.');
  assert.deepEqual(result.sequence.map(beat => beat.matches[0]), [photos[0], 'camera-focus']);
});

const holdouts = [
  ['Set the label above the images in motion. Leave each image right where it is so the views are easy to compare.',
    'retrieve', heading],
  ['Leave the exhibit title where it is. Glide the trail gallery pictures underneath it so visitors can compare them.',
    'retrieve', photos],
  ['Let the pictures sit exactly as they are. Only bring the field-guide title up into place.',
    'adapt', heading, {direction: 'up'}],
  ['Sweep the images to the right beneath the fixed title.',
    'adapt', photos, {direction: 'right'}],
  ['Move a long photo rail down behind the stationary masthead.',
    'missing', []],
  ['Turn it into a carousel without explaining which thing moves.',
    'missing', []],
  ['Show the composer send an outgoing blue text and then an incoming gray reply',
    'retrieve', ['conversation-handoff']],
  ['Show a person send a blue bubble, then let the other side answer with a gray bubble.',
    'retrieve', ['conversation-handoff']],
  ['Make the typing progress visible, but do not send any chat yet.',
    'retrieve', ['composer-type']],
  ['In a group thread called Field Crew, someone sent a bunch of pictures. Swipe the front one to the left to see the one behind it, then swipe again. Keep the composer exactly where it is.',
    'adapt', ['messages-attachment-stack'], {swipes: 2}],
  ['Pan horizontally between workspaces without zoom.',
    'retrieve', ['camera-truck-between']],
  ['A bunch of headshots come together around the words Everyone is here. The text gets smaller without leaving the center.',
    'retrieve', ['avatar-ring-assemble']],
  ['Tap the inline preview and bring a full-size control panel up from below, darkening the conversation that is still visible behind.',
    'retrieve', ['inline-card-expand']],
  ['Make the vertical comparison bars grow, then push the camera closer to the highest one.',
    'combine', ['comparison-bars-grow', 'camera-push-in']],
  ['Keep the time on-screen while we read it.',
    'hold', []],
  ['The viewer reads a reply naming a prop. The phone falls off the left as attention crosses to a red tin on the right. Cut to a closer continuation on the physical tin. Hold the tin and release attention from the phone.',
    'retrieve', ['screen-to-physical-prop']],
  ['Start on the message that identifies the little box. The handset leaves left toward the edge and our attention goes to the real prop, then cut closer and hold on the object.',
    'retrieve', ['screen-to-physical-prop']],
];

for (const [brief, action, matches, content] of holdouts) {
  test(`Catalog brief | ${brief}`, () => {
    const result = select(catalog, brief);
    assert.deepEqual([result.action, result.matches, result.content], [action, matches, content], JSON.stringify(result));
  });
}

test('each entry can be looked up by the authored sample wording', () => {
  for (const entry of catalog) {
    for (const brief of entry.intents) {
      assert.deepEqual(select(catalog, brief).matches, [entry.id], brief);
    }
  }
});
