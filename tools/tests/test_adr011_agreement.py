"""US0457: ADR-011 states the breakdown gate's REAL firing rule, and carries its amendment.

The ADR read as an unconditional refusal - "with any ungroomed unit in the batch, `sprint plan`
exits non-zero and prints no plan at all" - while the code had already been made goal-aware and
exempted one rung. A reader deciding whether to groom before planning got the wrong answer from
the document, and the ADR's `Status: Accepted` carried no sign it had been qualified at all.

The exempt set is DERIVED from `sprint._ungroomed_blocks_at`, so adding or removing an exemption
in the code reddens this guard rather than leaving the ADR unchallenged.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"
DECISIONS = REPO / "sdlc-studio" / "decisions.md"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))


def _sprint():
    spec = importlib.util.spec_from_file_location("sprint_us0457", SCRIPTS / "sprint.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint_us0457"] = mod
    spec.loader.exec_module(mod)
    return mod


def _adr_block() -> str:
    """ADR-011, extracted by its own heading. RAISES when the heading is gone - an empty block
    satisfies every absence rule and every containment check below it."""
    text = TRD.read_text(encoding="utf-8")
    i = text.find("### ADR-011")
    assert i != -1, "no ADR-011 heading in trd.md - the ADR was renamed or removed"
    rest = text[i:]
    m = re.search(r"^### ADR-012", rest, re.M)
    return rest[:m.start()] if m else rest


def _decision_row(rid: str, path: Path | None = None) -> str:
    for line in (path or DECISIONS).read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(f"| {rid} "):
            return line
    raise AssertionError(f"no {rid} row in decisions.md - the decision this guard cites cannot "
                         f"be resolved, and a deleted decision must not read as a compliant one")


def _declared_exempt() -> set:
    """The exempt set ADR-011 declares, from its machine-readable marker.

    A marker rather than prose, because a search for a backticked rung name is satisfied by
    every rung the paragraph mentions - which is all of them."""
    block = _adr_block()
    m = re.search(r"<!--\s*exempt-rungs:\s*(.*?)\s*-->", block)
    assert m, ("ADR-011 declares no `<!-- exempt-rungs: ... -->` marker, so the exempt set it "
               "states cannot be compared with the gate's")
    return {g.strip() for g in m.group(1).split(",") if g.strip()}


def _exempt_goals(sprint) -> set:
    """The goals at which an ungroomed batch is ACCEPTED, read from the gate itself."""
    exempt = set()
    for goal in sprint.GOALS:
        if not sprint._ungroomed_blocks_at(argparse.Namespace(goal=goal)):
            exempt.add(goal)
    return exempt


#: The three unreadable-goal cases the gate refuses, and the words ADR-011 must use to state
#: them TOGETHER. Three separate searches over the whole block passed on prose that was already
#: there for another reason - "an absent config BLOCKS and an unknown mode falls back to
#: enforce" carries two of these - so the whole D0062 fail-safe sentence could be deleted green.
_FAIL_SAFE_TERMS = ("absent", "empty", "ladder", "block")


def _sentences(block: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", block))


def _fail_safe_sentence(block: str) -> str | None:
    """The ONE sentence in which an absent, an empty and an off-ladder goal all block.

    A sentence rather than a block, because the claim is a conjunction: each case alone is
    stated elsewhere in the ADR about something else, and what a reader needs is the statement
    that all three close the escape.
    """
    for sentence in _sentences(block):
        low = sentence.lower()
        if all(term in low for term in _FAIL_SAFE_TERMS):
            return sentence
    return None


def _close_calls_grooming_report(case: unittest.TestCase, sprint, goal: str) -> list:
    """Run the close's review-anchor step over a throwaway root and REPORT what it reached.

    OBSERVED, not read off the source. `assertIn("grooming_report", inspect.getsource(...))` is
    a substring over source text: replacing the call with a comment that merely names it
    survives, which is the mutant US0457 AC3 says must redden. A spy on the module global -
    which is how the call resolves - can only fire if the call happens.
    """
    calls: list = []
    real = sprint.grooming_report

    def spy(root, batch):
        calls.append((str(root), list(batch)))
        return real(root, batch)

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / "stories" / "US0001-groomed.md").write_text(
            "# US0001: g\n\n> **Status:** Ready\n> **Affects:** a.py\n> **Points:** 3\n",
            encoding="utf-8")
        state = {"run_id": "RUN-FIXTURE", "outcome": "goal-reached",
                 "batch": ["US0001"], "goal": goal}
        sprint.grooming_report = spy
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                ok, msg, _hint = sprint._close_review_anchor(root, None, state)
        finally:
            sprint.grooming_report = real
    case.assertTrue(ok, f"the close's review-anchor step failed on the fixture: {msg}")
    return calls


class Adr011StatesTheFiringRule(unittest.TestCase):

    def test_the_exempt_goal_set_in_the_adr_is_derived_from_the_gate(self) -> None:
        sprint = _sprint()
        exempt = _exempt_goals(sprint)
        self.assertTrue(exempt, "no goal is exempt at all - if the gate has genuinely become "
                                "unconditional, this guard and the ADR must change together")
        # An EXACT comparison against the set the ADR declares. Searching the prose for a
        # backticked rung name passed however the gate behaved, because every rung is named
        # somewhere in the paragraph - caught by a mutant that exempted a second rung.
        declared = _declared_exempt()
        self.assertEqual(exempt, declared,
                         f"the gate exempts {sorted(exempt)} and ADR-011 declares "
                         f"{sorted(declared)} - the document and the code disagree about which "
                         f"rung accepts an ungroomed batch")

    def test_an_unreadable_goal_blocks_in_both_the_gate_and_the_adr(self) -> None:
        """The escape must not open merely because the rung could not be read - the property
        the function's own docstring commits to."""
        sprint = _sprint()
        for args in (argparse.Namespace(), argparse.Namespace(goal=""),
                     argparse.Namespace(goal="not-a-rung")):
            self.assertTrue(sprint._ungroomed_blocks_at(args),
                            f"the gate let an unreadable goal through: {vars(args)}")
        # ...and the ADR must state the same thing in ONE sentence. Word-presence over the whole
        # block was satisfied before the D0062 fail-safe sentence was even consulted, because
        # "an absent config BLOCKS and an unknown mode falls back to enforce" is in the Decision
        # for an unrelated reason - so deleting the fail-safe sentence outright survived.
        stated = _fail_safe_sentence(_adr_block())
        self.assertIsNotNone(
            stated,
            "no single sentence in ADR-011 says that an ABSENT goal, an EMPTY goal and a goal "
            "outside the ladder all BLOCK. The gate refuses all three, and a reader deciding "
            "whether to groom must be able to read that from one sentence rather than assemble "
            "it from words scattered through the ADR")

    def test_the_rendered_grooming_report_is_the_counterweight_the_adr_names(self) -> None:
        """The pure functions the close calls, over a fixture batch - and then the CALL from the
        close, because an exemption whose counterweight is unwired is an exemption nobody audits.
        """
        sprint = _sprint()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0001-groomed.md").write_text(
                "# US0001: g\n\n> **Status:** Ready\n> **Affects:** a.py\n> **Points:** 3\n",
                encoding="utf-8")
            (stories / "US0002-ungroomed.md").write_text(
                "# US0002: u\n\n> **Status:** Ready\n", encoding="utf-8")
            report = sprint.grooming_report(root, ["US0001", "US0002"])
            text = sprint.render_grooming_report(report)
        self.assertTrue(text.strip(), "the rendered report is empty")
        self.assertRegex(text, r"\d", "the report states no count of what the rung groomed")
        # The wiring: the close's review-anchor step must REACH it on the design rung. Observed
        # through a spy on the module global the call resolves through, because a substring over
        # `inspect.getsource` cannot tell a call from a comment that names one.
        self.assertTrue(_close_calls_grooming_report(self, sprint, "design"),
                        "the close does not render the grooming report, so the design "
                        "exemption has no counterweight behind it")
        self.assertIn("grooming_report", _adr_block(),
                      "ADR-011's Consequences do not name the close-side report as the "
                      "counterweight to the exemption")


class TheAgreementChecksDiscriminate(unittest.TestCase):
    """What each check refuses, pinned on its own. The real TRD and the real `sprint.py` agree
    today, so a green run against them shows only that they agree - not that the check would
    notice if they stopped."""

    #: The Decision paragraph as it stands, minus the D0062 fail-safe sentence. Deleting that
    #: sentence was a surviving mutant: two of the three words a word-presence check looked for
    #: are carried by the config sentence, which is about something else entirely.
    WITHOUT_THE_FAIL_SAFE = (
        "**Decision:** With any ungroomed unit in the batch, `sprint plan` exits non-zero. "
        "`sprint.breakdown: judgement` downgrades the lane to a report; an absent config BLOCKS "
        "and an unknown mode falls back to enforce.\n\n"
        "**Amended by D0062: the gate is GOAL-AWARE, and `design` is the only exemption.** "
        "An ungroomed batch is accepted at `--goal design` and refused at every other rung.\n")

    FAIL_SAFE = ("The exemption is deliberately narrow in the fail-safe direction: an ABSENT "
                 "goal, an EMPTY goal and a goal outside the ladder all BLOCK, so the escape "
                 "cannot open merely because the rung could not be read.")

    def test_deleting_the_fail_safe_sentence_is_refused(self) -> None:
        low = self.WITHOUT_THE_FAIL_SAFE.lower()
        self.assertIn("absent", low, "the fixture does not reproduce the words that survived")
        self.assertIn("block", low, "the fixture does not reproduce the words that survived")
        self.assertIsNone(
            _fail_safe_sentence(self.WITHOUT_THE_FAIL_SAFE),
            "an ADR with the D0062 fail-safe sentence deleted still satisfies the check, so it "
            "is pinned to words an unrelated sentence already carries")
        restored = self.WITHOUT_THE_FAIL_SAFE + "\n" + self.FAIL_SAFE + "\n"
        self.assertIsNotNone(_fail_safe_sentence(restored),
                             "the positive control fails: the check refuses the sentence it "
                             "exists to require, so the refusal above proves nothing")
        # ...and the three cases must sit in ONE sentence, not be assembled across the block.
        scattered = (self.WITHOUT_THE_FAIL_SAFE
                     + "\nAn empty goal is a case the ladder does not name.\n")
        self.assertIsNone(_fail_safe_sentence(scattered),
                          "words spread over two sentences satisfied the check")

    def test_the_close_calls_the_grooming_report_only_on_the_design_rung(self) -> None:
        """The counterweight is a REACHED call. A comment naming `grooming_report` where the
        call used to be leaves the exemption with nothing behind it while the source still spells
        the name, which is what the source-substring check could not tell apart."""
        sprint = _sprint()
        called = _close_calls_grooming_report(self, sprint, "design")
        self.assertTrue(called, "the design rung's close did not reach grooming_report")
        self.assertEqual([["US0001"]], [batch for _root, batch in called],
                         f"the close reached grooming_report with a batch it was not given: "
                         f"{called}")
        self.assertEqual([], _close_calls_grooming_report(self, sprint, "done"),
                         "a `done` rung rendered the design rung's counterweight, so the "
                         "observation is not about the rung the exemption applies to")


class Adr011AmendmentIsMarked(unittest.TestCase):

    def test_the_extracted_adr_block_carries_the_dated_d0062_amendment(self) -> None:
        """A reader who opens ADR-011 must see the decision is qualified. A bare
        `Status: Accepted` over an amended decision is the state this guard exists to catch."""
        block = _adr_block()
        status = re.search(r"^\*\*Status:\*\*\s*(.+)$", block, re.M)
        self.assertIsNotNone(status, "ADR-011 has no Status line")
        line = status.group(1)
        self.assertIn("D0062", line, f"the Status line does not cite the amendment: {line!r}")
        self.assertRegex(line, r"\d{4}-\d{2}-\d{2}", "the amendment carries no date")

    def test_the_history_row_cites_d0062_and_a_missing_row_fails_loud(self) -> None:
        row = _decision_row("D0062")
        decided = re.search(r"(\d{4}-\d{2}-\d{2})", row)
        self.assertIsNotNone(decided, "the D0062 row carries no date")
        history = [line for line in TRD.read_text(encoding="utf-8").splitlines()
                   if line.startswith("| 20") and "D0062" in line]
        self.assertTrue(history, "no TRD Revision History row cites D0062")
        stamped = re.match(r"\| (\d{4}-\d{2}-\d{2})", history[-1])
        self.assertIsNotNone(stamped, "the history row carries no date")
        self.assertGreaterEqual(stamped.group(1), decided.group(1),
                                "the history row predates the decision it cites")
        # ...and a decisions log without the row fails naming it.
        with tempfile.TemporaryDirectory() as d:
            stripped = Path(d) / "decisions.md"
            stripped.write_text("# Decisions\n\n| ID | Decision |\n| --- | --- |\n"
                                "| D0061 | other |\n", encoding="utf-8")
            with self.assertRaises(AssertionError) as ctx:
                _decision_row("D0062", stripped)
            self.assertIn("D0062", str(ctx.exception))

    def test_a_missing_adr_heading_fails_rather_than_comparing_nothing(self) -> None:
        real = globals()["TRD"]
        with tempfile.TemporaryDirectory() as d:
            empty = Path(d) / "trd.md"
            empty.write_text("# TRD\n\nno ADRs here\n", encoding="utf-8")
            globals()["TRD"] = empty
            try:
                with self.assertRaises(AssertionError) as ctx:
                    _adr_block()
                self.assertIn("ADR-011", str(ctx.exception))
            finally:
                globals()["TRD"] = real


if __name__ == "__main__":
    unittest.main()
