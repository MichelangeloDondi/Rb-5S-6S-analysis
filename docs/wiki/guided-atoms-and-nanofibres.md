# Guided atoms: hollow cores and nanofibres

*[wiki index](README.md) · concept*

**The question.** What changes when the atoms and the light are held in the
same waveguide instead of crossing in free space, and which of this
measurement's limits that fixes?
**Takes.** [The beam waist](the-beam-waist.md) for what an intensity is,
[transit-time broadening](transit-time-broadening.md) for the width a finite
crossing costs, and [the AC-Stark shift](ac-stark-shift.md) for what a
structured field does to the levels.
**Gives.** The two guided geometries, what each one buys and charges, and why
a guided platform is a different lever on this record's degeneracies rather
than a better version of the same one.
**Skip if.** You have no fibre. Nothing on the record's main path depends on
this page.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## The two geometries, and they are opposites

**A hollow-core fibre puts the atoms inside the light.** The guided mode runs
down a hollow channel and the atoms sit in it. Interaction length becomes a
design choice rather than a beam crossing, and it can be centimetres where a
free-space waist gives millimetres.

**A nanofibre puts the atoms outside the light.** The glass is drawn until its
diameter is below the wavelength, so a large fraction of the mode travels as
an evanescent field in the vacuum around it. Atoms are trapped in that
evanescent field, a few hundred nanometres from a glass surface.

**The consequences run in opposite directions**, which is why they are two
platforms and not two versions of one.

| | hollow core | nanofibre |
|---|---|---|
| where the atom sits | inside the mode | outside the glass, in the evanescent tail |
| interaction length | centimetres, by design | the taper waist, millimetres |
| what limits coherence | collisions with the wall, guided-mode light shifts | the surface, through van der Waals and its own thermal field |
| what it is good at | long interrogation of a dense guided sample | strong coupling of a few atoms to a single mode |

## The numbers this record actually holds

From [`results/onf_candidate.csv`](../../results/onf_candidate.csv), which
sizes a nanofibre alongside this measurement's vapour cell:

| quantity | value | what it sets |
|---|---|---|
| fibre diameter | 400 nm | below the wavelength, which is what makes the field evanescent |
| effective index band | 1.08 to 1.25 | how tightly the mode is bound, and therefore how far it reaches |
| evanescent decay length | 211 to 388 nm | **the atom-surface distance scale.** Everything about surface effects is measured against this |
| effective mode area | 0.50 um^2 | the intensity a given power makes, which is the nanofibre's whole advantage |

**Compare the last one with the cell.** The same file carries the cell's
effective intensity at 6.784e7 W per square metre and the light shift it makes
at 0.348 MHz for 225 mW. A mode area of half a square micron reaches that
intensity at microwatts. **The nanofibre's argument is not that it is bigger.
It is that a tiny power does what a large one does in free space.**

## Why this is a lever and not an improvement

This record's central difficulty is that a total width is well determined
while the split between its causes is not
([identifiability](identifiability.md)). Adding more of the same measurement
does not help, which
[`results/twin_span_sweep.csv`](../../results/twin_span_sweep.csv) shows
directly: ten times the data moves the width-width correlation by 0.0000.

**A guided platform moves a term no cell setting can reach.** Transit
broadening is set by how long an atom stays in the light, and in a guide that
is set by the geometry rather than by a thermal velocity through a waist. The
cell's transit contribution at 130 C is 0.9575 MHz and it cannot be turned
off. **In a guide it becomes a knob**, which is what makes the platform an
orthogonal lever on the degeneracy rather than more of the same.

**And the knobs are real, not hypothetical.** A two-colour trap can be turned
on and off, and the relative intensity of its two colours scans the
atom-surface distance. The red trapping beam can run as a travelling wave or
as a standing wave. The MOT can be on or off, and molasses temperature is a
ladder rather than a setting. **Each of those moves a different term**, which
is the property a lever needs.

## What it charges, stated because the page would be dishonest without it

**The surface is a new systematic, not a free lunch.** At a few hundred
nanometres the van der Waals interaction with the glass shifts and broadens
the line, and the fibre's own thermal field adds to it. A platform that
removes transit broadening and adds a surface shift has not obviously
improved anything until the new term is measured.

**Two-colour traps impose their own light shift distribution**, which is the
same class of problem as
[the Stark ramp](ac-stark-shift.md) in the cell: the atoms do not all see one
shift, they see a distribution, and a measurement that assumes one number
inherits the spread as a systematic.

**A guided measurement is not automatically better conditioned.** It is
differently conditioned, and the value comes from combining it with the cell,
not from replacing the cell with it.

## The design has a twin, and the twin's honesty is in its flags

`scripts/run_fibre_twin.py` runs the nanofibre candidate's molasses ladder
as 500 recovery trials per synthetic world into
[`fibre_twin.csv`](../../results/fibre_twin.csv). Its own flags carry its
scope, `design_validation_only TRUE` and `measures_laser_linewidth FALSE`:
it establishes that the proposed design can identify the homogeneous
component under worlds where the answer is known, with per-rung scatter
4.0 kHz against the 3.2 kHz the cell record demonstrates per condition,
and it carries the band-edge licensing sentence, since the lever and its
calibration are the same order and a disagreement therefore means
unidentifiable, not wrong. What the real fibre will do is not a
twin question.

## Further reading

* [Identifiability](identifiability.md), the degeneracy a second platform is
  meant to break.
* [Transit-time broadening](transit-time-broadening.md), the term a guide
  turns into a design choice.
* [The digital twin](the-digital-twin.md), which is how a guided design is
  scored before it is built.
* [`docs/notes/onf_candidate.md`](../notes/onf_candidate.md), the sized
  candidate this page summarises, with the three instruments one apparatus
  provides.

---

[← Vapour density and temperature](vapour-density-and-temperature.md) · *Experimental spectroscopy, 10 of 10* · [wiki index →](README.md)
