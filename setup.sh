#!/usr/bin/env bash
# One-time setup for Traversaal Video Studio. Safe to run again.
#   1. creates the `video` conda environment (Node, FFmpeg, Python) from environment.yml
#   2. downloads HyperFrames and its local voice once (about 27 MB), with a 2-second test
#   3. checks that Claude Code is installed
# Then start the app with ./start.sh
set -euo pipefail
cd "$(dirname "$0")"

say() { printf "\n\033[1m%s\033[0m\n" "$*"; }

say "1/3  Video environment"
if ! command -v conda >/dev/null 2>&1 && [ ! -x "$HOME/anaconda3/bin/conda" ] && [ ! -x "$HOME/miniconda3/bin/conda" ] && [ ! -x /opt/anaconda3/bin/conda ] && [ ! -x /opt/miniconda3/bin/conda ]; then
  echo "conda is not installed. Install Miniconda from https://docs.conda.io/en/latest/miniconda.html, then run ./setup.sh again."
  exit 1
fi
CONDA="$(command -v conda || ls "$HOME"/anaconda3/bin/conda "$HOME"/miniconda3/bin/conda /opt/anaconda3/bin/conda /opt/miniconda3/bin/conda 2>/dev/null | head -1)"
if "$CONDA" env list | awk '{print $1}' | grep -qx video; then
  echo "Environment 'video' already exists."
else
  "$CONDA" env create -f environment.yml
fi
render/env.sh ffmpeg -version | head -1

say "2/3  HyperFrames and the voice (first time downloads them)"
TMP="$(mktemp -d)"
render/env.sh npx --yes hyperframes@0.8.140 tts "Setup complete." -o "$TMP/test.wav" -v af_heart >/dev/null
render/env.sh ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/test.wav" | sed 's/^/Voice test OK, seconds: /'
rm -rf "$TMP"

say "3/3  Claude Code"
FOUND=""
for c in "${CLAUDE_BIN:-}" "$(command -v claude || true)" "$HOME/.claude/local/claude" "$HOME/.local/bin/claude"; do
  if [ -n "$c" ] && [ -x "$c" ]; then FOUND="$c"; break; fi
done
if [ -z "$FOUND" ]; then
  FOUND="$(ls -d "$HOME"/Library/Application\ Support/Claude/claude-code/*/*/claude.app/Contents/MacOS/claude 2>/dev/null | tail -1 || true)"
fi
if [ -n "$FOUND" ]; then
  "$FOUND" --version
  echo "If you have never used Claude Code on this computer, run it once in a terminal and sign in (a Claude Pro or Max plan is needed)."
else
  echo "Claude Code was not found. Install it from https://claude.com/claude-code, sign in once, then run ./setup.sh again."
  exit 1
fi

say "Done. Start the app with:  ./start.sh"
