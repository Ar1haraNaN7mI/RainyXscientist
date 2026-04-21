"""Compatibility package exposing Rainscientist as Rxscientist."""

import sys
from importlib import import_module
from pathlib import Path

# Make `Rxscientist.*` resolve modules from the existing `Rainscientist` tree.
_ROOT = Path(__file__).resolve().parent.parent
__path__ = [str(_ROOT / "Rainscientist")]

# Mirror submodule names so unittest.mock.patch("Rxscientist.X") hits Rainscientist.X.
for _suffix in ("mcp", "mcp.client", "middleware"):
    _module = import_module(f"Rainscientist.{_suffix}")
    sys.modules[f"Rxscientist.{_suffix}"] = _module
    if "." not in _suffix:
        globals()[_suffix] = _module

# Single implementation module object for Rainscientist.Rainscientist / Rxscientist.Rainscientist / Rxscientist.Rxscientist.
_rs = import_module("Rainscientist.Rainscientist")
sys.modules["Rxscientist.Rainscientist"] = _rs
sys.modules["Rxscientist.Rxscientist"] = _rs
