"""Engine adapters: translate a registry command template into something the
host can execute (native shell, Wine, DOSBox, or a Node/wasm module).

Each adapter exposes prepare(fmt, cmd, ctx) -> (cmd, env_overrides).
`ctx` carries staging paths so adapters can marshal files if needed.
"""
from __future__ import annotations

from . import dosbox, native, wine

_ADAPTERS = {
    "native": native,
    "wine": wine,
    "dosbox": dosbox,
}


def prepare(fmt, cmd: str, ctx) -> tuple[str, dict]:
    try:
        adapter = _ADAPTERS[fmt.engine]
    except KeyError:
        raise NotImplementedError(f"engine {fmt.engine} not supported yet")
    return adapter.prepare(fmt, cmd, ctx)
