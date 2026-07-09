"""DOSBox adapter: run DOS-era archivers under dosbox-x, headless.

The registry command is a DOS command line (8.3-safe, run from C:\\ which is
mounted on the staging input dir). We generate a conf whose [autoexec]
executes the command, drops a DONE.FLG sentinel, and exits the emulator.
Timings under CPU emulation are meaningless and are excluded from results;
only archive size and round-trip integrity are reported for tier D.
"""
from __future__ import annotations

import shlex
from pathlib import Path

CONF_TEMPLATE = """\
[sdl]
output=surface

[cpu]
core=dynamic
cycles=max

[autoexec]
MOUNT C "{mount_dir}"
C:
{dos_cmd} > RUN.LOG
ECHO done > DONE.FLG
EXIT
"""


def prepare(fmt, cmd: str, ctx) -> tuple[str, dict]:
    conf = ctx.staging / "dosbox.conf"
    conf.write_text(CONF_TEMPLATE.format(mount_dir=ctx.cwd, dos_cmd=cmd))
    shell_cmd = (
        f"dosbox-x -conf {shlex.quote(str(conf))} -fastlaunch -nogui "
        f"&& test -f DONE.FLG"
    )
    env = {"SDL_VIDEODRIVER": "dummy"}
    return shell_cmd, env
