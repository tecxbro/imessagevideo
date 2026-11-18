import { createCanvas, loadImage } from '@napi-rs/canvas';
import { edits, width, height } from './edit.mjs';
import { threadsForFilm } from './product.mjs';

const { coachThread, backupThread } = threadsForFilm();
const fixed = (f, a, b) => Math.max(0, Math.min(1, (f - a) / (b - a)));
const ease = t => t * t * (3 - 2 * t);
const ivory = '#f8ecda';
const blue = '#1558b5';

export async function picture(editName) {
  const edit = edits[editName];
  if (!edit) throw new Error('Unknown edit: ' + editName);
  const sheet = await loadImage(new URL('./assets/plates.png', import.meta.url).pathname);
  const payoff = editName === 'final'
    ? await loadImage(new URL('./assets/payoff-plates.png', import.meta.url).pathname)
    : null;
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');
  const tileWidth = Math.floor(sheet.width / 2);
  const tileHeight = Math.floor(sheet.height / 2);

  function plate(tile, scale = 1, shift = 0, y = 0.5) {
    const scaledHeight = height * scale;
    const scaledWidth = scaledHeight * tileWidth / tileHeight;
    ctx.drawImage(sheet, tile % 2 * tileWidth, Math.floor(tile / 2) * tileHeight,
      tileWidth, tileHeight, (width - scaledWidth) / 2 + shift,
      (height - scaledHeight) * y, scaledWidth, scaledHeight);
  }

  function label(text, x, y, size, color = ivory, family = 'Georgia', weight = '') {
    ctx.fillStyle = color;
    ctx.font = `${weight} ${size}px ${family}`.trim();
    ctx.fillText(text, x, y);
  }

  function panel(x, y, w, h, r, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, r);
    ctx.fill();
  }

  function veil(x, strength) {
    const grad = ctx.createLinearGradient(x, 0, x + 585, 0);
    grad.addColorStop(0, `rgba(14,18,13,${strength})`);
    grad.addColorStop(1, 'rgba(14,18,13,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);
  }

  function bubble(text, own, x, y, w, age) {
    if (age < 0) return;
    const offset = 12 * (1 - ease(fixed(age, 0, 7)));
    const bubbleColor = own ? blue : '#e9e4d8';
    ctx.save();
    ctx.globalAlpha = fixed(age + 1, 0, 5);
    ctx.translate(0, offset);
    ctx.font = '30px system-ui';
    const lines = [];
    for (const word of text.split(' ')) {
      const last = lines.length - 1;
      const next = lines[last] ? lines[last] + ' ' + word : word;
      if (last >= 0 && ctx.measureText(next).width < w - 50) lines[last] = next;
      else lines.push(word);
    }
    const actualWidth = Math.min(w, Math.max(...lines.map(line => ctx.measureText(line).width)) + 48);
    const left = own ? x + w - actualWidth : x;
    panel(left, y, actualWidth, 37 * lines.length + 24, 17, bubbleColor);
    lines.forEach((line, index) => label(line, left + 24, y + 39 + 37 * index, 30, own ? '#fff' : '#1f2828', 'system-ui'));
    ctx.restore();
  }

  function insert({ person, x, y, first, second, third, composer, historical = false }) {
    const w = 510;
    ctx.save();
    ctx.shadowBlur = 54;
    ctx.shadowColor = 'rgba(22,14,4,.52)';
    ctx.shadowOffsetY = 13;
    panel(x, y, w, 375, 19, '#fcf6e9');
    ctx.restore();
    panel(x + 25, y + 25, w - 50, 2, 1, '#e0d3bf');
    label('Pinch Hit', x + 25, y + 65, 30, '#292d22');
    label(person + '  /  iMessage', x + 25, y + 91, 16, '#575e53', 'system-ui', '600');
    const rows = person === 'Maya' ? backupThread : coachThread;
    bubble(rows[0].text, person !== 'Maya', x + 25, y + 111, w - 50, first);
    if (second >= 0 && !historical) {
      const secondY = person === 'Maya' ? 234 : 186;
      bubble(rows[1].text, person === 'Maya', x + 25, y + secondY, w - 50, second);
    }
    if (person !== 'Maya') bubble(rows[2].text, false, x + 25, y + (historical ? 192 : 252), w - 50, third);
    if (composer) {
      panel(x + 25, y + 291, w - 50, 57, 28, '#eae4d8');
      label(composer, x + 47, y + 329, 27, '#242d2e', 'system-ui');
      panel(x + 438, y + 299, 41, 41, 21, blue);
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2.5;
      ctx.lineJoin = 'round';
      ctx.beginPath();
      ctx.moveTo(x + 449, y + 317);
      ctx.lineTo(x + 458.5, y + 309);
      ctx.lineTo(x + 468, y + 317);
      ctx.moveTo(x + 458.5, y + 309);
      ctx.lineTo(x + 458.5, y + 330);
      ctx.stroke();
    }
  }

  function opening(f) {
    plate(0, 1 + f * 0.00042, f * -0.13, 0.74);
    if (f < edit.entrance) return;
    veil(0, 0.74);
    const locator = editName === 'final' ? 'SCORE TABLE  /  SATURDAY' : 'SATURDAY';
    label(locator, 82, 548, 20, ivory, 'system-ui', '700');
    label('First pitch, 9:00', 81, 607, 56);
  }

  function chair(f) {
    const elapsed = f - edit.chairReturn;
    if (editName === 'final') plate(0, 1.035 + elapsed * 0.0003, -5 - elapsed * 0.14, 0.75);
    else plate(0, 1.13 + elapsed * 0.00074, -72 - elapsed * 0.32, 0.87);
  }

  function book(f) {
    const elapsed = f - edit.bookCut;
    const p = ease(fixed(f, edit.pencilDown, edit.markComplete));
    ctx.save();
    const push = 1 + elapsed * 0.00023;
    ctx.translate(width * (1 - push) / 2, height * (1 - push) / 2);
    ctx.scale(push, push);
    plate(3);
    const x = 850 + 23 * p;
    const y = 191 - 17 * p;
    if (p > 0) {
      ctx.strokeStyle = 'rgba(35,31,29,.85)';
      ctx.lineCap = 'round';
      ctx.lineWidth = 3.8;
      ctx.beginPath();
      ctx.moveTo(850, 191);
      ctx.lineTo(x, y);
      ctx.stroke();
    }
    const arrival = ease(fixed(f, edit.bookCut + 5, edit.pencilDown));
    const retreat = ease(fixed(f, edit.markComplete + 7, edit.markComplete + 30));
    ctx.translate(x + 154 * (1 - arrival) + 215 * retreat, y + 147 * (1 - arrival) + 108 * retreat);
    ctx.rotate(0.78 + 0.17 * arrival - p * 0.14);
    ctx.shadowColor = 'rgba(27,16,10,.42)';
    ctx.shadowBlur = 12;
    ctx.shadowOffsetY = 8;
    panel(18, -6, 231, 12, 3, '#d4a248');
    panel(29, -5, 210, 2, 1, '#f3cb71');
    panel(242, -6, 18, 12, 2, '#9b5936');
    ctx.fillStyle = '#c5a479';
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(18, -6);
    ctx.lineTo(18, 6);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#362b28';
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(5, -2);
    ctx.lineTo(5, 2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
    if (f >= edit.title) {
      veil(0, 0.82);
      label('Pinch Hit', 81, 619, 81, ivory, 'Georgia', 'italic');
    }
  }

  function coachApproach(f) {
    plate(1, 1.055 + (f - edit.fieldCut) * 0.00027, -22, 0.62);
  }

  function coachRequest(f) {
    plate(1, 1.105, -62, 0.64);
    const typed = Math.floor(fixed(f, edit.requestCut + 7, edit.send - 11) * coachThread[0].text.length);
    insert({
      person: 'Coach', x: 650, y: 172, first: f - edit.send, second: f - edit.pending, third: -1,
      composer: f < edit.send ? coachThread[0].text.slice(0, typed) || ' ' : '',
    });
  }

  function coachConfirmation(f, alternate) {
    plate(alternate ? 0 : 1, alternate ? 1.08 : 1.105, alternate ? -22 : -62, 0.65);
    insert({
      person: 'Coach', x: 650, y: 172, first: 30, second: 30,
      historical: alternate, third: f - edit.confirmed,
    });
  }

  function kitchen(f) {
    const pulse = f - edit.vibrate;
    const jitter = pulse >= 0 && pulse < 19 ? Math.sin(pulse * 2.1) * (1 - pulse / 19) * 6 : 0;
    plate(2, 1.04 + f * 0.00017, -8 + jitter, 0.61);
    if (f < edit.askCut) return;
    const typed = Math.floor(fixed(f, edit.accept - (editName === 'final' ? 27 : 35), edit.accept - 11) * backupThread[1].text.length);
    insert({
      person: 'Maya', x: 658, y: 169, first: f - edit.askCut, second: f - edit.accept, third: -1,
      composer: f < edit.accept && typed ? backupThread[1].text.slice(0, typed) : '',
    });
  }

  function payoffPlate(row, f, from, drift) {
    const elapsed = f - from;
    const h = Math.floor(payoff.height / 2);
    const scale = 1.015 + elapsed * drift;
    const w = height * scale * payoff.width / h;
    ctx.drawImage(payoff, 0, row * h, payoff.width, h,
      (width - w) / 2, height * (1 - scale) / 2, w, height * scale);
    return scale;
  }

  function occupied(f) {
    payoffPlate(0, f, edit.occupiedCut, 0.00023);
    if (f < edit.confirmed) return;
    const fade = fixed(f - edit.confirmed + 1, 0, 7);
    ctx.save();
    ctx.globalAlpha = fade;
    ctx.translate(0, 9 * (1 - ease(fade)));
    ctx.shadowColor = 'rgba(7,14,12,.38)';
    ctx.shadowBlur = 22;
    ctx.shadowOffsetY = 5;
    panel(76, 82, 470, 142, 18, '#fbf2df');
    ctx.restore();
    ctx.save();
    ctx.globalAlpha = fade;
    ctx.translate(0, 9 * (1 - ease(fade)));
    label('PINCH HIT  /  TO COACH', 102, 118, 17, '#4a554b', 'system-ui', '700');
    const [line, rest] = coachThread[2].text.split('. ');
    label(line + '.', 102, 162, 32, '#1f2828', 'system-ui', '600');
    label(rest, 102, 198, 26, '#1f2828', 'system-ui');
    ctx.restore();
  }

  function finalBook(f) {
    const scale = payoffPlate(1, f, edit.bookCut, 0.00026);
    const p = ease(fixed(f, edit.pencilDown, edit.markComplete));
    if (p > 0) {
      const tipX = width / 2 + 364 * scale;
      const tipY = height / 2 - 23 * scale;
      ctx.strokeStyle = 'rgba(46,40,33,.8)';
      ctx.lineWidth = 2.8;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(tipX + 3 - 16 * p, tipY + 2 + 13 * p);
      ctx.lineTo(tipX + 3, tipY + 2);
      ctx.stroke();
    }
    if (f >= edit.title) {
      veil(0, 0.78);
      label('Pinch Hit', 81, 619, 81, ivory, 'Georgia', 'italic');
    }
  }

  function final(f) {
    if (f < edit.fieldCut) opening(f);
    else if (f < edit.requestCut) coachApproach(f);
    else if (f < edit.chairReturn) coachRequest(f);
    else if (f < edit.askCut) chair(f);
    else if (f < edit.occupiedCut) kitchen(f);
    else if (f < edit.bookCut) occupied(f);
    else finalBook(f);
  }

  function early(f) {
    if (f < edit.fieldCut) opening(f);
    else if (f < edit.requestCut) coachApproach(f);
    else if (f < edit.chairReturn) coachRequest(f);
    else if (f < edit.confirmationCut) chair(f);
    else if (f < edit.bookCut) coachConfirmation(f, false);
    else book(f);
  }

  function alternate(f) {
    if (f < edit.confirmationCut) kitchen(f);
    else if (f < edit.bookCut) coachConfirmation(f, true);
    else book(f);
  }

  return f => {
    ctx.fillStyle = '#1b1a16';
    ctx.fillRect(0, 0, width, height);
    if (editName === 'alternate') alternate(f);
    else if (editName === 'final') final(f);
    else early(f);
    return canvas;
  };
}
