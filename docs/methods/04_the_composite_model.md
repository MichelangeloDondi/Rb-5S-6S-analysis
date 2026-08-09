*Chapter 4 of 8 · [methods index](../methods.md)*

**The question.** How do the separate kernels become one profile in code, and
what is deliberately kept out of it?
**Takes.** The lineshape chapter and the AC-Stark chapter, whose kernels it
assembles.
**Gives.** `model_profile()` and `composite_profile()`, the two functions every
fit in the statistics and results chapters calls.
**Skip if.** You are not going to read the code. Most of this chapter is
radiation trapping, the mechanism that moves amplitudes without moving the
lineshape, and the trapping result itself is reported in the results chapter.

### 2.7 Radiation trapping — why it moves amplitudes, not the lineshape

At high density the cell becomes optically thick to the 795 nm detection
photons: a photon emitted deep inside can be **reabsorbed by a ground-state
atom** and re-emitted, possibly many times, before escaping. The optical depth
governing this is

$$\tau_\text{opt}=n_g\sigma_{795}L$$

with $n_g$ the ground-state density, $\sigma_{795}$ the absorption cross
section, $L$ the path. Here $n_g$ is the *thermal*
ground-state population, essentially the full density $N$, which the weak
two-photon excitation barely perturbs — and it is the **same at every point of
the 993 nm frequency scan**. So the photon escape probability
$\epsilon(\tau_\text{opt})$ is a constant multiplier across the scan: trapping
**rescales the amplitude** (and can alter photon-counting *statistics*) but
does **not** distort the two-photon lineshape. Onset is at
$\tau_\text{opt}\sim1$, i.e. $N\sim1/(\sigma_{795}L)\sim10^{12}$ to $10^{13}$
cm⁻³, straddled by our T-sweep. We tested the statistics route: the
shot-noise coefficient $b$ in the noise law ([§4.4](06_the_statistics.md)) is **flat in temperature**
(no growth of the Fano factor 70→130 °C), so trapping, if it shows anywhere,
shows in *amplitude ratios* versus density (module M7, against [Nieddu's 2019](../lit/nieddu2019.md)
same-channel baseline), never in the width. *Code:* the $b(T)$ table from
`noise.py`; the M7 finding is below.

There is one further subtlety that connects trapping to the **degeneracy law**
(§ amplitude ratios, module M10). Trapping is scan-constant *for a given peak*,
but it is **not** the same *across* peaks: the emitted 795 nm photon's frequency
is set by which $5P_{1/2}F'$ and $5SF''$ the cascade uses, so different
hyperfine paths and the two isotopes overlap the ground-state D1 absorption
differently. ⁸⁵Rb carries $\sim 2.6\times$ the ground-state
D1 absorbers of ⁸⁷Rb (its 72 % abundance), so at equal density it is
trapped harder. Differential trapping is therefore a candidate mechanism for
breaking the pure population ratios (5/3, 7/5, 2.42) — and, unlike the
between-block drift, it is **monotonic in density and isotope-ordered**, which
is exactly the discriminator M7 now runs.

### 2.8 The composite model in code

`model_profile()` assembles every kernel of
[the lineshape chapter](02_the_lineshape.md) and the ramp of
[the AC-Stark chapter](03_the_ac_stark_ramp.md) on a common fine grid (homogeneous
Lorentzians combined analytically, the rest convolved numerically), returns an
area-normalized profile, and `fit_condition()` fits it to data with the
per-trace nuisances of [§4.2](06_the_statistics.md). It uses the pure triangular ramp
(`stark_ramp()`); the archival fits keep it because $S_0$ is fixed per power
and the geometry correction sits far below the 2025 noise. A proposed fixed-lock session's
center-fits would swap in `stark_ramp_axial()` (the diverging-beam kernel of
[§2.6](03_the_ac_stark_ramp.md))
once the collection profile is measured. The no-Stark composite shared by the
$\beta_\text{self}$ and global fits is `composite_profile()` in the same
module.

---

**Where the numbers live.** Modules M3, M7, M10 · producers
`scripts/run_amplitude_trapping.py`, `scripts/run_amplitude_ratios.py` ·
results `results/amplitude_trapping.csv`, `results/amplitude_ratios.csv` ·
figures: none of its own. Library code: `rb5s6s/lineshape.py`, for
`model_profile()` and `composite_profile()`, and the $b(T)$ table from
`rb5s6s/noise.py`.

**What would falsify this.** A width that moved with density the way the
amplitudes do. The argument here is that trapping is constant across a scan, so
it can rescale a peak but cannot broaden it, and a density-ordered width change
surviving the between-block drift would break that.

[← The AC-Stark ramp](03_the_ac_stark_ramp.md) · [From volts to a frequency axis →](05_the_frequency_ruler.md)
