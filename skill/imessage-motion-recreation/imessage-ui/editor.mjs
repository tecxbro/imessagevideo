import {buildConversation,canvasMeasure} from './components.mjs';
import {trial} from './trial.mjs';
import {svgMarkup} from '../scripts/engines/common.mjs';

const $=id=>document.getElementById(id);
const measure=canvasMeasure(document.createElement('canvas').getContext('2d'));
let result, frame=0, playing=false, started;
function paint() {
  $('stage').innerHTML=svgMarkup(result.scene,frame/result.scene.fps);
  $('time').value=String(frame);
  $('clock').textContent=`${(frame/result.scene.fps).toFixed(2)}s · frame ${frame}`;
}
function apply(config) {
  const next=buildConversation(config,measure);
  result=next; frame=0; playing=false; $('play').textContent='Play';
  $('config').value=JSON.stringify(config,null,2);
  $('time').max=String(Math.round(result.scene.duration*result.scene.fps)-1);
  $('audit').textContent=JSON.stringify(result.audit,null,2); $('error').textContent=''; paint();
  return result;
}
$('apply').onclick=()=>{try{apply(JSON.parse($('config').value));}catch(error){$('error').textContent=error.message;}};
$('time').oninput=()=>{playing=false; $('play').textContent='Play';frame=Number($('time').value);paint();};
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause':'Play';started=performance.now()-frame/result.scene.fps*1000;};
$('export').onclick=()=>{
  const url=URL.createObjectURL(new Blob([JSON.stringify(result.scene,null,2)],{type:'application/json'}));
  const link=document.createElement('a');link.href=url;link.download='conversation.scene.json';link.click();URL.revokeObjectURL(url);
};
function tick(now) {
  if (playing) {frame=Math.floor((now-started)/1000*result.scene.fps);if(frame>=result.scene.duration*result.scene.fps){frame=0;playing=false;$('play').textContent='Play';}paint();}
  requestAnimationFrame(tick);
}
await document.fonts.ready;
apply(trial);
window.conversationLab={apply,get result(){return result;},seek(value){frame=value;paint();}};
requestAnimationFrame(tick);
