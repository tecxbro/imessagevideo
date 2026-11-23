# Orchard Crew

A fresh agent opened the Motion skill in a dedicated package and made a new conversation using [replacement content](orchard.json). The first retrieval exposed confusion between a stationary typing field and a live typing indicator. The same brief subsequently selected the reply-reflow entry directly.

From the repository root, with Clone iMessage UI installed beside Motion in the skill:

```sh
node skill/imessage-motion-recreation/motion/cli.mjs render --ui \
  --brief 'Let a reply from the other person become the line viewers take away. Have the older messages rise to give the new bubble space while the chat name and the typing field stay exactly where they are.' \
  --content review/imv-v3/motion/reuse/orchard/orchard.json --out /tmp/orchard.mp4
```

The export is 72 frames at 30 fps. The answer first appears at frame 35. In frames 34 and 35 the heading and composer crops are pixel-identical. The older outgoing bubbles move up 30 pixels at onset and 50 by frame 43. [MP4](orchard-ui.mp4) · [Events](orchard-ui.events.json) · [Consecutive frames](orchard-ui-onset.png) · [Decoded measurements](orchard-ui-decoded.json)
