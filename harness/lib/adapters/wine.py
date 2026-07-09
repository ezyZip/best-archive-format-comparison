"""Wine adapter: run Windows console archivers under Wine.

The command template already names the Windows executable (installed under
tools/wine/prefix by tools/setup_wine.sh). We prepend `wine`, point
WINEPREFIX at the repo-local prefix, and silence Wine's debug chatter.
Commands run with cwd = staging dir and use relative file names, so no
unix<->windows path marshaling is needed.
"""
from __future__ import annotations

from pathlib import Path

from ..registry import REPO_DIR

PREFIX = REPO_DIR / "tools" / "wine" / "prefix"


def prepare(fmt, cmd: str, ctx) -> tuple[str, dict]:
    env = {
        "WINEPREFIX": str(PREFIX),
        "WINEDEBUG": "-all",
    }
    return f"wine {cmd}", env
