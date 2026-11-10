from pathlib import Path
import json,copy
R=Path(__file__).resolve().parent
chat=json.loads((R/'group-1118.json').read_text())
nodes={node['id']:node for node in chat['children']}
original=nodes['middle-reaction-command-like']
budget=nodes['middle-message-budget']
def sample(node,key,frame):
    keys=node.get('keyframes',{}).get(key,[])
    time=frame/30
    if not keys:return node.get(key,1 if key.startswith('scale')else 0)
    if time<=keys[0]['t']:return keys[0]['value']
    for before,after in zip(keys,keys[1:]):
        if time<=after['t']:
            fraction=(time-before['t'])/(after['t']-before['t'])
            return before['value']+(after['value']-before['value'])*fraction
    return keys[-1]['value']
anchor=815
ratio=sample(original,'scaleX',anchor)/sample(budget,'scaleX',anchor)
x_offset=sample(original,'x',anchor)-sample(budget,'x',anchor)
y_offset=(sample(original,'y',anchor)-sample(budget,'y',anchor))/sample(budget,'scaleX',anchor)
replacement=copy.deepcopy(original)
measurements=[]
for frame in range(816,822):
    scale=sample(budget,'scaleX',frame)
    pose={'x':sample(budget,'x',frame)+x_offset,'y':sample(budget,'y',frame)+y_offset*scale,'scaleX':scale*ratio,'scaleY':scale*ratio}
    for key,value in pose.items():replacement['keyframes'][key].append({'t':frame/30,'value':value})
    measurements.append({'frame':frame,**pose})
replacement['end']=822/30
spec={'base':'outputs/02-danieltian/final-v16/scene.json','id':original['id'],'replacement':replacement,'changedFrames':list(range(816,822)),'measurements':measurements,'diagnosis':'Reaction tracks inherited from the Airbnb command stop815 when the parent body leaves. The reaction is offset lower, so it must continue under the authoritative still-visible Budget camera. Yellow thumb ends817, but neutral connector dots remain through821; old end819 omitted their last states. Original art and all earlier poses retained.'}
(R/'reaction-clip-candidate.json').write_text(json.dumps(spec,separators=(',',':')))
print(json.dumps({'anchor':anchor,'scaleRatio':ratio,'worldYOffset':y_offset,'poses':measurements},indent=2))
