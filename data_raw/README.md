# `data_raw/`, the dataset manifest

This directory holds **`MANIFEST.csv`** and not the traces it describes.

`MANIFEST.csv` is the frozen census of the 2025 archive: one row per unique
acquisition — its path, peak, role (`t_sweep` / `p_sweep` / `ruler_t` /
`ruler_p` / `quarantine`), temperature, power, curation flag, QC reason, the
source filenames it was merged from, and its MD5. 297 rows. It is the record
that fixes what the dataset *is*, and several tests in `tests/test_manifest.py`
check its internal consistency without needing the traces at all.

**The 297 raw traces themselves are held privately and available on request**
(michelangelo.dondi@unibo.it). They were taken at OIST in 2025. Their absence
here changes what can be run, not what can be checked:

| | runs in this repository |
|---|---|
| the analysis library and its full test suite | **yes**, the injection-recovery closures, the coverage study and minimum detectable effect, the transit-kernel asymptotics, identifiability, model comparison: all synthetic |
| the committed results, figures and ledger | **yes**, they are committed, and the docs↔code number locks check every quoted value against them |
| the lock-drift arc (audit addenda 4–7, 12) | **yes**, it runs off `data_recovered/CLOCK.csv`, which is hashes and timestamps rather than measurement data |
| the raw→results pipeline (`scripts/run_all.sh`) | **no**, it reads the traces |
| the four tests that re-hash traces against this manifest | **no**, they skip, with a stated reason |

With the traces restored to this directory, everything above runs and each
stage reproduces its committed CSV within the tolerance
`scripts/verify_results_fresh.py` states, and nothing else changes.

Provenance, decoding, curation history and the quarantine policy:
[`../docs/DATA.md`](../docs/DATA.md).
