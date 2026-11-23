"""Snapshot the checked-out skill or recover the pinned reference for independent testing."""
import argparse
import shutil
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--revision')
    args = parser.parse_args()
    prefix = Path('skill/imessage-video')
    base = args.repository.resolve() / prefix
    if args.revision:
        def git(*arguments):
            return subprocess.check_output(['git', '-C', str(args.repository), *arguments])
        for own in git('ls-tree', '-r', '--name-only', '-z', args.revision, str(prefix)).decode().split('\x00'):
            if not own:
                continue
            path = Path(own).relative_to(prefix)
            target = args.destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            candidate = base / path
            expected = git('rev-parse', f'{args.revision}:{own}').decode().strip()
            if candidate.is_file() and git('hash-object', str(candidate)).decode().strip() == expected:
                shutil.copyfile(candidate, target)
            else:
                target.write_bytes(git('show', f'{args.revision}:{own}'))
    else:
        shutil.copytree(base, args.destination, ignore=shutil.ignore_patterns('__pycache__'))


if __name__ == '__main__':
    main()
