---
citekey: leonard2017
type: article
authors:
  - Leonard, R. H.
  - Fallon, A. J.
  - Sackett, C. A.
  - Safronova, M. S.
title: 'Erratum: High-precision measurements of the 87Rb D-line tune-out wavelength [Phys. Rev. A 92, 052501 (2015)]'
journal: Phys. Rev. A
volume: 95
pages: 059901
year: 2017
doi: 10.1103/PhysRevA.95.059901
arxiv: null
pdf: PDF_papers/Leonard_2017_ERRATUM_Rb87-D-line-tune-out-wavelength.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'This erratum replaces leonard2015 on the tune-out and on the
    matrix-element ratio. Cite this for both. It is not on arXiv -- the 2015
    arXiv record (1507.07898) is pre-erratum through v3 -- which is why the repo
    carried the erratum values as merely REPORTED until the PDF was obtained.'
verified_date: 2026-07-31
summary: >
  One-page erratum to leonard2015, held and read. Corrects an error
  in the Zeeman treatment: the ground-state Zeeman shift was omitted from
  omega-prime when correcting the F=2, m=2 data taken in a 20.0 G bias field.
  The tune-out becomes 790.032326(32) nm, "an adjustment of about 2 sigma"
  from the published 790.032388(32); the matrix-element ratio
  R = |d_3/2|^2/|d_1/2|^2 becomes 1.99217(3); and the theoretical value becomes
  790.0315(7) nm, improving agreement. It also retires an apparent conflict in
  the literature: the disagreement with Lamporesi et al.'s 790.018(2) nm is not
  a discrepancy but a different ground state (F=1), and carried to F=1 this
  measurement gives 790.017496(32) against a 790.0167(7) theory. This is the
  source of the 5S tune-out validation anchor used by rb5s6s/polarizability.py.
loci:
  - M16
section: method-anchors
---

# leonard2017

**Held and read**, closing a flag that had stood since the tune-out
anchor was first checked: the erratum's numbers were carried as REPORTED while
the document itself was unavailable.

## What it corrects, in its own words

> "The most important error was in the correction of our experimental data for
> the Zeeman effect."

The measurements were made in a magnetic trap at $B = 20.0$ G, in $F=2, m=2$.
The Zeeman adjustment was subtracted using a formula that omitted the
**ground-state** shift from $\omega'$. Correcting it:

> "Because of this mistake the reported value for $\lambda^{(0)}$ is incorrect.
> The correct value is $\lambda^{(0)} = 790.032326(32)$ nm, an adjustment of
> about $2\sigma$."

Three consequences, all of which this repository now uses:

| quantity | 2015 | corrected |
|---|---|---|
| tune-out $\lambda^{(0)}$ (F=2) | 790.032388(32) nm | **790.032326(32) nm** |
| ratio $R = \lvert d_{3/2}\rvert^2/\lvert d_{1/2}\rvert^2$ | 1.99221(3) | **1.99217(3)** |
| theory | 790.0312(7) nm | **790.0315(7) nm** |

The theory correction is separate from the Zeeman one: the original polarization
averaging averaged $\lambda_0$ over two orthogonal linear polarizations, which is
"valid only if the derivative $d\alpha/d\lambda$ is independent of the
polarization angle, which is not the case here due to the tensor contribution".

## The Lamporesi resolution, which is worth carrying separately

The 2015 paper noted "considerable disagreement" with Lamporesi *et al.*'s
790.018(2) nm and did not explain it. The erratum does: Lamporesi measured in
the **$F=1$** ground state. Leonard's own measurement carried to $F=1$ gives
790.017496(32) nm against a theoretical 790.0167(7), and the two then agree. So
there is **no outstanding experimental conflict** on the Rb tune-out — useful,
because an unexplained disagreement between two precision measurements would
otherwise weaken the anchor that [polarizability.py](../../rb5s6s/polarizability.py)
is validated against.

## Effect on this repository

None on any conclusion. The model computes 790.0339 nm, which sits 1.57 pm from
the corrected value against a 0.062 pm gap between the two published numbers —
the correction is twenty-five times smaller than the residual it is compared to.
What changed is provenance: the anchor quoted in
`rb5s6s/polarizability.py`, `docs/THEORY_NOTE.md`, `scripts/run_polarizability.py`
and the results ledger is now the **erratum** value, read from the document,
rather than the 2015 value with a footnote about an unread correction.

## Values

The load-bearing numbers of this source, each at its stated
location, so a prose quote anywhere in this repository can
reference a row here and be checked against it.

| field | value | where in the paper |
|---|---|---|
| tuneout_nm | 790.032326(32) | the corrected 5S tune-out wavelength, the erratum's value and the anchor of this record's polarizability sign |
