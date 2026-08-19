*Chapter 10 of 11 of [the plan](../PLAN.md)*

### 10c.6 THE OSCILLOSCOPES

Two LeCroy WaveSurfers are on the bench, a 3104z and a 10, both 1 GHz, and
APPARATUS records them as present and unused for the 2025 dataset. The 2025
traces were taken on a 2000-point record while these sat beside the experiment.

The deep record removes the sampling constraint entirely rather than merely
satisfying it, so the information budget becomes time-limited through the
correlation time above and never sample-limited. FOUR CHANNELS EVERY BLOCK,
the ramp, the fluorescence, the cavity error signal and a marker for the
modulator state, with the sweep synchronisation on the external trigger input
so no signal channel is spent on it. The cavity error channel is the in-situ
laser-noise witness the 2025 session had to reconstruct afterwards from rulers.

SEQUENCE MODE, ONE SEGMENT PER SWEEP, NEVER ON-SCOPE AVERAGING. Averaging in
the instrument destroys the per-sweep centres the joint fit needs and the
timestamps an Allan deviation needs.

PULL THE TRACES OVER THE NETWORK AND WRITE THE BLOCK SETTINGS BESIDE THEM AT
ACQUISITION TIME. The corrupt files, the missing per-block settings and the
reconstructed modulation depths of the archive are all consequences of a
manual export, and a scripted campaign removes that class rather than
documenting it. The scope setup file is saved beside the traces every block,
the scope identity and firmware go in the block manifest, and the acquisition
script is versioned here.

THE VERTICAL RESOLUTION IS A REAL CONSTRAINT AND IT IS THE ONE MOST EASILY
MISSED, because it binds where the open questions live rather than at the peak.
An eight-bit front end with the line peak filling the screen puts one least
significant bit at about 0.39 per cent of the peak. The line itself is
therefore digitised comfortably, and the analog noise floor is close enough to
one bit to dither the quantiser rather than fight it. BUT THE PEDESTAL IS
ABOUT ONE BIT: its predicted height of 0.42 per cent of peak in 10c.7 is 1.1
LSB, and the measured band excess of 0.10 to 0.29 per cent is BELOW one bit at
0.26 to 0.74 LSB. Every question this record leaves open lives under the
quantisation step at a single vertical setting.

THIS MOTIVATES A TWO-WINDOW ACQUISITION, subject to the day-one measurement
below. The same detector feeds a second channel at ten to twenty times the
vertical gain with the peak deliberately clipped, which costs nothing because
the first window already owns the peak, and the wings, the pedestal and the
baseline are then digitised with real resolution. Counting below the crossover
is the same repair by a different route, and running both at once is the
detection cross-check this section already argues for.

DC COUPLING ALWAYS, since the baseline is data here rather than a nuisance to
be blocked, and the termination chosen once and recorded. THE COMMITTED NOISE
LAW BELONGS TO THE 2025 DETECTION CHAIN AND DOES NOT TRANSFER: change the
termination, the gain or the instrument and the coefficients the weights depend
on are no longer the measured ones, so the law is re-measured on the new chain
before any weighted fit is believed.

STORE RAW SINGLE SWEEPS AND FILTER OFFLINE. On-scope resolution enhancement is
an irreversible filter on the science channel, memory is not the binding
constraint here, and a filter applied in the instrument cannot be undone in
analysis. The one on-scope filter worth taking is the bandwidth limit, because
the signal bandwidth is far below it and the broadband noise it removes would
otherwise alias.

THE TRIGGER AND THE TIMESTAMPS DO DOUBLE DUTY. The sweep synchronisation on the
external trigger keeps every signal channel free, the per-segment timestamps of
sequence mode are what the Allan deviation of 10c.3a consumes, and the trigger
edge records which branch of a triangular ramp a segment belongs to, so the
branch-separated analysis needs no additional hardware.

THE TIMEBASE NEEDS STABILITY AND NOT ACCURACY, because the comb re-derives the
frequency-per-time scale in every block. Nothing here waits on a clock
calibration.

READ FROM THE MANUALS ON THE DAY, never from memory: the maximum record length
and the maximum number of segments per sequence on each unit, the resolution
enhancement modes available, and the transfer interface and its rate. Which
unit is which is settled by the bench photographs, which are a record of the
hardware and not a measurement of it.

PHOTON COUNTING IS WORTH TESTING, and the arithmetic says where it pays.
Inverting the committed noise law at the median committed amplitude gives a
peak photoelectron rate of order three to four hundred thousand per second, so
pile-up at nanosecond pulses is negligible and counting is easy at 1 GHz. The
analog floor and the shot term are equal at about 8.8 mV, which is 1.6 per
cent of the median peak, and BELOW that level counting wins: about 1.7 times
the signal-to-noise at one per cent of peak and 2.7 times at three parts in a
thousand. That is exactly the region where the band excess, the pedestal and
the wings live, which is to say every open question this record has. With two
oscilloscopes the analog and counting chains can run on the same photons
simultaneously, and any disagreement between them measures the detection
systematic directly rather than assuming it away.

### 10c.7 WHAT THE PEDESTAL IS GOOD FOR

A wide span makes the pedestal visible for the first time, and limit two of
section 10a records that it is NOT the band excess. What it does carry is the
Maxwell-Boltzmann width of the atoms actually being probed, which is a
different quantity from the thermocouple reading of a spot on the cell wall.

The predicted height is about 0.4 per cent of the line peak, from the ratio of
the cross term that drives the Doppler-free line to the same-beam term that
drives the pedestal, and it carries an order-unity assumption about the angular
factors that a derivation should close. At that amplitude the fitted pedestal
width gives a temperature to something like ten to twenty kelvin per sweep and
better with repeats.

THAT IS A CONSISTENCY CHECK AND NOT A DENSITY AXIS. Vapour pressure moves
several per cent per kelvin, so a density lever would need sub-kelvin
agreement, which this does not reach. What it does catch is a gross
disagreement between the thermocouple and the atoms, which is the cold-spot
systematic the density lever rests on and which nothing in the 2025 record
constrains.

### 10c.8 THE DAY-ONE MEASUREMENTS, BEFORE ANY SCIENCE BLOCK

Each of these decides a setting above, and none takes long.

1. THE DRIFT RATE OF THE REPAIRED LOCK. Decides the sweep timing and whether
   the laser width may be shared globally.
2. THE STEP RESPONSE OF THE DETECTION CHAIN, into both terminations. Partly
   answered from the archive already: the rehearsal's LeCroy traces put the
   chain faster than 10 us at 10^6 V/A, so the 1.9 ms correlation is neither
   the amplifier nor the light but the campaign's acquisition mode. What
   remains is converting that bound, which sits at the sampling limit, into a
   measured time constant, and establishing the response at whatever gain the
   next session actually uses.
3. THE SINGLE-PULSE SHAPE AND THE PEAK COUNT RATE. Decides whether the
   counting mode is available, and checks the inverted rate above against a
   direct measurement, which tests the committed noise model microscopically.
4. THE MODULATOR RESPONSE AT THE HIGHER DRIVE FREQUENCY, since the resonant
   tank may not reach it without retuning.
5. ONE QUICK SCAN ACROSS THE 85 ISOTOPE PAIR, to pin the separation and choose
   a drive frequency whose teeth clear both lines.
6. THE FLYBACK SETTLE TIME, from tooth spacing early and late in a comb block.
7. AN INDEPENDENT MEASUREMENT OF THE LASER WIDTH, which 10c.1 argues is worth
   more than any other single item here. The lineage gives the number to hold
   it against: [Nieddu 2019](../lit/nieddu2019.md) ran an MBR-110 at about 100
   kHz and saw 2.43 to 2.60 MHz on the laser axis, close to five on the
   transition axis, which is where the 2025 line already sits.
8. THE POLARISATION OPTICS OF 10c.9, which are a procurement item rather than
   a setting, and the extinction null they make possible.
9. THE NOISE LAW OF THE NEW DETECTION CHAIN, since the committed coefficients
   belong to the 2025 chain and every weighted fit depends on them. Half a day
   of dark and bright traces, and it also decides the two-window gains of
   10c.6.
10. THE MAXIMUM SCAN WIDTH THE CONTROL SOFTWARE ALLOWS, which decides whether
    the 87 pair of 10c.5 fits in one sweep. The photographed session used 3.5
    GHz, which is a setting and not a ceiling.
11. THE WAVEMETER LINK TO DISK. The photographed session shows no network link
    to the wavemeter, which is exactly the photographed-not-logged failure
    section 11 exists to remove.

### 10c.9 POLARISATION, AND WHAT THE LINEAGE ALREADY SETTLES

The polarisation of the two beams is a control this bench does not currently
have and the OIST lineage did. It separates the two components of the signal at
the source rather than by fitting, and one configuration is a null test rather
than an isolation.

THE LAW IS PUBLISHED IN THIS LINEAGE AND IS NOT A CONJECTURE.
[Rajasree and co-workers](../lit/rajasree2020spin.md), on this transition and in
the warm paraxial configuration, report the two-photon rate going as the
SQUARED DEGREE OF LINEAR POLARISATION and vanishing for circular light. For a
5S to 6S transition with no change of hyperfine number the two-photon operator
keeps only its scalar and vector parts, and the scalar part carries the dot
product of the two polarisation vectors, which is zero for two photons of the
same helicity.

WHAT THAT MEANS FOR THE THREE CONFIGURATIONS:

  PARALLEL LINEAR is the 2025 configuration and the standard science block.
  Doppler-free line and pedestal both present.

  ORTHOGONAL LINEAR kills the CROSS term between the counter-propagating
  beams, which is what drives the Doppler-free line, while the same-beam terms
  that drive the pedestal survive. This is a PEDESTAL-ONLY block, and the
  difference between parallel and orthogonal is the pure line with the
  pedestal removed by hardware rather than by baseline model. It answers
  directly what section 10a's baseline requirement can only approach by
  fitting: whether the pedestal is the shape the model assumes, and what its
  amplitude really is.

  CIRCULAR IS AN EXTINCTION NULL TEST AND NOT A LINE-ONLY MODE. An earlier
  draft of this section had it removing the pedestal while keeping the line.
  That is wrong in the way the published law makes plain: circular light
  removes the whole two-photon signal, line and pedestal together. Its value
  is as a null: everything the detector reports in that configuration is
  background, stray light or electronics, measured with the atoms switched off
  by polarisation alone and with nothing else in the apparatus altered.

THE HARDWARE IS A KNOWN GAP. [Nieddu 2019](../lit/nieddu2019.md) records
insertable quarter-wave plates before the focusing lens and before the retro
mirror, and APPARATUS records that this bench has no counterpart to them. So
this programme is a procurement item and not a settings change, and it is the
one place in section 10c where the plan asks for a component rather than a
choice.

A SECOND SUBSTITUTION FROM THE SAME SOURCE IS WORTH REVISITING WHILE THE OPTICS
ARE OPEN. [Nieddu 2019](../lit/nieddu2019.md) collects both cascade legs, 780 and
795 nm, through Nieddu's 800 nm short-pass. This bench collects 795 only,
through its own passband stack. Both legs is close to twice the signal for
every shape observable in this section, at the cost of the filtering argument
that currently rests on the photocathode red edge.

### 10c.10 THE COMB AS A STATISTICAL INSTRUMENT, NOT ONLY A RULER

With the modulator on, a science trace carries a small number of teeth on each
line rather than one profile, and they are not merely a frequency scale. The
strong teeth exist only where the Bessel amplitude is appreciable, which at the
depth of 10c.4 means about four strong and two weak orders per line rather than
a dense carpet, so the whole structure is a handful of resolvable features
whose relative amplitudes, positions and widths are all predicted.

FIT THEM TWICE, AND COMPARE. The FORCED model shares one centre, the
radio-exact tooth spacing and the Bessel amplitude law across the whole group,
and it has very few free parameters. The FREE model lets every tooth carry its
own amplitude, centre and width. The two are nested, so the comparison is the
information criterion of the statistics chapter rather than a matter of taste,
and each kind of disagreement points somewhere specific:

  AMPLITUDE residuals against the Bessel law read saturation and any
  depletion, since a saturating transition compresses the strong teeth toward
  the weak ones.
  CENTRE residuals map the axis nonlinearity tooth by tooth across the line
  window, at radio accuracy, which is the finest-grained version of the
  calibration of 10c.3a.
  WIDTH residuals across teeth of different strength read power broadening
  within a single trace, because the teeth sample different intensities of the
  same beam at the same instant.

THE SESSION GRAMMAR THAT MAKES THIS WORK is one set of blocks and it serves
every programme in this section: modulator OFF for the cleanest statistics on
one profile, modulator ON at the working depth for the ruler and these
diagnostics, ON at two or three other depths so the amplitude law is tested
rather than assumed, and the polarisation configurations of 10c.9 crossed with
whichever of those the optics allow. The two sweep rates of 10c.3 are
interleaved within each, since the lag separation there needs the same line
measured at several rates and nothing else in the block changes.

---

*[The fixed lock, and what it buys](09_the-fixed-lock.md) · [Beyond 993 nm](11_beyond-993.md)*
