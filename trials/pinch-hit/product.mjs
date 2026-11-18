export const coachCommand = 'cover 9am';
export const backupCommand = 'I can score';
export const coach = 'Coach';
export const backup = 'Maya';

export function openGame(backupOptedIn = true) {
  return { status: 'open', backupOptedIn, messages: [] };
}

export function receive(game, sender, text) {
  if (sender === coach && text === coachCommand && game.status === 'open' && game.backupOptedIn) {
    return {
      ...game,
      status: 'pending',
      messages: [
        { thread: coach, from: coach, text },
        { thread: coach, from: 'Pinch Hit', text: 'I asked Maya to keep score.' },
        { thread: backup, from: 'Pinch Hit', text: 'Can you keep score at 9 a.m.? Reply “I can score”.' },
      ],
    };
  }
  if (sender === backup && text === backupCommand && game.status === 'pending') {
    return {
      ...game,
      status: 'covered',
      messages: [
        ...game.messages,
        { thread: backup, from: backup, text },
        { thread: coach, from: 'Pinch Hit', text: 'Maya accepted. Scorekeeping is covered for 9.' },
      ],
    };
  }
  return game;
}

export function threadsForFilm() {
  const pending = receive(openGame(), coach, coachCommand);
  const covered = receive(pending, backup, backupCommand);
  return {
    coachThread: covered.messages.filter(message => message.thread === coach),
    backupThread: covered.messages.filter(message => message.thread === backup),
  };
}
