#!/usr/bin/env python3
"""Build a local, offline review page from completed recreation artifacts."""
from pathlib import Path
import json, html, subprocess, hashlib

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    '01-photonhq': 'Photon 2.0',
    '02-danieltian': 'Photon Agent to Agent',
    '03-photon-mini': 'Photon Mini Apps',
    '04-poke': 'Poke Apple Messages',
    '05-linq': 'Linq iMessage Apps',
    '06-gallery': 'Rene',
}
METHODS = ('remotion', 'gsap', 'html', 'pillow', 'motion-canvas')

def probe(path):
    result = subprocess.run(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=width,height,r_frame_rate,nb_frames,duration',
        '-of','json',str(path)], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)['streams'][0]
    except (ValueError, KeyError, IndexError):
        return {}

def relative(path):
    return str(path.relative_to(ROOT))

def build():
    videos = []
    state_path=ROOT/'delivery-state.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else {'scenes':{}}
    for folder, title in TITLES.items():
        current=state['scenes'].get(folder,{})
        scene_path=ROOT/current['scene'] if current.get('scene') else None
        current_hash=hashlib.sha256(scene_path.read_bytes()).hexdigest() if scene_path else None
        ref = ROOT/'references'/folder
        out = ROOT/'outputs'/folder
        source = ref/'source.mp4'
        candidates = []
        paths = [directory/(method+'.mp4')
                 for directory in (ROOT/'deliverables'/folder, out)
                 for method in METHODS]
        for p in paths:
            if not p.exists(): continue
            if not Path(str(p)+'.render.json').exists() and not p.with_suffix('.audio.json').exists():
                continue
            meta = probe(p)
            if meta:
                audio=p.with_suffix('.audio.json').exists()
                sidecar=p.with_suffix('.audio.json') if audio else Path(str(p)+'.render.json')
                record=json.loads(sidecar.read_text())
                if current_hash and record.get('sceneSHA256',record.get('sceneSha256'))!=current_hash:
                    continue
                candidates.append({'path':relative(p),'label':p.stem+(' · reference audio' if audio else ' · silent master'),'meta':meta,'reference_audio':audio,'provenance':record})
        candidates.sort(key=lambda c:(not(c['reference_audio'] and c['label'].startswith('remotion')),not c['label'].startswith('remotion'),c['label']))
        reports = []
        canonical=ROOT/'verification'/'final'/folder
        search_roots=([canonical] if canonical.exists() else
            [out,ref/'verification',ref/'qa',ROOT/'verification'/'results'/folder])
        seen=set()
        for search in search_roots:
            for p in search.rglob('report.json') if search.exists() else []:
                if p in seen: continue
                seen.add(p)
                data=json.loads(p.read_text())
                if not (p.parent/'index.html').exists(): continue
                if current.get('source_report'):
                    wanted=Path(current['source_report'])
                    if wanted.suffix=='.json':wanted=wanted.with_name('index.html')
                    if relative(p.parent/'index.html')!=str(wanted):continue
                reports.append({'label':p.parent.name,'path':relative(p.parent/'index.html'),
                    'summary':data.get('summary',{})})
        segments=[]
        for p in [ref/'segments.json',out/'segments.json']:
            if p.exists():
                data=json.loads(p.read_text())
                segments=data if isinstance(data,list) else data.get('segments',[])
                break
        timeline=ROOT/current['timeline_scan'] if current.get('timeline_scan') else None
        videos.append({'id':folder,'title':title,'source':relative(source),
            'source_meta':probe(source),'candidates':candidates,'reports':reports,
            'segments':segments,'analysis':relative(ref/'analysis.md'),
            'sceneSHA256':current_hash,'timeline_scan':json.loads(timeline.read_text()) if timeline and timeline.exists() else None})
    manifest={'videos':videos,'figma':json.loads((ROOT/'figma/status.json').read_text()),
        'fidelity':'Independent native reconstructions. Consult comparisons for remaining differences; no 100% equivalence claim.',
        'audio':'Silent graphic masters and explicitly labeled versions with the reference soundtrack are separate artifacts.'}
    (ROOT/'delivery-manifest.json').write_text(json.dumps(manifest,indent=2))
    encoded=json.dumps(manifest).replace('</','<\\/')
    page='''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>iMessage motion recreation review</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f5f7;color:#15171c;font:15px system-ui,sans-serif}
main{max-width:1480px;margin:auto;padding:32px}h1{font-size:32px;letter-spacing:-1px;margin:0 0 10px}h2{font-size:23px;margin:0 0 18px}p{line-height:1.6;max-width:900px}a{color:#1265cc}section{background:white;border:1px solid #dfe3e9;border-radius:18px;padding:24px;margin:24px 0}.players{display:grid;grid-template-columns:1fr 1fr;gap:16px}video{width:100%;background:#e9ebef;display:block;border-radius:10px;aspect-ratio:16/9;object-fit:contain}.caption{display:flex;justify-content:space-between;gap:12px;margin:10px 0;font-weight:600}select,button{font:inherit;padding:8px 12px;border:1px solid #cdd3dd;border-radius:8px;background:white}button{cursor:pointer}.controls{display:flex;align-items:center;gap:12px;margin:18px 0}.controls input{flex:1}.meta{color:#637083;font-size:13px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:9px;border-bottom:1px solid #e4e8ed}pre{white-space:pre-wrap}details{margin-top:14px}summary{cursor:pointer}code{background:#eef2f7;padding:2px 5px;border-radius:4px}@media(max-width:800px){main{padding:16px}.players{grid-template-columns:1fr}section{padding:16px}}
</style><main><h1>iMessage motion recreation review</h1>
<p>Compare each supplied reference with the independent editable reconstruction. The controls synchronize video time; Rene skips the live-action section through an explicit time map.</p>
<p class="meta">Five local methods are available. Figma Motion could not be accessed, so no Figma file or export was produced. Choose a reference-audio version to hear the supplied soundtrack, or a silent graphic master.</p>
<p><a href="skill/imessage-motion-recreation/SKILL.md">Reusable skill</a> · <a href="README.md">Artifacts and status</a> · <a href="delivery-manifest.json">Delivery manifest</a></p><div id="app"></div></main>
<script>const data=__DATA__;
const el=(tag,cls,text)=>{let e=document.createElement(tag);if(cls)e.className=cls;if(text)e.textContent=text;return e};
const fmt=n=>Number.isFinite(n)?n.toFixed(3):'—';
for(const v of data.videos){
 let s=el('section');s.dataset.reference=v.id;s.append(el('h2','',v.title));let players=el('div','players'),left=el('div'),right=el('div');
 let a=el('video'),b=el('video');a.src=v.source;a.preload=b.preload='metadata';a.muted=b.muted=true;a.controls=b.controls=true;
 left.append(el('div','caption','Reference'),a);let cap=el('div','caption'),select=el('select');cap.append(el('span','','Reconstruction'),select);right.append(cap,b);players.append(left,right);s.append(players);
 for(const c of v.candidates){let o=el('option','',c.label);o.value=c.path;select.append(o)}
 if(v.candidates.length)b.src=v.candidates[0].path;else right.append(el('p','','No completed reconstruction discovered yet.'));
 let m=v.source_meta;s.append(el('p','meta',`${m.width} × ${m.height} · ${m.r_frame_rate} fps · ${m.nb_frames||'?'} reference frames · ${m.duration||'?'} seconds`));
 let controls=el('div','controls'),play=el('button','','Play both'),sound=el('button','','Enable reconstruction sound'),slider=el('input'),time=el('span','meta','0.00s');slider.type='range';slider.min=0;slider.step='.01';slider.value=0;slider.max=Number(m.duration)||60;controls.append(play,sound,slider,time);s.append(controls);
 sound.onclick=()=>{b.muted=!b.muted;sound.textContent=b.muted?'Enable reconstruction sound':'Mute reconstruction'};
 function sourceTime(t){for(let q of v.segments){let st=q.candidate_start??q.output_start??0;if(t>=st&&t<st+q.duration)return(q.reference_start??q.source_start??0)+t-st}return t}
 function seek(t){b.currentTime=t;a.currentTime=sourceTime(t);slider.value=t;time.textContent=t.toFixed(2)+'s'}
 slider.oninput=()=>{a.pause();b.pause();play.textContent='Play both';seek(+slider.value)};
 select.onchange=()=>{let t=b.currentTime||0;b.src=select.value;b.onloadedmetadata=()=>{slider.max=b.duration;seek(Math.min(t,b.duration))}};
 b.addEventListener('loadedmetadata',()=>slider.max=b.duration);
 play.onclick=()=>{if(b.paused){seek(b.currentTime||0);Promise.allSettled([a.play(),b.play()]);play.textContent='Pause both'}else{a.pause();b.pause();play.textContent='Play both'}};
 b.addEventListener('timeupdate',()=>{slider.value=b.currentTime;time.textContent=b.currentTime.toFixed(2)+'s';let t=sourceTime(b.currentTime);if(Math.abs(a.currentTime-t)>.09)a.currentTime=t});
 b.addEventListener('ended',()=>{a.pause();play.textContent='Play both'});
 if(v.timeline_scan){let q=v.timeline_scan;s.append(el('p','meta',`All ${q.frames_scanned} aligned picture frames measured · Mean RGB error ${fmt(q.mean_native_mae)} · Maximum ${fmt(q.maximum_native_mae)}. These are error measurements, not a perfection percentage.`))}
 if(v.reports.length){let table=el('table'),head=el('tr');for(let t of ['Comparison','Frames','Global MAE ↓','Foreground MAE ↓','Luma SSIM ↑'])head.append(el('th','',t));table.append(head);
 for(let r of v.reports){let tr=el('tr'),td=el('td'),link=el('a','',r.label);link.href=r.path;td.append(link);tr.append(td);let q=r.summary;for(let n of [q.frames_sampled,q.global?.mae,q.foreground_union?.mae,q.global?.mean_ssim_luma])tr.append(el('td','',typeof n==='number'?fmt(n):'—'));table.append(tr)}s.append(table)}
 let link=el('a','','Source analysis');link.href=v.analysis;s.append(link);if(v.segments.length){let d=el('details'),p=el('pre','',JSON.stringify(v.segments,null,2));d.append(el('summary','','Source-to-output timing'),p);s.append(d)}document.querySelector('#app').append(s)
}
</script>'''.replace('__DATA__',encoded)
    (ROOT/'review.html').write_text(page)
    print(json.dumps({'review':str(ROOT/'review.html'),'videos':len(videos),
        'completed_video_files':sum(len(v['candidates']) for v in videos)},indent=2))

if __name__ == '__main__': build()
