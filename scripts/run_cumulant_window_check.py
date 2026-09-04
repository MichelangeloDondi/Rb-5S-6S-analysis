#!/usr/bin/env python3
"""The windowed third cumulant's survival ratios, for THIS record's line.

WHY THIS PRODUCER EXISTS. The three-layer cumulant statement went through
three wrong quantifications in two days, and the last was a convention slip:
a survival band computed for a bare Cauchy of half-width gamma was quoted for
a line whose Lorentzian is Gamma_nat plus gamma_coll in FULL width, under a
laser and a transit kernel. Every kernel width below names its convention,
and every prose surface quotes these rows instead of a hand computation.

WHAT THE RATIO IS. kappa_3 of the observed line, windowed at +/-W about the
window's own mean (fixed point, twenty passes), divided by the ramp's own
kappa_3 = +S0^3/135. One at no truncation loss; below one when the window
clips the composite's tails; it can exceed one when a kernel is comparable
to the window, so the suppression is truncation-limited, not guaranteed.

    python scripts/run_cumulant_window_check.py        # a few seconds
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _producer_lock import take_producer_lock                     # noqa: E402
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s._compat import trapezoid as tz                        # noqa: E402
from rb5s6s.constants import GAMMA_NAT_HZ                         # noqa: E402
from rb5s6s.lineshape import model_grid_step_mhz, model_profile, stark_shift_S0_mhz   # noqa: E402

OUT = C.RESULTS_DIR / "cumulant_window_check.csv"

S0 = 3.0                 # MHz, the REFERENCE shift; the ratio depends on the shift through the fixed window's
                         # clipping of the composite's tails (the survival_vs_S0 rows measure it, no page derives it yet, and the reference rows name this shift) once
                         # the ramp is resolved on the model's grid (the row at the
                         # archive's shift read 0.478 under-resolved and 0.498 resolved)
W = 8.0                  # MHz, window half-width about the self-centre
SIGMA_LASER_FWHM = 1.6   # MHz FWHM (the twin's own laser kernel)
# MHz FWHM at the archive's 130 C from the measured waist, the value
# twin_realism.csv carries as TRUTH; the config placeholder is the same function
# at 110 C and the archive's line is not at 110 C. Never a literal (E15).
TRANSIT_FWHM = C.transit_fwhm_from_w0(C.W0_MEASURED_M, 130.0)
GAMMAS = (0.2, 0.55, 1.1)   # MHz, gamma_coll grid spanning the record's range
S0_2025 = round(float(stark_shift_S0_mhz(0.225, C.W0_MEASURED_M, rho=C.RHO_RETRO)), 3)   # the 2025 campaign's shift, sourced (0.364)
S0_GRID = (S0_2025, 1.0, 3.0)  # MHz: the archive's shift, one, the reference
# 160001 points and twenty fixed-point passes. At four passes the gc=0.55 ratio
# reads 0.60 and RISES with gamma at 80001 points and at 160001 alike, so that
# artefact, which this producer's own first run shipped and a cross-check
# caught, is the pass count and not the point count (measured 2026-09-04).
FINE = np.linspace(-40.0, 40.0, 160001)
COARSE = np.linspace(-40.0, 40.0, 80001)   # the self-check's ambient grid: the only
                                           # axis the bare-core rows respond to


GRID_STEPS = 48.0        # model grid steps per kernel AND per shift (resolve_shift): with the shift
                         # on the grid this sets the ramp's cell count at a small shift, and the
                         # self-check below halves the model grid and the ambient grid and doubles
                         # the window grid and the fixed-point passes
MIN_RAMP_CELLS = 32      # a floor on the ramp's cell count, not a convergence proof: at 32
                         # cells the reference row still sits 5e-4 from its fine-grid limit,
                         # so the self-check below is what asserts convergence (2026-09-04)
M_WINDOW = 32001         # points of the resampled window grid; the self-check
                         # below recomputes every row at twice this and refuses
                         # any row that moves beyond its printed precision


def _selfcentred_mean(y: np.ndarray, w: float, m_pts: int = M_WINDOW, passes: int = 20,
                      grid: np.ndarray | None = None) -> float:
    """The self-centred windowed mean on the resampled window: the fixed point
    of the first cumulant, iterated `passes` times (twenty converge it; four
    left it wrong by 2.0x and of the wrong sign, 2026-09-04). `grid` is the
    ambient grid `y` was built on, so a caller can vary that axis."""
    amb = FINE if grid is None else grid
    c = 0.0
    for _ in range(passes):
        g = np.linspace(c - w, c + w, m_pts)
        yy = np.clip(np.interp(g, amb, y), 0, None)
        yy = yy / tz(yy, g)
        c = tz(g * yy, g)
    return c


def _selfcentred_k3(y: np.ndarray, w: float, m_pts: int = M_WINDOW, passes: int = 20,
                    grid: np.ndarray | None = None) -> float:
    # The window is RESAMPLED onto its own uniform grid rather than masked on
    # FINE: a mask snaps both edges to grid points, and for a small windowed
    # moment that edge noise (about eps * W^3 * p(W)) swamped the physics --
    # the first committed S0 row read 2.19 where the converged value is 0.40,
    # and a half-step nudge of W flipped its sign. Twenty fixed-point passes,
    # because four left the mean-pull row wrong by 2.0x at the record's transit
    # (3.3x at the retired 1.8 MHz one).
    amb = FINE if grid is None else grid
    c = 0.0
    for _ in range(passes):
        g = np.linspace(c - w, c + w, m_pts)
        yy = np.clip(np.interp(g, amb, y), 0, None)
        yy = yy / tz(yy, g)
        c = tz(g * yy, g)
    g = np.linspace(c - w, c + w, m_pts)
    yy = np.clip(np.interp(g, amb, y), 0, None)
    yy = yy / tz(yy, g)
    m1 = tz(g * yy, g)
    return float(tz((g - m1) ** 3 * yy, g))


def _line(gc: float, full: bool, s0: float = S0, steps: float = GRID_STEPS,
          grid: np.ndarray | None = None) -> np.ndarray:
    # `grid` is the AMBIENT grid the line is built on. The bare-core variant
    # below never consults `steps` (it is not a model_profile call), so the
    # ambient grid is the only axis those rows respond to and the self-check
    # varies it for every row (2026-09-04).
    amb = FINE if grid is None else grid
    if full:
        return model_profile(amb, gamma_coll=gc,
                             sigma_laser_fwhm=SIGMA_LASER_FWHM,
                             transit_fwhm=TRANSIT_FWHM, s0=s0, resolve_shift=True,
                             grid_steps_per_kernel=steps)
    # the Lorentzian-alone variant, built directly: model_profile's zero-width
    # kernel path divides by zero (this producer's first run shipped 0.000
    # rows from exactly that), so the textbook case convolves an explicit
    # Lorentzian of HWHM (Gamma_nat + gc)/2 with the ramp on the same grid.
    h = (GAMMA_NAT_HZ / 1e6 + gc) / 2.0
    lor = (h / np.pi) / (amb ** 2 + h ** 2)
    ds = amb[1] - amb[0]
    ramp = np.where((amb >= -s0) & (amb <= 0.0), -2.0 * amb / s0 ** 2, 0.0)
    return np.convolve(lor, ramp, mode="same") * ds


def main() -> int:
    take_producer_lock("run_cumulant_window_check")
    ramp = S0 ** 3 / 135.0
    gnat = GAMMA_NAT_HZ / 1e6
    unrounded: dict[tuple[str, str], float] = {}   # the self-check compares these, not the printed cells
    rows = []
    for gc in GAMMAS:
        for full in (True, False):
            r = _selfcentred_k3(_line(gc, full), W) / ramp
            tag = "full_line" if full else "lorentzian_alone"
            unrounded[(f"survival_{tag}", f"gc{gc}")] = r
            rows.append([f"survival_{tag}", f"gc{gc}", f"{r:.3f}", "",
                         f"self-centred windowed kappa_3 over the ramp's own at the reference shift {S0:g} MHz, "
                         f"W {W:g} MHz, gamma_coll {gc} MHz. Lorentzian FWHM is "
                         f"Gamma_nat {gnat:.2f} plus gamma_coll (both MHz FWHM)"
                         + (f", laser {SIGMA_LASER_FWHM} MHz FWHM Gaussian, "
                            f"transit {TRANSIT_FWHM:.4f} MHz FWHM cusp" if full
                            else ", no laser, no transit: the derivation "
                                 "page's textbook case")])
    # the S0 grid at the middle gamma. The windowed kappa_3 and the ramp's own
    # both scale as S0^3, so the ratio is shift-independent to first order and carries the window's clipping beyond it (measured, not derived); a first version
    # read 0.478 at the archive's shift because the ramp sat on fewer than five
    # of the model's grid cells. At MATCHED grid alignment the error collapses on
    # the ramp's cell count: at 12, 24 and 48 whole cells the deviation from the
    # fine-grid limit agrees across a factor eight in the shift, where at a fixed
    # steps-per-kernel it differs thirtyfold (measured 2026-09-04). Off the whole
    # cells the ramp's edge phase enters too, and between three and twenty cells
    # the row oscillates rather than falling, so the first version's 4.6 cells sat
    # inside that oscillation. The ramp is resolved on the grid here, its cell
    # count is printed, and a row below MIN_RAMP_CELLS is refused rather than
    # written. That floor is a tripwire rather than a convergence proof, and
    # on the calls this file makes it cannot fire at all: with the shift on the
    # grid the count is at least GRID_STEPS, so it reaches 32 only below about
    # 0.03 MHz, where the grid step floor binds instead. The self-check below,
    # not that constant, is what asserts convergence.
    survival_at: dict[float, float] = {}
    for s0 in S0_GRID:
        dnu_model = model_grid_step_mhz(gamma_coll=0.55, sigma_laser_fwhm=SIGMA_LASER_FWHM,
                                        transit_fwhm=TRANSIT_FWHM, s0=s0, resolve_shift=True,
                                        grid_steps_per_kernel=GRID_STEPS)
        cells = s0 / dnu_model
        if cells < MIN_RAMP_CELLS:
            raise SystemExit(f"survival_vs_S0 at {s0}: the ramp spans {cells:.1f} model cells, below {MIN_RAMP_CELLS}; not written")
        r = _selfcentred_k3(_line(0.55, True, s0), W) / (s0 ** 3 / 135.0)
        survival_at[s0] = r
        unrounded[("survival_vs_S0", f"S0_{s0:g}")] = r
        rows.append(["survival_vs_S0", f"S0_{s0:g}", f"{r:.3f}", "",
                     f"full-line ratio at gamma_coll 0.55 MHz, same kernels and window, the ramp on "
                     f"{cells:.0f} model grid cells (resolve_shift, {GRID_STEPS:g} steps per kernel and per shift)"])
    # the two smallest shifts must agree: the ratio carries the fixed window's
    # clipping of the composite's tails, which grows with the shift (the survival_vs_S0 rows
    # measure it; no page derives it yet), so it is compared where the shift is
    # smallest; a gap here is the grid (0.478 against 0.497 on the
    # unresolved grid, 2026-09-04, which this assertion would have refused) or
    # the fixed window clipping more of the composite's tails as the shift grows, which the
    # print below sizes against the gate from the unrounded values; a much
    # narrower window would trip this gate on that physics rather than on the
    # grid, and the message would misname the cause (a reader derived the
    # condition, 2026-09-04)
    s_lo, s_mid = sorted(S0_GRID)[:2]
    gap = abs(survival_at[s_lo] - survival_at[s_mid]) / survival_at[s_mid]
    print(f"survival gap between S0 {s_lo:g} and {s_mid:g} MHz: {gap:.2e} relative, {gap / 0.01:.2f} of the gate")
    if gap > 0.01:
        raise SystemExit(f"survival at S0 {s_lo:g} and {s_mid:g} differ by {gap*100:.1f} per cent: the ramp is not resolved; not written")
    # the first-cumulant pull's own window effect, for the 03 clause: the
    # windowed mean pull against the exact -2 S0/3, SIGNED (positive is an
    # excess), on the resampled window with the same twenty fixed-point passes
    # as the third cumulant. Four masked passes gave 0.104 as a shortfall and
    # the sign was hidden by abs(): an unconverged fixed point read as a
    # deficit for four days (a reader replayed it, 2026-09-04).
    y = model_profile(FINE, gamma_coll=0.55, sigma_laser_fwhm=SIGMA_LASER_FWHM,
                      transit_fwhm=TRANSIT_FWHM, s0=S0, resolve_shift=True,
                      grid_steps_per_kernel=GRID_STEPS)
    c = _selfcentred_mean(y, W)
    excess = 100 * (c / (-2 * S0 / 3) - 1)
    unrounded[("kappa1_window_excess_pct", "gc0.55")] = excess
    rows.append(["kappa1_window_excess_pct", "gc0.55",
                 f"{excess:.3f}", "",
                 "per cent EXCESS of the windowed mean pull over the exact -2 S0/3 "
                 "(a negative value would be a shortfall), same window and kernels "
                 "as above, twenty fixed-point passes on the resampled window, "
                 "agreeing at twice the grid and passes to half the last digit. "
                 "Four masked passes gave 0.104 as a shortfall: the earlier route's "
                 "0.07 at the retired 1.8 MHz transit was this converged value, not "
                 "a different edge handling"])

    # THE CONVERGENCE SELF-CHECK: every row recomputed at half the model grid
    # step, half the ambient grid's density, twice the window grid and twice the
    # fixed-point passes, which is every axis any row responds to. It compares
    # the UNROUNDED value, because a comparison against the printed cell spends
    # the whole half-digit budget on rounding: it then passes a row that moved a
    # full digit, so a converged row whose printed cell happens to sit near a
    # rounding boundary is refused for the rounding alone. A row that moves
    # beyond half its printed
    # precision is a refusal, not a result. This producer's first committed run
    # shipped a sign-flipping grid-noise row because nothing asserted this.
    for r in rows:
        if not r[0].startswith(("survival_", "kappa1_")):
            continue
        if r[0] == "survival_vs_S0":
            s0v = float(r[1].split("_")[1])
            v2 = _selfcentred_k3(_line(0.55, True, s0v, 2 * GRID_STEPS, COARSE), W,
                                 2 * M_WINDOW - 1, 40, COARSE) / (s0v ** 3 / 135.0)
        elif r[0] == "kappa1_window_excess_pct":
            y2 = model_profile(COARSE, gamma_coll=0.55, sigma_laser_fwhm=SIGMA_LASER_FWHM,
                               transit_fwhm=TRANSIT_FWHM, s0=S0, resolve_shift=True,
                               grid_steps_per_kernel=2 * GRID_STEPS)
            v2 = 100 * (_selfcentred_mean(y2, W, 2 * M_WINDOW - 1, 40, COARSE) / (-2 * S0 / 3) - 1)
        else:
            gcv = float(r[1][2:])
            full = r[0].endswith("full_line")
            v2 = _selfcentred_k3(_line(gcv, full, S0, 2 * GRID_STEPS, COARSE), W,
                                 2 * M_WINDOW - 1, 40, COARSE) / (S0 ** 3 / 135.0)
        v1 = unrounded[(r[0], r[1])]
        if abs(v2 - v1) > 5e-4:   # half the last printed digit, unrounded on both sides
            raise SystemExit(f"UNCONVERGED: {r[0]}/{r[1]} moves "
                             f"{v1:.6f} -> {v2:.6f} at half the model grid, half the ambient grid, twice the window grid and twice the passes")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    for r in rows:
        print(f"  {r[0]:>28} {r[1]:>7} = {r[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
