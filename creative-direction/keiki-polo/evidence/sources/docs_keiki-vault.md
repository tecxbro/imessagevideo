---
title: Keiki Vault
description: How agents open web cards and ask for Face ID approvals inside Messages with the Keiki Vault iOS app.
---

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

Keiki Vault is Keiki's own iMessage app (App Store bundle `com.keiki.vault`, Messages
extension `com.keiki.vault.messages`). Every agent on Keiki uses the same app: there is no
per-agent build, and a card opens inside Messages without opening the full app.

It does two things for an agent:

| Card | What it shows | Who sends it |
| --- | --- | --- |
| [Presentation card](#presentation-cards) | Your HTTPS page in a web view. | A tool that returns `presentation {type: "app"}`. |
| [Approval card](#face-id-approvals) | A native card with **Approve** and **Decline**, both behind Face ID. | Keiki, for a tool with `policy.approval: "ask"`. |

The recipient installs Keiki Vault once from the App Store. Keiki picks the line, recipient
and credentials; a tool never passes them.

## Native notifications and task activities

The platform includes a recipient-scoped native notification contract without rollout
flags. Delivery requires a compatible Vault build, platform APNs credentials and device permissions.
This is separate from Messages cards; existing App Store cards do not gain native
push simply because the backend is updated.

For a device already trusted for that recipient's Face ID approvals, open the Keiki
Vault iMessage app and tap **Enable agent updates**. The drawer opens the containing
Vault app, which proves possession of the existing approval key before showing a
named agent consent when opened from a card. The server resolves the card's token
to its originating tenant, agent and recipient, then narrows discovery in SQL.
The signed discovery proof binds that origin token; an expired or untrusted origin
cannot fall back to another agent. Standalone Vault entry retains the trusted-agent picker.
Review the consent, then connect with Face ID.
No agent-sent link or copied code is needed. Anonymous Messages participant IDs are
never used as phone numbers or recipient proof. Only active keys with an existing
inbound conversation under their tenant and recipient can appear in the picker.

Discovery and selected-agent consent use separate one-use challenges with a shared
five-minute expiry. Both are installation- and key-bound; selected-agent consent
also binds the server-derived tenant, agent, recipient and alert/activity scope.
Discovery only lists choices; it grants no consent. Key revocation, ownership and
expiry are checked again when connecting. A bad signature preserves the installation;
revoked credentials show reconnect guidance. New discovery replaces old choices.

If this iPhone has no approval key yet, Vault explains that the recipient should
approve a Keiki card in Messages first, then enable agent updates from that card.
An invalidated Secure Enclave key instead shows Face ID recovery guidance: approve
a card in Messages to set up a new key. Both offer **Open Messages**. Discovery and
connection consent never create or replace the key themselves.

The agent calls `vault_connect` without arguments. If the recipient already gets
this agent's updates on an authorized installation it returns `connected` and sends
nothing. On a direct iMessage chat it sends a Face ID approval card instead of a link
("Updates from <agent>"): approving it establishes or matches the approval key, and the
card opens Vault straight to that agent's named consent. Other channels get a connection
link; the recipient opens Vault, reviews the named agent and taps **Connect with Face ID**. The existing key
signs a single-use, ten-minute challenge bound to the installation, tenant, agent,
recipient and alert/activity consent. The server only matches an active enrolled key;
this flow cannot enroll or replace an approval key. Face ID alone is not recipient identity.

New or untrusted devices establish or recover their approval key in Messages.
After the first approval or key recovery, Vault opens directly to the originating
agent's consent. Settled approval cards also offer **Enable agent updates**.
There is no manual connection-code flow; `vault_connect` takes only `reconnect`.
When the recipient asks to reset or reconnect (for example on a new iPhone with the same
number, where the old install still counts as connected), the agent calls it with
`reconnect: true`: it sends the card even when connected, and Vault's consent then
subscribes the new install. Existing subscriptions stay until the recipient taps
**Disconnect agent** in Vault; the agent cannot disconnect anyone. Every reply is also
checked for platform token links (Vault connect, invites, connect links) that no tool
returned in that turn; such a reply is rejected and the model retries.
Each agent has independent alert/activity consent. A forwarded link cannot enroll a phone
without the recipient's trusted key, and notification consent never approves actions or payments.
Apple's notification permission is separate: denied permission leaves consent connected
but notifications disabled, with a Settings recovery path. Live Activities can also be disabled.

Managed agents use `vault_connect`, `notify`, `activity_start`,
`activity_update`, `activity_end`, `activity_status`, and `notification_status`. These tools derive the
recipient from the current conversation and never accept APNs tokens or a sender identity.

Developers use the cloud client (`@onkeiki/agents/cloud`):

```ts
import { createCloudClient } from '@onkeiki/agents/cloud'

const cloud = createCloudClient({ apiKey: process.env.KEIKI_API_KEY! })
const task = {
  agentId: 'your-agent-id',
  recipient: '+15555550123', // lookup of this agent's already-enrolled conversation
  id: 'flight-check',
  revision: 1,
  title: 'Checking your flight',
  body: 'Waiting for the airline.',
  phase: 'working' as const,
  expiresAt: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
}
await cloud.vault.activity.start(task)
await cloud.vault.activity.update({ ...task, revision: 2, body: 'Check-in is ready.' })
await cloud.vault.activity.end({ ...task, revision: 3, phase: 'completed' })
await cloud.vault.notify({ ...task, id: 'check-in-ready', title: 'Check-in is ready' })
```

The matching API routes are `POST /api/v1/developer/agents/:agentId/notifications`
and `POST /api/v1/developer/agents/:agentId/activities/{start,update,end}` with
`{ recipient, content }`. They require the owned agent and `agents:write` scope.
Read outcomes with `GET /api/v1/developer/agents/:agentId/notifications/:id?recipient=...`
or `cloud.vault.status({ agentId, recipient, id })`; the `id` is the request UUID
returned by start/notify, not the caller's logical `id`. Agent-bound keys cannot
address another agent. `recipient` looks up a consent grant, never a provider token.

Before updating an existing task, call `activity_status({})`, or
`cloud.vault.activity.status({ agentId, recipient })` /
`GET /api/v1/developer/agents/:agentId/activities?recipient=...` (`agents:read`).
This returns up to 20 recent unexpired tasks in that conversation, including ended tasks,
with their logical `id`, transport `requestId`, revision and complete content. Reuse the
exact logical ID and original `expiresAt`; do not invent a new task ID or recalculate
eight hours from the update. Increment the recovered revision by one and preserve the
remaining snapshot fields. A missing update/end target returns `activity_not_found`,
an ended one `activity_ended`, and a stale revision `revision_conflict` with
`expectedRevision`; each activity rejection also carries the same `activities` list as
the status call, so retry from that snapshot rather than guessing. An identical accepted
snapshot is an idempotent replay, while different content is a new update. A
notification ID is single-use: reusing it with different content returns
`notification_id_used`, so send a new ID at revision 1.
Start/notify receipts include `logicalId` and `expiresAt`; request-UUID status also
returns `logicalId`, `content` and `ended`. Server state is not device visibility.

Use revision 1 for a discrete notification or new task; then increment by one for
each full activity snapshot. Identical replays are idempotent, changed revisions
conflict, and terminal tasks cannot restart. Task end phases are `completed`,
`failed`, and `cancelled`. Title/body limits are 120/500 characters; optional real
progress is 0–1. Expiry is capped at eight hours from task creation; a later `expiresAt`
is stored and returned as that cap. Avoid sensitive
Lock Screen text and never copy raw tool arguments, secrets, or reasoning into updates.

Results distinguish `queued`, `not_enrolled`, `permission_denied`, `suppressed`, and
`unsupported`; transport status reports `provider_accepted`, `expired`, `failed`,
or `unknown`. A suppressed/unavailable surface includes reconnect guidance rather
than silently switching to SMS. APNs acceptance is not proof of visibility or reading.
Live Activities need iOS 17.2+ for remote starts and represent one bounded task,
not an always-on agent indicator. Keiki Vault keeps one stable app icon; agent
names and initials supply task branding. Communication-avatar presentation is
not part of this baseline.

## Where it works

Cards, presentation and approval alike, are sent only from a dedicated Keiki iMessage line
(a dedicated iMessage line bought through Keiki), in a 1:1 chat with the contact. Imported,
shared and pool lines, group chats and other channels get no card:

| Card | On any other line or channel |
| --- | --- |
| Presentation | Nothing is sent. The tool result's `presentationDelivery` is `unavailable` with reason `line_not_eligible` (or `unsupported_channel` off iMessage or in a group); `send_widget` returns `line_not_eligible`. |
| Approval | The approval is asked in words, or refused for verified-only tools. See [When no card can be sent](#when-no-card-can-be-sent). |

Not every iMessage line type supports app cards; `send_widget` is only offered on
supported lines. Send a plain link with `reply` on other lines.

Presentation cards also need the **Dynamic UI** add-on (feature `dynamicUi`; the older
`imessageApps` key is an alias). See [iMessage Apps](/docs/imessage-apps.md#turn-it-on).
Approval cards do not need the add-on.

## Presentation cards

### Send one

Any non-builtin tool (webhook, code, capability, or MCP `structuredContent`) can return a
`presentation` beside its normal result:

```json
{
  "status": "ready",
  "url": "https://your-app.example/checkout/123",
  "presentation": {
    "type": "app",
    "id": "checkout-123",
    "url": "https://your-app.example/checkout/123",
    "caption": "Review your order",
    "subcaption": "2 items · $48.00"
  }
}
```

| Field | Rule |
| --- | --- |
| `id` | Required, 1–128 characters. The same tool, `id` and `url` in one conversation send once; a retry gets the first delivery back. Use a new `id` for a new card. |
| `url` | Required absolute `https:` URL, up to 2,048 characters, no `user:password@`. |
| `live` | Optional boolean, default `false`. |
| `caption` | Optional, 1–60 characters. The bubble shows `Open app` without one. |
| `subcaption` | Optional, 1–80 characters. The bubble shows `Tap to open` without one. |

Keiki adds `presentationDelivery` (`accepted`, `unavailable`, `failed` or `unknown`) to the
result the model reads. The full table, the `send_widget` builtin, and `choice` /
`confirm` presentations are in [iMessage Apps](/docs/imessage-apps.md#send-a-card). Keep the URL
in the result so the agent can send it as a link when the card is not accepted.

### How it renders

Tapping the bubble opens the card expanded and loads `url` in a web view.

- The card URL must be `https:` with a host and no credentials, or the card shows as invalid.
- Keiki appends `#kv=<token>` to the URL's fragment (other fragment parts are kept). The
  token names this one send for telemetry. A fragment never reaches your server; do not
  depend on `kv`.
- A main-frame HTTP status of 400 or more, or a failed load, shows the load error and is
  reported as `card.load_failed`.
- `live: true` draws the page in the transcript bubble itself. Taps reach the page, but a
  tap does not open the expanded card. The bubble doesn't scroll: vertical swipes scroll the
  conversation, so fit a live page in the bubble. Keiki Vault 1.2.1 and earlier ignore taps
  on live cards.

### Navigation inside the card

| Navigation | Result |
| --- | --- |
| `https:` link, same origin as the card (scheme, host and port; 443 by default) | Loads in the card. |
| `https:` link to another origin | Opens outside Messages. |
| `target="_blank"` / `window.open` to the same origin | Loads in the card. |
| `https:` iframe or subresource | Allowed. |
| `tel:`, `mailto:`, `sms:` | Opens the system app. |
| Anything else (`http:`, `javascript:`, custom schemes) | Blocked. |

Put the whole flow on one origin. A sign-in or payment step on another origin leaves the card.

### Updating a sent card

Keiki stores the card session for each accepted send in
`presentation_intents.card_session` and can rewrite that same bubble in place with
`updateApp`: no second message. Keiki uses this for approval cards when they settle
(see [below](#after-the-decision)). A tool cannot edit its own card; to show something new,
return a presentation with a new `id`.

### Telemetry

The extension posts events to `POST /api/v1/vault/events`, keyed only by the per-send token:

| Event | When |
| --- | --- |
| `card.opened` | The card was opened. |
| `card.dwell_ms` | Time spent on the card. |
| `card.load_failed` | The page failed to load. |
| `card.nav_bounced` | A navigation bounce. |
| `approval.tapped`, `approval.biometric`, `approval.signed`, `approval.failed` | Steps of an approval. |

Events carry no page content, URLs or recipient identity. Keiki logs `approval.decided` itself
when a decision lands.

## Face ID approvals

A tool with `policy.approval: "ask"` never runs on the model's say-so. In a direct iMessage
conversation on an eligible line, Keiki sends an approval card instead of asking in words.
Approval policy fields are in [Governed actions](/docs/actions.md#live-approvals).

### What the recipient sees

The bubble reads **Approval needed** with the tool's name under it. Tapping it opens a
compact native card above the keyboard, so the chat stays visible:

- your [vendor card](/docs/vault-cards.md) if the tool has one, otherwise the tool name and the
  preview or argument lines;
- a `Runs <toolName>` footer that Keiki draws;
- exactly two buttons, **Decline** and **Approve**. Both run Face ID.

Decline is signed too, so a forwarded card cannot cancel the contact's action from another
phone.

### What happens on a tap

1. The extension reads the card: `POST /api/v1/vault/approval` with `{ "token": "<kv token>" }`
   returns `actionId`, `status` (`pending` or `settled`), `summary`, `description`,
   `preview`, `toolName`, `card`, `expiresAt` and `enrolled`.
2. Face ID unlocks a P-256 key held in the phone's Secure Enclave (bound to the current Face ID
   enrollment). It signs:

   ```
   keiki-vault-approval-v1
   <actionId>
   <approve|decline>
   <sha256 hex of the card token>
   <signedAt, epoch ms>
   ```

3. The extension posts `POST /api/v1/vault/decide` with `token`, `decision`, `signedAt`,
   `publicKey` (base64 X9.63), `signature` (base64 DER ECDSA/SHA-256) and `keyStorage`.
4. Keiki checks the signature, the clock (within 5 minutes), the enrolled key, and the tool's
   `requiredScopes`, then decides the action. The stored call runs through the action
   lifecycle (`pending → executing → completed | failed`) with `context.approval.decidedVia`
   set to `keiki_vault`.

| `/decide` error | Status | Meaning |
| --- | --- | --- |
| `not_found` | 404 | Unknown or expired token. The card shows "This request has expired." |
| `not_pending` | 409 | The action is no longer pending. |
| `signature_required`, `bad_signature` | 401 | No valid signature. |
| `signature_expired` | 401 | `signedAt` is more than 5 minutes off the server clock. |
| `confirm_device_key` | 403 | Signed by a key other than the enrolled one. `confirmationMessage` carries the native device-confirmation payload; see [Key enrollment](#key-enrollment). |
| `requires_speaker_scopes` | 409 | The contact lacks the tool's `requiredScopes`. |

`GET /api/v1/vault/approval` (the card URL opened in a browser or on a Mac) only says to
open the approval in Keiki Vault on an iPhone. It cannot approve.

### Key enrollment

Keys are trust on first use, per API key and phone number. The first valid signed decision
from a contact enrolls their key for that API key; after that only that key can decide.
A different key (a new phone, or a key lost when Face ID was re-enrolled) is held back:
the card offers **Confirm this iPhone**. This sends a Keiki Vault bubble ("This iPhone
confirmed") through the active direct iMessage conversation, without displaying or copying
a code. The bubble's hidden URL carries a random 256-bit nonce only in the fragment; opening that
URL cannot confirm anything. Only an authenticated inbound message from the same
recipient, tenant and originating agent can spend it, within 10 minutes and 5
attempts. The new key replaces only the enrolled key it was issued against.
The webhook body omits an app card's URL, so the server re-reads the card from the iMessage line
before matching it. Builds before 1.2.4 (24) send the confirmation as text instead, and
iMessage may deliver that text and link as two messages: the link alone
spends the nonce, and the bare text is kept from the agent until that confirmation expires,
so it is swallowed even when it arrives after the link.
The contact then approves again and continues directly to that agent's Vault consent.

### When no card can be sent

The card is only sent on a dedicated Keiki iMessage line in a 1:1 chat. Elsewhere, or
when the send fails, the agent asks in words and the contact's reply decides through
`action_respond`. Two policy fields change that:

| Policy | Effect |
| --- | --- |
| `approvalProof: "verified"` | A reply in words cannot approve (it can still decline). With no card or button to show, `approvalFallback` decides. |
| `approvalFallback: "refuse"` (default) | The tool does not run; the model gets `approval_unavailable`. |
| `approvalFallback: "tool"` | The tool runs without `context.approval`, so its own approval flow applies, such as returning a link to approve in your web app. |

`approvalFallback: "tool"` is how to keep a browser approval link as the fallback: when the
call arrives without `context.approval`, return your link instead of acting.

### Preflight

A bad call should fail before the contact sees Face ID, not after. Webhook tools can set
`policy.preflight: true` (requires `approval: "ask"`; other tool types are rejected with 400).
Before the card is shown, Keiki calls the webhook once with `context.preflight: true`:

```json
{
  "input": { "to": "ana@example.com", "subject": "Invoice" },
  "context": { "phone": "+15551234567", "agentId": "…", "preflight": true }
}
```

Validate the input and return 2xx without acting. Any non-2xx answer goes back to the model
as `status: "preflight_rejected"` with the first 2,000 characters of your body, and nobody is
asked. Only enable it if your server handles `context.preflight`; otherwise the check runs the
call for real.

### After the decision

- The bubble is rewritten in place: **Approved**, **Declined** or **Didn't go through**.
- If `freshnessFields` changed since the proposal, the action is superseded and the same card
  reloads with the new details.
- If an approved action fails, the agent gets a turn with the error, so it can tell the
  contact and propose a fixed call. It never claims success.

## Siri: message a connected agent

After connecting agents in Vault, use **Message agent** in Shortcuts or say
“Message my agent in Keiki.” (The app appears as **Keiki** on the iPhone, so that is the name Siri hears.) Choose the agent and say what you want it to
do or know. Siri shows and speaks the agent's reply in a small native snippet.
The action requires device authentication. **Message agent** cannot approve
actions or payments; approve actions with **Approve agent action** (below) and
payments in Messages. Agent names are available through entity
queries on iOS 17 and indexed to Spotlight on iOS 18 and later.
The connected-agent query also supports enumeration, so Siri AI can retrieve
the current installation's agent list without relying on Spotlight search.

Siri AI tool discovery is available only in internal builds made with Apple's
preview SDK and `SIRI_AI_PREVIEW` enabled. Standard App Store builds retain the
same intent through Shortcuts and App Shortcuts without preview APIs. A working
result means the agent continues; do not resend it. Alerts require existing
notification consent. See the app README for internal-build setup.
For preview testing, keep Vault in the foreground or include “in Keiki”
in the request while the app is in the background. Try `Ask Keiki agent
<name> to say hello` first. To test phone access, enable that agent's Read calendar
toggle and ask `In Keiki, ask <name> what's on my calendar tomorrow`. Siri
showing Apple's Calendar is not evidence that the agent received the request.

## Siri: agent items

Notifications that connected agents send to Vault, and Live Activities that have
ended, are Siri and Spotlight items (`AgentItemEntity`) for as long as Vault
keeps them. Each item has a title, details and the agent's name. Ask “what did
Nod book?”; Siri finds the item by title, details or agent name. Share it (“send
that to Sarah”) as plain text, or run **Add agent item to Calendar** to add it as
an event with the details in the notes. Items are indexed to Spotlight on iOS 18
and later and re-indexed each time Vault refreshes its connected agents.

`GET /api/v1/vault/devices/items` uses the installation bearer credential and
returns `{ items: [{ id, title, body, agentName, sentAt }] }`, newest first, only
for agents subscribed on that installation. `q` (1–100 characters) matches
title, body or agent name case-insensitively; `ids` takes up to 50
comma-separated item ids; `limit` is 1–50 (default 20, or the number of `ids`).

`POST /api/v1/vault/devices/subscriptions/:id/messages` uses the installation's
bearer credential, not an agent API key. Send `{ "text": "What is next today?" }`
(1–2,000 characters). Only subscriptions owned by that installation are accepted.
The message runs on the recipient's existing conversation, with its history,
memory and normal tools. The answer is stored in that conversation but is not
sent over iMessage; Siri displays it instead.
Recipient turns restore the stored dispatch context for that agent and recipient,
so the identity webhook can resolve the original verified sender. Missing sender
identity and denied tool scopes remain denied; a phone-access grant does not
grant developer-tool scopes. Dashboard staff steering does not inherit this identity.

Within the wait budget the response is `200 { status: "replied", reply, traceId }`.
An identity refusal returns its guidance as `reply` without a `traceId`: the model
and tools never ran. The same guidance can become a delayed notification.
After the budget it is `202 { status: "working" }`; the turn continues and its
answer becomes a completed Vault notification, respecting existing alerts consent.
The notification uses the agent's name, up to 500 characters of the reply, and
expires after five minutes. This is a preview; long account-link URLs can be
truncated. Immediate identity replies preserve the full guidance.
`VAULT_SIRI_WAIT_MS` sets the server wait budget
(default 20,000 milliseconds, capped at 25,000 to leave five seconds before the
iOS client's 30-second timeout). Requests are limited to 20 per minute per installation.
Unknown or foreign subscriptions and blocked conversations return `404 not_found`
without running a turn, so a blocked contact cannot distinguish a block from an
unknown subscription. A live turn returns
`409 agent_busy`, a paused agent `409 agent_paused`, and exhausted credits
`402 out_of_credits`. Invalid bodies return `400 invalid_request`.
SDK agents hosted on their owner's server return `409 sdk_agent_unsupported`
without forwarding the message: their webhook protocol cannot guarantee a reply
only to Siri. Use their Messages conversation instead.

## Siri: approvals

Say “Approve Nod's order”, or run **Approve agent action**. Siri shows the same card
as Messages: the vendor's card (amount, payee, items) when the tool has one, otherwise
the action and its details, plus the tool it runs. Siri snippets can't load remote
images, so Vault downloads the card's images first; one that fails shows “couldn't
load”, as in Messages. Siri then asks you to confirm, then Face ID signs the same
approval Messages signs and sends it to `POST /api/v1/vault/decide`. Payment cards are
never offered to Siri; pay in Messages. Siri can only approve: decline in Messages.
The Face ID approval key must already exist on this iPhone (from an approval in
Messages); a new or replaced key is confirmed in Messages, as for any card.

`GET /api/v1/vault/devices/approvals` uses the installation bearer credential and
returns `{ approvals: [{ id, actionId, agentName, title, lines, description, toolName, card, expiresAt }] }`
(`card` is the same vendor card `POST /vault/approval` returns, or `null`):
up to 10 pending, unexpired `approval` cards for agents subscribed on that
installation, newest first. `q` (1–100 characters) matches the agent name, action
summary or tool name; `id` returns one card. `POST /api/v1/vault/devices/approvals/:id/token`
mints the card token Siri signs over (`{ token }`, or `404 not_found`). It is a
second token for the same card, so the Messages card keeps working; the signed
message, signature window, key matching and decision are those of Messages.

## Phone access: agents use the iPhone

Connected agents can ask the recipient's iPhone for six things. Each is off until
the recipient allows it for that agent under **Phone access** in Vault; reading
and adding are separate grants and can be revoked any time.

| Tool | Grant | Returns |
| --- | --- | --- |
| `device_calendar_events { from, to }` | `calendar_read` (Read calendar) | events in the range (at most 31 days) |
| `device_add_event { title, start, end, all_day?, location?, notes? }` | `calendar_write` (Add to calendar) | the added event |
| `device_add_reminder { title, due?, notes? }` | `reminders_write` (Add reminders) | the added reminder |
| `device_contact_lookup { name }` | `contacts_read` (Look up contacts) | up to 5 matches with phones and emails |
| `device_location {}` | `location_read` (Current location) | coordinates, accuracy and place name |
| `device_find_photos { from, to, limit? }` | `photos_read` (Find photos) | up to 5 photos as conversation `attachment_id`s for `send_file` |

Timestamps are ISO 8601 with a UTC offset. Adding events and reminders needs no
per-call tap once the grant is on; the agent says what it added. There is no
Photos write access and no health data.

The recipient and installation are derived from the turn, never from tool
arguments; group conversations get `direct_conversation_required`. Dashboard
steers, held-back and background turns get `held_back_turn` and never reach the
iPhone. Each call:

1. Without the grant the tool returns `needs_permission` and Vault sends “Nod
   wants to read your calendar. Tap to choose in Keiki Vault.” If they allow it,
   Vault first requests the matching iOS permission, saves the agent grant only if
   allowed, then runs the request and the result arrives as a new turn. Denial
   posts `ios_permission_denied` without saving access and shows a per-grant
   message with Open Settings. Phone access toggles use that same authorization
   path before saving; already-authorized access does not prompt. Turning a toggle
   off removes only that agent's grant, not iOS permission. Calendar additions
   request write-only access; reads need full access. Limited Contacts and Photos
   access is accepted. Enabling location requests When In Use; background execution
   still needs Always. Permissions are checked again on execution after revocation.
   Vault asks at most once every 10 minutes per agent and kind of request;
   repeat calls in that window return `needs_permission` without another alert.
2. With the grant the server sends a silent (`content-available`) push and waits
   up to `VAULT_DEVICE_WAIT_MS` (default 10,000, capped at 20,000 milliseconds).
   An answer in time is returned in the same turn as `{ state: "completed", result }`.
3. Otherwise the tool returns `pending` and Vault sends a normal notification
   (“Tap to share your calendar”), because iOS throttles silent pushes and cannot
   ask for its own permission in the background. The answer arrives later as a
   new turn through steering, so paused agents and blocked conversations are respected.

A phone answer requires that agent's grant to still be on, except for `declined`
and `failed` with `ios_permission_denied`, which carry no device data. All other
answers after revocation are rejected (`409 permission_required`). `declined` and
`failed` (`ios_permission_denied`, `not_found`, `unavailable`, `timeout`) outcomes
are reported to the agent. Requests expire after one hour. Location answers in the
background only with iOS “Always” location access; otherwise the tap path opens Vault.
A Vault that is not connected returns `not_connected`; one without a notification
token returns `unavailable`.

Device endpoints, using the installation bearer credential:
`PUT /api/v1/vault/devices/subscriptions/:id/grants { grants: [...] }` replaces
one agent's grants; `GET /device-requests/:id` returns a pending request for this
installation; `POST /device-requests/:id/answer` takes `{ state: "completed", result,
photos? }`, `{ state: "failed", error }` or `{ state: "declined" }` (up to 8 MB,
60 per minute). Photos are JPEGs (base64, up to 5) stored as conversation attachments.

## Set it up through the API

Create a webhook tool with an approval policy, preflight and a vendor card. An
organization-wide key also passes `agent_id`:

```bash
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "<agent-id>",
    "name": "send_email",
    "description": "Send an email for the user",
    "inputSchema": {
      "type": "object",
      "properties": {
        "to": {"type": "string"},
        "subject": {"type": "string"},
        "body": {"type": "string"}
      },
      "required": ["to", "subject", "body"]
    },
    "executionType": "webhook",
    "webhookUrl": "https://mail.example/keiki/send",
    "policy": {
      "approval": "ask",
      "approvalProof": "verified",
      "preflight": true,
      "card": {
        "v": 1,
        "blocks": [{"kind": "email", "to": "$.to", "subject": "$.subject", "body": "$.body"}],
        "theme": {"approveLabel": "Send", "declineLabel": "Don'\''t send"}
      }
    }
  }' \
  https://<your-host>/api/v1/developer/tools
```

Change it later with `PATCH /api/v1/developer/tools/:id` and a `policy` body. Send the whole
policy: it replaces the stored one. An invalid policy is a 400 naming the field, for example
`policy.card.theme.accent must be a #RRGGBB colour`. SDK tools set the same `policy` beside
`execute` in `defineTool`, and deployments set it per entry in `tools[]`.
