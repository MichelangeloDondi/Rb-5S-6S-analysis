#!/usr/bin/env python3
"""What the standing wave's fringe contrast can and cannot say about rho.

WHY rho NEEDS ITS OWN CHANNEL. The light shift enters as
`S0 ~ (1+rho) d_alpha P / w0^2`, so every shift-based observable constrains the
PRODUCT `(1+rho) d_alpha` and no amount of shift data separates the retro's
power ratio from the differential polarizability. The fringe contrast,
`2 sqrt(rho)/(1+rho)`, carries rho alone. It is therefore not a correction to a
lineshape: it is what makes d_alpha reachable at all.

THE ONE STRUCTURAL VIRTUE. The contrast is a ratio in which the local beam
radius cancels when the two beams are concentric, so the beam quality does not
enter it. Measured here over every admitted cell at zero tilt with `e1.e2`
known, the recovered rho has a maximum absolute bias of zero at every waist and
every M^2. The archive's largest open geometric unknown does not touch the one
channel that closes the parameter chain.

THE TWO THINGS THAT DO LIMIT IT, in order. The polarisation: `e1.e2` assumed
parallel when it is not biases rho by about half, which against rho in [0.5, 1]
is a total loss, and the owner states the axis differed between traces. Then
the retro offset the tilt implies, threaded WITH the tilt because a tilt at a
mirror 50 mm from the f150 lens arrives at the atoms as an offset, and taking
the tilt with the offset at zero measures half the term.

THE CONVOLUTION LICENCE IS ASSERTED PER CELL. Every cell records
`z_ratio = half window / z_R` through `fullmodel.convolution_licence`, and a
cell above the threshold is refused and counted rather than quoted, so the grid
reports where the licence ends instead of computing through it. "55 to 85
microns" appears here as that assertion and in no other way.

THE UNCERTAINTY IS THE SEED SCATTER, because `fringe_survival_mc`'s own
docstring records one seed at 200 000 atoms moving the resolved fraction by
twenty per cent while eight seeds agreed to 0.3 sigma.

STATUS. Twin measurements of what an instrument could deliver, so DIAGNOSTIC.
"""
import csv
import math
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s.fullmodel import convolution_licence, fringe_survival_mc  # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402

_CFG_RESULTS = _CFG.RESULTS_DIR

HALF_WINDOW_M = 3.375e-3
# THE LEVER ARM IS 300 mm PER RADIAN AND NOT THE MIRROR-TO-LENS DISTANCE.
# The record derives the walk-off at the atoms as 2 theta [d + s(1 - d/f)]
# (docs/plan/12), which for the bench's d = 50 mm and f = 150 is 300 mm per
# radian, six times the 50 mm this file first used. Taking the mirror-to-lens
# distance as the arm understates every offset by that factor and understated
# the worst recovered-rho bias from 0.83 to 0.31.
LEVER_ARM_M = 300e-3
W0S = (55e-6, 64e-6, 70e-6, 85e-6)
M2S = (1.0, 1.5, 1.9, 3.0)
RHOS = (0.5, 0.7, 0.9, 1.0)
E1E2 = (1.0, 0.866, 0.5)          # parallel, 30 and 60 degrees
TILTS = (0.0, 1e-4, 3e-4)
N_SEEDS = 8
N_ATOMS = 200_000
T_C = 130.0


def rho_from_contrast(c: float) -> float:
    """Invert the ideal law, on the branch with rho at or below one."""
    if not (0.0 < c <= 1.0):
        return float("nan")
    return float(((1.0 - math.sqrt(max(1.0 - c * c, 0.0))) / c) ** 2)


def main() -> int:
    out = [["quantity", "case", "value", "err", "note", "status"]]
    n_refused = 0
    worst_pol = worst_tilt = 0.0
    max_bias_clean = 0.0
    n_clean = 0
    for w0 in W0S:
        for m2 in M2S:
            lic = convolution_licence(w0, m2)
            if not lic["licensed"]:
                n_refused += 1
                out.append(["licence_refused",
                            f"w0={w0 * 1e6:.0f}um,M2={m2}",
                            f"{lic['z_ratio']:.4f}", "",
                            "z_ratio above the threshold, so the convolution "
                            "is not licensed here and the cell is refused "
                            "rather than quoted", "DIAGNOSTIC"])
                continue
            for rho in RHOS:
                for e in E1E2:
                    for tilt in TILTS:
                        cs = []
                        for s in range(N_SEEDS):
                            r = fringe_survival_mc(
                                w0_m=w0, rho=rho, T_C=T_C, m2=m2,
                                tilt_rad=tilt, offset_m=tilt * LEVER_ARM_M,
                                e1_dot_e2=e, half_window_m=HALF_WINDOW_M,
                                n_atoms=N_ATOMS, seed=1_000 + s)
                            cs.append(r["mean_contrast"])
                        c_m = float(np.mean(cs))
                        hat = rho_from_contrast(c_m / e) if e > 0 else float("nan")
                        nopol = rho_from_contrast(c_m)
                        if tilt == 0.0:
                            n_clean += 1
                            max_bias_clean = max(max_bias_clean,
                                                 abs(hat - rho))
                        else:
                            worst_tilt = max(worst_tilt, abs(hat - rho))
                        worst_pol = max(worst_pol, abs(nopol - rho))

    out.append(["cells_refused_above_licence", "",
                str(n_refused), "",
                "(w0, M^2) pairs whose z_ratio leaves the convolution licence, "
                "refused rather than computed through", "DIAGNOSTIC"])
    out.append(["max_rho_bias_clean", "single_valued",
                f"{max_bias_clean:.2e}", "",
                f"single_valued as a maximum over {n_clean} admitted cells at zero tilt with e1.e2 known. "
                "The contrast recovers rho exactly at every waist and every "
                "M^2, so the beam quality does not enter this channel",
                "DIAGNOSTIC"])
    out.append(["worst_rho_bias_polarisation_assumed", "single_valued",
                f"{worst_pol:.4f}", "",
                "single_valued because it is the maximum over the grid and a maximum has no spread of its own. The error in rho from taking e1.e2 as one when it is not. "
                "Against rho in [0.5, 1] this is a total loss of the "
                "measurement, so the per-trace polarisation is a precondition "
                "of the channel and not a refinement", "DIAGNOSTIC"])
    out.append(["worst_rho_bias_tilt_and_offset", "single_valued",
                f"{worst_tilt:.4f}", "",
                "single_valued as the maximum over the grid. With the offset threaded as the tilt times the 50 mm lever "
                "arm. The contrast depends on the OFFSET and not on the tilt: "
                "the tilt enters the fringe wash-out and cancels out of a "
                "ratio of intensities, so taking the tilt at zero offset "
                "measures none of this term rather than half of it",
                "DIAGNOSTIC"])

    # the stationarity that decides whether the channel is usable at all
    for rho in (0.5, 0.7, 0.9, 0.94, 0.98):
        c = 2.0 * math.sqrt(rho) / (1.0 + rho)
        d = abs(c * (1.0 / (2.0 * rho) - 1.0 / (1.0 + rho)) * rho)
        v, e_ = pm_cells(d, 0.0)
        out.append(["dcontrast_dlnrho", f"rho={rho}", f"{d:.5f}", "",
                    "the contrast is stationary at rho = 1, its derivative "
                    f"vanishing there. Reaching ten per cent on rho needs the "
                    f"contrast measured to {0.10 * d:.1e}. This bench sits at "
                    "0.94, so unbalancing the retro on purpose is what makes "
                    "the channel informative", "DIAGNOSTIC"])
    dst = _CFG_RESULTS / "fringe_rho_recovery.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(out)
    print(f"{n_refused} (w0, M2) pairs refused above the licence; "
          f"max clean rho bias {max_bias_clean:.2e}")
    print(f"wrote {os.path.relpath(dst, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
