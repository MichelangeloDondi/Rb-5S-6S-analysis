# The beam waist

*[wiki index](README.md) · concept*

**The question.** What the beam waist is, why it stands between a measured
power and the intensity an atom feels, and how confidently this repository
knows its value.
**Takes.** Nothing beyond the idea of a focused beam, and no fitted data of
its own.
**Gives.** The waist's defining relations, its opposite-signed pull on the
light shift and the transit width, and the adopted value's provenance.
**Skip if.** You want what the waist does to the line shape rather than the
length itself, covered in [the AC-Stark shift](ac-stark-shift.md).

## What it is

A beam brought to a focus by a lens narrows to a minimum radius before
spreading out again. That minimum, $w_0$, is the beam waist, conventionally
the radius at which the on-axis intensity has fallen to $1/e^2$ of its peak.
The convention matters because a source stating a bare "beam diameter"
without naming it leaves a reader to guess between a radius and a diameter,
and between three different definitions of "edge".

The waist sets two other lengths through diffraction, not through any
property of the lens. The Rayleigh range,

$$z_R = \frac{\pi w_0^2}{\lambda}$$

is how far the beam travels before its radius grows appreciably beyond
$w_0$, and beyond that range the beam spreads at the far-field divergence
half-angle $\theta \approx \lambda/(\pi w_0)$. Multiplying the two
definitions together gives $w_0\theta = \lambda/\pi$, a fixed product: a
tighter focus always buys a shorter working distance and a wider spray
angle, in the same measure. No lens design escapes that trade, because it is
a statement about waves, not about glass.

The waist is also the step that converts a number a power meter can read
into a number that governs light-matter interaction. For a single pass of
power $P$, the on-axis peak intensity at the waist is

$$I_0 = \frac{2P}{\pi w_0^2}$$

Power is easy to measure and calibrate. Intensity is what an atom actually
responds to, and $w_0$ is the one length that stands between them.

Two standard instruments measure it directly. A knife-edge scan translates a
blade across the beam at several positions along its axis and fits the
transmitted-power transition at each position, an integrated measurement
that recovers $w(z)$ and, through it, $w_0$ and $z_R$ in absolute power
units. A camera scan images the transverse intensity profile directly
through the same axial range and fits a two-dimensional profile at each
position, a spatially resolved measurement that additionally recovers shape:
ellipticity, astigmatism, and whether the profile is Gaussian at all. The two
answer different questions and, run together, check each other.

## What problem it solves

Because $I_0 \propto 1/w_0^2$, the waist is not passive bookkeeping. It is a
multiplier on every intensity-dependent quantity, and different quantities
carry different powers of it, so the same fractional uncertainty on $w_0$
propagates by different amounts and even in different directions depending
on what is being computed.

The light shift is linear in intensity, so it runs as $1/w_0^2$. The
two-photon signal is quadratic in intensity, because it takes two photons
acting together, so it runs as $1/w_0^4$. A saturation parameter built from
the same two-photon coupling carries the same quadratic dependence and runs
as the fourth power of the inverse waist as well, which is the reason a
tighter focus stops paying off in signal before it stops paying off in
shift: the safe, unsaturated regime narrows faster than the square-law gain
grows. Transit time runs the other way. An atom crossing a beam of waist
$w_0$ at thermal speed $v$ spends a time of order $w_0/v$ inside it, so a
bigger waist means a longer transit and a *narrower* transit-broadened
width, the opposite sign to what a bigger waist does to intensity.

As illustration, and only as illustration: a five percent error on $w_0$
becomes roughly a ten percent error on the light shift and roughly a twenty
percent error on the two-photon signal or its saturation parameter, while it
moves the transit width by about five percent in the other direction. One
length, four different exponents and at least one sign flip. That is why an
unresolved waist dominates the propagated uncertainty of a spectroscopy
campaign built around a focused two-photon beam far more than its own
fractional size would suggest.

## Where this repository uses it

[`rb5s6s/constants.py`](../../rb5s6s/constants.py) holds `W0_MEASURED_M` and
`W0_BAND_M`, the adopted central value and the working band every
$w_0$-dependent quantity in the package reads from, so the band is never
hand-typed downstream. The status recorded there, and repeated plainly here,
is that this waist is ADOPTED, not MEASURED on this bench. It was measured
once, on this apparatus lineage, in the configuration [Nieddu
2019](../lit/nieddu2019.md) describes: the same focusing lens, the same
focal length, the same retro-reflecting geometry this campaign uses, stated
with its $1/e^2$ convention. [Rajasree 2020](../lit/rajasree2020thesis.md)
reprints the same number rather than adding a second, independent reading.
The laser is not the same laser, and five years separate the two benches, so
the value is a transfer across apparatus rather than a reading off the beam
this dataset was collected with. Two known effects, residual clipping at a
narrow downstream aperture and imperfect overlap of the retro-reflected
beam, both push the effective waist above the transferred value on this
bench, which is why the band leans high of the central number rather than
sitting symmetric around it. This is the repository's largest open
systematic.

[`docs/big_picture/04_what-2025-delivered.md`](../big_picture/04_what-2025-delivered.md)
reports what the 2025 archive did with the adopted value and its band, and
how the light-shift bound compares with the prediction it produces.
[`docs/plan/03_optics-protocol.md` section
4.2](../plan/03_optics-protocol.md#42-two-instruments-for-the-waist)
specifies the two instruments described above, a knife-edge stage and a
camera, as the pair of measurements the next session runs to replace the
adopted value with one measured on this bench, cross-checked against each
other and against the geometric relation $z_R = \pi w_0^2/\lambda$ as a
third, independent ruler.

The two effects the waist sets the scale for each have their own page: [the
AC-Stark shift](ac-stark-shift.md) for the light shift the waist converts
power into, and [transit-time broadening](transit-time-broadening.md) for
the width that runs the opposite way with the same number. The fourth-power
saturation dependence is worked through in
[`docs/GLOSSARY.md`](../GLOSSARY.md) and in [the saturation
companion](../notes/two_photon_saturation_companion.md).

## What can go wrong

The commonest error is a convention trap rather than a measurement error: a
source states a beam "diameter" without saying $1/e^2$, or states a $1/e^2$
diameter that a reader halves incorrectly, or reads a $1/e$ width where a
$1/e^2$ width was meant. Each is a factor of two, or worse, hiding inside a
single unlabelled adjective, and it costs nothing to check because the
convention is always stated somewhere in the source, once someone looks.

A second is a model failure: treating an ADOPTED value as though it carried
the confidence of a value MEASURED on the bench in question. A transferred
number can be the right thing to use, and often is, but every quantity
computed from it inherits the transfer's own uncertainty on top of whatever
band the number is quoted with, and dropping that extra step understates
every downstream result.

A third is a data-insufficiency point specific to inferring $w_0$ from a
fitted line rather than measuring it directly: the transit width and the
laser width both broaden the same line and trade against each other in a
fit, so a spectroscopic line alone under-determines the waist that produced
its transit contribution. Only an external, spatially resolved measurement
of the beam settles it.

Fourth, an instrument trap, and the reason the two standard measurements are
run together rather than singly. A knife-edge integrates away the beam's
two-dimensional shape, so a clipped or structured profile can fit an
error-function transition acceptably and return a confidently wrong waist.
A camera keeps the shape but struggles at the opposite end: a small spot is
undersampled by the pixel grid, and the same sensor gain that keeps the peak
off saturation loses exactly the faint wings a power-based measurement
needs. Neither instrument is trustworthy alone, and agreement between the
two, and with the geometric $z_R$ relation, is the actual check.

Fifth, a drift trap: a directly measured waist can still move between the
day it was measured and the day data is taken, if a lens position creeps.
Because intensity depends on the waist quadratically, a small mechanical
shift moves every intensity-dependent number by more than it moves a
caliper reading, which is why lens separations are worth checking at setup
and at teardown rather than trusted for the length of a campaign.

## Try it

`rb5s6s.constants` holds the adopted waist and its working band. Since
intensity runs as $1/w_0^2$, walking across the band shows directly how much
the light-shift prediction moves for a fixed power.

```python
from rb5s6s.constants import W0_MEASURED_M, W0_BAND_M, RHO_RETRO
from rb5s6s import stark_shift_S0_mhz

power_w = 0.225  # 225 mW, the top of the 2025 campaign's power sweep
w0_lo, w0_hi = W0_BAND_M

print("rb5s6s.constants.W0_MEASURED_M and W0_BAND_M:")
for label, w0 in (("band low", w0_lo), ("adopted", W0_MEASURED_M),
                  ("band high", w0_hi)):
    intensity_ratio = (W0_MEASURED_M / w0) ** 2
    s0_mhz = stark_shift_S0_mhz(power_w, w0, rho=RHO_RETRO)
    print(f"  {label:>9}: w0 = {w0 * 1e6:5.1f} um   "
          f"I / I(adopted) = {intensity_ratio:6.3f}   "
          f"S0(225 mW) = {s0_mhz:.4f} MHz")
print("intensity and the light shift both run as 1/w0^2: the same band "
      "moves both by the same fraction")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## What this repository got wrong, twice

The waist this page states did not arrive as one number.
[HISTORY.md](../HISTORY.md) records the design value at 32 µm, excluded
once the transit Monte Carlo's own crossing-flux weighting for atoms
crossing the beam was found missing, the same implementation trap
[transit-time broadening](transit-time-broadening.md) names in its "What
can go wrong" section. A separate note, carrying an unrelated
factor-of-two arithmetic error, had put the figure at roughly 90 µm before
2026-07-13 and was retracted outright. Fixing the Monte Carlo on
2026-07-13, and validating it against Lehmann's 41.2 kHz worked example,
moved the figure to roughly 50 µm. Rajasree 2020's direct measurement on
the same laser then replaced that Monte-Carlo estimate with the 64 µm
value this page calls ADOPTED, on 2026-08-01, still open.

A second failure came from trusting repetition over provenance rather than
from a bad number. A stand-in figure of 60 µm, chosen before the waist was
stated as measured, was written into three forward-looking documents,
while the correct 64 µm figure sat in a fourth. On 2026-08-15 a
consistency sweep counted the three against the one and edited the page
that was right. HISTORY.md states the lesson outright: "Corroboration
between documents is not independent evidence when they share an
ancestor." A reader who asked where each of the three 60 µm documents got
its number, rather than counting how many agreed, would have caught the
retraction before the sweep needed to.

## Further reading

- [`../lit/nieddu2019.md`](../lit/nieddu2019.md), the paper measuring the
  beam diameter this repository's adopted waist is read from.
- [`../lit/rajasree2020thesis.md`](../lit/rajasree2020thesis.md), the thesis
  that reprints the same measurement rather than adding an independent one.
- A. E. Siegman, *Lasers*, University Science Books (1986), the standard
  reference for Gaussian-beam propagation, the Rayleigh range and the
  divergence relation used above.
- [The AC-Stark shift](ac-stark-shift.md) for the effect the waist sets the
  scale of.
- [Transit-time broadening](transit-time-broadening.md) for the width that
  depends on the same length with the opposite sign.

## See also

- [The campaign page](../quantities/campaign.md), where the waist is the hub
  of the coupled system and the beam profile is the cheapest entry into the
  whole programme.
- [The AC-Stark shift](ac-stark-shift.md) for the shift distribution this
  length's intensity feeds directly.
- [Saturation](saturation.md) for the fourth-power waist dependence that sets
  the safe operating regime.
- [Sensitivity analysis](sensitivity-analysis.md) for how much a projection
  actually moves when an input like the waist is varied.

---

[← Transit-time broadening](transit-time-broadening.md) · *Experimental spectroscopy, 5 of 9* · [The AC-Stark shift →](ac-stark-shift.md)
