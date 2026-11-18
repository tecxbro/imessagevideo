# Hold-out H1 evidence index (anonymized; safe to commit)
The source identity, source hash and frames are deliberately left out. Each arm had a fresh builder, an identical prompt and the same budget; n = 1 per arm.

| Artifact | sha256 |
|---|---|
| A first_export | 8fd92c31f36aa66be1a82047aa21441f905eb50f0c2d6a55478ff2258808aa58 |
| A final | e5387ef3fc51b0b993a207fb63eb562a1bab148ae27abc386691ce0023085d76 |
| A edit | 6384d4bb2a6b7a3cdec898dd2ca33d38766210b66006c88a1d842e9e970ae8a6 |
| A project | 57eac4d4b888d4cac68eb703063877dc338a99074b202605c8436265e49a6fde |
| B first_export | 46c35dd6ba91c159fd5b200c48645b5f407c3937556e31e398ee66548c52bba0 |
| B final | 5233a94de7f9fc341e0a2b4a5a6429d46f61a8da871ae8474370b543f0990b8b |
| B edit | 811ec34a27e8933c3c21cb1e7fe0298a92d4f82209bc8c797a64784aa584417a |
| B project | c0ad163898474d947f7e46046a1af38e32d3ca8bb421209136844daeb29e8c21 |

| Arm | Skill SHA | Wall clock | Review passes | First / final mean MAE | Review-introduced regressions (>5 MAE) | Event gate |
|---|---|---|---|---|---|---|
| A baseline | c49482aec7b8ed0b840f97c61a5e5b860c4077b6 | 26.5 min | 2 | 11.56 / 11.41 | 18 frames | Not run by the A builder. 15 self-reported timestamped defects, 11 fixed. |
| B revised | 013635a457340e7d4b193bbd61a46ef4d0ec45b0 | ~19.5 min | 1 | 13.40 / 13.39 | 1 frame | event_onsets ±2 frames: 88/129 failing at first export, 83/129 at final. 10 self-reported defects, 7 fixed. |

Method: every one of the 778 frames is decoded, scaled to 250×250 RGB, and the mean absolute error to the source is taken. Lower is better.
Verdict: no fidelity gain from the revision.
