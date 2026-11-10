#!/usr/bin/env python3
"""Build the offline viewer from the archived v3 viewer without truncating source."""
from pathlib import Path
import hashlib, json, re, zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skill/imessage-motion-recreation'
source = ROOT / 'archives/imessage-motion-complete-skill-v3.zip'
with zipfile.ZipFile(source) as archive:
    html = archive.read('imessage-motion-recreation/library/index.html').decode()
match = re.search(r'<script[^>]+id="library-data"[^>]*>(.*?)</script>', html, re.S)
data = json.loads(match[1])
manifest = json.loads((SKILL / 'library/manifest.json').read_text())
examples = {x['id']: x for x in manifest['examples']}
data.pop('publicBase', None)
data.pop('driveFolder', None)
for film in data['films']:
    example = examples[film['id']]
    film['projectRoot'] = '../projects/' + example['complete_project_archive'] + '/imessage-recreations'
    film['originalPath'] = example['original_reference']['project_path']
    film['analysisPath'] = example['source_frame_analysis']
    for study in film['studies']:
        study['url'] = '../skill/imessage-motion-recreation/director/atlas/' + study['url'].rsplit('/', 1)[-1]
for item in data['files']:
    raw = (SKILL / item['skillPath']).read_bytes()
    assert len(raw) == item['bytes']
    assert raw.decode() == item['source']
    assert hashlib.sha256(raw).hexdigest() == item['sha256']

# Rewrite the compact viewer's navigation and prose for an already materialized
# local library; none of these anchors initiate external requests.
html = html.replace('href="../SKILL.md"', 'href="../skill/imessage-motion-recreation/SKILL.md"')
html = html.replace('href="../director/index.html"', 'href="../skill/imessage-motion-recreation/director/index.html"')
html = html.replace('href="https://drive.google.com/drive/folders/1RnlqjEO4KywzL7pnCPpz7IX5eYMIVzsO" target="_blank" rel="noopener noreferrer">Private Drive ↗', 'href="../">Local library root ↗')
html = html.replace('href="https://message-motion-studio.orchidhq.chatgpt.site/sound.html" target="_blank" rel="noopener noreferrer">New UI-audio studies are separate ↗', 'href="../resources/complete-ui-audio-source-v1/">Local UI-audio source folder ↗')
html = html.replace('href="https://message-motion-studio.orchidhq.chatgpt.site/director/index.html" target="_blank" rel="noopener noreferrer">Public director &amp; full atlas ↗', 'href="../skill/imessage-motion-recreation/director/index.html">Local director &amp; full atlas ↗')
html = html.replace('href="manifest.json"', 'href="../skill/imessage-motion-recreation/library/manifest.json"')
html = html.replace('href="README.md"', 'href="../reports/OFFLINE-VIEWER.md"')
html = html.replace('href="RESEARCH-FIRST.md"', 'href="../skill/imessage-motion-recreation/library/RESEARCH-FIRST.md"')
html = html.replace('href="materialize.py"', 'href="../skill/imessage-motion-recreation/library/materialize.py"')
html = html.replace('private · offline code', 'local · offline files')
html = html.replace('<title>The film &amp; the actual code — private motion library</title>', '<title>The film &amp; the actual code — local offline library</title>')
html = html.replace('Private offline code library: six completed iMessage motion studies, five genuine renderers, full source files and verified project-pack pointers.', 'Local offline library: six completed iMessage examples, five genuine renderers, full source, original videos, measured analysis and local assets.')
html = html.replace('Watch a finished study. Open its real renderer. Retrieve the complete scene and assets when you are ready to build.', 'Watch the local finished film and its original. Read the complete renderer. Open the full measured scene, assets and analysis from the same folder.')
html = html.replace('This HTML contains the complete selected renderer files and its catalogue data. Public video previews need a connection; the private project packs also contain the finished movies for offline viewing. No scene megafiles, private font bytes, external JavaScript, or account credentials are embedded here.', 'This viewer reads the restored files beside it. Videos, original references, visual atlases, code and analysis links are local. It loads no external JavaScript, web fonts, analytics or remote video. Keep the complete folder structure when moving this library. Rendering still needs the documented software dependencies.')
html = html.replace('Open the private Drive folder for complete projects, or the public film gallery for video links.', 'Open the projects folder for complete scenes and finished videos, or read the local manifest for file locations.')
html = html.replace('Retrieve one complete example rather than trying to reconstruct its scene from a preview. The full project and original authored history stay in the private library.', 'The six complete projects are already restored. Each contains its full accepted scene, local assets, actual renderer implementations, results and retained authoring history.')
html = html.replace('Archive identity and integrity', 'Verified backup archive identity')
html = html.replace('<div class="actions"><a class="pill dark" href="https://drive.google.com/drive/folders/1RnlqjEO4KywzL7pnCPpz7IX5eYMIVzsO" target="_blank" rel="noopener noreferrer">Open private Drive ↗</a><a class="pill" href="../skill/imessage-motion-recreation/library/manifest.json">Archive registry ↗</a></div>', '<code id="project-root"></code><div class="actions"><a class="pill dark" id="project-readme">Project README ↗</a><a class="pill" id="scene-file">Full scene JSON ↗</a><a class="pill" id="analysis-file">Measured analysis ↗</a><a class="pill" href="../skill/imessage-motion-recreation/library/manifest.json">Backup archive registry ↗</a></div>')
html = html.replace('Access uses the authorized Drive account. The registry contains observed file IDs, verified part hashes and byte counts. It is not a public asset endpoint; this viewer does not alter sharing or include signed download links.', 'The project and its videos open from local paths. The backup registry records the archived Drive copies and hashes; using this viewer does not require signing in or fetching those backups.')
html = html.replace('<h3>Retrieve, then render</h3><ol class="steps"><li>Open <a href="../skill/imessage-motion-recreation/library/manifest.json">manifest.json</a> and locate this example’s archive. Use the authorized Drive tools to download its observed parts.</li><li>Verify and assemble with <a href="../skill/imessage-motion-recreation/library/materialize.py">library/materialize.py</a>. It checks parts, archive and internal checksums; use an isolated output directory.</li><li>Read <code>README-COMPLETE-EXAMPLE.md</code> in the extracted project, install its pinned dependencies and assets, then use the actual example runner.</li></ol>', '<h3>Open locally, then render</h3><ol class="steps"><li>Use the selected project’s README, scene and analysis links above. All six projects are already extracted.</li><li>Read its <code>README-COMPLETE-EXAMPLE.md</code> and inspect the full scene and declared assets. The archive and checksum receipts remain available as backup evidence.</li><li>With the pinned dependencies installed locally, run the project’s actual example runner. New company research may require the internet; viewing these retained resources does not.</li></ol>')
html = html.replace('Read the complete retrieval instructions ↗', 'Read the local viewer notes ↗')
html = html.replace('Complete example:</strong> full accepted scene, assets, adapters, results and verification in the private pack.', 'Complete example:</strong> full accepted scene, assets, adapters, results and verification in its local project folder.')
html = html.replace('Native controls and static validation. No interactive browser QA is claimed.', 'Native controls; local path/source validation. No interactive browser playback pass is claimed.')
html = html.replace('Private code and project library · no external JavaScript or analytics.', 'Local code and project library · no automatic internet requests.')
html = html.replace('<p id="video-status"', '<details style="margin-top:20px"><summary>Compare with the local original reference</summary><div class="stage" style="margin-top:12px"><video id="reference-video" controls playsinline preload="none" aria-label="Original supplied reference"></video></div><p class="small"><a id="open-original" target="_blank" rel="noopener noreferrer">Open original MP4 ↗</a></p></details><p id="video-status"')
html = html.replace("const url=DATA.publicBase+'/deliverables/'+f.id+'/'+m.id+'.mp4';", "const url=f.projectRoot+'/deliverables/'+f.id+'/'+m.id+'.mp4';")
html = html.replace('Public preview needs a connection. Press play, or open the finished movie from the private pack.', 'Local movie selected. Press play, or use Open / save MP4 in your local player.')
html = html.replace('This public preview could not play here. Use Open / save MP4, or open the finished movie in the private example pack.', 'This local movie could not play here. Check that the complete projects folder is beside this catalog; use Open / save MP4 in your local player. Browser codec or local-file restrictions may also apply.')
html = html.replace("$('render-command').textContent='python tools/render_example.py", "$('render-command').textContent='cd '+f.projectRoot+'\\npython tools/render_example.py")
needle = "const paths=$('project-paths');"
insert = "$('project-root').textContent=f.projectRoot;$('project-readme').href=f.projectRoot+'/README-COMPLETE-EXAMPLE.md';$('scene-file').href=f.projectRoot+'/'+f.packScene;$('analysis-file').href=f.projectRoot+'/'+f.analysisPath;const original=f.projectRoot+'/'+f.originalPath;$('open-original').href=original;$('reference-video').pause();$('reference-video').src=original;$('reference-video').load();\n "
assert needle in html
html = html.replace(needle, insert + needle)
html = html.replace("window.addEventListener('pagehide',()=>video.pause());", "window.addEventListener('pagehide',()=>{video.pause();$('reference-video').pause();});")

# Replace only the data script, avoiding accidental changes inside genuine source.
html = re.sub(r'(<script[^>]+id="library-data"[^>]*>).*?(</script>)', lambda m: m[1]+json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')+m[2], html, flags=re.S)
out = Path(__file__).with_name('index.html')
out.write_text(html)
print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'films':len(data['films']),'methods':len(data['methods']),'full_sources':len(data['files']),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
