*Chapter 1 of 7 of [the big picture](../BIG_PICTURE.md)*

## 1. Why the line is worth characterising at all

*Status, plainly. 993 nm is not put forward as a better clock line. On
natural linewidth it is worse than the 778 nm standard. The
magic wavelengths are calculated and unvalidated. The method is demonstrated
on this dataset as a bound. What has actually been delivered is in §4.*

Stated at the size the evidence supports, in four parts. §1.1 is the case for
the line. §1.2 is the trapped-atom route, and the one O-band crossing that is a
lever rather than a trap. §1.3 is the method. §1.4 is the size the collisional
coefficient should have. Sections 5 and 6 say what the next measurements would
add.

### 1.1 An uncharacterised line in a well-motivated class, but not a better clock line

The 778 nm 5S→5D two-photon transition is an established optical
frequency reference, and the reason is structural: two-photon Doppler-free
excitation kills the first-order Doppler width without a beam-geometry trick,
so the apparatus is a cell, a laser and a detector. That compactness is the
documented draw of the whole class ([Martin 2018](../lit/martin2018.md),
[Newman 2021](../lit/newman2021.md)).

993 nm 5S→6S shares that structure. It does **not** share the linewidth
advantage: the 6S₁/₂ upper state lives 45.57 ns
([Gomez 2005](../lit/gomez2005.md)), giving the 3.49 MHz natural width every fit
here carries, whereas 5D₅/₂ is far longer-lived: [Bandi 2025](../lit/bandi2025.md)
quotes the 5S→5D two-photon working linewidth as **≈330 kHz**, about an order of
magnitude narrower. On natural quality factor alone, 993 nm starts *behind* the
line the compact-clock community already uses, and that
community is at 6×10⁻¹⁴/√τ ([Ahern 2025](../lit/ahern2025.md)). Nothing in this
record suggests 993 nm would overtake it, and this page should not be read as
claiming so.

What is true is narrower and worth stating on its own: the environmental
coefficients of 993 nm have only ever been bounded, and coarsely
([Orson 2021](../lit/orson2021.md)'s nulls at ~6 MHz). Those coefficients decide
how well an environment must be controlled for any target stability, so they
are worth knowing for a line nobody has measured them on, and they are the
entry the 5D/7S self-broadening series is missing. That is the case: an
uncharacterised line in a practically-motivated class, not a challenger.

The rungs either side of it are now measured, by one group and one method,
which makes the gap concrete rather than rhetorical. Both drive a
Doppler-free two-photon line in a pure Rb cell and read the cascade
fluorescence, and both infer density from cell temperature rather than
measuring it:

| line | self-broadening | in MHz per 10¹² cm⁻³ | convention |
|---|---|---|---|
| 5S→5D₃/₂ ([Cao 2025](../lit/cao2025.md)) | 40 ± 0.54 kHz/mTorr | ≈ 0.0018 | FWHM, stated |
| 5S→7S ([Wang 2025](../lit/wang2025.md)) | 0.32 ± 0.01 MHz/mTorr | ≈ 0.014 | not stated |
| **5S→6S, this work** | not measured | **bound 0.03–0.05** | FWHM |

Converted at 423 K, the temperature both papers use. The 7S paper never says
whether its linewidth is a half width or a full width, so the factor of eight
between the two rungs carries a factor-of-two caveat until someone settles it.
The 7S row is also not the 7S number §1.4 anchors on. Zameroski 2014 measured
the same 760 nm line at 129 ± 11 kHz/mTorr, about 0.0054 in the units of the
third column, a factor of 2.6 below Wang's, and §1.4 converts it at 403 K
rather than 423 K, which is a difference of a few percent and none of the
factor of 2.6
([FUTURE_TRANSITIONS_titsapph.md](../FUTURE_TRANSITIONS_titsapph.md) §3.2). The
one quantity the expectation in §1.4 rides on therefore has two published
values and no adjudication.

This record's bound sits 2.1 to 3.6 times above the 7S
entry, so it is consistent with the neighbouring rung without yet reaching
it. The per-peak *fitted* values here, 0.013 to 0.018, straddle
the 7S rung: three of the four are above 0.014 and the fourth just under it, even
though 6S is the more compact state. That is independent
support, from outside this record, for the reading its own lever test already
forces: those fitted widths are a floor, not resolved collisions. Inside the
2025 dataset the evidence is that the width rises only ×1.47 across a ×52.5
density span. The neighbouring rung says the same thing from the other direction.

[Wang 2025](../lit/wang2025.md) closes by
proposing 5S→7S as the basis for an optical frequency standard. The 5S→6S line
is not being characterised in an empty field.

### 1.2 Magic wavelengths would let it be done on trapped atoms

The awkwardness of a cell reference is that the atoms are hot, colliding and
moving through the beam. Those are the transit and collisional terms this
record spends its work bounding. Trapping fixes that, but a trap normally
shifts the very line you are measuring. A *magic* wavelength does not: both states shift equally, and
the transition frequency is untouched. That is the trick behind lattice
clocks (Sr at 813 nm). The polarizability recompute here gives the **first
5S–6S magic wavelengths**, ≈ 1203.9 / 1287.9 / 1339.6 nm, all trapping (α > 0 for
both states), with a 16 to 84 percent band of 1203.06 to 1204.73 nm on the
1203.9 nm crossing, so the
trapped-atom version of this measurement has candidate wavelengths where
before it had none. The state pair has to be said out loud: Zang *et al.* 2012
report six magic wavelengths between 1200 and 1600 nm for the **6s–5p₁/₂,₃/₂**
pairs of a four-level active clock, two of which (1336 and 1342 nm) bracket the
1339.6 here. They are a different state pair and a different magic condition,
and the crowding is expected: between the 5p₁/₂–6s₁/₂ and 5p₃/₂–6s₁/₂
resonances at 1323.88 and 1366.87 nm the 6S polarizability runs from one pole
to the other through every value, so any pair built on 6S tends to put a root
somewhere in that 43 nm window, theirs at 1336 and 1342 nm and this record's
at 1339.6 nm included. These are an envelope, and scalar only, which for
these states is less of a caveat than it sounds: the tensor polarizability
vanishes identically for $J=1/2$
(triangle rule), so with linear polarization the scalar term is exact, not an
approximation. None of the three crossings has been measured. The list is also
deliberately incomplete: three more crossings exist hard against poles, one at
1297.5 nm sitting 0.7 nm from the 6s₁/₂–7p₁/₂ resonance at 1298.3 nm and two
hugging the 6s–8p doublet near 1029.7 and 1031.9 nm, and the 1.5 nm pole guard
in `magic_wavelengths()` drops them by construction. That close to a resonance,
photon scattering and the sensitivity to trap-laser frequency make a crossing
magic in name only. `rb5s6s/hyperpolarizability.py` puts numbers on all six crossings, the
pole-hugging ones included, quantifying three trap-design quantities at each, the
two shifts to within a factor of two. The fourth-order differential shift, the hyperpolarizability term, is
+0.87 Hz per megahertz squared of trap depth at the 1203.9 nm crossing, where a
depth of h × 1 MHz is 48 µK, so a trap half a millikelvin deep moves the line
by somewhere between fifty and two hundred hertz against the transition's
3.49 MHz natural width. The vector shift is the
sharper requirement: at that same depth a stretched-state atom sees 280 kHz per
megahertz of depth per unit circularity of the trap light, so holding the trap
shift under a kilohertz needs the circularity below about 3 × 10⁻⁴. At the 1297.5 and 1339.6 nm
crossings the same coefficient is nearly ninety times larger, so those two are
usable only in strictly linear light. Trap photons scatter off the 6S state a few times per second per
megahertz of depth at 1203.9 nm and ten to sixty times faster at the 1287.9,
1297.5 and 1339.6 nm crossings. The pair near 1030 nm shows lower rates on
this line list, but there the module flags its upward entries as several-fold
understatements, and holding a trap wavelength against the adjacent 6s–8p
doublet would put the trap laser's own stability into the error budget. That
leaves 1203.9 nm as the one practical operating point. The crossings also read backwards. Where one sits is fixed by
the matrix elements that build the two polarizabilities, so measuring a
crossing constrains them, which is how the 5S–5D magic wavelength was turned
into a 5P–5D matrix element by [Hamilton 2023](../lit/hamilton2023.md). The lever
is best where the trap is worst, but the quantity that decides whether a
measurement is worth making is what the element is already known to.
`lever_table()` in the same module ranks all six on all three counts, and
exactly one crossing, the steep root at 1297.5 nm, would improve on the present
state of knowledge at all, by three per cent. [FUTURE_TRANSITIONS_titsapph.md](../FUTURE_TRANSITIONS_titsapph.md)
§5.1.1 carries the table and the reason steepness turned out to be the right
thing to have selected on.

![the polarizability ladder and the magic crossings](../../figures/fig9_polarizability_ladder.png)

*Where the magic wavelengths come from: the 5S and 6S dynamic polarizabilities
cross three times between 1200 and 1340 nm, and each crossing is a wavelength
where a trap would hold both states without pulling the 993 nm line. This
figure draws the curves and the crossing positions only. The 16 to 84 per cent
Monte-Carlo spread over the input matrix elements is drawn on
[fig17](../../figures/fig17_magic_wavelengths.png) and committed in
`results/polarizability.csv`, and it is the uncertainty of the calculation
rather than of a measurement, which is why the crossings below are quoted with
theirs. Nothing here has been checked against a trap.*

Where they landed was not designed for. **Two of the three sit inside the
telecom O-band** (1260–1360 nm, ITU), 1287.9 ± 0.2 and
1339.6 ± 0.1 nm over the same Monte-Carlo band
(`results/polarizability.csv`), so a trap at either could in principle be built
from datacom-grade
diodes, which are cheap, fibre-coupled by default and available space-qualified.
Those two are not the practical pair, though, and the reason is not the diode.
Both lie hard against 6S→nP resonances, where trap-photon scattering is high,
so the 1203.9 nm crossing, which sits on the smooth part of the curve, is the
usable one ([README.md](../../README.md)'s results table and
[CLAIMS.md](../CLAIMS.md) §1 both say so). The O-band also has no erbium
amplifier, so reaching trap power there is harder than in the C-band, but that
is the soluble half of the objection. Recorded as an observation about the
numbers, not a design: they remain unvalidated, scalar-only envelopes, and the
band edges are an external convention rather than anything this repo computes.

**A third O-band crossing is a lever rather than a trap, and it is the map's
cheapest arrow.** The three above cleared the pole guard. The same differential
polarizability also crosses zero on a steep root at 1297.5 nm, 0.745 nm from
the 6S to 7P resonance, trapping in sign like the other five but quantified out as
a trap by that proximity, and the proximity that ruins it as a trap is what
makes it precise for metrology: an auxiliary diode scanned across it while
the 993 nm lineshape is read locates the root, and the root's position gives
the 6S to 7P reduced dipole matrix elements with no intensity calibration and
no absolute frequency reference in the chain. The same beam is a sign-reversal
test of the asymmetry channel and a calibrated shift injector. It rides any
cell session on one commodity diode and no new laser time, which is why
[FUTURE_TRANSITIONS_titsapph.md](../FUTURE_TRANSITIONS_titsapph.md) §4.1 ranks it
first of four candidate papers on risk-adjusted distinctiveness per unit bench
cost, and §5.1 there carries the design and its envelope numbers. It is deliberately absent from the
magic-wavelength list above, whose criterion is usability as a trap.

---

*[the big picture](../BIG_PICTURE.md) · [The method and its limits](02_the-method-and-its-limits.md)*
