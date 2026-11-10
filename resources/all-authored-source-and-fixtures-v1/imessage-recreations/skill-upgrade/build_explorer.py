from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]/'skill/imessage-motion-recreation'
D=ROOT/'director'
parts=[]
for path in [ROOT/'scripts/engines/common.mjs',D/'components.mjs',D/'motions.mjs',D/'decisions.mjs']:
    code=re.sub(r'^import .*?;\s*$', '',path.read_text(),flags=re.M)
    code=re.sub(r'^export\s*\{[^}]*\};\s*$', '',code,flags=re.M)
    parts.append(re.sub(r'\bexport\s+', '',code))
parts.append('const CATALOGUE='+json.dumps(json.loads((D/'catalogue.json').read_text()),ensure_ascii=False).replace('<','\\u003c')+';')
parts.append((D/'explorer.js').read_text())
script='\n'.join(parts).replace('</script','<\\/script')
html=(D/'explorer-template.html').read_text().replace('__STYLE__',(D/'explorer.css').read_text()).replace('__SCRIPT__',script)
(D/'index.html').write_text(html)
print('Built standalone explorer:',len(html.encode()),'bytes')
