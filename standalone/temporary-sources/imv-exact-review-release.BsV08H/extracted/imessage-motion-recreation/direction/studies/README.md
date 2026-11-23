# Optional film studies

Open these on request for a particular editing question. Keep them out of the context for a fresh brief. Each study takes apart one choice from a different filmmaker or publishing team, then proposes a change to the launch cut or a reusable direction decision. The original post identifies the publishing entity where individual creative credits are unavailable.

| Study | Decision it changed |
| --- | --- |
| [Rene](01-rene.md) | Establish the audience’s reason to follow the first action before introducing the product. |
| [Poke](02-poke.md) | Let the answered question direct attention in the next shot. |
| [Linq](03-linq.md) | Allow the resolved state to register before moving on. |
| [Daniel Tian](04-daniel-tian.md) | Preserve the identity of each actor through a state change. |
| [Big Buck Bunny](05-big-buck-bunny.md) | Cut during continuous action to preserve it across a scale change. |
| [Vercel](06-vercel.md) | Test when the ending can carry evidence and brand in one image. |
| [Motionstash](07-motionstash.md) | Keep a visual anchor through a change of setting. |
| [Cero](08-cero.md) | Carry specific evidence from interface to physical consequence. |
| [AffordiHome Finder](09-affordihome.md) | Make editorial time compression legible when it changes the claim. |
| [Cash App](10-cash-app.md) | Show an observable prior state when delivery on a channel is the proof. |

## Picture evidence

The readings use overview contact sheets, closer frame samples, and 24-frame consecutive runs. Times are source playback seconds rounded to hundredths. Extract any listed moment from the matching file with `ffmpeg -ss <seconds> -i <source> -frames:v 1 <still.png>`. To inspect the transition, seek just before the moment and extract `-frames:v 24 frame-%02d.png`. The timing and descriptions refer to the pinned file bytes. The folder contains written, picture-only analysis. Intent is an inference from those frames.

| Study | Bytes inspected | SHA-256 |
| --- | --- | --- |
| Rene | `projects/06-gallery-complete-v1/imessage-recreations/references/06-gallery/source.mp4` | `fcbc98fa2f1697da5c947ed59b952128acd1c8f6194ce982c60133a423f1ddaf` |
| Poke | `projects/04-poke-complete-v1/imessage-recreations/references/04-poke/source.mp4` | `a3d5dd064dc4482813a332d7e3821a43d557c015c5cbb5be6ff09b29874db50f` |
| Linq | `projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4` | `86e22e698e141c5c2a161977289be1335bb0c0a1dd98769c4c146fcd57bbf2eb` |
| Daniel Tian | `projects/02-danieltian-complete-v1/imessage-recreations/references/02-danieltian/source.mp4` | `2c591738ac81b72d62ed51209c21820dc5a5d30e5197a732529ce833424830b2` |
| Big Buck Bunny | MediaElement sample `big_buck_bunny.mp4` at `4d21a042353022326071acb0251ab75cd6bae114` | `543a4ad9fef4c9e0004ec9482cb7225c2574b0f889291e8270b1c4d61dbc1ab8` |
| Vercel | Serena collection `videos/vercel-run-your-backend.mp4` | `ec902f70feb65b29781e80784569c646d62fa80599a2a1b0ac17a42fc77f44c3` |
| Motionstash | Serena collection `videos/motionstashco-they-remember.mp4` | `3b74a29a33d8253bf8d55f018aa3b7183cfcd1cc4f376d6391e1108ee21867ae` |
| Cero | Serena collection `videos/leomeethewoo-cero-upside.mp4` | `277072ee096dcfba11741f948ae22d89557661c14501616537b3eed205e70ec3` |
| AffordiHome Finder | Serena collection `videos/affordihome-finder-illustrated-launch.mp4` | `e192c529f74f582f25360916f79df5cec138d7e840ff421320d74837c9294ac3` |
| Cash App | Serena collection `videos/cash-app-weekly-bitcoin-rewards.mp4` | `82abf998073d8e09d6ac7e8e12e55d015aaff0dbda7527d04ce49e59cfaeca1a` |

The Serena source is pinned to `6a02fa07dfa5696ba3191dd905a06dbedc932e38`. Individual study links point to the original post and the inspected files where the review used a public mirror. [Serena collection](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/tree/6a02fa07dfa5696ba3191dd905a06dbedc932e38)
