#!/usr/bin/env python
"""B2: the orthogonal levers, as roles in an information geometry.

WHY THIS IS NOT A RANKING. An earlier framing scored three candidate levers
against each other and picked a winner. That framing is wrong about the
problem. Spectroscopy measures the INTEGRATED homogeneous response, and the
components of that response add exactly, so no single lever recovers the
budget: each supplies one coordinate while the others are held fixed. They are
COMPLEMENTS. In particular K5's attribution triangle needs the independent
laser diagnostic no matter which spectroscopic lever is chosen, so a ranking
that put the laser diagnostic third would have licensed skipping the one
measurement that closes the attribution.

WHAT EACH ROW MUST CARRY. A lever is only a lever if it moves one term while
leaving the others alone, so the useful columns are what it SEPARATES, its
ROLE, and — the column that stops this table from being wishful — the
ASSUMPTION its orthogonality rests on.

THE TEMPERATURE ROW IS THE REASON THE ASSUMPTION COLUMN EXISTS. Changing the
cell temperature is INTENDED to move the transit term while leaving the laser
contribution invariant. Temperature also moves density, optical depth,
absorption, thermal gradients, alignment drift, background, and the collision
rate. Treating the desired orthogonality as if it were given is exactly the
error this table exists to prevent, so the row states the intent as an intent
and names the controls a campaign would need.

NOTHING HERE IS A MEASUREMENT. Every row is a design statement about what a
configuration would separate, which is why the whole file carries DIAGNOSTIC.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402

OUT = C.RESULTS_DIR / "orthogonal_levers.csv"


def main() -> int:
    rows = []

    def add(lever, separates, role, assumption, evidence_class, note):
        rows.append(dict(lever=lever, separates=separates, role=role,
                         assumption=assumption, evidence_class=evidence_class,
                         note=note))

    add("density n",
        "gamma_coll from every term that does not scale with density",
        "the identifying coordinate the taken campaign already varied; it is "
        "what makes beta_self a measurable slope rather than a floor",
        "that the vapour-pressure density scale is correct, and that changing "
        "density does not change the laser or the transit term",
        "DEMONSTRATED",
        "this lever is the one the archive actually used; the others are "
        "PROSPECTIVE")

    add("temperature T",
        "Gamma_transit from the temperature-independent homogeneous terms",
        "the fibre platform's only spectroscopic lever, since transit is "
        "Lorentzian with FWHM v/(pi*Lambda) and so enters the same additive "
        "degeneracy as everything else",
        "INTENDED, NOT ESTABLISHED: that temperature moves transit while the "
        "laser contribution stays approximately invariant. Temperature also "
        "moves density, optical depth, absorption, thermal gradients, "
        "alignment and background. A campaign using this lever REQUIRES "
        "controls that validate the invariance. On the decay length, a "
        "stronger claim was drafted on 2026-08-22 and then WITHDRAWN by the "
        "twin that tested it: the raw magnitudes look alarming, since over the "
        "plausible Lambda band the ladder span is 161 to 297 kHz while the "
        "edge-to-edge ambiguity at the top rung is 214 kHz, and that was read "
        "as an unpinned Lambda consuming the lever. It does not. Gamma_L is "
        "temperature-INDEPENDENT while transit follows a known SHAPE, so a "
        "ladder fitting the intercept and the Lambda scale together separates "
        "them by shape rather than by magnitude, and results/fibre_twin.csv "
        "reaches 0.978 and 0.966 coverage at the two band edges with Lambda "
        "unpinned. Pinning Lambda independently is a REFINEMENT that returns a "
        "degree of freedom, not a precondition",
        "PROSPECTIVE",
        "in a vapour cell temperature and density are not independent at all, "
        "which is why this lever belongs to the fibre")

    add("independent laser diagnostic",
        "Gamma_L from the rest of the homogeneous budget, directly",
        "the leg K5's attribution triangle is missing; NO spectroscopic lever "
        "substitutes for it, which is why this table is not a ranking",
        "that the diagnostic integrates noise over the same band the scanned "
        "width does. The one in-situ measurement held samples a different "
        "band and is why attribution stays refused",
        "PROSPECTIVE",
        "without this row the identified component keeps its name "
        "Gamma_L,equiv and never becomes the laser")

    add("guided geometry (fibre)",
        "the spatial interaction length, and with it transit, from the bulk "
        "collisional response",
        "changes the interaction volume rather than a rate, so it moves terms "
        "no cell temperature or density can reach",
        "that the guided mode's light-shift distribution is characterised, "
        "and that the decay length is either pinned or fitted as a scale "
        "alongside the intercept, which the twin shows suffices; "
        "otherwise a new inhomogeneous term is added while an old one is "
        "being separated, and the transit calibration is ambiguous at the "
        "size of the lever itself",
        "PROSPECTIVE",
        "adds capability and adds systematics; both belong in the same row")

    add("differential operation",
        "common-mode drift from the physics, rather than one width from "
        "another",
        "not a component lever at all: it protects every other lever's "
        "measurement from the drift that made line POSITIONS uninformative "
        "in the taken campaign",
        "that the two arms share the drift being rejected",
        "PROSPECTIVE",
        "listed because omitting it implies the other levers work in the "
        "presence of arbitrary drift, and the archive is evidence they do not")

    with OUT.open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"wrote {OUT} with {len(rows)} levers")
    for r in rows:
        print(f"  {r['lever']:<30} {r['evidence_class']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
