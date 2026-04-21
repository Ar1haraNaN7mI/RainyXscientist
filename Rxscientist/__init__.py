"""Compatibility package exposing Rainscientist as Rxscientist."""

import sys
from importlib import import_module
from pathlib import Path

# Make `Rxscientist.*` resolve modules from the existing `Rainscientist` tree.
_ROOT = Path(__file__).resolve().parent.parent
__path__ = [str(_ROOT / "Rainscientist")]

# Provide eager aliases for commonly patched modules used in tests.
for _suffix in ("mcp", "mcp.client"):
    _module = import_module(f"Rainscientist.{_suffix}")
    sys.modules[f"Rxscientist.{_suffix}"] = _module
    if "." not in _suffix:
        globals()[_suffix] = _module

