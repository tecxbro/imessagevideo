"""Apply measured15-disc poses, preserving every nonportrait layer by ID."""
from pathlib import Path
import copy,json,argparse,hashlib
P=Path(__file__).parent;B=P/'portrait-helper-v18';IDS={f'rene-final11-group-{n}'for n in range(71,96,2)}
def build_layers(results,scene):
 originals={l['id'].split('-')[-1]:copy.deepcopy(l)for l in scene['layers']if l['id']in IDS}
 for id,g in originals.items():
  for c in g['children']:
   if c.get('src')and not Path(c['src']).is_absolute():c['src']=str((P/c['src']).resolve())
 for q in json.load(open(B/'new-portrait-provenance.json')):
  path=Path(q['src']).resolve();from PIL import Image
  w,h=Image.open(path).size;originals[q['id']]={'id':'rene-portrait-'+q['id'],'type':'group','children':[{'id':'rene-portrait-image-'+q['id'],'type':'image','src':str(path),'width':w,'height':h}],'provenance':q}
 byframe={}
 for id,rs in results.items():
  for r in rs:byframe.setdefault(r['frame'],{})[id]=r
 segments=[]
 for f,rs in sorted(byframe.items()):
  order=tuple(sorted(rs,key=lambda id:(rs[id]['diameter'],id)))
  if segments and segments[-1]['order']==order and segments[-1]['frames'][-1]+1==f:segments[-1]['frames'].append(f)
  else:segments.append({'order':order,'frames':[f]})
 layers=[]
 for seg in segments:
  fs=seg['frames'];first,last=fs[0],fs[-1]
  for id in seg['order']:
   g=originals[id];child=copy.deepcopy(g['children'][0]);w,h=child['width'],child['height'];child.update(x=0,y=0,id=f'rene-portrait-v18-{first}-{id}-image');tracks={k:[]for k in ['x','y','scaleX','scaleY','opacity','blur']}
   for f in fs:
    r=byframe[f][id];D=r['diameter'];blur=r['blurFraction'];visible=D>0 and r['cx']+D*(.5+4*blur)>0 and r['cx']-D*(.5+4*blur)<1920 and r['cy']+D*(.5+4*blur)>0 and r['cy']-D*(.5+4*blur)<1080
    for k,v in [('x',r['cx']-D/2),('y',r['cy']-D/2),('scaleX',max(.001,D/w)),('scaleY',max(.001,D/h)),('opacity',r['opacity'] if visible else 0),('blur',blur*w)]:tracks[k].append({'t':f/30,'value':v,'ease':'hold'if k=='opacity'else'linear'})
   layers.append({'id':f'rene-portrait-v18-{first}-{id}','type':'group','start':first/30,'end':(last+1)/30,'children':[child],'keyframes':tracks,'shadow':{'x':0,'y':w*.06,'blur':w*.06,'color':'#00000022'},'semanticPhotoId':g['id'],'editability':'Independent static original photographed disc with native measured camera/blur/opacity. Segment lifetime changes only native draw order as actual depth changes.','provenance':g.get('provenance',{'kind':'Original bounded portrait photo from existing source provenance.'})})
 return layers

def apply_portraits(scene,results):
 s=copy.deepcopy(scene);new=build_layers(results,s);count=sum(l['id']in IDS for l in s['layers']);assert count==13,count;at=next(i for i,l in enumerate(s['layers'])if l['id']in IDS);s['layers']=[l for l in s['layers']if l['id']not in IDS];s['layers'][at:at]=new;s['source']['notes']+=' Fifteen independent static original portrait photos with native measured perspective/depth camera and blur603–688. Two absent identities restored; diameter-based depth order replaces incorrect fixed layering. No original source frame/video is an output layer. Low-visibility camera priors are explicitly measured/inferred in the portrait helper evidence.';return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=P/'scene.json');p.add_argument('--poses',type=Path,default=B/'camera-fit.json');p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.load(open(a.input))
 def absolute(ls):
  for l in ls:
   if l.get('src')and not l['src'].startswith(('data:','http:','https:','/')):l['src']=str((a.input.parent/l['src']).resolve())
   absolute(l.get('children',[]))
 absolute(s['layers'])
 for font in s.get('fonts',[]):
  if not font['src'].startswith(('data:','http:','https:','/')):font['src']=str((a.input.parent/font['src']).resolve())
 s=apply_portraits(s,json.load(open(a.poses)));a.output.write_text(json.dumps(s,indent=2)+'\n');print(a.output)
