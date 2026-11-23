---
title: Governed actions
description: Approve and audit ask-gated developer tool calls.
---

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

Some tool calls are safe to run the moment the model asks for them. Others change a plan,
charge a card, delete a record, or email a customer, and someone should see exactly what is
about to happen and say yes first. Governed actions are how Keiki handles the second kind,
for every tool the agent has, on every channel, without you building approval UI.

A governed action is a durable record, not a prompt convention. It is created when the model
proposes an ask-gated dispatcher tool, shown as a card in Slack or a conversational question,
decided by a person, executed by the platform *from the stored record*, and closed with an
outcome the agent and webapp can see.

> Governed actions are rolling out in phases. This page marks what is **live** and what is
> **future**; unsupported policy fields are rejected.

## Tool policy

A tool opts in by declaring a `policy` beside its schema.

### Live: `requiredScopes`

```json
{ "requiredScopes": ["billing:write"] }
```

Scopes the caller must hold, as the [identity webhook](/docs/identity.md) reported them. The
dispatcher checks them before the tool's implementation runs, on every channel; a caller
without them gets a refusal the model is told to relay. Accepted on:

| Tool source | Policy comes from |
| --- | --- |
| SDK `defineTool` | A `policy` property beside `execute`; the SDK ships it on `kit.sync()`. |
| Custom tool (`POST /developer/tools`) | A `policy` field in the upload body. |
| Deployment tool (`POST /developer/deployments`) | A `policy` field on the matching entry in `tools[]`. |

Unknown policy keys are rejected, so a typo cannot silently leave a tool ungoverned.
MCP tools use the same persisted action lifecycle. A turn that has no verified speaker at all —
no identity webhook on the agent, or a harness that does not carry the sender — refuses every
tool with `requiredScopes`, so declaring them is safe before the webhook is configured.

### Live: approvals

```json
{
  "approval": "ask",
  "requiredScopes": ["billing:write"]
}
```

| Field | |
| --- | --- |
| `approval` | `allow` (default): runs immediately. `ask`: a person decides first. Other values are rejected. |
| `requiredScopes` | As above; any approver must hold them too. |
| `previewTool` | Names a tool in the same tool set that must run first with the same canonical arguments. The preview tool must be called with the write's arguments minus `descriptionArg`. |
| `freshnessFields` | Dot paths in the preview output to compare again at approval time. Requires `previewTool`. |
| `descriptionArg` | Argument containing a model-authored walkthrough; it is shown on the card but excluded from the argument hash. |
| `approvalProof` | `any` (default): any approval surface decides, including the contact's reply in words. `verified`: only a decision tied to a verified person approves — a Face ID-signed Keiki Vault card, a Slack button, or the dashboard. A reply in words can still decline. Requires `approval: "ask"`. |
| `approvalFallback` | What happens when no way to ask is available on the channel (for `verified`, no card or button can be shown). `refuse` (default): the tool does not run. `tool`: the tool runs without `context.approval`, so its own approval flow applies. Requires `approval: "ask"`. |
| `preflight` | Webhook tools only. Before asking, Keiki sends the call once with `context.preflight: true`; the tool validates it without running it. A non-2xx answer goes back to the model as `preflight_rejected` and nobody is asked. Only set it when your server handles `context.preflight`, or the check runs the call for real. Requires `approval: "ask"`. |
| `card` | Keiki Vault approval card, drawn natively in the iMessage card. See [Vault approval cards](/docs/vault-cards.md). |

### Vendor cards

`policy.card` is `{ v: 1, blocks, theme? }`. Strings that start with `$.` are filled from the call's arguments (`$.input.subject`); a path with no value drops that line. A tool with a `previewTool` can instead return a finished card as `card` in its preview result, which wins over the template. The card always has exactly two Face ID buttons and a Keiki-drawn `Runs <toolName>` footer; an invalid card falls back to the plain argument lines. Schema, limits and examples: [Vault approval cards](/docs/vault-cards.md).

When an approved action runs, a webhook tool's `context.approval` carries
`{ actionId, decidedVia, decidedBy }`. `decidedVia` is `keiki_vault`, `slack`, `dashboard`,
or `chat` (a reply in words). The body is signed when the agent has an identity webhook,
so the tool can trust it. A call without `context.approval` was not approved by Keiki.
A decision made outside the conversation (Keiki Vault, the dashboard) runs the tool as the
conversation's contact, with the same channel details and identity lookup as the turn that
proposed it.

Preview pairing, freshness checks, material-field diffs, and walkthroughs are live. MCP tools
do not add those fields during replay.

## Lifecycle

```
pending → executing → completed
                  ↘ failed
        ↘ declined
        ↘ superseded
```

| Status | Meaning |
| --- | --- |
| `pending` | A card or text question is outstanding. Nothing has run. |
| `executing` | Approval was claimed and the stored call is running under a renewable 60-second liveness lease. It is not yet settled and must not be treated as success. A recovery sweep settles interrupted executions as `failed` with an unknown-outcome error; it never re-executes them. |
| `completed` | The stored call finished successfully. |
| `failed` | The tool errored, or its process stopped during execution and the outcome is unknown. The error is on the record; nothing is retried without a new decision. For an unknown outcome, check whether it took effect before proposing it again. |
| `declined` | Someone said no. |
| `superseded` | A newer proposal replaced this one, or its preview changed before approval. Nothing ran from this record. |

The record keeps the tool name, exact arguments, who proposed it, who decided it, and what
happened, so webapp readers can answer who approved it and what it did.

## No drift

The card a person approves and the call Keiki makes are the same thing, twice over.

**The arguments are the arguments.** When the model calls a gated tool, its arguments are
canonicalised (keys sorted and `undefined` values dropped), stored on the record and hashed. Approval
executes *that* stored call. The model does not get another turn between "yes" and the
tool running, so there is nothing to rephrase, and a later prompt change cannot alter what
an already-approved action does.

If `previewTool` is configured, the dispatcher requires a matching preview from the
same agent and conversation within 24 hours. The hash sorts keys recursively and excludes
only `descriptionArg`; the original arguments, including that description, remain stored.
At approval time, configured `freshnessFields` are re-read from a fresh preview. If any
field differs, the action is marked `superseded`, a new pending action is created with the
fresh preview, and the approver is asked to review again. A preview refresh failure fails
closed and records `Could not refresh preview: ...`. Re-proposing a pending action also
supersedes the older proposal.

## Groups

Actions proposed in one turn share a group id. When at least two are pending, the agent
sees a group summary and Slack shows **Approve all** and **Decline all**. Approve-all runs
actions in creation order and stops at the first failed or superseded action; later actions
remain pending. Decline-all settles every pending action in the group. The web route
`POST /api/webapp/agents/:id/actions/groups/:groupId/decide` accepts
`{"decision":"approve"}` or `{"decision":"decline"}` and returns per-action results.

## Deep links and webhooks

Deployments may configure action settings:

```json
{
  "actions": {
    "view_url": "https://dashboard.example/actions/{actionId}",
    "webhook_url": "https://api.example/keiki/actions",
    "secret": "at-least-16-characters"
  }
}
```

At least one of `view_url` or `webhook_url` is required. A view URL must contain
`{actionId}` or `{groupId}` and may also use `{conversationId}` and `{toolName}`.
Each placeholder is substituted with a URL-encoded value. The webhook receives
`action.<status>` events with `agent_id`, `external_ref`, and the public action record
(never its API key). Requests use `X-Keiki-Timestamp` and
`X-Keiki-Signature` headers, signed as described in the
[identity signing section](/docs/identity.md#signing-requests). Webhook delivery uses a
five-second timeout, no retries, and never blocks action execution.

## Where actions show up

**Slack.** A card in the thread with the summary and buttons.
Buttons check the presser's [scopes](/docs/identity.md#how-permissions-are-enforced); a second
press on a decided card is a no-op, and a press by two people at once yields one execution.
After the decision the card updates in place with the outcome. Actions expire after 24 hours.

**iMessage (Keiki Vault).** On a dedicated iMessage line, a direct conversation gets an
approval card instead of a question. It opens in Keiki Vault with the summary, the
action's preview, and **Approve** and **Decline**. Both need Face ID: it unlocks a P-256
key held in the phone's Secure Enclave, which signs the action id, the decision, the card,
and the time.
Keiki verifies that signature before the action runs. The first signed decision (approve or
decline) from a contact enrolls their key for that API key; after that, only that key
decides, so a forwarded card cannot approve or decline from another phone. A signature from a different key (a
new phone, or a Face ID change, which voids the old key) is held back: the card shows a
six-digit code, and only once the contact sends it from their own number in the chat, within
10 minutes, does the new key replace the old one. If the details change before
the answer arrives, the same card reloads with the new ones. Each decision is logged as an `approval.decided` Vault event with the outcome and the key that signed.
If an approved action fails, on any surface outside the turn (Keiki Vault, Slack, dashboard), the agent gets a turn with the error, so it can tell the contact and fix the call.
If the card can't be sent, the agent asks in words instead, unless the tool sets `approvalProof: "verified"`; then `approvalFallback` decides.

**Words.** "yes", "go ahead", "no, leave it" in the thread can decide the action: the agent
calls `action_respond` with the action id or group id, decision, and exact words. It never
approves on someone's behalf.

**Webapp.** `GET /api/webapp/agents/:id/actions?status=&limit=` lists actions and
`POST /api/webapp/agents/:id/actions/:actionId/decide` lets an owner or admin decide;
`POST /api/webapp/agents/:id/actions/groups/:groupId/decide` decides every pending action
in a group.
A dashboard Actions UI is future work.

## What the agent knows

Every turn starts with an **Action state** section listing the conversation's open and
recently closed actions — status, summary, who decided, the result or error — so the agent
can answer "did that go through?" without a tool call and does not propose the same change
twice while one is pending. The section is written by the platform from the records.

The agent's instructions for gated tools are also the platform's: propose, then stop and
wait — no "I've applied it" until the record says `completed`.

## Approval window and stopping

A pending action waits for a decision independently of the turn that proposed it. The turn
ends; the agent replies that it is waiting; the record stays `pending` until it is decided
or expires. If an approved call's process crashes, a sweep runs at startup and every minute
to settle executions older than 60 seconds without a live lease. Interruptions decided within
the last 15 minutes wake the originating agent. Every settled interruption emits an event
and refreshes the approval card, including older interruptions. Callers must treat `executing` as not-yet-settled,
never as success. A [stop command](/docs/slack-agents.md#stopping-the-agent) aborts a running turn and
leaves pending actions where they are — stopping is never an approval or a decline.

## MCP Actions

MCP `ask` tools use persisted agent actions. The MCP path is stored as the Action
`toolName`, exact arguments are retained and replayed on the daemon after approval, and
URL or structured-form elicitations remain daemon-owned through `mcp_resume`.
MCP Actions currently do not add `requiredScopes`, `previewTool`, or `freshnessFields`;
those fields are not fabricated during MCP replay. Personal-scope approvals must be made
by the requester, because the action replays against that person's own MCP connection.
The current MCP permission is checked again at approval time; if the preset is disconnected
or the tool is denied, the action fails without calling the daemon.
