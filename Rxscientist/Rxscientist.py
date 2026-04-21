"""Compatibility wrapper for legacy module path."""

import sys
from importlib import import_module

_impl = import_module("Rxscientist.Rxscientist")
sys.modules[__name__] = _impl

