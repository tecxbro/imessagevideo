/* Run only in the functions.exec orchestration runtime. No credentials stored. */
(async()=>{
 const base='/workspace/imessage-motion-local/tools/restore_local.py';
 const q=s=>"'"+String(s).replaceAll("'","'\\''")+"'";
 const unwrap=r=>{if(r.isError)throw Error('Connected Drive read failed');if(r.structuredContent)return r.structuredContent;for(const c of r.content||[])if(c.type==='text'){try{return JSON.parse(c.text)}catch{}}throw Error('Unexpected Drive response');};
 const planned=await tools.exec_command({cmd:'python '+q(base)+' pending --limit 8',login:false,max_output_tokens:8000});
 if(planned.exit_code!==0)throw Error(planned.output);
 const rows=JSON.parse(planned.output);
 const results=await Promise.allSettled(rows.map(async x=>{
  const meta=unwrap(await tools.mcp__codex_apps__google_drive_get_file_metadata({link_id:x.account_link_id,fileId:x.drive_id,fields:'id,name,mimeType,size,permissions'}));
  if(Number(meta.size)!==x.bytes)throw Error('Remote size mismatch '+x.file_name);
  const raw=unwrap(await tools.mcp__codex_apps__google_drive_fetch({link_id:x.account_link_id,url:x.drive_url,download_raw_file:true,include_base64:false}));
  const uri=raw.file_uri||raw.structuredContent?.file_uri;
  if(!uri?.file_id?.startsWith('sediment://file_'))throw Error('No materializable private file '+x.file_name);
  const dl=await tools.download_file({file_id:uri.file_id.replace('sediment://','')});
  if(!dl.path)throw Error('No local materialization '+x.file_name);
  const committed=await tools.exec_command({cmd:'python '+q(base)+' commit --archive '+q(x.archive_id)+' --part '+x.number+' --source '+q(dl.path),login:false,max_output_tokens:500});
  if(committed.exit_code!==0)throw Error(committed.output);
  return JSON.parse(committed.output);
 }));
 for(const r of results)text(r.status==='fulfilled'?r.value:{error:String(r.reason)});
 const failures=results.filter(r=>r.status==='rejected');
 text(await tools.exec_command({cmd:'python '+q(base)+' progress',login:false,max_output_tokens:300}));
 if(failures.length)throw Error(failures.length+' download(s) failed; inspect before retry');
})();
