# Running the two-photon measurement in a hollow-core fibre

`provenance: DESIGN` - the numbers here are closed-form properties of a
proposed configuration, checked against `lineshape.stark_ramp`. Nothing on this
page is a measurement of data.
**Status: DESIGN NOTE, 2026-08-04. Nothing here is scheduled, agreed or
costed.** It sets out options and budgets for taking the record's
5S → 6S two-photon measurement out of the vapour cell and into a guided mode,
and it is written so that a reader can recompute every number. Where a number
comes from this repository's own modules the call is given. Where a parameter
had to be assumed, the assumption is labelled and its basis stated. Provenance
tags follow `docs/STYLE.md` (measured-here / calculated / established /
ENVELOPE / OPEN).

**The question.** What would it take to move this measurement out of the
vapour cell and into a hollow-core fibre?
**Takes.** [BIG_PICTURE.md](../BIG_PICTURE.md) §6, for why a guided mode is
interesting at all.
**Gives.** The optical budget, the expected signal, the surface and collision
terms a guided mode adds, and every assumption labelled where it had to be
made.
**Skip if.** You want the cell result. Nothing here is scheduled, agreed or
costed.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

The reader addressed throughout is a guided-mode platform, a hollow-core fibre
experiment holding either a warm fill or a trapped sample. No apparatus outside
this repository is assumed to exist.

Reproduce the arithmetic with
`.venv/bin/python` and the calls quoted inline. Every module used is read-only
here (`rb5s6s.constants`, `rb5s6s.polarizability`, `rb5s6s.lineshape`,
`rb5s6s.density`).

---

## 1. What changes from the cell

The record's line is built out of free atoms flying through a focused beam
inside a glass cell. Three of the four things that set its shape stop being
true in a guided mode, and one new mechanism appears that the cell has no
analogue for.

### 1.1 The intensity is delivered differently

In the cell the working point is 225 mW into a waist of
`constants.W0_MEASURED_M` = 64 µm, giving `2P/(pi w0^2)` = 3.497e7 W/m² per
travelling wave and, with `rho` = 0.94, an on-axis maximum shift

    lineshape.stark_shift_S0_mhz(0.225, 64e-6, 0.94) = 0.3641 MHz

on the transition axis, at the record's own pinned `DELTA_ALPHA_AU`. An
earlier version of this line passed `1093.0` explicitly and got 0.3476,
which matched `results/stark_joint.csv` only because that file's five-hour
producer has not re-run since this record pinned its own polarizability. A guided mode of radius 15 µm reaches the same intensity at
**11.45 mW**, and a 10 µm mode at **5.09 mW**. That is the first and largest
change: the power that a cell spends on one focal volume would instead buy
either a much lower shift at the same rate, or the same shift over tens of
centimetres of interaction length. A fibre buys intensity and length. It does
not buy collection, which section 3 quantifies.

### 1.2 Free atoms cross the beam. Trapped atoms do not.

**This is the one thing from the record that does not transplant, stated
plainly.** The closed-form ramp weight `lineshape.stark_ramp`, density
`f(s) ∝ |s|` on `s ∈ [-S0, 0]`, is derived for atoms **crossing a focused
beam**. Its derivation, quoted in the module docstring, is that the two-photon
signal goes as `I²`, the shift goes as `I`, and the transverse volume measure
of a Gaussian beam gives `du/u`, so that `dS/du ∝ u`. The step that fails for a
trapped sample is the volume measure. It assumes the emitting atoms are spread
over the beam with **uniform spatial density**. Trapped atoms are not. Their
density is `n(r) ∝ exp(+U0 I(r) / (I_0 k_B T))`, concentrated where the
intensity is highest, and the resulting shift distribution is a different
function with a different mean, a different width and the opposite sign of
skewness.

Working it through in the harmonic limit. Write the shift deficit of an atom as
`d = S0 · U_rel/U0`, where `U_rel` is its potential energy measured from the
bottom of the well. For a three-dimensional harmonic well and a classical
thermal sample, `U_rel/k_B T` is a chi-squared variable on three degrees of
freedom divided by two, that is a gamma distribution of shape 3/2. That gives,
against the record's ramp (both expressed as the positive deficit `d`, both
verified numerically against `lineshape.stark_ramp` itself):

| | record ramp, free atoms | trapped thermal sample |
|---|---|---|
| mean deficit | `(2/3) S0` | `(3/2) (k_B T/U0) S0` |
| sd / mean | 0.3536 (`= 1/sqrt(18) ÷ 2/3`) | 0.8165 (`= sqrt(2/3)`) |
| skewness | **−0.566** | **+1.633** |
| support | hard edge at `S0`, zero beyond | no edge, exponential tail |

The signs of the skewness are opposite. The ramp piles its weight at the
maximum shift and tails off toward zero, because the beam's high-intensity core
is where the `I²` weight lives. The trapped distribution piles its weight at
**zero** deficit, because a cold sample sits at the bottom of the well, and
tails off toward large deficits. Any analysis that carries the ramp over
unchanged would therefore get the sign of the line's asymmetry wrong, which
matters because the third cumulant is the drift-immune channel this programme
already relies on.

The two agree in one limit and it is the informative one. When `k_B T ≫ U0` the
Boltzmann factor goes to unity, the measure becomes uniform again, and the ramp
is recovered. A trap that fails to hold the atoms reproduces the cell.

Two corrections to the closed form, both computed rather than asserted:

- **Signal weighting.** The two-photon rate goes as `I²` here too, so the
  observed distribution carries a weight `(1 - U_rel/U0)²`. Monte Carlo over
  4e6 samples of the gamma variable gives a reduction of the mean deficit by a
  factor 0.981 at `k_B T/U0` = 0.0092, 0.813 at 0.0917, and 0.344 at 0.510.
  The leading behaviour is `1 - 2 k_B T/U0`.
- **Anharmonicity.** The harmonic step is the first term of both
  `cos²(kz)` axially and `exp(-2r²/w²)` radially, so the table above degrades
  once `k_B T/U0` approaches 1. At 0.51, the value a 556 µK sample in a
  1091 µK well would have, it should be read as indicative only (ENVELOPE).

### 1.3 The trap has its own differential shift, and its size does not depend on the trap

This is the mechanism with no cell analogue, and it is the largest single
number in the note.

From `rb5s6s.polarizability` at 1064 nm (calculated, the module's own line
lists): `alpha_5s(1064.0)` = 687.39 a.u., `alpha_6s(1064.0)` = −116.43 a.u.,
`delta_alpha(1064.0)` = −803.82 a.u. Two consequences follow immediately.

**The 6S state is anti-trapped at 1064 nm.** Its polarizability is negative, so
an atom promoted to 6S sees the lattice as a repulsive potential and is
expelled from the site it was held in. There is no bound-to-bound vibrational
structure to resolve. The transition runs from a bound 5S level onto a
repulsive 6S surface, and the lineshape maps the ground-state probability
density through the differential potential.

**The inhomogeneous shift it produces is independent of trap depth and waist.**
Combining the mean deficit `(3/2) k_B T/U0` with `S_trap = U0 · Δα/α_5S` gives

    mean trap-induced shift = (3/2) (k_B T / h) · |Δα / α_5S|,

in which `U0` has cancelled. At 1064 nm the ratio is 1.1694 and the coefficient
is **36.55 kHz per µK of atom temperature** (calculated). Making the trap
deeper does not help. Only colder atoms, or a different trap wavelength, would.

| atom temperature | mean trap-induced shift at 1064 nm |
|---|---|
| 1 µK | 0.037 MHz |
| 10 µK | 0.365 MHz |
| 100 µK | 3.655 MHz |
| 556 µK | 20.3 MHz (ENVELOPE, past the harmonic limit) |

For scale, the record's whole ramp edge is 0.364 MHz and the natural width is
`constants.GAMMA_NAT_HZ` = 3.4925 MHz. A 1064 nm trap reaches the record's
ramp edge at **9.5 µK** and the natural width at **95.6 µK**. A sample at the
few-hundred-µK temperature that a fibre load without further cooling would
plausibly deliver would be dominated by this term, not by anything the dataset
measures.

**The way out is a magic wavelength, and this repository already computes
them.** `polarizability.magic_wavelengths(950.0, 1500.0)` returns three
crossings in that window (calculated, and exact in the scalar-only sense
because both states have J = 1/2, so no tensor term exists to spoil them):

| magic wavelength | `alpha` there |
|---|---|
| 1203.886 nm | 546.70 a.u. |
| 1287.874 nm | 500.82 a.u. |
| 1339.571 nm | 479.76 a.u. |

At 1203.886 nm the differential shift vanishes by construction and the whole
`(3/2) k_B T/h · Δα/α` term with it, at the cost of 0.795 times the trap depth
per watt relative to 1064 nm, and subject to the fibre guiding 1204 nm
(section 5). A trap wavelength choice is therefore not a convenience here. It
is the difference between a 3.7 MHz systematic and none.

### 1.4 Vibrational structure, and why there are no recoil sidebands

For the 19 µm mode assumed in the sibling design studies, two counter-propagating
1064 nm beams of 1.0 W each give an antinode intensity of
`4 × 2P/(pi w²)` = 7.054e9 W/m², a depth `U0` = 22.727 MHz = 1090.7 µK, an
axial frequency of 429.4 kHz and a radial frequency of 5.41 kHz (all calculated
here from `alpha_5s(1064.0)`, and reproducing the sibling repositories' own
stored 430 kHz to 0.1 %). The recoil frequency is 2.028 kHz, so the fractional
intensity a single axial vibrational quantum costs is `2 E_rec/(h nu_z)` =
0.945 %, which on a 26.58 MHz differential trap shift is **251 kHz per
quantum**. At 100 µK the mean axial occupation would be 4.4, so the axial
ladder alone would smear the line over roughly 1 MHz in steps of a quarter of a
megahertz, unresolved under a 3.49 MHz natural width.

The radial motion is a different regime. At 5.41 kHz against a shift excursion
of megahertz, the radial modulation is slow compared with the excursion it
produces, so it is quasistatic and inhomogeneous, and the section 1.2
distribution is the right description of it. The axial motion at 429 kHz sits
closer to the boundary and would need the resolved treatment.

One thing the guided geometry gives for free. The two photons are absorbed from
exactly counter-propagating beams of the same wavelength, so the momentum
transfer is `k_eff` = 0 **exactly** and the confinement parameter for the
two-photon line vanishes. There are no first-order motional sidebands at all,
whatever the trap. A residual survives only through beam misalignment, and even
a 10 mrad misalignment gives `k_eff/k` = 0.010 and an effective confinement
parameter of 7.4e-4 (calculated). In a fibre the two beams are the same
guided mode counter-propagating, so the misalignment is bounded by the mode,
not by the alignment.

A second free simplification: `lineshape.stark_ramp_axial` exists because a
focused beam diverges across the collection window, and its `z_ratio = Z/z_R`
parameter is OPEN in the cell. A guided mode does not diverge, so **`z_ratio`
is exactly zero** and the transverse law applies without the axial correction.

### 1.5 The second, non-thermal layer: mode beating

Imperfect launch puts power into higher-order modes, and the beat between them
and the fundamental modulates the on-axis intensity along the fibre. This is
not a thermal effect and does not average away with temperature.

Using the standard hollow circular dielectric waveguide model of 1964, with
mode parameters `u` taken as the Bessel zeros `scipy.special.jn_zeros`
(2.4048 for the fundamental, 3.8317 for the first higher-order group, 5.5201
for the first higher-order mode with on-axis field) and

    L_beat = 8 pi² a² / [ lambda (u_2² - u_1²) ],

the beat lengths for a 48 µm core (a = 24 µm) are (calculated):

| wavelength | `L_beat` vs the first higher-order group | `L_beat` vs the first on-axis higher-order mode |
|---|---|---|
| 420.30 nm | 12.16 mm | 4.38 mm |
| 780.24 nm | 6.55 mm | 2.36 mm |
| 794.98 nm | 6.43 mm | 2.32 mm |
| 993.42 nm | 5.14 mm | 1.85 mm |
| 1064.0 nm | 4.80 mm | 1.73 mm |

Only the second column matters for the intensity an on-axis atom sees, because
the first higher-order group has zero field on axis. Normalising the capillary
modes by power, the on-axis amplitude ratio is
`|J1(2.4048)/J1(5.5201)|` = 1.5257, so a higher-order power fraction `eta`
gives an on-axis amplitude ratio `eps = 1.5257 sqrt(eta)` and an intensity
modulated by `1 ± 2 eps` (calculated):

| higher-order power fraction | intensity swing | two-photon rate swing | `S0` swing |
|---|---|---|---|
| 0.1 % | ±9.6 % | ±19.3 % | ±9.6 % |
| 0.3 % | ±16.7 % | ±33.4 % | ±16.7 % |
| 1.0 % | ±30.5 % | ±61.0 % | ±30.5 % |

An ensemble a few centimetres long spans many beat periods (10.8 periods of the
1.85 mm beat over 2 cm), so it samples the beat phase almost uniformly, and the
sampling distribution of `cos(2 pi z/L_beat)` is the arcsine, which piles up at
the two extremes rather than at the mean. Differential loss does not clean this
up over the length of an atom column: a published mode-resolved measurement puts
the first higher-order modes at 2.57 and 2.62 times the fundamental loss, which
at 70 dB/km is 0.11 dB/m, so 3 cm of fibre would strip 0.08 % of the
higher-order power (established from that measurement, arithmetic calculated).
Whatever the launch puts in is still there at the atoms.

---

## 2. Signal budget

### 2.1 The anchor, and the gap in it

The rate chain below was validated against four independent anchors before
being used: an independent rebuild of `polarizability.alpha_5s` agreeing to
1.000000 at four wavelengths, an Einstein-A route to the 6S lifetime giving
45.42 ns against the repository's `TAU_6S_S` = 45.57 ns (0.3 %), a computed
6S → 5P1/2 branch of 0.341 against the 34/66 split held in `docs/lit/`, and
`lineshape.stark_shift_S0_mhz` reproducing the C3d prediction at the pinned constant.

Backing the same chain out of the dataset's own detected photons does **not**
agree with it. The first-principles peak rate at the cell's working point is
2.68e4 per atom per second against 5.7e2 to 1.7e3 implied by the dataset, a
shortfall of 16x to 47x. The atomic side validates to sub-percent on three
anchors and cannot absorb that. It sits in the detection chain, where the
photomultiplier high voltage and gain are unrecorded (`docs/APPARATUS.md` §3
flags them OPEN, and a gain of 2e4 to 6e4 rather than the assumed 1e6 would
close the gap on its own), the lens clear aperture and quantum efficiency are
assumed, and the cell at 130 °C is optically thick on D1 so the imaged
collection efficiency is not the geometric one.

**Every count rate below is therefore quoted from the validated first-principles
rate, and dividing it by 16 to 47 gives the floor implied by taking the
dataset's own detected photons at face value.** That factor is the single
largest uncertainty in the table and it would be closed by one afternoon of
bench work, not by any calculation (section 6).

### 2.2 The three candidate lines

Geometry for the table: mode radius 10 µm (assumption, representing a core
radius near 15 µm), 100 mW per direction, perfect counter-propagating overlap
`rho` = 1 (assumption, against the cell's accepted 0.94), giving
`2P/(pi w²)` = 6.366e8 W/m² per travelling wave, 18.2 times the cell's
3.497e7. Cold case 1e4 atoms held on axis at the natural width. Hot case
100 °C from `density.number_density_cm3(100)` = 4.808e12 cm⁻³ over 10 cm of
filled fibre, line width natural plus transit plus ramp.

| | 5S → 6S | 5S → 7S | 5S → 5D5/2 |
|---|---|---|---|
| drive (from the repo's nist terms) | 993.418 nm | 760.126 nm | 778.104 nm |
| detection | 795.0 / 780.2 nm | 420.30 nm | 420.30 nm |
| `Δα` (a.u.) | 1144.6 | 4371.7 | 28649 (ENVELOPE) |
| natural FWHM | 3.4925 MHz | 1.802 MHz | 0.410 MHz (ENVELOPE) |
| `S0` at 100 mW | 6.83 MHz | 26.1 MHz | 171 MHz |
| power at which `S0` = natural width | **51.1 mW** | **6.91 mW** | **240 µW** |
| power at which `S0` = the cell's 0.364 MHz | 5.09 mW | 0.68 mW | 0.0049 mW |
| peak rate per atom at 100 mW | 6.22e6 /s | 5.48e6 /s | 1.29e6 /s |
| counts/s, 1e4 cold atoms, 100 mW | 2.7e5 | 1.6e5 | 9.9e3 |
| counts/s, cold, at the usable power | 1.2e5 | 2.2e4 | 4.2e3 |
| counts/s, hot fill, at the usable power | 2.8e5 | 3.4e6 | 3.0e5 |

The `Δα` values come from `polarizability.delta_alpha(993.4181)` and
`polarizability.delta_alpha_7s(760.1257)`. The module returns them with the
opposite sign convention to `constants.DELTA_ALPHA_AU_ORSON2021` = +1093, whose
sign is the subject of an unresolved dispute recorded elsewhere in this
repository. Magnitudes agree to 5 %, and nothing in this note depends on the
sign, only on the magnitude. The 5D5/2 column rests on a construction from one
verified pole plus an offset fixed at a measured magic wavelength, and on an
assumed 5D → 6P reduced matrix element. It is ENVELOPE grade throughout, and
its 420 nm branch is directly proportional to that assumption.

**The one-line reading of the table: light shift, not available power, sets the
ceiling.** All three lines would deliver 4e3 to 3e6 counts/s at a power low
enough to keep the shift under the natural width, and all three run out of
usable power long before they run out of laser. The 5D line runs out at
240 µW, which is why an experiment on that line suppresses the shift actively
rather than passively.

### 2.3 The signal photon is resonant with the gas it has to cross

For the 5S → 6S line this is the binding constraint, and it is the same
radiation-trapping physics the repository already carries for the cell.
`density.d1_optical_depth_per_cm` gives, at `f_hf` = 0.5 (calculated):

| | 85Rb | 87Rb |
|---|---|---|
| 60 °C, per cm | 1.35 | 0.52 |
| 100 °C, per cm | 26.0 | 10.0 |
| 100 °C, over 10 cm | 260 | 100 |
| 100 °C, over 40 cm | 1041 | 401 |

The D1 mean free path at 100 °C is 0.996 mm. Against a core radius of 22.5 µm
that is a **radial** optical depth of 0.023. The vapour is axially opaque and
radially transparent by four orders of magnitude, so essentially every cascade
photon leaves through the side wall on its first flight. Any scheme that
collects out the fibre ends at 795 or 780 nm is collecting from a channel that
is closed. Running the fill at 60 °C would reopen it (1.35 per cm, so 7.4 mm of
a fill contributes) at the cost of a 19-fold drop in density.

---

## 3. Readout comparison

Six schemes were costed. Collection into the guided mode uses
`NA = lambda/(pi w)` from the Gaussian mode divergence and
`eta = 1 - cos(arcsin NA)` counting both fibre ends (calculated):

| mode radius | `eta` at 420 nm | at 795 nm | at 1324 nm |
|---|---|---|---|
| 3.5 µm | 7.3e-4 | 2.6e-3 | 7.3e-3 |
| 10 µm | 9.0e-5 | 3.2e-4 | 8.9e-4 |
| 15 µm | 4.0e-5 | 1.4e-4 | 3.9e-4 |
| 20 µm | 2.2e-5 | 8.0e-5 | 2.2e-4 |

The cell's own lens is 1.21e-2 under its assumed clear aperture, so a 10 µm
guided mode collects **38 times less** than the bulk lens it would replace, and
a 15 µm mode 85 times less. Only a mode radius near 2 µm would match the lens,
and no fibre in this discussion has one.

| scheme | what it measures | assessment |
|---|---|---|
| 1. Guided D-line counting | 795 / 780 nm out the ends | **Dead.** Axial OD 100 to 1041. Not an efficiency problem, an opacity one. |
| 2. Hyperfine shelving read by guided absorption | ground-state population imbalance | **Loses in a hot fill, wins for trapped atoms.** See below. |
| 3. Dispersive or phase readout | the same imbalance via index | **An exact wash** at shot noise, for more hardware. |
| 4. Side-collected D-line fluorescence | 795 / 780 nm through the wall | **Best for a hot fill.** Turns the opacity into an advantage. |
| 5. Guided 1324 / 1367 nm counting | the first cascade photon | **Good cross-check, hard power ceiling.** |
| 6. Two-photon depletion of the drive | fractional loss of the drive | **Cheapest, common-mode with everything.** |

**Scheme 2 and the wall.** Shelving accumulates only if the ground hyperfine
state survives. On bare silica it does not: the mean thermal speed at 100 °C is
301.5 m/s, so an atom in a 22.5 µm core hits the wall every **149 ns**
(6.7e6 per second, calculated), and the state is re-randomised. That converts an
accumulation into a steady-state imbalance and costs a factor 3.5e3 in the
minimum detectable per-atom excitation rate, 1.22 /s against 3.5e-4 /s for
side-collected fluorescence. The break-even hyperfine memory time would be
0.526 ms, short by the same factor. **The comparison inverts for trapped atoms**,
because a trapped sample never touches the wall. The per-atom optical depth in
the guided mode is `sigma_0/A_eff` with `sigma_0 = 3 lambda²/2pi` = 3.018e-13 m²
at 795 nm, giving 4.27e-4 for a 15 µm mode and 9.6e-4 for a 10 µm mode with
`A_eff = pi w²`, so 1e4 trapped atoms would give an optical depth of 4.3 or 9.6
(and twice that under the `pi w²/2` convention). Absorption would then beat
guided fluorescence by roughly 89 times in a large core and 4.8 times in a small
one.

**Scheme 4 and why the geometry favours it.** The drive stays in the core and
exits the far end, so a radial collector sees only Rayleigh and bend scattering,
four to six orders down. That is geometric rejection bought for nothing, and it
cuts the filter requirement from about OD 12 to about OD 6 to 8, which is what
the cell's existing stack already delivers at 90 degrees. At the power where
`S0` = 1 MHz in a large core, an assumed 1e-3 side-collection efficiency would
give of order 1e10 counts/s, roughly a thousand times past single-photon-counter
saturation. Photon counting would be the wrong instrument and a photodiode with
a lock-in on a chopped drive would be the right one.

**Scheme 5 and its ceiling.** The 1324 / 1367 nm photon terminates on 5P, which
is nearly empty, so it is not reabsorbed by the fill. But the 5P population
builds with drive power, and the 5P3/2 → 6S cross-section at 1366.9 nm is
1.557e-15 m² on the same footing that reproduces `constants.SIGMA_D1_CM2` to
1.6 %, so the guide stays thin only while the excited fraction stays below
5.0e-3 in a large core. That fixes a transparent-guide operating power near
11 mW, above which the fibre becomes opaque to its own signal.

### Recommendation

**For a hot fill: side-collected D-line fluorescence as the primary channel,
guided 1324 / 1367 nm counting as a drive-immune cross-check, and drive
depletion as a free normalisation. The 993 nm drive, a large core, and about
11 mW.**

**For a trapped sample: hyperfine shelving read by a weak guided D1 probe**,
because the wall that kills it in a fill is absent and the per-atom optical
depth is 4e-4 to 1e-3.

Three reasons for 11 mW in a large core, all computed above. Transit broadening
is 3.93 MHz in a 15 µm mode against 16.84 MHz in a 3.5 µm mode at 100 °C
(`constants.transit_fwhm_from_w0`), so a small core would destroy the lineshape
the programme exists to measure. The 1367 nm cross-check channel closes above
about 11 mW. And at 11.45 mW in a 15 µm mode the shift edge would be 0.348 MHz,
matching what the record already carries rather than exceeding it.

---

## 4. Background and filtering budget

Drive photon flux at 10 mW delivered (calculated): 5.001e16 /s at 993.418 nm,
3.827e16 /s at 760.126 nm, 3.917e16 /s at 778.104 nm.

**Spectral rejection**, defined as the filter transmission at which drive
leakage equals signal after detector quantum efficiency, scales with the signal
rate:

| signal rate | 993 → 795/780 | 760 or 778 → 420 |
|---|---|---|
| 1e10 /s (side collection, full power) | OD 5.2 | OD 6.1 |
| 1e6 /s | OD 9.2 | OD 10.1 |
| 1e3 /s (photon counting) | OD 12.2 | OD 13.1 |

**Filter and fibre fluorescence is structurally suppressed, and the reason is
worth stating because it is unusual.** Both candidate pairings detect **bluer**
than they drive. From the repository's own term energies, 993 → 795 is
+2512.7 cm⁻¹ anti-Stokes, 778 → 420.30 is +10940.8 cm⁻¹, and 760 → 420.30 is
+10636.9 cm⁻¹ (calculated). One-photon fluorescence of glass, coatings and
cement is Stokes-shifted, so it cannot reach either detection band at all. Only
`I²` processes can, and those fall with drive power. Coloured-glass filter
fluorescence, normally the worst offender in a high-power fluorescence
experiment, is absent by construction.

**Raman in the silica.** The one-phonon band of fused silica peaks near
440 cm⁻¹ with an edge near 1200 cm⁻¹ (established from the literature, not
recomputed here, and worth checking against a source before it is relied on).
All three shifts above are outside it. The 993 → 795 case is additionally
suppressed thermally: `k_B T/hc` at 100 °C is 259.4 cm⁻¹, so
`exp(-2512.7/259.4)` = 6.2e-5. A hollow core puts 99 % or more of the field in
the gas, suppressing whatever silica overlap remains. The 993 → 1324 channel is
the mirror case at −2512.7 cm⁻¹ Stokes, outside the one-phonon band but
reachable by second-order and cascaded Raman, which would need checking at
higher powers (OPEN).

**In-band background that no filter removes.** The drive itself excites 5P
off-resonantly, and those atoms emit real D-line photons at exactly the nir
pairing's detection wavelength. At the working intensity a 993 nm drive gives
0.158 excitations per atom per second and a parasitic flux 1.6e-6 of the
two-photon signal, negligible. The parasitic term scales as `I` while the
signal scales as `I²`, so it only overtakes the peak far below any sensible
operating power. For the blue pairings the parasitic flux is much larger
(562 and 7.70 excitations per atom per second at 778 and 760 nm) but lands at
780 / 795 nm, out of band behind a 420 nm filter.

**Which pairing is easier: the near-infrared one, and the reason is on the input
side.** A 993 nm drive sits 200 nm from the D lines, so any amplified
spontaneous emission at 780 or 795 nm that would directly pump the D-line
resonance is trivially filtered before the fibre. A 778 nm drive sits **2.3 nm**
from D2, and separating drive from its own broadband pedestal across 2.3 nm
needs an etalon, a grating or an atomic filter rather than a dielectric stack.
A second, smaller advantage: silicon at 993 nm is near its band edge, so the
detector alone would give roughly 9.7 dB of rejection before any filter, while a
760 or 778 nm drive sits near the silicon peak and gives none.

---

## 5. Fibre feasibility

### 5.1 Guidance is not established at every wavelength this would need

A kagome fibre guides by inhibited coupling with an anti-resonant condition on
the silica strut of thickness `t`. High-loss resonances sit at
`lambda_m = (2t/m) sqrt(n² - 1)`, equally spaced in frequency. Using the
standard three-term Sellmeier fit for fused silica (1965), the margin of
`F = 2t sqrt(n²-1)/lambda` to the nearest integer, where 0.00 is on resonance
and 0.50 is mid-band, is (calculated):

| strut `t` | 420.30 | 780.24 | 794.98 | 993.42 | 1064.0 | 1203.89 | 1323.88 |
|---|---|---|---|---|---|---|---|
| 196 nm | **0.00** | 0.47 | 0.48 | 0.41 | 0.39 | 0.34 | 0.31 |
| 300 nm | 0.47 | 0.19 | 0.20 | 0.37 | 0.41 | 0.48 | 0.47 |
| 400 nm | **0.05** | 0.08 | 0.06 | 0.15 | 0.21 | 0.30 | 0.37 |
| 500 nm | 0.44 | 0.35 | 0.33 | **0.06** | **0.01** | 0.13 | 0.21 |
| 600 nm | **0.07** | 0.38 | 0.41 | 0.27 | 0.18 | **0.04** | **0.05** |

Because `F ∝ 1/lambda`, the blue line has the largest order parameter of the set
and crosses a resonance every 196 nm of strut thickness, against every 507 nm at
1064 nm. The concrete warning: a published kagome with a measured 196 nm strut
puts its first resonance at **421.3 nm**, within 1 nm of the 420.30 nm rubidium
line. Requiring 420.30 and 1064 nm to share one transmission band is
arithmetically impossible unless the first resonance falls below 420 nm, that is
`t` < 195.5 nm, because the frequency span from 281.8 to 713.3 THz is 431.5 THz
and broadband kagome bandwidths are quoted at "larger than 200 THz".

**A 420 nm detection channel is an advantage only if the specific fibre guides
420 nm, and nothing establishes that.** Published kagome loss records in the
visible stop at 130 dB/km at 532 nm and rise toward the blue. Collecting the
blue transversely through the side wall would make the guidance question moot,
at which point the collection solid angle rather than the fibre band sets the
signal.

There is a separate reason not to reach for the blue. The 420.30 nm photon
comes from 6P3/2, reached from 5D5/2 or 7S. The 993 nm two-photon line cascades
through 5P and emits 1324, 1367, 780 and 795 nm. It produces no blue at all.
Buying a blue channel means moving the drive to 778 or 760 nm, a different
transition with a different polarizability, a different magic-wavelength set and
a different Stark budget. That would be a programme decision, not a detection
upgrade.

### 5.2 The mode field radius has a provenance problem

The sibling design studies both assume a 19 µm mode radius at 1064 nm, and every
trap frequency and confinement parameter downstream is anchored to it. Two
independent checks put it wide. The capillary model gives `w0 = 0.6435 a`, so a
48 µm core implies **15.4 µm**, not 19. A published kagome measurement gives
`w0/a` = 0.694, which applied to a 24 µm core radius gives **16.7 µm**. Taking
16.7 µm raises the intensity by 1.30, so the depth would move from 1090.7 to
1411.9 µK and the axial frequency from 429.4 to 488.5 kHz (calculated).

For the shift budget of section 1.3 this does not matter, because the trap depth
cancels out of the closed form. For everything anchored to the axial frequency
it does.

### 5.3 What the beat lengths mean over a centimetres-long ensemble

Section 1.5 gives the numbers. The consequence for a design is that the
inhomogeneity is spatially structured on a millimetre scale, the ensemble
averages over it rather than sitting at one phase of it, and 3 cm of fibre
strips essentially none of the higher-order power that produced it. One
counterweight is worth stating because it argues the other way: a published
experiment ran a 32 mm atom column in a kagome fibre, which is 28 beat periods
on this model, and reported the atomic resonance uniform along the whole length
to within 2 kHz. A well-launched fibre evidently can hold its mode content low
enough that the beat does not show. That is an existence proof that the problem
is solvable, not evidence that any particular fibre has solved it.

### 5.4 The failure mode that is not on any of these lists

Rubidium condensation. A single cold spot anywhere along a heated hollow-core
fibre both blocks the guide and moves the local density, and progressive
darkening of the core is the known failure mode of warm rubidium in this fibre
class. Nothing in the budgets above depends on it, and it would dominate the
decision to run at all.

### 5.5 The conveyor as a scanning tool

**This subsection is an idea, not a design.** Nothing below has been costed,
none of it is proposed for a session, and it would need the mode content to be
non-negligible in the first place before it would be worth doing.

The observation. If the atoms were transported along the fibre while the line
was being measured, they would move through the mode-beating pattern of section
1.5, and the line centre and width would breathe with the beat period. The
inhomogeneity that section 1.5 treats as a nuisance would become a directly
scanned observable.

What it would look like. At a conveyor speed `v`, the modulation frequency would
be `v/L_beat`. For the 1.85 mm beat at 993 nm in a 48 µm core, that is 0.54 Hz
at 1 mm/s and 0.054 Hz at 0.1 mm/s, one full period every 1.85 or 18.5 seconds
(calculated). Both are slow enough to record a line at each phase.

Three features that would make it a measurement rather than a curiosity:

- **The amplitude gives the mode content.** From section 1.5, the fractional
  intensity swing is `2 eps` with `eps = 1.5257 sqrt(eta)`, so an observed
  swing inverts directly to a higher-order power fraction. A ±9.6 % swing would
  read 0.1 %, a ±30.5 % swing 1.0 %.
- **The spatial frequency identifies which mode.** The first on-axis
  higher-order mode beats at 1.85 mm at 993 nm and the first higher-order group
  at 5.14 mm, and the latter has no on-axis field so it should not appear at
  all. Finding power at 1/1.85 mm⁻¹ and nothing at 1/5.14 mm⁻¹ would be a
  specific, falsifiable prediction of the model in section 1.5.
- **Two observables move by different factors, which separates the effect from
  drift.** The shift scales as `I` and the two-photon rate as `I²`, so a ±9.6 %
  intensity swing would move the line centre by ±9.6 % of `S0` and the count
  rate by ±19.3 %. A pointing drift, a power drift or a density gradient would
  not reproduce that exact 2:1 ratio at a fixed spatial period.

What would have to be true for it to work. The atom position would need to be
known to well under a beat period, which a conveyor lattice provides. The
transported ensemble would need to be shorter than a beat period, or the
breathing would average out inside the sample itself, which is the same
arcsine-sampling problem section 1.5 describes and is the main reason this is
written as an idea. And the trap wavelength beat (1.73 mm) and the drive
wavelength beat (1.85 mm) differ, so the trap depth and the drive intensity
would breathe at slightly different periods and beat against each other over
roughly 2 cm. Whether that is a confound or a second handle is not worked out
here.

---

## 6. What would have to be measured to make any of this a plan

Ordered by how many open questions each one closes.

1. **The silica strut thickness, from an electron micrograph of a cleaved end.**
   One number, already in the drawing data or recoverable in an afternoon, and
   it determines the entire resonance comb and therefore whether 420, 760, 778,
   795, 993, 1064, 1204 and 1324 nm each sit mid-band or on a loss spike. The
   blue channel lives or dies on it.
2. **The photomultiplier high voltage and gain on the existing bench.** This
   closes the 16x to 47x anchor gap that every count rate in section 2 carries.
   It is a recorded setting and a datasheet curve, not an experiment.
3. **The mode field diameter at the trap and drive wavelengths.** The 19 µm
   currently assumed is a 780 nm measurement re-used, and two independent
   estimates put the true value nearer 15.4 to 16.7 µm.
4. **The atom temperature in the fibre**, by release and recapture or by
   time of flight. Section 1.3 turns it directly into the dominant systematic:
   36.55 kHz per µK at a 1064 nm trap.
5. **The higher-order mode content at the launch**, by mode-resolved imaging.
   Section 1.5 shows a few centimetres of fibre will not remove it.
6. **A white-light transmission scan of the actual fibre** across 420 to
   1400 nm, which would confirm or refute item 1 empirically and settle the
   1204 nm magic-wavelength option at the same time.
7. **The side-collection efficiency**, currently an assumed 1e-3 that the
   entire scheme-4 recommendation scales linearly with.

---

## 7. Open questions

**Would the fibre guide 420.30 nm?** Answerable by an electron micrograph of a
cleaved end plus the resonance-comb arithmetic in section 5.1, and confirmable
by a white-light transmission scan. Nothing in the analysis can settle it.

**Would it guide 1203.886 nm, the nearest computed magic wavelength?** The same
two measurements. If it would, the trap-induced shift of section 1.3 goes to
zero by construction and the largest systematic in the trapped case disappears.
If it would not, the next crossings are at 1287.874 and 1339.571 nm.

**What is the atom temperature after loading?** A release-and-recapture or
time-of-flight measurement on the fibre itself. No published number transfers,
because the loading geometry sets it.

**Is the sign of `Δα` the module's or the pinned constant's?** Unresolved in
this repository and untouched by anything here, since only the magnitude enters.
A fixed-lock mean-pull-versus-power measurement in the cell would settle it
before any fibre work started, and an external theory check would be the
cheaper route.

**Does the harmonic treatment of section 1.2 survive at the temperatures a
fibre load actually delivers?** At `k_B T/U0` = 0.51 it is already ENVELOPE
grade. A Monte Carlo over the true `cos²` and Gaussian potentials would answer
it in an hour of computing, and is the one open item on this list that needs no
apparatus at all.

**What is the hyperfine memory time on the inside of a hollow core?** This
decides scheme 2 in a hot fill, where bare silica gives 149 ns against the
0.526 ms needed to break even. A coating that survives rubidium at 100 °C on
an inner wall is not a solved problem, and only a measurement on a coated
sample would answer it.

**Can 40 cm of fibre be held above the condensation point uniformly enough?**
Answerable only by trying it, and it is the failure mode most likely to end the
attempt regardless of everything above.

**Does the conveyor idea in section 5.5 survive the ensemble length?** Answerable
from the existing transport parameters plus a beat-length measurement, without
any new hardware, by asking whether the transported sample is shorter than
1.85 mm.

---

## Provenance and how to re-run

All arithmetic in this note was computed on 2026-08-04 from
`rb5s6s.constants`, `rb5s6s.polarizability`, `rb5s6s.lineshape` and
`rb5s6s.density` at the versions then in the tree, plus `scipy.special` for
Bessel zeros and closed forms stated inline (the hollow circular dielectric
waveguide model of 1964, the three-term fused-silica Sellmeier fit of 1965, the
anti-resonant condition `lambda_m = (2t/m) sqrt(n²-1)`, and the Gaussian
mode divergence `NA = lambda/(pi w)`).

Numbers taken from outside those modules and carried here rather than
recomputed: the record's fitted peak amplitude and total width at the 225 mW,
130 °C working point, the shot-noise coefficient behind the anchor route, the
two-photon amplitudes and cascade branching ratios built from the module line
lists, the published kagome mode-ratio, strut thickness, differential-loss and
32 mm-column results, and the assumed detector quantum efficiencies. Each is
labelled where it appears.

Nothing in this note is a result. The dataset measures a vapour cell.
