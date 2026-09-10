"""Where the composite model stops being a convolution, and by how much.

THE CONVOLUTION IS A CONDITION, NOT A FORM. S = f * L holds exactly when the
homogeneous kernel is the same at every collected volume element. Two things
break it at a tight waist, and they break it for the same reason:

  the transit kernel   its width goes as the inverse local beam radius, so it
                       varies along z as the beam diverges over the collected
                       length. Geometric, and already sized in the record at
                       1.0 per cent rms at 64 um and 47 at 16.

  the Lorentzian       gamma_nat + gamma_coll is uniform, but the SATURATION
                       COMPANION is not: stark.companion_gamma_mhz is keyed on
                       the LOCAL light shift, and the local light shift is the
                       ramp variable itself. So the homogeneous width is a
                       function of the same intensity that sets the shift, and
                       the two are perfectly correlated rather than
                       independent. At 16 um it runs 4.04 MHz at the beam edge
                       to 13.13 on axis, a factor of 3.25.

So the correct object is a MIXTURE over volume elements, each carrying its own
shift AND its own kernel:

    S(nu) = sum_i w_i V(nu - s_i ; Gamma(s_i), sigma_laser, transit(z_i))

with w_i the two-photon weight (intensity squared) times the collection
efficiency. The convolution is the special case Gamma and transit constant.
`lineshape.ramp_mixture` already mixes over s at a FIXED kernel, which is the
first half of this; what is missing is letting the kernel follow s.

WHAT THIS PRODUCER REPORTS, per waist: the fitted centre and the windowed
third cumulant under three models, the exact mixture, the fixed-kernel mixture
the code ships today, and the pure convolution, so the chapter can say what
each approximation costs where.

The (s, transit) plane is binned rather than looped element by element, since
Gamma depends on s alone and transit on z alone, so the mixture is a 2D
histogram and not a million Voigts.
"""
import csv
import math
import os

import numpy as np

from rb5s6s import constants as K
from rb5s6s import stark
from rb5s6s.constants import collection_z_ratio
from rb5s6s.cumulants import windowed_cumulants
from rb5s6s.linefit import fit_condition
from rb5s6s.lineshape import model_profile

# THE SPAN AND NOT THE GRID CARRIES THE PULL'S BIAS (2026-09-09). The first moment of a mixture of symmetric kernels is the density's own
# mean, kernel-independent by one line of algebra. At +-80 MHz the committed
# pull sat 0.039 MHz off that limit at 16 microns, four times its own error,
# because the Lorentzian wing is truncated; at +-160 it read -2.25485 and at
# +-320 both models returned the analytic -2.26187 exactly, so the -0.43 per
# cent "cost to the standard channel" was this producer's own truncation and
# not a physical cost. The span is now wide enough to reach the limit and the
# producer reports its movement rather than assuming it.
NU = np.linspace(-320.0, 320.0, 128001)
GAMMA_COLL = 0.55
SIGMA_LASER = 1.6
GAMMA_NAT = stark._GAMMA_MHZ    # the kernel's own, never a rounded copy
T_C = 130.0
POWER_W = 0.225
CASES = ((64e-6, 6.0), (40e-6, 6.0), (24e-6, 8.0), (16e-6, 12.0))
# N_Z was 36 until 2026-09-09. The per-axis bar added that day then
# refused the 40 micron case outright, the FIXED row's own axial movement being
# 5.10 per cent against a five per cent bar, which is the finding working: a
# combined halving had hidden it. The axial axis carries essentially all of the
# movement, so it is the one that is doubled.
N_S, N_Z = 140, 72
COMPANION_RATIO = 1.2367          # the record's own, stark.COMPANIONS["ratio"]


def _refuse_unless_isolated() -> None:
    """A producer run from a clone must not import the canonical package."""
    import rb5s6s as _pkg
    here = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir))
    pkg = os.path.realpath(_pkg.__file__)
    if not pkg.startswith(here + os.sep):
        raise SystemExit(f"REFUSING: rb5s6s resolves to {pkg}, outside {here}")


def volume_grid(w0_m, n_s=N_S, n_z=N_Z, l_scale=1.0):
    """The collected volume as a joint density over (local shift, transit).

    At fixed z the radial integral of the two-photon weight is the record's own
    ramp, dN/du proportional to u on [0, u_ax(z)] (docs/methods/03, and
    4b-bis's substitution t = 2r^2/w^2 makes it exact rather than fitted). The
    axial coordinate enters twice and differently: it lowers the on-axis shift
    as the beam expands, and it widens the transit kernel by the same beam
    radius. The collection window is the record's own half-length."""
    zR = math.pi * w0_m ** 2 / K.LAMBDA_LASER_M
    L = collection_z_ratio(w0_m=w0_m) * zR * l_scale
    s0 = stark.stark_shift_S0_mhz(POWER_W, w0_m, K.RHO_RETRO)
    z = np.linspace(-L, L, n_z)
    w_z = w0_m * np.sqrt(1.0 + (z / zR) ** 2)
    s_ax = s0 * (w0_m / w_z) ** 2              # intensity falls as 1/w^2
    transit = np.array([K.transit_fwhm_from_w0(float(w), T_C) for w in w_z])
    cells = []
    for iz in range(n_z):
        edges = np.linspace(0.0, s_ax[iz], n_s + 1)
        mid = 0.5 * (edges[:-1] + edges[1:])
        # dN/du proportional to u, normalised on this z-slice
        wgt = mid * np.diff(edges)
        # THE WEIGHT IS SATURATED BECAUSE THE KERNEL IS (2026-09-09). The
        # first draft weighted each element by the unsaturated
        # two-photon law while broadening it by the saturated companion, which
        # is the same inconsistency in one object: under the steady-state law
        # the record's companion note assumes, the line AREA falls by the same
        # root the width grows by. Omitting it overstated the pull by 20 per
        # cent at 16 microns, and the twin cannot see it because it injects and
        # recovers under one weight law.
        om = COMPANION_RATIO * mid
        wgt = wgt / np.sqrt(1.0 + 2.0 * (om / GAMMA_NAT) ** 2)
        # AND THE BETWEEN-SLICE HALF OF THE SAME LAW (2026-09-09, round two).
        # The line above dimmed each element, and the line that stood here then
        # renormalised the whole slice to the UNSATURATED collected signal per
        # unit z, which divides the dimming straight back out. Round one
        # saturated within a slice and left the mechanism one line under it.
        # Scaling the raw `u du` weight by the square of the local beam radius
        # over the waist reproduces that unsaturated slice total up to one
        # global constant, so the dimming survives and the slices keep their
        # relative areas: the waist slices, which are the broad AND the shifted
        # ones, stop being over-counted.
        # Measured at 16 microns: the waist-to-edge slice weight ratio falls
        # from 18.316 to 9.043, the pull from -2.073 to -1.804 MHz, and the k3
        # cost from 92.7 to 89.7 per cent.
        wgt = wgt * (w_z[iz] / w0_m) ** 2
        cells.append((mid, transit[iz], wgt))
    return cells, s0, L / zR


_KCACHE: dict = {}


def _kernel(gamma_coll, transit):
    """One composite kernel, cached on its two widths.

    The kernel's SHAPE depends on the two widths and not on where the element
    sits, so a shift is a translation of the same curve. Caching on a rounded
    pair turns five thousand convolutions into a few hundred, and the rounding
    is a tolerance the convergence check below has to clear."""
    key = (round(gamma_coll, 3), round(transit, 4))
    if key not in _KCACHE:
        _KCACHE[key] = model_profile(NU, gamma_coll=key[0],
                                     sigma_laser_fwhm=SIGMA_LASER,
                                     transit_fwhm=key[1], s0=0.0,
                                     gamma_nat_mhz=GAMMA_NAT)
    return _KCACHE[key]


def _mix(cells, kernel_of):
    """Accumulate w * K(nu - s) over the volume, K chosen by `kernel_of`."""
    out = np.zeros_like(NU)
    for mid, tr, wgt in cells:
        for s, w in zip(mid, wgt):
            if w <= 0.0:
                continue
            # THE SHIFT IS RED, so the element's line sits at MINUS s and the
            # kernel is sampled at nu + s. The first draft sampled at nu - s
            # and returned a mean pull of the right size with the wrong sign,
            # which the closed form -2 S0 / 3 caught on the first run.
            out += w * np.interp(NU + float(s), NU, kernel_of(float(s), float(tr)),
                                 left=0.0, right=0.0)
    return out / out.sum()


def profile_exact(cells, companion_scale=1.0):
    """Every element carries its own kernel: transit from its z, Lorentzian
    from its own shift through the saturation companion.

    `companion_scale` multiplies that companion so the row's real uncertainty
    axis can be swept; it is 1.0 for the reported value.

    THE SWEEP MOVES THE KERNEL ONLY, AND THE CALLER MUST MOVE THE WEIGHT
    (2026-09-09, round two). Width and area are one object under the law this
    file uses: the area falls by the same root the width grows by. A sweep that
    widened the kernel while the weight's Rabi ratio stayed at its nominal
    value produced a half-span over an object no physics makes, understating
    the k3 cost's own bar by 1.8 at 16 microns and overstating k3's by 1.7.
    `swept_cells` below rebuilds the volume at the swept ratio, so the two
    halves move together; this function is left scaling the kernel alone so
    that the two can still be separated when one wants them separated."""
    return _mix(cells, lambda s, tr: _kernel(
        GAMMA_COLL + companion_scale * stark.companion_gamma_mhz(s, "4192"), tr))


def swept_cells(w0_m, companion_scale, **kw):
    """The volume rebuilt with the saturation ratio scaled by the ROOT of
    `companion_scale`, which is the companion times that factor at small shift,
    so the weight's dimming and the kernel's width are one sweep."""
    root = float(np.sqrt(companion_scale))
    saved_mod, saved_ratio = COMPANION_RATIO, dict(stark.COMPANIONS or {})
    try:
        globals()["COMPANION_RATIO"] = saved_mod * root
        stark.COMPANIONS = {**saved_ratio, "ratio": saved_ratio["ratio"] * root}
        return volume_grid(w0_m, **kw)[0]
    finally:
        globals()["COMPANION_RATIO"] = saved_mod
        stark.COMPANIONS = saved_ratio


def profile_fixed_kernel(cells, s_bar, tr_bar):
    """The BEST fixed kernel: the shift mixed, the kernel held at the volume's
    own weighted mean. This is `ramp_mixture`'s assumption at its most
    charitable, and it is what the licence question deserves to be asked
    against."""
    g = GAMMA_COLL + stark.companion_gamma_mhz(s_bar, "4192")
    return _mix(cells, lambda s, tr: _kernel(g, tr_bar))


def profile_forecast_kernel(cells, s0, tr_waist):
    """The fixed kernel the SHIPPED twin composes with, which is a different
    one (2026-09-09, round two). `rb5s6s/forecast.py:318` keys the companion on
    the ON-AXIS peak shift, `s0 * sqrt(rate)`, and passes the waist transit,
    where the mean-shift row above uses the volume's weighted mean. For a ramp
    whose density goes as |s| the mean is two thirds of the peak, so the twin's
    companion sits above the charitable one and the cost it pays is larger.
    Quoting the mean-shift row as the forecast's own cost understates it."""
    g = GAMMA_COLL + stark.companion_gamma_mhz(s0, "4192")
    return _mix(cells, lambda s, tr: _kernel(g, tr_waist))


def fitted_centre(prof, transit, window):
    """What the CAMPAIGN's pull channel actually reads, which is not the
    centroid (2026-09-09, round two).

    `run_three_channel_forecast.py` inverts a FITTED centre: `fit_condition`
    with `s0=0`, a symmetric composite with one width and a free centre. The
    centroid's immunity is an algebraic fact about the first moment of a
    mixture of symmetric kernels and it does NOT transfer to a least-squares
    fit, because a single-width symmetric model sits on the mode, and the mode
    is set by the narrow unshifted elements while the mean is not. The prose
    that read the centroid's zero as covering the pull rows was wrong at the
    two tight waists, and this function is what measures it instead.
    """
    m = np.abs(NU) < window
    res = fit_condition([NU[m]], [prof[m]], T_C=T_C, transit_fwhm=transit)
    return float(res["centers"][0])


_VCACHE: dict = {}


def kernel_windowed_variance(gamma_coll, transit, window):
    """V(u): the kernel's own second moment inside the analysis window.

    The covariance identity below needs the kernel's variance, and a Lorentzian
    has none: the second moment of gamma_nat + gamma_coll diverges. What the
    analysis actually integrates is the WINDOWED second moment, so that is what
    stands in for V, and the constant it produces therefore belongs to the
    estimator and not to the physics. Cached on the same rounded pair as the
    kernel itself.
    """
    key = (round(gamma_coll, 3), round(transit, 4), round(window, 3))
    if key not in _VCACHE:
        k = _kernel(key[0], key[1])
        m = np.abs(NU) <= window
        nu, pr = NU[m], k[m]
        tot = pr.sum()
        c = float((nu * pr).sum() / tot)
        _VCACHE[key] = float((((nu - c) ** 2) * pr).sum() / tot)
    return _VCACHE[key]


def covariance_term(cells, window):
    """Cov(u, V(u)) over the collected volume, and the two means behind it.

    THE IDENTITY THIS MEASURES. With the observed frequency X = -u + K, K
    conditional on u, symmetric about zero and of variance V(u), the third
    central moment expands to

        mu3(X) = -mu3(u) - 3 Cov(u, V(u))

    because the cross terms in K and K^3 vanish by symmetry. The first moment
    is untouched at any V, which is why the centroid is exactly immune while
    the skew is not. Nothing here is fitted: u is the element's own light
    shift, V is the windowed variance of the kernel that element carries, and
    the weights are the collected volume's.

    Written on 2026-09-10 because the identity and its constant stood on two
    prose surfaces with no script, no CSV and no route to re-derive them, which
    the four-things rule forbids.
    """
    us, vs, ws = [], [], []
    for mid, tr, wgt in cells:
        for s, w in zip(mid, wgt):
            if w <= 0.0:
                continue
            g = GAMMA_COLL + stark.companion_gamma_mhz(float(s), "4192")
            us.append(float(s))
            vs.append(kernel_windowed_variance(g, float(tr), window))
            ws.append(float(w))
    u = np.asarray(us)
    v = np.asarray(vs)
    w = np.asarray(ws)
    w = w / w.sum()
    cov = float((w * u * v).sum() - (w * u).sum() * (w * v).sum())
    return cov, float((w * v).sum()), float(v.max() - v.min())


def observables(prof, window):
    """The two the campaign reads: the centroid pull and the windowed third
    cumulant. The centroid is the profile's own first moment, which is what a
    free per-trace centre fits to at leading order."""
    m = float((NU * prof).sum() / prof.sum())
    v, info = windowed_cumulants(NU, prof, window, (3,), centre0=0.0,
                                 baseline="wings")
    k3 = float(v[3]) if info["converged"] and info.get("in_span", True) else float("nan")
    return m, k3


def main() -> int:
    _refuse_unless_isolated()
    # ONE LITERAL FOR ONE CONSTANT (2026-09-09, round two). This carried its
    # own 1.2367 beside COMPANION_RATIO's, so the weight and the kernel could
    # drift apart silently; the matched-weight test read the module literal and
    # passed with COMPANION_RATIO set to 2.0 against a kernel still at 1.2367.
    stark.COMPANIONS = {"ratio": COMPANION_RATIO, "scale": 1.0}  # the layer is ON
    rows = []

    def add(case, quantity, value, unit, basis, note, status):
        rows.append(dict(case=case, quantity=quantity, value=value, unit=unit,
                         basis=basis, note=note, status=status))

    for w0, W in CASES:
        name = f"w{int(w0 * 1e6)}um"
        cells, s0, zratio = volume_grid(w0)
        # the weighted means the fixed-kernel model is entitled to use
        tot = sum(float(w.sum()) for _, _, w in cells)
        s_bar = sum(float((m * w).sum()) for m, _, w in cells) / tot
        tr_bar = sum(float(tr * w.sum()) for _, tr, w in cells) / tot
        g_lo = GAMMA_COLL + stark.companion_gamma_mhz(0.0, "4192")
        g_hi = GAMMA_COLL + stark.companion_gamma_mhz(s0, "4192")

        tr_waist = min(tr for _, tr, _ in cells)
        m_e, k_e = observables(profile_exact(cells), W)
        m_f, k_f = observables(profile_fixed_kernel(cells, s_bar, tr_bar), W)
        _, k_fc = observables(profile_forecast_kernel(cells, s0, tr_waist), W)
        # THE THIRD CUMULANT IS A SMALL DIFFERENCE OF LARGE NUMBERS and this
        # construction does not resolve it everywhere. Summing one kernel per
        # (Lorentzian, transit) pair leaves a numerical floor, and where the
        # ramp's own k3 sits under that floor the row reports the floor. At the
        # archive's waist k3 was still moving by tens of per cent between grids
        # while the pull had converged to four digits, and an earlier draft of
        # this producer quoted the unconverged value with the wrong SIGN. So k3
        # is computed on a half grid too and refused unless the two agree.
        # THE AXES ARE HALVED SEPARATELY AND THE FIXED ROW IS BARRED TOO
        # (2026-09-09). A combined halving is not a
        # convergence check: the axial axis carried all of the movement while
        # the shift axis moved k3 by under 0.04 per cent, and the bar was
        # applied only to the exact row while the fixed row's own movement
        # reached 5.24 per cent at 24 microns, against a README sentence
        # claiming every cumulant row cleared it.
        cells_s, _, _ = volume_grid(w0, n_s=N_S // 2)
        cells_z, _, _ = volume_grid(w0, n_z=N_Z // 2)
        m_eh, k_es = observables(profile_exact(cells_s), W)
        _, k_ez = observables(profile_exact(cells_z), W)
        _, k_fz = observables(profile_fixed_kernel(cells_z, s_bar, tr_bar), W)
        k3_move = max(abs(k_e - k_es), abs(k_e - k_ez)) / max(abs(k_e), 1e-30)
        k3_move_fixed = abs(k_f - k_fz) / max(abs(k_f), 1e-30)
        pull_move = abs(m_e - m_eh) / max(abs(m_e), 1e-30)
        k3_ok = k3_move < 0.05 and k3_move_fixed < 0.05

        # EVERY CLAIM-CLASS ROW CARRIES ITS OWN UNCERTAINTY (8a.1), and the
        # guard's only escape is a sibling _err row, deliberately, so that a
        # reason cannot be written where a number belongs. Each of the three
        # below is a different kind of uncertainty and none is numerical.
        #   the shift  : the record's own band, the waist paired with the
        #                retro-ratio error, computed here from the constants
        #                rather than carried as a literal
        #   the widths : the saturation companion is uncertain at the
        #                factor-of-three level at this waist (docs/methods/04),
        #                so the span is re-evaluated with it scaled both ways
        #   the transit: the collected half-length is 0.26 +- 0.14 Rayleigh
        #                ranges (prediction_band.csv), a 54 per cent band, and
        #                the span follows the window
        _f_lo, _f_hi = (b / K.W0_MEASURED_M for b in K.W0_BAND_M)
        _s_hi = stark.stark_shift_S0_mhz(POWER_W, w0 * _f_lo, K.RHO_RETRO + K.RHO_RETRO_ERR)
        _s_lo = stark.stark_shift_S0_mhz(POWER_W, w0 * _f_hi, K.RHO_RETRO - K.RHO_RETRO_ERR)
        add(name, "on_axis_shift_err", f"{0.5 * (_s_hi - _s_lo):.4f}", "MHz",
            "the waist band paired with the retro-ratio error, the record's convention",
            "the shift goes as the inverse waist squared and as one plus the "
            "retro ratio, so the widest credible interval pairs the tight "
            "waist with the high ratio", "ENVELOPE")
        _span = lambda k: ((GAMMA_NAT + GAMMA_COLL + k * stark.companion_gamma_mhz(s0, "4192"))
                           / (GAMMA_NAT + GAMMA_COLL))
        add(name, "homogeneous_width_span_err", f"{0.5 * (_span(3.0) - _span(1 / 3.0)):.3f}",
            "dimensionless",
            "the span re-evaluated with the saturation companion scaled by three each way",
            "the companion rests on the two-level saturation law with a "
            "two-photon Rabi frequency, which the record carries as standard "
            "practice and not as a derivation for this level structure, so its "
            "magnitude is the span's uncertainty. The STRUCTURE does not "
            "depend on it: whatever the size, it is a function of the local "
            "shift", "ENVELOPE")
        _tr = [tr for _, tr, _ in cells]
        _cl, _ch = volume_grid(w0, l_scale=1.0 - 0.538)[0], volume_grid(w0, l_scale=1.0 + 0.538)[0]
        _sl = max(t for _, t, _ in _cl) / min(t for _, t, _ in _cl)
        _sh = max(t for _, t, _ in _ch) / min(t for _, t, _ in _ch)
        add(name, "transit_span_err", f"{0.5 * abs(_sh - _sl):.3f}", "dimensionless",
            "the span re-evaluated over the collected window's own 0.26 +- 0.14 band",
            "the window is 54 per cent uncertain and the span follows it "
            "directly, since the beam radius at the window EDGE is what sets "
            "the narrowest kernel and so the denominator of this ratio",
            "ENVELOPE")
        add(name, "on_axis_shift", f"{s0:.4f}", "MHz",
            "stark_shift_S0_mhz at 225 mW and the adopted retro ratio",
            "the ramp's upper end, and the companion's argument on axis", "CALIB")
        add(name, "homogeneous_width_span", f"{(GAMMA_NAT + g_hi) / (GAMMA_NAT + g_lo):.3f}",
            "dimensionless",
            "the homogeneous Lorentzian on axis over the same at the beam edge",
            "the saturation companion is keyed on the LOCAL shift, so the "
            "homogeneous width is a function of the ramp's own variable and "
            "the two cannot be separated into a kernel and a distribution",
            "CALIB")
        add(name, "transit_span", f"{max(tr for _, tr, _ in cells) / min(tr for _, tr, _ in cells):.3f}",
            "dimensionless",
            "the transit width AT THE WAIST over the same at the window edge",
            "transit_fwhm_from_w0 goes as one over the local beam radius, so "
            "the kernel is WIDEST where the beam is narrowest, at the waist. "
            "The first draft of this row said the opposite in both its basis "
            "and its error note, which inverted the mechanism the producer "
            "rests on: the broad elements are the shifted ones, and they are "
            "the same elements for both kernels",
            "CALIB")
        add(name, "centroid_pull_exact_err", f"{abs(m_e - m_eh):.5f}", "MHz",
            "the pull's movement between the full grid and half of it",
            "a model output's uncertainty here is numerical, and the grid is "
            "what bounds it", "ENVELOPE")
        add(name, "centroid_pull_fixed_kernel_err", f"{abs(m_e - m_eh):.5f}", "MHz",
            "the same grid movement, which bounds both models equally",
            "the two differ only in the kernel and share the grid", "ENVELOPE")
        # THE CUMULANT'S UNCERTAINTY IS THE COMPANION'S, NOT THE GRID'S
        # (2026-09-09). This row is a covariance between the
        # kernel width and the shift, so it is linear in the companion, and the
        # same file already declares that companion a factor of three
        # uncertain. Quoting a 0.2 per cent grid movement as its error named an
        # axis that does not carry it. The companion is scaled three ways
        # through the producer's own call path and the half-span reported.
        # THE SWEEP MOVES BOTH HALVES OF ONE OBJECT (2026-09-09, round two).
        # It scaled the kernel's companion and left the weight's Rabi ratio at
        # its nominal value, so the half-span was taken over a profile no
        # physics makes: width and area are one object under the law this file
        # uses. Rebuilt at the swept ratio the bar is 1.8 times wider on the
        # cost row at 16 microns and 1.7 times narrower on the cumulant.
        _k3_lo = observables(profile_exact(swept_cells(w0, 1 / 3.0),
                                          companion_scale=1 / 3.0), W)[1]
        _k3_hi = observables(profile_exact(swept_cells(w0, 3.0),
                                           companion_scale=3.0), W)[1]
        add(name, "k3_exact_err", f"{0.5 * abs(_k3_hi - _k3_lo):.6g}" if k3_ok else "",
            "MHz^3",
            "half-span with the saturation companion scaled by three each way",
            "the dominant axis by three orders over the grid. The "
            "k3_grid_movement row carries that separately", "ENVELOPE")
        add(name, "k3_fixed_kernel_err",
            f"{abs(k_f - k_fz):.6g}" if k3_ok else "", "MHz^3",
            "the fixed row's own axial-grid movement",
            "its own, not the exact row's copied across. The first draft copied "
            "one number to both and it exceeded the fixed row's real movement "
            "by a factor of seventeen", "ENVELOPE")
        add(name, "centroid_pull_exact", f"{m_e:.5f}", "MHz",
            "first moment of the element-by-element mixture",
            "every element carries its own kernel", "CALIB")
        add(name, "centroid_pull_fixed_kernel", f"{m_f:.5f}", "MHz",
            "first moment with the kernel held at the weighted mean",
            "the approximation the shipped mixture makes", "CALIB")
        add(name, "centroid_pull_error", f"{100.0 * (m_f - m_e) / abs(m_e):.3f}", "per cent",
            "the fixed kernel against the exact mixture",
            "what the convolution assumption costs the centroid, which is not "
            "the channel the campaign reads: see fitted_centre_error", "ENVELOPE")
        # THE CHANNEL THE CAMPAIGN ACTUALLY READS (2026-09-09, round two).
        c_e = fitted_centre(profile_exact(cells), tr_bar, W)
        c_f = fitted_centre(profile_fixed_kernel(cells, s_bar, tr_bar), tr_bar, W)
        add(name, "fitted_centre_exact", f"{c_e:.5f}", "MHz",
            "fit_condition with s0 zero on the element-by-element mixture",
            "the estimator run_three_channel_forecast inverts, and not the first "
            "moment", "CALIB")
        add(name, "fitted_centre_fixed_kernel", f"{c_f:.5f}", "MHz",
            "the same estimator on the fixed-kernel mixture",
            "the two differ only in the kernel", "CALIB")
        add(name, "fitted_centre_error", f"{100.0 * (c_f - c_e) / abs(c_e):.3f}",
            "per cent",
            "the fixed kernel against the exact mixture, through the fitter",
            "the centroid's immunity does not transfer. The first moment of a "
            "mixture of symmetric kernels is the density's own mean, exactly, "
            "so centroid_pull_error is zero at every waist. A least-squares fit "
            "with one width follows the mode, which the narrow unshifted "
            "elements set, and the broad elements are the shifted ones",
            "ENVELOPE")
        add(name, "fitted_centre_error_err", f"{100.0 * pull_move:.3f}", "per cent",
            "the exact row's own grid movement, which bounds this comparison",
            "the two profiles share the grid and differ only in the kernel",
            "ENVELOPE")
        # 8a.1: the two CALIB rows above carry their own uncertainty too, and
        # it is the same numerical one the pull rows use
        add(name, "fitted_centre_exact_err", f"{abs(m_e - m_eh):.5f}", "MHz",
            "the grid movement that bounds every row of this construction",
            "a model output's uncertainty here is numerical", "ENVELOPE")
        add(name, "fitted_centre_fixed_kernel_err", f"{abs(m_e - m_eh):.5f}", "MHz",
            "the same grid movement, which bounds both models equally",
            "the two differ only in the kernel and share the grid", "ENVELOPE")
        # AND THE KERNEL THE FORECAST ACTUALLY COMPOSES WITH, which is not this
        # one (2026-09-09, round two). The rows above ask the LICENCE question
        # and are entitled to the volume's own weighted mean, the most
        # charitable single kernel there is. rb5s6s/forecast.py keys its
        # companion on the ON-AXIS peak shift and passes the waist transit, and
        # for a density going as |s| the mean is two thirds of the peak, so the
        # twin's kernel is the wider one and pays more. A caveat citing the
        # mean-shift row as the forecast's own cost understates it.
        add(name, "k3_error_forecast_kernel",
            f"{100.0 * (k_fc - k_e) / abs(k_e):.3f}" if k3_ok else "", "per cent",
            "the forecast's own single kernel against the exact mixture",
            "the companion at the on-axis shift and the transit at the waist, "
            "as rb5s6s/forecast.py composes them, so this row and not the "
            "mean-shift one is what the campaign surfaces cite", "ENVELOPE")
        add(name, "k3_error_forecast_kernel_err",
            f"{100.0 * k3_move:.2f}" if k3_ok else "", "per cent",
            "the exact row's own grid movement, which bounds this comparison",
            "the two share the grid and differ only in the kernel", "ENVELOPE")
        add(name, "k3_grid_movement_fixed", f"{100.0 * k3_move_fixed:.2f}", "per cent",
            "the same bar applied to the fixed-kernel row, halving the axial axis",
            "the bar binds both rows, since the comparison between them is only "
            "as converged as the looser of the two", "DIAGNOSTIC")
        add(name, "k3_grid_movement", f"{100.0 * k3_move:.2f}", "per cent",
            "the worst of halving the shift axis and the axial axis separately",
            "the bar is five per cent. Above it the row reports this "
            "construction's numerical floor and not the physics, which is the "
            "case wherever the ramp's own third cumulant is small",
            "DIAGNOSTIC")
        add(name, "pull_grid_movement", f"{100.0 * pull_move:.3f}", "per cent",
            "the same for the centroid pull",
            "the pull converges three orders faster than the cumulant, which is "
            "why it is quotable at every waist and the cumulant is not",
            "DIAGNOSTIC")
        # LANGUAGE 8a.1: a claim-class row carries an uncertainty. For a
        # comparison between two models the uncertainty is numerical, and this
        # construction's own grid movement is what bounds it.
        add(name, "centroid_pull_error_err", f"{100.0 * pull_move:.3f}", "per cent",
            "the pull's grid movement, which bounds the comparison above",
            "the difference between two models is only as sharp as either is "
            "converged, and the pull converges three orders faster than the "
            "cumulant", "ENVELOPE")
        # THE RATIO'S OWN AXIS IS THE COMPANION TOO, and the ratio is far more
        # robust than either value: at the archive's waist the companion's
        # factor of three makes k3_exact uncertain by more than itself, while
        # the ratio moves only a little, which is why the headline survives and
        # the individual cells do not carry it alone.
        _r_lo = 100.0 * (k_f - _k3_lo) / abs(_k3_lo) if _k3_lo else float("nan")
        _r_hi = 100.0 * (k_f - _k3_hi) / abs(_k3_hi) if _k3_hi else float("nan")
        add(name, "k3_error_err", f"{0.5 * abs(_r_hi - _r_lo):.2f}" if k3_ok else "",
            "per cent",
            "half-span of the same ratio with the companion scaled three ways",
            "the grid movement is carried separately and is the smaller axis. "
            "Blank where the comparison is refused", "ENVELOPE")
        # THE COVARIANCE IDENTITY, MEASURED RATHER THAN ASSERTED (2026-09-10).
        # mu3(X) = -mu3(u) - 3 Cov(u, V(u)) is exact for a kernel symmetric
        # about each element's own centre. The contamination this producer
        # measures, k3_fixed minus k3_exact, is therefore -3 Cov up to whatever
        # the windowed stand-in for V costs, and the ratio of the two is the
        # constant the methods chapter quotes. It stood there for a day with no
        # script behind it, which is what these four rows repair.
        _cov, _vbar, _vspan = covariance_term(cells, W)
        add(name, "kernel_variance_covariance", f"{_cov:.6g}", "MHz^3",
            "Cov(u, V(u)) over the collected volume, V the kernel's windowed "
            "second moment, nothing fitted",
            "the exact cost of the correlation a convolution cannot represent. "
            "Zero for a kernel that does not vary with the shift, whatever its "
            "width, which is why a uniform broadening is free here", "DIAGNOSTIC")
        add(name, "kernel_variance_mean", f"{_vbar:.6g}", "MHz^2",
            "the volume-weighted mean of the same windowed variance",
            "the scale the covariance sits against, and the quantity a "
            "convolution replaces by a constant", "DIAGNOSTIC")
        add(name, "covariance_identity_ratio",
            f"{(k_f - k_e) / (3.0 * _cov):.4f}" if (k3_ok and _cov) else "",
            "dimensionless",
            "the measured contamination, k3_fixed minus k3_exact, over 3 Cov(u, V)",
            "THE IDENTITY PREDICTS ONE. The fixed-kernel profile carries a "
            "constant V, so its covariance term vanishes and the difference of "
            "the two third cumulants is exactly 3 Cov. This reads 0.386 with a "
            "spread of 4.0 per cent across a factor of sixteen in L/z_R and "
            "three orders of magnitude in the cumulant itself. The shortfall "
            "is the analysis window truncating a Lorentzian, whose second "
            "moment does not exist at all, so the windowed stand-in for V "
            "over-states the covariance by the reciprocal, 2.594, and the "
            "factor belongs to the estimator and not to the physics. This "
            "column divided by MINUS 3 Cov until 2026-09-10, which flipped the "
            "sign for nothing and left its own note predicting one while the "
            "arithmetic predicted minus one. Its CONSTANCY is the usable part, "
            "since a new waist or a new drive wavelength is then geometry "
            "alone. Blank where the comparison is refused", "DIAGNOSTIC")
        add(name, "kernel_variance_span", f"{_vspan:.6g}", "MHz^2",
            "the range of the windowed kernel variance over the volume",
            "zero here would mean the convolution condition holds exactly at "
            "this waist", "DIAGNOSTIC")
        add(name, "k3_exact", f"{k_e:.6g}" if k3_ok else "", "MHz^3",
            f"windowed third cumulant at a {W:.1f} MHz half-width, exact mixture",
            "the novelty channel's own observable", "CALIB")
        add(name, "k3_fixed_kernel", f"{k_f:.6g}" if k3_ok else "", "MHz^3",
            "the same under the fixed kernel", "the approximation", "CALIB")
        add(name, "k3_error",
            f"{100.0 * (k_f - k_e) / abs(k_e):.3f}" if k3_ok else "", "per cent",
            "the fixed kernel against the exact mixture",
            "what the convolution assumption costs the moment channel", "ENVELOPE")
        print(f"  {name}: pull {m_e:.4f} vs {m_f:.4f} MHz "
              f"({100*(m_f-m_e)/abs(m_e):+.2f}%), k3 {k_e:.4g} vs {k_f:.4g} "
              f"({100*(k_f-k_e)/abs(k_e):+.2f}%)", flush=True)


    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "results", "kernel_inhomogeneity.csv")
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"wrote {dest} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
