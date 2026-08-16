# Saturation

*[wiki index](README.md) · physical effect*

## What it is

A two-photon transition is driven by absorbing two photons at once, so the
excitation amplitude scales with the square of the field and the excitation
rate scales with the fourth power of the field, that is, with the square of
the intensity. At low drive that I-squared law is the whole story: doubling
the intensity quadruples the signal. It is also the reason a two-photon
signal weights the bright core of a focused beam so much more heavily than
its dim wings, which is what lets the [AC-Stark shift](ac-stark-shift.md)
page turn a beam profile into a calculable, asymmetric shift distribution.

The law cannot hold without limit. An atom already sitting in the excited
state cannot be excited again until it decays, so the excited-state
population approaches a ceiling as the drive strengthens rather than growing
forever. The dimensionless SATURATION PARAMETER, conventionally written $s$,
measures how close the drive sits to that ceiling. It is proportional to the
square of the coupling strength, the two-photon Rabi frequency, over the
square of the natural linewidth. The steady-state excited fraction then
follows the standard two-level form $s / (2(1+s))$, which reduces to the
I-squared law when $s$ is small and flattens toward one half as $s$ grows,
the atom now spending as much time excited as decay allows.

Because the two-photon coupling itself scales with intensity, $s$ scales with
the square of intensity, and intensity at fixed input power scales as the
inverse square of the focused spot size. Combining those two facts is the
scaling that governs beam design: $s$ grows as the inverse FOURTH power of
the spot size, while a first-order effect that is only linear in intensity,
such as the light shift, grows as the inverse square. Halving the spot size
doubles the light shift's reach but multiplies the saturation parameter by
sixteen. A tighter focus therefore leaves the weak-field regime, where every
I-squared argument in this analysis holds cleanly, twice as fast in
logarithmic terms as it gains signal.

The same law governs a phase-modulated drive. [EOM sidebands](eom-sidebands.md)
stamp a comb of copies of the line onto the light, and in a two-photon
transition the amplitude of the tooth at order $k$ follows a
[Bessel](bessel-functions.md) law, $J_k(2\beta)^2$ in the modulation depth
$\beta$. That law is a weak-field statement in its own right: it assumes every pair of
sidebands drives the atom independently and additively. Saturation breaks
that assumption asymmetrically, because the strongest teeth push the atom
closest to its excited-state ceiling while the weakest barely move it, so a
saturating comb reads out with its strong teeth compressed toward its weak
ones relative to the pure Bessel prediction. A single comb, at one drive
depth, cannot tell a genuine Bessel pattern apart from a compensated
deviation from it. A LADDER of modulation depths can, because it changes
which teeth carry the strong amplitude and checks that the law holds at
every rung rather than assuming it holds at one.

## What problem it solves

It sets the boundary of validity for every I-squared argument this analysis
makes, from the shape of the light-shift distribution to the amplitude
pattern of a modulation comb, and it gives that boundary a number rather than
a guess. It also turns the comb's amplitude law from an assumption a fit
takes on trust into a claim a session can check, by driving the modulator at
more than one depth and asking whether the same law fits all of them.

## Where this repository uses it

The weak-field limit and its cost are discussed in
[BIG_PICTURE, the method and its limits](../big_picture/02_the-method-and-its-limits.md),
with the committed panel at
[fig24](../../figures/fig24_weak_field_limit.png). The public function that
computes the two-photon coupling from bench quantities is
[`two_photon_rabi_hz`](../../rb5s6s/hyperpolarizability.py), the natural
linewidth it is compared against is
[`GAMMA_NAT_HZ`](../../rb5s6s/constants.py), and the measured beam waist that
sets the intensity is [`W0_MEASURED_M`](../../rb5s6s/constants.py). The
[`stark_ramp`](../../rb5s6s/lineshape.py) docstring states the same
weak-field caveat for the light-shift distribution and points at
`scripts/run_saturation_probe.py`, the script that measures how much a
saturation term would tighten the light-shift bound if it were folded into
the fitted model, a companion argument worked out in full in
[`docs/notes/two_photon_saturation_companion.md`](../notes/two_photon_saturation_companion.md).

The comb side of the same physics is planned rather than run yet.
[The fixed-lock instrument, section 10c.10](../plan/10_the-fixed-lock-instrument.md)
proposes fitting every comb twice, once with the tooth amplitudes forced to
the Bessel law and once with each tooth free, and reading the AMPLITUDE
residual between the two as the saturation and depletion diagnostic. The
session grammar it specifies runs the modulator at several depths for exactly
the reason above, so the amplitude law is tested at more than one point
rather than assumed at the single depth a session happens to use.

## What can go wrong

The first failure is a model one: treating the I-squared law, or the pure
Bessel comb it implies, as exact rather than as the limit it holds in at small $s$ for a
saturating response. Nothing in a single fit announces that the assumption
has been made, so a model that omits saturation entirely returns a plausible
answer whether or not the drive is actually weak.

The second is data insufficiency dressed as a clean result. A forced-versus-free
comparison at one modulation depth can come back statistically indistinguishable
even when real saturation is present, if the individual teeth are not resolved
well enough to constrain their amplitudes tightly. A quiet residual at one depth
is not evidence that the weak-field regime holds. Only a ladder across depths,
which changes which teeth carry the strong amplitude, converts silence at a
single setting into an actual test of the law.

The third is an implementation trap of the kind the [EOM sidebands](eom-sidebands.md)
page also warns about: computing the saturation parameter from the ONE-photon
Rabi frequency where the two-photon coupling belongs, or quoting the on-axis
value of $s$ where the beam-averaged, signal-weighted value is the one that
matters for a broadening or a comb prediction. The two differ by roughly a
factor of two in this apparatus's geometry, and either mistake changes the
conclusion about whether a configuration is safely weak-field.

The fourth is an experimental limitation stated plainly rather than smoothed
over. The two-level formula $\Gamma \to \Gamma\sqrt{1+s}$ used throughout this
page is standard practice for a two-level atom driven near resonance. Applied
here with a two-photon Rabi frequency, it is an approximation carried by
analogy rather than a law derived for this apparatus's real cascade of
hyperfine levels, and no committed bound in this repository is adjusted on
the strength of it alone.

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

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/bjorkholm1976.md`](../lit/bjorkholm1976.md), the classic closed-form
  theory of two-photon absorption strength and lineshape, the setting the
  I-squared law and its saturation both come from.
- [`../lit/steck_rb.md`](../lit/steck_rb.md), the standard compilation this
  repository draws its natural linewidths and two-level saturation formulas
  from.
- [EOM sidebands](eom-sidebands.md) for the comb the amplitude law is tested
  on, and [Bessel functions](bessel-functions.md) for the law itself.
- [The AC-Stark shift](ac-stark-shift.md) for the first-order effect this
  page's fourth-power scaling is contrasted against.

---

[← The AC-Stark shift](ac-stark-shift.md) · *Experimental spectroscopy, 7 of 8* · [Collisional self-broadening →](self-broadening.md)
