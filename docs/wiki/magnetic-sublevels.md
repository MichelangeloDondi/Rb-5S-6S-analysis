# Magnetic sublevels

*[wiki index](README.md) · concept*

**The question.** What the $2F+1$ magnetic sublevels of a level are, and
when averaging over them versus resolving one individually changes what a
measurement reports.
**Takes.** The $F$ levels [Hyperfine structure](hyperfine-structure.md)
builds, nothing else assumed beyond that.
**Gives.** The Zeeman splitting per sublevel and the scalar, vector and
tensor decomposition of the light shift across them.
**Skip if.** the reader wants the $F$ levels themselves rather than the
$m_F$ structure inside each one, in which case
[Hyperfine structure](hyperfine-structure.md) is the right page.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A level of total angular momentum $F$ is not one state but $2F+1$ of them,
labelled by the projection $m_F$, running in integer steps from $-F$ to $F$.
In zero external field every one of these magnetic sublevels carries the
same energy: nothing in the level's internal structure picks out a
direction, so nothing separates them. A magnetic field breaks that symmetry.
Coupling to the field through the level's magnetic moment, each sublevel
shifts by an amount proportional to $m_F$, to leading order
$\Delta E(m_F) = g_F \mu_B B m_F$, with $\mu_B$ the Bohr magneton and $g_F$
the level's own g-factor, the zeeman effect. The adjacent-sublevel spacing
$g_F \mu_B B$ is set entirely by $g_F$, so two levels sitting at the same
energy in zero field can respond completely differently once a field is
applied, and the size of that response is itself built from how the
electronic and nuclear angular momenta compose to make $F$ in the first
place, the subject of [hyperfine structure](hyperfine-structure.md).

That internal structure has a direct consequence for what an ordinary
measurement reports. In an unpolarised sample, with no field defining a
preferred direction and no process favouring one sublevel over another, the
$2F+1$ sublevels sit at equal population, weighted only by their own
degeneracy. Whatever a bulk measurement reads off, a rate, a shift, a line
strength, is an average over that whole manifold, not the property of any
one sublevel. Give the sample a defined quantisation axis, an applied field
of known direction, and a way to prepare or select a single $m_F$, optical
pumping or state-selective detection, and the average collapses into one
specific number that belongs to that sublevel alone.

The light shift is where this distinction stops being bookkeeping. The
AC-Stark shift of a level under off-resonant light separates into three
pieces by tensor rank. The scalar part is the same for every sublevel: it
has no $m_F$ dependence and no sensitivity to the light's polarisation
state, so it is what survives any averaging. The vector part depends
linearly on $m_F$ and on the light's degree of circular polarisation, acting
like a fictitious magnetic field pointed along the light's propagation
direction, and it vanishes for purely linearly polarised light regardless of
$m_F$. The tensor part depends quadratically on $m_F$, through a factor
proportional to $3m_F^2-F(F+1)$, and it needs the level's own angular
momentum to be at least one: a rank-2 operator cannot be built from an
angular momentum of $1/2$, so it is identically absent for any such level no
matter how the light is polarised. In an unpolarised, unprepared sample the
vector and tensor pieces average to zero across the equally populated
sublevels and only the scalar part survives, which is why a bulk
measurement can report a single polarizability. In a trapped, field-defined,
state-prepared sample none of that averaging happens, and the vector and
tensor pieces become quantities in their own right rather than a
correction folded into one number.

## What problem it solves

It draws the line between when "the $F$ level" is a sufficient description
and when the finer structure inside it has to be tracked. It also explains
why a light shift that looks like an unavoidable, single-number systematic
in one kind of sample turns into several independently informative
quantities in another: the scalar part is a background to subtract, while
the vector part reports on the light's circular character and the tensor
part reports on the level's own angular structure, both otherwise
invisible.

## Where this repository uses it

This repository's two levels, $5S_{1/2}$ and $6S_{1/2}$, are both $J=1/2$,
so their tensor light shift does not exist to find, at either wavelength
and under any polarisation, the same triangle rule stated for the
magic-wavelength crossings in
[BIG_PICTURE, why this line](../big_picture/01_why-this-line.md). The
vector part is not forbidden for either level, only switched off by the
apparatus itself:
[the optics protocol](../plan/03_optics-protocol.md) fixes the precision
path at one shared linear polarisation axis, under which the two-photon
line is $m_F$-blind by construction and the vector channel is brought in
only as an optional circular diagnostic, off that precision path. Between
the two, [`rb5s6s/polarizability.py`](../../rb5s6s/polarizability.py)
computes a single scalar polarizability for each level (`alpha_5s`,
`alpha_6s`, `delta_alpha`), and that is not a simplification of convenience,
it is the whole content a $J=1/2$ pair under linear light has to give.

The degeneracy weighting this page opens with is exactly what predicts the
four measured line strengths.
[`rb5s6s/amplitudes.py`](../../rb5s6s/amplitudes.py) derives each peak's
relative area from abundance times $(2F+1)$ over the isotope's total
ground-sublevel count, 8 for $^{87}\text{Rb}$ and 12 for $^{85}\text{Rb}$
(the same $F$ values [`constants.PEAKS`](../../rb5s6s/constants.py)
carries), with no preference for any one $m_F$ built in anywhere, a
prediction that only holds because the driving operator is scalar in the
first place.

What a defined quantisation axis and a prepared sublevel can buy is not
speculative. [Duspayev and Raithel](../lit/duspayev2023.md) trap
$^{85}\text{Rb}$ in an optical lattice and resolve a $J=3/2$ level's magic wavelength
splitting by $m_J$, a tensor effect with nothing analogous available to a
$J=1/2$ pair in a warm cell. The residual this repository's own record
still carries once the tensor and vector channels are both closed off is a
shift proportional to $\Delta g_J$ alone, at the sub-kilohertz-per-gauss
level ([the optics protocol](../plan/03_optics-protocol.md)), small enough
that no field-dependent term appears in any fitted model here.

## An S-to-S two-photon line is magnetically quiet, twice over

The 5S to 6S line is protected against a laboratory field by two independent
cancellations, and the numbers are worth carrying because they say when the
protection runs out.

First order. With identical linear photons the two-photon operator is
scalar, driving $m_F$ to the same $m_F$, so a component shifts by
$m_F (g_F^{6S} - g_F^{5S}) \mu_B B$. Both states are $S_{1/2}$ with the
same hyperfine structure: the nuclear part of $g_F$ cancels exactly, and the
electronic $g_J$ difference between the two S states is a core correction of
order $10^{-4}$, leaving under 140 Hz of spread at the Earth's 50 uT against
a line millions of hertz wide.

Second order. The Breit-Rabi quadratic term scales as
$(g_J \mu_B B)^2 / \Delta_\text{hf}$, under 3 kHz per state at Earth field.
The line barely moves, but a hyperfine pair separation inherits the
difference of two such terms, near one to two kHz, which matters exactly
once in this record's plans, at the coincidence block that reads the 6S
splitting to a few hundred hertz.

The cancellation is a property of $\Delta m_F = 0$ and of nothing else, so
the components that would not cancel are worth sizing before they are
dismissed. Because $g_F$ is the same in both states, a component with
$\Delta m_F = q$ shifts by $q g_F \mu_B B$, which is independent of $m_F$:
every such component moves together, as a displaced satellite rather than as
a spread. For $q = 2$ that is 700 kHz at the Earth's 50 uT on either
rubidium-87 line and 467 kHz on either rubidium-85 line, 13 and 9 per cent
of the 5.37 MHz observed width. A $\Delta m_F = \pm 2$ channel at any
appreciable strength would therefore be a visible broadening, and the reason
it is not one deserves a number rather than a rank.

Why that channel is not there, put the way a reader would check it. Two
sigma-plus photons carry two units of angular momentum and the natural
expectation is that the atom takes them. It cannot. In an S state the
electron's $m_J$ runs over exactly two values, $-1/2$ and $+1/2$, so the
largest change any operator can make is one unit. The nucleus could absorb
the other one, and the electric dipole operator does not touch the nucleus.
So a sigma-plus sigma-plus pair has nowhere to put its second unit: the
matrix element is zero rather than small, and that polarisation combination
does not drive an S to S two-photon transition at all. This is the ordinary
reason such spectroscopy uses linear or opposite-circular light.

The counter-propagating pair does not change this, and it is the place the
intuition most wants it to. In a retro geometry the two beams' linear momenta
cancel, which is the whole point, and it is tempting to expect the angular
momenta to cancel with them. They add. A photon of helicity $\lambda$
travelling along $\hat{n}$ contributes $\lambda (\hat{n} \cdot \hat{z})$
about the quantisation axis, so a forward photon with $\lambda = +1$ and a
returned photon with $\lambda = -1$ both contribute $+1$: the reversal of the
propagation direction is cancelled by the reversal of the helicity, and the
pair carries two units, not zero.

And the light really does offer two units, which is the part worth being
careful about. Linear polarisation is not one handedness: $\hat{x}$ carries
equal amounts of both circular components, in either direction, so the
counter-propagating pair offers all four products and the co-rotating ones
are not absent. Their amplitude in the field is one half, the same as the
opposite-handed pairs:

| pairing | amplitude in the field | $\Delta m$ | outcome |
|---|---|---|---|
| $\sigma^+\sigma^-$ and $\sigma^-\sigma^+$ | $-1/2$ each | 0 | drives the line |
| $\sigma^+\sigma^+$ and $\sigma^-\sigma^-$ | $+1/2$ each | $\pm 2$ | offered, and refused |

So nothing about the geometry or the polarisation removes the two-unit
pathway. It is delivered at full strength and the atom declines it, because
the rank-2 reduced element between two $J = 1/2$ states is zero. The
amplitude is one half in the field and zero in the matrix element.

The special case of co-rotating circular light is the same fact seen from
the other side: there the opposite-handed pairings are the ones that are
absent, $\vec{e}_1 \cdot \vec{e}_2$ vanishes with no conjugate because both
photons are absorbed, and the transition simply does not happen at all. That
is why this spectroscopy uses linear or opposite-circular light.

A field that is not along the beam adds nothing either. Tilting the
quantisation axis re-mixes which combinations are available from the light,
and changes nothing about what the atom can accept, which is the binding
constraint. The rule is atomic and not geometric.

The same statement in the coupled basis is the rank argument: the two-photon
operator is a product of two rank-1 dipoles, so it carries ranks 0, 1 and 2,
and the rank-2 reduced element between $J = 1/2$ states vanishes because
$0 \le 2 \le 1$ is false. What survives is rank one at most, one unit of $m$.

What is left of it. The argument holds to the extent that electronic and
nuclear coordinates factorise, which the intermediate states spoil through
their own hyperfine structure. At this drive that mixing is
$1.1 \times 10^{-5}$ and $6.0 \times 10^{-6}$ in amplitude for the two
fine-structure P levels, so near $10^{-10}$ in rate, and a transverse field
adds $4 \times 10^{-4}$ per unit of $m_F$, $3 \times 10^{-14}$ in rate for
two. The satellite that would sit 700 kHz out carries of order $10^{-10}$ of
the line's area.

Those two channels behave differently in field, which is worth stating
because the obvious summary is wrong. The intermediate-state channel is a
ratio of atomic energies and carries no $B$ at all. The transverse-mixing
channel carries $B^4$ in rate, so it grows fast, and the two are equal near
400 uT, some eight times the Earth's field. Below that the leakage is flat at
$10^{-10}$. Above it the leakage grows, reaching $5 \times 10^{-9}$ at a
millitesla. The conclusion survives either way, since $5 \times 10^{-9}$ of a
line's area is still nothing, but the reason is that both channels are tiny
rather than that the suppression is field-independent, and only one of them
is.

One route that looks OPEN and is not. A magnetic-dipole leg would act on the
nuclear moment directly and so would not need the hyperfine mixing above.
Parity closes it: 5S and 6S have the same parity, a two-photon path must
therefore be even overall, and one electric-dipole leg with one
magnetic-dipole leg is odd. The parity-allowed version needs both legs
magnetic, which costs $(\alpha/2)^2$ in amplitude, and the nuclear moment
costs a further $10^{-3}$ against the electronic one, so that path lands near
$10^{-16}$ in rate, six orders below the hyperfine channel.

Ellipticity does two different things, and they differ by two orders of
magnitude. `rb5s6s/polarisation.py` carries both.

The first is the vector light shift. Elliptical light shifts each $m_F$
sublevel by an amount odd in $m_F$, spreading the line rather than moving it.
Computed from this package's own line lists, the differential vector
polarizability is 1.7 per cent of the differential scalar one at the drive
wavelength. Which scalar shift it is a fraction of has to be said, because the
record carries two numbers at the campaign's highest power and they differ by
a third. `results/stark_joint.csv` gives the calibrated prediction
`S0_225mW_pred` as 0.348 MHz and the joint three-session bound
`S0_225mW_ub95` as 0.258 MHz. A systematic should be sized against the larger,
so on the prediction the spread is 6.0 kHz at the campaign's highest power
even for fully circular light, and on the bound it is 4.5 kHz. Either way it
stands against per-condition width errors near 30 kHz. It is
proportional to power, which is the only reason to carry it: that is the one
signature it shares with the light shift being measured.

What that shift does depends on the population, and this is the part that
will matter later rather than now. Being odd in $m_F$, it cancels in the mean
over a symmetric population and only spreads the line. Elliptical light also
pumps, though, through the cascade's own decay, and a biased population does
not cancel and the line shifts. On the same predicted scalar shift that is
1.5 kHz per unit of mean projection on rubidium-87 at the campaign's highest
power and full circularity, and 1.0 kHz on rubidium-85. Against this record's centre precision near
420 kHz per trace that is invisible, which is why it has never mattered. It
stops being invisible in a fixed-lock campaign, where centres become the
strong channel and a power-proportional shift is precisely what that channel
is being asked to measure. The isotope contrast is again the discriminant,
since the per-unit shift differs by the ratio of $2F$.

The second thing ellipticity was thought to do, it does not do. A first
version of this section said that a polarisation mismatch between the forward
and retro beams opens a rank-1 coupling, makes $\Delta m_F = \pm 1$ weakly
allowed, and lets those components carry the full uncancelled
$g_F \mu_B B$ of 350 kHz. **Retracted 2026-08-20**, and the reason closes the
channel far more firmly than the bound it replaced.

Write the two-photon amplitude with its two orderings. The rank-1 weight is
the product of two factors, $(1/D_1 - 1/D_2)$ and
$\vec{e}_1 \times \vec{e}_2$, so it needs both. Photons of equal energy make
the denominators equal and kill the first whatever the polarisations are.
Parallel polarisation vectors kill the second whatever the energies are. For a
stationary atom under one laser both factors vanish, and the transition
carries ranks 0 and 2 and nothing else:

| rank | polarisation factor | $\Delta m_F$ | available? |
|---|---|---|---|
| 0 | $\vec{e}_1 \cdot \vec{e}_2$ | 0 | yes, this is the line |
| 1 | $\vec{e}_1 \times \vec{e}_2$ | $\pm 1$ | only if both factors are nonzero |
| 2 | $\lbrace \vec{e}_1 \vec{e}_2 \rbrace^{(2)}$ | $\pm 2$ | NO, zero element for $J = 1/2$ |

$\Delta m_F = 0$ is therefore the only channel available to any useful
precision, and a sigma-pi pair is closed by the same table, since its one unit
of $\Delta m$ lives in ranks 1 and 2. But neither factor is exactly zero here,
which the first version of this section claimed and
[selection rules](selection-rules.md) corrected the same day.

The Doppler-free geometry makes the energy factor nonzero for every atom that
is moving, which is the whole ensemble. In the rest frame the forward photon
is blue-shifted and the retro photon red-shifted, so the pair the signal is
built from differs by $2\nu v/c$, which is 395 MHz at 130 °C against a
75.3 THz detuning, or $5.2\times10^{-6}$ in amplitude. That is sixteen times
what an EOM sideband pair would give at 25 MHz, so the geometry, not the
modulator, is the larger of the two energy splits.

What holds the channel shut is the polarisation factor, which an ideal retro
sets to zero exactly. A mismatch of angle $\theta$ reopens rank 1 at
$\sin\theta$ times the energy factor, which is $2\times10^{-13}$ in rate at
five degrees (`rb5s6s/polarisation.py`, `rank_one_leak_rate`). The line is
protected by the retro's polarisation fidelity, not by a symmetry that holds
whatever the apparatus does.

The distinction that the RETRACTED paragraph missed, and it is the whole
lesson. The transition operator is built from two absorptions, $e_1 e_2$, and
is symmetric. The light shift operator is built from an absorption and a
stimulated emission, $e^* e$, and its antisymmetric part $e^* \times e$ does
not vanish for elliptical light. That is the vector polarizability above,
which is real and is a few kilohertz. So ellipticity shifts levels and cannot
open transition channels. Conflating the two operators is what produced the
retracted claim.

The isotopes still supply a check. Any broadening scaling as $g_F^2$, from any
mechanism, must appear 2.25 times larger on the rubidium-87 lines. The
committed widths put that difference at $+4 \pm 18$ kHz, consistent with
zero, which is what the selection rule predicts
(`scripts/run_polarisation_bound.py`). That is agreement rather than a
constraint, and it is worth having on the record as such.

Where the protection ends. The scalar selection assumes linear polarisation.
A circular admixture opens the rank-1 vector light shift, odd in $m_F$ with
its axis set by the ambient field, and the same admixture pumps orientation,
so an imperfectly polarised beam acquires a power-dependent line asymmetry
that reverses when the field reverses. The reversal is the diagnostic: a
coil on the cell turns the one magnetic effect this line can show into a
switchable signature.

The atom also supplies a reversal of its own. The hyperfine g-factor
alternates sign between the two F manifolds, so the lines of one isotope are
built-in polarity pairs for anything odd in $m_F$: a vector-shift asymmetry
must flip sign between them at fixed field and fixed power. On this record
the per-line skew carries the same sign on all four lines, which excluded
the vector mechanism from numbers already on disk, the pattern
[reversal tests](reversal-tests.md) generalises.

And the immunity, read backwards, is a sensitivity statement. A line chosen
for magnetic quietness is by the same numbers a poor magnetometer, tesla
class through its width. The one exception inverts usefully: the quadratic
term on a hyperfine pair separation is a calibrated field-squared coefficient
of pure atomic structure, so a design that reads pair separations to a few
hundred hertz measures the field inside the cell at the microtesla scale,
where no external probe can sit, with the two isotopes' different
coefficients supplying an internal consistency check.

## Two atoms lift the closure that one atom cannot

Everything above is a single-atom argument, and one of its two legs is a
statement about one atom's electronic angular momentum: a $J=1/2$ state has
two magnetic sublevels, a rank-two operator has no reduced matrix element
between two of them, and the $\sigma^+\sigma^+$ content the beam offers at
amplitude one half is therefore refused. That leg does not survive being
asked about two atoms. A pair of ground-state atoms has four sublevel
products. It can accept two units of angular momentum by taking one unit
each, and the triangle rule that closed the single-atom channel says nothing
about it. The question was put on 2026-08-19 and
[`rb5s6s/cooperative.py`](../../rb5s6s/cooperative.py) is the answer. It has
three parts and only the third is a suppression.

Energy conservation is the hard constraint and it is exact. At the
two-photon energy the pair has exactly one resonant configuration, one atom
in 6S beside one still in the ground state. Every alternative the committed
level table can build is far off: the nearest is $5S + 4D_{5/2}$ at
$777\ \mathrm{cm}^{-1}$, which is 23.3 THz, about four million line widths. No pair
channel competes for the resonance, so a cooperative process cannot make a
new line. It can only move sublevels inside the resonance that already
exists.

The topology is where the point lands, and two of them behave oppositely.
Two absorption vertices on two different atoms, joined by one dipole-dipole
transfer, reach a final state in which each atom's $m_F$ has moved by one
unit. In the exchange topology the two units are opposite, which is what the
$\pi\pi$ and $\sigma^+\sigma^-$ content of linear light offers, and the two
Zeeman shifts cancel identically whenever the two atoms share a $g_F$. In
the aligned topology they are parallel, which is exactly the
$\sigma^+\sigma^+$ content a single atom must refuse, and the two shifts add.
Linear light offers that content at amplitude $\sin^2\theta/2$, where
$\theta$ is the angle between the field that sets the quantisation axis and
the polarisation, so one half is the maximum and it needs the field
perpendicular to the polarisation. Along the polarisation the light is pure
$\pi$ and this channel is off entirely, so the rate goes as $\sin^4\theta$
and rotating the field against the polarisation is the only control that
touches it.
A matched pair then sits at $2 g_F \mu_B B$, twice the single-atom
$\Delta m_F = \pm 1$ position: 700 kHz for rubidium-87 and 467 kHz for
rubidium-85 in 50 microtesla. This is the $\Delta m_F = \pm 2$ signature, and
it is carried by a pair rather than by one atom.

Their zeros are complementary, which is worth stating because it means no
field arrangement closes the channel as a whole. The exchange topology
vanishes for a same-F pair and is 700 kHz away for the opposite-sign
rubidium-87 pair. The aligned topology does the reverse.

The size is what closes it, and by less margin than expected. The transfer
vertex costs one factor $V_{dd}/\Delta$, where $\Delta = 5025\ \mathrm{cm}^{-1}$
is how far the pair virtual state $|5P, 5P\rangle$ sits above the two-photon
energy. Integrated over the pair distribution the rate ratio goes as
$4\pi n K^2 / 3R_c^3$ and is dominated by the closest pairs, so the cutoff
carries it and the cutoff is stated rather than implied. At the Weisskopf
radius of the same van der Waals difference the record already uses for
$\beta_{\rm self}$, inside which a collision is strong and fully dephasing
and therefore already MEASURED rather than new, the ratio is
$1.3\times10^{-9}$ at 130 °C, falling to $2.3\times10^{-11}$ at 70 °C
because it is linear in density.

That is about eight times the single-atom hyperfine-mixing route, which
`rb5s6s/polarisation.py` now computes rather than asserting: squaring the
admixture on each fine-structure leg and summing gives $1.5\times10^{-10}$,
of which the long-quoted $1.2\times10^{-10}$ is the dominant leg alone. The pair
route does not sit far below the single-atom one the way a higher-order
process usually would, it dominates the forbidden-channel budget, and it is
the only one of the two that puts any amplitude at the
$\Delta m_F = \pm 2$ position at all, since the single-atom rank-two channel
is closed outright at every order.

How far below visibility, with the floor named rather than asserted: the
tightest bound this record carries on an out-of-window feature is
`f_wing_red_mean` at 130 °C in `results/wing_check.csv`, 0.0009 of peak, so
roughly 0.0018 at 95 per cent. The pair channel sits six orders below that and
the single-atom route seven. Earlier drafts of this section said nine and ten,
neither sourced and both too generous.

The factor of ten replaces an earlier number on this page. The first
version of this section summed only the $5P_{1/2}$
intermediate leg and reported $1.5\times10^{-10}$, which made the two routes
look equal. An adversarial reading on 2026-08-20 asked why the other
fine-structure leg was absent. $5P_{3/2}$ is E1 allowed at every vertex, its
reduced matrix elements are the larger pair, and its energy denominators are
not much worse, so carrying all four leg combinations multiplies the
amplitude by 2.82 and the rate by 7.97.

### What the two atoms actually do, vertex by vertex

The word cooperative hides the mechanism, so here it is in full. Label the
two atoms A and B, both starting in the ground state.

1. Atom A absorbs one photon and is left in a virtual state near $5P$,
   off shell by 2513 reciprocal centimetres. If that photon was
   $\sigma^+$ it carried one unit, so A is momentarily at $m+1$.
2. Atom B absorbs the other photon, independently, and is left off shell
   in the same way at $m'+1$.
3. The pair is now in $|5P, 5P\rangle$ carrying the full two-photon energy
   but in the wrong configuration, 5025 reciprocal centimetres above where
   that energy belongs. Nothing can stay there.
4. The dipole-dipole interaction between the two atoms fixes that in one
   step. It takes $|5P, 5P\rangle$ to $|6S, 5S\rangle$: atom A goes up to
   6S and keeps all the energy, atom B falls back to the ground state and
   keeps none of it. Both keep the unit of angular momentum they took.

The final state is one atom in 6S at $m+1$ and one atom still in the ground
state at $m'+1$. Atom B has been left behind in a different sublevel without
absorbing any net energy, which is the whole trick. It is why the pair can
accept two units when neither atom alone can accept more than one.

Both $\Delta m_F$ values come from this one process, read two ways. **Per
atom it is $\pm 1$**, which is all a $J=1/2$ atom can take. **Per pair it is
$\pm 2$**, which is what the light delivered. The line the spectrometer sees
is set by the pair, because the pair is what absorbed the light, and that is
why the satellite sits at the two-unit position.

### The same process against the three knobs

The three knobs an experiment has do completely different things to this
channel, and only one of them touches its size.

**Laser power does nothing to it.** The pair channel absorbs the same two
photons the ordinary line absorbs, so both rates go as intensity squared and
the ratio between them is flat in power. Turning the laser up multiplies the
satellite and the line by the same factor and changes nothing about their
contrast. This is the most useful single fact about the channel, because it
says the obvious experiment does not work. The only power-tunable member of
the family is the FOUR-photon version, which goes as intensity to the fourth,
so its ratio to the line goes as intensity squared and doubling the power
quadruples it, from a base at most as large as the number below.

**Temperature is the only lever on the size**, and it is a strong one,
because the channel needs a second atom and temperature is what supplies
them. The rate fraction is linear in density:

| temperature | density | pair channel, as a fraction of the line |
|---|---|---|
| 70 °C | $5.6 \times 10^{11}\ \mathrm{cm}^{-3}$ | $2.3\times10^{-11}$ |
| 100 °C | $4.8 \times 10^{12}\ \mathrm{cm}^{-3}$ | $2.0\times10^{-10}$ |
| 130 °C | $2.9 \times 10^{13}\ \mathrm{cm}^{-3}$ | $1.3\times10^{-9}$ |

Fifty-five times across the campaign's own range, of which the density
supplies 52.5 and the rest comes from the Weisskopf cutoff shrinking slightly
as collisions get faster. **This is also the channel's fingerprint.** The
single-atom hyperfine-mixing route is density-INDEPENDENT, so the density
lever separates the two cleanly, and the record already sweeps density by a
factor of 53 for another reason entirely.

**The magnetic field moves the satellite and leaves the rate alone.** The
field never appears in the rate, only in the position, at
$2 g_F \mu_B B$ for a matched pair, which is 14.0 kHz per microtesla for
rubidium-87 and 9.3 for rubidium-85. Below the field at which that offset
reaches the line width, the satellite is not a feature at all but a
contribution to the second moment, growing as $B^2$ while the channel itself
does not change:

| field | satellite offset | added to the measured width |
|---|---|---|
| 5 µT | 70 kHz | $3\times10^{-6}$ Hz |
| 50 µT | 700 kHz | $3\times10^{-4}$ Hz |
| 200 µT | 2.80 MHz | $5\times10^{-3}$ Hz |
| 500 µT | 7.00 MHz | $3\times10^{-2}$ Hz |

**Above 384 microtesla the offset exceeds the 5.37 MHz line width**, and the
search changes character completely: no longer a width excess of order
$10^{-4}$ hertz, which nothing can measure, but a RESOLVED feature at a
position atomic structure fixes in advance. That is the only version of this
measurement that is not hopeless, and it is still six orders below the
tightest bound this record carries. The numbers in both tables are in
`results/cooperative_channel.csv` under the `knob` block.

### Is it in the 2025 data, and could a density sweep find it?

**No, and the second half of that answer is the more interesting one.**

The record already sweeps density by a factor 53, which is exactly the lever
this channel responds to, so the question is fair. Two things close it.

**The size.** At Earth's field and 130 °C the satellite adds
$3\times10^{-4}$ hertz to the measured width. The collisional width the
record actually measures at that density is 492 kHz. The pair channel is
$6\times10^{-10}$ of it.

**And the degeneracy, which matters more than the size.** The pair channel's
width contribution is linear in density, and so is $\beta_{\rm self}$. They
have the same signature in the one lever that reaches the channel, so a
density sweep cannot separate them even in principle. Whatever the pair
channel contributes is silently absorbed into the collisional coefficient,
at six parts in ten thousand million of it.

**What the density lever does separate** is the pair route from the
single-atom hyperfine route, because that one is density-INDEPENDENT. That
is a real discriminant between the two forbidden channels and it is worth
having written down, but neither channel is visible, so it is a discriminant
with nothing to discriminate.

**The only lever that separates the pair channel from collisions is the
field.** $\beta_{\rm self}$ does not care about it. The satellite's width
contribution goes as $B^2$, and above 384 microtesla the satellite leaves the
line entirely. A field sweep at fixed density is therefore the only design
that could ever isolate this term, which is a statement about what would be
needed rather than a proposal, since the term is six orders below the
tightest bound this record carries.

Four photons on one atom have NO line to shift. Four photon energies come to
$40265\ \mathrm{cm}^{-1}$, which is $6574\ \mathrm{cm}^{-1}$ above the $33691\ \mathrm{cm}^{-1}$ ionisation
limit, so a single atom taking four photons is photoionised rather than
excited. The question has no single-atom answer, only a pair one. In passing
this is also why the 6S population is safe from the drive itself: one further
photon from 6S reaches $30199\ \mathrm{cm}^{-1}$, still $3492\ \mathrm{cm}^{-1}$ below the limit,
so it takes two.

Four photons on two atoms add nothing further. Both atoms reaching 6S is
exactly resonant, since four photon energies are two 6S energies. Its uncorrelated
part is two independent single-atom events at the unshifted frequency, its
correlated part carries the same dipole-dipole factor times the square of an
already small excitation probability, and its resonance condition per photon
is unchanged.

## What can go wrong

The first failure is a model one: reading a population-averaged
measurement as if it described one sublevel, or the opposite mistake,
concluding a sublevel-dependent effect is absent because an unresolved
measurement washed it out. Averaging over $2F+1$ equally weighted
sublevels is a description of what the measurement did, not evidence about
what any one sublevel would show.

The second is an apparatus limitation dressed as a result. Without an
applied field of known, stable direction, $m_F$ is not a meaningful label
at all, an ambient stray field of unspecified and drifting orientation does
not define a quantisation axis, it only adds a small, uncontrolled scatter
on top of the degeneracy-weighted average that was already there. Calling
that scatter a measured vector or tensor shift claims more than an
unprepared sample supports.

The third is an implementation trap: writing the Lande g-factor formula
with the fine-structure quantum number $J$ where the hyperfine one $F$
belongs, or the reverse. The two formulas share the same shape and differ
only in which angular momenta enter, so the wrong one returns a plausible
number for the wrong level and raises no error on its own, the same class
of slip [hyperfine structure](hyperfine-structure.md) flags for the
interval-formula multiplier.

The fourth is an experimental limitation, not a fixable oversight. State
preparation only converts the vector or tensor channel into a measurable
quantity if the level carries that rank to begin with. For a pair of
$J=1/2$ levels the tensor channel is not merely small or hard to resolve,
it does not exist, so no trap, no field and no state preparation manufacture
one. That is why this record's own magic-wavelength search stays scalar by
right rather than by an unexamined omission.

## Try it

The $2F+1$ degeneracies and the linear Zeeman splitting per unit field for
the two ground hyperfine levels of one isotope, with the $F$ values read
from this repository's own `PEAKS` table rather than typed from memory.

```python
from rb5s6s.constants import PEAKS, H_PLANCK_JS

# Bohr magneton, CODATA 2018 (a universal constant, not a repository number).
MU_B_J_PER_T = 9.274_010_078_3e-24

# Lande g_J of an L=0 (S-state) level is, to leading order, the free-electron
# spin g-factor: a J=1/2 alkali ground state measures within 0.01% of it, and
# the (much smaller) nuclear contribution is dropped here.
G_J_S_STATE = 2.002_319_304_4


def ground_state_f_values(isotope):
    """The two ground F values this repository's own hyperfine components
    name (PEAKS), read rather than typed from memory."""
    return sorted({p["F"] for p in PEAKS.values() if p["isotope"] == isotope})


def lande_g_f(F, I, J=0.5):
    """Fine-structure-only Lande g_F for a hyperfine level F built from J and I."""
    return G_J_S_STATE * (F * (F + 1) + J * (J + 1) - I * (I + 1)) / (2 * F * (F + 1))


isotope = 87
f_lo, f_hi = ground_state_f_values(isotope)
nuclear_spin_i = f_hi - 0.5  # F_max = I + J, J = 1/2 for an S1/2 level

print(f"{isotope}Rb 5S1/2 ground state, I = {nuclear_spin_i:.1f}, "
      f"from the F values PEAKS already names:")
for F in (f_lo, f_hi):
    degeneracy = int(2 * F + 1)
    g_f = lande_g_f(F, nuclear_spin_i)
    hz_per_tesla = g_f * MU_B_J_PER_T / H_PLANCK_JS
    mhz_per_gauss = hz_per_tesla * 1e-4 / 1e6
    print(f"  F={F}: {degeneracy} sublevels (m_F = {-F:g}..{F:g}), "
          f"g_F = {g_f:+.3f}, Zeeman splitting {mhz_per_gauss:+.4f} MHz/G per unit m_F")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [`../lit/steck_rb.md`](../lit/steck_rb.md), the standard compilation of Rb
  atomic-structure constants against which this repository's own numbers are
  checked, and the usual source for the Lande g-factor and Zeeman-splitting
  formulas used above.
- C. Cohen-Tannoudji, J. Dupont-Roc and G. Grynberg, *Atom-Photon
  Interactions: Basic Processes and Applications* (Wiley, 1998), the standard
  graduate treatment of the scalar, vector and tensor light-shift operators
  for a degenerate atomic level.
- [Duspayev and Raithel](../lit/duspayev2023.md), a trapped, cold-atom
  measurement whose tensor polarizability visibly splits a magic-wavelength
  condition by $m_J$, the kind of result a $J=1/2$ pair in a warm cell
  cannot produce.
- [Hyperfine structure](hyperfine-structure.md), for the $F$ levels a field
  splits further.
- [The AC-Stark shift](ac-stark-shift.md), for the scalar shift a warm cell
  actually measures and the beam geometry that turns it into a lineshape.

## See also

- [Hyperfine structure](hyperfine-structure.md), the $F$ levels this
  page's sublevels sit inside.
- [Hyperfine populations and branching](hyperfine-populations-and-branching.md),
  for how atoms distribute among the sublevels this page describes.
- [Selection rules](selection-rules.md), for the angular-momentum rule
  that fixes which $J$ combines with nuclear spin to build each $F$.

---

[← Hyperfine structure](hyperfine-structure.md) · *Atomic structure and selection rules, 4 of 7* · [Hyperfine populations and branching →](hyperfine-populations-and-branching.md)
