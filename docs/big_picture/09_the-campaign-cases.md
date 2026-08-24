*Chapter 9 of 9 of [the big picture](../BIG_PICTURE.md)*

## 9. The two campaign cases, side by side

[Chapter 5](05_next-vapour-cell.md) weighs each vapour-cell measurement with its cost and
[chapter 6](06_next-nanofibre.md) does the same for the guided platform. This
chapter answers the question those two leave open: what does a new campaign
add in total, if it is cell-only, and what does the fibre add on top. Each
scenario is stated in three registers, the physics, the record, and the
instrumentation that outlives the campaign, because the three are different
kinds of gain and conflating them is how campaign cases go soft. Every
number is read from a committed file, named inline. Nothing below is
scheduled or agreed.

A reader with no fibre loses nothing on their path by stopping after the
first scenario. The fibre thread of this repository is chapter 6, the second
scenario here, and [the sized candidate](../notes/onf_candidate.md), and it
is deliberately separable: the analysis pipeline is platform-neutral, and
[ADAPTING.md](../ADAPTING.md) carries the seam map for a different
transition or a different geometry.

### Scenario one, a new vapour-cell campaign alone

**The physics.** Four conversions, from bounds to measurements.

* The beam waist, measured in an afternoon with no atoms, converts every
  intensity-denominated number in the record at once, since the light shift
  goes as one over the waist squared
  ([chapter 5](05_next-vapour-cell.md), item 1).
* The light-shift coefficient: one morning of randomised power cycling under
  the repaired lock detects the predicted shift at 3.8 sigma and separates
  the two disputed polarizability signs at 8 sigma if the shift is the
  predicted size, conditional on the lock holding 0.02 MHz per minute
  ([CLAIMS](../CLAIMS.md) section 3, `results/projections.csv`).
* The collisional coefficient: same-session 150 to 170 C points with the
  block noise cut fourfold resolve the expected rate near 10 sigma. Both
  halves are needed, and with the noise floor uncut the reach is 3 sigma.
  Even resolved, the coefficient carries the 20 per cent density-scale
  systematic until an independent density measurement
  ([CLAIMS](../CLAIMS.md) section 3).
* The laser content: the kernel question is tested at one corner and open in
  between (`results/laser_kernel.csv`). The cell campaign's own routes to
  the content are the lock's error signal and a fast-scan comb block
  ([plan chapter 7](../plan/07_acquisition-settings.md)).

**The record.** This scenario converts the flagship analysis from a method
with bounds into a method with measured coefficients, which is its strongest
single form, and it enables the matrix-element-by-null measurement at
1297.5 nm as a second, cheap result riding the same session
(`FUTURE_TRANSITIONS_titsapph.md` section 5.1: the 6S to 7P strength read at
1.8 per cent by frequency metrology, with a sign-reversal test of the
asymmetry channel and a calibrated shift injector as by-products).

**The instrumentation.** What outlives the campaign: a laser whose width
and drift budget are characterised against the atoms themselves, a measured
waist protocol for the bench, and the O-band shift injector as a standing
calibration tool, 3.6 kHz per picometre at a known crossing, usable by any
later experiment that needs a known injected shift.

### Scenario two, the fibre added

Everything in scenario one, plus four additions no cell can provide.

**The physics.**

* The laser's shape, measured independently. The cold trap-off line at the
  fibre is the known natural width plus the laser contribution plus a
  0.14 MHz transit, and the molasses temperature sweep turns the transit
  term into its own sqrt(T) ladder, so the laser measurement calibrates
  itself (`results/onf_candidate.csv`). Fed back as a prior, it recovers
  the collisional coefficient's error to 0.36 of the free-kernel fit
  on the DATA already taken, against the exact floor of 0.585 that any
  single-component measurement hits (`results/kernel_identifiability.csv`,
  the joint rows). This is the one addition that improves the committed
  record retroactively, before any new cell point is taken.
* The intercept budget closes. With density, the sqrt(T) ladder, the laser
  prior and geometry each pinning their own slot, the width intercept
  becomes overdetermined, and the sum of independently measured parts
  against the measured whole is a falsifiable closure test rather than a
  decomposition argued from a fit.
* The near-surface lineshape. The two-peak pushing profile observed on this
  exact line at this exact platform ([Gokhroo 2022](../lit/gokhroo2022.md))
  has never been modelled, and the atom-surface potential on this platform
  class is now known to carry two components, Casimir-Polder plus a
  device-dependent electrostatic term
  ([Pennetta 2026](../lit/pennetta2026.md)). Completing that observation
  quantitatively, with the 6S surface coefficient as an output, is an open
  problem this pipeline is built for
  ([the sized candidate](../notes/onf_candidate.md)).
* Signal feasibility is not a projection: this transition has been driven
  through a 400 nm nanofibre with cold atoms at 25 to 40 counts per
  millisecond ([Rajasree 2020](../lit/rajasree2020spin.md)).

**The record.** The guided-platform study becomes two results in one: the
near-surface physics above, and the joint-metrology payback into the
committed cell record, quantified row by row in
`results/kernel_identifiability.csv`. A fibre measurement therefore
improves the committed record retroactively, before any new cell point is
taken, which no other addition on this list does.

**The instrumentation.** This register is where the fibre scenario is
strongest, because every item below outlives the campaign as a working tool
of the platform it runs on.

* A per-run calibration of the electrostatic surface-charge term at 6S
  sensitivity, on the same class of fibre that Rydberg-near-fibre
  experiments probe at far higher sensitivity, where that term is a known
  limiter ([Pennetta 2026](../lit/pennetta2026.md)).
* A real-time, atom-based monitor of surface adsorbate dynamics, which is
  the community-wide fibre-degradation problem, watched through the line
  while it happens.
* The two-colour trap's magic power ratio for this transition, computed from
  the committed polarizability engine (the differential polarizability
  changes sign between the trap colours, +3086 atomic units at 750 nm
  against -804 at 1064 nm, `rb5s6s/polarizability.py`), so the trap can be
  made shift-free for spectroscopy by tuning a ratio the bench already
  controls, and the same ratio scans the trap-surface distance.
* The quadratic Zeeman injector: the hyperfine mismatch between 5S and 6S
  makes a bias field a calculable line shifter at 1.9 and 4.2 kHz per gauss
  squared for the two isotopes, from committed constants, a free calibration
  channel for any line-centre instrument on this bench.
* A characterised laser, as in scenario one, but now characterised through
  the same guided path that fibre experiments use, under the shared-path
  condition the candidate note states.

### What decides between them

The cell-only scenario stands on its own and converts the record's bounds
into coefficients. The fibre adds the only lever that acts on the
laser-shape confound retroactively, the closure test, and the near-surface
programme, at the cost of fibre time and the transfer condition. The two
scenarios nest rather than compete: the second contains the first, and the
fibre items are exactly the ones
[chapter 7](07_limitations-and-identifiability.md) names as outside any
cell's reach.
