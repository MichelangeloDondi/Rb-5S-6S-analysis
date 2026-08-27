#!/usr/bin/env python3
"""
Atomic saturation as a companion to the width-channel light-shift bound: the
probe that docs/notes/two_photon_saturation_companion.md is written from.

OPT-IN BY CONSTRUCTION. This script is not in run_all.sh, it writes no
results/*.csv and it changes no committed number. It exists because the note it
feeds was first produced by an in-session monkeypatch that was not preserved, so
the note's headline (the width-channel bound tightens from 0.6325 to about
0.23 MHz once saturation broadening is in the forward model) could not be re-run
by anyone, including its author. Everything the note quotes about the probe comes
from here now.

WHAT IT DOES, in four stages, the last opt-in.

Stage 1 rebuilds the two-photon Rabi frequency from bench quantities, printing
every intermediate, so the chain power -> intensity -> field -> coupling is
inspectable rather than asserted. It also prints the two combinations of the
forward and retro arms that the standing wave admits, because the shift and the
coupling take DIFFERENT ones (hyperpolarizability.two_photon_rabi_hz explains
why), and the two ratios of Omega to S0 that this project's two values of
Delta_alpha generate.

Stage 2 re-runs the C3d width-only bound with the saturation increment folded
into the model's own Lorentzian argument, at both ends of that ratio band. It
first runs UNPATCHED, which must reproduce the committed bound: that is the
check that the probe is driving production code and not a reimplementation.

Stage 3 reports on C3f, the joint three-session bound that outside documents
quote, and prints the analytic comparison at C3f's own bound, which fixes the
DIRECTION of the move without needing the fit.

Stage 4 runs it, behind --joint, because the joint fit reads two excluded data
trees from outside the repository and takes hours. Point RB5S6S_SESSION_20250704_DIR
and RB5S6S_SESSION_20250717_DIR at them. On 2026-08-09 this stage was reported as
impossible on the strength of the script's fallback path being empty, without
looking for the folders under their real names. They were present the whole
time.

THE INJECTED PHYSICS, stated so it can be attacked. The homogeneous
power-broadening law

    Gamma -> Gamma sqrt(1 + s),      s = 2 (Omega/2pi)^2 / Gamma^2

is used with the two-photon Rabi frequency and the natural FWHM, both as
frequencies, and the increment is added to gamma_coll. Folding it there is exact
rather than convenient: power broadening of a homogeneous line is Lorentzian and
Lorentzian widths add. What is NOT derived is the use of a two-level law for a
two-photon transition. It is standard, and the steady-state condition holds here
(the beam chord is about ten natural lifetimes), but it is an approximation, so
no committed bound moves on it.

    ./.venv/bin/python scripts/run_saturation_probe.py
    ./.venv/bin/python scripts/run_saturation_probe.py --joint
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import stark  # noqa: E402
from rb5s6s.constants import (C_M_PER_S,  # noqa: E402
                              DELTA_ALPHA_AU_ORSON2021,
                              EPS0_F_PER_M, GAMMA_NAT_HZ)
from rb5s6s.hyperpolarizability import (ATOMIC_FIELD_V_PER_M,  # noqa: E402
                                        HARTREE_HZ,
                                        two_photon_matrix_element,
                                        two_photon_rabi_hz)
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402
from rb5s6s.linefit import transit_fwhm_at_T  # noqa: E402
from rb5s6s.polarizability import delta_alpha  # noqa: E402

LAM_NM = 993.4192
P_MAX_W = 0.225
GAMMA_MHZ = GAMMA_NAT_HZ / 1e6

# C3f's committed numbers, read from the CSV rather than typed, so stage 3
# cannot quote a stale bound.
_C3F = "stark_joint.csv"


def _committed(name: str, quantity: str, key: str) -> float:
    for r in csv.DictReader(open(C.RESULTS_DIR / name)):
        if r["quantity"] == quantity and r["key"] == key:
            return float(r["value"])
    raise KeyError(f"{quantity}/{key} not in {name}")


def saturation_increment_mhz(s0_mhz: float, ratio: float) -> float:
    """The extra Lorentzian FWHM, in MHz, at a shift of s0_mhz.

    ratio converts the shift to the Rabi frequency and is field-independent
    (stage 1 prints where its two values come from). Returns 0 at s0 = 0, which
    is why both models agree where the production fit rails.
    """
    om_mhz = ratio * max(s0_mhz, 0.0)
    s = 2.0 * (om_mhz / GAMMA_MHZ) ** 2
    return GAMMA_MHZ * (math.sqrt(1.0 + s) - 1.0)


def ramp_increment_mhz(s0_mhz: float, gamma_coll: float, sigma_laser: float,
                       transit: float) -> float:
    """The ramp's own broadening at the same shift, through the fit's own code."""
    import numpy as np
    nu = np.arange(-45.0, 45.0, 0.01)
    return (stark._fwhm_of(gamma_coll, sigma_laser, transit, s0_mhz, nu)
            - stark._fwhm_of(gamma_coll, sigma_laser, transit, 0.0, nu))


# ---------------------------------------------------------------- stage 1
def stage1() -> dict:
    print("=" * 78)
    print("STAGE 1  the two-photon Rabi frequency, from the bench numbers up")
    w0 = C.W0_MEASURED_M
    rho = C.RHO_RETRO
    i_arm = 2.0 * P_MAX_W / (math.pi * w0 ** 2)
    e_arm_sq = 2.0 * i_arm / (EPS0_F_PER_M * C_M_PER_S)
    t_au = two_photon_matrix_element(LAM_NM)
    print(f"  P = {P_MAX_W*1e3:.0f} mW, w0 = {w0*1e6:.0f} um (measured), "
          f"rho = {rho}")
    print(f"  one arm, peak on axis:  I = {i_arm/1e4:.1f} W/cm^2, "
          f"E = {math.sqrt(e_arm_sq)/1e3:.1f} kV/m")
    print(f"  two-photon matrix element T = {t_au:.2f} a.u.")
    print()
    print("  the two combinations the retroreflected standing wave admits:")
    for label, e_sq, used_by in (
            ("arithmetic  (1+rho) E^2", (1.0 + rho) * e_arm_sq,
             "the AC-Stark shift (fringe mean of |E|^2)"),
            ("geometric  2 sqrt(rho) E^2", 2.0 * math.sqrt(rho) * e_arm_sq,
             "the Doppler-free coupling (the k-sum-zero term of E^2)")):
        m_hz = (e_sq / ATOMIC_FIELD_V_PER_M ** 2 / 4.0) * t_au * HARTREE_HZ
        print(f"    {label:26s} -> Omega/2pi = {2*m_hz/1e3:7.2f} kHz   {used_by}")
    contrast = 2.0 * math.sqrt(rho) / (1.0 + rho)
    print(f"    their ratio is the fringe contrast {contrast:.6f}, so at this "
          f"rho the\n    difference is {100*(1/contrast-1):.3f} per cent and no "
          f"digit moves. At rho = 0.75 it is\n    "
          f"{100*((1+0.75)/(2*math.sqrt(0.75))-1):.1f} per cent, which is why "
          f"the formula carries it.")
    om = two_photon_rabi_hz(P_MAX_W, w0, rho, LAM_NM)
    s0 = stark_shift_S0_mhz(P_MAX_W, w0, rho=rho)
    print()
    print(f"  ADOPTED  Omega/2pi = {om/1e3:.1f} kHz at the campaign maximum")
    print(f"  saturation parameter on axis s = "
          f"{2*(om/1e6/GAMMA_MHZ)**2:.4f} against Gamma = {GAMMA_MHZ:.4f} MHz")
    print()
    print("  the ratio of Omega to S0 is field-independent but NOT "
          "single-valued,\n  because two values of |Delta_alpha| are in play:")
    # STALE UNTIL 2026-08-26. This block was written when DELTA_ALPHA_AU
    # carried the CITED 1093, so "cited" against "this package's own" was a
    # real contrast. The 2026-08-24 adjudication made DELTA_ALPHA_AU the
    # record's own -1145, after which the branch labelled "cited" compared
    # that value with itself, and the printed gap read -200 per cent because
    # an abs() numerator sat over a signed denominator. Magnitudes on both
    # sides now, and the cited value read from its own constant.
    r_cited = 2.0 * t_au / abs(DELTA_ALPHA_AU_ORSON2021)
    r_module = 2.0 * t_au / abs(delta_alpha(LAM_NM))
    print(f"    cited  {abs(DELTA_ALPHA_AU_ORSON2021):.0f} a.u. "
          f"(constants.DELTA_ALPHA_AU_ORSON2021, Orson 2021) -> {r_cited:.4f}")
    print(f"    this package's own sum-over-states "
          f"{abs(delta_alpha(LAM_NM)):.1f} a.u.          -> {r_module:.4f}")
    print(f"    the gap is the documented "
          f"{100*(abs(delta_alpha(LAM_NM))/abs(DELTA_ALPHA_AU_ORSON2021)-1):.1f} "
          f"per cent Delta_alpha discrepancy, not a\n    convention error. "
          f"Stage 2 runs both ends. Direct check: Omega/S0 = "
          f"{om/(s0*1e6):.4f}.")
    return {"omega_hz": om, "s0_mhz": s0,
            "ratio_lo": min(r_cited, r_module), "ratio_hi": max(r_cited, r_module)}


# ---------------------------------------------------------------- stage 2
def _grid():
    grid = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "power_sweep.csv")):
        grid[(r["peak"], float(r["power_mW"]) / 1000.0)] = (
            float(r["fwhm"]), float(r["fwhm_err"]))
    return grid


def _run(grid, ratio: float | None):
    """fit_stark_sweep, optionally with the saturation term in the model.

    The patch wraps stark._fwhm_of, which is the single place the fit turns a
    shift into a width, so the shared kappa, the per-peak core re-minimization,
    the profile scan and the over-dispersion rescaling are all production code.
    """
    original = stark._fwhm_of
    if ratio is not None:
        def patched(gamma_coll, sigma_laser, transit, s0, nu):
            return original(gamma_coll + saturation_increment_mhz(s0, ratio),
                            sigma_laser, transit, s0, nu)
        stark._fwhm_of = patched
    try:
        return stark.fit_stark_sweep(grid)
    finally:
        stark._fwhm_of = original


def stage2(band: dict) -> None:
    print()
    print("=" * 78)
    print("STAGE 2  C3d, the width-only bound, with and without the companion")
    grid = _grid()
    committed = _committed("stark_sweep.csv", "S0_225mW_ub95_profile", "shared")
    rows = [("production, ramp only", None)]
    rows += [(f"with saturation, ratio {r:.4f}", r)
             for r in (band["ratio_lo"], band["ratio_hi"])]
    print(f"  committed S0(225) bound = {committed:.4f} MHz\n")
    print(f"  {'variant':34s} {'kappa (MHz/W)':>22s} {'S0(225) bound':>14s} "
          f"{'chi2_red':>9s}")
    base = None
    emitted = []
    for label, ratio in rows:
        res = _run(grid, ratio)
        b = res["S0_225_ub95_profile"]
        if ratio is None:
            base = b
            # the CSV carries three decimals, so compare at the printed digit
            flag = "  <- matches the committed value" if abs(
                round(b, 3) - committed) < 1e-9 else (
                "  <- MISMATCH, probe is not production")
        else:
            flag = f"  {base/b:.2f}x tighter"
        print(f"  {label:34s} {res['kappa']:+10.4f} +/- {res['kappa_err']:8.4f} "
              f"{b:14.4f} {res['chi2_red']:9.4f}{flag}")
        emitted.append({"label": label, "ratio": ratio, "bound": b,
                        "kappa": res["kappa"], "chi2_red": res["chi2_red"],
                        "factor": (base / b) if ratio is not None else None})
    return {"committed": committed, "rows": emitted}


# ---------------------------------------------------------------- stage 3
def stage3(band: dict) -> None:
    print()
    print("=" * 78)
    print("STAGE 3  C3f, the joint three-session bound: its direction, "
          "without the fit")
    try:
        k_ub = _committed(_C3F, "kappa_ub95", "primary")
        k_min = _committed(_C3F, "kappa_min", "primary")
    except (KeyError, FileNotFoundError) as exc:
        print(f"  cannot read the committed joint result: {exc}")
        return
    # Ask the paths rather than assert them. Until 2026-08-17 this message
    # stated the trees were absent on this machine as a fact, which is the same
    # mistake the module docstring records from 2026-08-09: they were present
    # under their real names the whole time.
    import run_stark_joint as _rsj
    _have = (_rsj.SESSION_20250704.is_dir() and _rsj.SESSION_20250717.is_dir())
    print("  The joint fit reads the 2025-07-04 rehearsal and the campaign-"
          "morning pilot\n  from two excluded trees outside this repository, "
          "and run_stark_joint.py\n  exits early when they are absent. On this "
          "machine they are "
          + ("PRESENT, so stage 4\n  can run: pass --joint.\n"
             if _have else
             "ABSENT, so the C3f bound\n  cannot be re-profiled here. Set "
             "RB5S6S_SESSION_20250704_DIR and\n  RB5S6S_SESSION_20250717_DIR "
             "and re-run.\n"))
    print()
    print("  What CAN be said without the data is the direction, because the "
          "mechanism\n  is arithmetic at C3f's own numbers. At its bound:")
    transit = transit_fwhm_at_T(130.0, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    for name, kap in (("profile minimum", k_min), ("95% bound", k_ub)):
        s0 = kap * P_MAX_W
        ramp = ramp_increment_mhz(s0, 0.60, 1.50, transit)
        for ratio in (band["ratio_lo"], band["ratio_hi"]):
            sat = saturation_increment_mhz(s0, ratio)
            print(f"    {name:16s} kappa = {kap:5.2f} MHz/W, S0(225) = "
                  f"{s0:.3f} MHz: ramp {ramp*1e3:6.1f} kHz, "
                  f"saturation {sat*1e3:6.1f} kHz, ratio {sat/ramp:5.2f}")
    print()
    print("  So the companion outgrows the ramp at C3f's bound as well, and by "
          "the same\n  factor stage 2 sees, which fixes the sign of the move: "
          "the joint bound must\n  TIGHTEN. Its SIZE will be smaller than "
          "stage 2's, because the joint fit\n  carries a gamma_coll prior that "
          "can absorb part of an added Lorentzian\n  width where the width-only "
          "fit cannot. Quoting a number for it before the\n  fit runs would be "
          "inventing one.")


# ---------------------------------------------------------------- stage 4
def stage4(band: dict) -> None:
    """The joint three-session bound, re-profiled with the saturation term.

    Stage 3 explains why this needs the two excluded trees. When they are
    reachable it runs here, patching `_shared_profile_grid` in the joint fit's
    own namespace, which is the single place that fit turns a shift into a
    profile, so the shared kappa, the per-peak priors, the per-trace centres and
    the chain seeding are all production code. It writes nothing: the committed
    results/stark_joint.csv is untouched, because only the two chains the primary
    bound needs are run and `main()` is never called.

    Two chains, the wing-variant minimum search and the primary seeded from it,
    are the fit's own documented order. Expect hours.
    """
    print()
    print("=" * 78)
    print("STAGE 4  C3f re-profiled with the companion (opt-in, hours)")
    sys.path.insert(0, str(ROOT / "scripts"))
    import run_stark_joint as rsj
    if not (rsj.SESSION_20250704.is_dir() and rsj.SESSION_20250717.is_dir()):
        print(f"  excluded trees not reachable at\n    {rsj.SESSION_20250704}\n"
              f"    {rsj.SESSION_20250717}\n  Set RB5S6S_SESSION_20250704_DIR and "
              f"RB5S6S_SESSION_20250717_DIR and re-run.")
        return
    ratio = band["ratio_lo"]        # the conservative end, as stage 2 uses
    original = rsj._shared_profile_grid

    def patched(gc, sl, transit, s0, *a, **k):
        return original(gc + saturation_increment_mhz(s0, ratio), sl,
                        transit, s0, *a, **k)

    priors = rsj.gc_priors()
    camp = rsj.load_campaign()
    reh, _ = rsj.load_session_20250704()
    _, prates = rsj.load_t_rates()
    pil = rsj.load_session_20250717(prates["4192"][0])
    traces = camp + reh + pil
    print(f"  {len(camp)} campaign + {len(reh)} rehearsal + {len(pil)} pilot "
          f"traces, ratio {ratio:.4f}")
    out = {}
    for label, inject in (("production", False), ("with saturation", True)):
        rsj._shared_profile_grid = patched if inject else original
        try:
            _, _, q_wing = rsj.bidi_profile(traces, priors, -1, True,
                                            f"{label[:4]}-C")
            prof, kmin, _ = rsj.bidi_profile(traces, priors, -1, False,
                                             f"{label[:4]}-A",
                                             seed=rsj.strip_wing(q_wing))
        finally:
            rsj._shared_profile_grid = original
        k_ub = rsj.ub95(prof)
        out[label] = (kmin, k_ub, k_ub * 0.225)
        print(f"  {label:18s} min kappa {kmin:6.2f}, 95% bound "
              f"{k_ub:6.3f} MHz/W -> S0(225) < {k_ub*0.225:.3f} MHz")
    if len(out) == 2:
        a, b = out["production"][2], out["with saturation"][2]
        print(f"\n  the joint bound moves {a:.3f} -> {b:.3f} MHz, a factor "
              f"{a/b:.2f}\n  (C3d moved by 2.8, and this one is expected to be "
              f"smaller because the\n  joint fit's gamma_coll prior can absorb "
              f"part of an added Lorentzian width)")
    print("  Nothing was written. results/stark_joint.csv is untouched.")



# ---------------------------------------------------------------- emission
def emit(stage2_out: dict) -> None:
    """Write the C3d half of this probe into results/, and ONLY that half.

    Added 2026-08-23. The script was opt-in and wrote nothing by design, and
    the consequence was that docs/RESULTS.md and README quoted its factors with
    no committed row behind them. The partition in unregenerated_claims.csv
    counted the 0.6325 MHz reproduction as the one ungoverned value reaching a
    reader-facing surface.

    WHAT IS WRITTEN: stage 2 only. It reads committed CSVs, re-runs production
    code, and carries its own check that the unpatched arm reproduces the
    committed bound, so it regenerates from a clean checkout.

    WHAT IS NOT, and this is the point: the JOINT factor. Stage 4 needs two
    data trees outside this repository and stage 3 says in terms that quoting a
    number for the joint bound before that fit runs would be inventing one. The
    joint factor is therefore recorded as a CLASSIFICATION with the date of the
    run that produced it, never as a value this producer computed. A row that
    cannot be regenerated here says so rather than carrying a digit.
    """
    import csv as _csv

    out = C.RESULTS_DIR / "saturation_companion.csv"
    rows = []

    def add(scope, quantity, value, unit, note):
        rows.append({"scope": scope, "quantity": quantity, "value": value,
                     "unit": unit, "note": note, "status": "DIAGNOSTIC"})

    add("C3d", "committed_bound_reproduced",
        f"{stage2_out['committed']:.4f}", "MHz",
        "the committed S0(225 mW) width-only bound, read from stark_sweep.csv "
        "and reproduced by the unpatched arm below. This IS the probe's check "
        "that it drives production code rather than a reimplementation")
    for r in stage2_out["rows"]:
        if r["ratio"] is None:
            add("C3d", "bound_ramp_only", f"{r['bound']:.4f}", "MHz",
                "the width-only bound with the ramp alone, this run. It must "
                "equal the committed value at the printed digit")
        else:
            key = f"bound_with_saturation_ratio_{r['ratio']:.4f}".replace(".", "p")
            add("C3d", key, f"{r['bound']:.4f}", "MHz",
                "the same bound with the saturation increment folded into the "
                "model's own Lorentzian argument, at this end of the "
                "Omega-over-S0 band. NOT a committed bound: the two-level law "
                "is standard and is an approximation for a two-photon "
                "transition, so nothing published moves on it")
            add("C3d", key.replace("bound_", "factor_"),
                f"{r['factor']:.2f}", "dimensionless",
                "how much tighter than the ramp-only arm. The pair of these is "
                "what documents quote as a factor of about 2.8")
    add("C3f", "joint_factor", "NEEDS_EXTERNAL_TREE", "classification",
        "the joint three-session bound tightens too, and BY HOW MUCH cannot be "
        "computed here: stage 4 reads two data trees outside this repository. "
        "A run on 2026-08-10 with those trees present reported 2.2, recorded in "
        "the companion note's postscript. It is NOT reproduced by this producer "
        "and is not carried here as a digit, because stage 3 states that "
        "quoting a joint number before the fit runs would be inventing one")

    with open(out, "w", newline="") as f:
        w = _csv.DictWriter(f, fieldnames=["scope", "quantity", "value",
                                           "unit", "note", "status"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nwrote {out} with {len(rows)} rows")


def main() -> int:
    band = stage1()
    stage2_out = stage2(band)
    stage3(band)
    if "--joint" in sys.argv:
        stage4(band)
    if "--emit" in sys.argv:
        emit(stage2_out)
    else:
        print()
        print("=" * 78)
        print("Nothing was written. Pass --emit to write the C3d half into "
              "results/saturation_companion.csv,\nwhich is what "
              "docs/RESULTS.md quotes. The joint factor is never written here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
