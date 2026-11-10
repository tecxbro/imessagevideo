from pathlib import Path
import subprocess, json, hashlib
R = Path('/workspace/imessage-recreations')
D = R / 'verification/final/06-gallery/v22'
outs = [1116,1117,1118,1178,*range(1179,1190),1190,1256,*range(1257,1262),1262,1263,1264,1265,1328,*range(1329,1336),1336,1365,1366,1367]
fs = [n+181 for n in outs]
P = D/'source-full'
P.mkdir(exist_ok=True)
T = D/'source-full-sequential'
T.mkdir(exist_ok=True)
expr = '+'.join(f'eq(n\\,{n})' for n in fs)
command = ['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(R/'references/06-gallery/source.mp4'),'-vf','select='+expr,'-fps_mode','passthrough','-frames:v',str(len(fs)),'-c:v','png','-threads','1',str(T/'%06d.png')]
subprocess.run(command,check=True)
records = []
for i,n in enumerate(fs,1):
    a = T/f'{i:06d}.png'
    b = P/f'{n:06d}.png'
    a.replace(b)
    records.append({'sourceFrame':n,'outputFrame':n-181,'sha256':hashlib.sha256(b.read_bytes()).hexdigest()})
(D/'full-native-source-decode.json').write_text(json.dumps({'command':command,'frames':records,'selection':'exact integer source picture indices; no timestamp seek'},indent=2))
print('decoded',len(records))
