"""The words a reader sees in a markdown source: one predicate for the guards that count them (V7.1).

A binding writes a number as a link whose title carries its reference, `[0.0089](path "ref:...")`, which is two
whitespace tokens where the bare number was one, and neither the path nor the title reaches a reader. Guards that
counted the raw source therefore charged every binding a word: the walls ratchet went red on three front-path pages
when the SSOT pass bound their numbers, with no sentence made longer. Counted through this, a link is its text alone.
A title may hold parentheses (a `ref:expr:` carries arithmetic), so a quoted title is skipped whole."""
import re

_LINK_TARGET = re.compile(r"\]\((?:[^()\"\n]|\"[^\"\n]*\")*\)")
#: an HTML comment is never rendered: the tags the moved-value scan asks for (`<!-- other-quantity: ... -->`) are
#: machine markers, and counting them as words made the act of tagging a coincidence grow a front page
_COMMENT = re.compile(r"<!--.*?-->", re.S)


def reader_text(text: str) -> str:
    """`text` as a reader meets it: every markdown link's target and title removed with its bracketed text kept,
    and every HTML comment removed."""
    return _LINK_TARGET.sub("]", _COMMENT.sub(" ", text))
