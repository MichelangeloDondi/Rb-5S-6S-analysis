# Exploiting the tunable Ti:Sapph — future transitions and the papers they enable

**Status: physics options / food-for-thought (2026-07-13).** Not a plan of record. The
premise (recorded 2026-07-13): the drive laser is a **tunable Ti:Sapphire**, so a new
measurement session is not locked to 993 nm — it can reach *other* Rb two-photon
transitions, "as long as we can reach the frequency and the optics is fine at the
next frequency." This note maps what that buys us, grounded in the 2024–2026
landscape (local literature-intake note, untracked).

## 1. The one-sentence picture

Our current line (5S→6S, 993 nm) is **little studied and not currently pursued elsewhere** — the only
active group (USAFA/Knize: Ayachitula 2024, and the earlier McLaughlin 5S–6S work)
reports *null* AC-Stark and density shifts at ~6 MHz resolution — so it is the
clean **demonstrator** of the drift-immune method. The **far more actively worked line is one
transition over**, at 778 nm 5S→5D, where 2024–2026 clock work (NIST/Andeweg,
Adelaide/Ahern, Feng, FEMTO-ST/Callejo, Gerginov, Li–Dou) suppresses the AC-Stark
shift **entirely with *active* schemes** (power modulation, dual interrogation,
two-color, magic-wavelength locking). **Nobody uses a passive lineshape-asymmetry
observable there.** A tunable Ti:Sapph lets us carry our reference-free method onto
that hot transition — so wavelength scans across the magic point become the measurement.

## 2. The transition menu the Ti:Sapph opens (verified)

Two-photon from 5S₁/₂; wavelength = 2×10⁷ / E_upper[cm⁻¹]. "Intermediate detuning"
= how far the virtual one-photon level sits from the nearest real 5P (the physics
that sets how much a near-resonant intermediate distorts the two-photon lineshape,
Bjorkholm–Liao 1976). **Reachability is set by the installed SolsTiS optics set, not
a single continuous range** — see the laser-specific §below; the M-Squared datasheet
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

The blunt consequence: **no single set covers everything.** The pivotal question is
which set is in *your* SolsTiS. If it is **700–1000 nm**, then 6S (993, near the red
edge), 5D (778) and 7S (760) are all reachable with **the same optics** — the whole
near-IR program needs no laser-optics swap, only the 420 nm detection change. If it
is **950–1050 nm**, 993 and 4D (1033) are easy but 5D/7S require an optics-set swap.
8S needs the dedicated 670–710 blue set; 9S (660) and any >1000 work are custom.

### Your laser (M-Squared SolsTiS + Coherent Verdi V18 @ 18.5 A)

- **Pump is not the limiter — the optics set is.** The Verdi V18 delivers up to
  **18 W at 532 nm** (datasheet-confirmed). Whether 18.5 A is your full-power point
  or a set-point, that is a *generous* pump for a SolsTiS (which needs far less), so
  tuning range is fixed by the installed BRF/mirror set, not by pump. Ample pump is
  exactly what buys usable power at a set's *edges* — which is how you reach 993 nm
  at the top of a 700–1000 set, and what the large-S₀ regime Paper A needs.
- **Tuning mechanism** (why "within a set it's continuous"): motorized
  birefringent filter (coarse, spans the whole set) + a 320 GHz-FSR etalon +
  cavity PZT (fine) — continuous within the set, no realignment.
- **Two things to check on the actual unit** (they decide the whole plan):
  1. **Which optics set is installed** — read the config label / M-Squared sheet,
     or just tune to the bluest and reddest points it will lase. If the blue end
     reaches ≲780 nm, 5D/7S are same-set (only a detection swap); if it starts at
     ~950 nm, 5D/7S need an optics-set change (M-Squared swap, non-trivial).
  2. **Output power at 760–778 nm vs at 993 nm.** A 700–1000 set gives *more* power
     mid-band (760–778) than at the 993 edge — good news: the 5D/7S work would run
     with *more* S₀ headroom than the current 6S work, which is what the asymmetry
     signal (∝S₀³) needs.
- You already reach **993 nm** with this pump, so your set reaches at least to 993
  (consistent with 700–1000 or 950–1050); running the V18 near max at 18.5 A is
  consistent with holding that red edge.

Three things fall out. (i) **5D and 7S sit in the Ti:Sapph sweet spot** (more power,
easier lock than the 993 nm red edge). (ii) **The whole upper ladder shares ONE
detection channel** — 420 nm (6P→5S blue fluorescence) serves 5D, 7S, 8S *and* 9S,
because they all cascade through 6P; only 6S is the near-IR (795 nm) outlier. So
the detection swap noted above (the 795 nm filters → a 420 nm bandpass + a
blue-sensitive PMT) is a **prerequisite for every upper-ladder transition**, and one
swap serves all four (see §Detection below). (iii) The intermediate
detuning now spans **~68×** across a five-rung ladder 5D→7S→8S→9S→6S (1 → 75 THz) —
a controlled sweep of intermediate-state admixture in one apparatus (§Paper C).

### Detection — how much does changing the 795 nm filters help?

A lot, but as an **enabler rather than an optimisation**. The 6S work detects the
6S→5P→5S cascade at **795/780 nm** (near-IR). Every *upper* transition (5D, 7S, 8S,
9S) instead cascades **through 6P**, emitting **420 nm** (6P→5S, blue) — a channel
the current near-IR path does not pass. So:

- To see *any* of the upper-ladder transitions at all, the detection filters must
  change to a **420 nm bandpass** (plus a PMT/APD with useful blue quantum
  efficiency — many near-IR-optimised detectors are poor at 420 nm). This is a
  hard requirement; it cannot be trimmed or optimised around.
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
  via 6P→5S), so a single detection upgrade unlocks the whole upper program.
- Caveat on signal: the 420 nm branching ratio is favourable for 5D and 7S but
  **dilutes for 8S/9S** (more open decay channels), compounding their blue-edge
  Ti:Sapph disadvantage — so 5D/7S are the high-yield targets, 8S/9S the reach.
- Practical check, now answered (experimenter-confirmed): the present 795 nm
  optics are a **passband stack**
  (~50 dB, `DATA.md`), not a pump-rejection notch — so this is the simple branch:
  the stack is swapped wholesale for a 420 nm bandpass, and no separate
  760–778 nm pump-blocking edge has to be sourced, provided the replacement's
  out-of-band blocking at 993 nm is specified (check the datasheet, don't assume:
  a visible bandpass is not obliged to block deep IR).

- **A note for the 6S line itself: a trapping-free 1.3 µm option.** The 6S cascade's
  *first* step, 6S→5P, emits at **1.32/1.37 µm** — and unlike the 780/795 nm D-line
  photons (ground-resonant, hence radiation-trapped in the dense cell), the 1.3 µm
  photon is resonant with nothing populated and escapes freely. Detecting it (an
  **InGaAs** detector — single-photon sensitivity below a Si PMT, plus hot-cell
  IR-background filtering) is a **trapping-free** amplitude channel, and the
  **795-vs-1.3 µm ratio discriminates a real degeneracy-law/amplitude deviation from
  a radiation-trapping artifact** (`PLAN.md` §8). The IR-cascade-to-beat-trapping
  trick is established on the sibling line — Hassanin et al. 2023 (5D→5P) and Beard
  et al. 2024 (5D→6P, 776 nm) — so it is proven, not speculative. Orthogonal to the
  420 nm upper-ladder swap — this is a 6S-detection refinement, not an enabler.

Net: the filter swap is required once to reach the upper ladder, and it is a
*cheap, one-time* price (one blue detection path) for a *large* payoff (four new
transitions, including the hot 5D clock line).

**But "cheap" describes the hardware, not the risk — and the risk is the noise
floor, which has to be measured rather than assumed** (2026-07-26). M1's fitted
law is σ² = a² + b·V: a detector floor plus a Poisson term. Which of the two
dominates sets how signal-to-noise responds to a *fainter* line, and the two
answers differ by a square:

- above the crossover V\* = a²/b the line is **shot-limited**, SNR ∝ √S — so a
  10× weaker signal costs only ~3× in SNR;
- below it the line is **floor-limited**, SNR ∝ S — the same 10× deficit costs
  the full 10×.

That distinction decides feasibility for any dimmer configuration, and it is not
a small effect: across the 32 archival conditions **V\* spans 2–258 mV**
(median ≈ 9 mV, `results/noise_model.csv`), so even one detection chain
straddles both regimes. The 795 nm path happened to land shot-limited over the
whole archival range — the faintest line, 20 mV, still sits above the median
crossover — which is *why* the archive's dimmest 70 °C dwells were fittable at
SNR ≈ 16. **A blue chain inherits none of that.** Blue-sensitive photocathodes,
different dark rates and a different filter stack move both a and b, and a
420 nm path landing at the high end of that V\* range would be floor-limited
exactly where an upper-ladder line is faintest.

**The check is a re-run of M1 on the new path, not new analysis:**
`rb5s6s.noise.condition_noise_model` fits a and b from a handful of repeats, so
the blue chain's V\* can be measured on the bench — a lamp, the filter, and the
detector — before any transition is attempted. Doing it first converts the
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
(2026-08-03):

    beta_self(6S) = beta_self(7S)_measured * [C6(5S+6S) / C6(5S+7S)]^(2/5)
                  = 5.386 * 0.3473^0.4
                  = 3.53 +- 0.30 kHz per 1e12 cm^-3

with C₆(5S+6S) = 28908 a.u. and C₆(5S+7S) = 83228 a.u. from the module's own
Casimir-Polder integrals, and 5.386 kHz per 10¹² cm⁻³ being Zameroski's measured
129 ± 11 kHz/mTorr converted at 403 K. Exactly one number in that chain comes
from outside. The archival bound sits 8 to 14 times above that expectation.

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

    beta(6S) / beta(7S) = 0.3473^0.4 = 0.655

A measured ratio would test the C₆ machinery. A 6S measurement on its own keeps
leaning on it. The absolute check already on record is of a different kind and
is weaker: run on 7S the module predicts 4.50 against the measured 5.39 kHz per
10¹² cm⁻³, 17% low, which the dropped core and tail plus the mean-speed step
account for at the 10 to 15% level. That tests the absolute scale at one n. A
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
fixed quantum defect of 3.131 is used instead), so β_self would grow as
**n\*^1.4** across the same step. Two points give a local slope. A third
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
file does not price that trade.

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

## What the decision-maker needs

Everything above is a physics menu. The host PI deciding bench time reads
cost, yield and risk instead, so this section restates the same items in
those columns, with the last naming the source class that reaches each rung's light-shift ceiling. Nothing below is scheduled, agreed or assigned. Every
duration is [PLAN.md](PLAN.md)'s own where PLAN.md prices the block, and is
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
| wide-scan Doppler pedestal | an acquisition setting on any session that runs at all, no hardware and no lock quality | an in-situ gas thermometer and an in-situ retro ratio, on the same traces | the pedestal may not separate from the scattered-light background, and the area ratio is flat in ρ near one | the design pins the temperature in about 1.9 hours to where the vapour curve's 22-fold leverage keeps the implied density inside the 20 percent scale systematic, and reaches the adopted retro ratio in about 2.1 hours, both on the four-pedestal comb and both about sixteen times longer on a single component | the drive itself, swept wide. The pedestal is 942 MHz wide on the transition axis at 130 °C, so no new source and no lock is involved |
| doubling stage | new hardware, none on the bench, unpriced | a resonant 420 nm source and an independent density read (§3.4) | nothing publishable on its own | not projected, since nothing here models its rates | the doubling stage is its own source, and a one-photon line carries no two-photon light-shift ceiling |

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
no new detection path, which is why the table above prices it against any
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

**The beam profile.** `PLAN.md` §3 puts w₀ in Tier 0, the systematic floor,
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
conditional on the waist prior.

**The fixed-lock cell session.** This is the full ask. `PLAN.md` §9 sizes it
at about eight days at the cell and orders it so that a truncation at any
point leaves the higher-priority conversions done, and the tiers of §3 are
what a shortened session would fall back through. Tier 0 is the systematic
floor, which is the ramp-monitor export, the beam profile and the retro ratio
measured in situ, and it converts the archival bounds whether or not a later
block runs. Tier 1 is the fixed lock itself plus same-session 150 to 170 °C
points in interleaved temperature order, which is what would turn β_self from
a bound into a rate. `PLAN.md` §1 names the smallest tranche that converts
even one bound: a geometry-setup block plus the two opposite-order
temperature-grid days, D1 to D3, returning β_self or a much tighter bound
along with the first fixed-lock laser width. Tier 2 buys handle strength
through a second and tighter waist. Tier 3 is sampling that refines without
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
first thing to settle. `PLAN.md` prices no session beyond 993 nm, so no
duration is quoted for this row. The yield is an adjudication. The archive's
expected β_self at 6S rides on one external number, and that number has two
published values disagreeing by a factor 2.6, Zameroski's 129 ± 11 kHz/mTorr
against Wang's 0.32 ± 0.01 MHz/mTorr, with no HWHM or FWHM convention stated
in the second. A rate measured here, with the convention stated, would
replace the choice between them, and a measured β(6S)/β(7S) would test the
C₆ ratio the module predicts at 0.655 rather than assume it. If 7S returned
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
produced here, so the cost is new hardware and `PLAN.md` prices none of it.
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

## 4. The papers this enables (ranked)

### Paper A — *Reference-free light shift & magic wavelength on the 778 nm 5S→5D clock line, via lineshape asymmetry* — **the topical extension (methodological, not a precision competitor)**

> **Caveat up front (2026-07-13).** This is a *reference-free, orthogonal-
> systematics, no-extra-hardware* determination — a complementary cross-check and a
> clean demonstration of the inverted-nuisance idea. It will **not** out-precision the
> active schemes (NIST/Adelaide), and must not claim to. Its value is method + physics,
> not a smaller error bar. The shape handles are weak (width ∝S₀², skew ∝S₀³) and the
> skew is contamination-prone (shot noise, instrument asymmetry), so it needs the
> *large-S₀* small-waist regime to be a measurement at all — see the scope note in
> the vapour-cell framing. That inherits a further dependency: at small waist the
> ramp skew is itself conditional on the axial collection geometry, which is
> unmeasured — the axial average can suppress it or reverse its sign
> (PLAN §6 #4). So this proposal is gated on the same collection-profile
> measurement, not only on reaching small waist. The reason "nobody does this" is not an oversight: with a
> stable reference the pull (∝S₀) is strictly better, so the passive shape route is
> preferable only where reference-freedom or orthogonal systematics are required.

- **Why now.** 5S→5D at 778 nm is *the* vapor-cell two-photon clock transition, and
  the 2024–2026 leaders (Andeweg 2026 ×1000 power-modulation suppression; Ahern 2025
  two-color 6×10⁻¹⁴/√τ; Feng 2026; Gerginov 2018; Li–Dou 2024) all fight the AC-Stark
  shift with **active** methods. Our drift-immune **ramp/asymmetry** channel is a
  *passive, reference-free, low-complexity* alternative — a real methodological
  differentiator on a maximally topical transition (Bandi 2025 is the review to cite
  for the benchmark landscape).
- **The measurement the tunability enables.** The ramp asymmetry (third-moment/skew observable)
  scales as S₀ ∝ Δα(λ). Hamilton 2023 puts a **magic wavelength at 776.179 nm**, right
  beside the transition. Tune the Ti:Sapph across it and the asymmetry **crosses zero
  and flips sign** as Δα→0 — a **passive determination of the magic wavelength /
  differential-polarizability zero-crossing**, with no reference cavity and no active
  feedback. That would be a reference-free determination of the differential-polarizability zero crossing.
  **Read §3.1 before this bullet.** In Hamilton's own apparatus the scan across
  776.179 nm is run with a *separate* tunable Ti:Sapph perturbing a clock that
  is driven by fixed 780 and 776 nm lasers, and a single-colour 778.104 nm drive
  cannot be tuned at all, so the field being scanned here is the perturbing one.
- **Magic wavelengths for our own 5S–6S pair now exist as computed candidates**
  (M16, `results/polarizability.csv`; unpublished elsewhere to the depth searched
  2026-07-17): α₅S = α₆S crossings at **≈1203.9 nm** (the clean one, far from every
  6S resonance; α ≈ +547 a.u., trapping both states; 16–84% band ±0.8 nm),
  ≈1287.9 nm and ≈1339.6 nm (both wedged near the 6S–7P / between the 6S–5P lines,
  where vector shifts need their own treatment). A trap at the 1203.9 nm crossing
  would hold atoms without perturbing the 993 nm line — the state-insensitive-trap
  ingredient for any trapped-atom version of this spectroscopy.
  Scalar only; a vector/tensor treatment and a
  blue-side crossing search are the follow-up.
- **Novelty (three claims).** (i) The *inversion* of lineshape asymmetry from
  nuisance-to-eliminate (Wieman 1987; Antypas–Budker 2018) into a self-calibrating
  observable, realized on a *focused* two-photon transition; (ii) magic-λ from an
  asymmetry sign-flip; (iii) reference-free complement to the active-suppression
  mainstream. The literature sweep found no passive-asymmetry light-shift measurement on any
  focused two-photon line, and none on 5D.
- **Feasibility flags (to decide at the bench).** 778 nm is easy for the Ti:Sapph. BUT: (a)
  detection moves to 420 nm (filter + blue PMT); (b) the **near-resonant 5P₃/₂
  intermediate (1 THz)** distorts the two-photon lineshape — the transit/ramp model
  needs the Bjorkholm–Liao intermediate-state term (this is exactly Paper C, so it
  reduces the risk on A); (c) verify the EOM/retro/waveplates behave at 778 vs 993 nm.

### Paper C — *The near-resonant intermediate state and the two-photon transit/AC-Stark lineshape: a clean-vs-resonant comparison (6S, 7S, 5D)* — **the engine-room companion to A**

- The intermediate-detuning **ladder** — 6S (75 THz, clean) → 9S (70) → 8S (46) →
  7S (10) → 5D (1 THz, near-resonant) — is a controlled **five-rung, ~68× sweep**
  of intermediate-state admixture **in one apparatus, one method** (8S/9S added
  2026-07-13; they are blue-edge/short-wave-optics reach but fill the gap
  between the clean 6S anchor and the resonant 5D). Walk it with the Ti:Sapph.
- Test Bjorkholm–Liao 1976 + our transit (Lehmann/Biraben) + ramp model: *how* the
  near-resonant intermediate reshapes the line and the intensity-shift ramp, and
  *where* the clean-case approximation (validated at 6S) breaks.
- This is the intermediate-state correction Paper A needs at 5D — so it can be the
  methods §of A, or a short standalone that A leans on. Either way it converts the
  993 nm work from "one transition" into "the clean anchor of a validated model."

### Paper B — *Self-broadening and drift-immune differential polarizability across the Rb 5S→nS/nD ladder (6S, 7S, 5D)* — **series / completeness (a strong thesis capstone)**

- Same rig, Ti:Sapph tuned to 993/760/778 nm: measure β_self, transit(w₀), and the
  drift-immune Δα for each upper state with **one** method.
- **Completes a real series.** Zameroski 2014 measured *foreign-gas* broadening of
  5D & 7S; Weber–Niemax the nS/nD self-broadening series; we add **self** rates +
  the drift-immune AC-Stark Δα(n), tested against the n-scaling (β ∝ C₆^{2/5},
  and the C₆ growth in n that §3.3 computes rather than assumes: the "C₆ ~ n*⁷"
  this bullet used to carry is the scaling of the *polarizability*, not of C₆
  for a ground-plus-excited pair) and the Safronova matrix elements. We find **no modern 6S dynamic
  polarizability at 993 nm exists** — a gap this fills.
- Feasibility: β_self is ~kHz at 6S (needs the fixed-lock session high-T, same-session shot-list
  upgrade already in PLAN §7); 5D/7S sit closer to resonance so *may* broaden more
  and be easier. Lower risk than A, lower ceiling.

## 5. Recommendation & sequencing

*A proposal for discussion, not a decided roadmap: none of the sessions or
papers below is scheduled, agreed, or assigned. The ordering is what the
physics argues for if the programme is pursued at all.*

1. **Finish this analysis (993 nm 5S→6S)** as the clean method demonstrator, then reframe
   its Intro: the *passive, reference-free inversion* of Wieman/Antypas,
   explicitly contrasted with the active 778 nm suppression schemes, on a line no other group is currently working
   transition (quote the USAFA nulls). (This is a vapour-cell Intro edit. It is cheap,
   do it in the vapour-cell pass. The refs are in `LITERATURE.md` §8.)
2. **Paper A + C together** are the high-impact next step: carry the method to the
   778 nm clock line and turn the Ti:Sapph tunability into a magic-wavelength /
   Δα(λ) measurement, with the intermediate-state lineshape (C) as the validated
   bridge from the clean 6S anchor. This is where the tunable laser pays off most.
3. **Paper B** is the completeness capstone — it reuses the exact rig and
   method across the ladder.

**The most distinctive experiment the Ti:Sapph enables** (distinctive, not
necessarily most precise): scanning the 776 nm magic wavelength on 5S→5D and watching
the ramp asymmetry flip sign — a reference-free magic-wavelength determination, on the
most actively worked transition, by a method those groups do not use. Its systematics
are orthogonal and it needs no active hardware, and it needs the large-S₀
small-waist regime to work at all (§Paper A caveat). The lower-risk
complement is **Paper B** (the β_self / Δα ladder), which reuses the exact
rig and method.

## 6. Open feasibility questions for the experimenter (Michelangelo)
- Ti:Sapph output power and lock quality at 760–778 nm vs the 993 nm red edge?
- Is the 420 nm detection path (filter + blue-sensitive PMT) available, or a build?
- Do the EOM (ruler), retro-mirror coatings, and waveplates cover 778 nm as well as
  993 nm, or need swaps? (The intensity-anchor / retro-ratio ρ must be re-characterised
  per wavelength.)
- Cell/oven: 5D/7S may want *lower* density than 6S (they are stronger / closer to
  resonance) — the fixed-lock session shot-list temperature range would differ per transition.

*References for §4 are collected in `docs/LITERATURE.md` §8 (2024–2026 landscape).
Source: the local literature-intake landscape note (untracked).*
