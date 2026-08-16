# Standing waves

*[wiki index](README.md) · physical effect*

## What it is

Retro-reflecting a laser beam back through itself sends two waves of the
same frequency through the same volume in opposite directions. Their
superposition does not travel. At each point the two fields add with a
phase that depends on position, so the total intensity is fixed in space
rather than sweeping through it: bright antinodes and dark nodes, spaced at
half the optical wavelength. The half comes from the round trip, not from
the reflection alone. A single forward wave has phase $kz$, the returning
wave has phase $-kz$, and their difference advances by $2k$ per unit
length, so the pattern repeats every $\lambda/2$, twice as often as either
wave would alone.

An atom moving through that pattern can be in either of two regimes,
and which one applies is a question of timescale, not of geometry. A slow
or nearly transverse atom crosses a negligible fraction of one fringe
during the time it takes to respond to the light, so it sits at
essentially one point of the standing wave and reads whatever intensity is
there. That is FRINGE-RESOLVED: the atom's response depends on where in
the fringe it happens to be, and an ensemble of such atoms carries the
fringe's spatial structure into the signal. A fast axial atom instead
sweeps through many fringes within that same response time, so what
reaches the atom is a rapid modulation about a well-defined mean, and to
lowest order only the mean survives. That is FRINGE-AVERAGED. The two
limits bracket every real ensemble, which is always a thermal mixture of
transverse and axial motion, and the fraction that falls into each regime
is set by the ratio of the fringe-crossing rate to the atom's response
rate.

A second, independent question is how much power actually comes back. The
RETRO RATIO is the fraction of forward power returned to the atoms after
every loss along the retro path, mirror reflectivity, window and lens
passes, and imperfect overlap between the outgoing and returning modes.
It is a number between zero and one for any real retro-reflector, one
only in the lossless, perfectly mode-matched limit.

The retro ratio matters beyond the fringe contrast because a
counter-propagating geometry drives two-photon absorption through two
distinct channels. An atom can take one photon from the forward beam and
one from the backward beam, a CROSS TERM whose rate scales with the
product of the two intensities. Because the two photons travelling in
opposite directions carry opposite first-order Doppler shifts, this
channel cancels the atom's velocity and produces the narrow,
Doppler-free line. Or an atom can take both photons from the same beam,
a SAME-BEAM term whose rate scales with the square of that beam's own
intensity. Both photons then carry the same first-order Doppler shift,
nothing cancels, and the ensemble produces a broad, Doppler-BROADENED
pedestal underneath the narrow line. Both channels are driven by the
same two beams, so their relative strength depends on nothing but how
those two intensities compare, which is exactly what the retro ratio
measures. The ratio of the two channels' areas is therefore a function of
the retro ratio alone, symmetric under exchanging which beam is called
forward, and it is largest when the two beams are equally strong and
falls away as either one comes to dominate.

## What problem it solves

A retro-reflected geometry is not optional in Doppler-free two-photon
spectroscopy: the cancellation that makes the line narrow needs both
counter-propagating beams, so the standing wave and the same-beam pedestal
it carries are unavoidable, not a design choice. What the fringe-resolved
and fringe-averaged limits settle is whether the spatial structure of
that standing wave needs to be carried explicitly through a lineshape
calculation or whether it safely collapses to its mean, which is the
difference between a model with one extra parameter distribution and one
without. And because the two absorption channels are locked together by
the same retro ratio, a feature that would otherwise look like pure
background, the pedestal, becomes a second observable: its size relative
to the narrow line is a prediction, not a nuisance, and a measured
departure from that prediction is informative about the retro ratio
itself.

## Where this repository uses it

[`rb5s6s.constants.RHO_RETRO`](../../rb5s6s/constants.py) holds the
adopted retro power ratio, 0.94 with an uncertainty of 0.04, a design
assumption rather than a bench measurement: the retro path is built to be
self-imaging so the forward and returning modes match by construction,
but loss at every extra surface and any residual misalignment push the
real ratio below the ideal value of one. Every absolute AC-Stark
prediction in the repository scales with $(1+\rho)$, so this constant
enters [the AC-Stark shift](ac-stark-shift.md) directly.

The fringe-averaging argument is worked out in
[THEORY_NOTE.md](../THEORY_NOTE.md). There the coupling that drives the
Doppler-free line is shown to be uniform along the standing wave, so only
the AC-Stark shift fringes, and a fast axial atom's modulation index at
that shift depth is small enough to put the effective intensity at the
fringe MEAN, which is the fringe-averaged limit above applied to this
transition. A frozen-fringe simulation of the weak-excitation amplitude
along each trajectory (module `rb5s6s/ramp_transit.py`) recovers that mean
in both the fast-sweep and frozen-fringe limits to about a tenth of a
per cent, independent of the quasi-static assumption the rest of the
argument relies on. The fringe-resolved tail left over from
near-transverse atoms does not move that mean, but it does suppress the
line's third moment, a separate and smaller effect documented in the same
note.

The wide-scan design in the fixed-lock proposal turns the same physics
around and reads it as a diagnostic.
[The fixed cavity lock chapter](../plan/09_the-fixed-lock.md) checks that
the drive depth chosen to null the sideband comb does not also null the
same-beam term, since a drive that suppressed the pedestal along with the
comb would defeat the wide scan's purpose, and confirms the two channels
share one Bessel law. The following chapter,
[§10c.7](../plan/10_the-fixed-lock-instrument.md), and
[`scripts/run_widescan_design.py`](../../scripts/run_widescan_design.py),
which is the actual source of the number below, carry the area ratio
forward into an in-situ, if weak, monitor of the retro ratio measured on
the same traces as the line itself, without a separate power meter.

## What can go wrong

The most common model failure is a factor-of-two slip in the fringe
period. Because the pattern is set by the round-trip phase, its spacing
is $\lambda/2$, and treating it as $\lambda$ mislabels every fringe by
one and shifts any node-antinode argument by half a period.

A subtler model failure is collapsing the two things that fringe and the
one that does not into a single picture. The AC-Stark shift fringes with
position because it follows the total field intensity, but the
Doppler-free coupling does not, because it is driven by a cross term that
stays uniform along the standing wave. Assuming both are governed by the
same spatial pattern, or that a fringe-averaged treatment of the shift
also settles the coupling, produces conclusions about the lineshape that
the underlying physics does not support.

A data-insufficiency limit is built into the area-ratio diagnostic itself.
Because the ratio is stationary at a retro ratio of one, its sensitivity
to a change in the retro ratio vanishes exactly where a well-aligned
retro-reflector is expected to sit, so a pedestal measured to some
fractional precision constrains the retro ratio far more loosely than the
same precision would suggest away from that point. A departure from the
adopted value that is small is, for that reason, the hardest one to
catch this way.

Finally, an experimental limitation shared by any pedestal-based
measurement: the same-beam channel has to be separated from whatever
broad, non-atomic background sits under it, stray and scattered light in
particular, before its area means anything. A pedestal that has not been
isolated from that background will read as a retro ratio that is too
large, since scattered light adds area the standing-wave physics did not
produce.

## Try it

The narrow-to-pedestal area ratio and its slope, evaluated at a perfect
retro reflector and at the value this repository adopts.

```python
from rb5s6s import RHO_RETRO


def area_ratio(rho):
    return 4.0 * rho / (1.0 + rho ** 2)


def area_ratio_slope(rho):
    return 4.0 * (1.0 - rho ** 2) / (1.0 + rho ** 2) ** 2


for rho, label in ((1.0, "perfect retro"), (RHO_RETRO, "adopted RHO_RETRO")):
    print(f"rho = {rho:.3f} ({label}): area ratio = {area_ratio(rho):.4f}, "
          f"slope = {area_ratio_slope(rho):+.4f} per unit rho")
print("the slope vanishes at rho = 1, so the ratio is a weak monitor near it")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/stalnaker2006.md`](../lit/stalnaker2006.md), which supplies the
  frequency-modulation framework behind the fringe-averaged, small
  modulation-index limit used above.
- [`../lit/biraben1974.md`](../lit/biraben1974.md), the founding
  demonstration of a retro-reflected two-photon geometry, including the
  polarisation control that isolates the same-beam pedestal from the
  Doppler-free line.
- [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md), for
  the cancellation the cross term performs and the pedestal it leaves
  behind.
- [The AC-Stark shift](ac-stark-shift.md), for what the fringe-averaged
  mean feeds into once the standing wave is resolved as a beam geometry.

---

[← Doppler-free two-photon spectroscopy](doppler-free-two-photon.md) · *Experimental spectroscopy, 2 of 8* · [The Voigt profile →](voigt-profile.md)
