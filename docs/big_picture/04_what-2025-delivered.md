*Chapter 4 of 10 of [the big picture](../BIG_PICTURE.md)*

## 4. Deliverables of the 2025 dataset

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

The 2025 campaign (297 traces: four hyperfine peaks, 70–130 °C, 25–225 mW)
was taken with a drifting, hand-re-centred lock (MHz-scale line motion
between blocks, with the held-lock rate itself bounded at order 0.02 MHz/min,
`APPARATUS.md` §6). That one fact organises
everything: **absolute centres are lost, line shapes survive**. The analysis
therefore extracts what shapes alone can support, and states everything else
as a bound. Concretely:

- **A validated lineshape model.** Natural (3.49 MHz) ⊗ transit ⊗ laser
  reproduces every line at reduced χ² between 0.78 and 1.09 across the 32
  fitted conditions, mean 0.89. Why those sit below one is stated once,
  beside the fit gallery in the README. The per-condition fits hold the
  ramp at zero, and the shared ramp coefficient of the width-versus-power
  fit rails at zero, so the ramp is a component the record bounds rather
  than one these fits resolve. The beam waist
  was, through 2026-09-21, **a convention taken from the apparatus lineage**: the value
  [Rajasree 2020](../lit/rajasree2020thesis.md) reprints from Nieddu's profile of the
  predecessor laser, through the same f = 150 mm lens and retro geometry and without
  this beam's 3 mm modulator bore. The 32 µm figure this
  work started from was a Gaussian-optics estimate that cannot account for how
  much of the beam the 3 mm EOM aperture removed, and transit physics excludes
  it. Residual clipping and imperfect retro overlap both pushed the *effective*
  waist above the lineage value, so that reading gave a band with ρ = 0.94 ± 0.04.

  **Neither the lineage convention nor that band stands.** The working region since
  2026-09-17 was revised to **40 to 45 µm**, on the reading that the beam is clipped
  by the 3 mm modulator bore and carries M² greater than one, both of which the
  lineage value predates, and owner order O44 (2026-09-21) then retired the lineage
  convention itself: the record now carries `constants.W0_CENTRAL_M`
  = [42.38](../../rb5s6s/constants.py "ref:constant:W0_CENTRAL_M:1e6") µm, so w0 ≈ 42 µm, the bore-limited actual focus this apparatus calculates for its own
  input beam, with its band 40 to 45 µm, anchored to that calculation.
  Every number on this page that is conditional
  on the waist is therefore conditional on this calculated value, and the
  conditional statements stand while their conditioning value has moved.

  **And the waist cannot be recovered from the line.** Closed on synthetic traces at three noise
  levels on 2026-09-19, the estimator carries a structural offset of about +0.32 µm that appears
  with any noise, saturates immediately, and survives the removal of its prior, so it is not a
  regularisation artefact and it may not be subtracted. The consequence for this page is direct:
  **a direct beam-waist measurement is load-bearing and not merely desirable**, and no
  twin-subtracted waist is quoted anywhere in this record.
  Derived in [the lineshape chapter](../methods/02_the_lineshape.md) and
  assembled in [the composite model](../methods/04_the_composite_model.md).
- **The width channel reaches the differential polarizability through the
  geometry, and it is a null.** What the traces bound is the shift per recorded
  watt, below [0.810](../../results/stark_joint.csv "ref:stark_joint:kappa_ub95:primary") MHz/W against
  [3.241](../../results/stark_joint.csv "ref:stark_joint:kappa_pred:prediction") predicted at the ruled
  waist. The bound is read through the fitter's scalar bore factor, which sits 9.1
  per cent from the spatially resolved clipped beam on the line's centroid (the
  strict xfail in `tests/test_volume_world.py`). How much of that reaches the width
  channel is not measured yet, against a margin of four. Taking the geometry as a
  stated prior and inverting the usual
  comparison, the magnitude comes out below
  [361](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:limit:delta_alpha_abs_ub95_profile")
  a.u. in this record's own construction and below
  [404](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:limit:delta_alpha_abs_ub95_posterior")
  a.u. read as a posterior over the same committed likelihood, against the
  [2.23](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:estimator:sigma_from_zero")
  σ that separates the fit from zero, short of a detection.

Which uncertainty dominates depends on
  the row taken: the posterior's spread is the data's, the geometry
  priors carrying
  [0.0123](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:budget:geometry_share_of_variance")
  of its variance, while the quoted limit's whole ±[20](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:limit:delta_alpha_abs_ub95_profile:err") is geometric, because
  the crossing behind it is a fixed committed number. Beam metrology sharpens
  the second and not the first. The older hand-scaled form, |Δα| ≲ 283 a.u.,
  is derived rather than typed: the computed value scaled by the bound over the
  prediction. Until 2026-09-22 it read 839 and agreed with the construction's limit
  because the two were one micrometre of waist apart, which is arithmetic and not
  corroboration. At the ruled waist they differ by a factor of 1.28, and why has
  not been read.

  The bound behind it is S₀(225 mW) < 0.18 MHz (95%, from a joint
  full-profile fit of three sessions, every trace with a free centre so the
  drifting laser costs nothing. An earlier, tighter figure was
  cold-start-inflated and is retracted, preregistration addendum 24). The
  predicted 0.73 MHz at the calculated geometry sits above it by a factor of
  about 4.0.

  The exclusion holds on the full fit, the limit lying
  below every point of the predicted envelope, and this bullet used to state
  it without its two qualifications. Its strength is a range, 8.0 to 9.4 σ
  across the envelope at the ruled waist, read off the committed profile (2.0 to 2.4 σ
  at the retired waist until 2026-09-22), and conditional on the fitter's reduced
  forward model, which carries no bore, no Doppler pedestal and no retro tilt and
  whose transit is narrower than the node Monte Carlo's by 3 to 5 per cent. On this
  construction it survives leaving any one
  peak out: every arm clearly excludes, so no count of arms weakens it.

  Those missing terms widen the model line or raise its shift, so adding them tightens
  the limit and does not relax it. The limit is also robust inside the fit's own model
  family: mirroring the ramp to the other side of the line, changing the natural width
  by 3 per cent, or narrowing the transit by 5 per cent moves it by at most about 7 per
  cent, and each change of width worsens the fit. What it does not test is the
  intensity at the atoms. It bounds the shift per recorded watt at the ruled waist, so
  it reaches the polarizability only through where the power was read and how strong
  the return beam is at the atoms, and the record measures neither there.

  The channel it is read from qualifies it further. The fitted model reads the shift off
  the width's growth with power, where at the ruled intensity saturation and hyperfine
  pumping should outweigh the ramp several times over, and neither is in the fit. The
  traces show no such growth, the signal outgrows the square of the recorded power in
  three lines, and their readings of the intensity at the atoms sit well below the
  model's. Nor do the widths narrow once the scatter between blocks is counted, and
  every ladder descended in power, so power and time are one regressor. The limit
  assumes each line's core width fixed across power. An unmodelled narrowing would
  hide the ramp's growth and make it too tight, not conservative.

  The fuller archive fit is stronger and keeps all four, and carries
  a failing prior-tension gate of its own. Separately the limit moves by
  a factor of [1.110](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:limit:construction_spread")
  between two readings of one likelihood, about 1.002 of which is generic to
  those two readings and would exist for an exactly Gaussian likelihood, and
  1.114 of which is this profile's own shape. **The gap is not
  withdrawn, only the number attached to it**: the computed value sits in the
  upper tail at posterior probability
  below 5e-06, which is 0 of 200 000 draws
  (4.9e-11 under the crossing), and Orson's value likewise below 5e-06
  (2.3e-10 under the crossing), the two candidate values 1.9e-10 apart
  under the crossing, real under both constructions and quotable to neither's
  third digit, and the primary limit sits below the whole predicted envelope.

Either the intensity sits lower than the accepted geometry implies, or |Δα|
  is smaller than computed, or the forward model is missing something that
  suppresses the width response to power. A beam-profile measurement
  separates the geometry reading from the other two.

  The prediction is built on the magnitude of this repository's own
  recompute, **[-1131.8](../../results/polarizability_deep.csv "ref:polarizability_deep:delta_alpha:at_drive") a.u.** (§3), the value `DELTA_ALPHA_AU` now carries, the
  earlier value having summed the 9P-and-above group at zero frequency, its digits
  kept in the private correction record. The
  same quantity re-derived with the 6S tail summed dynamically reads
  [-1131.8](../../results/polarizability_deep.csv "ref:polarizability_deep:delta_alpha:at_drive") ± [5.9](../../results/polarizability_deep.csv "ref:polarizability_deep:delta_alpha:at_drive:err") a.u.
  (`results/polarizability_deep.csv`), the constant moving in its own wave.
  [Orson
  2021](../lit/orson2021.md)'s computed value is 1093, about five per cent
  smaller and of the other sign, kept beside ours as
  `DELTA_ALPHA_AU_ORSON2021`. The sign is adjudicated and not measured, and
  no bound here depends on it, because every bound reads the magnitude. Set
  against the only prior search on this line, the comparison that transports
  is each bound against its own prediction, because no single cross-apparatus
  ratio survives: the two differ in power convention, waist and beam
  architecture, and their figure is a one-sigma resolution against this
  record's 95 per cent limit.

  Orson's null sits
  [18](../lit/orson2021.md "ref:lit:orson2021:null_over_own_prediction")
  times above the shift their own Δα predicts, so it tests neither the size
  nor the sign, where this bound sits below the shift predicted at its own
  conditions.
  The third of those readings has a named mechanism, and it is the reason the
  bound is quoted where it is rather than lower. Two effects broaden the line with the same
  square-of-power signature as the ramp and are absent from the forward model
  that produced the bound: atomic saturation, and hyperfine pumping through
  the real cascade, which sends 2 to 6 per cent of transiting atoms into the
  other ground state mid-flight.

  That is a smaller quantity than the 8 to 15
  per cent of atoms that decay at all, quoted earlier, since only a share of
  cascades lands in the other half, and its range is wider in kind: it spans
  both the signal-weighted-to-on-axis span and the branching fraction's
  variation across the four lines, which figure 23 computes per line.

  Injecting the saturation term and
  re-profiling tightens this bound by 2.21, which would widen the bracket
  from 1.4× to about 3× rather than relieving it. The committed bound does
  not move, because the injected law is the two-level homogeneous form used
  with a two-photon Rabi frequency, which is standard practice and not a
  derivation for this level structure, so the effect is carried as a stated
  conservatism with a measured size
  ([notes](../notes/two_photon_saturation_companion.md)).
  Derived in [the AC-Stark ramp chapter](../methods/03_the_ac_stark_ramp.md) and
  reported in [what we found](../methods/07_what_we_found.md) §5.4.

  ![the hyperfine branch, how often it fires, and the three terms it competes with](../../figures/fig23_hyperfine_pumping.png)

  *The model-incompleteness reading, drawn. The bound is built on the AC-Stark ramp, which
  is about a sixth of the sum of the three terms that broaden the line as the
  square of the power. Which of the three is smallest varies by line, since
  hyperfine pumping runs from below the ramp on 993.4207 and 993.4192 nm to
  above it on the other two, so no fixed ordering holds.

  The other two are absent from the model that produced it, and the
  second of them is the one worth a picture: the 5P decay does not preserve
  $F$, so an atom that decays while crossing the beam can land in the other
  ground state, hundreds of linewidths away, and is gone from the line rather
  than merely detuned.*
- **β_self is bounded, and the bound's necessity is demonstrated.** The
  fitted collisional width rises ×1.47 while the density rises ×48.1 (Alcock),
  a residual floor rather than resolved collisions, so a naive fit's "4–10σ
  detection" would be an artifact. The headline construction folds that same
  ×48.1-lever 130 °C point into the density-slope fit itself
  (`scripts/run_beta_self.py`), the apparatus having been confirmed unchanged
  across it. The per-peak bound is
  ≲ 0.02–0.04 MHz per 10¹² cm⁻³ (95%, four points on two degrees of freedom,
  with the small-sample scatter and the vapour-pressure density scale both
  propagated).

  That is an order of magnitude tighter than the three-point
  reading used earlier, which gave ≲0.2–0.4 MHz on one degree of freedom.
  Showing that the two-epoch design was *required* is reported as a
  vapour-cell result. The rule that decides bound against measurement is
  [the statistics chapter](../methods/06_the_statistics.md) §4.5, and the
  result is [what we found](../methods/07_what_we_found.md) §5.1.
- **The ramp's power laws hold in the width channel, and the amplitude
  departs.** The width shows no power trend, a null under 3–8% block scatter.
  The amplitude was read as consistent with P², and **tested rather than
  described in 2026-08-18 it is not**: three of the four log-log slopes
  exclude 2 under a block bootstrap, the departure replicates in an
  independent session and is invariant under ladder direction, and its
  ordering across lines follows their brightness rather than any atomic
  quantity, which makes it a detection signature with no attributed
  mechanism ([the note](../notes/amplitude_departure_from_p2.md)).

  The
  laser width is bounded at ≲1.2 MHz on the laser axis, with a central value
  of 1.088 MHz <!-- other-quantity: this section's own laser-width central value, not identifiability_profile's zoom_dchi2 cell --> at the waist convention, against the sub-MHz figure quoted for the
  same laser in [Gokhroo 2022](../lit/gokhroo2022.md). The drift-immune skew
  observable is derived and bounded, and detecting it requires a tighter
  focus. The premise
  the whole method rests on, that the line *shape* outlives the drift, is now
  **supported by a synthetic closure test**, not only by the timescale
  argument. Between-scan drift is absorbed exactly by the
  per-scan free centres, and a synthetic closure test
  (`tests/test_intrascan_drift.py`) bounds the leftover *within*-scan effect at
  well under a fifth of the statistical error on the recovered asymmetry at the
  recorded envelope rate of 4 MHz/min on the laser axis, which is far above any
  rate the campaign itself showed. It reaches order-S₀ only at tens of times
  the envelope.

  The power laws come from
  [the AC-Stark ramp chapter](../methods/03_the_ac_stark_ramp.md), and the laser
  bound from [the lineshape chapter](../methods/02_the_lineshape.md) §2.3.
- **A reproducible pipeline.** Every number regenerates from the frozen raw
  data, within the tolerance `scripts/verify_results_fresh.py` states and to
  the printed digit in the environment
  [`results/ENVIRONMENT_OF_RECORD.md`](../../results/ENVIRONMENT_OF_RECORD.md)
  records. Every CSV row carries a status tag (bound, null,
  measured and so on), and the documentation is written to be picked up by
  whoever works on this next. The pipeline itself is walked through in
  [`methods.md`](../methods.md).

**What of the method is actually new, stated at the size it will survive.** The
relation the analysis rests on, that the signal-weighted shift distribution goes
as $|s|^{n-1}$, is **not new**. It reduces exactly to Eq. (5.3) of the 1980
<!-- term-of-art: review names the cited article's genre -->
review of Delone, Kovarskii, Masalov and Perel'man, checked against the
shipped implementation to
$7\times10^{-12}$, and that review already carries the lineshape as a map of the
shift distribution and the $k$-photon intensity weighting
([delone1980](../lit/delone1980.md), and §5 of [LITERATURE.md](../LITERATURE.md) for
the full concession).

Three things survive it, and they are the list §5.2a of
[LITERATURE.md](../LITERATURE.md) leaves standing. In Delone's setting the shift
distribution is the statistics of a fluctuating field, unknown in advance, so
their integral stays formal. In a focused beam that distribution is fixed by
**geometry**, so the integral closes. The closure gives **analytic cumulants**
on bounded support, and in particular the intrinsic $g_1 = -0.566$ at $n = 2$,
which is a number and not a fit. And the third of those moments is a
**drift-immune channel**, which is
what makes a dataset with no usable line centres say anything at all.

§5 claim 1 of the same document still enumerates four rather than three. The
two it adds are the fringe-averaged treatment, with the M19 result that a
retro standing wave does not move the mean, and the evanescent-geometry
invariance of the dA ∝ dI/I step. §5.2a asks for claim 1 to be narrowed to the
three and that request is still open, so the count here follows
§5.2a. The invariance is the bridge §6 below is built on, and dropping it from
this list drops it as a novelty claim, not as a result.

This work turned a drifted-lock dataset into a validated model, one
near-prediction bound, one demonstrated-necessary bound, and a method, but no
coefficients.

---

*[Goals and prior art](03_goals-and-prior-art.md) · [The next vapour-cell session](05_next-vapour-cell.md)*
