# House avatar correction, root contribution

1. Inspected the source and existing neutral reasoning-row helper. The house artwork was authentic, but its parent row's anisotropic transform enlarged it to roughly167px in one axis. It needed an independent world-space pose, not replacement artwork.
2. Kept the original69×68 house asset, source identity and ownership. Measured visible birth at289, continuation through363, and genuine iris occlusion at364. Occlusion is not an inferred opacity fade.
3. Fitted independent position/size/opacity using masked authentic-sprite comparison. The first all-frame fit regressed291 by about.0118 MAE. That state was rejected; the original row artwork is retained exactly at291 and the independent overlay is hidden there.
4. Released apply-root-house-v17.py:apply_house after the neutral row helper, with its measured-world-poses.json payload. Exact changed states are289–290 and292–363,74 total. All74 improve native source error, mean.854686→.676467;288/291/364/365 are pixel-identical controls. All1,286 outside evaluated states are unchanged.
5. Scope, transport and native metrics are retained in outputs/02-danieltian/root-house-v17. The later source owner composed this helper with the other immutable V17 contributions; no contributor overwrote the canonical scene independently.

Lesson: a correct bitmap can still be wrong because its parent camera scales it. Preserve the original at a demonstrably stronger state instead of forcing a uniformly fitted replacement through every frame.
