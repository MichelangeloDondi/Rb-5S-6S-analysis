"""Gate A: does the predicted Stark coefficient's band reach the record's bound?

Rung 2 -- every number here is propagated from stated inputs and none is fitted.
Writes results/prediction_band.csv with BOOLEAN verdicts the docs quote, so that
a threshold comparison is never re-made by eye at a different number of digits.

Two sides are carried, because the comparison has two:

  * the PREDICTION, kappa_pred, with the waist band (entering squared), the
    retro ratio, the polarizability spread between this record's value and
    Orson 2021, and a power calibration that is an OPEN apparatus item
    (docs/plan/12) and is spanned rather than assumed;

  * the BOUND, kappa_ub95, read from results/stark_joint.csv, corrected for the
    fluorescence collection window. That correction is ONE-SIDED: the axial
    window carries the ramp's shape moments toward zero, so a fit that assumes
    the pure transverse ramp reads the shift LOW and the correction RAISES the
    bound, easing any tension, which is the conservative direction for a claim
    of tension.

    THAT ONE-SIDEDNESS IS CONDITIONAL AND THE CONDITION IS EMITTED. The third
    moment falls monotonically with the window, but the variance reaches a
    minimum near z_ratio 0.79 and returns to the pure ramp's value at 1.69,
    above which the width-channel bias changes sign. This bench sits at 0.26,
    inside the region by a factor of six, and the row
    width_bias_sign_flip_z_ratio carries the limit so a later geometry is
    checked against it rather than assumed to inherit it.

The window itself is constants.collection_z_ratio() and the moments are
lineshape.ramp_moment_contributions(), which has carried the closed form since
2026-07-12 with its window flagged OPEN; this producer is the first consumer to
close it from the apparatus.
"""
import csv
import math

from rb5s6s import config as C
from rb5s6s.stark import kappa_pred_per_watt  # noqa: E402  (SSOT)
from rb5s6s import constants as K
from rb5s6s import lineshape  # noqa: E402
from rb5s6s.lineshape import ramp_moment_contributions

# TWO QUANTITIES UNDER ONE NAME, separated 2026-09-12. The
# 0.005 is the owner-stated drive STABILITY, repeatability at the meter.
# The meter-to-atoms CALIBRATION is a different quantity, docs/plan/12
# says it "is still owed", and it is NOT spanned by this band: nothing
# here carries it, and the band narrowed from 0.05 when the constant was
# retyped without the name changing. A forecast that needs the
# calibration spanned must widen this and say which quantity it used.
POWER_STABILITY_SPAN = 0.005   # owner-stated drive stability, 2026-09-11
#: THE CALIBRATION IS STILL OPEN AND IS STILL SPANNED. Replacing this 0.05 with
#: the stability figure narrowed the band from a half-width of 0.108 to 0.096
#: and moved worst_lo from 1.273 to 1.333 as it stood at 2026-09-11 -- in the direction that STRENGTHENS
#: this record's published tension against its own bound, which is the direction
#: a dropped uncertainty always moves a result and the reason it is the one to
#: check. docs/plan/12 says the meter-to-atoms chain "is still owed", so it is
#: spanned here and the two quantities are added in quadrature rather than one
#: being silently substituted for the other (2026-09-12).
POWER_CAL_OPEN_SPAN = 0.05
POWER_CAL_SPAN = (POWER_CAL_OPEN_SPAN ** 2 + POWER_STABILITY_SPAN ** 2) ** 0.5
_REF_Z = 1e-6             # the pure transverse ramp, as the moments helper takes it


def _pair(value: float, err: float) -> tuple[str, str]:
    """Format to LANGUAGE 8a.2: two significant digits on the uncertainty, and
    the value carrying the same decimals. Returns an empty err for err <= 0."""
    if err <= 0:
        return f"{value:.3f}", ""
    decimals = max(0, -int(math.floor(math.log10(abs(err)))) + 1)
    return f"{value:.{decimals}f}", f"{err:.{decimals}f}"


def _polarizability_upper_magnitude(default: float) -> float:
    """The largest |delta_alpha| this record's own value allows: the dynamic sum of
    results/polarizability_deep.csv plus its bar. Falls back to the package constant when the
    row is absent, and never returns less than it, so a missing file widens nothing
    silently in the direction that would flatter the prediction.

    Until 2026-09-17 this read the static-tail recompute's band in results/polarizability.csv,
    whose edge sat 18 a.u. above the value of record, so the band's upper edge rested on a
    replaced construction."""
    path = C.RESULTS_DIR / "polarizability_deep.csv"
    if not path.exists():
        return default
    with open(path) as fh:
        for row in csv.DictReader(fh):
            if row["quantity"] == "delta_alpha" and row["key"] == "at_drive":
                return max(abs(float(row["value"])) + abs(float(row["err"] or 0.0)), default)
    return default


def _moments(z_ratio: float) -> tuple[float, float]:
    m = ramp_moment_contributions(1.0, z_ratio=z_ratio)
    return m["excess_var"], m["mu3"]


def _bisect(fn, lo: float, hi: float, tol: float = 1e-7) -> float:
    """Deterministic root of a monotone sign change; no optimiser, no seed."""
    f_lo = fn(lo)
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if (fn(mid) > 0) == (f_lo > 0):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _argmax(fn, lo: float, hi: float, tol: float = 1e-6) -> float:
    """Golden-section maximum of a unimodal function; deterministic."""
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi
    c, d = b - phi * (b - a), a + phi * (b - a)
    while b - a > tol:
        if fn(c) > fn(d):
            b, c, d = d, b - phi * (d - a), c
        else:
            a, c, d = c, d, a + phi * (b - c)
        c, d = b - phi * (b - a), a + phi * (b - a)
    return 0.5 * (a + b)


def main() -> int:
    w0, (lo_w, hi_w) = K.W0_CENTRAL_M, K.W0_BAND_M
    rho, rerr = K.RHO_RETRO, K.RHO_RETRO_ERR
    # SSOT: one predicted coefficient per RECORDED watt, from `stark.kappa_pred_per_watt`,
    # which carries the modulator bore's on-axis factor. Until 2026-09-17 this computed the
    # bare shift and the record held four values of one quantity (F82, F83).
    k0 = kappa_pred_per_watt(w0, rho)
    # THE TIGHT EDGE (C6a, 2026-09-22): W0_BAND_M's low edge (40 um, the owner's ruling) sits below the
    # bore's floor (about 40.89 um, F291), where the bench convention refuses. An ENVELOPE edge is computed
    # the way stark.fit_stark_sweep computes its own band: the ideal relation at the band's edge times the
    # floor's on-axis factor (lineshape.aperture_onaxis_factor_actual's documented clamp for envelopes),
    # so the two prediction bands of this record agree. A FIT never does this.
    k_lo = (lineshape.stark_shift_S0_mhz(1.0, lo_w, rho=rho)
            * lineshape.aperture_onaxis_factor_actual(lo_w, clamp_floor=True))
    k_w = (kappa_pred_per_watt(hi_w, rho), k_lo)
    k_r = (kappa_pred_per_watt(w0, rho - rerr), kappa_pred_per_watt(w0, rho + rerr))
    da, da_orson = abs(K.DELTA_ALPHA_AU), abs(K.DELTA_ALPHA_AU_ORSON2021)
    # The band reaches DOWN to Orson's magnitude and UP to this record's own
    # err_hi84. Taking max(da, da_orson) for the upper edge gave da itself and
    # so no widening upward at all, which understated worst_hi by half a per
    # cent. The low edge is the one the verdict turns on and it is unchanged:
    # 1093 sits below this record's own 1139 and below the 1123 that the
    # one-sided tail-dispersion systematic of polarizability.csv allows.
    da_hi = _polarizability_upper_magnitude(default=da)
    f_a = (min(da, da_orson) / da, max(da, da_hi) / da)
    worst = (k_w[0] * (k_r[0] / k0) * f_a[0] * (1 - POWER_CAL_SPAN),
             k_w[1] * (k_r[1] / k0) * f_a[1] * (1 + POWER_CAL_SPAN))
    rel = math.sqrt(((k_w[1] - k_w[0]) / 2 / k0) ** 2 + ((k_r[1] - k_r[0]) / 2 / k0) ** 2
                    + ((f_a[1] - f_a[0]) / 2) ** 2 + POWER_CAL_SPAN ** 2)
    quad = (k0 * (1 - rel), k0 * (1 + rel))

    # --- the collection window, and the one-sided correction it puts on the bound
    z_c = K.collection_z_ratio()
    z_hi = K.collection_z_ratio(f_m=K.COLLECTION_LENS_F_M + K.COLLECTION_LENS_F_ERR_M,
                                image_dist_m=K.COLLECTION_IMAGE_DIST_M - K.COLLECTION_IMAGE_DIST_ERR_M,
                                w0_m=lo_w)
    z_lo = K.collection_z_ratio(f_m=K.COLLECTION_LENS_F_M - K.COLLECTION_LENS_F_ERR_M,
                                image_dist_m=K.COLLECTION_IMAGE_DIST_M + K.COLLECTION_IMAGE_DIST_ERR_M,
                                w0_m=hi_w)
    var_ref, mu3_ref = _moments(_REF_Z)
    var_c, mu3_c = _moments(z_c)
    # mu3_obs = mu3(shape) S0^3 and var_obs = mu2(shape) S0^2, so a fit that
    # assumes the reference shape recovers S0 scaled by the root of the ratio.
    bias_width = math.sqrt(var_c / var_ref) - 1.0
    bias_mu3 = (mu3_c / mu3_ref) ** (1.0 / 3.0) - 1.0
    z_null = _bisect(lambda z: _moments(z)[1], 0.5, 2.5)
    z_flip = _bisect(lambda z: _moments(z)[0] - var_ref, 1.2, 2.5)
    z_opt = _argmax(lambda z: abs(_moments(z)[1]) * math.sqrt(2 * math.atan(z) / math.pi), 0.05, 1.05)
    collected = 2 * math.atan(z_c) / math.pi
    # The non-convolution: the transit kernel goes as 1/w(z) and the axial
    # signal density as 1/(1+zeta^2), so its signal-weighted rms spread over
    # the window is the size of the error in treating the composite as f * L.
    kernel_mean, kernel_sq, weight = 0.0, 0.0, 0.0
    steps = 4001
    for i in range(steps):
        zeta = -z_c + 2 * z_c * i / (steps - 1)
        wgt = 1.0 / (1.0 + zeta * zeta)
        kernel = 1.0 / math.sqrt(1.0 + zeta * zeta)
        kernel_mean += wgt * kernel
        kernel_sq += wgt * kernel * kernel
        weight += wgt
    kernel_mean /= weight
    kernel_rms = math.sqrt(max(kernel_sq / weight - kernel_mean ** 2, 0.0)) / kernel_mean

    bound = None
    profile = []
    with open(C.RESULTS_DIR / "stark_joint.csv") as fh:
        for row in csv.DictReader(fh):
            if row["quantity"] == "kappa_ub95" and row["key"] == "primary":
                bound = float(row["value"])
            elif row["quantity"] == "profile_point":
                profile.append((float(row["key"]), float(row["value"])))
    assert bound is not None, "kappa_ub95 absent from stark_joint.csv; there is nothing to compare and that is not a pass"
    # HOW FAR THE PREDICTION SITS FROM THE DATA, read from the SAME profile the bound is read from (C6a, 2026-09-22).
    # At the calculated waist the band lies far above the bound, so the old sentence ("Delta chi2 running 4.1 to 5.7
    # across the envelope") has no cell behind it. The floor is rigorous without interpolation: the profile rises
    # monotonically above its minimum (asserted), so every point of the band at or above the profile's last point
    # below the band's worst low edge sits at least that point's Delta chi2 above the minimum.
    profile.sort()
    assert len(profile) >= 3, "stark_joint.csv carries no profile to read the prediction's distance from"
    chi_min = min(c for _, c in profile)
    k_at_min = min(profile, key=lambda p: p[1])[0]
    rising = [(k, c - chi_min) for k, c in profile if k >= k_at_min]
    assert all(b[1] >= a[1] for a, b in zip(rising, rising[1:])), (
        "the stark profile is not monotone above its minimum, so a floor read at one of its points bounds nothing")
    below = [p for p in rising if p[0] <= worst[0]]
    assert below, "no profile point lies at or below the band's worst low edge"
    k_floor, d_floor = below[-1]
    node = min(profile, key=lambda p: abs(p[0] - k0))
    d_central = node[1] - chi_min if abs(node[0] - k0) <= 0.01 else float("nan")
    bound_corr = bound / (1.0 + bias_width)      # the fit read low, so the bound rises
    w_meet = w0 * math.sqrt(k0 / bound)

    v_c, e_c = _pair(k0, k0 * rel)
    v_z, e_z = _pair(z_c, 0.5 * (z_hi - z_lo))
    rows = [
        ["kappa_pred", "central", v_c, e_c, "MHz/W, stark.kappa_pred_per_watt(W0_CENTRAL_M, RHO_RETRO), which is stark_shift_S0_mhz at one recorded watt times the aperture on-axis factor. ENVELOPE on the waist this record carries, err the quadrature half-width"],
        ["kappa_pred_band", "worst_lo", f"{worst[0]:.3f}", "", "MHz/W, every input at the edge that lowers kappa, power calibration spanned at POWER_CAL_SPAN. single_valued: a band edge is constructed from the corners of stated inputs, not summarised over a population, so it has no spread of its own"],
        ["kappa_pred_band", "worst_hi", f"{worst[1]:.3f}", "", "MHz/W, every input at the edge that raises kappa. single_valued: the opposite corner of the same construction, so the same reason applies"],
        ["kappa_pred_band", "quadrature_lo", f"{quad[0]:.3f}", "", f"MHz/W, inputs in quadrature, relative half-width {rel:.3f}"],
        ["kappa_pred_band", "quadrature_hi", f"{quad[1]:.3f}", "", "MHz/W"],
        ["bound", "kappa_ub95", f"{bound:.3f}", "", "MHz/W, read from results/stark_joint.csv, whose row carries the claim"],
        ["collection_window", "z_ratio", v_z, e_z, "half the imaged axial extent in Rayleigh ranges, constants.collection_z_ratio(). Err is the half-span of the f, image-distance and waist corners"],
        ["collection_window", "fluorescence_collected_frac", f"{collected:.3f}", "", "fraction of the emitted fluorescence inside the window, 2 arctan(z_ratio)/pi"],
        ["collection_window", "mu2_ratio", f"{var_c / var_ref:.4f}", "", "the windowed ramp's variance over the pure transverse ramp's. Below one, so the width channel reads low"],
        ["collection_window", "mu3_ratio", f"{mu3_c / mu3_ref:.4f}", "", "the same for the third moment"],
        ["collection_window", "shift_bias_width_pct", f"{100 * bias_width:.2f}", "", "per cent, SIGNED: the shift a pure-ramp fit recovers through the WIDTH channel. Negative means read low. The committed bound comes from a full profile likelihood, and its bias measured start-free on that channel matched this proxy to a hundredth of a per cent under the retired convention (private/cache/profile_bias_scan.py) and is owed again at the calculated waist, where the window is wider"],
        ["collection_window", "shift_bias_mu3_pct", f"{100 * bias_mu3:.2f}", "", "per cent, SIGNED: the same through the THIRD MOMENT, which is the campaign's channel"],
        ["collection_window", "transit_kernel_rms_spread_pct", f"{100 * kernel_rms:.2f}", "", "per cent, the signal-weighted rms spread of the TRANSIT kernel across the window, which is one of the two mechanisms and the axial one. It is NOT the size of the non-convolution: the saturation companion follows the local light shift and is radial, and results/kernel_inhomogeneity.csv measures the cost on the third moment at this same waist. This row bounds the transit spread and nothing else"],
        ["collection_window", "skew_null_z_ratio", f"{z_null:.3f}", "", "the window at which the ramp's third moment vanishes and reverses sign. A design limit on the collection path"],
        ["collection_window", "width_bias_sign_flip_z_ratio", f"{z_flip:.3f}", "", "the window above which the ramp's variance exceeds the pure transverse ramp's, so the width-channel correction changes sign and stops being conservative"],
        ["collection_window", "snr_optimum_z_ratio", f"{z_opt:.3f}", "", "the window maximising |mu3| sqrt(collected), the third moment's signal-to-noise"],
        ["bound", "kappa_ub95_window_corrected", f"{bound_corr:.3f}", "", "MHz/W, the bound divided by (1 + shift_bias_width_pct/100). The correction is one-sided and RAISES the bound, which eases any tension"],
        ["profile", "dchi2_floor_kappa", f"{k_floor:.2f}", "", "MHz/W, the profile's last point at or below the band's worst low edge, results/stark_joint.csv's profile_point rows. single_valued: a grid point of the profile, not an estimate"],
        ["profile", "dchi2_floor_over_band", f"{d_floor:.1f}", "", "chi2(kappa) - chi2(min) at that point, on the profile the bound itself is read from. The profile rises monotonically above its minimum, so every point of the predicted band sits at least this far above the minimum. single_valued: a difference of two points of one profile on the same data, which carries no fluctuation of its own"],
        ["profile", "wilks_sigma_floor_over_band", f"{math.sqrt(d_floor):.1f}", "", "the one-sided Wilks significance of that floor, sqrt(dchi2). single_valued: a function of the row above"],
        ["profile", "dchi2_at_central", "" if math.isnan(d_central) else f"{d_central:.1f}", "", "chi2(kappa) - chi2(min) at the profile's point within 0.01 MHz/W of the central prediction, blank when none is. single_valued: as above"],
        ["profile", "wilks_sigma_at_central", "" if math.isnan(d_central) else f"{math.sqrt(d_central):.1f}", "", "sqrt of the row above. single_valued: as above"],
        ["verdict", "worst_band_spans_bound", str(worst[0] <= bound), "", "boolean, quoted by the docs and never re-made by eye. single_valued: a verdict is one comparison of two numbers and cannot carry a distribution"],
        ["verdict", "quadrature_band_spans_bound", str(quad[0] <= bound), "", "boolean"],
        ["verdict", "worst_band_spans_corrected_bound", str(worst[0] <= bound_corr), "", "boolean, against the window-corrected bound. The comparison Gate A reports. single_valued: a verdict is one comparison of two numbers and cannot carry a distribution"],
        ["verdict", "window_past_skew_null", str(z_c >= z_null), "", "boolean. True would mean the collection window destroys the asymmetry the third moment reads"],
        ["verdict", "window_correction_is_conservative", str(z_c < z_flip), "", "boolean. The window-corrected bound only eases tension while this holds, and that is a property of the geometry and not of the data"],
        ["waist_at_bound", "w0_um", f"{w_meet * 1e6:.1f}", "", "um, the waist at which kappa_pred equals the bound, everything else central. Compare W0_CENTRAL_M"],
        # THE CONSERVATIVE EDGE IS A CELL, NOT A READER'S DIVISION (2026-09-22, the thesis session's
        # request, and the same discipline that refused a central prediction over a bound as a "factor"):
        # a chapter that leads with the closing waist should lead with the edge that closes SOONEST, which
        # is the band's own low corner, and it should read it rather than compute it.
        ["waist_at_bound", "w0_um_worst_lo", f"{w0 * math.sqrt(worst[0] / bound) * 1e6:.1f}", "",
         "um, the waist at which the band's WORST LOW edge equals the bound: the conservative closing waist, "
         "the one to quote when a single number is wanted. single_valued: a corner of the band, not a population"],
        ["waist_at_bound", "w0_um_worst_hi", f"{w0 * math.sqrt(worst[1] / bound) * 1e6:.1f}", "",
         "um, the same at the band's worst HIGH edge. single_valued: the opposite corner of the same construction"],
        ["sign", "delta_alpha", "negative" if K.DELTA_ALPHA_AU < 0 else "positive", "", "this record's sign convention. The ramp side rides on it (test_ramp_side_matches_the_polarizability)"],
    ]
    with open(C.RESULTS_DIR / "prediction_band.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["quantity", "key", "value", "err", "unit"])
        writer.writerows(rows)
    for r in rows:
        print(f"  {r[0]:<18} {r[1]:<32} {r[2]:>10} {r[3]:>8}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
