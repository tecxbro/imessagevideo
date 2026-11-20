# Variable frame clock probe

The simulator's native [search-open.mov](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios/motion/search-open.mov) has 126 pictures with irregular decoded PTS. Its last frame starts at 3540/600 seconds and lasts 23/600 second. The stream advertises an earlier end, so the tool uses the last decoded frame duration.

The clock encoder placed 126 independently authored blank images on that clock. It checked all 126 decoded PTS and the exact final end at 3563/600 seconds. This probe measures timing only. [Clock result](search-open-encode.json)

```bash
R=skill/imessage-motion-recreation/recreate
W=/tmp/imv-clock-proof
mkdir -p "$W/frames"
python3 "$R/recreate.py" analyze "$SEARCH_OPEN" --out "$W/measurements"
ffmpeg -v error -f lavfi -i color=0xeeeeee:size=1206x2622:rate=30 -frames:v 1 -threads:v 1 "$W/canvas.png"
for frame in $(seq 0 125); do
  ln "$W/canvas.png" "$W/frames/$(printf %06d "$frame").png"
done
python3 "$R/recreate.py" encode-clock "$W/frames" --measurements "$W/measurements" --out "$W/clock.mp4"
```

A second probe used the long-press simulator capture. It retained all 239 PTS and the final one-microsecond sample. [Long-press clock result](longpress-encode.json)
