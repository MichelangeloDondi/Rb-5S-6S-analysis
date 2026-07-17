*Chapter 5 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

## 3. From volts-versus-time to a frequency axis (the EOM ruler)

The scope records fluorescence versus *time* while the laser sweeps; we need
$\nu$ versus time. The sweep is nonlinear and its rate unknown, so a ruler was
built into the scan: an EOM phase-modulates the light at exactly
$\Omega=12.5$ MHz, adding sidebands at $\nu_c\pm n\Omega$ around the carrier
$\nu_c$. Two-photon absorption picks any *pair* of sidebands whose frequencies
sum to the transition $\nu_0$:

$$(\nu_c+m\Omega)+(\nu_c+m'\Omega)=\nu_0
  \Longrightarrow
2\nu_c+(m+m')\Omega=\nu_0$$

Writing $k=m+m'$, resonances occur at carrier frequencies
$\nu_c=(\nu_0-k\Omega)/2$, i.e. a comb of line-copies spaced by

$$\boxed{ \Delta\nu_\text{tooth}=\frac{\Omega}{2}=6.25\ \text{MHz (laser axis)} }$$

— the same factor-2 as [§0 — conventions](../methods.md). Fitting the tooth spacing (in ms) per block gives
the sweep rate; we measure $0.04257(5)$ MHz/ms on the laser axis, and the
sweep is linear across the window to $<0.4$%. A half-wave-plate trick mixes in
amplitude modulation on the ruler traces to suppress the carrier so the
sidebands stand tall — so the tooth *spacing* is exact, but tooth *heights*
carry no information about the modulation depth. *Code:* `ruler.py` (M2);
$\Omega/2$ locked by a permanent test in `test_constants.py`.

### Why the ruler is a clean number — the common-mode rejections

The rate is a *differential* measurement across five copies of the **same
physical line**, and everything that afflicts the line afflicts every copy
equally:

- **The AC-Stark shift.** The atom sees the *total* field — carrier plus all
  sidebands, both beams — at every instant, regardless of which tooth is
  resonant, so the light shift translates the whole comb **rigidly**: the
  spacing is untouched. The residual is second-order — a power drift *within*
  one trace shifts teeth differentially by $S_0\times$(fractional drift per
  spacing) $\lesssim10^{-4}$ at the archival $S_0\lesssim0.6$ MHz — below the
  quoted precision.
- **The line asymmetry** (the ramp skew of [§2.6](03_the_ac_stark_ramp.md),
  or any other shape distortion). Same line, same intensity, same shape on
  every tooth ⇒ the same centre pull on every tooth ⇒ absorbed into the comb
  phase $t_0$, never into the spacing. The genuine second-order effect —
  **edge teeth have only one neighbour**, so overlapping *asymmetric* wings
  pull the comb ends differently — is why the fit is a *constrained
  simultaneous* comb (one shared tooth shape, free heights; at $\sim$147 ms
  spacing and $\sim$60 ms width a strong tooth's wing under a weak neighbour
  is $\sim$20% of the weak peak, and single-tooth fits pull centres by O(ms)),
  and why the free-centres nonlinearity map exists: it bounds *any*
  tooth-dependent pull — scan nonlinearity and differential shape effects
  together — **empirically at $\lesssim0.3$% per position**
  (`results/ruler_nlmap.csv`), already inside the quoted error through the
  PDG block-scatter inflation.
- **Sideband amplitude imbalance** (residual AM from the carrier-suppression
  trick): absorbed by the free per-tooth heights — amplitude never enters the
  spacing.
- **Laser drift during a trace** is not a bias but part of the *measured*
  effective rate, and the line fits use their own block's rate — the drift is
  self-consistently calibrated out, which is the whole point of a per-block
  ruler under a drifting lock.

`figures/fig8_ruler.png` shows a representative trace with its five-tooth comb
fit and the nonlinearity map.

### The comb amplitudes — and the pure-phase-modulation null

For *pure* phase modulation at index $\beta$ on both counter-propagating
beams, the two-photon tooth amplitudes obey an exact closed law: the tooth at
$k$ sums every sideband pair $m+m'=k$, and by Neumann's addition theorem

$$A_k \propto \Big|\sum_m J_m(\beta) J_{k-m}(\beta)\Big|^2 = J_k(2\beta)^2 .$$

This explains the 2025 design compromise and prescribes its fix:

- **At small $\beta$ the sidebands are buried**: $J_k(2\beta)^2$ gives
  $1 : 0.10 : 0.002$ at $\beta=0.3$ — the outer teeth drown in the central
  tooth's tails. The 2025 workaround rotated a half-wave plate to admix
  amplitude modulation and suppress the optical carrier — which worked, but
  put the ruler light at a **different polarization and power than the science
  light** (the reason the ruler traces cannot serve as a hardware-matched
  width monitor for the archive; PLAN §8.4).
- **The clean fix needs no polarizer at all**: drive the EOM at
  $\beta \approx 1.202$ (where $J_0(2\beta)=0$) and the central tooth **nulls
  by coherent pair interference** — the two-photon analogue of carrier
  suppression — leaving a comb $0 : 1.00 : 0.69 : 0.15$ ($k=0,\pm1,\pm2,\pm3$)
  with the ruler light *identical* to the science light.
- **The pattern is a built-in modulation diagnostic**: pure PM demands
  $A_{+k}=A_{-k}$ exactly; the 2025 traces violate it (e.g. $1.00$ vs $0.90$
  at $k=\pm1$ on a T-session ruler, with block-dependent central-tooth
  suppression) — the fingerprint of the AM admixture, visible per block. A
  fixed-lock session can monitor modulation purity live from the tooth
  asymmetry alone.

---

---

[← The composite model (and what does not enter it)](04_the_composite_model.md) · [The statistics →](06_the_statistics.md)
