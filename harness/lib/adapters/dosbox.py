"""DOSBox adapter: run DOS-era archivers under dosbox-x, headless.

DOSBox-X interprets x86 directly (no Rosetta/Wine PE translation), which is far
more robust for old DOS binaries than Wine is for Win32 ones. Timings under CPU
emulation are meaningless and are excluded from results; only archive size and
round-trip integrity are reported for tier D.

Model: the registry `create`/`extract` commands are DOS command lines that use
short 8.3 names and the placeholder {dos_archive} (a fixed short archive name).
This adapter mounts the working directory as C:, stages the format's DOS tools
(fmt.dos_tools, from tools/dos/apps/) onto it, runs the DOS command, and shuttles
the archive between its short DOS name and the harness's real (long) path:

  * create  ({archive} does not exist yet): run in the input dir, then move the
    short archive out to {archive}.
  * extract ({archive} already exists):     copy {archive} in under the short
    name first, then run in the output dir.
"""
from __future__ import annotations

import shlex
from pathlib import Path

from ..registry import REPO_DIR

DOS_APPS = REPO_DIR / "tools" / "dos" / "apps"

CONF_TEMPLATE = """\
[sdl]
output=surface
[cpu]
core=dynamic
cycles=max
[autoexec]
MOUNT C "{mount_dir}"
C:
{dos_cmd}
ECHO done > DONE.FLG
EXIT
"""


def prepare(fmt, cmd: str, ctx) -> tuple[str, dict]:
    is_extract = ctx.archive.exists()
    mount_dir = ctx.out_dir if is_extract else ctx.cwd

    for tool in fmt.dos_tools.split():
        (mount_dir / tool).write_bytes((DOS_APPS / tool).read_bytes())

    conf = mount_dir / "run.conf"
    conf.write_text(CONF_TEMPLATE.format(mount_dir=mount_dir, dos_cmd=cmd))

    short = mount_dir / ctx.dos_archive
    done = mount_dir / "DONE.FLG"
    dosbox = (f"dosbox-x -conf {shlex.quote(str(conf))} -fastlaunch -nogui "
              f">/dev/null 2>&1")

    if is_extract:
        pre = f"cp {shlex.quote(str(ctx.archive))} {shlex.quote(str(short))} && "
        post = f" && test -f {shlex.quote(str(done))}"
    else:
        pre = ""
        post = (f" && test -f {shlex.quote(str(done))} "
                f"&& mv {shlex.quote(str(short))} {shlex.quote(str(ctx.archive))}")

    return f"{pre}{dosbox}{post}", {"SDL_VIDEODRIVER": "dummy"}
