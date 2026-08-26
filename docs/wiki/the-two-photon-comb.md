# The two-photon comb

*[wiki index](README.md) · technique*

**The question.** How far a two-photon comb reaches, and what it costs to
use the same comb for a line shape instead of a total rate.
**Takes.** The two-photon Bessel-squared amplitude law derived in
[EOM sidebands](eom-sidebands.md), taken here as given.
**Gives.** The carrier-null depth, why the comb sits as two small islands
instead of a carpet, and the shape-weight sum a shape fit draws on.
**Skip if.** The derivation of the two-photon law is wanted instead of its
consequences, covered in [EOM sidebands](eom-sidebands.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A two-photon transition does not respond to one sideband at a time the way
a one-photon transition does: it needs two photons, and the field offers a
whole comb of frequencies to draw them from. Every ordered pair of
sidebands summing to the transition frequency contributes, and by
Neumann's addition theorem the sum over pairs collapses to a single Bessel
function at twice the modulation depth. The tooth at order $k$ carries
amplitude $J_k(2\beta)$, not the $J_k(\beta)$ a one-photon reading of the
same drive would give.

That doubled argument moves the carrier null. A one-photon carrier vanishes
at the first zero of $J_0$, near $\beta = 2.405$. A two-photon carrier
vanishes where $2\beta$ reaches that same zero, so near $\beta = 1.202$. A
depth chosen by one-photon intuition leaves a two-photon carrier far from
empty, because the argument it actually reaches is nowhere near a zero of
$J_0$.

The same doubling compresses the comb: only a handful of low orders carry
appreciable power at the null depth, so the comb sits as two small islands
of teeth around each line instead of a broad carpet, with reach bounded by
a small multiple of the drive frequency. A comb spanning gigahertz needs
more carrying orders than the amplitude law allows at this depth, or a
drive frequency in the gigahertz range that a resonant modulator, built
for one design frequency, does not supply.

One more identity matters. The rate is conserved across the comb at every
depth: $\sum_k J_k(2\beta)^2 = 1$ for any $\beta$, so redistributing light
into teeth never creates or destroys two-photon events, only moves them
between orders. A shape measurement, comparing tooth to tooth for a width
or an asymmetry, does not draw on that total: each tooth's leverage scales
with its own weight a second time, the way a brighter pixel dominates a
weighted fit, so the shape-fitting weight is $\sum_k J_k(2\beta)^4$, not
$\sum_k J_k(2\beta)^2$. The first sum is exactly one at any depth. The
second is well below it, since squaring an already fractional amplitude a
second time suppresses every tooth but the strongest few far more than
the rate sum does. The rate survives modulation intact. The precision of
a shape measurement from the same comb does not.

## What problem it solves

Two-photon spectroscopy cannot reuse a one-photon calibration recipe
unchanged. Setting the depth from one-photon intuition leaves a carrier
that never vanishes, sitting in the spectrum the comb calibrates.
Expecting the comb to reach further than a resonant drive can cover
leaves part of that span uncalibrated, with nothing in a single fit
announcing it. Working from the two-photon law instead fixes the depth
that empties the carrier, states in advance how far the comb can reach,
and separates what it measures at full precision, the total rate, from
what it measures only at reduced precision, the shape.

## Where this repository uses it

What runs today is the underlying sideband ruler: every committed trace
has its frequency axis set by fitting EOM tooth positions, the
construction of
[methods chapter 5](../methods/05_the_frequency_ruler.md), source of the
campaign's rate of 0.04252(5) MHz per ms.

![A ruler trace and its constrained comb-tooth fit](../../figures/fig8_ruler.png)

*A single ruler trace and its constrained comb-tooth fit, with the local
rate held flat across the sweep's interior.*

What is planned is the two-photon-specific treatment below: the carrier
null and a forced-against-free tooth diagnostic, neither yet run on data.
[docs/plan/09_the-fixed-lock.md](../plan/09_the-fixed-lock.md), section
10c.4, sets the modulation depth at the carrier null and treats the
resulting comb as the local part of the frequency ruler, with the ramp
channel and section 10c.5's atomic pair separations carrying the scale
between the comb's islands.
[docs/plan/10_the-fixed-lock-instrument.md](../plan/10_the-fixed-lock-instrument.md),
section 10c.10, reads the teeth as a statistical instrument: it fits every
group of teeth twice, once forced to the Bessel law and once with each
tooth free, and reads the residuals between the two fits as diagnostics of
saturation, axis nonlinearity and power broadening within a single trace.
[Information criteria](information-criteria.md) compares such nested
models by how much the extra freedom improves the fit, not by preference.

## Two spacings from one drive, and where the factor of two lives

The sidebands sit at $\nu_c + n\Omega$ on each beam, and no optical
component sits at $\Omega/2$. Yet the observed teeth stand $\Omega/2$
apart on the laser axis, because a two-photon resonance constrains the
sum: $2\nu_c + s\Omega = \nu_0$ with $s = n + m$, so the laser sits at
$\nu_c = (\nu_0 - s\Omega)/2$, and consecutive $s$ move the sum by $\Omega$
but the laser by $\Omega/2$. The half-spacing belongs to the scan axis,
not to any photon, and a pair such as $(+1,-1)$ has $s=0$ and lands on the
carrier tooth instead of making a new one.

## Tooth positions are not teeth

A tooth needs a position and a resonance. Positions repeat every
$\Omega/2$ across the sweep, but teeth exist only where an atomic line
supplies the resonance, with heights falling as $J_s(2\beta)^2$, leaving
about five usable teeth per line. Over a multi-GHz
span the comb is a few clusters a few tens of MHz wide around the lines,
with the gaps between them carrying no marks.

![Oscilloscope trace of the modulator's comb teeth](../apparatus/2025-07-15_eom_comb_five_teeth.jpg)

*An oscilloscope trace of the modulator's comb teeth, showing the islands
of usable orders instead of a continuous carpet.*

Counting positions where teeth are needed overstates the ruler by an
order of magnitude: at this drive, about 192 tooth positions span the
pairs, and about 20 of them fall on an atomic line and carry a resonance.

The repair is a second drive in cascade: with two tones the tooth at
offset $s_1\Omega_1 + s_2\Omega_2$ carries
$J_{s_1}(2\beta_1)^2 J_{s_2}(2\beta_2)^2$, so each coarse order is a
displaced copy of the whole fine cluster and the islands become a
lattice. The cost is that the carrier keeps only $J_0(2\beta_2)^2$ of its
height, under a tenth at gap-filling depths, so the cascade belongs on
interleaved calibration sweeps, not the science sweeps.

## What the teeth are worth as statistics

Each tooth is a copy of the atomic line, so a comb trace looks like free
replicas, and per sweep it never is: phase modulation conserves the total
signal but divides it among the teeth, and each tooth still sees the full
detector noise floor, so an RF-on sweep carries less width information
than the RF-off sweep it replaces. Where RF-on sweeps already exist as
calibration brackets, their information is marginal and free, and it
joins the same likelihood the science sweeps feed. The depth then splits
by the trace's job: a ruler trace goes deep, since spacing information climbs
with depth, and a trace meant for widths stays shallow or unmodulated.
Within one trace every tooth and every line shares a single detector
gain, so intra-trace height ratios are immune to gain drift that affects
ratios assembled across traces.

## Tooth heights between two limits, and where the crossovers go

The weights $J_s(2\beta)^2$ are an interference result, holding only when
every pathway to a tooth carries the same phase.

A tooth at sum offset $s$ is fed by every sideband pair $(n, s-n)$: the
carrier tooth by $(0,0)$, by $(+1,-1)$, by $(+2,-2)$, and so on. At zero
relative delay these pathways interfere, and their coherent sum is
$J_s(2\beta)$ by the Bessel addition theorem, so a carrier vanishes at
$2\beta = 2.405$ even though its crossover pathways still exist and
cancel. One photon of each pair comes from the retro beam, delayed
by $\tau(z)$ for an atom at $z$, so the pathway $(n, s-n)$ carries a phase
$(s-n)\Omega\tau$, and the sum collapses to a single tone at effective
depth $2\beta\cos(\pi f\tau)$. An atom shows weights
$J_s(2\beta\cos(\pi f\tau))^2$, and a cell shows their average.

Smearing $\tau$ across a cell undoes the cancellation: the $(k,-k)$ pairs
return to the carrier as added height, and the null at 2.405 fills in.
What matters is the phase $2\pi f\tau$: at a 12.5 MHz drive across a 10 cm
cell it is 0.05 rad and the zero-delay weights hold to two parts in a
thousand, while at 580 MHz it is order three, the effective depth sweeps
through zero, and a high-order tooth computed in the zero-delay limit can
be wrong by a factor of fifty.

Two escapes exist: modulate one arm only, between the cell and the retro
mirror, so each pathway carries a distinct order and the zero-delay
weights are exact at any drive, or stay at a drive low enough that the
phase is small, which the 12.5 MHz comb used here already does. Residual
amplitude modulation adds a separate, measured deviation on top of either
limit, the $\pm k$ height asymmetry the constants file documents.
`rb5s6s.forecast.comb_tooth_weights` computes both limits and the
average, tested against the explicit pathway sum.

## The comb and the atomic pairs divide the labour

An experiment with hyperfine structure carries a second ruler already:
two lines of the same isotope are separated by a combination of hyperfine
constants. The two rulers answer different needs.

The atomic pair is the anchor: absolute, needing no calibration of its
own, and sparse, two marks per isotope, far apart, saying nothing about
the axis between them, and immune at first order to a scalar light
shift, since both members move identically. The comb is the
interpolator: a mark every tooth spacing, exact against an RF
synthesiser, able to carry a per-block rate and a drift bound at
sub-second averaging times, and carrying no absolute frequency at all.

A third reading appears when the drive is set so an integer number of
tooth spacings equals the pair separation. The tooth of one line then
lands on the other line's carrier, both excited in the same millisecond,
and the pair stops being a ruler and becomes a measurable: the splitting
of the doublet reads the hyperfine separation against the synthesiser,
drift-free and light-shift-free, at whatever precision the line centres
support.

## What can go wrong

The first failure is a model one: reading the rate identity as a shape
identity. Because $\sum_k J_k(2\beta)^2$ equals one at every depth, the
comb can look costless, but the identity only says no two-photon events
are lost in aggregate. A width or an asymmetry compared tooth to tooth
draws on the much smaller $\sum_k J_k(2\beta)^4$, and nothing in a single
fit flags that the two totals answer different questions.

The second is a data-insufficiency failure created by the depth itself,
not the data: fixing $\beta$ at the carrier null fixes how many orders
carry usable power, so a session needing the ruler to reach further finds
the outer part of that span uncalibrated no matter how carefully the rest
of the fit is set up, and no choice of order recovers a reach the drive
frequency does not have.

The third is an implementation trap in the diagnostic itself. The
fourth-power weighting assumes each tooth's contribution to a shape
comparison is independent, photon-limited leverage, silently assuming the
teeth are not already distorted by whatever a forced-versus-free
amplitude residual would reveal, such as saturation compression. Reading
$\sum_k J_k(2\beta)^4$ as a
finished precision estimate before that residual is checked treats a
diagnostic built to test the Bessel law as though it already had the
answer.

The fourth is an experimental limitation. A resonant modulator runs
efficiently at one design frequency, and a comb spanning a wide range in
one sweep needs a different modulator or calibration channel, not a
deeper or shallower drive on the same device.

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
so one that stops working fails the suite instead of sitting here misleading
a reader.

## Further reading

- [EOM sidebands](eom-sidebands.md) for the derivation from Neumann's
  addition theorem, and the modulator design compromise the doubled
  argument forces.
- [Bessel functions](bessel-functions.md) for the Jacobi-Anger identity and
  the power-conservation identity the rate sum above is a special case of.
- [`../lit/bjorkholm1976.md`](../lit/bjorkholm1976.md), the closed-form
  two-photon absorption theory, for why a two-photon transition responds to
  the field as a pair of photons instead of one.
- [Information criteria](information-criteria.md) for the forced-versus-free
  comparison this repository's comb-as-instrument plan relies on.

## See also

- [EOM sidebands](eom-sidebands.md) for the derivation of the two-photon
  amplitude law this page treats as given.
- [Bessel functions](bessel-functions.md) for the Jacobi-Anger and
  power-conservation identities behind the rate and shape sums above.
- [Information criteria](information-criteria.md) for how the
  forced-versus-free tooth comparison is judged.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md)
  for how the comb's islands fit into the full frequency calibration.

---

[← EOM sidebands](eom-sidebands.md) · *Driving, modulating and detecting, 2 of 8* · [The wavemeter and the frequency axis →](the-wavemeter-and-the-frequency-axis.md)
