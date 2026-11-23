# Linq V18 measurement notes

This is a readable companion to the complete `steps-rebuild.md` log. The immutable V17 master remains the production baseline until the parent merges all V18 helpers and completes the final encoded source gate. Local native-frame results below are not full-timeline scores.

## Jewelry document and background

1. Inspect the native V17 error peak at frame 587. The source already shows the upper Jewelry UI and necklaces; the recreation is still entering from below.
2. Inspect the actual static document. It begins at an already-scrolled source 600 crop and omits about 421 pixels of upper UI. Three camera samples also fell into partial-white local minima: 584/585 and 587.
3. Register one bounded upper UI crop from frame 581 against the existing lower document. The measured offset is 421.417578 pixels. Keep a native rounded document clip, independent camera and fixed viewport; retain the accepted foreground from frame 600 onward.
4. Use the handle and complete product shapes as independent camera anchors. The actual top moves from 391.52 to −421.52 through frames 578–599.
5. Inspect the first candidate. Remove four exterior crop columns containing source background, using white outside the UI art and the independently native rounded clip for its silhouette.
6. Diagnose the missing gray link card behind the app. Background59 had frozen the same failed frame 578 fit at Y685.98 and opacity.055 instead of the valid near-Y291 state. Restore the original native thread components and measure blur/white wash against an independently rendered native template.
7. Reject a two-component-opacity experiment: its error reduction is negligible. Keep the simpler measured background model.
8. Check every affected native frame. All 73 frames 578–650 improve; local mean MAE falls1.934108→1.031196. Controls 577/651 are pixel-identical; all 1,385 outside active SVG states are identical.

Frozen release: `jewelry-v18-release.json`. The upper UI is one static bounded bitmap with provenance, not a source-frame sequence. Its internal text remains bitmap; outer camera and clipping are native.

## Foodash camera and Dillion label

1. Inspect the native frame 1031 peak and the actual camera data. The icon-height detector quantizes the whole document scale in 1/38 increments. Stable header/body supports confirm that some jumps are false.
2. Fit native document X/Y/SX/SY against the original static UI, excluding the changing Dillion and subtotal rows. Validate with the native browser renderer, not only the fitting loss.
3. Retain stronger original poses, including camera 1032/1033 and 1056 onward. Reject an isolated .016 MAE gain at 1057 as insufficient evidence. Accept54 camera states in 1000–1031/1034–1055.
4. Inspect the doubled Dillion name. The initial row was normalized with an inaccurate old camera, placing its word six pixels below the final row. Whole-row fading therefore doubles a label that should be a single solid word.
5. Reject a constant-label support fix: it helps the update but fails frame 1020. Expand independent word measurement to the complete entrance/update window.
6. Add one original native outlined word with semantic text, an independently measured pose, and a native paper mask over both bitmap names. Preserve every original product, price and subtotal asset and state curve. Keep word opacity solid.
7. Calibrate against the actual native path rendered at 4× resolution with pixel-coverage integration. A source raster template is not the same fitting model as a final outlined vector.
8. End the override at frame 1035, exactly when the original initial-row opacity reaches zero. The accepted settled label then supplies the word naturally.
9. Inspect native images even after the scalar gate improves. A white 255 paper mask was visibly different from the UI's measured dominant 252 paper. Correct both native fill and calibration model to #fcfcfc.
10. Check every affected native frame. All 58 frames 998–1055 improve; local mean MAE falls2.456299→1.487562. All 37 independent-name frames also improve against the camera-only candidate. Controls 997/1056 are pixel-identical; all 1,400 outside states are identical.

Frozen release: `foodash-v18-release.json`. Only `rich-group-12` changes. Other original roots, original UI artworks and dynamic product/price/subtotal content/state remain identical.

## A cached-frame failure

An all-frame lossless GSAP/Remotion comparison revealed one inherited Remotion frame 625 truncation missed by sparse verification. A fresh immutable V17 Remotion capture matches GSAP exactly. Archive the defective and fresh PNGs; the original failure cause is unproven. Explicitly recapture 625 in the next production refresh and check it again. The jewelry578–650 range already includes it.

## Production gate

Merge the released helpers with the parent's Games and boarding patches by their reserved IDs. Freeze a new immutable scene. Refresh each method from its actual cache revision using the union of all changes since that revision. Encode using the validated full-range BT.709 profile, verify cache hashes/cadence/dimensions, scan every aligned source frame, inspect separated native peaks, and compare the independently rendered method caches. Record nonzero residuals and actual scene hashes; never turn MAE into a perfection percentage.
