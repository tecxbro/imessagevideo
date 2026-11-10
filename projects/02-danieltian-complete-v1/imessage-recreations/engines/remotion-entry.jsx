import React,{useEffect,useState} from 'react';
import {Composition,registerRoot,useCurrentFrame,useVideoConfig,delayRender,continueRender,cancelRender} from 'remotion';
import {svgMarkup,fontCss} from './common.mjs';
const Scene=({scene})=>{const frame=useCurrentFrame();const {fps}=useVideoConfig();
 const [fontHandle]=useState(()=>delayRender('Loading measured scene fonts'));
 useEffect(()=>{let active=true;Promise.all((scene.fonts??[]).map(f=>document.fonts.load(`${f.style??'normal'} ${f.weight??400} 16px "${f.family}"`))).then(()=>{if(active)continueRender(fontHandle)}).catch(cancelRender);return()=>{active=false}},[scene,fontHandle]);
 return <><style dangerouslySetInnerHTML={{__html:fontCss(scene)}}/><div style={{width:'100%',height:'100%'}} dangerouslySetInnerHTML={{__html:svgMarkup(scene,frame/fps,undefined,false)}}/></>;};
const Root=()=> <Composition id="MeasuredScene" component={Scene} width={640} height={360} fps={30} durationInFrames={60} defaultProps={{scene:{width:640,height:360,fps:30,duration:2,layers:[]}}} calculateMetadata={({props})=>({width:props.scene.width,height:props.scene.height,fps:props.scene.fps,durationInFrames:Math.round(props.scene.duration*props.scene.fps)})}/>;
registerRoot(Root);
