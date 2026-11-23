import {readFileSync} from 'node:fs';
import {CameraRig, Conversation} from '../../components.mjs';

function photo(filename, alt) {
  const bytes = readFileSync(new URL(`./assets/${filename}`, import.meta.url));
  return {src: `data:image/jpeg;base64,${bytes.toString('base64')}`, alt};
}

const reply = 'Three rooted cuttings 🌱';
const conversation = Conversation({
  id: 'plant-swap',
  title: 'Mara Ortiz',
  x: 285,
  y: 6,
  width: 390,
  height: 528,
  people: [
    {id: 'mara', name: 'Mara Ortiz', initials: 'MO', fill: '#80658d'},
    {id: 'nico', name: 'Nico Park', initials: 'NP', fill: '#356f5a'},
  ],
  self: 'nico',
  messages: [
    {id: 'question', at: 0, person: 'mara', copy: 'Nico, still bringing pothos?'},
    {id: 'count', at: 3.27, person: 'nico', send: true},
    {
      id: 'cuttings',
      at: 3.83,
      person: 'nico',
      attachment: {
        type: 'photo-attachment',
        width: 192,
        height: 144,
        image: photo('pothos.jpg', 'Rooted pothos cuttings in a glass jar'),
      },
    },
    {id: 'direction', at: 5.03, person: 'mara', copy: 'Perfect. Look for the yellow table.'},
    {
      id: 'landmark',
      at: 5.57,
      person: 'mara',
      attachment: {
        type: 'photo-attachment',
        width: 192,
        height: 144,
        image: photo('yellow-table.jpg', 'Yellow plant-swap table beside the garden path'),
      },
      reaction: {at: 7.13, emoji: '👍'},
    },
  ],
  draft: [
    {at: 1.17, copy: 'T'},
    {at: 1.27, copy: 'Thr'},
    {at: 1.43, copy: 'Three'},
    {at: 1.63, copy: 'Three r'},
    {at: 1.87, copy: 'Three root'},
    {at: 2.03, copy: 'Three rooted'},
    {at: 2.20, copy: 'Three rooted c'},
    {at: 2.37, copy: 'Three rooted cut'},
    {at: 2.53, copy: 'Three rooted cuttin'},
    {at: 2.67, copy: 'Three rooted cuttings'},
    {at: 2.97, copy: reply},
  ],
});

const camera = CameraRig({
  id: 'plant-swap-camera',
  originX: 480,
  originY: 270,
  children: [conversation],
  keyframes: {
    x: [{t: 5.85, value: 0}, {t: 6.97, value: 20, ease: 'easeInOut'}],
    y: [{t: 5.85, value: 0}, {t: 6.97, value: -7, ease: 'easeInOut'}],
    scaleX: [{t: 5.85, value: 1}, {t: 6.97, value: 1.08, ease: 'easeInOut'}],
    scaleY: [{t: 5.85, value: 1}, {t: 6.97, value: 1.08, ease: 'easeInOut'}],
  },
});

process.stdout.write(`${JSON.stringify({
  title: 'Saturday plant swap',
  width: 960,
  height: 540,
  fps: 30,
  duration: 9,
  background: '#e7eadf',
  layers: [camera],
}, null, 2)}\n`);
