"""The AC-Stark ramp sits on ONE side of the line, and the package states that side ONCE.

Owner order O27 (2026-09-17) put the ramp's density on [0, s0], the blue side, because this record's
differential polarizability is negative. The kernel was flipped that day and the flip was recorded as
complete; a population query found the old side still coded in `ramp_transit` (so two functions of
one package disagreed in sign for the same ramp), in two producers that built their own textbook
ramp, in a published figure that plotted the flipped kernel outside its own axis, and restated in
46 lines of 29 files, the derivation page's boxed result among them (F90, F92). A completion claimed from the sites in mind is
the defect; these two tests are the population.

Failure modes: a construction of the ramp whose odd moments disagree with `lineshape.RAMP_SIDE`; a
line in the tracked tree that restates the old side. A line that describes the old side AS history
carries `O27` or a date before the ruling, and is admitted.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import lineshape as L
from rb5s6s.constants import RHO_RETRO, W0_MEASURED_M

ROOT = Path(__file__).resolve().parents[1]


def test_every_construction_of_the_ramp_agrees_with_the_one_stated_side():
    side = L.RAMP_SIDE
    assert side in (+1.0, -1.0)
    # the kernel itself
    nu = np.linspace(-2.0, 2.0, 40001)
    f = L.stark_ramp(nu, 1.0)
    assert np.sign(float(np.sum(nu * f) / np.sum(f))) == side, "stark_ramp's mean"
    # the closed forms and the moment predictions the fit calls
    assert L.ramp_mean_over_s0() == pytest.approx(side * 2.0 / 3.0)
    m = L.ramp_moment_contributions(0.5, z_ratio=1e-6)
    assert np.sign(m["pull"]) == side, "ramp_moment_contributions' pull"
    assert np.sign(m["kappa3"]) == -side == np.sign(L.ramp_kappa3(0.5)), "the third cumulant opposes the side"
    a = L.stark_ramp_axial_moments(0.5, 0.05, n_grid=20001)
    mean_key = next(k for k in a if "mean" in k or "pull" in k)
    assert np.sign(a[mean_key]) == side, f"stark_ramp_axial_moments' {mean_key}"
    # the centroid of the composed profile moves toward the side as the shift grows
    grid = np.linspace(-30.0, 30.0, 12001)
    c = []
    for s0 in (0.0, 1.0):
        y = L.model_profile(grid, gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575, s0=s0,
                            resolve_shift=True)
        c.append(float(np.sum(grid * y) / np.sum(y)))
    assert np.sign(c[1] - c[0]) == side, "model_profile's centroid"
    # the transverse crossing and the fringe Monte Carlo, at their cheap settings
    from rb5s6s import fringe_tail as F, ramp_transit as R
    assert np.sign(R.TRIANGLE_MEAN_OVER_S0) == side
    mv = R.moving_atom_moments(0.5, n_b=101, n_t=8001)
    assert np.sign(mv["mean_over_s0"]) == side, "ramp_transit.moving_atom_moments"
    ft = F.fringe_tail_mc(w0_m=W0_MEASURED_M, s0_mhz=0.6, rho=RHO_RETRO, n_atoms=20000, seed=3)
    assert np.sign(ft["mean_over_s0"]) == side, "fringe_tail_mc"
    d = F.fringe_shift_density(w0_m=W0_MEASURED_M, rho=RHO_RETRO, coherence_s=F.COHERENCE_TRANSIT, n_atoms=20000, seed=3)
    x, y = np.asarray(d["x_grid"]), np.asarray(d["density"])
    assert float(y[np.sign(x) == side].sum()) / float(y.sum()) > 0.999, "fringe_shift_density's support"


#: The old side, as it was written. Each pattern names what it catches.
OLD_SIDE = [
    ("a grid from -s0 to 0", r"linspace\(\s*-\s*s0\w*\s*,\s*0(\.0)?\s*[,)]"),
    ("a support test on [-s0, 0]", r">=\s*-\s*s0\w*\s*\)\s*&\s*\(\s*\w+\s*<=\s*0"),
    ("a negative shift built from s0", r"\b(shift|s_env|s_signed|s)\s*=\s*-\s*s0"),
    ("the mean as -2/3 of the shift", r"(?<![\w.])[-−]\s*\(?\s*2(\.0)?\s*/\s*3(\.0)?\s*\)?\s*\*?\s*(S_?0|s_?0|S₀|kappa|κ)"),
    ("the third cumulant as +s0^3/135", r"\+\s*\(?\s*(S_?0|s_?0|S₀)\s*(\^|\*\*)\s*3\s*\)?\s*/\s*135"),
    ("the interval [-S0, 0]", r"\[\s*[-−]\s*(S_?0|s_?0|S₀|S_\{?0\}?)\s*,\s*0\s*\]"),
    ("the uniform mean as -s0/2", r"mean\s*=\s*[-−]\s*s0\s*/\s*2"),
    ("the mean as -2 s0/3", r"(?<![\w.])[-−]\s*2(\.0)?\s*\*?\s*(S_?0|s_?0|S₀|s0v)\s*/\s*3"),
    ("an analytic mean built as minus a sum", r"analytic\s*=\s*-\s*sum\("),
    # THE FOUR FORMS THE SCAN WAS BLIND TO (the physics seat, 2026-09-17). The flip of that
    # morning was recorded as complete while the derivation page's own boxed result, the axial
    # geometry tables and every statement of g1 still carried the red side, and NONE of the
    # patterns above could see them: a LaTeX fraction has no slash to match, a table cell has no
    # words around it, and g1 was not looked for at all. A guard blind to the notation its subject
    # is actually written in reads exactly like a guard that passes.
    ("the mean as -2/3 in a LaTeX fraction", r"[-\u2212]\s*\\[dt]?frac\{\s*2\s*\}\{\s*3\s*\}\s*S"),
    ("the third cumulant as +1/135 in a LaTeX fraction", r"\+\s*\\[dt]?frac\{\s*1\s*\}\{\s*135\s*\}"),
    ("the ramp's standardised skew stated positive", r"\+\s*\$?0\.56[0-9]"),
    ("the ramp's mean over s0 stated negative", r"[-\u2212]\s*\$?0\.6[67][0-9]"),
]
HISTORY = re.compile(r"O27|until 2026-09-17|before 2026-09-17")
SCOPE = ("rb5s6s", "scripts", "examples", "tests", "docs", "README.md")


def old_side_lines(files, reader=lambda f: (ROOT / f).read_text(encoding="utf-8", errors="ignore")):
    hits = []
    for f in files:
        try:
            lines = reader(f).splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            # A HISTORY MARKER COVERS THE BLOCK IT INTRODUCES, not only its own line: a table
            # whose caption says the rows were measured on the retired side cannot repeat the
            # marker in every cell, and demanding that is how a guard trains a reader to delete it.
            if any(HISTORY.search(x) for x in lines[max(0, i - 4):i]):
                continue
            for name, pat in OLD_SIDE:
                if re.search(pat, line):
                    hits.append(f"{f}:{i} [{name}] {line.strip()[:100]}")
                    break
    return hits


def _tracked():
    out = subprocess.run(["git", "ls-files", *SCOPE], cwd=ROOT, capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith((".py", ".md")) and not f.startswith("docs/history/")
            and f != "tests/test_ramp_sign_convention.py"]


def test_the_scan_catches_the_old_side_and_admits_it_as_history():
    planted = {
        "a.py": "ramp = np.where((amb >= -s0) & (amb <= 0.0), -2.0 * amb / s0 ** 2, 0.0)\n",
        "b.md": "$$\\boxed{f(s) \\propto |s|\\quad\\text{on}\\quad s\\in[-S_0,0]}$$\n",
        "c.md": "the mean pull -(2/3) S0 and the third cumulant +S0^3/135\n",
        "d.md": "the kernel was coded on [-S0, 0] until 2026-09-17, which O27 changed\n",
        "e.py": "s = RAMP_SIDE * np.linspace(0.0, s0, 400)\n",
        "f.py": "    excess = 100 * (c / (-2 * S0 / 3) - 1)\n",
    }
    hits = old_side_lines(planted, reader=lambda f: planted[f])
    names = sorted({h.split(":")[0] for h in hits})
    assert names == ["a.py", "b.md", "c.md", "f.py"], hits


def test_no_tracked_line_restates_the_old_side():
    hits = old_side_lines(_tracked())
    assert not hits, (f"{len(hits)} line(s) restate the ramp's old side; read lineshape.RAMP_SIDE or "
                      f"its closed forms, or mark a historical line with O27:\n  " + "\n  ".join(hits[:60]))
