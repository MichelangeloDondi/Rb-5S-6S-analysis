# The band excess

*[History](../HISTORY.md) · the out-of-window band, its construction and its predictor*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The in-window structure and the band excess share a predictor, 2026-08-23

K4's in-window residual structure and the reproducible excess outside the fit window were described as an unresolved relation on three published surfaces. A joint regression, weighted by the inverse variance of each condition's own amplitude, over n = 32 conditions, now measures both against the same two predictors, the model's own profile height and log10 vapour number density, in `results/kernel_k8.csv`:

| predictor | z, inside window | z, outside window |
|---|---|---|
| profile height | +9.41 | +8.65 |
| log10 density | +1.30 | -0.75 |

The two predictors correlate +0.488, below the preregistered collinearity threshold of 0.8. Height dominates in both windows. Density is not significant in either. No mechanism is named for the structure. R_kernel and every committed bound are unchanged.

## The band-excess significance pair, 2026-08-24

The 2026-08-17 note reported the shared excess surviving per-trace cubic freedom at 3.6 sigma, joint height significance at 8.65 sigma, and its two predictors correlating at 0.415. `scripts/run_band_excess.py` rebuilds that construction from the same 79 committed traces, documenting every choice, and writes `results/band_excess.csv`. The census of 79 traces reproduces exactly. The headline rows do not. Cubic-surviving amplitude returns 1.4 sigma, joint height significance returns 3.05 sigma, and the predictors are collinear at 0.896. The note under-specified its own construction. Its height predictor was a different construction than its prose specifies. The density-negative reading the finding turns on is the one part both runs agree on.

## The band regression's density sign, 2026-08-24

The band-excess joint regression's density term was published as negative, the one point where the note and its reconstruction agreed. A preregistered enumeration recovered the note's original predictor, the absolute in-band model height, whose 0.415 correlation fingerprint the reconstruction's shape-only predictor did not match. Under that recovered predictor the current amplitudes give the opposite pattern: profile height near zero and density marginally positive, at +2.2. The band's mechanism is now OPEN, and the note, BIG_PICTURE, chapter 07 and K8's verdict note all say so. K8's own in-window result is unaffected.
