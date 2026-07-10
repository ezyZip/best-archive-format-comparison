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
