import { writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [project, prototype, take = 'payoff'] = process.argv.slice(2);
if (!project || !prototype || !['payoff', 'confirmation'].includes(take)) {
  throw Error('Usage: node build.mjs PROJECT PRODUCT_MODULE [payoff|confirmation]');
}
const { threadsForFilm } = await import(pathToFileURL(resolve(prototype)));
const { coachThread, backupThread } = threadsForFilm();
const write = (file, html) => writeFileSync(resolve(project, file), html);
const text = (input) => input.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
mkdirSync(resolve(project, 'compositions'), { recursive: true });
write('transcript.json', JSON.stringify({ coachThread, backupThread }, null, 2) + '\n');

const shots = [
  { id:'opening', start:0, duration:4, label:'Saturday · 9:00 a.m.', canvas:'paper',
    title:'The scorekeeper’s<br>seat is empty.',
    prop:'<div class="assignment"><small>SCOREKEEPER</small><span class="line"></span></div>',
    line:'Pregame · Score table' },
  { id:'request', start:4, duration:4.5, label:'Coach · Messages', canvas:'green',
    title:'One text<br>to start.',
    prop:`<div class="chat"><small>Pinch Hit</small><p class="sent">${text(coachThread[0].text)}</p><p class="incoming">${text(coachThread[1].text)}</p></div>`,
    line:'Scorekeeper · Pending' },
  { id:'choice', start:8.5, duration:5, label:'Maya · Messages', canvas:'paper',
    title:'Maya gets<br>the ask.',
    prop:`<div class="chat"><small>Pinch Hit</small><p class="incoming">${text(backupThread[0].text)}</p><p class="sent">${text(backupThread[1].text)}</p></div>`,
    line:'Maya replies in her own thread' },
  { id:'result', start:13.5, duration:3.5, label:'Saturday · 9:00 a.m.', canvas:'green',
    title:take === 'payoff' ? 'The seat<br>is filled.' : 'Coverage<br>confirmed.',
    prop:take === 'payoff'
      ? '<div class="assignment filled"><small>SCOREKEEPER</small><strong>Maya</strong><span class="stamp">COVERED</span></div>'
      : `<div class="chat"><small>Coach · Messages</small><p class="incoming">${text(coachThread[2].text)}</p></div>`,
    line:take === 'payoff' ? coachThread[2].text : '' },
  { id:'end-card', start:17, duration:3, label:'The first pitch', canvas:'paper',
    title:'Pinch Hit.',
    prop:'<div class="score"><small>FIRST INNING</small><span class="diamond"></span><strong aria-label="Six to three"><span>6</span><span>–</span><span>3</span></strong></div>',
    line:'Scorekeeping, covered.' },
];

for (const shot of shots) {
  write(`compositions/${shot.id}.html`, `<template>
<style>
#root { position:absolute; inset:0; color:${shot.canvas === 'green' ? '#fff2d7' : '#173632'}; background:${shot.canvas === 'green' ? '#173632' : '#f6ebd3'}; font-family:Georgia,serif; }
.rule {position:absolute; left:76px; right:76px; top:120px; height:2px; background:#bb3e26; }
.eyebrow {position:absolute; left:76px; top:74px; font:700 22px Arial,sans-serif; letter-spacing:3px; text-transform:uppercase;}
h1 {position:absolute; left:75px; top:195px; margin:0; font-size:81px; font-weight:500; letter-spacing:-4px; line-height:1.01;}
.action {position:absolute; top:195px; right:76px; width:524px;}
.assignment,.chat,.score {position:relative; padding:28px 36px; color:#173632; background:#fff7e5; border:2px solid #295149;}
small {display:block; font:700 24px Arial,sans-serif; letter-spacing:2px; margin-bottom:22px;}
.line {display:block; height:2px; margin-top:76px; margin-bottom:14px; background:#295149;}
.assignment strong,.score strong {font-size:76px; line-height:1.1; font-style:italic; font-weight:500;}
.stamp {display:block; color:#a53423; font:700 25px Arial,sans-serif; letter-spacing:2px; margin-top:16px;}
.chat p {font:26px/1.32 Arial,sans-serif; padding:15px 19px; margin:10px 0 0; width:fit-content; max-width:390px; border-radius:20px;}
.chat .sent {margin-left:auto; background:#164989; color:#fff;}
.chat .incoming {background:#eadfca;}
.score {height:235px;}
.score strong {position:absolute; top:104px; left:172px; font-size:64px; z-index:2;}
.score strong span {display:inline-block; filter:blur(var(--hf-number-blur, 0px));
  transform:translateY(var(--hf-number-y, 0px)) scale(var(--hf-number-scale, 1));}
.diamond {display:block; width:126px; height:126px; margin:35px auto; border:3px solid #c5a77b; transform:rotate(45deg);}
.caption {position:absolute; bottom:82px; left:76px; right:76px; font:24px/1.3 Arial,sans-serif; padding-top:18px; border-top:2px solid #bb3e26;}
</style>
<section id="root" data-composition-id="${shot.id}" data-width="1280" data-height="720">
  <div class="eyebrow">${shot.label}</div>
  <div class="rule"></div>
  <h1>${shot.title}</h1>
  <div class="action">${shot.prop}</div>
  ${shot.line && `<div class="caption">${text(shot.line)}</div>`}
</section>
<script>
{
  const root = document.querySelector('[data-composition-id="${shot.id}"]#root') ??
    document.getElementById('${shot.id}');
  const tl = gsap.timeline({ paused:true });
  tl.fromTo(root.querySelector('h1'), { opacity:0, y:26 }, { opacity:1, y:0, duration:.48, ease:'power2.out' }, .08);
  tl.fromTo(root.querySelector('.action'), { opacity:0, x:38 }, { opacity:1, x:0, duration:.62, ease:'power2.out' }, .26);
  const bubbles = root.querySelectorAll('.chat p, .stamp');
  if (bubbles.length) tl.fromTo(bubbles, { opacity:0, y:12 }, { opacity:1, y:0, duration:.24,
    stagger:${shot.id === 'choice' ? 1.72 : 1.04}, ease:'power1.out' }, .72);
  if ('${shot.id}' === 'end-card') {
    // HyperFrames registry number-pop-in, with scorebook type and static glyphs.
    tl.fromTo(root.querySelectorAll('.score strong span'),
      { opacity:0, '--hf-number-y':'24px', '--hf-number-scale':.82, '--hf-number-blur':'8px' },
      { opacity:1, '--hf-number-y':'0px', '--hf-number-scale':1, '--hf-number-blur':'0px',
        duration:.34, stagger:.055, ease:'back.out(1.8)' }, .72);
  }
  const line = root.querySelector('.caption');
  if (line) tl.fromTo(line, { opacity:0 }, { opacity:1, duration:.28 },
    ${shot.id === 'result' ? 1.36 : shot.id === 'choice' ? 2.72 : shot.id === 'end-card' ? .60 : .95});
  window.__timelines['${shot.id}'] = tl;
}
</script>
</template>\n`);
}

write('index.html', `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Pinch Hit · The score table</title>
<script src="assets/gsap.min.js"></script><style>html,body{margin:0;overflow:hidden}</style></head>
<body><main id="root" data-composition-id="main" data-start="0" data-duration="20" data-fps="24" data-width="1280" data-height="720">
${shots.map(({ id, start, duration }) =>
  `<div id="${id}" class="clip" data-composition-id="${id}" data-composition-src="compositions/${id}.html" data-start="${start}" data-duration="${duration}" data-track-kind="graphics" data-track-index="0" data-width="1280" data-height="720"></div>`
).join('\n')}
<audio id="pinch-hit-score" class="clip" data-start="0" data-duration="20"
  data-track-index="1" data-volume="1" src="assets/score.wav"></audio>
</main><script>window.__timelines.main = gsap.timeline({paused:true});</script></body></html>\n`);
