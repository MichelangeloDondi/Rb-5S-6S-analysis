"""Property sentences stay with the result that owns them.

The defect class this guards, with four real instances behind it: a
sentence describing ONE result's property gets attached to a DIFFERENT
result's number. The two results involved are the S0 width-only sweep
bound (C3d, 0.63 MHz), whose construction takes no waist input and
carries the over-dispersion-widened threshold, and the joint
three-session bound (C3f, 0.26 MHz), which fits full profiles at the
unscaled 2.706 threshold and depends on the waist weakly through the
transit kernel in its lineshape.

Both directions have occurred in the prose: the over-dispersion
widening attributed to C3f, and the joint bound described as
"waist-free" or as using only the width-versus-power data. The wording
wraps across the 72-column line breaks, which defeated hand fixes and
is why this test collapses whitespace before matching anything.

Scope is the paragraph, bullet or table row, not a character window:
the CLAIMS instance spans two sentences inside one bullet, while
RESULTS legitimately describes both constructions in adjacent bullets
that must not bleed into each other. A block that names the foreign
result next to a property phrase passes only if it carries an explicit
disclaimer (the corrective sentence in RESULTS C3f is the licensed
case).
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Known deferral: the archive README's S0 table row still carries the
# widening wording and is corrected there separately. The mirror's row
# is already correct, so this entry never fires here. Remove it once
# the archive row is fixed.
DEFERRED = [
    ("README.md", "joint three-session profile likelihood with the threshold widened"),
]

DOCS = [
    "README.md",
    "docs/CLAIMS.md",
    "docs/BIG_PICTURE.md",
    "docs/RESULTS.md",
    "docs/PLAN.md",
]

# (property phrases, owner tokens, foreign tokens). A block containing a
# property phrase must contain at least one owner token, and if it also
# contains a foreign token it must carry a disclaimer.
RULES = [
    (
        [r"waist[- ]free",
         r"does not depend on the waist",
         r"no w.?0 enters",
         r"only the width[- ](?:versus|against)[- ]power data"],
        [r"0\.63", r"width[- ]only", r"C3d", r"power lever"],
        [r"0\.26", r"joint", r"three[- ]session", r"C3f"],
    ),
    (
        [r"over[- ]dispersion[- ]widen",
         r"widened for (?:the )?(?:block[- ]to[- ]block )?over[- ]dispersion",
         r"threshold widened"],
        [r"0\.63", r"width[- ]only", r"C3d", r"power lever"],
        [r"0\.26", r"joint", r"three[- ]session", r"C3f"],
    ),
    (
        [r"unscaled 2\.706"],
        [r"0\.26", r"joint", r"three[- ]session", r"C3f"],
        [r"0\.63", r"width[- ]only", r"C3d"],
    ),
]

DISCLAIMER = re.compile(
    r"belongs to|not to this|misattribution|corrects|rather than the joint"
    r"|correctly attributed",
    re.I,
)


def _blocks(path):
    """Whitespace-normalized paragraph/bullet/table-row blocks."""
    text = (ROOT / path).read_text()
    rough = re.split(r"\n\s*\n|\n(?=[-*] )|\n(?=\|)", text)
    return [re.sub(r"\s+", " ", b).strip() for b in rough if b.strip()]


def _hits(block, patterns):
    return [p for p in patterns if re.search(p, block, re.I)]


@pytest.mark.parametrize("doc", DOCS)
def test_property_phrases_stay_with_their_owning_result(doc):
    if not (ROOT / doc).exists():
        pytest.skip(f"{doc} absent in this tree")
    offenders = []
    for block in _blocks(doc):
        for phrases, owners, foreigners in RULES:
            hit = _hits(block, phrases)
            if not hit:
                continue
            owned = bool(_hits(block, owners))
            foreign = bool(_hits(block, foreigners))
            excused = bool(DISCLAIMER.search(block))
            deferred = any(d == doc and sig in block for d, sig in DEFERRED)
            # A block that names the owning result licenses the phrase.
            # The offense is a property phrase in a block that names ONLY
            # the foreign result, with no disclaimer and no recorded
            # deferral.
            if foreign and not owned and not excused and not deferred:
                offenders.append((hit[0], block[:120]))
    assert not offenders, (
        f"{doc}: property phrase next to the wrong result, no disclaimer: "
        + "; ".join(f"[{p}] ...{b}..." for p, b in offenders)
    )
