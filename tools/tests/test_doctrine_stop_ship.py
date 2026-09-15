#!/usr/bin/env python3
"""The shipped doctrine states the stop-ship rule, its one store, and who rules it.

Every probe reads the STOP-SHIP PASSAGE only: the numbered rule under `## The rules` whose
heading carries the `{#stop-ship}` anchor, from that heading to the next numbered rule or `##`
heading. The doctrine already says `severity-rated bug` (rule 21) and names the operator
elsewhere, so a whole-file check is green before a word of this rule exists (BG0457, the
precedent `test_doctrine_review_scope.py`). A claim is probed inside ONE sentence of the
passage, and each test builds a gutted copy in memory as its own positive control.

The table name and the ruling vocabulary are read from `retro.py` at test time and never
restated (LL0042): the doctrine quotes what the close reads, or the test goes red.
"""
from __future__ import annotations

# The one script this file's unit declares beside it; the census cannot place a test of a
# document by name or by reference, so it is told.
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
DOCTRINE = SKILL / "reference-doctrine.md"
sys.path.insert(0, str(SKILL / "scripts"))

import retro  # noqa: E402

ANCHOR = "{#stop-ship}"
RULE_HEADING_RE = re.compile(r"^\d+\.\s")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")


def _token(word: str) -> re.Pattern:
    """`word` as a whole token, so `stop-ship` never matches inside `not-stop-ship`."""
    return re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])")


STOP_SHIP_RE = _token("stop-ship")
NOT_STOP_SHIP_RE = _token("not-stop-ship")

#: AC1 - the rule's three outcomes, each a set of patterns ONE sentence must carry together.
OUTCOME_CLAIMS: tuple[tuple[str, tuple[re.Pattern, ...]], ...] = (
    ("a not-stop-ship finding is filed as its own bug or CR",
     (NOT_STOP_SHIP_RE, re.compile(r"\bfiled\b"), re.compile(r"\bbug or CR\b"))),
    ("that finding's unit closes pointing at the filed id",
     (re.compile(r"\bcloses pointing at\b", re.I), re.compile(r"\bfiled id\b", re.I))),
    ("a stop-ship finding holds the close",
     (STOP_SHIP_RE, re.compile(r"\bholds the close\b", re.I))),
)

#: AC2 - severity bound to the ruling by the negation itself, never merely sharing a sentence
#: with one: "severity is its ruling ... needs no further ruling" keeps a negation and must fail.
SEVERITY_CLAIMS = (
    ("severity alone is not the ruling",
     (re.compile(r"\bseverity\b(?:\s+\w+){0,2}?\s+(?:is|are)\s+(?:not|never)\s+"
                 r"(?:\w+\s+){0,2}?ruling\b", re.I),)),
)

#: AC3 - a sentence that records something somewhere. One intervening word is allowed, so
#: "are also kept" counts; two are not, so "is made by the operator or a recorded delegate"
#: never does.
RECORDING_RE = re.compile(
    r"\b(?:is|are|be)\s+(?:\w+\s+)?(?:recorded|stored|kept|logged)\b|\blives?\s+in\b", re.I)
ONLY_RE = re.compile(r"\bonly\b", re.I)
#: The repository's other record stores. None may appear in the passage at all.
OTHER_STORES = ("ledger", "decisions.md", "decision log", "handoff", "LATEST.md", "charter")

#: AC4 - who rules (the operator and a recorded delegate in one sentence), and a proposal
#: denied the force of a ruling.
_MADE_BY = r"\b(?:made|given|ruled|decided|set)\s+by\s+the\s+operator"
RULER_CLAIMS: tuple[tuple[str, tuple[re.Pattern, ...]], ...] = (
    ("the operator rules", (re.compile(_MADE_BY + r"\b", re.I),)),
    ("or a recorded delegate rules",
     (re.compile(_MADE_BY + r",?\s+or\s+a\s+recorded\s+delegate\b", re.I),)),
    ("a reviewer's proposal is not a ruling",
     (re.compile(r"\bpropos", re.I), re.compile(r"\bnot a ruling\b", re.I))),
)

#: AC5 - the vocabulary sentence: `one of` followed by code spans.
VOCABULARY_RE = re.compile(r"\bone of\s+`", re.I)


def rules_section(text: str) -> str:
    """The numbered rules only, from `## The rules` to the next `##` heading."""
    start = text.find("## The rules")
    if start < 0:
        return ""
    end = text.find("\n## ", start + 1)
    return text[start:end if end > 0 else len(text)]


def stop_ship_passage(text: str) -> str:
    """The `{#stop-ship}` rule, heading to the next numbered rule or `##` heading."""
    lines = rules_section(text).splitlines()
    for i, line in enumerate(lines):
        if RULE_HEADING_RE.match(line) and ANCHOR in line:
            end = next((j for j in range(i + 1, len(lines))
                        if RULE_HEADING_RE.match(lines[j]) or lines[j].startswith("## ")),
                       len(lines))
            return "\n".join(lines[i:end])
    return ""


def split_sentences(block: str) -> list[str]:
    """`block` as sentences: lines unwrapped, bold markers dropped, code spans kept whole."""
    flat = " ".join(line.strip() for line in block.splitlines() if line.strip())
    flat = RULE_HEADING_RE.sub("", flat).replace(ANCHOR, "").replace("**", "")
    spans: list[str] = []

    def _hide(match: re.Match) -> str:
        spans.append(match.group(0))
        return f"\x00{len(spans) - 1}\x00"

    hidden = re.sub(r"`[^`]*`", _hide, flat)
    out = []
    for part in re.split(r"(?<=[.!?])\s+", hidden):
        part = re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], part).strip()
        if part:
            out.append(part)
    return out


def passage_sentences(text: str) -> list[str]:
    return split_sentences(stop_ship_passage(text))


def missing(text: str, claims) -> list[str]:
    """The claims no single sentence of the passage makes."""
    sentences = passage_sentences(text)
    return [name for name, patterns in claims
            if not any(all(p.search(s) for p in patterns) for s in sentences)]


def store_problems(text: str, section: str) -> list[tuple[str, str]]:
    """Why the passage fails to name exactly one store, as `(kind, reason)` pairs.

    Two independent assertions, so each catches what the other cannot: `count` (exactly one
    recording sentence) refuses a second store named in words nobody listed, `vocabulary`
    refuses another store named with no recording verb. `only` is the one recording sentence
    failing to name the section as the only store; `clash` is an AC4 sentence using either
    shape, which would make the who-rules or proposal sentence read as a second store.
    """
    sentences = passage_sentences(text)
    if not sentences:
        return [("passage", f"no numbered rule carries {ANCHOR}")]
    problems: list[tuple[str, str]] = []
    recording = [s for s in sentences if RECORDING_RE.search(s)]
    if len(recording) != 1:
        problems.append(("count", f"{len(recording)} recording sentences: {recording}"))
    elif f"`{section}`" not in recording[0] or not ONLY_RE.search(recording[0]):
        problems.append(("only", f"the recording sentence does not name `{section}` as the "
                                 f"only store: {recording[0]!r}"))
    flat = " ".join(sentences).lower()
    named = [term for term in OTHER_STORES if term.lower() in flat]
    if named:
        problems.append(("vocabulary", f"the passage names other stores: {named}"))
    for s in sentences:
        if any(all(p.search(s) for p in patterns) for _, patterns in RULER_CLAIMS):
            if RECORDING_RE.search(s) or any(t.lower() in s.lower() for t in OTHER_STORES):
                problems.append(("clash", f"an AC4 sentence reads as a store: {s!r}"))
    return problems


def vocabulary_mismatch(text: str, rulings) -> list[str]:
    """Where the passage's vocabulary sentence and `rulings` differ, compared as SETS.

    Both directions: a ruling the doctrine offers that the close refuses, and one the close
    accepts that the doctrine never offers. Whole code spans, never substrings.
    """
    vocab = [s for s in passage_sentences(text) if VOCABULARY_RE.search(s)]
    if len(vocab) != 1:
        return [f"{len(vocab)} vocabulary sentences (`one of` followed by code spans)"]
    offered, accepted = set(CODE_SPAN_RE.findall(vocab[0])), set(rulings)
    return ([f"the doctrine offers `{v}`, which the close refuses"
             for v in sorted(offered - accepted)]
            + [f"the close accepts `{v}`, which the doctrine never offers"
               for v in sorted(accepted - offered)])


def with_body(text: str, transform) -> str:
    """A copy whose passage body is `transform(body sentences)`, its heading kept."""
    passage = stop_ship_passage(text)
    lines = passage.splitlines()
    body = transform(split_sentences("\n".join(lines[1:])))
    return text.replace(passage, lines[0] + "\n    " + " ".join(body) + "\n")


def rehomed(text: str) -> str:
    """The passage deleted, its sentences closing rule 21 and quoted in a Revision History row.

    The adversarial copy: every word of the rule is still in the file, some of it still under
    `## The rules`, and none of it in a `{#stop-ship}` rule.
    """
    passage = stop_ship_passage(text)
    body = " ".join(split_sentences("\n".join(passage.splitlines()[1:])))
    gutted = text.replace(passage, "    " + body + "\n")
    return gutted + ("\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                     f"| 2026-09-15 | US0625 | State the stop-ship rule: {body} |\n")


def _replace_once(old: str, new: str):
    def transform(sentences: list[str]) -> list[str]:
        joined = "\n".join(sentences)
        if joined.count(old) != 1:
            raise AssertionError(f"{old!r} occurs {joined.count(old)} times in the passage")
        return joined.replace(old, new).split("\n")
    return transform


class StopShipDoctrineTests(unittest.TestCase):

    def setUp(self) -> None:
        self.text = DOCTRINE.read_text(encoding="utf-8")

    def test_the_rule_names_both_outcomes(self) -> None:
        """MUTANT: delete the sentence filing a `not-stop-ship` finding as its own bug or CR.

        Also: delete the closes-pointing-at sentence; name `not-stop-ship` as the ruling that
        holds; move the rule's sentences into rule 21 and drop its anchor. Each must go red.
        """
        self.assertEqual([], missing(self.text, OUTCOME_CLAIMS),
                         "the {#stop-ship} rule does not state both outcomes of a ruling")

        gutted = rehomed(self.text)
        self.assertNotIn(ANCHOR, gutted)
        self.assertIn("closes pointing at the filed id", rules_section(gutted),
                      "the control must leave the sentences under ## The rules")
        self.assertEqual(sorted(name for name, _ in OUTCOME_CLAIMS),
                         sorted(missing(gutted, OUTCOME_CLAIMS)),
                         "the outcome claims were found outside the {#stop-ship} rule - rule "
                         "21 or a Revision History row would turn this green")

        swapped = with_body(self.text, _replace_once(
            "ruled `stop-ship` holds the close", "ruled `not-stop-ship` holds the close"))
        self.assertEqual(["a stop-ship finding holds the close"],
                         missing(swapped, OUTCOME_CLAIMS),
                         "`not-stop-ship` satisfied the stop-ship token - a substring match")

    def test_severity_is_not_the_ruling(self) -> None:
        """MUTANT: delete the severity sentence from the {#stop-ship} rule, rule 21 intact.

        Also: invert it so severity IS the ruling while keeping a negation ("needs no further
        ruling"). Both must go red.
        """
        name = [n for n, _ in SEVERITY_CLAIMS]
        self.assertEqual([], missing(self.text, SEVERITY_CLAIMS),
                         "the {#stop-ship} rule never says severity alone is not the ruling")

        severity = SEVERITY_CLAIMS[0][1][0]
        gutted = with_body(self.text, lambda ss: [s for s in ss if not severity.search(s)])
        self.assertIn("severity-rated bug", rules_section(gutted),
                      "the control must keep rule 21's `severity-rated bug`")
        self.assertEqual(name, missing(gutted, SEVERITY_CLAIMS),
                         "the severity claim was found outside the {#stop-ship} rule")

        inverted = with_body(self.text, lambda ss: [
            "A finding's severity is its ruling: a High finding is stop-ship by default and "
            "needs no further ruling." if severity.search(s) else s for s in ss])
        self.assertEqual(name, missing(inverted, SEVERITY_CLAIMS),
                         "an inversion keeping a negation satisfied the severity claim")

    def test_the_one_store_is_named_and_no_second(self) -> None:
        """MUTANT: add a sentence recording a stop-ship ruling in the critic ledger as well.

        Also: add that rulings are also kept on the verdicts page (no listed store term, so
        only the count sees it); weaken `the only store` to `a store`. Each must go red.
        """
        section = retro.KNOWN_ISSUES_SECTION
        self.assertEqual([], store_problems(self.text, section),
                         "the {#stop-ship} rule does not name exactly one store")
        for s in passage_sentences(self.text):
            if any(all(p.search(s) for p in pats) for _, pats in RULER_CLAIMS):
                self.assertIsNone(RECORDING_RE.search(s), f"AC4 sentence records: {s!r}")
        self.assertIsNone(RECORDING_RE.search(
            "The ruling is made by the operator or a recorded delegate, at the close."),
            "the recording shape matched the who-rules sentence")

        def kinds(copy: str) -> set[str]:
            return {kind for kind, _ in store_problems(copy, section)}

        second = with_body(self.text, lambda ss: ss + [
            "Rulings are also kept on the verdicts page."])
        self.assertEqual({"count"}, kinds(second),
                         "a second store in unlisted words must be refused by the count alone")

        ledger = with_body(self.text, lambda ss: ss + [
            "The critic ledger carries each ruling as well."])
        self.assertEqual({"vocabulary"}, kinds(ledger),
                         "a store named with no recording verb must be refused by the "
                         "vocabulary alone")

        both = with_body(self.text, lambda ss: ss + [
            "A stop-ship ruling is also recorded in the critic ledger."])
        self.assertEqual({"count", "vocabulary"}, kinds(both))

        weakened = with_body(self.text, _replace_once("the only store", "a store"))
        self.assertEqual({"only"}, kinds(weakened),
                         "a store offered as an option passed as the only one")

    def test_the_ruler_and_the_proposal_are_named(self) -> None:
        """MUTANT: remove `or a recorded delegate` from the who-rules sentence.

        Also: delete the proposal sentence; name the adversarial reviewer instead of the
        operator. Each must go red.
        """
        self.assertEqual([], missing(self.text, RULER_CLAIMS),
                         "the {#stop-ship} rule does not say who rules, or that a proposal is "
                         "not a ruling")

        cut = with_body(self.text, _replace_once(" or a recorded delegate", ""))
        self.assertEqual(["or a recorded delegate rules"], missing(cut, RULER_CLAIMS),
                         "cutting the delegate must report the delegate claim and nothing else")

        self.assertEqual(sorted(name for name, _ in RULER_CLAIMS),
                         sorted(missing(rehomed(self.text), RULER_CLAIMS)),
                         "the ruler claims were found outside the {#stop-ship} rule")

    def test_the_quoted_table_is_the_one_the_close_reads(self) -> None:
        """MUTANT: in retro.py, change KNOWN_ISSUES_SECTION's value to `Known issues ruled`.

        Also: append or remove a value of KNOWN_ISSUE_RULINGS, or rename one at the same
        length; drop `stop-ship` from the doctrine's list; change its quoted section name.
        Each must go red on an assertion here, never on an AttributeError.
        """
        section, rulings = retro.KNOWN_ISSUES_SECTION, tuple(retro.KNOWN_ISSUE_RULINGS)
        spans = set(CODE_SPAN_RE.findall(" ".join(passage_sentences(self.text))))
        self.assertIn(section, spans,
                      f"the {{#stop-ship}} rule does not quote `{section}`, the table the "
                      f"close reads")
        self.assertEqual([], vocabulary_mismatch(self.text, rulings),
                         "the doctrine's rulings are not the ones retro.py accepts")

        for label, other in (("plus one", rulings + ("waived",)),
                             ("minus one", rulings[:-1]),
                             ("renamed", rulings[:-1] + (rulings[-1] + "-x",))):
            self.assertNotEqual([], vocabulary_mismatch(self.text, other),
                                f"the tuple {label} compared equal - not a set equality")

        dropped = with_body(self.text, _replace_once("`stop-ship`, ", ""))
        self.assertNotEqual([], vocabulary_mismatch(dropped, rulings),
                            "`not-stop-ship` stood in for `stop-ship` - a substring match")


if __name__ == "__main__":
    unittest.main()
