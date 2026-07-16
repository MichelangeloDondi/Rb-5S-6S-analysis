*Chapter 4 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

### 2.7 Radiation trapping — why it moves amplitudes, not the lineshape

At high density the cell becomes optically thick to the 795 nm detection
photons: a photon emitted deep inside can be **reabsorbed by a ground-state
atom** and re-emitted, possibly many times, before escaping. The optical depth
governing this is

$$\tau_\text{opt}=n_g\sigma_{795}L$$

with $n_g$ the ground-state density, $\sigma_{795}$ the absorption cross
section, $L$ the path. The decisive point: $n_g$ is the enormous *thermal*
ground-state population, essentially the full density $N$, which the weak
two-photon excitation barely perturbs — and it is the **same at every point of
the 993 nm frequency scan**. So the photon escape probability
$\epsilon(\tau_\text{opt})$ is a constant multiplier across the scan: trapping
**rescales the amplitude** (and can alter photon-counting *statistics*) but
does **not** distort the two-photon lineshape. Onset is at
$\tau_\text{opt}\sim1$, i.e. $N\sim1/(\sigma_{795}L)\sim10^{12}$–$10^{13}$
cm$^{-3}$, straddled by our T-sweep. We tested the statistics route: the
shot-noise coefficient $b$ in the noise law ([§4.4 — The statistics](06_the_statistics.md)) is **flat in temperature**
(no growth of the Fano factor 70→130 °C), so trapping, if it shows anywhere,
shows in *amplitude ratios* versus density (module M7, against Nieddu's 2019
same-channel baseline), never in the width. *Code:* the $b(T)$ table from
`noise.py`; the M7 finding is below.

There is one further subtlety that connects trapping to the **degeneracy law**
(§ amplitude ratios, module M10). Trapping is scan-constant *for a given peak*,
but it is **not** the same *across* peaks: the emitted 795 nm photon's frequency
is set by which $5P_{1/2}F'$ and $5SF''$ the cascade uses, so different
hyperfine paths and the two isotopes overlap the ground-state D1 absorption
differently. Crucially, $^{85}$Rb carries $\sim 2.6\times$ the ground-state
D1 absorbers of $^{87}$Rb (its 72 % abundance), so at equal density it is
trapped harder. Differential trapping is therefore a candidate mechanism for
breaking the pure population ratios (5/3, 7/5, 2.42) — and, unlike the
between-block drift, it is **monotonic in density and isotope-ordered**, which
is exactly the discriminator M7 now runs.

### 2.8 The composite model in code

`model_profile()` assembles [§2.1 — The lineshape, kernel by kernel](02_the_lineshape.md)–2.6 on a common fine grid (homogeneous
Lorentzians combined analytically, the rest convolved numerically), returns an
area-normalized profile, and `fit_condition()` fits it to data with the
per-trace nuisances of [§4.2 — The statistics](06_the_statistics.md). It uses the pure triangular ramp
(`stark_ramp()`); the archival fits keep it because $S_0$ is fixed per power
and the geometry correction sits far below the 2025 noise. A fixed-lock session
center-fits swap in `stark_ramp_axial()` (the diverging-beam kernel of [§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md))
once the collection profile is measured. The no-Stark composite shared by the
$\beta_\text{self}$ and global fits is `composite_profile()` in the same
module.

---

---

[← The AC-Stark ramp](03_the_ac_stark_ramp.md) · [From volts to a frequency axis →](05_the_frequency_ruler.md)
