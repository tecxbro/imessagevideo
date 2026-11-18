"""Editable vector UI inserts. All event boundaries come from timing data."""
import components as C

def track(samples, prop, fps):
    return [{'t':v['frame']/fps,'value':v[prop]} for v in samples]

def camera(id, children, samples, first, end, fps):
    keys={p:track(samples,p,fps) for p in ['x','y']}
    for p in ['scaleX','scaleY']:keys[p]=track(samples,'scale',fps)
    if 'rotation' in samples[0]:keys['rotation']=track(samples,'rotation',fps)
    return C.life(C.group(id,children,keyframes=keys),first,end)

def cursor(shot, pts, end, fps):
    shape='M 0 0 L 26 175 L 64 135 L 97 195 L 123 181 L 90 121 L 140 121 Z'
    size=1 if shot=='S2' else .77
    children=[C.path(shot+'-cursor-edge',shape,stroke='#000000',sw=13,fill='#000000'),C.path(shot+'-cursor-arrow',shape,stroke='#FFFFFF',sw=7,fill='#000000')]
    samples=[dict(v,scale=v['scale']*size) for v in pts]
    return camera(shot+'-cursor',children,samples,pts[0]['frame'],end,fps)

def x_post(copy, timing, fps):
    q=copy['x_post'];t=timing['insert_shots']['x'];first,end=timing['cuts']['S2']
    out=[C.rect('x-canvas',-900,-1000,4000,3000,'#000000'),C.rect('x-image-card',-400,-600,1950,930,'#FAF8F1',30),
         C.text('x-post-copy',q['post'],-350,-725,46),C.text('x-date',q['date'],-360,410,44,'#747A7C'),
         C.path('x-separators','M -500 545 L 1570 545 M -500 845 L 1570 845 M 1620 -800 L 1620 1500',stroke='#303537',sw=2),
         C.text('x-quotes',q['quotes'],1270,730,40,'#8A9294'),C.text('x-reply-placeholder',q['reply'],-150,955,54,'#777F83'),
         C.rect('x-reply-button',1350,900,210,110,'#707A78',55),C.text('x-reply-button-label',q['button'],1390,923,44,'#050606'),
         C.rect('x-sidebar-border',1700,-600,720,1270,'none',80,stroke='#303537',strokeWidth=2)]
    for i,v in enumerate(q['trends']):out.append(C.text(f'x-trend-{i}',v,1740,-350+i*156,38 if i%2 else 32,'#E7E9EA' if i%2 else '#747A7C',weight=600 if i%2 else 400))
    out.append(C.text('x-more',q['more'],1740,550,40,'#299CD8'))
    for i,v in enumerate(q['footer']):out.append(C.text(f'x-footer-{i}',v,1735,750+i*65,29,'#747A7C'))
    out += [C.path('x-retweet','M 220 650 L 220 600 L 265 600 M 205 617 L 220 600 L 238 617 M 275 604 L 275 650 L 232 650 M 260 635 L 275 652 L 290 636',stroke='#747A7C',sw=6),
            C.text('x-retweet-number',q['reposts'],300,602,43,'#747A7C'),C.text('x-replies',q['replies'],-180,602,43,'#747A7C'),
            C.path('x-heart','M 715 640 C 650 605 683 557 715 594 C 746 557 780 605 715 640 Z',stroke='#747A7C',sw=6),C.text('x-heart-number',q['likes'],766,597,43,'#747A7C'),
            C.path('x-share','M 1490 627 L 1535 627 L 1530 595 M 1510 615 L 1510 572 M 1495 589 L 1510 572 L 1525 589',stroke='#747A7C',sw=6)]
    mark='M 1110 593 L 1150 593 L 1150 651 L 1130 638 L 1110 651 Z'
    out.append(C.life(C.circle('x-hover',1074,569,112,'#071F2C'),t['halo'],end))
    out.append(C.life(C.path('x-bookmark-outline',mark,stroke='#747A7C',sw=5),first,t['fill']))
    out.append(C.life(C.path('x-bookmark-filled',mark,stroke='#26A1E9',sw=5,fill='#26A1E9'),t['fill'],end))
    for n,a,b,y in [('old',first,t['fill'],0),('selected',t['fill'],t['roll'][0],0),('rolling',t['roll'][0],t['roll'][1],-22),('new',t['roll'][1],end,0)]:
        out.append(C.life(C.text('x-count-'+n,q['bookmark_before'] if n in ['old','selected'] else q['bookmark_after'],1175,596+y,43,'#26A1E9' if a>=t['fill'] else '#747A7C'),a,b))
    for i,(a,b,label,w) in enumerate([(t['tooltip'][0],t['tooltip'][1],q['tooltip_before'],240),(t['tooltip'][1],t['tooltip'][2],q['tooltip_after'],460)]):
        out.append(C.life(C.group('x-tooltip-'+str(i),[C.rect('x-tip-bg-'+str(i),930,728,w,70,'#536875',5),C.text('x-tip-text-'+str(i),label,945,740,34)]),a,b))
    toast=C.group('x-toast',[C.rect('x-toast-bg',0,0,1110,130,'#26A1E9',12),C.text('x-toast-label',q['toast'][0],38,40,43),C.text('x-toast-action',q['toast'][1],755,40,43,weight=600)],x=300,rotation=-3.5,keyframes={'y':[{'t':t['toast']['slide_from']/fps,'value':1250},{'t':t['toast']['settled']/fps,'value':1050,'ease':'easeOut'}]})
    out.append(C.life(toast,t['toast']['first'],end))
    return [camera('x-ui-camera',out,timing['insert_shots']['planes']['S2'],first,end,fps),cursor('S2',timing['insert_shots']['cursor']['S2'],end,fps)]

def browser(copy,timing,fps):
    q=copy['browser'];t=timing['insert_shots']['browser'];first,end=timing['cuts']['S3']
    out=[C.rect('browser-paper',-900,-50,4000,2200,'#FFFFFF'),C.rect('browser-dark-chrome',-900,-600,4000,600,'#30394A'),
         C.rect('browser-tab',270,-390,370,100,'#5B5B57',35),C.rect('browser-url-pill',-500,-182,1980,84,'#1B2533',44),C.text('browser-url',q['url'],-225,-160,29,'#CFD3DA'),
         C.path('browser-star','M 1420 -160 L 1426 -146 L 1442 -145 L 1430 -135 L 1434 -120 L 1420 -128 L 1405 -120 L 1410 -135 L 1397 -145 L 1414 -146 Z',stroke='#BAC1CB',sw=3),
         C.rect('browser-extensions',1504,-183,280,88,'none',42,stroke='#7B8190',strokeWidth=2),C.rect('browser-yellow-extension',1526,-165,40,40,'#F7E82B',4),C.text('browser-yellow-mark',q['extension_mark'],1530,-167,40,'#101010',family='Brand',weight=700),
         C.rect('browser-purple-extension',1615,-163,43,43,'#8E41D3',10),C.text('browser-purple-mark',q['extension_mark'],1624,-166,39,family='Brand',weight=700),
         C.path('browser-puzzle','M 1710 -164 L 1723 -164 Q 1721 -185 1735 -180 Q 1746 -174 1740 -164 L 1753 -164 L 1753 -149 Q 1774 -151 1769 -137 Q 1765 -126 1753 -131 L 1753 -117 L 1710 -117 Z',stroke='#BCC4D0',sw=4),
         C.circle('browser-profile',1844,-166,58,'#32ACD9'),C.circle('browser-profile-head',1865,-158,14,'#E7F7FF'),C.path('browser-profile-shoulders','M 1856 -123 Q 1871 -144 1887 -123',sw=8)]
    for i,line in enumerate(q['article']):out.append(C.text(f'article-line-{i}',line,-150,1+i*64+(60 if i>=5 else 0),43,'#252520',family='Article'))
    out.append(C.life(C.group('browser-badge',[C.rect('browser-badge-blue',1544,-146,36,30,'#418FF4',4),C.path('browser-badge-check','M 1551 -132 L 1558 -126 L 1573 -139',sw=4)]),t['badge'],end))
    tools=[C.rect('reader-toolbar-bg',-900,0,4000,65,'#F5F8F8',stroke='#DDE0E1',strokeWidth=1),C.rect('reader-toggle',1210,17,52,27,'#899394',14),C.circle('reader-toggle-knob',1213,20,21,'#FFFFFF'),C.text('reader-toolbar-copy',q['toolbar'],1280,10,30,'#697477'),C.text('reader-toolbar-ink',q['ink'],1000,10,30,'#697477'),C.text('reader-toolbar-inbox',q['inbox'],1880,10,30,'#697477')]
    for i in range(3):tools.append(C.path(f'reader-tool-{i}','M 0 0 L 22 0 L 22 19 L 9 19 L 3 26 L 3 19 L 0 19 Z M 31 8 L 45 8 M 38 1 L 38 15',stroke='#697477',sw=3,x=1610+i*110,y=17))
    out.append(C.life(C.group('reader-toolbar',tools),t['toolbar'],end))
    toast=C.group('reader-toast',[C.rect('reader-toast-body',0,0,780,119,'#121C20',60,shadow={'x':0,'y':5,'blur':12,'color':'#00000055'}),C.path('reader-toast-check','M 35 58 L 48 71 L 75 40',sw=10),C.text('reader-toast-copy',q['toast'],102,32,40),C.rect('reader-toast-progress',45,115,710,5,'#71C36C')],y=128,keyframes={'x':[{'t':t['toast'][0]/fps,'value':1650},{'t':t['toast'][1]/fps,'value':1280,'ease':'easeOut'}]})
    out.append(C.life(toast,t['toast'][0],end))
    return [camera('browser-camera',out,timing['insert_shots']['planes']['S3'],first,end,fps),cursor('S3',timing['insert_shots']['cursor']['S3'],end,fps)]

def share_phone(copy,timing,fps):
    q=copy['share'];t=timing['insert_shots']['share'];first,end=timing['cuts']['S4']
    shell=C.phone_shell(copy)
    def prefix(node):
        node['id']='share-'+node['id']
        for c in node.get('children',[]):prefix(c)
    for n in shell:prefix(n)
    screen=[C.rect('share-screen-black',12,12,426,925,'#000000',60)]
    studio=[C.rect('studio-bg',12,300,426,260,'url(#studio-curtain)')]
    for i in range(19):studio.append(C.rect(f'curtain-{i}',12+i*23,300,12,260,'#1B1D25' if i%3 else '#282A31',opacity=.45))
    studio += [C.path('studio-silhouette','M 70 560 Q 90 450 174 451 L 168 405 C 152 330 270 322 262 409 L 252 450 Q 343 464 375 560 Z',stroke='none',fill='#080A10'),C.path('studio-microphone','M 325 395 L 270 444 M 340 387 L 420 370',stroke='#07080B',sw=14)]
    screen.append(C.life(C.group('vector-studio',studio),first,t['panel']))
    actions=[C.rect('youtube-action-sheet',18,530,414,420,'#201E22',19),C.rect('youtube-grabber',202,541,47,4,'#66636B',2)]
    for i,label in enumerate(q['actions']):
        actions += [C.text(f'youtube-action-{i}',label,80,566+i*61,20),C.path(f'youtube-action-icon-{i}','M 0 10 L 22 10 M 11 0 L 11 21 M 3 3 L 19 19',sw=2,x=42,y=568+i*61)]
    screen.append(C.life(C.group('youtube-actions',actions),first,t['sheet'][0]))
    sheet=[C.rect('ios-share-bg',16,470,418,490,'#212123',18),C.rect('share-thumbnail',32,488,94,94,'#176D71',6),C.text('share-thumb-much',q['thumbnail'][0],37,495,24,weight=700),C.text('share-thumb-op',q['thumbnail'][1],37,525,29,'#69DDD1',weight=700),C.text('share-title',q['title'],142,490,16,weight=600),C.text('share-site',q['site'],142,514,14,'#A2A1A6'),C.circle('share-close',389,484,29,'#37373A'),C.path('share-close-cross','M 398 493 L 410 505 M 410 493 L 398 505',stroke='#AAA8AF',sw=2),C.rect('shareplay-pill',280,548,139,37,'#22D44F',18),C.text('shareplay-label',q['shareplay'],319,558,16),C.path('shareplay-symbol','M 290 574 Q 291 554 309 560 M 294 574 Q 295 561 305 564 M 300 574 L 300 569',sw=2),C.path('share-separator','M 16 602 L 434 602',stroke='#3A393B',sw=1)]
    for i,label in enumerate(q['apps']):
        x=33+i*98
        if i==1:
            icon=C.app_icon('share-reader-icon',copy['brand']['mark']);icon.update(x=x,y=625,scaleX=.34,scaleY=.34);sheet.append(icon)
        else:
            sheet.append(C.rect(f'share-app-{i}',x,625,68,68,'#33DF56' if i==3 else '#FFFFFF',15))
            if i==0:
                for j,d in enumerate([48,34,17]):sheet.append(C.circle(f'airdrop-ring-{j}',x+34-d/2,659-d/2,d,'none',stroke='#1684E6',strokeWidth=2))
            elif i==2:
                for j,col in enumerate(['#31B7D2','#36BF88','#E7AC25','#DA246A']):sheet.append(C.rect(f'slack-bar-{j}',x+12+(j%2)*22,636+(j//2)*23,18,28,col,8))
            else:sheet.append(C.path('messages-balloon','M 0 0 Q -5 -24 20 -23 Q 48 -23 47 0 Q 43 20 16 17 L 5 24 L 8 14 Z',stroke='none',fill='#FFFFFF',x=x+10,y=661))
        sheet.append(C.text(f'share-app-label-{i}',label,x+34,700,13,textAnchor='middle'))
    sheet.append(C.rect('share-fifth-app',425,625,68,68,'#1E8BD4',15))
    sheet.append(C.life(C.rect('reader-pressed',131,625,68,68,'#000000',15,opacity=.48),*t['highlight']))
    for i,label in enumerate(q['rows']):
        y=745+i*56
        sheet += [C.rect(f'share-row-{i}',32,y,386,54,'#373639',10),C.text(f'share-row-label-{i}',label,49,y+17,18),C.path(f'share-row-icon-{i}','M 0 0 L 16 0 L 16 22 L 0 22 Z M 5 -5 L 21 -5 L 21 17',x=382,y=y+15,sw=1.5)]
    screen.append(C.life(C.group('ios-share-sheet',sheet,keyframes={'y':[{'t':t['sheet'][0]/fps,'value':350},{'t':t['sheet'][1]/fps,'value':0,'ease':'easeOut'}]}),t['sheet'][0],t['panel']))
    saved=[C.rect('reader-saved-bg',12,65,426,875,'#1D1B20',18),C.rect('reader-grabber',208,88,34,3,'#4E4B54',2),C.circle('reader-saved-close',393,77,29,'#2A272F'),C.path('reader-saved-x','M 402 86 L 413 97 M 413 86 L 402 97',stroke='#8C8893',sw=2)]
    content=[];icon=C.app_icon('saved-reader-icon',copy['brand']['mark']);icon.update(x=187,y=370,scaleX=.38,scaleY=.38);content.append(icon)
    content += [C.text('saved-reader-label',q['saved'],225,468,21,textAnchor='middle',weight=600),C.rect('read-now-pill',42,675,366,50,'#24262A',25),C.text('read-now-label',q['read'],225,691,18,textAnchor='middle'),C.text('dismiss-label',q['dismiss'],225,742,13,'#98939D',textAnchor='middle')]
    action_icons=['M 2 4 L 21 4 M 5 4 L 7 26 L 19 26 L 21 4 M 9 0 L 17 0 M 11 9 L 11 21 M 16 9 L 16 21',
                  'M 1 0 L 13 0 L 27 14 L 16 26 L 1 11 Z M 7 6 L 8 6',
                  'M 0 0 L 25 0 L 25 20 L 13 20 L 5 26 L 5 20 L 0 20 Z M 5 6 L 20 6 M 5 12 L 20 12',
                  'M 4 4 A 13 13 0 1 1 1 15 M 4 0 L 4 7 L 11 7 M 14 5 L 14 15 L 21 15',
                  'M 0 0 L 25 0 L 25 7 L 0 7 Z M 3 7 L 3 25 L 22 25 L 22 7 M 8 13 L 17 13']
    for i,d in enumerate(action_icons):content += [C.circle(f'saved-action-circle-{i}',52+i*72,810,53,'#26272C'),C.path(f'saved-action-icon-{i}',d,stroke='#D3D1D9',sw=1.5,x=68+i*72,y=825)]
    saved.append(C.life(C.group('reader-saved-content',content),t['saved'],end))
    spinner=C.group('reader-spinner',[C.path('reader-spinner-arc','M 213 484 A 18 18 0 1 1 238 462',stroke='#A5A1AB',sw=3)],originX=225,originY=475,keyframes={'rotation':[{'t':t['spinner'][0]/fps,'value':0},{'t':t['spinner'][1]/fps,'value':360}]})
    saved.append(C.life(spinner,*t['spinner']))
    screen.append(C.life(C.group('reader-panel',saved,keyframes={'x':[{'t':t['panel']/fps,'value':425},{'t':t['spinner'][0]/fps,'value':0,'ease':'easeOut'}]}),t['panel'],end))
    screen += [C.rect('share-home-indicator',151,932,148,5,'#F5F5F5',3),C.rect('share-island',147,21,156,35,'#000000',18)]
    shell.append(C.group('share-screen-clipped',screen,clip={'x':12,'y':12,'width':426,'height':925,'radius':60}))
    return [camera('share-phone-camera',shell,timing['insert_shots']['phone'],first,end,fps)]

def build(copy,timing,fps):
    return x_post(copy,timing,fps)+browser(copy,timing,fps)+share_phone(copy,timing,fps)
