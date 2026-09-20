"""The twin's bias on a windowed statistic, read from the window surface and never interpolated.

WHY THIS EXISTS (PLAN v2 Phase 2, 2026-09-18). The main aim subtracts the twin's bias from every
moment before it enters the joint fit ("using the twin to compute and factor out biases"), and until
this file nothing could: `scripts/run_ultra_joint.py` took its moments at windows 3.25, 6 and 12 MHz
while `results/window_surface.csv` was tabulated on 0.5, 1, 2, 3, 5, 8, 13 and 21, an EMPTY
intersection, so the surface was computed, climbed through its noise ladder, and read by nothing.
The windows agree (1, 2, 5 and 13 MHz quoted since 2026-09-19, with 3, 8 and 21 diagnostic, all on the surface's grid) and this is the one reader.

WHAT A BIAS IS HERE. At a noise level the surface carries, per (case, statistic), the replica mean of
the statistic over the twin's realisations and its standard error; at the noiseless level it carries
the statistic of the noise-free trace, the truth. The bias at a level is `mean(level) - truth`, and
its standard error is the replica mean's. It is subtracted ONCE from the data statistic, the
standard error added in quadrature, and both written as columns beside the result so the
subtraction is visible and reversible.

STATISTIC KEYS ARE `k<n>@<window>` (a cumulant, e.g. `k4@8`) OR `mu<n>@<window>` (a central
moment, e.g. `mu4@8`) AND THEIR RATIOS (owner order O33, 2026-09-20: central moments are the
producer's primary vector at fourth order and above, with the cumulant retained beside them as a
diagnostic). Both prefixes are read from the same surface files; a cell under one prefix says
nothing about the other, and each is looked up under its own key.

REFUSALS. A (case, statistic, level) absent from the surface RAISES `KeyError`: no interpolation
across windows, orders, conditions or levels, ever, because a bias read between cells is a number
nobody measured. A surface whose noiseless file and level file disagree on a case's existence is
refused the same way. The set-difference between the vector a producer reads and the surface's
cells is what Phase 2's DONE WHEN prints, through `missing()`.
"""
from __future__ import annotations

import csv
import pathlib
from typing import Dict, Iterable, Optional, Tuple


def _read(path: pathlib.Path) -> Dict[Tuple[str, str], Tuple[float, float]]:
    out: Dict[Tuple[str, str], Tuple[float, float]] = {}
    with pathlib.Path(path).open() as fh:
        for row in csv.DictReader(fh):
            q = row.get("quantity", "")
            if "@" not in q or not q.startswith(("k", "mu")):
                continue
            try:
                v = float(row["value"])
            except (KeyError, ValueError):
                continue
            try:
                e = float(row.get("err") or "nan")
            except ValueError:
                e = float("nan")
            out[(row["case"], q)] = (v, e)
    return out


class TwinBias:
    """The surface's bias table: one noiseless file and one file per noise level."""

    def __init__(self, noiseless: pathlib.Path, levels: Dict[float, pathlib.Path]):
        self.noiseless_path = pathlib.Path(noiseless)
        self.truth = _read(self.noiseless_path)
        self.levels: Dict[float, Dict[Tuple[str, str], Tuple[float, float]]] = {}
        for lvl, p in levels.items():
            self.levels[float(lvl)] = _read(pathlib.Path(p))
        if not self.truth:
            raise ValueError(f"{self.noiseless_path}: no k<n>@<window> rows; not a window surface")

    def bias(self, case: str, statistic: str, level: float) -> Tuple[float, float]:
        """(bias, standard error) of `statistic` (a key like 'k4@8' or 'mu4@8') for `case` at `level`.

        `level` 0 returns (0.0, 0.0) if the cell exists in the noiseless file (a noiseless trace has
        no bias by definition), and raises otherwise, so a missing case is never read as unbiased."""
        key = (str(case), str(statistic))
        if key not in self.truth:
            raise KeyError(f"no noiseless cell for {key} in {self.noiseless_path.name}")
        lvl = float(level)
        if lvl == 0.0:
            return 0.0, 0.0
        if lvl not in self.levels:
            raise KeyError(f"no surface at level {lvl:g}; the levels held are {sorted(self.levels)}")
        table = self.levels[lvl]
        if key not in table:
            raise KeyError(f"no cell for {key} at level {lvl:g}")
        mean, se = table[key]
        return mean - self.truth[key][0], se

    def missing(self, wanted: Iterable[Tuple[str, str]], level: float) -> list:
        """The (case, statistic) pairs a producer reads that the surface lacks at `level`: the
        set-difference Phase 2's DONE WHEN prints. Empty means every cell is there."""
        lvl = float(level)
        table = self.truth if lvl == 0.0 else self.levels.get(lvl, {})
        return sorted(k for k in set(tuple(w) for w in wanted) if k not in table or k not in self.truth)


def load(noiseless: pathlib.Path, levels: Optional[Dict[float, pathlib.Path]] = None) -> TwinBias:
    return TwinBias(noiseless, levels or {})
