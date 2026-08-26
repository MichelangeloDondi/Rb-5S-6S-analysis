# What the proposed levers would buy: two projections with their constructions

Status: DIAGNOSTIC projections for the quantities dossiers, 2026-08-18.
Nothing here is a result about the atom, and no committed number moves.
Producers: `scripts/run_extended_lever.py` and, for the pinning factor it
cites, `scripts/run_width_pinning.py`. Run logs under `private/run_logs/`.

`provenance: DESIGN` - projections of what proposed levers would buy, by its own header, with nothing about the atom and no committed number moving. It names `run_extended_lever.py` and `run_width_pinning.py`, both of which exist and neither of which writes a results file. All eleven of its values are grounded. **No claim on this page is unaccounted for.** Declared after checking every three-significant-figure value on the page against `results/`, not by labelling.


## 1. The extended temperature lever for the collisional bound

The [self-broadening dossier](../quantities/self-broadening.md) proposes
150 and 170 C blocks with an absorption channel. The projection runs the
committed coverage construction, the model-independent width slope under a
between-block drift proxy of 0.12 MHz and a within-block error of 0.05 MHz,
with the temperature grid as a parameter, 2000 trials per grid.

| grid | points | density lever | median 95 per cent bound under a true zero | minimum detectable beta at 95 per cent |
|---|---|---|---|---|
| committed, 70 to 130 C | 4 | 52.5 | 0.0203 | 0.0377 |
| extended to 150 C | 5 | 151 | 0.0057 | 0.0190 |
| extended to 170 C | 6 | 393 | 0.0020 | 0.0190 |

Units MHz per 10^12 per cubic centimetre. The committed-grid row is the
validation anchor: its simulated median bound of 0.0203 sits beside the
record's actual pooled bound of 0.0249, so the construction reproduces the
scale of the real analysis before its extensions are read.

Read with both eyes open. The gain is a factor 3.5 at 150 C and 10 at
170 C on the median bound, and the assumptions are optimistic by
construction: the block scatter is held at its 130 C value, while blackbody
redistribution and thermal gradients can only raise it, which is exactly the
dossier's kill criterion. The 170 C bound would sit below the van der Waals
anchor of about 0.0034, so at that lever the experiment would constrain the
prediction, while the detection threshold at 95 per cent, 0.019, stays
above it: the extension converts the bound into a prediction-constraining
one and does not yet promise a detection at the predicted size.

## 2. The 16 micron skew channel, and why its precision is not projected

The [AC-Stark dossier](../quantities/ac-stark-light-shift.md)'s competitive
level runs at a waist near 16 microns, where the predicted on-axis shift is
5.56 MHz against the measured skew threshold of about 2.5 MHz, a margin of
2.2. That margin is computable from committed numbers and is the
extent of what can be projected today.

The achievable uncertainty on kappa at that operating point is not
projected here, for a stated reason rather than an oversight: at 5.56 MHz
the shift is comparable to the 5.4 MHz linewidth, the perturbative
cumulant scaling that sets the skew channel's cost at the current bound does not
extrapolate across the four orders of magnitude in between, and the
tool it needs is a full lineshape simulation at the tight-focus geometry, which the
record does not yet carry. That simulation is the named remaining
calculation, and any number quoted for this level before it exists would be
an invented one.
