#!/bin/bash
# Build the paper: Markdown -> PDF via pandoc + pdflatex, with numbered
# IEEE-style citations resolved from references.bib.
set -euo pipefail
cd "$(dirname "$0")"

command -v pandoc >/dev/null   || { echo "pandoc not found (brew install pandoc)"; exit 1; }
command -v pdflatex >/dev/null || { echo "pdflatex not found (install MacTeX)"; exit 1; }

# Inject the generated results tables into the paper at the RESULTS_TABLES
# marker. paper.md itself stays free of generated numbers.
GEN="../results/tables/paper_results.md"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
if [[ -f "$GEN" ]]; then
    python3 - "$GEN" > "$WORK/paper.md" <<'PY'
import sys
gen = open(sys.argv[1]).read()
doc = open("paper.md").read()
print(doc.replace("<!-- RESULTS_TABLES -->", gen))
PY
else
    echo "warning: $GEN not found - run harness/report.py first; building without result tables"
    cp paper.md "$WORK/paper.md"
fi

pandoc "$WORK/paper.md" metadata.yaml \
    --citeproc \
    --bibliography=references.bib \
    --csl=ieee.csl \
    --pdf-engine=pdflatex \
    --number-sections \
    -V colorlinks=true \
    -o paper.pdf

echo "wrote paper/paper.pdf"
