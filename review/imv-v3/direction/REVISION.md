# The Moon Cue — direction and revision

## Which film to make

The viewer has already built an agent. The person who feels the difference is
the customer with a question when they need the answer. The capability is the
text exchange in iMessage. A second visible action should show why that reply
matters without adding a product claim. [Claim record](CLAIMS.md)

| Possibility | First image and what changes | Decision |
| --- | --- | --- |
| Dispatch desk from the builder’s side | An after-hours incoming-message pulse on a dark desk. A remote customer's problem appears one screen at a time. | The builder has the clearest point of view, but the screen sequence could become an explanation. An invented operator dashboard would need evidence of its own. |
| Two people hearing the same question | A technician crosses an empty backstage corridor while someone sends a message. The two actions are juxtaposed for a reveal. | Two sources of help muddy who answered. This version would need a more elaborate performance to make the distinction legible. |
| Shadow theater with a missing cue | The rabbit raises its head in a live shadow play. The operator’s question names what is absent. A reply sends the operator to the prop and the audience sees the missing shape complete the image. | The builder implicitly supplied the agent's knowledge. The operator does the physical work. The audience can see the result in a single altered image. Chosen. |

The small cast is a puppet operator, a paper rabbit and people already seated
in front of the screen. The motion starts in an amber pool with dark silhouetted
forms. Blue is reserved for the outgoing action. The miniature palette makes
the practical red tin easy to track as focus transfers. The last composition
preserves the stage and the material result under the wordmark.

## What changed

Picture judgment is from decoded contact sheets and consecutive frames.
Frame numbers below are zero-based at 24/1. The moving rough stays archived
with the exact source at `2873e04`. The revised picture is a separate export.

| Decision | Rough | Locked | Inference restored |
| --- | --- | --- | --- |
| Establish the speaker | At f56 the header says “Stage Crew” and “iMessage”. A picture-only reviewer read it as a human contact. | At f56 the compiled phone header says “Keiki agent · iMessage.” The draft is already there. At f84 send clears it. At f113 an incoming reply follows beneath the question. | From the start of the exchange, the viewer sees which participant is an agent and which person acts on the answer. |
| Give the viewer a reason to leave the phone | The reply is fully readable by f119 (4.96 s). I marked f120 as the point the static composition stops advancing the action. It gives the same information through f180, then cuts to the tin at f181 with no lead toward the object. | By f119 the revised reply has settled. The phone begins edging down-left after f141, the tin and stars sharpen on the right, and f153 cuts onto them in the same region. The cut is 28 frames earlier. | As soon as the text can be read, the next look follows a specific clue. The named stars give the match a checkable referent. |
| Make the physical result follow the clue | The tin opens at f197. The operator lifts the prop starting f218. The returning stage begins f246 and holds before the shadow moves. | The lid starts f165 and the lift f189. f211 retains the rising crescent in the glove. The stage returns at f212, the same shape becomes visible from screen right at f216, and the right audience figure leans from f270. | The hand carries the prop. A visible actor uses the answer and the audience responds after the picture is completed. |
| Let the ending keep its consequence | Title starts at f311. | Title starts at f307 over the held stage. The silhouette of the part the viewer followed stays present behind the copy. | There is time to register the completed cue before reading the product line. |

[Before and after](01-edit-comparison.jpg) · [Consecutive event frames](02-action-boundaries.jpg) · [Locked picture overview](03-picture-overview.jpg)

I used Recreation’s Poke measurement to check an editorial choice. In the
source, the question becomes legible at f413–414 and stays visible across
f509–512 as the controlled surface clears. Answer evidence appears at f513–514.
This film maintains the anchor as a physical object in the same screen region
while the presentation changes. The source’s motion, graphics and timings are
its own. [Recreation's measurement](https://github.com/tecxbro/imessagevideo/blob/f0d6567/review/imv-v3/recreate/poke/README.md)

For reproducible excerpts, replace the numbers with any adjacent run around
an event:

```sh
ffmpeg -v error -i locked.mp4 -vf "select=between(n\\,149\\,155)" -fps_mode passthrough /tmp/locked-%02d.png
```
