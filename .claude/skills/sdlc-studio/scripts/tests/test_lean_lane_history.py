"""US0931: a build lane's brief carries the same file history its reviewer will see.

`sprint.py lane brief` renders the history section `critic.py brief` renders for the unit, from
the same function under D0266's bounds, and opens it with the prior-art instruction: run
`git log -S <symbol>` before changing a symbol you did not write, let the history outrank an
artefact's account, and do not read the artefact corpus in bulk. The Done-unit corpus behind it
is walked once per dispatch, not once per unit.

Every test builds a throwaway workspace and drives the shipped entry points in-process.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import backlog_triage  # noqa: E402
import critic  # noqa: E402
import sprint  # noqa: E402

HEADING = "History of the files this unit touches"
LEDGER_HEAD = ("# Critic Verdicts\n\n"
               "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- |\n")


def _unit(root: Path, uid: str, status: str, affects: list[str], date: str = "2026-01-01"
          ) -> None:
    """A story or bug whose criterion the lane contract can parse."""
    type_ = "bug" if uid.startswith("BG") else "story"
    d = root / "sdlc-studio" / ("bugs" if type_ == "bug" else "stories")
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{uid}-x.md").write_text(
        f"# {uid}: a change to {', '.join(affects)}\n\n> **Status:** {status}\n"
        f"> **Affects:** {', '.join(affects)}\n> **Points:** 2\n\n"
        "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        f"| {date} | sdlc-studio | {status} |\n", encoding="utf-8")


def _workspace(d: str) -> Path:
    root = Path(d)
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True)
    (seats / "qa.md").write_text("# QA seat\n", encoding="utf-8")
    (root / "src").mkdir()
    for name in ("a.py", "b.py", "c.py"):
        (root / "src" / name).write_text("x = 1\n", encoding="utf-8")
    # Four Done units on src/a.py: the per-file bound lists the newest three, so a second
    # implementation without it lists four.
    for uid, date in (("US0001", "2026-03-01"), ("US0002", "2026-03-02"),
                      ("US0003", "2026-03-03"), ("US0004", "2026-03-04")):
        _unit(root, uid, "Done", ["src/a.py"], date)
    _unit(root, "BG0001", "Fixed", ["src/b.py"], "2026-03-05")
    _unit(root, "US0005", "Done", ["src/c.py"], "2026-03-06")
    p = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
    p.parent.mkdir(parents=True)
    p.write_text(LEDGER_HEAD + "| US0004 | REJECT | qa-rev | dev | 2026-03-04 | abcdef012345 | "
                 "full | [new] the walk read every artefact twice [LC-002] |\n",
                 encoding="utf-8")
    return root


def _run(main, argv: list[str]) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    if rc != 0:
        raise AssertionError(f"{argv[:2]} refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _lane_brief(root: Path, *units: str) -> str:
    return _run(sprint.main, ["lane", "brief", "--units", *units, "--root", str(root)])


def _review_brief(root: Path, unit: str) -> str:
    return _run(critic.main, ["brief", "--unit", unit, "--seat", "qa", "--tier", "full",
                              "--root", str(root)])


def _section(brief: str, unit: str | None = None) -> list[str]:
    """The history section's rendered lines: the heading line and the entry lines under it. With
    `unit`, the section of that unit's brief within a multi-unit lane dispatch."""
    lines = brief.splitlines()
    if unit is not None:
        start = next(i for i, ln in enumerate(lines) if ln.startswith(f"Unit: {unit} "))
        end = next((i for i, ln in enumerate(lines) if i > start and ln.startswith("Unit: ")),
                   len(lines))
        lines = lines[start:end]
    starts = [i for i, ln in enumerate(lines) if ln.startswith(HEADING)]
    if len(starts) != 1:
        raise AssertionError(f"expected one history section, found {len(starts)}")
    out = [lines[starts[0]]]
    for ln in lines[starts[0] + 1:]:
        if not (ln.startswith("- ") or ln.startswith("  - ")):
            break
        out.append(ln)
    return out


def _listed(section: list[str]) -> list[str]:
    return [m.group(1) for ln in section if (m := re.match(r"- ([A-Z]+\d+) ", ln))]


class LaneHistoryTests(unittest.TestCase):

    def test_the_lane_and_review_briefs_carry_the_same_history(self) -> None:
        """AC1. MUTANTS: a lane-side list without the per-file bound (lists four on src/a.py);
        the history left out of the lane brief; the findings left out of the lane's copy."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _unit(root, "US0010", "Ready", ["src/a.py", "src/b.py"])
            lane = _section(_lane_brief(root, "US0010"))
            review = _section(_review_brief(root, "US0010"))
            self.assertEqual(review, lane)
            # Not two empty sections agreeing: the bound applied, the bug on src/b.py ranked in,
            # and the recorded finding carried.
            self.assertEqual(["BG0001", "US0004", "US0003", "US0002"], _listed(lane))
            self.assertIn("  - [new] the walk read every artefact twice [LC-002]", lane)

    def test_the_history_section_carries_the_prior_art_instruction(self) -> None:
        """AC2. MUTANTS: no instruction; the instruction after the history or elsewhere in the
        brief; any of its three clauses dropped."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _unit(root, "US0010", "Ready", ["src/a.py"])
            # No prior unit changed src/d.py: the section is one line, still opened by it.
            _unit(root, "US0011", "Ready", ["src/d.py"])
            for unit in ("US0010", "US0011"):
                brief = _lane_brief(root, unit)
                lines = brief.splitlines()
                at = next(i for i, ln in enumerate(lines) if ln.startswith(HEADING))
                opener = lines[at - 1]
                self.assertIn("git log -S <symbol>", opener)
                self.assertIn("before changing a symbol you did not write", opener)
                self.assertIn("where an artefact and the history disagree, the history wins",
                              opener)
                self.assertIn("do not read the artefact corpus in bulk", opener)
                self.assertEqual(1, brief.count("git log -S"), "the instruction is not once")

    def test_the_corpus_is_walked_once_per_dispatch(self) -> None:
        """AC3. MUTANTS: render each unit's history outside a shared corpus cache (one walk per
        unit); walk the corpus although no unit needs it."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            for uid, f in (("US0010", "src/a.py"), ("US0011", "src/b.py"),
                           ("US0012", "src/c.py")):
                _unit(root, uid, "Ready", [f])
            corpus = len(list((root / "sdlc-studio").glob("*/*-x.md")))
            real = backlog_triage._last_date
            calls: list[int] = []

            def counted(*a, **k):
                calls.append(1)
                return real(*a, **k)

            with unittest.mock.patch.object(backlog_triage, "_last_date", counted):
                out = _lane_brief(root, "US0010", "US0011", "US0012")
            # The walk dates every unit once, so one walk is `corpus` calls and three are 3x.
            self.assertEqual(corpus, len(calls), f"{len(calls) / corpus:g} walks, not one")
            # Positive control: each brief did read the corpus it was walked for.
            self.assertEqual(["US0004", "US0003", "US0002"], _listed(_section(out, "US0010")))
            self.assertEqual(["BG0001"], _listed(_section(out, "US0011")))
            self.assertEqual(["US0005"], _listed(_section(out, "US0012")))


if __name__ == "__main__":
    unittest.main()
