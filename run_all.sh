#!/bin/bash
# The Ultimate Archive Format Comparison — one-command replication.
#
#   ./run_all.sh            full benchmark (many hours: includes PAQ-class tools)
#   ./run_all.sh --quick    smoke test: 1 timing run, text dataset only (~minutes)
#
# Stages: environment/tool checks -> corpus verification -> benchmark ->
#         report generation -> paper build.
set -euo pipefail
cd "$(dirname "$0")"

QUICK=""
if [[ "${1:-}" == "--quick" ]]; then
    QUICK="--quick"
fi

PY=python3
command -v "$PY" >/dev/null || { echo "python3 is required"; exit 1; }

echo "==> [1/5] Tool availability check"
"$PY" harness/bench.py check

echo "==> [2/5] Corpus integrity verification"
"$PY" harness/bench.py verify-corpus

echo "==> [3/5] Benchmark run (sequential, keep the machine otherwise idle)"
# caffeinate keeps the machine awake and prevents idle throttling mid-run.
caffeinate -dims "$PY" harness/bench.py run $QUICK

echo "==> [4/5] Reports, tables and figures"
"$PY" harness/report.py
"$PY" harness/bench.py env > results/environment.md

echo "==> [5/5] Paper build (pandoc + pdflatex)"
if command -v pandoc >/dev/null && command -v pdflatex >/dev/null; then
    (cd paper && ./build_paper.sh)
else
    echo "pandoc/pdflatex not found - skipping paper build (results are in results/)"
fi

echo "Done. See results/tables/ and paper/paper.pdf"
