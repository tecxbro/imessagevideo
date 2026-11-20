"""Capture one browser take of the original offline approval test."""

import argparse
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

FPS = 20
FRAME_COUNT = 96


def capture(chromium, output):
    command = ["ffmpeg", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS),
               "-vcodec", "png", "-i", "-", "-an", "-c:v", "libx264", "-threads", "1",
               "-crf", "19", "-pix_fmt", "yuv420p", str(output)]
    with sync_playwright() as playwright, subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        browser = playwright.chromium.launch(executable_path=chromium)
        page = browser.new_page(viewport={"width": 400, "height": 720}, offline=True)
        page.clock.install()
        page.set_content(Path(__file__).with_name("payment-test.html").read_text())
        page.clock.pause_at(page.evaluate("Date.now()") + 100)
        card = page.locator("#test-order").element_handle()
        dialog = page.get_by_role("dialog")
        result = page.get_by_role("status")
        action = {
            20: page.get_by_role("button", name="Review test payment"),
            40: page.get_by_role("button", name="Approve $12.00 test"),
        }
        for frame in range(FRAME_COUNT):
            if frame in action:
                action[frame].click(force=True)
            if dialog.is_visible() != (20 <= frame < 46) or result.is_visible() != (frame >= 61):
                raise RuntimeError(f"unexpected payment test state at frame {frame}")
            encoder.stdin.write(page.screenshot())
            page.clock.run_for(1000 // FPS)
        if not card.evaluate("(node) => node === document.querySelector('#test-order')"):
            raise RuntimeError("checkout card was replaced")
        encoder.stdin.close()
        browser.close()
        if encoder.wait():
            raise RuntimeError("FFmpeg could not encode the capture")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--chromium", default="/usr/bin/chromium")
    args = parser.parse_args()
    capture(args.chromium, args.output)


if __name__ == "__main__":
    main()
