import { test } from 'node:test';
import assert from 'node:assert/strict';
import { backup, backupCommand, coach, coachCommand, openGame, receive, threadsForFilm } from './product.mjs';

test('coach request goes to the opted-in backup and stays pending', () => {
  const game = receive(openGame(), coach, coachCommand);
  assert.equal(game.status, 'pending');
  assert.equal(game.messages.find(message => message.thread === backup)?.from, 'Pinch Hit');
  assert.equal(game.messages.some(message => message.text.includes('covered')), false);
});

test('only the invited backup can cover a pending slot', () => {
  const open = openGame();
  assert.equal(receive(open, backup, backupCommand), open);
  const pending = receive(open, coach, coachCommand);
  assert.equal(receive(pending, 'Uninvited', backupCommand), pending);
  assert.equal(receive(pending, coach, backupCommand), pending);
  assert.equal(receive(pending, backup, 'maybe'), pending);
  const covered = receive(pending, backup, backupCommand);
  assert.equal(covered.status, 'covered');
  assert.equal(covered.messages.at(-2).from, backup);
  assert.equal(covered.messages.at(-1).thread, coach);
  assert.match(covered.messages.at(-1).text, /Maya accepted/);
  assert.equal(receive(covered, backup, backupCommand), covered);
});

test('repeated requests and absent consent yield no duplicate or unsolicited prompts', () => {
  const open = openGame(false);
  assert.equal(receive(open, coach, coachCommand), open);
  const pending = receive(openGame(), coach, coachCommand);
  assert.equal(receive(pending, coach, coachCommand), pending);
});

test('picture copy comes from the exercised two-thread transcript', () => {
  const { coachThread, backupThread } = threadsForFilm();
  assert.deepEqual(coachThread.map(message => message.text), [
    'cover 9am',
    'I asked Maya to keep score.',
    'Maya accepted. Scorekeeping is covered for 9.',
  ]);
  assert.deepEqual(backupThread.map(message => message.text), [
    'Can you keep score at 9 a.m.? Reply “I can score”.',
    'I can score',
  ]);
});
