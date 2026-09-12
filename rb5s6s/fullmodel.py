"""The full forward model for the ultra-joint maximum-likelihood fit.

WHY THIS IS A NEW MODULE AND NOT AN EDIT TO `lineshape.model_profile`. That
function is the reproduction path for every committed CSV, so it stays
byte-identical; this module wraps it and adds the terms it deliberately or
accidentally lacks. `full_profile` with its defaults returns exactly what
`model_profile` returns, asserted in `tests/test_fullmodel.py`.

THE FOUR TERMS IT ADDS, and why each is needed for a joint fit over moments.

**1. The Doppler pedestal, which was missing and is not in `model_profile`'s
own list of deliberate absences.** The co-propagating two-photon absorption is
Doppler-broadened to about 931 MHz at 130 C and sits under the narrow line at
about three parts in a thousand of its height. Measured here, it moves the
windowed cumulants of the SAME model by:

    window      k3            k7
      6 MHz    +0.7 %        +0.7 %
     12 MHz   +17.4 %       -53.9 %
     24 MHz  +517.8 %      -819.2 %
     40 MHz +6494.7 %     -4257.3 %

after the estimator's own wing-baseline subtraction. **So a wide-window moment
fitted against a pedestal-free model is fitting the pedestal**, and the
`k5`/`k7` divergences the record struck those orders for cannot be separated
from this until the term is carried. The same pedestal is also two OBSERVABLES
the joint fit needs: its width is a thermometer and its area against the narrow
line's gives the retro ratio, which is now the largest apparatus term in the
waist-free route at 2.1 per cent.

**2. Saturation, parameterised by the two-photon Rabi frequency and NOT by the
light shift.** `stark.companion_gamma_mhz` computes `Omega = 1.2367 * S0`, so
every saturation term is proportional to the one fitted coefficient that this
archive drives to zero, and the companion refit found the exact consequence:
`dchi2` is 0.0000 for the pumping scale from A = 0.5 to 16, because at
`kappa = 0` the companion multiplies nothing. Omega and S0 are both proportional
to intensity but carry DIFFERENT atomic coefficients -- the two-photon matrix
element and the differential polarizability -- so tying them is a choice, not
physics. Taking `omega_mhz` as its own parameter keeps the saturation alive at
`kappa = 0` and makes it a waist meter going as `w0^-4`, the steepest in the
model.

**3. Hyperfine pumping, which is the only F-dependent broadener.** Its branching
runs 0.223, 0.248, 0.348, 0.372 across 4207, 4192, 4154 and 4121
(`results/cascade_branching.csv`, exact manifold computation), a factor of 1.67,
while the ramp and the saturation are F-independent. The peak axis is therefore
the only lever that splits the shift family internally, and it needs `peak` as
an argument, which `model_profile` does not take.

**4. Beam quality, which no function in this package carried.** `M^2` enters in
exactly one place, the Rayleigh range `z_R = pi w0^2 / (M^2 lambda)`, hence the
collection window's `z_ratio`. Everything else in the model is `M^2`-free.

FAILURE MODES. Passing `omega_mhz` AND expecting the old `S0`-tied behaviour
double-counts the saturation; pass one or the other. A pedestal fraction given
as an area where a height is meant is wrong by the width ratio, about 300 here,
so the argument is named for what it is. And the pedestal is added at the
SAMPLED points rather than convolved on the internal grid, which is exact
because it is already a smooth function of `nu` and carries no kernel of its own.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from . import constants as K
from . import stark
from .lineshape import local_ramp_density, model_profile, ramp_mixture

__all__ = ["doppler_pedestal_fwhm_mhz", "residual_doppler_fwhm_mhz",
           "saturation_companion_mhz",
           "collection_z_ratio_m2", "full_profile"]


def doppler_pedestal_fwhm_mhz(T_C: float, isotope: int = 87,
                              lam_m: float = 993.4e-9) -> float:
    """FWHM of the co-propagating two-photon Doppler pedestal, MHz.

    Two photons from the SAME direction give a momentum transfer of `2k`, so the
    pedestal carries twice the single-photon Doppler width. Returns 931 MHz at
    130 C, against 941.95 for 85Rb, which is the SAME formula for the other isotope and not a second measurement: the record's 942 comes from run_widescan_design.py's Rb85 default, so the two figures are one law read at two masses and are not in tension.
    """
    m = K.M_RB87_KG if isotope == 87 else K.M_RB85_KG
    v_th = math.sqrt(2.0 * K.K_B_J_PER_K * (T_C + 273.15) / m)
    sigma_hz = (2.0 / lam_m) * v_th / math.sqrt(2.0)
    return 2.0 * math.sqrt(2.0 * math.log(2.0)) * sigma_hz / 1e6


def residual_doppler_fwhm_mhz(tilt_rad: float, T_C: float, isotope: int = 87,
                              lam_m: float = 993.4e-9) -> float:
    """Residual Doppler FWHM from an imperfectly retro-reflected beam, MHz.

    Two counter-propagating photons cancel the first-order Doppler shift only
    when they are exactly anti-parallel. At a tilt ``tilt_rad`` the residual
    two-photon wave-vector is ``|k1 + k2| = 2 k sin(theta/2)``, so the
    Doppler-free line regains a Gaussian width of that wave-vector times the
    thermal speed.

    IT BROADENS WITHOUT SHIFTING, which is what makes it worth carrying. Every
    other broadener in this model either moves with the intensity, and so shows
    up in the light shift as well, or is already free in the fit.

    THE TERM IS SELF-LIMITING, which is why it is unlikely to be this bench's
    missing width. A tilt reaches the atoms as a lateral OFFSET through the
    retro lens, 300 mm per radian for a mirror 50 mm from an f = 150, so the
    beams walk apart in position 300 times faster than they tilt, and the
    Doppler-free rate goes as their overlap. Requiring only that the narrow line
    is present and not suppressed beyond a factor: at 90 per cent of aligned
    strength the tilt is under 0.069 mrad and this width under 0.031 MHz, and
    even at one per cent it reaches 0.21 against a 1.07 MHz gap. Disfavoured as
    the whole answer, not excluded as a contributor.

    DO NOT USE `constants.RHO_RETRO` TO TIGHTEN THAT. It is an ASSUMPTION of
    0.94 which the epistemic ledger records as never informed by these data, and
    the area ratio that would measure it needs a 931 MHz pedestal against traces
    spanning under 100 MHz. A bound built on it was withdrawn on 2026-09-12.

    What the term is for is the CAMPAIGN's tolerance, and the standing wave is
    where it bites hardest: the fringe contrast stops being unity once the beams
    are offset, and the fringe-resolved skew suppression is contrast-weighted.
    `docs/plan/12` carries the item.
    """
    if tilt_rad <= 0.0:
        return 0.0
    m = K.M_RB87_KG if isotope == 87 else K.M_RB85_KG
    sigma_v = math.sqrt(K.K_B_J_PER_K * (T_C + 273.15) / m)
    dk = 2.0 * (2.0 * math.pi / lam_m) * math.sin(0.5 * float(tilt_rad))
    return 2.0 * math.sqrt(2.0 * math.log(2.0)) * dk * sigma_v / (2.0 * math.pi) / 1e6


def saturation_companion_mhz(omega_mhz: float, peak: Optional[str] = None,
                             pump_scale: float = 1.0) -> float:
    """Homogeneous broadening from saturation plus hyperfine pumping, MHz.

    ``omega_mhz`` is the two-photon Rabi frequency IN ITS OWN RIGHT, which is
    what separates this from `stark.companion_gamma_mhz`: that function takes
    the light shift and multiplies by 1.2367, so it vanishes wherever the
    fitted shift does. Saturation is F-independent; the pumping term carries the
    per-line branching and is the only part that moves with ``peak``.
    """
    om = abs(float(omega_mhz))
    if om <= 0.0:
        return 0.0
    g = stark._GAMMA_MHZ
    sat = g * (math.sqrt(1.0 + 2.0 * (om / g) ** 2) - 1.0)
    if peak is None:
        return sat
    return sat * (1.0 + pump_scale * stark.F_PER_LINE[peak])


def collection_z_ratio_m2(w0_m: float, m2: float = 1.0, **kw) -> float:
    """`L / z_R` with the beam quality carried: `z_R = pi w0^2 / (M^2 lambda)`.

    `constants.collection_z_ratio` has no `M^2` and so assumes a
    diffraction-limited beam; this is the same quantity with the one place
    `M^2` enters the model put back.
    """
    return float(m2) * K.collection_z_ratio(w0_m=w0_m, **kw)


def full_profile(nu: np.ndarray, *, gamma_coll: float, sigma_laser_fwhm: float,
                 transit_fwhm: float, s0: float = 0.0,
                 gamma_nat_mhz: float = K.GAMMA_NAT_HZ / 1e6,
                 laser_kind: str = "gaussian", gamma_l: float = 0.0,
                 peak: Optional[str] = None,
                 omega_mhz: float = 0.0,
                 pump_scale: float = 1.0,
                 pedestal_height_frac: float = 0.0,
                 retro_tilt_rad: float = 0.0,
                 m2: float = 1.0,
                 w0_m: Optional[float] = None,
                 T_C: float = 130.0,
                 isotope: int = 87,
                 **model_kw) -> np.ndarray:
    """The composite line with saturation, hyperfine pumping and the pedestal.

    Defaults reproduce `lineshape.model_profile` exactly: `omega_mhz = 0` adds
    no companion and `pedestal_height_frac = 0` adds no pedestal.

    ``pedestal_height_frac`` is the pedestal's height as a fraction of the
    narrow line's PEAK, which is the convention the record quotes (about 3e-3).

    FAILURE MODE, and it is in the docstring because a caller who reads only
    this would otherwise miss it: ``m2`` is DISCONTINUOUS at exactly 1. The
    axial collection window is absent at 1 and present at 1 + 1e-9, so at a
    64 um waist a fifth of the excursion between m2 = 1 and 3 is the window
    switching on and not beam quality, and at 16 um the step exceeds the
    excursion and flips the third cumulant's sign. No committed producer calls
    this with m2 != 1 today, so no shipped number carries it; a Sobol scan over
    the beam-quality axis would. The repair is to take ``z_ratio`` explicitly
    and let ``m2`` scale a window that is already on, and it is owed its own
    commit because it moves every caller that passes a waist.
    """
    # M^2 REACHES THE PROFILE ONLY THROUGH THE COLLECTION WINDOW, and until
    # 2026-09-12 it did not reach it at all: a caller had to wire
    # collection_z_ratio_m2 through the `profile` seam and one who forgot got a
    # silently diffraction-limited beam. A test asserted that absence as though
    # it were the design, which is how a hole becomes a specification. Passing
    # m2 != 1 now REFUSES unless the waist is given too, because the ratio needs
    # both and a silent default is the failure this comment exists to prevent.
    if float(m2) != 1.0 and w0_m is None:
        raise ValueError(
            "m2 != 1 needs w0_m as well: beam quality reaches the line only "
            "through the collection ratio L/z_R with z_R = pi w0^2/(M^2 lambda), "
            "so a waist is required. Passing m2 alone would change nothing and "
            "report success.")
    # AND THE ARGUMENT MUST ACTUALLY REACH THE PROFILE. The first version of
    # this function took `m2`, refused the combination above, and then ignored
    # it: a switch that is thrown and does nothing, which is the defect the
    # refusal was added to prevent and which the refusal itself concealed,
    # because the refusal passing reads as the term working. Beam quality
    # enters through the collection ratio, so it is built into the axial
    # mixture here rather than left for a caller to wire.
    # THE SWITCH IS DISCONTINUOUS AT m2 == 1 AND THAT IS A DEFECT, named here
    # rather than hidden (2026-09-12). At m2 == 1 no axial
    # window is installed at all; at 1 + 1e-9 the window appears, and at
    # 64 um that step alone is 1.6e-3 of peak against 7.6e-3 for the whole
    # m2 = 1 -> 3 excursion, so a fifth of what this record attributes to
    # BEAM QUALITY is the window switching on. At 16 um the step is larger
    # than the excursion and flips the sign of k3. The repair is to take
    # `z_ratio` as an explicit argument and let `m2` only scale a window
    # that is already on; it is owed its own commit because it moves every
    # caller that passes a waist, and `test_m2_enters_the_collection_ratio_and_
    # refuses_to_be_a_no_op` passes on the window term alone until it lands.
    if float(m2) != 1.0 and "profile" not in model_kw:
        z_ratio = collection_z_ratio_m2(float(w0_m), float(m2))
        _xg = np.linspace(-1.0, 0.0, 4001)
        _gx = local_ramp_density(_xg)
        _memo: dict = {}

        def _profile(nu_, s0_, _zr=z_ratio, _xg=_xg, _gx=_gx, _memo=_memo):
            key = (float(s0_), nu_.shape[0], float(nu_[0]), float(nu_[1] - nu_[0]))
            if key not in _memo:
                _memo[key] = ramp_mixture(nu_, s0_, _zr, _xg, _gx)
            return _memo[key]

        model_kw["profile"] = _profile
    companion = saturation_companion_mhz(omega_mhz, peak, pump_scale)
    # the tilt's residual Doppler term is GAUSSIAN, as is the laser kernel, so
    # the two add in quadrature exactly and no second convolution is needed
    sig = sigma_laser_fwhm
    if retro_tilt_rad > 0.0:
        rd = residual_doppler_fwhm_mhz(retro_tilt_rad, T_C, isotope)
        sig = math.hypot(sig, rd)
    narrow = model_profile(nu, gamma_coll=gamma_coll + companion,
                           sigma_laser_fwhm=sig,
                           transit_fwhm=transit_fwhm, s0=s0,
                           gamma_nat_mhz=gamma_nat_mhz, laser_kind=laser_kind,
                           gamma_l=gamma_l, **model_kw)
    if pedestal_height_frac <= 0.0:
        return narrow
    fwhm = doppler_pedestal_fwhm_mhz(T_C, isotope)
    nu = np.asarray(nu, float)
    centre = float(nu[int(np.argmax(narrow))])
    ped = np.exp(-4.0 * math.log(2.0) * ((nu - centre) / fwhm) ** 2)
    return narrow + pedestal_height_frac * float(np.max(narrow)) * ped


# ---------------------------------------------------------------------------
# The fringe Monte Carlo, generalised to a real beam and a real retro
# ---------------------------------------------------------------------------

def fringe_survival_mc(*, w0_m: float, rho: float = 1.0, T_C: float = 130.0,
                       m2: float = 1.0, tilt_rad: float = 0.0,
                       offset_m: float = 0.0, half_window_m: float = 3.375e-3,
                       e1_dot_e2: float = 1.0,
                       coherence_s: Optional[float] = None,
                       n_atoms: int = 200_000, b_cut: float = 3.0,
                       seed: Optional[int] = None) -> dict:
    """The standing-wave fringe average with the beam quality and the retro
    geometry carried, which `fringe_tail` does not.

    `rb5s6s.fringe_tail` models a diffraction-limited beam retro-reflected
    perfectly: one waist constant over the interaction, one global fringe
    contrast `2 sqrt(rho)/(1+rho)` set by the power ratio alone, and a fringe
    phase `2 k z` that only an axial velocity can wash out. Three things a real
    bench has are therefore absent, and each reaches the fringe-resolved
    suppression by a different route.

    **THE BEAM QUALITY.** `z_R = pi w0^2/(M^2 lambda)`, so at `M^2 = 3` the
    Rayleigh range is a third of its ideal value and the beam radius over the
    COLLECTED region, millimetres long, is no longer nearly constant. The
    original is right that the waist barely moves during one atom's transit; it
    is silent on the waist differing between atoms at different `z`.

    **THE RETRO OFFSET.** A displaced return beam makes the local contrast
    `2 sqrt(I_f I_r)/(I_f + I_r)` a function of position rather than a number:
    unity on the bisector, falling away from it. The cross-term rate that makes
    the Doppler-free line goes as `I_f I_r`, so the offset reweights which atoms
    contribute at all.

    **THE RETRO TILT.** The fringe wave-vector is `k1 - k2`, which for a tilt
    `theta` is `k((1 + cos theta) z + sin theta x)`. The fringe phase therefore
    acquires a TRANSVERSE dependence, so an atom's crossing velocity washes
    fringes out alongside its axial velocity, where before only `vz` could.

    **AND THE POLARISATION, which this routine assumed away until 2026-09-12.**
    A standing wave only interferes to the extent the two fields share a
    polarisation, so the contrast carries `e1 . e2`. For this line that factor
    is not a small correction: `rb5s6s.polarisation` shows only rank 0 survives
    for J = 1/2, rank 0 goes as `e1 . e2`, and the owner states the axis was
    always different, so the archive's traces differ by cos of tens of degrees.
    Passing `e1_dot_e2 = 1` is the PARALLEL case and is an upper bound on the
    fringe effect, not a neutral default.

    Returns the fringe-resolved weight fraction and the survival moments, plus
    `reduces_to_ideal`, which is the whole plant: at `m2 = 1`, `tilt_rad = 0`
    and `offset_m = 0` this reproduces `fringe_tail`'s own construction.

    FAILURE MODE: the wavefront mismatch a tilted, displaced retro also
    produces is NOT modelled here. Its absence means the suppression this
    returns is an upper bound on the fringe effect at non-zero tilt, and the
    direction is stated rather than left to be inferred.
    """
    rng = np.random.default_rng(seed if seed is not None else 12345)
    k = 2.0 * math.pi / 993.4e-9
    m = K.M_RB87_KG
    sv = math.sqrt(K.K_B_J_PER_K * (T_C + 273.15) / m)

    vx, vy, vz = (rng.normal(0.0, sv, n_atoms) for _ in range(3))
    v_perp = np.maximum(np.hypot(vx, vy), 1e-6)

    # the closest-approach point as a VECTOR, because an offset breaks the
    # rotational symmetry the scalar impact parameter assumes
    ang = rng.uniform(0.0, 2.0 * math.pi, n_atoms)
    b_r = b_cut * w0_m * np.sqrt(rng.uniform(0.0, 1.0, n_atoms))
    bx, by = b_r * np.cos(ang), b_r * np.sin(ang)

    # the axial coordinate over the collected region, which is where M^2 enters
    z0 = rng.uniform(-half_window_m, half_window_m, n_atoms)
    z_R = math.pi * w0_m ** 2 / (float(m2) * 993.4e-9)
    w_z = w0_m * np.sqrt(1.0 + (z0 / z_R) ** 2)

    # forward and retro envelopes, the retro displaced along x
    i_f = np.exp(-2.0 * (bx ** 2 + by ** 2) / w_z ** 2)
    i_r = rho * np.exp(-2.0 * ((bx - offset_m) ** 2 + by ** 2) / w_z ** 2)
    denom = i_f + i_r
    contrast = np.where(denom > 0.0,
                        float(e1_dot_e2) * 2.0 * np.sqrt(i_f * i_r)
                        / np.maximum(denom, 1e-300), 0.0)

    inv2tau = 0.0 if coherence_s is None else 1.0 / (2.0 * coherence_s ** 2)
    a_num = 6.0 * v_perp ** 2 / w_z ** 2 + inv2tau
    a_den = 4.0 * v_perp ** 2 / w_z ** 2 + inv2tau
    kappa_path = np.sqrt(a_den / a_num)

    # the fringe wave-vector, tilted: K = k1 - k2
    kz = k * (1.0 + math.cos(tilt_rad))
    kx = k * math.sin(tilt_rad)
    omega = kz * vz + kx * vx                      # phase rate along the path
    F = np.exp(-(0.5 * omega) ** 2 / a_num)        # 2 k vz at zero tilt

    # THE INTENSITY NORMALISATION IS PART OF THE WEIGHT, and it was missing
    # until 2026-09-12. `i_f` and `i_r` are unit-peak Gaussians at every z,
    # but each beam's intensity falls as (w0/w_z)^2 down the collected
    # region, so the cross-term rate carries (w0/w_z)^4. Without it every z
    # is weighted as though it sat at the waist, which over-weights the far
    # field: at 16 um it inverted the beam-quality reading outright
    # (M^2 = 3 read as a 59 per cent loss of fringe survival against a true
    # 2.5). `ramp_mixture` carries the same law as (1+zeta^2)^(1-n).
    W = i_f * i_r * (w0_m / w_z) ** 4              # the CROSS-TERM rate
    w_tot = float(W.sum())
    # THE NOMINAL ATOM COUNT IS NOT THE SAMPLE SIZE. The weight is steeply
    # peaked, so the effective count is Kish's (sum w)^2 / sum w^2, and
    # frac_resolved is a weighted fraction of a small tail of THAT. A single
    # seed at 200,000 atoms moved this by twenty per cent while eight seeds
    # agreed to 0.3 sigma, which is how the shortfall was found.
    n_eff = float(w_tot ** 2 / np.sum(W ** 2)) if w_tot > 0 else 0.0
    f_res = float(W[F > 0.5].sum() / w_tot) if w_tot > 0 else 0.0
    se_res = float(math.sqrt(max(f_res * (1.0 - f_res), 0.0) / n_eff)) if n_eff > 0 else float("nan")
    return {
        "n_eff": n_eff,
        "frac_resolved_se": se_res,
        "frac_resolved": f_res,
        "mean_F": float((W * F).sum() / w_tot) if w_tot > 0 else 0.0,
        "mean_contrast": float((W * contrast).sum() / w_tot) if w_tot > 0 else 0.0,
        "fringe_variance_weight": float((W * 0.5 * (contrast * F) ** 2).sum() / w_tot)
        if w_tot > 0 else 0.0,
        "mean_kappa_path": float((W * kappa_path).sum() / w_tot) if w_tot > 0 else 0.0,
        "mean_w_over_w0": float((W * w_z).sum() / w_tot / w0_m) if w_tot > 0 else 1.0,
        "z_R_m": z_R,
        "reduces_to_ideal": bool(m2 == 1.0 and tilt_rad == 0.0
                                 and offset_m == 0.0 and e1_dot_e2 == 1.0
                                 and half_window_m == 0.0),
    }


# ---------------------------------------------------------------------------
# The ultra-joint likelihood over every observable at once
# ---------------------------------------------------------------------------

#: Statistics the joint fit reads. The windowed cumulants are SUMMARY
#: STATISTICS compared against their own forward prediction, never estimators of
#: an untruncated ramp cumulant: the windowed fifth of a Lorentzian-cored line
#: diverges as the window widens and that is a property of the window, not a
#: defect. Asking them to converge struck two usable channels twice.
DEFAULT_WINDOWS = (3.25, 6.0, 12.0)
DEFAULT_ORDERS = (2, 3, 5, 7)


def ultra_joint_statistics(nu: np.ndarray, *, windows=DEFAULT_WINDOWS,
                           orders=DEFAULT_ORDERS, with_ratios: bool = True,
                           **profile_kw) -> dict:
    """The statistic vector the ultra-joint fit matches, from `full_profile`.

    Returns raw windowed cumulants at every (window, order), and optionally the
    shift-free RATIOS `k5/k3` and `k7/k5`, which carry no information about the
    light shift and a great deal about whether the asymmetry IS the ramp: at the
    archive's parameters `k5/k3` sits near -40 and stable to a few per cent over
    a twenty-four-fold span in the shift, with the opposite sign to `k3`, so a
    sloped baseline or a detection nonlinearity carries its own value and is
    separable from the ramp's.

    FAILURE MODE: a window wider than the data's own span returns a statistic
    dominated by whatever the model puts in the wings, which on this archive is
    a pedestal degenerate with the detector offset. Keep the windows inside the
    trace.
    """
    from .cumulants import windowed_cumulants
    y = full_profile(nu, **profile_kw)
    out: dict = {}
    for w in windows:
        k, _ = windowed_cumulants(nu, y, w, orders=tuple(orders))
        for n in orders:
            out[f"k{n}@{w:g}"] = k[n]
        if with_ratios and 3 in orders and 5 in orders and abs(k[3]) > 0:
            out[f"k5/k3@{w:g}"] = k[5] / k[3]
        if with_ratios and 5 in orders and 7 in orders and abs(k[5]) > 0:
            out[f"k7/k5@{w:g}"] = k[7] / k[5]
    return out


def ultra_joint_nll(observed: dict, sigma: dict, nu: np.ndarray,
                    **profile_kw) -> float:
    """-2 ln L of the statistic vector under a Gaussian error model.

    `observed` and `sigma` are keyed as `ultra_joint_statistics` returns. Keys
    absent from either side are skipped and NOT silently counted as agreeing,
    which is the failure a sum over a shrinking population hides.

    THIS IS A LIKELIHOOD OVER SUMMARY STATISTICS AND NOT OVER THE TRACE. Its
    statistics are correlated, strongly so between orders at one window, and a
    DIAGONAL sigma therefore understates the uncertainty. The covariance is owed
    and `ultra_joint_covariance` is where it goes; until it exists this returns
    a number that ranks models and does not calibrate an interval.
    """
    model = ultra_joint_statistics(nu, **profile_kw)
    chi2, used = 0.0, 0
    for key, obs in observed.items():
        s = sigma.get(key)
        if s is None or key not in model or not np.isfinite(s) or s <= 0:
            continue
        chi2 += ((obs - model[key]) / s) ** 2
        used += 1
    if used == 0:
        raise ValueError("no statistic was comparable: every key was missing "
                         "from the model or carried a non-positive sigma, and "
                         "a zero chi-squared over an empty set is not a fit")
    return float(chi2)


def aic_bic(chi2: float, n_params: int, n_data: int) -> dict:
    """Model selection for the joint fit, which the record currently SPANS.

    The transit kernel form is carried as a 0.0142 model-form systematic on the
    collisional coefficient, more than three times its statistical error. But
    the cusp and the Voigt are not equally supported: on the committed grid the
    cusp leads by about 24 in AIC, so the data CHOOSE the form the record spans.
    Selecting rather than spanning would remove the largest bar on that
    coefficient.

    FAILURE MODE: both criteria scale with `n_data`. For a whitened fit the
    count to pass is the effective sample size `sum(n_block/tau_block)` and not
    the raw sample count, which inflates the evidence.
    """
    if n_data <= n_params:
        raise ValueError(f"n_data={n_data} must exceed n_params={n_params}")
    return {
        "aic": chi2 + 2.0 * n_params,
        "bic": chi2 + n_params * math.log(n_data),
        "aic_c": chi2 + 2.0 * n_params
        + 2.0 * n_params * (n_params + 1) / (n_data - n_params - 1),
    }


# ---------------------------------------------------------------------------
# The fitter, so the world and the estimator carry the same term list
# ---------------------------------------------------------------------------

#: Every term `full_profile` can generate, with its bounds and a start. The
#: fitter reads this table, so a term added to the world appears here and the
#: asymmetry between the two is computable instead of hand-maintained in a CSV.
FIT_TERMS = {
    "gamma_coll":           (0.0, 20.0, 0.55),
    "sigma_laser_fwhm":     (0.01, 10.0, 1.60),
    "transit_fwhm":         (0.05, 10.0, 0.96),
    "s0":                   (0.0, 20.0, 0.36),
    "gamma_l":              (0.0, 5.0, 0.40),
    "omega_mhz":            (0.0, 20.0, 0.45),
    "pedestal_height_frac": (0.0, 0.2, 3e-3),
    "retro_tilt_rad":       (0.0, 5e-3, 0.0),
    #: THE CENTRE IS A TERM AND NOT A CONVENIENCE, and which side of the fit it
    #: sits on decides what the asymmetry is worth. The ramp makes the line
    #: asymmetric by a FORWARD-MODEL amount: its density is |s| on [-S0, 0],
    #: fixed by the beam geometry and the polarizability, with no free shape.
    #: Expanding, P(nu; S0) = P0 - (2 S0/3) P0' + (S0^2/36) P0'' + ..., a free
    #: centre spans the first-order term EXACTLY, so freeing it removes the
    #: O(S0) channel and leaves O(S0^2). The information for S0 is then quartic
    #: at the origin, which is the floor this archive sits on. Pin the centre
    #: and the asymmetry is a prediction the fit must match; free it and the
    #: asymmetry is largely absorbed. Neither is wrong. Fitting S0 with a free
    #: centre and reporting its error as if the centre were pinned is.
    "centre_mhz":           (-20.0, 20.0, 0.0),
}

#: World terms with no fitter counterpart, and why. A term here is one the
#: generator can put in and the estimator cannot take out, so a closed loop
#: through it is biased in the direction named. THIS IS THE ASYMMETRY, and it
#: is listed rather than hidden because listing it is what makes a recovery
#: test readable.
UNFITTABLE = {
    "m2": "enters only through the collection ratio, which is degenerate with "
          "the waist at fixed z_ratio: fit z_ratio, not M^2 and w0 separately",
    "e1_dot_e2": "scales the fringe contrast, which the profile model does not "
                 "carry at all; it lives in the Monte Carlo",
    "t_bbr_k": "a centre shift, absorbed exactly by the free per-trace centre",
    #: NOT an amplitude effect, which is what this entry said until
    #: 2026-09-12 and what the master plan's section 5p already refuted.
    #: Time in the beam goes as one over the transverse speed, so the
    #: atoms that complete the most cycles are the SLOWEST, and the
    #: slowest are exactly the ones that make the transit kernel narrow.
    #: Depletion removes the narrow contributions preferentially and the
    #: surviving kernel is WIDER: 5.5 per cent at one mean cycle, 12.0 at
    #: three, 21.8 at ten. A free amplitude absorbs the surviving
    #: fraction and leaves that widening in the transit.
    "cascade_depletion": "a WIDTH and not an amplitude: depletion removes "
                         "the slow, narrow atoms preferentially, widening "
                         "the surviving transit kernel by 12 per cent at "
                         "three mean cycles (master plan 5p). The free "
                         "amplitude absorbs the surviving fraction and not "
                         "the widening. A wider kernel is fitted as a LARGER "
                         "transit and the waist goes as its inverse, so a fit "
                         "that ignores depletion reads the waist too SMALL: "
                         "64 um reads as 57 at three mean cycles, a third of "
                         "the way to the 42 the record cannot explain",
    "scope_quantisation": "read as noise by any weighted fit",
    "lock_drift": "absorbed by the free per-trace centre, and the oracle arm "
                  "exists to size what that absorption costs",
    #: pump_scale was in NEITHER table until 2026-09-12, so term_coverage's
    #: asymmetry list omitted a generative magnitude and fit_full silently held
    #: the world at 1.0 while FIT_TERMS' own comment claimed to name every term
    #: full_profile can generate.
    "pump_scale": "scales the saturation companion through the hyperfine F "
                  "weight, so it is exactly degenerate with omega_mhz at a "
                  "fixed peak: fit omega_mhz, which carries the same product",
}


#: What `full_profile` uses when a term is not passed. A pinned term must take
#: THIS and never its fitting start, or the fitter holds the world at a value
#: the world never had.
_GENERATOR_DEFAULTS = {
    "gamma_coll": 0.0, "sigma_laser_fwhm": 0.0, "transit_fwhm": 0.0,
    "s0": 0.0, "gamma_l": 0.0, "omega_mhz": 0.0,
    "pedestal_height_frac": 0.0, "retro_tilt_rad": 0.0,
    "centre_mhz": 0.0,
}


def term_coverage(free: "tuple[str, ...]") -> dict:
    """Which world terms this free set covers, and which it cannot.

    The census kept this by hand in a CSV column. Keeping it by hand is how it
    went stale within a day of the terms being added, so it is computed here
    from the two tables above and the census can read it.
    """
    free = tuple(free)
    unknown = [f for f in free if f not in FIT_TERMS]
    if unknown:
        raise ValueError(f"not fittable terms: {unknown}. Known: {sorted(FIT_TERMS)}")
    return {
        "free": list(free),
        "pinned": sorted(set(FIT_TERMS) - set(free)),
        "unfittable": dict(UNFITTABLE),
        "n_free": len(free),
        "closed_loop_is_symmetric": not UNFITTABLE,
    }


def fit_full(nu: np.ndarray, y: np.ndarray, *, free: "tuple[str, ...]",
             fixed: "Optional[dict]" = None, peak: Optional[str] = None,
             n_starts: int = 3, seed: int = 0) -> dict:
    """Fit `full_profile` to one trace, with the amplitude and offset profiled out.

    `free` names the terms to vary; everything else in `FIT_TERMS` is held at
    `fixed` or at its tabled start. The amplitude and a constant offset are
    linear and are solved exactly at each step rather than fitted, which keeps
    the non-linear problem small.

    **THE START-DEPENDENCE CHECK IS NOT OPTIONAL** (A45): this record has been
    misled once by an optimiser that returned whatever it was started at, on
    a profiled likelihood that is quartic at the origin. `n_starts` runs are
    made from spread starts and the returned `start_spread` is the range of the
    best-fit parameters across them. A spread comparable to the error bar means
    the answer is the start and not the data.

    FAILURE MODE: a term in `UNFITTABLE` cannot appear in `free`, and asking
    for one raises rather than silently pinning it, because a pinned term that
    the caller believes is free is how a recovery test reads as a success.
    """
    from scipy.optimize import least_squares
    fixed = dict(fixed or {})
    bad = [f for f in free if f in UNFITTABLE]
    if bad:
        raise ValueError(f"{bad} cannot be fitted: " +
                         "; ".join(f"{b}: {UNFITTABLE[b]}" for b in bad))
    cov = term_coverage(tuple(free))
    lo = [FIT_TERMS[f][0] for f in free]
    hi = [FIT_TERMS[f][1] for f in free]
    rng = np.random.default_rng(seed)
    y = np.asarray(y, float)

    def model(p):
        kw = {f: v for f, v in zip(free, p)}
        for k, v in fixed.items():
            kw.setdefault(k, v)
        # A PINNED TERM TAKES THE GENERATOR'S OWN DEFAULT, NOT ITS FITTING
        # START. The first version used the start, so a term the caller neither
        # freed nor fixed was silently held at a non-zero value the world never
        # had -- `omega_mhz` at 0.45 against a world built without it, which
        # moved a one-parameter transit recovery by six per cent. That is the
        # world-fitter asymmetry this whole function exists to remove,
        # reintroduced inside it.
        for k in FIT_TERMS:
            kw.setdefault(k, _GENERATOR_DEFAULTS[k])
        centre = kw.pop("centre_mhz", 0.0)
        m = full_profile(nu - centre, peak=peak, **kw)
        # amplitude and offset are linear: solve them exactly
        A = np.vstack([m, np.ones_like(m)]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        return A @ coef, coef

    def resid(p):
        return model(p)[0] - y

    best, sols = None, []
    for i in range(max(n_starts, 1)):
        p0 = [FIT_TERMS[f][2] for f in free] if i == 0 else [
            float(np.clip(FIT_TERMS[f][2] * rng.uniform(0.4, 2.2),
                          FIT_TERMS[f][0] + 1e-9, FIT_TERMS[f][1]))
            for f in free]
        s = least_squares(resid, p0, bounds=(lo, hi), xtol=1e-12)
        sols.append(s)
        if best is None or s.cost < best.cost:
            best = s
    xs = np.array([s.x for s in sols])
    out = {f: float(v) for f, v in zip(free, best.x)}
    out.update({
        "chi2": float(2.0 * best.cost),
        "n_free": len(free),
        "start_spread": {f: float(xs[:, j].max() - xs[:, j].min())
                         for j, f in enumerate(free)},
        "start_dependent": bool(np.any(
            (xs.max(axis=0) - xs.min(axis=0)) > 0.05 * np.abs(best.x + 1e-30))),
        "coverage": cov,
    })
    return out
