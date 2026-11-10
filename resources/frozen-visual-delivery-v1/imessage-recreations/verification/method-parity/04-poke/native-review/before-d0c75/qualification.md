Current Poke Motion Canvas review is bound to movie `2423f1be2099458c548fc6ebc236c9b0518489189bdaf31da0ed7165da259a06`, scene `bf46102ecdc578cdadac244ba85dec7e5ab19fe07b80277a2fdcdb4c2b191df1`, and engine `7080c58ce151d1966b44671dc9db0801f81cb514200a3e8ed8a6cd1401777195`. Exact source indices 932 and 958 use 30000/1001 fps.

| Frame | Native MC/G MAE | Error within 3px of edges | Encoded MC/G MAE |
|---|---:|---:|---:|
| 932 | 0.511902 | 99.99359% | 0.637215 |
| 958 | 0.511634 | 99.99677% | 0.645423 |

Both contacts retain the intended cards, copy, blue app artwork, bubble tails, ordering, and camera state. No missing artwork or dropped component was observed.

The main difference is text advance and edge coverage. Email and Calendar subtitles extend 3px at 932 and 4px at 958; their left and vertical bounds match. All sampled headings and the Reminders/Automations line bounds match. Icon and bubble-edge sampling differences are small. More than 99.993% of native error is near edges, with negligible flat-interior contribution.

Encoding adds a separate error contribution: each decoded frame differs from its own native image by mean RGB error .143–.152. The full 1,283-frame comparison has mean SSIM .998292909/minimum .990000, with no heuristic flag. This is a measured qualification, not a claim of pixel identity.

The earlier frame205 review is preserved in `before7080-frame205/`. See `current7080/contact.jpg`, `detail-contact.jpg`, `measurements.json`, and `text-line-bounds.json`. No scene, engine, media, or native cache was edited.

A subsequent bounded causal probe found that explicit Canvas `fontKerning: normal` removes the two tested subtitle discrepancies pixel for pixel. This policy has not been applied to production or certified globally. See `current7080/kerning-probe/finding.md`.
