"""Extract zero-based native evidence, never timestamp-rounded seeks."""
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]
EVENTS = [12, 90, 132, 140, 186, 432, 445, 451, 457, 463, 469, 474, 480, 486, 492,
          505, 510, 522, 525, 529, 532, 535, 538, 542, 545, 548, 575, 590]
frames = sorted({f+d for f in EVENTS for d in [-1, 0, 1]} | {0, 30, 60, 110, 155, 180, 200, 209, 210, 240, 270, 300, 330, 360, 390, 419, 420, 431, 500, 520, 560, 574, 580, 610, 660, 719})
frames = sorted(set(frames) | set(range(0,36)) | set(range(85,111)) | set(range(134,166)) | set(range(180,211)) | set(range(420,461)) | set(range(500,513)) | set(range(548,581)))
process = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(BASE/'v1-first-export.mp4'),
    '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
for f in range(720):
    raw = process.stdout.read(1080*1920*3)
    assert len(raw) == 1080*1920*3
    if f in frames:
        pixels = np.frombuffer(raw, np.uint8).reshape(1080,1920,3)
        Image.fromarray(pixels).save(BASE/'evidence'/f'frame-{f:03}.png')
assert process.wait() == 0
overview = [0,12,90,110,132,140,186,210,270,330,390,419,432,492,505,510,548,575,590,719]
sheet = Image.new('RGB', (1920, 5*298), '#222222'); draw = ImageDraw.Draw(sheet)
for i,f in enumerate(overview):
    x,y=(i%4)*480,(i//4)*298
    im=Image.open(BASE/'evidence'/f'frame-{f:03}.png').resize((480,270))
    sheet.paste(im,(x,y)); draw.text((x+8,y+275),f'frame {f} / {f/30:.3f}s',fill='white')
sheet.save(BASE/'evidence/contact-sheet.png')
print(f'Extracted {len(frames)} native frames; evidence/contact-sheet.png')
