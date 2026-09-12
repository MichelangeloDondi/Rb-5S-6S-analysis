*Chapter 6 of 9 of [the big picture](../BIG_PICTURE.md)*

## 6. What new nanofibre measurements would add

**The question.** What would a guided-atom campaign add that a vapour cell
cannot, and what does it cost the fibre it runs on?
**Takes.** The solved HE11 mode and the guided derivations of
[methods chapter 9](../methods/09_the_guided_geometry.md), and the lever
ranking in `results/onf_lever_ranking.csv`.
**Gives.** What the fibre removes from the width budget, what it measures that
the cell cannot, and the open items the forecast spans instead of assuming.
**Skip if.** You have no fibre. This chapter is the fibre thread's own
surface, declared in [BIG_PICTURE](../BIG_PICTURE.md), and the vapour-cell
result rests on nothing in it.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

> The signal, readout and feasibility budget for running this measurement in a
> guided mode is
> [notes/guided_mode_two_photon_design.md](../notes/guided_mode_two_photon_design.md),
> written for a hollow-core fibre holding either a warm fill or a trapped
> sample, and it is mostly a record of what does not carry over.
>
> **Updated 2026-08-21: the near-surface programme is now budgeted.**
> [The sized candidate](../notes/onf_candidate.md) sizes the optical
> nanofibre platform instrument by instrument, with every number labelled by its
> basis, and the joint forecast in `results/kernel_identifiability.csv`
> computes what a fibre-side laser measurement is worth to the committed
> cell coefficient. [Chapter 9](09_the-campaign-cases.md) states the whole
> case beside the cell-only alternative.

### What the fibre is for, and it is not a better number on the same axis

**The case is identifiability, not precision.** The cell measures one line in
which four channels broaden together, and it separates them only by how each
responds to power, temperature and density. Two of those separations are
weak. The fitted collision-against-laser split is degenerate at **-0.9**, and
the transit-against-laser split runs through the beam waist, which this record
carries as its largest open systematic and which the data bound from below at
38 microns with no ceiling at all.

A nanofibre does not fight those degeneracies. It removes them.

| channel | in the cell | in the evanescent field |
|---|---|---|
| collisional | 0.19 to 0.93 MHz, degenerate with the laser term at -0.9 | **178 Hz** at MOT density. Gone from the budget |
| geometry | w₀ assumed, sets transit and intensity together, no upper bound from the data | no waist. A **diameter**, which is measurable, and a mode that is computable from it |
| transit | cusp, 0.93 MHz, separable by shape | [73 to 98](../../results/onf_candidate.csv "ref:onf_candidate:transit_onf_cold_band:") kHz, and it enters the width at **second order**, contributing a small fraction of itself. A temperature ladder is the only lever that acts on it and it acts weakly |
| residual Gaussian | ~1 MHz unexplained, leading candidate a 0.19 degree retro tilt | no free-space retro to tilt, so the candidate is **testable** and not assumed |
| blackbody | the density lever and the thermal field share one knob | cold atoms against a 300 K room. The two **decouple** |
| atom to surface | absent | Casimir-Polder, a term to **measure** and not avoid |

**Four of those six are the systematics that limit this record now**, which is
why the fibre is not a second opinion on the cell's answer. It is the
instrument that tells you which part of the cell's answer was real.

**The sixth is somebody else's headline.** A group whose main programme is
Rydberg atoms near a nanofibre is limited by the near-surface field, and
[Raj 2026](../lit/raj2026.md) recovers that field as a free parameter of a fit
its own authors call qualitative only. The 5S-6S line is already driven on the
platform and is a low-lying state, so it probes the same environment without
the Rydberg population that complicates it.

### One method the guided programme keeps, and it needs no hardware

The modulation depth is a knob every phase-modulated experiment already has,
and it separates what a power ladder cannot. A phase modulation changes the
spectrum without changing the intensity, so the light shift is the same at
every depth while the excitation rate per tooth follows the Bessel weights and
the power broadening follows their square root. A fitted centre that moves
with depth is therefore not a light shift, and a summed tooth area that moves
with depth is pumping.
[The ramp chapter](../methods/03_the_ac_stark_ramp.md) derives it.

**Why it matters more in a guided geometry than in a cell.** The light shift
near a surface is what a guided programme has to control, and it sits on top
of a surface potential, adsorbate charging and a trap whose depth is itself
set by the light. Those all move with the drive, so a power ladder moves them
together with the shift and a depth ladder does not move them at all. The
method transfers with no new optics, since the ruler's modulator is already in
the beam, and it transfers to whatever line the programme drives next, which
is the property that makes it worth more to a group than a number about
rubidium.

### What the cell arm gives the fibre arm, on one sweep

The plan's lever table already carries the cell and the fibre on one scan and
refuses it as a drift architecture, because the correlation between the laser
and collisional widths is the same in both arms and differencing cancels
nothing. That verdict is about breaking a degeneracy and it stands. **The same
wiring buys something the record has not weighed: calibration transfer.**

A sweep wide enough to hold all four hyperfine components gives the cell arm
three quantities at once. The pair at 2318.537 MHz is fixed by the 85Rb
hyperfine constants alone, so it is an absolute frequency ruler that needs no
piezo calibration and no wavemeter. The co-propagating Doppler pedestal, about
942 MHz wide at 130 C, is a thermometer of the atoms themselves, and the two
isotopes' pedestals have a width ratio fixed by their masses at every
temperature, which makes that thermometer self-checking. The ratio of the
narrow line's area to the pedestal's is nearly stationary in the retro power
ratio near unity, its slope there a fifteenth of the ratio's own since the
narrow line goes as the product of the two beams and the pedestal as the sum
of their squares, so it reads that ratio only slowly, which the hours the
projections put on it carry. A calibrated attenuator in the retro path
does, and [the plan's open-items chapter](../plan/12_open-apparatus-items.md)
carries the law and the run.

**The fibre arm inherits all three for nothing**, because it is the same sweep,
the same laser and the same instant. None of the three can be produced by a
guided measurement on its own: there is no second isotope pair to rule the axis
with, and the trapped sample's velocity distribution is not the cell's. That is
the argument for the shared sweep, and it is stronger than the drift argument
the plan already refused.

**Three things bound it, and all are stated here instead of being discovered on
the bench.** The third is an instrument: the fibre's detector shares the
cell's oscilloscope only if the modulator's radio-frequency gate can be
triggered from the sweep, and otherwise it needs an instrument of its own
([plan 7](../plan/07_acquisition-settings.md)). The pedestal is roughly three parts in a thousand of the narrow line's
height in the cell, and the guided arm has orders of magnitude fewer atoms, so
the pedestal is almost certainly not measurable in the fibre arm itself. It is
the cell arm's instrument, lent to the fibre. And if the modulator sits upstream
of the beam split, the comb is common to both arms, so a setting that suits the
moment channel in one arm is forced on the other. Either the arms take turns, or
a second modulator goes in one of them.

### Two things the host group's own recent papers settle (2026-09-06)

**Their current fibre is thinner than the one this record commits.**
`results/onf_candidate.csv` carries a diameter of 400 nm, cited to the 2020
cold-atom measurement. The group's 2025 fictitious-field paper states a radius
of 175 nm, so a diameter of 350 nm, and the 2026 surface-charge paper's fibre is
370 nm, the middle value the guided-mode tables already carry, so the committed
400 is the thickest of three. Solved at each, the intensity decay length at 993.4 nm is
312 nm at 400 and **492 nm at 350**, a factor of 1.58. **Every guided intensity,
shift and rate in this chapter is keyed on the committed diameter**, and the
band those rows advertise spans a plus or minus 20 nm tolerance about it, which
is four times smaller than the gap between the two candidate fibres. The
diameter is cited and not measured, so this is a discrepancy to settle and not
an error to correct, and it is now the largest single lever on every guided
number here.

**Their trap wavelength lands where this record cannot compute.** The
fictitious-field trap is built at 790 nm, the ground-state tune-out where the
scalar shift on 5S vanishes and only the vector term, which is the trap itself,
survives. Whether 790 nm is also near a differential zero for 5S to 6S is a
natural question and **this repository cannot answer it**. The 6S line list
stops at 8P, whose transition lies at 1028.7 nm, while the 6S to nP series
continues through 13P near 797.9 nm and 14P near 787.1 nm to the ionisation
limit at 737.6 nm. **A trap at 790 nm sits between those two omitted states, a
few nanometres from each**, where their neglected denominators are far smaller
than any term the sum retains. `polarizability.magic_wavelengths` is scoped to
950 to 1500 nm for exactly this reason, and evaluating the differential below
that range returns a number the inputs do not support. The Ti:Sapph chapter's
790.1 nm entry carries the same limitation and now says so.

**What would answer it** is the 6S to 9P through 14P reduced matrix elements,
which no held paper carries. Until then the statement to the group is that
their trap wavelength is interesting for this transition and that its
differential shift there is not yet computable here.

### The platform in print

The group's platform is read here from this record's own notes on three of
their papers. The 2023 paper is a magneto-optical trap overlapped with a bare
fibre, its guided 1064 nm light a surface heater at 300 microwatts, with
detection by trap loss on a photomultiplier
([the note](../lit/vylegzhanin2023.md)). The 2026 surface-charge paper runs
the two-colour trap's light on a 370 nm fibre, counter-propagating 1064 nm
beams and one 762 nm beam with a minimum near 400 nm from the surface about a
sixth of a millikelvin deep, and measures on the MOT's atoms beside it without
reporting a loaded trap ([the note](../lit/raj2026.md)). The 2025
fictitious-field trap is a proposal ([the note](../lit/vylegzhanin2025.md)).
So the red beam this chapter's next section moves exists on the bench, a
loaded trap does not yet, and every row and section of this chapter that
depends on atoms held in the trap is conditional on that loading. What the proposed trap's design then
offers is the cleanest handle on the disputed polarizability this record knows
of: at the ground-state tune-out where it would operate, the trap light shifts
the 5S state by nothing and the 6S state by its own polarizability alone, so
the differential shift of the line under that light is a direct reading of the
upper state's polarizability at that wavelength, a quantity no experiment has
measured at any wavelength. This record cannot compute its value there, since
its 6S line list stops at 8P, so the offer is the measurement and not a
prediction, conditional on that trap being built. Two things the platform can
do with no loaded trap are in the table below, the single guided beam and the
heating beam's power, and a third, the molasses temperature as a knob on the
sampled intensity, waits on the near-surface density model the twin lacks.

### A red beam at 1204 nm would make the trap magic for this transition

An external analysis proposed moving the two-colour trap's red beam from 1064
nm to the record's own 1203.9 nm crossing, and its inputs reproduce from this
repository's modules: the ground-state polarizability is 687.4 a.u. at 1064 nm
and 546.7 at 1203.9, so about 1.26 times the red power restores the depth, and
at the group's 175 nm radius the fibre stays single-mode there, with a
V-number near 0.95. At that wavelength the differential scalar shift from the
red beam vanishes by construction, which removes the trap-light shift and the
need to gate the trap off during the probe, turning a gated snapshot into a
trapped, static line. **The blue beam still shifts the line**, by about 1.9 MHz
at 762 nm against the 7.4 MHz the 1064 nm red now contributes, and no blue-side
crossing is available because that window lies inside the 6S to nP forest.
**Check 1204 nm against the 5S to nP series before adopting it**, since a
trap wavelength sitting near an excited-state resonance is the error the same
analysis made once before with a 685 nm blue beam.

**One number in the same analysis is refused.** It infers an effective mode
area of 1.4 square microns backwards from the group's published trap depth,
and builds a table on it in which one milliwatt guided gives a 1.74 MHz shift.
This record's validated field solve gives 0.62 square microns on the
azimuthal-mean convention and 0.49 on the peak convention at the committed
400 nm, and
[0.826](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_350nm:mode_area_azimuthal_mean")
and
[0.642](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_350nm:mode_area_peak")
at the group's 350, with a shift of 1.253 MHz per milliwatt at the trap site
on the 370 nm fibre of `results/onf_lever_ranking.csv`, so the refusal is a
factor under two at the group's own diameter and over two at the committed
one. The later briefing from the
same source withdrew the 1.4 itself. And the table's claim that the shift
scales as the inverse square of the area is wrong on its face: a shift follows
intensity, which is power over area, so it scales as the inverse first power.

Scanning that red beam's wavelength across the crossing while watching the
line is the magic-wavelength measurement itself, a null that needs no intensity
calibration, and the fibre reaches the shift at a thousandth of the cell's
power, so the trap the fibre programme wants and the crossing the sign dispute
turns on are one experiment.

### The hollow-core case is stronger than the nanofibre one, and for a reason neither shares with the cell

A nanofibre puts atoms in an evanescent tail outside the glass. A hollow-core
fibre puts them inside a mode that does not diverge, and that second fact is
worth more than anything in the sections above. The interaction length stops
being a beam property and becomes a length of fibre:
[100.0000](../../results/platform_twins.csv "ref:platform_twins:hcpcf_warm:hcpcf:length_eff_mm")
mm of vapour-filled kagome mode holds more atoms in the probe than a tightly
focused beam reaches in a cell, and reads out at a signal-to-noise within a
small factor of one.

**For a host group the practical consequence is the observable.** A cell hands
you fluorescence against a dark background. A fibre hands you a transmission
dip, which an ideal shot-noise-limited photodiode would resolve at
[0.00604294](../../results/platform_twins.csv "ref:platform_twins:hcpcf_warm:hcpcf:absorbed_fraction")
with vapour in the mode and a part-per-million measurement at
[2.05542e-07](../../results/platform_twins.csv "ref:platform_twins:hcpcf_cold:hcpcf:absorbed_fraction")
once the vapour is replaced by a cold loaded column. The second number is the
one that decides whether a cold guided experiment is a measurement or a
proposal, and it rests on a shot-noise-limited detector this record has not
demonstrated.

**And on an atom number the host group's own measurement does not support.**
The cold guided row puts about a hundred and thirteen thousand atoms in the
mode. [Xin and co-workers](../lit/xin2018.md) load a hollow-core fibre and use
about ten thousand, read in transmission. The dip counts the atoms the mode
drives, not their spacing along it, so the comparison is those two numbers: the
row is optimistic by eleven, or by five against the larger count the paper's
own optical depth implies. **The arm survives that, slowly.** Both the dip and
the signal-to-noise fall by that same factor, because the probe flux setting
the shot noise does not move, so the row's committed
[2.51759](../../results/platform_twins.csv "ref:platform_twins:hcpcf_cold:hcpcf:snr_per_s")
per second divided by eleven, or by five on the larger count, is what the arm
delivers: the measurement that took sixteen seconds at the assumed number takes
about thirty-four minutes on the first reading and seven on the second. The loading efficiency behind it, a fifth of a per cent to three
per cent from a free-space trap, is [Wang and co-workers](../lit/wang2020.md).
What the cold platform buys instead is the transit width, which at one
microkelvin is a twenty-thousandth of the warm value, the square root of the
temperature ratio with the mass and the waist cancelling out, and that is the
width this record's own fits cannot separate from the collisional one. The
cooling that reaches it inside the fibre is
[Wang and co-workers](../lit/wang2022.md).

### What a guided arm adds to a joint fit, which is not its own signal-to-noise

A fibre arm would be run beside the cell, the trap and the nanofibre, so what
it is worth is what it does to the joint problem. This record's bound fails on
four couplings: the collisional width against the transit at
[-0.958](../../results/identifiability.csv "ref:identifiability:corr:gamma_coll_transit"),
the laser width against the collisional at
[-0.9411](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:cell:corr_laser_coll_5traces"),
a Lorentzian laser component and the collisional width entering only as their
sum, and a beam waist nobody has measured, which is why every absolute result here is a bound
and not a value. A guided arm attacks two of the four by geometry alone, and a cold free-space
arm attacks a third.

**The warm fibre shares its collisional width with the cell and cannot share
its transit.** Vapour at the same temperature has the same density and the same
collision physics, so that width is identical in the two arms by construction,
while the transit differs because the mode is
[19.000](../../results/platform_twins.csv "ref:platform_twins:hcpcf_warm:hcpcf:w0_um")
microns against the cell's
[64.000](../../results/platform_twins.csv "ref:platform_twins:cell_130C:cell:w0_um"),
giving
[3.22518](../../results/platform_twins.csv "ref:platform_twins:hcpcf_warm:hcpcf:transit_fwhm_mhz")
MHz against
[0.957477](../../results/platform_twins.csv "ref:platform_twins:cell_130C:cell:transit_fwhm_mhz").
Two arms, one shared nuisance, two different transits, and the fibre's
transverse scale is a manufactured mode field diameter with a datasheet, not
an alignment that drifts. So the pair returns the collisional width and
the cell's own waist, which is the foundational calibration the plan ranks
first and the reason every absolute number here carries a bound.

**A free beam locks the shift to the interaction length, and a fibre does
not.** The light shift goes as the inverse square of the waist while the
Rayleigh range goes as its square, so focusing buys shift and pays it straight
back. Tightening the cell from 64 to 16 microns multiplies the shift by sixteen
and divides the interaction length by sixteen, from
[12.9535](../../results/platform_twins.csv "ref:platform_twins:cell_130C:cell:length_eff_mm")
mm to
[0.8096](../../results/platform_twins.csv "ref:platform_twins:cell_130C_tight:cell:length_eff_mm"),
taking the atom count down with it. A guided mode does not diverge, so its
length is the length of fibre: the warm row carries
[100.0000](../../results/platform_twins.csv "ref:platform_twins:hcpcf_warm:hcpcf:length_eff_mm")
mm. Intensity and length become two knobs where the cell has one, and the
campaign can reach the shift its third-cumulant channel needs without
collapsing the interaction region to under a millimetre.

**The trap and the molasses switch off both unseparable widths at once.** In
the cold rows the transit is
[0.00233615](../../results/platform_twins.csv "ref:platform_twins:mot:mot:transit_fwhm_mhz")
MHz and the density three orders below the cell's, so the line is the natural
width plus the laser plus saturation, and the natural width is established here
at 210 sigma. At weak drive that line measures the laser width directly,
through the atoms' own optical path. The plan puts a per-cent laser-width
instrument at a factor of two on the coefficient's error, and this is that
instrument without new hardware.

**The convolution condition is exact in a guided mode.** A convolution holds
only where the homogeneous kernel is the same at every collected element, and
in a free beam the transit follows the local beam radius, so the kernel varies
along the axis by one per cent at 64 microns and by nearly half at 16. A guided
mode has the same transverse profile at every point along it, so the condition
holds identically. The shape channels, which is to say the asymmetry this whole
programme reads, are clean in the fibre at every length and contaminated in the
cell exactly where the campaign wants to work.

**And the observable carries no collection geometry.** A transmission dip is a
ratio of two powers on one detector. The cell's fluorescence arm carries an
axial collection window that biases the extracted shift and reverses sign past
a window-to-Rayleigh ratio this bench sits a factor of four inside. The fibre arm
has no such term to get wrong.

### What a guided trap costs this line, which is the design problem

The trap light shifts 5S and 6S by different amounts, so a trap deep enough to
hold a sample displaces the line and, because the atoms sample a range of
intensities, broadens it. At the wavelengths
[Wang and co-workers](../lit/wang2020.md) use the ground-state polarizability
is positive and the 6S one negative, so the two levels move apart and the line
shift *exceeds* the trap depth, and is not a small residue of it. Re-derive
with `rb5s6s.polarizability.alpha_5s` and `alpha_6s`, and size the depth with
`rb5s6s.platforms.trap_depth_uk`, which owns the intensity convention: the
excess is about seven per cent at 821 nm, one per cent at 797.25 and two and a
half at 802, so it is a wavelength-by-wavelength number and not a single
factor.

**The size of it is the problem.** In the 313 microkelvin trap of that paper's
first column the displacement is about seven megahertz, and the spread over a
sample at one to two hundred microkelvin across the fibre is one to one and a
half. Against a natural width of 3.493 MHz that is a dominant inhomogeneous
term, not a correction, and a ten millikelvin trap exchanges it for a two hundred
megahertz displacement with a two to four megahertz spread.

**A claim withdrawn, 2026-09-11.** An earlier form of this section argued
that the same physics made the transition a probe of the differential light
shift limiting the host group's own interferometer, at a leverage of about two
thousand. The coefficient ratio is real and the conclusion does not follow: a
probe resolves a shift against *its own* linewidth, and their ground-state
coherence gives a line of a few hertz where this one is megahertz wide. Their
clock transition measures the trap's intensity distribution some three orders
of magnitude better than this line could. What this line has instead is a
large and calculable differential polarizability, which suits it to an absolute
intensity or mode-area calibration and not to out-measuring their clock.

**And the escape is a magic trap, which nothing here has evaluated.** A
wavelength where the two polarizabilities are equal removes the displacement
and its spread together. [`docs/plan/11`](../plan/11_beyond-993.md) already
names the 5S-6S crossing near 1297.5 nm as a shift-injection lever and calls it
useless as a trap. On depth that verdict holds at a few hundred milliwatts and
fails at a watt or more, since the ground-state polarizability there is only
about eight times smaller than at 821 nm. Whether a hollow-core mode guides both that and
993.4 nm, and whether the crossing survives a sum that currently truncates at
8P, are open items in
[`docs/plan/12`](../plan/12_open-apparatus-items.md).

**Which rung these stand on, because it decides what may be claimed.** Every
argument in this section is physics and closed form: a shared collisional width
at two known transits, a light shift going as the inverse square of a
transverse scale against a Rayleigh range going as its square, a kernel that
does or does not vary along the axis, and two polarizabilities of opposite
sign. None of it is a twin forecast. **What the twin has not yet run is the joint
fit**, which is the number a proposal would quote: the error on the
coefficient from a cell arm and a guided arm fitted together with the
collisional width shared, against the cell alone. The paired-reference
forecast covers a cell-plus-nanofibre pair and has no hollow-core arm, so that
run is owed before any of this becomes a figure instead of an argument.

### What the guided arm measures that no cell can, and the observable that survives the radius

The guided light shift is a translation of the whole line and not an asymmetry
of a per cent, so at the record's 1.253 MHz per milliwatt
(`results/onf_lever_ranking.csv`) a few milliwatts move the line by a
linewidth, in a direction the two published signs of the differential
polarizability predict oppositely. The record settles that sign from the
measured 6S lifetime, and the guided arm reads it by inspection in a day, on an
apparatus that exists, and that is the confirmation to lead with. **The
observable that survives the fibre's own open item is a ratio.** The absolute
shift carries the mode area, hence the radius nobody has measured. The ratio of
the probe's shift to the trap light's shift at the same site carries the ratio
of two polarizabilities and the ratio of two intensities on one mode, and a
five-nanometre radius error moves that intensity ratio by under a per cent. On
the record's polarizabilities the ratio at 993 to 1064 nm is 1.42. It is the
trapped-ion light-shift-ratio method, whose lit note this record owes, and it
is the first determination of a 6S polarizability that does not ride on a beam-waist prior.

### The guided-platform open items

Listed here and not in [the plan's open-items chapter](../plan/12_open-apparatus-items.md),
which stays platform-neutral. Each is spanned by a producer or nothing rests
on it.

| item | what it changes | how the forecast proceeds |
|---|---|---|
| **the vector light shift of the guided mode** | the m_F structure of every guided line: the mode's longitudinal component makes the field's E* x E non-zero, and for two J = 1/2 states the tensor term vanishes while the vector term does not, so each hyperfine line is a set of m_F components under one fitted width | measured to exist on this transition at this laboratory's fibre, where polarisation alone does not extinguish the guided two-photon signal ([Ray 2020](../lit/ray2020.md)). Optical pumping into one m_F, a bias field, or the m_F-weighted lineshape in the model before the first guided fit |
| **the 6S decay rate at the trap site** | the guided line's natural width, which at the fibre is nearly the whole width once transit, collisions and Doppler are gone: a modification of a fifth would move it by 0.7 MHz | unmodelled in this record, which carries the free-space lifetime. Expected small, since the 6S decays at 1.3 microns where the fibre is a fifth of a wavelength across and the atom sits near three radii out, and in that limit the quasistatic term dominates with the guided contribution exponentially small ([Klimov and Ducloy 2004](../lit/klimovducloy2004.md), held). Computed with the Green's function of a dielectric cylinder before the first guided fit, and measured, it is a nanofibre-QED result on a lifetime known to 0.4 per cent |
| **the cloud's temperature against its density at the probe radius** | one potential sets both, so a temperature change is a density change and the guided transit's ensemble factor moves with it. A modelled correlation and no free lever | the trap potential, once the radius and the two powers are known, and clean in the sense that the coupling is computed and not read from a vapour-pressure curve |
| **the guided beam geometry, one beam or two** | whether the guided line is one component or two, whether the retro ratio and the comb's path-delay factor enter, and whether frozen fringes raise the rate-weighted mean shift by five thirds and spread it to four times the forward shift | at 150 uK the co-propagating Doppler width is a sixth of the natural width, so a single guided beam costs under three per cent of width and removes all three, a twin question once the guided world builder carries both geometries (2026-09-06) |
| **the 1064 nm heating beam as a potential** | on cold atoms the host's 300 microwatt guided 1064 nm light is an attractive potential on the ground state, computed with this record's mode solver on the azimuthal-mean convention (the guided power over the mode's effective area at the surface, then the solved flux profile) at 20, 10 and 2 microkelvin at 200, 400 and 1000 nm from the 2026 paper's 370 nm fibre, beside a van der Waals term from the committed coefficient of 5 microkelvin at 200 nm and under one at 400 | nothing at the 140 uK of the MOT, half of the thermal energy in a 20 uK molasses, where its power becomes a lever on the sampled intensity distribution with no loaded trap, conditional on a near-surface density model the twin does not carry. That beam also shifts the line itself, by about 0.4 MHz at 200 nm from the surface on the record's polarizabilities, an eighth of the natural width. And it is the adsorption heater the group runs it for, so turning it down costs the fibre what the adsorption row weighs (2026-09-06) |
| **the thermal near field of the fibre** | the blackbody shift at the atom's position, which the record takes as free space | the atom sits within a twentieth of the thermal wavelength of a warm dielectric with phonon resonances in the thermal band, so the free-space shift is a lower bound and the near-field value is unevaluated (2026-09-06) |
| **fibre diameter tolerance** | the mode area, and through it every guided intensity, shift and rate | a stated tolerance propagated through the mode solve in `results/onf_candidate.csv`, worked out with its two cited precisions in the open item further down this page  |
| **two-photon ionisation rate from 6S** | whether the probe perturbs the surface charge it reads | no forecast rests on it. Single-photon ionisation is excluded by [0.433](../../results/campaign_twin_forecast.csv "ref:campaign_twin_forecast:model:photoionisation_margin_from_6S") eV, and the surviving claim is narrower: a 5S-6S probe populates no Rydberg state, so the Rydberg-ground mechanism is absent by construction |
| **the evanescent envelope the transit kernel is built on** | [methods chapter 9](../methods/09_the_guided_geometry.md) section 9.1 states that the exponential approximation is not available at these radii, since $qa$ runs 0.18 to 0.32, and section 9.2 then builds the whole transit kernel on a plain exponential decay in time | **no forecast spans it, and it is the largest known error on the temperature ladder's value.** Carrying the chapter's own solved profile through shortens the effective decay length against the nominal 401 nm, and the kernel enters at second order so the width a ladder reads moves by the square of that factor. **The size depends on which effective length is meant and the definition has to be named.** Matched on the second moment, the quantity the added width depends on, the solved profile gives about 270 nm against the nominal, and about 2.2 on the width. A second evaluation of the same integral, written independently, lands a few nanometres shorter, so the length is good to about the nearest ten and the width factor to the first decimal. A log-linear fit over the first 600 nm gives about 218 nm and 3.3. **The second-moment length must exceed the fitted one**, because the profile's local decay length rises outward, 183 nm at 50 nm from the surface to 340 nm at two microns. **The direction is conservative under every definition**: the fibre lever is stronger than this chapter currently claims, so closing it is a gain and not a retraction. It is derivable and needs no apparatus fact, so it is mathematics and not a question for the group |
| **Rb adsorption against exposure time** | how long the fibre runs before its transmission degrades, which bounds the whole arm and is what the campaign costs the fibre itself | no forecast rests on it. `results/campaign_twin_forecast.csv` reports the integration time so the exposure is visible, but nothing converts exposure into degradation |
| **the trap's azimuth around the fibre** | which field magnitude an atom sees, and so every guided light shift. The field varies by about a third between the polarisation axis and perpendicular to it | spanned by a committed pair in `results/guided_mode_tables.csv`, the azimuthally averaged `stark_fraction` beside the on-axis one. The tensor term vanishes for this transition, both states having $J=1/2$, but the vector term does not, and a guided mode is strongly elliptically polarised near the surface. So the committed pair is a lower bound on how much the azimuth matters |
| **trap position and its thermal spread** | the intensity at the atom, and the atom-surface distance the surface term depends on | the distance-scan lever reaches a fractional [0.2895](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:distance_scan:sigma_lambda_frac") on the decay length at the 2025 lock, and under a hundredth at the photon floor. The spread itself is unmodelled and no forecast rests on it |
| **the Doppler pedestal's detectability in the guided arm** | whether the shared-sweep thermometer can be read at the fibre as well as lent to it | no forecast rests on it. The cell arm supplies the temperature either way, and the guided pedestal would measure the trapped sample instead of the vapour, which is a different and more valuable quantity if it is reachable at all |
| **whether the modulator is upstream of the beam split** | whether the comb state can differ between the cell and fibre arms in one sweep | no forecast rests on it. Every committed cell is single-arm. It decides only whether the two arms can hold different comb settings at once, or must take turns |

### The mode is now solved, and the assumption it replaces was wrong

`rb5s6s.fibre.solve_he11` solves the HE11 eigenvalue equation for a fibre in
vacuum, checked against two effective-index values standard for this geometry, which no note in this record cites to a paper, and against an independently written solver. The derivation,
with the transit, light-shift and atom-surface terms in the evanescent
geometry, is [methods chapter 9](../methods/09_the_guided_geometry.md). It replaces
`neff_band = 1.08 to 1.25`, which was tagged `assumed_parameter` and which
corresponds at 993 nm to fibres of **485 to 796 nm**. The fibres this group
runs are 350 to 400 nm, so the assumed band did not contain the apparatus.

| fibre | n_eff at 993.4 nm | amplitude 1/e | single mode |
|---|---|---|---|
| 350 nm | [1.01283](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_350nm:neff") | [984](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_350nm:amplitude_decay_length") nm | yes, V = 1.16 |
| 370 nm ([Raj 2026](../lit/raj2026.md)) | [1.01927](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_370nm:neff") | [802](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_370nm:amplitude_decay_length") nm | yes, V = 1.23 |
| 400 nm ([Rajasree 2020](../lit/rajasree2020spin.md)) | [1.03164](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_400nm:neff") | [624](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_400nm:amplitude_decay_length") nm | yes, V = 1.33 |

**Both defects it exposed are now fixed in the producer**, and twenty of
that file's rows moved. The band is computed from the diameter, and the
amplitude and intensity lengths are carried separately after the formula was
found returning one while labelled the other.

**The mode is not in the exponential regime at all**, since `q*a` is [0.231](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_370nm:qa") on the 370 nm fibre where the asymptotic form needs it far above one.

**The effective mode area is a convention as much as a number.** It is
**[0.615](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_400nm:mode_area_azimuthal_mean") µm²** as power divided by the azimuthally
averaged surface flux, and [0.489](../../results/guided_mode_tables.csv "ref:guided_mode_tables:mode_solve_400nm:mode_area_peak")
on the polarisation axis, so it is not quotable without saying which. Both come
from vector fields checked against their own boundary conditions before
integration. Earlier values are in HISTORY.

**What is not yet settled, stated so nothing rests on it.** No published
source gives a diameter tolerance for these fibres. Three routes were listed
here, and **the one this chapter recommended has since been costed through the
twin: the route is open, and it is worth about three times less than the
chapter assumed.** Nothing has been measured. Every precision below is an
`ENVELOPE` row from a design calculation, which is the third rung of the
ladder and not the first.

The group has scanning electron microscope access, and the published proximity
to the 352 nm mode cutoff at 480 nm gives a sharp diameter diagnostic. The
third route was sweeping the atom-surface distance and fitting the decay, and
this chapter called it the one the campaign can perform, measuring the quantity
that actually enters rather than a proxy for it.

**It reaches the diameter to about
[30.73](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.04:sigma_diameter_nm") nm at the
2025 drifting lock and
[0.67](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.0:sigma_diameter_nm") nm at the
photon floor.** The lock was repaired in August 2026 and its residual is
unmeasured, so the campaign sits inside that span.

**The design must marginalise over the drive's own surface shift**, which the
scan cannot know and the power sweep measures. Amplitude against decay length
is the classic degeneracy of a short near-exponential scan, and holding the
amplitude fixed makes the lever look about twice as good as it is. Earlier
values are in HISTORY.

**The route the campaign can run itself is open, and it is worth less than
this chapter claimed.** A repaired lock is what makes it competitive with the
10 nm the chapter originally assumed. At the 2025 rate it is not. SEM and the
mode-cutoff diagnostic stay as independent cross-checks, and they matter more
than they did.

The evanescent field of an optical nanofibre is, in one sense, the natural
home of the ramp physics: the intensity gradient is steep and exponential,
so the local light-shift distribution is large and strongly shaped. What
carries over is the operation the record is built on, mapping a known
intensity geometry onto a shift distribution and reading its cumulants. The
closed-form ramp weight itself does not. It is derived for atoms **crossing** a
focused beam, and a trapped sample sits concentrated where the intensity is
highest, so its shift distribution has no hard edge and carries the opposite
a skewness about three times larger with no hard edge (section 1.2 of the
design note, which computes both).
Carrying the ramp over unchanged would get the sign of the line's asymmetry
wrong, and the self-centred third cumulant is the drift-immune channel this programme
relies on, where the shift is large against the line, as it is in the
evanescent field and is not at the 2025 cell's waist.

![the third cumulant as an observable: the two-photon asymmetry, the cumulant ladder, what each mechanism reaches, and the ceiling the record's bound puts on it](../../figures/fig30_third_cumulant.png)

*Figure 30. Why this channel is worth the session. The first panel shows what
the ramp does to the observable, and the difference below it is the
antisymmetric one-lobe-up, one-lobe-down signature that the third cumulant
measures. The third panel is the argument: every symmetric kernel contributes
to the variance and nothing to a self-centred κ₃ (the Lorentzian to the truncation fraction
[the condition](../wiki/third-cumulant.md) quantifies), so
the collisional-against-laser
degeneracy that dominates the width budget cannot reach it. The ramp is the
only asymmetric term in the model.*

![the third cumulant computed on real traces: one trace folded about its centroid, the measured cumulant against power for two peaks, and the gap to the prediction](../../figures/fig31_third_cumulant_measured.png)

*Figure 31. And what the 2025 data actually say in it. The folded residual in
the first panel is noise, the measurements in the second straddle zero and the
two peaks disagree in sign, and the third puts the gap at a factor of about
2800 between the prediction at the record's own bound and the error on a single
condition. Because κ₃ goes as the cube of S₀, closing that gap needs about
fourteen times the ramp depth, which is fourteen times the power or a waist
smaller by a factor of 3.8. This measures the instrument's reach in this
channel, not the ramp.*

The group has already demonstrated the hard part. 5S–6S excitation in the
evanescent field of a nanofibre works on cold atoms
([Rajasree 2020](../lit/rajasree2020spin.md)'s count rates are the existence
proof). What does not exist, anywhere, is a **quantitative near-surface
lineshape program**:

- a fitted model of [Gokhroo 2022](../lit/gokhroo2022.md)'s pushing dip (its position, width and
  power dependence), which needs the force and density dynamics *plus* the
  lineshape pieces this repo provides, and the ramp is one ingredient, not
  the whole model
- the atom–surface (Casimir–Polder) shift and distortion that rides on the
  line for atoms within ~100 nm of the glass
- optionally, distance-resolved spectroscopy in a two-colour trap, where
  the red/blue power ratio tunes the atom–surface distance. That is the
  trapped case, so it needs the trapped shift distribution rather than the
  ramp. It is ambitious, and the per-distance signal budget is an open
  question.

**The group's own Rydberg work says the same thing about itself, which is
better evidence than our saying it.**
[Vylegzhanin 2023](../lit/vylegzhanin2023.md) excites Rydberg nS and nD states
through the evanescent field of the same kind of fibre, and fits each spectrum
with an *empirical skewed Gaussian* chosen to absorb the 1064 nm AC Stark shift
and the atom–surface interaction together. That locates a resonance well and
separates two mechanisms badly. The paper is explicit about what it therefore
leaves out: DC Stark shifts *"are not included as we have no experimental
mechanism for quantifying them"*, with stray fields and charging of the fibre
called *"difficult to quantify with no electrodes in the vacuum chamber"*.

A lineshape is not an electrode, and that is the opening. The quantity they set
aside is a field, the 6S line is already driven on this platform, and reading a
shift distribution out of a measured line with a stated prior is what §4–5
does in the cell. Note the scale is state-dependent and the two numbers do not
contradict: the Casimir–Polder shift on a *Rydberg* state is of order GHz
within 300 nm of the fibre, far larger than the ~100 nm scale that matters for
the low-lying states above.

[Vylegzhanin 2025](../lit/vylegzhanin2025.md) is the companion proposal, a trap
holding a ground and a Rydberg state in one potential built on the vector shift
at the 790.2 nm tune-out wavelength and matched by detuning to 788.1 nm. It is
a proposal and says so. What a trap engineered to cancel a differential shift
still needs is a measurement showing it cancelled, and the residual is a
distribution across an evanescent field, which is the same object again.

**A design validation exists for the temperature lever.**
`results/fibre_twin.csv` asks whether a molasses temperature ladder can
separate a guided transit contribution from a temperature-independent
homogeneous one. **That separation is harder than this chapter first stated**:
the guided kernel enters the width at second order and contributes only a few
per cent of its own FWHM, and the width a ladder sees grows as $T$ and not
as $\sqrt T$, so a ladder reading it through the total width has both less
signal and a different shape than an additive treatment implies. Under synthetic worlds calibrated to the
per-condition width precision this record already achieves, it identifies the
common Lorentzian component at [0.9640](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_312nm:coverage_gamma_l") and [0.9580](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_492nm:coverage_gamma_l") coverage at the two
decay-length band edges, and does **not** identify the Gaussian one, at
[0.4040](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_312nm:coverage_sigma_g") and [0.3760](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_492nm:coverage_sigma_g").
A single-rung control fails to split, which is what makes the ladder the lever,
not the fit. **Those worlds inject the transit width into the additive
Lorentzian channel, which the second-order result above shows is not how the
kernel enters**, so the coverage rows describe a design under an assumption the
same chapter now retracts, and re-running them against the correct kernel is
the next item and not a refinement. This is simulation-backed and not a
measurement: it says the design can identify the intended quantities under
stated worlds, not that
the apparatus will.

The cell line of §4–5 is the in-vacuo reference against which every
near-surface effect would be read. That is the connection between
the two halves of the program: the cell work is what makes the nanofibre
lineshapes *interpretable*.

---

*[The next vapour-cell session](05_next-vapour-cell.md) · [Limitations and identifiability](07_limitations-and-identifiability.md)*
