# UI trial review ledger

## First exports

- `authored-first.mp4`: 1080×1920, 30 fps, 480 frames; first authored demonstration.
- `observer-first.mp4`: 1080×1920, 30 fps, 810 frames; exact unfamiliar kiln content.
- Both are immutable first exports. Their adjacent scene and audit JSON are the
  measured editable inputs, not screenshot overlays.

## Independent observer findings before revision

The observer reviewed the decoded first kiln movie and reported:

| Finding | Evidence / cause | Changed variable and next check |
| --- | --- | --- |
| U1 major: reaction pills read as the previous message | Around 15s, owner labels floated above the next sender | Use compact emoji/initials badges touching target bubble/card corners; recheck all five owner/target pairs |
| U2 minor: duplicate raw URL | Long URL consumed five extra lines above preview | Keep original input verbatim, omit preview URL from display copy; recheck title/domain and absence of raw path |
| U3 major: camera crop | 11.5–16s zoom clipped avatar column; shell corner intruded around 13.5s | Widen logical framing aperture to 660 and adjust camera pan, retaining 1.6× push; recheck TW avatar and shell boundaries |
| U4 minor: photo proportions unreadable | Back cards reduced to slivers | Spread the three true-ratio rectangles with independent offsets and ratio labels; recheck 0.8, 1.0 and 1.78 |
| U5 minor: emoji too small | Jumbo emoji insufficiently distinct from body copy | Increase 38px to 48px, remeasure and reflow; recheck ZWJ and skin tones |
| U6 scope note: native device/OS unverified | No native measurement recording supplied | Keep explicit authored geometry/timing disclosure; no gesture fidelity claim |

The observer also passed long-token wrapping, composer growth and clearing,
initials avatars, self alignment, reaction retention during header masking and
joined emoji preservation. These are their reported observations, not a claim
of native iOS fidelity.

The revised movie and matching scene/audit preserve the unchanged text,
participants, emoji, colors, photo ratios and sends. Only presentation variables
above changed. A second local check noticed the photo badge still anchored to
the empty layout box, so it was attached to the visible first card corner before
sending the repaired candidate for independent recheck.

## Independent recheck and second repair

The observer rechecked `4f66e33`: U1/U2/U3 fixed, U4 fixed with a regression,
U5 improved; composer passes. Two new defects were reported before retry:

- R1: numerical aspect-ratio labels had become visible debug copy on photos.
  Remove the labels; preserve exact rectangle geometry and ratio data instead.
- R2: the photo reaction badge overlapped the end of the sender name.
  Reserve a separate sender-label line above badges for reacted incoming rows;
  verify vertical separation and recheck the decoded photo interval.
