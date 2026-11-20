"""The goal-review brief reads the live run, not the plan snapshot.

A persona the run declares with `plan --serves` reaches the brief's Goal serves line and its
personas designed for, whatever the goal's own wording traces to; and the batch line counts the
live run's batch, units added with `sprint batch add` after `plan --write` included.

Driven through `sprint.main`, the shipped entry point, in throwaway trees built on the goal-trace
fixture.
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
import test_lean_goal_trace as s1  # noqa: E402 - the plannable project with persona cards

sprint = loader.load_script("sprint")

_SERVED = ("# Hana Ito\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
           "| **Cast role** | Served |\n\n## Who They Are\n\nAffected, never a user.\n\n"
           "## End Goals\n\n1. Hear about a change before it lands\n")
_BUG = ("# {id}: b\n\n> **Status:** Open\n> **Severity:** Medium\n> **Affects:** src/{f}.py\n"
        "> **Points:** 1\n\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
        "- **Given** the recorded state\n- **Verify:** shell true\n")


def _fixture(root: Path) -> None:
    """S1's project (BG0001; Maya Okafor Primary, Trevor Hale Negative), a Served card, and two
    more bugs to add to the batch after the plan is written."""
    s1._project(root)
    (root / "sdlc-studio" / "personas" / "hana-ito.md").write_text(_SERVED, encoding="utf-8")
    for uid, f in (("BG0002", "b"), ("BG0003", "c")):
        (root / "src" / f"{f}.py").write_text("", encoding="utf-8")
        (root / "sdlc-studio" / "bugs" / f"{uid}-x.md").write_text(_BUG.format(id=uid, f=f),
                                                                   encoding="utf-8")


def _run(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        rc = sprint.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _plan(root: Path, goal: str, *extra: str) -> None:
    rc, _out, err = _run(root, "plan", "--worklist", str(root / "worklist.txt"),
                         "--sprint-goal", goal, "--no-fetch", "--write", *extra)
    assert rc == 0, err


def _brief(root: Path) -> str:
    rc, out, err = _run(root, "goal-review", "brief")
    assert rc == 0, err
    return out


def _serves_line(brief: str) -> str:
    return next(ln for ln in brief.splitlines() if ln.startswith("Goal serves"))


def _designed_for(brief: str) -> list[str]:
    """The persona headings listed under `Personas designed for`."""
    lines = brief.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("Personas designed for")),
                 None)
    if start is None:
        return []
    out = []
    for ln in lines[start + 1:]:
        if not ln.startswith("  "):
            break
        if not ln.startswith("    ") and not ln.strip().endswith("declined: the product does "
                                                                   "not design for them"):
            out.append(ln.strip())
    return out


class ServesTests(unittest.TestCase):

    def test_serves_declared_at_plan_reaches_the_brief(self) -> None:
        """Mutants: trace only the goal's own wording; list only Primary and Secondary personas
        as designed for; read a closed run's declaration."""
        for goal, traced in (("every open bug is fixed", []),
                             ("Maya Okafor sees every open bug fixed", ["Maya Okafor (Primary)"])):
            with self.subTest(goal=goal), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _fixture(root)
                _plan(root, goal, "--serves", "Hana Ito")
                brief = _brief(root)
                line = _serves_line(brief)
                self.assertTrue(line.startswith("Goal serves (the plan's own trace): "), line)
                for label in ["Hana Ito (Served)", *traced]:
                    self.assertIn(label, line)
                self.assertIn("Hana Ito (Served):", _designed_for(brief))
                at = brief.splitlines().index("  Hana Ito (Served):")
                self.assertEqual(brief.splitlines()[at + 1].strip(),
                                 "1. Hear about a change before it lands")
                # A closed run's declaration is not the run under review: a brief of a batch
                # after the close does not carry it.
                state = root / "sdlc-studio" / ".local" / "run-state.json"
                record = json.loads(state.read_text(encoding="utf-8"))
                state.write_text(json.dumps({**record, "outcome": "goal-reached"}),
                                 encoding="utf-8")
                rc, out, err = _run(root, "goal-review", "brief", "--goal", goal,
                                    "--brief-worklist", str(root / "worklist.txt"))
                self.assertEqual(rc, 0, err)
                self.assertNotIn("Hana Ito (Served)", _serves_line(out))
                self.assertNotIn("Hana Ito (Served):", _designed_for(out))
        # Negative control: no declaration, so the Served card is neither traced nor listed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            _plan(root, "every open bug is fixed")
            brief = _brief(root)
            self.assertTrue(_serves_line(brief).startswith("Goal serves: NONE"), brief)
            self.assertNotIn("Hana Ito (Served):", _designed_for(brief))


class BatchLineTests(unittest.TestCase):

    def test_batch_line_reads_the_live_run(self) -> None:
        """Mutants: count the plan snapshot's batch; count the live batch before the adds."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            _plan(root, "every open bug is fixed")
            self.assertRegex(_brief(root), r"(?m)^Batch: 1 unit\(s\), ")
            for uid in ("BG0002", "BG0003"):
                rc, _out, err = _run(root, "batch", "add", uid, "--reason", "found mid-run")
                self.assertEqual(rc, 0, err)
            batch = re.findall(r"(?m)^Batch: .*$", _brief(root))
            self.assertEqual(len(batch), 1, batch)
            self.assertRegex(batch[0], r"^Batch: 3 unit\(s\), ")


if __name__ == "__main__":
    unittest.main()
