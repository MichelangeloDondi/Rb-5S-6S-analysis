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
sweep is linear across the window to $<0.4\%$. A half-wave-plate trick mixes in
amplitude modulation on the ruler traces to suppress the carrier so the
sidebands stand tall — so the tooth *spacing* is exact, but tooth *heights*
carry no information about the modulation depth. *Code:* `ruler.py` (M2);
$\Omega/2$ locked by a permanent test in `test_constants.py`.

---

---

[← The composite model (and what does not enter it)](04_the_composite_model.md) · [The statistics →](06_the_statistics.md)
