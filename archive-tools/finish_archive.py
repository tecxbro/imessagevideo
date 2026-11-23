#!/usr/bin/env python3
"""Add final discovered skill copies, publish navigation, verify the archive."""
from pathlib import Path
import base64
import hashlib
import importlib.util
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('snapshots', HERE / 'publish_snapshots.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT = HERE.parent
BRANCH = s.PREFIX + '/index'


def main():
    primary = json.loads((s.TMP / f'imessage-video-standalone-published-{s.DATE}.json').read_text())
    parent = s.git(ROOT, 'ls-remote', 'origin', 'refs/heads/' + BRANCH).decode().split()[0]
    assert parent == primary['commit']
    inventory = json.loads(s.git(ROOT, 'cat-file', 'blob', parent + ':inventory.json'))
    files = []
    added_roots = []
    omitted = []
    for name in json.loads((s.TMP / f'imessage-video-supplemental-skills-{s.DATE}.json').read_text()):
        root = Path(name).parent
        label = 'standalone/additional-skill-copies/' + root.as_posix().lstrip('/')
        added_roots.append({'label': label, 'path': str(root), 'temporary_sources_only': False})
        for base, ds, fs in os.walk(root, followlinks=False):
            ds[:] = [d for d in ds if d not in s.SKIP and not (Path(base) / d).is_symlink()]
            for name in sorted(fs):
                source = Path(base) / name
                rel = source.relative_to(root).as_posix()
                result, reason = s.inspect_file(source, rel)
                if reason:
                    omitted.append({'source': str(source), 'reason': reason})
                    continue
                data, mode = result
                files.append((label + '/' + rel, data, mode, str(source)))
    existing_sources = {e['source'] for e in inventory['standalone_files']}
    for source in sorted(HERE.glob('*.py')):
        if str(source) not in existing_sources:
            data, mode = s.read_file(source)
            files.append(('archive-tools/' + source.name, data, mode, str(source)))
    new_manifest = []
    for rel, data, mode, source in files:
        new_manifest.append({'path': rel, 'source': source, 'bytes': len(data), 'mode': mode,
                             'sha256': hashlib.sha256(data).hexdigest(),
                             'git_blob': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()})
    old_count = len(inventory['standalone_files'])
    old_roots = len(inventory['standalone_roots'])
    inventory['standalone_files'].extend(new_manifest)
    inventory['standalone_roots'].extend(added_roots)
    inventory['omitted'].extend(omitted)
    new_count = len(inventory['standalone_files'])
    new_roots = len(inventory['standalone_roots'])
    docs_path = ROOT / 'GITHUB-ARCHIVE.md'
    docs = docs_path.read_text()
    docs = docs.replace(f'{old_count:,} files from {old_roots} source locations',
                        f'{new_count:,} files from {new_roots} source locations')
    old_gib = primary['bytes'] / 1024 ** 3
    new_bytes = primary['bytes'] + sum(e['bytes'] for e in new_manifest)
    docs = docs.replace(f'The raw total is {old_gib:.2f} GiB', f'The raw total is {new_bytes / 1024 ** 3:.2f} GiB')
    docs += '\nThe final name-based sweep added 20 older/extracted skill copies under `standalone/additional-skill-copies`, preserving each original directory hierarchy.\n'
    docs_path.write_text(docs)
    assert docs_path.read_text() == docs
    files += [('README.md', docs.encode(), '100644', str(docs_path)),
              ('inventory.json', (json.dumps(inventory, indent=2) + '\n').encode(), '100644', 'generated inventory')]
    commit, tree, manifest = s.make_commit(ROOT, parent, files,
        f'Include remaining extracted/demo skill copies and final inventory, {s.DATE}')
    s.git(ROOT, 'update-ref', 'refs/heads/' + BRANCH, commit)
    s.publish(ROOT, commit, BRANCH)
    print(json.dumps({'index_commit': commit, 'additional_files': len(new_manifest), 'standalone_files': new_count}), flush=True)

    # Add only navigation to the existing upstream main tree. Preserve its code.
    main_parent = s.git(ROOT, 'ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
    fetched = s.git(ROOT, 'rev-parse', 'refs/remotes/origin/main').decode().strip()
    if main_parent != fetched:
        s.git(ROOT, 'fetch', '--filter=blob:none', '--depth=1', '--no-tags', 'origin', 'main:refs/remotes/origin/main')
    readme_json = json.loads(subprocess.check_output(['gh', 'api', 'repos/tecxbro/imessagevideo/readme']))
    original_readme = base64.b64decode(readme_json['content'])
    expected = s.git(ROOT, 'ls-tree', main_parent, 'README.md').decode().split()[2]
    assert readme_json['sha'] == expected
    title, remainder = original_readme.split(b'\n', 1)
    link = b'\n\n[All local iMessage video skills, projects, and archived versions (November 22, 2026)](GITHUB-ARCHIVE.md)\n'
    updated_readme = title + link + remainder
    nav_commit, _, _ = s.make_commit(ROOT, main_parent,
        [('README.md', updated_readme, '100644', 'upstream README plus navigation'),
         ('GITHUB-ARCHIVE.md', docs.encode(), '100644', str(docs_path))],
        'Link the complete local iMessage video version archive')
    changed = s.git(ROOT, 'diff-tree', '--no-commit-id', '--name-only', '-r', main_parent, nav_commit).decode().splitlines()
    assert set(changed) == {'README.md', 'GITHUB-ARCHIVE.md'}, changed
    s.git(ROOT, 'update-ref', 'refs/heads/codex/archive-navigation-' + s.DATE, nav_commit)
    s.publish(ROOT, nav_commit, 'main')

    snapshots = json.loads(s.RESULTS.read_text())
    remote = dict((ref, sha) for sha, ref in (line.split() for line in s.git(ROOT, 'ls-remote', '--heads', 'origin').decode().splitlines()))
    assert len(snapshots) == 25
    assert all(remote.get('refs/heads/' + r['archive_branch']) == r['commit'] for r in snapshots)
    assert remote['refs/heads/' + BRANCH] == commit
    assert remote['refs/heads/main'] == nav_commit
    repo = json.loads(subprocess.check_output(['gh', 'api', 'repos/tecxbro/imessagevideo']))
    assert repo['private'] is True
    current_files = {}
    for record in s.git(ROOT, 'ls-tree', '-rz', commit).split(b'\0'):
        if record:
            meta, name = record.split(b'\t', 1)
            current_files[name.decode()] = meta.split()[2].decode()
    assert len(current_files) == new_count + 2
    assert all(current_files[e['path']] == e['git_blob'] for e in inventory['standalone_files'])
    verification = {'date': s.DATE, 'repository': repo['html_url'], 'private': True,
                    'worktree_snapshots_verified': len(snapshots),
                    'captured_worktree_files': sum(len(r['captured_files']) for r in snapshots),
                    'standalone_files': new_count, 'index_tree_files': len(current_files),
                    'index_commit': commit, 'main_navigation_commit': nav_commit,
                    'main_changed_files': changed, 'standalone_raw_bytes': new_bytes,
                    'source_locations': new_roots, 'omitted_supplemental_files': omitted,
                    'index_url': repo['html_url'] + '/blob/main/GITHUB-ARCHIVE.md'}
    path = ROOT / 'GITHUB-ARCHIVE-VERIFICATION.json'
    path.write_text(json.dumps(verification, indent=2) + '\n')
    assert json.loads(path.read_text()) == verification
    print(json.dumps(verification), flush=True)


if __name__ == '__main__':
    main()
