"""
numpy compatibility layer.

`np.trapezoid` was introduced in numpy 2.0 (rename of `np.trapz`). Our
declared dependency floor is numpy>=1.24 (pyproject.toml), so resolve the
name at import time and use `rb5s6s._compat.trapezoid` everywhere.

Revision record (2026-07-11): the code called np.trapezoid directly while the
manifest promised numpy>=1.24, so it broke on numpy 1.24-1.26; CI installed
the latest numpy and did not catch it. This shim honors the declared floor,
and CI now runs a minimum-versions job.
"""

import numpy as np

trapezoid = getattr(np, "trapezoid", None) or np.trapz
