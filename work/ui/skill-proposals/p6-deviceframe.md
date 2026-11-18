# P6 — DeviceFrame + camera discipline

**Priority 11** (rarely wrong in stills, catastrophic in motion if violated).

## Verified

Screen content is rigidly attached to the hardware through camera transforms
(gallery f330-480 — lock screen, banner, every pixel moves as one); marketing titles and
floating emoji stay world-space. Poke's measured scene splits hardware PNG + screen-mask
PNG; camera keyframes live on `*-camera` parent groups.

## Proposed change to `director/components.mjs`

Add `DeviceFrame` (v2:338) alongside/above `PhoneFrame`:

```js
DeviceFrame({id, x, y, width, height, children, bezel='#0b0b0f', wallpaper='#ffffff'})
// children: -bezel (rounded rect), -screen (clipped group = wallpaper + children),
//           -island (Dynamic Island pill), -home (home bar)
```

`PhoneFrame` remains for viewport-only mockups; `DeviceFrame` for any shot with camera moves.

## Proposed change to `component-contracts.md`

Extend the CameraRig sentence:

> CameraRig moves the parent without rewriting local UI geometry. Screen content lives
> inside DeviceFrame's clipped `-screen` group so hardware and pixels transform as one
> (verified gallery f330-480); world-space props (titles, floating emoji) stay siblings of
> the phone group. Never keyframe screen children during a camera move.
