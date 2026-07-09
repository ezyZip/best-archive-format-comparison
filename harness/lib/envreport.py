"""Generate the environment disclosure report (results/environment.md)."""
from __future__ import annotations

import datetime
import platform
import subprocess
import sys

from . import corpus
from .registry import REPO_DIR, load


def _sh(cmd: str, timeout: int = 15) -> str:
    import os
    env = dict(os.environ)
    env["PATH"] = f"{REPO_DIR / 'tools' / 'bin'}:{env.get('PATH', '')}"
    try:
        out = subprocess.run(
            ["/bin/sh", "-c", cmd], capture_output=True, text=True,
            timeout=timeout, cwd=REPO_DIR, env=env)
        text = (out.stdout or out.stderr).strip()
        return text if text else f"(exit {out.returncode}, no output)"
    except Exception as e:  # noqa: BLE001 - report, don't crash
        return f"(error: {e})"


def generate() -> str:
    lines = [
        "# Benchmark environment",
        "",
        f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Machine",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| macOS | {_sh('sw_vers -productVersion')} (build {_sh('sw_vers -buildVersion')}) |",
        f"| Kernel | {platform.platform()} |",
        f"| CPU | {_sh('sysctl -n machdep.cpu.brand_string')} |",
        f"| Cores | {_sh('sysctl -n hw.ncpu')} "
        f"({_sh('sysctl -n hw.perflevel0.physicalcpu')}P + {_sh('sysctl -n hw.perflevel1.physicalcpu')}E) |",
        f"| RAM | {int(_sh('sysctl -n hw.memsize')) // (1 << 30)} GiB |",
        f"| Filesystem | {_sh('mount | grep \" / \" | head -1')} |",
        "",
        "## Software",
        "",
        "| Component | Version |",
        "|---|---|",
        f"| Python (harness) | {sys.version.split()[0]} |",
        f"| Homebrew | {_sh('brew --version | head -1')} |",
        f"| Wine | {_sh('wine --version 2>/dev/null || echo not-installed')} |",
        f"| DOSBox-X | {_sh('dosbox-x --version 2>/dev/null | head -1 || echo not-installed')} |",
        f"| Node | {_sh('node --version 2>/dev/null || echo not-installed')} |",
        "",
        "## Corpus",
        "",
        f"- Manifest: `corpus/MANIFEST.sha256`, {len(corpus.read_manifest())} files, "
        f"{sum(p.stat().st_size for p in (REPO_DIR / 'corpus').rglob('*') if p.is_file() and p.parent.name in corpus.CATEGORIES):,} bytes",
        f"- Git commit: {_sh('git -C ' + str(REPO_DIR) + ' rev-parse HEAD')}",
        "",
        "## Archiver versions",
        "",
        "| Format | Origin | Version |",
        "|---|---|---|",
    ]
    for fmt in load():
        version = _sh(fmt.version_cmd).replace("\n", " ").replace("|", "\\|")[:120]
        lines.append(f"| {fmt.name} | {fmt.origin} | {version} |")
    lines.append("")
    return "\n".join(lines)
