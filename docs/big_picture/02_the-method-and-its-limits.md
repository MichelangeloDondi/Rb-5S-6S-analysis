*Chapter 2 of 7 of [the big picture](../BIG_PICTURE.md)*

**The question.** What is the drift-immune method, and what does it cost to
use it?
**Takes.** The motivation of chapter 1, or nothing if you already accept that
the line is worth measuring.
**Gives.** The method itself, the shape channels it reads, the size the
coefficients are expected to have, and the limits that follow from reading
shapes rather than positions.
**Skip if.** You want what the data delivered rather than how, in which case
[what the 2025 dataset delivered](04_what-2025-delivered.md) is the chapter.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

### 1.3 The method outlives the line

In any structured field the light shift is not one number but a distribution
over where the atoms sit, and because a two-photon signal goes as intensity
*squared*, that distribution has a closed form with a calculable asymmetry
that survives in the line *shape* even when the absolute frequency is
unusable.

The neighbouring field handles the same problem from the other
end. On the 778 nm 5S→5D line the AC-Stark shift is *the* limiting
systematic. [Ahern 2025](../lit/ahern2025.md) is explicitly light-shift-limited
at 6×10⁻¹⁴/√τ, and [Bandi 2025](../lit/bandi2025.md)'s review states that light-shift
variations "and vapor-cell temperature variations predominantly limit
performance for medium- to long-term averaging", against a field target of
better than 10⁻¹⁵ at a day. Note *both* halves of that pair: the light shift is
what the shape method reads, and the cell-temperature term is the
density-coefficient territory this record bounds. The work goes into
suppressing it: shift cancellation
([Gerginov 2018](../lit/gerginov2018.md)), active power modulation at ×1000
(Yudin 2020, [Andeweg 2026](../lit/andeweg2026.md)), magic
wavelengths ([Hamilton 2023](../lit/hamilton2023.md)). Every one of those
suppresses the **mean** shift.

![what each observable can and cannot see](../../figures/fig10_degeneracy_vs_observable.png)

*The method in one picture: which physical parameters each lineshape
observable responds to. The mean shift, the width and the asymmetry read
different projections of the same shift distribution, which is why nulling
the mean leaves the spread untouched. At the twenty conditions drawn, all at
130 °C, the total width is measured but its decomposition into components is not.
In the left panel the split between the two components slides freely along a grey
line of constant total width in MHz, the two are anticorrelated with a median
correlation coefficient of −0.90, and one of the twenty one-sigma ellipses reaches
negative Gaussian width. In the right panel the quantity actually measured, the
fitted total, is known to 1.0 per cent within a condition, and no trend with
laser power survives the scatter between measurement blocks, which is several
times larger than those bars.*

But the mean is not the distribution. [Hamilton 2023](../lit/hamilton2023.md)
builds the very same focus-average integral this analysis does and then
collapses it to a single spatially-averaged number, so the distribution is
set up and discarded. Nulling a mean leaves the *spread*, and a spread over atoms
does not average away: it dephases them. Whenever atoms are held long enough
for that to matter, whether an evanescent field around a nanofibre (§6), an
optical lattice or a hollow-core fibre mode, what limits coherence is the width of the
shift distribution, not its centre. This method reads that width from
lineshape, without needing the absolute frequency a drifting or structured
environment takes away.

None of the ingredients of that paragraph is new. Keeping the shift
distribution rather than its mean, reading a lineshape as a map of that
distribution, the I² weighting, and the closed form itself all appear in a 1980
review, and because that is a review they were established before it. §5 of
[LITERATURE.md](../LITERATURE.md) fixes what
is claimable after that concession, and §4 below states what survives it, at
the size it will survive.

The cell is simply where that is cheap to validate, which is why it was built
here first. **What is demonstrated so far is a bound, on one line, in one
geometry.** The claim is that the observable exists and is drift-immune, not
that it has yet beaten anything.

### 1.3a Why measuring the light shift is harder than it looks, in plain terms

Five findings from 2026-08-09 and 10 sit behind the numbers in section 4, and
none of them needs the machinery to follow. They are put here in the order a
reader meets the difficulty.

**1. Shining more light on the atoms stops helping, and it stops sooner at a
tight focus.** The signal is a two-photon event, so at low power it grows as
the square of the intensity. That square is what makes the whole method work:
it is the reason the distribution of light shifts across the atoms comes out
lopsided in a calculable way. But an atom that is already excited cannot be
excited again, so past some drive strength the square law flattens out. How
close the experiment is to that point is measured by one number, the saturation
parameter. The awkward part is how it scales. Focusing the beam tighter raises
the shift as the square of the inverse spot size, but it raises the saturation
parameter as the **fourth** power, because the two-photon coupling itself is
quadratic in the field. So tightening the focus leaves the safe regime twice as
fast as it gains signal. At the 64 µm spot of the 2025 sitting the parameter is
0.033 and the square law is safe. At the 16 µm a future sitting proposes it is
8.5, and the predicted lopsidedness changes by a factor of three
([fig24](../../figures/fig24_weak_field_limit.png)).

**2. An atom can fall out of the experiment mid-flight, and not come back.**
The rubidium ground state is split in two by the interaction with the nucleus,
and the laser is tuned to one half of it. An excited atom returns to the ground
state through an intermediate level, and that intermediate decay does not care
which half it lands in. If it lands in the other one, it is off resonance by
thousands of times the linewidth, which is to say it is gone: this dataset
resolves the two halves as two of its own four lines. Between 8 and 15 per cent
of atoms decay AT LEAST ONCE while crossing the beam, the two ends being the
signal-weighted average over the collection volume and the value on the beam
axis, so a real fraction of them leave the line while being measured. Only a
share of those decays actually lands in the other half, and that smaller
fraction is the pumping number quoted later in this document. That shortens
the effective time an atom spends contributing, and a shorter time means a
broader line ([fig23](../../figures/fig23_hyperfine_pumping.png)).

**3. Those two effects broaden the line in exactly the same way the light shift
does, and nothing this dataset can vary tells them apart.** All three grow as
the square of the drive power. All three also grow as the fourth power of the
inverse spot size. A power sweep cannot separate them and neither can a change
of focus, because they move together under both knobs. This is not a
statistical problem that more data would fix. It is structural. What does
separate them is that the two companions broaden the line **without moving
it**, while the light shift also drags the line centre. So the way out is to
measure the centre, which needs a laser lock that holds still, which the 2025
sitting did not have. That is the single most valuable thing a further sitting
would add, and section 5 costs it.

The consequence for the published numbers is stated plainly wherever they
appear: the light-shift bounds are **loose by a measured factor**, 2.8 on one
construction and 2.21 on the other, because the model behind them contains the
light shift and neither companion. They are quoted as they stand, with the
looseness and its size attached, rather than tightened by injecting a
saturation law that is standard practice but not derived for this level
structure.

**4. The mirror behind the cell is read differently by the two things it
does.** The beam is sent through the vapour and reflected straight back, so the
atoms sit in a standing wave. The light shift follows the local brightness, and
an atom crossing many bright and dark fringes feels their average. The
two-photon excitation is different: only the pairing of one photon from each
direction is free of Doppler broadening, so the rate depends on the product of
the two beams rather than on their sum. The two combinations differ by exactly
the fringe contrast, which at this bench's 94 per cent return is a correction
in the fourth digit and at a poorer return is not. The useful half of the
asymmetry is that the rate does not care where the fringes sit and the shift
does, which is what a future design exploits by making the fringes move
([fig25](../../figures/fig25_retro_combination.png)).

**5. Three more things could have done the same damage, and were computed
rather than waved away.** Each was a real candidate and each came out small, but
the sizes are the point, because "negligible" without a number is not a result.

The atoms radiate on two infrared lines as well as the one we detect, at 1324
and 1367 nm, and those lines absorb just as strongly per atom as the detected
one does. Inside the driven column they cannot pump atoms back up, because the
upper level is kept fuller than the lower one by the drive itself. Outside it
they can, in a halo the trapped light creates, and there it feeds the signal
back at about one per cent at the hottest condition, somewhere between a half
and two depending on a distance nobody wrote down, and nothing at the coldest.
It rescales the brightness rather than the shape, so it lands on the amplitude
comparisons and not on the widths.

The cell is hot, so it glows, and thermal light could in principle drive the
same transitions. It cannot, by twelve orders of magnitude, and the reason is a
single mismatch: the glow peaks near 7 µm while every line in the cascade sits
below 3 µm. The one channel that is not astronomically small is a transfer out
of the excited state at 2.7 µm, worth two parts in a million, which is worth
naming only because it rises steeply if the cell is run hotter. The same
thermal field shifts the line by about 160 Hz at the hottest condition, which
matters to nobody measuring widths and will matter to whoever measures centres.

And the two isotopes in the cell do not have the same mass, so they do not cross
the beam at the same speed: ⁸⁵Rb is 1.2 per cent faster, and every fit here uses
one crossing width for both. That misassigns 11 kHz. It is almost entirely a
constant offset rather than something that grows with density, and the fits let
each line find its own width, so it never reaches the collisional number the
experiment is for. It reaches 0.4 per cent of one error bar.

### 1.3b How much model the data is allowed to buy

Every result here rests on a model with a definite number of parts, and
somebody had to decide how many. Add too few and the missing physics does not
politely vanish: it is absorbed by whichever fitted parameter can imitate it,
and that parameter is then quoted as a measurement of something else. Add too
many and the model starts fitting the noise, which looks like a triumph and
reproduces nothing.

The standard way to arbitrate is to charge a penalty per parameter and ask
whether the improvement in fit covers it. Two penalties are in common use. AIC
charges a flat 2 per parameter. BIC charges the logarithm of the number of data
points, so it grows as data accumulate. That difference is usually a technical
footnote, and here it is not, because this analysis makes complexity decisions
at wildly different data volumes: ten binned noise levels in one place, four
thousand samples in another, four hundred thousand in the joint fit. At those
three scales BIC charges 1.15, 4.2 and 6.5 times what AIC charges.

Six times is not a footnote. On the largest fits BIC demands six times the
evidence before it will admit a component, and a dataset this big is exactly
where a conservative penalty is most likely to be refusing something real. But
the two penalties answer different questions, one about predicting new data
and one about identifying a single true model, and neither question is
obviously ours, so this record does not crown either. It reports a small
PANEL of criteria, numerically, everywhere a complexity decision is made, and
treats their disagreement as a measurement: when every member selects the
same model the choice is robust across the conventions the panel spans, and
when they split, the model ranking is sensitive to the selection convention
at this sample size, which is a fact about the data worth publishing rather
than a tie to be broken by taste. A split cannot by itself justify adopting
the richer model. Adoption then needs an independent basis, a synthetic
recovery, a residual structure, a physical constraint, stated as such.

Two honest limits on how much this can matter. Where two candidate shapes carry
the same number of parameters, as the Voigt and cusp lineshapes here do, the
penalty cancels and no criterion can separate them: only the fit quality can, and
on this dataset it does not. And where a component buys either far more or far
less than any plausible penalty, every criterion agrees. That second case covers
the conclusion a sceptical reader should care most about, namely that the
AC-Stark parameter is not warranted on the 2025 data, which is why the result
is reported as a bound. That parameter buys almost no improvement at all, so no
penalty scheme prefers it, and the conclusion does not depend on this choice.

The mechanics, with the arithmetic worked, are in
[the statistics chapter](../methods/06_the_statistics.md) section 4.7a.

### 1.4 The expected size of the collisional coefficient

Self-broadening coefficients are published for the 5D and 7S states, and 6S is
the missing entry. A measured β_self(6S) closes that series.

**The expected size is now computed rather than borrowed**
(`rb5s6s/vanderwaals.py`). Both 5S and 6S are S states, so there is no resonant
dipole-dipole term and the leading interaction is van der Waals, which means
the coefficient follows from the same matrix elements that produced Δα(993),
continued to imaginary frequency: C₆ = (3/π)∫α_5S(iω)α_6S(iω)dω. That gives
**C₆(5S+6S) ≈ 2.9×10⁴ a.u.**

That absolute value should not be used on its own, and the reason is worth
stating. Run on 7S, the one nS state in Rb whose self-broadening has been
measured at all, the same code returns 4.40 kHz per 10¹² cm⁻³ against
Zameroski 2014's measured 5.4 (129 ± 11 kHz/mTorr, converted at 403 K), 18%
low. That is close to (a bit past) the
±10–15% the valence-only truncation and the mean-speed approximation explain
(addendum 23 of [PREREGISTRATION_RESULTS.md](../PREREGISTRATION_RESULTS.md)
records an earlier, larger gap and the coding error behind it). The
(C₆/ħ)^0.4 v^0.6 scaling itself is [Lewis 1980](../lit/lewis1980.md)'s
(*Phys. Rep.* **58**, 1 (1980)) primary phase-shift derivation for an n=6
potential, specialised from his eq. (4.15)–(4.18). His own quoted ~4%
Lindholm-Foley error bound is for a different comparison (a J=1 excited-state
angular average our S–S pair does not have) and is far too small to be the
18% seen here, so it rules that approximation out as the cause of the
residual gap.

The input to the phase shift is the difference potential, not the pair
coefficient: what dephases the line is ΔC₆ = C₆(5S+nS) − C₆(5S+5S), the
excited pair against the ground pair (a 2026-08-04 referee point the
record adopted, [notes/vdw_difference_potential_and_4d_channel.md](../notes/vdw_difference_potential_and_4d_channel.md)).
The Lindholm-Foley prefactor, the mean-speed step and the dropped core
and tail are common to the 6S and 7S rungs and divide out of the ratio.
The ground-pair subtraction is not that kind of error and does not
cancel, which is why the adopted ratio is a ratio of differences: with
ΔC₆(6S) = 24728 and ΔC₆(7S) = 79048 a.u., the ratio 0.3128 enters
through the (ΔC₆/ħ)^0.4 scaling and scales the *measured* 7S rate of
5.386 kHz per 10¹² cm⁻³ by 0.3128^0.4 = 0.628, giving

**β_self(6S) = 3.4 kHz per 10¹² cm⁻³** (±0.29 from the anchor
measurement alone, envelope ±10–15% overall),

an expectation anchored on a measurement of the same observable on the
neighbouring state. That anchor is contested, and the number above is the
Zameroski branch of it. [Wang 2025](../lit/wang2025.md) measure the same 760 nm
line at 0.32 ± 0.01 MHz/mTorr, about 0.014 in these units against Zameroski's
0.0054, a factor of 2.6, with no half-width or full-width convention stated on
either side ([FUTURE_TRANSITIONS_titsapph.md](../FUTURE_TRANSITIONS_titsapph.md)
§3.2). On Wang's value the anchor is near 9 kHz instead, and every standoff
quoted from it loosens by that factor. The recorded bound of 0.03–0.05 MHz per
10¹² cm⁻³ (four-point, 70/90/110/130 °C) sits **8–15× above it** on the
Zameroski anchor and about 3 to 6 times above it on Wang's, tighter
than the earlier three-point bound (was 0.2–0.4 MHz, 57–113× above), because
folding the 130 °C point into the headline extends the density lever from
×16.2 to ×52.5 (`scripts/run_beta_self.py`).

The identical machinery gives C₆(5S+5S) = 4180 a.u. against the literature
Rb₂ value of ~4691, 11% low, in
the direction and roughly the size the deliberately-dropped core predicts.
Everything in this subsection is an envelope, good to 10–15%, and the
±0.29 above is the anchor measurement's error alone, not a total. The
same note records the two open items larger than anything inside that
envelope: an R⁻⁶ exchange contribution estimated at a substantial
fraction of the direct term, which is not obviously common to the two
rungs and could move the ratio, and the 6S→4D inelastic channel, which
sits above the elastic anchor and never below, making the expectation
one-sided upward. The impact
prefactor is quoted from the pressure-broadening literature rather than derived.

That expectation also has an upper anchor from measurement. [Weller 2011](../lit/weller2011.md) measures the Rb **D1**
self-broadening coefficient at β/2π = (0.69 ± 0.04)×10⁻⁷ Hz cm³, or **69 kHz per
10¹² cm⁻³**. D1 is the *resonant* dipole-dipole case, the largest such
mechanism, because its two states are dipole-coupled to each other. 5S–6S
cannot work that way: both states are S, so there is no resonant dipole
coupling and the interaction is van der Waals, which should sit well below
that figure. So 69 kHz is a ceiling the 6S coefficient should fall far
under, consistent with the ~kHz expectation, and it makes the bound recorded
above loose by a factor one can now name rather than guess. The record already
has the design for this one, and it needs only the higher-density points of §5.

---

*[Why this line](01_why-this-line.md) · [Goals and prior art](03_goals-and-prior-art.md)*
