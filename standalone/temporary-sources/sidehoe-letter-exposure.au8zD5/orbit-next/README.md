# Sidehoe editable project

The verified build uses Python 3.15.2, Pillow 13.0.0, NumPy 2.5.5, FFmpeg
with libx264, and the macOS system typeface and Apple Color Emoji.
The renderer falls back to bundled Inter for the system typeface when
the macOS font is unavailable. Set `SIDEHOE_EMOJI_FONT` to a compatible font path
when the default macOS path differs. Run from the project directory.

```sh
python3.15 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHON=.venv/bin/python bash export.sh exports /tmp/sidehoe-png
```

`scene.json` holds copy, independently drawn portrait parameters, palette, zero-based events, camera and cursor keyframes, appointment time slots, and score notes. y points downward. Stage geometry is 1000 × 1000, doubled on encode. Frame 0 starts at zero and 25 fps is exact. Tracks linearly interpolate between absolute frame indices. The Pillow stage redraws each frame from its absolute index. Change a string or track entry and render with `render.py --cache … --frames START:END` for a partial preview. `export.sh … --reuse-cache` re-encodes an already complete cache.

`render.py` draws the UI, plates and choreography. `artwork.py` provides independently authored app tiles, badges, inline pictograms and portrait placements. The selected generated heads are individual transparent PNGs under `assets/portraits`. Their color disks, scale, positions, masks and animation remain editable. `sound.py` synthesizes editable stereo score and Foley separately, plus the mix and the frame-to-audio-sample event map. Rendering uses the bundled code, font and head sprites alongside the local system fonts.

- Font. Inter variable font by Rasmus Andersson and contributors, SIL Open Font License 1.1. `assets/Inter-OFL.txt` contains the license. [Upstream font directory](https://github.com/google/fonts/tree/main/ofl/inter)
- Other visuals. Independently authored Pillow geometry for the hardware, interface and brand mark. Generated portrait sprites are guided by the supplied character reference. The reference film and evidence are separate from this project.
- Audio. Original synthesizer score and procedural Foley from `sound.py`. Event timing follows the observed visual beats. No audio samples are loaded.

The follow-up cursor uses `followPointerStage` from f670 through its
exit. Position, footprint, defocus and opacity are in stage coordinates.
`followLeadIn` holds the descent, rotation and sweep from the first
visible blur at f625 through f669.
`followPointerLean` controls the change in silhouette as it approaches.
`followYesRegistration` and `followYesInkBounds` hold the separate
control in phone coordinates.
`handsetRailLight` controls the bevel reflection, exit taper and softness.
`calendarTileTreatment` controls the blue tile's stage offset, coverage,
material blend, blur and aspect ratio. `calendarTileShutter` starts the
vertical exposure as the tile exits. Its cyan cap, pinched blue face and
two numerals are drawn independently in `treatments.py`. The other motion
keys remain editable in `scene.json`.

The handset reveal has separate tracks for outer pose, bevel depth,
camera island, pinned contacts, lens ripple and colored light.
`inboxChromePose` tracks the pins independently of the transcript rows.
`sofiaRelease` controls the phone interior and hardware during the
handoff. `personalHearts` sets each heart's pose and opacity. The export
flags preserve the stage's neutral paper color through encoding.

`sofiaPlateRegistration` controls the offsets for the chat history and
header and the direction of the shutter trail during the push. The
keyboard and outer handset follow their own measured tracks.
`sofiaHistorySettle`, `sofiaSuggestionInk` and `sofiaSettledControls`
set the positions of the history, captions and buttons as the push settles.
`sofiaBezelControls` sets the hardware button spans during that move.
`sendExitExposure` controls the outgoing suggestion's blur.
`sendPointerStage` controls the Send cursor's visible tip, hull, blur,
opacity and lean on the film clock.
`calendarDateExposure` and `calendarAppointmentExposure` track the
incoming date marker and two appointment bars independently.
`followBodyRegistration` registers the follow-up handset's separate
horizontal and vertical dimensions and the keyboard row boundary.
`followRailAperture` sets the two bevel widths and exposure on the
next part of the camera move.

The reply and suggestion have separate stage-coordinate tracks as the interface detaches. The calendar marker and right grid edge are independent tracks. The portrait disks and app tiles have individual poses. Each closing word has its own visible ink box and opacity. The two title washes use editable field tracks with center, falloff, shear and RGB amount for each light. `scene.json` records the measured landmarks and the interpolation used in the render.

The [calibration report](../README.md) documents the source and final
comparison.

The handset reveal uses `assistantLettering1` and `assistantLettering2`
for the moving letter forms. Each reading is a stage rectangle, opacity,
vertical shear, reveal edge and focus. `assistantPinControls` and
`assistantRowPose` move the pinned contacts and first message row.
`assistantBodyFocus` sets the handset softness. The two
`assistantWashResponse` values change how much light reaches dark artwork
while keeping the measured paper tint. `assistantPrism` holds the rim
refraction paths at the two visible entrance frames.

`personalLettering` supplies the two title lines' bounds, color and focus.
`personalHearts` holds each heart's position, size, angle and opacity.
The profile badge's three cards and shaded heart are drawn in `artwork.py`.
`closingMeasuredBox` and the six `closingInk-*` tracks hold the settled
badge and words through `endingFade`.

`calendarGridRegistration` moves the calendar's time labels independently
of the appointments. `calendarEntryPointer` sets the arriving tip's
position, angle, size, opacity and spread on both axes.

`threadRegistration` supplies the two close-ups with screen bounds, keyboard
rows, messages and exposed rail shading in stage coordinates. The dialogue
and control captions come from the same `copy` fields as the other frames.
`sendDepartureInk` places each line of the departing messages inside its
measured bubble. `clusterRegisteredWipe` moves the existing portrait actors
behind rectangular cuts during the wipe.

`assistantEntranceOptics` registers both casing contours, both lower
rail reflections, the optical distortion of the Messages heading, and
the incoming Sidehoe pin at f134–137. Its rail knots hold the stage-relative
row and the observed and authored outer and inner x positions for each
side. The renderer evaluates the contours around the editable handset.
`calendarHandoff` sets the time-label position, blur, shutter length and
opacity, plus the two appointment bars' left and right bounds and vertical
offset at f401–412. The outgoing bubbles retain independent bounds and
follow `sendExitExposure`.

The screen registration also covers the Sofia pullback at f352–354 and
the follow-up move at f660–671. It tracks screen edges, bubble and ink
bounds, the keyboard tray and key rows in stage coordinates. The
pointer continues to follow the independent `followLeadIn` and
`followPointerStage` tracks as the framing changes.

`personalWordRegistration` holds the measured box, weight, focus and
coverage for each word of the two editable captions from f186 through
f206. Caption edits with a different word count use the original line
layout. The hearts keep their own position, angle and opacity tracks.

`calendarTileFinish` controls the blue cheek, lower face shading and
numeral strokes as separate treatments on the existing tile motion.
`followPointerOptics` sets the arrow tip, outline dimensions, blur on
both axes, opacity and skew on each frame from f670 through f695.

`closingBadgeShape` stores the fit to the four moving badge edges and
corner rounding. `closingBadgeFinish` controls the separate upper
reflection. The three cards and heart are editable paths in `artwork.py`.

The Sofia screen registration at f337–341 measures both rails, the top
outgoing message and the visible keyboard rows during the push. The
additional focus controls keep the diagonal exposure separate from the
screen geometry. The follow-up screen applies its early defocus once.

`sendHandoffControls` stores independent positions for No and Send? as
the conversation travels upward. `calendarBarShutter` stores the two
appointment bars' positions, leading and trailing blur widths, and
pigments. The bar labels and the grid are separate editable layers.

`sendControlInk` holds each control's editable text bounds on the same
clock. Its coordinates are relative to the button being drawn.

The portrait cluster uses measured disk contours and independent head
placements at f218–253. `clusterDiskContours` stores the ellipse,
opacity and optional head bounds for each actor. `clusterShellContours`
stores the outer points of the shared lavender surround. The renderer
shades inward from those editable paths. The existing wipe carries that
plate into the first four transition frames.

`profileRegistrations` registers the disks, the top-to-bottom color
stops, each head, the name, and the interest-chip artwork at f271–286.
The names and interest text come from the editable profile records.
Lisa uses the existing wink asset in this passage. The three interest
icons load through the declared local emoji font.

`sofiaEarlyOptics` sets the casing position, horizontal and vertical
scale, shutter spread, coverage, and the widths of both rails and the
lower bevel at f314–319. The independently drawn Messages screen follows
the observed camera move. `sofiaHomeIndicator` holds the visible bar's
center, width, height, focus, and contrast through f330.

`followSettledRegistration` maps the contact badge, status cutout,
header boundary, editable conversation, composer, keyboard rows and home
indicator independently at f631–659. Coordinates are in the local
handset plane. Its optional camera values set the measured handset
position and aspect before the push. The outgoing bubble's stops set
color across its vertical gradient. The adjacent stage-space cursor
track sets tip, rotation, scale, shutter spread and opacity per frame.

`personalGlyphRegistration` sets each editable glyph's box, focus,
and opacity over the title move at f186–206. It uses the current word
weight and font. Changing the title copy restores the existing word
or line layout for that caption. `titleHeartOptics` moves the
independently drawn hearts over the same span with separate position,
scale, angle, coverage, shear, and focus controls.

`profileMotionRegistration` carries the independent pose, focus,
caption and chip geometry from f267–270 and f287–312. The retreating
portrait has separate head coverage, side fade, and color wash.
The closing follow-up shot uses `threadRegistration.follow` at f694–695
for the history, keyboard, visible header, controls and the casing's
blended edge profiles. Its arrow follows `followPointerOptics`.

`calendarTileProfiles` sets the stroke and fold adjustment and the surface
defocus at f603–619. `calendarTileTreatment` still controls its vertical
position, height and shutter smear. The numerals and blue face are editable
in `treatments.py`.

The follow-up push uses `threadRegistration.follow` to set the handset
and header at f660–664. The rail blend follows the rounded ends, and the
screen layers use the handset's silhouette as their mask. The keyboard
utility row and visible footer use stage coordinates. The focus entry
adjusts the screen independently of the casing and cursor.

`threadRegistration.sofia` registers the bubbles, casing, composer and
keyboard as the handset pushes in at f329–339. Through f336, the casing
has its own pose and exposure settings. Its interior glass mask clips
the separately softened screen. Before the suggestion appears, the
already visible reply uses `earlierReply` for the shape and editable ink.

`personalGlyphRegistration` accepts a seventh value for the glyph's
font weight. The heart placement and focus stay in `titleHeartOptics`.
`closingMotifFit` adjusts the finishing treatment of the badge's card
contours, face and heart during its arrival. The independent paths and
gradient stops are in `artwork.py`.

`assistantLighting` and `assistantWashResponse` control the pink light
on the paper and dark hardware. `assistantScreenRegistration` supplies
the camera cutout's shade and shape at f155–161. The right-side samples
in `assistantSideBevels` adjust its visible edge and reflection.
`assistantCaptionOptics` sets the two editable lines' downward motion
and directional focus as the handset departs.

`followEntryOptics` gives the casing and glass different focus and
exposure lengths from f624 through f630. The existing measured camera
and `followSettledRegistration` supply the handset shape, bubble
positions and keyboard rows through the entrance.

`redOrbit` and `blueOrbit` include stage-relative readings across the
turn from f518 through f544. The editable calendar face treatment
and its later exit use the same controls described above.

`inboxScrollRegistration` supplies the visible pinned header, unread
dots, contact disks, row copy, timestamps and home indicator at f42–101.
The header moves independently of the conversation list. Copy and
emoji tokens still resolve through `inboxRows`. The two small row
portraits use independently drawn paths in `artwork.py`, selected by
`inboxCompactPortraits`.

During the glossy reveal at f134–140, the camera island and the first
inbox row have separate tracks. The opening badge and the upper and
lower reflections use the controls in `assistantEntranceOptics`.
The same casing and pinned contact layers remain editable.

At f0–9, `inboxIntroRegistration` sets the position, focus and opacity
of each status and navigation element, the pinned contacts, the note,
and the first two conversation rows. The note text comes from
`copy.pinNote`. The transcript rows still use `inboxRows`.

At f314–328, the Sofia entrance uses `sofiaMeasuredCamera` and
`sofiaEarlyOptics`. From f319, `threadRegistration.sofia` places the
editable conversation, composer and keyboard on the screen separately
from the casing. The home indicator has its own bounds.

`calendarNumeralRegistration` controls the position, vertical scale
and stroke weight of the vector “31” as the tile exits.
`calendarFinishExposure` adjusts the reflection at the upper shoulder
and fold independently of the numerals. In `followPointerContour`,
the normalized vertices describe the arrow's flag and stem.
`followPointerOptics` applies the tip position and focus on the film clock.

From f134–161, `assistantRimRegistration` adjusts the thickness and
position of the upper rim and side rails. Each section stores the
position along the edge, the center of the cross-section, its offset
and its change in width. The handset and rim still come from editable
geometry. `assistantVeilRegistration` sets the color fields on the glass
and their strength on dark hardware independently.

The optional final three values in a `titleHeartOptics` pose set that
heart's red, green and blue. The closing badge's rear shoulders are
Bézier curves in `artwork.py`. The calendar tile's exposure during its
exit uses `calendarTileTreatment` and `calendarTileShutter`.

`assistantIslandRegistration` holds the camera cutout's shape,
the sensor insert and the lens reflections as separate editable
elements in stage coordinates. `assistantRailRefraction` casts the
lower colored flare after the two handset rails have moved.
`assistantRowRegistration` gives Natalie’s portrait, name, preview,
timestamp and chevron individual offsets and opacity.

The first reply during the follow-up uses the bounds, corners, ink
boxes and optional `bubbleFill` values in `threadRegistration.follow`.
The wording still comes from `copy.follow`. At the closing badge,
`closingBadgeRasterWidth` controls the resolution of the editable
artwork before applying its camera transform.

At Sofia’s close-up, `sofiaSuggestionRegistration` gives the two blue
bubbles and the No and Send? controls separate contours, colors and
text positions. Their copy comes from `copy.sofia`. The incoming lines
in `threadRegistration` can use `inkAppearance` to specify position,
font weight, color and focus. The follow-up’s `blueGradient` samples
describe the editable outgoing bubble’s vertical light falloff.

`inboxHeldRegistration` places each pinned face inside its own
independently lit disk at f10–41. The same records hold the name and
note bounds, note shadow, unread dots, conversation previews and times.
The note and conversations take their text from `copy.pinNote` and
`inboxRows`. Sofia's entrance at f319–328 uses `focus` and `keys`
in `threadRegistration.sofia` for the screen exposure and keyboard
tray color.

During the profile reveal at f260–270, each actor in
`profileMotionRegistration` has its own disk, head bounds, and focus.
The same actor record holds the name, tag, and emoji positions. The
optional character counts control how much text is visible, using
the editable names and tags in `profiles`.

`followSettledRegistration` holds the handset camera before the
follow-up choice. Its `preContactExposure` values are vertical
exposure length, horizontal softness, and vertical softness.

## Follow-up close-up and casing

In `threadRegistration.follow`, `blueInkAppearance` and `inkAppearance`
set the two outgoing lines and the incoming reply. Edit the words in
`copy.follow`. Composer, key faces, response controls and their glyphs
each have their own stage poses. `edgeRamps` set the rail light profile.
`railHardware` defines each side button's vertical extent, edge focus
and luminance difference from the adjoining rail. `followPointerOptics`
keeps the pointer separate and editable through the hold. The named Yes
contact and its 48 kHz cue stay at frame 675.

The earlier Sofia push uses `casingAspect` and `pushCamera` in
`threadRegistration.sofia` to register the handset and mask together.
`followSettledRegistration` adjusts the pre-contact handset corners,
header and composer through f650–659.

## Sofia’s handoff and closing title

`sofiaSuggestionRegistration` specifies the two blue bubbles, editable
lettering, response controls and separate optical focus through the handoff
at f352–359. The camera and screen retain their own motion. Edit the
suggestion in `copy.sofia` and the release header in `copy.follow`.
The departing follow-up handset has an editable header label, badge
smear and control poses in `threadRegistration.follow`, at f694–695.

`closingInkAppearance` sets per-word fit, weight and focus for the closing
text. Edit display copy in `copy.ending` and timing in the existing named
events and `closingInk-*` tracks. The paper lighting comes from two editable
fields in `closingWashFields`. `endingFade` controls the final exposure.

## Inbox scroll, assistant reveal and calendar wipe

The inbox's `rowExposure` and `chromeExposure` values give the scrolling
message rows and the pinned strip their own focus and offset in
`inboxScrollRegistration`. The existing conversation and actors
supply the visible copy and portraits.

On the rising handset, the words in `copy.assistant` use
`assistantCaptionReveal` for the visible width, lean and exposure.
`assistantIslandRegistration` holds the opening, inset sensor, lens
reflections and separate reflections on the surrounding glass.
`assistantScreenRegistration` supplies the pin face poses and disk
lighting. The source frames are outside the render inputs.

`calendarDeparture` holds the appointment boundaries, grid segments,
day marker and white wipe cells through f473–477. The calendar still
uses `copy.calendar` for the appointment captions. The cursor fades
as it leaves the schedule during the wipe.

## Follow-up handset and first orbit tiles

The assembled follow-up handset uses its existing camera track through
f630–659. `followSettledRegistration` holds independently editable bubble
ink, composer bounds, key faces, control poses, and case lighting.
The case uses separate light profiles for the four straight edges and a
separate side-button exposure. The No and Yes poses retain their named
reveal frames.

`followCameraWarp` describes the optical deformation during f660–670.
Its two coordinate lists define the mesh. Each row of offsets is in
stage pixels. The renderer applies the warp to the handset assembly
before drawing the separately timed cursor.

At the calendar handoff, `calendarDeparture` gives the remaining
appointment cells their own masks and specifies which part passes
in front of the ring tile. `orbitArrivalExposure` stores app-tile
position, size, coverage and focus through f478–482.

## Assistant handset optics and Sofia close-up

The assistant handset at frames 134–137 uses separate generated elements for
the brand artwork, status glyphs, Messages controls, and portrait disks.
In `scene.json`, `assistantScreenRegistration.badgeCalibration` controls the
badge pose, central motif scale, fringe, and light. The optional
`assistantScreenRefraction` entries define a stage-space crop and affine,
chromatic, contrast, and focus values for each UI control.
`assistantControlCaustics` entries place colored lobes along an editable ellipse.
Copy and glyphs come from the authored Messages layer.

The Sofia close-up at frames 343–351 uses `threadRegistration.sofia` for
the edge ramps, hardware, composer, and keyboard registration. Composer and
keyboard shapes and text render from their respective layers.

## Handset exit and closing badge outline

Between frames 153 and 161, `assistantExitCasing` supplies independent
rounded outlines for the metal shell and the opening where it meets
the glass. Each contour has a center x, top y, width and horizontal
and vertical shoulder radii in stage pixels. The light ramps are
evaluated across the depth of the casing and interpolated from left
to right. The status and Messages glyphs use separate
`assistantScreenRefraction` windows. Optional final values control the
distance between the two shutter-weighted exposures and their blend.

`closingBadgeOutline` defines the outer rounded shape at frames 701–711.
The three cards, their ink, and the heart are generated separately from
that outline.

## Handset hold, keyboard withdrawal, and closing artwork

The measured casing shoulders now reach back to frame 139. The
`assistantSpeakerSlot` track adds a machined recess and reflected lip
on the casing before the screen-space effects render. The slot's
position, size, falloff, and two RGB ramps are editable in stage pixels.

Frames 691–693 use measured `keyPoses` in `threadRegistration.follow`.
Each entry provides a white key face and a separate glyph rectangle.
The screen's horizontal shutter sweep, vertical sweep, and focus
are resolved separately across frames 690–695.

`closingBadgeArtwork` registers the left card, right card, center card,
and heart separately inside the badge. Each pose defines x and y offset
in the 512-pixel artwork coordinate system, then horizontal and vertical
scale. The closing badge still has an independent `closingBadgeOutline`.

## Glass clearance and key-specific withdrawal exposure

The optional `assistantCasingGlass` samples control how quickly the
casing material falls away inside the glass, across the center of the
handset. The shoulder outline and speaker slot remain editable separately.

In frames 691–695, `threadRegistration.follow.keyInkRegistration` gives
each drawn letter its own center, size, shear on both axes, shutter
direction, focus, and coverage. Key faces and their shadows use
`keyPoses`, independently from the letters. The camera shutter for
the rest of the Messages screen still uses the frame's separate focus
and exposure controls.
