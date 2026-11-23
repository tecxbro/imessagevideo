#!/bin/bash
set -euo pipefail
export CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
stage='/tmp/imv-native-analysis/build'
previews='director/motion-catalog/previews'
mkdir -p "$stage"
id="$1"
slug="$2"
shift 2
node director/cli.mjs scene --motion "$id" "$@" --out "$stage/$slug.json"
node scripts/engines/render.mjs --method html --scene "$stage/$slug.json" --out "$stage/$slug.mp4"
cp "$stage/$slug.mp4" "$previews/$slug.mp4"
