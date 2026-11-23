# Pinch Hit trial

A coach needs the score table covered for a 9 a.m. game. The product proof is
the difference between asking for help and a specific person accepting. The
authoring input is the tested two-thread transcript from the local Pinch Hit
prototype. The paper scorecard and first-inning notation are illustrations.

| Span at 24 fps | Beat | What the viewer learns |
| --- | --- | --- |
| 0–95 | Empty scorebook assignment | There is a specific job to fill before first pitch. |
| 96–203 | Coach sends `cover 9am` | The service requests help and leaves coverage pending. |
| 204–323 | Maya's own conversation | Maya sees the specific request and sends `I can score`. |
| 324–407 | Filled scorebook assignment | The same assignment now names Maya and coverage is confirmed. |
| 408–479 | First-inning notation and wordmark | The scorebook closes the opening question about whether play can start with coverage. |

Use dark field green, warm paper, and an oxide-red rule. Compose at
1280 × 720, leave a 76 px side gutter, and hold the final line for over two
seconds. Set the reader's attention through the isolated appearance of
the two chat turns. Avoid repeated setup shots and feature cards.

For the A/B test, replace only the filled assignment with a confirmation
card in frames 324–407. The score and timeline stay the same. The score's
paper ticks and pitched notes are synthesized in `score.py`. The ending
number uses the upstream `number-pop-in` tween from the vendored registry
component, adapted to static score glyphs.
