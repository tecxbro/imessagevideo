# iMessage video dataset pack

[Download this branch as one ZIP](https://github.com/tecxbro/imessagevideo/archive/refs/heads/dataset-pack.zip). Sign in to GitHub with access to this private repository. The download contains every file from the original 109-file dataset pack. Start with [PROMPT.md](PROMPT.md), [DATASETS.md](DATASETS.md) and [video-sources.csv](video-sources.csv).

- [originals/](originals/) holds the six original MP4s.
- [native-ui/](native-ui/) holds four simulator recordings and 76 reference images.
- [upstream/](upstream/) holds the skill and media ZIPs, inventories, source lists and checksums. Extract the media ZIP for motion previews, films and editable audio projects.

## Pull the dataset and the 99 additional launch films

```sh
git clone --depth 1 --branch dataset-pack --recurse-submodules --shallow-submodules https://github.com/tecxbro/imessagevideo.git imessage-video-dataset
```

The 99 additional films live in `launch-library/videos/` after cloning with submodules. To get them separately after using the browser ZIP, use the [pinned collection ZIP](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/archive/6a02fa07dfa5696ba3191dd905a06dbedc932e38.zip).

## Restore the original ZIP byte for byte

From the extracted folder or the clone run `python3 tools/restore_zip.py`. It checks all 109 source files and writes `imessage-video-dataset-pack.zip` (108,820,371 bytes). Its SHA-256 is `dce4f0dcb5ad4ad36d370dad98035c17a97b3cce311242b55449ab4d850473f1`.
