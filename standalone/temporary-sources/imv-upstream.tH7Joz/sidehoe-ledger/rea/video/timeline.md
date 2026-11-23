---
videomd: 1
part: timeline
shots: 9
tokens: 747
---

# Timeline

One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
`story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).

```videomd-timeline
#01 0.0-4.1 | seen Three pinned portraits flow into scrollable rows with UI lab… | camera smooth move | made~ code / template render 90% · runner-up 3D render 26% | material~ rendered by the creator | remake code render · Part 1
#02 4.1-5.4 | seen Dark rounded logo settles, then an enlarged handset rim ente… | camera smooth move | transition fade through 0.9s | made~ code / template render 91% · runner-up 3D render 21% | material~ rendered by the creator | remake code render · Part 1
#03 5.4-8.5 | seen Glossy handset and cream highlights move into pink bloom and… | camera smooth move | transition slide 0.4s | overlay subtitle | made~ 3D render 92% · runner-up code / template render 23% | material~ rendered by the creator | remake AI generation / 3D render · G1
#04 8.5-12.5 | seen Portrait discs fly in and resolve to three labelled profiles… | camera smooth move | transition whip pan 0.6s | overlay subtitle | made~ 3D render 91% · runner-up code / template render 35% | material~ rendered by the creator | remake AI generation / 3D render · G1
#05 12.5-19.1 | seen Handset, detached blue suggestion, pointer, and calendar sha… | camera smooth move | transition slide 0.3s | made~ code / template render 94% · runner-up 3D render 35% | material~ rendered by the creator | remake code render · Part 2
#06 19.1-25.0 | seen Colored app tiles orbit; check the distinct edge light and n… | camera smooth move | transition wipe 0.2s | overlay styled text | made~ 3D render 94% · runner-up code / template render 24% | material~ rendered by the creator | remake AI generation / 3D render · G1
#07 25.0-27.8 | seen Second handset reframes and the pointer closes in on control… | camera smooth move | transition fade through 1.1s | made~ code / template render 94% · runner-up 3D render 17% | material~ rendered by the creator | remake code render · Part 3
#08 27.8-29.2 | seen The black badge appears first and the closing copy follows a… | camera smooth move | made~ code / template render 94% · runner-up 3D render 28% | material~ rendered by the creator | remake code render · Part 3
#09 29.2-31.1 | seen Pink wash, lockup, and final fade change together; verify th… | camera static | transition slide 0.7s | made~ code / template render 91% · runner-up 3D render 41% | material~ rendered by the creator | remake code render · Part 3
```
