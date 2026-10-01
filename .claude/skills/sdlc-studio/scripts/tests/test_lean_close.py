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
    """Every chain step but those in `real` stubbed green, and the report holds cleared unless
    `real` names `report-holds`."""
    stack = contextlib.ExitStack()
    if "report-holds" not in real:
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
                rc, out, err = _close(root, real=("checklist",))
            self.assertEqual(0, rc, err)
            state = _read(root)
            self.assertTrue(state.get("report"), "no report was filed")
            self.assertIsNone(state.get("handoff"), "the close filed a handover (US0967)")
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
            # the full step detail is printed, not only the rows: its first and last lines both
            self.assertIn("covered by an independent pass", err)
            self.assertIn("The close certifies that a review happened", err)

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
                rc, _out, err = _close(root, real=("review-coverage", "checklist"))
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


def _cli(name: str, *argv: str) -> str:
    """Run a sibling script's `main` quietly, returning its stdout; a non-zero exit fails."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live(name).main(list(argv))
    if rc:
        raise AssertionError(f"{name} {' '.join(argv)} exited {rc}:\n{out.getvalue()}"
                             f"{err.getvalue()}")
    return out.getvalue()


def _fresh_run(root: Path, *, done: bool) -> tuple[str, str]:
    """A fresh `init` project whose only epic holds one story, the run's whole batch. With
    `done` the story reaches Done through the real gates (verified, reviewed, transitioned)."""
    _cli("init", "--root", str(root), "run")

    def new(*argv: str) -> str:
        return json.loads(_cli("artifact", "new", *argv, "--root", str(root),
                               "--format", "json"))["id"]

    eid = new("--type", "epic", "--title", "Calculator", "--summary", "adds numbers")
    uid = new("--type", "story", "--epic", eid, "--title", "A user can add numbers",
              "--points", "1", "--affects", "src/calc.py", "--ac", "the module exists",
              "--verify", "shell test -f src/calc.py")
    (root / "src").mkdir()
    (root / "src" / "calc.py").write_text("def add(a, b):\n    return a + b\n", "utf-8")
    for status in ("Ready", "In Progress"):
        _cli("transition", "set", "--id", uid, "--status", status, "--root", str(root))
    if done:
        _cli("verify_ac", "run", "--id", uid, "--root", str(root))
        _cli("critic", "record", "--unit", uid, "--verdict", "approve", "--reviewer",
             "Reviewer; agent; v1", "--author", "Builder; agent; v1", "--root", str(root))
        _cli("transition", "set", "--id", uid, "--status", "Done", "--root", str(root))
    _state(root, batch=[uid])
    _retro(root)
    return eid, uid


class CloseDriftTests(unittest.TestCase):
    """BG0799: the report hands over the drift the close could not settle, one row per item."""

    def test_the_close_does_not_hand_over_drift_it_settles(self) -> None:
        """AC1. Mutant: derive the run's parent epics only in the tail, after the reconcile step
        and the report holds have read drift (HEAD: five rows for one item the close settled)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            eid, _uid = _fresh_run(root, done=True)
            rc, out, err = _close(root, real=("reconcile", "report-holds"))
            self.assertEqual(0, rc, err)
            self.assertIn("reconcile: ok", out, "the reconcile step did not run clean")
            epic = next((root / "sdlc-studio" / "epics").glob(f"{eid}-*.md"))
            self.assertIn("> **Status:** Done", epic.read_text(encoding="utf-8"))
            state = _read(root)
            rows = [r["issue_detail"] for r in _known_issue_rows(root, state["report"])]
            self.assertEqual([], [r for r in rows if "epic-status-stale" in r], rows)

    def test_one_drift_item_is_one_known_issue(self) -> None:
        """AC2. Mutant: split the reconcile step's stdout per line (HEAD), which carries the
        `scope=` summary and the `Guidance:` block as issues; or carry the index-drift hold
        beside the step's own row, which names the one item twice."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            eid, uid = _fresh_run(root, done=False)
            index = root / "sdlc-studio" / "stories" / "_index.md"
            text = index.read_text(encoding="utf-8")
            # the row AND its summary count, so the one drift item is the row's stale status
            edits = {f"| {eid} | In Progress |": f"| {eid} | Draft |",
                     "| Draft | 0 |": "| Draft | 1 |", "| In Progress | 1 |": "| In Progress | 0 |"}
            for old, new in edits.items():
                self.assertEqual(1, text.count(old), text)
                text = text.replace(old, new)
            index.write_text(text, encoding="utf-8")
            _per_type, items = _live("reconcile").detect_all(root)
            self.assertEqual([("status-mismatch", uid)], [(i["kind"], i["id"]) for i in items])
            rc, _out, err = _close(root, real=("reconcile", "report-holds"))
            self.assertEqual(0, rc, err)
            state = _read(root)
            carried = [i["detail"] for i in state["close_known_issues"]
                       if i["source"] == "reconcile"]
            self.assertEqual(1, len(carried), carried)
            self.assertIn(uid, carried[0])
            self.assertIn("status-mismatch", carried[0])
            rows = [r["issue_detail"] for r in _known_issue_rows(root, state["report"])]
            self.assertEqual(1, sum(uid in r and "status-mismatch" in r for r in rows), rows)
            self.assertFalse([r for r in rows if r.startswith(("scope=", "Guidance:", "- "))],
                             rows)


def _preflight_lines(err: str) -> list[str]:
    """The pre-flight's listed rows, from its headline to the first line that is not a row."""
    lines = err.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("close pre-flight:")), None)
    if start is None:
        return []
    rows = []
    for ln in lines[start + 1:]:
        if not ln.startswith("  "):
            break
        rows.append(ln)
    return rows


class PreflightTests(unittest.TestCase):
    """BG0800: the pre-flight lists only what this invocation leaves unmet."""

    def test_the_preflight_lists_nothing_this_invocation_answers(self) -> None:
        """AC1. Mutant: evaluate the pre-flight before the verdict the invocation supplies, or
        list the review anchor the close's own review-anchor step writes (HEAD)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, sprint_goal_verdict=None)
            self.assertFalse((root / "sdlc-studio" / "reviews" / "LATEST.md").exists())
            rc, _out, err = _close(root, "--goal-verdict", "achieved", "--note", "it did")
            self.assertEqual(0, rc, err)
            rows = _preflight_lines(err)
            self.assertFalse([r for r in rows if "[goal-verdict]" in r], rows)
            self.assertFalse([r for r in rows if "goal-judged" in r], rows)
            self.assertFalse([r for r in rows if "review-current" in r], rows)
            # the positive control: an item the verdict does not answer is still listed
            self.assertTrue([r for r in rows if "[checklist] closing-review" in r], rows)
            self.assertEqual("achieved", _read(root)["sprint_goal_verdict"]["verdict"])

    def test_a_filing_close_lists_what_it_neither_records_nor_writes(self) -> None:
        """Round-2 review. `--file-and-close` records no verdict and never writes the review
        anchor. Mutant: apply the review-current skip on that path too (it then read ready and
        closed the run with no anchor), or read its verdict as supplied."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, sprint_goal_verdict=None)
            _rc, _out, err = _close(root, "--file-and-close", "--goal-verdict", "achieved",
                                    "--note", "it did")
            rows = _preflight_lines(err)
            self.assertTrue([r for r in rows if "review-current" in r], err)
            self.assertTrue([r for r in rows if "[goal-verdict]" in r], err)
            self.assertFalse((root / "sdlc-studio" / "reviews" / "LATEST.md").exists())

    def test_the_dry_run_reads_the_supplied_verdict_as_the_close_does(self) -> None:
        """Round-2 review. Mutant: the preview judges the goal unjudged although the close it
        previews records the verdict first; or it records that verdict on the real tree."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, sprint_goal_verdict=None)
            # the retro names its batch, so the checklist reads this run's goal
            retro = root / "sdlc-studio" / "retros" / "RETRO0001-lean.md"
            retro.write_text(retro.read_text(encoding="utf-8").replace(
                "> **Date:** 2026-09-23\n", "> **Date:** 2026-09-23\n> **Batch:** US0101\n"),
                encoding="utf-8")
            mod = _live("sprint")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                given = json.dumps(mod.close_dry_run(root, "RETRO0001", goal_verdict="achieved"))
                bare = json.dumps(mod.close_dry_run(root, "RETRO0001"))
            self.assertIn("goal-judged", bare)
            self.assertIn("the Sprint Goal is unjudged", bare)
            self.assertNotIn("goal-judged", given)
            self.assertNotIn("the Sprint Goal is unjudged", given)
            self.assertIsNone(_read(root).get("sprint_goal_verdict"), "the preview wrote")
            # and through the shipped entry point, which hands the dry run the verdict
            for extra, unjudged in (((), True), (("--goal-verdict", "achieved", "--note", "n"),
                                                 False)):
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    mod.main(["close", "--dry-run", "--retro", "RETRO0001", *extra,
                              "--root", str(root)])
                self.assertEqual(unjudged, "the Sprint Goal is unjudged" in out.getvalue(),
                                 out.getvalue())
            self.assertIsNone(_read(root).get("sprint_goal_verdict"), "the preview wrote")

    def test_a_close_given_no_verdict_still_lists_it(self) -> None:
        """AC2. Mutant: drop the goal-verdict item from the pre-flight altogether, or read a
        verdict the close refuses to record (no --note) as answered."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, sprint_goal_verdict=None)
            for extra, want_rc in (((), 1), (("--goal-verdict", "achieved"), 2)):
                rc, _out, err = _close(root, *extra)
                self.assertEqual(want_rc, rc, err)
                rows = _preflight_lines(err)
                self.assertTrue([r for r in rows if "[goal-verdict]" in r], err)


if __name__ == "__main__":
    unittest.main()
