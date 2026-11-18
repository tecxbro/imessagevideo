# Catalog trial evidence

## Source films

The three source intervals total 102 decoded frames. The review used zero-based source indices and consecutive decoded pictures at 30 fps. The [interval check](verify_source_intervals.py) reads the films directly and verifies the [hashes and presentation timestamps](source-interval-results.json).

- **Linq 1091–1111.** All 21 frames show one variable-width photo strip moving left inside a fixed viewport. Estimated travel is 1,140 px at the source's 960 × 720 resolution, with four repeated positional samples. Patches from the place name, rating, actions, tabs and address matched at zero displacement. The adaptation normalizes this sampled X track to the new strip's length and uses independently editable copy, actions and artwork. [Source film and measurements](../../skill/imessage-motion-recreation/director/motion-library/catalog.json)
- **Photon Mini 211–240.** The separate sheet enters from below and covers the original inline card. The grabber and controls travel with it. Its top edge briefly overshoots before settling. The underlying conversation dims and shifts slightly in the film. The adaptation reuses the vertical samples with a separately authored scrim and fixed underlay position.
- **Gallery 603–653.** Portraits converge on different paths, shrink and come into focus. The center of the headline holds while the headline scale falls to about 0.56 and portraits partly obscure it. The adaptation maps the sampled headline scale into a new arrangement with separately authored portrait paths and focus.
- **Messages attachment stack.** Apple describes grouping four or more photos or videos into a stack, with swiping available once the stack is opened. Apple's iOS 15 feature description also describes a swipeable stack in the conversation. The film adaptation stages two inline swipes by moving opaque, independently layered cards across a mask. The current preview's depth, motion and timing are authored. The sibling UI review found supporting documentation and lacked a matched recording of native inline paging, arrival and gestures. [Current Apple guide](https://support.apple.com/guide/iphone/share-content-iphb66cfeaad/27/ios/27) · [iOS 15 feature description](https://www.apple.com/jo/ios/ios-15-preview/features/) · [UI trial attachment evidence](https://github.com/tecxbro/imessagevideo/blob/ef83db187d7291a5d70f6dedb1f436f55b5abba3/skill/imessage-motion-recreation/director/ui-trial/ATTACHMENT-EVIDENCE.md)

The frames establish what moves in the source clips. The source films do not expose their gesture events, runtime group trees or original spring parameters.

## Retrieval and reuse

The original director planner at `c49482aec7b8ed0b840f97c61a5e5b860c4077b6` ranked `message-wall` first for the attachment request. The [preserved response](baseline-wrong-retrieval.json) came from the actual planner. The [same brief through the motion catalog](revised-retrieval.json) finds the attachment stack based on the stacked objects and the next item being behind the front one. The bare word [carousel](ambiguous-retrieval.json) returns the competing motions and requests the moving and fixed objects.

A fresh agent searched five briefs before inspecting the catalog. Four detailed briefs found the requested motions. The ambiguous brief triggered a follow-up. It replaced copy and artwork and rendered two new scenes. In Night Garden, stall illustrations share a clipped horizontal track under the fixed title and buttons. In Field Crew, two successive swipes expose different opaque front cards with the conversation and composer fixed. [Blind trial, configs and raw search results](blind/README.md)

## Export verification

The 45 Node tests cover retrieval, path rebasing, editable assets and layer behavior alongside the existing director tests. FFmpeg decoded all 600 frames across the [six shipped MP4s](preview-results.json). Review included ordered all-frame sheets and larger samples of the two custom renders. The motion samples were reviewed from decoded frames. Live playback timing and native touch physics were outside that review.

## References consulted

- The active skill established the director CLI conventions and editability boundaries. The original catalogue and production index provided the source projects and existing studies. [Skill](https://github.com/tecxbro/imessagevideo/blob/main/skill/imessage-motion-recreation/SKILL.md) · [Director catalogue](https://github.com/tecxbro/imessagevideo/blob/main/skill/imessage-motion-recreation/director/catalogue.json) · [Final production](https://github.com/tecxbro/imessagevideo/blob/main/FINAL-PRODUCTION.md)
- HyperFrames illustrates a search-to-editable-source flow with an explicit search miss. Its pattern informed the CLI sequence. [HyperFrames registry skill](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-registry/SKILL.md)
- Serena links discovery results to playable originals and tracks source metadata. This catalog couples each measured entry's original film and frame interval to a separate moving adaptation. [Reference discovery skill](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/blob/main/agent/SKILL.md) · [Source-video dataset](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos)
- Launch Video Clone uses contiguous decoded frames to inspect transitions. The source study here used that approach to distinguish shared motion from layer-specific motion. [Launch Video Clone skill](https://github.com/per-simmons/launch-video-clone/blob/main/SKILL.md)
