# Mini and Poke UI cues

These are **visual action manifests**, not extracted audio or a recreated soundtrack. Events are aligned to the accepted GSAP picture used by the audio previews. No music transient was used as evidence.

Files:

- `03-photon-mini.events.json`: accepted Mini v18, 30 fps, 1,260 native frames; 45 events.
- `04-poke.events.json`: accepted Poke v19, 30000/1001 fps, 1,283 native frames; 35 events.
- `03-04-validation.json`: canonical/media hashes, count and timing checks.
- `03-04-extract.py`: repeatable read-only extraction; run from any directory with `python3 /workspace/imessage-recreations/audio-recreation/ui-cues/03-04-extract.py`.

`frame` and `preview_frame` are zero-based accepted-render frames; `time = frame / fps`. Preserve the rational Poke cadence. JSON events contain the requested kind, group, confidence and evidence-layer/source reference. The manifests pin the exact accepted scene, GSAP MP4 and source video hashes.

Mini has 23 observed typing-prefix changes across frames 270–302, adding 27 characters. These come from source-measured native semantic outline states in the accepted Mail editor. Selection appears at 242; the selected 26-character phrase disappears at 268. This is one deletion, not 26 backspaces. A frame that adds `Satu` or `rd` remains one coalesced observation. Caret disappearance at 309 is not a key action.

Poke has 14 observed live-text prefix changes across frames 109–125, adding 30 exposed characters across two lines. Automatic wrapping is not a Return key. The text and its ancestor visibility are evaluated at every native frame; repeated held states do not generate more clicks.

Important measured discrepancy: source Poke selects Zareen’s at frame **633**, but actual accepted encoded GSAP first shows its blue checkmark at **645**. Before/after source and encoded-picture contacts and compact blue-control measurements are retained here. The cue schedules **645**, retains `reference_frame: 633`, and discloses the 12-frame difference. No visual was changed to hide it.

Direct press cues are grounded in pressed/selected material: Mini Mail card 205, food card 605; Poke calendar 232, Indian option press 339, restaurant selection 645. A finger/pointer is not shown. The manifests distinguish these visible confirmation states from speculative physical input. Mini cart numeral changes are `cart_update` events at 674/682/711, not fabricated earlier plus-button taps. Cart control birth at 668 is separate and can remain silent if the update sound is sufficient.

Mini email send is anchored at the accepted dismissal/result transition 354 with medium confidence; the blue arrow exposes no independent measured press state. No extra arrow-click frame is invented. Incoming messages, rich cards, and panel presentation events are secondary and should receive quieter sounds than typing/press/send actions. Avoid stacking a full-volume notification onto every message, panel and associated card.

Static paragraphs, bitmap message/card copy, keyboard legends, composer placeholders, typing-indicator dots, camera transitions, flying `Order!` graphics, marketing card reveals and the end montage do not supply keystroke evidence. They receive no invented typing burst or hidden user clicks. Voice-message appearance is a send event, not a claim about speech or playback-button interaction.

The extraction checks layer lifetimes and opacity through all ancestors. The Poke found-message root begins at 547 but remains below the 1080-pixel frame at 547–548; the audible arrival uses its first coherent onstage body at 549. Reappearing conversation layers and later camera phases are deduplicated, including the found-message reappearance at 664 and selected-card continuation at 734.

Only files with the `03-` / `04-` prefixes in this directory were authored for this task. Canonical scenes, media, music, audio mixes, site files and shared renderers were not modified.

Final encoded-picture spot checks are recorded in `03-04-encoded-action-check.json` and the two `03-accepted-action-contact.jpg` / `04-accepted-action-contact.jpg` sheets. They verify the two Mini card press boundaries, the Mail dismiss/result boundary, the Poke calendar selection, Indian-option first press fade, restaurant selection, and the first map-card reveal through the composer. These are checks of the actual accepted MP4s, in addition to deterministic semantic layer-state validation; they are not a claim that every possible invisible interaction has been recovered.
