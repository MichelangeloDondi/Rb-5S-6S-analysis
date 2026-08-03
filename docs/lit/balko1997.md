---
citekey: balko1997
type: article
authors:
  - Balko, B.
  - Kay, I. W.
  - Vuduc, R.
  - Neuberger, J. W.
title: 'Recovery of superfluorescence in inhomogeneously broadened systems through rapid relaxation'
journal: Phys. Rev. B
volume: 55
number: 18
pages: 12079-12085
year: 1997
doi: 10.1103/PhysRevB.55.12079
arxiv: null
pdf: PDF_papers/Balko_1997_superfluorescence-inhomogeneous-broadening-rapid-relaxation.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'DOI, volume, issue and page range confirmed against the APS record
    (link.aps.org/doi/10.1103/PhysRevB.55.12079) via a search snippet, not by
    loading the APS page directly (it returned 403). The PDF itself carries
    the same volume/issue/page header on every page, so the record and the
    held file agree independently of the APS fetch.'
verified_date: 2026-08-03
summary: >
  Nuclear superfluorescence (Institute for Defense Analyses / Cornell / North
  Texas), read for its perturbation-parameter-as-random-variable formalism.
  Section III writes a hyperfine perturbation alpha = delta_0 - delta_1 as a
  random variable with a probability density gamma, worked for Gaussian and
  Lorentzian gamma, and integrates gamma against an elementary time-domain
  response G(Omega,alpha,t) to build the inhomogeneously broadened emission.
  Structurally the same lineshape-as-a-probability-map logic as delone1980,
  independently arrived at in a third, unrelated field (nuclear Mossbauer
  physics), fourteen years later. No geometric distribution and no power-law
  family: both worked examples are the two textbook closed forms, not members
  of the |s|^(n-1) family this programme's triangular law belongs to.
loci:
  - THEORY
section: prior-art
---

# balko1997

**Read in full 2026-08-03.** Balko, Kay (Institute for Defense Analyses,
Alexandria VA), Vuduc (Cornell), Neuberger (University of North Texas). Phys.
Rev. B 55 (18), 12079-12085, received 22 February 1996, published 1 May
1997. Funded by the Ballistic Missile Defense Organization. This is the
"superfluorescence in inhomogeneously broadened systems, perturbation
parameter as a random variable" paper, precisely: Kielkopf is not an author
of this piece, the four names above are the complete author list on the PDF.

## What the paper is

Superfluorescence (SF) is the cooperative, directional, N-squared-intensity
emission pulse from an inverted ensemble of dipoles that manage to correlate
their phases before spontaneous decay destroys the correlation. Inhomogeneous
broadening, meaning each radiator sits at a slightly different transition
frequency, dephases that correlation and can suppress SF outright. The
authors' target system is nuclear, not atomic: a gamma-ray laser candidate,
where the individual radiators are nuclei whose transition energies are
shifted by isomer shifts, quadrupole interactions, magnetic hyperfine
interactions, dipole-dipole interactions and gravitational shifts (their
footnote 6). Their claim is that a fast enough relaxation of the perturbing
field, physically a hyperfine interaction of the nucleus with its electrons
that flips on a timescale short compared with the SF delay, can "collapse the
spectrum to an average value that approaches the unbroadened limit" and so
recover SF that inhomogeneous broadening alone would destroy.

## The formalism, verbatim and by equation

Section III.A sets up the perturbed Hamiltonian for a single resonator,

> "H(t) = H0 + delta_i f(t)," (Eq. 8)

with f(t) a random function of time and delta_i the perturbation energy of
level i. Following Blume, the emission probability is the real part of a
Fourier-Laplace transform of the dipole correlation function (Eq. 9), and the
correlation function factors into a fixed part and a stochastic average

> "<e^(i*alpha*Integral_0^t f(t')dt')>_av = (cos(x*Omega*t) + (1/x)sin(x*Omega*t))e^(-Omega*t)
> = G(Omega, alpha, t)," (Eq. 11, with x = [alpha^2/Omega^2 - 1]^(1/2))

where alpha = delta_0 - delta_1 is the perturbation-energy difference between
the two levels and Omega is the rate at which the field f(t) jumps between
+1 and -1 with equal probability. This is the elementary, per-value response:
for one fixed alpha, G(Omega,alpha,t) is the full time-domain lineshape
kernel, interpolating between a pure oscillation at frequency alpha (Omega
much less than alpha, "the maximum inhomogeneous broadening effect") and a
featureless decay (Omega much greater than alpha, "the inhomogeneous
broadening effect disappears").

Section III.A then takes the step the routing here cares about:

> "To apply Eq. (11) to inhomogeneous broadening, we further assume that
> alpha is a random variable with a probability density gamma. In this paper,
> we consider both Gaussian and Lorentzian distributions as examples."

For the Gaussian case, gamma(alpha,sigma) = (1/(sigma*sqrt(2*pi))) *
exp(-alpha^2/(2*sigma^2)), and the observed, inhomogeneously broadened
response is the density integrated against the elementary kernel,

> "Ḡ(Omega,sigma,t) = Integral_{-inf}^{inf} gamma(alpha,sigma) G(Omega,alpha,t) d alpha," (Eq. 13)

which is then fed back into Eq. (9) to get the actual line shape. Footnote 13
gives the Lorentzian case explicitly, gamma(alpha,a) = (a*Gamma/2*pi) /
[alpha^2 + (a*Gamma/2)^2], with a the "inhomogeneous broadening parameter"
normalising the width to the natural linewidth Gamma. Footnote 11 is the
paper's own statement of scope: "The assumption of a Lorentzian line shape is
a mathematical convenience and provides us with an exponential time
dependence. ... Other line shapes may be more appropriate in specific cases.
In this paper, we compare the effects of Lorentzian and Gaussian
distributions." Section III.B repeats the identical construction for the SF
intensity itself (Eqs. 14-16), and Section III.C feeds the resulting
time-dependent coupling g'(t) = Ḟ(Omega,sigma,t) into the Maxwell-Bloch
pulse-shape equations of the group's earlier paper (the Appendix here), so
the same density-to-response mapping is used twice: once for a cw line shape,
once for a transient pulse shape.

## LINEAGE BRIDGES

**The general shape of the construction matches this programme's exactly.**
Strip the nuclear-physics content away and Eq. (13) reads: observed response
equals the integral of [a probability density over a perturbation parameter]
against [an elementary, per-value response function]. That is the same
skeleton as this repository's f(s)-to-lineshape construction, where s is the
local AC-Stark shift set by the beam's intensity profile, f(s) is its
probability density, and the elementary response is a Lorentzian centred on
the shifted frequency. Both constructions convert a *distribution over a
perturbation* into an *observed lineshape* by the same kind of integral, and
both do it for the explicit reason that a single resonator's response is
known exactly (Eq. 11 here, a shifted Lorentzian there) while the ensemble
carries a spread of perturbation values that must be averaged over.

**Two structural differences, both real.** First, alpha here is a stochastic
quantity: it labels a *nucleus* whose local hyperfine environment is drawn
from a static distribution across the ensemble, and the elementary response
G(Omega,alpha,t) additionally carries a second, independent parameter Omega,
the rate at which the field driving that nucleus itself flips sign in time.
Nothing in this programme's construction has an analogue of Omega: the beam
intensity distribution sampled by the ensemble is fixed in space, not a
telegraph process with a jump rate, so there is no "motional narrowing" knob
comparable to the Omega much-greater-than-alpha limit here. Second, and this
is where the paper actually gets read for a verdict rather than a resemblance:

**Do the Gaussian and Lorentzian examples anticipate the power-law family the
triangular law belongs to? No.** The paper is explicit that Gaussian and
Lorentzian are chosen as the two standard textbook closed forms for
"comparison," not derived from any argument about the physical origin of the
perturbation. Their stated sources of inhomogeneous broadening (footnote 6:
isomer shifts, quadrupole interactions, magnetic hyperfine and dipole-dipole
interactions, gravitational shifts) are never connected to a specific
functional form for gamma beyond "Gaussian" and "Lorentzian," and footnote 11
explicitly leaves the door open ("other line shapes may be more
appropriate") without walking through it. There is no |s|^(n-1) power-law
family here, no geometric argument tying gamma to the shape of a beam profile
or any other spatial distribution, and no third closed form at all. The
verdict is the same one already reached for delone1980: the general
lineshape-as-a-probability-density-map logic recurs independently, this time
in nuclear Mossbauer and superfluorescence physics rather than multiphoton
atomic ionization, seventeen years after delone1980 and unconnected to it (no
shared citation, no shared author, no shared community). What does not recur
anywhere read so far is the geometric, closed-form power-law family itself:
both prior appearances stop at the two standard textbook distributions and
explicitly decline to generalize further.

**Net effect on the novelty claim.** This paper widens, rather than narrows,
the set of fields in which the bare "convolve a response against a
perturbation density" idea already existed before this programme, and it
does so with a second concrete pair of worked closed forms (Gaussian,
Lorentzian) that again fail to anticipate the specific power-law family this
programme derives from beam geometry. What remains distinctive, on the
evidence of both delone1980 and this paper, is unchanged: the geometric
origin of the density itself, the closed-form power-law family it produces,
and the analytic cumulants built on top of it.
