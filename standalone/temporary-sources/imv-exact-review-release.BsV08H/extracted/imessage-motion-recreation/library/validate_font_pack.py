#!/usr/bin/env python3
"""Validate the pinned Linux fallback subset without installing system fonts.

Only selected ZIP members are extracted into an owned /dev/shm temporary tree.
Fontconfig runs with per-process configuration/cache paths. No browser or renderer
is launched. The additive mode checks host aliases; the isolated mode retains
those aliases but resets font directories to the extracted pinned subset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time
import xml.sax.saxutils
import zipfile

EXPECTED = {
    'LiberationSans-Regular.ttf': 'bade59d822652f76e6941aa87b40a87c13d1cc70db98ededb5011127efafd1d3',
    'DejaVuSans.ttf': '57f73e11f51999432bf7ab22ce55b6f945d5eca1bf824404cfa9ec2e3718c84e',
    'NotoColorEmoji.ttf': 'dac5c27651082d6c53dab5081f50d2022ddf6877d730fa919cf6a4fc2af22de0',
}
QUERIES = {
    'Arial': 'LiberationSans-Regular.ttf',
    'Arial:charset=2302': 'LiberationSans-Regular.ttf',
    'Arial:charset=25a2': 'DejaVuSans.ttf',
    'Arial:charset=25a3': 'DejaVuSans.ttf',
    'Arial:charset=25b0': 'DejaVuSans.ttf',
    'Arial:charset=2659': 'DejaVuSans.ttf',
    'Arial:charset=265f': 'NotoColorEmoji.ttf',
    'Arial:charset=2669': 'LiberationSans-Regular.ttf',
}
STYLE_QUERIES = {
    'Arial:style=Bold': 'LiberationSans-Bold.ttf',
    'Arial:style=Italic': 'LiberationSans-Italic.ttf',
    'Arial:style=Bold Italic': 'LiberationSans-BoldItalic.ttf',
}
LICENSES = {
    'fonts-liberation-copyright.txt': 'f32df582a2aab128c07b2f7e36e7b928dc5f6bd82657b905c04f91459f9e5cf9',
    'fonts-dejavu-core-copyright.txt': '63d3ba759d12804c5b31a9d5940d855c1820d1f5999e6b0872eb1c7ff045fbc9',
    'fonts-noto-color-emoji-copyright.txt': '3720722d2046accb40e1696f096b57c658b0b47d74031b3d114cf7545b840b3c',
}
PREFIX = 'imessage-recreations/'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for data in iter(lambda: source.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def snapshot(paths):
    """Read-only metadata/content proof, excluding access times."""
    rows = []
    for folder in paths:
        folder = Path(folder)
        if not folder.exists():
            rows.append({'path': str(folder), 'exists': False})
            continue
        candidates = [folder] + sorted(folder.rglob('*')) if folder.is_dir() else [folder]
        for path in candidates:
            info = path.lstat()
            row = dict(path=str(path), mode=info.st_mode, size=info.st_size,
                       mtime_ns=info.st_mtime_ns, inode=info.st_ino)
            if path.is_symlink():
                row['symlink'] = os.readlink(path)
            elif path.is_file():
                row['sha256'] = sha(path)
            rows.append(row)
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    return dict(sha256=digest, entries=len(rows), rows=rows)


def config(fonts, cache, isolated):
    esc = xml.sax.saxutils.escape
    return ('<?xml version="1.0"?>\n'
            '<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">\n'
            '<fontconfig>\n'
            '  <include ignore_missing="no">/etc/fonts/fonts.conf</include>\n'
            + ('  <reset-dirs/>\n' if isolated else '')
            + f'  <dir>{esc(str(fonts))}</dir>\n'
            + f'  <cachedir>{esc(str(cache))}</cachedir>\n'
            + '</fontconfig>\n')


def run(command, env, records):
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    records.append(dict(command=command, returncode=result.returncode,
                        stdout=result.stdout, stderr=result.stderr))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--shm-parent', default=Path('/dev/shm'), type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    pack = args.pack.resolve(strict=True)
    pack_sha = sha(pack)
    temporary = Path(tempfile.mkdtemp(prefix='mini-poke-font-cold-', dir=args.shm_parent))
    monitored = [Path('/etc/fonts'), Path('/usr/share/fonts'),
                 Path('/var/cache/fontconfig'), Path.home()/'.cache/fontconfig',
                 Path.home()/'.fontconfig', Path.home()/'.fonts.conf',
                 Path.home()/'.config/fontconfig']
    before = snapshot(monitored)
    report = dict(schema='message-motion-font-cold-check/1', pack=str(pack),
                  pack_sha256=pack_sha, pack_bytes=pack.stat().st_size,
                  temporary_root=str(temporary), selected_members=[], modes=[], errors=[])
    try:
        with zipfile.ZipFile(pack) as archive:
            for member in archive.infolist():
                name = member.filename
                selected = name.startswith(PREFIX+'environment/fonts/') or name.startswith(PREFIX+'environment/licenses/')
                if not selected or member.is_dir():
                    continue
                rel = Path(name)
                mode = stat.S_IFMT(member.external_attr >> 16)
                if rel.is_absolute() or '..' in rel.parts or mode not in (0, stat.S_IFREG):
                    raise ValueError('Unsafe selected ZIP member: '+name)
                target = temporary/rel
                if not target.resolve().is_relative_to(temporary):
                    raise ValueError('ZIP member escapes owned SHM tree')
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open('xb') as dest:
                    shutil.copyfileobj(source, dest)
                report['selected_members'].append(dict(member=name, bytes=target.stat().st_size,
                                                       sha256=sha(target)))
        base = temporary/PREFIX
        fonts = base/'environment/fonts'
        licenses = base/'environment/licenses'
        for name, expected in EXPECTED.items():
            if not (fonts/name).is_file() or sha(fonts/name) != expected:
                report['errors'].append('Pinned font hash mismatch: '+name)
        for name, expected in LICENSES.items():
            if not (licenses/name).is_file() or sha(licenses/name) != expected:
                report['errors'].append('Pinned license text mismatch: '+name)
        apache = licenses/'Apache-2.0.txt'
        actual_apache = Path('/usr/share/common-licenses/Apache-2.0')
        if not apache.is_file() or sha(apache) != sha(actual_apache):
            report['errors'].append('Full Apache-2.0 license mismatch')
        for mode in ['additive-host-aliases', 'isolated-fonts-host-aliases']:
            isolated = mode.startswith('isolated')
            mode_dir = temporary/mode
            mode_dir.mkdir()
            cache = mode_dir/'cache'
            cache.mkdir()
            xdg_config = mode_dir/'xdg-config'
            xdg_config.mkdir()
            text = config(fonts, cache, isolated)
            filename = mode_dir/'fonts.conf'
            filename.write_text(text)
            env = dict(os.environ, FONTCONFIG_FILE=str(filename),
                       XDG_CACHE_HOME=str(cache), XDG_CONFIG_HOME=str(xdg_config))
            env.pop('FONTCONFIG_PATH', None)
            env.pop('FONTCONFIG_SYSROOT', None)
            records = []
            mode_report = dict(name=mode, config=text, config_sha256=sha(filename),
                               environment_overrides={k:env[k] for k in ['FONTCONFIG_FILE','XDG_CACHE_HOME','XDG_CONFIG_HOME']},
                               isolated_font_directories=isolated, probes=[], commands=records)
            # Force only the extracted font directory; caches are per-process SHM.
            cached = run(['fc-cache','--force',str(fonts)], env, records)
            if cached.returncode:
                report['errors'].append(mode+': fc-cache failed')
            for query, name in {**QUERIES, **STYLE_QUERIES}.items():
                result = run(['fc-match','-f','%{file}\n%{family}\n%{style}\n',query],env,records)
                lines = result.stdout.splitlines()
                actual = Path(lines[0]) if lines else None
                expected_path = fonts/name
                expected_hash = sha(expected_path) if expected_path.is_file() else None
                actual_hash = sha(actual) if actual and actual.is_file() else None
                from_extracted = bool(actual and actual.resolve().is_relative_to(fonts))
                good = bool(result.returncode == 0 and actual_hash == expected_hash
                            and (from_extracted or not isolated))
                mode_report['probes'].append(dict(query=query, expected_file=name,
                    expected_sha256=expected_hash, actual_file=str(actual) if actual else None,
                    actual_sha256=actual_hash, actual_family=lines[1] if len(lines)>1 else None,
                    actual_style=lines[2] if len(lines)>2 else None,
                    from_extracted_font_directory=from_extracted, passed=good))
                if not good:
                    report['errors'].append(mode+': unexpected font mapping for '+query)
            listed = run(['fc-list','-f','%{file}\n'],env,records)
            files = sorted(set(listed.stdout.splitlines()))
            mode_report['visible_font_files'] = files
            mode_report['all_visible_fonts_extracted'] = all(Path(f).resolve().is_relative_to(fonts) for f in files)
            if isolated and not mode_report['all_visible_fonts_extracted']:
                report['errors'].append(mode+': outside font file visible')
            mode_report['passed'] = all(p['passed'] for p in mode_report['probes'])
            report['modes'].append(mode_report)
        after = snapshot(monitored)
        report['protected_global_paths'] = [str(p) for p in monitored]
        report['global_before'] = {k:v for k,v in before.items() if k != 'rows'}
        report['global_after'] = {k:v for k,v in after.items() if k != 'rows'}
        report['global_paths_unchanged'] = before == after
        if before != after:
            old = {r['path']:r for r in before['rows']}
            new = {r['path']:r for r in after['rows']}
            report['changed_global_paths'] = [p for p in sorted(set(old)|set(new)) if old.get(p)!=new.get(p)]
            report['errors'].append('Protected font/config/cache paths changed')
        report['pack_unchanged'] = sha(pack) == pack_sha
        if not report['pack_unchanged']:
            report['errors'].append('Frozen font pack changed')
        report['limits'] = [
            'Fontconfig mapping validation only; no browser, image renderer or visual comparison was run.',
            'Both modes deliberately inherit this host /etc/fonts/fonts.conf alias/render policy. The isolated mode removes host font directories, but this is not an independent Fontconfig policy implementation.',
            'XDG config/cache are per-process SHM. A recipient user/site rule in a different host configuration can change mappings; use a clean pinned container or recheck every returned file hash.',
            'Identical selected fonts do not certify identical FreeType/Skia/Chromium/color-font rasterization on other operating systems.',
            'Keep the accepted canonical scene/subset fonts and Pillow per-glyph behavior unchanged; these files supply environment fallbacks only.',
        ]
        report['passed'] = not report['errors']
    except BaseException as error:
        report['passed'] = False
        report['errors'].append(type(error).__name__+': '+str(error))
    finally:
        report['temporary_bytes_before_cleanup'] = sum(f.stat().st_size for f in temporary.rglob('*') if f.is_file())
        shutil.rmtree(temporary)
        report['temporary_tree_removed'] = not temporary.exists()
        report['seconds'] = time.monotonic()-started
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(report=str(args.out.resolve()),passed=report['passed'],errors=report['errors'],
                          modes=[dict(name=m['name'],passed=m['passed']) for m in report['modes']],
                          pack_sha256=pack_sha,global_paths_unchanged=report.get('global_paths_unchanged'),
                          temporary_tree_removed=report['temporary_tree_removed']),indent=2))
    return int(not report['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
