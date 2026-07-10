# The Ultimate Archive Format Comparison

**Which archive format actually produces the smallest file for a typical user's
folder — across every archive format we could obtain, from 1985's ARC to
today's Zstandard?**

This repository benchmarks **every obtainable archive/compression format** on a
realistic ~50 MB "home folder" corpus (text, office documents, images, video):

- **Common:** zip, 7z, rar, tar.gz
- **Modern:** zstd, brotli, xz, lz4, bzip3, lrzip, zpaq
- **Vintage:** zoo, ARC, ARJ, LHA, .Z (compress), HA
- **macOS-native:** Apple Archive (.aar), compressed DMG, xar
- **Imaging/container:** SquashFS, WIM, ISO, cab, dar
- **Resurrected via Wine/DOSBox:** ACE (WinACE), UHARC, KGB, FreeArc,
  EGG/ALZ (ALZip), StuffIt, zipx (WinZip), SQX

Every archive is **round-trip verified** (extracted and SHA-256-compared
against the original files), timings are taken on an otherwise idle machine,
and all raw results are committed as JSON so every number in the paper is
auditable.

## Headline results

On the full 55 MB mixed corpus (a realistic home folder), tested at each tool's
default and maximum settings:

| Need | Format | Full-corpus size | vs. ZIP |
|---|---|---:|---|
| Universal compatibility | **ZIP** | 82% | baseline |
| Best size/speed balance | **7-Zip** (`.7z`), max | **60%** in ~4 s | ~27% smaller |
| Best size/speed balance | **Zstandard** (`.tar.zst`), max | 61% | ~25% smaller |
| Absolute smallest | **zpaq**, max | **56%** in ~150 s | ~32% smaller |

Other findings:

- **Office documents barely compress with ZIP** (99%, since `.docx`/`.xlsx` are
  already ZIPs internally) but **7-Zip recompresses them to 60%**.
- **Photos and video are near-incompressible** for every format (~98–100%);
  archiving them is about bundling, not size.
- **A 1993 PKZIP binary**, run under DOS emulation, still makes a `.zip` modern
  `unzip` opens — and its 35.5% on text is nearly identical to today's ZIP.
- **Some 2000s Windows-only archivers no longer run** to completion on Apple
  Silicon even under Wine (FreeArc, UHARC deadlock); a 40-year-old open DOS
  format proved more durable than a 20-year-old proprietary Windows one.

See [`paper/paper.md`](paper/paper.md) (and [`paper/paper.pdf`](paper/paper.pdf))
for the full academic write-up, [`results/tables/results.md`](results/tables/results.md)
for every ranking, [`results/tables/results.csv`](results/tables/results.csv)
for the raw data, and [`results/environment.md`](results/environment.md) for the
exact hardware/software environment (auto-generated).

## Create these archives online

The formats this study recommends can all be created in the browser with
[ezyZip](https://www.ezyzip.com) (the study's sponsor — see the paper's
funding disclosure), no software install required:

- **ZIP** — [zip-files-online](https://www.ezyzip.com/zip-files-online.html)
- **7Z** — [create-7z-file-online](https://www.ezyzip.com/create-7z-file-online.html)
- **TAR.ZST** — [create-tar-zst-file-online](https://www.ezyzip.com/create-tar-zst-file-online.html)

## Extract any of these formats online

All of the file types benchmarked here — including the ancient ones (ARC,
ARJ, LHA, zoo, .Z, …) — can be extracted in the browser with ezyZip's
extractor: [unzip-files-online](https://www.ezyzip.com/unzip-files-online.html).

## Reproduce it yourself

```sh
git clone <this repo>
cd best-archive-format-comparison
./run_all.sh            # setup checks → corpus verify → benchmark → reports → paper
./run_all.sh --quick    # fast smoke test (1 timing run, text dataset only)
```

Requirements: macOS (Apple Silicon tested), [Homebrew](https://brew.sh),
Python 3.11+, and — for the resurrected Windows/DOS formats — Wine and
DOSBox-X (installed by `tools/setup_brew.sh`). Some vintage tools are built
from source by `tools/setup_source_builds.sh`; Windows-only tools are
downloaded (URLs + SHA-256 recorded in [`tools/README.md`](tools/README.md))
and run under Wine by `tools/setup_wine.sh`.

## Repository layout

| Path | Contents |
|---|---|
| `corpus/` | The committed test corpus + `MANIFEST.sha256` + per-file provenance (`SOURCES.md`) |
| `harness/` | Python benchmark harness; `formats.yaml` is the declarative format registry |
| `tools/` | Setup scripts for brew/source/Wine/DOSBox tool acquisition |
| `results/raw/` | Committed raw JSON — one file per (dataset, format, level) run |
| `results/tables/` | Generated Markdown/CSV result tables |
| `paper/` | The academic paper (pandoc Markdown → PDF) with references |

## Methodology in one paragraph

Each format is tested at its tool's **default settings** and at its **maximum
compression level** — the only dial we allow is the level switch a casual user
could flip; no method/dictionary tuning. Single-stream compressors (gzip, xz,
zstd, …) and tools that cannot store directory trees compress a canonical,
deterministic tar of the corpus. Compression and decompression wall-times are
the median of 3 runs (1 for very slow tools), captured sequentially on an
unloaded machine. Tools running under Wine/DOSBox emulation are flagged: their
archive **sizes** are fully comparable; their timings are footnoted or
excluded. See the paper's Methodology section for full detail.

## Full results: every format, ranked best to worst

The complete ranking on the full 55.07 MB corpus. Ratio = archive size ÷ input
size (lower is better); Compress/Decompress are wall-times in seconds. Rows
marked (emu) ran under emulation (Wine/DOSBox); their **sizes** are comparable
but their **timings are excluded** (shown as —). Copied from
[`results/tables/results.md`](results/tables/results.md), which also has the
per-category rankings (text, documents, images, video) and the list of
attempted-but-not-completed formats (FreeArc, UHARC, shar).

| Rank | Format | Level | Size | Ratio | Compress | Decompress | Notes |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | zpaq (journaling PAQ-family) | max | 30.90 MB | 56.11% | 144.4 | 149.9 |  |
| 2 | tar.rz (rzip) | max | 32.95 MB | 59.82% | 4.65 | 0.97 |  |
| 3 | tar.rz (rzip) | default | 32.95 MB | 59.83% | 3.64 | 0.99 |  |
| 4 | 7z (7-Zip, LZMA2) | max | 33.02 MB | 59.96% | 4.43 | 0.43 |  |
| 5 | tar.xz (xz/LZMA2) | max | 33.03 MB | 59.98% | 13.5 | 0.60 |  |
| 6 | 7z (7-Zip, LZMA2) | default | 33.03 MB | 59.98% | 4.13 | 0.42 |  |
| 7 | tar.lz (lzip) | max | 33.21 MB | 60.31% | 16.7 | 2.28 |  |
| 8 | tar.lrz (lrzip) | max | 33.27 MB | 60.41% | 3.13 | 0.60 |  |
| 9 | tar.lrz (lrzip) | default | 33.27 MB | 60.42% | 3.05 | 0.60 |  |
| 10 | tar.zst (Zstandard) | max | 33.78 MB | 61.33% | 6.82 | 0.05 |  |
| 11 | tar.br (Brotli) | default | 35.80 MB | 65.00% | 84.0 | 0.23 |  |
| 12 | tar.bz3 (bzip3) | max | 36.74 MB | 66.72% | 7.46 | 6.87 |  |
| 13 | tar.bz3 (bzip3) | default | 38.24 MB | 69.43% | 7.16 | 5.79 |  |
| 14 | zpaq (journaling PAQ-family) | default | 39.90 MB | 72.46% | 0.72 | 1.84 |  |
| 15 | tar.xz (xz/LZMA2) | default | 40.21 MB | 73.02% | 6.73 | 0.35 |  |
| 16 | tar.lz (lzip) | default | 40.45 MB | 73.46% | 15.0 | 2.73 |  |
| 17 | RAR 4 (legacy format) | max | 42.38 MB | 76.96% | 0.90 | 0.41 |  |
| 18 | RAR 4 (legacy format) | default | 42.43 MB | 77.05% | 0.81 | 0.40 |  |
| 19 | tar.bz2 (bzip2) | default | 42.92 MB | 77.93% | 3.84 | 1.76 |  |
| 20 | RAR 5 (WinRAR/rar) | max | 43.01 MB | 78.09% | 1.02 | 0.20 |  |
| 21 | RAR 5 (WinRAR/rar) | default | 43.08 MB | 78.22% | 0.81 | 0.21 |  |
| 22 | DMG (ULMO, lzma-compressed image) | default | 43.97 MB | 79.83% | 11.1 | 0.84 |  |
| 23 | tar.gz (zopfli, exhaustive deflate) | default | 44.56 MB | 80.91% | 59.7 | 0.13 |  |
| 24 | LHA/LZH (1988, lh5) | max | 44.82 MB | 81.39% | 3.87 | 0.89 |  |
| 25 | ZIP (PKZIP 2.04g, 1993) (emu) | max | 44.97 MB | 81.66% | — | — | emulated (size only) |
| 26 | WIM (wimlib, LZX) | max | 45.04 MB | 81.78% | 0.40 | 0.14 |  |
| 27 | WIM (wimlib, LZX) | default | 45.06 MB | 81.83% | 0.29 | 0.15 |  |
| 28 | ZIP (PKZIP 2.04g, 1993) (emu) | default | 45.07 MB | 81.84% | — | — | emulated (size only) |
| 29 | ZIP (Info-ZIP) | max | 45.09 MB | 81.87% | 1.50 | 0.32 |  |
| 30 | dar (Disk ARchive) | default | 45.11 MB | 81.92% | 1.73 | 0.30 |  |
| 31 | xar (macOS eXtensible ARchiver) | default | 45.11 MB | 81.92% | 1.53 | 0.12 |  |
| 32 | ZIP (Info-ZIP) | default | 45.12 MB | 81.92% | 1.35 | 0.33 |  |
| 33 | tar.gz (gzip) | max | 45.12 MB | 81.92% | 1.50 | 0.10 |  |
| 34 | tar.gz (gzip) | default | 45.14 MB | 81.97% | 1.34 | 0.09 |  |
| 35 | ARJ (1991) | max | 45.20 MB | 82.07% | 1.09 | 0.63 |  |
| 36 | ARJ (1991) | default | 45.20 MB | 82.08% | 1.05 | 0.65 |  |
| 37 | SquashFS (mksquashfs) | default | 45.25 MB | 82.16% | 0.20 | 0.04 |  |
| 38 | tar.zst (Zstandard) | default | 45.40 MB | 82.44% | 0.08 | 0.05 |  |
| 39 | Apple Archive (.aar, lzfse) | default | 45.46 MB | 82.54% | 0.09 | 0.06 |  |
| 40 | LHA/LZH (1988, lh5) | default | 45.53 MB | 82.67% | 2.29 | 1.04 |  |
| 41 | zoo (1986) | max | 45.62 MB | 82.83% | 2.83 | 1.83 |  |
| 42 | CAB (gcab, MSZIP) | default | 45.68 MB | 82.95% | 0.96 | 0.16 |  |
| 43 | HA (1993, PPM-family) | default | 45.74 MB | 83.06% | 4.22 | 3.77 |  |
| 44 | freeze (1993) | default | 45.75 MB | 83.07% | 4.12 | 3.05 |  |
| 45 | DMG (UDZO, zlib-compressed image) | max | 46.09 MB | 83.69% | 6.07 | 0.32 |  |
| 46 | tar.lzo (lzop) | max | 46.50 MB | 84.44% | 3.75 | 0.07 |  |
| 47 | tar.lz4 (LZ4) | max | 46.51 MB | 84.45% | 0.39 | 0.05 |  |
| 48 | DMG (UDZO, zlib-compressed image) | default | 46.79 MB | 84.96% | 6.08 | 0.35 |  |
| 49 | tar.lz4 (LZ4) | default | 49.50 MB | 89.88% | 0.03 | 0.03 |  |
| 50 | tar.lzo (lzop) | default | 49.53 MB | 89.94% | 0.09 | 0.08 |  |
| 51 | cpio (appendix: store-only) | default | 55.07 MB | 100.00% | 0.26 | 0.06 |  |
| 52 | tar (uncompressed, baseline) | default | 55.09 MB | 100.03% | 0.06 | 0.05 |  |
| 53 | ar (appendix: unix archiver, store-only) | default | 55.10 MB | 100.05% | 0.17 | 0.08 |  |
| 54 | pax (appendix: POSIX archiver) | default | 55.10 MB | 100.05% | 0.10 | 0.10 |  |
| 55 | zoo (1986) | default | 55.10 MB | 100.05% | 2.65 | 0.18 |  |
| 56 | ISO 9660 (mkisofs, store-only) | default | 55.46 MB | 100.70% | 0.03 | 0.03 |  |
| 57 | tar.Z (compress, LZW 1984) | default | 58.36 MB | 105.97% | 1.05 | 0.47 |  |
| 58 | ARC (SEA, 1985) | default | 62.29 MB | 113.11% | 1.33 | 0.26 |  |

paq8px does not appear in this table because it was measured on the text
category only (17.76%, the smallest result in the study); the full mixed corpus
exceeds its practical runtime. See the per-category tables in
[`results/tables/results.md`](results/tables/results.md) for its entry.
