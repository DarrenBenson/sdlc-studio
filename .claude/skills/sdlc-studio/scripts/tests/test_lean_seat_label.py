"""BG0726: the report labels no reviewer `NO DECLARED SEAT` on a project that declares none.

`critic.seat_for` answers None both for a reviewer matching no declared seat and for every
reviewer on a project with no seat cards, and the review-attribution row rendered both as the
reviewer's omission. The row now carries the seat parenthetical only where seats are declared.
Runs `sprint_report.py checklist` in a temporary tree.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))

RETRO = ("# RETRO-9100: a sprint\n\n> **Batch:** US0001\n\n## Delivered\n- shipped\n\n"
         "## What went well\n- good\n\n## What was hard / what stalled\n- hard\n\n"
         "## Lessons\n- a real lesson worth keeping for next time\n")


def _tree(root: Path) -> None:
    (root / "sdlc-studio" / "retros").mkdir(parents=True)
    (root / "sdlc-studio" / ".local").mkdir(parents=True)
    (root / "sdlc-studio" / "retros" / "RETRO9100-t.md").write_text(RETRO, encoding="utf-8")
    (root / "sdlc-studio" / "stories").mkdir()
    (root / "sdlc-studio" / "stories" / "US0001-s.md").write_text(
        "# US0001: s\n\n> **Status:** Done\n> **Points:** 3\n", encoding="utf-8")
    (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
        {"schema": 1, "run_id": "RUN-TEST01", "started_at": "2026-01-01T00:00:00Z",
         "outcome": "running", "batch": ["US0001"], "batch_changes": []}), encoding="utf-8")
    import critic  # noqa: PLC0415
    critic.record_verdict(root, "US0001", "APPROVE", reviewer="Priya Raman", author="builder",
                          issues="probed")


def _row(root: Path) -> dict:
    r = subprocess.run([sys.executable, str(_SCRIPTS / "sprint_report.py"), "--root", str(root),
                        "checklist", "--id", "RETRO9100", "--format", "json"],
                       capture_output=True, text=True, timeout=300)
    return next(i for i in json.loads(r.stdout)["items"] if i["id"] == "review-attribution")


class SeatLabelTests(unittest.TestCase):

    def test_a_persona_less_project_is_not_reported_as_a_reviewer_omission(self) -> None:
        """MUTANTS: (1) HEAD - `(NO DECLARED SEAT)` on a project with no cards; (2) the label
        dropped everywhere - a reviewer matching none of the declared seats is no longer
        reported (the positive control)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root)
            bare = _row(root)
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "qa.md").write_text("# Sam Okoro\n\n<!-- role: qa -->\n", encoding="utf-8")
            declared = _row(root)
        self.assertIn("US0001 by Priya Raman", bare["detail"])
        self.assertNotIn("NO DECLARED SEAT", bare["detail"])
        self.assertIn("US0001 by Priya Raman (NO DECLARED SEAT)", declared["detail"])


if __name__ == "__main__":
    unittest.main()
