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
    cumulant falls monotonically with the window, but the variance reaches a
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
from rb5s6s import constants as K
from rb5s6s.lineshape import ramp_moment_contributions, stark_shift_S0_mhz

POWER_CAL_SPAN = 0.05     # OPEN apparatus item, spanned not assumed (docs/plan/12)
_REF_Z = 1e-6             # the pure transverse ramp, as the moments helper takes it


def _pair(value: float, err: float) -> tuple[str, str]:
    """Format to LANGUAGE 8a.2: two significant digits on the uncertainty, and
    the value carrying the same decimals. Returns an empty err for err <= 0."""
    if err <= 0:
        return f"{value:.3f}", ""
    decimals = max(0, -int(math.floor(math.log10(abs(err)))) + 1)
    return f"{value:.{decimals}f}", f"{err:.{decimals}f}"


def _polarizability_upper_magnitude(default: float) -> float:
    """The largest |delta_alpha| this record's own band allows, from
    results/polarizability.csv. Falls back to the package constant when the row
    is absent, and never returns less than it, so a missing file widens nothing
    silently in the direction that would flatter the prediction."""
    path = C.RESULTS_DIR / "polarizability.csv"
    if not path.exists():
        return default
    with open(path) as fh:
        for row in csv.DictReader(fh):
            if row["quantity"] == "delta_alpha_993":
                edges = [abs(float(row[k])) for k in ("value", "err_lo16", "err_hi84")]
                return max(max(edges), default)
    return default


def _moments(z_ratio: float) -> tuple[float, float]:
    m = ramp_moment_contributions(1.0, z_ratio=z_ratio)
    return m["excess_var"], m["kappa3"]


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
    w0, (lo_w, hi_w) = K.W0_MEASURED_M, K.W0_BAND_M
    rho, rerr = K.RHO_RETRO, K.RHO_RETRO_ERR
    k0 = stark_shift_S0_mhz(1.0, w0, rho=rho)
    k_w = (stark_shift_S0_mhz(1.0, hi_w, rho=rho), stark_shift_S0_mhz(1.0, lo_w, rho=rho))
    k_r = (stark_shift_S0_mhz(1.0, w0, rho=rho - rerr), stark_shift_S0_mhz(1.0, w0, rho=rho + rerr))
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
    var_ref, k3_ref = _moments(_REF_Z)
    var_c, k3_c = _moments(z_c)
    # k3_obs = kappa3(shape) S0^3 and var_obs = kappa2(shape) S0^2, so a fit that
    # assumes the reference shape recovers S0 scaled by the root of the ratio.
    bias_width = math.sqrt(var_c / var_ref) - 1.0
    bias_k3 = (k3_c / k3_ref) ** (1.0 / 3.0) - 1.0
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
    with open(C.RESULTS_DIR / "stark_joint.csv") as fh:
        for row in csv.DictReader(fh):
            if row["quantity"] == "kappa_ub95":
                bound = float(row["value"])
    assert bound is not None, "kappa_ub95 absent from stark_joint.csv; there is nothing to compare and that is not a pass"
    bound_corr = bound / (1.0 + bias_width)      # the fit read low, so the bound rises
    w_meet = w0 * math.sqrt(k0 / bound)

    v_c, e_c = _pair(k0, k0 * rel)
    v_z, e_z = _pair(z_c, 0.5 * (z_hi - z_lo))
    rows = [
        ["kappa_pred", "central", v_c, e_c, "MHz/W, stark_shift_S0_mhz(1 W, W0_MEASURED_M, RHO_RETRO). ENVELOPE on the waist this record carries, err the quadrature half-width"],
        ["kappa_pred_band", "worst_lo", f"{worst[0]:.3f}", "", "MHz/W, every input at the edge that lowers kappa, power calibration spanned at POWER_CAL_SPAN. single_valued: a band edge is constructed from the corners of stated inputs, not summarised over a population, so it has no spread of its own"],
        ["kappa_pred_band", "worst_hi", f"{worst[1]:.3f}", "", "MHz/W, every input at the edge that raises kappa. single_valued: the opposite corner of the same construction, so the same reason applies"],
        ["kappa_pred_band", "quadrature_lo", f"{quad[0]:.3f}", "", f"MHz/W, inputs in quadrature, relative half-width {rel:.3f}"],
        ["kappa_pred_band", "quadrature_hi", f"{quad[1]:.3f}", "", "MHz/W"],
        ["bound", "kappa_ub95", f"{bound:.3f}", "", "MHz/W, read from results/stark_joint.csv, whose row carries the claim"],
        ["collection_window", "z_ratio", v_z, e_z, "half the imaged axial extent in Rayleigh ranges, constants.collection_z_ratio(). Err is the half-span of the f, image-distance and waist corners"],
        ["collection_window", "fluorescence_collected_frac", f"{collected:.3f}", "", "fraction of the emitted fluorescence inside the window, 2 arctan(z_ratio)/pi"],
        ["collection_window", "kappa2_ratio", f"{var_c / var_ref:.4f}", "", "the windowed ramp's variance over the pure transverse ramp's. Below one, so the width channel reads low"],
        ["collection_window", "kappa3_ratio", f"{k3_c / k3_ref:.4f}", "", "the same for the third cumulant"],
        ["collection_window", "shift_bias_width_pct", f"{100 * bias_width:.2f}", "", "per cent, SIGNED: the shift a pure-ramp fit recovers through the WIDTH channel. Negative means read low. The committed bound comes from a full profile likelihood, and its bias measured start-free on that channel is -1.96 per cent against this proxy's -1.97 (private/cache/profile_bias_scan.py), flat across a factor of 5.5 in the shift"],
        ["collection_window", "shift_bias_k3_pct", f"{100 * bias_k3:.2f}", "", "per cent, SIGNED: the same through the THIRD CUMULANT, which is the campaign's channel"],
        ["collection_window", "transit_kernel_rms_spread_pct", f"{100 * kernel_rms:.2f}", "", "per cent, the signal-weighted rms spread of the transit kernel across the window. The size of the non-convolution the composite model neglects"],
        ["collection_window", "skew_null_z_ratio", f"{z_null:.3f}", "", "the window at which the ramp's third cumulant vanishes and reverses sign. A design limit on the collection path"],
        ["collection_window", "width_bias_sign_flip_z_ratio", f"{z_flip:.3f}", "", "the window above which the ramp's variance exceeds the pure transverse ramp's, so the width-channel correction changes sign and stops being conservative"],
        ["collection_window", "snr_optimum_z_ratio", f"{z_opt:.3f}", "", "the window maximising |kappa3| sqrt(collected), the third cumulant's signal-to-noise"],
        ["bound", "kappa_ub95_window_corrected", f"{bound_corr:.3f}", "", "MHz/W, the bound divided by (1 + shift_bias_width_pct/100). The correction is one-sided and RAISES the bound, which eases any tension"],
        ["verdict", "worst_band_spans_bound", str(worst[0] <= bound), "", "boolean, quoted by the docs and never re-made by eye. single_valued: a verdict is one comparison of two numbers and cannot carry a distribution"],
        ["verdict", "quadrature_band_spans_bound", str(quad[0] <= bound), "", "boolean"],
        ["verdict", "worst_band_spans_corrected_bound", str(worst[0] <= bound_corr), "", "boolean, against the window-corrected bound. The comparison Gate A reports. single_valued: a verdict is one comparison of two numbers and cannot carry a distribution"],
        ["verdict", "window_past_skew_null", str(z_c >= z_null), "", "boolean. True would mean the collection window destroys the asymmetry the third cumulant reads"],
        ["verdict", "window_correction_is_conservative", str(z_c < z_flip), "", "boolean. The window-corrected bound only eases tension while this holds, and that is a property of the geometry and not of the data"],
        ["waist_at_bound", "w0_um", f"{w_meet * 1e6:.1f}", "", "um, the waist at which kappa_pred equals the bound, everything else central. Compare W0_MEASURED_M"],
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
