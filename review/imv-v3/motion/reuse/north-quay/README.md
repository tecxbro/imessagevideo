# North Quay volunteers

A fresh tester received the packaged skill, its committed default preview and the installed render runtime. The request was:

> For our volunteer drive recap, keep the section heading and the word Registrations steady. The figure should climb from 620 to 1,280 so the audience sees the growth, then pause on the total. Use the heading North Quay volunteers.

The tester used the original wording for both selection and the edited render. `select` returned `adapt` with `metric-count`, the title, the label, both endpoints and an empty unit. `preview` located the fixture. `render --brief` applied the returned content and wrote the new editable scene and event map.

An earlier independent test with a prototype missed the exact wording and needed a rephrase. Its hold event was one frame late. The canonical implementation carries the revised grammar and derives the two stable event frames from actual displayed-value changes. A new agent repeated the unmodified brief in an isolated task input directory and identified six intermediate frames whose authored timestamp landed just after its output frame. The revised recipe writes those text changes directly at frame ÷ fps.

- [Picture](north-quay-volunteers.mp4) · [Editable scene](north-quay-volunteers.scene.json) · [Events](north-quay-volunteers.events.json)
- H.264 at 720×480, 30 fps, 72 frames. SHA-256 `d5e367b02fac37c9918696604444b41599a434e7300ed810d8a7c780b36352d1`.
- Frames 0–9 show 620. The value first changes on f10. The total 1,280 becomes visible on f55 and holds through f71. Event IDs survive the change of content.
