const native = 30000 / 1001;
const id = 'location-question-bridge';
export const entries = [{
  id,
  title:'Hold the location question while switching from keyboard to map',
  moves:'The lower camera pushes toward a location control; the keyboard and composer clear, and a map occupies their former region.',
  fixed:'The question remains the readable anchor. It nudges with the camera push, then holds through the change of surfaces.',
  notice:'The map is the direct answer to the same location question, and the empty interval gives the change room to read.',
  fits:'Carry a specific question across composer action and visual answer, retaining the question as the bridge.',
  avoid:'Use a traveling pin when the physical token itself has to trace the correspondence.',
  intents:['Keep the location question anchored while the composer suggests a location, then open the map','Hold the question while the keyboard drops away and the location card comes in','Show a location response without losing the original question'],
  editable:['heading','copy','title','detail','action'],
  defaults:{copy:'Where should we meet?', title:'North gate', detail:'Shared location', action:'Current location'},
  source:{
    kind:'measured-adaptation',
    ref:'projects/04-poke-complete-v1/imessage-recreations/references/04-poke/source.mp4',
    range:[413/native,520/native], framesInclusive:[413,519],
    note:'Recreation measured readable question f413–414, keyboard push f449–450, location control f455–457, dim f485, question held during gap f512 and map readable f513–514. The map card carries the measured pin rise f513–519 (centroid y 697.44 to 590.22) mapped onto a new travel distance. Other geometry and compressed timing are authored.',
  },
  build(ctx) {
    const {stage, group, rect, text, colors, content, track, event, ui} = ctx;
    const question = ui.MessageBubble({id:'held-question',x:30,y:18,width:351,height:46,copy:content.copy,side:'incoming',fontSize:16});
    const control = group('location-control',26,4,[
      rect('location-control-back',0,0,240,30,'#d5e7f8',14),
      text('location-control-copy',content.action,15,6,14,{fill:'#174675',fontWeight:700}),
    ]);
    const keys = 'QWERTYUIOPASDFGHJKLZXCVBNM'.split('').map((letter,i)=>{
      const col = i < 10 ? i : i < 19 ? i-10 : i-19;
      const row = i < 10 ? 0 : i < 19 ? 1 : 2;
      return group(`key-${i}`,24+col*42+row*10,96+row*26,[
        rect(`key-${i}-surface`,0,0,37,21,'#ffffff',4),
        text(`key-${i}-text`,letter,14,3,12,{fill:colors.ink}),
      ]);
    });
    const lower = group('location-composer-plane',0,112,[
      rect('keyboard-matte',10,43,480,128,'#d6e1eb',14),
      ui.Composer({id:'location-composer',x:23,y:39,width:454,copy:'',active:false}), ...keys, control,
    ],{originX:250,originY:44});
    const map = group('shared-location-map',26,75,[
      rect('shared-map-surface',0,0,448,191,'#dbe7da',18),
      {id:'shared-map-roads',type:'path',d:'M -4 123 C 61 96 129 99 190 137 S 303 119 452 46 M 230 -4 C 213 60 286 125 313 194 M 27 -7 C 53 50 129 74 107 191',fill:'none',stroke:'#ffffff',strokeWidth:9},
      rect('map-nameplate',20,117,220,54,'#ffffff',9),
      text('map-title',content.detail,29,124,17,{fontWeight:700}),
      text('map-location',content.title,29,149,15,{fill:colors.muted}),
      {id:'shared-map-pin',type:'circle',x:294,y:62,width:20,height:20,fill:colors.blue,stroke:'#ffffff',strokeWidth:2},
    ], {clip:{x:0,y:0,width:448,height:191,radius:18}});
    track(control,'opacity',[[0,0],[.33,0],[.40,1],[.59,1],[.67,.35]]);
    for (const prop of ['scaleX','scaleY']) track(lower,prop,[[0,1],[.24,1],[.37,1.08,'easeOut']]);
    track(lower,'y',[[0,112],[.24,112],[.37,91,'easeOut'],[.67,91],[.76,311,'easeIn']]);
    track(question,'y',[[0,18],[.24,18],[.37,10,'easeOut']]);
    track(map,'opacity',[[0,0],[.80,1,'hold']]);
    const pinY = [697.443,639.676,619.774,608.281,600.263,594.591,590.223];
    const mapFrame = Math.ceil(.80 * ctx.frameCount);
    const settleFrames = Math.round(.11 * ctx.frameCount);
    track(map,'y',pinY.map((y,i)=>[(mapFrame+i*settleFrames/6)/ctx.frameCount,
      75 + 35 * (y-pinY.at(-1))/(pinY[0]-pinY.at(-1))]));
    stage.children.push(lower,map,question);
    ctx.label(content.detail);
    event('question-readable',0,question.id,'message.readable');
    event('location-control-visible',.34,control.id,'location.suggest');
    event('location-control-pressed',.60,control.id,'location.select');
    event('map-visible',.80,map.id,'location.show');
  },
}];
