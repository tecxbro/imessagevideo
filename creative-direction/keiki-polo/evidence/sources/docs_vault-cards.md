---
title: Vault approval cards
description: Describe what a Face ID approval shows in Keiki Vault with policy.card templates or a card from your preview tool.
---

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

A [Face ID approval](/docs/keiki-vault.md#face-id-approvals) shows the tool name and plain
preview lines by default. A vendor card replaces those lines with your own layout: an email
preview, a refund summary, a receipt. You describe it as JSON; Keiki Vault draws it natively.

Vendor cards only render in Keiki Vault. Slack, the dashboard and approvals asked in words
keep the plain lines.

## Two ways to provide a card

| Source | When to use it |
| --- | --- |
| `policy.card` | A static template filled from the call's arguments. |
| `card` in the result of `policy.previewTool` | Your server builds the finished card, with data the arguments don't carry (balances, names, images). |

A valid preview `card` wins over the template. A preview with no `card`, or one Keiki cannot
parse, falls back to the template; a template that cannot render falls back to plain lines.
A preview field named `card` that is not card-shaped (no `v` plus a `blocks` array) stays
ordinary preview data.

### Templates and `$.` paths

A string value that starts with `$.` is a path into the call's arguments: `$.subject` reads
`args.subject`, `$.input.to` reads `args.input.to`, `$.items.0.name` reads the first item. The
whole string must be the path; `"To $.to"` is literal text.

| Argument value | Shown as |
| --- | --- |
| string | as is |
| number, boolean | `String(value)` |
| array | items joined with `, ` (empty items skipped) |
| `{ "email": "...", "name": "..." }` | `Name <email>` (or the email alone) |
| other object | its JSON |
| missing, `null`, empty | the line is dropped |

Paths work in block text, field values, email parts, image `url` / `alt`, and
`theme.logoUrl` / `logoDarkUrl`. Field labels, `accent`, `approveLabel` and `declineLabel` are
literal. A preview `card` is finished: `$.` strings in it are not filled.

### Snapshot at proposal

Keiki renders the card when the model proposes the call and stores it on the action. Later
edits to `policy.card`, or a changed preview, do not change a card already sent. A
`freshnessFields` change supersedes the action, and the replacement gets a fresh card.

## Schema

```ts
type VaultCard = {
  v: 1
  blocks: VaultCardBlock[]
  theme?: {
    accent?: string // #RRGGBB, tints the Approve button
    logoUrl?: string // https, 40×40
    logoDarkUrl?: string // https, used in dark mode; falls back to logoUrl
    approveLabel?: string // default "Approve"
    declineLabel?: string // default "Decline"
  }
}

type VaultCardBlock =
  | { kind: 'header'; title: string; subtitle?: string }
  | { kind: 'fields'; fields: Array<{ label: string; value: string }> }
  | { kind: 'text'; text: string }
  | { kind: 'email'; from?: string; to?: string; cc?: string; subject?: string; body?: string }
  | { kind: 'image'; url: string; alt?: string }
  | { kind: 'note'; text: string }
  | { kind: 'divider' }
```

| Block | Renders as | Notes |
| --- | --- | --- |
| `header` | Logo, bold title, secondary subtitle. | `title` is required; if it resolves empty the card is invalid. |
| `fields` | Label/value rows. | A field with no value is dropped. |
| `text` | Body text with inline Markdown. | |
| `email` | `From`, `To`, `Cc` rows, bold subject, body. | Needs at least one part with a value. |
| `image` | Image up to 220 pt tall; `alt` if it can't load. | A `url` that resolves empty drops the block. |
| `note` | Orange text with a warning icon, inline Markdown. | Use for caveats ("This can't be undone"). |
| `divider` | A rule. | A card with only dividers is empty. |

### Limits

| Limit | Value | Over the limit |
| --- | --- | --- |
| Blocks | 1–20 | Invalid |
| Fields per `fields` block | 20 | Invalid |
| `header`, field labels, `alt` | 200 characters | Truncated with `…` |
| `text`, `note`, field values, email `body` | 8,000 characters | Truncated with `…` |
| Email `from` / `to` / `cc` / `subject` | 1,000 characters | Truncated with `…` |
| `approveLabel`, `declineLabel` | 1–24 characters | Invalid |
| `accent` | `#RRGGBB` | Invalid |
| Image and logo URLs | `https:` only | Invalid |

### Validation and fallback

- Saving a tool validates `policy.card`; an invalid template is a 400 such as
  `policy.card.blocks must be 1-20 blocks`.
- A preview `card`, or a template that fails at proposal (a required value resolves empty, a
  resolved image URL is not `https:`), shows the plain lines instead.
- Unknown block kinds are skipped, by the server and by the app, so a newer block degrades on
  an older app.
- A card with no block that has a value falls back to plain lines.

## What vendors cannot change

Keiki draws the parts that make an approval safe:

- Exactly two buttons, Decline and Approve, both behind Face ID and signed by the phone's
  enrolled key. You can rename them; you cannot add, remove or restyle them beyond `accent`.
- A `Runs <toolName>` footer under your card, with the real tool name.
- What runs: the stored call, not anything in the card. The card describes the call; the
  call's arguments are what execute.

## Examples

### Email send

A `send_email` tool whose arguments are
`{ "connectionId": "...", "input": { "to": [{ "name": "Axel", "email": "axel@0.email" }], "cc": [], "subject": "Hello", "message": "Hi Axel" } }`:

```json
{
  "approval": "ask",
  "approvalProof": "verified",
  "card": {
    "v": 1,
    "blocks": [
      { "kind": "header", "title": "Send email", "subtitle": "$.input.subject" },
      {
        "kind": "email",
        "to": "$.input.to",
        "cc": "$.input.cc",
        "subject": "$.input.subject",
        "body": "$.input.message"
      }
    ],
    "theme": {
      "accent": "#1F3A93",
      "logoUrl": "https://mail.example/logo.png",
      "logoDarkUrl": "https://mail.example/logo-dark.png",
      "approveLabel": "Send",
      "declineLabel": "Don't send"
    }
  }
}
```

The card the contact sees (empty `cc` is dropped):

```json
{
  "v": 1,
  "blocks": [
    { "kind": "header", "title": "Send email", "subtitle": "Hello" },
    { "kind": "email", "to": "Axel <axel@0.email>", "subject": "Hello", "body": "Hi Axel" }
  ],
  "theme": {
    "accent": "#1F3A93",
    "logoUrl": "https://mail.example/logo.png",
    "logoDarkUrl": "https://mail.example/logo-dark.png",
    "approveLabel": "Send",
    "declineLabel": "Don't send"
  }
}
```

### Refund from a preview tool

The arguments only carry `{ "chargeId": "ch_3Px", "amount": 4800 }`, so the card comes from
the preview tool, which can look the charge up:

```json
{
  "approval": "ask",
  "previewTool": "preview_refund",
  "freshnessFields": ["amount"]
}
```

The model calls `preview_refund` with the same arguments first ([Governed actions](/docs/actions.md#live-approvals)). It returns its preview data with a `card`:

```json
{
  "amount": "$48.00",
  "customer": "Ana Ruiz",
  "card": {
    "v": 1,
    "blocks": [
      { "kind": "header", "title": "Refund $48.00", "subtitle": "Ana Ruiz · ana@example.com" },
      {
        "kind": "fields",
        "fields": [
          { "label": "Charge", "value": "ch_3Px · Oct 21" },
          { "label": "Card", "value": "Visa •••• 4242" },
          { "label": "Original", "value": "$96.00" },
          { "label": "Refund", "value": "$48.00 (partial)" }
        ]
      },
      { "kind": "image", "url": "https://shop.example/receipts/ch_3Px.png", "alt": "Receipt for order 1042" },
      { "kind": "divider" },
      { "kind": "note", "text": "Refunds take 5–10 days to reach the card and **can't be undone**." }
    ],
    "theme": {
      "accent": "#635BFF",
      "logoUrl": "https://shop.example/logo.png",
      "approveLabel": "Refund $48",
      "declineLabel": "Keep charge"
    }
  }
}
```

Set either policy with `POST` or `PATCH /api/v1/developer/tools`; see
[Set it up through the API](/docs/keiki-vault.md#set-it-up-through-the-api).
