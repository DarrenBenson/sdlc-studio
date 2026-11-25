"""`sprint close --file-and-close` never drops a supplied `--goal-verdict` without saying so.

The filing exit records no verdict. Given one, the close refuses before anything is filed,
naming the flag it would have ignored and the command that records it, so an operator does not
re-read a command that looks complete. Driven through `sprint.main` in throwaway project trees,
with the close chain's steps stubbed green.
"""
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")


def _live(name: str):
    """The module the close resolves at call time, whatever `sys.modules` holds now."""
    return sys.modules.get(name) or importlib.import_module(name)


def _fixture(root: Path) -> None:
    """An open run with a sprint goal and no verdict, one story in review, and a filed retro."""
    state = {
        "schema": 1, "run_id": "RUN-FAC00001", "started_at": "2026-11-24T00:00:00Z",
        "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0101"],
        "handoff": None, "appetite": {"minutes": 240.0, "units": 8},
        "sprint_goal": "the close says what it ignores", "sprint_goal_verdict": None,
    }
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    (stories / "US0101-widget.md").write_text(
        "# US0101: widget\n\n> **Status:** Review\n> **Points:** 3\n> **Epic:** EP0001\n"
        "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
        "- **Verify:** shell true\n", encoding="utf-8")
    retros = root / "sdlc-studio" / "retros"
    retros.mkdir(parents=True, exist_ok=True)
    (retros / "RETRO0001-fac.md").write_text(
        "# RETRO-0001: fac\n\n> **Date:** 2026-11-24\n\n## Delivered\n\n- US0101 - shipped\n\n"
        "## Lessons\n\n- learned a thing\n", encoding="utf-8")
    (retros / "_index.md").write_text(
        "# Retro Registry\n\n**Last Updated:** 2026-11-24\n\n| ID | Title | Date |\n"
        "| --- | --- | --- |\n| [RETRO-0001](RETRO0001-fac.md) | fac | 2026-11-24 |\n",
        encoding="utf-8")


def _run(root: Path, *argv: str) -> tuple[int, str, str]:
    """`sprint.main(argv)` with every close chain step stubbed green."""
    mod = _live("sprint")
    out, err = io.StringIO(), io.StringIO()
    with contextlib.ExitStack() as stack:
        stack.enter_context(unittest.mock.patch.object(mod, "_report_holds",
                                                       lambda *a, **k: []))
        for name in mod._CLOSE_CHAIN:
            stack.enter_context(unittest.mock.patch.object(
                mod, "_close_" + name.replace("-", "_"),
                lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
        stack.enter_context(contextlib.redirect_stdout(out))
        stack.enter_context(contextlib.redirect_stderr(err))
        rc = mod.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _state(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())


def _filed(root: Path) -> list[str]:
    crs = root / "sdlc-studio" / "change-requests"
    return sorted(p.name for p in crs.glob("CR*.md")) if crs.is_dir() else []


#: The refusal's own words: the flag it would have ignored, and the path it refuses.
_IGNORED = "--goal-verdict is ignored with --file-and-close"


class FileAndCloseGoalVerdictTests(unittest.TestCase):

    def test_a_supplied_verdict_not_silently_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            rc, _out, err = _run(root, "close", "--retro", "RETRO0001", "--file-and-close",
                                 "--goal-verdict", "achieved", "--note", "it did")
            self.assertEqual(2, rc, err)
            refusal = [ln for ln in err.splitlines() if _IGNORED in ln]
            self.assertEqual(1, len(refusal), err)
            self.assertIn("nothing was filed", refusal[0])
            self.assertIn("sprint.py goal-verdict --verdict achieved", err)
            self.assertNotIn("file-and-close REFUSED", err)     # refused before the filing
            state = _state(root)
            self.assertIsNone(state.get("sprint_goal_verdict"))
            self.assertFalse(state.get("deferred_blockers"))
            self.assertEqual([], _filed(root))
            # the verdict without its note is ignored by the filing path all the same
            rc, _out, err = _run(root, "close", "--retro", "RETRO0001", "--file-and-close",
                                 "--goal-verdict", "missed")
            self.assertEqual(2, rc, err)
            self.assertIn(_IGNORED, err)
            self.assertIn("sprint.py goal-verdict --verdict missed", err)
        with tempfile.TemporaryDirectory() as d:
            # the positive control: the verdict recorded first, the filing close goes on
            root = Path(d)
            _fixture(root)
            rc, _out, err = _run(root, "goal-verdict", "--verdict", "achieved", "--note", "ok")
            self.assertEqual(0, rc, err)
            _rc, _out, err = _run(root, "close", "--retro", "RETRO0001", "--file-and-close")
            self.assertNotIn(_IGNORED, err)
            self.assertNotIn("[goal-verdict]", err)
            self.assertEqual("achieved", _state(root)["sprint_goal_verdict"]["verdict"])


if __name__ == "__main__":
    unittest.main()
