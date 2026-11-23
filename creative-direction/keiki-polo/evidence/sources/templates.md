# Keiki agent templates

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

Reusable starting points for building agents that work across the channels customers already use.

Catalog page: https://onkeiki.com/templates

## 🌸 Orchid

- Blurb: The assistant that never sleeps: email intelligence, calendar, reminders, daily digest, browser handoff.
- Description: A complete personal assistant over SMS. Watches Gmail and Outlook for mail that matters, reminds before calendar events, fires user reminders, sends a morning digest, and hands off to a live browser when only the user can act. Users connect their own accounts via texted OAuth links.
- Model: google/gemini-3.5-flash
- Connections: gmail, calendar, outlook, outlook-calendar
- Attributions: Orchid — Ported from Orchid; Google — Works with Gmail, Google Calendar; Microsoft — Works with Outlook

## 🎓 Office Hours

- Blurb: YC office hours over text: the six forcing questions, real pushback, and one assignment you have to go do.
- Description: A product diagnostic that runs like YC office hours. Startup mode pushes on demand evidence, the status quo, the specific human, and the narrowest wedge. Builder mode chases the coolest shippable version. Both end in premises you have to agree with, alternatives you have to choose between, a brief, and one concrete assignment it follows up on days later. Ported from the gstack office-hours skill. No accounts to connect.
- Model: anthropic/claude-sonnet-5
- Connections: None required
- Attributions: Y Combinator — Built around the Y Combinator office hours format

## 🎟️ Event Companion

- Blurb: Cloudflare Connect 2025 in a text thread: what's on now, who's speaking, and a nudge before your next session.
- Description: A companion for attendees of Cloudflare Connect 2025 (Aria Resort & Casino, Las Vegas). Reads the event's own published sessions to answer what's on now, what's worth going to, and who a speaker is, holds the sessions and meetings the user picks, reminds them shortly before each one, and texts one short rundown of the day each morning in America/Los_Angeles. It also remembers the people they meet. Nothing to set up and no accounts to connect: the event is built in, so the first text is already about which sessions to see.
- Model: google/gemini-3.5-flash
- Connections: None required

## 🦷 Dental Receptionist

- Blurb: Your practice’s front desk over text: booking requests, reminders, insurance answers, and real triage.
- Description: A front desk for a dental practice that answers every text in seconds. Captures complete appointment requests with preferred times, sends day-before reminders, answers hours and insurance questions from the practice profile you fill in, and recognizes the emergencies that need a phone, not a text queue. Never diagnoses, never invents a price. No accounts to connect: edit the practice details in the prompt and go live.
- Model: google/gemini-3.5-flash
- Connections: None required

## 🏡 Realtor Concierge

- Blurb: Answers every lead in seconds, qualifies in conversation, books showings, and never drops a follow-up.
- Description: A lead concierge for a real estate agent. Replies to every inquiry instantly at any hour, learns intent, budget, timeline, and financing in conversation instead of a form, coordinates showings with morning-of reminders, and follows up on the exact date each lead comes due. Fair housing rules are built in and immutable. No accounts to connect: edit the agent profile in the prompt and go live.
- Model: google/gemini-3.5-flash
- Connections: None required

## 📖 Study Coach

- Blurb: Explains until it clicks, quizzes you on the forgetting curve, and flags deadlines before they’re emergencies.
- Description: A tutor and accountability partner over text. Explains course material one idea at a time until the student can say it back, turns what they learn into topics on a real spaced-repetition schedule with a nightly recall question, tracks every assignment and exam, and nudges 48 hours before deadlines. Helps them learn without doing graded work for them. No accounts to connect.
- Model: anthropic/claude-sonnet-5
- Connections: None required

## 💇 Salon Receptionist

- Blurb: Your salon’s booking desk over text: requests captured, reminders sent, regulars nudged when they’re due.
- Description: A booking desk for a salon that answers every text in seconds. Captures complete appointment requests (service, stylist, preferred times), remembers each client’s usual, sends day-before reminders, and nudges regulars when their next visit comes due, anchored to their cadence. Answers service and pricing questions from the salon profile you fill in and never invents an opening. No accounts to connect: edit the salon details in the prompt and go live.
- Model: google/gemini-3.5-flash
- Connections: None required

## 🏢 Property Desk

- Blurb: Maintenance requests captured complete, emergencies triaged, and no open request ever going silent.
- Description: A front desk for a property manager. Takes maintenance requests with everything a contractor needs (the problem, the unit, photos, access), recognizes gas, fire, and flooding as leave-now emergencies, answers building questions from the property profile you fill in, and checks back on every open request until it’s actually fixed. Lease and legal questions go to the office, never to a guess. No accounts to connect: edit the property details in the prompt and go live.
- Model: google/gemini-3.5-flash
- Connections: None required

## 🍽️ Restaurant Host

- Blurb: Your host stand over text: reservations captured, day-of reminders sent, regulars remembered.
- Description: A host stand for a restaurant that answers every text in seconds. Captures complete reservation requests (party size, time, name, what the kitchen should know), sends a day-of reminder with an easy out that beats a no-show, flags allergies to the kitchen without ever guessing, and remembers guests: their dietary notes, their occasions, the table they like. Answers hours, menu, and parking questions from the restaurant profile you fill in. No accounts to connect: edit the restaurant details in the prompt and go live.
- Model: google/gemini-3.5-flash
- Connections: None required

## 🛒 Instinct

- Blurb: Texts you back with the order number: it uses a browser to actually run your errands.
- Description: A personal assistant that does chores on the web. Orders the groceries, books the tickets, chases the refund, and reports the confirmation number. It never asks for a password over text: when a login or CAPTCHA needs a human it hands you the live browser session, and purchases spend from the agent wallet on a card the browser fills but the agent never sees, one approval per exact total. Remembers your usual store and address, and chases any errand left waiting on you. Ported from Merit Systems’ OpenInstinct. No accounts to connect.
- Model: anthropic/claude-sonnet-5
- Connections: None required
- Attributions: Merit Systems — Ported from Merit Systems' OpenInstinct

## 🏦 Night Drop

- Blurb: The vault, the alarm, and the tape: every inbound item stamped, danger rings you, mornings play the record.
- Description: A back-office vault for a small business, not a virtual employee. Forward the mail, the invoices, the voicemails, the form submissions, and the reviews: each becomes a stamped packet — what it is, what it matched, what it wants (pay, file, reply, ignore). Anything touching money, legal, or reputation waits behind a second key until the owner stamps it, like a night deposit that will not open until morning. The alarm rings only for danger: a duplicate invoice, a wire request, a license lapse, a review with legal teeth. Every morning it plays the tape — what came in, what was filed, what is waiting for a stamp — the audit trail a shop actually keeps. No accounts to connect: edit the shop details in the prompt and go live.
- Model: anthropic/claude-sonnet-5
- Connections: None required

## 🧠 Company Brain

- Blurb: Answers from what the team already wrote, with the link, and files the ticket while it is there.
- Description: A teammate that has read the workspace. Ask why a decision was made, who owns a system, or what was promised to a customer, and it answers from the actual thread with the permalink, then acts on it through the tools you connect. It answers with your access and never yours plus everyone else’s: private channels stay private, and an answer that only exists in a room you cannot see is named, not repeated. Unprompted, it speaks once per thread and only with a fact, a correction, or the link people are about to go looking for. Remembers what the room settled so the same question costs one message next month, digests the week when there is something to say, and chases the work it opened for you. Ported from Supermemory’s Company Brain. No accounts to connect.
- Model: anthropic/claude-sonnet-5
- Connections: None required
- Attributions: Supermemory — Ported from Supermemory's Company Brain

## 🍃 Leaf

- Blurb: Billing operations in Slack: looks it up, previews the change, proposes it, and waits for the approval.
- Description: A billing operations teammate for the organization that deploys it, ported from Autumn’s Leaf. Ask what plan a customer is on or tell it to move them to another one: it reads the answer from the billing tools you connect, previews the exact proration and next invoice, and puts the change in front of the thread as an approval card. Who may approve comes from your identity webhook, the card shows exactly what will run, edits supersede the pending card, and it never claims a pending change happened. Bring your own billing MCP server, identity webhook, and dashboard link at deploy time.
- Model: anthropic/claude-sonnet-5
- Connections: None required
- Attributions: Autumn — Ported from Autumn's Leaf

## 🏘️ Agency Desk

- Blurb: The enterprise AU real-estate desk for Rex CRM, Outlook, and scheduled portal research.
- Description: An enterprise Australian real-estate desk over text: CRM notes and inspection lists over the Rex API, appraisals booked in Outlook, and portal comparables researched on a schedule.
- Model: anthropic/claude-sonnet-5
- Connections: outlook
- Attributions: Rex CRM — Built for the Rex CRM API; Microsoft — Works with Outlook
