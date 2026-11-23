#!/usr/bin/env python3
"""Preserve local iMessage video variants without changing their branches/indexes.

The discovery inputs live in /private/tmp. Each snapshot uses a separate index,
keeps its original HEAD as its parent, and is published only to a new dated ref.
This is a backup, not a functional merge or a claim that archived films pass QA.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile

DATE = '2026-11-22'
PREFIX = f'codex/computer-archive-{DATE}'
TMP = Path('/private/tmp')
ROWS = TMP / f'imessage-video-status-{DATE}.json'
RESULTS = TMP / f'imessage-video-published-{DATE}.json'
SKIP = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.cache',
        '.pytest_cache', '.mypy_cache', '.ruff_cache', '.ssh', '.aws', '.azure'}
SECRET_NAMES = {'.git-credentials', '.npmrc', '.pypirc', 'credentials.json',
                'secrets.json', 'token.json', 'tokens.json', 'id_rsa', 'id_ed25519'}
TOKEN_PATTERNS = [
    rb'gh[pousr]_[A-Za-z0-9]{30,}',
    rb'xox[baprs]-[A-Za-z0-9-]{30,}',
    rb'sk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{32,}',
    rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
    rb'(?i)(?:X-Amz-Signature|X-Goog-Signature)=[a-f0-9]{32,}',
]
EXCLUSION_FILE = Path('/Users/darshan/Documents/video-analysis/imessagevideo-dl/skill/imessage-motion-recreation/observer/exclusions.json')
EXCLUDED_SHA256 = {entry['sha256'] for entry in json.loads(EXCLUSION_FILE.read_text())}


def git(root, *args, data=None, env=None):
    cfg = os.environ.copy()
    cfg.update({'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'})
    if env:
        cfg.update(env)
    p = subprocess.run(['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0',
                        *args], cwd=root, input=data, capture_output=True, env=cfg)
    if p.returncode:
        raise RuntimeError(f'git {args[0]} in {root}: {p.stderr.decode(errors="replace")[:1200]}')
    return p.stdout


def slug(root):
    p = Path(root)
    if p.parent.name == 'imv-wt':
        return 'devin-' + p.name
    if p.parent.name == 'codex-sound':
        return 'codex-sound-' + p.name
    if 'goal-test-the-imessage-video-skill' in root:
        return 'real-video-verification'
    if root.startswith('/private/tmp/'):
        return 'codex-observer'
    return p.name


def omit(rel):
    p = Path(rel)
    if any(x in SKIP for x in p.parts):
        return 'dependency/cache/version-control metadata'
    low = p.name.lower()
    if low in SECRET_NAMES or (low.startswith('.env') and not any(x in low for x in ['example', 'sample', 'template'])):
        return 'credential filename'
    if low == '.ds_store' or low.endswith(('.download', '.writing', '.partial', '.pyc')):
        return 'system metadata or incomplete/generated file'
    # Numeric decoded frame sequences are regenerable from the retained films.
    if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
        if re.match(r'^(?:frame[-_]?)?\d{3,}(?:[-_]diff)?\.', low):
            if not any(x in p.parts for x in {'assets', 'plates', 'portraits'}):
                return 'decoded frame sequence'
        if any('cache' in x.lower() or x.lower() in {'frames-all', 'frames-all-reference', 'frames-all-output'} for x in p.parts):
            return 'render frame cache'
    if any(x.startswith('evidence-chrome') for x in p.parts):
        return 'browser profile/session data'
    return None


def read_file(path):
    if path.is_symlink():
        return os.readlink(path).encode(), '120000'
    content = path.read_bytes()
    return content, '100755' if path.stat().st_mode & stat.S_IXUSR else '100644'


def inspect_file(path, rel):
    reason = omit(rel)
    if reason:
        return None, reason
    data, mode = read_file(path)
    if hashlib.sha256(data).hexdigest() in EXCLUDED_SHA256:
        return None, 'recorded source exclusion'
    if len(data) >= 100 * 1024 * 1024:
        return None, 'exceeds GitHub Git file-size limit; requires release asset'
    if b'\0' not in data[:8192]:
        for pattern in TOKEN_PATTERNS:
            if re.search(pattern, data):
                return None, 'possible credential or signed download URL'
    return (data, mode), None


def make_commit(root, parent, files, message):
    with tempfile.TemporaryDirectory(prefix='imv-index-', dir=TMP) as d:
        env = {'GIT_INDEX_FILE': str(Path(d) / 'index')}
        git(root, 'read-tree', parent if parent else '--empty', env=env)
        records = []
        manifest = []
        for rel, data, mode, source in files:
            oid = git(root, 'hash-object', '-w', '--stdin', data=data).decode().strip()
            records.append(f'{mode} {oid}\t{rel}'.encode() + b'\0')
            manifest.append({'path': rel, 'source': source, 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest(), 'git_blob': oid, 'mode': mode})
        if records:
            git(root, 'update-index', '-z', '--index-info', data=b''.join(records), env=env)
        tree = git(root, 'write-tree', '--missing-ok', env=env).decode().strip()
        args = ['commit-tree', tree]
        if parent:
            args += ['-p', parent]
        commit = git(root, *args, data=(message + '\n').encode()).decode().strip()
        # Re-read each object; confirm the stored bytes are exactly what was read.
        for entry in manifest:
            actual = git(root, 'cat-file', 'blob', entry['git_blob'])
            assert hashlib.sha256(actual).hexdigest() == entry['sha256']
        return commit, tree, manifest


def publish(root, commit, branch):
    # No force pushes, branch switches, real-index edits, or maintenance runs.
    git(root, 'push', 'origin', f'{commit}:refs/heads/{branch}')
    remote = git(root, 'ls-remote', 'origin', f'refs/heads/{branch}').decode().split()[0]
    assert remote == commit, (branch, commit, remote)


def main():
    rows = json.loads(ROWS.read_text())
    results = json.loads(RESULTS.read_text()) if RESULTS.exists() else []
    done = {r['local_path'] for r in results}
    for row in rows:
        root = row['path']
        if root in done:
            continue
        # Refresh status at capture time. Missing tracked payloads are preserved
        # in the parent tree; an incomplete checkout is not a mass deletion.
        entries = git(root, 'status', '--porcelain=v1', '-z', '--untracked-files=all').decode().split('\0')
        files = []
        omitted = []
        missing = []
        i = 0
        while i < len(entries):
            e = entries[i]
            i += 1
            if not e:
                continue
            state, rel = e[:2], e[3:]
            if 'R' in state or 'C' in state:
                i += 1  # porcelain -z has a second name for rename/copy.
            path = Path(root) / rel
            if not path.exists() and not path.is_symlink():
                missing.append(rel)
                continue
            if path.is_dir():
                omitted.append({'path': rel, 'reason': 'directory/submodule entry'})
                continue
            result, reason = inspect_file(path, rel)
            if reason:
                omitted.append({'path': rel, 'reason': reason})
                continue
            data, mode = result
            files.append((rel, data, mode, str(path)))
        parent = git(root, 'rev-parse', 'HEAD').decode().strip()
        branch = PREFIX + '/' + slug(root)
        if files:
            commit, tree, manifest = make_commit(root, parent, files,
                f'Archive local {slug(root)} work as of {DATE}')
        else:
            commit = parent
            tree = git(root, 'rev-parse', parent + '^{tree}').decode().strip()
            manifest = []
        # Retain a durable local ref, using a name separate from active branches.
        git(root, 'update-ref', 'refs/heads/' + branch, commit)
        publish(root, commit, branch)
        result = {'local_path': root, 'original_branch': row['branch'], 'original_head': parent,
                  'archive_branch': branch, 'commit': commit, 'tree': tree, 'captured_files': manifest,
                  'omitted_files': omitted, 'unmaterialized_tracked_paths': missing,
                  'url': 'https://github.com/tecxbro/imessagevideo/tree/' + branch,
                  'verified_remote': True}
        results.append(result)
        RESULTS.write_text(json.dumps(results, indent=2) + '\n')
        assert json.loads(RESULTS.read_text())[-1]['commit'] == commit
        print(json.dumps({'published': branch, 'commit': commit, 'captured_files': len(manifest),
                          'omitted': len(omitted), 'unmaterialized': len(missing)}), flush=True)


if __name__ == '__main__':
    main()
