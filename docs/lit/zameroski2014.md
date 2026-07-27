---
citekey: zameroski2014
type: article
authors:
  - Zameroski, Nathan D.
  - Hager, Gordon D.
  - Erickson, Christopher J.
  - Burke, John H.
title: 'Pressure broadening and frequency shift of the $5S_{1/2}\to5D_{5/2}$ and $5S_{1/2}\to7S_{1/2}$ two-photon transitions in $^{85}$Rb by the noble gases and {N$_2$}'
journal: 'J. Phys. B: At. Mol. Opt. Phys.'
volume: 47
number: 22
pages: 225205
year: 2014
doi: 10.1088/0953-4075/47/22/225205
arxiv: null
pdf: PDF_papers/Zameroski_2014_Rb-5S-5D-7S-pressure-broadening-and-shift.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: null
summary: >
  Measures the Rb 5S->7S self-BROADENING rate, 129 +- 11 kHz/mTorr = 5.39 kHz
  per 1e12 cm^-3 -- the only measured self-broadening rate for an nS state in
  Rb, and the anchor for this programme's expected beta_self(6S) = 3.5 kHz per
  1e12 cm^-3. Its 7S self-SHIFT could not be extracted; the -17.8 kHz/mTorr
  often attributed here is Morzynski 2013's, on the laser axis.
loci:
  - M4
  - P1
section: collision-series
---

# zameroski2014

**Re-read from the held PDF 2026-07-27, and the earlier reading was wrong in
its central number.** This entry used to build the expected beta_self from a
self-SHIFT of -17.82 kHz/mTorr attributed to Zameroski. That figure is not his.
Section 2.5 states plainly that for 7S "the self-shift rate could not be
extracted from the experimental data"; the -17.82 kHz/mTorr is Morzynski 2013's,
quoted on the LASER axis, which Zameroski restates on the transition axis as
-35.6 +- 1.6 kHz/mTorr. The old chain then converted that shift into a
broadening through a Lindholm-Foley ratio -- a conversion that was never needed,
because the paper measures the broadening directly.

**What it actually measures, and why it is the anchor.** Section 2.5, verbatim:
"The self-broadening rate gamma_B = 129 +- 11 kHz mTorr^-1", for the
85Rb 5S(F=2) -> 7S(F=2) two-photon line -- the sister transition to this
programme's, one principal quantum number up. Self-broadening is exactly what
beta_self is, so no conversion of any kind is required. At their cell
temperature (~403 K; 1 mTorr <-> 2.40e13 cm^-3) that is
**beta_self(7S) = 5.39 +- 0.46 kHz per 1e12 cm^-3**.

This is the **only measured self-broadening rate for an nS state in rubidium**,
and so the only external check M18 has.

**It failed that check by 1.7x, and the failure is informative.** Run on 7S,
M18's absolute prediction is 8.99 kHz per 1e12 cm^-3 against the measured 5.39.
The discrepancy is far outside the +-10-15% the valence-only truncation can
explain, and it lands on the weakness the module had already named: the
Lindholm-Foley prefactor is quoted from the pressure-broadening literature
rather than derived, and its convention is where a factor of that size lives.

That error is common to 6S and 7S -- same prefactor, same law, same units -- so
it cancels in a ratio. `vanderwaals.beta_self_anchored` therefore uses M18 only
for C6(6S)/C6(7S) = 0.347, a ratio of two sums over the same matrix elements,
and takes the absolute scale from this measurement:

    beta_self(6S) = 5.39 * 0.347^(2/5) = **3.53 +- 0.30 kHz per 1e12 cm^-3**

**Consequences.** The archival bound sits **57-113x above** this, rather than
the ~40-100x the old misattributed chain gave, or the 34-68x M18's uncorrected
absolute value gave. The conclusion is unchanged in kind -- the bound is far
above any expected value -- and is now anchored on a measurement of the same
observable on the neighbouring state.

The old entry's forward-looking point stands and is worth keeping: the 70-130 C
lever cannot MEASURE a beta of this size (Delta-N ~ 2e13 cm^-3 gives
Delta-gamma ~ 70 kHz at 3.5 kHz per 1e12, still under the width budget); a real
measurement needs 150-170 C points.

Also measured here, and not used by this programme: broadening and shift rates
of 5S->5D (778 nm) and 5S->7S (760 nm) by the noble gases and N2, reported for
the first time.
