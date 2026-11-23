#!/usr/bin/env python3
"""Check the fixture's actual recapture and decoded edit outcomes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


WIDTH = 640
HEIGHT = 360
FRAME_BYTES = WIDTH * HEIGHT * 3


def native_hashes(path):
    return [line.split()[0] for line in path.read_text().splitlines()]


def frame_observations(file):
    streams = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height",
        "-of", "json", str(file),
    ]))["streams"]
    if streams != [{"codec_type": "video", "width": WIDTH, "height": HEIGHT}]:
        raise ValueError(f"Expected one silent {WIDTH}x{HEIGHT} video in {file}")

    process = subprocess.Popen([
        "ffmpeg", "-v", "error", "-xerror", "-threads", "1", "-i", str(file),
        "-map", "0:v:0", "-an",
        "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-threads", "1",
        "-f", "rawvideo", "pipe:1",
    ], stdout=subprocess.PIPE)
    with process.stdout as output:
        hashes = []
        selected = []
        message = None
        while frame := output.read(FRAME_BYTES):
            if len(frame) != FRAME_BYTES:
                raise ValueError(f"Incomplete decoded frame {len(hashes)} in {file}")
            index = len(hashes)
            if 66 <= index < 89:
                # Interior pixel in the checkbox, outside the check mark stroke.
                offset = (222 * WIDTH + 445) * 3
                red, green, blue = frame[offset:offset + 3]
                if blue > red + 50 and blue > green + 50:
                    selected.append(index)
            if index == 38:
                # Text line of the fully settled outgoing bubble.
                message = b"".join(frame[(y * WIDTH + 266) * 3:(y * WIDTH + 447) * 3]
                                   for y in range(168, 181))
            hashes.append(hashlib.sha256(frame).hexdigest())
    if process.wait() != 0 or len(hashes) != 120:
        raise ValueError(f"Expected all 120 frames in {file}, got {len(hashes)}")
    return hashes, selected, message


def different_frames(left, right):
    return [frame for frame, (before, after) in enumerate(zip(left, right, strict=True))
            if before != after]


def main(output):
    changed_native = different_frames(
        native_hashes(output / "native-before.sha256"),
        native_hashes(output / "native-after.sha256"),
    )
    if changed_native != list(range(74, 78)):
        raise ValueError(f"Unexpected native repair extent: {changed_native}")

    _, first_selected, _ = frame_observations(output / "first.mp4")
    final, final_selected, final_message = frame_observations(output / "final.mp4")
    edited, edited_selected, edited_message = frame_observations(output / "edited.mp4")
    observed = [first_selected, final_selected, edited_selected]
    if observed != [list(range(first, 89)) for first in (78, 74, 69)]:
        raise ValueError(f"Wrong decoded selection states: {observed}")
    message_pixels_changed = sum(
        max(abs(before - after) for before, after in zip(final_message[i:i + 3], edited_message[i:i + 3])) > 30
        for i in range(0, len(final_message), 3)
    )
    if message_pixels_changed < 20:
        raise ValueError("Decoded outgoing copy region did not change visibly.")
    changed_encoded = different_frames(final, edited)
    report = {
        "native_cache_frames": 120,
        "recaptured_and_changed_native_frames": changed_native,
        "unchanged_native_frames": 120 - len(changed_native),
        "edited_copy": ["Two seats to Union Station.", "Two seats to Northgate."],
        "earliest_selected_decoded_frame": {
            "first": first_selected[0], "final": final_selected[0], "edited": edited_selected[0],
        },
        "edited_copy_frame": 38,
        "edited_copy_region": [266, 168, 181, 13],
        "changed_pixels_in_edited_copy_region_delta_gt_30": message_pixels_changed,
        "edited_decoded_frames_different": changed_encoded,
        "edited_complete_frame_count": len(edited),
        "note": "Delivery compression can change RGB outside the edited regions.",
    }
    (output / "repair-and-edit.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
