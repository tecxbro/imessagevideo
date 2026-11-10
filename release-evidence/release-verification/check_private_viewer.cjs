const {chromium}=require('/workspace/imessage-recreations/engines/node_modules/playwright');
const fs=require('node:fs');
const crypto=require('node:crypto');
const http=require('node:http');
(async()=>{
 const opts={executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']};
 const proxy=process.env.HTTPS_PROXY||process.env.https_proxy;
 if(proxy){const p=new URL(proxy);opts.proxy={server:p.protocol+'//'+p.host,bypass:(process.env.NO_PROXY||process.env.no_proxy||'').split(',').join(',')};if(p.username)opts.proxy.username=decodeURIComponent(p.username);if(p.password)opts.proxy.password=decodeURIComponent(p.password);}
 // Managed Chrome blocks file:// navigation. Serve the unchanged test page on
 // loopback, the supported app-test path; do not disable browser policy flags.
 const html=fs.readFileSync('/workspace/imessage-recreations/skill/imessage-motion-recreation/library/index.html');
 const server=http.createServer((req,res)=>{if(req.url!=='/'){res.writeHead(404);res.end();return;}res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(html);});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch(opts);
 let page;const errors=[];
 try{
  page=await browser.newPage({viewport:{width:1440,height:1100}});
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:'+server.address().port+'/');
  await page.locator('.film').last().waitFor({timeout:5000});
  const films=await page.locator('.film').count(),methods=await page.locator('.method').count();
  if(films!==6||methods!==5)throw Error('Incorrect visible resource count');
  const mappings=[];
  for(let i=0;i<films;i++){
   await page.locator('.film').nth(i).click();
   const title=await page.locator('#film-title').innerText();
   for(let j=0;j<methods;j++){
    await page.locator('.method').nth(j).click();
    const video=await page.locator('#film-video').getAttribute('src'),open=await page.locator('#open-video').getAttribute('href');
    if(video!==open||!video.endsWith('.mp4'))throw Error('Video/open link mismatch');
    if(await page.locator('.method[aria-pressed="true"]').count()!==1)throw Error('Method selection mismatch');
    mappings.push({title,method:await page.locator('.method').nth(j).innerText(),url:video});
   }
  }
  const options=await page.locator('#source-file option').evaluateAll(xs=>xs.map(x=>x.value)),sources=[];
  for(const name of options){await page.locator('#source-file').selectOption(name);const text=await page.locator('#source-code').textContent();if(!text?.length)throw Error('Missing full source');sources.push({name,bytes:Buffer.byteLength(text),sha256:crypto.createHash('sha256').update(text).digest('hex')});}
  await page.locator('.film').nth(3).click();await page.locator('.method').nth(0).click();
  const playback=await page.locator('#film-video').evaluate(async v=>{await Promise.race([v.play(),new Promise((_,no)=>setTimeout(()=>no(Error('Playback timeout')),20000))]);await new Promise(r=>setTimeout(r,1000));const x={currentTime:v.currentTime,readyState:v.readyState,paused:v.paused,width:v.videoWidth,height:v.videoHeight,duration:v.duration};v.pause();return x;});
  if(playback.currentTime<0.2||playback.readyState<2||!playback.width)throw Error('Video did not decode and advance');
  await page.screenshot({path:'/dev/shm/imessage-private-viewer-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  const mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
  if(mobile.scrollWidth>mobile.width)throw Error('Mobile horizontal overflow');
  await page.screenshot({path:'/dev/shm/imessage-private-viewer-mobile.png',fullPage:true});
  if(errors.length)throw Error(errors.join('\n'));
  const result={status:'pass',scope:'Headless Chromium: six film/five method selectors, thirty URL pairings, full code selections, one actual public film decode/advancing playback, desktop/mobile layout. No claim of all thirty film playbacks.',film_count:films,method_count:methods,video_mappings:mappings,full_sources:sources,playback,mobile,page_errors:errors};
  fs.writeFileSync('/workspace/imessage-recreations/complete-library/private-viewer-browser.audit.json',JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({status:result.status,films,methods,video_mappings:mappings.length,full_sources:sources.length,playback,mobile,page_errors:errors}));
 }catch(e){
  const diagnostic={error:e.message,page_errors:errors};
  if(page){diagnostic.url=page.url();diagnostic.title=await page.title();diagnostic.body=(await page.locator('body').innerText()).slice(0,1800);await page.screenshot({path:'/dev/shm/imessage-private-viewer-failure.png'});}
  fs.writeFileSync('/workspace/imessage-recreations/complete-library/private-viewer-browser.failure.json',JSON.stringify(diagnostic,null,2)+'\n');
  console.error(JSON.stringify(diagnostic));throw e;
 }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
