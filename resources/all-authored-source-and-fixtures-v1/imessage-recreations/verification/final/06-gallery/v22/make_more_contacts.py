from pathlib import Path
from PIL import Image, ImageDraw
R = Path('/workspace/imessage-recreations')
D = R / 'verification/final/06-gallery/v22'
for label, frames in [('black', list(range(1230, 1332, 4))), ('done', list(range(198, 219)))]:
    for batch in range(0, len(frames), 12):
        rows = frames[batch:batch + 12]
        canvas = Image.new('RGB', (1000, 170 * len(rows)), '#dddddd')
        draw = ImageDraw.Draw(canvas)
        for j, f in enumerate(rows):
            if label == 'black':
                src = Image.open(D / f'source-late/{f:06d}.png').convert('RGB')
                crop = (200, 300, 1720, 900)
            else:
                src = Image.open(D / f'source-done/{f:06d}.png').convert('RGB').crop((350, 430, 1520, 850))
                crop = (350, 430, 1520, 850)
            out = f if f < 1230 else f - 181
            cand = Image.open(R / f'outputs/06-gallery/frames-gsap/{out:06d}.png').convert('RGB').crop(crop)
            for x, im in [(0, src), (500, cand)]:
                im.thumbnail((498, 145))
                canvas.paste(im, (x, 170 * j + 23))
            draw.text((5, 170 * j + 4), f'source {f} / output {out} | source left, native right', fill='black')
        canvas.save(D / f'{label}-contact-{batch // 12}.jpg', quality=92)
print('contacts complete')
