import fs from 'node:fs';
import path from 'node:path';
import {buildMotion,MOTIFS} from '../skill/imessage-motion-recreation/director/motions.mjs';
import {COMPONENTS,MessageBubble,Composer,AppIcon,AppCard,BottomSheet,PhoneFrame,ActionButton,Avatar,CameraRig,rect,text,group} from '../skill/imessage-motion-recreation/director/components.mjs';
import {svgMarkup} from '../skill/imessage-motion-recreation/scripts/engines/common.mjs';
const D=path.resolve('skill/imessage-motion-recreation/director'),visuals=path.join(D,'visuals');fs.mkdirSync(visuals,{recursive:true});
for(const motif of MOTIFS){const result=buildMotion(motif),folder=path.join('skill-upgrade','starter-frames',motif);fs.mkdirSync(folder,{recursive:true});
 for(const frame of [0,24,48,72,96,119])fs.writeFileSync(path.join(folder,frame+'.svg'),svgMarkup(result.scene,frame/30));
 fs.mkdirSync(path.join(D,'examples/scenes'),{recursive:true});fs.writeFileSync(path.join(D,'examples/scenes',motif+'.json'),JSON.stringify(result.scene,null,2)+'\n');
 fs.writeFileSync(path.join(D,'examples/scenes',motif+'.events.json'),JSON.stringify({provenance:result.provenance,events:result.events},null,2)+'\n');
}
const demos=[
 MessageBubble({id:'bubble',x:30,y:65,width:255,height:76,copy:'A table for two?'}),
 Composer({id:'composer',x:18,y:80,width:290,copy:'Friday, please.'}),
 AppIcon({id:'icon',x:126,y:52,size:92,label:'A'}),
 AppCard({id:'card',x:46,y:48,width:255,height:210,title:'Friday dinner',detail:'7:00 PM · For two',action:'Reserve'}),
 BottomSheet({id:'sheet',x:22,y:48,width:305,height:208,children:[AppIcon({id:'sheet-a',x:25,y:88,size:60,label:'A'}),AppIcon({id:'sheet-b',x:125,y:88,size:60,label:'B',color:'#6e9c74'})]}),
 PhoneFrame({id:'phone',x:68,y:45,width:230,height:215,title:'Assistant',children:[MessageBubble({id:'phone-message',x:17,y:92,width:180,height:62,copy:'Ready to go.',side:'incoming',fontSize:16})]}),
 ActionButton({id:'button',x:80,y:90,width:190,copy:'Confirm'}),
 Avatar({id:'avatar',x:133,y:64,size:80,initials:'JD'}),
 CameraRig({id:'camera',originX:175,originY:100,children:[rect('camera-context',24,60,300,130,'#e4e9ec',18),MessageBubble({id:'camera-message',x:42,y:87,width:265,height:70,copy:'Focus on the result.',fontSize:18})]})
];
const layers=[];demos.forEach((demo,i)=>{const x=(i%3)*380,y=Math.floor(i/3)*310;layers.push(group('cell-'+i,x,y,[rect('cell-'+i+'-back',0,0,360,292,'#ffffff',16,{stroke:'#d7dde2',strokeWidth:1}),text('cell-'+i+'-label',COMPONENTS[i].name,19,14,19,{fontWeight:600}),demo,text('cell-'+i+'-params',COMPONENTS[i].parameters.slice(0,3).join(' · '),18,267,12,{fill:'#64717d'})]));});
fs.writeFileSync(path.join(visuals,'component-anatomy.svg'),svgMarkup({width:1140,height:930,fps:30,duration:1,background:'#f6f5f1',layers},0));
