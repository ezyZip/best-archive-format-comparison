"""Load and validate the declarative format registry (harness/formats.yaml)."""
from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Optional

import yaml

HARNESS_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = HARNESS_DIR.parent
REGISTRY_FILE = HARNESS_DIR / "formats.yaml"

ENGINES = {"native", "wine", "dosbox", "wasm"}
TIERS = {"A", "B", "C", "D", "W"}
INPUT_MODES = {"directory", "tar"}
VERIFY_MODES = {"tree", "tar"}


@dataclasses.dataclass
class Format:
    id: str
    name: str
    tier: str
    ext: str
    engine: str
    input_mode: str
    create: dict          # level name -> command template
    extract: str
    verify: str
    runs: int
    timeout: dict         # level name -> seconds
    version_cmd: str
    origin: str
    emulated: bool = False
    appendix: bool = False
    archive_glob: Optional[str] = None   # for tools producing slices (dar)
    notes: str = ""

    @property
    def levels(self) -> list[str]:
        return list(self.create.keys())

    def timeout_for(self, level: str) -> int:
        return int(self.timeout.get(level, self.timeout.get("default", 900)))


def load(path: Path = REGISTRY_FILE) -> list[Format]:
    entries = yaml.safe_load(path.read_text())
    formats, seen = [], set()
    for raw in entries:
        f = Format(**raw)
        if f.id in seen:
            raise ValueError(f"duplicate format id: {f.id}")
        seen.add(f.id)
        if f.tier not in TIERS:
            raise ValueError(f"{f.id}: bad tier {f.tier}")
        if f.engine not in ENGINES:
            raise ValueError(f"{f.id}: bad engine {f.engine}")
        if f.input_mode not in INPUT_MODES:
            raise ValueError(f"{f.id}: bad input_mode {f.input_mode}")
        if f.verify not in VERIFY_MODES:
            raise ValueError(f"{f.id}: bad verify {f.verify}")
        if not f.create:
            raise ValueError(f"{f.id}: no create commands")
        for level, cmd in f.create.items():
            if "{archive}" not in cmd and "{archive_base}" not in cmd:
                raise ValueError(f"{f.id}/{level}: create must reference "
                                 "{archive} or {archive_base}")
        formats.append(f)
    return formats
