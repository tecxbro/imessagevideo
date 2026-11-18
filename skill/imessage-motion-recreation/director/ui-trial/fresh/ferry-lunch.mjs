import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {buildWithBrowserText} from '../measure-text.mjs';

const output = process.argv[2];
if (!output || !output.endsWith('.json')) {
  throw new Error('Usage: node ferry-lunch.mjs /path/to/ferry-lunch.scene.json');
}

const assetDir = fileURLToPath(new URL('./assets/', import.meta.url));
const asset = name => path.relative(path.dirname(path.resolve(output)), path.join(assetDir, name + '.jpg')).split(path.sep).join('/');
const photos = names => names.map(name => ({src: asset(name)}));
const key = (t, value, ease = 'easeInOut') => ({t, value, ease});
const scale = [key(0, .95), key(1.93, .99), key(4.38, .99), key(8.17, 1.035), key(10.7, 1.035), key(12.3, 1.015), key(15.2, 1)];

const {scene, events} = await buildWithBrowserText({
  id: 'ferry-lunch',
  width: 960,
  height: 540,
  fps: 30,
  duration: 15.2,
  background: '#e6ecec',
  phone: {x: 303, y: 23, width: 354, height: 494},
  participant: {name: 'Mina', initials: 'MN', avatar: asset('pier')},
  messages: [
    {id: 'arrival', side: 'outgoing', text: 'Docking in 5. Meet at the clock? ⛴️'},
    {id: 'entrance', side: 'incoming', text: 'Yep! Here’s how to find me.'},
    {
      id: 'market-photos',
      side: 'incoming',
      attachment: {
        kind: 'native-stack',
        width: 246,
        height: 158,
        images: photos(['ferry-clock', 'market-hall', 'pier', 'approach']),
        swipes: [{at: 1.33, duration: .5}],
      },
    },
    {id: 'lunch-ideas', side: 'incoming', at: 2.23, text: 'A few lunch options inside.'},
    {
      id: 'lunch-photos',
      side: 'incoming',
      at: 2.67,
      attachment: {
        kind: 'photo-strip',
        width: 270,
        height: 81,
        images: photos(['fish-tacos', 'grilled-cheese', 'oysters']),
        swipes: [{at: 3.1, duration: .38}, {at: 3.79, duration: .38}],
      },
    },
    {
      id: 'lunch-request',
      side: 'outgoing',
      typingFrom: 4.38,
      at: 8.17,
      text: 'Fish tacos 👩🏽‍🍳 Can we get a table by the water?',
      reaction: {at: 8.83, type: 'heart'},
    },
    {
      id: 'table-card',
      side: 'incoming',
      at: 9.7,
      attachment: {
        kind: 'app-card',
        title: 'Table for two',
        detail: 'Today, 12:40 PM · Outside',
        action: 'See details',
        image: {src: asset('fish-tacos')},
        width: 266,
        height: 184,
      },
    },
  ],
  scroll: [
    {at: 11.5, offset: 124, duration: .67},
    {at: 13.33, offset: 0, duration: .67},
  ],
  camera: {
    originX: 480,
    originY: 270,
    keyframes: {
      x: [key(0, -29), key(1.93, -14), key(4.38, -12), key(8.17, 12), key(10.7, 12), key(12.3, -2), key(15.2, 1)],
      y: [key(0, 6), key(1.93, 1), key(8.17, -2), key(10.7, -2), key(15.2, 0)],
      rotation: [key(0, -2.25), key(1.93, -.75), key(4.38, -.75), key(8.17, .45), key(10.7, .45), key(12.3, -.2), key(15.2, 0)],
      scaleX: scale,
      scaleY: scale,
    },
  },
});

await mkdir(path.dirname(output), {recursive: true});
await writeFile(output, JSON.stringify(scene, null, 2) + '\n');
await writeFile(output.replace(/\.json$/, '.events.json'), JSON.stringify({events}, null, 2) + '\n');
