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
                      the experimenter (photos, datasheets, direct confirmation)
  - ``MEASURED-HERE`` extracted from the 2025 dataset's CSVs by this pipeline
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
"""Natural Lorentzian FWHM of the two-photon line, 3.4925 MHz on the
TRANSITION axis (1.746 MHz if read on the laser axis). CALCULATED from
TAU_6S_S. Note: the 6S->5P->5S cascade adds NO width to the 5S->6S resonance —
the 6S total decay rate already includes the branch; the 5P width belongs to
the emitted 795 nm photon (settled earlier)."""

TAU_5P12_S = 27.7e-9
"""5P1/2 lifetime. ESTABLISHED. Sets the ~73 ns cascade latency (matters only
for ONF geometry / the nanofibre extension, never for cell linewidths)."""

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
comb pattern -- weak outer teeth (higher-order sideband pairs) bracketing
three strong inner teeth -- across all 2025 ruler blocks (MEASURED-HERE,
2026-07-11 session). The 2026-07-11 reading resolved five teeth; the fit was
raised to seven orders on 2026-08-01 when the truncation was found to bias the
spacing (see ruler.TEETH). The central tooth's height varies block to block with
the HWP/AM setting (it is fed by (s+,s-) pairs as well as (c,c)); pure PM
would give exactly A_k ~ J_k(2 beta)^2 with A(+k) = A(-k), and the observed
+-k asymmetry is the AM-admixture fingerprint (methods section 3)."""

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
isotopes to ~1% - encoded as a permanent test in tests/test_constants.py.
The short keys ('4192') are the manifest/filename keys; use peak_label() for
all human-facing output (full '993.4192 nm ...' form).

WHAT THESE NUMBERS ARE, and it matters for what may be claimed with them
(recorded 2026-08-09 after the experimenter noted the wavemeter was not
calibrated). They are READINGS of an uncalibrated HighFinesse WS-8, recorded
in the campaign filenames. They are NOT absolute wavelength measurements and
no result here treats them as one.

What that costs is nothing measurable, for three separate reasons.

1. IDENTIFICATION USES SPACINGS, and an additive calibration offset cancels
   from a difference exactly. A multiplicative scale error enters the ~2 GHz
   spacings only in proportion, so at the offset measured below it is four
   orders below the 1% the identification test allows.
2. THE FREQUENCY AXIS NEVER USES THEM. It comes from the EOM ruler in MHz per
   ms of scan time, which is differential. Every width, the density lever, the
   collisional bound and the light-shift bound inherit that axis and not these
   labels.
3. THE OFFSET IS SMALL AND THE LABELS MEASURE IT, and the right comparison is
   per hyperfine component, not against the centroid (recomputed 2026-08-09,
   label_offset_mhz below). Comparing a component to the centroid mixes real
   hyperfine structure into the residual, which is how an earlier reading got
   -1575 to +3650 MHz. Against the component each label names, the four
   offsets are +284 to +303 MHz, mean +292 MHz, spread 19 MHz, and the labels'
   own four-decimal quantisation is 61 MHz, so the four measure ONE wavemeter
   calibration offset of about 0.48 ppm, half a picometre. The NIST entry does
   not state which isotope's centroid it is: taking 87Rb instead of 85Rb moves
   the mean to +391 MHz by exactly the isotope shift and moves the spread not
   at all, so the ambiguity is common-mode too. The centroid property itself
   is not assumed: the (2F+1)-weighted hyperfine shifts summing to zero is
   pinned in tests/test_constants.py.

The air-against-vacuum trap is excluded rather than assumed. Had these been
air readings treated as vacuum, doubling them would miss the NIST interval by
5.42 cm^-1, which is 162 GHz. It does not, so they are vacuum-consistent, as
a WS-8 reports by default.

What may NOT be claimed: that this work measures the absolute transition
wavelength. It does not, and it does not need to. The absolute frequencies are
Orson 2021 to MHz and Ayachitula 2024 to kHz, and the resonance those fix,
2e7/E_6S_CM = 993.4181 nm in vacuum, is an input here rather than an output."""


def peak_title(key: str) -> str:
    """The standard trace-figure title stem: the physical transition, stated
    fully, with the label wavelength. One helper so every trace figure agrees:

        $^{85}$Rb $5S_{1/2}$ F=3 $\\rightarrow$ $6S_{1/2}$ F'=3 at 993.4192 nm

    The hyperfine line is Delta F = 0 (S to S two-photon), so F' equals F.
    Part of the trace-figure standard adopted 2026-08-09 (RENDERING_PROTOCOL
    section 12.3 in the working notes): the title carries the transition and
    the condition, the parameter box carries fitted values with uncertainties
    and marks fixed inputs, the beam waist lives in the caption, never on the
    canvas."""
    info = PEAKS[key]
    F = info["F"]
    return (f"$^{{{info['isotope']}}}$Rb $5S_{{1/2}}$ F={F} "
            f"$\\rightarrow$ $6S_{{1/2}}$ F$'$={F} at 993.{key} nm")


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

def hyperfine_shift_hz(A_hz: float, I2: int, F: int) -> float:
    """Hyperfine shift of a J=1/2 level, Hz, for nuclear spin I = I2/2.

    E(F) = (A/2)[F(F+1) - I(I+1) - J(J+1)], the standard J=1/2 form. Weighted
    by (2F+1) the two shifts sum to zero, which is what makes the unshifted
    term energy the CENTROID and is checked in tests/test_constants.py.
    """
    I = I2 / 2.0
    return 0.5 * A_hz * (F * (F + 1) - I * (I + 1) - 0.75)


def two_photon_frequency_hz(key: str, centroid_isotope: int = 85) -> float:
    """Predicted two-photon transition frequency of one hyperfine component, Hz.

    Built from the NIST centroid interval and the measured hyperfine constants,
    so a campaign LABEL can be compared against the component it actually
    names rather than against the centroid. Comparing a component to the
    centroid mixes real hyperfine structure into what is meant to be a
    calibration residual: it gives a -1575 to +3650 MHz spread, of which almost
    all is physics. Per component the spread collapses to 19 MHz.

    centroid_isotope names which isotope's centroid the NIST term energy is,
    which the NIST entry does not state. The two choices differ by exactly the
    99.189 MHz isotope shift and shift all four components together, so the
    choice moves the mean offset and not the spread. 85 is the default as the
    abundant isotope.
    """
    from .polarizability import E_6S_CM
    info = PEAKS[key]
    iso, F = info["isotope"], info["F"]
    I2 = 3 if iso == 87 else 5
    A6 = A_6S_RB87_HZ if iso == 87 else A_6S_RB85_HZ
    # ground A from the measured total splitting: dE = A*(I + 1/2)
    split = HFS_GROUND_RB87_HZ if iso == 87 else HFS_GROUND_RB85_HZ
    A5 = split / (I2 / 2.0 + 0.5)
    centroid = E_6S_CM * 100.0 * C_M_PER_S
    if iso != centroid_isotope:
        centroid += ISOTOPE_SHIFT_85_87_HZ * (1 if iso == 85 else -1)
    return (centroid
            + hyperfine_shift_hz(A6, I2, F)
            - hyperfine_shift_hz(A5, I2, F))


def label_offset_mhz(key: str, centroid_isotope: int = 85) -> float:
    """How far a campaign label sits from the component it names, MHz.

    Positive means the label reads high. The four offsets are common-mode to
    19 MHz, which is inside the labels' own 61 MHz quantisation at four decimal
    places, so they measure one wavemeter calibration offset and not four.
    """
    lam_m = PEAKS[key]["lambda_nm"] * 1e-9
    return (2.0 * C_M_PER_S / lam_m - two_photon_frequency_hz(key, centroid_isotope)) / 1e6


ISOTOPE_SHIFT_85_87_HZ = -99.189e6
"""5S-6S isotope shift, 85 minus 87, -99.189(3) MHz. ESTABLISHED (Ayachitula
et al., Phys. Rev. A 110, 022803 (2024))."""


# --------------------------------------------------------------------------
# Hyperfine constants (used ONLY for the identification cross-check)
# --------------------------------------------------------------------------
HFS_GROUND_RB87_HZ = 6.834_682_610_904e9   # ESTABLISHED (87Rb ground splitting)
HFS_GROUND_RB85_HZ = 3.035_732_439_0e9     # ESTABLISHED (85Rb ground splitting)
A_6S_RB87_HZ = 807.355e6
"""87Rb 6S1/2 magnetic-dipole constant, 807.355(2) MHz. ESTABLISHED
(Ayachitula, Anderson, McLaughlin, Knize, Mungan, Lindsay, Phys. Rev. A 110,
022803 (2024) — Doppler-free two-photon spectroscopy, the kHz-precision
remeasurement. SWAPPED IN 2026-07-13, replacing A. Perez Galvan, Y. Zhao,
L. A. Orozco, Phys. Rev. A 78, 012502 (2008), which gave 807.66(8) MHz — a
0.3 MHz shift, negligible for peak ID). 6S splitting = 2A = 1614.709(3) MHz
(I=3/2). Isotope shift (85-87) = -99.189(3) MHz [same ref]. The
tests/test_constants.py peak-ID test is a labels<->constants CONSISTENCY LOCK
(either side drifting breaks it); it still passes (this change is ~0.01% of the
predicted gap, vs the test's 1% tolerance)."""
A_6S_RB85_HZ = 239.065e6
"""85Rb 6S1/2 magnetic-dipole constant, 239.065(2) MHz. ESTABLISHED (Ayachitula
et al., Phys. Rev. A 110, 022803 (2024); SWAPPED IN 2026-07-13, replacing Perez
Galvan et al. 2008's 239.18(3) MHz). 6S splitting F=3-F=2 = 3A = 717.195(3) MHz
(I=5/2)."""

# --------------------------------------------------------------------------
# AC-Stark / polarizability (fixed-lock physics; 2025 *prediction* only)
# --------------------------------------------------------------------------
DELTA_ALPHA_AU = 1093.0
"""alpha(6S) - alpha(5S) at 993 nm, atomic units. SOURCED (2026-07-13) to Orson
et al., J. Phys. B 54, 175001 (2021) -- prior art on THIS 5S-6S line: they
calculate the differential polarizability alpha_56 = alpha(5S) - alpha(6S) =
-1093 a.u. (= -1.80e-38 J m^2/V^2) "in a manner similar to Martin et al. 2019"
(the 5S-5D method paper, Phys. Rev. A 100, 023417). Our Delta_alpha =
alpha(6S) - alpha(5S) = -alpha_56 = +1093 a.u. (SAME number, opposite sign by
definition). This replaces the earlier "CALCULATED (provisional), refine
with theory" tag -- the value was right and is now a CITED number that
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
=> S0(225 mW, w0=64 um, rho=0.94) = 0.35 MHz transition (0.17 laser axis)
   [the v3.0.0 prior; was 0.59 at the replaced 50 um / rho=1, and 1.43 at the
   32 um nominal before that -- see W0_MEASURED_M and RHO_RETRO];
   S0(225 mW, w0=16 um, rho=0.94) = 5.56 MHz transition (why the fixed-lock
   session's small waist makes the skew, ~S0^3, measurable). See
   stark_shift_S0_mhz().
The 2025 ramp SHAPE is convention-free regardless: f(s) ∝ |s| on [-S0,0];
mean pull -(2/3) S0; third cumulant +S0^3/135 (the fringe-mean, focal Z->0 limit;
the small-waist collection geometry and the fringe tail below both modify the
skew -- see stark_ramp_axial and fringe_tail).

Fringe averaging (Stalnaker et al., PRA 73, 043416 (2006), Sec. IV): a FAST-axial
atom crossing the lambda/2 fringes sees the shift frequency-modulated at rate
2 v_z/lambda; at the mean axial speed ~280 m/s this is ~0.56 GHz, far above the
shift depth <~ 1 MHz, so it responds to the time-averaged (fringe-MEAN) intensity
-- I_eff IS that standing-wave mean (no coherent x2), and the MEAN/pull is exactly
fringe-immune. But the Doppler-free line accepts ALL v_z: near-transverse atoms
(small v_z) sit at a frozen fringe and sample the node-antinode arcsine -- a
fringe-RESOLVED tail. It is NOT benign: the fringe MULTIPLIES the shift,
s -> s(1+x) with x arcsine (mean 0), so it leaves the mean but SUPPRESSES the ramp
skew -- kappa3 -> S0^3 (1/135 - f_res*sigma_x^2/5) (= 1/135 - f_res/10 at rho=1),
a -13.5*f_res*contrast^2 fractional leverage (contrast = 2 sqrt(rho)/(1+rho); only
the product P = f_res*sigma_x^2 is observable). It is negligible at the w0=64 um
prior, where the whole ramp skew is below the 2025 noise anyway, and material
at w0=16 um, where it is SAME-SIGN-additive to the larger beam-divergence
correction (stark_ramp_axial) -- the two must be fit JOINTLY at the small waist.
Its SIZE is not restated here. rb5s6s/fringe_tail.py computes it and
results/fringe_tail.csv commits it, as d_skew: the change in the standardized
skew, per waist, retro ratio and coherence-window end. The percentages the prose
quotes (RESULTS.md C3c, THEORY_NOTE.md section 5, LITERATURE.md) are that
|d_skew| over the intrinsic triangular-ramp skew g1 = 18^1.5/135 = +0.566, and
that is the only normalisation any of them use. Remaining measured input
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
area ratios: 5/3 within 87Rb, 7/5 within 85Rb, 2.42 for 4192/4207.

Two footnotes added 2026-08-09 after this argument was checked with exact 3j
and 6j arithmetic rather than taken on trust.

TWO RANKS DROP OUT, FOR TWO DIFFERENT REASONS, and only one of them is the
selection rule named above. K = 2 is forbidden by the triangle rule between
J = 1/2 states, which is atomic. K = 1 is allowed by angular momentum and
vanishes instead because two photons sharing one polarization vector give a
symmetric polarization tensor, which is geometric. The argument therefore needs
the beamline to hold: a single linear polarization axis shared by the forward
and retro arms, which is what the apparatus has (one polarizer and one half-wave
plate ahead of the EOM, a plain flat retro mirror, no quarter-wave plate in the
retro path).

CIRCULAR POLARIZATION DOES NOT MAKE IT SCALAR, IT MAKES IT ZERO. For two
same-helicity photons the scalar contraction vanishes as well, so with K = 1
absent and K = 2 forbidden the whole amplitude is identically zero: the familiar
statement that Delta m = +/-2 is impossible for J = 1/2. Worth stating because
"purely scalar" reads as though circular light would merely rescale the rate.

The hyperfine factor is exactly 1 between lines, not approximately: the K = 0
matrix element evaluates to the same multiple of the J-reduced element for
85Rb F=3, 85Rb F=2, 87Rb F=2 and 87Rb F=1 alike, so the four lines share one
Rabi frequency at equal field. The area ratios above are the downstream check
on that, and they reproduce to five digits from population weighting alone,
which they could not do if a hidden F-dependent factor existed."""

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
W0_MEASURED_M = 64e-6
"""Beam waist, 64 um. ESTABLISHED: measured on this apparatus lineage, twice,
in this configuration. Enters the transit width (~1/w0) and all Stark
magnitudes (~1/w0^2), so it is quoted without hedging and used as measured.

THE MEASUREMENT, stated first because it is the reason this is not a prior.
Rajasree-KP 2020 (OIST thesis section 5.2) recorded the focused 993 nm cell
beam at a 1/e^2 DIAMETER of 128 um, so w0 = 64 um, on a Thorlabs BC106VIS
profiler, through L1 at f = 150 mm, at 130 C, in the same 2 f_CM retro
geometry, on the same laser model this campaign used (M Squared SolsTiS).
Nieddu 2019 quotes the identical 128 um on the previous laser, a Coherent
MBR 110. Two profiler measurements, one configuration, agreeing.

What this dataset does NOT do is re-measure it. The transit-against-laser-width
degeneracy means the 2025 line cannot pin w0 on its own, which is a
statement about this dataset and not about the value. The knife-edge scan of a
fixed-lock session would measure it here as well as in the lineage.

Re-centred 32 -> 50 um (2026-07-12) after the transit-broadening physics was
corrected: transit_fwhm_from_w0 (below), validated against Lehmann 2021's NNO
worked example to 0.2%, gives a BARE transit FWHM of ~1.87 MHz at w0 = 32 um,
110 C (transition axis). Convolved with the 3.49 MHz natural Lorentzian that
already OVERSHOOTS the observed ~5.25 MHz line (natural(x)transit = 5.64 > 5.25)
BEFORE any laser or collisional width -- so w0 = 32 um is EXCLUDED. The observed
width is consistent with w0 ~= 45-70 um (hard floor ~38 um); 50 um was the central value before the lineage measurement was found. That
intermediate step was an inference from our own line rather than a
measurement: the transit<->sigma_laser degeneracy means the 2025 line cannot
pin w0 on its own -- that is exactly what the knife-edge measurement settles. (The
Gaussian-optics estimate f = 150 mm, w_in = 1.5 mm gave ~32 um, attributed to
"the EOM aperture" clipping the beam. That attribution is now sourced rather
than inferred (2026-08-01, APPARATUS.md sec 1.2/2): no lens or telescope sits
between the SolsTiS and the EOM (EXPERIMENTER), the isolator before it (ISOWAVE
I-98T-5L, 5 mm clear aperture, manufacturer datasheet) is wide enough not to
clip, and the EOM-02-12.5-V's own clear aperture IS 3 mm per the manufacturer's
"Standard Characteristics" table -- confirmed directly from
photonicstechnologies.com, not from the test certificates, which do not state
it. The experimenter separately recalls an IR viewer card showing clipping at
the EOM (a recollection over a year old, not a contemporaneous measurement).
So w_in = 1.5 mm (3 mm diameter) is a real aperture with a real clipping
observation behind it, not a free parameter chosen to fit -- though a
recollected clipping EVENT does not by itself fix how MUCH of the beam was
clipped, which is why this stays a Gaussian-optics estimate and not a
measurement.)

THE LINEAGE MEASUREMENT, in full (2026-08-01, v3.0.0). This is the value the
group MEASURED on this apparatus lineage, not a value inferred from our own
line. The Rajasree-KP 2020 OIST thesis section 5.2 records the
focused 993 nm cell beam as a 1/e^2 DIAMETER of 128 um, i.e. w0 = 64 um, with
a Thorlabs BC106VIS profiler, through L1 with f = 150 mm, at 130 C, in the
same 2 f_CM retro geometry -- and on the SAME LASER MODEL this campaign used,
the M Squared SolsTiS. Nieddu 2019 quotes the identical 128 um on the older
Coherent MBR 110. That is this campaign's configuration in every documented
respect, which is why 64 um is used as measured rather than merely cited.

It is an ADOPTED prior, NOT a measurement of this beam. Two known effects sit
between Rajasree's bench and ours, and BOTH push the EFFECTIVE waist ABOVE
64 um:
  * residual clipping at the 3 mm EOM aperture (sourced from the
    manufacturer's specification table, APPARATUS.md sec 1.2/2), which
    truncates the beam and widens the focus;
  * imperfect superposition of the counter-propagating retro beam, which
    dilutes the effective on-axis intensity relative to a perfect overlap.
Five years of possible realignment separate the two benches as well. Hence
W0_BAND_M below is centred on 64 um and the residual effects are recorded
as biasing the effective value high rather than low.

The dataset's own light-shift data agree: the three-session bound (M23) sits
BELOW the prediction at every subset, which is what a larger waist (lower
intensity) produces. The knife-edge measurement in a fixed-lock session
remains the way to measure THIS beam; it is now confirmatory rather than the
sole route to a sane value."""

W0_BAND_M = (62e-6, 68e-6)
"""Prior band on w0 (m) around the measured 64 um central value.

NOT the old transit-inferred range: since v3.0.0 the central value comes from
an external lineage measurement (see W0_MEASURED_M), so this band expresses
confidence in transferring that measurement to this bench, not the width of
what our own line can accommodate. It leans high because the two residual
effects named in W0_MEASURED_M (EOM clipping, imperfect retro superposition)
both bias the EFFECTIVE waist upward, and -2/+4 um about 64 keeps that lean.
Single source for w0-conditional prediction bands (e.g. stark.fit_stark_sweep),
so the band is never hand-typed downstream.

NARROWED 2026-08-10, experimenter instruction, from (60, 70) um. Every quantity that
reads this constant moves with it, which is the point of there being one
source: the S0 prediction band, the laser-epoch band and the beta w0
systematic in lever_crosscheck all recompute. It does NOT touch the central
value, so no headline bound moves. The transit-inferred 45-70 um quoted in
W0_MEASURED_M's note above and in transit_mc is a DIFFERENT quantity, what the
dataset's own line can accommodate with no external input, and it is kept as
the historical inference it is rather than overwritten by this band."""

RHO_RETRO = 0.94
"""Retro-reflection power ratio (returning/forward intensity at the atoms).

ASSUMPTION, not a measurement. S0 scales as (1 + rho), so this enters every
absolute AC-Stark prediction. Until v3.0.0 the code asserted rho = 1 (a
perfect retro), justified as a geometric design property: the 2025 retro is
self-imaging, L2 maps the cell waist to an intermediate waist and a flat
mirror at that flat wavefront time-reverses the beam, so the forward/return
MODE MATCH is by construction. What that argument does not cover is LOSS --
two extra L2 passes, two extra window passes, mirror reflectivity -- nor
imperfect superposition from alignment. Both push rho below 1.

0.94 +/- 0.04 is adopted as a deliberately modest departure from the design
value, covering a few per cent of loss per surface. The exposure is bounded
either way: S0 ~ (1 + rho) confines the prediction to within a factor 2 of
the rho = 1 value for ANY rho, so no plausible error here changes an
order of magnitude. A fixed-lock session measures rho in situ (PLAN sec 8),
which is what turns this assumption into a number."""

RHO_RETRO_ERR = 0.04
"""One-sigma uncertainty on RHO_RETRO. Enters the S0 prediction band together
with W0_BAND_M: the band corners are (w0_hi, rho - err) and (w0_lo,
rho + err), so the widest credible prediction interval is quoted."""


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
TRACE_N_POINTS = 2000       # ESTABLISHED (from the files themselves; all files)
TRACE_DT_S = 0.5e-3         # s/point => 1.000 s window. ESTABLISHED.
DRIFT_RATE_LASER_HZ_PER_MIN = 4e6
"""Between-scan drift scale of the misconfigured 2025 lock, laser axis.
ENVELOPE (estimated figure; consistent with wavemeter photo). Within a repeat
block the measured scatter is only ~0.08 MHz (MEASURED-HERE) because repeats
were saved back-to-back.

IN TENSION. The reference was usually (not always) left alone within a
5-repeat block (experimenter-confirmed 2026-07-22). NOTE the 0.08 MHz is NOT
accumulated drift: it shows no trend with repeat index (p = 0.33,
scripts/run_intrablock_trend.py), so it is jitter. For 5 evenly spaced traces the scatter is
rate x T x 0.354, so this envelope requires a block spanning only ~3.4 s --
below the 5 x 1.000 s of acquisition the block must contain. The envelope is
therefore expected to revise DOWNWARD once block durations are known; the
recovered-timestamp audit pre-registers that prediction
(docs/PREREGISTRATION_timestamps.md 7). Treat as an upper bound until then.

NOT contradicted after all -- an earlier note here said it was. Three WS/8L
long-term records exist in the setup photos, but EXIF dates place only ONE
inside the 17-18 July 2025 campaign: IMG_2896 (2025-07-18 17:03) shows 37 MHz
over 8.5 min, ~4.35 MHz/min average, i.e. CONSISTENT with this figure. The two
records reading ~0.18 MHz/min are dated 2025-06-11 and 2025-07-23, five weeks
before and five days after acquisition, and cannot speak for it. The retracted
reading is recorded in docs/PREREGISTRATION_timestamps.md 8.2.
Six wavemeter records are tabulated in docs/APPARATUS.md 6, with lock state
where known: the reference-cavity lock is worth a factor 2-5 (0.19 MHz/min
with it, 0.4-1.0 without), and settled drift is ~1 MHz/min on etalon lock
alone. This constant bounds all of them, which is what an envelope should do.
Caveat on the in-campaign record: it is a smooth SETTLING TRANSIENT (local slope
falls 9.0 -> 2.4 MHz/min across 8.5 min), so 4 MHz/min covers the post-tuning
transient; the steady in-campaign rate is not established by any photograph.

RESOLVED 2026-07-23 (the "until then" above arrived): the recovered clock
measured the in-campaign rate (scripts/run_drift_settling.py, results report
addenda 4-7). The state-space refinement, under the residual-audited
mixture noise model, finds ONE CONSTANT drift, +0.016 [+0.007, +0.025]
MHz/min laser (~250x below this envelope; a ~2-sigma indication) across the
five-hour power session the fit sees; persisting, ~20 MHz over the 20.5 h --
with the recapture excursions, the scale that forced the re-centring. Bounded
<~0.17 MHz/min within blocks even in hour 1, matching the 0.19 the
cavity-locked photo shows. What settles (tau ~ 1-2.5 h) is the disturbance
amplitude -- cavity-lock drop-and-recapture excursions during the ~2 h etalon
thermal transient, executed by hand (experimenter, 2026-07-23, recalled AFTER
the blind fit found the same scale) -- not the held lock's drift. The tension
paragraph above dissolves: the envelope
describes RE-TUNE transients, and IMG_2896 (17:03) is exactly that -- shot 18
minutes before the 90 C dwell resumed (17:21, clock-dated), i.e. mid-re-lock
after the daytime break, not steady acquisition. The envelope stands, as an
envelope; the between-block position steps are the operator re-centring
(+-0.2-2 MHz laser), not free-running drift.
Its StdDev of 100 kHz is also the same order as the 0.08 MHz intra-block
scatter above, so that scatter may be jitter rather than drift.
This constant is used only as an
ENVELOPE (upper bound), so an over-estimate is conservative wherever it
appears -- but it should not be quoted as an estimate of the actual rate."""
