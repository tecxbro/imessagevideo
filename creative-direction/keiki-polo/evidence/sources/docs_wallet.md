---
title: Agent wallets
description: Give an agent a spending policy in front of your own payment account.
---

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

An agent wallet puts a spending policy in front of a payment account your organization
connects. The model never sees a card number. Every purchase starts as a purchase intent,
and your policy decides what happens to it. You set a per-purchase cap, daily and monthly
caps, a merchant allowlist, and an approval threshold. Each intent is then declined, parked
for a person, or authorized. An authorized intent creates a one-time card for exactly that
amount. An order the payment provider places itself may come in under the intent, never
over.

## Payment rails

A wallet connects to a payment account through one of two rails. You choose the rail when
you create the wallet, and it stays fixed while a connection is active. One rail connects by
showing a code the operator confirms in the provider's app. The other sends a code to the
operator's email or phone to type back.

|  | Device-flow rail | Code-verification rail |
| --- | --- | --- |
| Connecting | Keiki shows a code, and the operator confirms it in the provider | Keiki sends a code to the operator's email or phone, and they type it back |
| Before it can spend | Nothing. The account's own payment methods are used | The account holder adds a card on a hosted page |
| A purchase | A one-time card the agent spends at checkout | A one-time card, or an order the provider places itself |
| Per-purchase limit | Up to 5,000.00 | 1.00 to 20,000.00, USD only |
| On disconnect | The grant is revoked | Open purchases are closed at the provider first; an unknown outcome or outstanding order claim blocks disconnect while the grant works |

Connection grants are encrypted at rest and never leave the server. The provider account
secret is used only to start, verify and refresh a connection.

### Budget reservations

Authorizing a purchase reserves its full amount against the existing per-purchase, daily
and monthly policy before asking the payment provider for a credential. Purchases waiting
for approval reserve budget too, so two simultaneous requests cannot each spend the same
remaining budget. A user's own card has its own budget within the wallet; it does not consume
the owner's or another user's allowance.

The policy check and intent insert run in one short PostgreSQL transaction. It locks the
owner's `agent_wallets` row, or the paying user's `agent_conversation_wallets` row scoped to
that wallet, with `FOR NO KEY UPDATE`. The spend sum is read after acquiring the lock and
the current policy is re-read before insertion. A database timestamp captured after the
lock is used for both the budget windows and intent creation, including waits across midnight.
Different payers do not share a lock, and
provider calls happen after the reservation transaction commits. The intent ID remains the
provider request's idempotency reference.

For lifecycle changes: `pending_approval`, `authorized`, `cancelling` and `spent` intents count toward
the payer's budget, using the intent's creation date for the daily/monthly windows. An empty
sum is zero; a rolled-back insert reserves nothing. Moving to `declined`, `cancelled` or
`expired` releases the reservation; `spent` continues counting for its original windows.
Approval of a pending intent consumes its existing reservation, not a second one. Any path
that newly creates a commitment must use the same payer lock and transaction. A lifecycle
handler must establish that the provider can no longer charge before releasing a live
reservation: an unknown external outcome is not evidence of a safe-to-repeat failure.
Closing a provider-held purchase first makes it `cancelling`, which cannot be spent but
keeps its reservation until the provider confirms a final outcome. Expiry stops card use
immediately without releasing an unconfirmed reservation. Outstanding order-confirm claims
are reconciled with the provider, never expired by the local deadline; same-argument retries
can still recover their outcome after that deadline.

A successful cancel call alone does not prove that no payment happened. After
either a successful or failed cancellation, the provider request is read back:
`succeeded` is recorded as `spent`, terminal no-charge outcomes release the
reservation, and unreadable or non-terminal outcomes keep it counted. Disconnect
also requires this readback before it can discard the grant for a known request.
Agentcard closing an already-used card is idempotent, not evidence of a refund.

Order-confirm claims are identified by `redeemed_at` and the `#`-separated pending
order marker, regardless of `spend_request_id`. Agentcard owner authorizations
already have a card ID before `wallet_buy` claims them. A card's terminal status
does not resolve that separate order: expiry, cancellation and card polling leave
the claim reserved for the order ledger, and disconnect keeps its original grant
until the order is accounted for.

Link's `submitted` means a payment is processing, not failed. Unrecognised Link
statuses and Agentcard card statuses or closing reasons are `unknown`, not failures.
Neither releases budget: polling leaves the reservation unchanged, and a failed
cancellation remains `cancelling`. A newly created request that is submitted,
unknown, or approved without card details is held as `pending_approval` with its
provider request ID for later reconciliation. A succeeded request is `spent` even
without card details.

Revoking or disconnecting while an owner's card is being created keeps the intent
`cancelling`; when creation returns, its provider request is attached and closed,
never handed back as a usable authorization. A timeout, server error, or lost answer
keeps the reservation even past the local deadline. Before creation is sent, a
scoped conditional write saves the immutable creation payload, including approval
and the intent ID as the idempotency key, but no credentials or tokens. Background
reconciliation never replays a create, on either rail. The payload is durable
evidence and a marker that creation may have been sent, not permission to retry.
An uncertain create requires manual reconciliation and remains counted indefinitely.
A late original response may still attach its request ID and close the request.
The public result for an unknown creation is `cancelling`, with the intent ID and
a reason that says not to retry. It is never `declined` or a usable authorization.
An already paid result is `spent`; late cancellation/expiry returns its closed
outcome rather than pretending the original create was refused. Dashboard approval
decisions propagate these outcomes too.
A definitive rejection returned to the original
create can decline and release its reservation. Local validation before sending
and a missing grant can also decline without sending a request. Failures during
credential/configuration lookup or saving the payload are also pre-send failures,
not ambiguous legacy creations.

If Link creates a fallback request but cannot produce its approval URL, it tries
to cancel that request. Confirmed cancellation declines the original create;
failed cancellation preserves the request ID and reservation for synchronization
and cancellation on expiry or revoke.

Neither rail's documented idempotency is sufficient for automatic recovery here:
Agentcard's member-token guarantee is unverified, and Link's fallback/retention
semantics do not guarantee a safe replay after revoke. Original Link creates still
carry an idempotency key and recognize the documented duplicate-429 response.

Legacy owner intents with no provider ID and no saved payload may already have
sent a create. They remain reserved and require manual reconciliation: neither a
local deadline nor reconstructed input is proof of a safe release. Local approvals
that have never been authorized and user-card authorizations with no provider
requests close directly unless an order confirm has claimed them.

Operators can find unresolved owner creations by `status = 'cancelling'`,
`spend_request_id IS NULL`, `user_card_id IS NULL`, and `redeemed_at IS NULL`.
Unresolved creations also receive the visible `decline_detail`
diagnostic prefix `reconciliation_required:`. This is not creation provenance:
only `provider_create_payload` records creation evidence, and legacy rows without it
still require manual reconciliation.

Reconciliation holds compare the observed non-terminal status and provider request ID;
a stale grant failure never reopens a finalized purchase. Order confirms reject closed,
unapproved, already-used or locally expired authorizations before resolving or refreshing
a grant. A matching in-flight order remains reconcilable after local expiry.

A late original create chooses its accounting destination under the payer and intent row
locks: attach to an unclaimed row, or retain a separate commitment if the row is already
claimed or paid. Releasing the claim during that decision cannot discard the returned
provider request ID. Cancellation and readback happen only after the commitment is saved.

```sql
SELECT id, wallet_id, status, spend_request_id, decline_detail, provider_create_payload
FROM wallet_purchase_intents
WHERE wallet_id = :wallet_id AND status = 'cancelling'
  AND spend_request_id IS NULL AND user_card_id IS NULL AND redeemed_at IS NULL
ORDER BY created_at, id;
```

Each new intent and its saved create payload bind the original payer using the
provider, grant-holder row ID, provider user ID when available, and a non-secret
`grant_generation` UUID. Agentcard supplies a user ID; Link does not. Reconnecting
reuses the same wallet/user-card row but installs a new generation, even for the
same provider account. Token refresh preserves the generation and conditionally
saves only into that generation. No credentials or tokens are stored on intents
or in payloads.

Every existing-intent retrieval, cancellation, card redemption, order confirmation,
and ledger reconciliation requires the matching original grant. A mismatch or a
legacy intent without provenance is a manual hold: it is counted, never accessed
with the reconnected account's token, and tagged `reconciliation_required:`. Old
intents are not retroactively bound to whichever account is connected now. Local
unsent approvals/user-card rows may still close without provider operations.

To include known-ID/account-mismatch holds in an operator's wallet-scoped review:

```sql
SELECT id, wallet_id, status, spend_request_id, payer_provenance, decline_detail
FROM wallet_purchase_intents
WHERE wallet_id = :wallet_id AND decline_detail LIKE 'reconciliation_required:%'
ORDER BY created_at, id;
```

Background work discovers owners in wallet-ID pages, then uses wallet-scoped
intent-ID keyset pages through expiry, synchronization, stale order claims, and
disconnect. Page sizes bound each read, not total work. Permanently held manual
rows are excluded from work they cannot advance; unresolved ledger reads cannot
prevent later claims or owners from progressing. Manual holds require operator
evidence of a terminal outcome or no request before releasing the reservation.

Disconnect checks claims again after closing open purchases and throws before
removing the grant if a concurrent confirm won. A provider-placed order is only
reported as spent after the ledger records it (or already records that same order);
a late placement restores a cancelled, expired, declined, or cancelling claim
under the same payer lock used by authorization, without applying spending policy
again. A released claim can likewise be recorded as spent if no new claim won.
If another generation superseded it, a separate spent intent records the orphan
order for the original payer, using the provider total or the original cart's
total. Its accounting date is the provider's placement timestamp when available,
otherwise the original claim's redemption timestamp, not the recovery time.
Repeated proof of the same order is idempotent. Only the winning ledger
write notifies the agent. Missing parent accounts or a missing order ID/total
can still require manual reconciliation and return unavailable.

## What your agent can do

| Tool | What it does |
| --- | --- |
| `wallet_balance` | What is left today and this month, the per-purchase cap, and whether a person decides |
| `wallet_authorize_purchase` | Ask to spend: `authorized`, `pending_approval`, `declined`, held `cancelling`, already-paid `spent`, or a confirmed `cancelled`/`expired` outcome |
| `wallet_purchase_status` | Where an intent stands |
| `wallet_purchases` | Recent activity |
| `browse` with `purchase_intent_id` | Pay at a checkout. The card is redeemed server to server and typed in once |
| `wallet_buy_merchants` | Where the provider can place orders itself, and whether each merchant is ready |
| `wallet_buy` | Shop through the provider's own shopping agent and confirm a cart |

### Ordering through the provider

Buying through the provider is a conversation. The agent asks in plain language, a cart
comes back with items, an all-in total and a hash. Echoing the hash as a `confirm` places
the order. Money moves on the confirm and nowhere else, so that is where the wallet stands.

1. `ask` turns pass straight through and charge nothing.
2. A `confirm` must name the purchase intent. Keiki re-reads the conversation from the
   provider, finds the cart with that hash, and checks that its total is within the intent
   and its merchant matches. The agent's own account of the total never decides.
3. The intent is claimed once. Then the confirm is sent with the wallet's payment source:
   either the account holder's added card, which pauses for their approval, or the provider's
   default source.
4. A placed order with a provider order ID marks the intent spent. A direct no-charge
   answer to that confirm (a decline, question, or approval pause) releases its claim via
   CAS, so the same authorization can confirm a corrected cart. If the provider cannot say
   what happened, or reports placement without an order ID, the next call asks its ledger
   instead of placing again. The durable claim and reservation remain until an order ID
   can be reconciled. An empty ledger or an uncorrelated refusal is not proof that this
   confirm cannot still charge, even after local expiry; no grace period releases it.
   Without provider proof it requires manual reconciliation, not another confirm.

If an original card creation returns after an order has claimed its intent, its provider
request ID is retained on a separate, payer-bound intent without changing the order's
claim. That credential is independently counted until cancellation and readback prove it
closed; an already-paid credential is recorded spent. Repeated receipt of the same request
is idempotent. Closing uses only its original grant, and known-ID reconciliation can retry
the close without replaying creation. This records an existing liability without a fresh
policy check, even when the combined commitments exceed the wallet's limits.

A wallet on the device-flow rail is told that the provider does not place orders, and falls
back to paying at checkout with `browse`.

## Apple Pay submission retention

The iMessage payment card remembers submission before sending an authorized Apple Pay
token to the network. Presenting or dismissing a sheet checks that durable marker; an
in-flight attempt polls the existing payment instead of offering another sheet, even if
the extension restarts or the answer is lost. Duplicate authorization callbacks do not
send another token. A known card decline, pre-send failure, or confirmed no-charge payment
status clears the marker so retry remains possible. Unknown answers and unmodelled statuses
retain it until the payment is confirmed paid or closed, without a time-based release.

Each sheet is bound to the token and request details (including the payee, amount and
currency) it displayed, and callbacks must come from that exact sheet. Selecting another
card dismisses and invalidates the previous sheet, including a pending compact-to-expanded
retry. A stale authorization is refused before submission; an already-submitted charge
keeps its original token's marker, and its late completion cannot change a newer card.

Wallets and purchase intents are scoped to the agent's organization.
