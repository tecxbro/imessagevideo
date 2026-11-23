#!/usr/bin/env python3
"""Resolve pinned upstream source, reusing a clean checkout or fetching it once."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SOURCES = {
    "rea-video": ("JuneYaooo/rea-video", "86486c6e104b917fb4b6a2d6501134686c05b219",
                  "skills/rea-video/SKILL.md"),
    "hyperframes": ("heygen-com/hyperframes", "66156bf35ebecfe0075d3d01405773ab2792a6f0",
                    "skills/hyperframes/scripts/plugin-cli.mjs"),
}


def usable(path, revision, entrypoint):
    if not (path / ".git").exists() or not (path / entrypoint).is_file():
        return False
    # Local probes must never ask a partial clone's promisor remote for objects.
    env = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"}
    git = ["git", "-C", str(path)]
    head = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True, env=env)
    if head.returncode or head.stdout.strip() != revision:
        return False
    return subprocess.run(git + ["diff", "--quiet", "--no-ext-diff", "HEAD", "--"],
                          env=env).returncode == 0


def resolve(name, cache, roots, offline):
    repo, revision, entrypoint = SOURCES[name]
    key = f"{name}-{revision[:12]}"
    checkout = cache / key
    remembered = cache / f"{key}.path"
    with (cache / f"{key}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        candidates = [root / name for root in roots] + list(roots) + [checkout]
        if remembered.is_file():
            saved = remembered.read_text().strip()
            if saved:
                candidates.append(Path(saved))
        for candidate in dict.fromkeys(candidates):
            if usable(candidate, revision, entrypoint):
                path = candidate.resolve()
                if path != checkout:
                    remembered.write_text(str(path) + "\n")
                return {"path": str(path), "commit": revision, "status": "reused"}
        if offline:
            raise ValueError(f"No clean local {name} checkout at {revision}. "
                             "Supply --source-root with a matching checkout or run once online.")
        if checkout.exists():
            raise ValueError(f"Cache path {checkout} differs from the pin. Supply a clean "
                             "--source-root or choose a new --cache to preserve local changes.")
        # Fetch exactly this commit. A temporary directory keeps partial pulls out of the cache.
        with tempfile.TemporaryDirectory(dir=cache, prefix=f".{name}-") as tmp:
            work = Path(tmp) / "checkout"
            subprocess.run(["git", "init", "--quiet", str(work)], check=True)
            git = ["git", "-C", str(work)]
            subprocess.run(git + ["remote", "add", "origin", f"https://github.com/{repo}.git"], check=True)
            subprocess.run(git + ["fetch", "--quiet", "--depth=1", "origin", revision], check=True)
            subprocess.run(git + ["checkout", "--quiet", "--detach", revision], check=True)
            if not usable(work, revision, entrypoint):
                raise ValueError(f"Fetched {name} checkout is missing the pinned entrypoint.")
            work.rename(checkout)
        return {"path": str(checkout), "commit": revision, "status": "fetched"}


def main():
    default_cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "imessage-video" / "sources"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=default_cache, help="persistent source cache folder")
    parser.add_argument("--source-root", type=Path, action="append", default=[],
                        help="parent of checkouts, or an individual checkout (repeatable)")
    parser.add_argument("--offline", action="store_true", help="only use existing local source")
    parser.add_argument("--path", choices=SOURCES, help="resolve only this source and print its path")
    args = parser.parse_args()
    cache = args.cache.expanduser().resolve()
    try:
        cache.mkdir(parents=True, exist_ok=True)
        roots = [path.expanduser().resolve() for path in args.source_root]
        names = [args.path] if args.path else SOURCES
        results = {name: resolve(name, cache, roots, args.offline) for name in names}
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1
    print(results[args.path]["path"] if args.path else json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
