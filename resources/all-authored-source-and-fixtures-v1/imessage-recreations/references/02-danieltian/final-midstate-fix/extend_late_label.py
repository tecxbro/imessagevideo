from pathlib import Path
import json,copy
R=Path(__file__).resolve().parent
spec=json.loads((R/'late-birth-elements-candidate.json').read_text())
chat=json.loads((R/'chat-original.json').read_text())
label=next(n for n in chat['children']if n['id']=='middle-airbnb-card-sender-label')
def sample(key,frame):
    keys=label.get('keyframes',{}).get(key,[])
    time=frame/30
    if not keys:return label.get(key,1 if key.startswith('scale')else 0)
    if time<=keys[0]['t']:return keys[0]['value']
    for before,after in zip(keys,keys[1:]):
        if time<=after['t']:
            amount=(time-before['t'])/(after['t']-before['t'])
            return before['value']+(after['value']-before['value'])*amount
    return keys[-1]['value']
rows=json.loads((R/'label-clipping-measurements.json').read_text())
clones=[]
for row in rows:
    frame=row['frame']
    if not(905<=frame<=957):continue
    if row.get('clippedSource'):
        clone=copy.deepcopy(label)
        clone['id']=f'late-label-unclamped-{frame}'
        clone['start']=frame/30
        clone['end']=(frame+1)/30
        clone.pop('keyframes',None)
        for key in['x','y','scaleX','scaleY']:clone[key]=sample(key,frame)
        clone['y']+=row['nativeYCorrection']
        clone['sourceFrame']=frame
        clone['sourceInkBounds']=row['sourceInkBounds']
        clone['editability']='Existing native semantic glyph outline, independently posed beyond the viewport. Full geometry is retained while genuine viewport clipping hides upper glyphs.'
        clones.append(clone)
    else:
        assert row['sourceInkBounds']is None
spec['label']={'id':label['id'],'gateFrames':list(range(905,958)),'clones':clones,'diagnosis':'The old tracker clamped visible ink top to0 and treated a partial glyph as full. Source label moves beyond the viewport, briefly disappears915–918, reappears in the bounce, and leaves after954. Keep full existing glyph geometry, measure negative-Y poses, suppress genuinely absent states.'}
spec['changedFrames']=sorted(set(spec['changedFrames'])|set(range(905,958)))
(R/'late-birth-elements-candidate.json').write_text(json.dumps(spec,separators=(',',':')))
print('combined changed',len(spec['changedFrames']),'label clones',len(clones),'absent label states',[q['frame']for q in rows if 905<=q['frame']<=957 and not q.get('clippedSource')])
