"""
Lever cross-check for beta_self (module M4d) -- a lever-limited cross-check, NOT the headline
===================================================================

This is the packaged, single-call broadening result: the full 20-trace-per-
temperature joint fit run across the whole model-form matrix, returning ONE
headline beta_self per isotope carrying THREE separately-sourced error bars,
exactly as the audit (docs/PLAN.md, RESULTS ledger) specifies.

What it does that the exploratory M4b `run_global_fit` does not:
  * runs the model-form matrix along BOTH axes (an L-shaped 3-cell grid --
    the (gaussian, per_block) corner is dropped because per_block fits are
    ~50x costlier and the axes are near-independent) --
        transit kernel : exp (Lehmann/Biraben cusp) vs gaussian (Voigt, no cusp)
        sigma sharing  : per_T (Model A, M4c-validated) vs per_block (Model B);
    the beta spread across the cells IS the model-form error bar;
  * assembles the three error bars into one object:
        [1] statistical  -- the primary fit's joint covariance,
        [2] model-form   -- the 2x2 spread (transit axis + sharing axis),
        [3] confound/w0  -- the w0-band refit (the OPEN beam waist, dominant)
                            plus a leave-one-block-out robustness scan;
  * is PURE: it takes already-built blocks and only calls `fit_global`, so it
    is unit-testable on synthetic data (tests/test_lever_crosscheck.py injects a
    known beta and checks recovery). The block builder (manifest + ingest + the
    130 C density anchor) lives in scripts/run_lever_crosscheck.py.

The primary (headline) model is (exp, per_T) = the Lehmann cusp with one
sigma_laser(T) shared across the four peaks: the transit form is the published
one (docs/LITERATURE.md 3) and per-T sharing is M4c-validated. The other three
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
from .constants import transit_fwhm_from_w0
from .config import TRANSIT_FWHM_PLACEHOLDER_MHZ

# the 2x2 model-form matrix axes
TRANSIT_KINDS = ("exp", "gaussian")       # Lehmann cusp | Voigt (no cusp)
SIGMA_SHARINGS = ("per_T", "per_block")   # Model A (M4c-validated) | Model B
PRIMARY = ("exp", "per_T")                # the validated headline model
# L-shaped 3-cell model-form grid: the primary corner plus one step along each
# axis. Spans transit (exp->gaussian) and sharing (per_T->per_block) for the
# cost of a single expensive per_block fit; (gaussian, per_block) is omitted.
GRID_CELLS = (("exp", "per_T"), ("gaussian", "per_T"), ("exp", "per_block"))
# w0 confound band: transit_ref values from the CORRECTED transit<->w0 law at
# w0 = 65 / 50 / 40 um, bracketing the corrected-physics inference (~45-70 um,
# central 50). (Was (0.6,0.9,1.3) MHz mislabelled "w0 48/32/24 um" under the old
# ~2x-too-narrow transit; 32 um is now excluded -- see constants.W0_PRIOR_M.)
W0_BAND_UM = (65.0, 50.0, 40.0)
W0_BAND_MHZ = tuple(round(transit_fwhm_from_w0(w * 1e-6, 110.0), 3) for w in W0_BAND_UM)


def _fit(blocks, transit_kind, sigma_sharing, transit_ref, T_ref_C):
    return fit_global(blocks, transit_ref_mhz=transit_ref, T_ref_C=T_ref_C,
                      transit_kind=transit_kind, sigma_sharing=sigma_sharing)


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
    # axis for the price of one per_block fit. (gaussian, per_block) is dropped.
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
