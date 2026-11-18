"""Editable shared-contract vector components; geometry is in output pixels."""
import random
from functools import lru_cache
from PIL import ImageFont

FPS = 30
FONT_PATHS = {}

def configure(fonts, fps):
    global FONT_PATHS, FPS
    FONT_PATHS, FPS = fonts, fps

def rect(id, x, y, w, h, fill, radius=0, **kw):
    return dict(id=id, type='rect', x=x, y=y, width=w, height=h, fill=fill, radius=radius, **kw)

def circle(id, x, y, d, fill, **kw):
    return dict(id=id, type='circle', x=x, y=y, width=d, height=d, fill=fill, **kw)

def path(id, d, stroke='#FFFFFF', sw=2, fill='none', **kw):
    return dict(id=id, type='path', d=d, stroke=stroke, strokeWidth=sw, fill=fill, **kw)

def text(id, value, x, y, size=19, fill='#FFFFFF', family='UI', weight=400, **kw):
    return dict(id=id, type='text', text=value, x=x, y=y, fontSize=size, fill=fill,
                fontFamily=family, fontWeight=weight, lineHeight=size*1.23, **kw)

def group(id, children, **kw):
    return dict(id=id, type='group', children=children, **kw)

def life(layer, first, end):
    return dict(layer, start=first/FPS, end=end/FPS)

@lru_cache(maxsize=128)
def font(family, size):
    return ImageFont.truetype(FONT_PATHS[family], round(size*4))

def width(value, size=19, family='UI'):
    return font(family,size).getlength(value)/4

def wrap(value, final_lines):
    if '\n' in value:
        return value.split('\n')
    boundaries=[]
    n=0
    for line in final_lines[:-1]:
        n+=len(line)
        boundaries.append(n)
        n+=1
    lines=[];start=0
    for end in boundaries:
        if len(value)>end:
            lines.append(value[start:end]);start=end+1
    lines.append(value[start:])
    return lines

def rich_lines(id, lines, bold, x, y, size=18.5, line_height=24.5):
    result=[]
    for n,line in enumerate(lines):
        spans=[]
        for run in bold:
            start=line.find(run)
            if start>=0:spans.append((start,start+len(run)))
        cuts=sorted({0,len(line),*[p for span in spans for p in span]})
        advance=0
        for i,(a,b) in enumerate(zip(cuts,cuts[1:])):
            family='UIBold' if any(a>=s and b<=e for s,e in spans) else 'UI'
            result.append(text(f'{id}-line{n}-span{i}',line[a:b],x+advance,y+n*line_height,size,
                               family=family,weight=600 if family=='UIBold' else 400))
            advance+=width(line[a:b],size,family)
    return result

def background(copy, end_start, black_frame, frames):
    return life(group('shared-background',[
        life(rect('gradient-base',0,0,1920,1080,'url(#background-base)'),0,black_frame),
        life(rect('gradient-pink',0,0,1920,1080,'url(#background-pink)'),0,black_frame),
        life(circle('end-card-faint-arc',330,676,1260,'#B9A1DA',stroke='#B9A1DA',strokeWidth=2,opacity=.035),end_start,black_frame),
        rect('frame-evaluation-anchor',0,0,0,0,'#000000',keyframes={'x':[{'t':0,'value':0},{'t':frames/FPS,'value':1}]})
    ]),0,frames)

def title(id, copy, timing, size, y):
    full=copy['text'];accent=copy.get('accent');start_accent=full.find(accent) if accent else len(full)
    x=(1920-width(full,size,'Title'))/2
    layers=[]
    for i,b in enumerate(timing['births']):
        end=timing['births'][i+1]['frame'] if i+1<len(timing['births']) else timing['end']
        value=full[:b['count']]
        white=value[:start_accent];pink=value[start_accent:]
        children=[text(id+f'-{i}-white',white,x,y,size,family='Title',weight=700)]
        if pink:children.append(text(id+f'-{i}-pink',pink,x+width(white,size,'Title'),y,size,'#DC8C91',family='Title',weight=700))
        layers.append(life(group(id+f'-prefix-{i}',children),b['frame'],end))
    return layers

def app_icon(id, mark):
    return group(id,[rect(id+'-square',0,0,200,200,'url(#icon-dark)',38),
                     text(id+'-R',mark,38,9,174,family='Brand',weight=700),
                     path(id+'-curl','M 137 200 C 153 176 127 161 161 132 C 181 115 197 91 200 73 L 200 160 Q 200 200 162 200 Z',fill='url(#page-blue)',stroke='none'),
                     path(id+'-crease','M 143 200 C 159 171 160 154 178 133 C 168 167 176 179 168 198',stroke='#6544F2',sw=3)])

def doodles(seed=17):
    rng=random.Random(seed);out=[]
    drawings=[
        'M 3 13 L 7 0 L 16 7 Q 25 3 33 9 L 40 1 L 43 20 Q 40 39 23 39 Q 4 39 3 13 M 13 19 L 14 20 M 31 19 L 32 20 M 19 29 Q 23 33 27 28',
        'M 23 41 C -12 20 5 -3 23 12 C 44 -5 59 21 23 41 Z',
        'M 20 0 L 25 14 L 42 15 L 29 25 L 34 41 L 20 31 L 6 41 L 11 25 L 0 15 L 15 14 Z',
        'M 5 14 L 35 14 L 32 39 L 9 39 Z M 35 18 C 54 12 49 39 33 32 M 11 7 Q 19 3 12 0 M 25 7 Q 32 4 26 0',
        'M 0 28 Q 15 -6 31 0 Q 48 14 20 42 Z M 17 11 C 18 1 38 5 29 17 C 24 23 14 19 17 11 M 7 33 L 0 44 L 14 39',
        'M 2 25 Q 2 0 25 3 Q 51 0 49 25 Q 43 42 27 40 L 12 48 L 14 38 Q 3 35 2 25 M 12 20 L 14 20 M 25 20 L 27 20 M 38 20 L 40 20'
    ]
    for i in range(120):
        col=i%10;row=i//10
        out.append(path(f'doodle-{i}',rng.choice(drawings),stroke=rng.choice(['#6A4685','#7D4A72','#434770']),sw=1.1,
                        x=col*45+rng.uniform(-12,7),y=105+row*37+rng.uniform(-10,8),rotation=rng.uniform(-50,50),scaleX=.8,scaleY=.8,opacity=.52))
    return group('seeded-vector-wallpaper',out)

def avatar():
    return group('ghost-avatar',[
        circle('avatar-disc',0,0,42,'#CDB38E'),circle('avatar-face',4,3,34,'#FFF1CD'),
        path('ghost-shape','M 9 30 L 9 17 Q 10 6 22 8 Q 34 6 34 18 L 34 31 L 29 28 L 24 32 L 18 29 L 13 32 Z',stroke='#887156',sw=1.3,fill='#F5E5C9'),
        circle('eye-l',15,17,2.5,'#524A4A'),circle('eye-r',26,17,2.5,'#524A4A'),
        path('ghost-smile','M 19 24 Q 23 27 26 23',stroke='#887156',sw=1.1)
    ],x=375,y=83)

def phone_shell(copy):
    h=copy['header']
    return [rect('phone-shadow',0,0,450,950,'#060606',72,shadow={'x':0,'y':12,'blur':11,'color':'#000000'}),
            rect('phone-rail',0,0,450,950,'#5B5B56',72),rect('phone-black-body',4,3,442,944,'#030303',69),
            rect('side-mute',-3,152,4,42,'#6D6B66',2),rect('side-volume-up',-3,215,4,66,'#6D6B66',2),
            rect('side-volume-down',-3,298,4,66,'#6D6B66',2),rect('side-power',449,230,4,95,'#6D6B66',2)]

def phone_chrome(copy, timing):
    h=copy['header']
    children=[rect('header-glass-backdrop',12,13,426,118,'#060609',50,opacity=.7),
              rect('dynamic-island',147,21,156,35,'#000000',18),
              text('status-time',h['time'],70,34,17,weight=600),
              rect('battery-outline',374,36,23,11,'none',3,stroke='#6A6A6D',strokeWidth=1),
              rect('battery-terminal',398,39,2,5,'#777777',1),rect('battery-yellow',376,38,18,7,'#F5D52D',1),
              path('status-wifi','M 346 38 Q 355 31 365 38 M 350 42 Q 355 37 361 42 M 354 46 L 357 46',sw=2.1),
              circle('back-button',28,82,45,'#18171B',stroke='#353139',strokeWidth=1),
              path('back-chevron','M 55 94 L 46 104 L 55 114',sw=2),
              rect('header-pill',128,82,194,48,'#1B191D',25,stroke='#373239',strokeWidth=.8),
              text('header-name',h['name'],225,86,18,textAnchor='middle',weight=600),avatar(),
              rect('home-indicator',151,925,148,5,'#F5F5F5',3)]
    for i in range(4):children.append(rect(f'signal-{i}',319+i*6,45-i*3,4,4+i*3,'#FFFFFF',.6))
    bounds=sorted({timing['cuts']['S6'][0],timing['cuts']['S6'][1],*[f for pair in timing['waits'] for f in pair]})
    for i,(a,b) in enumerate(zip(bounds,bounds[1:])):
        waiting=any(s<=a<e for s,e in timing['waits'])
        children.append(life(text(f'header-subtitle-{i}',h['typing'] if waiting else h['subtitle'],225,109,12,'#68A3F5' if waiting else '#A8A4AC',textAnchor='middle'),a,b))
    return children

def key(id, label, x, y, w, h=44, size=26, fill='#69696C'):
    return [rect(id+'-cap',x,y,w,h,fill,5),text(id+'-label',label,x+w/2,y+(h-size)/2-1,size,textAnchor='middle')]

def keyboard(copy, layout, upper=False):
    k=copy['keyboard'];numeric=layout=='numeric'
    out=[rect('keyboard-surface',12,574,426,348,'#29282C'),rect('keyboard-prediction-back',12,574,426,56,'#29282C'),
         path('prediction-dividers','M 151 587 L 151 620 M 294 587 L 294 620',stroke='#414044',sw=.8)]
    rows=k['numeric'] if numeric else k['alpha']
    for ri,row in enumerate(rows):
        labels=list(row)
        if upper and not numeric:labels=[l.upper() for l in labels]
        y=634+ri*57
        if ri==0:x=17;w=37.5;gap=4.8
        elif ri==1 and not numeric:x=38;w=37.5;gap=5
        elif ri==1:x=17;w=37.5;gap=4.8
        elif not numeric:x=79;w=37.5;gap=5
        else:x=79;w=53;gap=5
        for ki,label in enumerate(labels):out+=key(f'{layout}-{upper}-{ri}-{ki}',label,x+ki*(w+gap),y,w,size=25)
    if numeric:
        out+=key('symbols-key',k['labels']['symbols'],17,748,52,size=16,fill='#49494B')
    else:
        out+=key('shift-key','',17,748,52,fill='#49494B')
        out.append(path('shift-arrow','M 33 774 L 33 766 L 27 766 L 43 751 L 58 766 L 52 766 L 52 780 L 33 780 Z',stroke='#FFFFFF',sw=1.6,x=-2,y=2))
    out+=key('delete-key','',382,748,51,fill='#49494B')
    out.append(path('delete-outline','M 399 761 L 419 761 L 419 780 L 399 780 L 389 770 Z M 402 766 L 412 776 M 412 766 L 402 776',sw=1.5))
    out+=key('layout-toggle',k['labels']['letters'] if numeric else k['labels']['numbers'],17,805,51,size=16,fill='#49494B')
    out+=key('emoji-toggle','',74,805,46,fill='#49494B')
    out.append(text('keyboard-smiley',copy['composer']['emoji'],97,809,30,textAnchor='middle'))
    out+=key('space-key',k['labels']['space'],126,805,204,size=18)
    out+=key('return-key',k['labels']['return'],336,805,97,size=18,fill='#49494B')
    out.append(path('keyboard-globe','M 37 878 A 14 14 0 1 0 65 878 A 14 14 0 1 0 37 878 M 37 878 L 65 878 M 51 864 Q 39 878 51 892 Q 63 878 51 864 M 39 872 L 63 872 M 39 884 L 63 884',sw=1.6))
    out.append(path('keyboard-mic','M 399 866 L 399 880 Q 399 886 405 886 Q 411 886 411 880 L 411 866 Q 405 859 399 866 M 395 877 Q 395 892 405 892 Q 416 892 416 877 M 405 892 L 405 899 M 400 899 L 410 899',sw=1.7))
    return group(f'keyboard-{layout}-{upper}',out)

def predictions(id, labels):
    labels=(labels+['','',''])[:3]
    return group(id,[text(id+'-label-'+str(i),label,x,589,18,'#E8E5EA',textAnchor='middle') for i,(label,x) in enumerate(zip(labels,[82,224,366]))])

def key_pop(id,label,row,column):
    x=(17+column*42.3) if row==0 else (38+column*42.5)
    y=634+row*57
    return group(id,[rect(id+'-pressed',x,y,37.5,50,'#77777A',5),
                     path(id+'-stem',f'M {x} {y+6} L {x} {y-6} L {x-8} {y-18} L {x+45} {y-18} L {x+37.5} {y-6} L {x+37.5} {y+6} Z',fill='#77777A',stroke='none'),
                     rect(id+'-cap',x-8,y-62,54,61,'#77777A',10),
                     text(id+'-label',label,x+19,y-59,43,textAnchor='middle')])

def composer(id, value, final_lines, copy, first, end, caret, empty_notice=False):
    lines=wrap(value,final_lines) if value else []
    height=44+max(0,len(lines)-1)*24
    top=568-height
    out=[rect(id+'-underlay',12,top-9,426,height+15,'#050505'),
         circle(id+'-menu',27,526,39,'#4D8CF5',stroke='#9CBFFF',strokeWidth=1),
         path(id+'-menu-lines','M 39 539 L 54 539 M 39 545 L 54 545 M 39 551 L 54 551',sw=1.4),
         circle(id+'-clip-button',77,526,39,'#17161A',stroke='#39353D',strokeWidth=1),
         path(id+'-paperclip','M 88 550 L 101 536 Q 111 532 108 542 L 94 556 Q 86 561 84 554 Q 81 549 88 543 L 98 533 M 90 550 L 102 538',sw=1.7),
         rect(id+'-field',122,top,292 if value else 256,height,'#19171B',23,stroke='#38343C',strokeWidth=1)]
    if value:
        out.append(text(id+'-draft','\n'.join(lines),136,top+7,19))
        cx=136+width(lines[-1],19)
        out.append(rect(id+'-caret',cx,top+7+(len(lines)-1)*24,1.8,24,'#4A9EFF',keyframes={'opacity':caret}))
        out.append(text(id+'-emoji',copy['composer']['emoji'],362,535,25,'#A4A1A7',textAnchor='middle'))
        out.append(circle(id+'-send',377,527,36,'#4D8CF5'))
        out.append(path(id+'-plane','M 385 545 L 404 536 L 399 555 L 394 548 L 385 545 Z M 394 548 L 404 536',fill='#FFFFFF',stroke='#FFFFFF',sw=1))
    else:
        out.append(text(id+'-placeholder',copy['composer']['placeholder'],136,top+9,19,'#8A858D'))
        out.append(circle(id+'-sticker',346,535,24,'none',stroke='#9E99A2',strokeWidth=1.6))
        out.append(path(id+'-sticker-fold','M 355 535 L 355 547 L 369 551',stroke='#9E99A2',sw=1.5))
        out.append(path(id+'-mic','M 399 536 L 399 548 Q 399 555 405 555 Q 411 555 411 548 L 411 536 Q 405 530 399 536 M 395 545 Q 395 560 405 560 Q 416 560 416 545 M 405 560 L 405 565',sw=1.7))
    if empty_notice:
        ey=326-max(0,len(lines)-1)*12
        out += [rect(id+'-empty-pill',137,ey,176,31,'#251D29',16),
                text(id+'-empty-notice',copy['header']['empty'],225,ey+7,14,textAnchor='middle')]
    return life(group(id,out),first,end),top

def bubble(id, lines, bold, outgoing, timestamp):
    lineh=24.5;size=18.5
    w=min(390,max(170,max((width(l,size) for l in lines),default=0)+24))
    h=len(lines)*lineh+24
    if outgoing and len(lines)==1:
        size=17
        w=min(390,width(lines[0],size)+88)
        h=35
    x=426-w if outgoing else 26
    nodes=[rect(id+'-body',x,0,w,h,'#8B36F6' if outgoing else '#302332',14)]
    nodes+=rich_lines(id,lines,bold,x+11,8,size,lineh)
    nodes.append(text(id+'-time',timestamp,x+w-(87 if outgoing else 62),h-16,11,'#B3A0BD'))
    if outgoing:nodes.append(path(id+'-ticks',f'M {x+w-26} {h-10} l 4 4 l 9 -10 M {x+w-19} {h-10} l 4 4 l 9 -10',stroke='#D1B6F3',sw=1.2))
    return group(id,nodes),h
