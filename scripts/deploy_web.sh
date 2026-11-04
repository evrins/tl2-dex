#!/usr/bin/env bash
# Build the static site and deploy it to Cloudflare Workers.
#
#   npx wrangler login      # once
#   scripts/deploy_web.sh   # package + upload
#
# `wrangler.jsonc` names the upload directory (`.nsh/out/TIDBI`) and no Worker
# script: every request is a static asset. `deploy/_headers` is copied beside
# them, because `nsh package` rewrites the output directory.
set -euo pipefail
cd "$(dirname "$0")/.."

nsh package --target web
cp deploy/_headers .nsh/out/TIDBI/_headers
exec npx --yes wrangler@latest deploy
