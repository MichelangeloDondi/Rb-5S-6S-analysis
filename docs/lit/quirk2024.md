---
citekey: quirk2024
type: article
authors:
  - Quirk, J. A.
  - Jacobsen, A.
  - Damitz, A.
  - Tanner, C. E.
  - Elliott, D. S.
title: 'Measurement of the static Stark shift of the 7s 2S1/2 level in atomic cesium'
journal: Phys. Rev. Lett.
volume: 132
pages: 233201
year: 2024
doi: 10.1103/PhysRevLett.132.233201
arxiv: '2311.09169'
pdf: PDF_papers/Quirk_2024_Cs-6s-7s-dc-Stark-shift-vector-polarizability.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Held as the arXiv version (2311.09169, dated 22 January 2024). The journal
    fields are the published PRL reference reported by a secondary source and
    should be confirmed against the published article before formal citation;
    the arXiv record carries no journal-ref.'
verified_date: 2026-07-30
summary: >
  A 0.04%-precision measurement of the dc Stark shift of the Cs 6s 2S1/2 ->
  7s 2S1/2 transition: k = 0.72246(29) Hz/(V/cm)^2, giving alpha_7s =
  6207.9(2.4) a0^3 against alpha_6s = 401.1(5) a0^3, i.e. a differential static
  polarizability of 5807 a0^3. It also revises the reduced matrix elements
  <7s||r||7p_j> and the vector transition polarizability to beta-tilde =
  27.043(36) a0^3, resolving a discrepancy between two techniques. The value
  here is a VALIDATION TARGET: the same nS -> (n+1)S differential this
  programme computes for Rb 5S-6S, measured in Cs to four significant figures.
loci:
  - M16
  - THEORY
section: prior-art
---

# quirk2024

Held. Verified against the arXiv preprint (2311.09169). The published journal reference has not been independently confirmed.

## The numbers

The differential Stark shift slope is k = 0.72246(29) Hz/(V/cm)², a relative uncertainty of 0.04%, about 0.5% smaller than the previous measurement (Bennett et al., 0.7262(8)) with an uncertainty more than twice smaller. Using a weighted average of ground-state measurements, α₆ₛ = 401.1(5) a₀³ = 0.09980(11) Hz/(V/cm)², Table II gives α₇ₛ = 6207.9(2.4) a₀³. So the differential is

    Δα_static(Cs 6s → 7s) = 6207.9 − 401.1 = 5806.8 ≈ 5807 a₀³.

## Units

k carries the ½ of ΔE = −½αE² while the paper's α↔Hz/(V/cm)² mapping does not. Dividing k by the α₆ₛ ratio gives 2903.6 a₀³, exactly half the right answer. Table II's α₇ₛ must be used, not a ratio of the two quoted units.

## Validity

This is a dc Stark measurement. It says nothing directly about the ac polarizability at 993 nm, where the Rb sign dispute lives and where the answer is a cancellation between an upward and a downward group.

## Use in this record

This project's static differential polarizability for Rb 5S → 6S is α₆S − α₅S = 5167.0 − 318.3 = 4848.7 a.u. Quirk's 5807 a₀³ is the same structural quantity, an alkali nS → (n+1)S differential static polarizability, measured in the neighbouring element to 0.04%. The two agree to about 20%, as two different alkalis should. Quirk derive α₇ₛ from a sum over |⟨7s‖r‖np_j⟩|² weighted by 1/(E_np − E_7s) (their Eq. 4), the same construction `rb5s6s/polarizability.py` uses.
