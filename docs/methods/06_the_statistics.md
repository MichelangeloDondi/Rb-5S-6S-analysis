*Chapter 6 of 8 · [methods index](../methods.md)*

**The question.** What makes a width taken from this dataset an honest number
rather than a confident one?
**Takes.** The lineshape, AC-Stark and composite-model chapters, whose
parameters are the ones being fitted.
**Gives.** The pre-registered rule that decides measurement against bound, and
the error budget every result in the next chapter carries.
**Skip if.** You are reading for the physics rather than the inference. This is
the longest chapter in the set at over four hundred lines, and §4.5 alone
carries the rule the headline results turn on.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## 4. The statistics, from first principles

### 4.1 Weighted least squares with *measured* weights

A fit minimizes $\chi^2=\sum_i \big(d_i-m_i\big)^2/\sigma_i^2$. The correct
$\sigma_i$ is the real per-sample noise, which here is *not* constant: PMT shot
noise grows with signal. We measured (module M1, §4.4)

$$\sigma^2(V)=a^2+bV$$

per condition and use it as the weights. Unweighted fitting would let the
bright peak dominate and would misstate every error bar. Using the measured
$\sigma(V)$ is what makes the reported uncertainties meaningful.

That law also sets the unit of every residual panel in this repository. A
residual strip is plotted in units of each point's own $\sigma(V)$ under its
block's noise law, so a value of one is a one-sigma miss wherever on the trace
it sits.

### 4.2 Hierarchical fitting: share what physics shares, free what drifts

Each condition has five back-to-back repeats of the *same* physical line, but
the drifting 2025 laser moves the line center and the PMT gain wanders. So we
fit the repeats **jointly**, sharing the physics and freeing the nuisances:

- **shared** across repeats: the lineshape parameters $\gamma_\text{coll}$,
  $\sigma_\text{laser}$ (and optionally transit),
- **per-trace**: amplitude $A_i$, center $\nu_i$, and a tilted baseline
  $b_{0,i}+b_{1,i}\nu$.

This is what makes drifted 2025 data usable: the drift lives in the per-trace
centers, the physics in the shared shape. The same idea extends across
temperatures, so `fit_beta_self()` ties $\gamma_\text{coll}(T)=\beta_\text{self}N(T)$
with a single shared $\beta_\text{self}$, turning four widths into one slope.
Treating $\beta_\text{self}$ as $T$-independent here is an approximation.
[Lewis 1980](../lit/lewis1980.md) Table 4.1 predicts an additional $T^{0.3}$
coefficient scaling for an $n=6$ potential, a rise of about 5% from 70 to
130 °C, checked directly by refitting each peak's four raw widths with that
scaling folded into the density axis. The result shifts $\chi^2$ by less than 0.4
against a between-block scatter of 140–250 kHz, roughly an order of
magnitude larger than the predicted effect, so today's dataset has no power
to test the exponent. The assumption of a flat $\beta_\text{self}$ is unresolved,
not confirmed.

**The full hierarchy** (`fit_global()`, module M4b) fits *all* peaks and
temperatures at once, sharing each parameter at the level the physics licenses
and the choice of level is where the physics really enters:

- $\sigma_\text{laser}$ is shared **per temperature, across the four peaks**.
  The four lines are measured within one temperature dwell, so they see the
  *same* laser at that moment and jointly over-constrain $\sigma_\text{laser}(T)$
  which lets its drift across the cooling session be *measured* rather than
  mistaken for collisions. (Sharing one *global* $\sigma_\text{laser}$ across
  all temperatures, as a naive fit does, is exactly what manufactures a false
  detection. See §4.5. For a stable lock, global sharing becomes
  correct.)
- $\beta_\text{self}$ is shared **per isotope**, not globally: collision
  cross-sections need not be equal for ⁸⁵Rb and ⁸⁷Rb, so we *test*
  $\beta_{85}$ vs $\beta_{87}$ rather than assume them equal.
- the transit width is shared globally (same beam, same $\sqrt T$ law),
  amplitude, center, baseline stay per-trace.

This breaks the Voigt degeneracy (§4.3) two ways at once, through the density lever
arm *and* the four peaks pinning one $\sigma_\text{laser}(T)$, and it comes with
a leave-one-condition-out check that no single block drives a shared
parameter. *Code:* `fit_condition()`, `fit_beta_self()`, `fit_global()`.

**The lever cross-check** (`lever_crosscheck_beta()`, module M4d) is the packaged form of
this hierarchy, the value and the *full error budget* the paper quotes. Its
headline is the **internally-consistent 70/90/110 °C cooling sweep** (one
session, monotonic cooling), fit across a model-form grid of transit cusp
(Lehmann) vs no-cusp (Voigt) $\times$ $\sigma_\text{laser}$ shared per $T$
(Model A) vs per-block (Model B). The spread of $\beta$ across those cells *is*
the model-form error bar. With the $w_0$-band and a leave-one-**peak** or
leave-one-**temperature** robustness scan it returns **one $\beta$ per isotope
carrying three separately-sourced error bars** (statistical, model-form,
$\text{confound}/w_0$). A synthetic-injection closure test (`tests/test_lever_crosscheck`)
recovers a known $\beta$ through the whole 20-trace machinery, so the pipeline
itself is validated by that recovery, not assumed.

The dataset's curated 130 °C anchor (the `serves_t130` traces, 225 mW) would
triple the density lever ($N{\times}16.2\to{\times}52.5$), and the lever cross-check
uses it as a **lever test**: adding it pulls the joint $\beta$ far below the
cooling-sweep value. The lesson is not "bad block". It is that
$\gamma_\text{coll}$ **barely grows with density**: it rises only ${\sim}1.47\times$
across a ${\times}52.5$ density span (70→130 °C), and the 130 °C widths sit *on*
that near-flat trend, whereas a real binary-collision width is *linear* in $N$.
So the fitted $\gamma_\text{coll}$ is a residual floor, not resolved collisions,
and $\beta$ is a **lever-dependent bound** and not a value, which is exactly why the
model-independent bound is the headline. (The 130 °C data are the extreme end of the
session, a secondary caveat that cannot be fully separated. Either way a fixed-lock session needs
*same-session* high-density points to resolve any real slope.)
*Run:* `run_lever_crosscheck.py` → `results/lever_crosscheck.csv`, with numbers in the
results ledger (`docs/RESULTS.md`).

### 4.3 The degeneracy and the full covariance

Because of the Voigt near-degeneracy ([§2.4](02_the_lineshape.md)), a single-condition fit returns
$\sigma_\text{laser}$ and $\gamma_\text{coll}$ with correlation
$\approx-0.85$: individually shaky, sum robust. We therefore (i) always report
the full covariance, and (ii) design $\beta_\text{self}$ to ride on the
$\gamma_\text{coll}$ **difference** across densities, where the shared laser
contribution cancels. Reported errors are additionally inflated by
$\sqrt{\chi^2_\text{red}}$ (model imperfection) and $\sqrt{\tau_\text{int}}$
(wing-noise correlation, §4.4), conservative by policy. Covariances are
obtained from a singular-value decomposition of the Jacobian rather than
$(J^{\mathsf T}J)^{-1}$, to stay numerically safe when parameters span very
different scales. *Code:* `fitutil.cov_from_jac()`.

### 4.4 The noise model and the second-difference estimator

To measure $\sigma(V)$ without contamination from the signal's slope, we use
**second differences**,

$$e_i=\frac{v_{i+1}-2v_i+v_{i-1}}{\sqrt{6}}$$

which annihilate any locally-linear trend exactly (so a bright line's steep
flank contributes nothing) while having unit response to white noise, so for
white noise of standard deviation $\sigma$, $e_i$ also has standard deviation
$\sigma$. Binning $e_i$ by local signal level and fitting the variance law
$\sigma^2=a^2+bV$ then gives $a$ (a floor by construction of the model, though measured on this dataset it rises with power, so it is shot noise on an optical background rather than electronics or dark current, and the law unifies as $\sigma^2=b(V+V_{\rm bg})$) and $b$ (the
shot-noise, "Fano", term). Wing-noise **correlation** is measured separately
by the blocking method and summarized as an integrated correlation time
$\tau_\text{int}$, which inflates the fit errors as above. We found $b$ flat in
$T$ (the trapping test of [§2.7](04_the_composite_model.md)) and $\tau_\text{int}$ small. *Code:*
`noise.py`.

### 4.5 Statistics versus systematics: the measurement-vs-bound rule

A large shared fit can return a very small formal error that is
nonetheless *wrong*. If you share $\sigma_\text{laser}$ across blocks recorded
hours apart and the laser width actually drifted between them, the fit will
absorb that drift into $\gamma_\text{coll}$ and report a confident collisional
signal that is really instrument drift. Our guard is **pre-registered** and
model-independent:

1. Collisional broadening *must* be monotonic in density. So take **raw**
   line widths (smoothed half-max $\times$ the ruler rate, no fitting) and
   check monotonicity in $N$.
2. Fit $W(N)=W_0+\beta_\text{eff}N$. The RMS scatter of the blocks about this
   line is treated as a **between-block systematic** and added in quadrature
   to each point's error.
3. Claim a **measurement** only if $|\beta_\text{eff}|/\sigma_\text{syst}\ge3$,
   otherwise report a **bound**.

Deciding this rule *before* looking is what separates a supported answer from
the overconfident one (see [what we found](07_what_we_found.md)). *Code:* `beta.collisional_slope()`,
`scripts/run_beta_self.py`.

### 4.6 Validation on synthetic data before real data

No fitter is allowed near real data until it recovers *known* injected truths
from campaign-like synthetics, checking bias, error coverage, and the
degeneracy. Then every headline conclusion is re-derived by
an **independent method** (for instance the sweep rate by FFT and autocorrelation, and the
noise law by differencing sibling repeats). Several of our own bugs were caught
exactly this way, and the verification records live in the module docstrings.

**What a same-model closure test does and does not establish.** Generating
synthetic data from the model and recovering the injected truth validates the
*implementation*: the estimator is unbiased, the optimizer converges, the
quoted intervals cover, the degeneracies behave, all of it **under the
simulated generative model**. It cannot validate the model itself: whether
the physical lineshape is the right one, whether a mechanism is missing, or
whether the real noise matches the simulated law. Those questions need
different evidence, and in this analysis they get it
elsewhere. The nested model ladder (§4.9) lets the data reject or demand each
component. The model-form comparison asks whether the dataset can even
distinguish competing kernels, and it cannot, which is reported rather than
resolved by assumption. The noise law is *measured* from sibling repeats
(§4.4) rather than assumed. The residual audits look for structure no fitted
component absorbs. Closure certifies the machinery. The physics has
to earn its place separately.

### 4.7 Choosing between competing lineshapes: the BIC

To ask *which* model form the data prefer, a smooth Gaussian extra-broadening
(a Voigt) against the cusped transit exponential (the Lehmann shape, [§2.5](02_the_lineshape.md)), we
compare the **Bayesian information criterion**, $\text{BIC}=\chi^2+k\ln N$,
whose definition and reading scale are in
[information criteria](../wiki/information-criteria.md).

Voigt and Lehmann have the *same* $k$, so their comparison is
essentially which shape fits better. This is the tool for the Lehmann-cusp
test, and [what we found](07_what_we_found.md) reports what it returned.

### 4.7a Which criterion, and why the answer depends on $N$

BIC is not the only way to penalise a parameter, and the choice is not a matter of
taste here because $N$ varies by four orders of magnitude across the places
this record makes a complexity decision. The two standard criteria differ only in that penalty,
$\text{AIC}=\chi^2+2k$ against $\text{BIC}=\chi^2+k\ln N$, so which is more
conservative depends entirely on how much data there is
([information criteria](../wiki/information-criteria.md)). In this repository
that means:

| where a complexity decision is made | $N$ | $\ln N$ | BIC penalty / AIC penalty |
|---|---|---|---|
| the noise variance law, over level bins | 10 | 2.30 | 1.15 |
| one condition's line fit | ~4400 | 8.40 | 4.20 |
| the global dataset fit | ~405000 | 12.91 | 6.46 |

So on a single condition BIC demands four times the evidence AIC does before
admitting a parameter, and on the global fit six times. A criterion that
conservative on this much data will decline structure that is really present,
and the cost of that is not neutral: an omitted component does not vanish, it
is absorbed by whichever fitted parameter can imitate it, and the record then
quotes that parameter as physics.

Two consequences bound how much the choice can matter here, and the general
form of both is in [information criteria](../wiki/information-criteria.md). A
comparison between forms with **equal** $k$, such as Voigt against Lehmann in
§4.7, is unaffected by the criterion entirely. And the criterion only decides
an outcome when the fit improvement lands **between** the two penalties.

The nested ladder of §4.9 is in the second category on the rung that matters:
the free AC-Stark parameter buys a summed $\chi^2$ improvement of well under
one unit across twelve conditions, so no penalty scheme can prefer it, and the
"bound, not a measurement" conclusion is criterion-independent. That is worth
knowing, because it is the conclusion a reader is most entitled to be
suspicious of.

A criterion is only as good as the fit it scores, and a violated nesting
inequality measures the optimizer rather than the data.
`rb5s6s.modelform.compare_ic` reports every criterion and
refuses to interpret a comparison whose nesting inequality is violated.

In practice this record reports a panel of four: AIC, AICc (its small-sample
correction, which the drift-settling analysis already uses at $n=26$ with that
stated reason), BIC over raw $N$, and BIC over the effective sample size
$N_\text{eff}=N/\tau_\text{int}$, the last being this repository's own
adjustment for correlated samples (§4.13) and labelled a sensitivity criterion
rather than an established theorem. The four are a robustness check across
selection conventions, not four independent votes, since each pair shares its
motivation. Every comparison quotes the numerical difference under every
member. Where all agree, the selection is robust across the panel. Where they
split, the ranking is convention-sensitive at this sample size, that fact is
itself reported, and a split alone never justifies adopting the richer model:
adoption then needs an independent, predeclared basis. The one known split in
this record is the $\sigma_\text{laser}$ sharing of §4.13, where the BIC taken
over $N_\text{eff}$ favours sharing by $+61$ and AIC opposes it by $-6.6$, the
record's own "underpowered data" caveat made quantitative.

*Code:* `rb5s6s.modelform.info_criteria` and `compare_ic`, validated against
hand-computed penalties in `tests/test_info_criteria.py`.

### 4.8 Restricting the fit window: the off-center-sweep mirror

The laser is swept by a triangular voltage ramp. When that ramp is not
centered on the transition, its *down-ramp* re-crosses the line and leaves a
**mirror image** of the peak elsewhere in the acquisition window (~40 MHz away
on the transition axis). A single-line fit over the full window would treat
that mirror as unmodelled signal and let it bias the baseline and width. So the
line fits are restricted to a window around each trace's peak, wide enough to
keep the fat Lorentzian wings (where $\gamma_\text{coll}$ lives, since cutting too
tight would bias it) but tight enough to exclude the mirror: $\pm3.5\times$ the
trace's own measured FWHM, clipped to $[9,25]$ MHz. The rulers need no such cut
on the same grounds. A symmetric triangle has the same rate magnitude on both
ramps, so a fold preserves the tooth *spacing* of a correctly labelled comb,
while a single line simply appears twice. That argument covers the spacing and
not the labelling. A mirror landing in an outer slot is fitted as a tooth, and
because it lands at a radius smaller than the slot it occupies the rigid grid
contracts to reach it, which is the separate failure the tooth-numbering ladder
and the excision rung address
([the ruler specification](../notes/ruler_validity_and_trim_prereg.md) §1, and
[`DATA.md`](../DATA.md) §7). Its disposition lands with the recompute's
addendum and is not settled here.

The window and the residual-tail trimmer are two guards against the same
contamination, and the window gets there first. The trimmer walks outward only
within the fitted samples, so a trim census reading zero on line fits is a fact
about the order of the guards and not about the data. Line traces with a rising
tail exist: three of the five repeats of the 993.4207 nm line at 130 °C and
25 mW carry an unmistakable one. Whether the window sits in the right place was
open until it was measured directly: neither clip is active on the dataset (the
25 MHz cap binds on 0 of 159 canonical traces and the 9 MHz floor on 0 of 159),
the recorded crossings sit 7.64 to 8.54 fitted widths out against a window edge
at 3.50, and the constant that is sensitive to the sweep rate in the widening
direction is the 9 MHz floor rather than the cap
([DATA](../DATA.md) §7, [the ruler specification](../notes/ruler_validity_and_trim_prereg.md)
§G3). *Code:* `linefit.adaptive_halfwidth()`.

### 4.9 Is each component warranted? The nested model ladder

§4.7's BIC compares two *shapes* with the same parameter count. A stricter
question is whether each physical *component* is warranted, or
whether a simpler model fits as well. So we fit a nested ladder of increasing
physics and compare by BIC ($\text{BIC}=\chi^2+k\ln N$, summed over conditions
since BIC is additive over independent data):

$$
\text{A: Voigt} \subset \text{B: +transit} \subset \text{C: +collisional width} \subset \text{D: +AC-Stark ramp}.
$$

On the T-sweep dataset the summed $\Delta\text{BIC}$ per rung is **A→B $\approx +879$** (transit decisively warranted), **B→C $\approx +1091$** (a free
Lorentzian width beyond natural is warranted, and the line genuinely needs both a
Lorentzian and a Gaussian component), and **C→D $\approx -100$**, *the free
AC-Stark parameter is decisively not warranted*. This is the two-epoch design
stated as a model comparison, and it answers "is
your novel AC-Stark component an unnecessary parameter?": on the *drifted*
dataset it **is**, because the free per-scan centres absorb the ramp's pull and
$\sigma_\text{laser}$ its width, so BIC declines to buy it, which is precisely
why the recorded AC-Stark result is a **bound**, not a measurement (§4.5).

Two checks qualify this result. The B→C rung warrants a free
homogeneous *width*, not resolved collisions: that width is separately shown
(M4) to be a **density-independent floor**, so $\beta_\text{self}$ stays a bound
regardless. And the *same* ladder, on synthetic data built with a stable lock
(no per-scan drift), **decisively warrants the AC-Stark rung and recovers the
injected $S_0$**, while on $S_0=0$ data it declines it. So the null on the real
dataset is a property of the drift, not of the method: a fixed-lock session
would flip C→D positive. *Code:* `rb5s6s/model_ladder.py`, `run_model_ladder.py`,
closure `tests/test_model_ladder.py`, numbers `results/model_ladder.csv`.

### 4.10 Is the decomposition identifiable? Covariance, condition number, and the profile-likelihood map

The degeneracy asserted throughout, that $\gamma_\text{coll}$,
$\sigma_\text{laser}$ and transit all broaden the same line, so the main fit
*fixes* transit and reports $\sigma_\text{laser}$ as a bound, is here made
quantitative in two layers: a local covariance analysis and the global
profile-likelihood map that first corrected and then certified it. Both on one
bright condition (993.4192 nm, 130 °C, 225 mW), all three widths free plus the
per-trace nuisances.

**The map found the fit's second local minimum first.** A single-start three-width fit
lands in a Gaussian-dominated local minimum ($\sigma_\text{laser}\approx2.4$ MHz,
transit railed at zero, $\chi^2 = 5026$). The profile map exposed a **deeper,
cusp-dominated local minimum**, at $\gamma_\text{coll}\approx0.22$,
$\sigma_\text{laser}\approx0.46$, transit $\approx1.43$ MHz, i.e. the transit
width the $w_0\approx43$ µm geometry predicts, at $\chi^2 = 4551$, a
$\Delta\chi^2\approx475$ preference. The local analysis is therefore anchored
by a **two-start fit** at the deeper branch, and both branches plus their gap
are committed (`branch`, `branch_gap` rows). Set beside the accepted prior that
is a tension the dataset owns rather than resolves: the shape prefers
$w_0\approx43$ µm where the beamline-lineage measurement puts it at the accepted
**64 µm**, which is 1.43 MHz of transit width against 0.96 MHz at 130 °C.
Taken at face value the shape data
*prefer* the physical decomposition (real transit cusp, narrow laser). But
$\Delta\chi^2 = 475$ over about 4400 points is a $\chi^2$ change of about 10%
($\chi^2_\text{red}$ 1.15 → 1.04), the territory where transit-kernel
model-form imperfection also lives, a **consistency indication and not a
shape-based $w_0$ measurement**. A direct beam-profile measurement stays the arbiter, and the
C1/C2 upper bounds are unaffected.

At the anchored branch, the covariance (SVD of the Jacobian,
`fitutil.cov_from_jac`), diagonalized over the $3\times3$ width block:

- the strongest trade-off is $\gamma_\text{coll}\leftrightarrow$ transit
  ($\approx-0.96$): the two cusp-generating widths swap almost freely.
- the **condition number** of the width-block *covariance* is $\approx345$,
  which is strongly ill-conditioned.
- the **eigen-directions**: the best-constrained combination (a
  total-width-like sum, mostly $\gamma_\text{coll}$ + transit) is pinned to
  $1\sigma\approx0.003$ MHz, while the worst-constrained direction (dominated
  by $\sigma_\text{laser}$) is $\approx0.06$ MHz, about **20× looser**.

**The global map** (the standard referee demand: profile, not just covariance)
fixes ($\gamma_\text{coll}$, $\sigma_\text{laser}$) on a grid and re-minimises
$\chi^2$ over transit and every per-trace nuisance at each point (variable
projection, each cell fit from two independent warm-start lineages, with a
fresh-seed audit on every fifth cell). Its certifications, all committed: audit
gains $\le0.05$ (no warm-start trapping) and a **straight** valley floor
(RMS 0.002 MHz against a 0.019 MHz grid step) whose ridge slope (+0.086) is
compared against the covariance ellipse's prediction (+0.110), since in the
Gaussian limit the profile contours are exactly the marginal covariance
ellipse.

**How much weight that comparison carries, and it is less than the word
agreement suggests.** The two numbers share a sign and an order of magnitude.
The prediction sits 28 per cent above the measurement, and both moved when the
arithmetic environment changed, the slope by 18 per cent and the prediction by
37. A pair that both moves and still tracks to this tolerance certifies the
shape of the valley, not the value of either number.

The whole neighbourhood moves together under an environment change: the
condition number and the valley-floor RMS are now 345.1 and 0.0020 against the
pre-migration 389.7 and 0.0032, and the map-minimum certification changed
character, from a free fit that was the map's optimum to a zoom map that finds
a point 1.3 below it. The pre-migration values and the reason they moved are
recorded once, in
[the history](../HISTORY.md#the-environment-migration-landed-2026-08-23).
That is what an
ill-conditioned family does, and it is the reason this section exists.

What has not been separated is how much of that movement is the arithmetic
environment and how much is a later change to the lineshape module, since the
committed digits predate both. The record says so rather than attributing it,
and the attribution is left as an open item.

So the agreement is evidence that the profile map and the local covariance are
describing the same geometry, and it is not a precision test: one side of it is
ill-conditioned by exactly the mechanism the section is about. The robust
quantity of the two is the profile measurement, which is the same conclusion
this record reaches everywhere else it sets a profile against an ellipse. The
committed digits here are those of the environment of record
([`results/ENVIRONMENT_OF_RECORD.md`](../../results/ENVIRONMENT_OF_RECORD.md)). The joint-95% region closes inside the physical range **except toward
$\sigma_\text{laser}\to0$**: the line *shape* alone cannot exclude a
near-zero laser width at this condition.

![the profile-likelihood map of the two-width decomposition, with the covariance ellipse overlaid](../../figures/fig7_identifiability_profile.png)

*What the whole chapter is about, at one condition. The total width is pinned
to about a tenth of a per cent, and the split between the two components that
make it is pinned twenty times worse: the valley runs almost along a line of
constant total, so the pair can slide along it at almost no cost in fit
quality. The overlaid ellipse is the marginal covariance, and it agrees with
the profile map, which is the check that the reported error bars mean what they
say. The valley staying open toward zero laser width is the statement that the
line shape alone cannot exclude a narrow laser, and it is why the individual
widths are bounds conditional on the beam waist rather than measurements.*

So the dataset constrains the total width to about 0.1% but the split
twenty-fold worse, now as a certified-global statement rather than a local one: the
individual widths are genuinely $w_0$-conditional bounds, not measurements,
and a measured $w_0$ **collapses** the degeneracy, because it fixes transit to
within that measurement's own precision, so the split becomes identifiable
within that uncertainty rather than removed exactly (a perfectly-known $w_0$
would remove it, and a real one greatly reduces it). This is the formal statement
behind the width correlations quoted in
§2.4.

The same numbers answer *why not fit $w_0$ jointly*: $w_0$ enters the line only
through this width block (transit $\propto 1/w_0$) and the intensity
normalization ($\propto 1/w_0^2$), so freeing it adds a fourth member to the one
subspace the data already cannot split, so the fit would return the prior dressed
as a posterior. $w_0$ is instead measured out of band (knife-edge and/or camera) and
propagated as an explicit band. *Code:* `rb5s6s/identifiability.py`,
`run_identifiability.py`, closure `tests/test_identifiability.py`, numbers
`results/identifiability.csv`.

### 4.11 Does the 95% bound actually cover? An injection-recovery study

The collisional bound's 95% is built from a between-block scatter estimated on
a small number of residual degrees of freedom, so it uses the Student-t
quantile rather than the Gaussian 2 (§4.5): $t(0.95,2)=2.92$ for the current
four-point headline (70/90/110/130 °C, since 2026-08-02, and the replaced
three-point 70–110 °C headline used $t(0.95,1)=6.31$). A bound is only worth
its coverage, so we check it by simulation rather than assert it: at a grid
of *known* true $\beta$ we generate 2000 synthetic four-point cooling+130 °C
sweeps each, with the dataset's own structure, a between-block scatter
mimicking the drift wander plus the small within-block SEM, run the
**shipped** estimator `beta.collisional_slope` on every one, and measure
bias, coverage, and the false-detection rate. The result:

- the point estimate is **unbiased** (bias $\approx-0.0001$ MHz per $10^{12}$
  cm⁻³, well below the bound).
- the Student-t 95% upper bound **covers the true $\beta$ $\approx100$% of the
  time**, valid and, on 2 dof, conservative (the safe direction for a bound, and
  the Gaussian-2 bound this replaced would *under*-cover, which is the whole
  the reason for the t-quantile).
- at $\beta_\text{true}=0$ the pre-registered SNR $\ge3$ "measurement" rule
  alone fires $\approx4$% of the time, a real false-positive rate, which is
  precisely why the analysis does **not** rely on SNR alone: the
  non-monotonic width-vs-density pattern (2/4 real peaks) is the decisive guard
  that forces the BOUND reading regardless (§C1).

So the headline is empirically calibrated: unbiased estimate, a 95%
(conservative) bound, and a documented false-detection rate that the
monotonicity guard suppresses. *Code:* `rb5s6s/coverage.py`, `run_coverage.py`,
closure `tests/test_coverage.py`, numbers `results/coverage.csv`.

### 4.12 Why a profile likelihood, not a posterior

Three features of this dataset drive the choice:

1. **The headline is a bound, and a bound is only worth its frequentist
   coverage**, which §4.11 buys by simulation. A credible interval would need
   the same injection study to earn the same trust, and the profile construction is
   the one we can, and do, calibrate directly.
2. **The dominant systematic is deliberately OPEN.** A posterior needs a prior
   on $w_0$, and marginalizing folds that prior invisibly into the quoted
   number. Keeping $w_0$ out of the likelihood and quoting an explicit
   $w_0$-band (§C1 of the ledger) keeps the conditionality on the page, and
   when the beam-profile measurement lands, the band collapses without redoing the inference.
3. **Where the data are weakest, a prior would dominate.** Four densities and
   two residual degrees of freedom (§4.5), or a $\chi^2$ flat to first order at
   the $\kappa=0$ rail (C3d): a posterior
   mostly reflects the prior, while the Student-t quantile and the profile scan
   state the data-poverty out loud.

Bayesian machinery is used where it is the right tool, model *selection*, as
the BIC ladder of §4.9.

**A profile is only as good as its local minimum.** A profile scan inherits every
weakness of the optimizer that walks it: a chain that starts cold and parks
in a false minimum produces a smooth, confident, wrong curve, and nothing
in the profile itself reveals the parking. This analysis learned that twice
on the joint fit, first on a direction variant and then on the primary
itself (a 283,000-unit false direction signal whose excess sat outside the
campaign data, the campaign column moving by only four units of it). The working discipline, now structural in the fitter:
the variant that finds the true local minimum most reliably runs first, every other
variant is seeded from its solution in addition to running cold, the
pointwise minimum over chains is what enters the profile, and no cold-start
profile is quoted without a seeded twin (docs/RESEARCH_DECISIONS.md §11).

### 4.13 How much evidence for the $\sigma_\text{laser}$ sharing? A BIC, and a cautionary one

The hierarchical fit (§4.2) shares one $\sigma_\text{laser}(T)$ across the four
peaks at each temperature (Model A, per $T$). The conservative alternative frees
it per (peak, $T$) block (Model B, per-block, 9 more parameters). §4.5 and the
M4c check argue the sharing is *consistent* but *underpowered*, and this puts a number
on it. Both models are fit with the same machinery (`fit_global`) and scored by
$\text{BIC}=\chi^2+k\ln N$, with $\Delta\text{BIC}=\text{BIC}_\text{block}-\text{BIC}_T$
($\Delta\text{BIC}$ above 0 favours the shared model).

The result depends on how the sample size is counted. Each trace is a smooth
line sampled at about 2000 **correlated** points, so the roughly 49k raw samples are
not 49k independent observations. Counting them as such over-weights the per-block
fit's tiny $\chi^2$ gain and returns $\Delta\text{BIC}\approx-52$ ("per-block
wins"). But the noise model already whitens each residual by $\sqrt{\tau_\text{int}}$
($\tau\approx3.5$). The **matching** effective size $N_\text{eff}=N/\tau$ with the
whitened $\chi^2$ gives $\Delta\text{BIC}\approx+61$ ("shared wins, decisively").
The $N_\text{eff}$ BIC is the statistically correct one, since correlated samples are not
independent, so the shared model is favoured: **the dataset cannot pay for
per-block $\sigma_\text{laser}$ freedom**. Two caveats apply:

- it is **parsimony and not physics**, since four peaks that co-drifted between
  acquisitions would look shared too (§4.2, M4c), and no in-sample score recovers
  the timing. A positive $\Delta\text{BIC}$ means "the alternative is not warranted", not
  "the sharing is real". The recovered clock sharpens this from "unlogged" to
  *dated and unfavourable*: the four peak-blocks of a dwell are **54–76 minutes
  apart**, not minutes ([RESULTS.md](../RESULTS.md) C1). Their widths show no
  correlation with that elapsed time ($r=+0.18$, $p=0.6$, n=12), so sharing is
  not refuted, but the design gave the test no power, which is why the fixed-lock
  session interleaves the peaks within minutes.
- the sign **flips** with the sample-counting, so the dataset does not *robustly*
  resolve shared-vs-independent, which is exactly the M4c reading, now
  quantitative. The headline therefore stays the model-independent width-slope
  bound (C1), not the sharing-dependent hierarchical value.

*Closure* (`tests/test_sharing_bic.py`, clean synthetics where $\tau=1$ so the two
$N$ values coincide): the score correctly favours per $T$ when the peaks truly share one
$\sigma_\text{laser}$ and per-block when they carry grossly different ones, so it
detects real sharing structure when the data carry the power the dataset lacks.
*Code:* `rb5s6s/sharing_bic.py`, `run_sharing_bic.py`, numbers `results/sharing_bic.csv`.

---

**Where the numbers live.** Modules M1, M4b, M4c, M4d, M8, M11, M12, M13, M14 ·
producers `scripts/run_noise.py`, `scripts/run_global_fit.py`,
`scripts/run_lever_crosscheck.py`, `scripts/run_modelform.py`,
`scripts/run_model_ladder.py`, `scripts/run_identifiability.py`,
`scripts/run_coverage.py`, `scripts/run_sharing_bic.py` · results
`results/noise_model.csv`, `results/global_fit.csv`,
`results/lever_crosscheck.csv`, `results/modelform.csv`,
`results/model_ladder.csv`, `results/identifiability.csv`,
`results/identifiability_profile.csv`, `results/coverage.csv`,
`results/sharing_bic.csv` · figures
`figures/fig7_identifiability_profile.png`. Library code: `rb5s6s/noise.py`,
`rb5s6s/linefit.py`, `rb5s6s/beta.py`, `rb5s6s/fitutil.py`,
`rb5s6s/modelform.py`, `rb5s6s/model_ladder.py`, `rb5s6s/identifiability.py`,
`rb5s6s/coverage.py`, `rb5s6s/sharing_bic.py`.

**What would falsify this.** A coverage study that failed to cover. The bound
this chapter licenses is only worth its frequentist coverage, so a
higher-statistics injection run in which the Student-t upper limit missed the
injected $\beta$ more often than five times in a hundred would retire the rule
rather than qualify it.

[← From volts to a frequency axis](05_the_frequency_ruler.md) · [What we found →](07_what_we_found.md)
