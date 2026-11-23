from pathlib import Path
import numpy as np
from PIL import Image
p=Path(__file__).parent
for f in range(396,414):
 images=[np.asarray(Image.open(r/f'{f:06}.png').convert('RGB'),dtype='int16') for r in (Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),Path('/tmp/sidehoe-thread-audit.oxTJaL/frames'),p/'calendar-probe')]
 a,b,c=images
 print(f,*(round(np.abs(a-z).mean(),4) for z in [b,c]),'ticks',*(round(np.abs(a[:,120:190]-z[:,120:190]).mean(),3) for z in [b,c]))
