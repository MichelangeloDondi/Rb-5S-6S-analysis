"""The sanctioned way to print a bias, and the only one.

WHY IT REFUSES WITHOUT A COVERAGE (2026-09-14, the defect that earned the rule). The twin was called
unbiased on a bias measurement while its SPREAD had never been compared with anything, and it was wrong
by a factor of two in variance. A bias without a coverage beside it is a statement about a mean with no
statement about the distribution it was drawn from, and the general form is this record's own: a claim
about an instrument needs a MEASUREMENT of that instrument, not an argument about it.

WHY IT REFUSES WITHOUT AN UNCERTAINTY, which is new (owner, O35, 2026-09-20: "always report the bias's
uncertainty, at two significant digits"). The two copies this replaces lived in
`private/cache/closure_2026-09-14/` and printed `bias {:+.3f}` with a hardcoded three decimals and no
standard error at all, so a bias of +0.142 read the same whether its error was 0.014 or 0.14 -- the
difference between a ten-sigma effect and a fluctuation. The standard error is COMPUTED from the sample
rather than passed in, because a caller that can be asked for it is a caller that can guess it.

WHY IT IS IN THE PACKAGE. This repository's working rules name this function as the only sanctioned way
to print a bias, and until this module existed that sentence was false: the only implementations were two
copies under a cache directory, importable by nothing, so every harness outside that directory printed
its biases however it liked. A rule naming a mechanism that does not exist is worse than no rule, because
it reads as covered.

FORMATTING is `rb5s6s.pmfmt`'s and is not restated here: two significant digits on the uncertainty, the
value carried to the uncertainty's own decimals (LANGUAGE 8a.2).
"""
from __future__ import annotations

import math

import numpy as np

from . import pmfmt


class BiasRefused(Exception):
    """Raised instead of printing. A bias this function will not print is a bias that is not reported."""


def bias_with_coverage(values, truth: float, bars) -> dict:
    """Return the bias, its standard error, the realised scatter and the coverage, or raise.

    `values` are the estimates from independent realisations, `truth` the injected value, `bars` the
    interval half-width each realisation reported for itself. Coverage is the fraction whose own bar
    covers the truth, which is the question a bar exists to answer.

    THE REFUSALS, each naming the defect it prevents:
      * fewer than two realisations -> no standard error exists, so the bias cannot be reported at all;
      * no finite bar -> no coverage, which is the 2026-09-14 defect;
      * a non-finite bias, standard error or coverage -> a NaN printed as a number is the ledger entry
        of 2026-09-20 02:25, and a NaN that reaches prose is indistinguishable from a measurement.
    """
    v = np.asarray(values, dtype=float)
    b = np.asarray(bars, dtype=float)
    if v.ndim != 1 or v.size < 2:
        raise BiasRefused(f"a bias needs at least two realisations to carry a standard error; got {v.size}")
    if not np.isfinite(v).all():
        raise BiasRefused("the realisations carry a non-finite value, so their mean is not a bias")
    if b.shape != v.shape:
        raise BiasRefused(f"one bar per realisation: {b.shape} bars against {v.shape} values")
    ok = np.isfinite(b)
    if not ok.any():
        raise BiasRefused("no finite bar, so no coverage can be computed and no bias may be reported")
    sd = float(v.std(ddof=1))
    out = {"bias": float(v.mean() - truth), "bias_se": sd / math.sqrt(v.size), "sd": sd,
           "coverage": float(np.mean(np.abs(v[ok] - truth) <= b[ok])), "n": int(v.size),
           "n_with_bar": int(ok.sum()), "median_bar": float(np.median(b[ok]))}
    for k in ("bias", "bias_se", "sd", "coverage", "median_bar"):
        if not math.isfinite(out[k]):
            raise BiasRefused(f"{k} is not finite ({out[k]}), so nothing here may be printed")
    # A ZERO SCATTER IS A FACT AT THE NOISELESS RUNG, NOT A REFUSAL. The first draft of this module
    # raised here, which would have made it useless for exactly the rung every ladder requires FIRST:
    # at zero noise the realisations of one truth are identical by construction, so the standard error
    # is zero and there is nothing wrong with the run. Refusing would have pushed every noiseless bias
    # back out to whatever each harness printed by hand, which is the state this module replaces.
    # `deterministic` is returned so a caller can say so instead of quoting a zero as a measurement.
    out["deterministic"] = out["sd"] == 0.0
    return out


def format_bias(stats: dict, unit: str = "") -> str:
    """The bias and its standard error as one cell, the value carried to the error's own decimals.

    A DETERMINISTIC RUN IS SAID, NEVER DRESSED AS A MEASUREMENT. `pmfmt` formats an uncertainty by its
    two significant digits, and zero has none, so a zero standard error is reported in words rather
    than as "+- 0.0" -- which a reader would take for a bar that had been measured and found tiny.
    """
    tail = f" {unit}" if unit else ""
    if stats.get("deterministic") or stats["bias_se"] == 0.0:
        return f"{stats['bias']:+.6g} exactly{tail} (no scatter across {stats['n']} realisations)"
    val, err = pmfmt.pm_cells(stats["bias"], stats["bias_se"])
    return f"{val} +- {err}{tail}"


def report_bias(label: str, values, truth: float, bars, unit: str = "", printer=print) -> dict:
    """Print a bias with its standard error and its coverage, or raise rather than print.

    Returns the statistics so a producer writes the same numbers it printed, rather than recomputing
    them at a different precision -- which is the "re-derive a summarising claim" defect in miniature.
    """
    s = bias_with_coverage(values, truth, bars)
    scatter = "0 exactly" if s["deterministic"] else pmfmt.fmt_err(s["sd"])
    printer(f"  {label}: bias {format_bias(s, unit)}, scatter {scatter}, "
            f"median bar {pmfmt.fmt_err(s['median_bar'])}, "
            f"coverage {s['coverage']:.2f} over {s['n_with_bar']} of {s['n']}")
    return s


def _self_test() -> int:
    """Planted both ways on every refusal, and on the FORMATTING contract that O35 asks for."""
    fails = []
    rng = np.random.default_rng(7)
    v = 42.0 + 0.6094 + rng.normal(0, 0.5, 40)
    b = np.full(40, 1.0)

    def refuses(what, *a, **k):
        try:
            bias_with_coverage(*a, **k)
        except BiasRefused:
            return True
        fails.append(f"no refusal for {what}")
        return False

    refuses("one realisation", [1.0], 0.0, [1.0])
    refuses("a NaN among the values", [1.0, float("nan"), 3.0], 0.0, [1.0, 1.0, 1.0])
    refuses("no finite bar", [1.0, 2.0], 0.0, [float("nan"), float("inf")])
    refuses("a bar per nothing", [1.0, 2.0, 3.0], 0.0, [1.0, 1.0])
    # AND THE NOISELESS RUNG MUST REPORT, NOT REFUSE (F226): identical realisations are what zero
    # noise produces, and the first draft raised here, which made this module useless for rung one.
    det = bias_with_coverage([2.0, 2.0, 2.0], 2.0, [1.0, 1.0, 1.0])
    if not det["deterministic"] or det["bias_se"] != 0.0 or det["bias"] != 0.0:
        fails.append(f"the noiseless case did not report as deterministic: {det}")
    if "exactly" not in format_bias(det):
        fails.append("a zero standard error was dressed as a measured bar instead of said in words")

    s = bias_with_coverage(v, 42.0, b)          # the positive case must NOT raise
    if not (0.0 <= s["coverage"] <= 1.0):
        fails.append(f"coverage outside [0, 1]: {s['coverage']}")
    if abs(s["bias_se"] - s["sd"] / math.sqrt(s["n"])) > 1e-12:
        fails.append("the standard error is not the scatter over root n")

    # O35'S OWN CONTRACT, which is the reason this module exists: two significant digits on the
    # uncertainty and the value carried to ITS decimals. 0.6094 +- 0.1372 reads "+0.61 +- 0.14".
    got = format_bias({"bias": 0.6094, "bias_se": 0.1372})
    if got != "0.61 +- 0.14":
        fails.append(f"format_bias gave {got!r}, not '0.61 +- 0.14'")
    got2 = format_bias({"bias": -0.00066, "bias_se": 0.000123})
    if "0.00012" not in got2:
        fails.append(f"a small uncertainty lost its two digits: {got2!r}")

    # AND IT MUST RAISE RATHER THAN PRINT: a refusal that prints first has not refused.
    printed = []
    try:
        report_bias("planted", [1.0], 0.0, [1.0], printer=printed.append)
    except BiasRefused:
        pass
    if printed:
        fails.append(f"report_bias printed before refusing: {printed}")

    for f in fails:
        print("FAIL:", f)
    print("report_bias self-test:", "FAIL" if fails else
          "PASS (five refusals fire, the positive case reports, the two-digit contract holds, "
          "and a refusal prints nothing)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(_self_test())
