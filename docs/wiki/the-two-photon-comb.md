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
to a single Bessel function taken at twice the modulation depth: the tooth at
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
worth separating. What runs today is the underlying sideband ruler: every
committed trace has its frequency axis set by fitting EOM tooth positions,
the construction of
[methods chapter 5](../methods/05_the_frequency_ruler.md), which is where
the campaign's rate of 0.04252(5) MHz per ms comes from. What is planned is
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

## Two spacings from one drive, and where the factor of two lives

The sidebands sit at $\nu_c + n\Omega$ on each beam, and there is no optical
component anywhere at $\Omega/2$. Yet the observed teeth stand $\Omega/2$
apart on the laser axis. The resolution is that a two-photon resonance
constrains the sum: $2\nu_c + s\Omega = \nu_0$ with $s = n + m$, so the
laser sits at $\nu_c = (\nu_0 - s\Omega)/2$ and consecutive $s$ move the sum
by $\Omega$ but the laser by $\Omega/2$. The half-spacing belongs to the
scan axis rather than to any photon, and a pair such as $(+1,-1)$ has $s=0$
and lands on the carrier tooth rather than making a new one. Running the
drive and the spacing together has already halved a hardware recommendation
once, which is why this paragraph exists.

## Tooth positions are not teeth

A tooth needs a position and a resonance. The positions repeat every
$\Omega/2$ across the whole sweep, and the teeth exist only where an atomic
line supplies the resonance, with heights falling as $J_s(2\beta)^2$, which
at practical depths leaves about five usable teeth per line. Over a
multi-GHz span the comb is therefore a few clusters a few tens of MHz wide
around the lines, with the gaps between them carrying no marks at all.
Counting positions where teeth are needed overstates the ruler by an order
of magnitude, and this record made exactly that error once, quoting 192
positions where 20 teeth existed.

The repair, where the gaps must be measured, is a second drive in cascade:
with two tones the tooth at offset $s_1\Omega_1 + s_2\Omega_2$ carries
$J_{s_1}(2\beta_1)^2 J_{s_2}(2\beta_2)^2$, so each coarse order is a
displaced copy of the whole fine cluster and the islands become a lattice.
The cost is that the carrier keeps only $J_0(2\beta_2)^2$ of its height,
under a tenth at gap-filling depths, so the cascade belongs on interleaved
calibration sweeps rather than on the science sweeps.

## What the teeth are worth as statistics

Each tooth is a copy of the atomic line, so a comb trace looks like free
replicas, and per sweep it never is: phase modulation conserves the signal
while the detector floor taxes every copy, so an RF-on sweep carries less
width information than the RF-off sweep it replaces. The design question is
usually different, though. Where the RF-on sweeps exist anyway, as
calibration brackets, their information is marginal and free, and it joins
the same likelihood the science sweeps feed. The depth then splits by the
trace's job: a trace that exists to be a ruler goes deep, because spacing
information is lever-weighted and climbs with depth, and a trace that
exists for widths stays shallow or unmodulated. Within one trace every
tooth and every line also shares a single detector gain, which makes
intra-trace height ratios immune to the gain drift that plagues ratios
assembled across traces.

## Tooth heights between two limits, and where the crossovers go

The weights $J_s(2\beta)^2$ are not a property of the modulator. They are an
interference result, and they hold only when every pathway to a tooth
carries the same phase.

A tooth at sum offset $s$ is fed by every sideband pair $(n, s-n)$: the
carrier tooth by $(0,0)$, by $(+1,-1)$, by $(+2,-2)$, and so on. At zero
relative delay these pathways interfere, and their coherent sum is
$J_s(2\beta)$ by the Bessel addition theorem, which is why a carrier can
NULL at $2\beta = 2.405$ while all its crossover pathways still exist: they
cancel. One photon of each pair comes from the retro beam, though, delayed
by $\tau(z)$ for an atom at $z$, so the pathway $(n, s-n)$ carries a phase
$(s-n)\Omega\tau$, and the sum collapses exactly to a single tone at
effective depth $2\beta\cos(\pi f\tau)$. An atom therefore shows weights
$J_s(2\beta\cos(\pi f\tau))^2$, and a cell shows their average.

The average is where the crossovers come back. Smearing $\tau$ across a
cell undoes the cancellation, the $(k,-k)$ pairs return to the carrier as
added height, and the null at 2.405 fills in. Whether any of this matters
is one number, the phase $2\pi f\tau$: at a 12.5 MHz drive across a 10 cm
cell it is 0.05 rad and the zero-delay weights hold to two parts in a
thousand, while at 580 MHz it is order three, the effective depth sweeps
through zero, and a high-order tooth computed in the zero-delay limit can
be wrong by a factor of fifty.

Two escapes exist. Modulate one arm only, between the cell and the retro
mirror: each pathway then carries a distinct order, nothing interferes, and
the zero-delay weights are exact at any drive. Or stay at a drive low
enough that the phase is small, which is what this record's 12.5 MHz comb
does without having had to know it. Residual amplitude modulation adds a
separate, MEASURED deviation on top of either limit, the $\pm k$ height
asymmetry the constants file documents.
`rb5s6s.forecast.comb_tooth_weights` computes both limits and the average,
with the identity tested against the explicit pathway sum.

## The comb and the atomic pairs divide the labour

An experiment with hyperfine structure carries a second ruler for free: two
lines of the same isotope are separated by a combination of hyperfine
constants, often known to kHz. It is tempting to ask which ruler is better,
and the question is wrong, because they answer different needs.

The atomic pair is the anchor. It is absolute and costs nothing, and it is
sparse: two marks per isotope, far apart, saying nothing about the axis
between them, and immune to the light shift at first order when the shift is
scalar, since both members move identically. The comb is the interpolator and
the CLOCK: a mark every tooth spacing, everywhere in the sweep, exact against
an RF synthesiser, able to carry a per-block rate and a drift bound at
sub-second averaging times, and carrying no absolute frequency at all.

A third reading appears when the drive is set so an integer number of tooth
spacings equals the pair separation. The tooth of one line then lands on the
other line's carrier, both are excited in the same millisecond, and the pair
stops being a ruler and becomes a measurable: the splitting of the resulting
doublet reads the hyperfine separation against the synthesiser, drift-free
and light-shift-free, at whatever precision the line centres support.

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
