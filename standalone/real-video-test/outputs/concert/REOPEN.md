# Reopen the concert project

The three shots, artworks, editable layer scenes and approved plans are in this folder. In the ZIP, the sibling `skill/imessage-video` folder supplies the same runtime used for the audit.

Run the following from the extracted `concert` folder after installing the dependencies listed in the skill’s real-video README.

```sh
python3 ../skill/imessage-video/scripts/shots.py check plan-reply-approved.json --for-production
python3 ../skill/imessage-video/scripts/shots.py render-cut plan-reply-approved.json fresh-concert.mp4
python3 ../skill/imessage-video/scripts/shots.py render-cut plan-edit-approved.json fresh-edited.mp4
```

To change an editable shot, start with the plan, bind the content in the named shot and render a new proof. The pitch approval is tied to the exact files under review. The proof directories also contain the resolved `scene.json` and any local assets for direct rendering with the supplied Pillow engine.
