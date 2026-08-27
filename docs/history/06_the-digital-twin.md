# The digital twin

*[History](../HISTORY.md) · the twin's own corrections*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The digital twin's blackbody term, corrected 2026-08-24

The twin previously produced idealised traces, not what a named instrument
at named settings would record. It is now instrument-aware: oscilloscopes
are objects with real limits (`rb5s6s/instruments.py`), each labelled in
place with its source, a manual or a measurement, and the two resolution
mechanisms, disjoint boxcar and moving average, are distinguished in code
instead of treated alike. The platform now decides the blackbody term: the heated cell
radiates against itself and is evaluated at the cell temperature, while
the nanofibre is fixed at 300 K regardless of the atom temperature, since
laser-cooled atoms near a fibre radiate against the room and not against
themselves. Reading the atom temperature as the radiation temperature
would return essentially zero. `results/twin_realism.csv` records what
each instrument stores against what the production fitter recovers,
ratios of 0.99 to 1.06 at two sample correlations.
