"""Apply independently measured source-only feature cameras at native cadence."""
import json,statistics,math
from scipy.optimize import brentq
from v8_utils import track

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};data=json.loads((p/'measurements-v8/feature-first-entry-v11-parent.json').read_text());rows=data['extension_931_1078']['records'];roles={'Email':'p0430','Calendar':'p0436','Reminders':'p0442','Automations':'p0448','Image Search':'p0454','Web':'p0460'};ratios={};fits=[]
    for role in roles:
        observed=[v['observed_height']/v['width']for r in rows for v in r['source_rows']if v['role_proposal']==role and not v['top_censored']and not v['bottom_censored']]
        ratios[role]=statistics.median(observed)
    for role,name in roles.items():
        poses=[]
        for r in rows:
            matches=[v for v in r['source_rows']if v['role_proposal']==role]
            if not matches:continue
            v=matches[0];b=v['bbox'];width=v['width'];left=b[0];censored=v['top_censored']or v['bottom_censored']
            if censored:
                # Visible width narrows at the rounded clipped cap. Recover its
                # full diameter from the authored elliptical corner, not by
                # treating a partial visible span as the entire card width.
                observed=v['observed_height'];ratio=ratios[role]
                def visible_span(full):
                    sx=full/1040;sy=full*ratio/222;rx=76*sx;ry=76*sy;cap=observed-24*sy if v['top_censored']else observed
                    if cap>=ry:return full
                    if cap<=0:return 0
                    return full-2*rx*(1-math.sqrt(max(0,1-((ry-cap)/ry)**2)))
                if visible_span(width)<width:
                    upper=width*1.3+100
                    if visible_span(upper)>width:width=brentq(lambda full:visible_span(full)-v['width'],width,upper)
                left=(b[0]+b[2]-width)/2
            height=width*ratios[role]if censored else v['observed_height'];top=b[3]-height if v['top_censored']else b[1]
            poses.append(dict(time=r['time'],x=left,y=top,scaleX=width/1040,scaleY=height/222));fits.append(dict(frame=r['frame'],role=role,raw_bbox=b,inferred_full_width=width,source_censored=censored,x=left,y=top,height=height))
        for prop in['x','y','scaleX','scaleY']:track(by[name],prop,poses)
        if role in['Automations','Image Search','Web']:
            g=by[name];g['start']=poses[0]['time'];g.setdefault('keyframes',{})['opacity']=[dict(t=g['start'],value=1)]+[k for k in g.get('keyframes',{}).get('opacity',[])if k['t']>g['start']]
    (p/'measurements-v8/feature-middle-fit-v11.json').write_text(json.dumps(dict(method='Exact raw native source931–1078body bounds. Uncensored role medians define full aspect. Censored rounded-cap width is recovered from editable76radius/1040width/222fullheight/24tail geometry; raw bounds retained. No frame shift: parent raw-vs-PNG988and513auditMAE0.',ratios=ratios,measurements=fits),indent=2))
    return scene
