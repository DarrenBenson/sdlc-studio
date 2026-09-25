"""US0927: a sprint plan names the PRD outcome or persona its goal serves, and flags a goal that
serves none - advice at the one approval the operator gives, never a refusal (D0266, LC-008).

Driven through `sprint.main`, the shipped entry point, in throwaway project trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

_O1 = "Maya ships features through a disciplined lifecycle (End goal 1)"
_O2 = "Maya knows the true state of the work after any reset (End goal 2)"
_PRD = (f"# Product Requirements Document\n\n## 1. Project Overview\n\nA tool.\n\n"
        f"## Outcomes\n\n- **O1:** {_O1}\n- **O2:** {_O2}\n\n"
        f"## 3. Feature Inventory\n\n- **O7:** not an outcome, a later section\n")
_CARD = ("# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
         "| **Cast role** | {role} |\n\n## Who They Are\n\nSomebody.\n")
_AC = ("\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n")


def _project(root: Path, *, prd: str | None = _PRD,
             personas: tuple[tuple[str, str], ...] = (("Maya Okafor", "Primary"),
                                                      ("Trevor Hale", "Negative"))) -> Path:
    """A plannable project with one bug; returns the worklist path."""
    (root / "src").mkdir(parents=True)
    (root / "src" / "a.py").write_text("", encoding="utf-8")
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    (bugs / "BG0001-x.md").write_text(
        "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** src/a.py\n> **Points:** 2\n{_AC}", encoding="utf-8")
    if prd is not None:
        (root / "sdlc-studio" / "prd.md").write_text(prd, encoding="utf-8")
    if personas:
        pdir = root / "sdlc-studio" / "personas"
        pdir.mkdir(parents=True)
        for name, role in personas:
            slug = name.lower().replace(" ", "-")
            (pdir / f"{slug}.md").write_text(_CARD.format(name=name, role=role),
                                             encoding="utf-8")
    worklist = root / "worklist.txt"
    worklist.write_text("BG0001\n", encoding="utf-8")
    return worklist


def _plan(root: Path, goal: str, *extra: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    argv = ["plan", "--worklist", str(root / "worklist.txt"), "--sprint-goal", goal,
            "--no-fetch", *extra, "--root", str(root)]
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        rc = sprint.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _json(root: Path, goal: str, *extra: str) -> dict:
    rc, out, err = _plan(root, goal, *extra, "--format", "json")
    assert rc == 0, err
    return json.loads(out)


def _serves_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith("goal serves:")]


class GoalTraceTests(unittest.TestCase):

    def test_serves_names_a_prd_outcome_with_its_text(self) -> None:
        """Mutant: echo the --serves flag without reading the PRD's outcome text."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            data = _json(root, "every open bug is fixed", "--serves", "O2")
            trace = data["goal_trace"]
            self.assertFalse(trace["flagged"])
            self.assertEqual([{"kind": "outcome", "id": "O2", "text": _O2}], trace["serves"])
            rc, out, err = _plan(root, "every open bug is fixed", "--serves", "O2")
            self.assertEqual(0, rc, err)
            self.assertIn(f"goal serves: O2 - {_O2}", _serves_lines(out))

    def test_a_goal_that_names_a_persona_or_outcome_is_traced(self) -> None:
        """Mutant: read only --serves, or match a persona name as a substring."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            for goal in ("Maya's open bugs are fixed", "Maya Okafor sees every bug fixed"):
                trace = _json(root, goal)["goal_trace"]
                self.assertFalse(trace["flagged"], goal)
                self.assertEqual([{"kind": "persona", "name": "Maya Okafor",
                                   "role": "primary"}], trace["serves"], goal)
            trace = _json(root, "every open bug is fixed, advancing O1")["goal_trace"]
            self.assertEqual([{"kind": "outcome", "id": "O1", "text": _O1}], trace["serves"])
            self.assertFalse(trace["flagged"])
            # a whole word, not a substring: neither Mayan nor O10 is a trace
            trace = _json(root, "the Mayan calendar bug is fixed per O10")["goal_trace"]
            self.assertEqual([], trace["serves"])
            self.assertTrue(trace["flagged"])
            rc, out, _err = _plan(root, "Maya Okafor sees every bug fixed")
            self.assertEqual(0, rc)
            self.assertIn("goal serves: Maya Okafor (Primary)", _serves_lines(out))

    def test_a_goal_serving_none_is_flagged_and_never_refused(self) -> None:
        """Mutant: refuse (non-zero) a goal serving none, or omit the NONE line."""
        results = {}
        for label, goal, extra in (("traced", "every open bug is fixed", ("--serves", "O1")),
                                   ("none", "every open bug is fixed", ()),
                                   ("o9", "every open bug is fixed", ("--serves", "O9"))):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root)
                rc, out, err = _plan(root, goal, *extra, "--write")
                # the batch as written, its temp root masked so two trees compare equal
                plan = json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json")
                                  .read_text(encoding="utf-8").replace(str(root), "<root>"))
                results[label] = (rc, out, err, plan)
        rc_t, _out_t, _err_t, plan_t = results["traced"]
        self.assertEqual(0, rc_t)
        self.assertFalse(plan_t["goal_trace"]["flagged"])
        for label in ("none", "o9"):
            rc, out, err, plan = results[label]
            self.assertEqual(rc_t, rc, err)
            self.assertEqual(plan_t["batch"], plan["batch"])
            self.assertTrue(plan["goal_trace"]["flagged"])
            lines = _serves_lines(out)
            self.assertEqual(1, len(lines), out)
            line = lines[0]
            self.assertTrue(line.startswith("goal serves: NONE"), line)
            for could in ("O1", "O2", "Maya Okafor"):
                self.assertIn(could, line)
            self.assertNotIn("Trevor Hale", line)   # never offered as a goal to serve
        _rc, out, _err, plan = results["o9"]
        self.assertEqual(["O9"], plan["goal_trace"]["unknown"])
        self.assertIn("the PRD lists no outcome O9", out)
        self.assertNotIn("no outcome", results["none"][1])

    def test_a_goal_serving_only_the_negative_persona_is_flagged(self) -> None:
        """Mutant: count any named persona as served, whatever its cast role."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            data = _json(root, "Trevor Hale gets an approval chain")
            trace = data["goal_trace"]
            self.assertTrue(trace["flagged"])
            self.assertEqual([{"kind": "persona", "name": "Trevor Hale", "role": "negative"}],
                             trace["serves"])
            rc, out, err = _plan(root, "Trevor Hale gets an approval chain", "--serves",
                                 "Trevor Hale")
            self.assertEqual(0, rc, err)
            lines = _serves_lines(out)
            self.assertEqual(1, len(lines), out)
            self.assertIn("NONE", lines[0])
            self.assertIn("Trevor Hale (Negative)", lines[0])
            self.assertIn("declines to design for", lines[0])
            # the Negative persona beside a served one is not a flag
            trace = _json(root, "Trevor Hale and Maya both see the tracker")["goal_trace"]
            self.assertFalse(trace["flagged"])

    def test_nothing_to_trace_against_prints_nothing(self) -> None:
        """Mutant: always print NONE, even where no outcome or persona could be named."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, prd="# PRD\n\n## 1. Project Overview\n\nNo outcomes here.\n",
                     personas=())
            data = _json(root, "every open bug is fixed")
            self.assertNotIn("goal_trace", data)
            rc, out, err = _plan(root, "every open bug is fixed", "--write")
            self.assertEqual(0, rc, err)
            self.assertEqual([], _serves_lines(out + err))
            written = json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json")
                                 .read_text(encoding="utf-8"))
            self.assertNotIn("goal_trace", written)
        # the shipped PRD template carries the section in the grammar the trace parses, once
        # filled: its unfilled `{{...}}` items are not outcomes (BG0765)
        template = (Path(sprint.__file__).resolve().parent.parent / "templates" / "core"
                    / "prd.md").read_text(encoding="utf-8")
        template = re.sub(r"\{\{[^}]*\}\}", "filled", template)
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            (Path(d) / "sdlc-studio" / "prd.md").write_text(template, encoding="utf-8")
            outcomes = sprint.prd_outcomes(d)
            self.assertEqual(["O1", "O2"], sorted(outcomes)[:2])
            self.assertTrue(all(text.strip() for text in outcomes.values()))


if __name__ == "__main__":
    unittest.main()
