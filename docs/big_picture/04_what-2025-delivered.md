*Chapter 4 of 7 of [the big picture](../BIG_PICTURE.md)*

## 4. What the 2025 dataset delivered

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
  is **measured on this apparatus lineage**: 64 µm (prior), the value
  [Rajasree 2020](../lit/rajasree2020thesis.md) measured on the same laser model,
  the same f = 150 mm lens and the same retro geometry. The 32 µm figure this
  work started from was a Gaussian-optics estimate that cannot account for how
  much of the beam the 3 mm EOM aperture removed, and transit physics excludes
  it. Residual clipping and imperfect retro overlap both push the *effective*
  waist above 64 µm, so the working band is 62–68 µm and ρ = 0.94 ± 0.04.
  Derived in [the lineshape chapter](../methods/02_the_lineshape.md) and
  assembled in [the composite model](../methods/04_the_composite_model.md).
- **The light-shift bound sits just below its own prediction.** S₀(225 mW)
  < 0.26 MHz (95%, from a joint full-profile fit of three sessions, every
  trace with a free centre so the drifting laser costs nothing. An earlier,
  tighter figure was cold-start-inflated and is retracted, preregistration
  addendum 24). The predicted 0.35 MHz at the adopted geometry puts the
  bound **1.3× below it**, equivalently Δα ≲ 810 a.u. against the 1093 a.u.
  the prediction is built on, which is [Orson 2021](../lit/orson2021.md)'s
  computed value and the repository's `DELTA_ALPHA_AU`. That bracket is
  derived rather than typed, the constant scaled by the bound over the
  prediction, so it moves whenever either of them does, and both of them are
  read from `results/stark_joint.csv` and `results/stark_sweep.csv`. The
  in-repo recompute of §3 is a different number, −1145 a.u., and it is not
  what the prediction uses. The tension is modest, and the most conservative
  data subset (dropping the peak that carries the campaign-morning
  session) reaches the prediction itself. Either the intensity sits
  slightly lower than the adopted geometry implies, or |Δα| is slightly smaller than
  computed. A beam-profile measurement decides which. More than twenty times
  below Orson's ~6 MHz null, from shape alone.
  There is a third candidate, and it is the reason the bound is quoted where
  it is rather than lower. Two effects broaden the line with the same
  square-of-power signature as the ramp and are absent from the forward model
  that produced the bound: atomic saturation, and hyperfine pumping through
  the real cascade, which sends 2 to 6 per cent of transiting atoms into the
  other ground state mid-flight. That is a SMALLER quantity than the 8 to 15
  per cent of atoms that decay at all, quoted earlier, since only a share of
  cascades lands in the other half, and its range is wider in kind: it spans
  both the signal-weighted-to-on-axis span and the branching fraction's
  variation across the four lines, which figure 23 computes per line. Injecting the saturation term and
  re-profiling tightens this bound by 2.21, which would widen the bracket
  from 1.3× to about 3× rather than relieving it. The committed bound does
  not move, because the injected law is the two-level homogeneous form used
  with a two-photon Rabi frequency, which is standard practice and not a
  derivation for this level structure, so the effect is carried as a stated
  conservatism with a measured size
  ([notes](../notes/two_photon_saturation_companion.md)).
  Derived in [the AC-Stark ramp chapter](../methods/03_the_ac_stark_ramp.md) and
  reported in [what we found](../methods/07_what_we_found.md) §5.4.

  ![the hyperfine branch, how often it fires, and the three terms it competes with](../../figures/fig23_hyperfine_pumping.png)

  *The third candidate, drawn. The bound is built on the AC-Stark ramp, which
  is the smallest of the three terms that broaden the line as the square of the
  power. The other two are absent from the model that produced it, and the
  second of them is the one worth a picture: the 5P decay does not preserve
  $F$, so an atom that decays while crossing the beam can land in the other
  ground state, hundreds of linewidths away, and is gone from the line rather
  than merely detuned.*
- **β_self is bounded, and the bound's necessity is demonstrated.** The
  fitted collisional width rises ×1.47 while the density rises ×52.5, a
  residual floor rather than resolved collisions, so a naive fit's "4–10σ
  detection" would be an artifact. The headline construction folds that same
  ×52.5-lever 130 °C point into the density-slope fit itself
  (`scripts/run_beta_self.py`), the apparatus having been confirmed unchanged
  across it. The per-peak bound is
  ≲ 0.03–0.05 MHz per 10¹² cm⁻³ (95%, four points on two degrees of freedom,
  with the small-sample scatter and the vapour-pressure density scale both
  propagated). That is an order of magnitude tighter than the three-point
  reading used earlier, which gave ≲0.2–0.4 MHz on one degree of freedom.
  Showing that the two-epoch design was *required* is reported as a
  vapour-cell result. The rule that decides bound against measurement is
  [the statistics chapter](../methods/06_the_statistics.md) §4.5, and the
  result is [what we found](../methods/07_what_we_found.md) §5.1.
- **The ramp's power laws hold.** The width shows no power trend, a null
  under 3–8% block scatter, and the amplitude is consistent with P². The
  laser width is bounded at ≲1.2 MHz on the laser axis, with a central value
  of 1.088 MHz at the measured waist, against the sub-MHz figure quoted for the
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
  the envelope. The power laws come from
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
on bounded support, and in particular the intrinsic $g_1 = +0.566$ at $n = 2$,
which is a number and not a fit. And the third of those cumulants is a
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
