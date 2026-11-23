from pathlib import Path
import ast, collections, hashlib, json, re, subprocess
work=Path('/tmp/imv-goal-production-01-02'); root=Path('codex-direction-library'); commit='c49482aec7b8ed0b840f97c61a5e5b860c4077b6'
TOPICS={
 'archive': r'gzip|unlink\(|replace\(tmp|os\.replace|archive',
 'verify': r'assert |proof|\bMAE\b|np\.array_equal|sha256|\bverif|control.?frame|outside',
 'native': r'ffmpeg|\bframe\b|\bframes\b|evaluateScene|evaluateLayer',
 'material': r'material|opacity|alpha|blur|matte|gradient|contour',
 'semantic-ui': r'emoji|avatar|composer|query|phonebook|body|bubble|glyph|typing|crop\(',
 'transform': r'\bscale[XY]\b|rotation|affine|camera|keyframes|origin[XY]',
 'inputs': r'read_text|read_bytes|open\(|\bload\(|\bloads\(',
 'mutating': r'write_text|write_bytes|unlink\(|\.save\(|copyfile\(|shutil\.|os\.replace',
 'subprocess':r'subprocess\.|\bexec\(|import.*from.*\.mjs|spawn\(|chromium|process\.argv',
 'historical-paths': r'/workspace/|scene.*v[0-9]+|cache.*v[0-9]+|outputs/|reference/|/tmp/',
}
paths=subprocess.check_output(['git','-C',str(root),'ls-tree','-r','--name-only',commit],text=True).splitlines()
for pack in ('01-photonhq-complete-v1','02-danieltian-complete-v1'):
 base=f'projects/{pack}/imessage-recreations/references/{pack.removesuffix("-complete-v1")}/'
 inputs=json.loads((work/(pack+'.json')).read_text()); known={x['asset'] for x in inputs}
 retained={x for x in paths if x.startswith(base) and Path(x).suffix in {'.py','.js','.mjs','.ts','.jsx','.tsx','.sh','.md','.css','.html'}}
 assert known == retained, (known-retained,retained-known)
 excluded=[x for x in paths if x.startswith(base) and x not in retained]
 print(pack,len(retained),len(excluded),dict(collections.Counter(Path(x).suffix for x in excluded)))
 summaries=[]
 for x in inputs:
  b=(root/x['asset']).read_bytes(); assert hashlib.sha256(b).hexdigest()==x['sha256']; assert len(b)==x['bytes']
  s=b.decode(); lines=s.splitlines(); assert abs(len(lines)-x['lines'])<=1
  x['excluded_scope']=None; x['recomputed_lines']=len(lines)
  x['topics']={topic:[i for i,l in enumerate(lines,1) if re.search(expr,l,re.I)] for topic,expr in TOPICS.items()}
  x['relevant_lines']=sorted(set(i for match in x['topics'].values() for i in match))
  if x['ext']=='.py':
   try:
    tree=ast.parse(s)
   except SyntaxError as e:
    x['parser']=f'Python syntax error {e.lineno}: {e.msg}'
   else:
    x['parser']='Python AST OK'
    x['funcs']=[{'name':n.name,'start':n.lineno,'end':n.end_lineno} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
    x['inputs_calls']=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['read_text','read_bytes','open']]
    x['outputs_calls']=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['write_text','write_bytes','save','unlink','replace','copyfile']]
  else:
   x['parser']='UTF-8 and line inventory'
  signatures=[]
  for l in lines:
   m=re.search(r'(?:scene|source|input|proof|render|gate|native|frame|cache|merge|patch|scope|compare|output|final|audit|resume)[-_/\w.]*\.(?:json|png|mp4|py|mjs|gz)',l,re.I)
   if m and m.group(0) not in signatures:signatures.append(m.group(0))
  x['file_references']=signatures[:8]
  flags=','.join(topic for topic,num in sorted(x['topics'].items(),key=lambda kv:-len(kv[1])) if num)
  print(f"{x['refpath']} {len(lines)}L {len(x['relevant_lines'])} indexed | {flags} |", ', '.join(f"{f['name']}:{f['start']}–{f['end']}" for f in x.get('funcs',[])[:8]),'|', ','.join(signatures[:4]))
 (work/('scan-'+pack+'.json')).write_text(json.dumps(inputs))
 (work/('excluded-'+pack+'.json')).write_text(json.dumps(excluded))
