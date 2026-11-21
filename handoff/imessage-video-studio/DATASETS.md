# Where the footage, sound, images and code live

[Download the full dataset ZIP](https://github.com/tecxbro/imessagevideo/archive/7eb234ab021f573fb8aa20eab08326f4e0e85b51.zip) or [open the dataset folder](https://github.com/tecxbro/imessagevideo/tree/dataset-pack). All 109 original packet files are on GitHub. The dataset folder also has a clone command that fetches the 99 additional launch films.

Open [video-sources.csv](video-sources.csv) for 391 individually indexed records. It includes the original post or provenance, the pinned media URL, the packet or upstream location and the available file size and hashes. Some historic inventory rows are archive duplicates. The CSV’s native-ui paths describe the packet layout. The links take you directly to the corresponding upstream files.

| Collection | What to open |
| --- | --- |
| Six original films | [originals/](originals/) holds Photon 2.0, Agent to Agent, Photon Mini Apps, Poke Apple Messages, Linq iMessage Apps and Rene. Match each to the first six CSV rows and the original posts in [PROJECT-HANDOFF.md](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/PROJECT-HANDOFF.md). The original MP4 paths, byte counts and SHA-256 values are in [LOCAL-LIBRARY.json](upstream/LOCAL-LIBRARY.json) under `examples[].source`. |
| Six editable projects and their assets | Use [LOCATIONS.md](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/LOCATIONS.md) and [inventory/](upstream/inventory/). The inventory covers 30 renderer outputs, 30 silent masters, fonts, artwork, audio, comparisons and the wider library. Clone the production repo at the pin below, then run `python3 tools/sync_library.py` and `python3 tools/library.py verify` from its root. Open `catalog/index.html`. |
| Native Messages images and recordings | The [pinned references directory](https://github.com/theswerd/imessage-ui/tree/1f132909792ff540501385f91d37ef20629c55b7/references) contains the spec, images and simulator motion. The [recordings](https://github.com/theswerd/imessage-ui/tree/1f132909792ff540501385f91d37ef20629c55b7/references/ios/motion) are send, long press, search open and search close. Clone at the UI pin below for the four movies and 76 comparison images. Exact paths, sizes and Git blob IDs are in [ui-file-identities.json](upstream/ui-file-identities.json). Review the upstream third-party notices. [CAPTURES.md](upstream/CAPTURES.md) identifies device, state and coverage gaps. |
| Prior skill, motion and sound | Download the two ZIPs in [upstream/](upstream/). Extract `imessage-motion-media-v3.2.1.zip` into an empty folder and `imessage-motion-recreation-v3.2.2.zip` into its `skill/` subfolder. From the media root run `sha256sum -c MEDIA-SHA256SUMS` (macOS: `shasum -a 256 -c MEDIA-SHA256SUMS`). There are 77 base motion previews, 13 UI variants, four other films/examples and 24 WAVs inside the editable project archives. See the [Observer verdict and evidence](https://github.com/tecxbro/imessagevideo/tree/d07bbae7c43cfcbf5182fff1a1d34e652a72c150/review/imv-v3/observer). |
| 99 broader launch films | Use the [creator and film index](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/blob/6a02fa07dfa5696ba3191dd905a06dbedc932e38/data/videos.json), [MP4s](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/tree/6a02fa07dfa5696ba3191dd905a06dbedc932e38/videos), [poster frames](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/tree/6a02fa07dfa5696ba3191dd905a06dbedc932e38/previews) or [full ZIP](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/archive/6a02fa07dfa5696ba3191dd905a06dbedc932e38.zip). These files live in the upstream repo. Each MP4 has its own row in video-sources.csv. |

## Starting checkouts

| Source | Pinned checkout |
| --- | --- |
| Historical production library and five rendering adapters | [tecxbro/imessagevideo](https://github.com/tecxbro/imessagevideo/tree/c49482aec7b8ed0b840f97c61a5e5b860c4077b6) |
| Messages UI, comparison stills and simulator recordings | [theswerd/imessage-ui](https://github.com/theswerd/imessage-ui/tree/1f132909792ff540501385f91d37ef20629c55b7) |
| Authored app and interaction evidence | [tecxbro/imessagedemo](https://github.com/tecxbro/imessagedemo/tree/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc) |
| HTML composition and video rendering | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/9813a6cbef97fffda70f5a147b87747f7e35a77b) |
| Editable launch-film implementation | [per-simmons/launch-video-clone](https://github.com/per-simmons/launch-video-clone/tree/7e97ac6488eb61ca4d25affe7fc1da7cfb80b376) |
| Launch-film discovery library | [serenakeyitan/awesome-ai-clonable-launch-videos](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/tree/6a02fa07dfa5696ba3191dd905a06dbedc932e38) |

Earlier imessagevideo commits to fetch are `a23bfb294fbc65739811a84f264ad306ca192fe1`, `b525e7e11279db836bbdd2ff4b1b8953b56b946f`, `69595dfa2ef588a59d1b0b4d5836817a49d0f809` and `b303dde12ca8a314a36a7e70ed42e3e0f1605464`. Read the [original team brief](https://github.com/tecxbro/imessagevideo/issues/7) alongside the seven `codex-video-v3/*` heads and `codex-main`.

Product and workflow references: [Keiki docs](https://onkeiki.com/docs), [channels](https://onkeiki.com/docs/channels), [iMessage apps](https://onkeiki.com/docs/imessage-apps) and [GitHub Actions events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
