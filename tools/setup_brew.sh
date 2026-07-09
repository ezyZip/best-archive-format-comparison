#!/bin/bash
# Install all Homebrew-available tools used by the benchmark.
# Formulae install without privileges; the wine-stable cask pulls in the
# gstreamer-runtime pkg which asks for an administrator password (sudo) -
# run this script interactively.
set -uo pipefail

FORMULAE=(
    # archivers / compressors under test
    sevenzip rar zstd xz lz4 brotli bzip2 bzip3 lzop lrzip lzip rzip
    zpaq dar gcab zopfli ncompress squashfs wimlib cdrtools
    # independent extractors used for round-trip verification
    unar lhasa cabextract
    # emulation for Windows/DOS-only archivers
    dosbox-x
    # reporting / paper toolchain
    pandoc parallel
)

echo "==> brew formulae"
brew install "${FORMULAE[@]}"

echo "==> wine (for Windows-only archivers: ACE, zipx, FreeArc, UHARC, KGB...)"
# Rosetta 2 is required to run x86 Windows binaries on Apple Silicon.
if [[ "$(uname -m)" == "arm64" ]] && ! /usr/bin/pgrep -q oahd; then
    softwareupdate --install-rosetta --agree-to-license || true
fi
# Official cask first (needs sudo for its gstreamer dependency); the
# sudo-free wine-crossover cask is an equivalent fallback.
brew install --cask wine-stable || \
    brew install --cask gcenx/wine/wine-crossover --no-quarantine

echo "==> done"
