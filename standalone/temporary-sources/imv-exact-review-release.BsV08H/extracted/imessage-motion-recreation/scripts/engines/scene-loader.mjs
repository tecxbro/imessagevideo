import fs from 'node:fs';
import path from 'node:path';

function asData(src,base){if(!src||/^(data:|https?:)/.test(src))return src;const p=path.resolve(base,src),ext=path.extname(p).slice(1).toLowerCase();const mime={png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',svg:'image/svg+xml',webp:'image/webp',ttf:'font/ttf',otf:'font/otf',woff:'font/woff',woff2:'font/woff2'}[ext]??'application/octet-stream';return `data:${mime};base64,${fs.readFileSync(p).toString('base64')}`;}
export function loadScene(filename){const full=path.resolve(filename),base=path.dirname(full),s=JSON.parse(fs.readFileSync(full,'utf8'));const walk=l=>{if(l.src)l.src=asData(l.src,base);(l.children??[]).forEach(walk);};s.layers.forEach(walk);for(const f of s.fonts??[])f.src=asData(f.src,base);return s;}
