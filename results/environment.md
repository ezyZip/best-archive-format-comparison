# Benchmark environment

Generated: 2026-07-09T13:30:50+00:00

## Machine

| Property | Value |
|---|---|
| macOS | 26.3.1 (build 25D771280a) |
| Kernel | macOS-26.3.1-arm64-arm-64bit |
| CPU | Apple M2 Pro |
| Cores | 10 (6P + 4E) |
| RAM | 16 GiB |
| Filesystem | /dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled) |

## Software

| Component | Version |
|---|---|
| Python (harness) | 3.12.10 |
| Homebrew | Homebrew 6.0.9 |
| Wine | wine-11.0 |
| DOSBox-X | (exit 0, no output) |
| Node | v23.11.1 |

## Corpus

- Manifest: `corpus/MANIFEST.sha256`, 18 files, 57,747,676 bytes
- Git commit: a6882156ce34fbd111bdad7958b2068f6c0f8433

## Archiver versions

| Format | Origin | Version |
|---|---|---|
| ZIP (Info-ZIP) | macOS bundled (Info-ZIP) | Copyright (c) 1990-2008 Info-ZIP - Type 'zip "-L"' for software license. This is Zip 3.0 (July 5th 2008), by Info-ZIP, w |
| 7z (7-Zip, LZMA2) | brew sevenzip | 64-bit arm_v:8.5-A locale=en_AU.UTF-8 Threads:10 OPEN_MAX:1048576, ASM |
| RAR 5 (WinRAR/rar) | brew rar (proprietary, licensed) | RAR 6.23   Copyright (c) 1993-2023 Alexander Roshal   1 Aug 2023 |
| RAR 4 (legacy format) | brew rar (proprietary, licensed) | RAR 6.23   Copyright (c) 1993-2023 Alexander Roshal   1 Aug 2023 |
| tar (uncompressed, baseline) | macOS bundled (libarchive) | bsdtar 3.5.3 - libarchive 3.7.4 zlib/1.2.12 liblzma/5.4.3 bz2lib/1.0.8 |
| tar.gz (gzip) | macOS bundled | Apple gzip 475 |
| tar.gz (zopfli, exhaustive deflate) | brew zopfli | zopfli 1.0.3_1 |
| tar.bz2 (bzip2) | macOS bundled | bzip2, a block-sorting file compressor.  Version 1.0.8, 13-Jul-2019. |
| tar.xz (xz/LZMA2) | brew xz | xz (XZ Utils) 5.8.3 liblzma 5.8.3 |
| tar.zst (Zstandard) | brew zstd | *** Zstandard CLI (64-bit) v1.5.7, by Yann Collet *** |
| tar.lz4 (LZ4) | brew lz4 | *** lz4 v1.10.0 64-bit multithread, by Yann Collet *** |
| tar.br (Brotli) | brew brotli | brotli 1.1.0 |
| tar.lzo (lzop) | brew lzop | lzop 1.04 |
| tar.lrz (lrzip) | brew lrzip | lrzip version 0.641 |
| tar.bz3 (bzip3) | brew bzip3 | bzip3 1.5.2 |
| tar.Z (compress, LZW 1984) | macOS bundled | compress (macOS bundled, ncompress also installed) |
| tar.lz (lzip) | brew lzip | lzip 1.26 |
| tar.rz (rzip) | brew rzip | rzip version 2.1 |
| zpaq (journaling PAQ-family) | brew zpaq | zpaq v7.15 journaling archiver, compiled Aug 17 2016 |
| Apple Archive (.aar, lzfse) | macOS bundled | aa (macOS bundled Apple Archive tool) |
| DMG (UDZO, zlib-compressed image) | macOS bundled | driver          : 681.60.1 |
| DMG (ULMO, lzma-compressed image) | macOS bundled | driver          : 681.60.1 |
| xar (macOS eXtensible ARchiver) | macOS bundled | xar 1.8dev |
| SquashFS (mksquashfs) | brew squashfs | mksquashfs version 4.7.4 (2025/11/09) |
| WIM (wimlib, LZX) | brew wimlib | wimlib-imagex 1.14.4 (using wimlib 1.14.4) |
| ISO 9660 (mkisofs, store-only) | brew cdrtools | mkisofs 3.02a09 (--) |
| dar (Disk ARchive) | brew dar | dar version 2.8.5, Copyright (C) 2002-2026 Denis Corbin |
| CAB (gcab, MSZIP) | brew gcab | gcab v1.6 |
| LHA/LZH (1988, lh5) | source build: github.com/jca02266/lha | LHa for UNIX version 1.14i-ac20220213 (aarch64-apple-darwin25.3.0) |
| zoo (1986) | source build: zoo 2.10 (Debian orig + patches) | zoo 2.1 $Date: 91/07/09 02:10:34 $ |
| ARC (SEA, 1985) | source build: github.com/hyc/arc (ARC 5.21p) | ARC - Archive utility, Version 5.21p, created on 08/07/2010 |
| ARJ (1991) | source build: arj 3.10.22 (Debian orig + patches) | ARJ32 v 3.10, Copyright (c) 1998-2004, ARJ Software Russia. |
| HA (1993, PPM-family) | source build: HA 0.999 (github.com/l-4-l/ha) | HA 0.999� Copyright (c) 1995 Harri Hirvola |
| freeze (1993) | source build: freeze 2.5.0 (ibiblio.org) | @(#) freeze.c 2.5.0 2/7/93 leo@ipmce.su |
| paq8px (context mixing, state of the art) | source build: github.com/hxim/paq8px (v216) | paq8px data compressor v216 (c) 2026, Matt Mahoney et al. |
| FreeArc 0.666 (2007, Wine) | archive.org FreeArc-portable-0.666-win32.zip, run under Wine 11 | FreeArc 0.666 (2007) console Arc.exe via Wine |
| UHARC 0.6b (2005, Wine) | archive.org uharc06b.zip, run under Wine 11 | UHARC 0.6b (2005) via Wine |
| ZIP (PKZIP 2.04g, 1993) | archive.org PKZ204G.EXE (1993), run under DOSBox-X | PKZIP 2.04g (1993), PKWARE - DOS binary via DOSBox-X |
| cpio (appendix: store-only) | macOS bundled (bsdcpio) | bsdcpio 3.5.3 - libarchive 3.7.4 zlib/1.2.12 liblzma/5.4.3 bz2lib/1.0.8 |
| ar (appendix: unix archiver, store-only) | macOS bundled | usage:  ar -d [-TLsv] archive file ... |
| pax (appendix: POSIX archiver) | macOS bundled | pax (macOS bundled, POSIX) |
| shar (appendix: shell archive) | macOS bundled | shar (macOS bundled) |

