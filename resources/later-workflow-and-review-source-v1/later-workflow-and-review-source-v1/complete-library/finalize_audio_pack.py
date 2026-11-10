from pathlib import Path
import hashlib,json,os,zipfile
ROOT=Path(__file__).resolve().parents[1];manifest=ROOT/'complete-library/packs.json';m=json.loads(manifest.read_text());r=next(v for v in m['archives'] if v['id']=='complete-ui-audio-source-v1');out=Path(r['path']);temp=out.with_suffix('.zip.portable.tmp');prefix='imessage-recreations/';checks={}
with zipfile.ZipFile(out) as src,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n in src.namelist():
  if n.endswith('/PACK-CHECKSUMS.json') or n in {prefix+'audio-recreation/scripts/render_example.py',*[prefix+'tools/'+name for name in ['rebuild_audio.py','mux_ui.py','source_aliases.py']]}:continue
  data=src.read(n)
  if n==prefix+'audio-recreation/README-COMPLETE.md':
   data=b'''# Complete UI audio source and portable rebuild tools

The complete bundle contains original accepted audio, pinned music, configurations,
source snapshots, original CC0 archives/source pages, prepared effects, all6mix reports,
all canonical/source cue sheets,12finished previews and signal/codec audits.

Use an empty sandbox to preserve accepted exports:
python tools/rebuild_audio.py --example05-linq --sandbox /your/empty/work
(Write --example and05-linq as separate arguments.) UI-only is the default;
--with-music uses the pinned music stem +mix-report without AI generation.

After retrieving a complete visual case, tools/mux_ui.py can combine its picture
stream with the UI audio using any of the5accepted methods. It explicitly maps only
video from the picture input and audio from the new UI track; it never copies the
source soundtrack into a new mix. UI-only preview gain is labelled separately.

tools/source_aliases.py optionally recreates legacy output/final-vXX scene paths
from portable scenes/ID for cue re-derivation. Already accepted cue schedules can
render without reading source scenes. The original Site-specific packager source
is retained for history; these portable helpers remove that implicit checkout need.

The original music-only mixer accepts --videos-json audio-recreation/videos.json.
Default full music rebuilding requires its pinned AI MP3/config snapshots, while
UI-with-music uses the accepted music.flac/mix-report directly. Music is optional.
No cookies, signed download-link responses or credentials are bundled.
'''.replace(b'--example05-linq',b'--example 05-linq').replace(b'(Write --example and05-linq as separate arguments.) ',b'')
  z.writestr(n,data);checks[n.removeprefix(prefix)]=hashlib.sha256(data).hexdigest()
 for name in ['rebuild_audio.py','mux_ui.py','source_aliases.py']:
  data=(ROOT/'complete-library'/name).read_bytes();rel='tools/'+name;z.writestr(prefix+rel,data);checks[rel]=hashlib.sha256(data).hexdigest()
 z.writestr(prefix+'PACK-CHECKSUMS.json',json.dumps(checks,indent=2)+'\n')
os.replace(temp,out)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==len(checks)+1
 for n,h in checks.items():assert hashlib.sha256(z.read(prefix+n)).hexdigest()==h
r.update(bytes=out.stat().st_size,sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),files=len(checks)+1,portable_helpers=['tools/rebuild_audio.py','tools/mux_ui.py','tools/source_aliases.py']);manifest.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(r))
