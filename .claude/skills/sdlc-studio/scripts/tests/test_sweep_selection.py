"""A test module or class marked `# test-selection: sweep` joins every commit's selection.

A sweep is a cheap test that reads the whole repository rather than one script: a census, a
claims check, a scan for a raw git call. No import, load, name or census subject ties it to the
file a commit changes, so selection by reach never picks it, and its red was first seen at review
or at the push gate. The marker sits in a module's first forty lines, the same head the census
subject is read from; naming a class runs only that class. Each marker records the seconds it was
measured at, and the marked set is held to a budget, because it is paid on every commit.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
REPO = SCRIPTS.parents[3]
sys.path.insert(0, str(SCRIPTS))

import gate  # noqa: E402

SKILL_TESTS = ".claude/skills/sdlc-studio/scripts/tests"
SPRINT = ".claude/skills/sdlc-studio/scripts/sprint.py"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _marker(rest: str) -> str:
    """A marker line, built here so this module's own source carries none at column 0."""
    return "# test-selection: " + rest + "\n"


def _fixture(root: Path) -> None:
    """Two suites: one module the sprint change reaches, one sweep that imports nothing changed,
    one bystander, and one module whose marker sits below the head and so marks nothing."""
    _write(root, f"{SKILL_TESTS}/test_sprint.py",
           "import sprint\n\n\ndef test_sprint():\n    assert sprint\n")
    _write(root, "tools/tests/test_sweep.py",
           '"""Reads the whole tree."""\n' + _marker("sweep 1.5s")
           + "\n\ndef test_tree():\n    assert True\n")
    _write(root, "tools/tests/test_bystander.py", "def test_b():\n    assert True\n")
    _write(root, "tools/tests/test_late_marker.py",
           "\n" * gate._CENSUS_HEAD_LINES + _marker("sweep 1.0s")
           + "\n\ndef test_late():\n    assert True\n")


class SweepSelectionTests(unittest.TestCase):

    def test_a_sweep_joins_every_commits_selection(self) -> None:
        """AC1. MUTANTS: select by imports, loads, name and census subject only; drop the sweeps
        on a change that reaches nothing; read a marker below the head; leave the reason silent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            code = gate.select_tests(str(root), [SPRINT])
            docs = gate.select_tests(str(root), ["docs/guide.md", "CHANGELOG.md"])
        self.assertTrue(code["resolved"], code)
        self.assertEqual([f"{SKILL_TESTS}/test_sprint.py", "tools/tests/test_sweep.py"],
                         code["selectors"],
                         "a sprint change must select what it reaches AND the sweep, nothing else")
        self.assertTrue(docs["resolved"], docs)
        self.assertEqual(["tools/tests/test_sweep.py"], docs["selectors"],
                         "a docs-only change must still run the sweep, and only the sweep")
        for got in (code, docs):
            self.assertRegex(got["reason"], r"\bsweeps?\b")
            self.assertIn("tools/tests/test_sweep.py", got["reason"],
                          "the reason must name the sweep it added")
            self.assertNotIn("test_late_marker", " ".join(got["selectors"]),
                             "a marker below the module's head marks nothing")
        self.assertEqual(3, docs["excluded"],
                         "the sprint test, the bystander and the late marker are excluded")

    def test_a_class_marker_selects_only_that_class(self) -> None:
        """AC2. MUTANTS: a class marker selecting the whole module; a class node added beside a
        module the change already selects whole; a node id pytest cannot collect."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "tools/tests/test_mixed.py",
                   '"""Mostly not a sweep."""\n' + _marker("sweep ScanTests 0.5s")
                   + "\nimport unittest\n\n\nclass OtherTests(unittest.TestCase):\n"
                   "    def test_other(self):\n        pass\n\n\n"
                   "class ScanTests(unittest.TestCase):\n"
                   "    def test_scan(self):\n        pass\n")
            docs = gate.select_tests(str(root), ["docs/guide.md"])
            reached = gate.select_tests(str(root), ["tools/tests/test_mixed.py"])
            unresolved = gate.unresolved_node_ids(docs["selectors"], str(root))
        self.assertEqual(["tools/tests/test_mixed.py::ScanTests"], docs["selectors"],
                         "a class marker must select that class's node id, not the module")
        self.assertEqual([], unresolved, "the class node id must collect")
        self.assertEqual(0, docs["excluded"], "a module a class of which runs is not excluded")
        self.assertEqual(["tools/tests/test_mixed.py"], reached["selectors"],
                         "a module the change selects whole carries no second class node")

    def test_the_repositorys_sweeps_are_marked_and_fit_the_budget(self) -> None:
        """AC3. MUTANTS: one named sweep unmarked; test_test_census.py's RealRepoTests (about
        250 s) marked; a marker with no recorded time read as zero."""
        markers = gate.sweep_markers(str(REPO))
        marked = {s for m in markers for s in m["selectors"]}
        expected = {
            "tools/tests/test_doc_claims.py",
            "tools/tests/test_precommit_floor_pending.py",
            f"{SKILL_TESTS}/test_root_census.py",
            "tools/tests/test_skill_tests_env.py::ScrubSiteSweepTests",
            f"{SKILL_TESTS}/test_gitutil.py::UnconfinedRawGitCallSweepTests",
            "tools/tests/test_commit_msg_hook.py::HookInvocationHermeticityTests",
        }
        self.assertEqual(set(), expected - marked, "a named sweep carries no marker")
        self.assertEqual([], [s for s in marked if s.startswith("tools/tests/test_test_census.py")],
                         "test_test_census.py runs at push, never on every commit")
        for selector in marked:
            path, _, cls = selector.partition("::")
            if cls:
                text = (REPO / path).read_text(encoding="utf-8")
                self.assertRegex(text, rf"(?m)^class {re.escape(cls)}\b",
                                 f"{selector}: the marker names a class the module lacks")
        budget = gate.sweep_budget(markers)
        self.assertEqual([], budget["unrecorded"], "a sweep with no recorded time")
        self.assertLessEqual(budget["seconds"], gate.SWEEP_BUDGET_SECONDS)
        self.assertEqual(30, gate.SWEEP_BUDGET_SECONDS)
        self.assertTrue(budget["within"], budget)
        # An unrecorded time is named, never counted as zero: the same set with one time lost.
        lost = [dict(m, seconds=None) if i == 0 else m for i, m in enumerate(markers)]
        lost_budget = gate.sweep_budget(lost)
        self.assertEqual(markers[0]["selectors"], lost_budget["unrecorded"])
        self.assertFalse(lost_budget["within"], "a missing time must not pass as zero")


if __name__ == "__main__":
    unittest.main()
