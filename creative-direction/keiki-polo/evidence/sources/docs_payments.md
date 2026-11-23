---
title: Payments
description: Let agents onboard businesses and send payment links through an organization’s connected account.
---

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

Agents with the **Payments** ability sign businesses up and send those businesses' customers payment links. The payments run on [Grosso](https://pay.grosso.ai). Each business is paid directly through its own Stripe connected account, and Keiki never holds the money.

## One Grosso account per organization

An owner or admin connects the organization through [Keiki Code Mode](/docs/mcp-codemode) (`POST /payments/signup`, then `POST /payments/verify`):

1. Enter a business name and email. Grosso emails a code to that address.
2. Enter the code and accept the [Grosso Terms](https://grosso.ai/legal/terms), [Grosso Merchant Terms](https://grosso.ai/legal/merchant-terms) and [Stripe Connected Account Agreement](https://stripe.com/legal/connect-account). Keiki stores the organization's Grosso key encrypted and never shows it again.

A new account can't take payments until its identity is verified. **Verify identity** opens Grosso's identity check. Once Grosso enables the account, **Switch to live** replaces the signup key with a live one, so the organization still holds exactly one key. **Disconnect** revokes the key at Grosso. Businesses, payments and payouts stay on Grosso.

If Grosso stops accepting the key, the page shows **Key rejected** and agents' payment tools return `payments_key_rejected` until someone reconnects.

## Agent tools

Turn on **Payments** in an agent's abilities (`features.payments`). Every call uses the organization's key on the server. The key never reaches the model, the sandbox or tool output.

| Tool | Grosso call |
| --- | --- |
| `payments_onboard_business` | `POST /v1/payees`. Grosso emails the owner the onboarding link. |
| `payments_businesses` | `GET /v1/payees` |
| `payments_request_limit` | `POST /v1/payee_grants`. The owner approves the largest single request and the daily total. |
| `payments_request` | `POST /v1/payment_requests`. Needs an approved limit that covers it. Returns the `checkout_url` the payer opens. On a Keiki iMessage line the payer also gets a Keiki Vault Pay card (`pay_card: 'sent'`), and the agent sends the link only if they ask for one. |
| `payments_request_status` | `GET /v1/payment_requests/:id` |
| `payments_cancel_request` | `POST /v1/payment_requests/:id/cancel` |
| `payments_request_refund` | `POST /v1/payment_requests/:id/refunds`. The owner approves the refund before it happens. |

Amounts are integer US cents. Write calls send an idempotency key derived from the tool call, so a replayed call never creates a second payee or payment request.

`GROSSO_API_BASE_URL` points the platform at another Grosso deployment (the default is `https://pay.grosso.ai`).

## Vault Pay card settlement

Grosso signs deliveries to `POST /webhooks/grosso/:orgId` with the organization's stored test or live endpoint secret. A request is looked up only within that organization. Refund events must include a numeric cumulative `amount_refunded`; an incompatible event type/status or missing refund total is acknowledged without looking up a card.

The stored projection compares `(money_settled, amount_refunded)`, where paid and refund statuses have money settled and closing statuses do not. Only an increasing key advances the card. A refund cannot be undone by a late paid delivery; a smaller partial refund cannot replace a larger one. Payment after expiration or cancellation is legitimate and advances the card. Cancellation and expiration tie, so the first received stays. Stale deliveries and completed duplicates do not rewrite cards, replace tokens or notify the agent.

Each advancing event claims a durable rewrite with a two-minute lease and stores its settled token hash before updating the card. A failed rewrite returns 503 so Grosso retries the same event (its delivery retries/backoff run for roughly three days). A redelivery resumes unfinished work; another delivery cannot rewrite under a fresh claim. A newer event supersedes an unfinished older projection but preserves its active rewrite lease and token hash. It returns 503 while that lease is live. When the older rewrite finishes, it releases its own claim without marking the newer projection rewritten; the newer event's redelivery then rewrites the card. No database transaction or row lock is held during the card update.

Cards settled before projection tracking existed recover the current payment request with a read-only Grosso GET before accepting their first projection. Recovery requires the organization's key, the delivery's explicit test/live mode, and a matching provider identity and mode. Missing credentials, mode changes, unavailable or malformed responses, and requests that are not settled leave the row and card untouched and return 503 for retry; the delivery's possibly stale facts are never a fallback. Modern cards and cards never rewritten do not need this provider read. A successful recovery persists the provider's status and cumulative refund total, then uses the normal rewrite lease. Notice eligibility is stored separately: only a delivery whose own status and refund total match the recovered facts owes a notice. A stale delivery can correct the card without announcing old news, including after a failed rewrite is retried.

If an iMessage card update outlasts its lease, a newer claim may finish first. When the superseded older call finally succeeds, it marks the current projection unfinished (unless another fresh claim is active) and returns 503. Redelivery of any event for that request can repair an unfinished card using the stored projection, never the stale delivery's status or refund total.

If recovery corrected a card silently, a later delivery matching that stored status and cumulative refund total makes the notice owed under its own event ID. An already rewritten card and its token stay unchanged; repeated matching deliveries do not resend a completed notice. If a rewrite is still unfinished or claimed, the matching delivery returns 503 until it can complete the normal rewrite and notice path. Notice failures also remain retryable.

The agent notice is sent only after a successful card update and its completion is recorded separately. If the process crashes after rewriting or sending the notice, redelivery resumes the notice without rewriting; `grosso:<stored event id>` deduplicates notice delivery downstream. Repairing a card does not resend an already completed notice. An unsent notice uses the stored projection's event ID and status, even when a stale delivery triggered the repair. Approval-card settlement is independent of this payment projection.
