#!/usr/bin/env python
"""What every platform the campaign could use would deliver, on one page.

WHAT THIS ANSWERS. The record has forecast machinery for a warm vapour cell and
nothing that says what a magneto-optical trap, a molasses or a hollow-core
fibre would deliver, so every cold or guided sentence in the plan has been an
extrapolation. This walks `rb5s6s.platforms` over the standard set at each
platform's own sensible drive power and writes what a reader would want
before choosing: how many atoms are in the probe, how wide the line's
inhomogeneous terms are, what the observable is, and what the signal-to-noise
per second of wall clock comes to.

THE TWO THINGS IT EXISTS TO MAKE VISIBLE.

  * **A guided mode has no Rayleigh range.** Free space truncates a two-photon
    rate within about one z_R of the focus; a fibre does not, so its
    interaction length is the fibre. That one difference puts a vapour-filled
    kagome mode within a factor of a few of a whole vapour cell.

  * **A fibre is read in transmission, not in fluorescence**, so its signal is
    a small dip in a large number and its noise is the shot noise of the full
    beam. The two modes scale differently and the CSV carries the absorbed
    fraction so a reader can see whether the dip is reachable at all.

STATUS. Every trapped platform's density and temperature is a DESIGN FIGURE and
the rows are tagged ENVELOPE. Only the two cell rows use conditions this record
has measured. Nothing here models loading, trap lifetime, radial heating, or
technical intensity noise, and the absorption arm is therefore the optimistic
end of what a real transmission measurement achieves.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as CFG                      # noqa: E402
from rb5s6s import platforms as PL                    # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz       # noqa: E402
from rb5s6s.hyperpolarizability import two_photon_rabi_hz  # noqa: E402
from rb5s6s import constants as C                     # noqa: E402

OUT = Path(CFG.RESULTS_DIR) / "platform_twins.csv"
RHO = 0.94
INTEGRATION_S = 1.0

#: The drive power each platform is evaluated at, and why it is not uniform.
#: The cell rows use the archive's own top rung. The trapped rows use 20 mW,
#: which A160 identified as the ceiling that keeps the probe's own dipole
#: potential well below the sample temperature; running them at 225 mW would
#: quote a number for atoms the probe has captured.
POWER_W = {"cell_130C": 0.225, "cell_130C_tight": 0.225, "mot": 0.020,
           "molasses": 0.020, "hcpcf_warm": 0.020, "hcpcf_cold": 0.020,
           "onf": 0.001}


def rows():
    out = []
    for key, p in PL.PLATFORMS.items():
        pw = POWER_W[key]
        sn = PL.signal_and_noise(pw, p, INTEGRATION_S, RHO)
        omega = two_photon_rabi_hz(pw, p.w0_m, RHO)
        sat = 2.0 * (omega / C.GAMMA_NAT_HZ) ** 2
        uncapped = PL.GAMMA_POP_PER_S * PL.excited_fraction(pw, p, RHO)
        capped = PL.excitation_rate_per_atom(pw, p, RHO)
        out.append(dict(
            platform=key, kind=p.kind, detection=p.detection,
            guided=int(p.guided),
            temperature_k=f"{p.temperature_k:.6g}",
            density_cm3=f"{p.density_cm3:.6g}",
            w0_um=f"{p.w0_m * 1e6:.3f}",
            power_mw=f"{pw * 1e3:.1f}",
            length_eff_mm=f"{PL.effective_length_m(p) * 1e3:.4f}",
            n_atoms_probe=f"{PL.atoms_in_probe(p):.6g}",
            transit_fwhm_mhz=f"{PL.transit_fwhm_mhz(p):.6g}",
            s0_mhz=f"{stark_shift_S0_mhz(pw, p.w0_m, rho=RHO):.6g}",
            saturation_s=f"{sat:.6g}",
            rate_per_atom_two_level=f"{uncapped:.6g}",
            rate_per_atom=f"{capped:.6g}",
            # WHAT THE CASCADE DOES, not whether a cap fired. The retired
            # column was `cascade_cap_binds` and read ZERO on every row, because
            # the model took a minimum against a ceiling that sat ABOVE the
            # two-level one and so never selected it, while results/README.md
            # sold the pair as "with and without the cascade dead-time
            # ceiling". The cascade is a saturation renormalisation: it lowers
            # every rate, by one to two per cent at weak drive and by thirty at
            # the saturated rows, and this column is that fraction.
            cascade_reduction=f"{1.0 - capped / uncapped:.4f}",
            events_per_s=f"{sn['events_per_s']:.6g}",
            absorbed_fraction=("" if sn["absorbed_fraction"] != sn["absorbed_fraction"]
                               else f"{sn['absorbed_fraction']:.6g}"),
            snr_per_s=f"{sn['snr']:.6g}",
            note=p.note,
        ))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plant", action="store_true",
                    help="re-runnable determinism and physics plant")
    args = ap.parse_args()
    if args.plant:
        return plant()
    data = rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)
    # not relative_to(ROOT): the output directory is redirectable through
    # RB5S6S_RESULTS_DIR and relative_to raises outside the repository, which
    # killed this producer under the freshness verifier's isolation.
    try:
        shown = os.path.relpath(OUT, ROOT)
    except ValueError:
        shown = OUT
    print(f"wrote {shown} with {len(data)} rows")
    for r in data:
        print(f"  {r['platform']:18s} {r['detection']:12s} "
              f"L={float(r['length_eff_mm']):8.3f} mm  "
              f"N={float(r['n_atoms_probe']):11.3e}  SNR/s={float(r['snr_per_s']):.3e}")
    return 0


def plant() -> int:
    """Three checks, each against something outside this module.

    1. DETERMINISM: two builds are byte-identical. There is no RNG here, so
       this guards against dict ordering and float formatting drift.
    2. THE SATURATION PARAMETER reproduces the record's own published value at
       the archive's waist, 0.033, which is computed by a different route in
       `docs/RESULTS.md`. If this fails the Rabi chain has moved.
    3. THE GUIDED BRANCH really ignores the Rayleigh range: a fibre's effective
       length must equal its physical length and must NOT equal z_R.
    """
    fails = []
    a, b = rows(), rows()
    if a != b:
        fails.append("determinism: two builds differ")

    p = PL.PLATFORMS["cell_130C"]
    om = two_photon_rabi_hz(0.225, p.w0_m, RHO)
    sat = 2.0 * (om / C.GAMMA_NAT_HZ) ** 2
    if not (0.030 < sat < 0.036):
        fails.append(f"saturation at the archive waist is {sat:.4f}, "
                     "the record publishes 0.033")

    f = PL.PLATFORMS["hcpcf_warm"]
    if abs(PL.effective_length_m(f) - f.length_m) > 1e-12:
        fails.append("guided length is not the fibre length")
    if abs(PL.effective_length_m(f) - PL.rayleigh_range_m(f.w0_m)) < 1e-6:
        fails.append("guided length coincides with z_R; the branch is not firing")

    free = PL.PLATFORMS["cell_130C_tight"]
    if abs(PL.effective_length_m(free) - PL.rayleigh_range_m(free.w0_m)) > 1e-9:
        fails.append("free-space length is not z_R-limited where it should be")

    print("platform plant:", "PASS" if not fails else "FAIL")
    for x in fails:
        print("  -", x)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
