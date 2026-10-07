#!/usr/bin/env bash
# Run a command inside the `video` conda env (Node, FFmpeg, Python + Kokoro TTS).
# Usage: tools/env.sh <command> [args...]
#   e.g. tools/env.sh npx hyperframes check runs/my-video/scenes/s01
# Works even when the calling shell has not activated conda (e.g. the Claude desktop app).
set -euo pipefail

ENV_NAME="${VIDEO_ENV:-video}"

find_conda() {
  if [ -n "${CONDA_EXE:-}" ] && [ -x "$CONDA_EXE" ]; then echo "$CONDA_EXE"; return; fi
  if command -v conda >/dev/null 2>&1; then command -v conda; return; fi
  for base in "$HOME/anaconda3" "$HOME/miniconda3" "$HOME/miniforge3" "$HOME/mambaforge" \
              /opt/anaconda3 /opt/miniconda3 /opt/miniforge3 \
              /opt/homebrew/anaconda3 /opt/homebrew/Caskroom/miniconda/base /usr/local/anaconda3; do
    if [ -x "$base/bin/conda" ]; then echo "$base/bin/conda"; return; fi
  done
  echo "conda not found; install Miniconda or set CONDA_EXE" >&2
  exit 1
}

CONDA="$(find_conda)"
PREFIX="$("$CONDA" env list | awk -v n="$ENV_NAME" '$1 == n { print $NF }')"
if [ -z "$PREFIX" ]; then
  echo "conda env '$ENV_NAME' not found; create it with: conda env create -f environment.yml" >&2
  exit 1
fi

export PATH="$PREFIX/bin:$PATH"
export HYPERFRAMES_PYTHON="$PREFIX/bin/python"
exec "$@"
