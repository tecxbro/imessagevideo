"""Keep six static assets; restore genuine opaque white within thumbnail shapes."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np
import json
import hashlib
import importlib.util
P = Path(__file__).resolve().parent
A = P/'assets/menu-rows-split-v15'
A.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location('trace',P.parent/'02-danieltian/trace_glyphs.py')
tracer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracer)
records = json.loads((P/'menu-rows-v15/assets.json').read_text())['rows']
for row in records:
    old = np.array(Image.open(row['asset']).convert('RGBA'))
    height,width = old.shape[:2]
    split = round(width*.70)
    support = old[:,:,3]>0
    support[:,:split] = False
    support[-4:] = False
    labels,_ = ndimage.label(support)
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    photo = ndimage.binary_fill_holes(labels==int(counts.argmax()))
    frame = row['source_frame']
    original = np.array(Image.open(P/'lunch-native'/f'{frame-609:03}.png').convert('RGB'))
    left,top,right,bottom = row['source_crop']
    crop = original[top:bottom,left:right]
    old[photo,:3] = crop[photo]
    old[photo,3] = 255
    path,_ = tracer.trace_alpha(photo.astype('float32'))
    file = A/f'row-{row["row"]}.png'
    Image.fromarray(old).save(file)
    row.update(asset=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),copy_photo_split_x=split,separator_height=4,photo_support_path=path)
    row['alpha_notice'] += ' Thumbnail interior white pixels are restored opaque; native white support behind each photo supplies its correct fade destination after the backplane stencil.'
(P/'menu-rows-v15/assets-split.json').write_text(json.dumps({'rows':records,'notice':'Still six static UI row assets. Copy and photo regions have separate native motion; photo internal whites are preserved.'},indent=2))
print('six split-ready assets')
