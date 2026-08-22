*Chapter 6 of 9 of [the big picture](../BIG_PICTURE.md)*

## 6. What new nanofibre measurements would add

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

The evanescent field of an optical nanofibre is, in one sense, the natural
home of the ramp physics: the intensity gradient is steep and exponential,
so the local light-shift distribution is large and strongly shaped. What
carries over is the operation the record is built on, mapping a known
intensity geometry onto a shift distribution and reading its cumulants. The
closed-form ramp weight itself does not. It is derived for atoms **crossing** a
focused beam, and a trapped sample sits concentrated where the intensity is
highest, so its shift distribution has no hard edge and carries the opposite
sign of skewness (section 1.2 of the design note, which computes both).
Carrying the ramp over unchanged would get the sign of the line's asymmetry
wrong, and the third cumulant is the drift-immune channel this programme
relies on.

![the third cumulant as an observable: the two-photon asymmetry, the cumulant ladder, what each mechanism reaches, and the ceiling the record's bound puts on it](../../figures/fig30_third_cumulant.png)

*Figure 30. Why this channel is worth the session. The first panel shows what
the ramp does to the observable, and the difference below it is the
antisymmetric one-lobe-up, one-lobe-down signature that the third cumulant
measures. The third panel is the argument: every symmetric kernel contributes
to the variance and exactly nothing to κ₃, so the collisional-against-laser
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
separate a Lorentzian transit contribution from a temperature-independent
homogeneous one, since in a fibre the transit kernel is Lorentzian and adds
exactly to everything else. Under synthetic worlds calibrated to the
per-condition width precision this record already achieves, it identifies the
common Lorentzian component at 0.978 and 0.966 coverage at the two
decay-length band edges, and does **not** identify the Gaussian one, at 0.474.
A single-rung control fails to split, which is what makes the ladder the lever
rather than the fit. This is SIMULATION-BACKED and not a measurement: it says
the design can identify the intended quantities under stated worlds, not that
the apparatus will.

The cell line of §4–5 is the in-vacuo reference against which every
near-surface effect would be read. That is the connection between
the two halves of the program: the cell work is what makes the nanofibre
lineshapes *interpretable*.

---

*[The next vapour-cell session](05_next-vapour-cell.md) · [Limitations and identifiability](07_limitations-and-identifiability.md)*
