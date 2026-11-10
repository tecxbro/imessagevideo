#!/usr/bin/env python3
"""Restore this checkout's private GitHub Release assets, without Git LFS.

Normal: gh downloads only whole ZIPs/snapshots; verified ZIP bytes recreate the
separately published parts. Existing materialize.extract safely fills missing
payload files. --verify-only is offline/read-only. --self-test uses a fake gh.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.parse import quote
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MATERIALIZER = 'skill/imessage-motion-recreation/library/materialize.py'


class SyncError(Exception):
    """An actionable integrity, manifest or provider failure."""


def digest(path: Path) -> str:
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def local_path(root: Path, value: str) -> Path:
    rel = PurePosixPath(value)
    if not value or rel.is_absolute() or '..' in rel.parts or '\\' in value:
        raise SyncError('Unsafe local manifest path: ' + value)
    target = root / Path(*rel.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise SyncError('Local manifest path escapes the checkout: ' + value)
    for parent in [target, *target.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise SyncError('Refusing a symlink in local asset path: ' + value)
    return target


def verify_file(path: Path, record: dict) -> None:
    if not path.is_file():
        raise SyncError('Missing local file: ' + str(path))
    if path.stat().st_size != record['bytes'] or digest(path) != record['sha256']:
        raise SyncError('File differs from its declared size/SHA256; it was not overwritten: '
                        + str(path) + '. Move it aside or repair it explicitly, then rerun.')


def load_plan(root: Path) -> tuple[dict, dict, dict[str, dict]]:
    release = json.loads((root / 'GITHUB-ASSETS.json').read_text())
    library = json.loads((root / 'LOCAL-LIBRARY.json').read_text())
    repo = release.get('repo', release.get('repository'))
    tag = release.get('tag', release.get('release_tag'))
    if not isinstance(repo, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise SyncError('GITHUB-ASSETS.json needs repo="owner/repository".')
    if not isinstance(tag, str) or not tag or tag.startswith('-') or any(c.isspace() for c in tag):
        raise SyncError('GITHUB-ASSETS.json has an invalid release tag.')
    release.update(repo=repo, tag=tag)
    by_path, names = {}, set()
    for asset in release['assets']:
        name = asset['file_name']
        if (not isinstance(name, str) or not name or name.startswith('-')
                or Path(name).name != name or '\\' in name or any(c in name for c in '*?[')):
            raise SyncError('Asset file_name must be a literal, single filename.')
        local_path(root, asset['path'])
        if asset['role'] not in {'archive', 'part', 'snapshot'}:
            raise SyncError('Unknown asset role: ' + str(asset['role']))
        if (not isinstance(asset['bytes'], int) or asset['bytes'] < 0
                or not re.fullmatch(r'[0-9a-f]{64}', asset['sha256'])):
            raise SyncError('Asset needs a nonnegative byte count and SHA256: ' + name)
        if asset['path'] in by_path or name in names:
            raise SyncError('Duplicate GitHub asset path/name: ' + name)
        by_path[asset['path']] = asset
        names.add(name)
    expected_archives, expected_parts = set(), set()
    for archive in library['archives']:
        local_path(root, archive['extracted_path'])
        expected_archives.add(archive['archive_path'])
        records = [(archive['archive_path'], archive, 'archive')]
        if sum(p['bytes'] for p in archive['parts']) != archive['bytes']:
            raise SyncError('Declared part sizes do not sum to archive: ' + archive['id'])
        for part in archive['parts']:
            expected_parts.add(part['path'])
            records.append((part['path'], part, 'part'))
        for path, expected, role in records:
            actual = by_path.get(path)
            if not actual or any(actual[k] != expected[k] for k in ['bytes', 'sha256']) or actual['role'] != role:
                raise SyncError('Release/local library manifests disagree at: ' + path)
            if actual.get('archive_id', archive['id']) != archive['id']:
                raise SyncError('Asset archive_id disagrees: ' + path)
    if expected_archives != {p for p, x in by_path.items() if x['role'] == 'archive'}:
        raise SyncError('Release archive set differs from LOCAL-LIBRARY.json.')
    if expected_parts != {p for p, x in by_path.items() if x['role'] == 'part'}:
        raise SyncError('Release part set differs from LOCAL-LIBRARY.json.')
    return release, library, by_path


def gh_json(command: list[str], arguments: list[str], operation: str) -> dict:
    try:
        result = subprocess.run(command + arguments, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SyncError('GitHub CLI is missing. Install gh and run gh auth login, then retry.') from exc
    if result.returncode:
        # Provider errors may contain bearer URLs; never echo raw stderr/stdout.
        raise SyncError(f'GitHub CLI failed during {operation} (exit {result.returncode}). '
                        'Check repository access and gh auth status locally.')
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        raise SyncError('GitHub CLI returned invalid JSON during ' + operation) from exc


def verify_release(release: dict, command: list[str]) -> None:
    # gh's REST read exposes both numeric asset ids and GraphQL node_ids; this
    # avoids comparing ids from different namespaces or silently ignoring them.
    endpoint = 'repos/' + release['repo'] + '/releases/tags/' + quote(release['tag'], safe='')
    observed = gh_json(command, ['api', endpoint, '--method', 'GET'], 'release metadata read')
    if observed.get('tag_name') != release['tag']:
        raise SyncError('Observed release tag differs from the declared tag.')
    published = {x['name']: x for x in observed.get('assets', [])}
    for expected in release['assets']:
        actual = published.get(expected['file_name'])
        if not actual or actual.get('size') != expected['bytes']:
            raise SyncError('Missing or wrong-size GitHub Release asset: ' + expected['file_name'])
        asset_id = expected.get('asset_id', expected.get('github_asset_id', expected.get('id')))
        node_id = expected.get('node_id', expected.get('github_node_id'))
        if isinstance(asset_id, str) and asset_id.startswith('RA_'):
            node_id, asset_id = asset_id, None
        if asset_id is not None and str(actual.get('id')) != str(asset_id):
            raise SyncError('GitHub asset ID differs: ' + expected['file_name'])
        if node_id is not None and str(actual.get('node_id')) != str(node_id):
            raise SyncError('GitHub asset node ID differs: ' + expected['file_name'])


def download(root: Path, release: dict, asset: dict, command: list[str]) -> bool:
    target = local_path(root, asset['path'])
    if target.exists():
        verify_file(target, asset)
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.library-download-', dir=target.parent) as directory:
        gh_json(command, ['release', 'download', release['tag'], '--repo', release['repo'],
                          '--pattern', asset['file_name'], '--dir', directory, '--skip-existing'],
                'download of ' + asset['file_name'])
        staged = Path(directory) / asset['file_name']
        verify_file(staged, asset)
        # Exclusive creation protects a file created concurrently by the user.
        try:
            with target.open('xb') as out, staged.open('rb') as source:
                shutil.copyfileobj(source, out, 1024 * 1024)
        except FileExistsError:
            verify_file(target, asset)
            return False
        except BaseException:
            target.unlink(missing_ok=True)
            raise
    verify_file(target, asset)
    return True


def recreate_parts(root: Path, archive: dict) -> int:
    created = 0
    with local_path(root, archive['archive_path']).open('rb') as source:
        for part in archive['parts']:
            target = local_path(root, part['path'])
            if target.exists():
                verify_file(target, part)
                source.seek(part['bytes'], 1)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.library-part-', dir=target.parent) as directory:
                staged = Path(directory) / 'part'
                remaining = part['bytes']
                with staged.open('wb') as out:
                    while remaining:
                        data = source.read(min(1024 * 1024, remaining))
                        if not data:
                            raise SyncError('Unexpected end of archive: ' + archive['id'])
                        out.write(data)
                        remaining -= len(data)
                verify_file(staged, part)
                try:
                    with target.open('xb') as out, staged.open('rb') as piece:
                        shutil.copyfileobj(piece, out, 1024 * 1024)
                except FileExistsError:
                    verify_file(target, part)
                except BaseException:
                    target.unlink(missing_ok=True)
                    raise
                else:
                    created += 1
            verify_file(target, part)
        if source.read(1):
            raise SyncError('Parts leave trailing archive bytes: ' + archive['id'])
    return created


def verify_extracted(root: Path, archive: dict) -> int:
    destination = local_path(root, archive['extracted_path'])
    with zipfile.ZipFile(local_path(root, archive['archive_path'])) as z:
        checks_name = next((n for n in z.namelist() if n.endswith('/PACK-CHECKSUMS.json')), None)
        checks_bytes = z.read(checks_name) if checks_name else None
        checks = json.loads(checks_bytes) if checks_bytes else None
        prefix = checks_name.rsplit('/', 1)[0] + '/' if checks_name else ''
        seen, count = set(), 0
        for entry in z.infolist():
            name = entry.filename
            path = PurePosixPath(name)
            if (path.is_absolute() or '..' in path.parts or '\\' in name or name in seen
                    or stat.S_IFMT(entry.external_attr >> 16) == stat.S_IFLNK):
                raise SyncError('Unsafe archive member: ' + name)
            seen.add(name)
            if name == checks_name:
                member = '.library-receipts/' + hashlib.sha256(checks_bytes).hexdigest() + '-PACK-CHECKSUMS.json'
            else:
                member = name
            target = local_path(root, archive['extracted_path'] + '/' + member)
            if entry.is_dir():
                if not target.is_dir():
                    raise SyncError('Missing extracted directory: ' + str(target))
                continue
            h = hashlib.sha256()
            with z.open(entry) as stream:
                while chunk := stream.read(1024 * 1024):
                    h.update(chunk)
            expected = h.hexdigest()
            if checks is not None and name != checks_name and checks.get(name.removeprefix(prefix)) != expected:
                raise SyncError('Internal pack checksum differs: ' + name)
            verify_file(target, {'bytes': entry.file_size, 'sha256': expected})
            count += 1
    return count


def materializer(root: Path):
    path = local_path(root, MATERIALIZER)
    spec = importlib.util.spec_from_file_location('_retained_library_materializer', path)
    if spec is None or spec.loader is None:
        raise SyncError('Cannot load the retained safe archive materializer.')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sync(root: Path, verify_only: bool = False, command: list[str] | None = None) -> dict:
    command = command or ['gh']
    release, library, assets = load_plan(root)
    # Refuse corrupt cached assets before any network request or extraction.
    for asset in assets.values():
        path = local_path(root, asset['path'])
        if path.exists():
            verify_file(path, asset)
        elif verify_only:
            raise SyncError('Missing local file in offline verification: ' + asset['path'])
    downloaded, parts_created, extracted_files = 0, 0, 0
    if not verify_only:
        verify_release(release, command)
        for asset in assets.values():
            if asset['role'] != 'part':
                downloaded += download(root, release, asset, command)
        extractor = materializer(root)
        for archive in library['archives']:
            parts_created += recreate_parts(root, archive)
            extractor.extract(local_path(root, archive['archive_path']),
                              local_path(root, archive['extracted_path']))
    for archive in library['archives']:
        extracted_files += verify_extracted(root, archive)
    return {'status': 'pass', 'mode': 'offline-verify' if verify_only else 'github-release-sync',
            'archives': len(library['archives']), 'snapshots': sum(a['role'] == 'snapshot' for a in assets.values()),
            'parts': sum(len(a['parts']) for a in library['archives']), 'assets_downloaded': downloaded,
            'parts_recreated': parts_created, 'extracted_files_verified': extracted_files,
            'existing_different_files_overwritten': False}


def self_test() -> dict:
    """Exercise the real sync with an isolated fake gh; never contact GitHub."""
    with tempfile.TemporaryDirectory(prefix='imessage-sync-test-') as directory:
        root = Path(directory); remote = root / '_fake_remote'; remote.mkdir()
        (root / MATERIALIZER).parent.mkdir(parents=True)
        shutil.copyfile(ROOT / MATERIALIZER, root / MATERIALIZER)
        payload = {'code/example.py': b'print("retained example")\n', 'README.md': b'fixture readme\n'}
        checks = {n: hashlib.sha256(v).hexdigest() for n, v in payload.items()}
        with zipfile.ZipFile(remote / 'case.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for n, value in payload.items(): z.writestr('case/' + n, value)
            z.writestr('case/PACK-CHECKSUMS.json', json.dumps(checks).encode())
        raw = (remote / 'case.zip').read_bytes(); cut = len(raw) // 2
        records = []
        def asset(name, path, value, role):
            record = {'file_name': name, 'path': path, 'bytes': len(value),
                      'sha256': hashlib.sha256(value).hexdigest(), 'role': role}
            records.append(record); return record
        whole = asset('case.zip', 'archives/case.zip', raw, 'archive')
        pieces = []
        for i, value in enumerate([raw[:cut], raw[cut:]], 1):
            a = asset(f'case.zip.part{i:03}', f'archives/parts/case.zip.part{i:03}', value, 'part')
            pieces.append({k: a[k] for k in ['path', 'bytes', 'sha256']})
        snapshot = b'frozen skill snapshot\n'; (remote / 'skill.zip').write_bytes(snapshot)
        snap = asset('skill.zip', 'archives/skill.zip', snapshot, 'snapshot')
        archive = {'id': 'case', 'archive_path': whole['path'], 'bytes': len(raw),
                   'sha256': whole['sha256'], 'extracted_path': 'projects/case', 'parts': pieces}
        (root / 'LOCAL-LIBRARY.json').write_text(json.dumps({'archives': [archive]}))
        (root / 'GITHUB-ASSETS.json').write_text(json.dumps({'repo': 'fixture/repo', 'tag': 'v1', 'assets': records}))
        meta = {'tag_name': 'v1', 'assets': [{'name': a['file_name'], 'size': a['bytes']} for a in records]}
        (remote / 'metadata.json').write_text(json.dumps(meta))
        shim = remote / 'gh.py'
        shim.write_text("""import sys,json,shutil
from pathlib import Path
r=Path(__file__).parent;a=sys.argv[1:]
with (r/'calls.jsonl').open('a') as f:f.write(json.dumps(a)+'\\n')
if a[:1]==['api']:print((r/'metadata.json').read_text())
elif a[:2]==['release','download']:
 name=a[a.index('--pattern')+1];d=Path(a[a.index('--dir')+1]);shutil.copyfile(r/name,d/name)
else:raise SystemExit(91)
""")
        command = [sys.executable, str(shim)]
        seed = root / 'projects/case/case/code/example.py'; seed.parent.mkdir(parents=True); seed.write_bytes(payload['code/example.py'])
        user = root / 'projects/case/user-not-in-archive.txt'; user.write_bytes(b'user content')
        result = sync(root, command=command)
        assert result['assets_downloaded'] == 2 and result['parts_recreated'] == 2
        calls = (remote / 'calls.jsonl').read_bytes()
        assert len([x for x in calls.splitlines() if b'"download"' in x]) == 2
        assert seed.read_bytes() == payload['code/example.py'] and user.read_bytes() == b'user content'
        assert sync(root, verify_only=True, command=['must-not-run'])['mode'] == 'offline-verify'
        assert (remote / 'calls.jsonl').read_bytes() == calls
        def refuses(action):
            try: action()
            except (SyncError, ValueError): return
            raise AssertionError('Unsafe operation was not refused')
        cached = root / whole['path']; cached.write_bytes(b'X' * len(raw))
        refuses(lambda: sync(root, command=command)); assert cached.read_bytes() == b'X' * len(raw)
        assert (remote / 'calls.jsonl').read_bytes() == calls
        cached.write_bytes(raw)
        part = root / pieces[0]['path']; correct = part.read_bytes(); part.write_bytes(b'Y' * len(correct))
        refuses(lambda: sync(root, command=command)); assert part.read_bytes() == b'Y' * len(correct); part.write_bytes(correct)
        seed.write_bytes(b'user changed source')
        refuses(lambda: sync(root, command=command)); assert seed.read_bytes() == b'user changed source'
        refuses(lambda: sync(root, verify_only=True)); seed.write_bytes(payload['code/example.py'])
        bad = json.loads((root / 'GITHUB-ASSETS.json').read_text()); bad['assets'][0]['path'] = '../escape.zip'
        original = (root / 'GITHUB-ASSETS.json').read_text(); (root / 'GITHUB-ASSETS.json').write_text(json.dumps(bad))
        refuses(lambda: sync(root, command=command)); (root / 'GITHUB-ASSETS.json').write_text(original)
        (root / snap['path']).unlink(); (remote / 'skill.zip').write_bytes(b'Z' * len(snapshot))
        refuses(lambda: sync(root, command=command)); assert not (root / snap['path']).exists()
        (remote / 'skill.zip').write_bytes(snapshot); meta['assets'][0]['size'] += 1
        (remote / 'metadata.json').write_text(json.dumps(meta)); refuses(lambda: sync(root, command=command))
        meta['assets'][0].update(size=len(raw), id=123, node_id='RA_fixture')
        (remote / 'metadata.json').write_text(json.dumps(meta))
        declared = json.loads(original); declared['assets'][0].update(id=123, node_id='RA_fixture')
        (root / 'GITHUB-ASSETS.json').write_text(json.dumps(declared))
        verify_release(load_plan(root)[0], command)
        declared['assets'][0]['id'] = 124
        (root / 'GITHUB-ASSETS.json').write_text(json.dumps(declared))
        refuses(lambda: verify_release(load_plan(root)[0], command))
        declared['assets'][0].update(id=123, node_id='RA_wrong')
        (root / 'GITHUB-ASSETS.json').write_text(json.dumps(declared))
        refuses(lambda: verify_release(load_plan(root)[0], command))
    return {'status': 'pass', 'fixture': 'isolated fake gh; no network',
            'checks': ['whole download SHA/size', 'no duplicate part downloads', 'exact part recreation',
                       'safe merge with equal Git files', 'unrelated user file preserved',
                       'offline verification makes no gh call', 'corrupt cache refused unchanged',
                       'corrupt part refused unchanged', 'changed user source refused unchanged',
                       'manifest traversal rejected', 'corrupt remote download not installed',
                       'wrong provider asset size rejected', 'declared REST asset ID checked',
                       'declared GraphQL node ID checked']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--verify-only', action='store_true', help='Verify all local archives, parts and extracted files; never use the network or modify files.')
    modes.add_argument('--self-test', action='store_true', help='Run an isolated fake-gh integrity/conflict test without network access.')
    args = parser.parse_args()
    try:
        result = self_test() if args.self_test else sync(ROOT, verify_only=args.verify_only)
    except (SyncError, ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print('Library sync failed: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
