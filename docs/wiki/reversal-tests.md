# Reversal tests

*[wiki index](README.md) · method*

**The question.** How are two systematics separated when they produce the
same signature in the data?
**Takes.** Nothing beyond the idea of a systematic. Pairs naturally with
[confounding by acquisition order](confounding-by-acquisition-order.md).
**Gives.** The odd-even decomposition under a flipped knob, the reversal
table as a design discipline, and the case where the atom supplies the
reversal for free.
**Skip if.** You want the statistics of separating parameters inside one
fit, which is [identifiability](identifiability.md). This page is about
separating effects by symmetry before any fit is asked to.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A reversal test separates effects by their parity under a knob the
experimenter can flip. Flip the knob, take the difference and the sum: the
difference isolates everything odd under that knob, the sum keeps everything
even, and the two halves are exact, model-free, and computed from the same
data.

The elementary example is a triangular sweep. Detection lag shifts the
apparent line centre one way on the rising half and the other way on the
falling half, so the half-difference measures the lag and the half-mean
cancels it exactly, while a real shift, even under sweep direction, survives
in the mean untouched. One knob, one flip, and a systematic becomes a
measurement of itself.

The discipline scales into a table. Where several mechanisms produce the
same raw signature, list each with the knob that flips it and the scaling
that grows it: one is odd under sweep direction, another follows power, a
third follows density, a fourth reverses with an ambient field. A mechanism
with no knob and no scaling is either exactly computable or it is not a
mechanism, it is an excuse.

## What problem it solves

Fitting cannot separate what the data do not distinguish, and two effects
with the same functional signature are one effect to any fit. A reversal
changes the DATA rather than the model: after the flip the two effects are
no longer degenerate because only one of them moved. This is the same move
as breaking a parameter degeneracy by design rather than by fitting, applied
to systematics rather than to parameters.

The decomposition is also immune to a whole class of modelling errors. The
half-difference of a triangular sweep does not care what the lineshape is,
only that it is the same shape on both halves, so the lag it returns is not
conditional on a profile choice.

```python
import numpy as np

# A line swept up and down, with a detection lag and a REAL shift injected.
nu = np.linspace(-30, 30, 1201)
line = lambda c: 1.0/(1.0 + ((nu - c)/2.7)**2)
lag_shift, real_shift = 0.8, 0.5          # both move the apparent centre
up, down = line(real_shift + lag_shift), line(real_shift - lag_shift)

def centre(v):
    """Midpoint of the half-maximum crossings: window-truncation-proof."""
    half = v.max()/2
    i = np.nonzero(v > half)[0]
    lo = np.interp(half, [v[i[0]-1], v[i[0]]], [nu[i[0]-1], nu[i[0]]])
    hi = np.interp(half, [v[i[-1]+1], v[i[-1]]], [nu[i[-1]+1], nu[i[-1]]])
    return 0.5*(lo + hi)

mean = 0.5*(centre(up) + centre(down))     # even part: the real shift
diff = 0.5*(centre(up) - centre(down))     # odd part: the lag
print(f"injected real shift {real_shift}, recovered from the mean: {mean:+.3f}")
print(f"injected lag        {lag_shift}, recovered from the diff:  {diff:+.3f}")
print("neither number needed the lineshape model to be right")
```

## Where this repository uses it

The measurement plan's asymmetry budget is a reversal table: detection lag
is odd under sweep direction, the AC-Stark ramp's asymmetry follows power,
speed-dependent collisional asymmetry follows density, and a vector light
shift reverses with the ambient magnetic field, so each candidate for an
observed asymmetry carries the flip that would convict or acquit it.

The sharpest instance cost nothing, because the atom supplied the reversal.
The hyperfine g-factor alternates sign between the two F manifolds of each
isotope, so the four lines of the spectrum form built-in polarity pairs for
anything odd in $m_F$: a vector-shift asymmetry would have to flip sign
between the two lines of an isotope at fixed field, fixed power and fixed
everything else. The committed record's per-line skew has the same sign on
all four lines, and one afternoon's reading of numbers already on disk
excluded the vector mechanism without a coil, a reversal block, or a single
new trace. The general lesson travels: before building the knob, check
whether the level structure already flipped it.

The same discipline runs backwards as a null-seeker. Where an effect
reverses through zero with a knob, scanning the knob to minimise the odd
signature finds the knob's zero, which is how a coil can null the ambient
field at the atoms without any calibrated magnetometer in the loop.

## What can go wrong

**The flip is not clean.** Reversing a sweep also changes which settling
transient the line meets, so the half-difference carries settling as well as
lag. A knob that changes two things separates nothing until the second thing
is controlled or modelled.

**The flip is incomplete.** A half-wave plate that rotates polarisation by
almost the right angle leaves a residual of the odd effect in the even
channel, suppressed but not gone. The suppression factor belongs in the
budget, not in the wastebasket.

**The even channel is read as clean.** The decomposition isolates what is
odd under this knob. Effects even under it, including the one being hunted,
remain superposed in the sum, and separating those needs a different knob or
a scaling.

**The reversal is run but never checked for closure.** Flipping twice must
reproduce the original within errors. A sequence that drifts between flips
converts drift into a fake odd signal, which is why reversal pairs are taken
adjacent in time, not at opposite ends of a session.

## Further reading

Reversal and modulation methods are the working spine of precision
measurement: parity experiments alternate handedness, electric-dipole-moment
searches reverse fields against comagnetometers, and clock evaluations
interleave states. Any of those literatures shows the same grammar, odd
signals as physics candidates, even signals as references, and every claimed
effect wearing the flip that would kill it.

## See also

[Confounding by acquisition order](confounding-by-acquisition-order.md), the
time-ordering member of the same family · [Identifiability](identifiability.md),
separation inside the fit where this page separates outside it ·
[Sweep rate and detection lag](sweep-rate-and-detection-lag.md), the
triangle-halves reversal in full · [Magnetic sublevels](magnetic-sublevels.md),
the g-factor sign structure that gives the free reversal ·
[The digital twin of an experiment](the-digital-twin.md), where a proposed
reversal is rehearsed before it is built

---

[← Confounding by acquisition order](confounding-by-acquisition-order.md) · *Robustness and influence, 7 of 7* · [wiki index →](README.md)
