"""THE WINDOW SETS, DEFINED ONCE (owner, 2026-09-19: "Solve the SSOT issue once for all").

WHY THIS MODULE EXISTS. On 2026-09-19 the half-widths at which this record takes its windowed moments
were defined in FOUR places that nothing bound together: `fullmodel.DEFAULT_WINDOWS`,
`run_cross_arm_ratios.WINDOWS`, `run_moment_power_map.WINDOW` and `run_ultra_joint.MOMENT_WINDOWS`. Three of
them still carried the set the joint vector had already left. That is the SSOT defect in its plainest form:
a quantity of the analysis, copied, with no route from one copy to another, so a change lands on whichever
copy the hand happened to be on.

THE SETS, AND WHAT EACH IS FOR.

`QUOTED` is the joint vector's own: the half-widths whose moments enter the likelihood and are quoted.
Chosen on the measured per-trace signal-to-noise at the archive's own noise law (the wave of 2026-09-19),
and re-chosen only on a measurement, never on taste.

`DIAGNOSTIC` is computed and written with `admitted=False` and a reason. Its members are where a statistic
is known to be at its worst -- an order passing through zero, where its cancellation conditioning collapses
(`docs/methods/11_the_window_limits.md` section 11.6) -- and they are kept precisely to SHOW that, so a
reader can see the channel die rather than take the choice on trust.

`SURFACE` is the window-surface grid, wider than either, because the surface exists to let the choice be
re-read and the limits of section 11 to be fitted.

`LEGACY` is the set this record quoted until 2026-09-19. It is NOT retired as a number -- a committed row
and a published figure at those half-widths are history and stay exactly as they are, and the repeats
reference the twin's spread is graded against is measured there (F150). It is retired as a DEFAULT: no new
analysis takes its windows from here, and `rb5s6s.windows.LEGACY` is the only name that may spell it, so a
producer that wants it says so in one token that a reader can grep.

THE RULE, and it is the mechanism: **no module outside this one writes a window half-width as a literal.**
`private/checks/window_ssot.py` scans the package and `scripts/` for a tuple of window-shaped literals and
refuses one that is not this module's, which is what makes the single source single. Planted both ways.
"""
from __future__ import annotations

#: the joint vector's half-widths, MHz. Every moment quoted by the MLE is taken here.
QUOTED: tuple[float, ...] = (1.0, 2.0, 5.0, 13.0)

#: computed, written with a reason, never quoted: the windows where an order is at or near its own zero.
DIAGNOSTIC: tuple[float, ...] = (3.0, 8.0, 21.0)

#: the window surface's grid: every quoted and diagnostic member, plus the ends the limits need.
SURFACE: tuple[float, ...] = (0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0)

#: the set quoted until 2026-09-19, kept for the historical producers and the repeats reference alone.
LEGACY: tuple[float, ...] = (3.25, 6.0, 12.0)

#: the orders the record takes at every window.
ORDERS: tuple[int, ...] = (2, 3, 4, 5, 6, 7)


def all_windows() -> tuple[float, ...]:
    """Every half-width the record computes at, sorted: what a surface must span to serve them all."""
    return tuple(sorted(set(QUOTED) | set(DIAGNOSTIC) | set(SURFACE)))


def role_of(window: float) -> str:
    """`quoted`, `diagnostic`, `surface` or `legacy` for a half-width, so a row can name its own role."""
    w = float(window)
    if w in QUOTED:
        return "quoted"
    if w in DIAGNOSTIC:
        return "diagnostic"
    if w in LEGACY:
        return "legacy"
    if w in SURFACE:
        return "surface"
    return "unregistered"
