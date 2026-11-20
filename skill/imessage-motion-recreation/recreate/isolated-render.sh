#!/usr/bin/env bash
# Bind only a prepared render input tree, system runtime and a new output tree.
set -euo pipefail
if (( $# < 3 )); then
  echo "Usage: bash isolated-render.sh STAGED_INPUT EMPTY_OUTPUT COMMAND [ARG ...]" >&2
  exit 2
fi
input="$(realpath -e -- "$1")"
mkdir -p -- "$2"
output="$(realpath -e -- "$2")"
shift 2
if [[ "$input" == "$output" || "$input" == "$output/"* || "$output" == "$input/"* ]]; then
  echo "Stage editable inputs and render output in distinct trees." >&2
  exit 2
fi
if [[ -n "$(find "$output" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo "The isolated output directory must be empty." >&2
  exit 2
fi
runtime=(--ro-bind /usr /usr --ro-bind /etc /etc)
for path in /bin /lib /lib64 /opt; do
  if [[ -e "$path" ]]; then
    runtime+=(--ro-bind "$path" "$path")
  fi
done
exec bwrap --die-with-parent --new-session --unshare-net --clearenv \
  "${runtime[@]}" --proc /proc --dev /dev --tmpfs /tmp \
  --ro-bind "$input" /input --bind "$output" /output --chdir /input \
  --setenv HOME /tmp --setenv PATH /opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin:/usr/local/bin:/usr/bin:/bin \
  --setenv CHROME_PATH /usr/bin/chromium --setenv LANG C.UTF-8 -- "$@"
