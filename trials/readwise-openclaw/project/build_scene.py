#!/usr/bin/env python3
"""Build the editable Part A film. No reference frames/audio are consumed."""
import json
from pathlib import Path
import components as C
import shots

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def load(name):
    return json.loads((HERE/name).read_text())

def build(copy, timing):
    fps=timing['fps'];frames=timing['frames'];cuts=timing['cuts']
    assets=ROOT/'resources/font-inputs-and-linux-fallbacks-v1/imessage-recreations/references/01-photonhq/assets'
    sf=ROOT/'resources/font-inputs-and-linux-fallbacks-v1/imessage-recreations/shared/fonts'
    fonts={'Title':str(assets/'Inter-600.ttf'),'UI':str(sf/'SF-Pro-Text-Regular.otf'),
           'UIBold':str(sf/'SF-Pro-Text-Semibold.otf'),
           'Brand':'/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
           'Article':'/System/Library/Fonts/Supplemental/Georgia Italic.ttf'}
    for p in fonts.values():
        if not Path(p).exists():raise FileNotFoundError(f'Required local font missing: {p}')
    C.configure(fonts,fps)
    black=cuts['black_tail'][0]
    scene={'title':'Readwise / OpenClaw — complete editable film','width':1920,'height':1080,'fps':fps,'duration':frames/fps,'background':'#000000',
           'source':{'notes':'Editable measured reconstruction. Source media is never consumed by builder. 2D rotation/scale approximates perspective; studio silhouette, predictions, doodles, avatar, camera anchors and brand curl are approximations; see README.'},
           'fonts':[{'family':k,'src':v,'weight':600 if k in ['Title','UIBold'] else 700 if k=='Brand' else 400} for k,v in fonts.items()],
           'gradients':[
               {'id':'studio-curtain','type':'linear','x1':'0%','y1':'0%','x2':'100%','y2':'30%','stops':[{'offset':'0%','color':'#06070B'},{'offset':'45%','color':'#282932'},{'offset':'100%','color':'#07080D'}]},
               {'id':'background-base','type':'linear','x1':'0%','y1':'15%','x2':'100%','y2':'25%','stops':[{'offset':'0%','color':'#000000'},{'offset':'100%','color':'#3B3B68'}]},
               {'id':'background-pink','type':'linear','x1':'10%','y1':'0%','x2':'85%','y2':'100%','stops':[{'offset':'0%','color':'#12101F','opacity':0},{'offset':'52%','color':'#292544','opacity':.14},{'offset':'100%','color':'#8D2C7E','opacity':.93}]},
               {'id':'icon-dark','type':'linear','x1':'0%','y1':'0%','x2':'100%','y2':'100%','stops':[{'offset':'0%','color':'#33394E'},{'offset':'100%','color':'#080E21'}]},
               {'id':'page-blue','type':'linear','x1':'0%','y1':'100%','x2':'100%','y2':'0%','stops':[{'offset':'0%','color':'#5120D9'},{'offset':'35%','color':'#5067FF'},{'offset':'60%','color':'#46D2F2'},{'offset':'100%','color':'#3D4DCF'}]}], 'layers':[]}
    layers=scene['layers'];layers.append(C.background(copy,cuts['S7'][0],black,frames))
    layers+=shots.build(copy,timing,fps)
    for key in ['S1','S5']:
        layers+=C.title(key,copy['titles'][key],timing['typing'][key],86,486)
    layers+=C.title('end-command',copy['command']['install'],timing['typing']['install'],58,643)
    icon=C.app_icon('readwise-vector-icon',copy.get('brand',{}).get('mark','R'))
    icon.update(x=860,y=365,originX=100,originY=100,keyframes={
        'opacity':[{'t':timing['end_icon']['start']/fps,'value':0},{'t':timing['end_icon']['first_changed']/fps,'value':.03},{'t':timing['end_icon']['settled']/fps,'value':1}],
        'scaleX':[{'t':timing['end_icon']['start']/fps,'value':.94},{'t':timing['end_icon']['settled']/fps,'value':1}],
        'scaleY':[{'t':timing['end_icon']['start']/fps,'value':.94},{'t':timing['end_icon']['settled']/fps,'value':1}]})
    layers.append(C.life(icon,cuts['S7'][0],timing['end_icon']['end']))
    phone=C.phone_shell(copy)
    screen=[C.rect('screen-black',12,12,426,925,'#020204',61),C.doodles()]
    # Chat stages are independently editable snapshots at stream/send boundaries.
    start,end=cuts['S6']
    events=sorted({start,end,*[s['frame'] for s in timing['sends'].values()],*[s['frame'] for stages in timing['streams'].values() for s in stages]})
    for i,(a,b) in enumerate(zip(events,events[1:])):
        items=[]
        if a<timing['sends']['user1']['frame']:continue
        items.append(('date',None))
        for key in ['user1','bot1','user2','bot2']:
            if key.startswith('user'):
                if a<timing['sends'][key]['frame']:continue
                lines=copy['drafts'][key]['bubble_lines'];bold=[];out=True
            else:
                chunks=[s for s in timing['streams'][key] if s['frame']<=a]
                if not chunks:continue
                lines=copy['replies'][key]['text'][:chunks[-1]['count']].split('\n')
                bold=copy['replies'][key]['bold'];out=False
            if key=='bot1':items.append(('unread',None))
            item,h=C.bubble(f'chat-stage-{i}-{key}',lines,bold,out,copy['timestamps'][key])
            if out and a==timing['sends'][key]['frame']:
                item['keyframes']={'y':[{'t':a/fps,'value':20},{'t':timing['sends'][key]['settled']/fps,'value':0,'ease':'easeOut'}]}
            items.append((item,h))
        total=sum((h+12 if h else 32) for _,h in items)
        y=516-total;children=[]
        for item,h in items:
            if item=='unread':
                children += [C.rect(f'unread-bar-{i}',12,y,426,25,'#1D1822',opacity=.85),C.text(f'unread-label-{i}',copy['header']['unread'],225,y+5,13,'#C9A9ED',textAnchor='middle')]
                y+=32
            elif item=='date':
                children += [C.rect(f'date-pill-{i}',195,y,60,24,'#251D29',12),C.text(f'date-copy-{i}',copy['header']['today'],225,y+4,14,textAnchor='middle')]
                y+=32
            else:
                item['y']=y
                if 'keyframes' in item:
                    for k in item['keyframes']['y']:k['value']+=y
                children.append(item);y+=h+12
        group=C.group(f'chat-stage-{i}',children,clip={'x':12,'y':127,'width':426,'height':390})
        active=next((s for stages in timing['streams'].values() for s in stages if s['frame']==a),None)
        if active:
            group['keyframes']={'y':[{'t':a/fps,'value':10},{'t':active['settled']/fps,'value':0,'ease':'easeOut'}],
                                'opacity':[{'t':a/fps,'value':.8},{'t':active['settled']/fps,'value':1}]}
        screen.append(C.life(group,a,b))
    # Clipped keyboard is retained during both whole-phone reading holds.
    switches=timing['keyboard_switches']
    bounds=sorted({start,end,*[s['frame'] for s in switches],*[s['frame'] for s in timing['keyboard_case']]})
    for i,(a,b) in enumerate(zip(bounds,bounds[1:])):
        layout=next(s['layout'] for s in reversed(switches) if s['frame']<=a)
        upper=next(s['upper'] for s in reversed(timing['keyboard_case']) if s['frame']<=a)
        k=C.keyboard(copy,layout,upper);k['id']+=f'-state{i}'
        # Child IDs must be unique even for repeated layout instances.
        def unique(node):
            node['id']+=f'-instance{i}'
            for c in node.get('children',[]):unique(c)
        unique(k)
        k['y']=-10
        screen.append(C.life(k,a,b))
    pred=[{'frame':start,'labels':copy['keyboard']['default_suggestions']},
          *[dict(s,labels=copy['keyboard']['suggestion_sets'][s['copy_id']]) for s in timing['suggestions']]]
    pred=sorted([p for p in pred if start<=p['frame']<end],key=lambda p:p['frame'])
    # A send restores the keyboard's idle predictions.
    pred.extend({'frame':s['frame'],'labels':copy['keyboard']['default_suggestions']} for s in timing['sends'].values())
    pred.sort(key=lambda p:p['frame'])
    for i,p in enumerate(pred):
        stop=pred[i+1]['frame'] if i+1<len(pred) else end
        labels=p['labels']
        if len(labels)==2 and labels[0]=='the':labels=copy['keyboard']['default_suggestions']
        if p['frame']<stop:
            bar=C.predictions(f'predictions-{i}',labels);bar['y']=-10
            screen.append(C.life(bar,p['frame'],stop))
    drafts=[]
    for key in ['user1','user2']:
        t=timing['typing'][key]
        for i,birth in enumerate(t['births']):
            stop=t['births'][i+1]['frame'] if i+1<len(t['births']) else timing['sends'][key]['frame']
            drafts.append((birth['frame'],stop,key,birth['count']))
    boundaries=sorted({start,end,*[f for a,b,_,_ in drafts for f in [a,b]]})
    blink=timing['caret'];caret=[{'t':f/fps,'value':1 if f%blink['period_frames']<blink['on_frames'] else 0,'ease':'hold'} for f in range(start,end)]
    for i,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
        draft=next((d for d in drafts if d[0]<=a<d[1]),None)
        if draft:
            _,_,key,count=draft;entry=copy['drafts'][key];value=entry['text'][:count];lines=entry['lines']
        else:value='';lines=[]
        comp,_=C.composer(f'composer-{i}',value,lines,copy,a,b,caret,a<timing['sends']['user1']['frame'])
        comp['y']=-10
        screen.append(comp)
    screen+=C.phone_chrome(copy,timing)
    phone.append(C.group('phone-screen-clipped',screen,clip={'x':12,'y':12,'width':426,'height':925,'radius':60}))
    camera=C.group('phone-camera',phone,keyframes={name:[{'t':k['frame']/fps,'value':k[prop]} for k in timing['camera']] for name,prop in [('x','x'),('y','y'),('scaleX','scale'),('scaleY','scale')]})
    layers.append(C.life(camera,start,end))
    return scene

if __name__=='__main__':
    scene=build(load('copy.json'),load('timing.json'))
    out=HERE/'build';out.mkdir(exist_ok=True)
    (out/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':'))+'\n')
    print(f'Built {out / "scene.json"}: {round(scene["fps"]*scene["duration"])} frames, all seven shots, editable vectors/text.')
