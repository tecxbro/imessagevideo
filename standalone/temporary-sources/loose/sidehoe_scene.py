import json
from pathlib import Path
p=Path('sidehoe-recreation/first-source/scene.json')
scene={
    'title':'Sidehoe / editable choreography study','designSize':1000,'outputSize':2000,'fps':25,'duration':31.12,
    'sourceMap':{'sha256':'f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327','startFrame':0,'endFrame':777,'outputStart':0},
    'palette':{'paper':'#fafafa','ink':'#17171d','secondary':'#73747e','hairline':'#e5e5ec','incoming':'#e8e7ed','cyan':'#11c0e6','accent':'#7848ab','negative':'#dedee5','control_a':'#daedff','control_b':'#f2ccfa'},
    'copy':{
        'status':'7:13','chatStatus':'9:41','inbox':'Messages','edit':'Edit',
        'pinNote':'Dating is hard {broken}','brand':'Sidehoe',
        'assistant':['Your personal','assistant'],'personal':['For a very active','personal life'],
        'keyboardPrompt':'iMessage','today':'Today',
        'sofia':['Sofia','Yesterday was really nice:)','Yes, it was awesome!','Do you wanna go out again tmrw?',"Yeah let's do it",'Sideho suggestion',['Or do you wanna just','come over tonight :)'],'No','Send?'],
        'follow':['Sidehoe',['Can you please schedule','in a date with Linda?'],['Certainly, Linda is available at 4pm.','Does that work for you?'],["It's been 6 months since you spoke","to Liliana. Want me to shoot her a","text?"],'No {cry}','Yes {wink}'],
        'calendar':['Date with Lisa {plum}{drops}','Date with Marie {cat}'],
        'ending':[['The','most','personal'],['iMessage','assistant','yet']],
    },
    'inboxPins':[['Marie','marie'],['Sydney','sydney'],['Darla','darla']],
    'inboxRows':[
        ['Eleanor','Heyyyy','1:50 PM','eleanor'],
        ['Charlotte','Let’s go out tonight!','11:00 AM','ella'],
        ['Thea','You don’t have a job?!','10:34 AM','lisa'],
        ['Margot','Wanna go out tmrw?','10:12 AM','margot'],
        ['Darla','hey bby what r u doin?','9:55 AM','darla'],
        ['El','Heyyyy cutie :3','1:30 PM','eleanor'],
        ['Danielle','You want to come over? {wink}','2:25 PM','danielle'],
        ['Thea','OMG, I love sushi! {sushi}','8:00 PM','lisa'],
        ['Margot','Wanna go out tmrw?','7:20 AM','margot'],
    ],
    'avatars':{
        'marie':['#dec297','#edbe9f','#604438','#a16857','#66578d','braids','glasses'],
        'sydney':['#8a9ca5','#f2cba6','#b69563','#d99174','#42535c','bob','sad'],
        'darla':['#78bee9','#c78f74','#394553','#9b687f','#484c78','waves','glasses'],
        'eleanor':['#d9cef5','#a6714f','#846953','#955852','#d0b55e','waves','glasses'],
        'ella':['#f0a9c4','#f2c39d','#d1a574','#cb766e','#b13e74','sweep','smile'],
        'margot':['#ccebf4','#efc09d','#ac7b4e','#bc7770','#576dc4','waves','smile'],
        'danielle':['#dacdf3','#dca17e','#623943','#ae666a','#82518e','long','smile'],
        'lisa':['#a7e9b0','#efb792','#4a302b','#cb7b67','#3a6f55','long','wink'],
        'maria':['#f2d7a6','#eec4a0','#c29c66','#bc756d','#b87b55','waves','smile'],
        'rae':['#f7e1a1','#ad6c50','#56362c','#eb655c','#d75a63','braids','shades'],
    },
    'profiles':[
        ['Lisa','lisa','{boot} likes hiking','#e0fae8','#23833f'],
        ['Ella','ella','{heart} likes dancing','#f2dcfa','#9b2bb3'],
        ['Maria','maria','{art} likes art','#fcf1dc','#ab681c']
    ],
    'cluster':[
        ['ella',299,345,112,213,'#f3bee0'],[None,515,353,60,213,'#d1c7f3'],
        [None,616,305,44,214,'#c6edf8'],['rae',700,455,86,215,'#fbebad'],
        [None,166,470,42,215,'#f8deb9'],['eleanor',456,539,84,216,'#f9deb4'],
        [None,310,580,63,217,'#d6c9f3'],[None,588,482,43,217,'#f3bfd3'],
        ['danielle',650,683,126,217,'#d8cbf7'],[None,804,586,50,218,'#c5ebfa'],
        ['margot',227,735,94,219,'#c8edf8'],[None,455,738,70,219,'#bdf4d0'],
        [None,558,837,48,220,'#f5c9e0'],
    ],
    'tracks':{
        'inboxY':[[0,100],[6,14],[11,0],[37,-7],[42,-23],[46,-57],[50,-128],[54,-256],[59,-593],[63,-863],[67,-1054],[72,-1191],[81,-1206],[96,-1194],[101,-1134]],
        'inboxScale':[[0,.92],[10,.965],[35,1.02],[53,1.02],[72,1.04],[95,1],[101,.90]],
        'identityY':[[102,514],[105,490],[112,461],[122,458],[129,465],[133,515]],
        'assistantY':[[134,352],[137,409],[144,441],[154,469],[159,497],[161,605]],
        'profileCamera':[[258,0,0,1],[275,0,0,1],[284,0,0,1],[289,142,0,1.25],[293,154,0,1.32],[308,173,18,1.37],[312,171,424,1.37]],
        'sofiaCamera':[[313,-317,1.0],[315,-142,1.02],[318,29,1.0],[320,66,1.0],[325,91,1.0],[330,88,1.02],[335,62,1.24],[336,9,1.37],[338,-155,1.60],[339,-295,1.77],[341,-420,2.04],[345,-517,2.24],[349,-530,2.34],[352,-532,2.37],[354,-545,2.38],[360,-654,2.56]],
        'sendGroup':[[353,0,-532,2.37],[355,0,-570,2.42],[360,-45,-648,2.55],[371,-45,-645,2.55],[385,-53,-647,2.60],[391,-55,-663,2.67],[396,-62,-684,2.80],[402,-70,-1020,2.85]],
        'sendCursor':[[381,750,1055,-7],[383,751,939,-8],[388,778,804,5],[391,826,709,0],[393,854,649,0],[396,864,633,0],[402,869,359,0]],
        'calendarCamera':[[397,175,1145,81],[403,160,490,87],[410,196,325,90],[420,192,289,91],[427,186,283,94],[435,160,264,99],[442,146,257,104],[452,142,253,106],[460,142,253,106],[473,153,263,102],[478,197,306,90]],
        'calendarMarie':[[397,1.82],[429,1.82],[437,1.05],[442,1.0],[478,1.0]],
        'calendarLisa':[[397,.91],[447,.98],[452,.98],[457,1.98],[461,2.0],[478,2.0]],
        'calendarCursor':[[402,1140,638,-80],[407,883,493,-70],[411,813,440,-100],[415,550,549,-47],[420,511,532,0],[429,518,540,0],[435,508,471,0],[441,511,531,-4],[452,470,525,0],[456,449,607,-5],[460,458,617,-54],[470,451,622,-55],[478,90,680,-34]],
        'orbitPhase':[[478,-.04],[486,-.055],[497,.02],[508,-.018],[520,.025],[530,0],[536,.25],[545,.31],[550,.35],[556,.49],[565,.54],[570,.57],[575,.66],[586,.75],[597,.77],[613,.78],[621,.78]],
        'orbitY':[[478,105],[486,-4],[515,2],[550,-4],[600,2],[613,19],[619,249],[622,678]],
        'followCamera':[[624,-323,1],[626,-181,1],[630,-18,1],[633,40,1],[639,50,1],[645,48,1],[653,45,1.03],[659,8,1.19],[662,-139,1.40],[665,-244,1.67],[670,-351,1.89],[675,-400,2.03],[684,-398,2.05],[690,-391,2.00],[693,-326,1.73],[695,-134,1.47]],
        'followCursor':[[624,879,141,-13],[634,886,300,-13],[645,883,350,-13],[653,895,360,-13],[659,882,403,-14],[664,709,650,-46],[669,576,668,-12],[674,480,571,0],[676,478,564,0],[686,478,564,0],[691,465,561,0],[695,465,506,0]],
        'closingY':[[696,520],[704,459],[713,451],[718,438],[765,438],[777,437]],
        'closingSize':[[696,172],[703,241],[712,241],[720,209],[765,209],[777,209]],
        'endingFade':[[765,1],[766,.992],[767,.968],[768,.921],[769,.85],[770,.746],[771,.64],[772,.522],[773,.396],[774,.265],[775,.145],[776,.049],[777,0]],
    }
}
raw_events=[
(0,'inbox.open','entrance','inbox'),(2,'inbox.outer-pins','reveal','pins'),(9,'inbox.note-legible','read','pin-note'),
(42,'inbox.scroll','move','inbox'),(57,'inbox.scroll-fast','move','inbox'),(75,'inbox.settled','settle','inbox'),
(102,'identity.in','cut','identity'),(106,'identity.name','type','identity'),(134,'assistant.in','cut','assistant'),(141,'assistant.read','read','copy'),
(162,'personal.line-one','type','copy'),(178,'personal.line-two','type','copy'),(213,'profiles.cluster','assemble','avatars'),(222,'profiles.cluster-settle','settle','avatars'),
(254,'profiles.mosaic','wipe','avatars'),(258,'profiles.directory','entrance','profiles'),(271,'profiles.read','read','profiles'),(285,'profiles.push','move','camera'),
(290,'profiles.lisa-focus','select','hiking-chip'),(313,'sofia.in','cut','sofia'),(336,'sofia.suggestion','reveal','suggestion'),(341,'sofia.no','reveal','no'),(343,'sofia.send-control','reveal','send'),
(353,'sofia.transpose','dissolve','suggestion'),(360,'sofia.isolated','settle','suggestion'),(382,'sofia.pointer','point','send'),(393,'sofia.send-contact','contact','send'),
(397,'calendar.in','slide','calendar'),(408,'calendar.overlap','read','appointments'),(430,'calendar.marie-start','move','marie'),(441,'calendar.marie-settled','settle','marie'),
(452,'calendar.lisa-start','move','lisa'),(460,'calendar.separate','settle','lisa'),(474,'calendar.mosaic','wipe','calendar'),(478,'apps.in','entrance','apps'),
(532,'apps.first-turn','move','apps'),(550,'apps.rings-turn','move','apps'),(573,'apps.date-turn','move','apps'),(622,'apps.blank','cut','stage'),
(624,'follow.in','entrance','follow'),(648,'follow.no','reveal','no'),(650,'follow.yes','reveal','yes'),(659,'follow.push','move','camera'),(675,'follow.yes-contact','contact','yes'),
(686,'follow.yes-feedback','highlight','yes'),(690,'follow.out','move','follow'),(696,'ending.logo','cut','identity'),
(717,'ending.the','type','copy'),(721,'ending.most','type','copy'),(726,'ending.personal','type','copy'),(741,'ending.imessage','type','copy'),
(749,'ending.assistant','type','copy'),(757,'ending.yet','type','copy'),(765,'ending.last-read','hold','copy'),(766,'ending.fade','fade','stage'),(777,'ending.black','hold','stage')]
events=[{'frame':f,'id':i,'kind':k,'target':t} for f,i,k,t in raw_events]
sound=[
    ('opening','inbox.open','chime',0),('inbox-scroll','inbox.scroll-fast','swish',-720),
    ('identity','identity.in','chime',0),('assistant-drop','assistant.in','swish',0),
    ('heart-title','personal.line-two','chime',0),('profile-cluster','profiles.cluster','chime',0),
    ('mosaic','profiles.mosaic','swish',0),('hiking','profiles.lisa-focus','tap',0),
    ('sofia-drop','sofia.in','swish',0),('suggest','sofia.suggestion','chime',0),
    ('send','sofia.send-contact','tap',0),('calendar-in','calendar.in','swish',0),
    ('move-marie','calendar.marie-start','swish',0),('move-lisa','calendar.lisa-start','swish',0),
    ('calendar-done','calendar.separate','tap',0),('calendar-out','calendar.mosaic','swish',0),
    ('orbit','apps.first-turn','chime',0),('follow-drop','follow.in','swish',0),
    ('idle-actions','follow.yes','chime',0),('confirm','follow.yes-contact','tap',0),
    ('close','ending.logo','chime',0),('closing-type','ending.imessage','tap',0)
]
scene['timeline']={'version':1,'picture':{'fpsNum':25,'fpsDen':1,'frameCount':778},'initialUI':None,'events':events,
                   'cues':[{'id':i,'eventId':e,'offsetSamples':o,'asset':s} for i,e,s,o in sound]}
scene['score']={'bpm':114,'chords':[[45,52,57,60],[41,48,53,57],[48,55,60,64],[43,50,55,59]],'melody':[0,2,1,3,2,1,3,1],'gain':.94}
p.write_text(json.dumps(scene,indent=2,ensure_ascii=False)+'\n')
