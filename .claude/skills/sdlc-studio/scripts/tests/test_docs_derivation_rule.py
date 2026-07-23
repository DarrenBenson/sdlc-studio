"""Doc invariants for the derivation rule (US0316) and the agreement pattern (US0317 AC3).

The rule these guides must carry: a user-facing sentence about what a guard will do is
DERIVED from the guard's own predicate, not restated beside it. CR0394's evidence is that the
`window open` sentence was wrong five times in one sprint, every one an independent
restatement of a rule living in code elsewhere.

What these checks are, stated plainly and no higher: a POLARITY SCAN over prose, the same
guarantee `test_docs_single_writer.py` establishes. Each criterion requires a specific
sentence PRESENT and reads sentences about the guarded topic for polarity, so prose asserting
the opposite fails wherever it sits. Presence is not meaning and a polarity scan is not a
semantic proof; a contradiction phrased in words the scan does not select still escapes, and
nothing here should be read as claiming otherwise. AC1/AC2 are the halves the story's own
kill-list flags as not fully discriminating - a curated required-sentence plus a blocklist,
each with a control proving it is not inert. What rises above a grep is AC3, which holds the
rule to itself: one statement, one place, reached by a link whose anchor resolves.

These guides ship in the skill, so the checks run identically from an installed copy. Prose is
normalised (asterisk emphasis and code markers dropped, whitespace collapsed) before matching,
so a required sentence wrapped across lines still matches - which a line-oriented grep cannot.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

BP_DIR = Path(__file__).resolve().parents[2] / "best-practices"
SCRIPT_DOC = BP_DIR / "script.md"
DOCUMENTATION_DOC = BP_DIR / "documentation.md"
TESTING_DOC = BP_DIR / "testing.md"


# -----------------------------------------------------------------------------
# Text handling (kept identical in rule to test_docs_single_writer.normalise)
# -----------------------------------------------------------------------------

def normalise(text: str) -> str:
    """Drop markdown emphasis / code markers and collapse whitespace."""
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")).strip()


def sentences(raw: str) -> list[str]:
    """Every sentence in the document, normalised - split on terminal punctuation."""
    out: list[str] = []
    for para in re.split(r"\n\s*\n", raw):
        norm = normalise(para)
        if norm:
            out.extend(s for s in re.split(r"(?<=[.!?])\s+", norm) if s)
    return out


def _requires(raw: str, needle: str, where: str, ac: str) -> list[str]:
    """One failure string when `needle` (a regex) is absent from the normalised text."""
    if re.search(needle, normalise(raw), re.I):
        return []
    return [f"{ac}: {where} does not state: /{needle}/"]


# -----------------------------------------------------------------------------
# The rule, and the polarity of prose that may not sit beside it
# -----------------------------------------------------------------------------

#: The rule sentence, stated ONCE (in script.md). Bounded by `[^.]` so it cannot span a
#: sentence boundary, matched over the normalised whole document so a line wrap is invisible.
RULE = (r"a user-facing sentence about what a guard[^.]*is computed from the guard.?s own "
        r"predicate,? not written alongside it")

#: The two halves of the counter-example. Naming only one is the failure AC2 catches: the
#: enumeration alone reads as "list the cases carefully" and the probe alone gives an author no
#: shape to recognise, so only the guide carrying both is a usable rule.
ENUMERATION_HALF = (r"an enumeration of[^.]*spellings[^.]*is a restatement wearing a "
                    r"function.?s clothes")
PROBE_HALF = r"probing the real predicate[^.]*is what makes .*a derivation"

#: A blocklist half: a sentence asserting the OPPOSITE - that a message written by hand beside
#: the predicate is acceptable. Requires a "written by hand / beside the predicate" cue AND a
#: positive verdict word in the one sentence, so correct prose stating the rule (which pairs
#: the cue with no positive verdict) does not trip it. Belt-and-braces, honest about being a
#: blocklist: a new phrasing of the same denial has to be added here.
DENIAL = re.compile(
    r"\b(hand-written|hand-authored|restated|written alongside|written beside|"
    r"a second copy|copied)\b[^.]*\b(fine|acceptable|allowed|ok|okay|permitted|"
    r"enough|sufficient|correct|safe|right)\b", re.I)


def _denies_rule(text: str, ac: str) -> list[str]:
    """One failure string per sentence asserting a hand-written message is acceptable."""
    return [f"{ac}: sentence denies the derivation rule: {s!r}"
            for s in sentences(text) if DENIAL.search(s)]


def check_rule_stated(script: str) -> list[str]:
    """AC1: the rule is present, and no sentence denies it wherever it sits."""
    ac = "AC1"
    return _requires(script, RULE, "script.md", ac) + _denies_rule(script, ac)


def check_counter_example(script: str) -> list[str]:
    """AC2: BOTH halves of the counter-example are named; either alone fails."""
    ac = "AC2"
    return (_requires(script, ENUMERATION_HALF, "script.md", ac + " (enumeration half)")
            + _requires(script, PROBE_HALF, "script.md", ac + " (probe half)"))


def check_one_statement(script: str, documentation: str) -> list[str]:
    """AC3: the rule appears exactly once across the two guides, and documentation.md reaches
    it by a link whose anchor resolves in script.md - the rule applied to its own statement."""
    ac = "AC3"
    bad: list[str] = []
    joined = normalise(script) + " \n " + normalise(documentation)
    n = len(re.findall(RULE, joined, re.I))
    if n != 1:
        bad.append(f"{ac}: the rule sentence appears {n} time(s) across the two guides, not once")
    m = re.search(r"\]\(script\.md#([a-z0-9-]+)\)", documentation)
    if not m:
        bad.append(f"{ac}: documentation.md does not link to the rule in script.md")
    elif not re.search(r"\{#" + re.escape(m.group(1)) + r"\}", script):
        bad.append(f"{ac}: documentation.md links to #{m.group(1)}, which script.md does not "
                   f"define as an anchor")
    return bad


# -----------------------------------------------------------------------------
# US0317 AC3: the testing guide states the agreement pattern
# -----------------------------------------------------------------------------

#: The pattern: one test drives the message and the verdict from one battery and asserts they
#: agree.
AGREEMENT_PATTERN = (r"drives? the message and the verdict[^.]*one shared battery[^.]*assert"
                     r"[^.]*agree")
#: The counter-example it replaces: asserting the message's text on its own.
AGREEMENT_COUNTER = r"asserting the message.?s text on its own"


def check_agreement_guide(testing: str) -> list[str]:
    """US0317 AC3: the pattern is stated AND the counter-example it replaces is named; a
    version stating only the pattern fails."""
    ac = "US0317-AC3"
    return (_requires(testing, AGREEMENT_PATTERN, "testing.md", ac)
            + _requires(testing, AGREEMENT_COUNTER, "testing.md", ac + " (counter-example)"))


def read_guides() -> tuple[str, str, str]:
    """The three shipped best-practice guides, as text."""
    return (SCRIPT_DOC.read_text(encoding="utf-8"),
            DOCUMENTATION_DOC.read_text(encoding="utf-8"),
            TESTING_DOC.read_text(encoding="utf-8"))


# =============================================================================
# US0316 AC1
# =============================================================================

class DerivationRuleStatedTests(unittest.TestCase):
    """The script guide states the rule, and prose denying it fails wherever it sits."""

    def test_the_script_guide_states_the_rule_and_no_sentence_denies_it(self) -> None:
        script, _, _ = read_guides()
        self.assertEqual([], check_rule_stated(script))

    def test_a_guide_missing_the_rule_fails_the_required_half(self) -> None:
        """The state before this story: the guide says nothing about it, so the required half
        fails. Proven by removing the rule sentence from the shipped guide."""
        script, _, _ = read_guides()
        without = re.sub(RULE, "SOME UNRELATED SENTENCE", normalise(script), flags=re.I)
        self.assertTrue(check_rule_stated(without),
                        "a guide without the rule sentence must fail the required half")

    def test_prose_asserting_a_hand_written_message_is_acceptable_fails(self) -> None:
        """The polarity half: a denial appended anywhere fails, even beside the intact rule."""
        script, _, _ = read_guides()
        for denial in ("A hand-written message beside the predicate is perfectly acceptable.",
                       "A message written alongside the predicate is fine.",
                       "A second copy of the rule in the message is enough."):
            with self.subTest(denial=denial):
                self.assertTrue(check_rule_stated(script + "\n\n" + denial),
                                f"denial slipped past the scan: {denial!r}")


# =============================================================================
# US0316 AC2
# =============================================================================

class CounterExampleTests(unittest.TestCase):
    """The counter-example is named in BOTH halves, and half of it alone fails."""

    def test_the_shipped_guide_names_both_halves(self) -> None:
        script, _, _ = read_guides()
        self.assertEqual([], check_counter_example(script))

    def test_either_half_of_the_counter_example_alone_fails(self) -> None:
        script, _, _ = read_guides()
        norm = normalise(script)
        enumeration_only = re.sub(PROBE_HALF, "AND THAT IS THAT", norm, flags=re.I)
        probe_only = re.sub(ENUMERATION_HALF, "A CAREFUL LIST OF THE CASES", norm, flags=re.I)
        self.assertTrue(check_counter_example(enumeration_only),
                        "the enumeration alone reads as 'list the cases carefully' and must fail")
        self.assertTrue(check_counter_example(probe_only),
                        "the probe alone gives no shape to recognise and must fail")
        # the control: only the guide carrying BOTH passes, so the two above are discriminating
        self.assertEqual([], check_counter_example(script))


# =============================================================================
# US0316 AC3
# =============================================================================

class OneStatementTests(unittest.TestCase):
    """The rule is stated once and pointed at, not copied into the second guide."""

    def test_the_rule_is_stated_once_and_the_documentation_guide_links_to_it(self) -> None:
        script, documentation, _ = read_guides()
        self.assertEqual([], check_one_statement(script, documentation))

    def test_a_second_copy_of_the_rule_in_documentation_fails(self) -> None:
        """The rule applied to its own statement: a copy in the second guide is the drift this
        forbids, and the count catches it."""
        script, documentation, _ = read_guides()
        holder = next(s for s in sentences(script) if re.search(RULE, s, re.I))
        self.assertTrue(check_one_statement(script, documentation + "\n\n" + holder + "."),
                        "a second copy of the rule must fail the once-only count")

    def test_a_link_to_a_missing_anchor_fails(self) -> None:
        script, documentation, _ = read_guides()
        broken = re.sub(r"\]\(script\.md#[a-z0-9-]+\)", "](script.md#no-such-anchor)",
                        documentation)
        self.assertTrue(check_one_statement(script, broken),
                        "a link whose anchor script.md does not define must fail")

    def test_a_documentation_guide_that_does_not_link_fails(self) -> None:
        script, documentation, _ = read_guides()
        no_link = re.sub(r"\]\(script\.md#[a-z0-9-]+\)", "]", documentation)
        self.assertTrue(check_one_statement(script, no_link),
                        "documentation.md must REACH the rule by a link, not merely omit a copy")


# =============================================================================
# US0317 AC3
# =============================================================================

class AgreementPatternGuideTests(unittest.TestCase):
    """The testing guide states the agreement pattern and names what it replaces."""

    def test_the_testing_guide_states_the_agreement_pattern_and_names_what_it_replaces(self) -> None:
        _, _, testing = read_guides()
        self.assertEqual([], check_agreement_guide(testing))

    def test_a_guide_stating_only_the_pattern_without_the_counter_example_fails(self) -> None:
        _, _, testing = read_guides()
        without_counter = re.sub(AGREEMENT_COUNTER, "SOME OTHER APPROACH",
                                 normalise(testing), flags=re.I)
        self.assertTrue(check_agreement_guide(without_counter),
                        "the pattern without the counter-example it replaces must fail")

    def test_a_guide_missing_the_pattern_fails(self) -> None:
        _, _, testing = read_guides()
        without_pattern = re.sub(AGREEMENT_PATTERN, "WRITE A TEST", normalise(testing),
                                 flags=re.I)
        self.assertTrue(check_agreement_guide(without_pattern),
                        "a guide that never states the pattern must fail the required half")


if __name__ == "__main__":
    unittest.main()
