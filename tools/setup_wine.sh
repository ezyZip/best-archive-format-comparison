#!/bin/bash
# Acquire the Windows-only archivers and run them under Wine.
#
# On Apple Silicon this requires Rosetta 2 (installed by setup_brew.sh) to
# translate x86 Windows binaries. NOTE: on this stack (Wine 11 + Rosetta 2)
# the heavy Win32 compressors deadlock in their compression cores - see
# tools/README.md. They are included in the benchmark as *attempted* formats
# and recorded as timeouts; this script still downloads them so the attempt
# is reproducible.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DL="$HERE/wine/downloads"
PREFIX="$HERE/wine/prefix"
mkdir -p "$DL" "$PREFIX"

export WINEPREFIX="$PREFIX"
export WINEDEBUG=-all

# One-time: Gatekeeper quarantine must be cleared for the unsigned Wine app,
# and the prefix bootstrapped.
if [[ -d "/Applications/Wine Stable.app" ]]; then
    xattr -dr com.apple.quarantine "/Applications/Wine Stable.app" 2>/dev/null || true
fi
command -v wine >/dev/null || { echo "wine not found - run setup_brew.sh first"; exit 1; }
wineboot --init >/dev/null 2>&1 || true

fetch() {  # url  dest
    [[ -f "$2" ]] || curl -fL -A "Mozilla/5.0" -o "$2" "$1"
}

echo "==> FreeArc 0.666 (console)"
fetch "https://archive.org/download/FreeArc-0.666-win32bin-Sources/FreeArc-portable-0.666-win32.zip" \
      "$DL/freearc-portable.zip"
[[ -d "$DL/freearc" ]] || unzip -o -q "$DL/freearc-portable.zip" -d "$DL/freearc"

echo "==> UHARC 0.6b"
fetch "https://archive.org/download/uharc06b/uharc06b.zip" "$DL/uharc06b.zip"
[[ -d "$DL/uharc" ]] || unzip -o -q "$DL/uharc06b.zip" -d "$DL/uharc"

echo "==> WinACE 2.69 (for reference / independent-extraction cross-check only)"
fetch "https://archive.org/download/winace_winace_2.65_anglais_9748/winace_winace_2.69.exe" \
      "$DL/winace269.exe"

cat <<'NOTE'

Downloaded. Checksums are recorded in tools/README.md.
Reminder: FreeArc and UHARC deadlock under Wine 11 + Rosetta 2 on Apple
Silicon and will show up in results as timeouts (a documented finding).
ACE creation is GUI-only; ACE archives are read back with acefile.py.
NOTE
