from pathlib import Path
import json
R=Path(__file__).resolve().parent
s=json.loads((R/'reasoning-combined-candidate.json').read_text());root=s['replacement'];before=len(root['children'])
root['children']=[n for n in root['children']if not n['id'].startswith('reason-neutral-native-373-')]
old=next(n for n in root['children']if n['id']=='peak-reasoning-exit-glyphs-373');old.pop('opacity',None)
assert not any(n['id'].startswith('reason-emoji-native-')and n['id'].endswith('-373')for n in root['children'])
s['changedFrames']=[f for f in range(272,375)if f!=373];s['preservedStrongerControl']={'frame':373,'reason':'Tiny approximate neutral edge contour regressed .0023153globalMAE; retain exact original native exit glyph component, omit new neutral trace. Other states unchanged.'}
(R/'reasoning-final.json').write_text(json.dumps(s,separators=(',',':')));print('final',len(s['changedFrames']),'states; removed',before-len(root['children']),'373groups',flush=True)
