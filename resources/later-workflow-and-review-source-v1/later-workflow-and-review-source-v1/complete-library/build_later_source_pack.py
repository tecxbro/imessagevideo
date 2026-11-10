#!/usr/bin/env python3
"""Build the private, literal later-workflow/frontend source add-on.

Only this script's own audit and its dedicated new archive are outputs. It does
not publish, upload, render, modify source files, or rewrite other pack plans.
"""
from __future__ import annotations
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'complete-library'
IDENTITY = 'later-workflow-and-review-source-v1'
DESTINATION = Path('/dev/shm/imessage-complete-library') / (IDENTITY + '.zip')
AUDIT = LIBRARY / 'later-source-pack.audit.json'
PREFIX = IDENTITY + '/'
ROOTS = [
    (LIBRARY, 'complete-library'),
    (Path('/workspace/sites/message-motion'), 'sites/message-motion'),
    (Path('/workspace/sites/message-motion-originals'), 'sites/message-motion-originals'),
    (Path('/workspace/sites/message-motion-library'), 'sites/message-motion-library'),
]
PRUNED_DIRECTORIES = {
    '.git', 'node_modules', '.venv', 'venv', 'env', '__pycache__', '.cache',
    '.pytest_cache', '.mypy_cache', '.ruff_cache', '.openai', 'drive-ledger',
}
MEDIA = {'.mp4', '.m4v', '.mov', '.webm', '.mkv', '.avi', '.mpg', '.mpeg',
         '.m4a', '.mp3', '.wav', '.aac', '.flac', '.ogg', '.opus', '.aif',
         '.aiff', '.wma', '.m3u8'}
ARCHIVES = {'.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz', '.7z', '.rar', '.zst'}
INSTALLERS = {'.dmg', '.pkg', '.deb', '.rpm', '.exe', '.msi', '.iso'}
SOURCE_SUFFIXES = {'.py', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx', '.html',
                   '.htm', '.css', '.scss', '.sass', '.less', '.json', '.jsonl',
                   '.md', '.txt', '.csv', '.yaml', '.yml', '.toml', '.ini',
                   '.cfg', '.conf', '.xml', '.sh', '.bash', '.lock', '.map',
                   '.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp', '.avif', '.ico'}
SOURCE_NAMES = {'.gitignore', '.gitattributes', '.npmrc.example', '_headers',
                '_redirects', 'Dockerfile', 'Makefile', 'LICENSE', 'COPYING'}
RAW_THIRD_PARTY = {
    'research/sundays.html', 'research/sundays.css',
    'research/sundays-page.js', 'research/sundays-fonts.css',
}
REQUIRED_REPORTS = {
    'complete-library/photon-audit.json',
    'complete-library/mini-poke-audit.json',
    'complete-library/linq-rene-audit.json',
    'complete-library/audio-audit.json',
    'complete-library/font-cold-check.json',
    'complete-library/cold-command-check.jsonl',
    'complete-library/audio-cold-check.json',
    'complete-library/font-env-tools/validate_font_pack.py',
}
SENSITIVE_VALUE_KEYS = {
    'access_token', 'refresh_token', 'client_secret', 'private_key',
    'id_token', 'authorization', 'cookie', 'password', 'api_key',
    'apikey', 'secret_access_key', 'aws_secret_access_key',
}
PLACEHOLDER = re.compile(r'^(?:<.*>|YOUR[_ -].*|REPLACE[_ -].*|example|dummy|test(?:[_ -].*)?|fixture|\$\{.*\})$', re.I)
SECRET_PATTERNS = [
    ('private-key material', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('OAuth access-token literal', re.compile(r'\bya29\.[A-Za-z0-9_-]{30,}')),
    ('GitHub credential literal', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,})')),
    ('OpenAI credential literal', re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}')),
    ('AWS access-key literal', re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
    ('literal bearer credential', re.compile(r'Bearer\s+eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}')),
    ('signed/private download capability', re.compile(r'[?&](?:X-Amz-Signature|X-Goog-Signature|access_token|refresh_token|upload_id|uploadId)=[A-Za-z0-9._~-]{20,}', re.I)),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def json_findings(value, trail=()):
    """Return classifications only; never emit credential values."""
    results = []
    if isinstance(value, dict):
        # MCP/HTTP envelopes are saved runtime responses, not authored source.
        if ('jsonrpc' in value or 'structuredContent' in value or
            (isinstance(value.get('content'), list) and
             any(isinstance(x, dict) and x.get('type') in ('text', 'image', 'resource')
                 for x in value['content']))):
            results.append('raw protocol/tool response envelope')
        for key, child in value.items():
            if key.lower() in SENSITIVE_VALUE_KEYS and isinstance(child, str):
                if child and not PLACEHOLDER.match(child):
                    results.append('credential/header value in JSON key ' + key)
            results.extend(json_findings(child, trail + (key,)))
    elif isinstance(value, list):
        for child in value:
            results.extend(json_findings(child, trail))
    return results


def classify(path: Path, root: Path, label: str):
    rel = path.relative_to(root).as_posix()
    name = path.name.lower()
    suffix = path.suffix.lower()
    if path.is_symlink():
        return 'symlink excluded to avoid implicit/out-of-root inputs'
    if path == AUDIT:
        return 'external final archive audit excluded to avoid self-hash circularity'
    if name.startswith('.env') and name not in ('.env.example', '.env.sample', '.env.template'):
        return 'environment/credential state'
    if name in ('.npmrc', '.netrc', '.pypirc', 'credentials.json', 'token.json', 'tokens.json') or suffix in ('.pem', '.key', '.p12', '.pfx', '.jks'):
        return 'credential/config state'
    if suffix in MEDIA:
        return 'binary video/audio media'
    if suffix in ARCHIVES:
        return 'archive or compressed distribution artifact'
    if suffix in INSTALLERS:
        return 'third-party installer/download binary'
    if suffix in ('.body', '.headers', '.har', '.pcap', '.log') or name == 'header-echo.json':
        return 'raw HTTP/protocol/diagnostic response'
    if label.startswith('sites/') and rel in RAW_THIRD_PARTY:
        return 'downloaded raw third-party website/font resource'
    if 'research' in path.relative_to(root).parts and suffix in ('.ttf', '.otf', '.woff', '.woff2', '.ttc'):
        return 'downloaded research font binary'
    if name.endswith(('.tmp', '.part', '.partial')):
        return 'temporary/in-progress artifact'
    if suffix not in SOURCE_SUFFIXES and path.name not in SOURCE_NAMES:
        return 'not an authored source/config/fixture/image/audit format'
    return None


def read_snapshot(path: Path):
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    signature = lambda s: (s.st_ino, s.st_size, s.st_mtime_ns)
    if signature(before) != signature(after):
        raise RuntimeError('Source changed while being read: ' + str(path))
    return data, after


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--replace-unuploaded', action='store_true',
                        help='Only this new add-on, before upload; never another archive.')
    args = parser.parse_args()
    if DESTINATION.exists():
        if not args.replace_unuploaded:
            raise RuntimeError('New add-on already exists; default never overwrites archives')
        if any((LIBRARY / 'drive-ledger').glob('*' + IDENTITY + '*')):
            raise RuntimeError('Upload ledger exists; published/uploaded add-on is immutable')
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    protected_names = ['packs.json', 'upload-plan.json', 'upload_drive.js']
    protected = {n: file_digest(LIBRARY / n) for n in protected_names}
    existing_archives = {str(p): (p.stat().st_size, p.stat().st_mtime_ns)
                         for p in DESTINATION.parent.glob('*.zip') if p != DESTINATION}
    payloads = []
    excluded = []
    skipped_directories = []
    snapshot_notes = []
    for root, label in ROOTS:
        if not root.is_dir():
            raise FileNotFoundError(root)
        for folder, directories, files in os.walk(root, followlinks=False):
            folder = Path(folder)
            keep = []
            for name in sorted(directories):
                child = folder / name
                if name in PRUNED_DIRECTORIES or child.is_symlink():
                    skipped_directories.append({'root': label, 'path': child.relative_to(root).as_posix(),
                                                'reason': 'installed/VCS/platform/Drive-ledger/cache state' if not child.is_symlink() else 'symlink directory'})
                else:
                    keep.append(name)
            directories[:] = keep
            for name in sorted(files):
                path = folder / name
                rel = path.relative_to(root).as_posix()
                reason = classify(path, root, label)
                if reason:
                    excluded.append({'root': label, 'path': rel, 'reason': reason})
                    continue
                data, metadata = read_snapshot(path)
                findings = []
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    text = None
                if text is not None:
                    findings.extend(rule for rule, pattern in SECRET_PATTERNS if pattern.search(text))
                    if path.suffix.lower() == '.json':
                        try:
                            findings.extend(json_findings(json.loads(text)))
                        except json.JSONDecodeError:
                            # A genuine fixture can intentionally be invalid JSON.
                            pass
                if findings:
                    excluded.append({'root': label, 'path': rel,
                                     'reason': 'credential/signed-response/protocol quarantine',
                                     'classifications': sorted(set(findings))})
                    continue
                if label == 'complete-library' and name in ('packs.json', 'upload-plan.json', 'drive-config.json'):
                    snapshot_notes.append({'path': label + '/' + rel,
                                           'note': 'Nonsecret point-in-time operational config/plan, not the final v3 distribution index. IDs do not supply authorization.'})
                payloads.append({'archive_path': PREFIX + label + '/' + rel,
                                 'logical_path': label + '/' + rel, 'source_path': str(path),
                                 'bytes': len(data), 'sha256': digest(data),
                                 'crc32': f'{zlib.crc32(data) & 0xffffffff:08x}',
                                 'mode': stat.S_IMODE(metadata.st_mode),
                                 'source_mtime_ns': metadata.st_mtime_ns,
                                 '_data': data})
    payloads.sort(key=lambda r: r['archive_path'])
    logical = {r['logical_path'] for r in payloads}
    missing = REQUIRED_REPORTS - logical
    if missing:
        raise RuntimeError('Required audit/cold/font source excluded or missing: ' + ', '.join(sorted(missing)))
    if not any(p.startswith('sites/message-motion-library/worker/') for p in logical):
        raise RuntimeError('Private abandoned R2 worker source was not captured')
    if not any(p.startswith('sites/message-motion/dist/') and p.endswith('.html') for p in logical):
        raise RuntimeError('Actual authored dist frontend was not captured')
    if len({p['archive_path'] for p in payloads}) != len(payloads):
        raise RuntimeError('Duplicate archive entry')
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    readme = f'''# Private later workflow and review source add-on

This is a private source snapshot ({timestamp}), not a deployment or upload.
It contains literal complete files with per-file SHA256/CRC32, not snippets.

Included roots preserve their relative structure:

- complete-library: current workflow/build/verification code, all four audits,
  all three cold-check reports, and font-env-tools.
- sites/message-motion: genuine authored frontend, director/review/sound pages,
  tests, configs, fixtures, helper scripts, analysis JSON/CSV and images.
- sites/message-motion-originals: original-reference bridge/source and tests.
- sites/message-motion-library: an ABANDONED PRIVATE R2 PROTOTYPE. It was NEVER
  DEPLOYED. worker/index.js and its dist/server copy are historical source, not
  an active service or evidence of a public library deployment.

The dist folders are included because they contain the actual authored static
HTML/CSS/JS and fixtures, not merely a disposable dependency build.

Excluded: VCS and installed dependencies, virtualenv/cache/platform state,
Drive ledgers, raw HTTP/protocol/tool responses, signed download capabilities,
credentials, video/audio binaries, archive files, third-party font installers
and four raw downloaded Sundays website/font resources. Derived reference
posters/contact sheets and genuine frontend images remain source assets.

packs.json, upload-plan.json and drive-config.json, if included, are unmodified
nonsecret point-in-time workflow inputs. They are NOT the final v3 distribution
index; IDs alone grant no access. The root coordinator supplies the final v3
skill/index separately. No skill source or already-built pack was modified.

Publisher/uploader helpers are archived as code and were not executed by this
build. Dependencies/media are intentionally absent: use the separate verified
code/font/example/result packs and their setup instructions where required.

MANIFEST.json inventories every source payload and this README. The manifest
cannot contain its own SHA256 without circularity; all ZIP members, including
the manifest, receive a full CRC check. The external later-source-pack.audit.json
binds the final archive SHA256, size, entry count and per-file verification.
'''.encode()
    generated = {'archive_path': PREFIX + 'README-PRIVATE.md',
                 'logical_path': 'README-PRIVATE.md', 'bytes': len(readme),
                 'sha256': digest(readme), 'crc32': f'{zlib.crc32(readme) & 0xffffffff:08x}',
                 'mode': 0o600, '_data': readme, 'generated': True}
    inventory = [{k: v for k, v in r.items() if not k.startswith('_')} for r in payloads] + [
        {k: v for k, v in generated.items() if not k.startswith('_')}]
    manifest = {'id': IDENTITY, 'version': 1, 'visibility': 'PRIVATE',
                'captured_utc': timestamp, 'source_payload_files': len(payloads),
                'source_roots': [{'path': str(r), 'archive_root': label} for r, label in ROOTS],
                'prototype_status': {'root': 'sites/message-motion-library',
                                     'status': 'abandoned PRIVATE R2 prototype; NEVER DEPLOYED'},
                'files': inventory, 'operational_snapshots': snapshot_notes,
                'excluded_files': excluded, 'excluded_directories': skipped_directories,
                'final_external_audit_not_embedded': 'complete-library/later-source-pack.audit.json',
                'extra_latest_skill_tree_not_added': 'Website director code/docs/images are captured in the site worktree; root bundles final v3 skill and IDs separately.'}
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode()
    target_tmp = DESTINATION.with_name('.' + IDENTITY + f'.building-{os.getpid()}.zip')
    try:
        with zipfile.ZipFile(target_tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6,
                             allowZip64=True) as archive:
            for row in payloads + [generated]:
                info = zipfile.ZipInfo(row['archive_path'], date_time=(2026, 11, 9, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | row['mode']) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, row['_data'], compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
            archive.writestr(PREFIX + 'MANIFEST.json', manifest_bytes,
                             compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
        with zipfile.ZipFile(target_tmp) as archive:
            crc_failure = archive.testzip()
            if crc_failure is not None:
                raise RuntimeError('CRC failed: ' + crc_failure)
            for row in payloads + [generated]:
                data = archive.read(row['archive_path'])
                if len(data) != row['bytes'] or digest(data) != row['sha256']:
                    raise RuntimeError('Payload readback differs: ' + row['archive_path'])
                if f'{archive.getinfo(row["archive_path"]).CRC:08x}' != row['crc32']:
                    raise RuntimeError('Payload CRC differs: ' + row['archive_path'])
            if archive.read(PREFIX + 'MANIFEST.json') != manifest_bytes:
                raise RuntimeError('Internal manifest differs')
            total_entries = len(archive.infolist())
        # Literal payloads must still match current source before the freeze.
        for row in payloads:
            if file_digest(Path(row['source_path'])) != row['sha256']:
                raise RuntimeError('Source changed before freeze: ' + row['source_path'])
        if protected != {n: file_digest(LIBRARY / n) for n in protected_names}:
            raise RuntimeError('Protected workflow plan/uploader changed concurrently')
        for path, before in existing_archives.items():
            p = Path(path)
            if (p.stat().st_size, p.stat().st_mtime_ns) != before:
                raise RuntimeError('An existing archive changed concurrently: ' + path)
        os.chmod(target_tmp, 0o600)
        os.replace(target_tmp, DESTINATION)
        report = {'id': IDENTITY, 'path': str(DESTINATION), 'visibility': 'PRIVATE',
                  'bytes': DESTINATION.stat().st_size, 'sha256': file_digest(DESTINATION),
                  'files': total_entries, 'source_payload_files': len(payloads),
                  'source_payload_bytes': sum(p['bytes'] for p in payloads),
                  'captured_utc': timestamp, 'archive_mode': oct(stat.S_IMODE(DESTINATION.stat().st_mode)),
                  'all_payload_sha256_readbacks_pass': True, 'all_zip_crc_checks_pass': True,
                  'source_files_unchanged_at_freeze': True,
                  'protected_plans_and_uploader_unchanged': True,
                  'other_archive_sizes_mtimes_unchanged': True,
                  'source_counts_by_root': dict(collections.Counter(p['logical_path'].split('/')[0] if p['logical_path'].startswith('complete-library/') else '/'.join(p['logical_path'].split('/')[:2]) for p in payloads)),
                  'required_audits_and_cold_checks_included': sorted(REQUIRED_REPORTS),
                  'prototype_status': manifest['prototype_status'],
                  'scope': manifest['source_roots'], 'exclusions_by_reason': dict(collections.Counter(x['reason'] for x in excluded)),
                  'excluded_files': excluded, 'excluded_directories': skipped_directories,
                  'credential_scan': {'literal_secret_or_protocol_files_excluded': [x for x in excluded if x['reason'] == 'credential/signed-response/protocol quarantine'],
                                      'secret_values_emitted': False, 'source_redaction_used': False},
                  'operational_snapshots': snapshot_notes,
                  'manifest': {'path': PREFIX + 'MANIFEST.json', 'sha256': digest(manifest_bytes)},
                  'payloads': inventory,
                  'note': 'Complete literal bytes. No upload/deploy/render/browser. No existing pack,plan,uploader,skill source,or source worktree was modified. External final audit is deliberately not self-embedded.'}
        temporary_audit = AUDIT.with_name(AUDIT.name + f'.tmp-{os.getpid()}')
        temporary_audit.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
        os.replace(temporary_audit, AUDIT)
        print(json.dumps({k: report[k] for k in ('id', 'path', 'bytes', 'sha256', 'files', 'source_payload_files', 'all_payload_sha256_readbacks_pass', 'all_zip_crc_checks_pass')}, indent=2))
    finally:
        target_tmp.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
