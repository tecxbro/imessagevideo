# Unfamiliar film for the recreation transfer test

**Choice: `03-photon-mini`** ("Introducing API for Mini Apps in iMessage")
— 1920x1080, 30 fps, 1,260 frames, 42.0 s.
Source: `projects/03-photon-mini-complete-v1/imessage-recreations/references/03-photon-mini/source.mp4`
(copy to a neutral path for the trial; see `observations/trial-protocol.md`).

## Rationale

Of the five eligible films (04-poke is the recreate agent's documented
known-defect training case), 03-photon-mini is the median difficulty and the
most representative of the skill's core value: an iMessage conversation that
spawns mini-app surfaces. It is 1080p30 like the majority, median length,
and contains a realistic difficulty mix rather than an extreme:

- Tractable majority: title cards, one iPhone conversation, composer/send
  flight, chat-card→mini-app expansion, sheet depth transitions, end taglines.
- Bounded hard sections: the Uber Eats full-sheet menu (photographic food
  thumbs, per-item Memoji pickers, cart badge — src ~f618–734), the
  world-release finale where food props and "Order!" bubbles detach into
  canvas space (~f730–799), the Jump Jump game card artwork (~f800), and a
  ~20-tile mini-app mosaic end card.

Ranked estimates of the others: 06-gallery is pathological for a timed test
(live-action segments, longest runtime, non-1:1 source↔output mapping even in
the accepted scene). 05-linq has the most distinct polished app interiors
(seven+), 1458 frames and only 960x720 — hardest in scope, coarsest truth.
02-danieltian is the longest pure-motion narrative with bespoke avatar-swarm
choreography. 01-photonhq is shortest but the least iMessage-native (giant
SMS/email/voice/WhatsApp walls) with extreme unique-copy density — atypical
of what the skill teaches. 03-photon-mini sits in the middle: hard enough to
separate a weak skill from a strong one, standard enough that a strong skill
should materially help.

## Access rule for the trial

The recreating agent receives **only** the source.mp4 (at a neutral path).
It must NOT open anything under `projects/03-photon-mini-complete-v1/` — its
accepted `scenes/03-photon-mini/scene.json`, `deliverables/`, `verification/`,
engines copies, or any view of its rendered movies (including
`catalog/index.html` / `inventory/` entries that resolve to that project's
outputs). The `skill/` directory ships with three measured studies derived
from this film (mini.rich_card_arrival f546–617, mini.sheet_depth f618–734,
mini.world_release f730–799), its atlas panels and `analysis/03-photon-mini/`
CSVs; those are legitimate skill knowledge and are **allowed** in both legs —
the revised skill is expected to add more such knowledge.

Grading ground truth (observer only): the accepted scene + five deliverable
MP4s + verification evidence of `03-photon-mini-complete-v1`, plus the
historical per-frame comparison `director/analysis/03-photon-mini/frames.csv`
(mean native MAE 1.5265, max 4.4732 vs accepted GSAP — the reference bar a
perfect-skill leg would approach, not a realistic target for a fresh
single-session recreation).
