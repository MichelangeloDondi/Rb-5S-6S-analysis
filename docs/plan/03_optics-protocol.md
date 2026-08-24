*Chapter 3 of 11 of [the plan](../PLAN.md)*

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
aperture. The PMT of record is the side-on r636-10 with a 3 × 12 mm cathode,
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
