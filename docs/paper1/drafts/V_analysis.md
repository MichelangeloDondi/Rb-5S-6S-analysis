# Paper 1 — §V draft prose: analysis (calibration, noise, the fit hierarchy)

**FIRST-PASS DRAFT, for MD/Síle to revise.** Fills the §V stub of
`PAPER1_SKELETON.md`. Not final text; numbers from the committed ledger
(`docs/RESULTS.md`), provenance/framing in **[brackets]**, LaTeX inline. This is
the last substantially self-contained section — §I/II/IV/VII/VIII need your voice
and apparatus detail.

---

## V. Analysis

### V.A Frequency axis

Every trace is a fluorescence signal versus time as the laser is swept; the
horizontal axis is calibrated to frequency by the electro-optic-modulator (EOM)
sidebands, whose $6.25$ MHz spacing appears as a comb of evenly spaced teeth in
each ruler acquisition. Fitting the tooth spacing gives a sweep rate of
$$0.04257(5)\ \text{MHz/ms}\quad(\text{laser axis})$$
[MEASURED-HERE], i.e. $0.08514$ MHz/ms on the two-photon transition axis (twice
the laser detuning; we state the factor of two once and work on the transition
axis throughout). The rate is measured **per block** from that block's own
before/after ruler brackets, not assumed global; within a block the sweep is
linear to better than 0.4%.

The campaign rate is the inverse-variance mean over the 20 blocks. Its
$\chi^2_\text{red}=6.8$ (0.65% block-to-block scatter) is genuine
over-dispersion — drift between the before/after brackets — so the quoted error
is PDG-inflated by $\sqrt{\chi^2_\text{red}}\approx2.6$ to absorb it. The
scatter is block-level and bracket-resolved, **not** a peak-ordered axis
distortion: the per-peak rates are non-monotonic and the two brackets disagree on
the ordering, so it inflates the common-axis error symmetrically without biasing
the cross-peak differential comparisons that carry the isotope and degeneracy-law
results. [Robustness, now committed:] dropping the one flagged outlier block (the
993.4207 nm *after* bracket, 1.4% above its own *before*) shifts the campaign
rate by only 0.08% ($0.70\sigma$) and drops $\chi^2_\text{red}$ to 3.8 — the rate
is robust to it, and it is retained under the pre-registered policy of not
auto-cutting statistical outliers.

Two geometry effects are handled at fit time rather than by discarding data.
First, the rulers are **fold-robust**: the sweep is a symmetric triangle, so if
it is not centred on the line the down-ramp re-crosses it, but the up- and
down-ramps share the same rate magnitude, so a fold preserves the tooth
*spacing* that sets the rate (only the tooth indexing scrambles). Second, that
same off-centre fold places a **mirror** of the main line $\sim40$ MHz away
inside the window for the edge component (993.4207 nm, up to 79% of peak height
at low power); line fits therefore use an adaptive window ($\pm3.5$ times the
trace's own FWHM, clipped to $[9,25]$ MHz) that excludes the mirror while keeping
a fixed fraction of the Lorentzian wings. [App. C / §IV has the provenance;
here just state the method.]

### V.B Noise model

Each condition's photon-counting noise is characterized by a variance law
(variance affine in signal level) fitted from the repeats, and — because the
high-resolution samples within a trace are correlated — by an integrated
correlation time $\tau_\text{int}$ (ranging $\approx1.3$–$20$ across conditions)
that inflates each trace's per-sample error to its true information content. The
raw variance-law fit is a deliberately loose diagnostic; the weights it produces
are validated *downstream* by the near-unity reduced chi-squared of the line fits
that consume them. One noise feature is itself a result rather than a nuisance:
the low-power residual skewness of §VI.C is the right-skewed Poisson shot noise
this model predicts, which is how we separate it from the AC-Stark ramp.

### V.C The fit hierarchy and its degeneracies

The lineshape (§III) is fit at three levels of sharing, chosen so that the drift
lives in nuisance parameters and the physics in shared ones. **Per trace:**
amplitude, centre, and a tilted baseline — the lock drift and gain scatter are
absorbed here, which is precisely what makes a shape-only archive usable.
**Shared across a condition and across temperature:** the collisional width
$\gamma_\text{coll}(T)=\beta_\text{self}N(T)$ (one $\beta$ per isotope), the laser
width $\sigma_\text{laser}(T)$ (one per temperature, across the four components),
and the transit width (one, scaling as $\sqrt T$); the natural width is fixed at
its physical value.

Two near-degeneracies set what is and is not recoverable, and we quote them
rather than hide them. The laser Gaussian and the collisional Lorentzian trade
off in a Voigt profile: in a single condition their widths anti-correlate at
$-0.85$ to $-0.92$, so the *total* width is well determined but its *split* is
not. The hierarchical fit breaks this two ways at once — the density lever (a
factor 52 in $N$) and the four components sharing one $\sigma_\text{laser}(T)$ —
reducing the anti-correlation to $-0.78$ to $-0.80$; that is why the joint fit is
a more powerful cross-check than the per-condition fits, even though it remains
lever-limited (§VI.A). The second degeneracy, between the transit width and the
beam waist $w_0$, is *not* broken by any amount of archival data: every absolute
width — and hence every absolute $\beta_\text{self}$ and $\sigma_\text{laser}$ —
rides on the open $w_0$, which is the single reason those quantities are bounds
here and measurements only after the knife-edge measurement. All reported fit errors
are marginal (from the full covariance, folding in the anti-correlations), and
where a fit is over-dispersed the covariance is conservatively rescaled by
$\max(\chi^2_\text{red},1)$.

---

### Numbers used (all from `docs/RESULTS.md` / committed CSVs, keep synced)

- rate $0.04257(5)$ MHz/ms laser ($=0.08514$ transition); EOM teeth $6.25$ MHz; per-block; sweep linear $<0.4\%$
- campaign $\chi^2_\text{red}=6.8$ (0.65% scatter, 20 blocks), PDG-inflated $\times2.6$; drop-4207-after shift $0.08\%$/$0.70\sigma$
- adaptive window $\pm3.5\times$FWHM, $[9,25]$ MHz; 993.4207 nm mirror up to 79% @ $\sim40$ MHz
- noise $\tau_\text{int}\approx1.3$–$20$; Voigt corr $-0.85$ to $-0.92$ (single) $\to$ $-0.78$ to $-0.80$ (global)
- $\Gamma_\text{nat}=3.4926$ MHz fixed; covariance rescaled by $\max(\chi^2_\text{red},1)$

### Open framing choices for you
- Depth of the fold-robust / mirror-crossing material: it is careful data hygiene and reviewers like it, but it can also read as in-the-weeds — decide main-text vs appendix (App. C already holds the provenance).
- Whether the "drift lives in the per-trace centres" idea is stated here or promoted to §II as the conceptual core of the two-epoch design (I lean §II for the idea, §V for the mechanics).
- How much of the noise-model validation-by-downstream-χ² to keep — it is honest but methodological; a sentence may suffice.
