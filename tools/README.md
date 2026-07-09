# Tool acquisition

Every archiver in the benchmark, and exactly how it is obtained. Three setup
scripts install them; run them in order (each is idempotent):

```sh
./setup_brew.sh            # Homebrew formulae + Wine + DOSBox-X
./setup_source_builds.sh   # vintage/experimental archivers, built from source
./setup_wine.sh            # Windows-only archivers under Wine
```

Built binaries land in `tools/bin/` (the harness prepends it to `PATH`).
Downloaded Windows tools land in `tools/wine/downloads/`. Both directories are
git-ignored; this file is the provenance record.

## Tier A — Homebrew / macOS-bundled

Installed by `setup_brew.sh` or already present in macOS. See
`results/environment.md` (generated) for the exact version of every tool as
run. Formulae: `sevenzip rar zstd xz lz4 brotli bzip2 bzip3 lzop lrzip lzip
rzip zpaq dar gcab zopfli ncompress squashfs wimlib cdrtools unar lhasa
cabextract`. macOS-bundled: `zip/unzip, tar/bsdtar, gzip, compress, cpio, ar,
pax, shar, aa (Apple Archive), xar, hdiutil, ditto, mkisofs`.

## Tier B — built from source (`setup_source_builds.sh`)

These have no Homebrew package and are compiled from upstream sources, with
patches (in `tools/patches/`) where modern clang / 64-bit ARM requires them.
All verified to build and round-trip on macOS arm64 (Apple Silicon), Apple
clang 21, July 2026.

| Tool | Format era | Source | Patch (why) |
|---|---|---|---|
| ARC 5.21p | ARC, 1985 | `github.com/hyc/arc` | build flags only (`-DBSD`, K&R-tolerant) |
| LHa (jca02266) | LZH, 1988 | `github.com/jca02266/lha` | none (clean autotools build) |
| zoo 2.10 | zoo, 1986 | `archive.debian.org/.../zoo_2.10.orig.tar.gz` + Debian `zoo_2.10-21.diff.gz` | `zoo-macos-arm64.patch` (BSD block → STDARG; stale `/usr/include` deps) |
| ARJ 3.10.22 | ARJ, 1991 | `deb.debian.org/.../arj_3.10.22.orig.tar.gz` + Debian `arj_3.10.22-26.debian.tar.xz` | `arj-macos.patch` (`<sys/statfs.h>` → macOS `statvfs`) |
| HA 0.999 | HA, 1993 | `github.com/l-4-l/ha` | `ha-lp64-types.patch` (`U32B`/`S32B` `long`→`int` on LP64) |
| freeze 2.5.0 | freeze, 1993 | `ibiblio.org/pub/linux/utils/compress/freeze-2.5.0.tar.gz` | `freeze-modern-libc.patch` (drop SysV `_cnt`/`_ptr` stdio macros) |
| paq8px v216 | context-mixing, current | `github.com/hxim/paq8px` | `paq8px-clang-arm64.patch` (drop GCC-only flags; disambiguate `min()`) |

## Tier C — Windows tools under Wine (`setup_wine.sh`)

Downloaded from the Internet Archive / original vendors and run under Wine
(`wine-stable`, Wine 11) with Rosetta 2 for x86 translation. **Archive sizes
produced under emulation are directly comparable; timings are not** (see the
paper's methodology) and are excluded or footnoted.

| Tool | Format | Download URL | SHA-256 | Notes |
|---|---|---|---|---|
| FreeArc 0.666 (console `Arc.exe`) | FreeArc `.arc` | `archive.org/download/FreeArc-0.666-win32bin-Sources/FreeArc-portable-0.666-win32.zip` | `2abc7be9603efbc797f1f44ab3cc50304fff7062e41aab10e833ff953375fb79` | see emulation status below |
| UHARC 0.6b (`UHARC.EXE`) | UHARC `.uha` | `archive.org/download/uharc06b/uharc06b.zip` | `6312b7468cb85f1afdba31b077f88522c8ac2df433322ab6c201d5a0e48008b6` | see emulation status below |
| WinACE 2.69 | ACE `.ace` | `archive.org/download/winace_winace_2.65_anglais_9748/winace_winace_2.69.exe` | `426b19f26c03dfc5db649f980b77dfbdb0aed7623dd0451418cdcc6c535eb696` | GUI installer (ACE SFX); ACE creation is GUI-only. Extraction verified independently with `acefile.py` (pure-Python). |

### Emulation status (empirical, this machine)

On Apple Silicon + Wine 11 + Rosetta 2, the heavy Win32 compressors
**deadlock in their compression cores** under x86→ARM binary translation —
they start, print their banner, begin compressing, and hang. This was observed
identically for **UHARC** (hangs after "Adding file"), **FreeArc** (hangs after
its version banner, single- or multi-threaded), and the **WinACE** self-
extracting installer (GUI, no silent path). These are recorded by the harness
as `timeout` and discussed as a *format-longevity finding* in the paper
(§Limitations / §Discussion): a 2007-era Win32 archiver is not reliably
runnable on a 2026 ARM Mac even under emulation. Where an independent
*extractor* exists (ACE via `acefile.py`; ALZ/EGG via the bundled wasm
`unalz`/`unegg`; many formats via `unar`), format read-back is still verified.

## Documented exclusions

Formats attempted but not creatable on this platform, with the reason:

| Format | Tool | Why excluded from creation |
|---|---|---|
| ACE | WinACE | Creation is GUI-only; the console DOS ACE binary is not redistributable/locatable. Extraction verified via `acefile.py`. |
| UHARC | UHARC.EXE | Compression core deadlocks under Wine/Rosetta (above). No DOS build exists. |
| FreeArc | Arc.exe | Compression core deadlocks under Wine/Rosetta (above). |
| KGB | KGB Archiver | PAQ-based Win32 tool; same deadlock class as UHARC, and no independent extractor. |
| EGG / ALZ | ALZip | ESTsoft ALZip is GUI-only (no CLI / silent-create path). Extraction verifiable via `unalz`/`unegg`. |
| StuffIt `.sitx` | StuffIt for Windows | GUI-only; extraction verifiable via `unar`. |
| SQX | Squeez | Vendor defunct; no obtainable console creator. |
| WinRK, CMIX | — | Activation-locked/defunct (WinRK); infeasible RAM/time (CMIX — cited from Mahoney's LTCB instead). |
| Compact Pro, DiskDoubler | — | Classic Mac OS only; no creator runs on modern macOS. `unar` can still *extract* `.cpt` (a format-longevity anecdote). |
