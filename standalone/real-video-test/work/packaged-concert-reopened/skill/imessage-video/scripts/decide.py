#!/usr/bin/env python3
"""Turn the user's request and identified inputs into the next production decisions."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
JOBS = ("recreate", "learn", "direct", "edit")

# Conversational hints for the command-line entry. The calling agent can pass its
# semantic interpretation explicitly, including for requests in other languages.
REVISION = re.compile(r"\b(?:edit|revise|replace|swap|substitute|rewrite|reword|update|shorten|retime)\b|\bchange\b.{0,100}\b(?:to|into|the|this|that|copy|text|wording|shot|video|motion)\b|\binstead of\b|\bkeep\b.{0,90}\b(?:but|except)\b|\bmake (?:the|this|that)\b.{0,45}\b(?:faster|slower|shorter|longer)\b", re.I)
DIRECT = re.compile(r"\b(?:make|create|build|direct|produce|design|shoot)\b.{0,70}\b(?:film|video|clip|animation|commercial|ad)\b|\b(?:new|original|another) (?:\w+ ){0,2}(?:film|video|clip)\b|\b(?:as|for) inspiration\b|\buse\b.{0,65}\b(?:in|for) (?:my|a new|another)\b", re.I)
LEARN = re.compile(r"\b(?:learn|memorize|catalog(?:ue)?|extract|register|study)\b|\b(?:save|add|store)\b.{0,70}\b(?:motion|movement|animation|swipe|slide|transition|library|recipe|effect)\b", re.I)
RECREATE = re.compile(r"\b(?:recreat(?:e|ion)|rebuild|reconstruct|remake|replicate|reproduce|copy|duplicate|match)\b|\b1\s*(?:to|:|[-])\s*1\b|\bone[ -](?:to|on)[ -]one\b", re.I)
MOTION_SCOPE = re.compile(r"\b(?:motion|movement|swipe|slide|gesture|tapback|toggle|switch|bounce|pan|zoom|press|transition|carousel|reveal|animation|effect|seconds?|frames?)\b", re.I)
FILM_SCOPE = re.compile(r"\b(?:film|video|whole|entire|full|sequence)\b", re.I)

def interpret(request, explicit=None, scope=None, has_project=False):
    text = ' '.join(request.split())
    direct_by_reference = re.search(r'\b(?:in|for) (?:a |my |an? )?(?:different|new|another|own) (?:\w+ ){0,2}(?:film|video|clip)\b|\b(?:want|need) (?:an? |my )?(?:imessage |motion graphic )?(?:film|video) about\b',text,re.I)
    if explicit:
        intent = explicit
    elif REVISION.search(text) or (has_project and re.search(r'\b(?:make it|switch|retitle|trim|cut)\b', text, re.I)):
        intent = 'edit'
    elif direct_by_reference and re.search(r'\b(?:save|learn|keep|store|catalog) (?:it|that|this|the motion)\b', text, re.I) and not re.search(r'\b(?:make|direct|create|build|produce)\b', text, re.I):
        intent = 'learn'
    elif (DIRECT.search(text) or direct_by_reference) and not re.search(r'\b(?:identical|exact (?:copy|replica)|frame[- ]for[- ]frame)\b',text,re.I):
        intent = 'direct'
    elif RECREATE.search(text) and (not LEARN.search(text) or FILM_SCOPE.search(text)):
        intent = 'recreate'
    elif LEARN.search(text):
        intent = 'learn'
    elif RECREATE.search(text):
        intent = 'recreate'
    else:
        intent = 'clarify'
    if scope is None:
        if intent == 'learn':
            scope = ('motion' if MOTION_SCOPE.search(text) and not re.search(r'\b(?:all|every|motions|moves|movements)\b', text, re.I)
                     else 'source-motions')
        elif intent == 'edit':
            scope = 'changes'
        elif intent == 'recreate' and MOTION_SCOPE.search(text) and (
            not FILM_SCOPE.search(text) or re.search(r'\b(?:recreate|copy|rebuild|match) (?:just |only )?(?:(?:that|this|the|a) )?(?:\w+ ){0,2}(?:swipe|slide|gesture|motion|transition|pan|zoom|press)\b', text, re.I)
        ):
            scope = 'motion'
        else:
            scope = 'film'
    return intent, scope


def library_root(override=None):
    return Path(override or os.environ.get('IMESSAGE_VIDEO_MOTION_LIBRARY') or ROOT/'assets'/'library').expanduser().resolve()


def catalog_coverage(identified):
    from recipes import inventory, info
    by_reference = set()
    for match in identified['matches']:
        source = match.get('source') or {}
        by_reference.update(p for p in (source.get('repository_path'), source.get('url'), source.get('origin')) if p)
    candidates = []
    for row in inventory().values():
        source = row.get('source') or {}
        if source.get('ref') not in by_reference:
            continue
        local=info(row['id'])
        candidates.append({'id':row['id'],'title':row['title'],'source':source,'preview':local['preview'],
                           'implementation':local['implementation']})
    return candidates


def review_source(role, identified):
    status = identified['status']
    if status == 'new':
        steps = ['segment_source', 'observe_moving_and_fixed_layers', 'find_or_author_each_motion',
                 'replay_from_library', 'compare_consecutive_frames', 'record_verified_coverage']
    elif status == 'candidate':
        steps = ['align_candidate_to_source', 'compare_consecutive_frames_and_audio', 'reuse_matching_coverage',
                 'learn_and_replay_uncovered_motions']
    else:
        steps = ['inspect_registered_coverage', 'reuse_matching_coverage', 'learn_and_replay_uncovered_motions']
    return dict(role=role, identity=identified, documented_motions=catalog_coverage(identified), steps=steps)


def lookup(request, library, limit=3):
    from recipes import suggest, info
    import learn
    seed = suggest(request, limit=limit)
    learned = learn.search(library, request)
    # A registered entry is discoverable by its literal ID, including IDs that
    # share descriptive words with a seed. Do not silently pick a fuzzy tie.
    exact = re.sub(r"[^a-z0-9]+", "-", request.casefold()).strip("-")
    direct = next((x for x in learned if x['id'] == exact), None)
    if direct:
        return {'query': request, 'decision': 'inspect_learned_preview', 'learned': [learn.show(library, exact)], 'seed': []}
    try:
        record = info(exact)
    except (ValueError, KeyError, LookupError):
        record = None
    if record:
        return {'query': request, 'decision': 'inspect_seed_preview', 'learned': [], 'seed': [record]}
    has_seed = bool(seed.get('matches')) and seed.get('action') != 'missing'
    return {'query': request, 'decision': 'inspect_candidates' if learned or has_seed else 'author_motion',
            'seed_decision':seed.get('action'), 'seed_reason':seed.get('reason'),
            'learned': learned[:limit], 'seed': seed['candidates'] if has_seed else []}


def decision(request, videos=(), donors=(), library=None, intent=None, scope=None, project=None, motion=None, brief_ready=False, workdir=None, rea_bin=None):
    from sources import identify
    library = library_root(library)
    mode, extent = interpret(request, intent, scope, bool(project))
    receipt = dict(request=request, intent=mode, scope=extent, library=str(library))
    if mode == 'clarify':
        return {**receipt, 'next': 'ask_intent',
                'question': 'Would you like a recreation, a saved movement, a new film, or a change to an existing edit?'}
    inputs = []
    cache = {}
    for role, paths in [('reference' if mode != 'edit' else 'edit-target', videos), ('motion-donor', donors)]:
        for path in paths:
            resolved = Path(path).expanduser().resolve(strict=True)
            if resolved not in cache:
                cache[resolved] = identify(resolved, library)
            inputs.append({'path': str(resolved), **review_source(role, cache[resolved])})
    if workdir:
        from intake import prepare
        studies = {}
        for item in inputs:
            identity = item['identity']
            digest = identity['sha256']
            if identity['status'] != 'known':
                if digest not in studies:
                    studies[digest] = prepare(item['path'], identity, workdir, rea_bin)
                item['intake'] = studies[digest]
    if project:
        project = str(Path(project).expanduser().resolve(strict=True))
    receipt.update(sources=inputs, project=project)
    has_target = bool(videos)
    if mode in ('learn', 'recreate') and not has_target:
        receipt.update(next='request_source', question='Which clip or saved source should I use?')
        return receipt
    if mode == 'edit' and not (has_target or project):
        receipt.update(next='request_edit_target', question='Which video or editable shot plan should I change?')
        return receipt
    if mode == 'direct':
        receipt['workflow'] = ['establish_brief', 'search_library_for_each_shot', 'show_shots_with_motion_previews_and_code',
                               'review_direction_with_user', 'choose_one_renderer', 'prove_hardest_shot', 'render_approved_cut']
        if not brief_ready:
            receipt['next'] = 'clarify_missing_brief' if not has_target else 'work_out_reference_role_and_brief'
            if not has_target:
                receipt['question'] = ('Do you have a reference, or should I start from the motion library? '
                                       'What should the viewer understand from the main action?')
            receipt['guidance'] = ('Use known answers first. Ask only about a missing story decision. '
                                   'With a vague brief and no reference, offer the choice to supply one once; '
                                   'an empty answer or no reference proceeds to the director and saved library.')
        else:
            receipt['next'] = 'draft_shots_from_library'
    elif mode == 'edit':
        receipt.update(next='locate_target_shots',
                       workflow=['open_editable_target_or_recover_its_layers', 'identify_changed_copy_and_motion',
                                 'retrieve_selected_donor_motion', 'patch_named_shots', 'render_changed_passage',
                                 'check_changed_and_unchanged_regions', 'deliver_revised_film'])
    elif mode == 'learn':
        receipt.update(next='resolve_motion_coverage',
                       workflow=['isolate_requested_intervals', 'check_existing_recipes', 'author_missing_recipes',
                                 'replay_saved_code_against_reference', 'verify_transfer_with_changed_content',
                                 'return_preview_code_and_usage'])
    else:
        receipt['workflow'] = ['check_exact_requested_deliverable', 'reuse_existing_verified_result_when_available',
                               'learn_and_verify_missing_motions', 'choose_one_renderer', 'recreate_from_saved_recipes',
                               'compare_every_frame_and_audio', 'deliver_editable_result']
        statuses = [item['identity']['status'] for item in inputs if item['role']=='reference']
        if 'new' in statuses:
            receipt['next'] = 'learn_before_recreating'
        elif 'candidate' in statuses:
            receipt['next'] = 'check_visual_match'
        elif extent == 'motion':
            receipt['next'] = 'reuse_existing_motion_or_measure_missing_interval'
        else:
            covered = [m['coverage'] for item in inputs if item['role']=='reference' for m in item['identity']['matches']]
            if covered and all(c=='verified-local-reconstruction' for c in covered):
                receipt['next'] = 'return_verified_editable_project_and_master'
            elif covered and all(c in ('archived-reconstruction','verified-local-reconstruction') for c in covered):
                receipt['next'] = 'open_archived_project_and_master'
            else:
                receipt['next'] = 'reuse_verified_parts_and_build_missing_coverage'
    if motion:
        choice = lookup(motion, library)
        receipt['motion_choices'] = choice
        if mode in ('learn', 'recreate') and extent == 'motion' and choice['decision'] in ('inspect_learned_preview','inspect_seed_preview'):
            selected = (choice['learned'] or choice['seed'])[0]['id']
            for item in inputs:
                evidence = item['identity']
                if evidence['status'] == 'known' and any(selected in m['recipe_ids'] for m in evidence['matches']):
                    receipt['next'] = 'return_verified_motion_and_code'
                    break
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('request')
    ap.add_argument('--video', action='append', default=[], help='Reference or video to edit; repeat as needed.')
    ap.add_argument('--donor', action='append', default=[], help='Separate source of replacement movement.')
    ap.add_argument('--project', help='Existing editable scene or shot plan.')
    ap.add_argument('--library')
    ap.add_argument('--intent', choices=JOBS, help='Intent resolved by the calling agent or explicit user choice.')
    ap.add_argument('--scope', choices=('film','motion','source-motions','changes'))
    ap.add_argument('--workdir', help='Prepare source frames automatically for each unfamiliar input and reuse the same study on retries.')
    ap.add_argument('--rea-bin', help='Optional installed REA executable for local shot breakdown during intake.')
    ap.add_argument('--motion', help='Shot-level goal, or a library recipe ID, for preview and code lookup.')
    ap.add_argument('--brief-ready', action='store_true', help='The user supplied enough to propose a story.')
    args = ap.parse_args()
    try:
        result = decision(args.request, args.video, args.donor, args.library, args.intent, args.scope, args.project, args.motion, args.brief_ready, args.workdir, args.rea_bin)
        print(json.dumps(result, indent=2, default=str))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        ap.exit(2, f'{exc}\n')

if __name__ == '__main__':
    main()
