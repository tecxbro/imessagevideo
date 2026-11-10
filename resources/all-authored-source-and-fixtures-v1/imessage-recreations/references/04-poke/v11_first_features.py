"""Independent first feature entry and shared material fade from native source."""
import json
from v8_utils import track

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};fps=scene['fps'];data=json.loads((p/'measurements-v8/feature-first-entry-v11-parent.json').read_text());roles={'Email':'p0430','Calendar':'p0436','Reminders':'p0442'};alpha=[dict(time=r['frame']/fps,opacity=r['approx_opacity_if_role_core26'])for r in data['faint_first_email_text']]
    for r in data['records']:
        items=r['feature_candidates'];email=next((v for v in items if v['role_by_vertical_order']=='Email'),None)
        if email is not None:alpha.append(dict(time=r['time'],opacity=max(0,min(1,email['opacity_from_role_normalized_black_core'] or email['opacity_from_body_gray']))))
    for role,name in roles.items():
        g=by[name];rows=[];ratio=data['later_full_height_width_ratios'][role]
        for r in data['records']:
            values=[v for v in r['feature_candidates']if v['role_by_vertical_order']==role]
            if not values:continue
            v=values[0];b=v['bbox'];width=v['width'];sx=width/1040;sy=width*ratio/222
            rows.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=sx,scaleY=sy))
        if role=='Email':
            # Flat gray fill is below codec quantization893–894; coherent blue
            # icon establishes the birth. Bound camera by the first full895pose.
            ratio=data['later_full_height_width_ratios'][role];early=[]
            for n,y in[(893,913),(894,889)]:early.append(dict(time=n/fps,x=298,y=y,scaleX=844/1040,scaleY=844*ratio/222))
            rows=early+rows
        g['start']=rows[0]['time']
        for prop in['x','y','scaleX','scaleY']:track(g,prop,rows)
        track(g,'opacity',alpha)
        # The authored path's full body+tail height is222. Preserve the measured
        # aspect between the new entry and independently fitted1079exit phase.
        for k in g['keyframes']['scaleY']:
            if 930/fps<k['t']<1079/fps:k['value']*=1040*ratio/222
