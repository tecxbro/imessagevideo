"""Reproducible bounded revision; all tracks come from saved native evidence."""
import sys,json
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p))
import v8_grid,v8_modals,v8_intro,v8_ui_cameras,v8_intro_finish,v8_states,v8_ui_finish
s=json.loads((p/'scene-v7-fonts.json').read_text())
for module in [v8_grid,v8_modals,v8_intro,v8_ui_cameras,v8_intro_finish,v8_states,v8_ui_finish]:module.apply(s,p)
s['title']='Poke Apple Messages launch — native recreation v8 measured complete timeline'
s['source']['notes']='Independent full native graphic recreation at1440x1080,30000/1001fps,1283frames. Editable native text/bubbles/controls/sheets/waveforms and separately measured favorites/inbox/header/physical/keyboard/composer/conversation cameras. Genuine static photos/maps/Memoji/logos and screen-transparent device hardware are individually declared in asset provenance; no source video or complete source frame is an output layer. Official SF Pro fonts are embedded with coverage verified. Exact source frame cuts142,263,361,800,1215 and dense frame-index motion fits correct the every-frame v7 peaks. This is a measured reconstruction, not a pixel-identity certification; glyph rasterization, glass illumination, artwork sampling and some optical transition details differ. See verification reports and steps-rebuild.md for quantified limits.' 
(p/'scene-v8-batch-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False))
print('Built',len(s['layers']),'roots')
