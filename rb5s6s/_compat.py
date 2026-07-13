"""
numpy compatibility layer.

`np.trapezoid` was introduced in numpy 2.0 (rename of `np.trapz`). Our
declared dependency floor is numpy>=1.24 (pyproject.toml), so resolve the
name at import time and use `rb5s6s._compat.trapezoid` everywhere.

Revision record (2026-07-11): the audit caught that the code called
np.trapezoid directly while the manifest promised numpy>=1.24 — on numpy
1.24-1.26 the entire physics core failed, and CI never noticed because it
silently installed the latest numpy. This shim honors the declared floor,
and CI now runs a minimum-versions job so the contract is actually tested.
"""

import numpy as np

trapezoid = getattr(np, "trapezoid", None) or np.trapz
