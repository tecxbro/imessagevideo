"""Single-frame Alice camera glitch and first visible group-title lifecycle."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
from scipy.optimize import least_squares
import copy,json,numpy as np
R=Path('/workspace/imessage-recreations');REF=R/'references/03-photon-mini';P=R/'verification/fidelity-review/03-peaks';BASE=R/'outputs/03-photon-mini/final-v14';scene=json.load(open(BASE/'scene.json'))
def state(layer,time):
    result={key:value for key,value in layer.items() if key not in ['children','keyframes']}
    for key,keys in layer.get('keyframes',{}).items():
        if time<=keys[0]['t']:
            result[key]=keys[0]['value']
            continue
        for left,right in zip(keys,keys[1:]):
            if time<=right['t']:
                ratio=(time-left['t'])/(right['t']-left['t'])
                result[key]=left['value']+(right['value']-left['value'])*ratio
                break
        else:
            result[key]=keys[-1]['value']
    return result

def rename(layer,prefix):
    layer=copy.deepcopy(layer)
    def walk(node):
        node['id']=prefix+node['id']
        if node.get('src') and not node['src'].startswith(('/','data:','http:')):
            node['src']=str((BASE/node['src']).resolve())
        for child in node.get('children',[]):
            walk(child)
    walk(layer)
    return layer

ui=next(layer for layer in scene['layers'] if layer['id']=='measured-entrance-ui-v13')
reference=state(ui,439/30)
# Both first T top bars are completely visible, despite lower word clipping.
def first_t(file):
    pixels=np.array(Image.open(file).convert('RGB'))
    labels,count=ndimage.label(pixels[930:1080,:600].max(2)<80)
    candidates=[]
    for index,box in enumerate(ndimage.find_objects(labels),1):
        if box is None:continue
        yy,xx=box
        area=int((labels[box]==index).sum())
        if area>100:candidates.append(dict(x=xx.start,y=930+yy.start,width=xx.stop-xx.start,height=yy.stop-yy.start,area=area))
    return min(candidates,key=lambda row:row['x'])
source_t=first_t(P/'source-438/0009.png');native_t=first_t(P/'baseline-v14/000439.png');scale=source_t['width']/native_t['width'];dx=source_t['x']-scale*native_t['x'];dy=source_t['y']-scale*native_t['y']
children=[rename(layer,'mini-review-caption-') for layer in ui['children'] if layer['id'] in ['entrance-entrance-header-title','entrance-entrance-header-chevron']]
caption=dict(id='mini-review-caption-438',type='group',x=scale*reference.get('x',0)+dx,y=scale*reference.get('y',0)+dy,scaleX=scale*reference.get('scaleX',1),scaleY=scale*reference.get('scaleY',1),start=438/30,end=439/30,children=children)

parent=next(layer for layer in scene['layers'] if layer['id']=='measured-entrance-avatar-clip-v13');old=next(layer for layer in parent['children'] if layer['id']=='entrance-avatar-alice');parent_pose=state(parent,438/30);old_pose=state(old,438/30)
fits=json.load(open(P/'alice-left-edge-fits.json'));fit=next(row for row in fits if row['frame']==438);target=fit['source'];current=fit['native'];ratio=target['radius']/current['radius'];global_x=parent_pose.get('x',0)+parent_pose.get('scaleX',1)*old_pose.get('x',0);global_y=parent_pose.get('y',0)+parent_pose.get('scaleY',1)*old_pose.get('y',0)
new_x=target['cx']-ratio*current['cx']+ratio*global_x;new_y=target['cy']-ratio*current['cy']+ratio*global_y
alice=rename(old,'mini-review-alice-');alice.pop('keyframes',None);alice.update(x=(new_x-parent_pose.get('x',0))/parent_pose.get('scaleX',1),y=(new_y-parent_pose.get('y',0))/parent_pose.get('scaleY',1),scaleX=old_pose.get('scaleX',1)*ratio,scaleY=old_pose.get('scaleY',1)*ratio,start=438/30,end=439/30)
old_end=old.get('end',scene['duration']);gate=[dict(t=437/30,value=old_end,ease='hold'),dict(t=438/30,value=438/30,ease='hold'),dict(t=439/30,value=old_end,ease='hold')]
spec=dict(changed_ranges=[[438,438]],insert_before_root={'measured-entrance-avatar-clip-v13':[caption]},append_children={'measured-entrance-avatar-clip-v13':[alice]},gate_ends={'entrance-avatar-alice':gate},provenance=dict(caption='First visible Team Lunch header arrived at438 while the whole UI parent was still opacity0. Reuse existing semantic title/chevron native paths under an independently fitted camera, below avatars. Only438;439+ accepted states preserved.',titleFit=dict(sourceT=source_t,nativeReferenceT=native_t,scale=scale,dx=dx,dy=dy),alice='A one-frame independent pose outlier, not a different portrait asset. Source uncontaminated peach left arc radius249 versus native216.8; source437/439 are already strong. Correct the whole existing native-circle/genuine-portrait actor together.',aliceFit=fit,portraitScaleCorrection=ratio,limitations='Minor437 chevron first-pixel sliver remains unchanged rather than opening a strong adjacent state. Native source AA residuals remain.'))
# The whole avatar cluster is itself still inside a circular aperture at438.
# Its lower-right arc clips the robot; the old 10000px aperture lost that edge.
pixels=np.asarray(Image.open(P/'source-438/0009.png').convert('RGB')).astype(float)
teal=(pixels[:,:,1]-pixels[:,:,0]>7)&(pixels[:,:,2]-pixels[:,:,0]>7)&(pixels[:,:,1]>140)&(pixels[:,:,2]>140)
points=[]
for yy in range(820,1020):
    xx=np.where(teal[yy,1250:1700])[0]
    if len(xx):points.append([int(xx.max()+1250),yy])
points=np.asarray(points)
circle=least_squares(lambda pose:np.sqrt(((points-pose[:2])**2).sum(1))-pose[2],[980,580,580])
cx,cy,radius=map(float,circle.x)
private_parent=rename(parent,'mini-review-aperture-')
private_parent.pop('keyframes',None)
private_parent.update({key:parent_pose[key]for key in ['x','y','scaleX','scaleY']})
private_parent['children']=[child for child in private_parent['children']if child['id']!='mini-review-aperture-entrance-avatar-alice']+[alice]
outer=dict(id='mini-review-cluster-aperture-438',type='group',start=438/30,end=439/30,clip=dict(x=cx-radius,y=cy-radius,width=2*radius,height=2*radius,radius=radius),children=[private_parent])
parent_end=parent.get('end',scene['duration'])
spec['gate_ends']={'measured-entrance-avatar-clip-v13':[dict(t=437/30,value=parent_end,ease='hold'),dict(t=438/30,value=438/30,ease='hold'),dict(t=439/30,value=parent_end,ease='hold')]}
spec['append_children']={}
spec['insert_before_root']={'measured-entrance-avatar-clip-v13':[caption,outer]}
spec['provenance']['clusterAperture']=dict(cx=cx,cy=cy,radius=radius,edgeResidual=float(np.sqrt((circle.fun**2).mean())),native='One-frame native circular clip; all genuine portrait actors retained.')
(REF/'peaks-review-avatar-elements.json').write_text(json.dumps(spec,indent=2));print(json.dumps(spec['provenance'],indent=2))
