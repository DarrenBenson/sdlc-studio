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
import importlib.util
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
        block = _adr_block().lower()
        for word in ("absent", "empty", "block"):
            self.assertIn(word, block,
                          f"ADR-011 does not say an {word} goal case is refused")

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
        # The wiring: the close's review-anchor step must reach it on the design rung.
        import inspect
        src = inspect.getsource(sprint._close_review_anchor)
        self.assertIn("grooming_report", src,
                      "the close does not render the grooming report, so the design "
                      "exemption has no counterweight behind it")
        self.assertIn("grooming_report", _adr_block(),
                      "ADR-011's Consequences do not name the close-side report as the "
                      "counterweight to the exemption")


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
