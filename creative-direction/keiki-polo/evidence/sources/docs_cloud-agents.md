---
title: Cloud-served agents
description: Write one config for your agent, then let Keiki run everything.
---

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

A cloud-served agent is hosted by Keiki. You write one config with the agent's instructions,
model and feature toggles, then call `kit.sync()`. Keiki runs the whole loop for you and
handles delivery, billing, memory, browsing and code execution across every channel the
agent speaks on. You do not run a server.

```ts
await kit.sync() // push config, tools and plugins to Keiki; Keiki runs everything
```

## Quick start

```bash
bun add @onkeiki/agents
```

```ts
// src/index.ts
import { Effect } from 'effect'
import { AgentKit } from '@onkeiki/agents'

const kit = AgentKit.create({
  apiKey: process.env.KEIKI_API_KEY!,
  name: 'My Agent',

  resolveNumber: (ctx) => Effect.succeed(process.env.SMS_LINE!),

  agent: {
    model: '<model-id>',
    maxSteps: 10,
    historyLimit: 40,

    systemPrompt: ({ user, now, context }) => [
      `You are a helpful assistant.`,
      `Current time: ${now.toISOString()}`,
      context.memorySummary ? `\nAbout this user:\n${context.memorySummary}` : '',
    ].join('\n'),

    tools: [],
  },
})

await kit.sync()
```

```bash
bun run src/index.ts
# Config synced to Keiki. Keiki now runs your agent.
```

## Channels

The same config serves SMS, Telegram, Slack, email and WhatsApp. You add channels in the
dashboard, one identity per iMessage line, bot token or inbox. The config itself stays free of
channels, apart from `resolveNumber`, which picks the outbound SMS line.

Tools, plugins, memory, steering and billing all sit above the channel layer, so adding a
channel never means rewriting the agent.

### Phone calls

Add a line from an agent's **Channels** tab → **Phone calls** → **Add line**. Either buy a new
number (pick an area code or let Keiki choose one), or choose **Use the agent's iMessage line** so
callers dial the number the agent already texts from. An agent can hold more than one line; each
line has its own voice settings and can be released from the same row.

An iMessage line answers calls by forwarding them to a number only Keiki sees, billed monthly like
a bought line. What happens depends on the line:

- **Imported lines that forward instantly** answer calls as soon as they connect.
- **Dedicated lines whose provider forwards by request** show as pending until the provider
  finishes setup; Keiki checks every few minutes and marks the line live, or shows an error if
  forwarding failed.
- **Shared lines** can't forward calls; buy a new number instead.
- **Other lines** can't forward automatically yet. **Request call forwarding** emails the team to
  set it up by hand.

**Stop answering calls** turns forwarding off before the hidden number is released. When the
provider turns it off by request, the agent stops answering right away and the hidden number is
kept until the provider confirms. Releasing the iMessage line, or removing it from the agent, also stops its calls.
If the line's provider account is disconnected first, the agent stops answering and the hidden
number is kept, since the provider can no longer be asked to stop forwarding.

### RCS and A2A (early access)

RCS and A2A (agent-to-agent communication) are not live yet. Request early access from
**Channels → Add channel → RCS** or **A2A**, or from an agent editor's **Channels** section,
including while creating a draft. Tell us your purpose and expected monthly message volume; you can
update each request later, and the team will follow up.

### iMessage

A threaded reply is answered as what the contact wrote, and the agent also sees the message
they replied to. A photo and the text sent with it in one go arrive as a single message: the
agent reads the text and the attachment together.

On a dedicated iMessage line bought in Keiki, the agent can also send screen and bubble
effects, reply to a specific message in the thread, send a voice note that plays in a bubble
(send_file with voice), and use app cards when the iMessage Apps add-on is on.

The agent sees each contact message's id, so it can leave a tapback on it or answer it as a
threaded reply. Tapbacks, effects and threaded replies work on every iMessage line, imported
lines included; polls and voice notes work on iMessage lines, and app cards need the iMessage Apps
add-on plus a dedicated line bought in Keiki.

If no iMessage device receives a message within about 10 minutes, the conversation on the
dashboard shows it as **Not delivered**.

#### Shared iMessage number

When Keiki has a shared iMessage number, the agent's Channels tab shows it as **Shared iMessage
number**, with a join code such as `K-7QF2MD` and a **Copy link** button. The link opens Messages
with a first text already typed: a message a customer of this agent might send, written from the
agent's name and prompt, followed by the code (for example `do you have a table for 4 friday? (K-7QF2MD)`).
Editing the name or prompt writes a new one; with no prompt, or when it can't be written, the text is `Hi!`. A contact who texts the code is connected to this agent, and their
later messages on that number reach it without the code. The shared number needs an active plan, except as
a test from onboarding: without a plan, the row shows Plan required, but while **/onboarding** is open
(and for 15 minutes after, up to a day after the code first showed) a code sent to the number connects
the contact and the agent replies under the Live Test limits (a small model, no tools, no memory, a few
steps) without using credits. Once the test ends, the agent can't reply or send on the number.

A shared number carries agents from many organizations, so:

- A contact talks to one agent per shared number. Texting another agent's code switches the
  contact to that agent: the message reaches the new agent, which replies to it, and the previous
  agent no longer receives or sends to that contact on the number. The switch is refused, and the
  message reaches neither agent, when the new agent can't take contacts (no plan and no open test).
- A message from someone who hasn't sent a code reaches no agent.
- The agent only replies to contacts who texted it first.
- A group chat on the shared number also talks to one agent. A code posted in the group connects
  the group to that agent; with no code, the group takes the agent of the first connected member
  who writes in it. Only an agent with [Group chats](#group-chats) enabled takes a group. After
  that, any member posting another agent's code switches the group to that agent, the same way a
  contact switches. A group no agent is connected to is ignored.
- Contact cards (name and photo) aren't sent from a shared number, because they would belong to
  every agent on it.
- The daily ceilings in [iMessage best practices](/docs/imessage-best-practices.md) count every
  organization's sends on the shared number together.

Photos, videos, voice notes and files sent to an iMessage line are stored the same way as
WhatsApp attachments (see [Attachments](#attachments)): the annotation carries `attachment_id`,
`mime` and `size` next to the description, and a webhook tool called with that ID gets a
`context.attachments[<id>].url` to fetch the original file. Code tools get the same entry as
`ctx.attachments[<id>]`.

### WhatsApp

#### Native cards with `send_card`

`send_card` sends one json-render spec as reply buttons, a list, a URL button or text,
depending on the card's actions. Oversized bodies or labels come back to the agent as
`issues` instead of being truncated. The same spec renders as Block Kit on Slack and an
Adaptive Card on Teams. See [Native cards](/docs/native-cards.md).

A reply doesn't end the turn. The agent can say "one moment, I'm searching" and keep calling
tools in the same turn, as it does on every other channel.

A photo or file and the text sent alongside it are answered together after the attachment has
been read; an unsent reply with no tools run is redone when another message arrives.

A reply that quotes an earlier message reaches the agent with the quoted text, and the SDK
receives it as `replyToContent` alongside `replyToMessageId`. WhatsApp sends only the quoted
message's ID, so Keiki looks up its text in the conversation. A quote of a message Keiki never
saw, such as one sent from another app, arrives with the ID only.

A reaction is feedback, not a message. It never starts a turn, so the agent doesn't answer a
❤️ with another one. It is saved as a feedback signal on the message it was left on, not shown
in the conversation. A negative one such as 👎 counts in Improvements as the contact rejecting
that reply. Reactions work the same way on every iMessage line.

Keiki tracks a delivery receipt for every message the agent sends: sent, delivered, read or
failed. A failed message shows **Not delivered** under its bubble in the conversation, with
WhatsApp's error code and reason (for example `131047 Re-engagement message`). Receipts
arrive on the same `messages` webhook field as inbound messages, so a Meta number needs no
extra subscription. Kapso numbers are subscribed to receipt events automatically.

#### Contacts who hide their number

A WhatsApp user who turns on a username can write without sharing their phone number. Meta
then names them only by their business-scoped user ID (BSUID), such as
`EG.2102026660705306`. Webhook tools receive it on every call as `context.userId` and in an
`X-Orchid-User-Id` header, authored tools read it as `ctx.channel.businessScopedUserId`, and
the escalation webhook carries it as `userId`. This happens
whether or not a phone number came with the message. `context.phone` stays `wa:` plus the
contact's number whenever Meta sends one. For a contact with no number it is `wa:` plus their
BSUID, and replies go to that BSUID. A contact who wrote from their number before turning on a
username stays in the same conversation.

#### Attachments

When durable storage is available, an inbound WhatsApp media annotation includes
`attachment_id`, `media_id`, `mime` and `size`, along with any filename and extracted
description. A webhook tool called with an attachment ID receives a
`context.attachments[<id>]` entry with `filename`, `mime_type`, `size`, `sha256` and a
`url` that is valid for 15 minutes; code tools get the same entry as
`ctx.attachments[<id>]`. Attachments are kept for 90 days by default
(`ATTACHMENT_RETENTION_DAYS`) and removed when conversation history is cleared. The
bytes live in the platform's object store (`OBJECT_STORE_BUCKET`, an S3 bucket only the
server can reach); without one the conversation's Archil disk is used, and without
either, annotations keep the `media_id` but have no `attachment_id`.

##### Reading images and PDFs

The built-in agent's model receives a text description of an inbound photo, not pixels
or a download link. A separate media model describes the image through OpenRouter.
The platform's `MEDIA_MODEL` environment variable selects that reader; the default is
`google/gemini-2.5-flash`. Selecting a vision-capable model for the agent does not change
this input format.

PDFs become extracted text: Keiki tries Context.dev parsing when configured, then falls
back to the media model. The prompt includes up to 20,000 characters of document text.
When overflow can be stored, the annotation includes a marker for `spill_read` and
`spill_search` to retrieve the rest. Otherwise it says the remaining text was not kept.

For work that needs the original file, use `download_attachment`. For example, a stored
photo can appear in the agent's message as:

```text
[Attachment: receipt.jpg; attachment_id=att_D6kl04dQnJ7pvFI49OCHmw; mime=image/jpeg; size=4830: A receipt showing a total of $6.75.]
```

The tool takes these parameters:

| Parameter | Required | Meaning |
|---|---|---|
| `attachment_id` | Yes | Copy the ID from the inbound attachment annotation. |
| `path` | Yes | Destination relative to this conversation's folder in the persistent sandbox, such as `receipt.jpg`. |
| `message_id` | Email only | Copy the message ID from the email attachment annotation. Not needed for iMessage. |

Example tool arguments and result for the stored photo:

```json
{ "attachment_id": "att_D6kl04dQnJ7pvFI49OCHmw", "path": "receipt.jpg" }
```

```json
{ "success": true, "path": "receipt.jpg", "bytes": 4830, "mime": "image/jpeg" }
```

Code tools can then run OCR or parse the downloaded file using software available in the
sandbox. Downloading does not add pixels to the agent model's context; return the OCR or
parser output as text. Only files from the current conversation can be downloaded.
Stored-file downloads are limited to 100 MB and fail if the file is missing or expired.
The 90-day default retention above applies to stored originals, not a new retention
period for a copy already downloaded to the persistent sandbox.

The tool is offered on channels with native `receiveFiles` capability and requires the
sandbox add-on. It is not available in billing sandbox mode, which disables model tools;
that mode is separate from the persistent code sandbox. Stored-file downloads work for
iMessage, WhatsApp and Microsoft Teams; Slack, Telegram and email also support
downloads using their provider attachment IDs.

If your model needs the image itself, an [external harness](/docs/external-harness#reading-attachments-with-your-own-model)
can fetch stored attachments and pass them to its own vision model.

#### Sending files and voice notes

`send_file` delivers a sandbox file on WhatsApp as well as iMessage, Slack, Telegram and email.
On WhatsApp, JPEG and PNG images, MP4 and 3GP videos and common audio formats play inline;
anything else arrives as a document with its file name. Files are limited to 100 MB, and Meta
applies its own lower limits per type (5 MB for images, 16 MB for audio and video). Pass
`reply_to_message_id` to send the file as a reply to a message, as on Telegram.

With `voice`, an audio file is sent as a voice note: on WhatsApp it must be OGG/Opus, on
Telegram OGG/Opus, MP3 or M4A, and on iMessage any of the formats the tool lists. WhatsApp
voice notes and audio files carry no caption, so the tool returns `caption_delivered: false`
and the agent sends the caption as its own message.

#### Editing and deleting sent messages

`update_message` replaces the text of a message the agent sent on iMessage, Slack,
Microsoft Teams and Telegram. `delete_message` removes it for everyone on the same channels.
Both take the `message_id` that `reply` returned. On iMessage, the contact must be on iMessage
rather than SMS, and Apple's own time limits apply. Some iMessage lines can edit but not unsend;
`delete_message` is not offered on those lines.
On Slack, the message must be in the current thread.
Telegram only lets a bot change or delete its own messages; for deletion, the message must
also be less than 48 hours old in a private chat. When Telegram refuses, the tool returns
Telegram's own reason. A deleted message is also removed from the conversation's transcript,
so the agent does not recall it on later turns.

#### Steered turns

A turn someone on your team steers from the dashboard runs with the conversation's real
history and tools, but nothing it does reaches the contact. A webhook tool called from such a
turn receives `X-Orchid-Internal: true` and `context.internal: true`, and `context.messages`
holds what the team member typed, because that message never arrived through the channel.
A tool that keeps its own record of inbound messages should read `context.messages` in that
case instead of concluding the contact said nothing new.

Direct desktop chats use `POST /api/webapp/conversations/:identity/steer?agentId=...`
with `{ "text": "...", "stream": true }`. A fresh `api:<agentId>:<conversationId>`
identity can start its first turn when the signed-in organization owns that agent
and the identity names the same agent. Other identities must already have messages
for the selected agent. Browser, terminal and takeover controls still require an
existing conversation.

### Group chats

Enable **Group chats** (`features.groupChats`) on the agent to join groups. It is off
for new agents; agents already seen in a Telegram group keep it enabled. When off,
group messages are ignored without storing context or updating group routing. Private
chats are unaffected. Telegram and iMessage share the same
group-chat engine and context buffer.

iMessage groups work on lines with channel `photon` or `blooio`, dedicated or
[shared](#shared-imessage-number). Lines with channel `linq` ignore groups with reason
`group_chats_unsupported`, regardless of the toggle.
The agent answers when someone leads with its name (or the first word of its name),
uses an `@name` anywhere, or replies to one of its messages. Replies within a native
thread the agent has already answered also address it, even when the provider names
the original group message as the reply target. A message that names the agent mid-sentence
("thoughts, Pablo?"), any message within five minutes of the agent's last group reply, or
any message while it is still answering someone in the group gets a second look from a
small decisions model, which answers only when the message is for the agent (a follow-up
like "and tomorrow?", or "also Rome" from anyone while it answers). The model also sees the
request a running reply is answering, and a message it passes then is folded into that
reply, whoever sent it. If that model is unavailable, the agent stays quiet. Other
messages are saved quietly as context.
Each group has its own `imsg:chat:<provider chat id>` conversation, with sender
names on observed and current messages. Replies stay on the group's exact line and
chat, threaded to the message that addressed the agent. Contact cards, per-contact
location requests and new-contact counters do not apply to group identities.

In a Telegram group, the bot answers only when someone addresses it. That means an @-mention
of its handle, a reply to one of its own messages, a slash command such as `/cmd` or
`/cmd@thisbot`, or its display name leading the message. Commands aimed at another bot are
ignored. Everything else is read quietly and kept as context, so staying silent does not mean
losing the thread. Group messages reach the model labelled with the sender's name, and the
whole group shares one conversation, so members share history and memory. Private chats are
unchanged, and every message there is answered under the sender's own conversation.

For Telegram, you can change this per identity:

```json
{ "replyMode": "always", "identity": "user", "mentionAliases": [] }
```

`mentionAliases` defaults to the bot's display name. Set it to `[]` to require a real
@-mention, or list your own aliases. A value of `null` restores the default. With
`replyMode: "always"` the bot answers every group message. With `identity: "user"` each
member gets their own conversation.

The SDK's `telegram()` plugin does the same for agents you host yourself:

```ts
import { telegram } from '@onkeiki/agents-plugins'

telegram({
  botToken: process.env.TG_BOT_TOKEN!,
  groupReplyMode: 'mention',        // 'always' answers every group message
  mentionAliases: ['roomie'],       // extra leading names that address the bot
  groupIdentity: 'chat',            // 'user' splits members into separate conversations
  allowedChatIds: [-1001234567890], // optional allowlist
})
```

> Mention-gating is the default. A group that used to answer every message needs
> `replyMode: "always"` to keep doing so.

### Telegram widgets

With **Dynamic UI** on, a private Telegram chat offers `send_widget`, the same tool that sends
app cards on iMessage. It sends a
self-contained HTML document that Telegram draws inside the message, and
`update_widget` replaces its data later. Telegram shows widgets in private chats
only and runs them offline, so they can't load anything from the network. Inline
`<style>` and `<script>` work, and images must be `data:` URLs or inline SVG. The HTML can
be up to 32,768 bytes, and 4,096 bytes after zlib compression. The tool checks both limits
before sending.

```js
// Inside the widget: read state, ask the agent, redraw when it answers.
render(JSON.parse(TelegramWidget.chatData || '{}'))
TelegramWidget.onEvent('chatDataChanged', () => render(JSON.parse(TelegramWidget.chatData)))
button.addEventListener('click', () => TelegramWidget.request('vote:2'))
```

With `allow_queries: true`, `TelegramWidget.request(data)` reaches the agent as a widget
request in the conversation, with the widget's `message_id` and the data. Telegram wants
an answer within 15 seconds, so Keiki settles the request at once with `{ result: null }`.
The agent answers by calling `update_widget`, and open widgets get the new data
through `chatDataChanged`. A bot connected before widgets existed has its webhook
re-registered to receive widget requests the first time it sends an interactive widget.

### Card numbers on Telegram

Telegram marks bank card numbers in the messages it delivers. Keiki replaces each marked
number with a note that keeps only the last four digits, before the message is stored,
observed in a group or shown to the agent. This covers captions and quoted replies too, and
needs no setup.

### iMessage app cards

The iMessage Apps add-on lets tools open an HTTPS page as a card on an eligible
Keiki-bought dedicated line. Not every line type supports cards; `send_widget` is
only offered on supported lines. See [iMessage Apps](/docs/imessage-apps) for setup,
tool inputs and delivery results.

## Add your own tools

```ts
import { AgentKit, defineTool } from '@onkeiki/agents'
import { Schema, Effect } from 'effect'

const checkWeather = defineTool({
  name: 'check_weather',
  description: 'Get current weather for a city',
  input: Schema.Struct({ city: Schema.String }),
  // execute cannot fail with a typed error. A thrown error or rejected promise
  // fails the tool call, and the model sees that the call failed.
  execute: (input) =>
    Effect.promise(async () => {
      const res = await fetch(`https://api.example.com/weather?city=${encodeURIComponent(input.city)}`)
      return (await res.json()) as { tempC: number }
    }),
})

const searchFlights = defineTool({
  name: 'search_flights',
  description: 'Search for flights between two cities',
  input: Schema.Struct({ from: Schema.String, to: Schema.String, date: Schema.String }),
  execute: (input, ctx) =>
    Effect.gen(function* () {
      const result = yield* ctx.platform.browse(
        `Search flights from ${input.from} to ${input.to} on ${input.date}`
      )
      return { flights: result.content }
    }).pipe(Effect.orDie),
})

const kit = AgentKit.create({
  // ...
  agent: {
    // ...
    tools: [checkWeather, searchFlights],
  },
})
```

## Managed features

Turn a feature on in config, and Keiki runs the infrastructure behind it.

```ts
import { Effect } from 'effect'
import { AgentKit } from '@onkeiki/agents'

const kit = AgentKit.create({
  // ...
  agent: {
    model: '<model-id>',
    maxSteps: 10,
    historyLimit: 40,
    systemPrompt: ({ user, now, context }) => `...`,
    tools: [checkWeather],

    // Per-user memory: facts, preferences, context recall
    memory: {
      enabled: true,
      provider: 'supermemory',
      autoRetrieve: true,
      categories: ['personal', 'work', 'preference', 'context'],
    },

    // Cloud browser, with a handoff to a person when needed
    browser: { enabled: true, handoff: true, screenshotDelivery: true },

    // Persistent code sandbox
    sandbox: { enabled: true, persistent: true, maxExecTime: '5 minutes' },

    // Background job runner
    executor: { enabled: true, maxConcurrent: 3, timeout: '10 minutes', onComplete: 'notify' },

    // State shared across the steps of one turn
    blackboard: true,

    // Cache breakpoints to cut inference cost
    promptCache: true,

    // Send a conversation to a person
    escalation: {
      enabled: true,
      requireConfirmation: true,
      routes: {
        webhook: 'https://my-app.com/api/escalations',
        slack: { channel: '#support' },
        email: 'support@mycompany.com',
      },
    },

    // Gather rapid messages, and interrupt a turn when a new one lands
    steering: { debounceWindow: '2 seconds', midTurnStrategy: 'interrupt', maxBatch: 5 },

    // Handle attachments before the agent sees them
    media: {
      audio: { action: 'transcribe' },
      image: { action: 'describe' },
      video: { action: 'describe' },
      document: { action: 'extract' },
      fallback: '[Unreadable attachment]',
    },
  },

  // Lifecycle hooks
  events: {
    onInbound: (msg) => Effect.succeed({ proceed: true }),
    onOutbound: (msg) => Effect.promise(() => analytics.track('sent', msg)),
    onNewUser: (event) => Effect.promise(() => slack.post('#signups', event.phone)),
    onOptOut: (event) => Effect.promise(() => crm.markOptedOut(event.phone)),
  },
})
```

When self-hosted, `/turn`, `/alerts/execute`, `/delivery` and `/events/*` require
`Authorization: Bearer <agent API key>`. Requests without the correct key receive 401 before
the route handler runs.
The server answers CORS preflight (`OPTIONS`) on these routes itself with 204, allowing
`Authorization` and `Content-Type` from any origin; non-OPTIONS requests still require the key.

## Plugins

Plugins are the main way to extend an agent with reusable abilities. Each one is
self-contained. It owns its config and contributes tools, hooks, routes and layers without
touching the core agent config.

```bash
bun add @onkeiki/agents-plugins
```

```ts
import { AgentKit, braintrustExporter } from '@onkeiki/agents'
import { memory, browser, steering, media, observability, alerts } from '@onkeiki/agents-plugins'

const kit = AgentKit.create({
  apiKey: process.env.KEIKI_API_KEY!,
  name: 'My Agent',

  plugins: [
    memory({ provider: 'supermemory', autoRetrieve: true }),
    browser({ handoff: true, screenshotDelivery: true }),
    steering({ debounceWindow: '2 seconds', midTurnStrategy: 'interrupt', maxBatch: 5 }),
    media({ audio: 'transcribe', image: 'describe', video: 'describe', document: 'extract' }),
    observability({ exporters: [braintrustExporter({ apiKey: '...', projectName: 'my-agent' })] }),
    alerts({ alerts: [dailyBriefing] }),
  ],

  agent: {
    model: '<model-id>',
    maxSteps: 10,
    historyLimit: 40,
    systemPrompt: () => `...`,
    tools: [myCustomTool],  // only your custom tools here
  },
})

await kit.sync()
```

### Built-in plugins

| Plugin | What it does |
| --- | --- |
| `memory(opts)` | Per-user memory. It retrieves facts before each turn and extracts new ones after. |
| `browser(opts)` | Cloud browser, with a handoff to a person and screenshot delivery. |
| `sandbox(opts)` | Persistent code sandbox. |
| `executor(opts)` | Background job runner with concurrency limits. |
| `steering(opts)` | Gathers rapid messages, and interrupts, appends or queues mid-turn. |
| `media(opts)` | Handles inbound attachments: transcribe audio, describe images, extract documents. |
| `escalation(opts)` | Always queues a conversation in the dashboard Handoffs queue; configured webhook, Slack or email routes add notifications. |
| `observability(opts)` | Exports traces to Braintrust, Axiom, OpenTelemetry or a backend of your own. |
| `alerts(opts)` | Scheduled or triggered broadcasts, with de-duplication. |
| `events(handlers)` | Lifecycle handlers: onInbound, onOutbound, onNewUser, onOptOut. |
| `mcp(opts)` | Lets people add MCP servers and OpenAPI specs at runtime. Requires `sandbox()`. |

### Write a plugin

A plugin satisfies the `AgentKitPlugin` interface. Use `definePlugin()` for type safety.

```ts
import { Effect } from 'effect'
import { definePlugin } from '@onkeiki/agents'

export const analytics = (opts: { posthogKey: string }) =>
  definePlugin({
    id: 'analytics',
    hooks: {
      afterTurn: (result) =>
        Effect.promise(() =>
          posthog.capture('sms_turn', {
            phone: result.phone,
            toolCalls: result.toolCalls.length,
            tokensUsed: result.tokensUsed,
            durationMs: result.durationMs,
          })
        ),
    },
  })
```

### MCP plugin

The `mcp()` plugin lets the agent, and the people talking to it, connect tools at runtime.
It runs inside the agent's sandbox and exposes two tools:

- `mcp_add_source` connects a remote MCP server by URL, or a REST API by its OpenAPI spec;
- `mcp_execute` runs JavaScript against the connected sources' tools.

Sources with no auth connect on their own. Sources that need an API key or OAuth return a
link the user opens once to authorize. The plugin requires `sandbox()` and throws at boot
without it.

```ts
import { AgentKit } from '@onkeiki/agents'
import { sandbox, mcp } from '@onkeiki/agents-plugins'

const kit = AgentKit.create({
  // ...
  plugins: [
    sandbox({ persistent: true }),
    mcp({
      maxServers: 5,
      userCanAdd: true,
      servers: [{ url: 'https://my-internal-mcp.example.com/mcp' }],
    }),
  ],
})
```

### Plugin interface

```ts
import type { Effect, Layer } from 'effect'
import type {
  AlertDefinition,
  PluginContext,
  PluginInitResult,
  ToolDefinition,
  RouteContext,
  TurnEvent,
  TurnResult,
  ToolCallEvent,
  ToolCallResult,
  SyncPayload,
  PluginMigration,
} from '@onkeiki/agents'

type AgentKitPlugin = {
  readonly id: string

  // Called once at boot. It may return partial config overrides.
  readonly init?: (ctx: PluginContext) => PluginInitResult | void

  // Tools contributed to the agent
  readonly tools?: ReadonlyArray<ToolDefinition<any, any>>

  readonly alerts?: ReadonlyArray<AlertDefinition>

  // HTTP routes, for webhooks and alert execution
  readonly routes?: Readonly<Record<string, (req: Request, ctx: RouteContext) => Promise<Response>>>

  // Lifecycle hooks
  readonly hooks?: {
    readonly beforeTurn?: (turn: TurnEvent) => Effect.Effect<TurnEvent>
    readonly afterTurn?: (result: TurnResult) => Effect.Effect<void>
    readonly beforeToolCall?: (call: ToolCallEvent) => Effect.Effect<ToolCallEvent>
    readonly afterToolCall?: (result: ToolCallResult) => Effect.Effect<ToolCallResult>
  }

  // Global request and response interceptors
  readonly onRequest?: (req: Request) => Effect.Effect<Request | Response | void>
  readonly onResponse?: (res: Response) => Effect.Effect<Response>

  // Effect service layers
  readonly layers?: ReadonlyArray<Layer.Layer<any>>

  // Add to the sync payload
  readonly onSync?: (payload: SyncPayload) => SyncPayload

  // Path-matched middleware
  readonly middleware?: ReadonlyArray<{
    readonly path: string
    readonly handler: (req: Request, ctx: RouteContext) => Effect.Effect<Response | void>
  }>

  // Database migrations owned by this plugin
  readonly migrations?: ReadonlyArray<PluginMigration>
}
```

The `plugins` field is optional. Configs that set features directly on `agent`, such as
`memory: { enabled: true }`, keep working. Plugins are additive.

## Observability

Send turn traces to your own observability platform. Keiki always records traces internally
and keeps them for 14 days. Exporters send copies to external services.

```ts
import { AgentKit, braintrustExporter, axiomExporter, otelExporter, customExporter } from '@onkeiki/agents'

observability: {
  enabled: true,
  exporters: [
    braintrustExporter({ apiKey: process.env.BRAINTRUST_API_KEY!, projectName: 'my-agent' }),
    axiomExporter({ apiToken: process.env.AXIOM_TOKEN!, dataset: 'my-agent-traces' }),
    otelExporter({
      endpoint: process.env.OTEL_ENDPOINT!,      // e.g. https://tempo.myinfra.com
      headers: { 'X-Scope-OrgID': 'my-org' },
      serviceName: 'my-agent',
    }),
  ],
  sampleRate: 0.5,       // Export 50% of traces. Keiki keeps 100%.
  redactInputs: true,    // Strip PII from span inputs before export
  redactOutputs: false,  // Keep outputs, which helps when debugging
}
```

A custom exporter is a name plus an `exportFn(trace)` pointed at your own endpoint.

## Storage

For a cloud agent, Keiki stores message history, users and metering, so your config needs no
storage setup. If you run the loop yourself, you supply a storage adapter. The SDK ships
adapters for the common databases, and you can implement a `Storage` backend of your own.

## Phone numbers

You can assign phone numbers per person, or spread the load across a pool.

```ts
import { AgentKit } from '@onkeiki/agents'
import { Effect } from 'effect'

const kit = AgentKit.create({
  // ...
  resolveNumber: (ctx) =>
    Effect.gen(function* () {
      // Check whether the user already has a sticky line
      const existing = yield* ctx.platform.getUserMeta(ctx.phone, 'assigned_line')
      if (existing) return existing

      const line = yield* ctx.platform.acquireLine({
        pool: 'us-west',
        strategy: 'least-active',
        sticky: true,
      })

      yield* ctx.platform.setUserMeta(ctx.phone, 'assigned_line', line.number)
      return line.number
    }),
})
```

## Alerts

Alerts run on a schedule and broadcast to subscribers.

```ts
import { AgentKit, defineAlert } from '@onkeiki/agents'
import { Effect } from 'effect'

const dailyBriefing = defineAlert({
  name: 'daily_briefing',
  description: 'Morning summary of tasks and weather',
  schedule: { type: 'cron', expression: '0 7 * * *', timezone: 'America/New_York' },
  dedupKey: (ctx) => `briefing-${ctx.now.toISOString().slice(0, 10)}`,
  shouldSend: (ctx) => Effect.succeed(ctx.subscriber.preferences.dailyBriefing !== false),
  generate: (ctx) =>
    Effect.succeed({ text: `Good morning! Here's your briefing for ${ctx.now.toLocaleDateString()}...` }),
})

const kit = AgentKit.create({
  // ...
  agent: {
    // ...
    alerts: [dailyBriefing],
  },
})
```

## Developer REST API

You can manage your agent over REST, using your API key.

`/config` and `/tools` act on one agent. A key bound to an agent always acts on that agent.
An org-wide key can act on any agent in your organization by naming it with `agent_id`: in the
query for `GET` and `DELETE`, and in the JSON body otherwise. `GET /agents` lists the agents a
key can name. If an org-wide key names no agent, `/config` acts on the key's only active agent,
and returns `400` with the key's agents when it has more than one. Until the key has an agent,
`/config` reads and writes the key-level config (`agent_id: null` in the response). `/tools`
without `agent_id` uses the key's most recently active agent. A `PATCH` only changes the fields it sends, and `features` only changes the flags it
names. A `PATCH` with a `rollout` stages the change for a share of conversations instead (see
[Staged rollouts](#staged-rollouts)). `escalation_routes` must point at your organization's own webhooks and Slack workspaces.
`steering_config` applies to every agent on the key.

A key bound to an agent only reaches that agent. Outcomes, alerts, traces and harness turns are
held to it, and a sibling agent's record answers `404`. What belongs to the whole organization
answers `403` (`An org-wide API key is required`): `/api/v1/keys`, `/api/v1/orgs`,
`/api/v1/billing`, `/audit`, `/usage`, `/people`, the line routes (`/phones/*` and line provisioning), `steering_config`, and
every secret write (`PUT` and `DELETE /secrets/:name`, `/secrets/:name/proxy`, `/secrets/sync`).
`GET /secrets` still lists secret names. `/sync` from a bound key answers `403` for `secrets` or
a capability with a `runtime` to publish, and `409` for an alert name another agent already uses.

```bash
# List the agents this key can act on
curl -H "Authorization: Bearer $API_KEY" https://<your-host>/api/v1/developer/agents

# Read agent config (org-wide key: add ?agent_id=<agent-id>)
curl -H "Authorization: Bearer $API_KEY" https://<your-host>/api/v1/developer/config

# Update the system prompt; other fields keep their values
curl -X PATCH -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "<agent-id>", "system_prompt": "You are..."}' \
  https://<your-host>/api/v1/developer/config

# Upload a custom tool that Keiki calls over a webhook
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "check_weather",
    "description": "Get weather for a city",
    "inputSchema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    "executionType": "webhook",
    "webhookUrl": "https://my-app.com/api/tools/weather"
  }' \
  https://<your-host>/api/v1/developer/tools

# Acquire a phone number
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -d '{"pool": "us-west", "strategy": "least-active"}' \
  https://<your-host>/api/v1/developer/phones/acquire

# Check usage
curl -H "Authorization: Bearer $API_KEY" https://<your-host>/api/v1/developer/usage
```

Usage is counted per API key per month, the same way for every harness, the external harness
included: `turns` (conversation turns, playground and copilot excluded), `tokens_in` and
`tokens_out` (as each turn reports them), `messages` (each message the agent sent, counted once
when it is stored, so an edit is not a new message) and `tool_calls` (tool calls that
completed).

A webhook tool receives `{ "input": {...}, "context": {...} }` and returns JSON, which the agent
reads as the tool's result. If the tool sends the contact something itself, from your own
backend (a card, a document), add `delivered` to the result: a short description of what the
contact received, or an array with one per message (up to 10, each kept to its first 2,000
characters). Keiki records each as a message the agent sent in that turn. Later turns can then read it in their history and find it with
`conversation_search`, and the dashboard shows it in the conversation. Without it, the
transcript only has the reply that came after.

```json
{
  "cardDelivery": { "state": "accepted" },
  "delivered": "Job card: Growth Marketing Manager, iGaming (Remote) at SmartRecruitment.com"
}
```


### When a handoff closes

Every escalation opens a handoff in the dashboard Handoffs queue. While nobody has claimed it, the
agent keeps answering the contact, so it can still solve the problem itself. A handoff closes in
one of these ways:

- **A teammate resolves it or hands it back**, from the dashboard or the Slack thread.
- **The agent closes it** with the `resolve_escalation` tool, when it solved the problem without a
  person (for example, it sent the sign-in link the contact needed). It passes a short `summary`,
  which the transcript shows on the handoff's resolved marker. It only closes handoffs the agent
  opened itself, not a takeover a teammate started.
- **It goes stale.** A handoff nobody claims closes itself 7 days after it was opened or last
  escalated again, closed by system.

When the agent closes a handoff, its Slack thread is closed with the agent's summary. A stale
handoff's thread is closed when the agent next escalates that conversation, and the new
escalation gets a fresh thread.

Once a teammate claims a handoff, it stays with them: the agent is silent, `resolve_escalation`
refuses to close it, and it never goes stale. It only ends when the teammate hands it back or
resolves it.

### Hand work to a person

You can hand any kind of work to an operator, whether or not the agent escalated it. Keiki
announces it in the agent's Slack destination as a thread, with the buttons your request
supplied. It needs the agent's operator-handoff capability. If the response says
`announced: false`, the thread exists but no Slack install is configured to show it.

```bash
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: signup_9f2" \
  -d '{
    "workType": "waitlist_review",
    "subject": {
      "provider": "keiki",
      "connectionId": "wh_7",
      "resourceType": "waitlist_entry",
      "resourceId": "e_412"
    },
    "title": "Waitlist review",
    "summary": "Ada, 4, mornings",
    "details": [{"label": "Signed up", "value": "today"}],
    "actions": [
      {
        "key": "approve",
        "label": "Approve",
        "style": "primary",
        "operation": { "type": "webhook.invoke", "webhookId": "wh_7" }
      },
      {
        "key": "open_ticket",
        "label": "Open a ticket",
        "operation": {
          "type": "capability.tool",
          "capability": "zendesk",
          "tool": "create_ticket",
          "arguments": { "requester_id": "91" }
        }
      }
    ]
  }' \
  https://<your-host>/api/v1/developer/handoffs
```

Send `conversation` instead of `subject` to hand over one of the agent's own conversations.
That thread also offers reply (which takes the conversation over) and hand back, and operators can answer straight from it ([Handoff threads](/docs/slack-agents.md#handoff-threads)). Anything else is named by reference
and gets no conversation controls.

A reply a person sends while they hold a conversation, from that Slack thread or from a
dashboard takeover, stays in the agent's history as sent by the team, not by the agent. Once
the conversation is handed back, the agent reads that reply as something the contact was
told by a person, so it doesn't take it back or apologise for it as its own. The history the
SDK receives marks those messages the same way, and `conversation_search` returns them with
role `team`.

Each action names something your organization already has, never a URL in the request.
`webhook.invoke` names one of your saved endpoints. `capability.tool` names an installed
capability and one of its tools, so a button runs the same operation the agent runs, pressed
by a person instead. Where two publishers use the same slug, write `capability` as
`"publisher/slug"`. An action is delivered at most once when someone presses it, and the
click is recorded. Add `"repeatable": true` for a button you want pressed more than once.

To collect something before the call, send `form` as a JSON Schema object of flat values
(`string`, `number`, `integer`, `boolean`, or an `enum`). The operator is then asked for it in
a Slack modal. A `capability.tool` action needs no `form`, because the tool's own input
schema is the form, minus whatever `arguments` already answers.

An agent key hands the work over as that agent. An org-wide key can name one with `agentId`.
Send `Idempotency-Key`, and a retry returns the same thread with `200` instead of announcing
it again.

### API key management

```bash
# Create a key. The full key is returned once.
curl -X POST -H "Authorization: Bearer $ADMIN_KEY" -H "X-Org-Id: my-org" \
  -H "Content-Type: application/json" \
  -d '{"name": "Production Agent", "scopes": ["*"]}' \
  https://<your-host>/api/v1/keys

# List the keys for your organization
curl -H "Authorization: Bearer $ADMIN_KEY" -H "X-Org-Id: my-org" \
  https://<your-host>/api/v1/keys

# Rotate a key. The key id stays, the old secret stops working at once.
curl -X POST -H "Authorization: Bearer $ADMIN_KEY" -H "X-Org-Id: my-org" \
  https://<your-host>/api/v1/keys/<key-id>/rotate

# Revoke a key now
curl -X POST -H "Authorization: Bearer $ADMIN_KEY" -H "X-Org-Id: my-org" \
  https://<your-host>/api/v1/keys/<key-id>/revoke
```

Keys are `sk_live_<random>` for production and `sk_test_<random>` for sandbox. Only a hash is
stored, so the full key is shown once, when you create it.
A key manages only its own organization: another organization's key id or org id answers `404`.
An org-wide key needs `keys:manage` to manage keys. It may create or rotate only keys
whose scopes it already holds; omitting `scopes` requests `*`, so a restricted key
must specify its delegated scopes explicitly. The platform admin key can issue `*`.

The org-wide skill library is available through `POST /api/v1/developer/skills`,
`GET /api/v1/developer/skills`, and `GET`, `PATCH`, or `DELETE` on
`/api/v1/developer/skills/:id`. Use `skills:read` for reads or `skills:write` for
management. Agent-bound keys cannot access the library. See
[skill library and deployment attachments](/docs/partner-deployments.md#skill-library)
for request bodies and the deployment `skills` field.

Developer API resource permissions use `<resource>:read` for GET and
`<resource>:write` for mutations; write also allows reads. Resources are
`config`, `agents` (including versions and storage), `tools`, `lines` (phone
and line provisioning routes), `secrets`, `alerts`, `usage`, `people`, `outcomes`, and
`handoffs`. `/sync` always requires `agents:write`, `tools:write`, `config:write`,
and `alerts:write`, because it updates configuration and reconciles alerts even
when omitted. Supplying secrets or capabilities (including an empty replacement
list) also requires `secrets:write` or `capabilities:write`, respectively.
Audit, deployments, and trace exporters retain their dedicated scopes. Default
`*` keys continue to access these routes. An org key cannot edit organization
metadata; platform administration owns SSO eligibility.
Restoring an agent version also requires write scopes for the config, tools,
alerts, capabilities, lines, skills, scripts, and MCP definitions it can change.

### Traces and logs

Every turn is recorded as a trace with nested spans. Keiki keeps them for 14 days by default.

```bash
# List recent traces
curl -H "Authorization: Bearer $API_KEY" "https://<your-host>/api/v1/traces?limit=20"

# Get one trace with all of its spans
curl -H "Authorization: Bearer $API_KEY" \
  https://<your-host>/api/v1/traces/<trace-id>
```

Each trace carries the model, tokens in and out, steps and duration, plus a span for every
model call, tool execution and memory retrieval, with inputs, outputs, errors and metadata.
A failed turn on the dashboard Logs page can be retried, replaying its original messages through
the same conversation or re-running its loop. Retry is refused once the conversation has moved
on or another turn is in progress. Retry is also available on failed messages in Conversations.

The Logs page has two tabs. **Activity** lists the turns above. **Approvals** lists the actions
agents asked to take: the ones waiting for a decision, which owners and admins approve or decline,
then the recent ones with how they went. The sidebar's Logs badge counts the actions waiting.

## What Keiki runs for you

You supply the config. Keiki runs the rest:

| Service | What it does |
| --- | --- |
| Memory | Per-user facts, recall and categorisation |
| Browser | Cloud browser tasks, saved logins, screenshots and signed handoff links for login/CAPTCHA walls; completion automatically resumes the agent |
| Scrape | Pages to Markdown or HTML, site crawling, and brand assets by domain |
| Sandbox | Persistent code execution per user |
| Media | Transcribe audio, describe images, extract documents |
| Learning | Quiet fact extraction after each turn |
| Steering | Gather rapid messages, and interrupt mid-turn |
| Escalation | Queue the conversation in the dashboard Handoffs queue; configured webhook, Slack or email routes add notifications |
| Transport | Outbound delivery and delivery receipts |
| Tracing | Per-turn traces with spans, kept for 14 days |
| API keys | Create, rotate and revoke scoped keys |

## Versions and restore

Every agent has a version history. Each time its config is written, through the dashboard or
through a `kit.sync()` from your SDK, Keiki records an immutable snapshot of the whole
config. Secret values are never versioned, only the fact that they are present.

Open an agent and go to **Versions** to see its history and restore an earlier version.
Restoring applies that config and records a new version, so history only moves forward. The
same history is available under `/api/v1/developer/agents/:agentId/versions`.

An SDK-managed agent can also be restored, but the SDK owns its live config and overwrites it
on the next `kit.sync()`.

### Staged rollouts

A config change can go out to a share of conversations before it goes out to all of them.
Only the fields a turn reads from its version can be staged: `model`, `system_prompt`,
`max_steps`, `history_limit`, `reasoning_effort` and `features`. A change to anything else
(tools, skills, MCP, capabilities, lines, webhooks) ships Full.

| Mode | What happens |
|---|---|
| `full` (default) | The change is written live for every conversation and channel. A Full change to a staged field ends any open rollout; other edits leave it running. |
| `manual` | The live config is unchanged. The change runs for `percent` (1-99) of conversations until it is promoted or rolled back. |
| `auto` | Like `manual`, starting at `percent` (default 1) and stepping up a `ladder` (default `1, 2, 5, 10, 25, 50, 100`) while quality holds. See below. |

```bash
curl -X PATCH -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "<agent-id>", "system_prompt": "...", "rollout": {"mode": "manual", "percent": 10}}' \
  https://<your-host>/api/v1/developer/config
# => { "status": "staged", "agent_id": "...", "rollout": { "id": "rol_...", "percent": 10, ... } }
```

Each conversation lands in a fixed bucket per rollout, so it keeps the same version for the
whole rollout, and raising the percent only adds conversations. Playground conversations
always run the staged version. An agent has at most one open rollout; a new staged save
replaces it. Every turn's trace records which side of the rollout it ran (`metadata.rollout`).

**Promote** writes the staged change live and records a new version. **Roll back** ends the
rollout and sends every conversation back to the live version; the config is not written.
Either takes effect within a minute. `kit.sync()` and restoring a version are always Full.

#### Auto

Every 5 minutes, each Auto rollout's two sides are compared over the current step, using the
quality reviews of their turns (playground turns are not reviewed, so they never count):

- **Broken turns** (a trace error, no reply, an empty reply, every tool failing, a model stall)
  or **rejected replies**: when the staged version's rate is at least 5 points above live and
  that gap is statistically clear (at least 3 such turns and 20 reviewed live turns, one-sided
  z ≥ 2.33), it is rolled back at once, whatever the step.
- **Judge score** (0-1): once both sides have 20 judged turns in the step, a clear drop of 0.05
  or more rolls back. A smaller or noisier dip holds the step until there is more evidence.
- **Next step**: after at least 30 minutes, with 20 judged turns on each side and the score
  clearly within 0.05 of live (one-sided 95% bound), the rollout moves to the next rung. When the next rung is 100%, it is promoted.
- **Stall**: a step with no verdict for 7 days is paused. It keeps routing at its share;
  setting a share resumes stepping from there.

A rollback only ends the rollout, so the live config is never written to undo it. Each rollback
or pause emails the org's owners and admins and the Keiki team, with both sides' numbers (a
failed send is retried every pass until it goes out), and the agent page shows it for a week. Auto needs quality review on (`QUALITY_REVIEW`, on by
default); `AUTO_ROLLOUTS=0` holds every Auto rollout at its current step.

In the dashboard, open the agent's **⋯** menu, choose **Stage changes** and turn on **Stage new
edits**. Edits to the instructions, model and features then wait in a draft (kept in that browser)
while every other edit keeps saving live, and a **Staging on** chip in the header reopens the
dialog. **Roll out…** there sends the draft Full, Manual or Auto. The **Versions** tab shows the
open rollout with its share, which you can change while it is Manual or paused, plus Promote and Roll back
and the last few finished rollouts.
