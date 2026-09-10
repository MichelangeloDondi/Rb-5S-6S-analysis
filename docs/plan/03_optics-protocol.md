*Chapter 3 of 12 of [the plan](../PLAN.md)*

**The question.** What configurations the cell runs in, how the waist and the retro ratio are measured, and what has to be redone when either the focus or the drive wavelength changes.
**Takes.** The aim of chapter 1 and the priority order of chapter 2.
**Gives.** The configuration set, the two-instrument waist measurement, the realignment protocol for a retune, and the creep detectors.
**Skip if.** You want what the measurements buy and not how they are taken.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## 4. Configurations and optics protocol

### 4.1 The three configurations

Two working waists plus one continuity check (a third full waist is dropped
by design):

- **L (w₀ ≈ 64 µm, z_R ≈ 13 mm).** The width workhorse. Transit ~1.0 MHz,
  collection inside z_R, clean geometry. Runs the full two-day T grid.
- **S (w₀ ≈ 15–16 µm, z_R ≈ 0.8 mm).** The Stark, skew and cusp configuration,
  where the cusp is the discontinuous slope the transit-limit lineshape predicts
  at exact resonance and the Voigt does not, reachable only cold and at low
  drive power (§5).
  One model caveat is specific to it: the composite lineshape convolves transit
  with the natural Lorentzian, which is rigorous when the crossing time is long
  against the 6S lifetime (45 ns). At the 2025 dataset's waist the ratio is
  ~4. At 16 µm it is ~1.3, so this is where a referee should ask for the
  convolution's validity range and where a Bloch-equation cross-check earns
  its time. A caveat
  to state and test, not a reason to retreat.
- **M (the 2025 dataset's geometry, 64 µm, measured, band 62 to 68 µm).** Half-day spot
  check: knife-edge, camera, P grid, one 130 °C point, for direct 2025-epoch
  continuity.

![the bench of record](../apparatus/apparatus_schematic.svg)

*The 2025 bench the session modifies, at its three touch points: a telescope
before the EOM sets the configuration waist, the retro leg (lens, mirror, exit
window) is where ρ is measured, and the collection arm is rebuilt as the relay
plus slit of §6.*

Size the telescope so the beam enters the EOM at ≤ 1 mm waist (the 3 mm
aperture then clips nothing). Per configuration, before science: knife-edge
w(z) at five or more z positions in two orientations, camera z-scan through the
same focus (§4.2), lens separations calipered at setup and teardown (§4.3), ρ in
situ (both directions), collection geometry measured (u, v, and the detector
aperture. The PMT of record is the side-on R636-10 with a 3 × 12 mm cathode,
mounted with its long axis along the beam, an attribution that is ASSUMED rather than verified on this
bench: it comes from the lineage's nanofibre setup, and an in-campaign
photograph shows the cell detector labelled as a Thorlabs PXT1/M, so the
cathode geometry is an open item and not a measured fact), and polarization
defined at the cell with a polarizer, not merely logged (§4.4).

### 4.2 Two instruments for the waist

w₀ is the dominant systematic of the whole analysis, and the one thing you do
not do to a dominant systematic is measure it once with an instrument that has
a single failure mode. The knife-edge gives absolute size in true power units,
down to the smallest waist, but integrates away the 2D shape: a clipped or
structured profile fits an error function acceptably and returns the wrong
waist. The camera gives shape (ellipticity, astigmatism, M², the
forward-against-retro overlap that backs ρ), but under-samples a 16 µm spot and
its saturation corrupts exactly the wings a power measurement needs. Each is
strongest where the other is blind. Run the camera first to find the focus and
validate the Gaussian the analysis integrates over, then size it with the
knife-edge. The camera pixel scale is also a third independent length ruler
beside the knife stage and z_R = πw₀²/λ, so a scale error must fool three
unrelated instruments to pass.

**Needs.** Knife-edge stage, camera, and the configuration's telescope already
installed. No atoms and no lock. **Shots.** Knife-edge w(z) at five or more z
positions in two orientations, and a camera z-scan through the same focus.
**Go/no-go.** The knife-edge waist, the camera waist and z_R = πw₀²/λ must agree
to better than the 10% that sets a 20% systematic on Δα. Disagreement beyond
that aborts the science blocks that quote absolute units, not the session.
**Empty.** A knife-edge returns a number, so the exposure is not failure but
transfer: the number describes the present bench, and carrying it back to 2025
needs the configuration-M spot check of §4.1. **Record.** Both waists, the
ellipticity and M² from the camera, the pixel scale, and the disagreement
between the three length rulers.

**The retro ratio ρ, measured in the same afternoon.** §3 item 2 states why ρ
matters and how it drifts. This is the block that delivers it, costed inside the
metrology afternoon above because it uses the same access to the beam path.
**Needs.** A pick-off that reads the outgoing and the returning beam separately,
so no symmetry between the two passes has to be assumed, and a power meter good
enough to hold the two readings to better than the ~8% drift the window filming
produces across the temperature range. The retro leg as installed
(`APPARATUS.md`). **Shots.** The stable part, lens² times mirror, once per
configuration before science. The drifting part, window transmission before and
after the cell, at every temperature condition. Where the wide-scan pedestal of
§5 runs, its area ratio gives a second ρ on the same traces. **Go/no-go.** The
pick-off ρ and the pedestal ρ must agree within the pedestal route's own weak
sensitivity, and the pick-off must resolve the outgoing from the returning beam
at all, which is the thing the geometry can refuse. **Empty.** A pick-off that
does not separate the two directions returns the product rather than the ratio,
in which case ρ stays a computed quantity from component transmissions and only
its drift is measured. **Record.** ρ per configuration and per temperature
condition, the window transmission before and after the cell at each, the
stable lens and mirror term, and the pedestal ρ beside the pick-off ρ where both
exist.

### 4.2b Realignment when the waist or the transition changes

**This block fires on any change of the expander setting and on any change of
the drive wavelength, and the second case is the one the record missed until
2026-09-09.** The waist is not a property of the bench alone. Through a fixed
lens and a fixed input beam it is `w0 = λf/(πw_in)`, so retuning the laser
moves the waist with nothing touched: the measured 64 µm at 993.4 nm becomes
[48.589](../../results/transition_ladder.csv "ref:transition_ladder:7S:waist_aperture_limited") µm at
760.1 nm and [44.455](../../results/transition_ladder.csv "ref:transition_ladder:6D:waist_aperture_limited") µm
at 697.5. The light shift goes as the inverse square of that, so the same power
is a different experiment. Nothing downstream of this block may be carried
across a retune.

**The order matters and it is not the obvious one.** Refocus before you
re-collimate, re-collimate before you re-retro, and measure the waist last, so
that what is measured is what the science blocks will run on.

1. **Refocus the cell lens.** L1 is a singlet, so its focal length disperses as
   `1/(n-1)`: 150.00 mm at 993.4 nm against 148.83 at 760.1. The focus moves
   about 1.2 mm toward the lens, which is under a tenth of a Rayleigh range and
   so harmless to the waist, and about a third of the collection half-length,
   which is not harmless to the axial window. Translate the lens, do not
   translate the cell.
2. **Re-collimate lens 8 and re-set the retro mirror.** The returning mode
   matches the forward one when the mirror sits one focal length beyond the
   lens and not otherwise. Left at the 993 nm setting, a 760 nm retro returns
   the mode with a power overlap near 0.986, and the same geometry restores
   unity when both are translated to the new focal length. **The retro ratio is
   therefore not transferable across a retune** and §4.2's ρ block runs again.
3. **Refocus the f = 18 mm collection lens onto the new focus.** The collection
   half-length is fixed by the optics while the Rayleigh range falls with the
   waist, so the ratio the axial window model uses rises from
   [0.2605](../../results/transition_ladder.csv "ref:transition_ladder:6S:collection_z_ratio") at 993.4 nm to
   [0.3459](../../results/transition_ladder.csv "ref:transition_ladder:7S:collection_z_ratio") at 760.1 and
   [0.4051](../../results/transition_ladder.csv "ref:transition_ladder:9S:collection_z_ratio") at 655.8. No rung
   in the band reaches the 1.117 at which the windowed third cumulant changes
   sign, so the shape channel keeps its sign, and the ratio still has to be
   recomputed because it enters the ramp's own moments.
4. **Re-measure the waist with both instruments**, exactly as §4.2 prescribes:
   camera first to find the focus and validate the profile, knife-edge second
   to size it, and the three length rulers cross-checked. The go/no-go is
   §4.2's, unchanged.
5. **Re-measure ρ** on the same afternoon, per §4.2's block.

**Go/no-go for the retune itself, and it is a physics check and not an
optical one.** The transit width carries the geometry to the first power while
the light shift carries it to the second, so the ratio of transit widths between
the two drives is a prediction the bench has to meet: about
[1.261](../../results/transition_ladder.csv "ref:transition_ladder:7S:transit_fwhm") MHz at 760.1 nm against
[0.958](../../results/transition_ladder.csv "ref:transition_ladder:6S:transit_fwhm") at 993.4, at the same cell
temperature and the same atom. **A disagreement here is not a failed
alignment.** It says the input beam is not what the waist model assumed, which
is the open item §12 carries, and the measurement it delivers is worth more
than the alignment it was checking. Record the ratio whether or not it agrees.

**What it costs.** An afternoon per drive and per expander setting, with no
atoms and no lock for steps 1 to 4. It is the same afternoon §4.2 already
schedules, run again, and a campaign that drives two lines schedules it twice.

### 4.2c The slit that sets the axial window, and the scan that measures it

**Why it is hardware and not a fit.** The collected axial half-length `L`
divided by the Rayleigh range is the `z_ratio` of the ramp's own closed form,
and it enters every moment the campaign reads. `docs/methods/03` derives what
it does: the mean pull falls from the pure ramp's value as the window
lengthens, the third cumulant passes through zero near `z_ratio` 1.117 and
reverses beyond it, and the axial mixture is what gives a ONE-photon line a
third cumulant at all. The record knows the ratio as 0.26 with a `+0.20/-0.09`
excursion, and at the tighter waists the window's own correction is 29 per cent
of the pull at 25 microns and 42 at 16. **A number that large, known that
poorly, and sitting inside the observable is a hardware problem and not an
analysis one.**

**Why a slit and not the detector's own aperture.** The R636-10's cathode is
taken as 3 by 12 mm with the 12 mm axis along the beam, and **that geometry is
ASSUMED and not measured**: the attribution comes from Nieddu 2019, a different
bench, while an in-campaign photograph of 2025-07-18 shows the cell detector
labelled Thorlabs PXT1/M. Chapter 12 carries it as an open item and the
arithmetic below inherits that. On the assumed geometry, rotating the tube into
portrait divides the window by four in one discrete step, which keeps 25.5 per
cent of the light at 64 microns, 38.8 at 25 and 60.4 at 16, the loss shrinking
as the waist tightens because the collected share goes as `arctan(L/z_R)` and
saturates. It is still not worth doing, for three reasons that do not depend on
the exact cathode size. It lands at `z_ratio` 1.042 at 16 microns, seven per
cent from the null, which zeroes the third cumulant. It is a discrete step
where the useful variable is continuous. And the tube is side-on, so its
cathode's long axis stands in a fixed relation to the dynode chain and a
ninety-degree rotation puts the light on a different part of the cathode
relative to the electron optics, which changes the gain and the spatial
response and not only the geometry.

**The block.** An adjustable slit at the real image plane of the two-lens relay
of chapter 4, long axis across the beam and narrow dimension along it.

**Needs.** The relay and a slit reading 0.3 to 12 mm. The relay must be
telecentric enough that closing the slit does not change the collection solid
angle, or the scan measures the product of the two and not the window. At the
present conjugates the magnification is 1.78, so that slit range covers
`z_ratio` 0.013 to 0.46 at a 64 micron waist and 0.21 to 7.4 at 16 microns,
the top end capped by the cathode itself.

**Shots.** Four or five slit settings at one power and one temperature, on the
same block, with the fitted centre and the windowed cumulants read at each.
Interleaved with a repeat of the first setting at the end, since the whole
value of the scan is that nothing else moved.

**Go/no-go.** The fitted pull against slit setting follows the closed form the
ramp predicts for `mean(z_ratio)`. It passes if the measured curve matches
within the block scatter. **A disagreement is worth more than the check**: it
says the collection weight is not uniform across the window, which chapter 9
carries as an open item and which the ramp's derivation assumes.

**The sharp test it makes available.** At 16 microns the slit range crosses
`z_ratio` 1.117, where the windowed third cumulant changes sign. That crossing
is a prediction of the geometry with no free parameter, and walking the slit
through it is the strongest single check of the axial model this bench can
make. It also walks the one-photon contamination from 0.0001 at the short
setting to nine times the two-photon cumulant at the long one, so the same scan
measures the delineation from the one-photon prior art instead of assuming it.

**Empty.** A slit returns a number at every setting, so the exposure is not a
null but a transfer: the curve describes this relay, and moving to another
configuration means measuring it again.

**Record.** The slit setting, the relay magnification measured on a target, the
implied `L` and `z_ratio`, the fitted centre, the windowed cumulants at each
analysis window, and the repeat of the first setting.

### 4.3 Lens separations as a creep detector

Caliper the two lens separations bracketing the cell at every setup and
teardown. Absolute accuracy (~1–2 mm) does not pin w₀, but it catches gross
mispositioning where it bites hardest: at configuration S a 1 mm placement
error costs over 2× in on-axis intensity (z_R ≈ 0.8 mm), directly an S₀ error.
Repeatability on fiducial marks is < 0.1 mm, so a setup-against-teardown change
flags mechanical drift of the focus or the retro overlap during the run. A
configuration whose lenses moved is a configuration whose w₀ and ρ are suspect.

### 4.4 Polarization

For S→S lines the strong ΔF = 0 components are driven by the scalar part of
the two-photon operator, with amplitude ∝ ε_f·ε_b. Rajasree (2020) measured
on this line that the rate scales as the squared degree of linear
polarization and vanishes for circular. The configuration table (Nieddu 2019,
verified from the paper): parallel linear (π–π) gives the Doppler-free peak
on a Doppler pedestal and is the 2025 dataset's default. Crossed linear kills the
peak, same-handed circular is forbidden, and opposite-circular (σ–σ′, quarter
waveplates before both the cell and the mirror) gives a background-free peak
at half height.

Prescriptions:

- **Default π–π, polarization defined by a polarizer at the cell**, with a
  per-configuration extinction null: the forbidden settings must read zero, and
  any residual calibrates the impurity.
- **Characterize the retro-path retardance** by Stokes tomography of the
  returning beam. Double-passed birefringence in window, lens and mirror
  pulls ε_f·ε_b below 1 and lets it drift as optics warm: a concrete
  candidate for the 2025 dataset's 30–50% amplitude wander.
- **Fit removable QWP slots before the lens and before the mirror**, so σ–σ′
  is available on demand. It is valuable as a diagnostic, never as the
  default: it removes the Doppler pedestal (a pedestal-subtraction
  cross-check) and it switches off the intensity standing wave, so comparing
  π–π with σ–σ′ at matched power measures the fringe contribution the
  analysis otherwise only models. It stays off the precision path because it
  halves the signal, runs on the vector channel (a computable coupling
  change), and is B-sensitive.
- **One deliberate B block, a bound not a scan.** The line itself is
  m_F-blind (pure scalar operator, J = ½ has zero tensor polarizability) and
  nearly B-blind (Δg_J only, sub-kHz per Gauss). What can bite is the heater:
  its stray field tracks T, and with any circular impurity it opens vector
  satellites that mimic a T-dependent shift. Kill it with bifilar winding or
  bound it with a magnetometer, and measure dν/dB at one condition with a
  known applied field.

---

*[Priorities if the budget shrinks](02_priorities.md) · [Intensity and the light shift](04_intensity-and-light-shift.md)*
