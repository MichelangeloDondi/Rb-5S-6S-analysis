"""
Lever cross-check for beta_self (module M4d) -- a lever-limited cross-check, NOT the headline
===================================================================

This is the packaged, single-call broadening result: the full 20-trace-per-
temperature joint fit run across the whole model-form matrix, returning ONE
headline beta_self per isotope carrying FOUR separately-sourced error bars,
exactly as the audit (docs/PLAN.md, RESULTS ledger) specifies.

What it does that the exploratory M4b `run_global_fit` does not:
  * runs the model-form matrix along BOTH axes (an L-shaped 3-cell grid --
    the (gaussian, per_block) corner is dropped because per_block fits are
    ~50x costlier and the axes are near-independent) --
        transit kernel : exp (Lehmann/Biraben cusp) vs gaussian (Voigt, no cusp)
        sigma sharing  : per_T (Model A) vs per_block (Model B);
    the beta spread across the cells IS the model-form error bar;
  * assembles the four error bars into one object:
        [1] statistical  -- the primary fit's joint covariance,
        [2] model-form   -- the 2x2 spread (transit axis + sharing axis),
        [3] confound/w0  -- the w0-band refit (the waist measurement band)
                            plus a leave-one-block-out robustness scan,
        [4] kernel       -- the extra homogeneous component held at zero
                            against what the kernel chain fits, added
                            2026-09-11 and the LARGEST of the four by a
                            factor of three, reported outside [2] because
                            [2] is a published number defined over three
                            cells (see GAMMA_L_MEASURED_MHZ below);
  * is PURE: it takes already-built blocks and only calls `fit_global`, so it
    is unit-testable on synthetic data (tests/test_lever_crosscheck.py injects a
    known beta and checks recovery). The block builder (manifest + ingest + the
    130 C density anchor) lives in scripts/run_lever_crosscheck.py.

The primary (headline) model is (exp, per_T) = the Lehmann cusp with one
sigma_laser(T) shared across the four peaks: the transit form is the published
one (docs/LITERATURE.md 3) and per-T sharing is M4c-CHECKED but not validated
(the chi2<1 test cannot discriminate; RESULTS.md C2). The other three
cells of the matrix exist to MEASURE how much the headline moves if either
modelling choice is wrong -- that movement IS the model-form error, not a hidden
assumption.

STILL a model-based cross-check, not the archival headline: absolute beta rides
on the OPEN w0 (the confound bar spans it), so the model-independent raw-width
BOUND (run_beta_self.py) stays the paper's headline number. The value here is
(a) the isotope test beta_85 vs beta_87, (b) turning the between-block laser
drift into a measured sigma_laser(T), and (c) an auditable, fully-bracketed
error budget the fixed-lock data will collapse.
"""

from __future__ import annotations

from typing import Dict, List

from .global_fit import fit_global
from .constants import W0_BAND_M, W0_MEASURED_M, transit_fwhm_from_w0
from .config import TRANSIT_FWHM_PLACEHOLDER_MHZ

# the 2x2 model-form matrix axes
TRANSIT_KINDS = ("exp", "gaussian")       # Lehmann cusp | Voigt (no cusp)
SIGMA_SHARINGS = ("per_T", "per_block")   # Model A | Model B
PRIMARY = ("exp", "per_T")                # the headline model (sharing CHECKED, not validated)
# L-shaped 3-cell model-form grid: the primary corner plus one step along each
# axis. Spans transit (exp->gaussian) and sharing (per_T->per_block) for the
# cost of a single expensive per_block fit; (gaussian, per_block) is omitted.
GRID_CELLS = (("exp", "per_T"), ("gaussian", "per_T"), ("exp", "per_block"))
# THE THIRD MODEL-FORM AXIS, ADDED 2026-09-11, and it moves beta further than
# the two above it put together. `gamma_l` is composite_profile's extra
# homogeneous Lorentzian component, ADDED into the homogeneous width rather
# than convolved. Every producer of this coefficient had left it at its default
# of zero, while results/kernel_k3.csv fits it free across the SAME density
# ladder and finds 0.315 to 0.449 MHz in every peak, weighted mean 0.398.
# Measured at that mean, the hierarchical coefficient moves from 0.0534 to
# 0.0057 and the per-peak values from 0.0131-0.0181 to 0.0054-0.0082, and the
# whitened chi-squared prefers it on all four (transit x sharing) forms by 28 to
# 46. The account is in this repository's private correction record, which
# is not published; the reader-facing half is
# docs/quantities/self-broadening.md section 4.
#
# IT IS A SEPARATE CELL AND NOT A FOURTH MEMBER OF `GRID_CELLS`, deliberately.
# `err_modelform` is a published number defined over the three cells above, and
# widening its DEFINITION in the same change that first measures the new axis
# would move a pushed figure without a reader being able to see which part
# moved. So the axis reports as `err_kernel`, beside the other two, and the
# surfaces are corrected against a number that is already in the file.
#
# ATTRIBUTION IS NOT SETTLED AND THIS CONSTANT DOES NOT SETTLE IT.
# run_kernel_k3.py's own header licenses only "a non-Gaussian homogeneous
# component"; whether it is instrumental or collisional is the K5 transfer
# triangle's question. The axis is an uncertainty either way, which is why it
# belongs in an error budget rather than in the central value.
# AND THE MEAN IS QUOTED HERE UNDER A CAVEAT TWO SURFACES STATE.
# docs/RESULTS.md and docs/BIG_PICTURE.md both say this inverse-variance mean
# is never written on its own, because the four per-peak values span 0.315 to
# 0.449 and a common scalar is neither rejected nor established, at a
# heterogeneity p of 0.097. What justifies a single value HERE is that this is
# a SCAN COORDINATE and not a reported quantity: the axis is walked from zero,
# the coefficient is linear along it, and the whitened chi-squared moves by 1.1
# across the whole fitted range, so no value inside that range is
# distinguishable from another (A193). The mean is where the axis is sampled,
# not what the kernel is claimed to be, and nothing downstream reports it.
# The name keeps MEASURED because the kernel chain does FIT this component
# and the value is its weighted mean. What the comment above withdraws is
# any claim that the width fit MEASURES it: that likelihood is flat, and
# its own minimum sits nearer 0.375 (A193).
GAMMA_L_MEASURED_MHZ = 0.398
KERNEL_CELL = ("exp", "per_T", GAMMA_L_MEASURED_MHZ)
# w0 confound band: transit_ref values from the CORRECTED transit<->w0 law at
# the wide edge / central prior / tight edge. DERIVED from the constants since
# v3.0.0 (was a parallel hard-coded (65,50,40) that had to be edited by hand
# whenever the prior moved, and silently went stale when it did).
W0_BAND_UM = (W0_BAND_M[1] * 1e6, W0_MEASURED_M * 1e6, W0_BAND_M[0] * 1e6)
W0_BAND_MHZ = tuple(round(transit_fwhm_from_w0(w * 1e-6, 110.0), 3) for w in W0_BAND_UM)


def _fit(blocks, transit_kind, sigma_sharing, transit_ref, T_ref_C,
         gamma_l: float = 0.0):
    """One cell of the grid. `gamma_l` defaults to zero, so every existing call
    is byte-identical and only the cell that asks for the axis moves."""
    return fit_global(blocks, transit_ref_mhz=transit_ref, T_ref_C=T_ref_C,
                      transit_kind=transit_kind, sigma_sharing=sigma_sharing,
                      gamma_l=gamma_l)


def lever_crosscheck_beta(blocks: List[Dict], *,
                    transit_ref_mhz: float = TRANSIT_FWHM_PLACEHOLDER_MHZ,
                    T_ref_C: float = 110.0, do_w0_band: bool = True,
                    do_loo: bool = True) -> Dict:
    """Run the lever cross-check for beta_self over `blocks`.

    blocks: the fit_global block dicts (peak, isotope, T_C, N_units, freqs,
    volts, law), typically 4 peaks x several temperatures x ~5 repeats.

    Returns one dict with the headline beta per isotope and the three error
    bars (see module docstring). do_w0_band / do_loo can be switched off to
    keep unit tests fast (they add ~3 and ~N extra fits respectively).
    """
    isos = sorted({b["isotope"] for b in blocks})

    # --- the model-form matrix: three cells spanning BOTH axes ---
    # The full 2x2 would add (gaussian, per_block), but the per_block fit is
    # ~50x more expensive (one sigma_laser per block = dozens of free widths)
    # and the two axes are near-independent, so the L-shaped 3-cell design
    # (share the exp/per_T corner) measures the transit axis AND the sharing
    # axis for the quantify of one per_block fit. (gaussian, per_block) is dropped.
    grid = {cell: _fit(blocks, cell[0], cell[1], transit_ref_mhz, T_ref_C)
            for cell in GRID_CELLS}
    prim = grid[PRIMARY]
    headline = {iso: prim["beta_by_isotope"][iso] for iso in isos}
    err_stat = {iso: prim["beta_err_by_isotope"][iso] for iso in isos}

    # model-form spread over the evaluated cells, and each axis in isolation
    # (so we can say WHICH modelling choice dominates -- the transit, in practice)
    modelform, transit_axis, sharing_axis = {}, {}, {}
    for iso in isos:
        allv = [grid[cell]["beta_by_isotope"][iso] for cell in GRID_CELLS]
        modelform[iso] = max(allv) - min(allv)
        transit_axis[iso] = abs(grid[("exp", "per_T")]["beta_by_isotope"][iso]
                                - grid[("gaussian", "per_T")]["beta_by_isotope"][iso])
        sharing_axis[iso] = abs(grid[("exp", "per_T")]["beta_by_isotope"][iso]
                                - grid[("exp", "per_block")]["beta_by_isotope"][iso])

    # --- the kernel axis, one step from the primary corner (2026-09-11) ---
    kern = _fit(blocks, KERNEL_CELL[0], KERNEL_CELL[1], transit_ref_mhz,
                T_ref_C, KERNEL_CELL[2])
    kernel_axis = {iso: abs(prim["beta_by_isotope"][iso]
                            - kern["beta_by_isotope"][iso]) for iso in isos}

    # --- confound/w0 band on the primary model (the dominant systematic) ---
    w0_range = {}
    if do_w0_band:
        band = {iso: [] for iso in isos}
        for tr in W0_BAND_MHZ:
            f = _fit(blocks, *PRIMARY, tr, T_ref_C)
            for iso in isos:
                band[iso].append(f["beta_by_isotope"][iso])
        w0_range = {iso: (min(band[iso]), max(band[iso])) for iso in isos}

    # --- leave-one-out on the primary model: TWO physically distinct scans ---
    # loo_peak  -- drop a whole PEAK: the robustness question ("does the
    #              993.4207 nm suspect peak drive beta?"). SHOULD be small; a
    #              large value would mean one peak is anomalous.
    # loo_temp  -- drop a whole TEMPERATURE: this REMOVES a chunk of the density
    #              lever, so a large value is EXPECTED (dropping the 110 C long-
    #              lever end of a 3-point sweep collapses the arm) and is a
    #              LEVER-LEVERAGE diagnostic, NOT a robustness failure. Reporting
    #              them separately stops the (benign) lever effect from masking
    #              the (meaningful) per-peak robustness.
    def _loo(field, fmt, detail=None):
        out = {iso: (0.0, "") for iso in isos}
        for val in sorted({b[field] for b in blocks}):
            sub = [b for b in blocks if b[field] != val]
            if len({b["isotope"] for b in sub}) < len(isos):
                continue
            try:
                f = _fit(sub, *PRIMARY, transit_ref_mhz, T_ref_C)
            except (RuntimeError, ValueError):
                continue
            if detail is not None:
                # full per-drop record (audit, 2026-07-12):
                # beta AND sigma_laser(T) with this group removed, so the reader
                # sees whether the suspect peak drives the coefficient or the
                # sigma_laser(T) trend -- not just the max |dbeta| headline.
                detail[fmt(val)] = {
                    "beta": {iso: f["beta_by_isotope"].get(iso) for iso in isos},
                    "sigma_laser_by_T": dict(f.get("sigma_laser_by_T", {})),
                }
            for iso in isos:
                if iso not in f["beta_by_isotope"]:
                    continue
                dd = abs(f["beta_by_isotope"][iso] - headline[iso])
                if dd > out[iso][0]:
                    out[iso] = (dd, fmt(val))
        return out

    loo_peak_detail: Dict = {}
    loo_peak = (_loo("peak", lambda v: f"peak {v}", detail=loo_peak_detail)
                if do_loo else {iso: (0.0, "") for iso in isos})
    loo_temp = _loo("T_C", lambda v: f"{v:.0f} C") if do_loo else {iso: (0.0, "") for iso in isos}

    return {
        "isotopes": isos,
        "primary": PRIMARY,
        "headline": headline,
        "err_statistical": err_stat,
        "err_modelform": modelform,       # grid max-min
        "err_transit": transit_axis,      # transit axis alone (dominant)
        "err_sharing": sharing_axis,      # sigma-sharing axis alone
        "err_kernel": kernel_axis,        # the extra homogeneous component, alone
        "kernel_cell": KERNEL_CELL,
        "kernel_beta": {iso: (kern["beta_by_isotope"][iso],
                              kern["beta_err_by_isotope"][iso]) for iso in isos},
        # THE CLAMP MUST BE VISIBLE. The coefficient is bounded below at zero and
        # reaches that bound at gamma_l = 0.449, which is inside the range the
        # kernel chain fits, so a cell one step further along this axis would
        # report 0.0000 with nothing saying it is a bound and not a value.
        "kernel_params_at_bound": kern["params_at_bound"],
        "kernel_chi2_red": kern["chi2_red"],
        "kernel_chi2_whitened": kern["chi2_whitened"],
        "primary_chi2_whitened": prim["chi2_whitened"],
        "w0_band": w0_range,              # (lo, hi) beta over transit_ref band
        "loo_peak": loo_peak,             # (largest |dbeta|, which peak) -- robustness
        "loo_peak_detail": loo_peak_detail,  # per-drop {beta, sigma_laser_by_T}
        "loo_temp": loo_temp,             # (largest |dbeta|, which T) -- lever leverage
        "grid": {f"{tk}|{sh}":
                 {iso: (grid[(tk, sh)]["beta_by_isotope"][iso],
                        grid[(tk, sh)]["beta_err_by_isotope"][iso]) for iso in isos}
                 for (tk, sh) in GRID_CELLS},
        "chi2_red": {f"{tk}|{sh}": grid[(tk, sh)]["chi2_red"]
                     for (tk, sh) in GRID_CELLS},
        "n_traces": prim["n_traces"],
    }
