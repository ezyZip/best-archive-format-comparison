#!/usr/bin/env python3
"""Benchmark CLI.

  bench.py check                     tool availability for every registry row
  bench.py verify-corpus             corpus vs MANIFEST.sha256
  bench.py run [options]             run the benchmark (resumable)
  bench.py env                       print environment report (markdown)
  bench.py clean                     remove work dirs and produced archives

run options:
  --quick            1 timing run, text dataset only (smoke test / phase gate)
  --force            re-run even if a result JSON exists
  --retry-timeouts   re-run units whose status is timeout/failed
  --only a,b,c       only these format ids
  --dataset d        only this dataset (text|documents|images|video|full)
  --tier X           only this tier (A|B|C|D|W)
  --level l          only this level (default|max)
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import corpus, envreport, registry, runner  # noqa: E402


def cmd_check(_args) -> int:
    failures = 0
    for fmt in registry.load():
        out = subprocess.run(["/bin/sh", "-c", fmt.version_cmd],
                             capture_output=True, text=True, timeout=30)
        text = (out.stdout or out.stderr).strip().splitlines()
        ok = bool(text)
        print(f"{'ok  ' if ok else 'MISS'} {fmt.id:<16} {text[0][:80] if text else '(no output)'}")
        failures += 0 if ok else 1
    print(f"\n{failures} tools missing" if failures else "\nall tools present")
    return 1 if failures else 0


def cmd_verify_corpus(_args) -> int:
    problems = corpus.verify_corpus()
    if problems:
        print("\n".join(problems))
        print(f"\ncorpus FAILED verification ({len(problems)} problems)")
        return 1
    print(f"corpus ok: {len(corpus.read_manifest())} files match MANIFEST.sha256")
    return 0


def cmd_run(args) -> int:
    formats = registry.load()
    datasets = corpus.DATASETS
    if args.quick:
        datasets = ["text"]
    if args.dataset:
        datasets = [args.dataset]
    if args.only:
        wanted = set(args.only.split(","))
        unknown = wanted - {f.id for f in formats}
        if unknown:
            sys.exit(f"unknown format ids: {sorted(unknown)}")
        formats = [f for f in formats if f.id in wanted]
    if args.tier:
        formats = [f for f in formats if f.tier == args.tier]

    print("staging datasets and canonical tars…")
    corpus.build_datasets()

    units = [(f, level, ds)
             for ds in datasets
             for f in formats
             for level in f.levels
             if not args.level or level == args.level]
    print(f"{len(units)} run-units queued\n")

    t0 = time.monotonic()
    counts = {"ok": 0, "failed": 0, "timeout": 0, "skipped": 0}
    for i, (fmt, level, ds) in enumerate(units, 1):
        tag = f"[{i}/{len(units)}] {ds:<10} {fmt.id:<16} {level:<8}"
        existing = runner.load_result(runner.result_path(fmt.id, level, ds))
        if not args.force and runner.should_skip(existing, args.retry_timeouts):
            counts["skipped"] += 1
            print(f"{tag} skipped ({existing['status']})")
            continue
        res = runner.run_unit(fmt, level, ds,
                              runs_override=1 if args.quick else None)
        counts[res["status"]] += 1
        if res["status"] == "ok":
            print(f"{tag} ok    {res['ratio_pct']:7.2f}%  "
                  f"c={res['compress_s_median']:.2f}s d={res['decompress_s_median']:.2f}s")
        else:
            print(f"{tag} {res['status'].upper()}  {res['error'][:120]}")

    dt = time.monotonic() - t0
    print(f"\ndone in {dt/60:.1f} min: {counts}")
    return 1 if counts["failed"] else 0


def cmd_env(_args) -> int:
    print(envreport.generate())
    return 0


def cmd_clean(_args) -> int:
    for sub in ("work", "archives", "logs"):
        path = registry.REPO_DIR / "results" / sub
        if path.exists():
            shutil.rmtree(path)
            print(f"removed {path}")
    if corpus.BUILD_DIR.exists():
        shutil.rmtree(corpus.BUILD_DIR)
        print(f"removed {corpus.BUILD_DIR}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("verify-corpus")
    run = sub.add_parser("run")
    run.add_argument("--quick", action="store_true")
    run.add_argument("--force", action="store_true")
    run.add_argument("--retry-timeouts", action="store_true")
    run.add_argument("--only")
    run.add_argument("--dataset", choices=corpus.DATASETS)
    run.add_argument("--tier", choices=sorted(registry.TIERS))
    run.add_argument("--level")
    sub.add_parser("env")
    sub.add_parser("clean")
    args = parser.parse_args()
    return {
        "check": cmd_check,
        "verify-corpus": cmd_verify_corpus,
        "run": cmd_run,
        "env": cmd_env,
        "clean": cmd_clean,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
