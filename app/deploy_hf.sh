#!/usr/bin/env bash
# Publish the committed repo to a Hugging Face Space (Docker), so anyone with the link can use
# the app in a browser. See app/README.md, "Put it online".
#
# Usage (from the repo root): HF_TOKEN=hf_... app/deploy_hf.sh <hf-user>/<space-name>
#
# A Space reads its settings from a header at the top of README.md. This script adds the header
# to the copy it pushes, so the README on GitHub stays as it is. Only committed files are pushed
# (never .env or runs/*/audio).
set -euo pipefail

SPACE="${1:?usage: HF_TOKEN=hf_... app/deploy_hf.sh <hf-user>/<space-name>}"
: "${HF_TOKEN:?set HF_TOKEN to a Hugging Face access token with write permission}"
cd "$(dirname "$0")/.."
REV="$(git rev-parse --short HEAD)"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git archive HEAD | tar -x -C "$TMP"
{
  printf -- '---\ntitle: Traversaal Video Agent\nemoji: 🎬\ncolorFrom: blue\ncolorTo: indigo\n'
  printf -- 'sdk: docker\napp_port: 7860\npinned: false\n---\n\n'
  cat README.md
} > "$TMP/README.md"

cd "$TMP"
git init -q -b main
git add -A
git -c user.name="deploy" -c user.email="deploy@localhost" commit -qm "Deploy $REV"
git push --force "https://user:${HF_TOKEN}@huggingface.co/spaces/${SPACE}" main
echo "Pushed $REV. The Space now builds (about 10-15 minutes): https://huggingface.co/spaces/${SPACE}"
