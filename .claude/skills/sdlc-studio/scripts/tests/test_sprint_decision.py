"""`sprint.py decision defer --block` on a bug, through the shipped entry point.

A bug has no Blocked status, so the block is held on the run state, as a field any unit may
carry, and `decision list` shows it beside the bug's own status.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")
status = loader.load_script("status")

STATE_REL = Path("sdlc-studio") / ".local" / "run-state.json"


def _main(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(list(argv))
    return rc, out.getvalue(), err.getvalue()


def _bug(root: Path, num: int) -> Path:
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"BG{num:04d}-x.md"
    path.write_text(f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Low\n"
                    "> **Points:** 1\n> **Affects:** src/thing.py\n\n## Acceptance Criteria\n\n"
                    "- [ ] **AC1** it works\n  - **Verify:** manual look\n", encoding="utf-8")
    return path


def _open_run(root: Path, batch: list[str]) -> None:
    state = {"schema": 1, "run_id": "RUN-TEST0001", "started_at": "2026-07-16T00:00:00Z",
             "ended_at": None, "outcome": "running", "goal": "done", "batch": batch,
             "plan": "sdlc-studio/.local/sprint-plan.json", "handoff": None,
             "appetite": {"minutes": 240.0, "units": 8}, "sprint_goal": "hold it honestly"}
    (root / STATE_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / STATE_REL).write_text(json.dumps(state), encoding="utf-8")


def _status(root: Path) -> list[str]:
    """The dashboard's lines naming a held unit, through `status.py pillars`."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        rc = status.main(["pillars", "--root", str(root)])
    assert rc == 0, out.getvalue()
    return [ln for ln in out.getvalue().splitlines() if ln.startswith("Blocked:")]


def _defer(root: Path, unit: str, *extra: str) -> tuple[int, str, str]:
    return _main("decision", "defer", "--unit", unit, "--question", f"Which way for {unit}?",
                 "--option", "a|the first way", "--option", "b|the second way",
                 "--root", str(root), *extra)


class DeferBlockTests(unittest.TestCase):

    def test_a_deferred_bug_is_shown_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            held, free = _bug(root, 1), _bug(root, 2)
            _open_run(root, ["BG0001", "BG0002", "BG0003"])
            _bug(root, 3)
            rc, out, err = _defer(root, "BG0001", "--block")
            self.assertEqual(0, rc, err)
            self.assertNotIn("NOT marked Blocked", out + err)
            self.assertIn("BG0001 held Blocked on the run state", out)
            self.assertIn("Status stays Open", out)
            # the bug's own file still carries a status its type has
            self.assertIn("> **Status:** Open", held.read_text(encoding="utf-8"))
            # the control: deferred without --block, so held by its question alone
            rc, out, err = _defer(root, "BG0002")
            self.assertEqual(0, rc, err)
            self.assertNotIn("Blocked", out)

            state = json.loads((root / STATE_REL).read_text(encoding="utf-8"))
            self.assertEqual(["BG0001"], state["blocked_units"])
            self.assertEqual([True, False], [p["blocked"] for p in state["pending_decisions"]])

            rc, out, err = _main("decision", "list", "--root", str(root))
            self.assertEqual(0, rc, err)
            self.assertIn("[1] BG0001 (Open, BLOCKED on the run state): Which way for BG0001?",
                          out)
            self.assertIn("[2] BG0002 (Open): Which way for BG0002?", out)
            rc, out, err = _main("decision", "list", "--format", "json", "--root", str(root))
            self.assertEqual(0, rc, err)
            listed = json.loads(out)
            self.assertEqual([("BG0001", True, "Open"), ("BG0002", False, "Open")],
                             [(p["unit"], p["blocked"], p["status"]) for p in listed])
            # and in status, the dashboard every session starts from
            held = _status(root)
            self.assertEqual(1, len(held), held)
            self.assertTrue(held[0].startswith("Blocked:      BG0001 (Open) - held by "), held)

            # answered, the block goes with the question
            rc, out, err = _main("decision", "resolve", "--index", "1", "--choice", "a",
                                 "--root", str(root))
            self.assertEqual(0, rc, err)
            state = json.loads((root / STATE_REL).read_text(encoding="utf-8"))
            self.assertEqual([], state["blocked_units"])
            rc, out, err = _main("decision", "list", "--root", str(root))
            self.assertNotIn("BLOCKED", out)
            self.assertEqual([], _status(root))
            self.assertIn("> **Status:** Open", free.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
