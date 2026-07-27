# Research decisions

Why the analysis has the shape it has: which questions this archive can answer,
which it cannot, and what was done about the gap. The methods pages say what the
pipeline computes; this one says why it stops where it does.

Every entry points at the code or document that carries the decision.

The dataset was taken with a **drifting, hand re-centred laser lock**, so
absolute line centres are unusable and only line *shapes* survive. Most of what
follows is downstream of that one fact.

---

## 1. The total width is the observable; the split is reported with its error and correlation

The composite line is a Lorentzian (natural + collisional, `gamma_coll`)
convolved with Gaussian-like components (laser width `sigma_laser`, transit).
A single-condition fit returns both, strongly anti-correlated at
`corr(sigma_laser, gamma_coll) ~ -0.9`, closure-measured at SNR ~ 130
([linefit.py:37](../rb5s6s/linefit.py#L37)):

> the TOTAL Voigt width (their combination) is robust; the individual split is
> not — never quote a single-condition sigma_laser or gamma_coll as physics
> without its error and this correlation.

From `results/linefit_conditions.csv`, 20 conditions at one temperature (four
peaks × five powers), where the width was measured flat against power (C3a):

| quantity | range across the 20 | median error | largest error |
|---|---|---|---|
| total FWHM (the observable) | 5.28 – 5.71 MHz (8%) | 0.056 MHz (1.0%) | 0.17 MHz |
| `gamma_coll` (a component) | 0.249 – 0.695 MHz (2.8×) | 0.077 MHz | 0.33 MHz |
| `sigma_laser` (a component) | 0.216 – 2.056 MHz (9.5×) | 0.222 MHz | 1.11 MHz |

The extremes of both component ranges come from the 25 mW conditions, whose own
errors run three to five times the median — the largest `sigma_laser` error,
1.11 MHz, exceeds that column's median *value*. The wide ranges and the large
errors are one fact, not two.

![the degeneracy against the observable](../figures/fig10_degeneracy_vs_observable.png)

*Left: each condition's 1σ error ellipse from its own covariance, over contours
of constant total FWHM. The ellipses are elongated along the contours, two of
the twenty reaching unphysical negative widths, and the centres scatter in the
same direction. Right: the quantity actually measured.*

**Decision: the estimator uses only the informative direction.** `beta_self`
rides on the *difference* in `gamma_coll` across temperature, driven by the ×50
density lever, and not on any absolute per-condition value
([linefit.py:40](../rb5s6s/linefit.py#L40)).

[M12](../rb5s6s/identifiability.py) maps the degeneracy: the χ² surface is
profiled over the (`gamma_coll`, `sigma_laser`) plane with every other parameter
re-minimised at each point ([fig7](../figures/fig7_identifiability_profile.png)),
giving

> the archive constrains the TOTAL width well but the SPLIT poorly — so the
> individual coefficients are w0-conditional bounds, not measurements
> ([identifiability.py:37](../rb5s6s/identifiability.py#L37))

The local covariance is a quadratic approximation at the optimum and so
"cannot exclude a curved ('banana') valley or a second minimum"
([identifiability.py:27](../rb5s6s/identifiability.py#L27)); the global map
tests whether the free fit is one of several near-degenerate optima
([run_identifiability.py:265](../scripts/run_identifiability.py#L265)).

### 1.1 Constraining the fit relocates the degeneracy

The natural response is to impose physics: tie `gamma_coll` to `beta * N(T)`,
with `N(T)` from Nesmeyanov's liquid-Rb vapour-pressure correlation as tabulated
by Steck ([density.py:9](../rb5s6s/density.py#L9)), share `sigma_laser`, and let
the constrained fit report smooth curves. That is
[M4b](../rb5s6s/global_fit.py).

The constrained fit then produces a `sigma_laser(T)` rising to 1.5–1.6 MHz at
70/90 °C and dropping to 1.06 at 110 °C, while the *free* per-condition value is
flat at 1.0–1.2. The rise is not a measured laser drift:

> that σ_laser(T) trend is the **β↔σ_laser degeneracy** under the density
> constraint, NOT a physical laser drift — so the trend is a model artifact,
> not a stale block ([RESULTS.md](RESULTS.md) M4c)

A smooth curve from a constrained fit is not better evidence than a scattered
one from a free fit. The same missing information has been redistributed into a
parameter where it resembles physics. `fig5`'s panel-B title names the
degeneracy on the plot itself
([make_figures.py:267](../scripts/make_figures.py#L267)), and §2 is why the
constrained fit is a cross-check.

---

## 2. The model-independent bound is the headline; the global fit is a cross-check

Two estimates of `beta_self` exist: a model-independent width-versus-density
slope, and the hierarchical global fit, which is tighter. The tighter one is not
the headline.

> its beta is the best MODEL-BASED cross-check of the model-independent
> raw-width bound (M4), not a replacement for it
> ([global_fit.py:37](../rb5s6s/global_fit.py#L37))

M4's own producer says the same about its error bars, and gives the mechanism:

> the archival T-sweep BOUNDS beta_self (it does not measure it). The global-fit
> sigmas above are OVERCONFIDENT — they assume one shared sigma_laser across
> blocks and so omit exactly this between-block drift.
> ([run_beta_self.py:300](../scripts/run_beta_self.py#L300))

Between-block width scatter (residuals ~0.06–0.16 MHz) is the dominant error:
laser drift over the cooling session is comparable to the collisional trend
itself.

The per-temperature `sigma_laser` sharing was originally justified by the four
peaks having been acquired close together in time. A recovered acquisition clock
measured the blocks **54–76 minutes apart** ([RESULTS.md](RESULTS.md)). The
sharing may still hold; that justification does not.

## 3. The model ladder declines the AC-Stark parameter

The AC-Stark ramp is this programme's own proposed component. On the archival
data the ladder rejects it
([06_the_statistics.md](methods/06_the_statistics.md)):

> **A→B ≈ +1700** (transit decisively warranted), **B→C ≈ +435** … and **C→D
> ≈ −100** — *the free AC-Stark parameter is decisively NOT warranted*

> A model-comparison that *declined* to add the AC-Stark term is the statement
> of "we do not claim to have measured it here."
> ([model_ladder.py:30](../rb5s6s/model_ladder.py#L30))

On synthetic data under a stable lock the same ladder decisively warrants an
injected Stark shift ([run_model_ladder.py:12](../scripts/run_model_ladder.py#L12)),
so the null is a property of the drifted archive and not of the ladder's
sensitivity: the free per-scan centres, which the drifting lock forces, absorb
the ramp's pull.

## 4. The shared-versus-independent verdict flips with the sample counting

[M14](../rb5s6s/sharing_bic.py) scores shared against independent `sigma_laser`
by BIC. Counting the ~49k correlated samples as independent favours the free
model (ΔBIC ≈ −46); the effective sample size favours the shared one
(ΔBIC ≈ +62). The effective-N version is the statistically correct one and is
the primary number. The sign flip bounds what the archive can settle: it does
not robustly resolve shared against independent
([sharing_bic.py:37](../rb5s6s/sharing_bic.py#L37)).

A favourable score would not have meant much either:

> dBIC > 0 reads "the archive cannot justify per-block freedom" (Occam on
> underpowered data), NOT "the sharing is confirmed"
> ([sharing_bic.py:36](../rb5s6s/sharing_bic.py#L36))

The in-sample check (M4c) returns χ²/dof of 0.19/0.58/0.33 — all *below* one,
so the error bars are too large for the test to discriminate.
[RESULTS.md](RESULTS.md) records the sharing as "**untested**, not merely
unverifiable."

## 5. An aborted power block stays excluded

A first attempt at the 993.4154 nm 130 °C power sweep was aborted and redone in
full. Three reasons keep it out
([annotate_manifest_qc.py:62](../scripts/annotate_manifest_qc.py#L62)): it is
**redundant** — the canonical sweep covers all five powers and the partial retry
only 25/125/225 mW; its 225 mW set "carries a ~80x steeper baseline slope
(high-power drift, the likely abort cause)"; and it was cut before unblinding.

The lines are individually clean, matching the redo in height and width to
within 2%, and re-admitting them tightens the S0 bound while leaving `beta`
untouched:

> re-admitting previously-cut, drift-flagged data to improve a number is
> declined

Both bounds are recorded. (The specific pair quoted in that comment, 2.04 →
1.92 MHz, predates the switch to a profile-likelihood construction; the current
archival bound is **0.633 MHz** at 225 mW, `results/stark_sweep.csv`. The
comment's numbers need refreshing, the decision does not.)

A pre-registered prediction was voided rather than scored when its corroborating
wavemeter photographs turned out to lie outside the campaign window
([PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md)); the audit script
enforces the void on the integrity gate
([run_timestamp_audit.py:23](../scripts/run_timestamp_audit.py#L23)).

## 6. Withdrawn claims stay on the page

Six readings were withdrawn after publication in the pre-registration record.
Each withdrawal is recorded in place, next to the reading it replaces, with the
direction of the error ([PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md)).

Novelty claims have retreated twice. The prior-art assessment of Wall 2014 was
downgraded from "scooped" to "distinct" after the paper was read in full, and
the entry lists five specific distinctions — purely numerical treatment,
inference running the opposite direction, longitudinal rather than transverse
geometry, per-plane lines peaking at the maximum shift, and a regime where the
shift far exceeds the linewidth ([lit/wall2014.md](lit/wall2014.md)).

An earlier note claimed the transit Monte Carlo had two bugs and inferred
w0 ≈ 90 µm; that inference is retracted in place
([notes/transit_width_resolved.md](notes/transit_width_resolved.md)).

## 7. Guards added after specific failures

Most of the suite's guards are regression guards for mistakes that were made:

- a freshness guard, because a physics fix moved `beta` from 0.056 to 0.036 and
  stale figures survived it, "found only by accident"
  ([test_figures_fresh.py:4](../tests/test_figures_fresh.py#L4));
- a canonical-value guard, because one superseded number lingered "in eight
  files" ([test_docs_canonical.py:21](../tests/test_docs_canonical.py#L21));
- that guard's ±4-line window was widened after a planted violation was
  "satisfied by the very correction note explaining the reversal"
  ([test_docs_canonical.py:428](../tests/test_docs_canonical.py#L428));
- an asymptotic w0 → ∞ test, after an external red-team review found it untested
  ([test_transit_mc.py:119](../tests/test_transit_mc.py#L119)).

[M19](../rb5s6s/ramp_transit.py) came from an objection in
[Camparo and Lambropoulos 1992](lit/camparo1992.md): a distribution of light
shifts skews a line only when sampled slowly compared with the atomic response.
Atoms in flight sweep their own shift within a transit time (~0.2 µs) only a few
times 1/Γ (~45 ns), and the ramp/transit factorisation had assumed the answer.
M19 propagates the weak-excitation amplitude along each trajectory with no
quasi-static step: the first two moments reproduce the static triangle to ~0.1%
across S₀/transit-FWHM = 0.09–7.6, and the result holds under the retro standing
wave and a thermal spread of speeds. **κ₃ is not resolved** — the ν³-weighted
FFT noise floor swamps it — and κ₃ is the moment the asymmetry claim rests on.

## 8. What is not modelled, and what would revive it

Eight load-bearing assumptions are listed as a numbered attack surface
([08_assumptions_and_outlook.md](methods/08_assumptions_and_outlook.md) §6), and
individual assumptions are also flagged at the point of use — the retro ratio
ρ = 1 is "a *geometric design property, not a measured number*", and the transit
kernel's *shape* is "untested by the archival data and … a genuine attack
surface."

Descoped items carry the condition under which they return: the EOM modulation
index is dropped because the 2025 drive voltage was never recorded, and revives
in a fixed-lock session ([beta.py:8](../rb5s6s/beta.py#L8),
[PLAN.md](PLAN.md)). The waist w0 remains **OPEN**, and the config module warns
at the point of use — "Do not quote a number built on this without the w0
caveat" ([config.py:286](../rb5s6s/config.py#L286)). Every absolute result is
conditional on it.

Two negative results: no Rb 6S self-broadening coefficient exists in the
literature after four independent search framings, and Russian-language coverage
could not be closed with the tools available — a limitation, not an absence
([lit/beterov1973.md](lit/beterov1973.md)).

---

## Status vocabulary

Statuses are attached by [a script](../scripts/annotate_results_status.py), so a
status cannot be strengthened without changing the producing code.

| status | meaning |
|---|---|
| `MEASURED` | a measurement with its error |
| `BOUND` | an upper/lower limit, conditional on the OPEN w0 and/or the model |
| `NULL` | a test performed that returned no effect |
| `PRELIM` | computed, not yet load-bearing |
| `ENVELOPE` | an order-of-magnitude scale, not a fitted value |
| `DIAGNOSTIC` | an internal check, not a physics claim |
| `ARTIFACT` | a feature identified as non-physical |

`beta_self`, `sigma_laser` and the AC-Stark `S0` are all **BOUND**.
