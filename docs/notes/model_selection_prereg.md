# Preregistration: AIC as the model-complexity criterion

**Written 2026-08-15, BEFORE any recomputation.** Nothing in this note reports
a result. Its whole purpose is to fix, in advance, what is being re-decided and
what each outcome would mean, because changing a selection criterion after
seeing which way it goes is the failure mode preregistration exists to stop.

## Why this note exists

Standing instruction from the owner, 2026-08-15: use AIC as the main criterion
for choosing the complexity of the models we adopt, and explain the choice in
the documents, in the methods and in the big picture.

The record currently chooses complexity with BIC in the places it chooses at
all. This note fixes what changing that would mean before it is tried.

## What the two criteria are, and the arithmetic that matters here

Both score a fitted model as goodness of fit plus a penalty for parameters.
The penalty per parameter is the whole difference:

    AIC penalty = 2            always
    BIC penalty = ln(n)        grows with the number of data points

So which is more conservative depends entirely on n, and **n is not one number
in this project**. Measured:

| decision site | n | ln(n) | BIC penalty / AIC penalty |
|---|---|---|---|
| noise variance law (`fit_variance_law`) | 10 level bins | 2.30 | 1.15 |
| one condition line fit (5 traces, ~889 points each) | 4445 | 8.40 | 4.20 |
| M25 global dataset fit | 404615 | 12.91 | 6.46 |

This table is the reason the change is worth making carefully rather than
globally. A first draft of the night plan asserted "n of order 10^4 to 10^5" at
every site and that is wrong: the noise law's n is the number of LEVEL BINS,
ten of them, where the two criteria are within 15 per cent of each other. At
that site BIC is not the conservative element at all. `NOISE_BIC_MARGIN = 6.0`
is: a hand-set margin requiring the quadratic term to win by six units on top
of whichever criterion is used. Switching criteria there would change almost
nothing, and removing or justifying that margin is the real question.

Where the criterion DOES matter is the fits over raw samples, four to six times
the penalty per parameter, and that is exactly where the open physics sits.

## The comparisons being re-decided

### C1. The noise variance law, quadratic term

`rb5s6s/noise.py fit_variance_law` chooses between `sigma^2 = a^2 + bV` and
`sigma^2 = a^2 + bV + cV^2`, currently by BIC with the margin above.

- What AIC would admit: the `c` term more often.
- What depends on it: every per-point weight in every fit, hence every error
  bar and every profile-likelihood bound.
- PREDICTION, fixed here: because n is 10 and the margin is 6.0, the criterion
  switch alone will flip few or no conditions. If many flip, the cause is the
  margin and not the criterion, and the note reporting it must say so.

### C2. Cusp against pure Voigt, the transit kernel

`rb5s6s/lineshape.py:178-183` documents a `transit_kind` switch, `'exp'` (the
Biraben-Cagnac two-sided exponential, whose central cusp is the transit
signature) against `'gaussian'` (making the whole line a pure Voigt, no cusp).
`docs/THEORY_NOTE.md:293` calls this "checkable by BIC and the M8 cusp fit".

- **THIS COMPARISON IS STRUCTURALLY IMMUNE TO THE CRITERION, and an earlier
  draft of this note had it wrong.** `rb5s6s/modelform.py:8-9` states it
  plainly: the Voigt and the Lehmann cusp "have the same parameter count, so a
  Bayesian-information-criterion comparison is essentially a chi^2 comparison".
  With k equal on both sides the penalty term cancels in the difference,
  whatever the penalty is. AIC changes nothing here, at any n. The committed
  `results/modelform.csv` differences are 0.44 to 3.70, below "decisive" on any
  scale, and they stay exactly where they are.
- What depends on it: `beta_self`. The lineshape module states in its own words
  that running the fit under both and differencing beta "gives the model-form
  error bar the paper must quote". That remains worth producing. It is a
  MODEL-FORM SYSTEMATIC to be quoted, not a selection to be made, and this note
  should never have filed it under the criterion change.
- A BLOCKER THAT MUST BE FIXED FIRST: the production path cannot do this
  comparison. `rb5s6s/linefit.py:100` hardcodes `two_sided_exponential` with no
  `transit_kind` argument, so the switch exists only in the sibling builder in
  `lineshape.py`. The model-form error bar the record says the paper must quote
  is not currently producible by the fit that makes the record's widths. Adding
  the argument, defaulting to the current behaviour so no committed number
  moves, is a precondition for C2.

### C3. The sigma_laser sharing comparison. THE ONE SITE THAT FLIPS.

`rb5s6s/sharing_bic.py` (M14) compares `sigma_laser` shared per temperature
(241 parameters) against per block (250, nine more), scored with a
correlation-corrected BIC on an effective sample size `N_eff = N / tau_int`.
The committed `results/sharing_bic.csv` has `N_eff = 13853` and
`dBIC_eff = +61.3`, decisive in favour of sharing.

Working the arithmetic back from those committed numbers: the chi-squared
difference is 61.3 - 9 ln(13853) = -24.6, meaning per-block genuinely fits
better, as a nested richer model must. BIC charges 9 ln(13853) = 85.8 for the
nine extra parameters and AIC would charge 18, so

    dAIC = -24.6 - 18 = -6.6

**AIC reverses the verdict**: BIC says share decisively, AIC says do not share,
mildly. This is the only site in the repository where the criterion change
demonstrably flips an answer.

- What depends on it: `sharing_bic.csv` and the default `sigma_sharing="per_T"`
  baked into `rb5s6s/global_fit.py:58`, which feeds the lever cross-check.
- What does NOT depend on it: the headline. Both `docs/RESULTS.md` and
  methods 4.13 already say the headline stays the model-independent width-slope
  bound rather than the sharing-dependent hierarchical value, and the sharing
  axis contributes about 0.001 of the quoted 0.014 model-form spread. So the
  flip changes a cross-check and an interpretive label.
- Note the direction, because it is the opposite of the intuition that started
  this: AIC here admits LESS sharing, that is MORE free parameters, which is
  the "admits more structure" direction. It just lands on a cross-check.

### C4. The nested model ladder (M11), robust

`rb5s6s/model_ladder.py`, summed over 12 t-sweep conditions with n of 4005 to
4322 each. From the committed `results/model_ladder.csv`:

| rung | dBIC | under AIC | flips? |
|---|---|---|---|
| A Voigt -> B +transit | +878.9 | unchanged | no: B adds NO free parameter, so no penalty term exists to change |
| B -> C +collisional width | +1090.8 | about +1167 | no, and more decisive |
| C -> D +AC-Stark ramp | -100.1 | about -24 | no: the chi-squared gain from the Stark term is about 0.33 in total, so nothing buys it |

The C to D rung is the one that matters for the headline, because it is the
statement that the AC-Stark parameter is not warranted on the drifted data and
therefore that the result is a bound rather than a measurement. **It survives
the criterion change comfortably**: the ramp buys essentially zero chi-squared,
so no penalty scheme can prefer it. That is a reassuring result for the record
and it should be stated rather than left implicit.

### C5. What already uses AIC, and the convention that exists

`scripts/run_drift_settling.py` already uses AIC and AICc, and its stated
reason is small n ("At n=26 the criterion is AICc"). It writes nothing to
`results/`.

So the codebase already practises a defensible convention: AICc where n is
tens, BIC where n is thousands. **Adopting AIC everywhere would REVERSE that
convention at the large-n sites rather than extend it**, and the owner should
know that before it is adopted, because the existing behaviour is not an
oversight. There are three ways forward: AIC everywhere as instructed, AIC
everywhere with the small-n sites using AICc (which is AIC, corrected, and is
what small n requires), or the current split made explicit and defended. This
note recommends none of them and exists so the choice is made with the
consequences in hand.

## What this preregistration commits to

1. **The PANEL is reported at every site, always, as numbers.** (Amended
   2026-08-15 by owner instruction: not AIC alone but three or four criteria,
   their pros and cons weighed, their disagreement used informatively.) The
   panel is AIC, AICc, BIC over raw n, and BIC over the repository's
   effective sample size n/tau_int, the last labelled as a repository-defined
   sensitivity criterion rather than an established theorem. These are a
   robustness check across selection conventions, not four independent votes:
   AIC and AICc are near-kin, as are the two BIC forms. Output is the
   numerical delta under every member, so a reader can tell a marginal
   disagreement from a large-but-opposed one. Agreement means the selection
   is robust across the panel's conventions. A split means the ranking is
   convention-sensitive at this sample size, and a split cannot by itself
   justify adoption: adoption then requires a predeclared independent basis
   (synthetic recovery, residual structure, a physical constraint, or owner
   adjudication), stated as such. Comparability precondition: same likelihood
   and data basis, same objective and weights, consistent parameter
   accounting, or the panel is not run and the reason is stated.
2. **The helper is validated before use.** One shared implementation, in
   `rb5s6s/modelform.py`, checked against a case whose answer is known
   independently. This is the discipline the Sobol estimator earned when it
   returned first-order indices above total-order ones and the estimator turned
   out to be correct but under-sampled.
3. **Reproduction before belief.** The new helper, handed BIC, must reproduce
   the current committed decision at every site. A helper that cannot reproduce
   the present answer has not earned the right to give a new one.
4. **Adoption is not mine.** This note preregisters a MEASUREMENT of what the
   criterion change would do. Whether any flip enters the record is the owner's
   decision, and no committed CSV or results narrative changes without it.
5. **No outcome is a failure.** If AIC changes nothing anywhere, that is a
   clean and publishable statement about the robustness of the model choices,
   and it will be reported as plainly as any flip.

## What would have to change if a comparison flips

- C1 flips: the weights change, so every bound must be recomputed before any of
  them is quoted again. This is the widest-reaching outcome and the one most
  likely to be a lot of work for little movement.
- C2 flips toward the cusp: nothing moves, because the cusp is already what
  production uses. It would confirm the current choice on a stated criterion
  rather than by inheritance, which is worth having.
- C2 flips toward the Voigt: `beta_self` moves by the model-form difference,
  and the record gains the error bar it currently says it owes.
- C3 flips: the sharing structure of the affected fit changes, which is a
  model-class change and therefore automatically an owner decision.

## Relation to the open wing question

Measured 2026-08-15 and written up in the private evidence directory: the model
runs a few tenths of one per cent of peak BELOW the data through the whole
unfitted outer region, symmetrically, on every peak. Separately, the fitted
window sets `gamma_coll` at the 30-per-cent level while chi-squared stays flat.

Both are reasons to expect the data to support MORE structure than the current
model carries, and AIC is the criterion that would let it. That is a motivation
and explicitly NOT a prediction: this note does not assume the wing excess is
real physics, and the density evidence for it stands at 2.8 sigma, which is not
a detection.
