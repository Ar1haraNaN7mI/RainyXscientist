"""Compatibility: ``Rxscientist.Rxscientist`` is the implementation module.

Tests and monkeypatches target ``Rxscientist.Rxscientist.*``; aliasing
``sys.modules`` ensures they apply to ``Rainscientist.Rainscientist`` as well.
"""

from __future__ import annotations

import sys
from importlib import import_module

_impl = import_module("Rainscientist.Rainscientist")
sys.modules[__name__] = _impl
