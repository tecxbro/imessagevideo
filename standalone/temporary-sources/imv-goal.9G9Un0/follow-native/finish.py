import csv, json, hashlib, math
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

work=Path(__file__).parent
root=Path('codex-trial/review/imv-v3/goal-audit')
scope={r['frame']:r for r in json.loads((work/'probe-scope.json').read_text())}
observations=json.loads((work/'analysis.json').read_text())
components_code=(work/'observe.py').read_text().split('def components(')[1].split('\nresult=[]')[0]
from scipy import ndimage
exec('def components('+components_code)

def read(label,f):
    return np.asarray(Image.open(work/label/f'{f:06d}.png').convert('RGB'))

def metric(a,b,roi):
    x,y,r,t=roi
    return round(float(np.abs(a[y:t,x:r].astype(np.int16)-b[y:t,x:r]).mean()),5)

def hard_rail(im,hints):
    out=[]
    for index,hint in enumerate(hints):
        center=round(hint)
        values=[]
        for y0,y1 in [(360,460),(740,840),(1500,1580)]:
            roi=im[y0:y1,center-65:center+65].max(2)
            valid=np.flatnonzero((roi<90).mean(0)>.4)
            if len(valid):
                values.append(center-65+int(valid[0] if index==0 else valid[-1])+index)
        out.append(float(np.median(values)) if len(values)==3 else None)
    return out

def add_xy(row,role,tips):
    for k,axis in enumerate('xy'):
        row[f'{role}_tip_{axis}']=tips[k] if tips else None

rows=[]
for state in observations:
    f=state['frame']
    row=dict(frame=f,source_pts_s=f'{f/25:.2f}',scope='follow' if f<=695 else 'after cut')
    rows.append(row)
    if f in scope:
        row['probe_native_changed']=scope[f]['changedNativePixels']
    if 'source' not in state:continue
    images={label:read(label,f) for label in ['source','pre2000','encoded']}
    for label in images:
        rail=state[label]['rail']
        patch=images[label][935:1190,839:872].astype(float)
        chroma=np.median(patch[:,:,2]-patch[:,:,1],axis=1)
        strength=float(chroma.max())
        rows_in_half_chroma=np.flatnonzero(chroma>=strength/2)
        row.update({f'{label}_yes_band_upper':935+int(rows_in_half_chroma[0]),
                    f'{label}_yes_band_lower':935+int(rows_in_half_chroma[-1]),
                    f'{label}_yes_band_peak_blue_minus_green':strength})
        hard=hard_rail(images[label],state['railOuter'])
        for i,side in enumerate(['left','right']):
            row.update({f'{label}_{side}':rail[i]['x'],f'{label}_{side}_band_spread':rail[i]['bandSpread'],
                        f'{label}_{side}_edge20to80':rail[i]['edgeWidth20to80'],f'{label}_{side}_hard90':hard[i]})
        pointer=state[label]['pointer'][1]
        add_xy(row,label,pointer['tip'] if pointer else None)
        row[f'{label}_dark_area']=pointer['area'] if pointer else None
    row.update(eval_rail_left=state['railOuter'][0],eval_rail_right=state['railOuter'][1],
               eval_phone_top=state['phoneTop'],eval_phone_scale=state['phoneScale'],eval_phone_blur=state['phoneBlur'],eval_phone_vertical_smear=state['phoneSmear'],
               eval_yes_left=state['yesBounds'][0],eval_yes_top=state['yesBounds'][1],eval_yes_right=state['yesBounds'][2],eval_yes_bottom=state['yesBounds'][3],
               eval_cursor_scale=state['cursorScale'],eval_cursor_opacity=state['cursorOpacity'])
    add_xy(row,'eval_pivot',state['cursorPivot'])
    if 674<=f<=694:
        r0=state['source']['pointer'][1]
        r1=state['pre2000']['pointer'][1]
        x0,y0,x1,y1=[min(r0['bbox'][0],r1['bbox'][0])-15,min(r0['bbox'][1],r1['bbox'][1])-12,max(r0['bbox'][2],r1['bbox'][2])+15,max(r0['bbox'][3],r1['bbox'][3])+15]
        roi=(x0,y0,x1,y1)
        x,y=r0['tip']
        probe={label:read(label,f) for label in ['probe-pre','probe-encoded']}
        row['probe_roi_xyxy']=','.join(map(str,roi))
        row['roi_source_vs_pre']=metric(images['source'],images['pre2000'],roi)
        row['roi_source_vs_encoded']=metric(images['source'],images['encoded'],roi)
        for label,im in probe.items():
            side='probe_pre' if label=='probe-pre' else 'probe_encoded'
            p=components(im,roi,(x,y),110)
            add_xy(row,side,p['tip'] if p else None)
            row[f'roi_source_vs_{side}']=metric(images['source'],im,roi)
            for i,landmark in enumerate('xy'):
                if p:row[f'{side}_tip_{landmark}_abs_error']=abs(p['tip'][i]-r0['tip'][i])
            if p:row[f'{side}_tip_error']=math.dist(p['tip'],r0['tip'])
        row['baseline_pre_tip_error']=math.dist(r1['tip'],r0['tip'])
    if f==695:
        # Fixed region below the visibly separate colored Yes glyph and above the blank transcript.
        roi=(942,1101,1001,1151)
        x0,y0,x1,y1=roi
        src=images['source'][y0:y1,x0:x1].mean(2)
        row['695_weak_source_visible_roi']=','.join(map(str,roi))
        row['695_weak_source_min_luma']=round(float(src.min()),2)
        row['695_weak_source_luma_below_185_pixels']=int((src<185).sum())

fields=list(dict.fromkeys(k for row in rows for k in row))
with (root/'sidehoe-follow-native.csv').open('w',newline='') as stream:
    table=csv.DictWriter(stream,fieldnames=fields)
    table.writeheader()
    table.writerows(rows)

by_frame={r['frame']:r for r in rows}
valid=[r for r in rows if 'probe_pre_tip_error' in r]
moving=[r for r in rows if 675<=r['frame']<=695]
early=moving[:15]
summary=dict(passed_identical_cache_controls=[r['frame'] for r in rows if r.get('probe_native_changed')==0],
    source_vs_pre_width_delta_early=[round(float(fn([(r['pre2000_right']-r['pre2000_left'])-(r['source_right']-r['source_left']) for r in early])),2)for fn in [min,np.median,max]],
    rail_pre_to_encoded_max=max(abs(r['pre2000_'+side]-r['encoded_'+side])for r in moving for side in ['left','right']),
    rail_eval_to_pre_max=max(abs(r['eval_rail_'+side]-r['pre2000_'+side])for r in moving for side in ['left','right']),
    pointer_pre_to_encoded_max=max(math.dist([r['pre2000_tip_x'],r['pre2000_tip_y']],[r['encoded_tip_x'],r['encoded_tip_y']]) for r in moving),
    probe_before_after_mean_tip=[float(np.mean([r[k] for r in valid])) for k in ['baseline_pre_tip_error','probe_pre_tip_error']],
    probe_before_after_max_tip=[max(r[k] for r in valid) for k in ['baseline_pre_tip_error','probe_pre_tip_error']],
    probe_before_after_mean_roi=[float(np.mean([r[k] for r in valid])) for k in ['roi_source_vs_pre','roi_source_vs_probe_pre']],
    probe_roi_counts=[sum(comparison(r['roi_source_vs_pre'],r['roi_source_vs_probe_pre']) for r in valid)for comparison in [lambda a,b:b<a,lambda a,b:b==a,lambda a,b:b>a]],
    probe_encoded_measured=len([r for r in valid if 'probe_encoded_tip_error' in r]),
    probe_native_changed_frames=[r['frame'] for r in rows if r.get('probe_native_changed',0)>0])
print(json.dumps(summary,indent=2))
for f in [674,675,683,689,690,691,692,693,694,695]:
    r=by_frame[f]
    print({k:r.get(k) for k in ['frame','source_left','source_right','source_left_hard90','source_right_hard90','pre2000_left_hard90','pre2000_right_hard90','source_left_edge20to80','pre2000_left_edge20to80','source_tip_y','pre2000_tip_y','probe_pre_tip_y','roi_source_vs_pre','roi_source_vs_probe_pre','695_weak_source_min_luma','695_weak_source_luma_below_185_pixels']})
(work/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

for index in range(3):
    start=672+index*8
    bs=Image.new('RGB',(810,8*220),'#eee')
    draw=ImageDraw.Draw(bs)
    for row,f in enumerate(range(start,start+8)):
        state=observations[f-672]
        if f<=694 and state['source']['pointer'][1]:
            x,y=state['source']['pointer'][1]['tip']
        else:
            x,y=955,1110
        box=(round(x)-85,round(y)-62,round(x)+185,round(y)+136)
        for j,tag in enumerate(['source','pre2000','probe-pre' if f in scope else 'encoded']):
            label={'source':'source','pre2000':'baseline pre-encode','probe-pre':'pose-only probe','encoded':'baseline encoded'}[tag]
            x0=j*270;y0=row*220
            im=Image.open(work/tag/f'{f:06d}.png').crop(box)
            bs.paste(im,(x0,y0+18))
            draw.text((x0+3,y0+2),f'{f} {label}',fill='black')
    bs.save(work/f'pointer-contact-{index+1}.png')
