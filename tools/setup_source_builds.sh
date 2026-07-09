#!/bin/bash
# Build the vintage/experimental archivers that have no Homebrew package.
# Sources are fetched from the canonical locations recorded in tools/README.md,
# patched where modern clang/arm64 requires it (patches in tools/patches/),
# and installed into tools/bin/ (which the harness prepends to PATH).
#
# Verified on macOS arm64 (Apple Silicon), clang 21, 2026-07.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/src"
BIN="$HERE/bin"
PATCHES="$HERE/patches"
mkdir -p "$SRC" "$BIN"
cd "$SRC"

KNR_FLAGS="-O2 -std=gnu89 -Wno-implicit-int -Wno-implicit-function-declaration \
-Wno-deprecated-non-prototype -Wno-return-type -Wno-parentheses \
-Wno-incompatible-function-pointer-types"

# --- ARC 5.21p (SEA, 1985) --------------------------------------------------
if [[ ! -x "$BIN/arc" ]]; then
    echo "==> ARC (SEA)"
    [[ -d arc ]] || git clone -q --depth 1 https://github.com/hyc/arc.git
    (cd arc && make clean >/dev/null 2>&1 || true
     make SYSTEM="-DBSD=1" OPT="$KNR_FLAGS" arc)
    cp arc/arc "$BIN/"
fi

# --- LHA (jca02266 fork of LHa for UNIX, format of 1988) ---------------------
if [[ ! -x "$BIN/lha" ]]; then
    echo "==> LHA"
    [[ -d lha ]] || git clone -q --depth 1 https://github.com/jca02266/lha.git
    (cd lha && autoreconf -i >/dev/null 2>&1 && ./configure -q && make -s)
    cp lha/src/lha "$BIN/"
fi

# --- zoo 2.10 (1986) ---------------------------------------------------------
if [[ ! -x "$BIN/zoo" ]]; then
    echo "==> zoo"
    if [[ ! -d zoo/zoo-2.10.orig ]]; then
        mkdir -p zoo && cd zoo
        curl -sfLo zoo.tar.gz "http://archive.debian.org/debian/pool/main/z/zoo/zoo_2.10.orig.tar.gz"
        curl -sfLo zoo.diff.gz "http://archive.debian.org/debian/pool/main/z/zoo/zoo_2.10-21.diff.gz"
        tar xzf zoo.tar.gz
        gunzip -c zoo.diff.gz | patch -s -p1 -d . || true   # unpacks debian/ dir
        cd zoo-2.10.orig
        for p in ../debian/patches/*.patch; do patch -s -p1 < "$p"; done
        patch -s -p1 < "$PATCHES/zoo-macos-arm64.patch"
        # strip stale makedepend paths that no longer exist on macOS
        sed -i.bak 's|/usr/include/[a-z/.]*||g' makefile
        cd "$SRC"
    fi
    (cd zoo/zoo-2.10.orig &&
     make CFLAGS="-c $KNR_FLAGS -DBSD4_3 -DLONG64 -DANSI_HDRS" zoo)
    cp zoo/zoo-2.10.orig/zoo "$BIN/"
fi

# --- ARJ 3.10.22 (format of 1991) --------------------------------------------
if [[ ! -x "$BIN/arj" ]]; then
    echo "==> ARJ"
    if [[ ! -d arj ]]; then
        mkdir -p arj && cd arj
        curl -sfLo arj.tar.gz "https://deb.debian.org/debian/pool/main/a/arj/arj_3.10.22.orig.tar.gz"
        curl -sfLo arj-debian.tar.xz "https://deb.debian.org/debian/pool/main/a/arj/arj_3.10.22-26.debian.tar.xz"
        tar xzf arj.tar.gz --strip-components=1
        mkdir -p debian-patches && tar xf arj-debian.tar.xz -C debian-patches
        for p in $(cat debian-patches/debian/patches/series); do
            patch -s -p1 < "debian-patches/debian/patches/$p"
        done
        patch -s -p1 < "$PATCHES/arj-macos.patch"
        cp /opt/homebrew/share/automake-*/config.sub gnu/
        cp /opt/homebrew/share/automake-*/config.guess gnu/
        cd "$SRC"
    fi
    (cd arj/gnu && autoreconf -i >/dev/null 2>&1 && ./configure -q)
    (cd arj && make prepare >/dev/null 2>&1 || true; make >/dev/null 2>&1 || true)
    cp arj/darwin*/en/rs/arj/arj "$BIN/"   # rearj postproc fails; arj itself links fine

fi

# --- HA 0.999 (1993, PPM-family) ----------------------------------------------
if [[ ! -x "$BIN/ha" ]]; then
    echo "==> HA"
    if [[ ! -d ha ]]; then
        git clone -q --depth 1 https://github.com/l-4-l/ha.git
        # On LP64 (64-bit) targets HA's U32B/S32B typedef to `long` (8 bytes),
        # tripping its runtime size check; the patch pins them to int (4 bytes).
        (cd ha && patch -s -p1 < "$PATCHES/ha-lp64-types.patch")
    fi
    (cd ha && cc $KNR_FLAGS -o ha \
        acoder.c archive.c asc.c cpy.c error.c ha.c haio.c hsc.c info.c \
        machine.c misc.c swdict.c)
    cp ha/ha "$BIN/"
fi

# --- freeze 2.5.0 (1993) -------------------------------------------------------
if [[ ! -x "$BIN/freeze" ]]; then
    echo "==> freeze"
    if [[ ! -d freeze ]]; then
        mkdir -p freeze
        curl -sfLo freeze.tar.gz "https://www.ibiblio.org/pub/linux/utils/compress/freeze-2.5.0.tar.gz"
        tar xzf freeze.tar.gz -C freeze
        (cd freeze && patch -s -p1 < "$PATCHES/freeze-modern-libc.patch")
    fi
    (cd freeze && ./configure -q >/dev/null && make CFLAGS="$KNR_FLAGS" freeze)
    cp freeze/freeze "$BIN/"
fi

# --- paq8px v216 (context mixing) ----------------------------------------------
if [[ ! -x "$BIN/paq8px" ]]; then
    echo "==> paq8px"
    if [[ ! -d paq8px ]]; then
        git clone -q --depth 1 https://github.com/hxim/paq8px.git
        (cd paq8px && patch -s -p1 < "$PATCHES/paq8px-clang-arm64.patch")
    fi
    (cd paq8px && mkdir -p build && cd build &&
     cmake -DCMAKE_BUILD_TYPE=Release .. >/dev/null && make -j"$(sysctl -n hw.ncpu)" -s)
    cp paq8px/build/paq8px "$BIN/"
fi

echo "==> installed:"
ls -l "$BIN"
