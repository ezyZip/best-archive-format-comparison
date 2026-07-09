# Introduction

Compressing a folder of files is one of the most common things a computer user
ever does, and yet the choice of *how* to do it has never been more confusing.
The graphical "compress" command on Windows and macOS produces a ZIP file whose
core algorithm, DEFLATE, was standardized in 1996 [@rfc1951] and whose lineage
runs back to the Lempel–Ziv work of 1977 [@ziv1977]. Meanwhile, a casual user
who looks a little further finds 7-Zip, RAR, and a growing list of modern
codecs—Zstandard [@rfc8878], Brotli [@rfc7932], and others—each promising
smaller files, faster operation, or both. Beyond these lies a long tail of
formats that were once dominant and are now curiosities: ARC, ARJ, LHA, zoo,
and the venerable Unix `compress`.

The practical question this paper answers is deliberately narrow: **for a
typical person compressing a typical folder, which format produces the smallest
file while remaining practical to create and to open?** "Practical" is the
operative word. We restrict every tool to settings a non-expert could plausibly
use—its out-of-the-box defaults, and the single "maximum compression" dial that
most archivers expose—and we deliberately avoid the method- and
dictionary-tuning that dominates specialist compression benchmarks. Where prior
public benchmarks such as the Squash Compression Benchmark [@squash_benchmark],
lzbench [@lzbench], and Matt Mahoney's Large Text Compression Benchmark
[@mahoney_ltcb] measure *codecs* on standardized corpora like Silesia
[@silesia], we measure *end-user archive formats*—complete with their container
overhead, their real command-line tools, and their round-trip integrity—on a
realistic mixed corpus that resembles a home user's folder.

Our contribution is threefold:

1. **Breadth.** We benchmark **42 archive and compression formats** in a single,
   uniform harness, spanning four decades: from 1984's Unix `compress` (.Z)
   [@welch1984] and 1985's ARC [@arc_format] to today's context-mixing paq8px
   [@paq8px]. The set includes mainstream formats (ZIP, 7z, RAR, gzip), modern
   codecs (Zstandard, Brotli, xz, LZ4, bzip3, lrzip, zpaq), vintage formats
   (ARC, ARJ, LHA, zoo, HA, freeze, compress), macOS-native formats (Apple
   Archive, compressed DMG, xar), filesystem/imaging containers (SquashFS, WIM,
   ISO, cab, dar), and formats we resurrect under emulation—most notably PKZIP
   2.04g (1993) run under DOSBox.

2. **Rigor and reproducibility.** Every archive is round-trip verified: it is
   extracted—often with an *independent* implementation—and compared byte-for-
   byte against the original via SHA-256. The entire study runs from a single
   command on committed, public-domain inputs, and every raw measurement is
   committed as machine-readable JSON so that each number in this paper is
   auditable and re-derivable.

3. **A longevity finding.** In the course of the study we document an empirical
   result about format longevity: several Windows-only archivers can no longer
   be run to completion on a current Apple Silicon Mac, even under the Wine
   compatibility layer, because they deadlock in their compression cores under
   x86-to-ARM binary translation.

# Related work

**Codec benchmarks.** The most rigorous public compression comparisons focus on
raw codecs. The Squash Compression Benchmark [@squash_benchmark] wraps dozens of
compression libraries behind a single abstraction layer and measures them across
machines and datasets; lzbench [@lzbench] does likewise in-memory for the
LZ-family. Mahoney's Large Text Compression Benchmark [@mahoney_ltcb] and the
associated PAQ line of work [@mahoney2000] chart the extreme frontier of ratio
on a single large text file. These efforts are authoritative for *algorithm*
selection but deliberately abstract away the archive *container*, the actual
end-user tool, and file-system realities such as directory structure and mixed
content.

**Standard corpora.** Benchmarks conventionally use fixed corpora—Silesia
[@silesia], the Canterbury corpus, or `enwik8`/`enwik9` for text. These enable
cross-study comparison but are unrepresentative of a consumer's folder, which
mixes already-compressed media (JPEG, H.264) with highly compressible text and
semi-structured office documents.

**Format references.** The formats themselves are documented across standards
and primary sources: DEFLATE and gzip [@rfc1951; @rfc1952], the ZIP container
[@pkware_appnote], Brotli [@rfc7932], Zstandard [@rfc8878], the Burrows–Wheeler
transform underlying bzip2 [@burrows1994], LZW underlying `compress` and GIF
[@welch1984], and the context-mixing/PAQ family [@mahoney2000]. Our work sits
between the codec benchmarks and the format references: we ask what an ordinary
user actually gets, today, from each *format's real tool*, on *their kind of
data*.

# Methodology

## Corpus

The benchmark corpus is a 55 MB collection assembled to mirror a typical user's
"Documents" folder, drawn entirely from public-domain or freely reusable
sources so that it can be committed to the repository and redistributed
(Table 1). It is partitioned into four categories, each of which is also
benchmarked on its own so that we can report where format choice matters:

: Corpus composition. All files are public domain; provenance and SHA-256
checksums of every source are recorded in `corpus/SOURCES.md`.

| Category | Size | Contents |
|---|---:|---|
| Text | ~11 MB | Complete works of Shakespeare and *War and Peace* [@gutenberg]; a USGS earthquake catalog CSV [@usgs_quakes]; a synthetic web-server log |
| Documents | ~15 MB | Generated `.docx`, `.epub`, `.pdf`, `.pptx`, `.odt`, and `.xlsx` files built from the public-domain texts and data |
| Images | ~16 MB | NASA/JWST and Apollo photographs (JPEG, PNG) [@nasa_images]; uncompressed TIFF and BMP derivatives |
| Video | ~13 MB | Public-domain NASA Apollo footage (H.264 in MP4 and MOV containers) [@nasa_images] |

The mix is deliberate. Office documents (`.docx`, `.xlsx`, `.pptx`, `.epub`,
`.odt`) are themselves ZIP containers, so they stress an archiver's ability to
compress already-compressed data. The JPEG, PNG, and H.264 media are near-
incompressible, providing an honest lower bound on what any format can achieve.
The uncompressed TIFF and BMP images and the plain-text files are where formats
can genuinely differentiate.

To make results byte-reproducible across machines, single-stream compressors
(gzip, xz, Zstandard, and so on) and archivers that cannot store directory
trees compress a *canonical tar* of each category: a deterministic archive with
entries sorted by name, zeroed ownership, and fixed timestamps, so that its
bytes—and therefore the resulting archive size—do not depend on the clone's
filesystem metadata.

## Format roster and level policy

We test 42 formats, organized into four acquisition tiers:

- **Tier A (native):** tools available from Homebrew or bundled with macOS.
- **Tier B (source builds):** vintage and experimental archivers compiled from
  upstream source, with small patches (committed in `tools/patches/`) where
  modern compilers or 64-bit ARM require them: ARC 5.21p, LHa, zoo 2.10, ARJ
  3.10.22, HA 0.999, freeze 2.5, and paq8px.
- **Tier C (Wine):** Windows-only archivers run under Wine with Rosetta 2.
- **Tier D (DOSBox):** DOS-era archivers run under DOSBox-X, most notably PKZIP
  2.04g (1993).

The **level policy** is central to the study's "practical" framing. Each tool is
run at its **default** settings and at its **maximum** compression level—the one
dial a casual user could reasonably change. We do *not* tune methods,
dictionary sizes, filters, or thread counts beyond what the level switch
implies. This produces some deliberate judgment calls, which we disclose rather
than hide (Table 2).

: Level-policy judgment calls.

| Format | Note |
|---|---|
| bzip2 | Its default block size (`-9`) already is its maximum; default = max. |
| Brotli | The CLI's default quality is already the maximum (`-q 11`); default = max. |
| bzip3 | Its only dial is block size; we treat default (16 MiB) and max (511 MiB) as the two levels. |
| Zstandard | Default level 3 vs. `--ultra -22` maximum. |
| DMG | We report UDZO (zlib, with a level dial) and ULMO (LZMA) as sibling format rows. |
| RAR | We report RAR5 and RAR4 (`-ma4`) as distinct formats, since the flag selects an archive-format version, not a tuning parameter. |
| zopfli | Reported as a separate "gzip, exhaustive" row: same `.gz` format, a different, far slower encoder. |

## Measurement protocol

For each (format, level, category) combination the harness stages the input,
runs the create command, records the resulting archive size, then runs the
extract command and verifies the result. Compression and decompression wall-
clock times are the **median of three runs** for fast tools and a **single run**
for very slow ones (zpaq at maximum, paq8px); peak resident memory is captured
from `/usr/bin/time -l`. Timed runs are executed sequentially on an otherwise
idle machine, kept awake with `caffeinate`. The exact hardware and every tool
version are auto-recorded in `results/environment.md`.

**Verification.** Every archive is round-trip verified. For directory-mode
formats we extract into a scratch directory, hash every file with SHA-256, and
compare against the corpus manifest; content and relative path must match, while
timestamps and permissions are ignored. For single-stream formats we confirm the
decompressed tar is byte-identical to the canonical tar. Wherever possible we
verify with an *independent* extractor—for example, LHA archives created by our
built `lha` are read back and cross-checked, ACE archives are read by the pure-
Python `acefile` [@acefile], and PKZIP's DOS output is read by modern Info-ZIP
`unzip` [@infozip]—so that a bug shared between a tool's compressor and
decompressor cannot mask a corruption.

This verification is not a formality. On the image category, ARC 5.21p produced
an archive that its *own* extractor unpacked while reporting a CRC failure and
emitting a file 55 bytes longer than the original; the harness's SHA-256 check
rejected it. Had we trusted the tool's exit status, a silent corruption would
have passed as a successful result—a concrete argument for content-level
verification over exit codes. Likewise, the 1980s `shar` shell-archive format
succeeds on the text category but fails on every binary category, exactly as its
text-only design predicts; we report these as honest failures rather than
omitting the format.

**Emulation policy.** Formats produced under emulation (Tier C Wine, Tier D
DOSBox) are flagged. Their archive **sizes are directly comparable** to native
formats and are reported as first-class results; their **timings are excluded**
because CPU emulation makes wall-clock time meaningless. These rows are drawn
with hollow markers on the Pareto charts and shown with an em-dash in timing
columns.

# Results

The full, auto-generated ranking tables for every content category are in
`results/tables/results.md`, and the complete machine-readable data is in
`results/tables/results.csv`; the numbers below are drawn directly from those
committed results. Ratio denotes archive size as a percentage of the original
(lower is better).

<!-- RESULTS_TABLES -->

## The size/speed frontier

Figures 1 and 2 plot every native format on the size/time plane for the full
corpus and for text. The frontier is steep and then flat: moving from gzip to
xz or 7-Zip buys a large ratio improvement for a modest time cost, but pushing
further—into zpaq's maximum mode or paq8px—buys a few more percentage points at
one to three *orders of magnitude* more time. For a casual user, the knee of
this curve, occupied by 7-Zip, xz, and Zstandard, is where the practical choice
lies.

![Size versus compression time on the full corpus. Lower and to the left is
better; the x-axis is logarithmic. Emulated formats are omitted (their timings
are not comparable).](figures/pareto_full.png){width=90%}

![Size versus compression time on the text category, where formats differ most.
](figures/pareto_text.png){width=90%}

# Discussion

**What should a casual user actually use?** Three answers, by need:

- *For universal compatibility*—a file anyone can open with no extra
  software—plain **ZIP** remains the correct choice. On the full mixed corpus it
  reached 82% of the original size; it is not the smallest, but every operating
  system has opened it natively for thirty years.
- *For the best mainstream size/speed balance*, **7-Zip** (`.7z`) and
  **Zstandard** (`.tar.zst`) dominate the knee of the frontier. On the full
  corpus 7-Zip reached **60% in about four seconds**—a quarter smaller than ZIP
  for no perceptible extra effort—and Zstandard reached 61%. On the office-
  document category the gap is starker still: ZIP left the already-compressed
  `.docx`/`.xlsx` files essentially untouched at 99%, while 7-Zip recompressed
  them to **60%** by working across the archive members.
- *For the absolute smallest file*, when time is no object, the journaling
  context-mixing archiver **zpaq** reached **56%** at its maximum setting—the
  smallest of any format on the full corpus—but took roughly 150 seconds to
  compress and again to decompress, against 7-Zip's four. The even more extreme
  paq8px goes further still on pure text, at a throughput of roughly 12 KB/s
  that makes it impractical for a whole folder, and only paq8px itself can open
  its output.

**Diminishing returns are dramatic.** On text, the best mainstream tools
(bzip2 at 25.8%, 7-Zip and xz at about 27%) sit within a few percentage points
of the exotic maximum, while costing a fraction of a second rather than tens of
seconds. Plain ZIP reached 35%—and, strikingly, the *1993* PKZIP 2.04g binary
we ran under DOS emulation produced a nearly identical 35.5%, a reminder that
the ZIP format a casual user gets today is essentially the one from three
decades ago. This is the single most important practical takeaway: beyond the
mainstream tools, users pay large time and compatibility costs for small size
gains.

**Already-compressed data resists everyone.** On the video category every
format—old or new—clustered between 98% and 100% of the original size, because
H.264 is already compressed; several formats even *expanded* the data slightly
through container overhead. The corollary for users is that "zipping" a folder
of videos saves essentially nothing; the value of an archive there is bundling
and convenience, not size. Photographs behaved similarly, though the
uncompressed TIFF and BMP images in our set gave the stronger compressors
(RAR4 at 70%, 7-Zip at 76%) some room to work.

**Format longevity cuts both ways.** Remarkably, every vintage *format* in our
set from 1985 onward can still be both created and read on a 2026 machine, once
its tool is rebuilt from source—ARC, zoo, LHA, ARJ, HA, and freeze all round-
trip cleanly. A 1993 PKZIP binary, run under DOS emulation, still produces a ZIP
that a modern `unzip` opens. Yet the *Windows-only* archivers of the 2000s fared
worse: FreeArc and UHARC, run under Wine with Rosetta 2 on Apple Silicon,
consistently deadlocked in their compression cores under double binary
translation, and ACE creation is available only through a discontinued
graphical installer. Paradoxically, a 40-year-old open DOS format proved more
durable than a 20-year-old proprietary Windows one—an argument, for archival
purposes, in favor of simple, open, well-documented formats.

# Limitations

This is a single-machine study; absolute timings will differ on other hardware,
though relative orderings should be stable. Multithreaded tools (7-Zip,
Zstandard, some others) are run at their default thread behavior, which favors
them on wall-clock time; we disclose this rather than force single-threading,
because default behavior is what a user experiences. Timings for emulated tools
are excluded entirely. The corpus is 55 MB—large enough to be realistic, small
enough to commit and to keep paq8px tractable—but ratios can shift with scale,
particularly for long-range and dictionary-based methods. Our level policy
intentionally forgoes method tuning, so specialist configurations that an expert
might use (for example PPMd for text in 7-Zip) are out of scope by design. We
did not evaluate encryption, archive splitting, solid-archive tuning, or
recovery records.

# Reproducibility

The entire study is reproducible from the repository with a single command,
`./run_all.sh`, which verifies the corpus, runs the benchmark, regenerates the
tables and figures, and rebuilds this paper. The corpus and all raw per-run JSON
results are committed, so the tables and figures can be regenerated—and every
claim in this paper checked—without re-running the multi-hour benchmark. The
exact environment is recorded in `results/environment.md`; tool provenance,
including download URLs and SHA-256 checksums for every non-package binary, is
in `tools/README.md`.

# Conclusion

Across 42 formats and four decades, the practical advice for a casual user is
simple and perhaps reassuring: **ZIP for sharing, 7-Zip or Zstandard for
size.** The exotic tail of formats is fascinating—and we have shown that most of
it still works, some of it heroically—but it offers ordinary users little that
the mainstream does not, at costs in time and compatibility they should not pay.
The enduring lesson is about openness and durability: the formats that survived
four decades did so because they were simple, open, and well documented, and
those are the properties worth valuing in a format meant to outlast the software
that made it.

# References
