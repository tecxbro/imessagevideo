from pathlib import Path
import json
root=Path('/workspace/sites/message-motion/dist')
p=root/'sound-lab.js';s=p.read_text()
s=s.replace("const value = mode === 'reference' ? film.reference_gain : film.recreated_gain;", "const value = mode === 'ui' ? film.ui_gain : mode === 'reference' ? film.reference_gain : film.recreated_gain;")
s=s.replace("const poster = assetURL(record.poster, base, [base.origin]);", "const ui = record.ui_video ? assetURL(record.ui_video, base, [MEDIA_ORIGIN]) : null;\n    if (ui && ui.pathname !== `/audio-previews/${record.id}/ui.mp4`) throw new Error('Unexpected UI preview path.');\n    const poster = assetURL(record.poster, base, [base.origin]);")
s=s.replace("reference_audio_video: reference.href, recreated_video: recreated.href", "reference_audio_video: reference.href, recreated_video: recreated.href, ui_video: ui?.href || null")
s=s.replace("if (data.variant !== undefined && data.variant !== 'recreated') return null;", "if (data.variant !== undefined && data.variant !== (pending.variant || 'recreated')) return null;")
s=s.replace("variant: 'recreated'}, MEDIA_ORIGIN", "variant: item.variant}, MEDIA_ORIGIN")
s=s.replace("load(film, signal) {\n    if (this.disposed", "load(film, signal, variant = 'recreated') {\n    if (!['recreated','ui'].includes(variant)) return Promise.reject(new Error('Unexpected sound variant.'));\n    if (this.disposed")
s=s.replace("`sound-lab-recreated-${Date.now()}-${++messageSequence}`", "`sound-lab-${variant}-${Date.now()}-${++messageSequence}`")
s=s.replace("const item = {id, film, signal, resolve, reject, sent: false};", "const item = {id, film, variant, signal, resolve, reject, sent: false};")
s=s.replace("mode: 'recreated', request:", "mode: 'ui', request:")
s=s.replace("load: (request, signal) => request.mode === 'recreated' ? bridge.load(request.film, signal) : fetchMediaBlob(request.url, signal)", "load: (request, signal) => request.mode === 'reference' ? fetchMediaBlob(request.url, signal) : bridge.load(request.film, signal, request.mode === 'ui' ? 'ui' : 'recreated')")
s=s.replace("url: state.mode === 'recreated' ? state.film.recreated_video : state.film.reference_audio_video", "url: state.mode === 'ui' ? state.film.ui_video : state.mode === 'recreated' ? state.film.recreated_video : state.film.reference_audio_video")
s=s.replace("$('levels-note').hidden = !matchedPlaybackLevels", "$('levels-note').hidden = state.mode === 'ui' || !matchedPlaybackLevels")
s=s.replace("$('video-mode-label').textContent = state.mode === 'recreated' ? 'recreated sound / new draft' : 'reference sound / supplied soundtrack';", "$('video-mode-label').textContent = state.mode === 'ui' ? 'UI sounds only / timing study' : state.mode === 'recreated' ? 'UI sounds with quiet music' : 'reference sound / supplied soundtrack';")
s=s.replace("$('sound-provenance').textContent = state.mode === 'recreated' ? 'New instrumental score + original synthesized effects. No reference audio in this mix.' : 'The supplied soundtrack, on the same recreated picture. Switch to Recreated sound to hear the new draft.';", "$('sound-provenance').textContent = state.mode === 'ui' ? 'Downloaded UI and real keyboard sounds, aligned to visible actions. Custom synthesized accents fill the gaps. No reference audio in this mix.' : state.mode === 'recreated' ? 'The same UI effects with a quiet music bed. No reference audio in this mix.' : 'The supplied soundtrack, on the same recreated picture. Switch to UI sounds only to hear the new layer.';")
s=s.replace("$('audio-status-note').textContent = state.mode === 'recreated' ? state.film.audio_status || 'A new draft following the sound direction of the supplied film; not an identical reproduction.' : 'Reference sound is included for comparison. It is not part of the recreated mix.';", "$('audio-status-note').textContent = state.mode === 'ui' ? state.film.ui_status || 'UI-only audition brings the effects forward for timing review.' : state.mode === 'recreated' ? state.film.audio_status || 'A new UI sound study with optional background music.' : 'Reference sound is included for comparison. It is not part of the new UI layer.';")
s=s.replace("state.mode === 'recreated' ? 'recreated sound' : 'reference sound'", "state.mode === 'ui' ? 'UI sounds only' : state.mode === 'recreated' ? 'UI sounds with music' : 'reference sound'")
s=s.replace("item.key === 'sfx' ? 'synthesized effects'", "item.key === 'sfx' ? 'UI effects layer'")
s=s.replace("const [wanted, mode] = host.location.hash.slice(1).split('/'); state.mode = mode === 'reference' ? 'reference' : 'recreated'; const index = state.films.findIndex(film => film.id === wanted); selectFilm(index < 0 ? 0 : index);", "const [wanted, mode] = host.location.hash.slice(1).split('/'); state.mode = ['ui','recreated','reference'].includes(mode) ? mode : 'ui'; const index = state.films.findIndex(film => film.id === wanted); selectFilm(index < 0 ? 4 : index);")
p.write_text(s)
p=root/'sound.html';s=p.read_text().replace('Six motion studies, with newly produced instrumental scores and synthesized effects. Compare the sound, with the same picture.','Message sends, clicks, and typing. UI sound studies aligned to the recreated films, with music optional.')
s=s.replace('Same picture. A new feeling. Six soundtrack drafts to listen to and pull apart.','The small sounds matter. Six UI sound studies to hear without music, then in context.')
s=s.replace('same picture.<br><em>a new feeling.</em>','the little things.<br><em>make it feel real.</em>')
s=s.replace('New instrumental scores. Small, tactile effects.<br>Six fresh takes on the rhythm of a message.','Message sends. Taps. Keystrokes.<br>Placed on the action, with the music out of the way.')
s=s.replace('new scores / familiar motion','UI sounds / familiar motion').replace('drafts to hear, compare &amp; explore','clicks, typing &amp; message sends')
s=s.replace('<span class="sound-draft-badge mono">new soundtrack drafts</span>','<span class="sound-draft-badge mono">UI sound studies</span>')
s=s.replace('two ways to hear it.','hear the small things.')
start=s.index('<div class="sound-mode-switch"');end=s.index('</div>',start)+6
s=s[:start]+'''<div class="sound-mode-switch" role="group" aria-label="Soundtrack">
              <button type="button" class="sound-mode-option" data-sound-mode="ui" aria-pressed="true"><span class="sound-mode-number mono">01</span><span><strong>UI sounds only</strong><small>Message sends, clicks &amp; keystrokes</small></span><span class="sound-mode-check" aria-hidden="true">↗</span></button>
              <button type="button" class="sound-mode-option" data-sound-mode="recreated" aria-pressed="false"><span class="sound-mode-number mono">02</span><span><strong>With music</strong><small>The effects, with a quiet music bed</small></span><span class="sound-mode-check" aria-hidden="true">↗</span></button>
              <button type="button" class="sound-mode-option" data-sound-mode="reference" aria-pressed="false"><span class="sound-mode-number mono">03</span><span><strong>Reference sound</strong><small>The supplied film’s soundtrack</small></span><span class="sound-mode-check" aria-hidden="true">↗</span></button>
            </div>'''+s[end:]
s=s.replace('New instrumental score + original synthesized effects. No reference audio in this mix.','Stock UI and keyboard effects, with custom accents for the gaps. No reference audio in this mix.')
s=s.replace('Switch soundtracks at the same moment. The picture stays the same.','Switch at the same moment. UI-only mode brings the details forward; With music puts them in context.')
s=s.replace('Original synthesized effects.','Downloaded and custom UI effects.')
s=s.replace('The taps, swishes and textures.','The taps, sends and keystrokes.')
s=s.replace('These are newly produced drafts, following the pacing and sound direction of the supplied films. They are not identical reproductions of the reference music.','These studies focus on the small interface sounds. Effects follow visible clicks, message changes and typed input; titles and AI responses do not become keyboard noise. They are not identical reproductions of the reference recordings.')
s=s.replace('The new music was generated with ElevenLabs Music through fal. The effects were synthesized from oscillators and noise, then timed and mixed to the animation.','UI effects come from Kenney’s CC0 Interface Sounds and unicae games’ CC0 keyboard recordings. Custom synthesis fills gaps such as message movement. Music is an optional background layer.')
s=s.replace('<a class="text-link" href="https://message-motion-originals.orchidhq.chatgpt.site/audio-previews/original-sfx-bank.zip">download the 8 original effects ↗</a>', '<a class="text-link" href="https://message-motion-originals.orchidhq.chatgpt.site/audio-previews/ui-sound-kit.zip">download the UI sound kit ↗</a>')
s=s.replace('a little motion. a little feeling.','a little click makes a difference.')
p.write_text(s)
p=Path('/workspace/sites/message-motion-originals/dist/bridge.html');s=p.read_text().replace("!['reference','recreated'].includes(variant)","!['reference','recreated','ui'].includes(variant)")
s=s.replace("const path=variant==='recreated'?'audio-previews/'+film+'/recreated.mp4':'references/'+film+'/source.mp4';", "const path=variant==='ui'?'audio-previews/'+film+'/ui.mp4':variant==='recreated'?'audio-previews/'+film+'/recreated.mp4':'references/'+film+'/source.mp4';")
p.write_text(s)
p=root/'sound-data.json';rows=json.loads(p.read_text())
for row in rows:
 row['ui_video']='https://message-motion-originals.orchidhq.chatgpt.site/audio-previews/'+row['id']+'/ui.mp4';row['ui_gain']=1
 row['ui_status']='UI-only preview brings the details forward for timing review. The downloadable layer keeps its actual mix gain.'
 row['reference_samples_reused']=False;row['library_samples_used']=True
p.write_text(json.dumps(rows,indent=2)+'\n')
