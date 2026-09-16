"""The THEORY self-broadening coefficient of the 5S-6S line, with its budget.

WHY THIS FILE EXISTS. Until 2026-09-15 the theory value of beta_self lived in
`rb5s6s.vanderwaals` and in prose, and nowhere in `results/`. Three surfaces
quoted it and they had drifted to three different pairs -- 3.35 with a 0.29
bar on one page, 3.35 with a 0.37 bar on another, 3.5 in a memory -- because
nothing resolved a quoted number against a committed cell. That is the exact
shape the `ref:` mechanism exists to close, and it could not be used while the
number had no cell to point at. Every surface now cites this file by key, so a
re-run that moves the value fails each stale quoting site BY NAME.

WHAT IT COMPUTES, and the two steps that were one wrong step before:

  * `vanderwaals.beta_self_anchored` takes Zameroski's measured 7S rate, the
    only measured nS self-broadening rate in rubidium, converts it to a rate
    per DENSITY at HIS OWN cell temperature (393 K, his table-note), carries it
    to this record's 403.15 K by the T^0.3 the impact width's <v^(3/5)> gives,
    and scales it to 6S through the ratio of pair-coefficient DIFFERENCES,
    which is the part a truncated sum does well.
  * `vanderwaals.beta_self_budget` then moves each input in turn and reads the
    fractional move in beta, so every row of the budget is measured and none is
    an exponent typed into a comment.

THE HEADLINE THE BUDGET RETURNS: the coefficient is known as well as that one
measurement is and no better. Zameroski's own bar is 8.5 per cent of the value;
every term of the recipe together is 2.0 per cent in quadrature, which moves the
total from 8.5 to 8.8.

WHAT A READER MUST NOT TAKE FROM IT. The anchor divides out the recipe's
absolute scale error on the ASSUMPTION it is common to 6S and 7S. That error is
measured, once, on 7S, at +6.1 per cent; whether it carries an n-dependence has
no second measurement anywhere in the literature, and this file records it as
an open term rather than absorbing it into a bar.

Re-run: `python scripts/run_beta_self_theory.py` (about a second, no data).
"""
from __future__ import annotations

import csv
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _producer_lock import take_producer_lock  # noqa: E402
from rb5s6s import config as _CFG  # noqa: E402
from rb5s6s import vanderwaals as V  # noqa: E402


def cells(value, err):
    """The committed pair: the VALUE at full precision, the BAR at two digits.

    LANGUAGE 8a.2 is a PROSE convention -- two significant digits on an
    uncertainty, the value matching its decimals -- and applying it to a
    committed cell broke the SSOT edge on 2026-09-16:
    `tests/test_vanderwaals.py::test_the_committed_theory_row_matches_the_module`
    exists to assert this file against the module "which is what a stale quote
    resolves through", and a value rounded to 3.50 stopped equalling the
    module's 3.4971763. A reader resolving the ref: key got a number the package
    no longer returns, which is the staleness the citation mechanism exists to
    make impossible.

    So BOTH cells carry what a consumer needs and the PROSE rounds at the point
    of quotation, where `pm_cells` belongs. The bar is not exempt: the same test
    resolves through `err` as through `value`, and a carve-out for it was wrong
    for exactly the reason the carve-out for the value was.
    """
    return repr(float(value)), repr(float(err))

T_REF = 403.15          # 130 C, the temperature every theory row here is quoted at
T_COLD = 343.15         # 70 C, the cold end of the archive's temperature arm


def main() -> int:
    take_producer_lock("run_beta_self_theory")
    a = V.beta_self_anchored(T_REF)
    b = V.beta_self_budget(T_REF)

    rows: list[dict] = []

    def add(case, quantity, value, err, unit, basis, note, status):
        rows.append(dict(case=case, quantity=quantity, value=value, err=err,
                         unit=unit, basis=basis, note=note, status=status))

    unit_k = "kHz per 1e12 cm^-3 at 403.15 K"
    add("beta_self_6s", "anchored", *cells(b["beta6_khz"], b["err_khz"]), unit_k,
        "Zameroski's measured 7S rate carried to 6S by the ratio of pair-coefficient "
        "differences and of exchange-branch factors",
        "THE ADOPTED VALUE. Quoted in prose as 3.50 +- 0.37 under LANGUAGE 8a.2, two "
        "significant digits on the bar with the value matching its decimals",
        "ENVELOPE")
    add("beta_self_6s", "first_principles", f"{a['beta6_first_principles_khz']:.4f}", "", unit_k,
        "the Lindholm-Foley impact width run directly on the 6S pair coefficient",
        "an independent route, not an independent bar: it carries the recipe's own "
        "absolute scale, which the anchored row divides out. It sits "
        f"{(a['beta6_first_principles_khz'] - b['beta6_khz']) / b['err_khz']:.2f} of the "
        "adopted bar above it, which is the consistency and not a second measurement",
        "ENVELOPE")
    add("beta_self_6s", "rel_uncertainty", f"{100 * b['rel']:.2f}", "", "per cent",
        "the quadrature sum of the measured budget rows below",
        "8.8 per cent, of which 8.5 is the anchor measurement alone",
        "ENVELOPE")
    add("beta_self_6s_mhz", "anchored", *cells(b["beta6_khz"] / 1e3, b["err_khz"] / 1e3),
        "MHz per 1e12 cm^-3 at 403.15 K",
        "the same number in the estimator's own units",
        "what `rb5s6s.beta.fit_beta_self` returns and what `results/beta_self.csv` "
        "is compared against. The archive's fits sit 3.9 to 5.5 times above it",
        "ENVELOPE")

    add("beta_self_7s", "measured", f"{a['beta7_measured_khz']:.4f}",
        f"{a['beta6_err_khz'] / (b['beta6_khz'] / a['beta7_measured_khz']):.2f}", unit_k,
        "Zameroski 2014, 129 +- 13 kHz/mTorr (TABLE 3, the total), converted at the "
        "slope's effective temperature and carried to 403.15 K by T^0.3",
        "the anchor. The only measured nS self-broadening rate in rubidium",
        "CALIB")
    add("beta_self_7s", "predicted", f"{a['beta7_predicted_khz']:.4f}", "", unit_k,
        "the same recipe run on the 7S pair coefficient",
        "the one place the recipe can be graded against an experiment",
        "ENVELOPE")
    add("beta_self_7s", "recipe_scale_error", f"{100 * b['recipe_scale_error_on_7s']:.2f}", "", "per cent",
        "predicted over measured, minus one, both at 403.15 K",
        "0.72 of the measurement's own bar. The anchor divides this out "
        "assuming it is common to 6S and 7S, and its n-dependence is the budget's first open term",
        "ENVELOPE")

    for key, frac in sorted(b["terms_rel"].items(), key=lambda kv: -kv[1]):
        add("budget", key, f"{100 * frac:.2f}", "", "per cent",
            "measured by displacing that one input and reading beta",
            "a row of the quadrature. See `vanderwaals.beta_self_budget` for what each "
            "displacement is and why it enters where it does",
            "ENVELOPE")
    add("budget", "retracted_double_count_claim", "5.00", "", "per cent",
        "Zameroski's 5 per cent vapour-pressure(density) uncertainty",
        "RETRACTED the same day it was written. This record removed the term as a "
        "double count on 2026-09-15, reading his section 2.5 as putting it inside the "
        "+-11. It is not inside it: section 2.5 quotes 129 +- 11 and TABLE 3 quotes "
        "129 +- 13, and sqrt(11^2 + 6.45^2 + 1.29^2) = 12.8 closes on the paper's own "
        "recipe, so the 5 per cent is the DIFFERENCE between the two bars. The source's "
        "total is adopted and the row is kept so the deletion cannot return",
        "ARTIFACT")

    # WHAT HIS BAR WOULD BE READ AS ONE SIGMA, recorded and NOT adopted.
    # RE-DERIVED 2026-09-15 after the +-11 was found to be the fit interval
    # alone and the +-13 the total. The composition the paper states is a 95 per
    # cent linear-fit interval, a 1 per cent transducer calibration and a 5 per
    # cent vapour-pressure term, in quadrature; solving the TOTAL for the fit
    # half gives sqrt(13^2 - 6.45^2 - 1.29^2) = 11.2, which is the +-11 section
    # 2.5 prints, so the paper's two bars are internally consistent and the fit
    # half is known. Dividing it by the t-factor of a fit over a handful of
    # pressures leaves a one-sigma total between 6.6 and 8.0 per cent of 129.
    # Carrying the +-13 whole is therefore conservative by about 1.3x, and it is
    # carried whole because the division needs degrees of freedom the paper does
    # not give and a bar a reader cannot rebuild from the source is worse than
    # one that is wide.
    fit95 = math.sqrt(max((V.ZAMEROSKI_7S_BROADENING_ERR
                           / V.ZAMEROSKI_7S_BROADENING_KHZ_PER_MTORR) ** 2
                          - 0.01 ** 2 - 0.05 ** 2, 1e-12))
    for lab, t in (("gaussian_1.96", 1.96), ("t_dof6_2.45", 2.447), ("t_dof3_3.18", 3.182)):
        add("anchor_bar_one_sigma", lab,
            f"{100 * math.sqrt((fit95 / t) ** 2 + 0.01 ** 2 + 0.05 ** 2):.2f}", "", "per cent",
            "the paper's stated composition solved for the fit half and divided by that "
            "t-factor",
            "NOT ADOPTED. Recorded so the size of the conservatism is known: the adopted "
            "bar carries his 10.08 per cent whole", "DIAGNOSTIC")
    add("anchor_bar_one_sigma", "fit_half_95pc", f"{100 * fit95:.2f}", "", "per cent",
        "sqrt(13^2 - 6.45^2 - 1.29^2) over 129, the TOTAL with the two systematics removed",
        "it reproduces the 11.2 per cent section 2.5 prints as +-11, which is how the two "
        "bars are known to be the fit interval and the total rather than two readings of "
        "one thing", "CALIB")

    add("anchor", "effective_temperature_k", f"{a['zameroski_eff_t_k']:.1f}",
        f"{(V.zameroski_effective_T('unit') - V.zameroski_effective_T('inv_p2')) / 2:.0f}", "K",
        "the rate is a SLOPE fitted over 353 to 438 K (figure 7 caption), not a rate at one "
        "temperature. A point's influence on a SLOPE is its regression leverage w(P-Pbar) "
        "and not its weight, and the Rb pressure is exponential in T, so the hot end "
        "carries it whatever the weighting: 402 to 429 K across the defensible families",
        "the 393 K this record carried for one afternoon is Table 4's note, giving the "
        "self-broadening contribution to a different experiment at that experiment's "
        "temperature. Retracted the same day it was written",
        "ENVELOPE")
    add("anchor", "t_factor_to_403k", f"{a['t_factor']:.6f}", "", "dimensionless",
        "(403.15/393)^0.3, and the 0.3 is measured on `beta_self_vdw` to six digits",
        "the second of the two steps, and the one that was missing entirely",
        "CALIB")

    for k, lab in (("c6_5s5s_au", "c6_5s_5s"), ("c6_5s6s_au", "c6_5s_6s"),
                   ("c6_5s7s_au", "c6_5s_7s")):
        add("pair_coefficients", lab, f"{a[k]:.3f}", "", "a.u.",
            "this module's direct sum over the tabulated matrix elements",
            "the ratio of DIFFERENCES against the ground pair is what the anchor uses, and "
            "swapping the ground pair for the literature 4691 a.u. moves beta by 0.28 per cent",
            "CALIB")

    # THE CONVENTION COST THE ESTIMATOR PAYS, recorded here because establishing the
    # T^0.3 law is what makes it computable and no other file would carry it.
    spread = (T_REF / T_COLD) ** 0.3 - 1.0
    add("estimator_convention", "t_independence_cost_70_to_130c", f"{100 * spread:.2f}", "", "per cent",
        "(403.15/343.15)^0.3 - 1",
        "`rb5s6s.beta` regresses gamma_coll on N(T) with ONE beta across 70 to 130 C, "
        "so it treats the coefficient as temperature-independent while the impact width "
        "goes as T^0.3. That is 4.9 per cent of model form on the fitted coefficient, "
        "small against the 3.9-5.5x the fits sit above theory but not zero, and it is "
        "not in any bar the fits quote",
        "ENVELOPE")

    dest = os.path.join(str(_CFG.RESULTS_DIR), "beta_self_theory.csv")
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {dest} with {len(rows)} rows")
    print(f"  beta_self(6S) = {b['beta6_khz']:.2f} +- {b['err_khz']:.2f} "
          f"kHz per 1e12 cm^-3 at 130 C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
