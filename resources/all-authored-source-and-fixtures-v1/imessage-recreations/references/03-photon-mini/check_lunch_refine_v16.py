from measure_lunch_refinement_v16 import *
frames=list(range(541,618))+list(range(735,800));records=[]
for f in frames:
 s=source(f).astype(float);a=np.array(Image.open(P.parent.parent/f'outputs/03-photon-mini/frames-gsap/{f:06}.png').convert('RGB'),float)
 name=str(f//30) if f%30==0 else str(f/30);b=np.array(Image.open(P/f'lunch-refine-joint-v16-dense/{name}.png').convert('RGB'),float)
 old=float(np.abs(s-a).mean());new=float(np.abs(s-b).mean());records.append(dict(frame=f,before=old,after=new,delta=new-old))
controls=[]
for f in [540,618,734,800]:
 name=str(f//30) if f%30==0 else str(f/30);b=np.array(Image.open(P/f'lunch-refine-joint-v16-dense/{name}.png').convert('RGB'),float);a=np.array(Image.open(P.parent.parent/f'outputs/03-photon-mini/frames-gsap/{f:06}.png').convert('RGB'),float)
 controls.append(dict(frame=f,pixel_mae=float(abs(b-a).mean()),maximum=float(abs(b-a).max())))
r=dict(scope=[[541,617],[735,799]],frames=len(records),mean_before=float(np.mean([r['before'] for r in records])),mean_after=float(np.mean([r['after'] for r in records])),maximum_after=max(records,key=lambda r:r['after']),regressions=[r for r in records if r['delta']>0.00001],records=records,controls=controls)
(P/'lunch-refine-v16-native-metrics.json').write_text(json.dumps(r,indent=2))
print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2))
print('top',sorted(records,key=lambda r:r['after'],reverse=True)[:12])
