#!/bin/bash
# Acquire the DOS-era archivers and stage them for DOSBox-X.
#
# DOSBox-X interprets x86 directly (no Wine/Rosetta PE translation), so it runs
# these decades-old DOS binaries reliably. PKZIP 2.04g (PKWARE, 1993) creates a
# standard .zip that modern Info-ZIP unzip reads back - the benchmark's
# "resurrected 1993 encoder" data point.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DL="$HERE/dos/downloads"
APPS="$HERE/dos/apps"
mkdir -p "$DL" "$APPS"

command -v dosbox-x >/dev/null || { echo "dosbox-x not found - run setup_brew.sh first"; exit 1; }

echo "==> PKZIP 2.04g (PKWARE, 1993)"
[[ -f "$DL/PKZ204G.EXE" ]] || \
    curl -fL -o "$DL/PKZ204G.EXE" "https://archive.org/download/PKZ204G_EXE/PKZ204G.EXE"
# PKZ204G.EXE is a PKSFX self-extracting ZIP; modern unzip opens it.
[[ -d "$DL/pkzip" ]] || { mkdir -p "$DL/pkzip" && (cd "$DL/pkzip" && unzip -o -q "../PKZ204G.EXE"); }
cp "$DL/pkzip/PKZIP.EXE" "$DL/pkzip/PKUNZIP.EXE" "$APPS/"

echo "==> staged DOS tools:"
ls -l "$APPS"
