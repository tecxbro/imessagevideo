# Direct and revise shots

For an open brief, establish what the audience should understand, who acts, and what changes. Ask for the product action, intended audience, or an example only when it would change the creative direction. Give the user an opportunity to supply inspiration. If they have none, make a concrete opening, payoff and transition from their brief. When the user supplies a reference, ask whether they want the same film, just its motion, or a specific change only if their wording leaves the task ambiguous. Explicit recreation can proceed directly.

Build each shot around a visible change. Decide which object carries attention, what moves, what stays in place, and what the viewer sees before, during and after. Retrieve suitable learned and bundled motions by that description. Open the preview and inspect the implementation. One small group of identity marks moving into a header calls for a different technique from the entire camera moving across stationary avatars. If the library falls short, show the closest option and explain the difference, or propose developing the missing movement.

## Pitch a shot plan

Create an input JSON in the project folder. Give each shot a permanent ID, a frame count, its purpose and its visual action. In the following example the displayed copy is bound to the gallery's real editable heading field.

```json
{
  "mode": "director",
  "fps": 30,
  "brief": "Let a shopper see a store's range without losing track of the store.",
  "shots": [
    {
      "id": "browse",
      "frames": 72,
      "purpose": "Keep the shop identifiable while the shopper compares items.",
      "visual": "Hold the shop name and frame in place. Move the clipped photo strip left until the second item settles.",
      "motion": {"kind": "seed", "id": "photos-under-fixed-heading"},
      "copy": "Juniper Goods",
      "copy_key": "heading",
      "bindings": {"detail": "Spring collection", "direction": "left"}
    }
  ]
}
```

Replace the example with the actual assets and content. Set `bindings.photos` to a list of project images for this motion. Inspect `recipes.py info ID` or `learn.py show ID` for the entry's editable fields. Use `kind: learned` and the saved ID for a learned recipe. Use `{"kind":"original","intent":"..."}` for a newly directed effect. For a donor video, use `{"kind":"reference","source":"other.mp4","frames":[31,61],"intent":"Keep the header fixed as the rows move."}`; frames count from zero and the end is exclusive. The donor remains a proposal until its passage has been measured and a working proof authored. Learning and promoting an entry lets subsequent projects use its ID.

```bash
python3 scripts/shots.py create project/brief.json project/v1.json
python3 scripts/shots.py render-shot project/v1.json browse project/browse-proof
python3 scripts/shots.py pitch project/v1.json --out project/pitch-v1.md
python3 scripts/shots.py check project/v1.json
```

Attach genuine project evidence with the optional shot fields `board` (a still or image strip), `preview` (the moving passage) and `code` (its editable source). All local paths are relative to the initial brief's parent directory. A pitch embeds the board and links the project proof, the selected library example and its implementation separately. To pull a board from a rendered passage run `ffmpeg -v error -i project/browse-proof/preview.mp4 -vf "select=eq(n\,31)" -frames:v 1 project/browse-frame31.png`. A set of before/during/after boards is appropriate when one still hides the decision. Open the media; tell the user which links show their content and which show a library example. Avoid using an unmodified gallery preview as a storyboard for a different shot.

For a new or donor-derived effect, inspect the actual moving proof. Attach a local JSON file via the shot’s `review` field with `preview_sha256`, `reviewer` and a concrete `observation` describing the visible intermediate movement and its landing. For a donor study, also include the same `donor` locator and exclusive-end `donor_frames` pair as the shot. This records the reviewer's scope. Literal recreation additionally needs the frame-by-frame comparison and sound checks.

For Director, show the sequence, timing, decisive intermediate state, moving examples and resulting viewer inference. Ask for changes or confirmation before full production unless the user has already delegated direct execution; set `confirmation:false` on that brief. Full visual recreation defaults to direct execution. Set `confirmation:true` if the user explicitly asks for a review stop.

```bash
python3 scripts/shots.py approve project/v1.json REVISION_FROM_PITCH project/approved-v1.json --response "User's actual reply"
python3 scripts/shots.py check project/approved-v1.json --for-production
```

A user can approve creative direction while a proof still needs work. The check reports both open motion work and the confirmation state. It compares the plan and local review files to the revision shown. External URLs identify links only. Save local evidence when its exact bytes matter. The user can confirm in natural language; the assistant records the reply and the revision that reply covered. Production requires separate final picture, sound and delivery review.

## Revise a selected shot

Resolve the user's edit to its stable shot ID, exact copy or bounded visible action. Leave all other shot records intact. Create a derivative and retain the baseline. If given only an MP4, locate the exact cut and reconstruct that passage with editable layers first. Keep audio and neighboring frames on their original clock unless the edit expressly changes timing.

```bash
# rename.json contains {"copy":"Juniper Studio"}
python3 scripts/shots.py revise project/approved-v1.json browse project/rename.json project/v2.json
python3 scripts/shots.py render-shot project/v2.json browse project/browse-v2
# proof.json contains {"preview":"browse-v2/preview.mp4","code":"browse-v2/scene.json","board":"browse-v2.png"}
python3 scripts/shots.py revise project/v2.json browse project/proof.json project/v2-review.json
python3 scripts/shots.py pitch project/v2-review.json --out project/pitch-v2.md
```

A content change clears earlier board, preview and code links on the selected shot unless you explicitly supply refreshed links in the patch. Existing files and all other shot records remain intact. To replace only the motion, patch `motion`, set any different `copy_key`/`bindings` to the new recipe's editable fields, and keep the original duration. For learned entries you may override individual asset slots through the shot's `assets` mapping. Confirm the revised plan if confirmation was requested. Inspect the whole revised passage, both cuts and the preserved regions in the assembled film. A rendered individual passage establishes only its own frame count and clock.

Use `IMESSAGE_VIDEO_MOTION_LIBRARY` or `shots.py --library PATH ...` to select a learned library. `render-shot` calls the actual seed or learned renderer in a fresh directory; it rejects output that changes the selected shot's frame count or rate. Authored effects using other engines can attach their own proof and code. For a complete film, assemble the reviewed shots using the production engine and retain the project, assets, audio, timing and editable source.
