"""Orchestrate one run-unit: (format, level, dataset) -> results/raw JSON.

Per unit:
  1. stage the input (dataset tree clone, or the canonical tar)
  2. run the create command N times (archive deleted between runs),
     recording wall time and peak RSS; keep the final archive
  3. run the extract command N times the same way
  4. verify the final extraction (tree hash compare, or tar hash compare)
  5. write results/raw/{dataset}/{id}.{level}.json

Existing result files are skipped (resume); see bench.py flags.
"""
from __future__ import annotations

import dataclasses
import datetime
import glob
import json
import shutil
import statistics
import subprocess
from pathlib import Path

from . import adapters, corpus, execute, verify
from .registry import Format, REPO_DIR

SCHEMA_VERSION = 2
RAW_DIR = REPO_DIR / "results" / "raw"
WORK_DIR = REPO_DIR / "results" / "work"
ARCHIVE_DIR = REPO_DIR / "results" / "archives"
LOG_DIR = REPO_DIR / "results" / "logs"


@dataclasses.dataclass
class Ctx:
    staging: Path
    cwd: Path          # where the create command runs
    out_dir: Path
    archive: Path      # the run-unit's archive path (for engine adapters)
    dos_archive: str = ""   # short 8.3 archive name (dosbox engine)


def result_path(fmt_id: str, level: str, dataset: str) -> Path:
    return RAW_DIR / dataset / f"{fmt_id}.{level}.json"


def load_result(path: Path):
    try:
        data = json.loads(path.read_text())
        if data.get("schema_version") == SCHEMA_VERSION:
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return None


def should_skip(existing, retry_timeouts: bool) -> bool:
    if existing is None:
        return False
    if retry_timeouts and existing["status"] in ("timeout", "failed"):
        return False
    return existing["status"] in ("ok", "timeout", "failed")


def run_unit(fmt: Format, level: str, dataset: str, runs_override: int | None = None,
             keep_archive: bool = True) -> dict:
    runs = runs_override or fmt.runs
    timeout = fmt.timeout_for(level)
    unit = f"{fmt.id}.{level}.{dataset}"

    staging = WORK_DIR / unit
    if staging.exists():
        shutil.rmtree(staging)
    input_dir = staging / "input"
    out_dir = staging / "out"
    input_dir.mkdir(parents=True)
    out_dir.mkdir()

    if fmt.input_mode == "directory":
        subprocess.run(
            ["cp", "-Rc", str(corpus.dataset_dir(dataset)) + "/.", str(input_dir)],
            check=True)
    else:
        subprocess.run(
            ["cp", "-c", str(corpus.canonical_tar(dataset)),
             str(input_dir / "CORPUS.TAR")], check=True)

    archive_dir = ARCHIVE_DIR / fmt.id
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive = archive_dir / f"{dataset}.{level}.{fmt.ext}"

    dos_archive = f"A.{fmt.ext.upper()[:3]}"
    ctx = Ctx(staging=staging, cwd=input_dir, out_dir=out_dir, archive=archive,
              dos_archive=dos_archive)
    subst = {
        "archive": str(archive),
        "archive_base": str(archive.with_suffix("")),
        "archive_name": archive.name,
        "dos_archive": dos_archive,
        "tar_file": "CORPUS.TAR",
        "out_dir": str(out_dir),
        "out_tar": str(out_dir / "CORPUS.TAR"),
        "wine_dl": str(REPO_DIR / "tools" / "wine" / "downloads"),
    }

    base = {
        "schema_version": SCHEMA_VERSION,
        "id": fmt.id, "name": fmt.name, "tier": fmt.tier, "level": level,
        "dataset": dataset, "engine": fmt.engine, "emulated": fmt.emulated,
        "appendix": fmt.appendix, "input_mode": fmt.input_mode,
        "origin": fmt.origin, "notes": fmt.notes,
        "create_cmd": fmt.create[level], "extract_cmd": fmt.extract,
        "runs": runs, "timeout_s": timeout,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "input_bytes": corpus.input_bytes(dataset),
    }

    # ---- create ----------------------------------------------------------
    create_cmd, env = adapters.prepare(fmt, fmt.create[level].format(**subst), ctx)
    c_walls, c_rss = [], []
    for i in range(runs):
        _remove_archive(archive, fmt, subst)
        res = execute.run(create_cmd, cwd=ctx.cwd, timeout=timeout, env=env)
        _log(unit, f"create.{i}", create_cmd, res)
        if res.timed_out:
            return _finish(base, status="timeout",
                           error=f"create timed out after {timeout}s")
        if res.exit_code != 0:
            return _finish(base, status="failed",
                           error=f"create exited {res.exit_code}: {res.stderr[-2000:]}")
        # Tools writing archives relative to cwd get moved into place.
        rel = ctx.cwd / archive.name
        if not _archive_exists(archive, fmt, subst) and rel.exists():
            rel.rename(archive)
        if not _archive_exists(archive, fmt, subst):
            return _finish(base, status="failed",
                           error=f"create succeeded but archive not found: {archive}")
        c_walls.append(res.wall)
        if res.rss_bytes:
            c_rss.append(res.rss_bytes)

    archive_bytes = _archive_size(archive, fmt, subst)

    # ---- extract ---------------------------------------------------------
    extract_cmd, env = adapters.prepare(fmt, fmt.extract.format(**subst), ctx,
                                        engine=fmt.extract_engine)
    d_walls, d_rss = [], []
    for i in range(runs):
        shutil.rmtree(out_dir)
        out_dir.mkdir()
        res = execute.run(extract_cmd, cwd=out_dir, timeout=timeout, env=env)
        _log(unit, f"extract.{i}", extract_cmd, res)
        if res.timed_out:
            return _finish(base, status="timeout", archive_bytes=archive_bytes,
                           error=f"extract timed out after {timeout}s")
        if res.exit_code != 0:
            return _finish(base, status="failed", archive_bytes=archive_bytes,
                           error=f"extract exited {res.exit_code}: {res.stderr[-2000:]}")
        d_walls.append(res.wall)
        if res.rss_bytes:
            d_rss.append(res.rss_bytes)

    # ---- verify ----------------------------------------------------------
    if fmt.verify == "tree":
        verdict = verify.verify_tree(out_dir, dataset)
    else:
        verdict = verify.verify_tar(out_dir / "CORPUS.TAR", dataset)
    if not verdict.ok:
        return _finish(base, status="failed", archive_bytes=archive_bytes,
                       error=f"verification failed: {verdict.detail}")

    result = _finish(
        base, status="ok", archive_bytes=archive_bytes,
        compress_s=c_walls, decompress_s=d_walls,
        compress_rss=max(c_rss) if c_rss else None,
        decompress_rss=max(d_rss) if d_rss else None,
        verify_detail=verdict.detail,
        verify_method=verdict.method,
        extras_ignored=verdict.extras_ignored,
    )
    shutil.rmtree(staging)
    if not keep_archive:
        _remove_archive(archive, fmt, subst)
    return result


def _finish(base: dict, status: str, archive_bytes: int | None = None,
            compress_s=None, decompress_s=None, compress_rss=None,
            decompress_rss=None, error: str = "", verify_detail: str = "",
            verify_method: str = "", extras_ignored=None) -> dict:
    result = dict(base)
    result["status"] = status
    result["archive_bytes"] = archive_bytes
    if archive_bytes and base["input_bytes"]:
        result["ratio_pct"] = round(100.0 * archive_bytes / base["input_bytes"], 3)
    result["compress_s"] = compress_s
    result["decompress_s"] = decompress_s
    result["compress_s_median"] = round(statistics.median(compress_s), 3) if compress_s else None
    result["decompress_s_median"] = round(statistics.median(decompress_s), 3) if decompress_s else None
    result["compress_rss_bytes"] = compress_rss
    result["decompress_rss_bytes"] = decompress_rss
    result["verify"] = {"method": verify_method, "detail": verify_detail,
                        "extras_ignored": extras_ignored or []}
    result["error"] = error
    path = result_path(base["id"], base["level"], base["dataset"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=1))
    return result


def _archive_paths(archive: Path, fmt: Format, subst: dict) -> list[Path]:
    if fmt.archive_glob:
        pattern = fmt.archive_glob.format(**subst)
        return [Path(p) for p in glob.glob(pattern)]
    return [archive]


def _archive_exists(archive: Path, fmt: Format, subst: dict) -> bool:
    paths = _archive_paths(archive, fmt, subst)
    return bool(paths) and all(p.exists() for p in paths)


def _archive_size(archive: Path, fmt: Format, subst: dict) -> int:
    return sum(p.stat().st_size for p in _archive_paths(archive, fmt, subst))


def _remove_archive(archive: Path, fmt: Format, subst: dict) -> None:
    for p in _archive_paths(archive, fmt, subst):
        if p.exists():
            p.unlink()


def _log(unit: str, step: str, cmd: str, res: execute.Result) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_DIR / f"{unit}.log", "a") as f:
        f.write(f"\n$ {cmd}\n[{step}] wall={res.wall:.3f}s exit={res.exit_code} "
                f"timed_out={res.timed_out}\n")
        if res.stdout.strip():
            f.write(res.stdout + "\n")
        if res.stderr.strip():
            f.write(res.stderr + "\n")
