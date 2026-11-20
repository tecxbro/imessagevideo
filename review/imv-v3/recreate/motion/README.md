# Motion handoff

Motion revision `de04deb` rendered the provided photo rail at 30/1 for 72 frames. Recreation supplied independently authored Union and Northgate placeholders and an edited heading. The heading stayed fixed while the old asset paths and the viewport content were replaced. Viewport changes across f19→20 and f38→39 were measured in the rendered file. [Matched frame and crop measurements](motion-proof.json)

From a checkout containing the Motion handoff, pass the supplied content to the Motion CLI. Use a Python environment with the pinned Pillow renderer dependencies.

```bash
S=skill/imessage-motion-recreation
D=review/imv-v3/recreate/motion
node "$S/motion/cli.mjs" render --id photos-under-fixed-heading --content "$D/train-stops.json" --out /tmp/recreation-motion.mp4
```
