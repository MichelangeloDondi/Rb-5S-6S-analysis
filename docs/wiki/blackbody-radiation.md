# Blackbody radiation

*[wiki index](README.md) · physical effect*

**The question.** Whether the cell's own thermal glow drives or shifts the 5S
to 6S cascade, and by how much.
**Takes.** The cascade's transition wavelengths and the cell temperature, and
no fitted data of its own.
**Gives.** The two blackbody peaks and why they rarely matter here, plus the
one channel and the one shift that do.
**Skip if.** You want the light shift from the drive laser itself rather than
from the cell's own thermal field, covered in
[the AC-Stark shift](ac-stark-shift.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Any object at temperature $T$ glows. The spectrum of that glow is set by
temperature alone, and the quantity that matters for atoms is not the power
but the mean number of photons per mode,

$$\bar n(\nu) = \frac{1}{e^{h\nu/k_BT}-1}$$

which is the Bose-Einstein occupation number. It is the number an atom
responds to, because a stimulated rate is proportional to it.

Two regimes follow, and almost every practical question is decided by which
one a transition sits in. Where $h\nu \ll k_BT$ the exponential can be
expanded and $\bar n \approx k_BT/h\nu$, a large number: the mode is
thermally crowded. Where $h\nu \gg k_BT$ the occupation collapses as
$e^{-h\nu/k_BT}$, and the collapse is violent, because the exponent is
linear in frequency. At 400 K the thermal energy $k_BT$ corresponds to a
wavelength near 36 µm.

WHICH PEAK IS QUOTED MATTERS, and the two differ by a quarter. The familiar
Wien displacement law, $\lambda T = 2898$ µm K, locates the peak of the
spectrum of ENERGY per unit wavelength. The peak of the PHOTON NUMBER per
unit wavelength sits at $\lambda T = 3670$ µm K, because dividing the energy
density by the photon energy shifts the maximum. At 400 K those are 7.2 µm and
9.1 µm. A transition at 1 µm sits far out on the exponential tail of either,
and its occupation number is smaller by ten or more orders of magnitude than
one near the peak, which is why the distinction rarely changes a conclusion
even though it changes the number.

Blackbody light does two distinct things to an atom. It drives transitions,
at a rate proportional to $\bar n$ times the spontaneous rate, which
redistributes population. And it shifts levels, because the thermal field is
an oscillating electric field like any other and produces an AC-Stark shift
proportional to the differential polarizability and to the mean squared field
$\langle E^2\rangle \propto T^4$. The two effects have different sizes and
different consequences, and a transition can be immune to one and not the
other.

## What problem it solves

It does not solve a problem, it creates one, and the useful move is to bound
it. In precision spectroscopy the blackbody shift is often the largest
uncontrolled systematic, because a cell or a trap has a temperature and the
$T^4$ scaling is steep. Knowing where a transition sits relative to the
thermal peak tells you in advance whether it can be ignored, which is worth
more than measuring it afterwards.

## Where this repository uses it

The cell runs at 70 to 130 °C, so it sits inside its own glow, and
[methods chapter 4](../methods/04_the_composite_model.md) asks the two
questions separately for the 5S to 6S cascade. Both are computed by
[`scripts/run_blackbody_channels.py`](../../scripts/run_blackbody_channels.py).

One comparison decides most of it. At 403 K the thermal peak is at 7.2 µm by
energy and 9.1 µm by photon number, while every line of the cascade lies
between 0.79 and 2.8 µm, so the cascade lives on the exponential tail of
either. The rates below do not depend on which peak is quoted, because they
are computed from $h\nu/k_BT$ line by line. Blackbody light does not re-drive 5P to 6S:
the occupation numbers are around $10^{-12}$ on the infrared legs, which is
$10^{-8}$ of a channel that is itself one per cent. And it does not reach the
795 nm signal, where the blocking element turns out to be the photocathode's
own red edge rather than the interference filters.

Two things survive that argument and the chapter records both. The one real
blackbody channel is 6S to 6P near 2.73 and 2.79 µm, close enough to the peak
that the occupation number is about $2\times10^{-6}$, leaking two parts per
million out of the detected cascade. And the blackbody AC-Stark shift is
hundreds of hertz rather than the order of one hertz the ground state alone
would give, because the differential polarizability is large and the 6S
resonances sit inside the thermal band. It shifts the line and does not
broaden it, which is why it cannot reach the width results this repository
reports.

## The campaign boundary it sets

`rb5s6s/blackbody.py` turns this into a design number. The deliverable is not
"blackbody is included" but a FAMILY,

    T_max(target precision),

the temperature above which thermal radiation enters the systematic budget at
a given target, with two branches. UNCORRECTED, where a campaign does not
subtract the shift, the ceiling is where the shift itself reaches the target.
CORRECTED, where it computes and subtracts it, only the shift's own
uncertainty remains and the ceiling is far higher. The gap between the two is
the value of doing the correction.

For this experiment the answer is that **the boundary is not binding**. Across
the cell's 70 to 130 C range the differential shift runs 79.9 to 161.0 Hz,
four orders of magnitude below the light-shift bound the record quotes, and
even a campaign chasing one kilohertz has an uncorrected ceiling near 340 C,
far above any vapour cell this experiment would use. The temperature lever is
limited by the oven and the cell, not by thermal radiation.

One detail is worth carrying, because using the naive scaling would err in the
unsafe direction. A pure quadratic Stark shift in a thermal field scales as
the fourth power of temperature. The measured shift scales as **T to the
4.35**, the excess being the near-resonant 6S to 6P contribution whose weight
grows with temperature, so a model using four understates the shift where a
ceiling matters most.

## What can go wrong

The commonest modelling error is to reason from the POWER spectrum, whose
peak sits at a different wavelength from the photon-number peak, and then to
place a transition on the wrong side of it. Occupation number is the quantity
an atomic rate is proportional to, and it is the one to plot. The first draft
of the section above made exactly this mistake, quoting the Wien energy peak
and calling it the photon peak, which is how easily it happens.

The second is to assume a single temperature. The relevant temperature is
that of the surfaces the atom actually sees, and a cell with a cold window, a
warm oven and a room-temperature viewport has no single $T$. A quoted
blackbody shift is only as good as the assumed enclosure, which is an
experimental limitation rather than a calculational one.

The third is to bound the driving and then assume the shift is bounded too.
They scale differently. A transition can be utterly immune to blackbody
driving, because its occupation number is $10^{-12}$, and still carry a
measurable blackbody shift, because the shift sums over ALL levels the state
couples to and is dominated by whichever resonance lies nearest the thermal
band. That is exactly what happens here.

## Try it

Both peaks, from their own displacement constants, and the occupation numbers
of three lines of this cascade.

```python
import numpy as np
from scipy.optimize import brentq

h, c, k = 6.62607015e-34, 2.99792458e8, 1.380649e-23
c2 = h * c / k * 1e6
x_energy = brentq(lambda x: 5 * (1 - np.exp(-x)) - x, 1e-6, 20)
x_photon = brentq(lambda x: 4 * (1 - np.exp(-x)) - x, 1e-6, 20)
T = 403.15
print(f"at {T - 273.15:.0f} C the peak is at")
print(f"  {c2 / x_energy / T:5.2f} um by energy        ({c2 / x_energy:.0f} um.K)")
print(f"  {c2 / x_photon / T:5.2f} um by photon number ({c2 / x_photon:.0f} um.K)")
for lam in (0.795, 1.324, 2.73):
    print(f"  {lam:5.3f} um: occupation {1 / np.expm1(c2 / (lam * T)):.2e}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/safronova2004.md`](../lit/safronova2004.md) for the dynamic
  polarizabilities a blackbody shift is computed from.
- W. M. Itano, L. L. Lewis and D. J. Wineland, "Shift of $^2S_{1/2}$ hyperfine
  splittings due to blackbody radiation", *Phys. Rev. A* **25**, 1233 (1982),
  the paper that put the effect on the map for frequency standards.
- [Wikipedia: Planck's law](https://en.wikipedia.org/wiki/Planck%27s_law) for
  the spectrum and its two limits.

## See also

- [The AC-Stark shift](ac-stark-shift.md) for the other source of level shift
  acting on the same states, driven by the beam rather than by the cell.
- [Hyperfine populations and branching](hyperfine-populations-and-branching.md)
  for the population bookkeeping a driving channel like this one feeds into.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md)
  for another background effect that has to be bounded rather than measured
  away.

---

[← Bessel functions](bessel-functions.md) · *Driving, modulating and detecting, 8 of 8* · [wiki index →](README.md)
