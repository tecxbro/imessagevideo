# Payment sequence evidence

Checked November 20, 2026 Pacific time. Direction and Dataset were asked for
an approved continuous test capture and provenance. The supplied local
reference is the Linq launch edit, 960 × 720, constant 30 fps, 1,458 decoded
frames. Its SHA-256 is
`86e22e698e141c5c2a161977289be1335bb0c0a1dd98769c4c146fcd57bbf2eb`.
Frame numbers are zero-based. The local file is
`projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4`.
Device, OS, and test versus live mode are unknown for this passage.
[Capture handoff request](https://github.com/tecxbro/imessagevideo/issues/7#issuecomment-7052500167) · [Repository source index](../../../../PROJECT-HANDOFF.md)

| Moment | Observation from consecutive Linq frames | Editable test mock |
| --- | --- | --- |
| Inline card | f708–720, about 23.60–24.00 s. A dark request card with an amount and Pay control enters beneath the reply. | f14, `ui.payment-mock.card`. A labeled request enters as message `request`. |
| Approval | f771–779, about 25.70–25.97 s. The edited composition reveals an amount-entry panel. This interval shows entry controls. Verified approval and its outcome are capture gaps. | f34, `ui.payment-mock.approval`. A separate sheet reads “TEST MOCK · NO CHARGE” and “Simulated approval.” |
| Dismissal | f829–843, about 27.63–28.10 s. The amount panel exits the editorial crop. A continuous return from approval to the same thread needs a test recording. | f59, `ui.payment-mock.dismiss`. The sheet fades out by f66. The same request remains visible and awaiting payment. |
| Result | f831–843, about 27.70–28.10 s. A chat follow-up appears. Provider settlement needs independent evidence. | f78, `ui.payment-mock.result`. The inline card updates in place to “Paid · Simulated.” |

Keiki documents that a payer on a Keiki iMessage line gets a Vault Pay card.
Its payments documentation distinguishes card delivery and later settlement
rewrites. The Linq editorial reference depicts a different provider. The
editable fixture uses local test events and original graphics with visible
mock labels on all payment surfaces. No provider session, payment method, or
charge was used. [Keiki Payments](https://onkeiki.com/docs/payments) ·
[Keiki iMessage Apps](https://onkeiki.com/docs/imessage-apps) ·
[Keiki Vault](https://onkeiki.com/docs/keiki-vault)

The pinned Photon demo notes describe merchant-checkout presentation
f66–181, card growth f101–121, and cancellation f185–198 in a 512×1112,
30 fps source. Its original clip, device build and reuse permission are
unverified. The notes exclude authorization and settlement. Apple's
no-charge merchant web demo describes selection, authentication and a
result on the sheet before dismissal between 00:38 and 04:12. That is a
different platform and flow from a Messages test order. The fixture's
post-dismissal result remains authored.
[Photon presentation notes](https://github.com/tecxbro/imessagedemo/blob/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc/docs/apple-pay-presentation.md)
[Apple Developer web demo](https://developer.apple.com/videos/play/tech-talks/111381/)

[Editable test fixture](../../../../skill/imessage-motion-recreation/ui/examples/payment-mock.json) ·
[Decoded test clip](payment-mock.mp4) · [Event map](payment-mock.events.json) ·
[Consecutive frames](payment-mock-frames.jpg)
