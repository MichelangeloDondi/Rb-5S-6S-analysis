# The environment and the code

*[History](../HISTORY.md) · migrations, renames and switches that moved committed numbers*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The headline beta_self shift under the laser-kernel switch, 2026-08-20

`laser_kind` chooses a Gaussian or a Lorentzian for the laser's own contribution to the line, wired through `composite_profile`, `model_profile`, `fit_condition`, and `beta.py`, but had never been run at anything but its Gaussian default. Exercising it moves the headline collisional coefficient `beta_self` by 45 to 67 per cent, nine to eighteen sigma on its quoted statistical error. A per-condition figure of 45 per cent was also published and is withdrawn without replacement: at fixed condition a Lorentzian laser width and `beta_self` are identified only through their sum, so the split carries no information. The mechanism and the fix are at [the entry below](02_the-lineshape-and-its-kernel.md#an-exact-degeneracy-that-the-code-broke-and-the-number-that-had-no-referent-2026-08-20).

## The identifiability diagnostics moved under the arithmetic environment, 2026-08-22

Regenerating `run_identifiability` under a different numpy environment moved four numbers quoted in [the statistics chapter](../methods/06_the_statistics.md). The ridge slope moved from 0.073 to 0.086, the covariance prediction from 0.080 to 0.110, the condition number from 389.7 to 345.1, and the valley-floor RMS from 0.0032 to 0.0020. The best-constrained sigma is unchanged. The cause is the arithmetic environment, not the analysis change made that week, since pre-change code under the new environment gives the new values too. The prediction exceeds the measurement, so the chapter's relative claim stands, but its statement that the ridge slope reproduces unchanged did not survive and is corrected. These values were provisional pending [the environment migration](07_the-environment-and-the-code.md#the-environment-migration-landed-2026-08-23), which landed 2026-08-23 and made them the committed ones.

## A results path was renamed away from a collision, 2026-08-22

`results/lever_table.csv` and `scripts/run_lever_table.py` are now `results/orthogonal_levers.csv` and `scripts/run_orthogonal_levers.py`. The old name collided with `rb5s6s.hyperpolarizability.lever_table()`, an unrelated function that ranks candidate transitions for the Ti:Sapphire study, so a reader grepping the tree for one found the other. No content changed. A link to the old path from a commit before this date will not resolve.

## The environment migration landed, 2026-08-23

Committed result digits were made under Python 3.9.6 and numpy 2.0.2. They are now made under Python 3.14.6, numpy 2.5.2, scipy 1.18.0, pandas 3.0.5, Apple Accelerate, macOS 26.6.2 on arm64, recorded in `results/ENVIRONMENT_OF_RECORD.md` with the old-version recovery recipe. Of 58 committed result files, two moved, both from a changed `np.convolve`. `results/linefit_conditions.csv` moved by a part in a thousand or less on every row but one, condition `t_sweep / 4121 / 70 C`, given below. `results/identifiability.csv` moved on fourteen rows, including every value this migration changed in a published document, given below with the file each appears in. `results/resolving_power.csv` and `results/sigma_laser_sharing.csv` were regenerated from the drifted inputs. The shared sigma_laser range of 1.5 to 1.7 and the sharing chi-squares are unchanged.

| quantity | was | now | relative |
|---|---|---|---|
| `sigma_laser` | 0.4052 | 0.3531 | 1.29e-01 |
| `corr` | -0.70340 | -0.66265 | 5.79e-02 |
| `gamma_coll_err` | 0.23210 | 0.22059 | 4.96e-02 |
| `sigma_laser_err` | 1.4270 | 1.4721 | 3.16e-02 |
| `gamma_coll` | 0.78394 | 0.79727 | 1.70e-02 |
| `total_fwhm_err` | 0.18185 | 0.17972 | 1.17e-02 |
| `total_fwhm` | 5.07133 | 5.07598 | 9.17e-04 |

| quantity | was | now | quoted in |
|---|---|---|---|
| split sigma | 0.0624 | 0.0588 | front page and chapter 7 (ratio to total width 20 to 18) |
| collisional-to-transit correlation | -0.964 | -0.958 | `docs/PLAN.md`, opening chapter |
| collisional-to-laser correlation | +0.152 | +0.196 | `docs/PLAN.md`, opening chapter |
| condition number | 389.7 | 345.1 | quoted across public documents (rounds to 345) |
| ridge slope | 0.073 | 0.086 | `results/identifiability.csv` |
| covariance-side prediction | 0.080 | 0.110 | `results/identifiability.csv` |
| valley-floor RMS | 0.0032 | 0.0020 | `results/identifiability.csv` |
| `profile_free_gap` | -0.01 | -1.30 | `results/identifiability.csv` |
| `wide_free_gap` | -0.1 | +1.2 | `results/identifiability.csv` |
| resolving power, `sigma_laser` | 2.3 | 2.4 | `docs/RESULTS.md` (range 2.3-6.0 to 2.4-6.0) |
| K4 self-consistency, `t_sweep / 4121 / 70 C` | 1.700e-02 and 6.596e-08 | 0 and 0 | `results/kernel_k4.csv` |
