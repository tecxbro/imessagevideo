---
videomd: 1
part: timeline
shots: 9
tokens: 628
---

# Timeline

One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
`story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).

```videomd-timeline
#01 0.0-4.1 | camera smooth move | made~ code / template render 62% · runner-up screen recording / screenshot 12% | material~ rendered by the creator | remake code render · Part 1
#02 4.1-5.4 | camera smooth move | transition fade through 0.9s | made~ code / template render 76% · runner-up AI-generated video 12% | material~ rendered by the creator | remake code render · Part 1
#03 5.4-8.5 | camera smooth move | transition slide 0.4s | overlay subtitle | made~ 3D render 55% · runner-up code / template render 28% | material~ rendered by the creator | remake AI generation / 3D render · G1 | flag low confidence
#04 8.5-12.5 | camera smooth move | transition whip pan 0.6s | overlay subtitle | made~ 3D render 60% · runner-up code / template render 18% | material~ rendered by the creator | remake AI generation / 3D render · G1 | flag low confidence
#05 12.5-19.1 | camera smooth move | transition slide 0.3s | made~ code / template render 59% · runner-up 3D render 32% | material~ rendered by the creator | remake code render · Part 2 | flag low confidence
#06 19.1-25.0 | camera smooth move | transition wipe 0.2s | overlay styled text | made~ 3D render 62% · runner-up code / template render 30% | material~ rendered by the creator | remake AI generation / 3D render · G1
#07 25.0-27.8 | camera smooth move | transition fade through 1.1s | made~ code / template render 85% · runner-up screen recording / screenshot 10% | material~ rendered by the creator | remake code render · Part 3
#08 27.8-29.2 | camera smooth move | made~ code / template render 75% · runner-up 3D render 17% | material~ rendered by the creator | remake code render · Part 3
#09 29.2-31.1 | camera static | transition slide 0.7s | overlay subtitle | made~ 3D render 40% · runner-up code / template render 39% | material~ rendered by the creator | remake AI generation / 3D render · G1 | flag low confidence
```
