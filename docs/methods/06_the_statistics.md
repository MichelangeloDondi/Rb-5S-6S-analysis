*Chapter 6 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

## 4. The statistics, from first principles

### 4.1 Weighted least squares with *measured* weights

A fit minimizes $\chi^2=\sum_i \big(d_i-m_i\big)^2/\sigma_i^2$. The correct
$\sigma_i$ is the real per-sample noise, which here is *not* constant: PMT shot
noise grows with signal. We measured (module M1, §4.4)

$$\sigma^2(V)=a^2+bV$$

per condition and use it as the weights. Unweighted fitting would let the
bright peak dominate and would misstate every error bar; using the measured
$\sigma(V)$ is what makes the reported uncertainties meaningful.

### 4.2 Hierarchical fitting — share what physics shares, free what drifts

Each condition has five back-to-back repeats of the *same* physical line, but
the drifting 2025 laser moves the line center and the PMT gain wanders. So we
fit the repeats **jointly**, sharing the physics and freeing the nuisances:

- **shared** across repeats: the lineshape parameters $\gamma_\text{coll}$,
  $\sigma_\text{laser}$ (and optionally transit);
- **per-trace**: amplitude $A_i$, center $\nu_i$, and a tilted baseline
  $b_{0,i}+b_{1,i}\nu$.

This is what makes drifted 2025 data usable: the drift lives in the per-trace
centers, the physics in the shared shape. The same idea extends across
temperatures — `fit_beta_self()` ties $\gamma_\text{coll}(T)=\beta_\text{self}N(T)$
with a single shared $\beta_\text{self}$, turning four widths into one slope.

**The full hierarchy** (`fit_global()`, module M4b) fits *all* peaks and
temperatures at once, sharing each parameter at the level the physics licenses
— and the choice of level is where the physics really enters:

- $\sigma_\text{laser}$ is shared **per temperature, across the four peaks**.
  The four lines are measured within one temperature dwell, so they see the
  *same* laser at that moment and jointly over-constrain $\sigma_\text{laser}(T)$
  — which lets its drift across the cooling session be *measured* rather than
  mistaken for collisions. (Sharing one *global* $\sigma_\text{laser}$ across
  all temperatures — as a naive fit does — is exactly what manufactures a false
  detection; see §4.5. For a stable lock, global sharing becomes
  correct.)
- $\beta_\text{self}$ is shared **per isotope**, not globally: collision
  cross-sections need not be equal for $^{85}$Rb and $^{87}$Rb, so we *test*
  $\beta_{85}$ vs $\beta_{87}$ rather than assume them equal.
- the transit width is shared globally (same beam, same $\sqrt T$ law);
  amplitude, center, baseline stay per-trace.

This breaks the Voigt degeneracy (§4.3) two ways at once — the density lever
arm *and* the four peaks pinning one $\sigma_\text{laser}(T)$ — and comes with
a leave-one-condition-out check that no single block drives a shared
parameter. *Code:* `fit_condition()`, `fit_beta_self()`, `fit_global()`.

**The lever cross-check** (`lever_crosscheck_beta()`, module M4d) is the packaged form of
this hierarchy — the value and the *full error budget* the paper quotes. Its
headline is the **internally-consistent 70/90/110 °C cooling sweep** (one
session, monotonic cooling), fit across a model-form grid — transit cusp
(Lehmann) vs no-cusp (Voigt) $\times$ $\sigma_\text{laser}$ shared-per-$T$
(Model A) vs per-block (Model B). The spread of $\beta$ across those cells *is*
the model-form error bar; with the $w_0$-band and a leave-one-**peak** /
leave-one-**temperature** robustness scan it returns **one $\beta$ per isotope
carrying three separately-sourced error bars** (statistical, model-form,
confound/$w_0$). A synthetic-injection closure test (`tests/test_lever_crosscheck`)
recovers a known $\beta$ through the whole 20-trace machinery, so the pipeline
itself is validated, not just trusted.

The archive's curated 130 °C anchor (the `serves_t130` traces, 225 mW) would
triple the density lever ($N{\times}16\to{\times}53$), and the lever cross-check
uses it as a **lever test**: adding it pulls the joint $\beta$ far below the
cooling-sweep value. The lesson is not "bad block" — it is that
$\gamma_\text{coll}$ **barely grows with density**: it rises only ${\sim}1.5\times$
across a ${\times}52$ density span (70→130 °C), and the 130 °C widths sit *on*
that near-flat trend, whereas a real binary-collision width is *linear* in $N$.
So the fitted $\gamma_\text{coll}$ is a residual floor, not resolved collisions,
and $\beta$ is a **lever-dependent bound**, not a value — exactly why the
model-independent bound is the headline. (The 130 °C data are also a different
session, a secondary caveat we cannot fully separate; either way a fixed-lock session needs
*same-session* high-density points to resolve any real slope.)
*Run:* `run_lever_crosscheck.py` → `results/lever_crosscheck.csv`; numbers in the
results ledger (`docs/RESULTS.md`).

### 4.3 The degeneracy and honest covariances

Because of the Voigt near-degeneracy ([§2.4 — The lineshape, kernel by kernel](02_the_lineshape.md)), a single-condition fit returns
$\sigma_\text{laser}$ and $\gamma_\text{coll}$ with correlation
$\approx-0.85$: individually shaky, sum robust. We therefore (i) always report
the full covariance, and (ii) design $\beta_\text{self}$ to ride on the
$\gamma_\text{coll}$ **difference** across densities, where the shared laser
contribution cancels. Reported errors are additionally inflated by
$\sqrt{\chi^2_\text{red}}$ (model imperfection) and $\sqrt{\tau_\text{int}}$
(wing-noise correlation, §4.4) — conservative by policy. Covariances are
obtained from a singular-value decomposition of the Jacobian rather than
$(J^{\mathsf T}J)^{-1}$, to stay numerically safe when parameters span very
different scales. *Code:* `fitutil.cov_from_jac()`.

### 4.4 The noise model and the second-difference estimator

To measure $\sigma(V)$ without contamination from the signal's slope, we use
**second differences**,

$$e_i=\frac{v_{i+1}-2v_i+v_{i-1}}{\sqrt{6}}$$

which annihilate any locally-linear trend exactly (so a bright line's steep
flank contributes nothing) while having unit response to white noise — for
white noise of standard deviation $\sigma$, $e_i$ also has standard deviation
$\sigma$. Binning $e_i$ by local signal level and fitting the variance law
$\sigma^2=a^2+bV$ then gives $a$ (electronics/dark floor) and $b$ (the
shot-noise, "Fano", term). Wing-noise **correlation** is measured separately
by the blocking method and summarized as an integrated correlation time
$\tau_\text{int}$, which inflates the fit errors as above. We found $b$ flat in
$T$ (the trapping test of [§2.7 — The composite model (and what does not enter it)](04_the_composite_model.md)) and $\tau_\text{int}$ small. *Code:*
`noise.py`.

### 4.5 Statistics versus systematics — the measurement-vs-bound rule

A large shared fit can return a beautifully small formal error that is
nonetheless *wrong*. If you share $\sigma_\text{laser}$ across blocks recorded
hours apart and the laser width actually drifted between them, the fit will
absorb that drift into $\gamma_\text{coll}$ and report a confident collisional
signal that is really instrument drift. Our guard is **pre-registered** and
model-independent:

1. Collisional broadening *must* be monotonic in density. So take **raw**
   line widths (smoothed half-max $\times$ the ruler rate, no fitting) and
   check monotonicity in $N$.
2. Fit $W(N)=W_0+\beta_\text{eff}N$; the RMS scatter of the blocks about this
   line is treated as a **between-block systematic** and added in quadrature
   to each point's error.
3. Claim a **measurement** only if $|\beta_\text{eff}|/\sigma_\text{syst}\ge3$;
   otherwise report a **bound**.

Deciding this rule *before* looking is what separates the honest answer from
the overconfident one (see [§5 — What we found (2025 archive)](07_what_we_found.md)). *Code:* `beta.collisional_slope()`,
`scripts/run_beta_self.py`.

### 4.6 Validation on synthetic data before real data

No fitter is allowed near real data until it recovers *known* injected truths
from campaign-like synthetics — checking bias, error coverage, and the
degeneracy — across 113 tests. Then every headline conclusion is re-derived by
an **independent method** (e.g. the sweep rate by FFT and autocorrelation; the
noise law by differencing sibling repeats). Several of our own bugs were caught
exactly this way; the verification records live in the module docstrings.

### 4.7 Choosing between competing lineshapes — the BIC

To ask *which* model form the data prefer — a smooth Gaussian extra-broadening
(a Voigt) versus the cusped transit exponential (the Lehmann shape, [§2.5 — The lineshape, kernel by kernel](02_the_lineshape.md)) — we
compare the **Bayesian information criterion**

$$\text{BIC}=\chi^2+k\ln N$$

with $k$ the number of free parameters and $N$ the data points. The $\chi^2$
rewards fit quality; the $k\ln N$ term penalizes complexity, so BIC asks "is
the better fit worth its extra parameters?". Lower BIC wins; on the
Kass–Raftery scale $|\Delta\text{BIC}|<2$ is "indistinguishable" and $>10$ is
"decisive". Voigt and Lehmann have the *same* $k$, so their comparison is
essentially which shape fits better. This is the tool for the Lehmann-cusp
test (module M8; [§5 — What we found (2025 archive)](07_what_we_found.md)). *Code:* `modelform.py`.

### 4.8 Restricting the fit window — the off-center-sweep mirror

The laser is swept by a triangular voltage ramp. When that ramp is not
centered on the transition, its *down-ramp* re-crosses the line and leaves a
**mirror image** of the peak elsewhere in the acquisition window (~40 MHz away
on the transition axis). A single-line fit over the full window would treat
that mirror as unmodelled signal and let it bias the baseline and width. So the
line fits are restricted to a window around each trace's peak, wide enough to
keep the fat Lorentzian wings (where $\gamma_\text{coll}$ lives — cutting too
tight would bias it) but tight enough to exclude the mirror: $\pm3.5\times$ the
trace's own measured FWHM, clipped to $[9,25]$ MHz. The rulers need no such cut
— a symmetric-triangle fold preserves the tooth *spacing*, so the ruler rate is
intrinsically fold-robust (only a single line, which literally appears twice,
is at risk). *Code:* `linefit.adaptive_halfwidth()`.

### 4.9 Is each component warranted? — the nested model ladder (M11)

§4.7's BIC compares two *shapes* with the same parameter count. A stricter
question a referee asks is whether each physical *component* earns its place, or
whether a simpler model fits as well. So we fit a nested ladder of increasing
physics and compare by BIC ($\text{BIC}=\chi^2+k\ln N$, summed over conditions
since BIC is additive over independent data):

$$
\text{A: Voigt} \subset \text{B: +transit} \subset \text{C: +collisional width} \subset \text{D: +AC-Stark ramp}.
$$

On the T-sweep archive the summed $\Delta\text{BIC}$ per rung is **A→B $\approx
+1700$** (transit decisively warranted), **B→C $\approx +435$** (a free
Lorentzian width beyond natural is warranted — the line genuinely needs both a
Lorentzian and a Gaussian component), and **C→D $\approx -100$** — *the free
AC-Stark parameter is decisively NOT warranted*. This is the two-epoch design
stated as a model comparison, and it is the honest referee-facing answer to "is
your novel AC-Stark component an unnecessary parameter?": on the *drifted*
archive it **is** — the free per-scan centres absorb the ramp's pull and
$\sigma_\text{laser}$ its width, so BIC declines to buy it, which is precisely
why the archival AC-Stark result is a **bound**, not a measurement (§4.5).

Two guards keep this from being mere blindness. The B→C rung warrants a free
homogeneous *width*, not resolved collisions: that width is separately shown
(M4) to be a **density-independent floor**, so $\beta_\text{self}$ stays a bound
regardless. And the *same* ladder, on synthetic data built with a stable lock
(no per-scan drift), **decisively warrants the AC-Stark rung and recovers the
injected $S_0$** — while on $S_0=0$ data it declines it. So the null on the real
archive is a property of the drift, not of the method: a fixed-lock session
would flip C→D positive. *Code:* `rb5s6s/model_ladder.py`, `run_model_ladder.py`;
closure `tests/test_model_ladder.py`; numbers `results/model_ladder.csv`.

---

---

[← From volts to a frequency axis](05_the_frequency_ruler.md) · [What we found (2025 archive) →](07_what_we_found.md)
