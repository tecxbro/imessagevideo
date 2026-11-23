import json
from pathlib import Path
checks={'global_mae':18,'pixel_floor':30,'audio':'present','audio_checks':{'max_start_delta_seconds':'1/25'},'regions':[]}
regions=[
('inbox-build',0,12,[320,360,1380,1440],31),('inbox-scroll',42,69,[290,0,1410,1930],24),
('identity',102,119,[640,590,720,810],30),('assistant-hull',134,161,[105,390,1790,1610],32),
('personal-life',162,212,[370,400,1260,780],20),('avatar-assemble',213,228,[135,400,1730,1350],36),
('mosaic',251,273,[90,370,1820,1260],39),('profile-focus',282,312,[245,545,1600,940],31),
('sofia-phone',313,335,[490,0,1020,2000],34),('suggestion',336,352,[730,640,1110,830],27),
('phone-dissolve',353,361,[0,505,2000,1495],29),('send-approach',381,402,[645,475,1300,1310],29),
('calendar-enter',397,417,[230,350,1550,1060],28),('calendar-marie',427,443,[235,660,1570,540],18),
('calendar-lisa',447,463,[235,660,1650,700],18),('calendar-out',471,486,[235,390,1530,1150],30),
('icons-depth',529,590,[350,430,1300,1120],35),('phone-reentry',613,634,[560,0,880,2000],33),
('options-appear',644,658,[555,825,875,630],27),('yes-approach',659,689,[285,535,1430,975],25),
('phone-exit',690,704,[135,190,1740,1610],31),('end-copy',716,765,[480,650,1040,760],27),
('end-fade',766,777,[0,0,2000,2000],16)]
for name,a,b,rect,mae in regions:
    checks['regions'].append({'id':name,'start':a,'end':b,'rect':rect,'mae':mae})
Path('sidehoe-recreation/checks.json').write_text(json.dumps(checks,indent=2)+'\n')
