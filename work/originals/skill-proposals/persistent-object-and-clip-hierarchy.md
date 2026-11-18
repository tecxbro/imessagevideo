# Proposal: name the "persistent mutating object" pattern + clip-hierarchy rule

Source: creative agent, after film-01 + a deliberate generality test (brief-02).

## Verdict on forced sameness — NO

The skill did **not** force the two briefs into the same structure. Film-01 is
a growing-stack film (send → receipts → cutaway → payoff); brief-02's test
scene is a single card mutating in place with a clock-chip time montage, a
proactive agent, and almost no scroll. Both fit the existing shot grammar.
The friction found is documentation-level, not structural.

## Friction 1: no named pattern for state-ful objects

`director/brief-schema.json` describes shots as component lists + sound
events; it assumes the interesting change is *things arriving*. A persistent
object that mutates (live card, order tracker, boarding pass, poll) has to be
described in prose inside `validation`, and reviewers can't tell at a glance
that the shot's event is *internal*.

Suggested addition to `directing.md` (grammar only — no schema break):

> **Persistent objects.** When a card/tracker is the evidence, keep it anchored
> and mutate it via sibling layers with `start`/`end` windows (or keyframed
> content) — do not scroll it away and re-show it. Declare the states in the
> shot's `components` as `LiveCard(state-a…d)` and anchor `sound_events` to the
> *state-change frames*, which may sit inside one component's span.

The brief-02 test scene (`work/originals/brief-02/test-scene/`) is a working
example: four states on one card via `start`/`end`, clock chip advancing
2:12→2:18 with zero scroll.

## Friction 2: clips belong on the viewport, not the scrolling group

film-01 bug: a `clip` on a scrolling message stack was evaluated in the
group's *local* space, so content that scrolled past the clip rect vanished —
the payoff cards never appeared mid-film. Fixed by clipping an unmoved
wrapper ("viewport") around the moving stack.

Suggested addition to `scripts/shared/SCHEMA.md` near `clip`:

> Clips evaluate in the layer's local space. For scrolling stacks, put the
> clip on an **unmoved wrapper** around the moving group — never on the
> scrolling group itself.

## Friction 3 (minor): grouped keyframe shorthand

Per-property keyframes make synchronized multi-property moves verbose and
error-prone (film-01 had keyframe-order bugs around repeated `t` values).
Authors will write a `K(t, {y, opacity, scale})`-style helper anyway; an
official example in `director/components.mjs` docs would prevent the
ordering class of bugs.
