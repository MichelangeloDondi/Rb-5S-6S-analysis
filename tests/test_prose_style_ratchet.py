"""A ratchet on two punctuation marks the house style does not use.

Why a ratchet and not a ban. The style rule is that where a sentence wants an
em-dash or a semicolon, it should end and the next should begin. The corpus
began with 3063 of them across 112 files, so a hard ban would have failed on
the first run and been switched off on the second. A guard that cannot pass is
not a guard.

So this records a per-file budget and fails only when a file gets WORSE. Every
cleanup pass lowers a number and locks the gain in. The budget can only fall,
never rise, which is the whole point: it makes the repository monotonically
more readable without demanding one enormous rewrite first.

Lowering the numbers is the work, not a chore to be automated around. Run
`python tests/test_prose_style_ratchet.py --relax` after a genuine cleanup to
re-record the improved counts. Raising a budget by hand means admitting that a
file got worse, which should feel like what it is.

Scope. Tracked Markdown only. Generated files are excluded because their prose
lives in the generator, so editing the output is pointless; fix the generator
and the output follows. Code fences, tables and display maths are stripped
before counting, because a semicolon in a code sample is not a style problem.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).parent / "_style_baseline.json"

# Generated: their prose lives in the generators, not in the output.
#
# docs/RESULTS.md left this set on 2026-08-04. Being exempt meant the guard
# could not see the ledger at all, and the ledger is the second link on the
# README's first screen. Its generator now writes prose without either mark,
# so the file is held to the same budget as every hand-written document. The
# other two stay exempt until their generators get the same pass.
GENERATED = {
    "docs/LITERATURE_INDEX.md",
    "PDF_papers/README.md",
}


def _tracked_markdown() -> list[str]:
    """Markdown this commit would ship: tracked, PLUS untracked and not ignored.

    WHY THE SECOND HALF EXISTS. `git ls-files` lists TRACKED files only, so a
    brand new document is invisible here until it is staged. Write it, run the
    gate, watch it pass, then add and commit, and the ratchet never saw the
    file that shipped. That is exactly what happened on 2026-08-15: `0caf19a5`
    was reported green while adding `docs/HISTORY.md`, which has failed this
    guard from the moment it existed.

    `test_repo_hygiene._about_to_be_tracked` had solved this for its own
    guards two days earlier, on 2026-08-13, for the same reason. The remedy
    was written into one guard and not into its sibling, which is the defect
    class protocol rule 19.24 now states. A guard reads what is about to ship,
    not what already shipped.
    """
    tracked = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                             capture_output=True, text=True).stdout.split()
    new = subprocess.run(["git", "ls-files", "--others", "--exclude-standard",
                          "*.md"], cwd=ROOT, capture_output=True, text=True)
    untracked = new.stdout.split() if new.returncode == 0 else []
    return sorted(f for f in set(tracked) | set(untracked)
                  if f not in GENERATED)


def _prose(text: str) -> str:
    """Drop code fences, tables and display maths: only running prose counts.

    THE $$ FIX (2026-08-10). This used to skip only lines that START with $$,
    which drops the delimiters of a display block and keeps everything between
    them. A multi-line equation therefore had its interior counted as prose,
    and LaTeX argument separators were counted as semicolons: the composite
    line in methods/02 contributed four that no rewrite could remove without
    breaking the mathematics. $$ now toggles a mode the way ``` does, and a
    line carrying an odd number of them flips it.
    """
    kept, in_fence, in_math = [], False, False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        n_delim = line.count("$$")
        if n_delim:
            # a line with one $$ opens or closes; with two it is a whole
            # one-line display and is dropped either way
            if n_delim % 2:
                in_math = not in_math
            continue
        if in_fence or in_math or stripped.startswith("|"):
            continue
        kept.append(line)
    return "\n".join(kept)


def _count(path: Path) -> int:
    prose = _prose(path.read_text(encoding="utf-8"))
    return prose.count("—") + prose.count(";")


def _current() -> dict[str, int]:
    counts = {}
    for rel in _tracked_markdown():
        p = ROOT / rel
        if not p.exists():          # staged deletion
            continue
        n = _count(p)
        if n:
            counts[rel] = n
    return counts


def test_no_file_gains_splice_punctuation():
    """Em-dash and semicolon counts may fall or hold, never rise."""
    baseline = json.loads(BASELINE.read_text())
    current = _current()

    worse = []
    for rel, now in sorted(current.items()):
        was = baseline.get(rel)
        if was is None:
            worse.append(f"{rel}: NEW file with {now} (write it without them, "
                         f"or add it to the baseline with --relax)")
        elif now > was:
            worse.append(f"{rel}: {was} -> {now} (+{now - was})")

    assert not worse, (
        "prose style regressed. The house rule is no em-dashes and no "
        "semicolons in prose: end the sentence instead.\n  "
        + "\n  ".join(worse)
        + "\n\nIf a cleanup pass genuinely lowered other files, re-record with:"
          "\n  python tests/test_prose_style_ratchet.py --relax")


def test_the_baseline_itself_only_ever_shrinks():
    """The recorded budget must not drift above what the files actually need.

    Without this, --relax could be run on a dirty tree and silently bless a
    regression. Here the baseline is required to be tight: no entry may sit
    above its file's real count.
    """
    baseline = json.loads(BASELINE.read_text())
    current = _current()
    slack = {rel: (was, current.get(rel, 0))
             for rel, was in baseline.items() if was > current.get(rel, 0)}
    assert not slack, (
        "the baseline is looser than reality, which leaves room for silent "
        "regressions. Re-record it:\n  "
        + "\n  ".join(f"{r}: budget {w}, actual {c}" for r, (w, c) in sorted(slack.items()))
        + "\n  python tests/test_prose_style_ratchet.py --relax")


@pytest.mark.parametrize("phrase", [
    "it is worth noting",
    "it should be noted",
    "crucially,",
    "importantly,",
    "needless to say",
    "at the end of the day",
    # Added 2026-08-10, owner instruction, after measuring all of them against
    # the tree. EVERY phrase below was already at zero, which is why they can
    # be banned outright at no cost. The measurement is the point: of
    # forty-nine candidates tested, thirty-seven were already absent, five were
    # genuine filler and were removed in the same pass, and the rest turned out
    # to be technical usage and were KEPT. Those keepers are named in the
    # rendering protocol section 2.3 with the reason, because a word list that
    # bans "leverage" in a project with a density lever, or "underscore" in a
    # project whose filenames turn on one, would be worse than no list.
    "delve",
    "deep dive",
    "dive into",
    "shed light on",
    "sheds light on",
    "pave the way",
    "paves the way",
    "unleash",
    "harness the",
    "game-changer",
    "game changer",
    "showcase",
    "boasts",
    "seamless",
    "tapestry",
    "ever-evolving",
    "a testament to",
    "highlights the importance",
    "navigate the complexities",
    "at its core",
    "key takeaway",
    "empower",
    "meticulous",
    "utilize",
    "utilise",
    "myriad",
    "plethora",
    "when it comes to",
    "in conclusion",
    # Added 2026-08-26 on the experimenter's instruction, after he read a
    # release note and said it "sounds so much AI written". Measured the same
    # way the 2026-08-10 batch was: each of these is at ZERO across the tracked
    # corpus, which is what makes an outright ban free. "Comfortable" was the
    # word he named and it is NOT here, because it appears 32 times with a
    # legitimate margin sense ("750 Hz is comfortable against a 1 s scan")
    # beside the vague one. It gets the falling budget below instead, which is
    # how this file already treats "rather than".
    "compelling",
    "multifaceted",
    "rich tapestry",
    "in today's",
    "it's worth noting",
    "delving",
    "underscoring",
    "to summarize",
    "to summarise",
    "double-edged sword",
    "in the realm of",
    "cutting-edge",
    "in today's",
    "pivotal",
    # Added 2026-08-17, owner instruction: prose that narrates EDITING the
    # document rather than reporting the science. The same measurement rule as
    # the 2026-08-10 block above was applied, and it changed the answer twice.
    #
    # "reword" and its forms were NOT at zero: four markdown sites carried
    # them, three in the literature ledger and one in a big-picture chapter,
    # every one of them about a novelty claim losing scope. They were changed
    # to say NARROWED, which is both bannable-compatible and more accurate,
    # since a claim that lost scope did not merely change its words.
    #
    # KEPT DELIBERATELY, measured and rejected as candidates, for the reason
    # section 2.3 of the rendering protocol gives: "tighten" appears in
    # thirty-six files and is what one does to a bound or a focus, "polish" is
    # a derivative-free refinement step in the wavemeter reconstruction,
    # "rewrite" is what happens to a document when a preregistered condition
    # fires and to code that changed format, and "leverage" is a lever arm in
    # a project that has several. A list that banned those would be worse than
    # no list.
    "reword",
    "re-word",
    "rephrase",
    "rephrasing",
    "wordsmith",
    "redraft",
    "copy-edit",
    "copyedit",
    "streamline",
    # The assistant self-reference is NOT repeated here. The forbidden-phrase
    # bank in tests/test_repo_hygiene.py already owns that family, and adding
    # it here as a literal made THAT bank fail on this file, twice: once for
    # the entry and once for a comment explaining the entry. Two banks with
    # overlapping scope is a design to avoid, and this is the cheap version of
    # finding that out.
    "i have updated",
    "i\'ve updated",
    "let me know if",
    "hope this helps",
    "feel free to",
    # Banned on the experimenter's instruction: "adopted" misdescribes this
    # bench. The 64 um waist is Rajasree's measurement on the SAME optical
    # table, laser and lenses, and the cell temperature was instrumented with
    # four thermocouples between the cell and its metal case inside a
    # foil-wrapped cubic oven. Calling either "adopted" turns a measurement
    # into a convention someone chose. Replacements by sense: a measured
    # quantity is measured (name whose measurement), a fixed input is "of
    # record" or "in force", a prior is "assumed", a set point is a set
    # point, and a decision is "accepted".
    "adopted",
    "adopte",
    # Banned on the experimenter's instruction, same reading: each one
    # dresses a measurement as something else. A projection is not
    # "defeated", a condition breaks it. A range is not "snug", it is
    # tight. A measurement is not an "intervention", and where the word
    # named a real event, the operator re-centring the lock, "re-centring"
    # says it exactly.
    "defeat",
    "snug",
    "intervention",
    # The evening additions are loaded from _banned_words.json: naming them
    # here as literals made this file fail the internal-vocabulary bank,
    # which is the guard-fixture-is-prose lesson a second time. The family:
    # words that dress work as drama, and the assistant register's verbs.
    *json.loads((Path(__file__).parent / "_banned_words.json").read_text())[
        "banned_words_2026_08_24_evening"],
])
def test_filler_openers_stay_absent(phrase):
    """Phrases that announce importance instead of demonstrating it.

    These are at zero. Unlike the punctuation above they can be banned
    outright, so they are, before they get a foothold.
    """
    # docs/lit/ holds one note per paper and quotes published titles and
    # abstracts VERBATIM, so a phrase there is the source's word and not this
    # project's. Two of the phrases added on 2026-08-10 turned up only there,
    # in a paper title and in an abstract, which is what surfaced the gap:
    # tests/test_repo_hygiene.py has skipped that directory for this reason
    # since it was written, and this guard never learned to.
    hits = [rel for rel in _tracked_markdown()
            if not rel.startswith("docs/lit/") and (ROOT / rel).exists()
            and phrase in (ROOT / rel).read_text(encoding="utf-8").lower()]
    assert not hits, f"{phrase!r} appears in: {', '.join(hits)}"


# --- the constructions ratchet, added 2026-08-24 ------------------------------
CONSTRUCTION_BASELINE = Path(__file__).parent / "_construction_baseline.json"
RATHER_THAN = re.compile(r"\brather than\b")


def _rather_than_counts() -> dict[str, int]:
    out = {}
    for rel in _tracked_markdown():
        if not (ROOT / rel).exists():
            continue
        n = len(RATHER_THAN.findall((ROOT / rel).read_text(encoding="utf-8")))
        if n:
            out[rel] = n
    return out


def test_no_file_gains_the_rather_than_construction():
    """A per-file falling budget on one syntactic tic.

    The word banks cannot see a construction, and this one is the single
    largest machine-register tell the case-page review measured: 14 instances
    in 2098 words on the page a PI reads first, where two or three is what a
    person writes. The rewrite then made it SIXTEEN before anyone counted,
    which is why this is a machine and not a style note. The corpus baseline
    is seeded at measured counts (BIG_PICTURE alone carries 22), so nothing is
    retrofitted: files fall as they are edited and may not rise.

    Only this one construction is mechanised. The review also named "not X
    but Y" and coordinated clause-lists of four or more, and both are left to
    judgement DELIBERATELY: a regex for either matches ordinary contrast and
    ordinary lists far too often, and a guard that cries wolf gets relaxed
    into uselessness.
    """
    baseline = json.loads(CONSTRUCTION_BASELINE.read_text())
    current = _rather_than_counts()

    worse = []
    for rel, now in sorted(current.items()):
        was = baseline.get(rel)
        if was is None:
            if now > 3:
                worse.append(f"{rel}: NEW file with {now}")
        elif now > was:
            worse.append(f"{rel}: {was} -> {now} (+{now - was})")

    assert not worse, (
        "a file gained 'rather than' constructions. Two or three per document "
        "is what a person writes: end the contrast or restructure the "
        "sentence.\n  " + "\n  ".join(worse)
        + "\n\nAfter a genuine cleanup, re-record with:"
          "\n  python tests/test_prose_style_ratchet.py --relax-constructions")


VAGUE_JUDGEMENT = re.compile(r"\bcomfortabl[ey]\b", re.I)
VAGUE_BASELINE = Path(__file__).parent / "_vague_judgement_baseline.json"


def _vague_counts() -> dict[str, int]:
    out = {}
    for rel in _tracked_markdown():
        if not (ROOT / rel).exists():
            continue
        n = len(VAGUE_JUDGEMENT.findall((ROOT / rel).read_text(encoding="utf-8")))
        if n:
            out[rel] = n
    return out


def test_no_file_gains_a_vague_judgement_word():
    """A per-file falling budget on "comfortable", which cannot be banned.

    THE FAILURE, 2026-08-26. The experimenter read the v4.3 release note and
    said it sounded machine-written. One phrase he could have pointed at was
    "not a comfortable exclusion": it reads as considered judgement and
    carries no number, where "the margin is 1.35x and one subset arm does not
    exclude at all" says the same thing and can be checked.

    IT CANNOT JOIN THE FILLER BAN ABOVE, because that list is zero-cost by
    construction and this word is not at zero. It appears 32 times, and some
    of those are the legitimate engineering sense of margin, "DC to 750 Hz is
    comfortable against a 1 s scan", or "39 sits comfortably inside it". A
    ban would forbid the good use with the vague one, which is the mistake
    the 2026-08-10 batch avoided by keeping "leverage" and "underscore".

    So it takes the shape this file already uses for "rather than": a
    per-file budget seeded at the measured counts, allowed down, never up.
    Each file loses its vague uses when someone edits it for another reason.
    """
    baseline = json.loads(VAGUE_BASELINE.read_text())
    current = _vague_counts()
    worse = [f"{rel}: {baseline.get(rel, 0)} -> {n}"
             for rel, n in sorted(current.items()) if n > baseline.get(rel, 0)]
    assert not worse, (
        "a file gained a vague-judgement word. Say the number instead: "
        "'not a comfortable exclusion' is 'the margin is 1.35x, and one "
        "subset arm does not exclude at all'.\n  " + "\n  ".join(worse)
        + "\n\nAfter a genuine cleanup, re-record with:"
          "\n  python tests/test_prose_style_ratchet.py --relax-vague")


def test_the_vague_counter_sees_a_planted_word():
    """Ceiling test: the counter must be able to fire."""
    assert len(VAGUE_JUDGEMENT.findall("this is a comfortable margin")) == 1
    assert len(VAGUE_JUDGEMENT.findall("it sits comfortably inside")) == 1
    assert len(VAGUE_JUDGEMENT.findall("no such word here")) == 0


def test_the_construction_counter_sees_a_planted_tic():
    """Ceiling test, including the wrapped-phrase blind spot named."""
    assert len(RATHER_THAN.findall("bounded rather than measured")) == 1
    assert len(RATHER_THAN.findall("bounded rather\nthan measured")) == 0, (
        "a wrapped instance is invisible to the per-line form, recorded as "
        "the known blind region: flattening would also merge hyphenated "
        "wraps, and the budget errs toward under-counting rather than noise")


# --- the results-CSV register ratchet, added 2026-08-24 -----------------------
CSV_SEMICOLON_BASELINE = Path(__file__).parent / "_csv_semicolon_baseline.json"


def _csv_semicolon_counts() -> dict[str, int]:
    out = {}
    for f in sorted((ROOT / "results").glob("*.csv")):
        n = f.read_text(encoding="utf-8").count(";")
        if n:
            out[f"results/{f.name}"] = n
    return out


def test_no_results_csv_gains_semicolons():
    """A per-file falling budget on semicolons in results CSVs.

    The prose ratchet reads markdown and nothing else, and the note columns
    of results CSVs carry prose that no guard read: 31 files held semicolons
    when the region was finally measured (the blast radius recorded before
    mechanising, per the register rules). Producers write these columns, so
    the ban that governs tracked prose reaches them only through this
    ratchet: files fall as their producers are edited and may not rise, and
    a NEW csv starts clean.
    """
    baseline = json.loads(CSV_SEMICOLON_BASELINE.read_text())
    current = _csv_semicolon_counts()
    worse = []
    for rel, now in sorted(current.items()):
        was = baseline.get(rel)
        if was is None:
            worse.append(f"{rel}: NEW file with {now}")
        elif now > was:
            worse.append(f"{rel}: {was} -> {now} (+{now - was})")
    assert not worse, (
        "a results CSV gained semicolons in its note prose. Split the "
        "sentence in the producer instead.\n  " + "\n  ".join(worse)
        + "\n\nAfter a genuine cleanup, re-record with:"
          "\n  python tests/test_prose_style_ratchet.py --relax-csv-semicolons")


def test_the_csv_semicolon_counter_sees_a_planted_one():
    """Ceiling test: the counter is a raw count, so a planted one is seen."""
    assert "a; b".count(";") == 1
    assert "clean note text".count(";") == 0


# --- the emphasis-capitals guard, added on the experimenter's instruction ---
# "all cap-locs words are banned unless they are acronyms which have to be
# written in capital letters." A measurement found 3003 of them across 130
# pages before the sweep, so this is a ratchet on a habit, not a style note.
CAPS_ALLOWLIST = json.loads(
    (Path(__file__).parent / "_caps_allowlist.json").read_text())
# The two lists live in a data file, not here. A long run of capitalised words
# inside a test file reads as prose to three other guards, and putting them
# here failed the cathode-attribution guard, the internal-vocabulary guard and
# the named-person guard at once. A guard's own fixtures are data.
CAPS_ACRONYM = set(CAPS_ALLOWLIST["acronyms"])
CAPS_TOKEN = set(CAPS_ALLOWLIST["tokens"])
CAPS_NOTATION = re.compile(r"(?:\d+[SPDFG]\d*(?:/\d)?|[A-Z]_?\d+|[A-Z]{1,3}\d+[A-Z]?"
                           r"|[A-Z]+\d[A-Z0-9\-]*)")   # manufacturer part numbers
CAPS_PROT = re.compile(r"```.*?```|`[^`]*`|\$[^$]*\$|\]\([^)]*\)"
                       r"|\b[A-Za-z_][A-Za-z0-9_]*\.(?:md|py|csv|png|sh|json|svg|toml|cff|txt|jsonl)\b",
                       re.S | re.M)
CAPS_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*")


def _caps_ok(word: str) -> bool:
    bare = word.strip("-")
    if ("_" in bare or bare in CAPS_ACRONYM or bare in CAPS_TOKEN
            or bool(CAPS_NOTATION.fullmatch(bare)) or len(bare) < 2):
        return True
    # a hyphenated compound is fine when every piece is: 5S-6S, AC-DC,
    # a manufacturer part number. Without this the state-notation repair and this guard
    # disagree about the same string, which is how 5s-6s got stuck lowered.
    if "-" in bare:
        parts = [x for x in bare.split("-") if x]
        return bool(parts) and all(
            p in CAPS_ACRONYM or p in CAPS_TOKEN
            or CAPS_NOTATION.fullmatch(p) or p.isdigit()
            # a single-letter piece of a part number (DSO-X, I-98T-5L)
            # carries no emphasis a reader could hear
            or len(p) == 1 for p in parts)
    return False


def _emphasis_caps(rel: str) -> list[str]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    spans = [m.span() for m in CAPS_PROT.finditer(text)]
    out = []
    for m in CAPS_TOKEN_RE.finditer(text):
        w = m.group(0)
        letters = [ch for ch in w if ch.isalpha()]
        if not letters or not all(ch.isupper() for ch in letters):
            continue
        if _caps_ok(w) or any(a <= m.start() < b for a, b in spans):
            continue
        out.append(w)
    return out


def test_no_emphasis_capitals_in_tracked_prose():
    """Capitals are for acronyms and defined tokens, never for emphasis.

    The corpus carried 3003 emphasis capitals when this was first measured,
    almost all of them written by the assistant, and the sweep that cleared
    them is only worth as much as the guard that stops them coming back.
    What stays capitalised is enumerated above and each class has a reason:
    an acronym has no lower-case form, a status token is graded by a
    machine, an underscore marks a machine identifier, and 6S is physics.
    """
    hits = {}
    for rel in _tracked_markdown():
        if rel.startswith("docs/lit/") or not (ROOT / rel).exists():
            continue
        head = (ROOT / rel).read_text(encoding="utf-8")[:400].lower()
        if "generated" in head and "do not edit" in head:
            # BLIND REGION, named rather than papered over: a generated page
            # copies note columns out of results/*.csv, so its capitals are
            # written by producers. Sweeping those means regenerating every
            # CSV, and this machine is not the environment of record for the
            # fitted ones. The debt sits with the results-CSV semicolon
            # ratchet, which has the same source and the same fix.
            continue
        found = _emphasis_caps(rel)
        if found:
            hits[rel] = sorted(set(found))[:6]
    assert not hits, (
        "emphasis capitals in tracked prose. Write the word normally, or add "
        "it to CAPS_ACRONYM/CAPS_TOKEN if a machine or a reader needs it "
        "capitalised:\n  "
        + "\n  ".join(f"{k}: {', '.join(v)}" for k, v in sorted(hits.items())))


def test_no_lowered_state_notation_in_prose():
    """Atomic-state notation stays uppercase, and LOWERED notation is found.

    The caps guard PREVENTS new lowering, and prevention has a blind spot
    this test closes: the first, broken caps pass lowered `5S-6S` to
    `5s-6s` across twenty files, one of them the third word of the case
    page, and the repaired guard never looked back. A detector for the
    already-lowered form is the other half of the rule. Code spans, math
    and lit notes keep their own case (a paper may typeset states however
    it likes, and code identifiers are not prose).
    """
    lowered = re.compile(r"\b\d[spdf]\b(?!\))")
    strip = re.compile(r"```.*?```|`[^`]*`|\$[^$]*\$", re.S)
    hits = {}
    for rel in _tracked_markdown():
        if rel.startswith("docs/lit/") or not (ROOT / rel).exists():
            continue
        text = strip.sub("", (ROOT / rel).read_text(encoding="utf-8"))
        found = sorted(set(lowered.findall(text)))
        if found:
            hits[rel] = found[:5]
    assert not hits, (
        "lowered atomic-state notation in prose, write 5S not 5s:\n  "
        + "\n  ".join(f"{k}: {', '.join(v)}" for k, v in sorted(hits.items())))


def test_the_state_notation_detector_sees_a_planted_case():
    """Ceiling test on the planted forms."""
    pat = re.compile(r"\b\d[spdf]\b(?!\))")
    assert pat.search("the 5s level")
    assert pat.search("the 5s-6s line") 
    assert not pat.search("the 5S-6S line")
    assert not pat.search("about 5 seconds")


def test_the_emphasis_caps_detector_sees_a_planted_word():
    """Ceiling test, with the blind region named."""
    assert not _caps_ok("IMPORTANT")
    assert _caps_ok("FWHM") and _caps_ok("VERIFIED") and _caps_ok("6S")
    assert _caps_ok("NOT_ESTABLISHED") and _caps_ok("K8")
    # Blind region, recorded rather than fixed: a capitalised word inside
    # backticks, a link target or a filename is invisible here, because those
    # are code and paths where capitals carry meaning this guard cannot judge.




BANNED_SHAPED = [
    # The bound-measurement fusion, banned at the owner's third correction
    # of the class (2026-08-24, "make sure to avoid confusion between
    # measurement and bounds, as you have done already many times").
    # LANGUAGE 2.3c holds the full rule and its three-step form; these two
    # patterns catch only the clean fusions a machine can judge. "the
    # reason it is a bound is measured" is legitimate, grades the evidence
    # and not the bound, and is deliberately NOT matched.
    ("measured-bound", re.compile(r"\bmeasured (bound|limit)\b"),
     "a bound is not measured, it is set, and the evidence for it may be"),
    ("measurement-of-bound",
     re.compile(r"\bmeasurement of (the|a|this|its) (bound|limit)\b"),
     "a bound is a limit on a quantity, not a measurement of one"),
    # (name, pattern, what may stand)
    ("trade", re.compile(r"\btrade[sd]?\b(?!-off)|\btrading\b|\btradeoffs?\b"),
     "trade-off and trade-offs stand, the owner's own carve-out, and the "
     "unhyphenated spelling is normalised to it rather than allowed to hide"),
    ("corner", re.compile(r"\bcorners?\b"),
     "a literal geometric corner stands with a term-of-art marker on its line"),
    ("landscape", re.compile(r"\blandscapes?\b"),
     "nothing stands: orientation is said as the axis, surveys are fields"),
]


def test_shaped_bans_stay_at_zero():
    """Three bans that need a shape, not a substring.

    "trade" must not match "trade-off", which the experimenter kept. "corner"
    has one literal geometric use, marked term-of-art where it stands. Each
    ban was measured before it was made: 49 exchanges of parameter weight,
    24 corners of model classes and grids, 31 landscapes of surveys and
    cathode orientation, every one replaced by the word that says it exactly
    (exchange, end-member or vertex or region, field or the axis itself).
    """
    hits = []
    for rel in _tracked_markdown():
        if rel.startswith("docs/lit/") or not (ROOT / rel).exists():
            continue
        for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
            if "term-of-art" in line:
                continue
            line = re.sub(r"`[^`]*`", "", line)   # code labels are identifiers
            for name, pat, _ in BANNED_SHAPED:
                if pat.search(line):
                    hits.append(f"{rel}: [{name}] {line.strip()[:90]}")
    assert not hits, ("a shaped ban regressed:\n  " + "\n  ".join(hits[:12]))


if __name__ == "__main__":  # `python tests/test_prose_style_ratchet.py --relax`
    import sys
    if "--relax-vague" in sys.argv:
        VAGUE_BASELINE.write_text(json.dumps(_vague_counts(), indent=1, sort_keys=True) + "\n")
        print("re-recorded the vague-judgement baseline")
    elif "--relax-csv-semicolons" in sys.argv:
        CSV_SEMICOLON_BASELINE.write_text(
            json.dumps(_csv_semicolon_counts(), indent=1, sort_keys=True)
            + "\n")
        print(f"re-recorded {CSV_SEMICOLON_BASELINE.name} "
              f"({sum(_csv_semicolon_counts().values())} total)")
    elif "--relax-constructions" in sys.argv:
        CONSTRUCTION_BASELINE.write_text(
            json.dumps(_rather_than_counts(), indent=1, sort_keys=True) + "\n")
        print(f"re-recorded {CONSTRUCTION_BASELINE.name} "
              f"({sum(_rather_than_counts().values())} total)")
    elif "--relax" in sys.argv:
        cur = _current()
        old = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
        BASELINE.write_text(json.dumps(cur, indent=1, sort_keys=True) + "\n")
        before, after = sum(old.values()), sum(cur.values())
        print(f"baseline re-recorded: {before} -> {after} ({after - before:+d})")
    else:
        print(f"total splice punctuation in prose: {sum(_current().values())}")


# The acronyms the 2026-08-24 caps sweep lowered, restored the same night and
# guarded here. DATA, not prose: rule 19.102. Kept beside the detector rather
# than in the allowlist file because these two lists answer different
# questions. The allowlist says "this may be capitalised". This says "this
# MUST be", and only the second one catches a form already lowered.
LOWERED_ACRONYM_FORMS = (
    # journals, publishers, institutions, projects
    "pra", "prr", "njp", "rmp", "aps", "josa", "pnas", "crc", "pdg",
    "nist", "usafa", "usaf", "ncku", "itu", "onna",
    # instruments and model numbers
    "dso", "3054a", "r636", "ds9010", "tpms1016e", "mtcd", "mbr", "98t",
    "wavedesc", "wlm", "swr", "brf", "apd",
    # statistics and computing initialisms
    "crlf", "exif", "acf", "dfbeta", "dfbetas", "dffits", "bfgs", "lopo",
    "lrt", "cusum", "mcse", "rempi", "bbc",
)


def test_no_lowered_acronyms_in_prose():
    """Journal, instrument and institution acronyms stay capitalised.

    THE FAULT THIS CLOSES, and it is the twin of the state-notation one
    above. The emphasis-capitals sweep of 2026-08-24 carried an allowlist
    built from a SAMPLE of the words it had touched rather than from its
    own diff, so a second class went through undetected: `Proc. IEEE`
    became `Proc. Ieee`, `NIST Special Publication` became `nist`, the
    Coherent `MBR-110` became `mbr-110`, and the EU project `CRYST3`
    became lower case in the literature index. Ninety prose instances
    across forty-two terms, found a day later by a wiki audit that
    noticed two citations and by then measuring the commit's own
    word-level diff rather than grepping guesses.

    Prevention was never the missing half. The allowlist already stopped
    NEW lowering; nothing looked back at what the first pass had done.
    So this detector reads the already-lowered form, which is the only
    shape that catches a repair that was never completed.

    Code spans, math, link targets and file paths are out of scope: a
    path is a path and `dso_x_3054a.csv` is a filename, not a sentence.
    """
    strip = re.compile(
        r"```.*?```|`[^`]*`|\$\$.*?\$\$|\$[^$\n]*\$|\]\([^)]*\)"
        r"|https?://\S+|\b[\w/.-]+\.(?:md|csv|py|png|jpg|jpeg|json|sh|txt"
        r"|pdf|yml|toml)\b|^\s{4,}\S.*$",
        re.S | re.M)
    pattern = re.compile(
        r"\b(" + "|".join(LOWERED_ACRONYM_FORMS) + r")\b")
    hits = {}
    for rel in _tracked_markdown():
        if rel.startswith("docs/lit/") or not (ROOT / rel).exists():
            continue
        text = strip.sub(" ", (ROOT / rel).read_text(encoding="utf-8"))
        found = sorted(set(pattern.findall(text)))
        if found:
            hits[rel] = found[:6]
    assert not hits, (
        "acronyms lowered in prose, write NIST not nist and PRA not pra:\n  "
        + "\n  ".join(f"{k}: {', '.join(v)}" for k, v in sorted(hits.items()))
        + "\n(if one of these is genuinely lower case in its context, the "
          "term belongs out of LOWERED_ACRONYM_FORMS, not silenced here)")


def test_the_lowered_acronym_detector_sees_a_planted_case():
    """Ceiling test, both directions, and the deliberate exclusions.

    The exclusions are as load-bearing as the inclusions: `dof` and
    `ad hoc` are correctly lower case in physics prose, and unit
    prefixes like `64k` are not acronyms at all, so none of the three
    may ever enter the list.
    """
    pat = re.compile(r"\b(" + "|".join(LOWERED_ACRONYM_FORMS) + r")\b")
    assert pat.search("published in pra 86")
    assert pat.search("the nist term energies")
    assert pat.search("an mbr-110 at about 100 kHz")
    assert not pat.search("published in PRA 86")
    assert not pat.search("2.83 on 3 dof")
    assert not pat.search("an ad hoc correction")
    assert not pat.search("exports at most 64k points")
