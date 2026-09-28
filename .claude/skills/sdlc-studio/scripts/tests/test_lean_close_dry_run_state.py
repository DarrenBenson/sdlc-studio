"""BG0823: `sprint close --dry-run` reads the open run, and labels what it did on its copy.

The preview scaffolded its retro in the scratch copy with `artifact.py new`, which fills no
Batch line, so every checklist row that finds its run through the retro's units read no goal,
no units and no start time for a run whose state held all three - while the real close moments
later scaffolded a retro titled with the goal and naming both units. The preview now mints its
retro through the close's own scaffold. Its reconcile step derived a parent epic on the copy and
printed `close: derived EP0001 terminal` exactly as a real close does; every line a step prints
while it acts on the copy is now marked `[copy]`.

Driven through `sprint.main`, the shipped entry point, in throwaway project trees.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402 - git confined to the fixture

GOAL = "widgets ship to the operator"
UNITS = ("US0101", "US0102")


def _live(name: str):
    """The module the close resolves at call time, whatever `sys.modules` holds now."""
    return sys.modules.get(name) or importlib.import_module(name)


def _fixture(root: Path, status: str) -> None:
    """An open run with a goal, a start time and two batch units at `status`, each carrying an
    independent APPROVE, under an epic whose breakdown names both."""
    gitutil.git(["init", "-q"], root)
    sd = root / "sdlc-studio" / "stories"
    sd.mkdir(parents=True)
    critic = _live("critic")
    for uid in UNITS:
        (sd / f"{uid}-widget.md").write_text(
            f"# {uid}: widget\n\n> **Status:** {status}\n> **Points:** 2\n> **Epic:** EP0001\n\n"
            "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
            encoding="utf-8")
        critic.record_verdict(root, uid, "APPROVE", reviewer="qa-seat", author="builder",
                              issues="probed the edges; none blocking")
    ed = root / "sdlc-studio" / "epics"
    ed.mkdir(parents=True)
    (ed / "EP0001-widgets.md").write_text(
        "# EP0001: widgets\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
        + "".join(f"- [x] [{u}: x](../stories/{u}-widget.md)\n" for u in UNITS),
        encoding="utf-8")
    state = {"schema": 1, "run_id": "RUN-LEAN0823", "started_at": "2026-09-28T00:00:00Z",
             "ended_at": None, "outcome": "running", "goal": "done", "batch": list(UNITS),
             "handoff": None, "sprint_goal": GOAL}
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")


def _dry_run(root: Path) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main(["close", "--dry-run", "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class CloseDryRunStateTests(unittest.TestCase):

    def test_the_preview_reads_the_open_run(self) -> None:
        """AC1. MUTANTS: HEAD's `artifact.py new --type retro` scaffold, which fills no Batch;
        a scaffold that fills the Goal line but not the Batch."""
        report_mod = _live("sprint_report")
        seen: list[dict] = []
        real = report_mod.report

        def spy(*a, **k):
            rep = real(*a, **k)
            seen.append(rep)
            return rep

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, "Review")
            with unittest.mock.patch.object(report_mod, "report", spy):
                _rc, out, err = _dry_run(root)
            self.assertTrue(seen, f"the preview composed no report:\n{out}{err}")
            rep = seen[-1]
            self.assertEqual(GOAL, rep.get("sprint_goal"), out)
            self.assertEqual(sorted(UNITS), sorted(rep.get("units") or []), out)
            rows = {r["id"]: r for r in rep["checklist"]["items"]}
            self.assertNotEqual("no goal to judge", rows["goal-judged"]["value"])
            attribution = f"{rows['review-attribution']['value']} " \
                          f"{rows['review-attribution']['detail']}"
            for uid in UNITS:
                self.assertIn(uid, attribution)
            self.assertNotIn("no start time", rows["known-issues"]["detail"])
            # and the operator's reading of the preview agrees
            for said in ("no goal to judge", "the batch named no units",
                         "carries no start time"):
                self.assertNotIn(said, out + err)
            # the preview wrote nothing to the real tree
            self.assertFalse((root / "sdlc-studio" / "retros").exists())

    def test_copy_actions_are_labelled(self) -> None:
        """AC2. MUTANTS: HEAD's bare step call, whose `close: derived EP0001 terminal` reads as
        done; a mark on stdout that leaves stderr bare."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, "Done")
            _rc, out, err = _dry_run(root)
            derived = [ln for ln in out.splitlines() if "derived EP0001" in ln]
            self.assertTrue(derived, f"the preview derived nothing on its copy:\n{out}")
            for line in derived:
                self.assertTrue(line.startswith("[copy] "), line)
            # THE CONTROL: the real epic is untouched - the derivation happened on the copy.
            epic = (root / "sdlc-studio" / "epics" / "EP0001-widgets.md").read_text("utf-8")
            self.assertIn("> **Status:** In Progress", epic)
        # A step writing to stderr on the copy is marked too.
        sprint = _live("sprint")

        def noisy(root, retro, state, **_k):
            print("close: wrote a thing", file=sys.stderr)
            return True, "ok", ""

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, "Review")
            with unittest.mock.patch.object(sprint, "_close_reconcile", noisy):
                _rc, _out, err = _dry_run(root)
            self.assertIn("[copy] close: wrote a thing", err.splitlines())


if __name__ == "__main__":
    unittest.main()
