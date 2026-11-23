#!/usr/bin/env python3
"""Complete a partially published archive with one batched Git object import."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('archive', HERE / 'archive_standalone.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
s = a.s


def main():
    plan = json.loads(a.PLAN.read_text())
    parent = s.git(a.ROOT, 'ls-remote', 'origin', 'refs/heads/' + a.BRANCH).decode().split()[0]
    regular = [e for e in plan['files'] if e['mode'] != '120000']
    assert all('\n' not in e['source'] and not e['source'].startswith('"') for e in regular)
    paths = ''.join(e['source'] + '\n' for e in regular).encode()
    oids = s.git(a.ROOT, 'hash-object', '-w', '--no-filters', '--stdin-paths', data=paths).decode().splitlines()
    assert len(oids) == len(regular)
    by_source = dict(zip((e['source'] for e in regular), oids))
    print(json.dumps({'batch_imported_files': len(regular)}), flush=True)
    records = []
    for e in plan['files']:
        data, mode = s.read_file(Path(e['source']))
        assert hashlib.sha256(data).hexdigest() == e['sha256'], e['source']
        oid = by_source.get(e['source'])
        if mode == '120000':
            oid = s.git(a.ROOT, 'hash-object', '-w', '--stdin', data=data).decode().strip()
        assert oid == hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        e['git_blob'] = oid
        records.append(f"{mode} {oid}\t{e['path']}".encode() + b'\0')
    discovery = json.loads((s.TMP / f'imessage-video-discovery-{s.DATE}.json').read_text())
    inventory = {'date': s.DATE, 'repository': 'tecxbro/imessagevideo',
                 'worktrees': json.loads(s.RESULTS.read_text()), 'standalone_roots': plan['source_roots'],
                 'standalone_files': plan['files'], 'omitted': plan['omitted'],
                 'scan_scope': discovery['roots'], 'protected_locations': discovery['errors']}
    docs = (a.ROOT / 'GITHUB-ARCHIVE.md').read_bytes()
    for rel, data in [('inventory.json', (json.dumps(inventory, indent=2) + '\n').encode()), ('README.md', docs)]:
        oid = s.git(a.ROOT, 'hash-object', '-w', '--stdin', data=data).decode().strip()
        records.append(f'100644 {oid}\t{rel}'.encode() + b'\0')
    with tempfile.TemporaryDirectory(prefix='imv-final-batch-index-', dir=s.TMP) as tmp:
        env = {'GIT_INDEX_FILE': str(Path(tmp) / 'index')}
        s.git(a.ROOT, 'read-tree', parent, env=env)
        s.git(a.ROOT, 'update-index', '-z', '--index-info', data=b''.join(records), env=env)
        tree = s.git(a.ROOT, 'write-tree', '--missing-ok', env=env).decode().strip()
        commit = s.git(a.ROOT, 'commit-tree', tree, '-p', parent,
                       data=f'Complete standalone source and export archive, {s.DATE}\n'.encode()).decode().strip()
    actual = {}
    for record in s.git(a.ROOT, 'ls-tree', '-rz', commit).split(b'\0'):
        if record:
            meta, name = record.split(b'\t', 1)
            actual[name.decode()] = meta.split()[2].decode()
    assert len(actual) == len(plan['files']) + 2
    assert all(actual[e['path']] == e['git_blob'] for e in plan['files'])
    s.git(a.ROOT, 'update-ref', 'refs/heads/' + a.BRANCH, commit)
    s.publish(a.ROOT, commit, a.BRANCH)
    result = {'branch': a.BRANCH, 'commit': commit, 'tree': tree, 'files': len(actual), 'verified_remote': True,
              'bytes': sum(e['bytes'] for e in plan['files']),
              'unique_bytes': sum({e['sha256']: e['bytes'] for e in plan['files']}.values())}
    a.RESULT.write_text(json.dumps(result, indent=2) + '\n')
    assert json.loads(a.RESULT.read_text()) == result
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
