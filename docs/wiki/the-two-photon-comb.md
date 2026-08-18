# The two-photon comb

*[wiki index](README.md) · technique*

**The question.** How far does a two-photon comb reach, and what does it
cost once the same comb is asked to measure a line shape rather than a
total rate.
**Takes.** The two-photon Bessel-squared amplitude law derived in
[EOM sidebands](eom-sidebands.md), taken here as given rather than
re-derived.
**Gives.** The carrier-null depth, why the comb sits as two small islands
rather than a carpet, and the shape-weight sum a shape fit actually draws
on.
**Skip if.** The derivation of the two-photon law itself is wanted rather
than its consequences, a case covered by [EOM sidebands](eom-sidebands.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

[EOM sidebands](eom-sidebands.md) derives what a two-photon transition does
with a phase-modulated field: it does not respond to one sideband at a time
the way a one-photon transition does, because the transition needs two
photons and the field offers a whole comb of frequencies to draw them from.
Every ordered pair of sidebands that sums to the transition frequency
contributes, and by Neumann's addition theorem the sum over pairs collapses
to a single Bessel function taken at TWICE the modulation depth: the tooth at
order $k$ carries amplitude $J_k(2\beta)$ rather than the $J_k(\beta)$ a
one-photon reading of the same drive would give. This page takes that result
as given rather than re-deriving it, and works out what it implies for how
far a two-photon comb reaches and what it can and cannot be trusted to
measure.

The doubled argument moves the feature every phase-modulation calculation
reaches for first, the carrier null. A one-photon carrier vanishes at the
first zero of $J_0$, near $\beta = 2.405$. A two-photon carrier vanishes
where $2\beta$ reaches that same zero, so near $\beta = 1.202$, not at the
familiar one-photon value. A modulation depth chosen by one-photon intuition,
set to the point that would empty a one-photon carrier, leaves a two-photon
carrier far from empty, because the argument it actually reaches is nowhere
near a zero of $J_0$.

The doubled argument also compresses the comb. Bessel amplitudes fall away
once the order exceeds the argument, so fixing $2\beta$ near the carrier null
fixes how many orders can carry appreciable power at all, independent of how
hard the modulator is driven otherwise. Only a handful of low orders qualify,
so the comb sits as two small islands of teeth around each line rather than
as a broad carpet across a spectrum, and the reach of those islands is
bounded by a small multiple of the drive frequency itself. A comb spanning
gigahertz would need either far more carrying orders than the amplitude law
allows at this depth, or a drive frequency in the gigahertz range, and a
resonant modulator, built to run efficiently at one design frequency rather
than to be retuned across that range, supplies neither.

The Bessel amplitudes carry one more identity worth separating from the null
and the reach. The two-photon rate is conserved across the comb at every
depth, not only at the null: $\sum_k J_k(2\beta)^2 = 1$ for any $\beta$, so
redistributing the light into teeth never creates or destroys two-photon
events in aggregate, it only moves them between orders. A shape measurement
built from the same comb, one that compares tooth to tooth for a width or an
asymmetry, does not draw on that same total. Each tooth's leverage on a shape
fit scales with its own weight a second time, since a brighter tooth
dominates the comparison the way a brighter pixel dominates a weighted fit,
so the total shape-fitting weight summed across teeth is
$\sum_k J_k(2\beta)^4$, not $\sum_k J_k(2\beta)^2$. The first sum is exactly
one at any depth. The second is well below it, because squaring an already
fractional amplitude a second time suppresses every tooth but the strongest
few far more than the rate sum does. That gap is what the technique costs:
modulation buys a radio-accurate frequency ruler at no cost to the total
signal, and pays for it in the precision of any shape measurement drawn
from the same comb.

## What problem it solves

Two-photon spectroscopy does not get to reuse a one-photon calibration
recipe unchanged, and the mismatch fails in two different directions at
once. Setting the depth from one-photon intuition leaves a carrier that
never actually vanishes, sitting in the middle of the very spectrum the comb
is meant to calibrate. Expecting the resulting comb to reach across a wider
span than a resonant drive can cover leaves part of that span uncalibrated
with nothing in a single fit announcing it. Working from the two-photon law
instead fixes the depth that genuinely empties the carrier, states in
advance how far the comb it produces can reach, and separates what that comb
can measure at full precision, the total rate, from what it can only measure
at a stated discount, the shape.

## Where this repository uses it

The comb's use here is partly running and partly planned, and the two are
worth separating. What RUNS today is the underlying sideband ruler: every
committed trace has its frequency axis set by fitting EOM tooth positions,
the construction of
[methods chapter 5](../methods/05_the_frequency_ruler.md), which is where
the campaign's rate of 0.04252(5) MHz per ms comes from. What is PLANNED is
the two-photon-specific treatment below, the carrier null and the
forced-against-free tooth diagnostic, neither of which has been run on data.
[docs/plan/09_the-fixed-lock.md](../plan/09_the-fixed-lock.md), section
10c.4, sets the modulation depth at the two-photon carrier null derived
above and treats the resulting comb as the local part of the frequency
ruler, with the recorded ramp channel and the atomic pair separations of
section 10c.5 carrying the scale between the comb's islands over a span the
comb itself cannot reach.
[docs/plan/10_the-fixed-lock-instrument.md](../plan/10_the-fixed-lock-instrument.md),
section 10c.10, goes further and reads the teeth as a statistical instrument
rather than only a ruler: it fits every group of teeth twice, once with the
amplitudes forced to the Bessel law derived above and once with each tooth
left free, and reads the amplitude, centre and width residuals between the
two fits as diagnostics of saturation, axis nonlinearity and power
broadening within a single trace. That comparison is exactly what
[information criteria](information-criteria.md) exist to make principled,
comparing nested models by what the extra freedom actually buys rather than
by preference.

## What can go wrong

The first failure is a model one: reading the rate identity as if it were a
shape identity. Because $\sum_k J_k(2\beta)^2$ equals one at every depth, it
is tempting to conclude the comb never costs anything, but the identity only
says that no two-photon events are lost in aggregate. A width or an
asymmetry compared tooth to tooth draws on the much smaller
$\sum_k J_k(2\beta)^4$, and nothing in a single fit flags that the two totals
answer different questions.

The second is data insufficiency created by the depth itself rather than by
the data. Fixing $\beta$ at the carrier null fixes how many orders carry
usable power, so a session that needs the ruler to reach further than that,
across a wider span or a more distant line, finds the outer part of that
span uncalibrated by the comb no matter how carefully the rest of the fit is
set up. No choice of order recovers a reach the drive frequency does not
have.

The third is an implementation trap in the diagnostic itself. The
fourth-power weighting assumes each tooth's contribution to a shape
comparison is independent, photon-limited leverage, which silently assumes
the teeth are not already distorted by whatever a forced-versus-free
amplitude residual would reveal, such as saturation compressing the strong
teeth toward the weak ones. Reading $\sum_k J_k(2\beta)^4$ as a finished
precision estimate before that residual has been checked treats a
diagnostic built to test the pure Bessel law as though it already had the
answer.

The fourth is an experimental limitation, stated plainly rather than
engineered around. A resonant modulator is built to run efficiently at one
design frequency, and reaching a comb that spans a genuinely wide range in a
single sweep needs either a different kind of modulator or a different
calibration channel entirely, not a deeper or shallower drive on the same
device.

## Try it

The squared Bessel amplitudes at the two-photon carrier null: the rate sum,
the much smaller shape-weight sum, and what a one-photon-chosen depth would
have left behind in the carrier instead.

```python
import numpy as np
from scipy.special import jv, jn_zeros

# The two-photon carrier vanishes where 2*beta reaches the first zero of J0
# (see bessel-functions.md), so the carrier-null depth is half that zero.
first_zero_of_j0 = jn_zeros(0, 1)[0]
beta_two_photon_null = first_zero_of_j0 / 2.0
argument = 2.0 * beta_two_photon_null  # equals first_zero_of_j0

orders = np.arange(-12, 13)
rate = np.array([jv(k, argument) ** 2 for k in orders])  # J_k(2 beta)^2

sum_rate = rate.sum()
sum_shape = (rate ** 2).sum()

print(f"two-photon carrier null at beta = {beta_two_photon_null:.4f} "
      f"(the one-photon null is at beta = {first_zero_of_j0:.4f})")
print(f"sum of J_k(2 beta)^2 across the comb: {sum_rate:.6f}  <- the total rate")
print(f"sum of J_k(2 beta)^4 across the comb: {sum_shape:.6f}  <- the shape weight")

# Driven at the one-photon null instead, the two-photon argument is 2x that,
# nowhere near a zero of J0, so the carrier tooth is far from empty.
carrier_at_one_photon_null = jv(0, 2.0 * first_zero_of_j0) ** 2
print(f"if the depth were chosen from one-photon intuition instead, the "
      f"two-photon carrier would still carry {carrier_at_one_photon_null:.3f} "
      f"of its zero-drive weight, not the near-zero a one-photon reading expects")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [EOM sidebands](eom-sidebands.md) for the derivation of the two-photon
  amplitude law from Neumann's addition theorem, and the modulator design
  compromise the doubled argument forces.
- [Bessel functions](bessel-functions.md) for the Jacobi-Anger identity and
  the power-conservation identity the rate sum above is a special case of.
- [`../lit/bjorkholm1976.md`](../lit/bjorkholm1976.md), the closed-form
  two-photon absorption theory, for why a two-photon transition responds to
  the field as a pair of photons rather than one.
- [Information criteria](information-criteria.md) for the forced-versus-free
  comparison this repository's comb-as-instrument plan relies on.

## See also

- [EOM sidebands](eom-sidebands.md) for the derivation of the two-photon
  amplitude law this page treats as given.
- [Bessel functions](bessel-functions.md) for the Jacobi-Anger and
  power-conservation identities behind the rate and shape sums above.
- [Information criteria](information-criteria.md) for how the
  forced-versus-free tooth comparison is judged in a principled way.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md)
  for how the comb's islands fit into the full frequency calibration.

---

[← EOM sidebands](eom-sidebands.md) · *Driving, modulating and detecting, 2 of 8* · [The wavemeter and the frequency axis →](the-wavemeter-and-the-frequency-axis.md)
