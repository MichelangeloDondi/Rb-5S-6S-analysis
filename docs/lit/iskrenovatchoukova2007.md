---
citekey: iskrenovatchoukova2007
type: article
authors:
  - Iskrenova-Tchoukova, E.
  - Safronova, M. S.
  - Safronova, U. I.
title: 'High-precision study of Cs polarizabilities'
journal: J. Comput. Methods Sci. Eng.
volume: null
pages: null
year: 2007
doi: null
arxiv: '0705.4425'
pdf: PDF_papers/IskrenovaTchoukova_2007_Cs-polarizabilities-all-order.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Held as arXiv v1 (0705.4425, 30 May 2007). No journal-ref is carried by the
    arXiv record and none was found; the journal field above is UNCONFIRMED and
    must be established before formal citation. Cite the arXiv identifier until
    then.'
  - 'All polarizabilities in the paper''s tables are in units of 10^3 a0^3. The
    values quoted in this note have been multiplied out to a0^3 to match the
    convention of quirk2024 and rb5s6s/polarizability.py. Check the exponent
    before reusing any number from the PDF directly.'
verified_date: 2026-07-30
summary: >
  First-principles relativistic all-order (linearized coupled-cluster
  single-double) static dipole polarizabilities for Cs Ns (N=6-12), Npj (N=6-10)
  and Ndj (N=5-10), with evaluated uncertainties and a comparison table against
  every available experiment. The numbers this programme needs are
  alpha(6s) = 398.4(7), alpha(7s) = 6238(41) and alpha(8s) = 38270(280) a0^3.
  The 7s value agrees with quirk2024's MEASURED 6207.9(2.4) within the theory
  bar (0.7 sigma), a validation target for the repository's sum-over-states
  machinery. NOTE the complication in the body: their own Expt. column carries
  6238(6) from the older Bennett Stark-shift lineage, which quirk2024 supersedes
  and disagrees with at about 4.6 sigma, so the target is a ~0.5% BAND, not a
  four-figure number. Also carries the 8s-6pj matrix elements that
  sieradzan2004 measured and the alpha(8s) that sets the scale of lee2010's
  measured 6S-8S light shift.
loci:
  - M16
  - THEORY
section: method-anchors
---

# iskrenovatchoukova2007

**Read 2026-07-30** from the held arXiv v1 (0705.4425), Tables I and VIII.
Delaware / Nevada — the same Safronova lineage as
[safronova2004](safronova2004.md), which is this repository's Rb anchor. This is
its Cs counterpart.

## The method, in one paragraph

Relativistic all-order **linearized coupled-cluster single–double (SD)**, with
single and double excitations of the Dirac–Fock wavefunction summed to all
orders, partial triples in the harder cases, and a $N_B = 70$ B-spline basis per
partial wave up to $l_{\max} = 6$ (the paper notes that $N_B = 50$ is *not*
sufficient for the highly excited states). Uncertainties are assigned by the
difference between *ab initio* and scaled matrix elements, so — their words — the
procedure "allows to place an uncertainty on our theoretical data that is not
derived from the comparison with the experiment". That is a claim about the
*uncertainty*. This note originally over-read it into a claim that the whole
Table VIII comparison is independent; it is not, since several input matrix
elements are experimental values substituted for theoretical ones. The comparison
is **partly** independent — see the complication below.

## The numbers, converted out of the paper's $10^3 a_0^3$ units

Scalar static polarizabilities of the Cs $Ns$ sequence (their Table VIII):

| state | this work ($a_0^3$) | experiment ($a_0^3$) |
|---|---|---|
| 6s | 398.4 ± 0.7 | 401.0 ± 0.4 |
| 7s | 6238 ± 41 | 6238 ± 6 |
| 8s | 38270 ± 280 | 38060 ± 250 |
| 9s | 153700 ± 1000 | — |
| 10s | 478000 ± 3000 | 479000 ± 1000 |
| 11s | 1246000 ± 8000 | 1246000 ± 1000 |

## Why it is worth a note of its own: it closes the Cs validation triangle

[quirk2024](quirk2024.md) established the *measurement* side — a 0.04% dc Stark
measurement giving $\alpha_{7s} = 6207.9(2.4)$ and hence
$\Delta\alpha({\rm Cs}\ 6s\to7s) = 5807~a_0^3$. This paper supplies the
*first-principles* side, computed by exactly the construction
`rb5s6s/polarizability.py` implements (a sum over states of
$|\langle \beta \Vert r \Vert v\rangle|^2$ over energy denominators):

- $\alpha_{7s}$: theory **6238 ± 41** against Quirk's measured
  **6207.9 ± 2.4** — a difference of 30, i.e. **0.7σ of the theory bar** and
  0.5% in absolute terms (CALCULATED here).
- The differential: theory gives $6238 - 398.4 = \mathbf{5840}$ against
  Quirk's $6207.9 - 401.1 = \mathbf{5807}~a_0^3$ — **agreement to 0.57%**.

**A complication this note must state rather than bury, because the table above
already contains it.** Their Table VIII's own *Expt.* entry for 7s is
**6238 ± 6**, footnoted as derived from the Bennett *et al.* (1999) 7s–6s Stark
shift measurement together with the Amini & Gould ground-state result — i.e. the
theory agrees with the *pre-2024* experiment to four figures. Quirk's measurement
moves the experimental value **down** by 30 against a stated ±6, so Quirk and the
older determination sit about 4.6σ apart on the combined bar. Quirk say as much:
their $k$ is about 0.5% smaller than Bennett's with an uncertainty more than
twice smaller, and they present it as superseding.

Two consequences. First, the theory–experiment comparison in Table VIII is **less
independent than it looks**: the scaling that assigns the theoretical uncertainty
is genuinely not tuned to experiment, but several input matrix elements are
experimental, and the 7s *Expt.* column derives from the same Stark-shift lineage
Quirk revises. Second, the 0.7σ theory-vs-Quirk agreement quoted above is
therefore weaker than it looks, since the theory sits essentially on the older
measurement. **In summary: theory and both measurements agree to about
0.5%, and the two measurements disagree with each other by more than either
quotes.** For validating a sum-over-states code at the percent level that is
ample — and it is why the target should be a band, not a four-figure number.

So the repository's own sum-over-states code now has a Cs target it must
reproduce *twice over*, from independent directions, on the structural analogue
of the disputed Rb 5s–6s quantity (`polarizability.py` gives
$\alpha_{6S} - \alpha_{5S} = 5167.0 - 318.3 = 4848.7$ a.u.). A code that
reproduces both to a fraction of a percent, signs included, is not making a
global sign error. That is the strongest available argument for the
$\Delta\alpha(993~{\rm nm})$ sign short of a new measurement, and it remains a
day's work.

**What it does not do**, and the caveat is the same as Quirk's: these are
**static** polarizabilities. The Rb dispute lives at 993 nm, where the answer is
a cancellation between an upward-shifting and a downward-shifting group of
states, and no amount of dc agreement constrains that cancellation directly. It
validates the machine, not the answer.

## Two further hooks into the current reading

**It carries the matrix elements `sieradzan2004` measured.** Their Table I lists
$\langle 8s \Vert r \Vert 6p_{1/2}\rangle = 17.78(7)$ and
$\langle 8s \Vert r \Vert 6p_{3/2}\rangle = 24.56(10)\ ea_0$ (all-order SD
scaled), a ratio of 1.381. Sieradzan, Havey & Safronova measured precisely the
**relative** $6p~^2P_j \to 8s~^2S_{1/2}$ matrix elements — so that paper is the
experimental check on these two numbers, and the two belong together. It is not
held (see `LITERATURE.md`).

**It sets the scale for `lee2010`.** $\alpha_{8s} = 38270(280)~a_0^3$ against
$\alpha_{6s} = 398.4(7)$ gives a static
$\Delta\alpha({\rm Cs}\ 6s\to8s) \approx 37900~a_0^3$ — about **6.5 times** the
$6s\to7s$ differential and **7.8 times** this repository's Rb 5s–6s value of
4848.7 a.u. (this note first said "35 times", which is simply wrong:
$37872/4848.7 = 7.8$). That
is the quantity behind the light shift [lee2010](lee2010.md) measures at 822 nm.
The comparison is *static against ac* and so is not a test, but it explains why a
Cs 6S–8S line is an unusually sensitive light-shift probe, and it is the first
thing to compute properly if that transition is ever a candidate for the
guided-mode work.
