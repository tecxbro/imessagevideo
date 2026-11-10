/** Streaming, hash-addressed example archive store. No third-party dependencies. */
const ALLOWED=/^[a-z][a-z0-9-]{0,70}$/;
const PART_SIZE_LIMIT=8*1024*1024;
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Access-Control-Allow-Origin':'*'}});
const hex=bytes=>Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('');
const authorized=(request,env)=>Boolean(env.UPLOAD_TOKEN)&&request.headers.get('Authorization')==='Bearer '+env.UPLOAD_TOKEN;
export function parseRange(header,size){
  if(!header)return {start:0,end:size-1,partial:false};
  const m=/^bytes=(\d*)-(\d*)$/.exec(header);if(!m||(!m[1]&&!m[2]))return null;
  let start=m[1]?Number(m[1]):Math.max(0,size-Number(m[2]));
  let end=m[1]?(m[2]?Number(m[2]):size-1):size-1;
  if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start<0||start>=size||end<start)return null;
  return {start,end:Math.min(end,size-1),partial:true};
}
export function segmentsFor(manifest,start,end){
  const result=[];let position=0;
  for(const p of manifest.parts){const a=Math.max(start,position),b=Math.min(end,position+p.bytes-1);if(a<=b)result.push({key:p.key,offset:a-position,length:b-a+1});position+=p.bytes;}
  return result;
}
export function streamArchive(bucket,segments){
  let index=0,reader=null,cancelled=false;
  return new ReadableStream({
    async pull(controller){
      try{
        while(!cancelled){
          if(!reader){if(index>=segments.length){controller.close();return;}const s=segments[index++];const object=await bucket.get(s.key,{range:{offset:s.offset,length:s.length}});if(!object?.body)throw Error('Stored archive part is unavailable');reader=object.body.getReader();}
          const next=await reader.read();if(next.done){reader.releaseLock();reader=null;continue;}
          controller.enqueue(next.value);return;
        }
      }catch(error){if(reader)await reader.cancel().catch(()=>{});controller.error(error);}
    },
    async cancel(){cancelled=true;if(reader)await reader.cancel().catch(()=>{});}
  });
}
async function fetchHandler(request,env){
  const url=new URL(request.url),bucket=env.BUCKET;
  if(request.method==='OPTIONS')return new Response(null,{status:204,headers:{'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'GET, HEAD, OPTIONS','Access-Control-Allow-Headers':'Range','Access-Control-Expose-Headers':'Content-Range, Content-Length, ETag'}});
  if(url.pathname==='/health')return json({ready:Boolean(bucket),writes_enabled:Boolean(env.UPLOAD_TOKEN)});
  if(!bucket)return json({error:'Archive storage binding is unavailable'},503);
  const upload=/^\/admin\/parts\/([a-z][a-z0-9-]{0,70})\/(\d{4})$/.exec(url.pathname);
  if(upload){
    if(request.method!=='PUT'||!authorized(request,env))return json({error:'Not authorized'},403);
    const expected=request.headers.get('X-Content-SHA256');if(!/^[a-f0-9]{64}$/.test(expected??''))return json({error:'Missing SHA256'},400);
    const length=Number(request.headers.get('Content-Length'));if(!Number.isSafeInteger(length)||length<1||length>PART_SIZE_LIMIT)return json({error:'Part exceeds bounded size'},413);
    const body=await request.arrayBuffer();if(body.byteLength!==length)return json({error:'Length mismatch'},400);
    const actual=hex(await crypto.subtle.digest('SHA-256',body));if(actual!==expected)return json({error:'Hash mismatch'},422);
    const key=`parts/${upload[1]}/${upload[2]}`;const existing=await bucket.head(key);
    if(existing&&(existing.size!==length||existing.customMetadata?.sha256!==actual))return json({error:'Immutable part already differs'},409);
    if(!existing)await bucket.put(key,body,{customMetadata:{sha256:actual},httpMetadata:{contentType:'application/octet-stream'}});
    return json({key,bytes:length,sha256:actual,verified:true});
  }
  const commit=/^\/admin\/commit\/([a-z][a-z0-9-]{0,70})$/.exec(url.pathname);
  if(commit){
    if(request.method!=='POST'||!authorized(request,env))return json({error:'Not authorized'},403);
    const m=await request.json();if(m.id!==commit[1]||!ALLOWED.test(m.id)||!Number.isSafeInteger(m.bytes)||m.bytes<1||!/^[a-f0-9]{64}$/.test(m.sha256)||!Array.isArray(m.parts)||m.parts.length<1||m.parts.length>2048)return json({error:'Invalid archive manifest'},400);
    let total=0;const keys=new Set();
    for(let i=0;i<m.parts.length;i++){const p=m.parts[i];if(p.key!==`parts/${m.id}/${String(i).padStart(4,'0')}`||keys.has(p.key)||!Number.isSafeInteger(p.bytes)||p.bytes<1||p.bytes>PART_SIZE_LIMIT||!/^[a-f0-9]{64}$/.test(p.sha256))return json({error:'Invalid part order'},400);keys.add(p.key);const h=await bucket.head(p.key);if(!h||h.size!==p.bytes||h.customMetadata?.sha256!==p.sha256)return json({error:'Part verification failed',part:i},422);total+=p.bytes;}
    if(total!==m.bytes)return json({error:'Archive total mismatch'},422);
    const old=await bucket.get(`manifests/${m.id}.json`);if(old){const previous=await old.json();if(previous.sha256!==m.sha256||previous.bytes!==m.bytes)return json({error:'Immutable archive already differs'},409);}
    await bucket.put(`manifests/${m.id}.json`,JSON.stringify(m),{httpMetadata:{contentType:'application/json'}});return json({id:m.id,bytes:m.bytes,sha256:m.sha256,parts:m.parts.length,committed:true});
  }
  const manifestMatch=/^\/manifests\/([a-z][a-z0-9-]{0,70})\.json$/.exec(url.pathname);
  if(manifestMatch){if(!['GET','HEAD'].includes(request.method))return json({error:'Method not allowed'},405);const obj=await bucket.get(`manifests/${manifestMatch[1]}.json`);if(!obj)return json({error:'Not found'},404);return new Response(request.method==='HEAD'?null:obj.body,{headers:{'Content-Type':'application/json','Access-Control-Allow-Origin':'*','Cache-Control':'public, max-age=3600'}});}
  const archive=/^\/archives\/([a-z][a-z0-9-]{0,70})\.zip$/.exec(url.pathname);
  if(archive){
    if(!['GET','HEAD'].includes(request.method))return json({error:'Method not allowed'},405);
    const object=await bucket.get(`manifests/${archive[1]}.json`);if(!object)return json({error:'Archive not found'},404);const m=await object.json();
    const etag='"'+m.sha256+'"';if(request.headers.get('If-None-Match')===etag)return new Response(null,{status:304,headers:{ETag:etag,'Access-Control-Allow-Origin':'*'}});
    const useRange=!request.headers.get('If-Range')||request.headers.get('If-Range')===etag;
    const range=parseRange(useRange?request.headers.get('Range'):null,m.bytes);if(!range)return new Response(null,{status:416,headers:{'Content-Range':`bytes */${m.bytes}`,'Access-Control-Allow-Origin':'*'}});
    const headers={'Content-Type':'application/zip','Content-Length':String(range.end-range.start+1),'Content-Disposition':`attachment; filename="${m.id}.zip"`,'Accept-Ranges':'bytes','ETag':etag,'Cache-Control':'public, max-age=31536000, immutable','Access-Control-Allow-Origin':'*','Access-Control-Expose-Headers':'Content-Length, Content-Range, ETag, Accept-Ranges'};
    if(range.partial)headers['Content-Range']=`bytes ${range.start}-${range.end}/${m.bytes}`;
    return new Response(request.method==='HEAD'?null:streamArchive(bucket,segmentsFor(m,range.start,range.end)),{status:range.partial?206:200,headers});
  }
  if(url.pathname==='/'&&request.method==='GET')return new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Message motion — complete example archives</title><style>body{font:18px/1.6 system-ui;max-width:760px;margin:10vh auto;padding:24px;background:#f6f5f1;color:#1c252c}h1{font:48px/1.1 Georgia}a{color:inherit}</style><h1>Complete example archives.</h1><p>Verified source projects, assets, evidence and finished motion films for the iMessage director skill.</p><p><a href="https://message-motion-studio.orchidhq.chatgpt.site/director/library.html">Open the full code and video catalogue →</a></p><p>Archives have immutable SHA256 identities and support streaming downloads and byte ranges. The skill’s resource manifest selects the required project instead of loading every example into the model context.</p>`,{headers:{'Content-Type':'text/html; charset=utf-8'}});
  return json({error:'Not found'},404);
}
export default {async fetch(request,env){try{return await fetchHandler(request,env);}catch{return json({error:'Archive request failed'},500);}}};
