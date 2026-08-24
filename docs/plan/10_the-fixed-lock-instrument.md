*Chapter 10 of 11 of [the plan](../PLAN.md)*

**The question.** Which instruments acquire the fixed-lock campaign, at which settings, and what actually limits them?
**Takes.** Chapter 9's fixed-lock design and the measured noise budget of [`quantisation.csv`](../../results/quantisation.csv).
**Gives.** The oscilloscope allocation and settings, the noise budget that retires the bit-depth argument, the pulse and count-rate branch, and the day-one measurement list.
**Skip if.** You want the acquisition record's format, which is chapter 8, or the lock itself, which is chapter 9.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term.

### 10c.6 the oscilloscopes

Two LeCroy WaveSurfers are on the bench, a 3104z and a 10, both 1 GHz, and
APPARATUS records them as present and unused for the 2025 dataset. The 2025
traces were taken on a 2000-point record while these sat beside the experiment.

The deep record removes the sampling constraint entirely rather than merely
satisfying it, so the information budget becomes time-limited through the
correlation time above and never sample-limited. Four channels every block,
the ramp, the fluorescence, the cavity error signal and a marker for the
modulator state, with the sweep synchronisation on the external trigger input
so no signal channel is spent on it. The cavity error channel is the in-situ
laser-noise witness the 2025 session had to reconstruct afterwards from rulers.

Sequence mode, one segment per sweep, never on-scope averaging. Averaging in
the instrument destroys the per-sweep centres the joint fit needs and the
timestamps an Allan deviation needs.

Pull the traces over the network and write the block settings beside them at
acquisition time. The corrupt files, the missing per-block settings and the
reconstructed modulation depths of the archive are all consequences of a
manual export, and a scripted campaign removes that class rather than
documenting it. The scope setup file is saved beside the traces every block,
the scope identity and firmware go in the block manifest, and the acquisition
script is versioned here.

The vertical resolution is not the constraint, and an earlier version of
this section said it was. The experimenter asked whether the small features
were not already below the noise, and the measurement answered him
([`quantisation.csv`](../../results/quantisation.csv), threshold fixed
before the first run): across all 35 quality-passed conditions the analogue
baseline noise is 5.2 to 246 times the true quantisation step, median 37,
so the quantiser is heavily dithered and contributes at most 0.155 per cent
of the noise in quadrature. Even this section's own eight-bit hypothetical,
the peak filling the screen, gives 1.3 steps of dither and a 2.5 per cent
contribution. The pedestal at 1.1 LSB and the band excess at 0.26 to 0.74
LSB are hidden by the noise, not by the step, and a dithered converter is
precisely the device that lets averaging recover structure below its step.

What binds instead is the analogue noise per point and the number of
independent samples. The noise is light-linked in the wings, growing
linearly with power (8 to 10 times worse at 225 mW than at 25 mW, the
`BUDGET` rows of the same file), shot-limited on the peak, and correlated
at about 1.9 ms, so a sweep carries at most its duration over that time of
independent samples regardless of sample rate. The design levers, in order:
identify and reduce the light-linked background (its linear power scaling
fits shot noise on a background growing as the power squared, with a
coherence test against a monitor photodiode separating that from intensity
noise), repeats that are actually independent because they are interleaved
in time rather than taken back to back, and collection solid angle on the
shot-limited peak.

A second channel at higher vertical gain therefore buys no resolution, and
the two-window acquisition loses its stated justification. It stays in the
design only if it earns its keep another way: as clipping headroom, or as
the second simultaneous chain the dual-chain check wants. Counting below
the crossover keeps its own justification, which was never about bits.

DC coupling always, since the baseline is data here rather than a nuisance to
be blocked, and the termination chosen once and recorded. The committed noise
law belongs to the 2025 detection chain and does not transfer: change the
termination, the gain or the instrument and the coefficients the weights depend
on are no longer the measured ones, so the law is re-measured on the new chain
before any weighted fit is believed.

Store raw single sweeps and filter offline. On-scope resolution enhancement is
an irreversible filter on the science channel, memory is not the binding
constraint here, and a filter applied in the instrument cannot be undone in
analysis. The one on-scope filter worth taking is the bandwidth limit, because
the signal bandwidth is far below it and the broadband noise it removes would
otherwise alias.

The trigger and the timestamps do double duty. The sweep synchronisation on the
external trigger keeps every signal channel free, the per-segment timestamps of
sequence mode are what the Allan deviation of 10c.3a consumes, and the trigger
edge records which branch of a triangular ramp a segment belongs to, so the
branch-separated analysis needs no additional hardware.

The timebase needs stability and not accuracy, because the comb re-derives the
frequency-per-time scale in every block. Nothing here waits on a clock
calibration.

Read from the manuals on the day, never from memory: the maximum record length
and the maximum number of segments per sequence on each unit, the resolution
enhancement modes available, and the transfer interface and its rate. Which
unit is which is settled by the bench photographs, which are a record of the
hardware and not a measurement of it.

Photon counting is worth testing, and the arithmetic says where it pays.
Inverting the committed noise law at the median committed amplitude gives a
peak photoelectron rate of order three to four hundred thousand per second, so
pile-up at nanosecond pulses is negligible and counting is easy at 1 GHz. The
analog floor and the shot term are equal at about 8.8 mV, which is 1.6 per
cent of the median peak, and below that level counting wins: about 1.7 times
the signal-to-noise at one per cent of peak and 2.7 times at three parts in a
thousand. That is exactly the region where the band excess, the pedestal and
the wings live, which is to say every open question this record has. With two
oscilloscopes the analog and counting chains can run on the same photons
simultaneously, and any disagreement between them measures the detection
systematic directly rather than assuming it away.

### 10c.7 what the pedestal is good for

A wide span makes the pedestal visible for the first time, and limit two of
section 10a records that it is not the band excess. What it does carry is the
Maxwell-Boltzmann width of the atoms actually being probed, which is a
different quantity from the thermocouple reading of a spot on the cell wall.

The predicted height is about 0.4 per cent of the line peak, from the ratio of
the cross term that drives the Doppler-free line to the same-beam term that
drives the pedestal, and it carries an order-unity assumption about the angular
factors that a derivation should close. At that amplitude the fitted pedestal
width gives a temperature to something like ten to twenty kelvin per sweep and
better with repeats.

That is a consistency check and not a density axis. Vapour pressure moves
several per cent per kelvin, so a density lever would need sub-kelvin
agreement, which this does not reach. What it does catch is a gross
disagreement between the thermocouple and the atoms, which is the cold-spot
systematic the density lever rests on and which nothing in the 2025 record
constrains.

### 10c.8 the day-one measurements, before any science block

Each of these decides a setting above, and none takes long.

1. The drift rate of the repaired lock. Decides the sweep timing and whether
   the laser width may be shared globally.
2. The step response of the detection chain, into both terminations. Partly
   answered from the archive already: the rehearsal's LeCroy traces put the
   chain faster than 10 us at 10^6 V/A, so the 1.9 ms correlation is neither
   the amplifier nor the light but the campaign's acquisition mode. What
   remains is converting that bound, which sits at the sampling limit, into a
   measured time constant, and establishing the response at whatever gain the
   next session actually uses. This is the 3104z's job: the bound is that
   instrument's sampling limit, and its deep fast record is what converts a
   limit into a curve.
3. The single-pulse shape and the peak count rate. Decides whether the
   counting mode is available, and checks the inverted rate above against a
   direct measurement, which tests the committed noise model microscopically.
4. The modulator response at the higher drive frequency, since the resonant
   tank may not reach it without retuning.
5. One quick scan across the 85 isotope pair, to pin the separation and choose
   a drive frequency whose teeth clear both lines.
6. The flyback settle time, from tooth spacing early and late in a comb block.
7. An independent measurement of the laser width, which 10c.1 argues is worth
   more than any other single item here. The lineage gives the number to hold
   it against: [Nieddu 2019](../lit/nieddu2019.md) ran an mbr-110 at about 100
   kHz and saw 2.43 to 2.60 MHz per photon, which is 4.86 to 5.20 on the
   transition axis, where the 2025 line already sits at about 5.25. The
   natural width of 3.49 MHz on that axis is what makes the reading
   unambiguous, since a line narrower than natural is impossible.
8. The polarisation optics of 10c.9, which are a procurement item rather than
   a setting, and the extinction null they make possible.
9. The noise law of the new detection chain, since the committed coefficients
   belong to the 2025 chain and every weighted fit depends on them. Half a
   day of dark and bright traces, and it also decides whether the two-window
   split of 10c.6 earns its keep at all.
9a. The wing-noise discriminator, which the measured budget makes the
   highest-yield half hour on this list: baseline noise against power with
   the laser far off line, then the coherence between the monitor
   photodiode of chapter 8 and the fluorescence baseline. A coherent share
   is intensity noise and regresses out, an incoherent linear-in-power
   share is shot on a background growing as the power squared and is
   attacked with the filter, a pinhole at the collection image plane, and
   the retro dump. The 8-to-10-times growth of the wing noise from 25 to
   225 mW ([`quantisation.csv`](../../results/quantisation.csv), budget
   rows) is the prize: every open question in this record lives in the
   wings.
10. The maximum scan width the control software allows, which decides whether
    the 87 pair of 10c.5 fits in one sweep. The photographed session used 3.5
    GHz, which is a setting and not a ceiling.
11. The wavemeter link to disk. The photographed session shows no network link
    to the wavemeter, which is exactly the photographed-not-logged failure
    section 11 exists to remove.
12. The split-signal dual recording. Tee the detector output into the Agilent
    and the 3104z and record a handful of conditions on both at once. The
    amplitude departure from the square-of-power law orders by peak brightness,
    which reads as a detection signature, and two different chains digitising
    one photocurrent is the direct discriminator: what both records share
    belongs to the light, what differs belongs to acquisition. No single
    instrument can make that separation at any setting, and the 2025 archive
    cannot make it at all.
13. The pedestal thermometer. One slow wide sweep per temperature block with
    the Doppler pedestal in frame, on the Agilent, whose High Resolution mode
    gains bits exactly at slow sweep and holds the low broad pedestal and the
    tall narrow peaks on one range. The pedestal width is an in-situ
    temperature, and no 2025 session measured temperature at all: the archive
    carries variac set points, two of which have already been mistaken for
    temperatures.

### 10c.9 polarisation, and what the lineage already settles

The polarisation of the two beams is a control this bench does not currently
have and the OIST lineage did. It separates the two components of the signal at
the source rather than by fitting, and one configuration is a null test rather
than an isolation.

The law is published in this lineage and is not a conjecture.
[Rajasree and co-workers](../lit/rajasree2020spin.md), on this transition and in
the warm paraxial configuration, report the two-photon rate going as the
squared degree of linear polarisation and vanishing for circular light. For a
5S to 6S transition with no change of hyperfine number the two-photon operator
keeps only its scalar and vector parts, and the scalar part carries the dot
product of the two polarisation vectors, which is zero for two photons of the
same helicity.

What that means for the three configurations:

  Parallel linear is the 2025 configuration and the standard science block.
  Doppler-free line and pedestal both present.

  Orthogonal linear kills the cross term between the counter-propagating
  beams, which is what drives the Doppler-free line, while the same-beam terms
  that drive the pedestal survive. This is a pedestal-only block, and the
  difference between parallel and orthogonal is the pure line with the
  pedestal removed by hardware rather than by baseline model. It answers
  directly what section 10a's baseline requirement can only approach by
  fitting: whether the pedestal is the shape the model assumes, and what its
  amplitude really is.

  Circular is an extinction NULL test and not a line-only mode. An earlier
  draft of this section had it removing the pedestal while keeping the line.
  That is wrong in the way the published law makes plain: circular light
  removes the whole two-photon signal, line and pedestal together. Its value
  is as a null: everything the detector reports in that configuration is
  background, stray light or electronics, measured with the atoms switched off
  by polarisation alone and with nothing else in the apparatus altered.

The hardware is a known gap. [Nieddu 2019](../lit/nieddu2019.md) records
insertable quarter-wave plates before the focusing lens and before the retro
mirror, and APPARATUS records that this bench has no counterpart to them. So
this programme is a procurement item and not a settings change, and it is the
one place in section 10c where the plan asks for a component rather than a
choice.

A second substitution from the same source is worth revisiting while the optics
are OPEN. [Nieddu 2019](../lit/nieddu2019.md) collects both cascade legs, 780 and
795 nm, through Nieddu's 800 nm short-pass. This bench collects 795 only,
through its own passband stack. Both legs is close to twice the signal for
every shape observable in this section, at the cost of the filtering argument
that currently rests on the photocathode red edge.

### 10c.10 the comb as a statistical instrument, not only a ruler

With the modulator on, a science trace carries a small number of teeth on each
line rather than one profile, and they are not merely a frequency scale. The
strong teeth exist only where the Bessel amplitude is appreciable, which at the
depth of 10c.4 means about four strong and two weak orders per line rather than
a dense carpet, so the whole structure is a handful of resolvable features
whose relative amplitudes, positions and widths are all predicted.

Fit them twice, and compare. The forced model shares one centre, the
radio-exact tooth spacing and the Bessel amplitude law across the whole group,
and it has very few free parameters. The free model lets every tooth carry its
own amplitude, centre and width. The two are nested, so the comparison is the
information criterion of the statistics chapter rather than a matter of taste,
and each kind of disagreement points somewhere specific:

  Amplitude residuals against the Bessel law read saturation and any
  depletion, since a saturating transition compresses the strong teeth toward
  the weak ones.
  Centre residuals map the axis nonlinearity tooth by tooth across the line
  window, at radio accuracy, which is the finest-grained version of the
  calibration of 10c.3a.
  Width residuals across teeth of different strength read power broadening
  within a single trace, because the teeth sample different intensities of the
  same beam at the same instant.

The session grammar that makes this work is one set of blocks and it serves
every programme in this section: modulator off for the cleanest statistics on
one profile, modulator on at the working depth for the ruler and these
diagnostics, on at two or three other depths so the amplitude law is tested
rather than assumed, and the polarisation configurations of 10c.9 crossed with
whichever of those the optics allow. The two sweep rates of 10c.3 are
interleaved within each, since the lag separation there needs the same line
measured at several rates and nothing else in the block changes.

---

*[The fixed lock, and what it buys](09_the-fixed-lock.md) · [Beyond 993 nm](11_beyond-993.md)*
