"""Round-trip verification: prove every archive reproduces the input bytes.

tree mode: walk the extraction directory, SHA-256 each file, compare against
the dataset's manifest slice. Content and relative path must match; mtimes
and permissions are ignored (disclosed in the paper). Container/filesystem
artifacts (e.g. .DS_Store inside a mounted DMG) are tolerated but reported.

tar mode: the extract command reproduces CORPUS.TAR; its SHA-256 must equal
the canonical tar's. Bit-identical tar => bit-identical corpus content.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

from . import corpus

IGNORABLE = {
    ".DS_Store", ".fseventsd", ".Trashes", ".TemporaryItems",
    ".HFS+ Private Directory Data\r", ".journal", ".journal_info_block",
    ".apdisk", "__MACOSX", ".metadata_never_index",
}


@dataclasses.dataclass
class Verdict:
    ok: bool
    method: str
    detail: str
    extras_ignored: list[str]


def verify_tree(out_dir: Path, dataset: str) -> Verdict:
    expected = corpus.manifest_slice(dataset)
    root = _effective_root(out_dir, expected)

    found: dict[str, Path] = {}
    extras_ignored: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORABLE for part in path.relative_to(root).parts):
            extras_ignored.append(str(path.relative_to(root)))
            continue
        found[str(path.relative_to(root))] = path

    missing = sorted(set(expected) - set(found))
    unexpected = sorted(set(found) - set(expected))
    mismatched = [
        rel for rel, digest in expected.items()
        if rel in found and corpus.sha256_file(found[rel]) != digest
    ]

    problems = []
    if missing:
        problems.append(f"missing {len(missing)}: {missing[:3]}")
    if mismatched:
        problems.append(f"hash mismatch {len(mismatched)}: {mismatched[:3]}")
    if unexpected:
        problems.append(f"unexpected files {len(unexpected)}: {unexpected[:3]}")

    return Verdict(
        ok=not problems,
        method="tree",
        detail="; ".join(problems) if problems else
               f"{len(expected)} files verified against manifest",
        extras_ignored=extras_ignored,
    )


def verify_tar(out_tar: Path, dataset: str) -> Verdict:
    if not out_tar.is_file():
        return Verdict(False, "tar", f"decompressed tar missing: {out_tar}", [])
    got = corpus.sha256_file(out_tar)
    want = corpus.canonical_tar_sha256(dataset)
    ok = got == want
    return Verdict(
        ok=ok,
        method="tar",
        detail="decompressed tar SHA-256 matches canonical tar" if ok
               else f"tar hash mismatch: got {got[:16]}…, want {want[:16]}…",
        extras_ignored=[],
    )


def _effective_root(out_dir: Path, expected: dict[str, str]) -> Path:
    """Descend through wrapper directories some extractors introduce.

    If out_dir itself doesn't contain the expected top-level entries but a
    single child directory does (e.g. unsquashfs's `tree/`, an archived `./`
    folder, or a mount-style copy), use that child as the comparison root.
    """
    top_expected = {rel.split("/", 1)[0] for rel in expected}

    def visible(children_of: Path) -> set[str]:
        return {p.name for p in children_of.iterdir() if p.name not in IGNORABLE}

    root = out_dir
    for _ in range(3):
        entries = visible(root)
        if entries & top_expected:
            return root
        dirs = [p for p in root.iterdir()
                if p.is_dir() and p.name not in IGNORABLE]
        if len(dirs) == 1:
            root = dirs[0]
        else:
            return root
    return root
