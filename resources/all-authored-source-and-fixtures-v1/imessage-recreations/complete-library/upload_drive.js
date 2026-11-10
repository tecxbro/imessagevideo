/* Runs in the functions.exec MCP orchestration runtime, not a browser or Node.
 * upload_selection = [{archive,part}], account/folder IDs come from observed calls.
 * Every part is <=24MiB and gets a private ACL/size check +full SHA readback.
 */
(async()=>{
  const base='/workspace/imessage-recreations/complete-library/drive-ledger/';
  const account='link_6a7d1d2fa9b88191a69772ceb53e1d41';
  const q=s=>"'"+String(s).replaceAll("'","'\\''")+"'";
  const unwrap=r=>{
    if(r.isError)throw Error((r.content?.find(c=>c.type==='text')?.text||'Drive action failed').slice(0,500));
    if(r.structuredContent)return r.structuredContent;
    for(const c of r.content||[]){if(c.type==='text'){try{return JSON.parse(c.text);}catch{}}}
    throw Error('Unexpected connected-file response');
  };
  const write=async(name,value)=>tools.apply_patch('*** Begin Patch\n*** Add File: '+base+name+'\n+'+JSON.stringify(value,null,2).split('\n').join('\n+')+'\n*** End Patch');
  const selection=load('upload_selection');
  const results=await Promise.allSettled(selection.map(async({archive,part})=>{
    const key=archive.id+'-'+String(part.number).padStart(3,'0');
    let record=load('drive_uploaded_'+key);
    if(!record){
      const folder=load('complete_drive_'+archive.category);
      const d=unwrap(await tools.mcp__codex_apps__google_drive_upload_file({link_id:account,parent_folder_id:folder.id,file_uri:part.path,file_name:part.file_name,mime_type:'application/octet-stream'}));
      if(!d.success||!d.id||!d.url)throw Error('Upload did not confirm a file ID');
      record={archive_id:archive.id,part_number:part.number,file_name:part.file_name,bytes:part.bytes,sha256:part.sha256,drive_id:d.id,drive_url:d.url,parent_id:folder.id,account_link_id:account,uploaded:true,verified:false};
      store('drive_uploaded_'+key,record);await write('uploaded-'+key+'.json',record);
      notify({uploaded:part.file_name,bytes:part.bytes});
    }
    const meta=unwrap(await tools.mcp__codex_apps__google_drive_get_file_metadata({link_id:account,fileId:record.drive_id,fields:'id,name,mimeType,size,webViewLink,parents,permissions'}));
    if(Number(meta.size)!==part.bytes||!(meta.parent_ids||meta.parents||[]).includes(record.parent_id))throw Error('Drive size or parent readback mismatch');
    if(!Array.isArray(meta.permissions)||!meta.permissions.length||meta.permissions.some(p=>p.type==='anyone'||p.type==='domain'||p.type==='group'||p.type==='user'&&p.role!=='owner'))throw Error('Cannot verify owner-private file permissions');
    const raw=unwrap(await tools.mcp__codex_apps__google_drive_fetch({link_id:account,url:record.drive_url,download_raw_file:true,include_base64:false}));
    const uri=raw.file_uri||raw.structuredContent?.file_uri;
    if(!uri?.file_id?.startsWith('sediment://file_'))throw Error('Raw private Drive fetch did not return a materializable file reference');
    const materialized=await tools.download_file({file_id:uri.file_id.replace('sediment://','')});
    if(!materialized.path)throw Error('Connected file materialization returned no local path');
    const proof=await tools.exec_command({cmd:'python /workspace/imessage-recreations/complete-library/verify_readback.py '+q(materialized.path)+' '+q(part.sha256)+' '+q(part.bytes),login:false,max_output_tokens:500});
    if(proof.exit_code!==0)throw Error('Private readback verification failed: '+proof.output.slice(0,300));
    record={...record,verified:true,permission_scope:'owner-private',metadata_size_verified:true,full_download_sha256_verified:true};
    store('drive_uploaded_'+key,record);await write('verified-'+key+'.json',record);
    notify({verified:part.file_name,bytes:part.bytes});return record;
  }));
  results.forEach(r=>text(r.status==='fulfilled'?{archive:r.value.archive_id,part:r.value.part_number,verified:true}:{error:String(r.reason)}));
})();
