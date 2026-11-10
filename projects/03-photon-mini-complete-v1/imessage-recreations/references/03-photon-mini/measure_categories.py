from pathlib import Path
from PIL import Image
import subprocess,json
p=Path(__file__).parent/'category-measurements'
rows=[]
for i,f in enumerate(sorted(p.glob('[0-9]*.png'))):
    image=Image.open(f).convert('L').point(lambda value: 0 if value < 100 else 255)
    image.save(p/'threshold.png')
    result=subprocess.run(['tesseract',str(p/'threshold.png'),'stdout','--psm','7'],capture_output=True,text=True)
    rows.append({'t_bin_approx':32.5+(i+.5)*.1,'black_active_text_ocr':result.stdout.strip()})
(p/'ocr.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
