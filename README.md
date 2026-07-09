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

## Results

See [`paper/paper.md`](paper/paper.md) (and the PDF built from it) for the full
academic write-up, and [`results/tables/`](results/tables/) for the data
tables. The exact hardware/software environment is auto-generated into
[`results/environment.md`](results/environment.md).

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
