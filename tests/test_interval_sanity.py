"""Committed intervals must actually be intervals.

WHY THIS EXISTS. On 2026-08-10 an uncertainty audit found that
results/global_dataset_fit.csv reported

    beta_self_min   0.0150
    beta_self_lo95  0.0150
    beta_self_hi95  0.0150

described in its own unit column as a "1-parameter 95% (dchi2 < 3.841)" interval.
The two edges were identical, so the interval had ZERO WIDTH, which is narrower
than the 0.01 grid step that produced it. The cause was a membership test rather
than a crossing: the edges were taken as the smallest and largest GRID POINTS
under the threshold, and where exactly one grid point qualified both edges landed
on it. The kappa bound in the same file already interpolated. Nothing noticed for
two releases because no check ever compared the two edges to each other.

The producer is fixed to interpolate both edges (run_global_dataset_fit._crossings).
This is the check that keeps it fixed, and it is deliberately a check on the
COMMITTED CSVs rather than on the code, because the defect was in a shipped number
and a reader reads the CSV.

Scope. It pairs any lo/hi rows sharing a quantity stem and key, whatever the
naming convention, and it also refuses a stated interval narrower than the grid
that could resolve it, which is the tell that caught this one.
"""
from __future__ import annotations

import csv
import re

import pytest

from rb5s6s import config as C

# lo/hi naming conventions in use across the ledger
_PAIRS = (("_lo95", "_hi95"), ("_lo68", "_hi68"), ("lo95_", "hi95_"),
          ("_lo", "_hi"))


def _rows():
    for path in sorted(C.RESULTS_DIR.glob("*.csv")):
        try:
            with open(path) as fh:
                head = next(csv.reader(fh))
        except (StopIteration, OSError):
            continue
        if "quantity" not in head or "value" not in head:
            continue
        with open(path) as fh:
            for r in csv.DictReader(fh):
                yield path.name, r


def _numeric(s):
    s = (s or "").strip()
    return float(s) if re.fullmatch(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", s) else None


def test_no_committed_interval_has_zero_or_negative_width():
    """Every lo/hi pair in the ledger must satisfy hi > lo."""
    seen = {}
    for fname, r in _rows():
        q = (r.get("quantity") or "").strip()
        k = (r.get("key") or "").strip()
        v = _numeric(r.get("value"))
        if v is None:
            continue
        seen[(fname, q, k)] = v

    bad = []
    for (fname, q, k), v in sorted(seen.items()):
        for lo_tag, hi_tag in _PAIRS:
            if lo_tag not in q:
                continue
            partner = q.replace(lo_tag, hi_tag)
            hi = seen.get((fname, partner, k))
            if hi is None:
                continue
            if hi <= v:
                bad.append(f"{fname}: {q}={v} but {partner}={hi} "
                           f"(width {hi - v:+.6g}, must be positive)")
            break
    assert not bad, ("a committed interval is not an interval:\n  "
                     + "\n  ".join(bad))


def _partner(fname, quantity, key):
    """The value of `quantity` at `key` in the same file, or None."""
    for f2, r2 in _rows():
        if (f2 == fname and (r2.get("quantity") or "").strip() == quantity
                and (r2.get("key") or "").strip() == key):
            return _numeric(r2.get("value"))
    return None


@pytest.mark.parametrize("stem,default_step", [
    # the joint region's beta grid STARTS at linspace(0.005, 0.075, 8), step
    # 0.01, and the producer refines it down until the interval spans several
    # steps. Where the producer records the step it resolved on, read that;
    # 0.01 is the unrefined fallback. An interval narrower than the grid that
    # produced it is a membership artifact rather than a likelihood crossing,
    # which is the shape of the 2026-08-10 defect.
    ("beta_self", 0.01),
])
def test_a_stated_interval_is_not_narrower_than_its_own_grid(stem, default_step):
    for fname, r in _rows():
        q = (r.get("quantity") or "").strip()
        if q != f"{stem}_lo95":
            continue
        k = (r.get("key") or "").strip()
        lo = _numeric(r.get("value"))
        hi = _partner(fname, f"{stem}_hi95", k)
        if lo is None or hi is None:
            continue
        step = _partner(fname, f"{stem.split('_')[0]}_grid_step", k)
        if step is None:
            step = _partner(fname, "beta_grid_step", k) or default_step
        width = hi - lo
        assert width > step, (
            f"{fname}: {stem} 95% interval [{lo}, {hi}] is {width:.6g} wide "
            f"against a grid step of {step}. An interval no wider than the grid "
            f"resolving it is a membership test, not a crossing. Refine the "
            f"grid, do not widen the claim.")


def test_a_stated_interval_contains_its_own_point_estimate():
    """An interval that excludes its own best fit is reporting the wrong thing.

    WHY THIS EXISTS (2026-08-10, addendum 30). The zero-width interval above was
    fixed by interpolating the crossings, and the interpolated result was still
    wrong: [0.0150, 0.0151] on a quantity whose minimum three rows above it in
    the SAME FILE at the SAME KEY read 0.0150 and whose free joint fit read
    0.0183. Interpolating chi2 linearly understated the width by a factor of 14
    (a profile is quadratic about its minimum, so the locally linear variable is
    sqrt(dchi2)), and the 0.01 grid could not locate the minimum to better than
    half a cell. The tell that needs no knowledge of either cause: an interval
    that does not bracket its own point estimate. Pairs only within one file and
    one key, so two genuinely different constructions of the same coefficient
    are not required to agree.
    """
    bad = []
    for fname, r in _rows():
        q = (r.get("quantity") or "").strip()
        if not q.endswith("_lo95"):
            continue
        stem = q[: -len("_lo95")]
        k = (r.get("key") or "").strip()
        lo = _numeric(r.get("value"))
        hi = _partner(fname, f"{stem}_hi95", k)
        if lo is None or hi is None:
            continue
        for cand in (f"{stem}_min", stem, f"{stem}_best", f"{stem}_fit"):
            point = _partner(fname, cand, k)
            if point is None:
                continue
            if not (lo <= point <= hi):
                bad.append(f"{fname}: {cand}={point} at key '{k}' is outside "
                           f"its own 95% interval [{lo}, {hi}]")
            break
    assert not bad, ("a committed interval excludes its own point estimate:\n  "
                     + "\n  ".join(bad))
