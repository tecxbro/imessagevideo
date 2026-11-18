# Check In v3 — native-picture verification

Input SHA256 verified against the supplied value: `9dc4a812480d778c4b453f1eeb8d87e19569683ea2f4d78e8015b9f2f9952d9e`. FFprobe confirms silent H.2641920×1080,30/1fps,720 frames,24 seconds. `director-events.json` and `frame-map.json` are unchanged copies of the supplied attachments.

Sequential decoding, not timestamp seeking, extracted144 native PNGs. All35 supplied actions were checked visually in before/at/after native-frame sheets. **No supplied event frame needed correction or removal.** The list already excludes invisible spaces. This is a new v3 review, not a blanket−120 shift of the first-export cues. Its frame map describes840-frame v2 →720-frame v3, with source210–419 compressed into output210–299.

Evidence: `evidence/opening-actions.png`, `typing.png`, `backspaces.png`, `late-actions.png`, and `contact-sheet.png`. Individual native PNGs remain local and are reproducible with `tools/inspect_frames.py`.

## Early and semantic actions

| Listed frame | Native-frame observation | Decision |
|---:|---|---|
|13|Ask absent12, faint first fade13, clearer14|Receive13 confirmed|
|90|Plus is **on screen**; ring appears90, absent89|Tap90 confirmed. Do not carry forward first-export's replacement panel sound103|
|132|Check In row highlights/ring132, absent131|Tap132 confirmed|
|186|Send-button ring186, absent185|One send186; no separate tap or backspace for composer clear|
|460|Visible second-phone card turns green/Arrived460, locator dot disappears; not yet changed459|One shared semantic arrival confirmation460, not two hits|
|570|Heart first appears570 with send ring, absent569|One send570; no separate tap/backspace|
|615|Heart first appears on first phone615, absent614|Receive615 confirmed|

The first phone is offscreen at460, so simultaneous change on that phone is director-declared, **not independently visible at that instant**. Later dual-phone frames show both arrived. The sound is justified by the visible second-phone confirmation alone and is not duplicated.

## Visible composer insertions

Each row was checked against frame−1/frame/frame+1 in `typing.png`.

| Frame | Before → visible after | Cue |
|---:|---|---|
|325|placeholder → `a`|key325|
|331|`a` → `ar`|key331|
|339|`ar` → `are`|key339|
|356|`are` → `are y`|key356|
|362|`are y` → `are yo`|key362|
|369|`are yo` → `are you`|key369|
|384|`are you` → `are you h`|key384|
|391|`are you h` → `are you ho`|key391|
|397|`are you ho` → `are you hom`|key397|
|406|`are you hom` → `are you home`|key406|
|419|`are you home` → `are you home y`|key419|
|425|`are you home y` → `are you home ye`|key425|
|432|`are you home ye` → `are you home yet`|key432|
|440|`are you home yet` → `are you home yet?`|key440|

Fourteen visible glyph updates, not seventeen physical character events including spaces. Spaces between words do not earn separate sounds without visible composer changes.

## Visible composer deletions

Each row was checked against frame−1/frame/frame+1 in `backspaces.png`; all native frames485–542 were also retained.

| Frame | Visible after deletion | Cue |
|---:|---|---|
|488|`are you home yet`|backspace488|
|491|`are you home ye`|backspace491|
|495|`are you home y`|backspace495|
|498|`are you home`|backspace498|
|505|`are you hom`|backspace505|
|508|`are you ho`|backspace508|
|511|`are you h`|backspace511|
|515|`are you`|backspace515|
|521|`are yo`|backspace521|
|524|`are y`|backspace524|
|528|`are`|backspace528|
|534|`ar`|backspace534|
|538|`a`|backspace538|
|541|empty/iMessage placeholder|backspace541|

## Explicitly silent / adaptation decisions

- No extra key events for trailing spaces or their deletion; no inferred events between listed visible glyph changes.
- Menu/card appearances and camera reveals remain silent. In particular, do not add first-export's camera-reveal receive or an extra panel accent103 after the now-visible tap90.
- Locator progress, clock/countdown changes and end-card/logo animation receive no UI cues.
- One semantic arrival460, not a hit for each card, dot, clock and state change.
- One send186 and one send570. Composer clearing is not backspace.
- The retimed walk210–299 has **zero UI cues**. A separate nonmusical motion texture covers only those90 frames, preserving the restrained T-M8 approach without retaining its old seven-second duration.

## Inspection issue

The initial composer crop reused the old right-phone coordinates and showed background, so it did not verify typing. Changed crop to centered v3 composer `(650,760,1280,850)`, regenerated those two sheets from existing native PNGs, and visually inspected every row. This changed only evidence framing, not an event frame or cue threshold. Native-frame visual verification was performed; no human audio audition or real-time audiovisual playback is claimed.
