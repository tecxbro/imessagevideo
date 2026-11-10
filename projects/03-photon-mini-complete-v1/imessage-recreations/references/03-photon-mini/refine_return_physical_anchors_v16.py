from measure_lunch_refinement_v16 import *
p=P/'return-camera-v16-measurements.json';data=json.loads(p.read_text());rows=data['frames'];device=root('measured-lunch-device-v13')
def runs(a):
 out=[]
 for y in np.where(a)[0]:
  if out and y==out[-1][1]+1:out[-1][1]=int(y)
  else:out.append([int(y),int(y)])
 return out
def pill(im,center):
 a=im[:180,int(center-35):int(center-20)].max(2);rs=runs(np.mean(a<30,axis=1)>.65);rs=[v for v in rs if v[1]-v[0]+1>20]
 if len(rs)!=1:return None,rs
 return (rs[0][0]+rs[0][1]+1)/2,rs
cal=next(r for r in rows if r['frame']==738);old=matrix(device,738);center=old[0,2]+400*old[0,0]
c=np.array(Image.open(P.parent.parent/'outputs/03-photon-mini/frames-gsap/000738.png').convert('RGB'));pc,pr=pill(c,center)
cp=(pc-old[1,2])/old[1,1];cb=(cal['native_anchors']['bottom']-old[1,2])/old[1,1];canonical_height=(pr[0][1]-pr[0][0]+1)/old[1,1]
for r in rows:
 f=r['frame'];old=matrix(device,f);center=old[0,2]+400*old[0,0];pc,pr=pill(source(f),center)
 if pc is None:raise ValueError((f,pr))
 censored=pr[0][0]==0
 if censored:
  # Visible bottom is observed; full capsule height is projected from independently observed body width.
  pc=pr[0][1]+.5-canonical_height*r['scale_x']/2
 bottom=r['source_anchors']['bottom'];sy=(bottom-pc)/(cb-cp);y=pc-sy*cp
 r.update(physical_matrix=[[r['scale_x'],0,r['position_x']],[0,sy,y],[0,0,1]],aperture_measurement=dict(source_runs=pr,source_center=pc,top_censored=censored,canonical_center=cp,canonical_bottom=cb,canonical_height=canonical_height,notice='Unoccluded left-centre capsule band excludes lens and the independently moving Order chip. Top-clipped735/736 centres use observed capsule bottom and projected height, not the midpoint of a clipped run.'))
 print(f,r['physical_matrix'],r['aperture_measurement']['source_runs'],r['scrim_alpha'])
p.write_text(json.dumps(data,indent=2))
