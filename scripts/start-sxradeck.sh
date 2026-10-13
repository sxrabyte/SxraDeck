#!/usr/bin/env bash
# Launch the SxraDeck TUI. Resolves the repo + its virtualenv relative to this
# script, so it works regardless of where the deck is cloned.
#
# This is the *inner* command - it expects to already be running inside a
# terminal emulator that reports xterm-style mouse (so touch arrives as taps).
# See scripts/sxradeck.service and docs/TOUCH-SETUP.md for how that terminal
# gets started on the Waveshare panel at boot.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -x "$REPO/.venv/bin/python" ]]; then
    PY="$REPO/.venv/bin/python"
else
    PY="$(command -v python3)"
fi

# Textual reads mouse via the terminal; make sure a mouse-capable TERM is set.
export TERM="${TERM:-xterm-256color}"

cd "$REPO"
exec "$PY" -m sxradeck.ui.app
