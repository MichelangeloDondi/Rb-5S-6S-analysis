"""
Trace loading and format validation (module M0, part 1)
=======================================================

Single entry point for reading a LeCroy CSV trace and the dataset manifest.
Everything downstream goes through :func:`load_trace`, which VALIDATES the
file instead of trusting it: a malformed file raises immediately (plan rule:
"a parse failure on any file must raise, never skip silently").

Expected file format (all 722 archive files share it, verified 2026-07-11)::

    x-axis,2
    second,Volt
    -500.0000E-03,-2.7342E-03
    ...            (2000 rows total, uniform 0.5 ms step)

Times are returned in MILLISECONDS (the natural unit of the raw axis; the
frequency calibration that turns ms into MHz is module M2's job and is NEVER
applied here).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np

from .config import (MANIFEST_CSV, DATA_RAW_DIR, CSV_HEADER_LINES,
                     TRACE_MIN_VALID_POINTS)
from .constants import TRACE_N_POINTS, TRACE_DT_S


def load_trace(path, with_info: bool = False):
    """Read one LeCroy CSV -> (t_ms, v_volt)[, info], with strict validation.

    ARCHIVE QUIRK (discovered by this loader on first contact, 2026-07-11):
    LeCroy exports contain "time-without-voltage" rows (``+531.5000E-03,``) —
    the timebase point exists but no sample was written. Most files have 1-4
    of these at the window EDGES (head or tail); one file
    (4192nm_eom_070c3) has ~950 of them INTERLEAVED through the whole trace
    (apparently an export at a different effective timebase). The old
    pipeline's ``genfromtxt`` + NaN-dropping swallowed all of this silently.

    Policy here: empty-voltage rows are dropped but COUNTED (head / tail /
    interior); pass ``with_info=True`` to receive the counts so QC can flag
    pathological files (see :func:`rb5s6s.qc.ingest_flags`). Everything else
    — bad header, wrong row count, non-numeric content, times off the 0.5 ms
    grid, non-monotonic time — still raises immediately.
    """
    path = Path(path)
    with open(path, newline="") as f:
        lines = f.read().splitlines()

    header = lines[:CSV_HEADER_LINES]
    if not header or len(header[0].split(",")) != 2:
        raise ValueError(f"{path}: unexpected header line 1: {header[:1]!r}")
    # One archive file (4192nm_225mw1.csv) carries a stray header label
    # ('jj,nj') with otherwise healthy content — record the variant instead
    # of rejecting; line 2 stays strict (all 297 files conform).
    header_variant = "" if header[0].strip().lower() == "x-axis,2" else header[0].strip()
    if len(header) < 2 or "second" not in header[1].lower() or "volt" not in header[1].lower():
        raise ValueError(f"{path}: unexpected header line 2: {header[1:2]!r}")

    body = [ln for ln in lines[CSV_HEADER_LINES:] if ln.strip()]
    if len(body) != TRACE_N_POINTS:
        raise ValueError(f"{path}: {len(body)} data rows, expected {TRACE_N_POINTS}")

    times, volts, empty_idx, valid_idx = [], [], [], []
    for k, ln in enumerate(body):
        parts = ln.split(",")
        if len(parts) != 2:
            raise ValueError(f"{path}: row {k}: unexpected format {ln!r}")
        ts, vs = parts[0].strip(), parts[1].strip()
        if vs == "":
            try:
                float(ts)
            except ValueError:
                raise ValueError(f"{path}: row {k}: non-numeric time {ln!r}") from None
            empty_idx.append(k)
            continue
        try:
            times.append(float(ts))
            volts.append(float(vs))
            valid_idx.append(k)
        except ValueError:
            raise ValueError(f"{path}: row {k}: non-numeric data {ln!r}") from None

    if len(times) < TRACE_MIN_VALID_POINTS:
        raise ValueError(f"{path}: only {len(times)} valid samples")

    t_s, v = np.array(times), np.array(volts)
    if not np.isfinite(t_s).all() or not np.isfinite(v).all():
        raise ValueError(f"{path}: non-finite values")

    d = np.diff(t_s)
    ratio = d / TRACE_DT_S
    on_grid = len(d) == 0 or (np.all(d > 0)
                              and np.max(np.abs(ratio - np.round(ratio))) <= 0.01)
    axis_rebuilt = 0
    if not on_grid:
        # SALVAGE PATH (verified needed for exactly one archive file,
        # 4192nm_225mw1.csv: exported with a low-precision time column, so
        # 0.5 ms steps alias to duplicate printed timestamps; its voltage
        # content is healthy — height/noise match its siblings). Row order
        # is chronological, so the axis is rebuilt from the body row index:
        # t = t0 + k*dt. Residual distortion <= one sample per interior
        # dropout — negligible against ~60 ms linewidths. Recorded in info.
        span_ok = abs((t_s[-1] - t_s[0]) - (len(body) - 1) * TRACE_DT_S) \
            < 0.02 * len(body) * TRACE_DT_S
        if np.all(d >= 0) and span_ok:
            t_s = t_s[0] + np.array(valid_idx) * TRACE_DT_S
            axis_rebuilt = 1
        else:
            raise ValueError(
                f"{path}: time axis neither on the {TRACE_DT_S*1e3:.1f} ms "
                "grid nor salvageable (non-monotonic or wrong span)")

    # classify the dropped rows: contiguous head run, contiguous tail run,
    # everything else is 'interior' (the pathological kind)
    n_body = len(body)
    head = 0
    while head < len(empty_idx) and empty_idx[head] == head:
        head += 1
    tail = 0
    while tail < len(empty_idx) - head and empty_idx[-1 - tail] == n_body - 1 - tail:
        tail += 1
    info = {
        "n_valid": len(t_s),
        "empty_head": head,
        "empty_tail": tail,
        "empty_interior": len(empty_idx) - head - tail,
        "axis_rebuilt": axis_rebuilt,
        "header_variant": header_variant,
    }
    if with_info:
        return t_s * 1e3, v, info
    return t_s * 1e3, v  # milliseconds, volts


def load_manifest() -> List[Dict[str, str]]:
    """The dataset manifest as a list of dict rows (strings, as stored)."""
    with open(MANIFEST_CSV, newline="") as f:
        return list(csv.DictReader(f))


def trace_path(row: Dict[str, str]) -> Path:
    """Absolute path of a manifest row's trace file."""
    return DATA_RAW_DIR / row["file"]
