# Information criteria

*[wiki index](README.md) · method*

**The question.** Whether an extra parameter or model component is justified
by the data, not merely by a lower chi-squared.
**Takes.** Two or more fits already carried out on the same data, each with
its own chi-squared and parameter count. No new fitting.
**Gives.** The AIC and BIC penalties, when a comparison is
criterion-independent, and the F-test for the narrower case of nested
models.
**Skip if.** The question is whether a single parameter is determined by the
data at all, not whether a model deserves an extra one. That is
[identifiability](identifiability.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A richer model always fits better. Adding a parameter cannot increase the
best achievable $\chi^2$, so goodness of fit alone always prefers the more
complicated model and is useless for choosing between them. An information
criterion scores a model as its fit quality plus a penalty for the parameters
it used, and the model with the lowest score wins.

The two standard criteria differ only in that penalty:

$$\text{AIC}=\chi^2+2k \qquad \text{BIC}=\chi^2+k\ln N$$

with $k$ the number of free parameters and $N$ the number of points. Akaike's
criterion penalizes each parameter by 2, whatever the data volume, and
derives from estimating out-of-sample predictive loss. The Bayesian criterion
penalizes each parameter by $\ln N$, which grows as data accumulate, and
approximates a Bayes factor between models. AICc is Akaike's small-sample
correction, which matters when $N$ is not large compared with $k$.

![the per-parameter penalty for each criterion](figures/wiki_ic_penalty.png)

*The two penalties against sample size. They agree at $N = e^2$, about seven
points. Beyond that the Bayesian penalty grows without limit, so on a large
dataset it demands several times the evidence Akaike's does before admitting
a parameter.*

Two consequences bound how much the choice can matter. A comparison between
two forms with the same number of parameters is unaffected by the criterion
entirely, because the penalty is identical on both sides and cancels, so such
a comparison is a $\chi^2$ comparison however it is dressed. A criterion only
decides an outcome when the fit improvement lands between the two penalties.
When a component improves the fit by far more than $\ln N$ per parameter, or
by far less than 2, every criterion agrees, and the conclusion comes from the
data, not from the choice of criterion.

A criterion is also only as good as the fit it scores. A richer model that
contains a simpler one cannot fit worse at its own optimum, so a comparison
showing it doing so is measuring the optimiser, not the data, and no penalty
term repairs that.

## What problem it solves

It converts "is this extra component justified" from a matter of taste into
an arithmetic with a stated convention, and it does so without requiring the
models to be nested, which is where a likelihood-ratio test cannot go.

## Where this repository uses it

For every complexity decision, and
[methods chapter 6 sections 4.7 and 4.7a](../methods/06_the_statistics.md)
carry both the choice and the sensitivity to it, implemented in
[`rb5s6s/modelform.py`](../../rb5s6s/modelform.py).

![the four line-shape kernels compared directly](../../figures/fig26_lineshape_kernels.png)

*The four line-shape kernels compared directly. This is the
equal-parameter-count comparison this page cites as criterion-independent.*

The choice is not academic here, because $N$ varies by four orders of
magnitude across the places this record makes a complexity decision, from a
handful of noise-law bins to a global fit over hundreds of thousands of
points. The chapter tabulates the penalty ratio at each. It also reports a
panel of criteria instead of one. Agreement across the panel is read as
robustness. Disagreement is read as a fact about the sample size, not as a
choice among answers.

Two applications are worth singling out. The comparison between competing
line-shape kernels has equal parameter counts on both sides, so it falls in
the criterion-independent case above. The decision that the light-shift
parameter is a bound, not a measurement, rests on an improvement far below
any penalty, so it is criterion-independent too, which matters because it is
the conclusion a reader is most entitled to be suspicious of.

## The implemented hierarchy

`rb5s6s/model_compare.py` computes the comparison as an evidence vector. A
separate function makes the judgement, so no threshold inside the comparison
itself returns "preferred".

| statistic | what it assumes | status here |
|---|---|---|
| delta chi-square, likelihood ratio | nested models, and a residual structure the reference distribution matches | reported where nesting holds |
| parametric bootstrap of the selection statistic | only that the generative model can be sampled | reported, and uncalibrated until a coverage run measures it on this noise |
| classical F | independent, homoscedastic, Gaussian residuals from linear models | reported as a labelled convention, never as a verdict |
| AIC, AICc, BIC | differing parsimony conventions, and a sample size | reported both raw and effective |

This experiment has correlated samples, a fitted noise law, nonlinear models
and nuisance parameters. Substituting an effective sample size for N does not
restore the reference distribution, because under correlation the numerator
and denominator sums of squares stop being independent scaled chi-squares,
and no substitution for N recovers that. The implementation therefore returns
the statistic together with a validity flag and the specific condition
violated.

An effective BIC is the whitened chi-square against a penalty on the
effective count. Using a raw chi-square against a reduced penalty inflates
the fit's apparent gain by roughly the correlation time while lowering its
parameter cost, and on this archive that half-treatment reverses a verdict,
moving a delta-BIC from decisively negative to decisively positive (the two
rows of [`sharing_bic.csv`](../../results/sharing_bic.csv), -51.9 and +61.3 at
this writing, regenerated with the rates). The implementation refuses to
compute the effective form unless both are supplied.

The interpretation layer returns one of four outcomes:

**robust**, every available criterion agrees and at least one separates
decisively. **convention-dependent**, the criteria disagree among themselves,
so the preference is a choice of convention, not a fact about the data.
**assumption-dependent**, the raw and effective forms point opposite ways, so
the answer is about the correlation treatment. **unresolved**, nothing
separates the models at the threshold treated as decisive.

## What can go wrong

The deepest failure is a comparability one. These criteria compare models
fitted to the same data with likelihoods on the same scale. Comparing scores
across different datasets, different weightings, or a fit whose likelihood
was rescaled, is meaningless arithmetic that produces a perfectly ordinary
looking number.

The second is correlated data. Both penalties count $N$ as independent
samples, and when samples are correlated the effective count is smaller,
which makes the Bayesian penalty too harsh. Correcting by an effective sample
size is a defensible sensitivity check, not an established theorem, and
should be labelled as one.

Third, a model failure the criteria cannot see. They rank the models offered
and say nothing about whether the best of them is any good. A criterion will
select the least-wrong member of a set of wrong models, so an absolute
goodness-of-fit check belongs beside the ranking.

Fourth, an implementation trap: the penalties above assume $\chi^2$ is a
proper log-likelihood times minus two, which requires the weights to be the
real measurement uncertainties. With arbitrary weights the fit may be fine
and the criterion arithmetic is not.

Finally, a reporting failure. Selecting a model and then quoting its
parameter uncertainties as though the model had been fixed in advance
understates them, because the selection itself used the data.

## The nested case

An information criterion compares models that need not be related. When one
model is a restriction of another, obtained by fixing or tying parameters,
not by changing the functional form, a sharper tool applies. The F-test
compares the drop in the residual sum of squares against the number of
parameters given up, referred to an F distribution with those two degrees of
freedom. It answers a question different from a criterion. A criterion asks
which model predicts better. The F-test asks whether the extra freedom
produced a statistically significant improvement.

![a frequency comb at two modulation depths](figures/wiki_eom_comb.png)

*A frequency comb at two modulation depths. This is the structure the
forced-versus-free tooth model in the nested F-test example is fitted
against.*

The distinction matters for a modulated spectrum. A comb of teeth can be
fitted twice. The forced model shares one centre, the radio-exact tooth
spacing and the Bessel amplitude law across the whole group, and has very few
free parameters. The free model lets every tooth carry its own amplitude,
centre and width. The second contains the first exactly, so the pair is
nested, and the F-test asks whether releasing the constraints improved the
fit by more than the parameters cost. A significant result does not say the
comb model is wrong in general, it says the data see structure the
constraints forbid, and the residuals then say which constraint: amplitude
residuals against the Bessel law read saturation, centre residuals map the
frequency axis tooth by tooth, and width residuals across teeth of different
strength read power broadening within one trace.

Two cautions carry over unchanged. The test assumes the larger model is
correct and the weights are real uncertainties, so a poor overall fit
invalidates the comparison instead of being reported by it. And an F-test on
models that are not nested is not a smaller version of the same idea, it is
undefined, which is where a criterion remains the only instrument.

## Try it

The case where the criteria disagree. A gain of eight in chi-squared for one
extra parameter, on four thousand points.

```python
import numpy as np

n, gain, k = 4000, 8.0, 1
d_aic = 2 * k - gain
d_bic = k * np.log(n) - gain
print(f"a {gain:.0f}-unit chi2 gain for {k} parameter at N = {n}")
print(f"  Akaike:   {d_aic:+.1f}  -> prefers the "
      f"{'richer' if d_aic < 0 else 'simpler'} model")
print(f"  Bayesian: {d_bic:+.1f}  -> prefers the "
      f"{'richer' if d_bic < 0 else 'simpler'} model")
```

## Further reading

- K. P. Burnham and D. R. Anderson, *Model Selection and Multimodel
  Inference* (Springer, 2002), the standard treatment of AIC and AICc.
- R. E. Kass and A. E. Raftery, "Bayes factors", *J. Am. Stat. Assoc.* **90**,
  773 (1995), for the BIC scale on which a difference below 2 is
  indistinguishable and above 10 decisive.
- [Methods chapter 6](../methods/06_the_statistics.md) for this repository's
  panel and the one case where its members disagree.

## See also

- [Identifiability](identifiability.md), for the question of whether a
  parameter is determined at all, which a criterion does not ask.
- [The profile likelihood](profile-likelihood.md), for the interval
  construction that shares this repository's likelihood machinery.
- [Weighted least squares](weighted-least-squares.md), for the real weights
  a criterion's chi-squared has to be built from.

---

[← Pooling across groups](pooling-across-groups.md) · *Statistical inference, 4 of 9* · [Identifiability →](identifiability.md)
