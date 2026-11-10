from pathlib import Path
import subprocess,os,json
root=Path('/workspace/sites/message-motion')
def git(*args,input=None,env=None):return subprocess.check_output(['git',*args],cwd=root,input=input,env=env)
old=git('rev-parse','HEAD').decode().strip();oldtree=git('rev-parse','HEAD^{tree}').decode().strip()
git('update-ref','refs/archive/before-bounded-push',old)
entries=[]
for entry in git('ls-tree','-r','-z','HEAD').split(b'\0'):
 if not entry:continue
 meta,path=entry.split(b'\t',1);mode,kind,sha=meta.split();assert kind==b'blob'
 size=int(git('cat-file','-s',sha.decode()))
 entries.append({'mode':mode.decode(),'sha':sha.decode(),'path':path.decode(),'bytes':size})
entries.sort(key=lambda x:(x['path'].endswith('.mp4'),x['path']))
batches=[];batch=[];size=0;limit=45*1024*1024
for entry in entries:
 if batch and size+entry['bytes']>limit:batches.append(batch);batch=[];size=0
 batch.append(entry);size+=entry['bytes']
if batch:batches.append(batch)
env=os.environ.copy();env['GIT_INDEX_FILE']=str(root/'.git/site-bounded-index')
git('read-tree','--empty',env=env);parent=None;plan=[]
for i,batch in enumerate(batches):
 payload=b''.join((e['mode']+' '+e['sha']+'\t'+e['path']+'\0').encode() for e in batch)
 git('update-index','-z','--index-info',input=payload,env=env)
 tree=git('write-tree',env=env).decode().strip();args=['commit-tree',tree]
 if parent:args+=['-p',parent]
 parent=git(*args,input=f'Publish gallery source batch {i+1}/{len(batches)} within upload limit\n'.encode()).decode().strip()
 plan.append({'commit_sha':parent,'new_bytes':sum(e['bytes'] for e in batch),'new_files':[e['path'] for e in batch]})
assert git('rev-parse',parent+'^{tree}').decode().strip()==oldtree
git('update-ref','refs/heads/main',parent,old);git('config','pack.window','0')
(root/'.git/site-bounded-index').unlink(missing_ok=True)
report={'failure':'267883027-byte initial push rejected by explicit 67108864-byte per-push limit; identical retry prohibited','previous_commit_sha':old,'tree_sha':oldtree,'commit_sha':parent,'raw_batch_limit':limit,'batches':plan,'final_tree_unchanged':True}
(root/'verification/bounded-source-upload.json').write_text(json.dumps(report,indent=2)+'\n')
package=json.loads((root/'verification/source-package.json').read_text());package['previous_commit_sha']=old;package['commit_sha']=parent;package['final_tree_unchanged']=True
(root/'verification/source-package.json').write_text(json.dumps(package,indent=2)+'\n')
print(json.dumps({'batches':len(plan),'largest_raw_batch':max(x['new_bytes'] for x in plan),'commit_sha':parent,'tree_unchanged':True}))
