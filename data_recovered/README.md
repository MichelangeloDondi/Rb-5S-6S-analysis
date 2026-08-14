# data_recovered/, the backup-recovered layer

The frozen analysis dataset is `data_raw/` and nothing here changes it. This
layer holds what the timestamped backup added *after* the dataset was frozen
(recovered 2026-07-22/24 and audited under pre-registration, see
[docs/PREREGISTRATION_timestamps.md](../docs/PREREGISTRATION_timestamps.md)
and the results report
[docs/PREREGISTRATION_RESULTS.md](../docs/PREREGISTRATION_RESULTS.md),
addenda 1–9):

| item | what it is |
|---|---|
| `CLOCK.csv` | the acquisition clock: content hash → FAT mtime for all 438 files across the four backup source trees, whose `source` column still carries the labels it was built with (`main` / `rawdata2` / `pilot` / `prehistory`, the last two being the campaign-morning session and the 4 July sessions), with the manifest identity where content matches the dataset. Epochs are integers (FAT 2 s granularity); interpret in JST (UTC+9) for acquisition-local time. Built by `scripts/build_clock_table.py`; byte-deterministic. |
| `discarded_backup/` | the 16 discarded acquisitions that survive only in the backup, the evidence behind the curation test (addendum 3). **None ever entered a fit.** |
| `lineage_4192nm_225mw1/` | the four variants of the dataset's one degraded trace, whose dated degradation chain addendum 8 closed. |
| `RECOVERED_MANIFEST.csv` | file → original name, source, role, md5, bytes for everything above. Built by `scripts/publish_recovered.py`. |

**Match by hash, never by name**: nine of the recovered names collide with
*different* bytes in `data_raw/`. That collision is how an entire re-take
series stayed hidden until content hashing exposed it. Filenames here carry
an `__<md5-8>` suffix for that reason.

The complete timestamped backup (438 files including the campaign-morning
session and the 4 July session, the latter's evening run made on the LeCroy
scope) is preserved verbatim as a release asset, so see the release notes
and addendum 10 for the backup's hash. The results that *use* this layer:
`scripts/run_drift_settling.py`
(reads `CLOCK.csv`) and the curation test of addendum 3.
