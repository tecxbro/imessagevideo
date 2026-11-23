---
name: photon-demo-creator
description: Route Photon demo discussions, local edits, conversation changes, full new-company builds, and publish/start/provision/rehearsal operations to proportionate workflows. Use for Photon Spectrum demo work; not for unrelated production agents.
metadata:
  short-description: Plan, edit, or operate Photon demos
---

# Photon Demo Creator

Choose the narrowest path that satisfies the request. The full product-research and planning ceremony belongs only to a full new-company demo. Checks for every path are additive by changed surface; an operational request does not silently become a redesign.

Keep demos deterministic unless the user explicitly requests live integrations or AI. In developer documentation and handoffs, distinguish scripted behavior from verified live search, generation, diagnosis, booking, payment, or external access.

Keep the visible demo conversation product-like. Do not insert “demo preview,” “scripted demo,” “simulated,” “no real payment,” or similar disclaimers into messages, mode-selection replies, or mini-app copy unless the user explicitly requests that wording. Put simulation and integration limitations in the README or developer handoff instead. This copy rule does not authorize real transactions or changes to no-charge payment mechanics.

## Choose one path

### 1. Read-only discussion

Explain, compare, inspect, or propose without changing files or external state. Read only the source or reference needed to answer. Do not require a demo contract, company preflight, test suite, server startup, or cloud access.

### 2. Small local edit

Use for a bounded change to an existing demo that does not alter conversation states, delivery gates, route identity, or external state: copy, colors, logo, item, price, metadata, or a similarly narrow correction.

- Treat the named target and existing behavior as authoritative; do not redo company analysis.
- Inspect the target source, its focused spec, and directly coupled surfaces only.
- For color changes, load `brand-mini-app`. For item or price changes, keep rendered checkout, Apple Pay amount, and any conversation mention consistent.
- Do not publish, restart, provision, rehearse, or expand a one-surface edit without an explicit request.

### 3. Conversation-flow change

Use when an existing demo's transcript, state transitions, media/reaction gates, reset, card timing, or delivery behavior changes. Read [Conversation design](references/conversation-design.md), then only the closest domain reference if it changes a domain-specific interaction.

Before editing, state the exact affected transcript and gates. Keep state per `space.id`, transitions deterministic, outbound messages ignored, and provider side effects separate from pure planning. Reactions must target the intended message or attachment; requested reactions and reads should start concurrently and stay off an immediate reply or card's critical path. Verify focused state and delivery behavior, including reset and per-space isolation when affected.

### 4. Full new-company demo

This is the only path that uses the full ceremony. Read [Company analysis](references/company-analysis.md), [Conversation design](references/conversation-design.md), and the closest of [Travel](references/travel.md), [Health](references/health.md), [Video](references/video.md), or [New category](references/adding-categories.md).

Research current first-party product evidence, choose one narrow product thesis, and show the user before editing:

- the user, job, natural first message, and proof moment;
- the exact transcript, state gates, failure/reset behavior, and mini-app handoff;
- whether photos, video, reactions, typing, polls, or groups are used and why;
- the checkout item/amount, target route, brand evidence, and single next action;
- the checkout, Photon project/number, hosted route, visible brand, and requested operational scope.

In `photon-travel-demo`, also read [Canonical Sites and Apple Pay](references/sites-apple-pay.md) and resolve its route, item/amount, and conversation preflight before implementation. Then implement the smallest deterministic flow that earns the checkout. Use `appCard(publicHttpsUrl, { live: true })` only at the planned transition; a rich link is not a mini-app. Load `brand-mini-app` for the palette rather than duplicating palette logic.

A build request authorizes local implementation, not publication, a cloud project mutation, an unsolicited message, or device rehearsal.

### 5. Operations

Use for an explicit request to publish, start, stop, restart, provision, switch, or rehearse. Preserve the current product and conversation unless an edit is also requested.

- Read [Server lifecycle](references/server-lifecycle.md) for server or Photon project operations.
- Read [Canonical Sites and Apple Pay](references/sites-apple-pay.md) for checkout publication or hosted-route verification in `photon-travel-demo`.
- Reverify checkout, revision, config, route, process ownership, and cloud target appropriate to the operation.
- Treat publication, local startup, provider acceptance, card delivery, and physical-device rendering as separate outcomes.
- A device rehearsal requires an explicit request and direct physical observation; successful tests, startup, or provider calls are not substitutes.

## Verification matrix

Apply every row touched by the work. Use repository-defined commands and focused specs where available.

| Change | Required checks |
| --- | --- |
| Copy only | Target spec test and typecheck |
| Color only | Palette/contrast evidence and target render |
| Price or item | Target render, exact Apple Pay amount, and conversation consistency |
| Conversation | Focused state and delivery tests |
| New route | Checkout suite and retained-route inventory |
| Publish | Full checkout checks and hosted target/retained-route verification |
| Restart | Agent tests, typecheck, process ownership, and fresh startup |
| Device rehearsal | All relevant rows plus physical observation |

Do not run unrelated repositories merely for ceremony. Report product evidence and inference, source changes, local checks, authentication/startup, provider acceptance, hosted availability, and physical-device behavior as distinct evidence tiers.

## Shared implementation boundaries

- Inspect the target checkout, branch/base, dirty state, installed Spectrum version, relevant assets, and process ownership only to the depth required by the chosen path. Preserve unrelated work.
- Use the installed `spectrum` skill for SDK/provider contracts when code touches Spectrum. Use `photon-cli` only for authorized Photon cloud operations; never print or rotate a live secret casually.
- Keep server logic, Photon project/number, hosted mini-app, route identity, and visible brand independent.
- Preserve supplied assets and established compact mini-app behavior unless the request explicitly changes them.
- Building one company demo does not authorize modifying the reusable category library.
