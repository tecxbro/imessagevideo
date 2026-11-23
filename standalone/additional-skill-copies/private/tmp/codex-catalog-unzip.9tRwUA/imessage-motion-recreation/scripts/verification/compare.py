#!/usr/bin/env python3
"""Evidence-first video comparison. Dependencies: ffmpeg, ffprobe, Pillow, NumPy."""
import argparse, csv, html, io, json, math, subprocess, sys, hashlib, tempfile
from pathlib import Path
from fractions import Fraction
import numpy as np
from PIL import Image, ImageFilter


def command(args):
    result = subprocess.run(args, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {args[0]}\n{result.stderr.decode(errors='replace')[-3000:]}")
    return result.stdout


def probe(path):
    raw = json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    video = next(s for s in raw['streams'] if s['codec_type']=='video')
    fps = float(Fraction(video.get('avg_frame_rate','0/1')))
    nominal_fps = float(Fraction(video.get('r_frame_rate','0/1')))
    return {'path':str(Path(path).resolve()), 'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(), 'width':video['width'],'height':video['height'],
            'fps':fps,'nominal_fps':nominal_fps,'duration':float(video.get('duration',raw['format']['duration'])),
            'frame_count':int(video['nb_frames']) if video.get('nb_frames','N/A').isdigit() else None,
            'codec':video['codec_name'],'pixel_format':video.get('pix_fmt'),'raw':raw}


def get_frame(path,t,width=None):
    args=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss',f'{t:.9f}','-i',str(path),'-frames:v','1']
    if width: args += ['-vf',f'scale={width}:-1:flags=lanczos']
    args += ['-f','image2pipe','-vcodec','png','-threads','1','pipe:1']
    data = command(args)
    if not data: raise RuntimeError(f'No frame at {t:.9f}s in {path}')
    return Image.open(io.BytesIO(data)).convert('RGB')

def native_frame_index(t,info):
    """Accept exact average cadence, or negligible MP4 duration-rounding drift.

    Keep fps/average timing unchanged for existing reports. Nominal cadence is
    allowed only within one part per million and when both rates round to the
    same integer picture. This never silently snaps an arbitrary sample time.
    """
    average=info['fps'];position=t*average;n=round(position)
    if abs(position-n)<=1e-5:return n
    nominal=info.get('nominal_fps',0)
    if nominal>0 and average>0 and abs(nominal-average)/average<=1e-6:
        nominal_position=t*nominal
        if abs(nominal_position-round(nominal_position))<=1e-5 and round(nominal_position)==n:
            return n
    raise ValueError('--batch-native requires exact native frame timestamps')

def batch_native_frames(path,times,info,width,folder):
    """Decode requested native indices once; reject non-native timestamps."""
    indices=sorted({native_frame_index(t,info) for t in times})
    folder.mkdir(parents=True,exist_ok=True)
    ranges=[]
    for n in indices:
        if ranges and n==ranges[-1][1]+1:ranges[-1][1]=n
        else:ranges.append([n,n])
    select='select='+ '+'.join(f'eq(n\\,{a})' if a==b else f'between(n\\,{a}\\,{b})' for a,b in ranges)
    if width:select+=f',scale={width}:-1:flags=lanczos'
    command(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(path),
        '-vf',select,'-fps_mode','passthrough','-frames:v',str(len(indices)),
        '-pix_fmt','rgb24','-c:v','png','-threads','1',str(folder/'%06d.png')])
    result={n:folder/f'{i+1:06}.png' for i,n in enumerate(indices)}
    if any(not p.is_file() for p in result.values()):raise ValueError('Incomplete native batch decode')
    return result


def mean_box(a,size=11):
    # Valid box mean. Float64 integral sum avoids accumulated precision error.
    p=np.pad(a.astype(np.float64),((1,0),(1,0))).cumsum(0).cumsum(1)
    return (p[size:,size:]-p[:-size,size:]-p[size:,:-size]+p[:-size,:-size])/(size*size)


def ssim_map(a,b):
    # Luma SSIM, uniform 11x11 window, population variance, standard C1/C2.
    a=np.dot(a.astype(np.float64),[.2126,.7152,.0722]); b=np.dot(b.astype(np.float64),[.2126,.7152,.0722])
    k=min(11,min(a.shape)); k=k if k%2 else k-1
    ma,mb=mean_box(a,k),mean_box(b,k)
    va=np.maximum(0,mean_box(a*a,k)-ma*ma); vb=np.maximum(0,mean_box(b*b,k)-mb*mb)
    cov=mean_box(a*b,k)-ma*mb
    return ((2*ma*mb+6.5025)*(2*cov+58.5225))/((ma*ma+mb*mb+6.5025)*(va+vb+58.5225)),k


def metrics(a,b,mask=None,delta=8):
    d=a.astype(np.float64)-b.astype(np.float64)
    if mask is not None:
        if not mask.any(): return {'pixels':0,'mae':None,'rmse':None,'psnr_db':None,'changed_pixel_percent':None}
        d=d[mask]
    mse=float(np.mean(d*d)); rmse=math.sqrt(mse)
    changed=np.max(np.abs(d),axis=-1)>delta
    return {'pixels':int(d.size//3),'mae':float(np.mean(np.abs(d))),'rmse':rmse,
            'psnr_db':(10*math.log10(255*255/mse) if mse else None),
            'psnr_infinite':mse==0,'changed_pixel_percent':float(changed.mean()*100)}


def measure(reference,candidate,bg=None,threshold=12,delta=8):
    a=np.asarray(reference); b=np.asarray(candidate)
    if a.shape!=b.shape: raise ValueError(f'Frame dimensions differ: reference {a.shape}, candidate {b.shape}. Recreate the reference dimensions or explicitly use --width.')
    border=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]],axis=0)
    background=np.asarray(bg if bg is not None else np.median(border,axis=0),dtype=float)
    mask=np.maximum(np.max(np.abs(a.astype(float)-background),axis=2),np.max(np.abs(b.astype(float)-background),axis=2))>threshold
    # Grow one pixel to include antialiased boundaries and small displaced layers.
    mask=np.asarray(Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.MaxFilter(3)))>0
    global_metrics=metrics(a,b,delta=delta); foreground_metrics=metrics(a,b,mask,delta)
    sm,k=ssim_map(a,b); global_metrics['ssim_luma']=float(sm.mean())
    pad=k//2; center_mask=mask[pad:a.shape[0]-pad,pad:a.shape[1]-pad] if pad else mask
    foreground_metrics['ssim_luma']=float(sm[center_mask].mean()) if center_mask.any() else None
    return {'global':global_metrics,'foreground_union':foreground_metrics,
            'background_rgb':background.tolist(),'foreground_percent':float(mask.mean()*100)},a,b,mask


def preview_triptych(a,b,mask,output):
    ref=Image.fromarray(a); can=Image.fromarray(b)
    diff=np.clip(np.abs(a.astype(float)-b.astype(float))*4,0,255).astype('uint8')
    dif=Image.fromarray(diff)
    thumbs=[]
    for im in (ref,can,dif):
        im.thumbnail((480,360)); thumbs.append(im)
    w=max(im.width for im in thumbs); h=max(im.height for im in thumbs)
    sheet=Image.new('RGB',(w*3,h),(32,32,32))
    for i,im in enumerate(thumbs): sheet.paste(im,(i*w,0))
    sheet.save(output)


def aggregate(frames,key):
    rows=[x['metrics'][key] for x in frames]; pixels=sum(x['pixels'] for x in rows)
    def weighted(field):
        valid=[r for r in rows if r.get(field) is not None and r['pixels']]
        return sum(r[field]*r['pixels'] for r in valid)/sum(r['pixels'] for r in valid) if valid else None
    rmse=math.sqrt(sum((r['rmse'] or 0)**2*r['pixels'] for r in rows)/pixels) if pixels else None
    return {'pixels_compared':pixels,'mae':weighted('mae'),'rmse':rmse,
            'psnr_db':10*math.log10(255*255/(rmse*rmse)) if rmse else None,
            'psnr_infinite':rmse==0,'changed_pixel_percent':weighted('changed_pixel_percent'),
            'mean_ssim_luma':weighted('ssim_luma')}


def write_html(report,path):
    sections=[]
    for f in report['frames']:
        m=f['metrics']; sections.append(f'''<article><h2>{html.escape(f['segment'])}: source {f['reference_time']:.4f}s → render {f['candidate_time']:.4f}s</h2>
        <p>Global MAE {m['global']['mae']:.3f} · SSIM {m['global']['ssim_luma']:.5f} · changed pixels {m['global']['changed_pixel_percent']:.2f}%<br>
        Foreground MAE {str(round(m['foreground_union']['mae'],3)) if m['foreground_union']['mae'] is not None else 'n/a'} · foreground coverage {m['foreground_percent']:.2f}%</p>
        <img loading="lazy" src="{f['preview']}" alt="Reference, recreation, amplified absolute difference"></article>''')
    text=f'''<!doctype html><html><meta charset="utf-8"><title>Recreation comparison</title><style>
    body{{background:#161616;color:#eee;font:15px system-ui;max-width:1500px;margin:32px auto;padding:0 24px}}h1{{font-size:28px}}h2{{font-size:17px}}p{{line-height:1.6}}article{{border-top:1px solid #444;padding:20px 0}}img{{width:100%;height:auto}}pre{{white-space:pre-wrap}}a{{color:#91caff}}</style>
    <h1>Reference / recreation / difference ×4</h1><p>{html.escape(report['limitations'])}</p><p><a href="report.json">Full JSON report</a> · <a href="metrics.csv">Per-frame CSV</a></p>
    <pre>{html.escape(json.dumps(report['summary'],indent=2))}</pre>{''.join(sections)}</html>'''
    path.write_text(text)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference'); p.add_argument('candidate'); p.add_argument('--out',required=True)
    p.add_argument('--reference-start',type=float,default=0); p.add_argument('--candidate-start',type=float,default=0)
    p.add_argument('--duration',type=float); p.add_argument('--fps',type=float,default=1,help='Sample rate, not export fps')
    p.add_argument('--all-frames',action='store_true'); p.add_argument('--times',help='Comma-separated offsets in each segment')
    p.add_argument('--batch-native',action='store_true',help='Decode native-index samples once per video instead of repeatedly seeking')
    p.add_argument('--segments',help='JSON path: list of {name,reference_start,candidate_start,duration}')
    p.add_argument('--width',type=int,help='Explicit diagnostic downscale. Omit for native-resolution comparison.')
    p.add_argument('--background',help='Fixed foreground background RGB, e.g. 255,255,255')
    p.add_argument('--foreground-threshold',type=float,default=12); p.add_argument('--changed-threshold',type=float,default=8)
    args=p.parse_args(); output=Path(args.out); (output/'frames').mkdir(parents=True,exist_ok=True)
    ref=probe(args.reference); can=probe(args.candidate)
    if args.width is None and (ref['width'],ref['height'])!=(can['width'],can['height']):
        p.error('Native frame sizes differ. Correct the recreation or explicitly choose --width for diagnostic scaling.')
    bg=[int(x) for x in args.background.split(',')] if args.background else None
    if bg is not None and (len(bg)!=3 or any(x<0 or x>255 for x in bg)): p.error('--background requires three RGB integers from 0 to 255')
    segments=json.loads(Path(args.segments).read_text()) if args.segments else [{'name':'comparison','reference_start':args.reference_start,'candidate_start':args.candidate_start,'duration':args.duration if args.duration is not None else min(ref['duration']-args.reference_start,can['duration']-args.candidate_start)}]
    rate=ref['fps'] if args.all_frames else args.fps
    if rate<=0: p.error('Sample fps must be positive')
    requests=[]
    for segment in segments:
        dur=segment['duration']; rs=segment.get('reference_start',0); cs=segment.get('candidate_start',0)
        if dur<=0 or rs<0 or cs<0 or rs+dur>ref['duration']+.05 or cs+dur>can['duration']+.05:
            p.error(f'Invalid or out-of-bounds segment: {segment}')
        offsets=[float(x) for x in args.times.split(',')] if args.times else list(np.arange(0,dur-1e-8,1/rate))
        for offset in offsets:
            if not 0<=offset<dur: p.error(f'Offset {offset} outside segment {segment}')
            rt=rs+offset; ct=cs+offset
            requests.append((segment,offset,rt,ct))
    frames=[]
    with tempfile.TemporaryDirectory(prefix='native-comparison-') as temporary:
        reference_cache=candidate_cache=None
        if args.batch_native:
            reference_cache=batch_native_frames(args.reference,[q[2] for q in requests],ref,args.width,Path(temporary)/'reference')
            candidate_cache=batch_native_frames(args.candidate,[q[3] for q in requests],can,args.width,Path(temporary)/'candidate')
        for segment,offset,rt,ct in requests:
            ri=Image.open(reference_cache[native_frame_index(rt,ref)]).convert('RGB') if reference_cache is not None else get_frame(args.reference,rt,args.width)
            ci=Image.open(candidate_cache[native_frame_index(ct,can)]).convert('RGB') if candidate_cache is not None else get_frame(args.candidate,ct,args.width)
            result,a,b,mask=measure(ri,ci,bg,args.foreground_threshold,args.changed_threshold)
            preview=f'frames/{len(frames):05d}.jpg'; preview_triptych(a,b,mask,output/preview)
            frames.append({'segment':segment.get('name','comparison'),'offset':offset,'reference_time':rt,'candidate_time':ct,
                'reference_frame':native_frame_index(rt,ref) if reference_cache is not None else None,
                'candidate_frame':native_frame_index(ct,can) if candidate_cache is not None else None,
                'metrics':result,'preview':preview})
            print(f"{len(frames):04d} source={rt:.4f} render={ct:.4f} MAE={result['global']['mae']:.4f} foreground={result['foreground_union']['mae']}",flush=True)
    summary={'frames_sampled':len(frames),'sample_fps':rate,'all_reference_frames_requested':args.all_frames,
             'global':aggregate(frames,'global'),'foreground_union':aggregate(frames,'foreground_union'),
             'sampled_frames_pixel_identical':all(f['metrics']['global']['rmse']==0 for f in frames)}
    report={'version':1,'reference':ref,'candidate':can,'segments':segments,'settings':vars(args),'summary':summary,
            'limitations':'Metrics cover selected sampled frames and mapped graphic excerpts only. They do not certify whole-video identity, audio, editable layers, or perceptual perfection. Foreground uses the union of both images differing from a reported border-median background; inspect that mask assumption for complex scenes. SSIM is luma, valid uniform 11×11 windows (population variance). Infinite PSNR is represented by null plus psnr_infinite=true. Difference previews amplify absolute channel differences ×4.',
            'frames':frames}
    (output/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    with (output/'metrics.csv').open('w',newline='') as file:
        writer=csv.writer(file); writer.writerow(['segment','reference_time','candidate_time','global_mae','global_rmse','global_psnr_db','global_ssim','changed_pixels_percent','foreground_mae','foreground_ssim','foreground_percent'])
        for f in frames:
            g=f['metrics']['global']; fg=f['metrics']['foreground_union']; writer.writerow([f['segment'],f['reference_time'],f['candidate_time'],g['mae'],g['rmse'],g['psnr_db'],g['ssim_luma'],g['changed_pixel_percent'],fg['mae'],fg['ssim_luma'],f['metrics']['foreground_percent']])
    write_html(report,output/'index.html'); print(json.dumps(summary,indent=2))

if __name__=='__main__':
    try: main()
    except (RuntimeError,ValueError) as error:
        print(f'Comparison failed: {error}',file=sys.stderr); sys.exit(1)
