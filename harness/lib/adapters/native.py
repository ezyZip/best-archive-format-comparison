"""Native adapter: run the command as-is on the host."""
from __future__ import annotations


def prepare(fmt, cmd: str, ctx) -> tuple[str, dict]:
    return cmd, {}
