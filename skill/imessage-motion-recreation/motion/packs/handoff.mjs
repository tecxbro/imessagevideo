import {buildMotion as legacy} from '../../director/motions.mjs';

const id = 'conversation-handoff';
const source = {
  kind: 'authored-adaptation', ref: 'skill/imessage-motion-recreation/director/motions.mjs',
  range: [0, 4], note: 'The accepted base starter supplies the draft-to-send and reply choreography. This example replants it in the Motion stage with editable copy and v3 events.',
};

function conversationState(copy, reply, draft) {
  const messages = [];
  if (copy !== null) messages.push({id: 'message.sent', senderId: 'account.self', text: copy});
  if (reply !== null) messages.push({id: 'message.reply', senderId: 'account.remote', text: reply});
  return {
    conversationId: 'thread.motion',
    messages,
    composer: {text: draft, focused: true},
    viewport: {surface: 'conversation', anchorMessageId: messages.at(-1)?.id ?? null},
  };
}

export const entries = [{
  id,
  composite: true,
  title: 'Send an outgoing text and receive a reply',
  moves: 'Draft characters arrive in the composer, transfer into an outgoing blue bubble, and an incoming gray reply arrives after a pause.',
  fixed: 'The phone, conversation header, composer field and reading area stay in place.',
  notice: 'An outgoing request leads to an incoming answer. The quiet gap separates the two actors.',
  fits: 'Show a short request and reply in the same conversation, with composer send and inbound text.',
  avoid: 'A one-way delivery or a manual reply composition needs different event timing.',
  intents: [
    'Show the composer send an outgoing blue text and then an incoming gray reply',
    'Show a request typed, an outgoing message sent and an incoming reply',
    'Type and send a message then receive an answer in the same thread',
  ],
  editable: ['heading','copy','reply','detail'],
  source,
  build(ctx) {
    const {scene, events} = legacy(id, {copy: ctx.content.copy, duration: Math.max(2, ctx.duration), fps: ctx.fps});
    const phone = scene.layers[0];
    phone.children.find(layer => layer.id === 'phone-title').text = ctx.content.heading;
    const rows = phone.children.find(layer => layer.id === 'phone-screen').children;
    const sent = rows.find(layer => layer.id === 'sent');
    const reply = rows.find(layer => layer.id === 'reply');
    if (sent) {
      sent.keyframes.y.at(-1).value = 166;
      reply.keyframes.y[0].value = 321;
      reply.keyframes.y[1].value = 297;
      reply.children.find(layer => layer.id === 'reply-copy').text = ctx.content.reply;
    }
    const speed = ctx.duration / scene.duration;
    const retime = layer => {
      for (const keys of Object.values(layer.keyframes ?? {}))
        for (const key of keys) key.t *= speed;
      for (const child of layer.children ?? []) retime(child);
    };
    retime(phone);
    ctx.stage.children.push(ctx.group('handoff-scale', -46, -2, [phone], {scaleX: .62, scaleY: .58}));
    ctx.label(ctx.content.detail);
    ctx.setInitialUI(conversationState(null, null, ''));
    for (const event of events) {
      const fraction = event.kind === 'message_send' ? .44 : .70;
      if (event.kind === 'message_send')
        ctx.event('send', fraction, 'sent', 'message.send', conversationState(ctx.content.copy, null, ''));
      if (event.kind === 'message_arrival')
        ctx.event('receive', fraction, 'reply', 'message.receive', conversationState(ctx.content.copy, ctx.content.reply, ''));
    }
  },
}];
