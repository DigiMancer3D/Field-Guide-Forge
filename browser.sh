#!/usr/bin/env bash
set -euo pipefail
URL="${1:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/index.html}"
# FGF_BROWSER can be set to a full executable path or a command on PATH.
if [[ -n "${FGF_BROWSER:-}" ]]; then exec "$FGF_BROWSER" --new-window "$URL"; fi
if command -v librewolf >/dev/null 2>&1; then exec librewolf --new-window "$URL"; fi
if command -v flatpak >/dev/null 2>&1 && flatpak info io.gitlab.librewolf-community >/dev/null 2>&1; then
  exec flatpak run io.gitlab.librewolf-community --new-window "$URL"
fi
# Direct Firefox / Chromium fallback, unlike xdg-open which follows the OS default.
if command -v firefox >/dev/null 2>&1; then exec firefox --new-window "$URL"; fi
if command -v chromium >/dev/null 2>&1; then exec chromium --new-window "$URL"; fi
if command -v xdg-open >/dev/null 2>&1; then exec xdg-open "$URL"; fi
printf 'No compatible browser found. Open %s manually.\n' "$URL" >&2
exit 1
