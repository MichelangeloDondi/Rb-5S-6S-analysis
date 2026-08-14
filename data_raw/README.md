# `data_raw/`: the traces and their manifest

This directory holds the 297 recorded traces of the 2025 dataset and
**`MANIFEST.csv`**, the census that says what the dataset is. The traces are
withheld from the published mirror, where this file says so and lists what can
still be run without them. They are available on request.

`MANIFEST.csv` carries one row per unique acquisition: its path, peak, role,
temperature, power, curation flag, QC reason, the source filenames it was
merged from, and its MD5. 297 rows. `tests/test_manifest.py` checks the
manifest's internal consistency, and four further tests re-hash every trace in
this directory against it, which is the check the mirror cannot run.

The subdirectories are the roles the manifest names:

| directory | what is in it |
|---|---|
| `t_sweep/` | the temperature ladder, 70 to 130 °C at 225 mW |
| `p_sweep/` | the power ladder, 25 to 225 mW at 130 °C |
| `rulers_t/`, `rulers_p/` | the EOM frequency-ruler calibration traces bracketing each ladder |
| `excluded/` | acquisitions held out of every fit, each with its reason in the manifest |
| `discarded/` | files replaced before any fit, kept so the exclusion is auditable |

A file's presence here is not what admits it to a fit. The manifest's curation
flag decides that, and `docs/DATA.md` carries the provenance, the decoding, the
curation history and the excluded policy, including why each excluded
acquisition was excluded.

Nothing in this directory is edited. A correction enters as a new acquisition
with its own manifest row, so that what was analysed stays recoverable.

Provenance and exclusions: [`../docs/DATA.md`](../docs/DATA.md). The dataset's
own census: [`MANIFEST.csv`](MANIFEST.csv).
