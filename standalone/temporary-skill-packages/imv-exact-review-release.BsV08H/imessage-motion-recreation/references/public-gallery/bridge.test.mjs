import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../dist/bridge.html',import.meta.url),'utf8').match(/<script>([\s\S]*)<\/script>/)[1];
const origin='https://message-motion-studio.orchidhq.chatgpt.site';
function setup(fetchImpl=async()=>({ok:true,headers:new Headers({'content-type':'video/mp4','content-length':'4'}),arrayBuffer:async()=>new Uint8Array([1,2,3,4]).buffer})) {
  let listener;const messages=[],calls=[];const parent={postMessage:(...args)=>messages.push(args)};
  vm.runInNewContext(source,{parent,window:{addEventListener:(type,fn)=>listener=fn},fetch:(...args)=>{calls.push(args);return fetchImpl(...args)},AbortController,ArrayBuffer,Set,Map});
  return {parent,messages,calls,send:data=>listener({origin,source:parent,data}),raw:event=>listener(event)};
}
test('bridge announces readiness only to the exact gallery origin',()=>{const c=setup();assert.equal(c.messages[0][0].type,'ready');assert.equal(c.messages[0][1],origin)});
test('untrusted origins and windows cannot request media',async()=>{const c=setup();await c.raw({origin:'https://example.com',source:c.parent,data:{id:'a',type:'load',film:'01-photonhq'}});await c.raw({origin,source:{},data:{id:'a',type:'load',film:'01-photonhq'}});assert.equal(c.calls.length,0)});
test('unknown paths and malformed requests never reach fetch',async()=>{const c=setup();for(const data of [null,{type:'load',film:'01-photonhq'},{id:'a',type:'load',film:'../../private'},{id:'a',type:'load',film:'https://example.com/x.mp4'}])await c.send(data);assert.equal(c.calls.length,0)});
test('valid original request fetches the fixed public path and transfers exact bytes',async()=>{const c=setup();await c.send({id:'a',type:'load',film:'01-photonhq'});assert.equal(c.calls[0][0],'references/01-photonhq/source.mp4');assert.equal(c.calls[0][1].credentials,'omit');const result=c.messages.at(-1);assert.equal(result[0].type,'loaded');assert.equal(result[0].id,'a');assert.equal(result[1],origin);assert.deepEqual([...new Uint8Array(result[0].bytes)],[1,2,3,4]);assert.equal(result[2][0],result[0].bytes)});
test('non-media responses and errors never become a video payload',async()=>{const c=setup(async()=>({ok:true,headers:new Headers({'content-type':'text/html'})}));await c.send({id:'a',type:'load',film:'04-poke'});assert.equal(c.messages.at(-1)[0].type,'error');assert.ok(!c.messages.some(m=>m[0].type==='loaded'))});
test('cancelling an in-flight reference aborts it and prevents stale transfer',async()=>{let finish;const c=setup(()=>new Promise(resolve=>finish=resolve));const work=c.send({id:'a',type:'load',film:'05-linq'});await c.send({id:'a',type:'cancel'});assert.equal(c.calls[0][1].signal.aborted,true);finish({ok:true,headers:new Headers({'content-type':'video/mp4'}),arrayBuffer:async()=>new ArrayBuffer(4)});await work;assert.ok(!c.messages.some(m=>m[0].type==='loaded'))});
