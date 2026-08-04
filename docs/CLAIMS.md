# Claims

What this archive establishes, what it deliberately does not claim, and what
a further measurement campaign would convert or add. The bound values quoted
here sit under the same canonical-number guard that checks the front door
against the committed CSVs. Details and derivations:
[RESULTS.md](RESULTS.md) for the numbers, [BIG_PICTURE.md](BIG_PICTURE.md)
for context, [PLAN.md](PLAN.md) for the proposed session,
[PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md) for everything
that was withdrawn along the way and why.

Terms used throughout: S₀ is the peak light shift on the beam axis at a
stated power, the "ramp" is the closed-form distribution of light shifts a
focused beam imprints on a two-photon line, and the transition axis is the
two-photon sum frequency, twice the laser frequency.

## 1. What the 2025 archive establishes

**Bounds** (95%, each with its own conditionality stated):

- Collisional self-broadening of the 993 nm line:
  β_self < 0.03-0.05 MHz per 10¹² cm⁻³ across the four hyperfine
  components, from a 52.5-fold density lever at four temperatures. This is
  the model-independent, geometry-robust construction: it does not lean
  on the beam waist, and the 20% density-scale systematic is folded in
  on the conservative side. The fitted collisional width grows only 1.47
  times across that 52.5-fold span, so it is read as a floor, not as
  resolved collisions, and that observation is what licenses the bound
  framing.
- Light shift at the campaign maximum of 225 mW:
  S₀(225 mW) < 0.27 MHz, from a joint three-session fit of every point
  of every power profile, minimum consistent with zero shift. The bound
  itself uses only the width-versus-power data, so it does not depend on
  the waist. The prediction it is compared against does: 0.35 MHz
  central, with a 0.28-0.40 MHz band over the waist prior band and the
  retro ratio. The predicted coefficient lies above the 95% limit at
  roughly the two-sigma level (delta chi-square about 4), an exclusion
  but not a comfortable one, and the most conservative data subset's
  bound rises marginally above the central prediction (0.355 against
  0.348), so it excludes none of it. The constraint lands on the
  (Δα, intensity) pair, that is, on the product the light shift actually
  measures, rather than on either factor alone.
- The 2025 laser linewidth: below 1.2 MHz per photon at the waist prior,
  rising with the waist. The per-block fitted values, 1.75 to 2.15 MHz
  on the transition axis, are preliminary: their block-to-block
  variation is partly the collision-laser degeneracy rather than
  resolved laser physics, and they are quoted as the working range, not
  as a result.
- The ramp asymmetry: the skew channel sits below the noise floor at the
  campaign maximum of 225 mW, so what the archive carries is an upper
  bound consistent with zero rather than a quoted interval. The centroid
  pull is a separate channel, and every scan carrying a free centre
  absorbs the first-order shift, which leaves the pull uninformative
  about S₀ in the 2025 data by construction.

**Nulls and scaling laws:**

- No power trend in the linewidth at fixed temperature, against 3-8%
  between-block scatter.
- The two-photon amplitude laws hold within stated exceptions: peak
  amplitude scales as P² at fixed density (log-log slopes 1.83-2.12,
  the one low slope unresolved between SNR bias and real saturation)
  and linearly with density at fixed power (slopes 0.85-1.02).

**Calculated** (anchored, not fitted to this data):

- Differential polarizability Δα(993 nm) recomputed at −1145 a.u.,
  opposite in sign to the published computation it is compared against,
  with the magnitudes agreeing to about 5%. The sign rests on the
  measured 6S lifetime: the published sign would require 9.9 ns against
  the measured 45.57(17) ns, an exclusion at about 210 sigma, with the
  measured static polarizability and tune-out anchoring the 5S side.
  The disagreement is established as real rather than a convention
  artifact. Which side is right remains open until an external
  adjudication.
- The first scalar magic wavelengths for the 5S-6S pair, near 1203.9,
  1287.9 and 1339.6 nm, the 1204 nm crossing being the practically
  usable one. Its 16 to 84 percent band runs 1203.06 to 1204.73 nm. No
  published values were found to the depth searched.

**Method:**

- The lineshape-as-shift-map frame is not new: it is the 1980
  multifrequency-field review of Delone, Kovarskii, Masalov and
  Perel'man, and this archive's core relation reduces exactly to their
  Eq. (5.3). What this archive adds is the closure of that frame for a
  focused beam, where the shift distribution is fixed by geometry
  rather than by unknown field statistics: a closed-form distribution,
  analytic cumulants on bounded support, and a third cumulant that a
  drifting lock cannot corrupt. That channel is why a dataset with no
  usable line centres constrains anything at all.
- A self-calibrating frequency axis: an EOM comb acquired as its own
  bracketing traces in every block, so the axis is calibrated per block
  under a drifting lock, and the tooth spacing is proved exact by a
  velocity-symmetry argument.
- A validation discipline: model ladder, identifiability profiles,
  coverage tested on synthetic truth, and a preregistered audit trail
  in which twenty-four dated addenda record every claim that was
  withdrawn, corrected, or downgraded, including the basin retraction
  of this archive's own headline light-shift bound.

## 2. What is not claimed

- No environmental coefficient of the 993 nm line is measured here.
  The coefficients are bounds, and the collisional floor is not read as
  a detection of Rb-Rb collisions.
- No claim that 993 nm competes with the 778 nm two-photon reference.
  On natural linewidth it starts an order of magnitude behind.
- No claim to the lineshape frame itself, which is 1980 review
  material. The claim is the geometric closure and its cumulants.

## 3. What another campaign would convert or add

Everything in this section is proposed, not scheduled. Verbs are
conditional on the sessions happening.

**A beam-profile measurement alone** (knife-edge or camera, no physics
run) would collapse the transit-laser degeneracy, sharpen the
waist-conditional statements in place, and put the laser-width range on
a measured geometry. It is the cheapest single improvement to the
existing archive, specified in [PLAN.md](PLAN.md).

**A fixed-lock cell session** (the specified follow-up, [PLAN.md](PLAN.md) §8)
would add:

- The first measured AC-Stark coefficient of the 993 nm line, from the
  centre pull that the 2025 drift erased. With the waist also measured,
  that would split the (Δα, intensity) pair and let the experiment
  adjudicate the sign-disputed polarizability.
- The first measured collisional self-shift, from the same centre
  channel across density.
- β_self as a measurement rather than a bound, from same-session
  150-170 °C points interleaved against the block scatter that
  co-limits the archival lever.
- A demonstration of the drift-immune third-cumulant readout, under a
  named condition: the ramp asymmetry reaches detection only with the
  small-waist option (a tighter focus raises S₀ about tenfold), which
  the plan carries as a second-tier item, and the cumulant's sign
  depends on collection geometry that would have to be measured in the
  same session. The fixed lock alone does not reach this.

**A tunable-drive campaign (options map, not a plan)**, mapped in
[FUTURE_TRANSITIONS_titsapph.md](FUTURE_TRANSITIONS_titsapph.md): the drive
laser is tunable, so the same machinery would reach other rubidium
two-photon lines. Running it on the 778 nm reference line, where other
groups have already measured the environmental coefficients and the magic
wavelength, would calibrate the method against known values rather than
add a coefficient. Measuring the 760 nm 7S line would re-derive on this
bench the external rate that the expected self-broadening of the 993 nm
line is currently anchored to, and would turn the computed van der Waals
ratio behind that anchor from an input into something the data test.
Across three or more rungs the per-line coefficients would become scaling
laws in the principal quantum number, which discriminate a calculation
more sharply than any single coefficient does.

**A guided-mode extension**, sketched in
[BIG_PICTURE.md](BIG_PICTURE.md) §6 and budgeted in
[notes/guided_mode_two_photon_design.md](notes/guided_mode_two_photon_design.md),
not specified as a session: the same measurement inside a hollow-core
fibre or around a nanofibre, where the intensity distribution is set by
the guided mode rather than by a Gaussian focus. The budget note is
mostly a record of what does not carry over. The closed-form ramp
weight is derived for atoms crossing a focused beam and does not
describe trapped atoms, whose shift distribution is set by their
vibrational energies and carries the opposite skewness. Fluorescence
cannot leave along the fibre at any density that gives signal. The
light shift rather than the available power sets the usable drive. What
does carry over is the operation the archive is built on, mapping a
known intensity geometry onto a shift distribution and reading its
cumulants, and one result closes analytically on the new geometry: the
trap's own inhomogeneous shift is set by the atom temperature alone,
with the trap depth and waist cancelling out of it. None of this family
is claimable from the 2025 data.

The dependency map, which measurement unlocks which claim, is the first
section of [BIG_PICTURE.md](BIG_PICTURE.md).
