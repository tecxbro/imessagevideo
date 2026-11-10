#!/usr/bin/env python3
"""Read-only scene extraction for UI sound cues in accepted Mini/Poke pictures.

Outputs are small event manifests. No audio analysis, synthesis, rendering, source
mutation, or inferred subframe keystroke sequence is performed here.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'engines'))
from render_pillow import state


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


class Scene:
    def __init__(self, identifier, version, expected_sha, frames):
        self.id = identifier
        self.path = f'outputs/{identifier}/final-v{version}/scene.json'
        assert sha(ROOT / self.path) == expected_sha, self.path
        self.data = read(self.path)
        self.fps = self.data['fps']
        self.frames = frames
        self.by = {}
        self.ancestors = {}

        def visit(node, ancestors):
            assert node['id'] not in self.by
            self.by[node['id']] = node
            self.ancestors[node['id']] = ancestors
            for child in node.get('children', []):
                visit(child, ancestors + [node])

        for node in self.data['layers']:
            visit(node, [])

    def active(self, identifier, frame):
        t = frame / self.fps
        opacity = 1.0
        for node in self.ancestors[identifier] + [self.by[identifier]]:
            if t + 1e-9 < node.get('start', 0) or t >= node.get('end', self.data['duration']) - 1e-9:
                return False
            opacity *= state(node, t)['opacity']
        return opacity > 1e-5

    def first_active(self, identifier):
        return next(n for n in range(self.frames) if self.active(identifier, n))

    def event(self, frame, kind, group, description, evidence, confidence=0.95, **extra):
        return dict(frame=frame, time=round(frame / self.fps, 9), kind=kind,
                    group=group, confidence=confidence, description=description,
                    evidence_layer_or_source=evidence, **extra)


def base(scene, rational):
    return dict(schema='message-motion-ui-cues/1', id=scene.id,
                fps=scene.fps, fps_rational=rational, frames=scene.frames,
                duration=scene.data['duration'], frame_indexing='zero-based',
                scheduling_picture='accepted GSAP render; events.frame is preview_frame',
                canonical_scene=dict(path=scene.path, sha256=sha(ROOT / scene.path)),
                accepted_preview=dict(path=f'outputs/{scene.id}/gsap.mp4',
                                      sha256=sha(ROOT / f'outputs/{scene.id}/gsap.mp4')),
                source_video=dict(path=f'references/{scene.id}/source.mp4',
                                  sha256=sha(ROOT / f'references/{scene.id}/source.mp4')),
                method='Native visual layer states and source-observation helpers only; no waveform/transient analysis.',
                mixing_note='Use quiet key taps for typing; one action per observed frame delta. Do not invent timing for coalesced characters. Card/panel cues are optional and quieter than direct actions.',
                confidence_meaning='Confidence in visible state/timing, not proof of a physical finger/pointer gesture.',
                events=[])


def prefix_delta(before, after):
    assert after.startswith(before), (before, after)
    added = after[len(before):]
    return dict(added_text=added, added_count=len(added), before=before, after=after)


def mini():
    scene = Scene('03-photon-mini', 18,
                  'b720b3a955688bd464e8fbdd2662e5119575ba9f80c8b00e61919caf07c9e646', 1260)
    result = base(scene, '30/1')
    e = result['events']

    def add(frame, kind, group, description, identifier, confidence=.95, **extra):
        assert scene.active(identifier, frame), (identifier, frame)
        e.append(scene.event(frame, kind, group, description,
                             f'{scene.path} #{identifier}', confidence,
                             preview_frame=frame, priority='primary' if kind in ['typing', 'delete', 'tap', 'text_select', 'message_send', 'cart_update'] else 'secondary',
                             **extra))

    add(98, 'message_send', 'email-request', 'Outgoing request begins its independent flight: Draft an email to Alice about our dinner.', 'p03-27',
        text='Draft an email to Alice about our dinner.', timing_basis='First accepted visible bounded outgoing-message state; static bitmap copy is not a typing sequence.')
    add(scene.first_active('p03-35'), 'message_arrival', 'email-working', 'Working on it. incoming bubble begins revealing.', 'p03-35', text='Working on it.')
    add(176, 'message_arrival', 'email-rich-card', 'Mail rich card begins its accepted independent reveal.', 'p03-50',
        timing_basis='Accepted original-card root starts176; static internal copy does not expose per-character typing.')
    add(205, 'tap', 'email-card-open', 'Mail rich card enters its measured pressed state.', 'early-mail-pressed-skin-v13', .97,
        end_frame=213, release_frame=209, action_inference='Visible pressed-card material; no finger or pointer is shown.',
        helper='references/03-photon-mini/refine_early_v13.py: mail-pressed skin205–213')
    add(214, 'panel_open', 'email-editor', 'Mail editor begins the measured visible sheet presentation.', 'p03-77', .9,
        timing_basis='Observed sheet birth214; root212 starts with offstage paper and is not used as the audible action.',
        helper='references/03-photon-mini/refine_early_v13.py: pane trajectory')

    edits = read('references/03-photon-mini/mail-edit-v17-elements.json')
    select_first = min(r['frame'] for r in edits['selections'])
    add(select_first, 'text_select', 'email-availability-edit', 'Blue selection fill and handles first appear on the original availability phrase.',
        f'mail-edit-selection-fill-{select_first}-v17', .99,
        end_frame=max(r['frame'] for r in edits['selections']),
        helper='references/03-photon-mini/mail-edit-v17-elements.json selections',
        timing_basis='Visible selection onset only; no invented double tap/long-press preparation.')
    first = edits['edit_states'][0]
    assert first['start'] == 268 and first['typed_text'] == ''
    old = 'Thursday or Friday evening.'
    add(268, 'delete', 'email-availability-edit', 'Selected availability phrase disappears in one observed edit state.',
        'mail-edit-secondline-268-v17', .99,
        character_or_delta=dict(deleted_text=old, deleted_count=len(old), before=old, after=''),
        helper='references/03-photon-mini/mail-edit-v17-elements.json edit_states[0]',
        timing_basis='One observed selection deletion; not 26 repeated backspace events.')
    prior = ''
    for row in edits['edit_states'][1:]:
        text = row['typed_text']
        if text == prior:
            continue
        delta = prefix_delta(prior, text)
        frame = row['start']
        add(frame, 'typing', 'email-availability-edit', 'Observed visible availability-prefix change.',
            f'mail-edit-secondline-{frame}-v17', .99,
            character_or_delta=delta, source_frame=row['source_frame'],
            helper='references/03-photon-mini/mail-edit-v17-elements.json edit_states',
            timing_basis='Source-observed semantic native glyph outline state; multiple new characters in one frame remain coalesced.')
        prior = text

    # The blue arrow has no measured press/fill change. Anchor the actual send
    # to the accepted dismiss/result transition rather than invent a click.
    e.append(scene.event(354, 'message_send', 'email-send',
                         'Mail editor dismisses toward the sent card; no separate arrow-press state is exposed.',
                         'references/03-photon-mini/refine_early_v13.py: mail-post starts354; accepted early-email-perspective-v13-354 pose; 03-send-dismiss-contact.jpg',
                         .82, preview_frame=354, priority='primary',
                         action_inference='Send outcome inferred from editor dismissal and following Sent. bubble; no physical tap frame is claimed.'))
    add(scene.first_active('p03-81'), 'message_arrival', 'email-sent-status', 'Sent. bubble starts its opacity/scale reveal.', 'p03-81', text='Sent.')
    add(scene.first_active('p03-85'), 'message_arrival', 'email-reply-status', 'Follow-up status bubble starts revealing.', 'p03-85', text="I'll let you know when she replies.")

    add(scene.first_active('entrance-p03-118'), 'message_arrival', 'lunch-alice', 'Alice incoming message first appears.', 'entrance-p03-118', text='Can someone order lunch for us?')
    add(scene.first_active('entrance-p03-124'), 'message_arrival', 'lunch-bob', 'Bob incoming message first appears.', 'entrance-p03-124', text='Vegetarian for me.')
    add(scene.first_active('p03-128'), 'message_send', 'lunch-user', 'Something light. outgoing message starts its independent flight.', 'p03-128', text='Something light.')
    add(scene.first_active('p03-133'), 'message_arrival', 'lunch-agent', 'Agent preference paragraph starts revealing as one message.', 'p03-133',
        text='Taking everyone’s preferences into account, I found a few good options.',
        timing_basis='Whole-message reveal; static paragraph copy is not simulated keyboard typing.')
    add(546, 'message_arrival', 'lunch-rich-card', 'First tiny accepted rich-app artwork appears; independent source-observed affine arrival.',
        'measured-preview-inner-affine-v14', .86,
        helper='references/03-photon-mini/food-preview-native-measure/preview-arrival-affine-measurements.json',
        timing_basis='Tiny optical-fit first state546;547+ image-feature fits are stronger. No exact tap is inferred.')
    add(605, 'tap', 'lunch-card-open', 'Uber Eats card receives measured independent dark pressed material.', 'card-press-material-v16', .99,
        end_frame=614, peak_frame=605, release_frame=609,
        action_inference='Visible card press and release material, not a guessed click from a camera movement.',
        helper='references/03-photon-mini/lunch-material-copy-v16-elements.json press')
    add(618, 'panel_open', 'lunch-menu', 'Rich-app food menu begins presentation.', 'measured-menu-surface-v13', .97)

    cart = read('references/03-photon-mini/cart-v14-components.json')
    # Separate control birth from count ink: count1 is known semantically at668
    # but its first native visible numeral is674. Avoid a synthetic item tap.
    add(668, 'control_appear', 'lunch-cart', 'Measured compact cart control first appears in accepted picture.', 'measured-cart-frame-668-v14', .94,
        timing_basis='Legacy tiny 666–667 source birth is not modeled in accepted picture; cue follows accepted 668 control.')
    previous_count = 0
    visible_counts = []
    for row in cart['root']['children']:
        for child in row.get('children', []):
            if child.get('id', '').endswith('-item-count'):
                count = int(child['semanticText'])
                frame = round(row['start'] * scene.fps)
                if count != previous_count:
                    visible_counts.append((frame, previous_count, count, child['id']))
                    previous_count = count
    assert [(n, c) for n, _, c, _ in visible_counts] == [(674, 1), (682, 2), (711, 3)]
    for frame, previous_count, count, identifier in visible_counts:
        add(frame, 'cart_update', 'lunch-cart', f'Visible cart numeral changes to {count}.', identifier, .99,
            character_or_delta=dict(before=previous_count, after=count, added_count=count-previous_count),
            action_inference='Observed cart confirmation, not an invented earlier plus-button/finger frame.',
            helper='references/03-photon-mini/cart-v14-components.json semantic item-count paths')
    add(730, 'panel_close', 'lunch-menu', 'Food sheet begins its return/closing phase.', 'measured-menu-clip-v13', .9,
        timing_basis='Measured730–734 closing foreground; flying Order! labels are decorative copies, not new sends or typing.')

    result['typing_spans'] = [dict(group='email-availability-edit', first_frame=270,
                                  last_change_frame=302, hold_through_frame=308,
                                  final_text=edits['edit_states'][-1]['typed_text'],
                                  individual_key_times='Unavailable within a frame containing several newly visible characters.')]
    result['exclusions'] = [
        'Intro/title/closing word reveals, all camera cuts, collage panels and flying Order! labels are motion graphics, not keyboard/input events.',
        'Initial draft, fixed Mail prose and incoming paragraphs use static bitmaps/outlines/whole-message reveals; no unseen keystroke sequence is generated.',
        'Typing-indicator dots and the visible keyboard/composer placeholder do not prove typing or individual key presses.',
        'Game/Uber/Google/collage demo cuts after800 are not treated as user taps: no measured physical/control press state is exposed.',
        'Only the measured availability replacement supplies per-prefix typing; caret blink/removal309 creates no extra key sound.',
    ]
    return result


def poke():
    scene = Scene('04-poke', 19,
                  'bf46102ecdc578cdadac244ba85dec7e5ab19fe07b80277a2fdcdb4c2b191df1', 1283)
    result = base(scene, '30000/1001')
    e = result['events']

    def add(frame, kind, group, description, identifier, confidence=.96, **extra):
        assert scene.active(identifier, frame), (identifier, frame)
        e.append(scene.event(frame, kind, group, description, f'{scene.path} #{identifier}', confidence,
                             preview_frame=frame, priority='primary' if kind in ['typing','tap','message_send'] else 'secondary', **extra))

    # Each live line exposes actual text changes. Keep line-wrap separate and
    # do not manufacture a Return/space key between visual lines.
    for identifier in ['v8-preview-line1', 'v8-preview-line2']:
        prior = ''
        last_frame = -1
        for frame in range(scene.frames):
            if not scene.active(identifier, frame):
                continue
            current = state(scene.by[identifier], frame / scene.fps)['text']
            if current == prior:
                continue
            assert current.startswith(prior), (identifier, frame, prior, current)
            add(frame, 'typing', 'poke-preview-request', 'Observed live preview text prefix changes.', identifier, .99,
                character_or_delta=prefix_delta(prior, current), line=1 if identifier.endswith('1') else 2,
                helper='references/04-poke/measurements-v8/preview-typing-fit.json; references/04-poke/v8_intro.py',
                timing_basis='Native live-text keyframe, with ancestor life/opacity gate. Coalesced characters remain on the observed frame; wrapping creates no synthetic key.')
            prior = current
            last_frame = frame
        assert last_frame >= 109

    actions = [
        (142,'message_arrival','sarah-request','Incoming Sarah request first appears.','v19-Sarah-incoming','sarah wants to grab dinner tmrw'),
        (175,'panel_open','calendar-picker','Calendar time-picker sheet begins presentation.','p0100',None),
        (232,'tap','calendar-selection','7:30 PM selected button turns blue.','p0091',None),
        (268,'message_arrival','calendar-confirmation','locked friday incoming confirmation appears.','p0113','locked friday'),
        (280,'message_arrival','dinner-question','Cuisine question arrives.','p0117','what r u in the mood for?'),
        (301,'message_arrival','cuisine-options','Cuisine options rich message appears.','p0132',None),
        (339,'tap','cuisine-selection','Indian option starts its measured press fade.','p0125',None),
        (361,'message_send','cuisine-result','Indian selected-option outgoing card appears.','p0135','Indian'),
        (375,'message_arrival','find-spot-question','Follow-up find-a-spot question appears.','p0146','want me to find a spot?'),
        (413,'message_arrival','location-question','Location question appears.','p0155','where are you rn?'),
        (455,'control_appear','location-suggestion','Current Location keyboard suggestion appears.','v8-currentlocation','Current Location'),
        (513,'message_send','shared-location','Shared Location outgoing message appears.','p0223','Shared Location · Palo Alto, CA'),
        (549,'message_arrival','restaurant-found','First coherent, onstage found-spots message appears.','v17-found-early-ui','found a few solid spots near you'),
        (575,'panel_open','restaurant-picker','Restaurant chooser starts its accepted presentation.','p0255',None),
        (645,'tap','restaurant-selection','Zareen’s selection circle/checkmark first appears in accepted GSAP picture.','p0249',None),
        (664,'message_arrival','restaurant-question','anything catching your eye? new prompt appears as sheet dismisses.','p0259','anything catching your eye?'),
        (687,'message_send','restaurant-result','Selected Zareen’s outgoing result card appears.','p0262','Zareen’s · I’ll take it from here.'),
        (728,'message_arrival','restaurant-map','Maps rich card starts its accepted reveal behind the composer.','p0300',"Zareen's · maps.apple.com"),
        (756,'message_arrival','restaurant-distance','Distance response enters.','p0307','only 0.16 mi away from you'),
        (800,'message_send','voice-reminder','Outgoing 0:04 voice-message bubble appears; no fake keyboard sequence.','p0310','Please remind me about this dinner 1 hour before.'),
        (853,'message_arrival','reminder-confirmation','Reminder confirmation incoming message appears.','p0362','sure, i’ll remind you on time'),
    ]
    for frame, kind, group, description, identifier, text in actions:
        extra = dict(text=text) if text else {}
        if group == 'calendar-selection':
            extra.update(helper='references/04-poke/v8_modals.py; measurements-v8/calendar-fit.json: first blue_area>10000 at232',
                         action_inference='Visible selected-button state; no finger/pointer is shown.')
        if group == 'cuisine-selection':
            extra.update(end_frame=360, peak_frame=347, release_frame=348,
                         helper='references/04-poke/measurements-v8/menu-press-v11.json',
                         action_inference='Measured option ink opacity first falls below 1 at 339, minimum 347, recovery 348–360.')
        if group == 'restaurant-selection':
            extra.update(reference_frame=633, reference_time=round(633/scene.fps,9),
                         discrepancy_frames=12,
                         helper='audio-recreation/ui-cues/04-accepted-restaurant-selection-measurement.json; 04-restaurant-selection-measurement.json',
                         action_inference='Accepted preview selection is 12 frames later than source. Audio follows accepted picture 645, not reference 633.',
                         actual_encoded_preview_verified=True)
        if group == 'restaurant-found':
            extra.update(timing_basis='Root starts547 but y1200 is outside1080px frame at 547–548; measured onstage body starts 549. Reappearance664 is not a second found-message event.')
        if group == 'restaurant-distance':
            extra.update(timing_basis='Root wall-clock25.2s lies between native755 and756; first included native frame is756.')
        add(frame, kind, group, description, identifier, **extra)

    result['typing_spans'] = [dict(group='poke-preview-request', first_frame=109,
                                  last_change_frame=125, final_text='sarah wants to grab dinner tmrw',
                                  individual_key_times='Only observed prefix changes; two/three character additions within one frame have no invented subdivisions.',
                                  line_wrap='Automatic two-line layout. No Return or synthetic inter-line space sound.')]
    result['exclusions'] = [
        'Intro avatars/inbox-name reveals, static on-screen keyboard letters, composer placeholders and location accessory A icon are not keystrokes.',
        'Selected card continuation734–788 is a camera/scroll phase, not a second send.',
        'Found-spots message reappearing 664 after the modal is the same message; only the new question at664 is an arrival cue.',
        'Calendar/restaurant open sheets are presentation cues; no hidden preceding button/finger time is invented.',
        'Voice bubble 800 supplies a send cue, not synthesized speech or waveform-derived key taps.',
        'Marketing feature cards/connect-tool tiles after887 are showcase graphics; no unsupported user click/typing events are assigned.',
    ]
    return result


def main():
    reports = []
    for data in [mini(), poke()]:
        events = sorted(data['events'], key=lambda row: (row['frame'], row['kind'], row['group'], row.get('line',0)))
        assert len({(e['frame'],e['kind'],e['group'],e.get('line',0)) for e in events}) == len(events)
        assert all(0 <= e['frame'] < data['frames'] for e in events)
        assert all(abs(e['time'] - e['frame']/data['fps']) < 1e-8 for e in events)
        data['events'] = events
        data['counts'] = dict(Counter(row['kind'] for row in events))
        data['typing_added_characters'] = sum(row.get('character_or_delta',{}).get('added_count',0) for row in events if row['kind']=='typing')
        data['source_inputs'] = []
        inputs = ['audio-recreation/ui-cues/03-04-extract.py',
                  'audio-recreation/ui-cues/03-04-encoded-action-check.json']
        if data['id'].startswith('03'):
            inputs += ['references/03-photon-mini/mail-edit-v17-elements.json',
                       'references/03-photon-mini/cart-v14-components.json',
                       'references/03-photon-mini/lunch-material-copy-v16-elements.json',
                       'references/03-photon-mini/refine_early_v13.py']
        else:
            inputs += ['references/04-poke/measurements-v8/preview-typing-fit.json',
                       'references/04-poke/measurements-v8/menu-press-v11.json',
                       'references/04-poke/measurements-v8/calendar-fit.json',
                       'audio-recreation/ui-cues/04-accepted-restaurant-selection-measurement.json',
                       'audio-recreation/ui-cues/04-restaurant-selection-measurement.json']
        for path in inputs:
            data['source_inputs'].append(dict(path=path, sha256=sha(ROOT/path)))
        output = OUT/(data['id']+'.events.json')
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
        reports.append(dict(path=str(output.relative_to(ROOT)), events=len(events), counts=data['counts'], typing_added_characters=data['typing_added_characters'], sha256=sha(output)))
    (OUT/'03-04-validation.json').write_text(json.dumps(dict(status='PASS', checks=['Accepted canonical scene SHA pins','No duplicate IDs in either scene','All event evidence-layer ancestor lifetimes and opacity gates active','Typing prefixes monotonic and exact frame changes','No duplicate semantic event tuples','All frame/time conversions exact within1e-8 seconds','Restaurant reference 633 vs accepted 645 independently decoded and retained'],reports=reports),indent=2)+'\n')
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    main()
