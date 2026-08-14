# Exploiting the tunable Ti:Sapph: future transitions and the papers they enable

**Status: a survey of physics options, not a plan of record (2026-07-13).** The
premise (recorded 2026-07-13): the drive laser is a **tunable Ti:Sapphire**, so a new
measurement session is not locked to 993 nm. It can reach *other* Rb two-photon
transitions, "as long as we can reach the frequency and the optics is fine at the
next frequency." This note maps what that buys us, grounded in the 2024–2026
landscape collected in [`docs/LITERATURE.md` §8](LITERATURE.md#8-the-20242026-landscape).

**The question.** The drive laser tunes, so what else could this bench measure,
and what would each option be worth?
**Takes.** [BIG_PICTURE.md](BIG_PICTURE.md) §1, for why this class of line is
worth the effort at all.
**Gives.** The candidate rubidium two-photon lines ranked, the computed magic
wavelengths, the one-colour three-photon rung and the scaling argument that
makes it the cliff regime rather than the delicate measurement it was proposed
as.
**Skip if.** You want the 2025 result. Nothing in this document is a
measurement, and several of its options are here because working them out was
the only way to find out they do not work.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.


![computed differential polarizability against wavelength, with the magic crossings marked](../figures/fig17_magic_wavelengths.png)

*The survey's own object, before the survey. Every option below is a different
rung of the same ladder, reached by tuning one laser, and this is the quantity
that decides whether a rung is worth reaching: the computed differential
polarizability, whose zero crossings are the wavelengths where a trap would
hold both states equally. The bracket printed under each crossing is its 16 to
84 per cent Monte-Carlo spread over the input matrix elements, so it is the
uncertainty of a calculation and not of a measurement. The spread is also
shaded on the axis, but at this scale it is narrower than the line marking the
crossing, so the bracket is what to read: 1.67 nm at the 1204 nm crossing
against 0.13 nm at 1340. The same figure appears again in
section 4 with the published measurement this document reads against it.*

## 1. The one-sentence picture

Our current line (5S→6S, 993 nm) is **little studied and not currently pursued elsewhere**. The only
active group (USAFA/Knize: Ayachitula 2024, and the earlier McLaughlin 5S–6S work)
reports *null* AC-Stark and density shifts at ~6 MHz resolution, so it is the
clean **demonstrator** of the drift-immune method. The **far more actively worked line is one
transition over**, at 778 nm 5S→5D, where 2024–2026 clock work (NIST/Andeweg,
Adelaide/Ahern, Feng, FEMTO-ST/Callejo, Gerginov, Li) suppresses the AC-Stark
shift **entirely with *active* schemes** (power modulation, dual interrogation,
two-color, magic-wavelength locking). **Nobody uses a passive lineshape-asymmetry
observable there.** A tunable Ti:Sapph lets us carry our reference-free method onto
that hot transition, so wavelength scans across the magic point become the measurement.

## 2. The transition menu the Ti:Sapph opens (verified)

Two-photon from 5S₁/₂, with wavelength = 2×10⁷ / E_upper[cm⁻¹]. "Intermediate detuning"
= how far the virtual one-photon level sits from the nearest real 5P (the physics
that sets how much a near-resonant intermediate distorts the two-photon lineshape,
Bjorkholm–Liao 1976). **Reachability is set by the installed SolsTiS optics set, not
a single continuous range**. See the laser-specific section below. The M-Squared datasheet
lists discrete sets 670–710 / 725–875 / 725–975 / 700–1000 / 950–1050 nm (custom
<700 or >1000 on enquiry), each ≤300 nm wide.

| upper | 2-photon λ | intermediate Δ | character | detection | SolsTiS optics set | competition |
|---|---|---|---|---|---|---|
| **5D₅/₂** | **778 nm** | **1.1 THz** | **near-resonant** (5P₃/₂) | 420 nm (6P→5S) | 725–875 / 725–975 / **700–1000** | **hot** (clock frontier) |
| **7S₁/₂** | **760 nm** | 10 THz | intermediate | 420 nm (6P→5S) | 725–875 / 725–975 / **700–1000** | light (Morzyński, Chui) |
| 8S₁/₂ | 697 nm | 46 THz | ~clean | 420 nm (6P→5S) | **670–710 only** (blue set) | none |
| 9S₁/₂ | 660 nm | 70 THz | clean | 420 nm (6P→5S) | custom <700 nm | none |
| **6S₁/₂** | **993 nm** | 75 THz | **clean** | 795 nm (5P₁/₂→5S) | **700–1000** (edge) or 950–1050 ← *current* | none (us + USAFA) |
| 4D_J | 1033 nm | 87 THz | clean | (5D→…) | 950–1050 / custom >1000 | 4D_J clock (2024) |

### A selection criterion the menu was choosing without: the thermal field

Added 2026-08-10, after the blackbody environment was computed for 6S. What
couples an upper state to the cell's own thermal radiation is not the drive
wavelength but **the gap to the nearest nP level**, and that gap SHRINKS as
the upper state climbs. So the occupation number at the coupling wavelength
spans five orders of magnitude across a menu whose entries differ by less than a
factor of two in drive wavelength:

| upper | 2-photon | nearest nP gap | hν/kT at 130 °C | occupation number | verdict |
|---|---|---|---|---|---|
| 4D_J | 1033 nm | 2.30 µm | 15.5 | 1.8e−7 | negligible |
| **6S₁/₂** | **993 nm** | **2.79 µm** | **12.8** | **2.8e−6** | **negligible** |
| 5D₅/₂ | 778 nm | 5.22 µm | 6.8 | 1.1e−3 | watch |
| 7S₁/₂ | 760 nm | 6.58 µm | 5.4 | 4.4e−3 | watch |
| 8S₁/₂ | 697 nm | 12.13 µm | 2.9 | 5.6e−2 | **matters** |
| 9S₁/₂ | 660 nm | 22.26 µm | 1.6 | 2.5e−1 | **matters** |

Upper-state energies are the verified two-photon wavelengths of the table above,
and the nP ladder is this package's own `LINES_5S`
(`scripts/run_campaign_conditions.py`). A quarter of a photon per mode at 9S
means blackbody transfer out of the upper state at a fair fraction of its own
decay rate, which is a systematic rather than a footnote, and it grows with cell
temperature exactly where the collisional programme wants to go. On 6S it is two
parts per million and stays there.

The reading for the menu: **6S and 4D are the two lines this consideration is
silent on, and the climb up the S ladder buys a shorter drive wavelength at the
cost of entering the thermal field.** That is not a reason to avoid 8S or 9S,
which have their own strong arguments above, but it is a term their budgets have
to carry and a reason to prefer a cooler cell for them.

The blunt consequence: **no single set covers everything.** The question is
which set is in *your* SolsTiS. If it is **700–1000 nm**, then 6S (993, near the red
edge), 5D (778) and 7S (760) are all reachable with **the same optics**, so the whole
near-IR program needs no laser-optics swap, only the 420 nm detection change. If it
is **950–1050 nm**, 993 and 4D (1033) are easy but 5D/7S require an optics-set swap.
8S needs the dedicated 670–710 blue set. 9S (660) and any >1000 work are custom.

### Your laser (M-Squared SolsTiS + Coherent Verdi V18 @ 18.5 A)

- **Pump is not the limiter, the optics set is.** The Verdi V18 delivers up to
  **18 W at 532 nm** (datasheet-confirmed). Whether 18.5 A is your full-power point
  or a set-point, that is a *generous* pump for a SolsTiS (which needs far less), so
  tuning range is fixed by the installed BRF/mirror set, not by pump. Ample pump is
  exactly what buys usable power at a set's *edges*, which is how you reach 993 nm
  at the top of a 700–1000 set, and what the large-S₀ regime Paper A needs.
- **Tuning mechanism** (why "within a set it's continuous"): motorized
  birefringent filter (coarse, spans the whole set) + a 320 GHz-FSR etalon +
  cavity PZT (fine), continuous within the set and with no realignment.
- **Two things to check on the actual unit** (they decide the whole plan):
  1. **Which optics set is installed.** Read the config label or M-Squared sheet,
     or just tune to the bluest and reddest points it will lase. If the blue end
     reaches ≲780 nm, 5D/7S are same-set (only a detection swap). If it starts at
     ~950 nm, 5D/7S need an optics-set change (M-Squared swap, non-trivial).
  2. **Output power at 760–778 nm vs at 993 nm.** A 700–1000 set gives *more* power
     mid-band (760–778) than at the 993 edge, which is good news, since the 5D/7S work would run
     with *more* S₀ headroom than the current 6S work, which is what the asymmetry
     signal (∝S₀³) needs.
- You already reach **993 nm** with this pump, so your set reaches at least to 993
  (consistent with 700–1000 or 950–1050). Running the V18 near max at 18.5 A is
  consistent with holding that red edge.

Three things fall out. (i) **5D and 7S sit in the Ti:Sapph sweet spot** (more power,
easier lock than the 993 nm red edge). (ii) **The whole upper ladder shares ONE
detection channel**, 420 nm (6P→5S blue fluorescence), which serves 5D, 7S, 8S *and* 9S,
because they all cascade through 6P. Only 6S is the near-IR (795 nm) outlier. So
the detection swap noted above (the 795 nm filters → a 420 nm bandpass + a
blue-sensitive PMT) is a **prerequisite for every upper-ladder transition**, and one
swap serves all four (see §Detection below). (iii) The intermediate
detuning now spans **~68×** across a five-rung ladder 5D→7S→8S→9S→6S (1 → 75 THz),
a controlled sweep of intermediate-state admixture in one apparatus (§Paper C).

### Detection: how much does changing the 795 nm filters help?

A lot, but as an **enabler rather than an optimisation**. The 6S work detects the
6S→5P→5S cascade at **795/780 nm** (near-IR). Every *upper* transition (5D, 7S, 8S,
9S) instead cascades **through 6P**, emitting **420 nm** (6P→5S, blue), a channel
the current near-IR path does not pass. So:

- To see *any* of the upper-ladder transitions at all, the detection filters must
  change to a **420 nm bandpass** (plus a PMT/APD with useful blue quantum
  efficiency, since many near-IR-optimised detectors are poor at 420 nm). This is a
  hard requirement. It cannot be trimmed or optimised around.
- **Corrected 2026-08-03 (see §3.2): the requirement above is not hard for 7S,
  and probably not for 5D either.** Wang *et al.* (2026) read the 5S→7S cascade on
  five channels at once and measure the branching, normalised to 780 nm, as
  1 : 0.64 : 0.52 : 0.35 : 0.20 for 780 / 741 / 795 / 728 / 420 nm, which puts
  420 nm last of the five ([wang2025](lit/wang2025.md)). The 741 and 728 nm
  lines are the direct 7S→5P decays, at 741.02 and 728.20 nm from the same NIST
  energies this repository uses for its polarizability sums, and the 780 and
  795 nm lines are the D-line terminals the present chain already works in. Cao
  *et al.* 2025 likewise read 5D₃/₂ on 795, 762 and 420 nm
  ([cao2025](lit/cao2025.md)). What is still open for 7S is a datasheet
  question of the same kind asked in the other direction just below: whether the
  installed 795 nm passband passes those lines, and whether it blocks a 760 nm
  drive.
- The payoff is broad: **one 420 nm path serves 5D, 7S, 8S and 9S together** (all
  via 6P→5S), so a single detection upgrade reaches the whole upper program.
- Caveat on signal: the 420 nm branching ratio is favourable for 5D and 7S but
  **dilutes for 8S/9S** (more open decay channels), compounding their blue-edge
  Ti:Sapph disadvantage, so 5D/7S are the high-yield targets and 8S/9S the reach.
- Practical check, now answered (experimenter-confirmed): the present 795 nm
  optics are a **passband stack**
  (~50 dB, `DATA.md`), not a pump-rejection notch, so this is the simple branch:
  the stack is swapped wholesale for a 420 nm bandpass, and no separate
  760–778 nm pump-blocking edge has to be sourced, provided the replacement's
  out-of-band blocking at 993 nm is specified (check the datasheet, don't assume:
  a visible bandpass is not obliged to block deep IR).

- **A note for the 6S line itself: a trapping-free 1.3 µm option.** The 6S cascade's
  *first* step, 6S→5P, emits at **1.32/1.37 µm**, and unlike the 780/795 nm D-line
  photons (ground-resonant, hence radiation-trapped in the dense cell), the 1.3 µm
  photon is resonant with nothing populated and escapes freely. Detecting it (an
  **InGaAs** detector, whose single-photon sensitivity is below a Si PMT's, plus hot-cell
  IR-background filtering) is a **trapping-free** amplitude channel, and the
  **795-vs-1.3 µm ratio discriminates a real degeneracy-law/amplitude deviation from
  a radiation-trapping artifact** (`PLAN.md` §8). The IR-cascade-to-beat-trapping
  trick is established on the sibling line by Hassanin et al. 2023 (5D→5P) and Beard
  et al. 2024 (5D→6P, 776 nm), so it is proven rather than speculative. Orthogonal to the
  420 nm upper-ladder swap, this is a 6S-detection refinement and not an enabler.

Net: the filter swap is required once to reach the upper ladder, and it is a
*cheap, one-time* cost (one blue detection path) for a *large* payoff (four new
transitions, including the hot 5D clock line).

**But "cheap" describes the hardware and not the risk. The risk is the noise
floor, which has to be measured rather than assumed** (2026-07-26). M1's fitted
law is σ² = a² + b·V: a detector floor plus a Poisson term. Which of the two
dominates sets how signal-to-noise responds to a *fainter* line, and the two
answers differ by a square:

- above the crossover V\* = a²/b the line is **shot-limited**, SNR ∝ √S, so a
  10× weaker signal costs only ~3× in SNR.
- below it the line is **floor-limited**, SNR ∝ S, and the same 10× deficit costs
  the full 10×.

That distinction decides feasibility for any dimmer configuration, and it is not
a small effect: across the 32 archival conditions **V\* spans 2–258 mV**
(median ≈ 9 mV, `results/noise_model.csv`), so even one detection chain
straddles both regimes. The 795 nm path happened to land shot-limited over the
whole archival range. The faintest line, 20 mV, still sits above the median
crossover, which is *why* the dimmest 70 °C dwells were fittable at
SNR ≈ 16. **A blue chain inherits none of that.** Blue-sensitive photocathodes,
different dark rates and a different filter stack move both a and b, and a
420 nm path landing at the high end of that V\* range would be floor-limited
exactly where an upper-ladder line is faintest.

**The check is a re-run of M1 on the new path, not new analysis:**
`rb5s6s.noise.condition_noise_model` fits a and b from a handful of repeats, so
the blue chain's V\* can be measured on the bench with a lamp, the filter and the
detector, before any transition is attempted. Doing it first converts the
detection swap from an assumption into a number, and it is the cheapest
derisking step on this page.

## 3. The case for running more than one line

The menu above says what is reachable. This section says why running more than
one rung would be worth the sessions, in four parts. Each part names the
measurement, the published number it would be tested against, and the module in
this repository it would test. The status in the header is unchanged: nothing
below is scheduled, agreed or assigned.

### 3.1 778 nm as the calibration line

Section 1 argues that 5S→5D is the *topical* line. The argument here does not
depend on topicality at all. 5S→5D is the only rung of this ladder whose
environmental coefficients are published with error bars small enough to fail
against, which makes it the one line where running the passive machinery would
test the **method** rather than produce a number nobody can check.

| quantity | published value | source |
|---|---|---|
| self-broadening, 5S→5D₃/₂ | 40 ± 0.54 kHz/mTorr, FWHM stated, 1.3% relative | [cao2025](lit/cao2025.md) |
| the same, in this repository's units | ≈0.0018 MHz per 10¹² cm⁻³ | [cao2025](lit/cao2025.md) |
| foreign-gas broadening and shift, 778 and 760 nm | first reported there | [zameroski2014](lit/zameroski2014.md) |
| Δα against wavelength, 770–800 nm | magic wavelength 776.179(5) nm | [hamilton2023](lit/hamilton2023.md) |
| 5P₃/₂–5D₅/₂ reduced matrix element | 1.80(6) a.u. | [hamilton2023](lit/hamilton2023.md) |

Running the passive machinery at 778 nm would produce the same three
observables the 993 nm work produces, width against power, centre against power
and the third cumulant, against values another group has already measured to
better than 2%. A method that reproduced 40 kHz/mTorr and 776.179 nm would have
been calibrated against the field's own numbers. One that did not would have
been caught. Neither outcome needs a new coefficient, which is what separates
this from Paper B.

![computed differential polarizability against wavelength, with the magic crossings marked](../figures/fig17_magic_wavelengths.png)

*What a magic wavelength is, and what this repository can and cannot say about
one. The curve is the computed differential polarizability of the 993 nm
transition, and a crossing of zero is a wavelength at which a trap shifts both
levels equally. The crossings here are calculated and unvalidated, which is the
whole reason the section below reads one published measurement so carefully.
That measurement is on the 778 nm line rather than this one, so it validates
the method of getting such a number against a bench and not these crossings.*

**What the wavelength scan actually is, from the held Hamilton PDF.** The scan
is real and it is not a scan of the drive. Hamilton's clock is driven by *fixed*
780 nm and 776 nm lasers locked to the two-photon line, and the magic wavelength
is measured with a **third** tunable Ti:Sapph, 760 to 800 nm, that illuminates
the same cell, perturbs the clock, and is read out as a frequency change of the
778 nm clock output against a comb referenced to a ULE cavity. Two things
follow. The single-colour drive at **778.104 nm** (computed in §3.4) is pinned
by the resonance and cannot be tuned, so the field scanned across 776.179 nm is
the *perturbing* one, not the drive. And that is exactly the configuration in
which the passive channel would substitute for hardware: Hamilton needs a comb
and a cavity to see the induced shift, and the asymmetry channel would read the
same shift off the lineshape, so the scan across a wavelength already measured
to 5 pm would be the measurement, with no frequency reference in the chain.
Section 4 (Paper A) states this as a scan of the Ti:Sapph *drive*, and that is
what this paragraph corrects.

One condition, stated because the closed form depends on it. The distribution
f(s) closes because the shift and the signal weight come from the **same** beam,
s ∝ I and weight ∝ Iⁿ. With a separate perturbing beam the two intensities are
different functions of position, and the closed form survives only if the two
beams are mode-matched over the collection volume. Otherwise the map has to be
recomputed for the overlap of two profiles, which the machinery here supports
and has not been asked to do.

### 3.2 7S closes the anchor loop this archive currently leans on

The archive's *expected* self-broadening of the 993 nm line is neither measured
nor purely computed. It is one external measurement carried across one rung by a
computed ratio. Verified by running `rb5s6s.vanderwaals.beta_self_anchored`
(2026-08-05):

    beta_self(6S) = beta_self(7S)_measured * [DC6(5S+6S) / DC6(5S+7S)]^(2/5)
                  = 5.386 * 0.3128^0.4
                  = 3.38 +- 0.29 kHz per 1e12 cm^-3

    DC6(5S+nS)    = C6(5S+nS) - C6(5S+5S)

with C₆(5S+6S) = 28908 a.u., C₆(5S+7S) = 83228 a.u. and C₆(5S+5S) = 4180 a.u.
from the module's own Casimir-Polder integrals, and 5.386 kHz per 10¹² cm⁻³
being Zameroski's measured 129 ± 11 kHz/mTorr converted at 403 K. Exactly one
number in that chain comes from outside. The archival bound sits 8.5 to 14.6
times above that expectation. The rounded 8 to 14 quoted elsewhere in the
portfolio predates the correction below and is due to become 8 to 15.

**Why the subtraction.** The impact phase is set by the difference between the
upper- and lower-state interactions with the ground-state perturber, not by the
upper state's coefficient alone, so the ground-pair term enters both rungs and
does not cancel between them. That was corrected on 2026-08-05 after a referee
raised it, and it moved the anchor from 3.53 to 3.38, 4.1 per cent and inside
the quoted error. `rb5s6s/vanderwaals.py` carries the adjudication and its
Lewis 1980 sources, and
[the difference-potential note](notes/vdw_difference_potential_and_4d_channel.md)
carries the working.

**That one external number is contested.** Wang *et al.* (2026) measure
self-broadening on the same 760 nm 5S→7S line at 0.32 ± 0.01 MHz/mTorr, about
0.014 MHz per 10¹² cm⁻³ against Zameroski's 0.0054, a factor of 2.6
([wang2025](lit/wang2025.md)). Wang states no HWHM/FWHM convention anywhere in
the paper, so a factor of two of that gap may be bookkeeping rather than
physics, which still leaves two published values disagreeing by far more than
their quoted errors. The quantity this archive's expected β_self rides on
therefore has two numbers and no adjudication. Measuring 7S here, with the
convention stated, would replace the choice between them with a rate from the
same instrument that measured 6S.

**And the ratio would become the test.** Once β_self(6S) and β_self(7S) were
both measured on one bench, the comparison to make is the *ratio*, and the ratio
is the part the van der Waals module does well: the Lindholm-Foley prefactor,
the mean-speed approximation and the dropped core and tail are common to the two
states and cancel in it. The module predicts

    beta(6S) / beta(7S) = 0.3128^0.4 = 0.628

A measured ratio would test the C₆ machinery. A 6S measurement on its own keeps
leaning on it. The absolute check already on record is of a different kind and
is weaker: run on 7S the module predicts 4.40 against the measured 5.39 kHz per
10¹² cm⁻³, 18% low, just past the 10 to 15% level the dropped core and tail
plus the mean-speed step account for. That tests the absolute scale at one n. A
ratio tests the n dependence.

**7S may also be the cheapest rung on this bench rather than the second
cheapest.** The Detection subsection above calls a 420 nm path a hard
requirement for every upper-ladder transition. For 7S it is not, and the
correction is recorded there. Wang's five-channel measurement puts 420 nm last
of five, and the two brightest channels are the D-line terminals the present
near-IR chain already works in. If the installed passband stack passes them and
blocks a 760 nm drive, both datasheet questions rather than physics, then 7S
would need a laser retune and no new detection path.

### 3.3 The ladder is worth more than its rungs

A single environmental coefficient constrains a calculation at one value of n.
A series in n constrains the n dependence of the matrix elements behind it,
which is the sharper object, because a calculation can be tuned to reproduce one
number and cannot be tuned to reproduce a slope it did not predict. What follows
separates what this repository can already verify from what it can only map.

**Self-broadening: exponent verifiable, two points in hand.** The relation
β_self ∝ C₆^(2/5) is not assumed here. It is the n = 6 case of the Anderson
phase-shift cross-section, Lewis 1980 §4.2 eq. (4.15) to (4.17), written out in
`vanderwaals.beta_self_vdw`. The C₆ side is computed rather than borrowed.
Between the 6S and 7S rungs the module's own Casimir-Polder integrals give
C₆(5S+nS) growing as **n\*^3.5** (28908 to 83228 a.u., with n\* = 2.845 and
3.856 from the NIST term energies and the Rb ionization limit, or 3.54 if a
fixed quantum defect of 3.131 is used instead). The quantity the broadening
law reads is the difference against the ground pair, which grows a little
faster because the same 4180 a.u. is subtracted from both, **n\*^3.8** (24728
to 79048 a.u.), so β_self would grow as **n\*^1.5** across the same step. Two points give a local slope. A third
measured rung would turn it into a fitted exponent with an error bar, and that
is the whole difference.

**This corrects the parenthetical in §5, Paper B.** That bullet used to give
"C₆ ~ n\*⁷". n\*⁷ is the scaling of the excited state's own *polarizability*,
and this repository reproduces it: the module's static values 318.3, 5167 and
32411 a.u. for 5S, 6S and 7S grow as n\*^6.0 across the 6S to 7S step. C₆ for a
ground-plus-excited pair is a different quantity, because the London form
carries the excited state's energy denominator as well as its polarizability,
and both the local 3.5 computed here and the n\*⁴ that estimate gives
asymptotically sit well below 7.

**Differential polarizability: two rungs computed, and opposite in sign.**

| rung | drive λ | Δα = α_upper − α_5S | note |
|---|---|---|---|
| 5S→6S | 993.418 nm | −1145 a.u. | sign under dispute, THEORY_NOTE §5 |
| 5S→7S | 760.126 nm | +4372 a.u. | independent line list, Safronova 2004 |
| 5S→5D₅/₂ | 778.104 nm | ≈ +28600 a.u., anchored not recomputed | J = 5/2, tensor term dropped, magnitude only |

Two consequences. The magnitude is 3.8 times larger at 7S, and the ramp
observables are powers of S₀ ∝ Δα, so at equal intensity 7S is the more
favourable line for the shape channel. The sign is opposite, and it is a
prediction of the same sum-over-states machinery whose 6S sign is disputed. A
bench that measured both signs would be testing that machinery's structure
rather than adjudicating the 6S dispute, because a convention error would flip
both together. 5D is left un-recomputed on purpose (`polarizability.py`,
Ti:Sapph ladder block header), and Hamilton's measurement is adopted instead.

**The anchored 5D entry, and what it is allowed to be used for.** The third row
is not a sum over states. It is two statements with no free parameter, which is
what the adopted measurement licenses. Hamilton's measured 776.179 nm magic
wavelength is where Δα crosses zero. Moving from there to the 778.104 nm drive,
Δα changes by the near-resonant 5P₃/₂–5D₅/₂ term evaluated with Hamilton's own
measured 1.80 a.u. element, minus the change in α₅S, which the module computes
and which is itself steep here because the drive sits 2 nm from the D2 line.
Every slowly varying part of α(5D₅/₂) cancels between the two evaluations, so it
never has to be known. The construction is scalar only, it drops the tensor term
and the hyperfine dependence Hamilton measures, and it is evaluated at the drive
and nowhere near the pole. It sizes a drive-power ceiling. It is not a
polarizability and nothing else in this file uses it as one. Computed in
[scripts/run_projections.py](../scripts/run_projections.py), carried with its
assumption set in [results/projections.csv](../results/projections.csv).

**What the three differentials cost in drive power.** They span a factor of
twenty-five, and the light shift is what limits the drive long before the
available power does. Fixing the ceiling at the power where the on-axis shift
reaches one tenth of the width the archive measures, at the archive's own 64 µm
waist and 0.94 retro ratio, gives the 993 nm ceiling of 332 mW, the 760 nm
ceiling of 87 mW and the 778 nm ceiling of 13 mW. The 993 nm figure sits above
the campaign's own 225 mW maximum, so that rung is not capped at all. The other
two are, and because the two-photon rate goes as the square of the intensity, a
width precision measured at the archive's power degrades in proportion when the
drive is capped. On the 760 nm rung the projected self-broadening precision goes
from about 8 to about 18 kHz per mTorr and the adjudication keeps a ceiling
margin of 2.0, so it still holds and 6.7 repeats of the design would buy the
uncapped precision back. On the 778 nm rung it goes from about 8 to about
108 kHz per mTorr and the factor-two test drops to a ceiling margin of 0.12,
which is the one result in this file the ceiling takes away. About 66 repeats would
restore its power. The ceiling goes as the square of the waist, so a looser
focus raises it, at the cost of transit width and of the density lever, and this
file does not cost that trade.

**Magic wavelengths: a family that moves along the ladder.** The way the zero
crossings of Δα move with n is a map in its own right, and the three rungs this
repository can speak to do not look alike.

| pair | crossings found | character |
|---|---|---|
| 5S–6S | 1203.9 nm (α = +547 a.u.), 1287.9, 1339.6 nm | 1204 is far from every 6S resonance and traps both states, the other two sit among the 6S–5P and 6S–7P lines |
| 5S–6S, inside the Ti:Sapph band | 790.1 nm (α = −244 a.u.) | between the 5S D lines, 0.1 nm from the ground-state tune-out, so a ground-state vapour absorbs it hard |
| 5S–7S | 742.6 nm (α = −2667 a.u.), 790.2 nm (α = −410 a.u.) | 742.6 sits 1.6 nm from the 5P₃/₂–7S pole at 741.0 nm, an *excited*-state transition that a ground-state vapour does not absorb, but Δα is steep there and the crossing position is correspondingly sensitive. 790.2 carries the D-line problem above |
| 5S–5D₅/₂ | 776.179(5) nm, measured | 0.2 nm from the 5P₃/₂–5D₅/₂ resonance, also an excited-state transition, and 1.9 nm from the 778.104 nm two-photon wavelength |

So the family runs from far-infrared and isolated at 6S, to in-band but pressed
against steep excited-state resonances at 7S, to in-band and already measured at
5D. What the ladder would map is not one number but where each crossing sits
relative to the resonances that make it hard to use. Neither 5S–7S crossing is a
usable trap wavelength, and both are zero crossings of the 5S→7S light shift,
which is what the asymmetry channel reads, so both are scan targets even where
they are not trap targets. As at 5D, they are reachable with a *perturbing*
field and not with the drive (§3.1), since the 5S→7S drive is pinned at
760.126 nm.

Two caveats on those searches. The windows were 700 to 1500 nm for 5S–6S and
700 to 1000 nm for 5S–7S, and nothing outside them was looked for. And the
742.6 nm crossing sits at the search's own 1.5 nm pole guard, so read its
position as indicative.

**What stays qualitative.** This repository carries no 8S line list and no
independent 4D or 5D polarizability, so no exponent is quoted for those rungs.
What they would supply is the third and fourth points that turn every two-point
slope above into a fitted exponent.

### 3.4 What a doubling stage would add (options map)

A second-harmonic stage on the Ti:Sapph reaches the single-photon UV resonances
out of the 5S ground state. The wavelengths below are computed from the NIST
term energies this repository already carries in `rb5s6s/polarizability.py`
(`LINES_5S`), as 10⁷/E, in vacuum, to 0.1 nm.

| line | term energy (cm⁻¹) | UV output | Ti:Sapph fundamental |
|---|---|---|---|
| 5S→6P₃/₂ | 23792.591 | **420.3 nm** | 840.6 nm |
| 5S→6P₁/₂ | 23715.081 | **421.7 nm** | 843.3 nm |
| 5S→7P₃/₂ | 27870.11 | **358.8 nm** | 717.6 nm |
| 5S→7P₁/₂ | 27835.02 | **359.3 nm** | 718.5 nm |

The optics-set question of §2 does not go away, it is re-asked at the
fundamental. The 6P pair needs 840.6 or 843.3 nm, inside the 725–875, 725–975
and 700–1000 sets. The 7P pair needs 717.6 or 718.5 nm, which is inside
700–1000 only, above the 670–710 blue set and below the 725 nm edge of the two
mid sets.

What the UV would and would not be for:

- **Not a lineshape target in the sense used elsewhere in this file.** A
  single-photon line is Doppler broadened. At 400 K, near the top of the
  archive's 70–130 °C range, the 5S→6P₃/₂ Doppler FWHM is **1.10 GHz** and the
  5S→7P₃/₂ is **1.28 GHz**, against the 3.49 MHz natural width the 993 nm work
  fits. The passive shape method assumes a Doppler-free line and does not carry
  over without a sub-Doppler scheme.
- **Not a collinear Doppler-free three-photon route either, although it looks
  like one.** Three photons are the only way to reach an **F** state from
  5S₁/₂, since one photon reaches P and two reach S and D, so a doubled beam
  invites the question. It does open exactly one first-order-Doppler-free
  collinear combination, two fundamental photons one way against one doubled
  photon the other, k + k − 2k = 0, with no three-beam geometry needed. The
  same condition fixes the energy sum at 4ℏω rather than 3ℏω, and 4ℏω clears
  the Rb ionization limit (33690.81 cm⁻¹) for every fundamental blue of
  **1187.3 nm**. The reddest catalogue set stops at 1050 nm, where the sum
  overshoots by 4404 cm⁻¹, and the present 993.418 nm drive overshoots by
  6574 cm⁻¹. So on this laser the combination would photoionize rather than
  excite a bound state, and the ion collection it would need for detection,
  which doubles as its own REMPI background, would return a smooth yield and
  no line. It would reopen only for a fundamental redder than 1187.3 nm, which
  no listed set covers.
- **A resonant source at the wavelength the upper ladder detects on.** The
  Detection subsection asks for the blue chain's noise model to be re-measured
  before any upper-ladder transition is attempted, because a 420 nm path landing
  floor-limited would cost the full factor rather than its square root. A
  doubler at 420.3 nm puts light of exactly that wavelength into exactly that
  cell, which is the source that measurement wants.
- **A resonant density handle.** Both external self-broadening entries of §3.1
  and §3.2 infer density from a vapour-pressure curve rather than measuring it,
  and the archive's own density scale carries a 20% systematic. Resonant UV
  absorption on the same cell would be an independent column-density read.

Two-colour ladder options, from the same term energies:

- **5S→5P₃/₂ at 780.2 nm plus 5P₃/₂→5D₅/₂ at 776.0 nm.** Both legs sit inside
  one Ti:Sapph optics set, so a two-colour route to 5D would need two sources
  rather than two optics sets. This is Hamilton's scheme and Ahern's, and it is
  the configuration in which the drive wavelength becomes a free parameter
  (§3.1), because only the *sum* of the two colours is pinned.
- **5S→5P₁/₂ at 795.0 nm plus 5P₁/₂→6S at 1323.9 nm, or 5S→5P₃/₂ at 780.2 nm
  plus 5P₃/₂→6S at 1366.9 nm.** The first leg is in band and the second is not,
  so a two-colour route to the *current* line would need a source outside the
  Ti:Sapph. Those two second-leg wavelengths are the 6S–5P poles that bracket
  the 1339.6 nm crossing of §3.3.
- **6P→7S sits at 3.85 and 3.97 µm.** A 420 nm first leg opens no Ti:Sapph
  second leg to 7S.

**Status.** This subsection is an options map on the same footing as the rest of
the file. No doubling stage is on the bench, none of these wavelengths has been
produced here, and the feasibility questions of §6 apply to each of them
separately.

### 3.5 The one-colour three-photon rung, and the parabolic ramp

Proposed by the experimenter on 2026-08-09. Three photons of ONE colour from
5S reach an odd-parity state, and the reason to want that is not a new
coefficient but a new SHAPE. This archive's signal-weighted shift distribution
is $f(s)\propto|s|^{n-1}$ on $[-S_0,0]$ with $n$ the number of photons, so
$n=2$ gives the triangle the 993 nm work fits and $n=3$ gives a PARABOLA,
$f(s)=3s^2/S_0^3$. Its cumulants follow by the same direct integration:

$$\langle s\rangle=-\tfrac34 S_0,\qquad \mathrm{Var}=\tfrac{3}{80}S_0^2,\qquad
\kappa_3=+\tfrac{1}{160}S_0^3,\qquad g_1=\tfrac{2\sqrt{15}}{9}=0.861$$

so the intrinsic standardised skew is **1.52 times the triangle's 0.566**, on a
distribution that is simultaneously more concentrated (relative variance 0.0375
against 0.0556). A larger shape asymmetry on a tighter distribution is exactly
what the passive method wants, and `rb5s6s.lineshape.stark_ramp_axial_moments`
already takes `n_photon`, reproducing all three numbers at `n_photon=3` to
better than $10^{-3}$ (pinned in `tests/test_lineshape.py`).

**This does not contradict the doubled-beam paragraph above.** That paragraph
rules out the collinear $k+k-2k$ combination because its energy sum is
$4\hbar\omega$, which clears the ionization limit for any fundamental blue of
1187.3 nm. A one-colour scheme sums to $3\hbar\omega$ instead, which stays bound
across the whole useful band: for a fundamental between 950 and 1120 nm the sum
runs 26786 to 31579 cm^-1, below the 33690.81 cm^-1 limit by 2112 to 6905 cm^-1,
and only crosses it blue of about 890 nm.

**The candidate table.** Term energies from the committed line list where it has them, which already
carries 8P, 9P and 10P, and from NIST ASD otherwise, verified 2026-08-09. The
F-state quantum defect runs with $n$ rather than sitting at its asymptote, so a
fixed-defect estimate is 17 cm^-1 out at 4F and converges by 7F. The column that decides the rate is where the
TWO-photon virtual level $2E/3$ falls relative to a real state that couples to
the target, since that detuning is the second energy denominator.

| target | $E$ (cm^-1) | $\lambda_3$ (nm) | $2E/3$ from 6S | $2E/3$ from 4D | natural width |
|---|---|---|---|---|---|
| 8P1/2 | 29834.94 | 1005.53 | **-242** | +534 | 302 kHz |
| **8P3/2** | 29853.79 | **1004.90** | **-230** | +547 | 327 kHz |
| **5F** | 29277.78 | **1024.67** | -614 | **+163** | 1.51 MHz |
| 6F | 30627.97 | 979.50 | +286 | +1063 | |
| 9P3/2 | 30970.19 | 968.67 | +514 | +1291 | |
| 7F | 31441.72 | 954.15 | +829 | +1606 | |
| 10P3/2 | 31661.16 | 947.53 | +975 | +1752 | |
| 4F | 26792.10 | 1119.73 | -2271 | -1494 | |

Every candidate above sits inside the 950 to 1050 nm set this laser already
carries, so none of them needs the doubling stage. 4F needs a redder set.

**5F is the stronger target, and it is not the one the question named.** For 8P
the chain is 5S to 5P to 6S to 8P, and the near resonance is with the 6S state
this archive characterises, 230 cm^-1 away. For 5F the chain is 5S to 5P to 4D
to 5F, near resonant with 4D at 163 cm^-1, and BOTH upper dipoles are far
larger: 5P3/2-4D5/2 is the committed 10.90 a.u. against 6S-8P3/2 at 0.629, and
4D-5F is a near-hydrogenic D-to-F transition of order 10 to 20 a.u. The figure
of merit $|d_1d_2d_3|/(\Delta_1\Delta_2)$ puts 5F ahead by a factor of about
**21**, on an honest range of 10 to 40 once the unmeasured element and the choice
of 4D fine-structure partner are both allowed to move. A first pass here quoted
38 to 76, from a coarser treatment of the same two freedoms.

The trade is real and runs the other way on quality. 5F's natural width is
1.51 MHz against 8P3/2's 327 kHz, a factor 4.6, and the ramp is measured as a
distortion of the observed line, so 8P needs 4.6 times less $S_0$ for the same
fractional asymmetry. Reading the two together: **5F first, because a
three-photon rate is the thing most likely to make the experiment impossible,
and 8P3/2 as the precision follow-up once a signal exists.** 8P also carries a
programmatic advantage worth naming, that its second denominator is set by the
very state this archive has already measured, so the existing 6S numbers feed
its prediction directly.

**The Doppler problem, and it has a demonstrated answer.** A one-colour
three-photon line in a hot cell is Doppler broadened at three times the
one-photon width, about 1.38 GHz at 130 C, against natural widths of 0.3 to
1.5 MHz. Collinear geometry in a cell is therefore useless for shape work. The
fix is the STAR: three coplanar beams of equal $|k|$ at 120 degrees, whose wave
vectors sum to zero exactly, so the $(1,1,1)$ absorption channel is
first-order-Doppler-free AND recoil-free, the recoil vanishing because the net
momentum transfer is zero rather than merely small. The other channels are the
cost: $(2,1,0)$ leaves net $|k|=\sqrt3 k$ and $(3,0,0)$ leaves $3k$, so a sharp
Doppler-free peak sits on a pedestal 1.7 and 3 times the one-photon Doppler
width, which is the three-beam version of the same-beam pedestal the
retro-reflected two-photon geometry already has.

This is not speculative. Grynberg and Cagnac gave the general
$\sum \mathbf{k}_i\cdot\mathbf{v}=0$ theory (Rep. Prog. Phys. 40, 791, 1977),
Ryabtsev and co-workers proposed the star geometry for three-photon Rydberg
excitation (Phys. Rev. A 84, 053409, 2011), and a 2025 warm-vapour experiment
measured the narrowing directly, 4.36(6) MHz collinear against 1.18(8) MHz in
the tailored geometry with three times the excited density
(arXiv:2506.04504). All of that work is THREE-COLOUR through real stepwise
intermediates. **A one-colour three-photon 5S to nP or nF measurement in Rb was
not found in the literature**, and the difference is structural rather than
cosmetic: at 1005 nm the single-photon detuning from 5P is tens of terahertz, so
this is a genuinely virtual-intermediate process with no real intermediate
population, which is what the shape method needs and what the stepwise schemes
do not provide.

**The cold-atom route is the alternative, and it is weaker than it looks.** At
10 microkelvin the one-dimensional rms speed is 3.1 cm/s, so a COLLINEAR
one-colour scheme keeps a residual three-photon Doppler width of about 92 kHz
at one sigma, 215 kHz full width. Against 8P3/2's 327 kHz that is a 20 per cent
broadening rather than a negligible one, and collinear geometry also carries a
net recoil shift $(3\hbar k)^2/2M = 20.4$ kHz that the star geometry does not
have at all. For 5F, whose 1.51 MHz width dominates, the cold-atom residual is
negligible. So cold atoms alone suffice for 5F and do not quite suffice for 8P,
while the star geometry suffices for both and works in a cell.

**What is not settled here.** The 4D-5F dipole is an estimate rather than a
value, and it carries the whole factor-of-two spread in the ranking. The
detection path for each target is unexamined, and it decides feasibility as much
as the excitation rate does. Whether a fourth photon ionizes the excited state
fast enough to matter for detection is unasked. And the pedestal changes the
fitting problem the shape method solves, since the archive's own machinery
assumes a Doppler-free line with no broad background under it.

### Addendum, 2026-08-09: four things this section was silent about

Written after an adversarial pass over the section. Two of the four change what
the rung is for, so they are here rather than in a note.

**The drive's own light shift is not a small distortion, and this reframes the
rung.** The section motivates a one-colour three-photon transition partly because
its shift distribution is parabolic where the two-photon one is linear, and it
treats that as a subtle asymmetry to be measured on a natural-width line. The
scaling forbids it. A three-photon Rabi frequency goes as the intensity to the
three halves while an AC Stark shift goes as the first power, so the ratio of rate
to shift is fixed by the atom and not by a knob: the shift can be made small only
by making the rate smaller still. And the near resonance that makes the rate
viable is the same small denominator that makes the shift large, so the two are
locked. Computed here from the ARC reduced elements and this section's own
detunings, the level repulsion between target and near-resonant intermediate
reaches the target's natural width at 740 W/cm^2 for 5F and 1.85e4 W/cm^2 for
8P3/2, against the 3497 W/cm^2 per arm the present 993 nm drive already runs at.
**The 5F target's own shift therefore exceeds its natural width at one fifth of
today's intensity, and a three-photon rate needs far more intensity than a
two-photon one, not less.** So the rung does not deliver a delicate parabolic
skew. It delivers the cliff regime by construction, the one PLAN.md item 6
describes as the shift greatly exceeding the linewidth and the ramp directly
visible. That is a legitimate and arguably easier measurement of a shift. It is
not the measurement this section proposed, and anything wanting a narrow line
from these levels, a frequency reference above all, is excluded rather than
merely degraded.

**The star geometry's ranking carries no geometric factor, and the missing factor
is asymmetric.** The figure of merit that puts 5F ahead by 21 is built from
reduced matrix elements alone. Because 5S has zero orbital angular momentum, the
matrix element to a target of orbital angular momentum L is carried entirely by
the rank-L part of the three-photon operator, and reaching L = 3 admits exactly
one path, the monotonic one through P and D. Three coplanar beams cannot all be
circularly polarized about the one distinguished axis, so in-plane linear
polarizations reach the maximally coupled route only through each photon's
circular component, an amplitude factor per photon and a rate suppression of
about eight. Nothing comparable bites the 8P channel, which is reachable at rank
one by two different intermediate sequences. An eightfold handicap alone would
take the 21 to about 2.6. Whether it inverts needs the full recoupling
calculation, which is not done here, but treating the geometric factor as one is
not defensible and the ranking should be read as an upper bound on 5F's advantage
until it is done.

**The quoted natural widths are 0 K values, and both targets have hyperfine
structure wider than them.** The 302, 327 and 1510 kHz in the table are
spontaneous-decay widths at zero temperature. At the cell's 110 to 130 C,
blackbody transfer widens them by 2.0 per cent for 5F and 4.2 to 5.2 per cent for
8P, small but worth labelling since everything else in this document runs at cell
temperature. The hyperfine structure is not small: 8P1/2 splits by exactly twice
its dipole constant, 64.2 MHz, and 8P3/2 spreads its four levels over some tens
of megahertz, both two orders of magnitude above the widths tabulated as though a
single line were being driven. Rb-85 adds its own manifold in a natural-abundance
cell. So 8P is a resolved multiplet to be assigned, not a line, which is a
detection and fitting problem rather than a rate problem. For 5F no measured
hyperfine constant appears in ARC's compilation or in the literature searched,
and the F-state trend in n suggests sub-megahertz to a few megahertz, which is
comparable to the 1.5 MHz natural width. That is an unmeasured input, and it is
now listed among them.

**The star geometry needs an alignment tolerance nobody has stated.** Closing the
three wavevectors to zero only cancels the first-order Doppler shift to the
accuracy of the closure. Keeping the residual below a tenth of the natural width
at the cell's 400 K needs the 120 degree vertices held to roughly 24 arcseconds
for 8P3/2 and 115 for 5F. Achievable, and a specification rather than an
afterthought.

## The same items costed

Everything above is a physics menu. Deciding bench time takes
cost, yield and risk instead, so this section restates the same items in
those columns, with the last naming the source class that reaches each rung's light-shift ceiling. Nothing below is scheduled, agreed or assigned. Every
duration is [PLAN.md](PLAN.md)'s own where PLAN.md costs the block, and is
marked as an estimate with its basis where PLAN.md does not. Every entry in
the last column is a projection rather than a result, computed in
[scripts/run_projections.py](../scripts/run_projections.py) from the
archive's own measured precision and PLAN.md's own session parameters, with
the assumption set behind each figure carried in
[results/projections.csv](../results/projections.csv).

| item | bench cost | what it would return | what could come back empty | projected precision | source that reaches the ceiling |
|---|---|---|---|---|---|
| beam profile w₀ | about an afternoon, no physics run (`PLAN.md` §9 D4, §4.1) | measured geometry under every absolute number in the archive, applied retroactively | nothing, but the number may not carry back to the 2025 bench | an intensity axis good to about 15 percent once the differential transit width is folded in | no line is driven, so no source question |
| fixed-lock cell session | about eight days at the cell, ordered so any prefix is useful (`PLAN.md` §9) | three bounds converted into measured coefficients (`PLAN.md` §1) | β_self may stay a bound, and the shape channel may stay below noise | 0.09 MHz on S₀(225 mW) from one morning of power cycling, and the expected β_self resolved at about 10 sigma | the Ti:Sapph on the bench, at 0.68 of the 993 nm ceiling of 332 mW, so this is the one rung the ceiling does not make it unnecessary. A diode-seeded ytterbium fibre amplifier would be at its band edge and that reach is unconfirmed here |
| 7S rung, 760 nm | a laser retune, and no new detection path if two datasheet questions answer favourably (§3.2) | a self-broadening rate that adjudicates two published values differing by 2.6 | a bound rather than a rate, and a blue detection build if the filter answer goes the other way | about 8 kHz per mTorr at the archive's own drive power, a fourfold margin over what the adjudication needs, and about 18 at the light-shift ceiling where the adjudication keeps a ceiling margin of 2.0 | an extended-cavity diode laser with a tapered amplifier clears the 760 nm ceiling of 87 mW, so the Ti:Sapph is unnecessary. No note in `lit/` states that amplifier's output at 760 nm, so the class is established practice rather than a held citation |
| 778 nm rung | a detection change plus a second source for the scan (§3.1) | the method tested against coefficients published to better than 2% | no new coefficient by design, and the scan needs two mode-matched beams | about 8 kHz per mTorr at the archive's own drive power, which is 20 percent of the published coefficient, and about 108 at the light-shift ceiling where the factor-two test drops to a ceiling margin of 0.12 | a 1556 nm fibre amplifier with second-harmonic generation, the compact-clock architecture of [feng2026](lit/feng2026.md) and [li2024b](lit/li2024b.md), at 2.3 times the 778 nm ceiling on that demonstration's own 30 mW, so the Ti:Sapph is unnecessary |
| O-band null at 1297.5 nm | one telecom-band diode and its wavemeter, no Ti:Sapph time, riding any cell session (§5.1, Paper D) | the 6S to 7P matrix element by frequency metrology where no measurement exists, a sign-reversal test of the asymmetry channel, and a calibrated shift injector | the delivered perturber intensity at the cell could undershoot, stretching the localization beyond the useful range | root located to about 26 pm at the projected 92 kHz shift precision, reading the 7P residue near 3% | a commodity O-band diode, no ceiling issue at these powers |
| wide-scan Doppler pedestal | an acquisition setting on any session that runs at all, no hardware and no lock quality | an in-situ gas thermometer and an in-situ retro ratio, on the same traces | the pedestal may not separate from the scattered-light background, and the area ratio is flat in ρ near one | the design reaches both in about two hours each, and section 8 gives the arithmetic and the assumptions | the drive itself, swept wide. The pedestal is 942 MHz wide on the transition axis at 130 °C, so no new source and no lock is involved |
| doubling stage | new hardware, none on the bench, unpriced | a resonant 420 nm source and an independent density read (§3.4) | nothing publishable on its own | not projected, since nothing here models its rates | the doubling stage is its own source, and a one-photon line carries no two-photon light-shift ceiling |

**How long the pedestal row takes, since the cell above only gives the total.**
The design pins the temperature in about 1.9 hours, to where the vapour curve's
22-fold leverage keeps the implied density inside the 20 percent scale
systematic, and it reaches the adopted retro ratio in about 2.1 hours. Both
figures are for the four-pedestal comb, and both are about sixteen times longer
on a single component.

**The wide-scan pedestal, and what the archive can already say about it.** The
retro-reflected drive makes two kinds of two-photon event. One photon from each
beam gives the Doppler-free line every number in this repository is fitted to.
Two photons from the same beam give a line broadened at the full 2kv, 942 MHz
wide on the transition axis at 130 °C, which sits under the narrow line as a
pedestal. Its width goes as the square root of the temperature and its area
against the narrow line's area is 4ρ/(1 + ρ²), so one wide trace measures the
gas temperature and the retro power ratio together. Both are quantities this
archive currently adopts rather than measures.

The cost is an acquisition setting. A gigahertz-wide feature does not care about
a megahertz of lock drift, so the scan needs no lock quality, no new source and
no new detection path, which is why the table above costs it against any
session that runs at all rather than against a session of its own. What it does
cost is time on the stack: the design pins the temperature in about 1.9 hours
and reaches the adopted retro ratio in about 2.1 hours, both on the comb of four
hyperfine pedestals, and both about sixteen times longer if only one component
is fitted.

The archive-side honesty. The 2025 windows span 85 MHz on the transition
axis, a tenth of the pedestal, so every archival trace samples the pedestal's
flat top and the linear baseline absorbs it as an offset. The archive can
therefore bound the retro ratio through that offset and can say nothing at all
about the width, which needs the session. Two further conditions travel with the
projection. The pedestal has to be separated from the scattered-light
background, which is not modelled, and the area ratio peaks at ρ equal to one
where its slope in ρ vanishes, so it is a weak lever on the very quantity it
measures and is symmetric under ρ to 1/ρ. Computed in
[scripts/run_projections.py](../scripts/run_projections.py).

**The beam profile.** `PLAN.md` §3 puts w₀ in stage 0, the systematic floor,
because S₀ ∝ 1/w₀² and the transit width rides on w₀, so a 10% waist error is
20% on Δα. The afternoon quoted above is PLAN's own allocation: §9 gives an
afternoon of D4 to a metrology block of knife-edge, camera and retro ratio,
and §4.1 gives half a day to the archival-geometry spot check. No atoms are
needed for it. What it returns is retroactive. Every waist-conditional
statement in the 2025 archive would sharpen in place, and the degeneracy
between transit width and laser width would collapse. The risk is not that
the measurement fails, since a knife-edge returns a number, but that the
number describes the present bench rather than the 2025 one. Carrying it
back needs the config-M spot check of `PLAN.md` §4.1, the archival geometry
plus one 130 °C point. If that bridge did not hold, nothing would be
retracted, because the archival statements are already published as
conditional on the measured waist.

**The fixed-lock cell session.** This is the full ask. `PLAN.md` §9 sizes it
at about eight days at the cell and orders it so that a truncation at any
point leaves the higher-priority conversions done, and the grades of §3 are
what a shortened session would fall back through. stage 0 is the systematic
floor, which is the ramp-monitor export, the beam profile and the retro ratio
measured in situ, and it converts the archival bounds whether or not a later
block runs. stage 1 is the fixed lock itself plus same-session 150 to 170 °C
points in interleaved temperature order, which is what would turn β_self from
a bound into a rate. `PLAN.md` §1 names the smallest tranche that converts
even one bound: a geometry-setup block plus the two opposite-order
temperature-grid days, D1 to D3, returning β_self or a much tighter bound
along with the first fixed-lock laser width. stage 2 buys handle strength
through a second and tighter waist. stage 3 is sampling that refines without
enabling, and it is the first thing to cut. The analysis end carries no
development risk: the archival pipeline ingests session data unchanged, so
what a session buys is shots rather than software.

What could come back empty there. β_self is intrinsically a few kHz per
10¹² cm⁻³, and `PLAN.md` §1 states the deliverable as a modest first
measurement or a much tighter bound rather than a precision number. At the
archival block-noise floor the hot points reach only about 1 to 3σ per block,
and only the interleaving and the per-trace power logging take the same
signal to about 3 to 12σ, so both halves have to work. The third cumulant
would reach detection only at the tighter waist and only with the collection
geometry measured in the same session, because the axial average over the
collection window sets both its size and its sign. A lock that dropped out
would repeat 2025. Even then the geometry blocks would still convert the
archival bounds, the fixed-lock laser width would be a number the archive
does not contain, and the centre pull needs minutes-scale lock stability
rather than all-night stability, which makes it the least exposed of the
three conversions.

What that reads as, projected on the archive's own numbers. One morning
of randomized power cycling with the four lines interleaved, at the
per-trace centre precision the archive measured and the held-lock drift
rate it bounded, would give 0.09 MHz on S₀(225 mW). That detects a shift
of the predicted 0.35 MHz size at 3.8 sigma, and separates the two
disputed polarizability signs at 8 sigma if the shift is that size. Which
sign the pull has needs no intensity calibration. How far apart the two
signs sit does, because a common scale error moves both predictions
together. One hour instead of one morning halves the reach to 1.9 sigma.
On the width
side, five temperature blocks per peak reaching 170 °C with the block
scatter cut fourfold would put the expected β_self resolved at about
10 sigma, against 3 sigma with the scatter uncut, which is the
quantitative form of the claim that both halves of the prescription are
load-bearing. Every figure here is conditional on the cold-spot lag the
archive prefers at face value, and the coefficient itself would still
carry the 20 percent density scale until the absorption channel measures
the density directly.

**The 7S rung at 760 nm.** On the corrected detection argument of §3.2 this
is the cheapest new line rather than the second cheapest. Wang's
five-channel branching puts 420 nm last of five, and the two brightest
channels are the D-line terminals the present near-IR chain already works
in, so if the installed passband passes the 741 and 728 nm direct decays and
blocks a 760 nm drive, 7S would need a laser retune and no new detection
path. Both are datasheet questions rather than physics, and they are the
first thing to settle. `PLAN.md` costs no session beyond 993 nm, so no
duration is quoted for this row. The yield is an adjudication. The archive's
expected β_self at 6S rides on one external number, and that number has two
published values disagreeing by a factor 2.6, Zameroski's 129 ± 11 kHz/mTorr
against Wang's 0.32 ± 0.01 MHz/mTorr, with no HWHM or FWHM convention stated
in the second. A rate measured here, with the convention stated, would
replace the choice between them, and a measured β(6S)/β(7S) would test the
rate ratio the module predicts at 0.628, the ΔC₆ ratio 0.3128 to the
power 0.4, rather than assume it. If 7S returned
only a bound it would still separate the two published values, provided the
bound landed below the higher one. If the filter answer goes the other way,
7S needs the 420 nm path and the blue chain's noise model would have to be
measured first, which moves it behind the cell session in cost.

Projected, the adjudication is not close. Separating the two published
rates at five sigma needs 37 kHz per mTorr once the larger of their own
errors is folded in, and 102 if Wang's unstated convention turns out to
be half-width, so the harder of the two readings is the one quoted.
Running the same five-block density design on the 760 nm line, with the
archive's own per-block width scatter and per-block ruler spacing
precision carried over unchanged, would deliver about 8 kHz per mTorr.
The margin is fourfold, which is why the row is worth its retune even if
the rate lands between the two published values.

**The 778 nm rung.** 5S→5D is the only rung whose environmental coefficients
are published with error bars small enough to fail against, at 40 ± 0.54
kHz/mTorr for self-broadening and a magic wavelength at 776.179(5) nm.
Running the same three observables there would test the method rather than
produce a coefficient nobody can check, and that is also the limit of what it
returns. A reproduction would add no new number by design. The case for the
bench time is that this is the one line where the method can be caught. Two
conditions belong in the decision. Detection moves to 420 nm unless the 5D
cascade channels the near-IR path already passes turn out to be sufficient,
which is the same open question as at 7S. And the magic-wavelength scan is a
scan of a perturbing beam rather than of the drive, since a single-colour
drive is pinned at 778.104 nm, so the closed-form shift distribution holds
only where the perturbing and driving beams are mode matched over the
collection volume. Where they are not, the map would have to be recomputed
for the overlap of two profiles, which the machinery supports and has not
been asked to do.

Projected, this rung tests the method's bookkeeping and not its accuracy.
The same five-block design would deliver about 8 kHz per mTorr on the
778 nm rate, which is 20 percent of Cao's published 40. That clears the
13 kHz per mTorr a three sigma rejection of a factor-two convention error
would take, and it falls threefold short of the 2.6 kHz per mTorr a
20 percent method bias would take, so a reproduction would establish that
the passive method counts half-widths and full widths correctly and would
not establish that it is accurate at the level the published error bar
allows. The magic-wavelength scan is sized the same way. Placing the
crossing to Hamilton's own 5 pm, which is 2.5 GHz on the laser axis,
would need 9 points at a step of 0.045 nm across the 0.18 nm of half span
the neighbouring 5P₃/₂ to 5D₅/₂ pole leaves usable on the blue side, with
each point good to 8 percent of the shift at the edge of that span. The
wavelength axis
is not the limitation there. The archive's ruler axis carries 0.4 percent,
and the wavemeter of `PLAN.md` §11 places 5 pm to a fraction of a percent
of itself, so what the scan would be limited by is the per-point precision
on the shift observable, which is the quantity a session would have to
demonstrate.

**The doubling-stage options.** Exploratory, and last in priority. No
doubling stage is on the bench and none of these wavelengths has been
produced here, so the cost is new hardware and `PLAN.md` costs none of it.
A second-harmonic stage would not be a lineshape target: a single-photon line
out of the ground state is Doppler broadened to about 1.10 GHz at 400 K,
against the 3.49 MHz natural width the 993 nm work fits. Two secondary uses
would survive that. A 420.3 nm source would put light of exactly the
detection wavelength into the same cell, which is what the blue-chain noise
measurement of §2 asks for, and resonant absorption on the same cell would be
an independent column-density read against the archive's 20% density-scale
systematic. Neither would be publishable on its own, which is why the row
sits last.

If only one item were approved, PLAN's own ranking puts the beam profile
first, because it is the only one of the five that improves a result already
in hand.

## 4. The paper portfolio (ranked)

Four papers could be written out of the material above. The ranking criterion is
risk-adjusted distinctiveness per unit bench cost: how far a result would sit
from anything another group could produce, divided by the bench time and the
hardware it would take, discounted by the chance of returning nothing. That
criterion prefers a cheap measurement of a quantity nobody has published to an
expensive measurement of a quantity several groups have already published well,
so the order below is not the order of headline appeal.

Every entry carries the same seven fields in the same order. The claim the paper
would make. Who would read it and why. What stands against it in the published
record. What data it would need beyond the 2025 archive. The projected precision
and where that projection comes from. The principal way it could come back
empty. Its rank and the reason.

Three conventions hold throughout. The letters are the labels of record used in
[LITERATURE.md](LITERATURE.md) §5 and §8, so they are identifiers rather than
positions. The decision-maker table above holds the numbers for the rungs it
costs and this section holds the narrative, so the two point at each other once
rather than restating each other. And nothing here is scheduled, agreed or
assigned, which is why every verb below is conditional. §5 sequences the same
four papers by scientific impact if the whole programme ran, which puts A and C
first. The two orders differ because the criteria differ, and this one is the
order to read when only part of the programme is affordable.

### 4.1 Rank 1, Paper D (the cheapest new number)

*The 6S to 7P matrix elements by a differential null in a hot cell.* The design
is §5.1.

**Claim.** That the 6S to 7P reduced dipole matrix elements can be read from the
position of the differential-polarizability zero crossing at 1297.5 nm, located
by scanning one auxiliary beam across it and watching the induced shift pass
through zero in the lineshape channel this archive already extracts. The chain
would contain no intensity calibration and no absolute frequency reference.

**Readers.** The all-order atomic-structure methods, which run unbenchmarked on
excited-to-excited channels because a 7P lifetime sums over every decay channel
and ground-state absorption never reaches 6S to 7P. Separately, anyone weighing
this archive's asymmetry channel, since the same dataset would carry the
sign-reversal test of it.

**Prior art.** The logic is the tune-out family's, transplanted from a
single-state zero to a differential one. Herold et al., *Phys. Rev. Lett.* 109,
243003 (2012) is the nearest example and is also the source of the 5S to 6P
matrix elements [rb5s6s/polarizability.py](../rb5s6s/polarizability.py) uses,
so the method is already load-bearing here. No measurement of the 7P
fine-structure ratio exists for this doublet, which is what the companion null
at 1287.9 nm would push toward.

**Data beyond the archive.** One telecom O-band diode and its wavemeter, riding
any session that runs at all, plus the fixed-lock campaign's shift precision.
No Ti:Sapph time.

**Projected precision.** §5.1 puts the root at about 26 pm at the fixed-lock
campaign's projected shift precision, which would read the 7P residue against
the 496-atomic-unit background at about the 3 per cent level, and at about 18 pm
and 2.4 per cent at the two-day cadence. The shift precision those conversions
ride on is the one carried in
[results/projections.csv](../results/projections.csv) for a day of randomized
power cycling.

**How it could come back empty.** The delivered perturber intensity at the cell
could undershoot, which stretches the localization beyond the range where it
reads a matrix element. Every conversion also rides the measured waist, so these
are envelope numbers and would sharpen with the beam profile.

**Rank and reason.** First. Lowest bench cost of the four by a wide margin, and
the only one whose measurand has no published value at all, so the numerator of
the criterion is large and the denominator is one commodity source.

### 4.2 Rank 2, Paper B (the series capstone)

*Self-broadening and drift-immune differential polarizability across the Rb 5S to
nS and nD ladder, at 6S, 7S and 5D.*

**Claim.** That β_self, the transit width at a measured waist, and the
drift-immune Δα can be measured for each upper state with one method on one
bench, and that the resulting ratio β(6S)/β(7S) tests the van der Waals
machinery where a single rung can only be compared against it. §3.3 gives the
scaling this would test and corrects the parenthetical this entry used to carry.

**Readers.** The collision-rate series, which currently has one measured
self-broadening rate for an nS state in rubidium. The group advancing 7S as a
frequency standard. The theory groups on either side of the differential
polarizability sign, as [CLAIMS.md](CLAIMS.md) §4 sets out.

**Prior art.** [zameroski2014](lit/zameroski2014.md) measured foreign-gas
broadening and shift of the 5S to 5D₅/₂ and 5S to 7S₁/₂ two-photon lines by the
noble gases and N₂, and measured the 5S to 7S self-broadening rate directly.
Weber and Niemax, *Z. Phys. A* 307, 13 (1982) is the Rb nS and nD
self-broadening series that makes a completeness claim quotable, and
[LITERATURE.md](LITERATURE.md) §2 records it as not yet held, so it can be cited
for the series existing and for nothing further until it is read.
[wang2025](lit/wang2025.md) disagrees with Zameroski on the 7S rate by a factor
of 2.6 with no half-width convention stated. LITERATURE.md §8 records that no
dedicated modern 6S dynamic polarizability at 993 nm exists.

**Data beyond the archive.** The fixed-lock 993 nm session. A 760 nm retune,
with the two datasheet questions of §3.2 deciding whether a blue detection path
is needed. The 778 nm rung would additionally need the detection change.

**Projected precision.** The decision-maker table above costs the 7S and 778 nm
rows, with the assumption set behind each figure in
[results/projections.csv](../results/projections.csv). The 7S adjudication
carries a fourfold margin at the archive's own drive power and holds at the
light-shift ceiling.

**How it could come back empty.** β_self is intrinsically a few kHz per 10¹²
cm⁻³ and could stay a bound, which would still separate the two published 7S
values if the bound landed below the higher of them. The 778 nm rung is the
exposed one, because its light-shift ceiling leaves the factor-two test short
and [CLAIMS.md](CLAIMS.md) §4 states the consequence, that at this waist the
calibration would need about seventy times the session length before it could
catch even a convention error.

**Rank and reason.** Second. The 6S and 7S core is a laser retune away from a
number with a stated audience and a margin over what the adjudication needs. The
5D rung is what pulls the entry down, and dropping it would leave a shorter
series rather than no paper.

### 4.3 Rank 3, Paper C (the model validation A depends on)

*The near-resonant intermediate state in the two-photon transit and AC-Stark
lineshape, a clean against resonant comparison.*

**Claim.** That walking the intermediate-detuning ladder in one apparatus and
with one method would show how a near-resonant intermediate reshapes both the
line and the intensity-shift ramp, and where the clean-case approximation
validated at 6S stops holding. §2 gives the ladder, 6S at 75 THz down to 5D at
1.1 THz, a sweep of about 68 in intermediate-state admixture.

**Readers.** Anyone applying a passive lineshape method to a line with a nearby
intermediate state, who currently has to assume the clean case or model it from
scratch. Also the referee of Paper A, since this is the correction Paper A needs
at 5D and could be its methods section instead of a standalone.

**Prior art.** [bjorkholm1976](lit/bjorkholm1976.md) is the closed-form
two-photon lineshape with a resonant or nearly resonant intermediate state, and
its note records that it is not prior art for reading a light shift off the
line, because AC-Stark effects are excluded there by construction and its one
distortion effect comes from Doppler-velocity integration rather than from
spatial intensity structure. The transit side is
[biraben1979](lit/biraben1979.md) and [lehmann2021](lit/lehmann2021.md).

**Data beyond the archive.** Two rungs would do for a first result, 6S and 7S,
which is a sweep of about 7.5 and needs no new detection path if §3.2's
datasheet questions answer favourably. The resonant end at 5D needs everything
Paper A needs. 8S and 9S would fill the middle and require the blue optics set.

**Projected precision.** Not projected.
[results/projections.csv](../results/projections.csv) carries no row for it,
because the discriminating quantity is a comparison
between two lineshape models rather than a coefficient with an error bar, and
sizing it would need the model comparison run on synthetic traces first.

**How it could come back empty.** The intermediate-state term could sit below
the per-trace fit residual at 7S, in which case the affordable half of the
sweep would return the clean-case approximation holding everywhere it can be
tested, and the informative end would be the expensive rung.

**Rank and reason.** Third. Cheap at the 6S and 7S end and it lowers Paper A's
risk, which is why it ranks above A. Its own distinctive result lives at the 5D
end, which carries Paper A's cost, which is why it ranks below B.

### 4.4 Rank 4, Paper A (the topical extension)

*Reference-free light shift and magic wavelength on the 778 nm 5S to 5D clock
line, by lineshape asymmetry.*

**Claim.** That the differential-polarizability zero crossing beside the 778 nm
line could be located from the sign flip of the lineshape asymmetry as Δα passes
through zero, with no reference cavity and no active feedback in the chain. The
claim is methodological. It would not out-precision the active schemes and must
not be written as though it could. The same machinery gives computed 5S to 6S
crossings (§3.3), which are a trapped-atom follow-up on a different state pair
rather than part of this paper.

**Readers.** The 778 nm clock groups, whose published AC-Stark handling is
active throughout: [andeweg2026](lit/andeweg2026.md) suppresses by power
modulation at a factor of a thousand, [ahern2025](lit/ahern2025.md) runs
two-colour at 6×10⁻¹⁴/√τ and is light-shift limited in the long term,
[feng2026](lit/feng2026.md) chooses a sub-transition with a smaller tensor
shift, [li2024b](lit/li2024b.md) nulls by dual interrogation, and
[gerginov2018](lit/gerginov2018.md) is the suppress-the-shift stance this
programme contrasts with. [bandi2025](lit/bandi2025.md) is the review that
frames the benchmark landscape.

**Prior art, and it is the field that most constrains this entry.**
[delone1980](lit/delone1980.md), a 1980 review, already carries the
lineshape-as-map frame, the multiphoton intensity weight and the
shift-dominated asymmetric limit, and this repository's closed form is its Eq.
(5.3) evaluated for the intensity distribution of a focused Gaussian beam.
[camparo1992](lit/camparo1992.md) states the mapping for a two-photon line.
[wieman1987](lit/wieman1987.md) and [antypas2018](lit/antypas2018.md) own
asymmetry from a distributed AC-Stark shift and its elimination.
[slepkov2010](lit/slepkov2010.md) and [wall2014](lit/wall2014.md) both keep the
shift distribution rather than averaging it away, and Wall carries the
two-photon intensity weighting too. LITERATURE.md §5.1 and §5.2a fix what
survives that: the closed form with its analytic cumulants, the inversion of the
lineshape for the shift where the frequency reference is unusable, which Slepkov
and Wall do not perform, and the third cumulant as a drift-immune channel. The
closest external precedent to the inversion is a 2015 nanofibre-trap analysis
recorded in LITERATURE.md §8 as reported and not held, so the wording stays
scoped until it is read. No passive-asymmetry determination on the 778 nm line
appears anywhere in the swept landscape.

**Data beyond the archive.** A 778 nm drive, detection at 420 nm unless the 5D
cascade channels the near-IR path already passes turn out to be sufficient, and
a second source for the scan, because §3.1 shows the single-colour drive is
pinned at 778.104 nm and the field scanned across the crossing is the perturbing
one. The closed-form shift distribution holds only where the two beams are mode
matched over the collection volume. The asymmetry channel needs the large-S₀
tighter-waist regime to be a measurement at all, and at that waist the axial
average over the collection window sets both the size and the sign of the ramp
skew, so the collection geometry would have to be measured in the same session.
[PLAN.md](PLAN.md) §6 item 4 gives the closed form for that average and shows
the sign flip holding across the plausible magnification range.

**Projected precision.** The decision-maker table above costs the 778 nm row
and §3 sizes the scan, at nine points across the usable half span the
neighbouring 5P₃/₂ to 5D₅/₂ pole leaves on the blue side, each point good to
about 8 per cent of the shift at the edge of that span. The limitation is the
per-point precision on the shift observable rather than the wavelength axis.

**How it could come back empty.** The most exposed of the four. The light-shift
ceiling at this rung leaves the factor-two test short, so on the design as it
stands the calibration would need about seventy times the session length before
it could catch even a convention error, and [CLAIMS.md](CLAIMS.md) §4 states
that the audience is served by a longer session or a looser focus rather than by
this design. The skew is contamination-prone, from shot noise and from
instrument asymmetry, and it would have to be separated from both.

**Rank and reason.** Fourth. The most distinctive result on the list and the
most expensive to reach, on the most actively worked transition, with the
narrowest surviving novelty claim of the four and the largest number of
conditions that all have to hold at once. On this criterion that combination
ranks last. On §5's impact ordering it ranks first, and the difference between
the two orderings is the whole content of the criterion.

## 5. Recommendation & sequencing

*A proposal for discussion, not a decided roadmap: none of the sessions or
papers below is scheduled, agreed, or assigned. The ordering is what the
physics argues for if the programme is pursued at all.*

1. **Finish this analysis (993 nm 5S→6S)** as the clean method
   demonstrator, and reframe its introduction around the scoped novelty
   section 4.4's prior-art field states: the closed form, its cumulants,
   and the reference-free extraction, against the active 778 nm
   suppression schemes and the USAFA nulls. A vapour-cell introduction
   edit, cheap, with the references in `LITERATURE.md` §8.
2. **Paper D** rides whichever cell session runs first, because it costs
   one commodity diode and no Ti:Sapph time (§5.1, and rank 1 of §4 on
   exactly that ground). Impact-wise it is the one new number nobody
   else has, so it belongs in the sequence wherever a cell session does.
3. **Paper A + C together** are the high-impact Ti:Sapph step: carry the
   method to the 778 nm clock line, with the intermediate-state
   lineshape study (C) as the validated bridge from the clean 6S anchor.
   The tunability argument is for the SCAN across the magic point, not
   for reaching 778 nm as such, which the decision-maker table costs
   with a fibre-amplifier alternative that makes the Ti:Sapph
   unnecessary for a fixed-wavelength run.
4. **Paper B** is the completeness capstone, reusing the rig and method
   across the ladder.

**The most distinctive experiment the Ti:Sapph enables** (distinctive, not
necessarily most precise): scanning the 776 nm magic wavelength on 5S→5D and watching
the ramp asymmetry flip sign, a reference-free magic-wavelength determination, on the
most actively worked transition, by a method those groups do not use. Its systematics
are orthogonal and it needs no active hardware, and it needs the large-S₀
small-waist regime to work at all (§Paper A caveat). The lower-risk
complement is **Paper B** (the β_self / Δα ladder), which reuses the exact
rig and method.

### 5.1 The steep root at 1297.5 nm: useless as a trap, precious as a lever

The differential polarizability of the 5S and 6S clock states has a fourth
zero crossing at 1297.533 nm, sitting 0.745 nm (133 GHz) from the 6S to
7P resonance, between the two 7P fine-structure poles. Both numbers are the
electric-dipole valence computation at its central inputs, and the
multipole scrutiny below bounds what the neglected terms can do to them. As a trap wavelength
it is disqualified three times over: the crossing is 915 times steeper than
the tamest reported magic wavelength (11.3 atomic units per picometre), the
band where the differential stays within ten atomic units is under two
picometres wide, and the near-resonant scattering closes the case. Those
same three numbers, read as an instrument rather than a trap, are the
opportunity, and it is one this repository's machinery is already built for.

**A matrix-element measurement by a null, on the vapour cell, drift-immune.**
Add one auxiliary beam near 1297.5 nm to the existing cell experiment and
scan its wavelength across the root while reading the light shift it induces
on the 993 nm line through the lineshape channel this archive already
extracts. The induced shift crosses zero at the root and its asymmetry
changes sign there, so the null is identified from the SHAPE of the line,
needing no absolute frequency reference, which is the property this whole
programme is built on. The position of the null is set by the 6S to 7P line
strength, so locating it measures that matrix element by frequency metrology
instead of intensity calibration, the same logic as the tune-out
measurements of Herold and co-workers, transplanted to a differential zero.
The steepness is the whole budget: at the fixed-lock campaign's projected
shift precision of 92 kHz, the root localizes to 26 pm, which reads the 6S
to 7P residue at about the 3 per cent level (18 pm and about 2.4 per cent at
the two-day cadence). The tamest root would localize to 23 nanometres at the
same precision and measures nothing. Every conversion here rides the
campaign intensity and the measured waist, so these are envelope numbers in
the sense of the projections table, and they sharpen with the waist
measurement like everything else.

**A sign-reversal test of the asymmetry channel.** The archive's asymmetry
observable is claimed as a light-shift channel. Sweeping the auxiliary
beam's wavelength through the root drives the induced shift distribution
through zero and out the other side, so the asymmetry must flip sign at the
null while every instrumental confound stays put. That is the cleanest
falsifiable test the asymmetry claim can be given, and it is a test the
2025 campaign could not perform at fixed wavelength.

**A dial-a-shift knob.** Off the null, one picometre of wavelength is 3.6
kilohertz of controllable differential shift at campaign intensity, with
either sign available within a few picometres. That is a calibrated shift
injector for rehearsing the fixed-lock campaign's analysis on data with a
KNOWN light shift, which no other knob on the bench provides.

**And the practicality is the punchline**: 1297.5 nm sits in the telecom O
band, where stabilized diode lasers and calibrated wavemeters are commodity
items. The steep root is the one zero crossing of the four that needs no
Ti:Sapph time at all. It is a crossing and not a magic wavelength: the reported
list has three, on the criterion of usability as a trap, and this one fails
that criterion for the three reasons above.

**What the paper actually is: the electric-dipole inputs become the
measurand.** The theory envelope paragraph below says the root's predicted
position is good to about a tenth of a nanometre because of the
electric-dipole inputs. Measuring the root to 26 pm therefore does not
test the prediction so much as replace it, and the paper this makes is a
matrix-element paper. Between two excited states the dipole matrix
elements are the least measured numbers in the alkali tables: a 7P
lifetime sums over every decay channel and cannot isolate 6S to 7P, and
absorption from the ground state never reaches it, which is why these
channels are where the all-order atomic-structure methods run
unbenchmarked. The null position reads the ratio of the 7P residue to the
496-atomic-unit background the clock pair balances at, by frequency
metrology against a spectroscopically exact pole, with no intensity
calibration anywhere in the chain. And the doublet offers a second
handle: a companion null at 1287.87 nm sits 4.5 nm below the 7P 3/2 pole
(shallower, 0.64 atomic units per picometre, so localized to about half a
nanometre at the same shift precision), and the pair of nulls bracketing
the fine-structure doublet separates the two 7P residues from the shared
background, pushing toward the fine-structure ratio with the background
dependence reduced. That ratio is the classic observable of the tune-out
literature, and no measurement of it exists for this doublet.

**What the neglected multipoles can and cannot do to the root.** The
computation behind the crossing is electric-dipole and valence-only, so the
question of whether quadrupole or octupole terms move a root quoted to
0.745 nm from a pole has to be answered rather than waved at. Two facts
answer it. First, no multipole-allowed one-photon resonance of either clock
state falls inside the 1292.4 to 1298.3 nm gap the root lives in: the
nearest electric-quadrupole channels are 6S to 6D at 1169 nm and 6S to 5D
at 1796 nm, the nearest magnetic-dipole channels are 6S to 8S at 1122 nm
and 6S to 7S at 1618 nm, the nearest electric-octupole channel is 6S to 4F
at 1502 nm, and on the ground state everything sits below 520 nm. So the
neglected terms contribute background, never a local pole. Second, that
background is generically suppressed by the square of the wavenumber times
the Bohr radius, 6.6 times ten to the minus eight here, and granting the
radial matrix elements two orders of magnitude of enhancement still leaves
the multipole background below ten to the minus five of the
8400-atomic-unit electric-dipole background the root balances against,
which moves the root by under a hundredth of a picometre. The octupole
family enters at the fourth power of the same small parameter and is beyond
consideration. What actually limits the theory position is the
electric-dipole inputs themselves: a ten per cent error on the 7P residue
or on the background moves the root by about 75 pm, and the 7P hyperfine
substructure smears the pole by under half a picometre at this detuning.
The measurement is insensitive to all of it in the direction that matters,
because the proposal is to MEASURE the root against the spectroscopically
exact pole position, and the theory envelope on its location is precisely
why a 26 pm localization buys a matrix element.

The root stays out of the reported magic-wavelength list, where the
criterion is usability as a trap, and the polarizability module's search
guard stays. The disposition note in the calibration record carries the
slope table behind these numbers.


#### 5.1.1 Amendment (2026-08-08): the other five roots, computed, and why this one was the right choice

Section 5.1 chose 1297.5 nm because it is the steepest crossing, and everything
it says about that root stands. What it did not do is compute the same budget
for the other five. Doing so confirms the choice and replaces the reason.

Two quantities decide what a crossing can measure, and steepness, which is
what section 5.1 selected on, is neither of them.

**Steepness** sets how precisely a crossing can be LOCATED in wavelength from
a measured shift. **Position sensitivity** sets how far the crossing moves in
wavelength when an element changes. Both scale as one over the steepness, the
first because a steep root turns a shift precision into a short wavelength
interval and the second because the same steep curve absorbs an element change
in a short distance, so steepness cancels out of their ratio exactly.
`lever_table()` shows the cancellation to six figures across a factor of nine
hundred in steepness. What a crossing measures is the differential
polarizability itself, to 288 atomic units at the campaign intensity and a
shift precision of 92 kHz, and the precision it delivers on an element is that
288 divided by how strongly the differential responds to the element, which is
176 atomic units for a one per cent change at 1339.6 nm against 163 at the
steep root. On
the response alone, 1339.6 nm looks like the better lever, at 1.6 per cent
against 1.76 for the steep root.

**The quantity that decides the case is what the element is already known
to**, and it reverses that reading. The line lists carry their own quoted uncertainties, so the
comparison needs no judgement. `rb5s6s.hyperpolarizability.lever_table()`
computes all of it, and the last column is the one that matters, the currently
quoted uncertainty divided by what the crossing would deliver:

| crossing (nm) | steepness (a.u./pm) | locates to (pm) | reads | would give | already known | gain |
|---|---|---|---|---|---|---|
| 1297.5 | −11.3 | 26 | 6S–7P₁/₂ | 1.76% | 1.81% | **1.03** |
| 1287.9 | −0.64 | 447 | 6S–7P₃/₂ | 4.5% | 1.62% | 0.36 |
| 1029.7 | −2.2 | 133 | 6S–8P₃/₂ | 9.2% | 1.53% | 0.17 |
| 1339.6 | +0.77 | 374 | 6S–5P₃/₂ | 1.6% | 0.21% | 0.13 |
| 1203.9 | +0.012 | 23400 | 6S–5P₃/₂ | 11% | 0.21% | 0.02 |
| 1031.9 | −0.54 | 529 | 6S–6P₃/₂ | 24% | 0.26% | 0.01 |

One crossing out of six would tell anyone anything they do not already know,
and it is the one section 5.1 picked, though at 1.03 the improvement is three
per cent on the error bar and no more, so what the measurement would add is an
independent determination by frequency metrology in a channel that has none
rather than a materially tighter number. The apparent better lever at 1339.6 nm
reads an element the 6S lifetime already pins eight times more tightly than the
measurement could, so its 1.6 per cent buys nothing.

**Why steepness was the right thing to select on even though it cancels, which
is the part worth keeping.** Steepness and ignorance are not independent. A
crossing is steep because it sits close to a resonance. The resonances the crossings sit near are
the weak, high-lying ones, and those are precisely the transitions whose matrix
elements nobody has measured well, because a weak line is hard to measure by
any method. So the steepest crossing automatically reads the least known
element. Section 5.1 selected on the property it could see and got the right
answer for a reason it did not state.

**Two corrections to what this amendment first claimed.** The first version
presented steepness as one of three quantities that set the precision a
crossing delivers. It sets none of it. The table's arithmetic was never
affected, since the code divides one steepness-scaled quantity by another, but
the account of what the number rests on was wrong, and the paragraph above now
states the cancellation.

Second, an earlier version
of this section argued that a crossing reading 6S–5P₃/₂ would settle the
differential-polarizability sign question, since that dispute turns on a
revision of the 6S–5P strength of about a third. It would not, and the reason
is the same third column: 6S–5P₃/₂ is already known to 0.21 per cent, so a
revision of that size is excluded by a factor of roughly 150, which is the
same conclusion the archive reaches from the measured 6S lifetime. The sign
question was already decided by existing data. Nothing here adds to it.

**What this does not claim.** The sensitivities are one element at a time, so
they name the element each crossing speaks to rather than delivering a joint
error budget, which needs the covariance of the whole set. The conversion from
shift precision to wavelength rides the campaign intensity and the adopted
waist, like every other projection here, and sharpens with the waist
measurement.
## 6. Open feasibility questions, to be settled at the bench
- Ti:Sapph output power and lock quality at 760–778 nm vs the 993 nm red edge?
- Is the 420 nm detection path (filter + blue-sensitive PMT) available, or a build?
- Do the EOM (ruler), retro-mirror coatings, and waveplates cover 778 nm as well as
  993 nm, or need swaps? (The intensity-anchor / retro-ratio ρ must be re-characterised
  per wavelength.)
- Cell/oven: 5D/7S may want *lower* density than 6S (they are stronger / closer to
  resonance). The fixed-lock session shot-list temperature range would differ per transition.
- The ruler comb itself: in the archive the scan clips one third-order tooth window on
  every recorded trace, and at the measured drive depth (2β = 1.57 median across the combs) a fully covered
  third-order tooth still sits below the per-trace fit residual (pre-registration
  amendment 4). Widening the scan by about one tooth spacing per side and deepening the
  EOM drive until J₃² clears the noise would give every calibration trace seven standing
  teeth instead of six: one more spacing constraint per trace, and outer-slot checks
  that no longer run at the ramp edge.

*References for §4 are collected in
[`docs/LITERATURE.md` §8](LITERATURE.md#8-the-20242026-landscape), which is where
the 2024–2026 landscape is held and is the citable source for every claim above.*
