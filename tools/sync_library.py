#!/usr/bin/env python3
"""Restore this checkout from its tracked, lossless binary parts; no network.

Normal mode verifies all local parts, assembles missing whole archives and uses
the retained safe extractor to fill missing payloads. Existing different files
are refused. --verify-only never writes. --self-test uses local fixtures only.
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
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MATERIALIZER = 'skill/imessage-motion-recreation/library/materialize.py'
# These two byte-frozen snapshots are ordinary tracked Git files. Their original
# recorded checksums survive independently of the abandoned provider manifest.
FROZEN_SNAPSHOTS = [
    {'path': 'archives/imessage-motion-complete-skill-v3.zip', 'bytes': 8588186,
     'sha256': '4d3f780b872e11d5d9562008b88ea2db7e90973b310c7eeed02c4ae27b18114f'},
    {'path': 'archives/release-verification-v3.zip', 'bytes': 29931,
     'sha256': 'aa5838e0158c42a510977beca803d217e9ec1c798aeafa5a707df27751af97ab'},
]


class SyncError(Exception):
    """An actionable local integrity or manifest failure."""


def digest(path: Path) -> str:
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def local_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or '\\' in value:
        raise SyncError('Invalid local manifest path.')
    rel = PurePosixPath(value)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise SyncError('Unsafe local manifest path: ' + value)
    target = root / Path(*rel.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise SyncError('Local manifest path escapes the checkout: ' + value)
    for parent in [target, *target.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise SyncError('Refusing a symlink in a local asset path: ' + value)
    return target


def validate_record(record: dict) -> None:
    if (not isinstance(record['bytes'], int) or record['bytes'] < 0
            or not re.fullmatch(r'[0-9a-f]{64}', record['sha256'])):
        raise SyncError('A manifest record needs a nonnegative byte count and SHA256.')


def verify_file(path: Path, record: dict) -> None:
    if not path.is_file():
        raise SyncError('Missing local file: ' + str(path))
    if path.stat().st_size != record['bytes'] or digest(path) != record['sha256']:
        raise SyncError('File differs from its declared size/SHA256; it was not overwritten: '
                        + str(path) + '. Move it aside or repair it explicitly, then rerun.')


def load_library(root: Path) -> tuple[dict, list[dict]]:
    library = json.loads((root / 'LOCAL-LIBRARY.json').read_text())
    if not isinstance(library.get('archives'), list) or not library['archives']:
        raise SyncError('LOCAL-LIBRARY.json must declare its resource archives.')
    snapshots = library.get('snapshots', FROZEN_SNAPSHOTS)
    ids, paths = set(), set()
    for archive in library['archives']:
        if archive['id'] in ids:
            raise SyncError('Duplicate archive ID: ' + archive['id'])
        ids.add(archive['id'])
        validate_record(archive)
        local_path(root, archive['extracted_path'])
        entries = [(archive['archive_path'], archive), *[(p['path'], p) for p in archive['parts']]]
        if not archive['parts'] or sum(p['bytes'] for p in archive['parts']) != archive['bytes']:
            raise SyncError('Part sizes do not sum to the whole archive: ' + archive['id'])
        for name, record in entries:
            validate_record(record)
            local_path(root, name)
            if name in paths:
                raise SyncError('Duplicate archive/part path: ' + name)
            paths.add(name)
    for snapshot in snapshots:
        validate_record(snapshot)
        local_path(root, snapshot['path'])
        if snapshot['path'] in paths:
            raise SyncError('Duplicate snapshot path: ' + snapshot['path'])
        paths.add(snapshot['path'])
    return library, snapshots


def assemble(root: Path, archive: dict) -> bool:
    target = local_path(root, archive['archive_path'])
    if target.exists():
        verify_file(target, archive)
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(target.parent).free < archive['bytes']:
        raise SyncError('Insufficient space for assembled archive: ' + archive['id'])
    with tempfile.TemporaryDirectory(prefix='.library-assemble-', dir=target.parent) as directory:
        staged = Path(directory) / 'archive.zip'
        whole, total = hashlib.sha256(), 0
        with staged.open('wb') as output:
            for part in archive['parts']:
                piece, count = hashlib.sha256(), 0
                with local_path(root, part['path']).open('rb') as source:
                    while data := source.read(1024 * 1024):
                        output.write(data)
                        piece.update(data)
                        whole.update(data)
                        count += len(data)
                        total += len(data)
                if count != part['bytes'] or piece.hexdigest() != part['sha256']:
                    raise SyncError('Part changed during assembly: ' + part['path'])
        if total != archive['bytes'] or whole.hexdigest() != archive['sha256']:
            raise SyncError('Joined archive does not match its declared size/SHA256: ' + archive['id'])
        # Same-volume hard-link installation is atomic and refuses an existing
        # filename. Unlike replace(), it cannot overwrite a concurrently created
        # user archive. The temporary link is removed by TemporaryDirectory.
        try:
            os.link(staged, target)
        except FileExistsError:
            verify_file(target, archive)
            return False
        except OSError as exc:
            raise SyncError('Cannot atomically install the verified archive on this filesystem: '
                            + str(target) + '. Use a local filesystem supporting hard links.') from exc
    verify_file(target, archive)
    return True


def materializer(root: Path):
    path = local_path(root, MATERIALIZER)
    spec = importlib.util.spec_from_file_location('_retained_library_materializer', path)
    if spec is None or spec.loader is None:
        raise SyncError('Cannot load the retained safe archive materializer.')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_extracted(root: Path, archive: dict) -> int:
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


def sync(root: Path, verify_only: bool = False) -> dict:
    library, snapshots = load_library(root)
    # Validate every required part and any existing whole archive before writes.
    for archive in library['archives']:
        for part in archive['parts']:
            verify_file(local_path(root, part['path']), part)
        path = local_path(root, archive['archive_path'])
        if path.exists() or verify_only:
            verify_file(path, archive)
    for snapshot in snapshots:
        verify_file(local_path(root, snapshot['path']), snapshot)
    assembled, extracted_files = 0, 0
    if not verify_only:
        extractor = materializer(root)
        for archive in library['archives']:
            assembled += assemble(root, archive)
            extractor.extract(local_path(root, archive['archive_path']),
                              local_path(root, archive['extracted_path']))
    for archive in library['archives']:
        extracted_files += verify_extracted(root, archive)
    return {'status': 'pass', 'mode': 'offline-verify' if verify_only else 'offline-chunk-sync',
            'archives': len(library['archives']), 'snapshots': len(snapshots),
            'parts': sum(len(a['parts']) for a in library['archives']),
            'archives_assembled': assembled, 'extracted_files_verified': extracted_files,
            'network_used': False, 'existing_different_files_overwritten': False}


def self_test() -> dict:
    """Use isolated local parts and actual extraction; never contact a provider."""
    with tempfile.TemporaryDirectory(prefix='imessage-sync-test-') as directory:
        root = Path(directory)
        (root / MATERIALIZER).parent.mkdir(parents=True)
        shutil.copyfile(ROOT / MATERIALIZER, root / MATERIALIZER)
        source = root / 'fixture.zip'
        payload = {'code/example.py': b'print("retained example")\n', 'README.md': b'fixture readme\n'}
        checks = {n: hashlib.sha256(v).hexdigest() for n, v in payload.items()}
        with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED) as z:
            for n, value in payload.items(): z.writestr('case/' + n, value)
            z.writestr('case/PACK-CHECKSUMS.json', json.dumps(checks).encode())
        raw = source.read_bytes(); cut = len(raw) // 2
        def record(path, value):
            target = root / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(value)
            return {'path': path, 'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest()}
        pieces = [record('archives/parts/case.part001', raw[:cut]), record('archives/parts/case.part002', raw[cut:])]
        snapshot = record('archives/frozen-snapshot.zip', b'frozen snapshot bytes\n')
        archive = {'id': 'case', 'archive_path': 'archives/case.zip', 'bytes': len(raw),
                   'sha256': hashlib.sha256(raw).hexdigest(), 'extracted_path': 'projects/case', 'parts': pieces}
        library = {'archives': [archive], 'snapshots': [snapshot]}
        manifest = root / 'LOCAL-LIBRARY.json'
        manifest.write_text(json.dumps(library))
        seed = root / 'projects/case/case/code/example.py'; seed.parent.mkdir(parents=True); seed.write_bytes(payload['code/example.py'])
        user = root / 'projects/case/user-not-in-archive.txt'; user.write_bytes(b'user content')
        result = sync(root)
        assert result['archives_assembled'] == 1 and (root / archive['archive_path']).read_bytes() == raw
        assert seed.read_bytes() == payload['code/example.py'] and user.read_bytes() == b'user content'
        def state():
            return {str(p.relative_to(root)): (digest(p), p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
        before = state(); assert sync(root)['archives_assembled'] == 0; assert state() == before
        before = state(); assert sync(root, verify_only=True)['mode'] == 'offline-verify'; assert state() == before
        def refuses(action):
            try: action()
            except (SyncError, ValueError): return
            raise AssertionError('Unsafe operation was not refused')
        cached = root / archive['archive_path']; cached.write_bytes(b'X' * len(raw))
        refuses(lambda: sync(root)); assert cached.read_bytes() == b'X' * len(raw); cached.write_bytes(raw)
        part = root / pieces[0]['path']; correct = part.read_bytes(); part.write_bytes(b'Y' * len(correct))
        refuses(lambda: sync(root)); assert part.read_bytes() == b'Y' * len(correct); part.write_bytes(correct)
        part.unlink(); refuses(lambda: sync(root)); assert not part.exists(); part.write_bytes(correct)
        seed.write_bytes(b'user changed source'); refuses(lambda: sync(root)); assert seed.read_bytes() == b'user changed source'
        refuses(lambda: sync(root, verify_only=True)); seed.write_bytes(payload['code/example.py'])
        cached.unlink(); archive['sha256'] = '0' * 64; manifest.write_text(json.dumps(library))
        refuses(lambda: sync(root)); assert not cached.exists(); assert not list(cached.parent.glob('.library-assemble-*'))
        archive['sha256'] = hashlib.sha256(raw).hexdigest(); manifest.write_text(json.dumps(library)); sync(root)
        pieces[0]['path'] = '../escape.part'; manifest.write_text(json.dumps(library)); refuses(lambda: sync(root))
        pieces[0]['path'] = 'archives/parts/case.part001'; manifest.write_text(json.dumps(library))
        evil = root / 'traversal.zip'
        with zipfile.ZipFile(evil, 'w') as z: z.writestr('../escape.txt', b'escape')
        refuses(lambda: materializer(root).extract(evil, root / 'unsafe-destination'))
        assert not (root / 'escape.txt').exists()
        frozen = root / snapshot['path']; frozen.write_bytes(b'bad snapshot')
        refuses(lambda: sync(root)); assert frozen.read_bytes() == b'bad snapshot'
    return {'status': 'pass', 'fixture': 'isolated local files only; no network',
            'checks': ['byte-exact whole archive assembly from complete ordered parts',
                       'part and whole SHA256/size validation', 'safe merge with equal Git files',
                       'unrelated user file preserved', 'idempotent repeated sync',
                       'verify-only leaves file set/content/mtimes unchanged',
                       'corrupt existing archive refused unchanged', 'corrupt part refused unchanged',
                       'missing part refused', 'changed user source refused unchanged',
                       'wrong joined archive hash never installed and staging cleaned',
                       'manifest traversal rejected', 'archive traversal rejected',
                       'corrupt frozen snapshot refused unchanged']}


def main() -> int:
    if sys.version_info < (3, 11):
        print('Library sync requires Python 3.11 or newer.', file=sys.stderr)
        return 1
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--verify-only', action='store_true', help='Read-only verification of local archives, parts and extracted files.')
    modes.add_argument('--self-test', action='store_true', help='Run isolated local integrity/conflict tests without network access.')
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
