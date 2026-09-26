"""BG0776: `sprint sign --principal` refuses a principal that names nobody.

The guard used to strip the raw string, so `-` passed it while the id normaliser the
independence check compares with reads `-` as empty: the run was sealed with a signature that
named no principal. Driven through `sprint.main`, the shipped entry point, in a throwaway run
whose batch is empty, so nothing is stubbed and the seal is the real one.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
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


def _closed_run(root: Path) -> None:
    """A run the close prepared: it names its report and a goal verdict, and is not sealed."""
    state = {
        "schema": 1, "run_id": "RUN-BG0776", "started_at": "2026-09-26T00:00:00Z",
        "ended_at": None, "outcome": "running", "goal": "done", "batch": [],
        "handoff": None, "report": "RPT0001", "sprint_goal": "sign names its principal",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"},
    }
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")


def _read(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())


def _sign(root: Path, principal: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(["sign", "--report", "RPT0001", "--principal", principal,
                          "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class SignPrincipalTests(unittest.TestCase):

    def test_a_principal_that_normalises_to_empty_is_refused(self) -> None:
        """Mutant: check the raw string for emptiness (`principal.strip()`) before the id
        normaliser runs, so `-` and `_` pass the guard and the run is sealed unnamed."""
        for principal in ("-", "  ", "_"):
            with self.subTest(principal=principal), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _closed_run(root)
                rc, out, err = _sign(root, principal)
                self.assertNotEqual(0, rc, out)
                self.assertIn(f"sign REFUSED: --principal {principal!r}", err)
                state = _read(root)
                self.assertEqual("running", state["outcome"])
                self.assertIsNone(state.get("signature"))

    def test_a_real_principal_still_seals(self) -> None:
        """Mutant: a guard that refuses every principal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _closed_run(root)
            rc, out, err = _sign(root, "Darren Benson")
            self.assertEqual(0, rc, err)
            self.assertIn("signed by Darren Benson", out)
            state = _read(root)
            self.assertEqual("goal-reached", state["outcome"])
            self.assertEqual("Darren Benson", state["signature"]["principal"])


if __name__ == "__main__":
    unittest.main()
