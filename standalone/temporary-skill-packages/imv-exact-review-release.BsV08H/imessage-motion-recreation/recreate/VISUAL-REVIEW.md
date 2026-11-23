# Visual review for recreation

Match the reference's composition, type, color, materials, depth, lighting,
optics and transitions wherever the authorized scope permits. A supplied asset
may have an independent substitute. Preserve how it reads in the shot and
document any visible difference. Obtain the user's agreement before changing
the visual target. Keep evidence images and the reference movie and audio out
of the render inputs.

## Measure before building a shot

For Messages and handset shots, use the
[native interface measurements](UI-FIDELITY.md) for bubbles, keyboard, casing,
status and composer icons, glyphs, emoji, color and motion. Assign a separate
criterion and region to each visible component and state.

Use one ledger for the entire cut. For each shot, record its inclusive source
frame range, output frame mapping, native comparison crops and the observable
criteria for a pass. Cite decoded source frames at entry, a representative
moving or most changed pose, and settlement. Include both sides of cuts and
sample fast changes consecutively. Record numerical targets and tolerances
where the source supports measurement. Capture the following wherever visible.
Save the [review plan](COMPLETION.md#lock-and-verify-the-review) before authoring
or changing a repair baseline.

| Feature | Measurements and evidence |
| --- | --- |
| Layout and type | Frame and object bounds, relative spacing, clipping, exact copy and wrap, text ink bounds, baselines, weight and visible glyphs. |
| Camera and interaction | Independent landmarks across the full span of a moving surface, plus separately moving features. For a calendar, track both grid edges and the day marker. For a pointer, track its tip against the moving target's bounds through approach, contact and release. |
| Color, light and materials | Color samples across foreground and background, including gradient placement, falloff and coverage at key frames. Measure features such as bezel thickness, edge highlights, reflection shape and portrait scale, silhouette and apparent depth. |
| Masks and optics | Mask bounds, layer order, occlusion, and reveal timing. Track each rectangle and its reveal order in a staggered wipe. Sample visible blur extent and direction, fringe width and color, and apparent opacity as they change. |

Flag estimates and obscured features with their evidence. Where the underlying
parameter is ambiguous, check the observable result, such as the composited RGB
at named points. A qualitative criterion should describe a visible property
that a reviewer can confirm or reject. Measure both independently visible edges
before inferring a width or tracking a child feature with a parent transform.

Batch reference decoding for the planned shot windows. Keep the reference
frames, accepted measurements and probe frame map available for later passes.
When parts move differently, measure separate bounds for those parts at the
same frames. A passing camera or group transform can still leave a child
misplaced. Confirm a fitted track at a moving frame between its anchors.
Fit editable lighting controls from unobstructed patches at multiple shot
phases. Verify intervening frames and sample foreground edges separately.

When a moving panel is cropped, measure the visible side edges for horizontal
position and scale. Track an interior landmark for vertical registration as
the top or bottom goes out of frame. Record which landmark supplies each axis
and check the handoff across consecutive frames. Use a second interior feature
to test the fit. If that feature drifts while the first stays aligned, give the
drifting feature a local track. During a press, derive the pointer's target
from the evaluated control bounds on each frame and check the tip separately
as it arrives and leaves.

For repeated rows or tiles, label at least two identifiable features before
tracking. A spacing match can be one row off during a fast scroll. Check the
order and identity on both sides of the fastest frames. When text reveals
word by word, measure each word in the range where it is visible. An ink box
around a partial line gives the width of the visible text at that instant.

For each cut or transition, list what is already visible on its first frame,
what enters later and what remains from the outgoing shot. Record the last
absent, first visible and first settled frame of each consequential element.
Attach separate source measurements to the camera, independently moving layers,
text reveals, masks and lighting when they change at different rates. A pose
copied from the end of the shot only establishes its held appearance.

## Review decoded probes before the first full render

Decode a representative in-context still from an export of each shot and
compare it at native scale and intended viewing size. Review important assets
in their actual framing, scale, lighting and masks. Choose the authoring method
that passes that review.
Editable geometry suits text and controls. Independently made raster or 3D
assets can supply dimensional portraits and reflective hardware. Use generated
assets when authorized and retain their provenance and editable placement.
For faces or other recognizable assets, compare silhouette, expression and
lighting in the actual shot before investing in animation. Use the supplied
visual evidence to guide asset generation when the approved workflow permits it.

Export a short passage for each distinct visual treatment that changes over
time and for each materially different interaction or transition the renderer
has to handle. Reuse a probe when shots share the same treatment and behavior,
and cite the applicable frames in each shot's ledger. Probe the hardest
passage first. Use the intended renderer, resolution, fonts, effects, color
and encoding path. Decode consecutive frames from before onset through
settlement and compare aligned full frames and native crops. Save the command,
export and source-to-probe frame map. Check the measured targets and verify
that the layers and timing still support the required edits.
For optical blur, review masked edges over the final background. Test
premultiplied alpha if the decoded export shows dark halos around translucent
layers. Leave enough transparent space for the full blur streak and for
rotation around an off-center pivot. Compare the complete silhouette at the
most extreme angle. Sample a lighting effect on a blank surface and across a
dark edge. Fit opacity and color separately when the source lifts the dark
edge as well as tinting the surface.

Compare consecutive frames at shot boundaries and during the fastest motion.
Check the visible onset against the source before using an event as a pass. A
fade keyed at the first visible frame can still render zero opacity there.
Check both entry and exit, even when the shot uses a previously accepted rig.
For a transition with multiple elements, compare their individual order of
appearance, trajectories and occlusion before fitting a shared motion curve.

For a revision, state the failed criterion and the scene property being
changed. Rerender only affected windows, including any other shots that share
the changed component or material. Carry forward verified evidence for inputs
that stayed identical. Where several shots share a miss, fix the shared cause
before tuning individual frames.

Record **Pass**, **Fail** or **Unverified** per shot with the relevant stills,
probe frames and observed differences. Proceed to the full recreation export
once every shot passes and the [comparison limits are calibrated](CHECKS.md#calibrate-for-the-shot-review).
Resolve failures in the asset, scene or renderer and repeat the affected probes.
If a target remains out of reach, report the affected shots and evidence.
Record any user-approved scope change and review against that target before
proceeding.

When the user requests a complete benchmark export despite probe failures,
record the failing shots first and label the export as a benchmark. Review
every decoded shot of that export against the original criteria. For a request
to finish the recreation, keep working through the open checks after a
benchmark export. Use the [repair loop and completion check](COMPLETION.md).

## Review the finished export

Repeat the shot review against the decoded full export, including the ending.
Use `prepare-review` on the decoded comparison to get the tasks, then open
the linked native crops and adjacent-frame evidence yourself. Start with the
flagged tasks. Step consecutive source and candidate frames, use full-cut
playback to judge apparent motion, and record the concrete observation for each
check you viewed. Leave unseen checks unanswered. The
[frame pair viewer](CHECKS.md#browse-aligned-frame-pairs) is for full-frame
context. Use the PNG evidence to judge tiny features. If a crop shows a miss,
record the component and first failing frame, even if its interaction landed.

For each failure, record the frame range, region, expected and observed result,
and the governing source measurement and scene property. Compare the editable
scene or lossless frame against the encoded frame when you suspect export.
Identify whether a measurement was missing, the scene failed to follow a
known measurement, the asset was different, or the encoder changed the result.
Keep a hypothesis labeled until a focused repair or isolation run tests it.
Pair evidence and a repair test with each affected shot. Recheck adjacent
states and any shot that shares the repaired element.

Use the decoded pixel and motion errors to locate differences. A cross-shot
average, matching clock or passing end state leaves local failures open.
For a one-to-one request, any differing decoded pixel or timestamp fails
acceptance, even if all manual observations pass. Retest the failure against
the revised exported file and keep repairing the open items.

## Review references

HyperFrames ranks local failures and exposes motion, runtime and layout checks
with per-finding screenshots. Its reverse workflow matches cuts and inspects
consecutive crops for changing text and effects.
[HyperFrames diff command](https://github.com/heygen-com/hyperframes/blob/de63e9731196d1cdf62bf57bc064f15a2d31c4a0/packages/cli/src/commands/diff.ts)
· [HyperFrames review workflow](https://github.com/heygen-com/hyperframes/blob/de63e9731196d1cdf62bf57bc064f15a2d31c4a0/skills/hyperframes-cli/references/lint-validate-inspect.md)
· [Reverse-video matching](https://github.com/heygen-com/hyperframes/blob/de63e9731196d1cdf62bf57bc064f15a2d31c4a0/skills/reverse-any-video/references/match.md)

REA Video generates per-shot review tasks with images, identifies high-priority
items and keeps unanswered observations open. This skill uses that review
pattern on source and export crops.
[REA Video review implementation](https://github.com/JuneYaooo/rea-video/blob/4d98dd8dd1838edfa58037cf4df9d1cccc245da7/rea_video/review.py)
