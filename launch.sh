#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Original SBC app entrypoint, now launching FGF via its local catalog helper.
# Detaches immediately: does not require a terminal or Ctrl+C.
exec python3 "$DIR/studio_cues_alpha4/fgf_app_launcher.py" "$@"
