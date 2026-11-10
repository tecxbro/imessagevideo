"""Measured native sheet travel and backdrop contrast, exact rational frames."""
import json
from v8_utils import track, amend, flat
FPS=30000/1001

def apply(scene, directory):
    by={l['id']:l for l in scene['layers']}
    data=json.loads((directory/'measurements-v8/calendar-fit.json').read_text())['measurements']
    rows=[]
    for r in data:
        if r['frame']>=263: continue
        r=dict(r)
        controls=[c for c in r.get('first_column_controls',[]) if c['width']>=320]
        if controls and r.get('white_top')==0:
            r['sheet_y']=min(c['bbox'][1] for c in controls)-877
        if 'sheet_y' in r: rows.append(r)
    track(by['p0100'],'y',rows,'sheet_y')
    by['p0100']['keyframes']['opacity']=[{'t':rows[0]['time'],'value':1}]
    for name in ['p0066','p0068','p0100']: by[name]['end']=263/FPS
    for name in ['p0109','p0113']: by[name]['start']=263/FPS
    shade=[r for r in data if r['frame']<263]
    track(by['p0068'],'opacity',shade,'scrim_opacity')
    # Follow source selected button rather than approximate wall-clock tap.
    selected=next((r['time'] for r in data if any(c['blue_area']>10000 for c in r.get('first_column_controls',[]))),7.8)
    for child in by['p0100']['children']:
        if child['id'] in ['p0091','p0092']: child['start']=selected
    data=json.loads((directory/'measurements-v8/restaurant-fit.json').read_text())['measurements']
    rows=[r for r in data if 'sheet_y'in r and r['frame']>=578 and r['frame']<=666 and (r['frame']>=664 or r['photo_ncc']>.8)]
    track(by['p0255'],'y',rows,'sheet_y')
    shade=[r for r in data if 'scrim_opacity'in r and 578<=r['frame']<=669]
    track(by['p0231'],'opacity',shade,'scrim_opacity')
    # Verified real apostrophe coverage, with existing measured glyph span retained.
    for font in scene.get('fonts',[]):
        if font.get('family')=='SF Pro Display' and str(font.get('weight'))=='500':
            font['src']='assets/SF-Pro-Display-Medium.finalchars.woff'
    for l in flat(scene['layers']):
        if l.get('text')=="Zareen's" and l.get('fontWeight')==500:
            l['scaleX']=l.get('scaleX',1)*165/169
    fit=directory/'measurements-v8/calendar-ink-fit.json'
    if fit.exists():
        lookup={l['id']:l for l in by['p0100']['children']}
        for record in json.loads(fit.read_text())['measurements']:
            for prop in ['x','y','scaleX','scaleY']:lookup[record['id']][prop]=record[prop]
    return scene
