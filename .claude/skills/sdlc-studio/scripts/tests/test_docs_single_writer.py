"""Doc invariants for the single-writer rule in reference-sprint.md / reference-review.md.

Why this module exists rather than four `grep` Verify lines: a substring grep is a
presence check, and presence does not establish meaning. The four criteria this locks
were originally evidenced by `grep "green"`, `grep "symlink"`, `grep "window"` and one
distinctive phrase; a reviewer replaced the documentation with prose asserting the
OPPOSITE of every criterion and all four greps still passed, because each word survives
inside its own denial. `grep` is exempt from the vacuity gate, so nothing flagged it.

The shape used here has three parts, and none of them proves the documents MEAN the right
thing. What each part actually establishes:

  REQUIRED  a specific whole sentence is PRESENT, plus the facts that have to sit beside it
            (the ceremony commits, the incident, the mechanism, the command). Presence, and
            nothing more: `_requires` searches the whole normalised document, so a
            contradiction written BESIDE the required sentence satisfies this half too. An
            earlier version of this docstring claimed that negated prose fails here
            structurally. That was FALSE, and false in the way this module exists to catch:
            it holds only for a whole-document REPLACEMENT, which is not how documentation
            rots. A reviewer appended four contradicting sentences to the shipped files and
            every criterion stayed green.
  POLARITY  every SENTENCE about one of the guarded properties is read for polarity, and one
            asserting the opposite fails wherever in the file it sits. This is the half that
            answers the appended contradiction, and the half a presence check cannot be. Its
            reach is bounded and the bound is stated at POLARITY_AXES.
  FORBIDDEN a curated family of contradicting phrasings. This half is belt-and-braces. It is
            a blocklist, not a semantic proof, and it is honest about that: a new way of
            writing the same contradiction has to be added to it.

So: the statements are present, no sentence using the guarded vocabulary asserts their
opposite, and no known contradicting phrasing appears. A contradiction written in words none
of the axes select is still not caught, and no test here should be read as saying otherwise.
AC2 has no axis: its mechanism is guarded by the blocklist alone.

Both reference files are part of the shipped skill, so these checks run identically from
an installed copy. Prose is normalised (emphasis and code markers dropped, whitespace
collapsed) before matching, so a required sentence wrapped across two lines still matches
- which a line-oriented grep cannot do.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared loader
import loader  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parents[2]
SPRINT_DOC = SKILL_DIR / "reference-sprint.md"
REVIEW_DOC = SKILL_DIR / "reference-review.md"


# -----------------------------------------------------------------------------
# Text handling
# -----------------------------------------------------------------------------

def normalise(text: str) -> str:
    """Drop markdown emphasis / code markers and collapse whitespace."""
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")).strip()


def paragraphs(raw: str) -> list[str]:
    """Blank-line separated blocks, each normalised."""
    return [normalise(p) for p in re.split(r"\n\s*\n", raw) if normalise(p)]


def sentences(raw: str) -> list[str]:
    """Every sentence in the document, normalised.

    Split on terminal punctuation followed by whitespace only, so `mutation.py window`
    and `retro.py` stay whole.
    """
    out: list[str] = []
    for para in paragraphs(raw):
        out.extend(s for s in re.split(r"(?<=[.!?])\s+", para) if s)
    return out


def _mentioning(raw: str, pattern: str) -> list[str]:
    """Sentences matching `pattern` (case-insensitive)."""
    rx = re.compile(pattern, re.I)
    return [s for s in sentences(raw) if rx.search(s)]


def _requires(raw: str, needle: str, where: str, ac: str) -> list[str]:
    """One failure string when `needle` (a regex) is absent from the normalised text."""
    if re.search(needle, normalise(raw), re.I):
        return []
    return [f"{ac}: {where} does not state: /{needle}/"]


def _forbids(raw: str, pattern: str, why: str, ac: str) -> list[str]:
    """One failure string per sentence matching a contradicting phrasing."""
    return [f"{ac}: contradicting sentence ({why}): {s!r}"
            for s in _mentioning(raw, pattern)]


# -----------------------------------------------------------------------------
# Polarity: what may not be asserted BESIDE the required sentence
# -----------------------------------------------------------------------------
# `_requires` searches the whole document, so a required sentence and its contradiction can
# sit in the same file and both match. The scan below is what carries the meaning: every
# sentence about a guarded property is judged for POLARITY, so a contradiction fails wherever
# it is added and whatever words it uses inside the topic vocabulary.
#
# THE BOUND, stated rather than implied, and CORRECTED after round 3 caught this comment
# overstating it. A sentence is SELECTED by topic vocabulary and JUDGED by negation cues, both
# enumerated here. Four things slip through, and the fourth was previously DENIED here:
#   1. prose about a guarded property that uses none of its topic words;
#   2. a reversal carried by irony or by layout rather than by a cue;
#   3. a negation sitting further from its verb than NEG_REACH;
#   4. an UNRELATED negation within NEG_REACH of the asserting word, which launders a direct
#      contradiction. There is NO attachment check: any cue in the run-up counts. So
#      "Nothing else matters: a green run proves the staged tree is clean" passes, because
#      "Nothing" sits within reach of "proves" while modifying something else entirely.
# It also OVER-fires in the same way: "A review must never proceed without a declared window"
# is correct prose that this scan reports as asserting the opposite, because the cue attaches
# to "proceed" rather than to the rule being stated.
# This is a polarity scan over named topics, not a semantic proof. It raises the cost of
# contradicting the docs; it does not make it impossible. Treat a green result as "no
# contradiction in the shapes enumerated here", never as "the documentation is consistent".

#: Words that flip an assertion, looked for in the run-up to the asserting word.
NEG_CUES = re.compile(r"\b(not|never|no|nobody|none|nothing|neither|nor|cannot|can't|doesn't|"
                      r"don't|isn't|won't|rarely|refus\w*|forbid\w*|banned)\b", re.I)

#: How far back from the asserting word a negation is taken to reach. Long enough for the
#: auxiliaries the docs actually use ("does not establish", "is NOT evidence"). It does NOT
#: establish that an unrelated negation cannot launder the assertion - this comment claimed it
#: did, and round 3 disproved it with five natural sentences. Shortening the reach does not fix
#: the class either, it only moves which sentences escape; an attachment check would, and is
#: not implemented. See THE BOUND above, item 4.
NEG_REACH = 40

#: (ac, property, topic patterns ALL of which must match the sentence, asserting word,
#: expected polarity). `negated` = every occurrence of the asserting word must carry a
#: negation; `asserted` = none of them may.
POLARITY_AXES = (
    ("AC3", "what a green run shows",
     (r"\b(green|clean|passing|passes|passed)\b",
      r"\b(gate|suite|run|runs|test|tests|check)\b",
      r"\b(tree|concurrent write|staged|staging|nothing but)\b"),
     r"\b(establish\w*|mean\w*|prove\w*|proof|show\w*|evidence|guarantee\w*|impl(y|ies)|"
     r"confirm\w*|tell\w*)\b", "negated"),
    ("AC1", "whether a review needs a declared window",
     (r"\bwindow\b", r"\breview\w*\b", r"\bdeclar\w*\b"),
     r"\bdeclar\w*\b", "asserted"),
    ("AC1", "what may be staged during the window",
     (r"git add -A|\bstag(e|es|ed|ing)\b", r"\bwindow\b|\breview\w*\b"),
     r"\b(may|can|fine|acceptable|allowed|permitted|normal|safe|okay|ok)\b", "negated"),
    # Topic is the bare word here: the asserting list is specific enough on its own, and
    # requiring a second guard word let "the declared window is optional" through.
    ("AC4", "the force of the window guard",
     (r"\bwindow\b",),
     r"\b(advisory|optional|informational|suggestion|cosmetic|toothless)\b", "negated"),
)


def _polarity(docs: tuple[tuple[str, str], ...], ac: str) -> list[str]:
    """One failure string per sentence asserting the opposite of a guarded property."""
    bad: list[str] = []
    for axis_ac, prop, topic, word, expect in POLARITY_AXES:
        if axis_ac != ac:
            continue
        rx = re.compile(word, re.I)
        for name, raw in docs:
            for s in sentences(raw):
                if not all(re.search(t, s, re.I) for t in topic):
                    continue
                for m in rx.finditer(s):
                    negated = bool(NEG_CUES.search(s[max(0, m.start() - NEG_REACH):m.start()]))
                    if (expect == "negated") != negated:
                        bad.append(f"{ac}: {name} asserts the opposite of the rule on "
                                   f"{prop} ({m.group(0)!r}): {s!r}")
    return bad


# -----------------------------------------------------------------------------
# The CLI the prose points at (AC4's anti-drift half)
# -----------------------------------------------------------------------------

def window_cli() -> tuple[set[str], set[str]]:
    """The real `mutation.py window` verbs and flags, read from its argparse.

    Prose naming a command the tool does not have is drift, and drift is exactly what
    AC4 is written to prevent, so the prose is checked against the parser rather than
    against another copy of the prose.
    """
    mutation = loader.load_script("mutation")
    parser = mutation.build_parser()
    subs = [a for a in parser._actions if hasattr(a, "choices") and isinstance(a.choices, dict)]
    window = subs[0].choices["window"]
    verbs: set[str] = set()
    flags: set[str] = set()
    for action in window._actions:
        if action.option_strings:
            flags.update(action.option_strings)
        elif action.choices:
            verbs.update(action.choices)
    return verbs, flags


_CMD_RE = re.compile(r"mutation\.py window ([a-z|]+)((?:\s+--[a-z-]+(?:\s+<[^>]*>)?)*)")


def cited_commands(raw: str) -> list[tuple[str, list[str]]]:
    """Every `mutation.py window ...` invocation the prose cites: (verb, flags)."""
    out: list[tuple[str, list[str]]] = []
    for verbs, tail in _CMD_RE.findall(normalise(raw)):
        flags = re.findall(r"--[a-z-]+", tail)
        out.extend((verb, flags) for verb in verbs.split("|") if verb)
    return out


# -----------------------------------------------------------------------------
# The four criteria
# -----------------------------------------------------------------------------

#: The ceremony commits an author makes during a review, which AC1 requires named
#: beside the rule rather than left to the reader.
CEREMONY_TERMS = ("retro", "review anchor", "findings", "CHANGELOG")


def check_ac1(sprint: str, review: str = "") -> list[str]:
    """The single-writer rule covers review time, not only a build-time mutation run.

    `review` is optional only so a fixture can be checked on its own; the shipped pair is
    always passed both, because a contradiction is as damaging in either file."""
    ac = "AC1"
    claim = (r"an independent review is a concurrent-writer window too, "
             r"and it is the more dangerous of the two")
    bad = _requires(sprint, claim, "reference-sprint.md", ac)
    if not bad:
        holder = next(p for p in paragraphs(sprint) if re.search(claim, p, re.I))
        missing = [t for t in CEREMONY_TERMS if t.lower() not in holder.lower()]
        if missing:
            bad.append(f"{ac}: the rule states the window but does not name the ceremony "
                       f"commits made during one: {', '.join(missing)}")
    bad += _forbids(sprint, r"concurrent-writer window[^.]*\b(den(y|ies|ied)|no such thing)",
                    "denies the window it is meant to state", ac)
    bad += _forbids(sprint, r"(is|are|was) (not|never) a concurrent-writer window",
                    "denies the window it is meant to state", ac)
    bad += _polarity((("reference-sprint.md", sprint), ("reference-review.md", review)), ac)
    return bad


def check_ac2(sprint: str, review: str) -> list[str]:
    """The documented mechanism is the corrected one: a redirect through a symlink."""
    ac = "AC2"
    bad: list[str] = []
    for name, raw in (("reference-sprint.md", sprint), ("reference-review.md", review)):
        joint = [s for s in sentences(raw)
                 if re.search(r"redirect", s, re.I) and re.search(r"symlink", s, re.I)]
        if not joint:
            bad.append(f"{ac}: {name} has no sentence naming the redirect AND the symlink "
                       f"as one mechanism")
        bad += _forbids(raw, r"\bmutants?\b[^.]*\b(caused|was the cause)\b|"
                             r"\b(caused by|the cause was|because of|due to)\b[^.]*\bmutants?\b",
                        "attributes the incident to a mutant", ac)
        bad += _forbids(raw, r"\bno symlink\b|\bsymlink[^.]*\b(was|were) not involved",
                        "denies the symlink mechanism", ac)
    return bad


def check_ac3(sprint: str, review: str) -> list[str]:
    """A passing gate is not evidence that no concurrent write is staged."""
    ac = "AC3"
    bad = _requires(sprint, r"a passing gate does not establish that no concurrent write is "
                            r"staged", "reference-sprint.md", ac)
    bad += _requires(review, r"green suite is (not|never) evidence the tree is clean",
                     "reference-review.md", ac)
    for name, raw in (("reference-sprint.md", sprint), ("reference-review.md", review)):
        # Polarity, not presence: every claim about what a green run shows must be negated.
        for match in re.finditer(r"evidence the tree is clean", normalise(raw), re.I):
            lead = normalise(raw)[max(0, match.start() - 30):match.start()]
            if not re.search(r"\b(not|never|no)\b", lead, re.I):
                bad.append(f"{ac}: {name} claims a green run IS evidence the tree is clean: "
                           f"{lead.strip()!r}")
        bad += _forbids(raw, r"\bdoes establish\b",
                        "asserts a gate establishes what the rule says it cannot", ac)
    bad += _polarity((("reference-sprint.md", sprint), ("reference-review.md", review)), ac)
    return bad


def check_ac4(sprint: str, review: str, cli: tuple[set[str], set[str]] | None = None) -> list[str]:
    """Both files point at the declared-window guard, and cite it as it really is."""
    ac = "AC4"
    verbs, flags = cli if cli is not None else window_cli()
    bad = _requires(sprint, r"mutation\.py window open --owner", "reference-sprint.md", ac)
    bad += _requires(sprint, r"mutation\.py window close --owner", "reference-sprint.md", ac)
    bad += _requires(sprint, r"the enforcement path is the declared window",
                     "reference-sprint.md", ac)
    bad += _requires(review, r"mutation\.py window open\|close", "reference-review.md", ac)
    for name, raw in (("reference-sprint.md", sprint), ("reference-review.md", review)):
        for verb, cited in cited_commands(raw):
            if verb not in verbs:
                bad.append(f"{ac}: {name} cites `mutation.py window {verb}`, which the tool "
                           f"does not have (has: {', '.join(sorted(verbs))})")
            for flag in cited:
                if flag not in flags:
                    bad.append(f"{ac}: {name} cites `{flag}` on `window {verb}`, which the "
                               f"tool does not accept")
        bad += _forbids(raw, r"no such thing as a[^.]*window|windows? (do|does) not exist",
                        "denies the guard the rule points at", ac)
    bad += _polarity((("reference-sprint.md", sprint), ("reference-review.md", review)), ac)
    return bad


def check_all(sprint: str, review: str,
              cli: tuple[set[str], set[str]] | None = None) -> dict[str, list[str]]:
    """Every criterion, keyed by AC id."""
    return {"AC1": check_ac1(sprint, review),
            "AC2": check_ac2(sprint, review),
            "AC3": check_ac3(sprint, review),
            "AC4": check_ac4(sprint, review, cli)}


def read_docs(skill_dir: Path = SKILL_DIR) -> tuple[str, str]:
    """The two shipped reference files, as text."""
    return ((skill_dir / "reference-sprint.md").read_text(encoding="utf-8"),
            (skill_dir / "reference-review.md").read_text(encoding="utf-8"))


# -----------------------------------------------------------------------------
# The negated prose these checks exist to catch
# -----------------------------------------------------------------------------
# Verbatim from the review that rejected the original grep evidence. Held here as data,
# never written to disk in this tree: every check below must go RED on it, or the
# criterion it belongs to is once again evidenced by nothing.

NEGATED_SPRINT = """## The single-writer rule {#single-writer}

There is no such thing as a window here, and a review is a concurrent-writer window is a
phrase we deny. Stage whatever you like; git add -A is fine during a review.
"""

NEGATED_REVIEW = """**Single-writer during a review.** A green gate DOES establish that no
concurrent write is staged, and the RUN-01KY321Q incident was caused by a stale
hand-applied mutant; no symlink was involved, so a green suite is evidence the tree is
clean.
"""

#: The shape documentation ACTUALLY rots into, and the one the first version of this module
#: could not see: the correct prose is left exactly where it is and a contradiction is written
#: BESIDE it. Verbatim from the review that rejected that version. Held as data, appended to
#: the shipped files in memory only, never written to this tree (LL0039).
APPENDED_CONTRADICTION = """

The window guard is advisory only. While one is open you may stage anything you like, and
`git add -A` remains the normal way to commit during a review. A gate run that comes back clean
does mean the tree holds nothing but your own edits, so there is no need to check further.
Nobody need declare a window for a review; only an automated rewrite loop should bother.
"""


class SingleWriterDocTests(unittest.TestCase):
    """GREEN against the shipped documentation."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sprint, cls.review = read_docs()
        cls.cli = window_cli()

    def test_the_rule_covers_review_time_and_names_the_ceremony_commits(self) -> None:
        self.assertEqual([], check_ac1(self.sprint))

    def test_the_mechanism_documented_is_the_redirect_through_a_symlink(self) -> None:
        self.assertEqual([], check_ac2(self.sprint, self.review))

    def test_a_passing_gate_is_documented_as_no_evidence_of_a_clean_tree(self) -> None:
        self.assertEqual([], check_ac3(self.sprint, self.review))

    def test_both_files_cite_the_window_guard_as_the_tool_really_offers_it(self) -> None:
        self.assertEqual([], check_ac4(self.sprint, self.review, self.cli))


class DisclosedLimitsAreRealTests(unittest.TestCase):
    """The gaps THE BOUND admits, made executable.

    Round 3 found the NEG_REACH comment asserting a property the scan does not have: that an
    unrelated negation cannot launder an assertion. It can. The comment is now corrected, and
    these tests exist so the correction cannot rot back into a claim - if someone later adds an
    attachment check, these go RED and the prose must be updated with the code.

    A disclosed limit that nothing exercises is just a sentence, and a sentence about code is
    what eight consecutive closing reviews on this project have found wrong."""

    #: Direct contradictions of a guarded property that the scan does NOT catch, each because an
    #: unrelated negation sits within NEG_REACH of the asserting word (THE BOUND, item 4).
    LAUNDERED = [
        "Nothing else matters: a green run proves the staged tree is clean.",
        "No two ways about it, a green gate shows the staged tree is clean.",
        "Never skip the gate: a passing suite proves the staged tree is clean.",
        "It is not unusual for the window guard to be advisory.",
    ]

    #: Correct prose the scan wrongly reports as asserting its opposite (THE BOUND, over-firing).
    OVER_FIRED = [
        "A review must never proceed without a declared window.",
        "No review may run unless a window is declared first.",
    ]

    def test_the_laundering_gap_is_real_and_still_open(self) -> None:
        sprint, review = read_docs()
        for line in self.LAUNDERED:
            with self.subTest(line=line):
                self.assertEqual(
                    check_all(sprint + "\n\n" + line, review), {"AC1": [], "AC2": [],
                                                                 "AC3": [], "AC4": []},
                    "if this now FAILS, the scan improved: update THE BOUND item 4 and this list")

    def test_the_over_firing_is_real_and_still_open(self) -> None:
        sprint, review = read_docs()
        hits = 0
        for line in self.OVER_FIRED:
            res = check_all(sprint + "\n\n" + line, review)
            hits += sum(len(v) for v in res.values())
        self.assertGreater(hits, 0,
                           "if this now finds nothing, the over-firing was fixed: update THE "
                           "BOUND and this list rather than deleting the test")

    def test_the_shipped_docs_are_still_clean(self) -> None:
        """The control that keeps the two above honest: the gaps are real, and the scan is not
        simply inert."""
        sprint, review = read_docs()
        self.assertEqual(check_all(sprint, review),
                         {"AC1": [], "AC2": [], "AC3": [], "AC4": []})


class NegatedProseTests(unittest.TestCase):
    """RED against prose asserting the opposite of each criterion.

    This is the class the original `grep` evidence lacked. Without it, a checker that
    passes on the shipped files proves only that the files exist.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.cli = window_cli()

    def test_ac1_rejects_a_denial_of_the_review_window(self) -> None:
        self.assertTrue(check_ac1(NEGATED_SPRINT))

    def test_ac2_rejects_blaming_a_staged_mutant(self) -> None:
        self.assertTrue(check_ac2(NEGATED_SPRINT, NEGATED_REVIEW))

    def test_ac3_rejects_a_green_gate_treated_as_proof_of_a_clean_tree(self) -> None:
        self.assertTrue(check_ac3(NEGATED_SPRINT, NEGATED_REVIEW))

    def test_ac4_rejects_prose_that_names_no_window_command(self) -> None:
        self.assertTrue(check_ac4(NEGATED_SPRINT, NEGATED_REVIEW, self.cli))

    def test_every_criterion_is_red_on_the_negated_pair(self) -> None:
        failures = check_all(NEGATED_SPRINT, NEGATED_REVIEW, self.cli)
        self.assertEqual([], [ac for ac, msgs in failures.items() if not msgs])

    def test_a_ceremony_list_stripped_from_the_rule_is_caught(self) -> None:
        # The statement survives, the facts beside it do not: presence alone is not enough.
        thin = ("**An independent review is a concurrent-writer window too, and it is the "
                "more dangerous of the two.** Be careful.\n")
        self.assertTrue(check_ac1(thin))

    def test_a_command_the_tool_does_not_have_is_caught(self) -> None:
        sprint, review = read_docs()
        invented = sprint.replace("window close --owner", "window unlock --owner")
        self.assertTrue(check_ac4(invented, review, self.cli))

    def test_a_flag_the_tool_does_not_accept_is_caught(self) -> None:
        sprint, review = read_docs()
        invented = sprint.replace("window open --owner", "window open --holder")
        self.assertTrue(check_ac4(invented, review, self.cli))


class AppendedContradictionTests(unittest.TestCase):
    """RED against a contradiction added BESIDE the shipped prose, which is how documentation
    rots: nothing is deleted, so every presence check still passes.

    This class is the one the round-1 module lacked, and the reason its docstring's structural
    claim was false. The polarity scan is what makes it red; the required half cannot be, by
    construction, since the sentences it requires are all still there."""

    @classmethod
    def setUpClass(cls) -> None:
        sprint, review = read_docs()
        cls.sprint = sprint + APPENDED_CONTRADICTION
        cls.review = review + APPENDED_CONTRADICTION
        cls.cli = window_cli()

    def test_the_required_sentences_all_still_pass(self) -> None:
        """The premise. Every required sentence survives untouched, so presence alone can
        never see this edit - and a checker built only from presence reports all green."""
        for needle in (r"an independent review is a concurrent-writer window too",
                       r"a passing gate does not establish that no concurrent write is staged",
                       r"mutation\.py window open --owner"):
            self.assertEqual([], _requires(self.sprint, needle, "reference-sprint.md", "AC0"))

    def test_the_contradiction_is_caught_on_every_criterion_it_denies(self) -> None:
        failures = check_all(self.sprint, self.review, self.cli)
        for ac in ("AC1", "AC3", "AC4"):
            self.assertTrue(failures[ac], f"{ac} stayed green beside its own contradiction")
        # AC2 is NOT asserted here: the appended text says nothing about the mechanism, so it
        # is not contradicted, and claiming otherwise would be the same over-claim again.
        self.assertEqual([], failures["AC2"])

    def test_each_denied_criterion_is_red_in_the_file_the_contradiction_sits_in(self) -> None:
        sprint, review = read_docs()
        self.assertTrue(check_ac1(sprint + APPENDED_CONTRADICTION, review))
        self.assertTrue(check_ac1(sprint, review + APPENDED_CONTRADICTION))
        self.assertTrue(check_ac3(sprint + APPENDED_CONTRADICTION, review))
        self.assertTrue(check_ac3(sprint, review + APPENDED_CONTRADICTION))
        self.assertTrue(check_ac4(sprint + APPENDED_CONTRADICTION, review, self.cli))
        self.assertTrue(check_ac4(sprint, review + APPENDED_CONTRADICTION, self.cli))

    def test_a_rewording_of_the_same_contradiction_is_still_caught(self) -> None:
        """The blocklist half cannot do this; the polarity scan is what makes it hold. None
        of these phrasings appears in `_forbids`."""
        for line in ("\n\nA suite that passes proves the tree is clean.\n",
                     "\n\nDuring a review it is fine to stage everything at once.\n",
                     "\n\nThe declared window is optional for a reviewer's hand-edits.\n"):
            sprint, review = read_docs()
            self.assertTrue([f for msgs in check_all(sprint + line, review).values()
                             for f in msgs], f"not caught: {line.strip()!r}")

    #: One contradiction per guarded property, phrased in words no `_forbids` pattern holds.
    #: Keyed by the property name so an axis added without a probe fails the check below.
    AXIS_PROBES = {
        "what a green run shows":
            "\n\nA suite that passes proves the tree is clean.\n",
        "whether a review needs a declared window":
            "\n\nNobody need declare a window for a review.\n",
        "what may be staged during the window":
            "\n\nDuring a review it is fine to stage everything at once.\n",
        "the force of the window guard":
            "\n\nThe declared window is optional.\n",
    }

    def test_every_axis_catches_a_contradiction_of_its_own_property(self) -> None:
        """An axis nothing proves is an axis that can be deleted without a test noticing,
        which is how the round-1 module ended up with a claim and no mechanism."""
        sprint, review = read_docs()
        self.assertEqual({prop for _, prop, *_ in POLARITY_AXES}, set(self.AXIS_PROBES),
                         "every axis carries a probe, and every probe an axis")
        for prop, line in self.AXIS_PROBES.items():
            docs = (("reference-sprint.md", sprint + line), ("reference-review.md", review))
            hits = [f for ac in ("AC1", "AC2", "AC3", "AC4")
                    for f in _polarity(docs, ac) if prop in f]
            self.assertTrue(hits, f"the {prop!r} axis caught nothing")

    def test_the_scan_is_silent_on_the_shipped_files(self) -> None:
        """The other half of a discrimination proof: red on the contradiction is worth
        nothing without green on the prose it is meant to allow."""
        sprint, review = read_docs()
        docs = (("reference-sprint.md", sprint), ("reference-review.md", review))
        for ac in ("AC1", "AC2", "AC3", "AC4"):
            self.assertEqual([], _polarity(docs, ac))


if __name__ == "__main__":
    unittest.main()
