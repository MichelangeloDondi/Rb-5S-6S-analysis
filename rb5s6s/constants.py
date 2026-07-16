"""
Physical constants and fixed apparatus parameters
=================================================

Every value in this file is a *physics* quantity: something nature or the
apparatus fixed. Tunable analysis choices (fit windows, thresholds, seeds, ...)
live in ``rb5s6s/config.py`` instead. Nothing numeric may be hard-coded in any
other module.

House rules
-----------
* Every number carries a provenance tag in its comment:

  - ``ESTABLISHED``   published/cited value, or an apparatus fact verified by
                      the experimenter (photos, datasheets, user confirmation)
  - ``MEASURED-HERE`` extracted from the 2025 archival CSVs by this pipeline
  - ``CALCULATED``    derived; the derivation is stated where first used
  - ``ENVELOPE``      order-of-magnitude; must be re-derived before publication
  - ``OPEN``          not yet settled; must never reach a published number

* Frequency-axis convention (project-wide): the TRANSITION (two-photon sum)
  frequency. The laser axis is exactly half of it; anything quoted on the
  laser axis carries a ``_LASER`` suffix. Never mix silently.
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# Fundamental
# --------------------------------------------------------------------------
C_M_PER_S = 299_792_458.0  # m/s, exact. ESTABLISHED.
H_PLANCK_JS = 6.626_070_15e-34    # J*s, exact. ESTABLISHED (CODATA).
EPS0_F_PER_M = 8.854_187_8128e-12  # vacuum permittivity, F/m. ESTABLISHED (CODATA).

# --------------------------------------------------------------------------
# The 6S_1/2 upper state
# --------------------------------------------------------------------------
TAU_6S_S = 45.57e-9
"""6S1/2 lifetime, 45.57(17) ns. ESTABLISHED (Gomez et al., PRA 72, 012502 (2005))."""

GAMMA_NAT_HZ = 1.0 / (2.0 * math.pi * TAU_6S_S)
"""Natural Lorentzian FWHM of the two-photon line, ~3.4926 MHz on the
TRANSITION axis (1.746 MHz if read on the laser axis). CALCULATED from
TAU_6S_S. Note: the 6S->5P->5S cascade adds NO width to the 5S->6S resonance —
the 6S total decay rate already includes the branch; the 5P width belongs to
the emitted 795 nm photon (settled earlier)."""

TAU_5P12_S = 27.7e-9
"""5P1/2 lifetime. ESTABLISHED. Sets the ~73 ns cascade latency (matters only
for ONF geometry / Paper 2, never for cell linewidths)."""

# --------------------------------------------------------------------------
# EOM frequency ruler
# --------------------------------------------------------------------------
OMEGA_EOM_HZ = 12.5e6
"""EOM drive frequency (Photonic Technologies EOM-02-12.5-V, resonant tank).
ESTABLISHED (datasheet + test certificates; RF-oscillator accurate, i.e. exact
at our precision)."""

TOOTH_SPACING_LASER_HZ = OMEGA_EOM_HZ / 2.0
"""6.25 MHz between adjacent two-photon comb teeth on the LASER axis.
CALCULATED: with phase-modulation sidebands on both counter-propagating beams,
Doppler-free resonances occur when 2*nu_c + n*Omega = nu_0, so adjacent n are
Omega/2 apart in laser frequency. Locked experimentally by the observed
5-tooth amplitude pattern (weak / strong / suppressed-carrier / strong / weak)
across all 2025 ruler blocks (MEASURED-HERE, 2026-07-11 session)."""

TOOTH_SPACING_TRANSITION_HZ = OMEGA_EOM_HZ
"""Same teeth measured on the transition axis: 12.5 MHz. CALCULATED (x2)."""

# --------------------------------------------------------------------------
# The four hyperfine components (file-label wavelengths)
# --------------------------------------------------------------------------
PEAKS = {
    # label: vacuum wavelength (nm), isotope, hyperfine line (S->S, Delta F=0), F
    "4207": {"lambda_nm": 993.4207, "isotope": 87, "line": "F=2->2", "F": 2},
    "4192": {"lambda_nm": 993.4192, "isotope": 85, "line": "F=3->3", "F": 3},
    "4154": {"lambda_nm": 993.4154, "isotope": 85, "line": "F=2->2", "F": 2},
    "4121": {"lambda_nm": 993.4121, "isotope": 87, "line": "F=1->1", "F": 1},
}
"""ESTABLISHED (campaign file labels). Identification is independently locked:
the label spacings reproduce (Delta_HFS_ground - Delta_HFS_6S)/2 for both
isotopes to ~1% — encoded as a permanent test in tests/test_constants.py.
The short keys ('4192') are the manifest/filename keys; use peak_label() for
all human-facing output (full '993.4192 nm ...' form)."""


def peak_label(key: str, isotope: bool = False, line: bool = False) -> str:
    """Human-facing label for a peak key: '993.4192 nm' by default, optionally
    '993.4192 nm (85Rb F=3->3)'. The bare 4-digit key is for files/columns
    only; every printout, plot, and doc should use this."""
    s = f"993.{key} nm"
    info = PEAKS[key]
    extra = []
    if isotope:
        extra.append(f"{info['isotope']}Rb")
    if line:
        extra.append(info["line"])
    return s + (f" ({' '.join(extra)})" if extra else "")

# --------------------------------------------------------------------------
# Hyperfine constants (used ONLY for the identification cross-check)
# --------------------------------------------------------------------------
HFS_GROUND_RB87_HZ = 6.834_682_610_904e9   # ESTABLISHED (87Rb ground splitting)
HFS_GROUND_RB85_HZ = 3.035_732_439_0e9     # ESTABLISHED (85Rb ground splitting)
A_6S_RB87_HZ = 807.355e6
"""87Rb 6S1/2 magnetic-dipole constant, 807.355(2) MHz. ESTABLISHED
(Ayachitula, Anderson, McLaughlin, Knize, Mungan, Lindsay, Phys. Rev. A 110,
022803 (2024) — Doppler-free two-photon spectroscopy, the kHz-precision
remeasurement. SWAPPED IN 2026-07-13, superseding A. Perez Galvan, Y. Zhao,
L. A. Orozco, Phys. Rev. A 78, 012502 (2008), which gave 807.66(8) MHz — a
0.3 MHz shift, negligible for peak ID). 6S splitting = 2A = 1614.709(3) MHz
(I=3/2). Isotope shift (85-87) = -99.189(3) MHz [same ref]. The
tests/test_constants.py peak-ID test is a labels<->constants CONSISTENCY LOCK
(either side drifting breaks it); it still passes (this change is ~0.01% of the
predicted gap, vs the test's 1% tolerance)."""
A_6S_RB85_HZ = 239.065e6
"""85Rb 6S1/2 magnetic-dipole constant, 239.065(2) MHz. ESTABLISHED (Ayachitula
et al., Phys. Rev. A 110, 022803 (2024); SWAPPED IN 2026-07-13, superseding Perez
Galvan et al. 2008's 239.18(3) MHz). 6S splitting F=3-F=2 = 3A = 717.195(3) MHz
(I=5/2)."""

# --------------------------------------------------------------------------
# AC-Stark / polarizability (fixed-lock physics; archival *prediction* only)
# --------------------------------------------------------------------------
DELTA_ALPHA_AU = 1093.0
"""alpha(6S) - alpha(5S) at 993 nm, atomic units. SOURCED (2026-07-13) to Orson
et al., J. Phys. B 54, 175001 (2021) -- prior art on THIS 5S-6S line: they
calculate the differential polarizability alpha_56 = alpha(5S) - alpha(6S) =
-1093 a.u. (= -1.80e-38 J m^2/V^2) "in a manner similar to Martin et al. 2019"
(the 5S-5D method paper, Phys. Rev. A 100, 023417). Our Delta_alpha =
alpha(6S) - alpha(5S) = -alpha_56 = +1093 a.u. (SAME number, opposite sign by
definition). This supersedes the earlier "CALCULATED (provisional), refine
with Brion" tag -- the value was right and is now a CITED number that
cross-checks our Stark code THREE ways (all verified 2026-07-13):
  (i)   SI: 1093 * ATOMIC_POLARIZABILITY_SI = 1.80e-38 J m^2/V^2 = Orson exactly;
  (ii)  SIGN: Delta_alpha > 0 => 6S pulled down more than 5S => the two-photon
        transition RED-shifts => S0 > 0 (Orson's shift is negative, consistent);
  (iii) MAGNITUDE: stark_shift_S0_mhz(0.8 W, 63 um, rho=0) = 0.66 MHz reproduces
        Orson's predicted |Df| = 0.66 MHz at their conditions to the digit
        (tests/test_lineshape.py::test_stark_S0_reproduces_orson2021).
An independent recompute from Safronova, Arora & Clark, Phys. Rev. A 73, 022505
(2006) matrix elements remains available if a referee pushes; no longer OPEN.

CONVENTION (pinned 2026-07-12, so the coefficient is no longer factor-of-2
ambiguous). Standard AMO light-shift convention (Grimm, Weidemueller &
Ovchinnikov, Adv. At. Mol. Opt. Phys. 42, 95 (2000); Steck): for a real field
E(t) = E0 cos(wt) the time-average is <E^2> = E0^2/2, and a level shifts by
    dE_i = -(1/2) alpha_i <E^2> = -(1/4) alpha_i E0^2 = -alpha_i I / (2 eps0 c).
The two-photon transition (sum axis) therefore shifts by
    S0 = |dE_6S - dE_5S| / h = Delta_alpha * I_eff / (2 eps0 c h),
with I_eff = (1+rho) * 2P/(pi w0^2) the TIME-AVERAGED on-axis intensity
(forward + retro, NO coherent x2 -- the fringe-averaging argument below).
=> S0(225 mW, w0=50 um, rho=1) = 0.59 MHz transition (0.29 laser axis) [archival
   prior; was 1.43 at the old 32 um nominal, now excluded -- see W0_PRIOR_M];
   S0(225 mW, w0=16 um, rho=1) = 5.7  MHz transition (why the fixed-lock session's small
   waist makes the skew, ~S0^3, measurable). See stark_shift_S0_mhz().
The archival ramp SHAPE is convention-free regardless: f(s) ∝ |s| on [-S0,0];
mean pull -(2/3) S0; third cumulant +S0^3/135.

Fringe averaging (Stalnaker et al., PRA 73, 043416 (2006), Sec. IV): an atom
crossing the lambda/2 fringes sees the shift frequency-modulated with depth
xi = S0 <~ 1 MHz at rate 2v/lambda ~ 0.56 GHz (axial thermal speed ~280 m/s);
modulation index ~2e-3 => pure carrier at the time-averaged intensity, no
coherent x2. (Atoms with axial speed <~ 5 m/s, ~1-2% of weight, are
fringe-resolved -- a percent-level MC correction.) Remaining measured input
before an absolute Stark coefficient: the retro ratio rho (measured in a fixed-lock session, per
config) and the Delta_alpha magnitude. Novelty delineation: docs/LITERATURE.md
and docs/THEORY_NOTE.md."""

ATOMIC_POLARIZABILITY_SI = 1.648_772_7436e-41
"""1 atomic unit of polarizability = 4*pi*eps0*a0^3 in C^2 m^2 / J.
ESTABLISHED (CODATA). Converts DELTA_ALPHA_AU to SI for stark_shift_S0_mhz()."""

# --------------------------------------------------------------------------
# Isotopic abundances (amplitude-ratio physics, module M10)
# --------------------------------------------------------------------------
ABUNDANCE_RB85 = 0.7217
ABUNDANCE_RB87 = 0.2783
"""Natural isotopic abundances. ESTABLISHED (IUPAC). For S->S two-photon
excitation with two IDENTICAL photons the effective operator is purely
SCALAR (rank K=2 cannot connect J=1/2 -> J=1/2), so the per-atom rate is the
same for every F and m_F, and the line strength is pure POPULATION:
abundance x (2F+1)/G_iso with G_87=8, G_85=12 ground sublevels. Predicted
area ratios: 5/3 within 87Rb, 7/5 within 85Rb, 2.42 for 4192/4207."""

SIGMA_D1_CM2 = 1.5e-11
"""Doppler-broadened peak absorption cross-section of the Rb D1 line
(5S->5P1/2, 795 nm) at ~100 C. ENVELOPE (standard Rb value ~1-2e-11 cm^2 at
these temperatures). Sets the trapping optical depth of the DETECTED 795 nm
cascade photon: tau = f_HF * abundance * N * sigma * L. The emitted 795 photon
is on the D1 line, so it is resonantly reabsorbed by ground-state atoms
(module M7 / amplitude-trapping analysis)."""

# --------------------------------------------------------------------------
# Atomic masses and Boltzmann constant (transit-broadening Monte-Carlo)
# --------------------------------------------------------------------------
_U_KG = 1.660_539_066_60e-27            # atomic mass unit, ESTABLISHED
K_B_J_PER_K = 1.380_649e-23             # Boltzmann constant, exact. ESTABLISHED.
M_RB87_KG = 86.909_180_53 * _U_KG      # ESTABLISHED
M_RB85_KG = 84.911_789_74 * _U_KG      # ESTABLISHED
LAMBDA_LASER_M = 993.4e-9              # drive wavelength (sets the Rayleigh range). ESTABLISHED.

# --------------------------------------------------------------------------
# Beam geometry
# --------------------------------------------------------------------------
W0_PRIOR_M = 50e-6
"""Beam waist PRIOR (central value), OPEN until the knife-edge measurement. Enters
the transit width (~1/w0) and all Stark magnitudes (~1/w0^2).

Re-centred 32 -> 50 um (2026-07-12) after the transit-broadening physics was
corrected: transit_fwhm_from_w0 (below), validated against Lehmann 2021's NNO
worked example to 0.2%, gives a BARE transit FWHM of ~1.87 MHz at w0 = 32 um,
110 C (transition axis). Convolved with the 3.49 MHz natural Lorentzian that
already OVERSHOOTS the observed ~5.25 MHz line (natural(x)transit = 5.64 > 5.25)
BEFORE any laser or collisional width -- so w0 = 32 um is EXCLUDED. The observed
width is consistent with w0 ~= 45-70 um (hard floor ~38 um); 50 um is adopted as
the central corrected-physics prior. NOTE this is still a PRIOR, not a
measurement: the transit<->sigma_laser degeneracy means the archival line cannot
pin w0 on its own -- that is exactly what the knife-edge measurement settles. (The
Gaussian-optics estimate f = 150 mm, w_in = 1.5 mm gave ~32 um, but the 3 mm EOM
aperture clipped the beam, widening the true waist -- consistent with ~50 um.)

DIRECT-MEASUREMENT CORROBORATION (2026-07-13, from the group's own 993 nm
lineage): Nieddu 2019 (Opt. Express, and his OIST thesis: "measured to be
128 um") AND the Rajasree-KP 2020 OIST thesis both quote the focused 993 nm cell
beam as a 1/e^2 DIAMETER of 128 um -- i.e. w0 = 64 um -- with the SAME f = 150 mm
lens. That direct measurement lands at the top of the transit-inferred 45-70 um
band and definitively excludes 32 um (the naive Gaussian value was ~2x too small
because the 3 mm aperture truncated the ~3 mm-diameter input). We KEEP 50 um as
the central prior (the transit-width match, which slightly prefers ~50-55 um so
the drifted 2025 laser stays comfortably under its C2 bound) because the 2025
alignment is not guaranteed identical to Nieddu's; the honest archival range is
w0 ~ 50-64 um. If the archival beam WERE exactly 64 um, the observed line pins
sigma_laser ~ 1.1 MHz laser-axis (the transit<->laser degeneracy collapses once
w0 is fixed) -- which the knife-edge measurement will do directly."""

W0_BAND_M = (45e-6, 70e-6)
"""The transit-inferred w0 band (hard floor ~38 um) that reproduces the observed
~5.25 MHz line under a laser-width prior -- a CONDITIONAL prior range, NOT a
measurement (the archive cannot pin w0 on its own; that is the knife-edge's job,
see W0_PRIOR_M). Single source for w0-conditional prediction bands (e.g. the S0
prediction range in stark.fit_stark_sweep), so the band is never hand-typed."""


def transit_fwhm_from_w0(w0_m: float, T_C: float, isotope: int = 87,
                         mass_kg: float | None = None) -> float:
    """Bare transit-time FWHM (MHz, TRANSITION axis) of the weak-field two-photon
    lineshape for a Gaussian beam of waist ``w0_m`` at temperature ``T_C``.

    Closed form ``ln2 * v_th / (pi * w0)`` with ``v_th = sqrt(2 k_B T / m)``. This
    is the FWHM of the Biraben-Cagnac two-sided-exponential (Lehmann 2021, cusp),
    i.e. the Maxwell-Boltzmann average of the per-atom Gaussian ``exp(-delta^2
    w0^2 / 4 v^2)`` weighted by the crossing FLUX (v-power 0 -> finite peak). It is
    the analytic counterpart of transit_mc.transit_lineshape_mc and the SINGLE
    source of the transit<->w0 map used to set TRANSIT_FWHM_PLACEHOLDER_MHZ.

    VALIDATED: for Lehmann's NNO worked example (m = 44 u, w0 = 0.90 mm, 300 K,
    via mass_kg) this returns HWHM = FWHM/2 = 41.3 kHz vs his 41.2 kHz (0.2%)."""
    m = mass_kg if mass_kg is not None else (M_RB87_KG if isotope == 87 else M_RB85_KG)
    v_th = math.sqrt(2.0 * K_B_J_PER_K * (T_C + 273.15) / m)
    return math.log(2.0) * v_th / (math.pi * w0_m) / 1e6

# --------------------------------------------------------------------------
# 2025 campaign acquisition facts
# --------------------------------------------------------------------------
TRACE_N_POINTS = 2000       # ESTABLISHED (LeCroy WaveSurfer 3104z export; all files)
TRACE_DT_S = 0.5e-3         # s/point => 1.000 s window. ESTABLISHED.
DRIFT_RATE_LASER_HZ_PER_MIN = 4e6
"""Between-scan drift scale of the misconfigured 2025 lock, laser axis.
ENVELOPE (user figure; consistent with wavemeter photo). Within a repeat
block the measured scatter is only ~0.08 MHz (MEASURED-HERE) because repeats
were saved back-to-back."""
