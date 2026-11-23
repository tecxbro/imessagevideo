import {writeFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {buildWithBrowserText} from './measure-text.mjs';

export function conversationDemo({short = false} = {}) {
  return {
    id: 'lantern',
    width: 620,
    height: 650,
    fps: 30,
    duration: 9,
    background: '#e5eaf1',
    phone: {x: 127, y: 22, width: 366, height: 606},
    participant: {name: 'Nora Reyes', initials: 'NR'},
    messages: [
      {id: 'welcome', side: 'incoming', text: 'Lantern workshop is back this Friday!'},
      {id: 'schedule', side: 'outgoing', text: 'What time are you starting this year?'},
      {id: 'hours', side: 'incoming', text: 'Six and seven. The second group gets to light the lanterns at dusk.'},
      {id: 'sister', side: 'outgoing', text: 'My sister gets off work at six. Could we do seven?'},
      {id: 'availability', side: 'incoming', text: 'Seven is still open. Bring a jacket for when we go outside.'},
      {id: 'check', side: 'outgoing', text: 'Is there room at the window bench?'},
      {
        id: 'seats',
        side: 'incoming',
        text: 'Yes, two seats.',
        edit: short ? undefined : {
          at: 1.12,
          text: 'Yes! The window bench is free for the evening session. You’ll have the best view when we light the lanterns.',
        },
      },
      {
        id: 'invite',
        side: 'outgoing',
        text: 'She’s been looking forward to it 🫶🏽',
        reaction: {at: 0.65, type: 'heart'},
      },
      {
        id: 'request',
        side: 'outgoing',
        text: 'Could you hold two window seats for the evening lantern workshop? ✨',
        typingFrom: 1.63,
        at: 4.5,
      },
      {id: 'reply', side: 'incoming', text: 'Two seats held! See you at 7 🌙', at: 5.14},
    ],
    scroll: [
      {at: 5.8, offset: 125, duration: 0.65},
      {at: 7.15, offset: 0, duration: 0.65},
    ],
    camera: {
      originX: 310,
      originY: 325,
      keyframes: {
        scaleX: [{t: 0, value: 0.96}, {t: 5.3, value: 0.96}, {t: 6.7, value: 1.06, ease: 'easeInOut'}, {t: 8.6, value: 1.04, ease: 'easeInOut'}],
        scaleY: [{t: 0, value: 0.96}, {t: 5.3, value: 0.96}, {t: 6.7, value: 1.06, ease: 'easeInOut'}, {t: 8.6, value: 1.04, ease: 'easeInOut'}],
        x: [{t: 0, value: 0}, {t: 5.3, value: 0}, {t: 6.7, value: 32, ease: 'easeInOut'}, {t: 8.6, value: 24, ease: 'easeInOut'}],
      },
    },
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [destination, option] = process.argv.slice(2);
  if (!destination || (option !== undefined && option !== '--short')) {
    throw Error('Usage: node demo.mjs SCENE.json [--short]');
  }
  const {scene, events} = await buildWithBrowserText(conversationDemo({short: option === '--short'}));
  writeFileSync(destination, JSON.stringify(scene, null, 2) + '\n');
  writeFileSync(destination.replace(/\.json$/, '') + '.events.json', JSON.stringify(events, null, 2) + '\n');
}
