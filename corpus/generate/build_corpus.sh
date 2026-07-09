#!/bin/bash
# Rebuild every corpus file from its raw public-domain sources.
#
#   ./build_corpus.sh <downloads-dir>
#
# <downloads-dir> must contain the raw source files listed in
# corpus/SOURCES.md (Project Gutenberg texts, NASA assets, USGS CSV).
# Outputs are written into corpus/{text,documents,images,video}.
#
# The committed corpus files are the ground truth (see MANIFEST.sha256);
# this script is their provenance. Some generators (pandoc, pdflatex,
# ImageMagick, ffmpeg) embed tool versions or timestamps, so regenerated
# documents may not be byte-identical to the committed ones - the committed
# bytes are what the benchmark measures.
set -euo pipefail

DL="${1:?usage: build_corpus.sh <downloads-dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
CORPUS="$(dirname "$HERE")"
GEN="$HERE"

mkdir -p "$CORPUS"/{text,documents,images,video}
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "==> text/"
python3 "$GEN/strip_gutenberg.py" "$DL/pg100.txt" "$CORPUS/text/shakespeare-complete.txt"
python3 "$GEN/strip_gutenberg.py" "$DL/pg2600.txt" "$CORPUS/text/war-and-peace.txt"
cp "$DL/earthquakes.csv" "$CORPUS/text/earthquakes.csv"
python3 "$GEN/gen_access_log.py" "$CORPUS/text/server-access.log"

echo "==> images/"
cp "$DL/carina_nebula.png" "$CORPUS/images/carina-nebula-jwst.png"
cp "$DL/as11-40-5874.jpg" "$CORPUS/images/aldrin-apollo11.jpg"
cp "$DL/as17-148-22727.jpg" "$CORPUS/images/blue-marble-apollo17.jpg"
cp "$DL/as08-14-2383.jpg" "$CORPUS/images/earthrise-apollo8.jpg"
# Uncompressed raster derivatives: realistic scans/exports, and the only
# corpus files where compressors can differentiate on image data.
magick "$DL/carina_nebula.png" -compress none "$CORPUS/images/carina-nebula.tiff"
magick "$DL/as11-40-5874.jpg" -resize 800x "$CORPUS/images/moon-surface.bmp"

echo "==> documents/"
python3 "$GEN/strip_gutenberg.py" "$DL/pg11.txt" "$WORK/alice.txt"
python3 "$GEN/strip_gutenberg.py" "$DL/pg84.txt" "$WORK/frankenstein.txt"
python3 "$GEN/strip_gutenberg.py" "$DL/pg1342.txt" "$WORK/pride.txt"

pandoc "$WORK/alice.txt" -f markdown -t docx \
    --metadata title="Alice's Adventures in Wonderland" \
    --metadata author="Lewis Carroll" \
    -o "$CORPUS/documents/alice-in-wonderland.docx"

pandoc "$WORK/frankenstein.txt" -f markdown -t epub \
    --metadata title="Frankenstein; Or, The Modern Prometheus" \
    --metadata author="Mary Wollstonecraft Shelley" \
    -o "$CORPUS/documents/frankenstein.epub"

{
    printf -- '---\ntitle: "Pride and Prejudice"\nauthor: "Jane Austen"\n---\n\n'
    printf '![Earthrise](%s)\n\n' "$CORPUS/images/earthrise-apollo8.jpg"
    cat "$WORK/pride.txt"
} > "$WORK/pride.md"
pandoc "$WORK/pride.md" -f markdown --pdf-engine=pdflatex \
    -V geometry:margin=1in -o "$CORPUS/documents/pride-and-prejudice.pdf"

(cd "$GEN" && pandoc mission-report.md -f markdown -t pptx \
    -o "$CORPUS/documents/mission-report.pptx")
(cd "$GEN" && pandoc mission-report.md -f markdown -t odt \
    -o "$CORPUS/documents/mission-report.odt")

python3 "$GEN/make_xlsx.py" "$DL/earthquakes.csv" "$CORPUS/documents/earthquake-data.xlsx"

echo "==> video/"
# Stream copy (no re-encode): trims are cut at keyframes, codecs untouched.
ffmpeg -y -v error -ss 0 -t 32 -i "$DL/moonwalk_720p.mp4" -c copy \
    "$CORPUS/video/moonwalk-montage.mp4"
ffmpeg -y -v error -ss 32 -t 13 -i "$DL/moonwalk_720p.mp4" -c copy \
    "$CORPUS/video/moonwalk-clip.mov"

echo "==> MANIFEST.sha256"
(cd "$CORPUS" && find text documents images video -type f | LC_ALL=C sort \
    | xargs shasum -a 256 > MANIFEST.sha256)

echo "done:"
du -sh "$CORPUS"/{text,documents,images,video}
