# 01-photonhq reference analysis

Actual downloaded source: **1920×1080, 30/1 fps, 655 frames, 21.833333 seconds video**. Audio and container durations are slightly longer. All inspected scenes are motion graphics, so the full video is in the requested scope.

The original MP4 and raw metadata are preserved. `contact-*.jpg` show every whole second with a timestamp and frame index. `keyframes/` holds selected full-resolution frames. `scenes.json` is an implementation handoff; its initial scene boundaries are approximate, not certified exact cuts.

## Visual breakdown

| Approximate interval | Scene | Observed content and behavior |
|---|---|---|
| 0.00–1.45s | Introducing Photon 2.0 | Centered black headline; Photon 2.0 cyan/blue gradient. Scale pulse while holding. Dense typography around 105px at full stage. |
| 1.45–3.15s | Blue pill / cursor / With just one click | Rounded glossy cyan pill appears center, black arrow cursor moves/clicks; title enters at right while pill shrinks/slides left. |
| 3.15–4.45s | With just one click | Pill exits left, black centered phrase holds. |
| 4.45–6.85s | Your agent is everywhere | Centered phrase then replaces with vertical channels list: iMessage, Whatsapp, Telegram, SMS, Email, Phone. Matching colored application icons; stack scrolls vertically. |
| 6.85–8.50s | And it’s free for everyone. | Black centered line; free in cyan. |
| 8.50–9.65s | 10,000+ SMS | Rows of bright green/gray SMS bubbles slide horizontally above and below centered black heading. |
| 9.65–10.65s | 100,000+ emails | Rounded notification cards with avatars and logos form scrolling rows above/below heading. |
| 10.65–11.65s | 8000+ voice minutes | Black call strips with avatar, green duration, white name, speaker and red hangup icons. |
| 11.65–12.95s | Unlimited iMessage | Blue/gray tailed message bubbles arranged horizontally. Text remains centered in white gap. |
| 12.95–14.35s | Unlimited WhatsApp | Green/gray angular message bubbles with subtle timestamps/checkmarks; continuous lateral flow. |
| 14.35–15.65s | Unlimited Telegram | Pale blue/gray message bubbles; timestamps; lateral flow. |
| 15.65–16.85s | Even 10DLC registration | Black centered title and green verification badge. |
| 16.85–17.45s | On us. | Short centered black line. |
| 17.45–19.65s | Try it today at / photon.codes/beta | Two centered lines; URL cyan; blur/wipe reveal on URL. |
| 19.65–21.83s | Photon logo | Three black leaning lozenges on white; centered mark. |

## Fidelity dependencies

- Typography family is not established by metadata. It resembles SF Pro/Inter; measure glyph widths and use matching licensed fonts rather than assume an exact family.
- Reuse original branded assets where obtainable, then reconstruct editable geometry and timing. Do not pass a reference video through an output container and call it a recreation.
- Full-resolution reference frames and temporal samples are needed for geometry and easing; a one-second contact sheet cannot verify spring curves or transition start frames.
- White stage and native Messages blue/gray/green imagery dominate. Rich-link photo in source 02 is an embedded graphic asset, not live action.

## Measured palette

{
  "background": "#FFFFFF",
  "background_measurement": "Most frequent RGB pixel on multiple full-resolution decoded frames",
  "black_text": "#000000",
  "font_family": "Unverified SF Pro / Inter-like sans-serif",
  "source_dimensions": [
    1920,
    1080
  ],
  "source_fps": 30
}

## Timing refinement

Quarter-second contact sheets (`quarter-contact-*.jpg`) were inspected end-to-end. `scenes.json` now contains the refined boundaries and additional branding details; it supersedes the initial table above. Exact per-frame easing remains to be measured. The source first decoded frame is a fully composed title, followed by an intro reset within ~0.1s. Treat that artifact separately from intended reveal motion.
