#!/usr/bin/env python3
"""Archive standalone source, assets and exports; omit regenerable frame grids."""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('snapshots', HERE / 'publish_snapshots.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT = HERE.parent
PLAN = s.TMP / f'imessage-video-standalone-plan-{s.DATE}.json'
RESULT = s.TMP / f'imessage-video-standalone-published-{s.DATE}.json'
BRANCH = s.PREFIX + '/index'
TEXT = {'.py', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx', '.html', '.css', '.sh',
        '.md', '.json', '.csv', '.toml', '.yaml', '.yml', '.lock', '.glsl', '.svg'}


def roots():
    fixed = [
        ('sidehoe-recreation', ROOT / 'sidehoe-recreation', False),
        ('sidehoe-skill-trial', ROOT / 'sidehoe-skill-trial', False),
        ('recreation-evidence', ROOT.parent / 'imessagevideo-recreation-evidence', False),
        ('v3-prompts', ROOT.parent / 'imessagevideo-v3-prompts', False),
        ('real-video-test', Path('/Users/darshan/Documents/Codex/2026-11-21/goal-test-the-imessage-video-skill'), False),
        ('iv-test', Path('/Users/darshan/Documents/video-analysis/iv-test'), False),
        ('recording-skills/pony-demo-creator', Path('/Users/darshan/Documents/PONY/.agents/skills/pony-demo-creator'), False),
        ('recording-skills/pony-demo-deep', Path('/Users/darshan/Documents/PONY/.agents/skills/pony-demo-deep'), False),
        ('recording-skills/pony-demo-instant', Path('/Users/darshan/Documents/PONY/.agents/skills/pony-demo-instant'), False),
        ('recording-skills/pony-record-imessage-demo', Path('/Users/darshan/Documents/PONY/.agents/skills/record-imessage-demo'), False),
        ('recording-skills/chatgpt-record-imessage-demo', ROOT.parent / 'imessagedemo/.agents/skills/record-imessage-demo', False),
        ('recording-skills/documents-record-imessage-demo', Path('/Users/darshan/Documents/imessagedemo/.agents/skills/record-imessage-demo'), False),
    ]
    # Preserve the standalone clean-room skill packages and unique temporary
    # authored sources. Third-party setup checkouts and render output stay out.
    for p in sorted(s.TMP.iterdir()):
        if p.is_dir() and re.match(r'(?:sidehoe[-_]|imv[-_])', p.name):
            if any(x in p.name for x in ['python', 'cache']):
                continue
            fixed.append(('temporary-sources/' + p.name, p, True))
    existing = {str(p) for _, p, _ in fixed}
    for p in sorted(Path('/Users/darshan/Documents/PONY/.agents/skills').iterdir()):
        if p.is_dir() and p.name != 'pony-lookalike-icp' and str(p) not in existing:
            fixed.append(('recording-skills/' + p.name, p, False))
    fixed.append(('recording-skills/global-photon-demo-creator', Path('/Users/darshan/.codex/skills/photon-demo-creator'), False))
    discovery = json.loads((s.TMP / f'imessage-video-discovery-{s.DATE}.json').read_text())
    for name in discovery['skills']:
        p = Path(name).parent
        if name.startswith('/private/tmp/'):
            fixed.append(('temporary-skill-packages/' + p.parts[3] + '/' + p.name, p, False))
    return fixed


def reason(path, rel, source_only):
    why = s.omit(rel)
    if why:
        return why
    p = Path(rel)
    if source_only and p.suffix.lower() not in TEXT:
        return 'temporary render/media output (authored sources retained)'
    if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
        if not any(x in p.parts for x in {'assets', 'plates', 'portraits'}):
            parts = [x.lower() for x in p.parts]
            if any('cache' in x or 'frames' in x or 'comparison' in x or x in {'native', 'crops', 'diff', 'pairs', 'final-pairs'} for x in parts):
                return 'regenerable decoded/comparison images'
            if re.match(r'^(?:frame[-_]?|ref[-_]?|out[-_]?|f|r)?\d{3,}', p.name.lower()):
                return 'decoded frame sequence'
    return None


def make_plan():
    entries, omitted, source_roots = [], [], []
    for label, root, source_only in roots():
        if not root.exists():
            continue
        source_roots.append({'label': label, 'path': str(root), 'temporary_sources_only': source_only})
        for base, ds, fs in os.walk(root, followlinks=False):
            for d in list(ds):
                sub = Path(base) / d
                if d in s.SKIP or d == 'site-packages' or (sub / 'pyvenv.cfg').exists() or (sub / '.git').exists() or sub.is_symlink() or d.startswith('evidence-chrome'):
                    ds.remove(d)
                    omitted.append({'source': str(sub), 'reason': 'nested repository, dependency, browser profile, or symlink directory'})
            for name in sorted(fs):
                source = Path(base) / name
                rel = source.relative_to(root).as_posix()
                why = reason(source, rel, source_only)
                if why:
                    omitted.append({'source': str(source), 'reason': why})
                    continue
                result, why = s.inspect_file(source, rel)
                if why:
                    omitted.append({'source': str(source), 'reason': why})
                    continue
                data, mode = result
                entries.append({'source': str(source), 'path': 'standalone/' + label + '/' + rel,
                                'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'mode': mode})
    for source in sorted(ROOT.glob('archive-tools/*.py')) + [ROOT / 'AGENTS.md', ROOT / 'GIT-INCIDENT-2026-11-18.md']:
        data, mode = s.read_file(source)
        entries.append({'source': str(source), 'path': 'archive-tools/' + source.name if source.suffix == '.py' else 'workspace/' + source.name,
                        'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'mode': mode})
    # Loose temporary Sidehoe scripts can contain unique uncommitted work.
    for source in sorted(s.TMP.glob('sidehoe*.py')):
        result, why = s.inspect_file(source, source.name)
        if why:
            omitted.append({'source': str(source), 'reason': why})
            continue
        data, mode = result
        entries.append({'source': str(source), 'path': 'standalone/temporary-sources/loose/' + source.name,
                        'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'mode': mode})
    plan = {'date': s.DATE, 'branch': BRANCH, 'source_roots': source_roots, 'files': entries, 'omitted': omitted}
    PLAN.write_text(json.dumps(plan, indent=2) + '\n')
    assert len(json.loads(PLAN.read_text())['files']) == len(entries)
    unique = {x['sha256']: x['bytes'] for x in entries}
    reasons = collections.Counter(x['reason'] for x in omitted)
    print(json.dumps({'files': len(entries), 'bytes': sum(x['bytes'] for x in entries),
                      'unique_bytes': sum(unique.values()), 'source_roots': len(source_roots),
                      'omitted_reasons': reasons, 'plan': str(PLAN)}), flush=True)


def publish():
    plan = json.loads(PLAN.read_text())
    if not s.git(ROOT, 'remote').strip():
        s.git(ROOT, 'remote', 'add', 'origin', 'https://github.com/tecxbro/imessagevideo.git')
    with tempfile.TemporaryDirectory(prefix='imv-standalone-index-', dir=s.TMP) as tmp:
        env = {'GIT_INDEX_FILE': str(Path(tmp) / 'index')}
        s.git(ROOT, 'read-tree', '--empty', env=env)
        records, manifest = [], []
        parent = None
        pending_bytes = 0
        seen_blobs = set()
        def flush_batch():
            nonlocal parent, records, pending_bytes
            if not records:
                return
            s.git(ROOT, 'update-index', '-z', '--index-info', data=b''.join(records), env=env)
            tree = s.git(ROOT, 'write-tree', '--missing-ok', env=env).decode().strip()
            args = ['commit-tree', tree] + (['-p', parent] if parent else [])
            parent = s.git(ROOT, *args, data=f'Preserve standalone archive batch ({len(manifest)} files), {s.DATE}\n'.encode()).decode().strip()
            s.git(ROOT, 'update-ref', 'refs/heads/' + BRANCH, parent)
            s.publish(ROOT, parent, BRANCH)
            print(json.dumps({'published_batch_files': len(manifest), 'commit': parent}), flush=True)
            records = []
            pending_bytes = 0
        for i, entry in enumerate(plan['files']):
            data, mode = s.read_file(Path(entry['source']))
            digest = hashlib.sha256(data).hexdigest()
            if digest != entry['sha256']:
                raise RuntimeError('File changed since review: ' + entry['source'])
            oid = s.git(ROOT, 'hash-object', '-w', '--stdin', data=data).decode().strip()
            assert oid == hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            entry['git_blob'] = oid
            manifest.append(entry)
            records.append(f"{mode} {oid}\t{entry['path']}".encode() + b'\0')
            if oid not in seen_blobs:
                pending_bytes += len(data)
                seen_blobs.add(oid)
            if pending_bytes >= 450 * 1024 * 1024:
                flush_batch()
            if i and i % 500 == 0:
                print(json.dumps({'stored_files': i}), flush=True)
        # Inventory is part of the archive itself, with no credentials or raw chats.
        inventory = {'date': s.DATE, 'repository': 'tecxbro/imessagevideo',
                     'worktrees': json.loads(s.RESULTS.read_text()),
                     'standalone_roots': plan['source_roots'], 'standalone_files': manifest,
                     'omitted': plan['omitted'], 'scan_scope': json.loads((s.TMP / f'imessage-video-discovery-{s.DATE}.json').read_text())['roots'],
                     'protected_locations': json.loads((s.TMP / f'imessage-video-discovery-{s.DATE}.json').read_text())['errors']}
        inv = (json.dumps(inventory, indent=2) + '\n').encode()
        docs = (ROOT / 'GITHUB-ARCHIVE.md').read_bytes()
        for rel, data in [('inventory.json', inv), ('README.md', docs)]:
            oid = s.git(ROOT, 'hash-object', '-w', '--stdin', data=data).decode().strip()
            records.append(f'100644 {oid}\t{rel}'.encode() + b'\0')
        s.git(ROOT, 'update-index', '-z', '--index-info', data=b''.join(records), env=env)
        tree = s.git(ROOT, 'write-tree', '--missing-ok', env=env).decode().strip()
        args = ['commit-tree', tree] + (['-p', parent] if parent else [])
        commit = s.git(ROOT, *args, data=f'Archive standalone iMessage video sources and exports from {s.DATE}\n'.encode()).decode().strip()
        actual = {}
        for entry in s.git(ROOT, 'ls-tree', '-rz', commit).split(b'\0'):
            if entry:
                meta, name = entry.split(b'\t', 1)
                actual[name.decode()] = meta.split()[2].decode()
        assert all(actual[x['path']] == x['git_blob'] for x in manifest)
        assert len(actual) == len(manifest) + 2
        s.git(ROOT, 'update-ref', 'refs/heads/' + BRANCH, commit)
        s.publish(ROOT, commit, BRANCH)
        result = {'branch': BRANCH, 'commit': commit, 'tree': tree, 'files': len(actual), 'verified_remote': True,
                  'bytes': sum(x['bytes'] for x in manifest), 'unique_bytes': sum({x['sha256']: x['bytes'] for x in manifest}.values())}
        RESULT.write_text(json.dumps(result, indent=2) + '\n')
        assert json.loads(RESULT.read_text()) == result
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    publish() if '--publish' in sys.argv else make_plan()
