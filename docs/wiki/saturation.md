# Saturation

*[wiki index](README.md) · physical effect*

**The question.** Where the two-photon I-squared law this analysis leans on
stops holding, and what that costs a tightly focused beam.
**Takes.** The two-photon Rabi frequency and the natural linewidth, and no
fitted data of its own.
**Gives.** The saturation parameter, its fourth-power waist scaling, and the
size of the bound available if a saturation term is folded into the fit.
**Skip if.** You want the light shift itself. That is covered in
[the AC-Stark shift](ac-stark-shift.md). This page covers the ceiling on the
drive that produces it.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A two-photon transition absorbs two photons at once: the excitation
amplitude scales with the square of the field, the rate with the square of
the intensity. At low drive this I-squared law is exact, doubling the
intensity quadruples the signal. It is also why a two-photon signal weights
a beam's bright core over its dim wings, feeding the
[AC-Stark shift](ac-stark-shift.md) page's calculable, asymmetric shift
distribution.

![Two EOM comb shapes at different modulation depths](figures/wiki_eom_comb.png)

*Two comb shapes at different modulation depths. The ladder separates
saturation-driven compression from a genuine Bessel pattern.*

The law cannot hold without limit: an atom already excited cannot be excited
again until it decays, so the excited-state population approaches a ceiling
as the drive strengthens. The saturation parameter $s$, proportional to the
square of the two-photon Rabi frequency over the square of the natural
linewidth, measures proximity to that ceiling. The steady-state excited
fraction follows $s/(2(1+s))$, reducing to the I-squared law at small $s$ and
flattening toward one half as $s$ grows.

Because the two-photon coupling scales with intensity, $s$ scales with
intensity squared, and intensity at fixed power scales as the inverse square
of the spot size: $s$ grows as the inverse fourth power of the spot size,
while a linear effect such as the light shift grows only as the inverse
square. Halving the spot size quadruples the light shift but multiplies $s$
by sixteen. A tighter focus therefore leaves the weak-field regime, where
every I-squared argument in this analysis holds cleanly, twice as fast in
logarithmic terms as its signal grows, since the saturation parameter's
exponent is double the intensity's.

The same law governs a phase-modulated drive: [EOM sidebands](eom-sidebands.md)
stamp a comb onto the light, and the tooth amplitude at order $k$ follows a
[Bessel](bessel-functions.md) law, $J_k(2\beta)^2$ in the modulation depth
$\beta$. That law is a weak-field statement in its own right: it assumes
every pair of sidebands drives the atom independently and additively.
Saturation compresses it asymmetrically: the strongest teeth sit
nearest the excited-state ceiling, the weakest barely move it, so a
saturating comb reads out with its strong teeth pulled toward its weak ones.

## What problem it solves

It sets the boundary of validity for every I-squared argument this analysis
makes, from the light-shift distribution to a modulation comb's amplitude
pattern, and gives that boundary a number instead of a guess. It also turns
the comb's amplitude law from an assumption into a checkable claim, by
driving the modulator at more than one depth and testing whether the law
holds at all of them.

## Where this repository uses it

The weak-field limit and its cost are discussed in
[BIG_PICTURE, the method and its limits](../big_picture/02_the-method-and-its-limits.md),
with the committed panel at [fig24](../../figures/fig24_weak_field_limit.png).
[`two_photon_rabi_hz`](../../rb5s6s/hyperpolarizability.py) computes the
two-photon coupling from bench quantities, compared against
[`GAMMA_NAT_HZ`](../../rb5s6s/constants.py) using the measured waist
[`W0_MEASURED_M`](../../rb5s6s/constants.py). The
[`stark_ramp`](../../rb5s6s/lineshape.py) docstring states the same caveat
and points at `scripts/run_saturation_probe.py`, which measures the
light-shift tightening from a saturation term, detailed in
[`docs/notes/two_photon_saturation_companion.md`](../notes/two_photon_saturation_companion.md).

![Fitted width response against drive power showing saturation departure from the square law](../../figures/fig24_weak_field_limit.png)

*The committed weak-field panel: fitted width response against drive power,
with the saturating departure from the square law.*

The comb side of the same physics has been planned but not yet run.
[The fixed-lock instrument, section 10c.10](../plan/10_the-fixed-lock-instrument.md)
proposes fitting every comb twice, once with tooth amplitudes forced to the
Bessel law and once free, reading the residual as the saturation and
depletion diagnostic. It runs the modulator at several depths so the
amplitude law is tested at more than one point.

## What can go wrong

The first failure is a model one: treating the I-squared law, or the pure
Bessel comb it implies, as exact instead of the small $s$ limit it is.
A model that omits saturation returns a plausible answer regardless of
drive strength.

The second is data insufficiency that can look like a clean result: a
forced-versus-free comparison at one modulation depth can come back
indistinguishable from a genuine Bessel pattern when the teeth are not
resolved tightly. Only a ladder across depths converts a quiet residual
into an actual test.

The third is an implementation trap: using the one-photon Rabi frequency
where the two-photon coupling belongs, or the on-axis $s$ where a broadening
or comb prediction needs the beam-averaged, signal-weighted value. The two
differ by roughly a factor of two in this apparatus's geometry, and either
mistake changes the weak-field verdict.

The fourth concerns the formula itself. $\Gamma \to \Gamma\sqrt{1+s}$ is
standard for a two-level atom driven near resonance. Applied here with a
two-photon Rabi frequency, it is carried over by analogy, not derived for
this apparatus's real cascade of hyperfine levels. No committed bound
currently depends on it.

## Try it

The fourth-power waist scaling, and the power at which a saturating
two-photon rate departs from the naive square law by a stated percentage.

```python
import numpy as np
from rb5s6s import (GAMMA_NAT_HZ, W0_MEASURED_M, stark_shift_S0_mhz,
                    two_photon_rabi_hz)

def saturation_parameter(power_w, w0_m):
    omega_hz = two_photon_rabi_hz(power_w, w0_m)
    return 2.0 * (omega_hz / GAMMA_NAT_HZ) ** 2

power = 0.225  # W, one reference point on this bench
w_wide, w_tight = W0_MEASURED_M, W0_MEASURED_M / 4.0
shift_ratio = stark_shift_S0_mhz(power, w_tight) / stark_shift_S0_mhz(power, w_wide)
sat_ratio = saturation_parameter(power, w_tight) / saturation_parameter(power, w_wide)
print(f"waist tightened 4x: the light shift grows {shift_ratio:.1f}x (4^2 = 16), "
      f"the saturation parameter grows {sat_ratio:.1f}x (4^4 = 256)")

powers = np.geomspace(1e-3, 4.0, 4000)
s = np.array([saturation_parameter(p, w_wide) for p in powers])
departure = s / (1.0 + s)          # true rate vs. the small-s square-law rate
for target in (0.01, 0.05, 0.10):
    i = np.searchsorted(departure, target)
    print(f"the square law is wrong by {target:.0%} at P = {powers[i] * 1e3:.0f} mW"
          f" (s = {s[i]:.3f})")
```

## The P-squared family

Saturation broadening at small $s$ grows as the drive intensity, and for a
two-photon line that intensity grows as the power squared. The AC-Stark
ramp broadens as the shift squared, also power squared, and hyperfine
pumping rides the excitation rate, power squared again. A measured width
rising quadratically with power identifies none of them: a fit offered only
the width channel hands the family to whichever member it was allowed to
vary.

Separating them needs channels with different parities: the shift channel
is linear in power where all three widths are quadratic, the saturation
member alone bends the amplitude law away from power squared, and the
pumping member alone shifts amplitude ratios between hyperfine components.
This is the [reversal tests](reversal-tests.md) discipline applied to a
power law: a light-shift bound from the width channel is conditional on
which family members the forward model carried.

## The companion calculation

No committed bound has moved on this calculation, detailed in
[`docs/notes/two_photon_saturation_companion.md`](../notes/two_photon_saturation_companion.md).
Folding the homogeneous saturation increment into the forward model, using
the two-photon Rabi frequency `scripts/run_saturation_probe.py` rebuilds
from bench quantities, the width-channel bound $S_0$(225 mW) tightens from
the committed 0.6325 MHz to about 0.23 MHz, a factor of 2.8. This matches
the first failure above: the ramp-only fit rails at $\kappa = 0$ because its
width response has no gradient there until the saturation term supplies one.

The bound has not moved in any committed result. The injected law,
$\Gamma \to \Gamma\sqrt{1+s}$ built from the two-photon Rabi frequency, is
the standard two-level steady-state form carried over by analogy, not
derived for this apparatus's real cascade of hyperfine levels, the same
caveat as above. The factor of 2.8, and the factor of 2.21 the note records
for the joint-fit analogue, are conservative estimates that have not
changed the committed number.

## Further reading

- [`../lit/bjorkholm1976.md`](../lit/bjorkholm1976.md), the closed-form
  theory behind the I-squared law and its saturation.
- [`../lit/steck_rb.md`](../lit/steck_rb.md), the reference for natural
  linewidths and saturation formulas.
- [EOM sidebands](eom-sidebands.md) and [Bessel functions](bessel-functions.md)
  for the comb and the law it follows.
- [The AC-Stark shift](ac-stark-shift.md) for the effect the fourth-power
  scaling contrasts against.

## See also

- [The AC-Stark dossier](../quantities/ac-stark-light-shift.md), where
  saturation shares the light shift's power law with the mechanisms the
  width channel cannot separate.
- [The beam waist](the-beam-waist.md) for the length whose fourth power the
  spot-size argument turns on.
- [EOM sidebands](eom-sidebands.md) and [Bessel functions](bessel-functions.md)
  for the comb and the amplitude law saturation is tested against.
- [Identifiability](identifiability.md) for what it takes to tell a
  saturation term apart from the model's other mechanisms.

---

[← The inhomogeneous light shift](the-inhomogeneous-light-shift.md) · *Experimental spectroscopy, 8 of 11* · [Collisional self-broadening →](self-broadening.md)
