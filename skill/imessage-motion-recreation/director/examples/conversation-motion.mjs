import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { CameraRig, Conversation } from '../components.mjs';

export function conversationMotion({ compact = false } = {}) {
  const phone = Conversation({
    id: 'thread',
    x: 284,
    y: 26,
    width: 392,
    height: 486,
    title: 'Noor & Inez',
    self: 'me',
    people: [
      { id: 'me', name: 'You' },
      { id: 'noor', name: 'Noor', initials: 'N', fill: '#d5e2f1' },
      { id: 'inez', name: 'Inez', initials: 'I', fill: '#eadce8' },
    ],
    messages: [
      { id: 'theater', person: 'noor', copy: 'Is everyone out of the theater?' },
      { id: 'floor', person: 'me', copy: 'Last sweep done.' },
      { id: 'lights', person: 'inez', copy: 'The hall lights are still on.' },
      { id: 'keys', person: 'me', copy: 'I’ve got the spare keys.' },
      {
        id: 'detour',
        person: 'inez',
        copy: compact ? 'Take the courtyard steps.' :
          'The side door is locked again. Take the steps by the mural and cut through the courtyard.',
      },
      {
        id: 'awning',
        person: 'noor',
        copy: 'Blue awning. I’ll wait there. ☔',
        reaction: { at: 0.93, emoji: '❤️' },
      },
      { id: 'sent', person: 'me', copy: 'On my way 🌙', at: 2.6, send: true },
      { id: 'reply', person: 'inez', copy: 'I’ll bring the thermos.', at: 3.57 },
    ],
    draft: [
      { at: 1.40, copy: 'O' },
      { at: 1.51, copy: 'On' },
      { at: 1.72, copy: 'On my' },
      { at: 1.96, copy: 'On my w' },
      { at: 2.12, copy: 'On my way' },
      { at: 2.28, copy: 'On my way 🌙' },
    ],
    scroll: [
      { at: 4.12, offset: 0 },
      { at: 5.13, offset: 138 },
      { at: 5.48, offset: 138 },
      { at: 6.42, offset: 0 },
    ],
  });
  const key = (t, value) => ({ t, value, ease: 'easeInOut' });
  const zoom = [key(0, .92), key(2.25, .98), key(5.13, 1.08), key(7.5, 1)];
  return {
    title: 'Blue Awning',
    width: 960,
    height: 540,
    fps: 30,
    duration: 7.5,
    background: '#e3e9e7',
    source: { notes: 'Original conversation and authored motion. Neutral messaging UI study.' },
    layers: [CameraRig({
      children: [phone],
      keyframes: {
        scaleX: zoom,
        scaleY: zoom,
        x: [key(0, -14), key(2.25, 2), key(5.13, 26), key(7.5, 12)],
        y: [key(0, 2), key(5.13, -3), key(7.5, 0)],
        rotation: [key(0, -1.6), key(2.25, 0), key(5.13, 1.2), key(7.5, 0)],
      },
    })],
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const [destination, variant] = process.argv.slice(2);
  if (!destination || (variant && variant !== '--compact')) {
    throw new Error('Usage: node conversation-motion.mjs OUTPUT.json [--compact]');
  }
  mkdirSync(dirname(destination), { recursive: true });
  writeFileSync(destination, JSON.stringify(conversationMotion({ compact: Boolean(variant) }), null, 2) + '\n');
}
