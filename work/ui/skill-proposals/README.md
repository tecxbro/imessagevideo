# Skill-change proposals — UI agent

These are **proposals only** — `skill/imessage-motion-recreation/director/` is outside this
agent's write scope. Each file below describes a concrete patch; the v2 reference
implementation lives at `work/ui/components/components-v2.mjs` (+ `textmetrics.mjs`) and
every claim is evidenced in `work/ui/{behavior,attachments}-evidence.md`.

| Proposal | File | Touch points |
|---|---|---|
| P1 Auto-wrap + measured bubble geometry | `p1-message-bubble.md` | `components.mjs MessageBubble`; `component-contracts.md` "Text is editable…" paragraph |
| P2 Tapback component (child-anchored) | `p2-tapback.md` | new export; contracts "State transitions" |
| P3 Composer draft→send lifecycle | `p3-composer.md` | `components.mjs Composer`; contracts state paragraph |
| P4 Typing indicator + group sender chrome + DeliveryStatus | `p4-conversation-details.md` | new exports; `MessageBubble` params |
| P5 AppCard anatomy + PhotoStrip + card→panel morph | `p5-appcard.md` | `components.mjs AppCard`; contracts "State transitions" |
| P6 DeviceFrame + camera discipline | `p6-deviceframe.md` | `components.mjs PhoneFrame`; contracts "CameraRig" sentence |
| P7 Emoji cross-engine caveat | `p7-emoji-caveat.md` | `component-contracts.md` only (doc patch) |

Priority order follows `work/ui/priority-list.md` (tails > wrap > tapback > composer > typing > card > group > status > + affordance > emoji > device > voice). P1–P5 are the ones that force rework today; P6–P7 are correctness/documentation.

If maintainers prefer a drop-in: `components-v2.mjs` is self-contained, emits the same scene
contract, and is a superset of the nine v1 builders (all v1 names keep working signatures
except `AppCard`/`PhoneFrame`, which gain strictly-optional params — see each proposal's
compat note).
