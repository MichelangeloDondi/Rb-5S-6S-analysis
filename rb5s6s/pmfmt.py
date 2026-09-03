"""One place for the value-uncertainty cell format (LANGUAGE 8a.2).

The rule: a Gaussian uncertainty carries exactly two significant digits
and the value is rounded to the same decimal place, so the pair reads
as one statement. Before this module, three producers held three
re-implementations, and the third lacked the decade handling the first
had been guarded for: the audit that found it counted 397 of 544 err
cells across the committed results falling short of the significant-digit
rule alone (the ratchet's own checker, adding the decimal match and the
zero cells, seeds higher over the same corpus). CSV-writing
producers converge here as their formatters are touched; the figure
renderer's display form (the ``pm`` function in ``scripts/make_figures.py``, which may divide by
the uncertainty's decade for plot text) shares the rule and its own
20000-pair guard, and is deliberately not merged here because its
output contract is figure text, not a CSV cell.

Failure mode this guards against: a fixed ``:.2f`` printing one
significant digit for an uncertainty like 0.03, or four for 24.09.

OUT-OF-BAND MAGNITUDES: LANGUAGE 8a.2a already specifies the cure when
plain decimal stops working in either direction, the decade factored
out of both numbers ((2.6 +/- 3.4) x 10^-5; (-70.0 +/- 2.6) x 10^3),
and the figure renderer's ``pm`` implements it. Committed err cells
outside the plain band exist (an audit named 415 +/- 315 in the
delta-alpha posterior and 311.8 +/- 130 in the scenario forecast,
with twenty-two chi-square values parked in err columns besides).
The audited out-of-band set also includes the too-small side, eight
cells across the coverage and wing-check files near one part in ten
thousand, the failure mode the protocol records as the costly one.
This module does NOT yet emit a factored CSV-cell form, because the
two-column cell convention for it is an open design decision; until
that lands, ``in_plain_band`` below exposes 8a.2a's threshold so the
err-format ratchet counts out-of-band plain cells as nonconforming
rather than blessing them. Today every out-of-band committed cell
also fails the digit check, so the band's live marginal count is
zero; it exists for the cell whose digits conform while its
magnitude does not, which the ratchet's plant holds.
"""
from __future__ import annotations

import math


def fmt_err(e: float) -> str:
    """Two significant digits on a positive uncertainty, carry included.

    Rounding can push the leading digit across a decade (0.0999 prints
    as 0.100 at three decimals, three digits), so after formatting once
    the decade is recomputed from the ROUNDED value and the format
    re-run when it moved. The figure renderer's guard hit this case in
    its 20000 random pairs; the first CSV port of this function did
    not, and an audit's probe (1.0 +/- 0.0999) found it.
    """
    if not (e > 0) or not math.isfinite(e):
        return ""
    exp = int(math.floor(math.log10(e)))
    digits = max(0, 1 - exp)
    # round to two significant digits BEFORE formatting: above 100 the
    # format alone prints every integer digit of the raw value (131.5
    # gave 132, three digits, where the rule says 130) -- found when the
    # third producer's convergence moved one committed cell
    out = f"{round(e, 1 - exp):.{digits}f}"
    rounded = float(out)
    if rounded > 0:
        digits2 = max(0, 1 - int(math.floor(math.log10(rounded))))
        if digits2 != digits:
            out = f"{e:.{digits2}f}"
    return out


def pm_cells(v: float, e: float) -> tuple[str, str]:
    """(value, err) cell strings, the value matching the err's decimals.

    With no usable uncertainty the value keeps two decimals and the err
    cell is empty, which is how the committed results mark an errless
    quantity.
    """
    es = fmt_err(e)
    if not es:
        return f"{v:.2f}", ""
    dec = len(es.split(".")[1]) if "." in es else 0
    return f"{v:.{dec}f}", es


def in_plain_band(v: float, e: float) -> bool:
    """8a.2a's plain-decimal band: plain while the larger of the two
    magnitudes stays at or above 1e-3 and the PRINTED uncertainty is
    unambiguous. The ambiguity test reads the rounded form, not the
    raw one, for the same reason fmt_err rounds before formatting:
    99.5 prints as 100, three ambiguous digits."""
    if not (e > 0) or not math.isfinite(e):
        return True
    if max(abs(v), e) < 1e-3:
        return False
    printed = fmt_err(e)
    try:
        return float(printed) < 100
    except ValueError:
        return True

