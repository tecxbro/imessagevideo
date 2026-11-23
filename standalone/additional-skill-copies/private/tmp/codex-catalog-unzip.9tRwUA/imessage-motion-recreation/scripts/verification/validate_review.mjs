import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {chromium} from '../engines/node_modules/playwright/index.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const args=Object.fromEntries(process.argv.slice(2).reduce((p,v,i,a)=>v.startsWith('--')?[...p,[v.slice(2),a[i+1]]]:p,[]));
const root=path.resolve(args.root??path.join(here,'..'));
const manifestBytes=fs.readFileSync(path.join(root,'delivery-manifest.json'));
const manifest=JSON.parse(manifestBytes);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const result={root,manifestSHA256:hash(manifestBytes),reviewSHA256:hash(fs.readFileSync(path.join(root,'review.html'))),checks:[],pageErrors:[]};
function referenceTime(video,time){
 for(const segment of video.segments){
  const start=segment.candidate_start??segment.output_start??0;
  if(time>=start&&time<start+segment.duration)return(segment.reference_start??segment.source_start??0)+time-start;
 }
 return time;
}
async function decodedSeek(page,id,candidateTime,sourceTime){
 await page.waitForFunction(({id,candidateTime,sourceTime})=>{
  const videos=[...document.querySelectorAll(`section[data-reference="${id}"] .players video`)];
  return videos.length===2&&(videos.some(v=>v.error)||
   videos.every(v=>v.readyState>=2&&!v.seeking)&&Math.abs(videos[1].currentTime-candidateTime)<.02&&Math.abs(videos[0].currentTime-sourceTime)<.09);
 },{id,candidateTime,sourceTime});
 const states=await page.locator(`section[data-reference="${id}"] .players video`).evaluateAll(videos=>videos.map(v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,currentTime:v.currentTime,readyState:v.readyState,seeking:v.seeking,error:v.error?.code??null})));
 if(states.length!==2||states.some(v=>v.error||v.readyState<2||v.seeking))throw new Error('Both players must decode the mapped seek: '+id);
 return states;
}
const server=http.createServer((req,res)=>{
 const pathname=decodeURIComponent(new URL(req.url,'http://local').pathname);
 const file=path.resolve(root,'.'+pathname);
 if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
 try{
  const size=fs.statSync(file).size;let first=0,last=size-1,status=200;
  const match=req.headers.range?.match(/^bytes=(\d+)-(\d*)$/);
  if(match){first=Number(match[1]);last=match[2]?Math.min(Number(match[2]),last):last;status=206;}
  if(first>last||first>=size){res.writeHead(416);res.end();return;}
  const mime={'.html':'text/html','.mp4':'video/mp4','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.md':'text/plain'}[path.extname(file)]??'application/octet-stream';
  const headers={'Content-Type':mime,'Content-Length':last-first+1,'Accept-Ranges':'bytes'};
  if(status===206)headers['Content-Range']=`bytes ${first}-${last}/${size}`;
  res.writeHead(status,headers);fs.createReadStream(file,{start:first,end:last}).pipe(res);
 }catch{res.writeHead(404);res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try{
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH??'/usr/bin/chromium',headless:true,args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});page.setDefaultTimeout(30000);
 page.on('pageerror',error=>result.pageErrors.push(String(error)));
 await page.goto(`http://127.0.0.1:${server.address().port}/review.html`,{waitUntil:'domcontentloaded'});
 if(await page.locator('section[data-reference]').count()!==6)throw new Error('Expected six review sections');
 for(const video of manifest.videos){
  const section=page.locator(`section[data-reference="${video.id}"]`);
  const candidates=video.candidates.filter(c=>c.reference_audio);
  if(candidates.length!==5)throw new Error(video.id+' requires five current soundtrack versions');
  await page.waitForFunction(({id})=>{const v=document.querySelector(`section[data-reference="${id}"] .players>div:first-child video`);return Boolean(v&&(v.readyState>=1||v.error));},{id:video.id});
  const sourceMetadata=await section.locator('video').nth(0).evaluate(v=>({width:v.videoWidth,height:v.videoHeight,readyState:v.readyState,error:v.error?.code??null}));
  if(sourceMetadata.error||sourceMetadata.readyState<1||sourceMetadata.width!==video.source_meta.width||sourceMetadata.height!==video.source_meta.height)throw new Error('Invalid reference player metadata: '+video.source);
  for(const candidate of candidates){
   await section.locator('select').selectOption(candidate.path);
   await page.waitForFunction(({id,target})=>{const v=document.querySelector(`section[data-reference="${id}"] .players>div:last-child video`);return v?.currentSrc.endsWith('/'+target)&&v.readyState>=2&&!v.seeking;},{id:video.id,target:candidate.path});
   const metadata=await section.locator('video').nth(1).evaluate(v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,error:v.error?.code??null}));
   if(metadata.error||metadata.width!==candidate.meta.width||metadata.height!==candidate.meta.height)throw new Error('Invalid player metadata: '+candidate.path);
   const target=Math.min(metadata.duration-.2,metadata.duration*.55);
   const seekTime=await section.locator('input[type=range]').evaluate((slider,t)=>{slider.value=String(t);slider.dispatchEvent(new Event('input',{bubbles:true}));return Number(slider.value);},target);
   const decoded=await decodedSeek(page,video.id,seekTime,referenceTime(video,seekTime));
   await section.locator('button').nth(1).click();
   if(await section.locator('video').nth(1).evaluate(v=>v.muted))throw new Error('Sound toggle failed');
   await section.locator('button').nth(1).click();
   const starts=await section.locator('.players video').evaluateAll(videos=>videos.map(v=>v.currentTime));
   await section.locator('button').nth(0).click();
   await page.waitForFunction(({id,starts})=>{const videos=[...document.querySelectorAll(`section[data-reference="${id}"] .players video`)];return videos.length===2&&videos.every((v,i)=>!v.error&&!v.paused&&!v.seeking&&v.readyState>=2&&v.currentTime>starts[i]+.12);},{id:video.id,starts});
   await section.locator('button').nth(0).click();
   result.checks.push({reference:video.id,path:candidate.path,metadata,sourceMetadata:decoded[0],methodSwitch:true,seek:true,bothPlayersDecoded:true,sourceTimeSync:true,soundToggle:true,playPause:true,bothTimelinesAdvanced:true});
  }
  if(video.segments.length>1){
   const q=video.segments[1],t=(q.candidate_start??q.output_start)+.5;
   const seekTime=await section.locator('input[type=range]').evaluate((slider,t)=>{slider.value=String(t);slider.dispatchEvent(new Event('input',{bubbles:true}));return Number(slider.value);},t);
   await decodedSeek(page,video.id,seekTime,referenceTime(video,seekTime));
   result.timeMapCutPassed=true;
  }
 }
 if(result.pageErrors.length)throw new Error('Review page JavaScript errors');
 result.passed=true;
}catch(error){result.passed=false;result.error=String(error);throw error;}
finally{
 const out=path.resolve(args.out??path.join(here,'review-browser.json'));fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result,null,2));
 if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));
 console.log(JSON.stringify({passed:result.passed,checks:result.checks.length,report:out}));
}
