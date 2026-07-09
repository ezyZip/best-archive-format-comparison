"""Corpus integrity checks, dataset staging, and canonical tar construction.

Datasets are the four corpus categories plus 'full' (all of them). Directory-
mode formats archive a staged copy of the dataset tree; tar-mode formats
(single-stream compressors and tools that cannot store directory trees)
compress a canonical, deterministic tarball of the same tree.

The canonical tar is byte-reproducible across clones: entries sorted by
name, uid/gid 0, empty owner names, all mtimes pinned to SOURCE_DATE_EPOCH
(git does not preserve mtimes), USTAR format.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import tarfile
from pathlib import Path

from .registry import REPO_DIR

CORPUS_DIR = REPO_DIR / "corpus"
MANIFEST = CORPUS_DIR / "MANIFEST.sha256"
BUILD_DIR = REPO_DIR / "corpus-build"

CATEGORIES = ["text", "documents", "images", "video"]
DATASETS = CATEGORIES + ["full"]

# 2026-07-09T00:00:00Z - the corpus retrieval date.
SOURCE_DATE_EPOCH = 1783728000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def read_manifest() -> dict[str, str]:
    """relative path -> sha256"""
    entries = {}
    for line in MANIFEST.read_text().splitlines():
        digest, rel = line.split(None, 1)
        entries[rel.lstrip("*")] = digest
    return entries


def verify_corpus() -> list[str]:
    """Return a list of problems (empty = corpus matches MANIFEST.sha256)."""
    problems = []
    manifest = read_manifest()
    for rel, digest in manifest.items():
        path = CORPUS_DIR / rel
        if not path.is_file():
            problems.append(f"missing: {rel}")
        elif sha256_file(path) != digest:
            problems.append(f"hash mismatch: {rel}")
    on_disk = {
        str(p.relative_to(CORPUS_DIR))
        for cat in CATEGORIES
        for p in (CORPUS_DIR / cat).rglob("*")
        if p.is_file() and p.name != ".DS_Store"
    }
    for extra in sorted(on_disk - set(manifest)):
        problems.append(f"not in manifest: {extra}")
    return problems


def manifest_slice(dataset: str) -> dict[str, str]:
    """Manifest entries for one dataset, keyed by path relative to dataset root."""
    manifest = read_manifest()
    if dataset == "full":
        return dict(manifest)
    prefix = dataset + "/"
    return {rel[len(prefix):]: d for rel, d in manifest.items() if rel.startswith(prefix)}


def dataset_dir(dataset: str) -> Path:
    return BUILD_DIR / "datasets" / dataset


def canonical_tar(dataset: str) -> Path:
    return BUILD_DIR / "tars" / f"{dataset}.tar"


def canonical_tar_sha256(dataset: str) -> str:
    return (canonical_tar(dataset).with_suffix(".tar.sha256")).read_text().strip()


def input_bytes(dataset: str) -> int:
    return sum(p.stat().st_size for p in dataset_dir(dataset).rglob("*") if p.is_file())


def build_datasets(force: bool = False) -> None:
    """Stage dataset trees and canonical tars under corpus-build/."""
    for dataset in DATASETS:
        dst = dataset_dir(dataset)
        if dst.exists() and not force:
            pass
        else:
            if dst.exists():
                shutil.rmtree(dst)
            dst.mkdir(parents=True)
            sources = CATEGORIES if dataset == "full" else [dataset]
            for cat in sources:
                target = dst / cat if dataset == "full" else dst
                # APFS clonefile copies: instant, no extra disk.
                subprocess.run(
                    ["cp", "-Rc", str(CORPUS_DIR / cat) + "/.", str(target)],
                    check=True,
                )
            # Deterministic mtimes for directory-mode archivers too.
            for p in sorted(dst.rglob("*")):
                if p.name == ".DS_Store":
                    p.unlink()
            subprocess.run(
                ["find", str(dst), "-exec", "touch", "-t", "202607090000", "{}", "+"],
                check=True,
            )

        tar_path = canonical_tar(dataset)
        if tar_path.exists() and not force:
            continue
        tar_path.parent.mkdir(parents=True, exist_ok=True)
        _write_canonical_tar(dataset_dir(dataset), tar_path)
        tar_path.with_suffix(".tar.sha256").write_text(sha256_file(tar_path) + "\n")


def _write_canonical_tar(src: Path, dst: Path) -> None:
    def normalize(info: tarfile.TarInfo) -> tarfile.TarInfo:
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mtime = SOURCE_DATE_EPOCH
        info.mode = 0o755 if info.isdir() else 0o644
        return info

    with tarfile.open(dst, "w", format=tarfile.USTAR_FORMAT) as tf:
        for path in sorted(src.rglob("*")):
            if path.name == ".DS_Store":
                continue
            tf.add(path, arcname=str(path.relative_to(src)), recursive=False,
                   filter=normalize)
