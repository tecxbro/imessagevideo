"""Separate favorites, inbox rows, device and typed preview from exact source data."""
import copy,json
from v8_utils import at,track,flat
FPS=30000/1001

def text(identifier,value,x,y,size=40,fill='#000000',weight=400,**kw):
    return dict(id=identifier,type='text',text=value,x=x,y=y,fontSize=size,fontFamily='SF Pro Display',fontWeight=weight,fill=fill,**kw)
def apply(scene,p):
    by={l['id']:l for l in scene['layers']};end=142/FPS
    raw=json.loads((p/'measurements-v8/intro-pose-fit.json').read_text())['measurements']
    oldlogo=copy.deepcopy(by['p0014'])
    for id,field in [('p0007','braden_pose'),('p0010','sydney_pose')]:
        l=by[id];rows=[dict(r[field],time=r['time']) for r in raw if r.get(field)]
        for prop in ['x','y','opacity']:track(l,prop,rows)
        for prop in ['scaleX','scaleY']:track(l,prop,rows,'scale')
        l['end']=end
    poses=[dict(r['poke_pose'],time=r['time'])for r in raw if r.get('poke_pose')]
    for id in ['p0012','p0014']:
        l=by[id]
        for prop in ['x','y']:track(l,prop,poses)
        for prop in ['scaleX','scaleY']:track(l,prop,poses,'scale')
        if id=='p0014':l['end']=end
    for id in ['p0015','p0016']:
        l=by[id];saved=copy.deepcopy(l);l['end']=end;rows=[]
        for r in poses:
            t=r['time'];ratio=r['scale']/at(oldlogo,'scaleX',t)
            rows.append(dict(time=t,x=r['x']+(at(saved,'x',t)-at(oldlogo,'x',t))*ratio,
                y=r['y']+(at(saved,'y',t)-at(oldlogo,'y',t))*ratio,
                fontSize=at(saved,'fontSize',t)*ratio,
                scaleX=at(saved,'scaleX',t)*ratio,scaleY=at(saved,'scaleY',t)*ratio))
        for prop in ['x','y']+(['fontSize']if id=='p0015'else['scaleX','scaleY']):track(l,prop,rows)
    # Independently measured contact row camera, genuine individual avatars.
    fit=json.loads((p/'measurements-v8/intro-ui-fit.json').read_text())
    rows=[r for r in fit['measurements']if r.get('name_ink_bbox')]
    ref=fit['reference_name_ink_bbox'];reference=next(r for r in rows if r['frame']==120)
    ui=dict(id='v8-inbox-rows',type='group',start=rows[0]['time'],end=end,children=[
      text('v8-Nikki','Nikki Freeman',452,680,40,weight=600),
      text('v8-NikkiSub','hey when are you coming home',451,733,36,fill='#858585'),
      text('v8-NikkiTime','1:50 AM',930,685,34,fill='#858585'),
      text('v8-Jony','Jony',452,875,40,weight=600),
      text('v8-JonySub','ngl i should’ve been sober when\ndesigning that car',451,927,36,fill='#858585',lineHeight=43),
      text('v8-JonyTime','12:15 AM',914,880,34,fill='#858585'),
      *[dict(id='v8-contact-'+name,type='image',src='assets/intro-'+name+'-native4.png',x=x,y=y,width=w,height=w)for name,x,y,w in [('nikki',342,707,88),('jony',342,907,88),('nikki-emoji',985,735,44)]],
      *[dict(id='v8-unread-'+str(y),type='circle',x=303,y=y-11,width=22,height=22,fill='#009df0')for y in [752,952]],
      *[dict(id='v8-sep-'+str(y),type='rect',x=456,y=y,width=650,height=2,fill='#e4e4e4')for y in [855,1045]],
      *[dict(id='v8-chevron-'+str(y),type='path',d=f'M1095 {y-11} L1106 {y} L1095 {y+11}',fill='none',stroke='#dedede',strokeWidth=5)for y in [705,899]]])
    uirows=[]
    for r in rows:
        scale=r['ui_scale_ratio'];uirows.append(dict(time=r['time'],x=r['name_ink_bbox'][0]-ref[0]*scale,y=r['name_ink_bbox'][1]-ref[1]*scale,scaleX=scale,scaleY=scale,opacity=r['ui_opacity']))
    for prop in ['x','y','scaleX','scaleY','opacity']:track(ui,prop,uirows)
    physical=[]
    for r in fit['measurements']:
        box=r.get('physical_bbox');island=r.get('island_bbox')
        if not box:continue
        scale=(box[2]-box[0])/974
        y=box[1]-10*scale if box[1]>0 else (island[3]-150*scale if island else at(by['p0054'],'y',r['time']))
        physical.append(dict(time=r['time'],x=box[0]-13*scale,y=y,scaleX=scale,scaleY=scale,opacity=1))
    phone=copy.deepcopy(by['p0054']['children'][0]);phone.update(id='v8-intro-physical',start=physical[0]['time'],end=end)
    for l in flat([phone]):
        l['id']='v8-'+l['id']
        if l.get('text')=='9:43':l['text']='9:41'
    for prop in ['x','y','scaleX','scaleY','opacity']:track(phone,prop,physical)
    refp=next(r for r in physical if abs(r['time']-120/FPS)<1e-6)
    header=dict(id='v8-inbox-header',type='group',start=3.35,end=end,children=[
      text('v8-Messages','Messages',628,283,40,weight=600),
      dict(id='v8-editpill',type='rect',x=334,y=264,width=131,height=85,radius=43,fill='#fafafa',shadow=dict(x=0,y=2,blur=12,color='#ededed')),
      text('v8-Edit','Edit',364,284,40,weight=600),
      dict(id='v8-menupill',type='circle',x=1023,y=265,width=85,height=85,fill='#fafafa',shadow=dict(x=0,y=2,blur=12,color='#ededed')),
      *[dict(id='v8-menuline'+str(i),type='rect',x=1046+4*i,y=294+12*i,width=44-8*i,height=4,radius=2,fill='#000000')for i in range(3)]])
    hr=[]
    for r in physical:
        ratio=r['scaleX']/refp['scaleX'];hr.append(dict(time=r['time'],x=r['x']-refp['x']*ratio,y=r['y']-refp['y']*ratio,scaleX=ratio,scaleY=ratio))
    for prop in ['x','y','scaleX','scaleY']:track(header,prop,hr)
    ix=scene['layers'].index(by['p0054']);scene['layers'][ix:ix+1]=[phone,header,ui]
    scene['layers'].remove(by['p0062'])
    # Native frosted white bubble and separately observed typing prefixes.
    popup=by['p0058'];popup['start']=109/FPS;popup['end']=end;popup['originX']=153.5;popup['originY']=56
    popup['children']=[dict(id='v8-preview-body',type='rect',x=0,y=0,width=307,height=112,radius=32,fill='#ffffff',opacity=.90,shadow=dict(x=0,y=1,blur=12,color='#e8e8e8')),
        dict(id='v8-preview-tail',type='path',d='M215 98 L233 96 Q248 106 233 118 L226 123 Q223 126 224 116 Z',fill='#ffffff',opacity=.90),
        text('v8-preview-line1','',43,18,33),text('v8-preview-line2','',25,55,33)]
    for l in popup['children'][2:]:l['fontFamily']='SF Pro Text'
    fits=json.loads((p/'measurements-v8/preview-typing-fit.json').read_text())['measurements']
    fits=[r for r in fits if not r.get('registration_failed')]
    popup['keyframes']={}
    for prop in ['x','y','rotation','scaleX','scaleY']:track(popup,prop,fits)
    for i,l in enumerate(popup['children'][2:]):
        l['keyframes']={'text':[dict(t=r['time'],value=(r['text'].split('\n')+[''])[i],ease='hold')for r in fits]}
    return scene
