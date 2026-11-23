#!/usr/bin/env python3
"""Append discovered packaged skill copies without excluding their cache parent."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('snapshots', HERE / 'publish_snapshots.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT = HERE.parent


def main():
    report = ROOT / 'GITHUB-ARCHIVE-VERIFICATION.json'
    v = json.loads(report.read_text())
    parent = v['index_commit']
    branch = s.PREFIX + '/index'
    assert s.git(ROOT, 'ls-remote', 'origin', 'refs/heads/' + branch).decode().split()[0] == parent
    inv = json.loads(s.git(ROOT, 'cat-file', 'blob', parent + ':inventory.json'))
    old_count = len(inv['standalone_files'])
    old_roots = len(inv['standalone_roots'])
    files = []
    for name in json.loads((s.TMP / f'imessage-video-final-missing-skills-{s.DATE}.json').read_text()):
        root = Path(name).parent
        label = 'standalone/cached-skill-packages/' + root.as_posix().lstrip('/')
        inv['standalone_roots'].append({'label': label, 'path': str(root), 'temporary_sources_only': False})
        for base, ds, fs in os.walk(root):
            ds[:] = [d for d in ds if d not in s.SKIP and not (Path(base) / d).is_symlink()]
            for name in sorted(fs):
                source = Path(base) / name
                rel = source.relative_to(root).as_posix()
                result, reason = s.inspect_file(source, rel)
                if reason:
                    inv['omitted'].append({'source': str(source), 'reason': reason})
                    continue
                data, mode = result
                files.append((label + '/' + rel, data, mode, str(source)))
    source = Path(__file__)
    data, mode = s.read_file(source)
    files.append(('archive-tools/' + source.name, data, mode, str(source)))
    for rel, data, mode, source in files:
        inv['standalone_files'].append({'path': rel, 'source': source, 'bytes': len(data), 'mode': mode,
            'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()})
    new_count = len(inv['standalone_files'])
    new_roots = len(inv['standalone_roots'])
    old_bytes = v['standalone_raw_bytes']
    new_bytes = old_bytes + sum(len(data) for _, data, _, _ in files)
    docs_path = ROOT / 'GITHUB-ARCHIVE.md'
    docs = docs_path.read_text().replace(f'{old_count:,} files from {old_roots} source locations',
                                       f'{new_count:,} files from {new_roots} source locations')
    docs = docs.replace(f'The raw total is {old_bytes / 1024 ** 3:.2f} GiB',
                        f'The raw total is {new_bytes / 1024 ** 3:.2f} GiB')
    docs += '\nA separately packaged motion skill found inside the codex-ui build cache is preserved under `standalone/cached-skill-packages`; the complete package is retained even though its parent is a cache.\n'
    docs_path.write_text(docs)
    assert docs_path.read_text() == docs
    files.extend([('README.md', docs.encode(), '100644', str(docs_path)),
                  ('inventory.json', (json.dumps(inv, indent=2) + '\n').encode(), '100644', 'generated inventory')])
    commit, _, _ = s.make_commit(ROOT, parent, files, 'Preserve final cached motion skill package')
    s.git(ROOT, 'update-ref', 'refs/heads/' + branch, commit)
    s.publish(ROOT, commit, branch)
    main_parent = s.git(ROOT, 'ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
    main_commit, _, _ = s.make_commit(ROOT, main_parent,
        [('GITHUB-ARCHIVE.md', docs.encode(), '100644', str(docs_path))],
        'Update the complete skill archive directory')
    changed = s.git(ROOT, 'diff-tree', '--no-commit-id', '--name-only', '-r', main_parent, main_commit).decode().splitlines()
    assert changed == ['GITHUB-ARCHIVE.md']
    s.git(ROOT, 'update-ref', 'refs/heads/codex/archive-navigation-' + s.DATE, main_commit)
    s.publish(ROOT, main_commit, 'main')
    tree_paths = s.git(ROOT, 'ls-tree', '-rz', commit).split(b'\0')
    tree = {}
    for item in tree_paths:
        if item:
            meta, name = item.split(b'\t', 1)
            tree[name.decode()] = meta.split()[2].decode()
    assert len(tree) == new_count + 2
    assert all(tree[e['path']] == e['git_blob'] for e in inv['standalone_files'])
    v.update({'initial_main_navigation_commit': v['main_navigation_commit'],
              'index_commit': commit, 'main_navigation_commit': main_commit,
              'standalone_files': new_count, 'index_tree_files': len(tree),
              'standalone_raw_bytes': new_bytes, 'source_locations': new_roots,
              'main_changed_files': changed})
    report.write_text(json.dumps(v, indent=2) + '\n')
    assert json.loads(report.read_text()) == v
    print(json.dumps(v), flush=True)


if __name__ == '__main__':
    main()
