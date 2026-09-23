"""US0876: `sprint close` runs once and finishes - gaps become known issues, not refusals.

Driven through `sprint.main`, the shipped entry point, in throwaway project trees. Chain steps
this story is not about are stubbed green; each test leaves real the step whose outcome it
judges.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

sprint = loader.load_script("sprint")


def _live(name: str):
    """The module the close resolves at call time - its own steps through
    `sys.modules[__name__]`, its siblings through lazy imports - whatever `sys.modules` holds
    NOW, imported only when first needed. A sibling suite that loads a script by path replaces
    that entry, so a module held from import time is where a patch lands unread, and loading a
    sibling early pins it to modules later suites replace."""
    return sys.modules.get(name) or importlib.import_module(name)


def _state(root: Path, **over) -> dict:
    state = {
        "schema": 1, "run_id": "RUN-LEAN0001", "started_at": "2026-09-23T00:00:00Z",
        "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0101"],
        "handoff": None, "appetite": {"minutes": 240.0, "units": 8},
        "sprint_goal": "the close finishes in one pass",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"},
    }
    state.update(over)
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")
    return state


def _story(root: Path) -> Path:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    path = d / "US0101-widget.md"
    path.write_text(
        "# US0101: widget\n\n> **Status:** Review\n> **Points:** 3\n> **Epic:** EP0001\n"
        "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
        "- **Verify:** shell true\n", encoding="utf-8")
    return path


def _retro(root: Path) -> None:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    (d / "RETRO0001-lean.md").write_text(
        "# RETRO-0001: lean\n\n> **Date:** 2026-09-23\n\n## Delivered\n\n- US0101 - shipped\n\n"
        "## Lessons\n\n- learned a thing\n", encoding="utf-8")
    (d / "_index.md").write_text(
        "# Retro Registry\n\n**Last Updated:** 2026-09-23\n\n| ID | Title | Date |\n"
        "| --- | --- | --- |\n| [RETRO-0001](RETRO0001-lean.md) | lean | 2026-09-23 |\n",
        encoding="utf-8")


def _fixture(root: Path, **over) -> None:
    _state(root, **over)
    _story(root)
    _retro(root)


def _green_steps(mod, real: tuple[str, ...] = ()) -> contextlib.ExitStack:
    """Every chain step but those in `real` stubbed green, and the report holds cleared."""
    stack = contextlib.ExitStack()
    stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
    for name in mod._CLOSE_CHAIN:
        if name not in real:
            stack.enter_context(unittest.mock.patch.object(
                mod, "_close_" + name.replace("-", "_"),
                lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
    return stack


def _close(root: Path, *extra: str, real: tuple[str, ...] = ()) -> tuple[int, str, str]:
    mod = _live("sprint")
    out, err = io.StringIO(), io.StringIO()
    with _green_steps(mod, real), contextlib.redirect_stdout(out), \
            contextlib.redirect_stderr(err):
        rc = mod.main(["close", "--retro", "RETRO0001", *extra, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _read(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())


#: Two compulsory items left unanswered, in the shape `sprint_report.checklist` returns.
_UNANSWERED = {
    "items": [
        {"id": "goal-seat-reviewed", "title": "the goal was read by a seat", "value": "no",
         "detail": ""},
        {"id": "lessons-recorded", "title": "the retro records its lessons", "value": "no",
         "detail": "no lesson row names this run"},
        {"id": "retro-filed", "title": "the retro is filed", "value": "yes", "detail": ""},
    ],
    "outstanding": ["goal-seat-reviewed", "lessons-recorded"],
    "expired": [], "stop_ship": [], "pending_in_close": [],
}


class OnePassCloseTests(unittest.TestCase):

    def test_close_finishes_in_one_pass_with_gaps_as_known_issues(self) -> None:
        """Mutant: restore the chain's early return on a failed step, or record the checklist as
        one opaque row instead of one row per unanswered item."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            # the retro is on disk but not in its index: filing it is the close's job
            index = root / "sdlc-studio" / "retros" / "_index.md"
            index.write_text(index.read_text().replace(
                "| [RETRO-0001](RETRO0001-lean.md) | lean | 2026-09-23 |\n", ""), encoding="utf-8")
            with unittest.mock.patch.object(_live("sprint_report"), "checklist",
                                            lambda *a, **k: _UNANSWERED):
                rc, out, err = _close(root, real=("checklist", "handoff"))
            self.assertEqual(0, rc, err)
            state = _read(root)
            self.assertTrue(state.get("report"), "no report was filed")
            self.assertTrue(state.get("handoff"), "no handover was filed")
            self.assertIn("RETRO0001-lean.md", index.read_text(), "the retro was not filed")
            report = _live("sprint_report").read_report(root, state["report"])
            self.assertEqual("RETRO0001", report["retro_id"], "the report is not the retro's")
            self.assertIn("handed over on the report", out)
            issues = state["close_known_issues"]
            # one row per unanswered item, plus the unit the run cannot end over (US0101 has
            # no adversarial pass in this fixture) - each its own known issue
            self.assertEqual(
                ["goal-seat-reviewed", "lessons-recorded", "known-issues"],
                [i["detail"].split(":")[0] for i in issues if i["source"] == "checklist"],
                issues)
            self.assertIn("sprint.py sign", out)

    def test_a_failing_gate_lane_is_a_known_issue_not_a_refusal(self) -> None:
        """Mutant: the gate step's failure returns non-zero, or the lane is not named."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)

            def red_gate(argv):
                print("  [FAIL] conformance: US0101 does not conform to its template")
                return 1

            with unittest.mock.patch.object(_live("gate"), "main", red_gate):
                rc, _out, err = _close(root, real=("gate",))
            self.assertEqual(0, rc, err)
            issues = _read(root)["close_known_issues"]
            self.assertIn({"source": "gate",
                           "detail": "conformance: US0101 does not conform to its template"},
                          issues)

    def test_an_early_refusal_is_not_a_counted_attempt(self) -> None:
        """Mutant: count the attempt before the goal-verdict refusal, or keep capping attempts
        at `review.max_rounds`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, sprint_goal_verdict=None)
            rc, _out, err = _close(root)
            self.assertNotEqual(0, rc)
            self.assertIn("goal-verdict", err)
            self.assertFalse(_read(root).get("close_attempts"), "a refusal was counted")
            # Now a run past any cap: three recorded attempts against a cap of one.
            cfg = root / "sdlc-studio" / ".config.yaml"
            cfg.write_text("review:\n  max_rounds: 1\n", encoding="utf-8")
            prior = [{"at": "2026-09-22T00:00:00Z", "outstanding": 5, "stages": ["gate"]}] * 3
            _state(root, close_attempts=prior)
            rc, _out, err = _close(root)
            self.assertEqual(0, rc, err)
            self.assertEqual(4, len(_read(root)["close_attempts"]))

    def test_a_dirty_tree_still_refuses(self) -> None:
        """Mutant: drop the batch-repair refusal along with the others."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            env = gitutil.git_env()
            for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
                subprocess.run(["git", "-C", str(root), *argv], env=env, check=True,
                               capture_output=True)
            (root / "src" / "widget.py").write_text("x = 2\n", encoding="utf-8")
            # the close's own git calls must see the fixture, never an inherited GIT_DIR
            with unittest.mock.patch.dict(os.environ, env, clear=True):
                rc, _out, err = _close(root)
            self.assertEqual(2, rc)
            self.assertIn("src/widget.py", err)
            self.assertIsNone(_read(root).get("report"))


#: A stop-ship ruling beside two unanswered items, in the shape `sprint_report.checklist` returns.
_STOP_SHIP = {**_UNANSWERED, "stop_ship": ["BG0009"]}


def _known_issue_rows(root: Path, report_id: str) -> list[dict]:
    report = _live("sprint_report").read_report(root, report_id)
    section = next(s for s in report["sections"] if s["key"] == "known_issues")
    return [{k: f["value"] for k, f in row.items()} for row in section["rows"]]


class KnownIssueDetailTests(unittest.TestCase):
    """The review's findings 3, 4 and the D0257 stop-ship ruling."""

    def test_every_detail_line_of_a_failed_step_is_its_own_known_issue(self) -> None:
        """Mutant: keep only the step's last line, so review-coverage names no unit and
        retro-validate records one missing section of several."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            (root / "sdlc-studio" / "retros" / "RETRO0001-lean.md").write_text(
                "# RETRO-0001: lean\n\n> **Date:** 2026-09-23\n", encoding="utf-8")
            rc, _out, err = _close(root, real=("review-coverage", "retro-validate"))
            self.assertEqual(0, rc, err)
            issues = _read(root)["close_known_issues"]
            coverage = [i["detail"] for i in issues if i["source"] == "review-coverage"]
            self.assertTrue(any("US0101" in row for row in coverage), coverage)
            missing = [i["detail"] for i in issues if i["source"] == "retro-validate"
                       and "missing section" in i["detail"]]
            self.assertGreaterEqual(len(missing), 2, issues)
            self.assertEqual(len(missing), len(set(missing)), "one row per section")
            # the full step detail is printed, not only the rows: the placement line is neither
            # the step's first line nor its last
            self.assertIn("finding placement:", err)

    def test_the_handover_is_claimed_only_when_the_report_was_filed(self) -> None:
        """Mutant: print "handed over on the report" whether or not a report was filed."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            with unittest.mock.patch.object(_live("sprint"), "_file_the_report",
                                            lambda *a, **k: ("", "")):
                rc, out, err = _close(root, real=("review-coverage",))
            self.assertEqual(0, rc, err)
            self.assertTrue(_read(root)["close_known_issues"])
            self.assertNotIn("handed over on the report", out)
            self.assertIn("no report was filed", out)

    def test_a_stop_ship_ruling_is_a_known_issue_listed_first_on_the_report(self) -> None:
        """D0257. Mutant: the stop-ship row keeps its chain position, loses its STOP-SHIP mark,
        or hides the unanswered items the checklist also found."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            with unittest.mock.patch.object(_live("sprint_report"), "checklist",
                                            lambda *a, **k: _STOP_SHIP):
                # review-coverage runs first and fails, so the stop-ship row is not first by
                # chain order - only the ordering rule can put it there
                rc, _out, err = _close(root, real=("review-coverage", "checklist", "handoff"))
            self.assertEqual(0, rc, err)
            state = _read(root)
            issues = state["close_known_issues"]
            self.assertNotEqual("checklist", issues[0]["source"])
            stop = [i for i in issues if i.get("stop_ship")]
            self.assertEqual(1, len(stop), issues)
            self.assertIn("BG0009", stop[0]["detail"])
            details = [i["detail"] for i in issues]
            self.assertTrue(any(d.startswith("lessons-recorded") for d in details), details)
            rows = _known_issue_rows(root, state["report"])
            self.assertEqual("STOP-SHIP", rows[0]["issue_priority"], rows)
            self.assertIn("BG0009", rows[0]["issue_detail"])
            self.assertEqual(1, sum(r["issue_priority"] == "STOP-SHIP" for r in rows))


if __name__ == "__main__":
    unittest.main()
