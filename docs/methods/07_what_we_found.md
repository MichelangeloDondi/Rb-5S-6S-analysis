*Chapter 7 of 8 · [methods index](../methods.md)*

**The question.** What did the 2025 archive actually deliver, and why is every
headline a bound or a null?
**Takes.** The lineshape through statistics chapters, chapters 2 to 6.
**Gives.** The results the paper reports and the reason each one is
conditional, which the assumptions chapter then turns into what to challenge.
**Skip if.** You have read [`docs/RESULTS.md`](../RESULTS.md), the generated
ledger of the same numbers with its full audit trail.

## 5. What we found (2025 archival data)

### 5.1 $\beta_\text{self}$: the T-sweep bounds it

**Headline: the T-sweep *bounds* $\beta_\text{self}$ and shows why it cannot
measure it.** The raw, model-independent widths are **non-monotonic in
density** for two of the four peaks (993.4154 and 993.4207 nm): somewhere along
the sweep the line gets *narrower* at higher density, which no collision can
produce. The scatter left over about the fitted width-versus-density line is
0.14 to 0.25 MHz across the four peaks, and it is between-block scatter, the
2025 laser width wandering between cooling steps by about as much as the entire
collisional trend. No peak resolves a slope: the four signal-to-noise ratios are
1.1, 0.7, 0.8 and 1.9. Applying [§4.5](06_the_statistics.md), the model-independent 95% per-peak bound is

$$\boxed{ \beta_\text{self}\lesssim 0.03\text{ to }0.05\ \text{MHz per }10^{12}\ \text{cm}^{-3}. }$$

The four density points are 70, 90, 110 and 130 °C, a $\times52.5$ lever. The
130 °C point is the 225 mW power session, taken in the same optical and cell
configuration and inside the same continuous campaign, with each session's axis
calibrated from its own rate source before the two are put on one density axis
(`docs/RESEARCH_DECISIONS.md` §9). Folding it in stretches the lever from
$\times16.2$, and no three-point construction is kept alongside it.

Two coverage corrections define this bound (both 2026-07-16). First, the
between-block scatter that dominates the slope error is estimated on only
**two residual degrees of freedom** (4 density points, 2 fit parameters), so a
one-sided 95% limit needs the Student-t quantile $t(0.95, 2)=2.92$, not the
Gaussian-asymptotic 2 an earlier revision used. Second, $\beta\propto 1/N$, so
the roughly 20% spread between published vapor-pressure correlations is a
density-scale systematic that moves every $\beta$ by the same fraction, and the
cold-spot direction makes the fitted $\beta$ an underestimate, so the bound is
inflated on the + side ($\times1.2$, see `density.py`). (The scatter estimate
divides by the degrees of freedom, not by $n$. Using $n$ would tighten the
bound, a directional bug fixed 2026-07-12.) The spread across the boxed range
is systematics rather than physics, because the four bounds track each peak's
residual scatter and not a physical rate, so the number to quote is the loosest
of the four. A naive global Voigt fit instead reports a
4–10 sigma "detection", the [§4.5](06_the_statistics.md) cautionary tale in practice. This bound is
the archival data *showing the two-epoch design was necessary*, and is reported as a
vapour-cell result.

### 5.2 A hierarchical cross-check ($\beta$ per isotope)

The full fit ([§4.2](06_the_statistics.md),
`fit_global`), which lets $\sigma_\text{laser}$ drift per temperature
and weights each block by its own correlation time, returns
$\beta_{85}=0.0535(43)$ and $\beta_{87}=0.0528(47)$ MHz per $10^{12}$ cm⁻³:
**no isotope dependence**, the two differing by $0.0007$, well inside either
error bar, and dropping any one peak moves the value by at most $0.007$. It is
a *model-based* value, and it sits **above** both the per-peak model fits
(0.013–0.018) and all four model-independent per-peak bounds
(0.03–0.05). The three estimators of the same quantity therefore span about
a factor of four, and that spread across $\sigma_\text{laser}$ treatments is
itself the uncertainty on this deliverable, larger than any single fit's error
bar. This $0.053$ carries **four separate error bars**, and the systematics
dominate the statistical one: statistical
$\pm0.004$ (joint-fit covariance), **transit model-form $\pm0.014$**, the
largest of the four (the
$|\text{Voigt}-\text{Lehmann}|$ shift, [§4.7](06_the_statistics.md), `run_global_fit`: the Gaussian-transit
Voigt gives the *higher* $\beta\approx0.068$ because a narrower transit core forces
more width onto collisions), **density scale $\pm0.011$** ($\beta\propto1/N$, the
roughly 20% spread between published vapor-pressure correlations, `density.py`),
and the $w_0$-band $[0.050,0.057]$, which covers transit reference widths from
$w_0=65$ down to 40 µm and is the narrowest of the four.
The paper must quote all four, not the optimistic $\pm0.004$ alone.
So the conservative model-independent bound, not this value, stays the headline.
Its real value is the isotope test, and the in-sample consistency check
(`run_sigma_laser_sharing`) that the four peaks at each temperature agree on a
single $\sigma_\text{laser}$. That check is *passive*: χ²/dof = 0.28/0.59/0.29,
all well below 1, so the peak-blocks are closer to the shared model than their
own error bars, and the test cannot discriminate. It does not license the
sharing, it merely fails to contradict it (RESULTS §σ_laser sharing). It also
covers only 70, 90 and 110 °C, so it says nothing about sharing at the 130 °C
point that now carries most of the lever. The fit's
$\sigma_\text{laser}(T)\approx2.1/2.2/1.5$ MHz is **not** a clean drift curve,
though: the free per-condition fit gives a *flat* 1.5–1.75 MHz, so that trend
is the $\beta \leftrightarrow \sigma_\text{laser}$ degeneracy under the density
tie, not a physical laser drift. The 110 °C dip is a model artifact, not a
stale block, and it does not corrupt $\beta$, which the density lever still
pins.

The **lever cross-check** (`run_lever_crosscheck`) packages exactly this, the
cooling-sweep $\beta$ with its stacked error bars and a leave-one-peak and
leave-one-temperature scan, and adds the lever test: folding in the
130 °C anchor ([§4.2](06_the_statistics.md)) pulls $\beta$ down
to $0.020$, a shift of $-0.034$, because $\gamma_\text{coll}$
rises only ${\sim}1.47\times$ across a ${\times}52.5$ density span. That is a
residual floor rather than resolved collisions, so $\beta$ is a lever-dependent
bound. The full audited
budget is in the results ledger (`docs/RESULTS.md`).

### 5.3 The 2025 laser width

$\sigma_\text{laser}(2025)\lesssim2.2$ MHz (transition axis; below 1.2 MHz
laser axis; it is $\sim1.09$ MHz laser-axis at the adopted $w_0=64$ µm
prior) —
a bound, not a measurement, because that non-Lorentzian Gaussian
is degenerate with the transit width, and the transit Monte-Carlo ([§2.5](02_the_lineshape.md), M9)
now makes the degeneracy quantitative: the corrected transit adds $\sim2.1$ MHz
at $w_0=32$ µm (which OVERSHOOTS the observed line, excluding 32 µm) but only
$\sim0.93$ MHz at the 64 µm prior, so below $w_0\approx38$ µm transit
alone fills the observed 5.25 MHz and **the laser is narrow**, while at the
adopted 64 µm prior the laser carries $\sim1.09$ MHz laser-axis, close to the
bound itself: widening the waist hands width from transit to laser. The
archival data cannot locate that crossover; only a direct beam-profile $w_0$
can. (Slow drift is *not* the culprit — only $\sim0.01$ MHz within a scan.)
A measured $w_0$ (fixing transit) would turn this bound into a measurement; meanwhile it is the
ONF starting linewidth for the nanofibre extension.

### 5.4 The power sweep against the ramp law

At fixed
130 °C only the AC-Stark $S_0$ varies, so the ramp law ([§2.6](03_the_ac_stark_ramp.md)) predicts, and the
data confirm: (C3a) the linewidth is **flat** — no monotonic power broadening,
with 3–8% block scatter that is the same between-block wander seen elsewhere;
(C3b) the amplitude is **consistent with $P^2$** (log-log slopes 1.83–2.12,
clustered on the two-photon rate law; 993.4121 nm sits below at 1.83). We say
*consistent with*, not *confirms*: at the thick-cell end ($\tau/\text{cm}$ up to 160)
a slope below 2 could be genuine saturation OR a weak power-dependence of the
trapping collection efficiency through the saturating emitter profile, and the
single-temperature archival sweep cannot separate the two — the 4121 low slope
is the visible symptom of that degeneracy, resolvable only by the fixed-lock session's
multi-temperature sweeps;
(C3c) the **ramp** skew (growing as $P^3$) is below detection, a bound — but the
committed residual skew is emphatically *not* zero: it is large and positive at
low power (up to about 10 sigma at 25 mW, e.g. 993.4154 nm $0.345\pm0.036$)
and *falls* with amplitude as $\sim\text{amp}^{-0.5}$. That is the Poisson
**shot-noise skewness** (the noise is right-skewed $\propto1/\sqrt{\text{counts}}$,
vanishing as the line brightens) — a statistical artifact with the *opposite*
sign and power dependence to the ramp, not a physical asymmetry. So the ramp is
the genuine null; the significant low-power skew is identified, not unexplained.
The old "power null" thus resolves into a typed suite — a null (width), a
consistency check ($P^2$), a bound (skew) — with the residual skew attributed
to shot noise rather than reported as zero.

(C3d) the same width-vs-power data **bound the AC-Stark coefficient itself**
(module M4e, `run_stark_sweep`): one shared $\kappa$ ($S_0=\kappa P$) fit to the
four peaks' FWHM-vs-power, each floating its power-independent core. In the
drifted archive the *shift* (the pull $\propto S_0$) is dead, so $\kappa$ is
constrained only through the ramp's $\propto S_0^2$ width broadening — a weak,
one-sided handle, so the best fit **rails at $\kappa=0$**. That boundary is why
the bound needs care: at $\kappa=0$ the width handle has *zero gradient*, so a
linearized (Wald) $\kappa+1.645\sigma$ interval is evaluated where the Jacobian
column vanishes and its "sigma" is a finite-difference artifact with no 95%
coverage (that route reads 1.0 MHz un-inflated and 2.4 MHz inflated, both kept
in the CSV as superseded diagnostics). The quoted limit is therefore a
**profile likelihood** — scan $\kappa$ upward, re-minimizing the per-peak cores,
to the one-sided crossing $\Delta\chi^2=2.706\times\chi^2_\text{red}$ (the
threshold scaled by the block-to-block over-dispersion $\chi^2_\text{red}=5.5$,
the same conservative rescale the $\sqrt{\chi^2_\text{red}}$ inflation applies
elsewhere). It gives a 95% profile-likelihood bound of 0.63 MHz from the
widths alone. The joint three-session full-profile fit
(`run_stark_joint`, RESULTS C3f), over 100 campaign, 46 rehearsal and 26 pilot
traces, sharpens the same channel to $S_0(225\ \text{mW})$ below 0.26 MHz,
under the 0.35 MHz predicted at the adopted waist, so the $\Delta\alpha$
bracket sits under both values on the table (Orson's published 1093 and this
work's recomputed 1145,
[§2.6](03_the_ac_stark_ramp.md)). The constraint
therefore lands on the (Δα, intensity) pair rather than adjudicating the
theory, and since the waist prior is now itself the lineage measurement, the
comparison is a direct test of it. The comparison is on magnitude and is
therefore untouched by the sign disagreement between them
([THEORY_NOTE §5](../THEORY_NOTE.md)).
The reading is a conservative bound, not a sensitivity claim: the width
channel is over-dispersed ($\chi^2_\text{red}=5.5$, block-to-block drift),
so it does not cleanly resolve or exclude $\kappa$. The $0.63$ MHz limit uses the
inflated threshold and brackets the predicted $0.35$ without measuring it. It bounds the drift, not the
coefficient's scale. There is no second channel behind it. The centre channel
was worked and yields nothing: the fitted pull reverses sign between drift
models, and the limit loosens as the drift model gains freedom,
$|S_0(225\ \text{mW})|$ below $9.49$, $14.57$ and $17.65$ MHz for linear,
one-exponential and two-exponential drift, so the pull is unidentifiable in
this archive rather than merely imprecise. The tighter centre bounds earlier
releases carried are withdrawn, because they differenced centres across changes
of the scope horizontal position ([`THEORY_NOTE.md`](../THEORY_NOTE.md) §3).
Width and shape are the archive's only light-shift channel, and the two
constructions above are two readings of that one channel, not two channels. A
fixed-lock session's stable lock would resurrect the pull
$\propto S_0$ (a far stronger handle), and the small waist makes $S_0$
several-fold larger, which would turn this bracket into a measured coefficient.

### 5.5 Radiation trapping

Thick cell, near-linear signal, drift-dominated ratios. Peak amplitude scales roughly *linearly* with density: log-log
slopes $0.94(13)$, $0.91(5)$, $0.85(15)$, $1.02(8)$ across $\times52$ in $N$ —
all consistent with slope 1 within about 1–2 sigma, so any
trapping/993-absorption rollover is weak and not resolved, consistent with
M1's temperature-flat shot-noise coefficient. This is at first sight *surprising*: the
D1 optical depth ([§2.7](04_the_composite_model.md)) is $\tau/\text{cm}\approx1$ to $60$ (⁸⁷Rb) and
$3$ to $160$ (⁸⁵Rb) across the sweep, so over the few-cm path the cell is
optically **thick** and naive trapping should bite hard. The resolution is a
real physical statement about the geometry: a thick cell without quenching
still emits nearly one collected 795 nm photon per excitation — trapping
*redistributes* the photons (a random walk to the walls) rather than destroying
them, and the wide $f18$ mm collection captures the diffuse re-emission — so the
collected signal stays $\propto N$. The near-linearity thus **bounds
non-radiative quenching to be weak** over the trapping random-walk.

Trapping's degeneracy-breaking (peak-differential) effect ([§2.7](04_the_composite_model.md)) is then sought
three ways, all model-independent. (i) The isotope-averaged slope difference is
the cleanest fingerprint: ⁸⁷Rb $\langle s\rangle=1.00(7)$ vs ⁸⁵Rb
$\langle s\rangle=0.91(5)$, i.e. ⁸⁵Rb is $0.09(8)$ *more* sublinear — the
sign trapping predicts (⁸⁵Rb has $2.6\times$ the absorbers), but only
$\sim1\sigma$: a hint, not a detection. (ii) The peak-*height* ratios are
**non-monotonic** in density (e.g. 993.4207/993.4121 nm runs
$1.09\to1.01\to2.48\to1.94$), whereas trapping would bend them *monotonically* —
so the 30–50% degeneracy-law disagreement (module M10, on the *areas*) is
between-block **drift**, not trapping. (iii) A one-parameter trapping model does not improve
the fit over pure $\propto N$ (both $\chi^2_\text{red}\gg1$, dominated by the
drift scatter). *Conclusion:* trapping is physically present and expected-large by
$\tau$, but its net effect on the collected amplitude is modest and its
degeneracy-breaking effect is $\lesssim10$%, buried under drift. Separating it
needs a fixed-lock interleaved-peak run with a controlled collection
geometry. A clean separation of the trapping/993-absorption losses and an
absolute trapping fraction additionally want [Nieddu's 2019](../lit/nieddu2019.md) same-channel
baseline (not loaded here).

### 5.6 The Lehmann cusp, not resolvable in 2025 as designed

At the
cold-dim 70 °C corner the BIC comparison ([§4.7](06_the_statistics.md)) gives
$\Delta\text{BIC}(\text{Voigt}-\text{Lehmann})=+0.4/+0.9/+3.6/-0.1$ across
peaks — a **statistical null**: three of four have $|\Delta\text{BIC}|$ below 2
(the "not worth a mention" band) and the fourth is 3.6 (weak, and it is the
same peak, 993.4192 nm, whose fits are noisiest elsewhere), against a claim gate of
$\Delta\text{BIC}\gtrsim10$. The statement is that **the archival data
cannot distinguish a cusped (Lehmann) from a smooth (Voigt) extra-broadening**
— exactly as the two-epoch design anticipated, since the $\sim2$ MHz bad-lock
laser Gaussian smears the cusp and the transit/laser split is itself
unresolved ([§2.5](02_the_lineshape.md)). No lean is claimed. The decisive cusp test is the fixed-lock session's
narrow-laser data, for which this module (closure-tested to prefer the right
form when a cusp *is* present) is validated infrastructure.

### 5.7 Area ratios against the degeneracy law

A parameter-free prediction the archive cannot yet test. For two *identical* photons the
$S\to S$ two-photon operator is purely **scalar** (rank 2 cannot connect
$J=\tfrac12\to\tfrac12$), so every $F,m_F$ has the same per-atom rate and the
line *areas* (not heights — heights confound with width) must be pure initial
population: $S\propto\text{abundance}\times(2F{+}1)$, i.e. within-isotope
ratios of exactly $5/3$ (⁸⁷Rb) and $7/5$ (⁸⁵Rb). Measured: the
within-block repeatability is 1–3%, but the area ratios swing
30–50% *between* temperatures, non-monotonically (the 993.4207/993.4121 nm
*area* ratio runs $1.10\to0.98\to2.53\to1.97$ against a constant $5/3$; the
slightly different height ratios in the trapping paragraph above tell the
same drift story) — that is between-block power/alignment drift, not physics
(real differential trapping would be smooth in density).
Two consequences: cross-peak amplitude comparisons in this archive carry
roughly 30–50% systematics (per-peak, within-block analyses like M7 are
unaffected), and the clean degeneracy-law test is a task for a fixed-lock session — measure
the four peaks **interleaved**, with power logging.

`figures/fig4_amplitude_ratios.png` draws the two measured area ratios against
those two predictions, each on its own dashed line, over cell temperature. Its
bars combine the scatter over repeats with the drift between measurement blocks,
and that combination is far larger than the difference the prediction would
show, which is the sense in which this dataset cannot test the law.

### 5.8 Foundational results underpinning the above

The sweep rate is
$0.042524(51)$ MHz/ms (laser axis), $\times11$ slower than the pre-analysis
seed, confirmed by three independent methods, sweep linear to better than 0.3% within a
block. The 20 blocks over-disperse ($\chi^2_\text{red}=8.1$), block-level
ruler scatter (bracket-to-bracket drift, and the calibrated spacing rule removes
three temperature-session combs while missing
`rulers_p/4207nm_eom_before5.csv`, which the top-three amplitude test does
flag, so the two instruments disagree about that one trace, see
[`DATA.md`](../DATA.md) §5 and
[the ruler specification](../notes/ruler_validity_and_trim_prereg.md)
amendment 3 C6),
**not** a peak-ordered trend (bracket-resolved rates are non-monotonic) — and
the quoted error is already $\sqrt{\chi^2_\text{red}}$-inflated (≈2.8×)
to absorb it, so it is a symmetric common-axis uncertainty, not a cross-peak
bias; the fits use each condition's own block rate. Total
line widths are 4.8–5.7 MHz, sitting on the [lineshape chapter](02_the_lineshape.md) budget; and the dataset
is decoded and frozen (722 files → **297 unique traces**, every anomaly —
double-saves, renames, discards, off-center-sweep mirrors — explained and
either quarantined or handled).

---

**Where the numbers live.** Modules M2, M4, M4b, M4d, M4e, M5, M6, M7, M8, M10,
M23 · producers `scripts/run_beta_self.py`, `scripts/run_global_fit.py`,
`scripts/run_lever_crosscheck.py`, `scripts/run_laser_epoch.py`,
`scripts/run_power_sweep.py`, `scripts/run_stark_sweep.py`,
`scripts/run_stark_joint.py`, `scripts/run_amplitude_trapping.py`,
`scripts/run_modelform.py`, `scripts/run_amplitude_ratios.py`,
`scripts/run_ruler.py` · results `results/beta_self.csv`,
`results/global_fit.csv`, `results/lever_crosscheck.csv`,
`results/laser_epoch.csv`, `results/power_sweep.csv`,
`results/stark_sweep.csv`, `results/stark_joint.csv`,
`results/amplitude_trapping.csv`, `results/modelform.csv`,
`results/amplitude_ratios.csv`, `results/ruler_campaign.csv` · figures
`figures/fig1_width_vs_density.png`, `figures/fig2_power_sweep.png`,
`figures/fig4_amplitude_ratios.png`, `figures/fig8_ruler.png`. The deliverable
codes C1, C2 and C3a to C3g index the same results in
[`docs/RESULTS.md`](../RESULTS.md), which is generated from these CSVs.

**What would falsify this.** A width that grew monotonically with density on
all four peaks. Every bound in this chapter is a bound because the archive's
raw widths are non-monotonic, so a clean monotonic set at the same conditions
would turn the collisional headline from a bound into a measurement and would
say the non-monotonicity was an artifact of this analysis rather than of the
2025 lock.

[← The statistics](06_the_statistics.md) · [Assumptions, and where this can go →](08_assumptions_and_outlook.md)
