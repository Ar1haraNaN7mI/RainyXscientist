"""Compatibility package exposing Rxscientist under the Rxscientist name."""

import sys
from importlib import import_module
from pathlib import Path

# Make `Rxscientist.*` resolve modules from the existing `Rxscientist` package tree.
_ROOT = Path(__file__).resolve().parent.parent
__path__ = [str(_ROOT / "Rxscientist")]

# Provide eager aliases for commonly patched modules used in tests.
for _suffix in ("mcp", "mcp.client"):
    _module = import_module(f"Rxscientist.{_suffix}")
    sys.modules[f"Rxscientist.{_suffix}"] = _module
    if "." not in _suffix:
        globals()[_suffix] = _module

