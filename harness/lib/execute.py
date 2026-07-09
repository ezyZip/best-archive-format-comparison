"""Subprocess execution with wall-clock timing, peak-RSS capture and
process-group timeouts.

Commands are shell strings (registry templates after placeholder
substitution), run through /bin/sh -c and wrapped in /usr/bin/time -l so we
can parse `maximum resident set size` (bytes on macOS) from stderr. Wall time
is measured with time.monotonic() around the child; the /usr/bin/time wrapper
adds only process-spawn overhead (identical for every tool).
"""
from __future__ import annotations

import dataclasses
import os
import signal
import subprocess
import time

TIME_BIN = "/usr/bin/time"


@dataclasses.dataclass
class Result:
    wall: float
    rss_bytes: int | None
    exit_code: int | None
    timed_out: bool
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return not self.timed_out and self.exit_code == 0


def run(cmd: str, cwd, timeout: int, env: dict | None = None) -> Result:
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    start = time.monotonic()
    proc = subprocess.Popen(
        [TIME_BIN, "-l", "/bin/sh", "-c", cmd],
        cwd=str(cwd),
        env=full_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,   # own process group => clean timeout kill
    )
    try:
        out, err = proc.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
        timed_out = True
    wall = time.monotonic() - start

    stderr = err.decode("utf-8", "replace")
    rss = _parse_rss(stderr)
    return Result(
        wall=wall,
        rss_bytes=rss,
        exit_code=None if timed_out else proc.returncode,
        timed_out=timed_out,
        stdout=out.decode("utf-8", "replace")[-8000:],
        stderr=_strip_time_output(stderr)[-8000:],
    )


def _parse_rss(stderr: str) -> int | None:
    for line in stderr.splitlines():
        if "maximum resident set size" in line:
            try:
                return int(line.split()[0])
            except (ValueError, IndexError):
                return None
    return None


def _strip_time_output(stderr: str) -> str:
    """Remove /usr/bin/time -l statistics lines, keep the tool's own stderr."""
    markers = (
        "real ", "maximum resident set size", "average shared memory",
        "average unshared", "page reclaims", "page faults", "swaps",
        "block input", "block output", "messages ", "signals received",
        "voluntary context", "involuntary context", "instructions retired",
        "cycles elapsed", "peak memory footprint",
    )
    kept = [
        line for line in stderr.splitlines()
        if not any(m in line for m in markers)
    ]
    return "\n".join(kept)
