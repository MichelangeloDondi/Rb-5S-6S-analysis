#!/usr/bin/env python3
"""Which windowed cumulants this archive can actually read, and which it cannot.

THE QUESTION THIS ANSWERS, and it had never been asked with the noise in it.
`fullmodel.DEFAULT_ORDERS` carried the odd orders (2, 3, 5, 7) until
2026-09-12, on the reasoning that the odd orders carry the ASYMMETRY and the
asymmetry is where the light shift lives. That reasoning is sound about the
signal and silent about the noise. Measured here on the twin's own world, under
the correlation time `results/noise_model.csv` reports, every odd statistic
sits below a per-trace signal-to-noise of 3 and every even one sits far above
it. So the odd ladder is not a weaker channel than the even one; on THIS
archive it is not a channel.

A windowed cumulant of pure noise is largest exactly where the signal is
smallest (register A74), so a refused statistic averaged into a joint fit does
not dilute the answer, it inverts it. That is why this file exists as an
ADMISSION test with a stated floor rather than as a ranking.

WHAT THE ROWS ARE. One row per (statistic, window): its mean over the
realisations, its per-trace scatter, the per-trace SNR, the SNR pooled over the
105-trace power arm, and ADMITTED or REFUSED against the floor. Then the
summary rows: the effective rank of the admitted set, which is what says how
many independent numbers the ladder really carries, and the covariance's
condition number, which is what says an interval through it needs a stability
check before it is quoted.

THE NOISE LAW IS INTERNALLY INCONSISTENT AND THE CONSERVATIVE BRANCH IS TAKEN.
The committed law gives `tau_int = 2.515` and `rho1 = 0.098`. An AR(1) at that
first lag has `tau_int = (1+r)/(1-r) = 1.217`, so the measured integrated time
is 2.07 times what its own first lag implies and the real autocorrelation is a
small first lag with a long tail. A statistic's variance is set by the
INTEGRATED time, so this matches `tau_int` and records the discrepancy in a
row. Matching `rho1` would understate the correlation and OVERSTATE the
information, which is the direction that flatters.

STATUS. Every row is a twin measurement about what the archive's data COULD
support, not a fit to the 2025 traces, so every row is DIAGNOSTIC.
"""
import csv
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s.fullmodel import ultra_joint_covariance                # noqa: E402
from rb5s6s.noise import load_noise_model                          # noqa: E402
from rb5s6s.pmfmt import in_plain_band, pm_cells                   # noqa: E402

# RESOLVED AT CALL TIME, never bound at import: `_CFG.RESULTS_DIR` is computed
# from RB5S6S_RESULTS_DIR when `config` is first imported, so a module-level
# name freezes whatever the environment held then, and a caller that redirects
# the directory after importing this producer in-process would write to the
# wrong place. The freshness checker runs producers in a subprocess with the
# override already in the environment, so that is not what it saw: its cheap
# path reported "did not write into RB5S6S_RESULTS_DIR" for this producer
# because it compared BYTES, and a deterministic producer reproduces its
# committed file byte for byte. The checker tests the write itself now (an
# mtime sentinel, 2026-09-12); the resolution here stays because it is right.

NU = np.linspace(-25.0, 25.0, 1501)
N_REAL = 600
#: the counts the effective-rank uncertainty is measured over
N_REAL_SWEEP = (600, 1200, 4000)
SNR_FLOOR = 3.0
ROLE = "p_sweep"          # the arm this producer loads its noise law for


def _power_arm_traces() -> int:
    """The pooled arm's size, COUNTED from the manifest and never typed.

    It was typed once, as 105, which is `ruler_p + ruler_t` and not the
    `p_sweep` role this producer selects its noise law by. The manifest counts
    101. The two must agree by construction or the label drifts from the
    population, which is what happened on 2026-09-12 in the same wave that
    recorded register entry A206 for exactly this class.

    FAILURE MODE: `data_raw/` is excluded from the public mirror by the porter,
    so a clone without raw traces cannot count. The committed CSV carries the
    number in its own row and that is what such a clone reads, which is why the
    row exists rather than being derivable.
    """
    import csv as _csv
    src = _CFG.DATA_RAW_DIR / "MANIFEST.csv"
    if not src.exists():                       # a clone without raw traces
        prev = _CFG.RESULTS_DIR / "moment_admission.csv"
        if prev.exists():
            for row in _csv.DictReader(prev.open(encoding="utf-8")):
                if row["quantity"] == "power_arm_traces":
                    return int(float(row["value"]))
        raise SystemExit(
            "run_moment_admission: no manifest to count the arm from and no "
            "committed row to read it back, so the pooled figures would rest "
            "on a typed number, which is the defect this function replaced")
    with src.open(encoding="utf-8") as fh:
        return sum(1 for r in _csv.DictReader(fh) if r["role"] == ROLE)
# the archive's own working point, the values the record fits to
POINT = dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575,
             gamma_l=0.40, s0=0.364, peak="4192", T_C=110.0)


def main() -> int:
    POWER_ARM_TRACES = _power_arm_traces()
    law = load_noise_model(str(_CFG.RESULTS_DIR / "noise_model.csv"),
                           role=ROLE, pool="median")
    tau_int, rho1 = law["tau_int"], law["rho1"]
    a_ar = (tau_int - 1.0) / (tau_int + 1.0)

    # THE SPREAD IS MEASURED, NOT TYPED. The note beside these rows says the
    # uncertainty is the spread over realisation counts of 600, 1200 and 4000,
    # and the first cut wrote a bare 0.05 while calling the function once. The
    # real spread of the admitted rank is about half that, and the literal was
    # only close for the OTHER row, which is what made it look right. The
    # counts the note names are the counts the code runs.
    ranks, ranks_all = [], []
    for _n in N_REAL_SWEEP:
        _r = ultra_joint_covariance(NU, n_real=_n, tau_int=tau_int,
                                    snr_floor=SNR_FLOOR, seed=4_000_000, **POINT)
        ranks.append(_r["effective_rank"]); ranks_all.append(_r["effective_rank_all"])
        if _n == N_REAL:
            r = _r
    er_spread = float(np.std(ranks, ddof=1))
    era_spread = float(np.std(ranks_all, ddof=1))

    # `err` and not `uncertainty`: it is the house column name (see
    # `polarisation_bound.csv`) and the one
    # `test_every_claim_carries_an_uncertainty` recognises.
    out = [["quantity", "window_mhz", "value", "err", "note", "status"]]
    admitted = set(r["admitted"])
    for key, mean, sd, snr in zip(r["keys"], r["mean"], r["sd"], r["snr"]):
        stat, wtxt = key.split("@")
        verdict = "ADMITTED" if key in admitted else "REFUSED"
        pooled = snr * np.sqrt(POWER_ARM_TRACES) if np.isfinite(snr) else float("nan")
        # NO COLON IN A QUANTITY NAME. `check_references.py` splits a
        # `ref:<stem>:<col0>:<col1>` tag on colons, so a quantity carrying one
        # is uncitable, which is the whole point of putting it in results/.
        # written through pm_cells so the uncertainty carries two significant
        # digits and the value matches its decimals (LANGUAGE 8a.2). A
        # statistic refused this hard can fall out of 8a.2a's plain-decimal
        # band, where the factored form is owed and two separate cells cannot
        # carry it: the uncertainty then goes into the NOTE rather than being
        # dropped, because a refused statistic still states how well it is
        # known.
        se = float(snr / np.sqrt(2.0 * N_REAL)) if np.isfinite(snr) else float("nan")
        if np.isfinite(snr) and in_plain_band(float(snr), se):
            v_cell, e_cell, se_txt = (*pm_cells(float(snr), se), "")
        elif np.isfinite(snr):
            v_cell, e_cell = f"{snr:.3g}", ""
            se_txt = f" Its standard error is {se:.2g}, outside the plain-decimal band."
        else:
            v_cell, e_cell, se_txt = "", "", ""
        out.append([
            f"snr_{stat}", wtxt, v_cell, e_cell,
            f"{verdict} at a floor of {SNR_FLOOR:g}. Mean {mean:.6g}, "
            f"per-trace sd {sd:.4g}. Pooled over {POWER_ARM_TRACES} traces "
            f"it reaches {pooled:.4g}.{se_txt}",
            "DIAGNOSTIC"])

    even = sorted({int(k[1:k.index("@")]) for k in r["admitted"] if "/" not in k})
    odd = sorted({int(k[1:k.index("@")]) for k in r["refused"] if "/" not in k})
    out.append(["admitted_orders", "", ",".join(map(str, even)), "",
                "the orders clearing the floor at every window", "DIAGNOSTIC"])
    out.append(["refused_orders", "", ",".join(map(str, odd)), "",
                "the orders below it at every window. The split is exactly "
                "by parity and that is the result", "DIAGNOSTIC"])
    # THE RANGES ARE CELLS SO A DOCSTRING CAN CITE THEM. Three surfaces
    # quoted "30 to 2332 against 0.01 to 0.22" from an earlier run; the
    # committed maximum is 1832 and no cell held 2332. A range stated in prose
    # and held nowhere is unciteable by construction, so `check_references`
    # could not see it. It can now.
    _adm = [s for k, s in zip(r["keys"], r["snr"]) if k in set(r["admitted"])]
    _ref = [s for k, s in zip(r["keys"], r["snr"]) if k not in set(r["admitted"])]
    for name, vals in (("snr_admitted_min", _adm), ("snr_admitted_max", _adm),
                       ("snr_refused_min", _ref), ("snr_refused_max", _ref)):
        v = (min(vals) if name.endswith("min") else max(vals)) if vals else float("nan")
        out.append([name, "single_valued", f"{v:.4g}", "",
                    "single_valued because it is one end of a span and an "
                    "extreme has no spread of its own. The per-statistic rows "
                    "above carry the distribution. Written as a cell so a "
                    "docstring or a page cites it instead of restating it",
                    "DIAGNOSTIC"])

    out.append(["n_admitted", "", str(len(r["admitted"])), "",
                f"of {len(r['keys'])} statistics over three windows",
                "DIAGNOSTIC"])
    er_v, er_e = pm_cells(float(r["effective_rank"]), er_spread)
    out.append(["effective_rank_admitted", "", er_v, er_e,
                "participation ratio of the admitted correlation matrix: the "
                "admitted set carries about three independent numbers and "
                "not its column count. The uncertainty is the spread over "
                f"realisation counts of {N_REAL_SWEEP}", "DIAGNOSTIC"])
    era_v, era_e = pm_cells(float(r["effective_rank_all"]), era_spread)
    out.append(["effective_rank_all", "", era_v, era_e,
                "the same over every statistic including the refused ones. "
                "It reads higher because pure noise is nearly full rank, and "
                "quoting it as the information content is the trap",
                "DIAGNOSTIC"])
    out.append(["condition_number_admitted", "", f"{r['cond']:.3g}", "",
                "an interval taken through a pseudo-inverse of a matrix "
                "this ill-conditioned is only quotable where it is stable "
                "against the cutoff. The width is and the shift is not",
                "DIAGNOSTIC"])
    out.append(["tau_int", "", f"{tau_int:.3f}", "",
                "integrated correlation time in samples, from noise_model.csv "
                "pooled over the p_sweep role", "DIAGNOSTIC"])
    out.append(["rho1_measured_vs_ar1", "", f"{a_ar / rho1:.2f}", "",
                f"the AR(1) first lag matching tau_int is {a_ar:.3f} against "
                f"a measured rho1 of {rho1:.3f}. The two committed numbers are "
                "not mutually consistent, the autocorrelation has a long tail, "
                "and matching tau_int is the conservative branch", "DIAGNOSTIC"])
    out.append(["power_arm_traces", "", str(POWER_ARM_TRACES), "",
                f"counted from the manifest at role={ROLE}, and read back from "
                "this row by a clone without raw traces", "DIAGNOSTIC"])
    out.append(["pooling_divisor", "", str(POWER_ARM_TRACES), "",
                "POOLING OVER TRACES DIVIDES BY THE TRACE COUNT, not by the "
                "count over tau_int. The correlation time is between SAMPLES "
                "inside one trace and is already carried by the per-trace "
                "covariance these SNRs come from. Dividing again double counts "
                "it, which is the error master plan 17u records for the waist "
                "figure and which this row exists to stop repeating",
                "DIAGNOSTIC"])

    dst = _CFG.RESULTS_DIR / "moment_admission.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(out)
    print(f"{len(r['admitted'])} admitted, {len(r['refused'])} refused; "
          f"effective rank {r['effective_rank']:.2f}")
    print(f"wrote {os.path.relpath(dst, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
