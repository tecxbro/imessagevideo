export const esc=(s)=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
export const defaults={x:0,y:0,opacity:1,rotation:0,scaleX:1,scaleY:1,originX:0,originY:0};
function cubic(a,b,c,t){let u=1-t;return 3*u*u*t*a+3*u*t*t*b+t*t*t*c;}
export function easeValue(p,name='linear'){
  if(name==='hold')return p>=1?1:0;
  if(name==='easeIn')return p*p*p;
  if(name==='easeOut')return 1-(1-p)**3;
  if(name==='easeInOut')return p<.5?4*p*p*p:1-(-2*p+2)**3/2;
  const match=name.match(/^cubic-bezier\(([^)]+)\)$/);
  if(match){const [x1,y1,x2,y2]=match[1].split(',').map(Number);let lo=0,hi=1;for(let i=0;i<24;i++){let m=(lo+hi)/2;if(cubic(x1,x2,1,m)<p)lo=m;else hi=m;}return cubic(y1,y2,1,(lo+hi)/2);}
  return p;
}
export function interpolate(a,b,p){
 if(typeof a==='number'&&typeof b==='number')return a+(b-a)*p;
 if(/^#[0-9a-f]{6}$/i.test(a)&&/^#[0-9a-f]{6}$/i.test(b)){const channels=[1,3,5].map(i=>Math.round(parseInt(a.slice(i,i+2),16)+(parseInt(b.slice(i,i+2),16)-parseInt(a.slice(i,i+2),16))*p));return '#'+channels.map(v=>v.toString(16).padStart(2,'0')).join('');}
 return p>=1?b:a;
}
export function sampleTrack(track,t){const keys=[...track].sort((a,b)=>a.t-b.t);if(t<=keys[0].t)return keys[0].value;for(let i=1;i<keys.length;i++){const a=keys[i-1],b=keys[i];if(t<=b.t)return interpolate(a.value,b.value,easeValue((t-a.t)/(b.t-a.t),b.ease));}return keys.at(-1).value;}
export function stateAt(layer,t,states){let s={...defaults,...layer,...(states?.[layer.id]??{})};if(!states)for(const [key,track] of Object.entries(layer.keyframes??{}))s[key]=sampleTrack(track,t);return s;}
export function layerMarkup(layer,t,duration,states){
 const s=stateAt(layer,t,states);if(t<(s.start??0)||t>=(s.end??duration)||s.opacity<=0)return '';
 const trans=`translate(${s.x} ${s.y}) translate(${s.originX} ${s.originY}) rotate(${s.rotation}) scale(${s.scaleX} ${s.scaleY}) translate(${-s.originX} ${-s.originY})`;
 const common=`fill="${esc(s.fill??'#000000')}" stroke="${esc(s.stroke??'none')}" stroke-width="${s.strokeWidth??0}"`;
 let shape='';
 if(s.type==='rect')shape=`<rect width="${s.width??0}" height="${s.height??0}" rx="${s.radius??0}" ${common}/>`;
 if(s.type==='circle'){const w=s.width??((s.radius??0)*2),h=s.height??w;shape=`<ellipse cx="${w/2}" cy="${h/2}" rx="${w/2}" ry="${h/2}" ${common}/>`;}
 if(s.type==='path')shape=`<path d="${esc(s.d)}" ${common}/>`;
 if(s.type==='image')shape=`<image href="${esc(s.src)}" width="${s.width}" height="${s.height}" preserveAspectRatio="${s.preserveAspectRatio??'none'}"/>`;
 if(s.type==='text'){const fontSize=s.fontSize??32;const lines=String(s.text??'').split('\n');shape=`<text ${common} font-family="${esc(s.fontFamily??'Arial, sans-serif')}" font-size="${fontSize}" font-weight="${s.fontWeight??400}" letter-spacing="${s.letterSpacing??0}" text-anchor="${s.textAnchor??'start'}" text-decoration="${s.textDecoration??'none'}" dominant-baseline="text-before-edge">${lines.map((line,i)=>`<tspan x="0" y="${i*(s.lineHeight??fontSize*1.2)}">${esc(line)}</tspan>`).join('')}</text>`;}
 if(s.type==='group')shape=(s.children??[]).map(child=>layerMarkup(child,t,duration,states)).join('');
 const clip=s.clip?`clip-path="url(#clip-${esc(s.id)})"`:'';
 if(s.clip)shape=`<defs><clipPath id="clip-${esc(s.id)}"><rect x="${s.clip.x??0}" y="${s.clip.y??0}" width="${s.clip.width}" height="${s.clip.height}" rx="${s.clip.radius??0}"/></clipPath></defs><g ${clip}>${shape}</g>`;
 const filters=[s.shadow?`drop-shadow(${s.shadow.x??0}px ${s.shadow.y??0}px ${s.shadow.blur??0}px ${s.shadow.color??'#000000'})`:null,s.blur?`blur(${s.blur}px)`:null].filter(Boolean).join(' ');
 return `<g data-layer="${esc(s.id)}" transform="${trans}" opacity="${s.opacity}"${filters?` style="filter:${esc(filters)}"`:''}>${shape}</g>`;
}
export function fontCss(scene){return (scene.fonts??[]).map(f=>`@font-face{font-family:'${f.family.replaceAll("'",'')}';src:url('${f.src}');font-weight:${f.weight??400};font-style:${f.style??'normal'};}`).join('');}
export function gradientDefs(scene){return (scene.gradients??[]).map(g=>g.type==='radial'?`<radialGradient id="${esc(g.id)}" cx="${esc(g.cx??'50%')}" cy="${esc(g.cy??'50%')}" r="${esc(g.r??'50%')}">${g.stops.map(s=>`<stop offset="${esc(s.offset)}" stop-color="${esc(s.color)}" stop-opacity="${s.opacity??1}"/>`).join('')}</radialGradient>`:`<linearGradient id="${esc(g.id)}" x1="${esc(g.x1??'0%')}" y1="${esc(g.y1??'0%')}" x2="${esc(g.x2??'0%')}" y2="${esc(g.y2??'100%')}">${g.stops.map(s=>`<stop offset="${esc(s.offset)}" stop-color="${esc(s.color)}" stop-opacity="${s.opacity??1}"/>`).join('')}</linearGradient>`).join('');}
export function svgMarkup(scene,t,states,includeFonts=true){return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${scene.width}" height="${scene.height}" viewBox="0 0 ${scene.width} ${scene.height}">${includeFonts?`<style>${fontCss(scene)}</style>`:''}<defs>${gradientDefs(scene)}</defs><rect width="100%" height="100%" fill="${esc(scene.background??'#ffffff')}"/>${scene.layers.map(l=>layerMarkup(l,t,scene.duration,states)).join('')}</svg>`;}
