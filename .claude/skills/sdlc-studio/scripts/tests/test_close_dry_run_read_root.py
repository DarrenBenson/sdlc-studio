"""BG1058: the close's dry run names no unit the live unanswered-unit predicate answers.

The dry run judges a scratch copy holding only `sdlc-studio/`. The unanswered-unit hold asks the
seal's own bar of each batch unit, and that bar reads the unit's risk band from its Affects files
and, for a light-tier APPROVE on a unit the band now tiers full, git history: neither is in the
copy. So a bug whose light APPROVE meets the bar on the real tree read `unfinished and not ruled`
in the preview. Driven through `sprint.main(["close", "--dry-run"])` on the lean close fixture,
with the real checklist step (its compulsory items answered) and every other step stubbed green.

MUTANT, which the test fails on: the hold asks the seal bar of the scratch copy again.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture and its green chain, shared

BUG = "BG0101"
ANSWERED = {"items": [{"id": "retro-filed", "title": "the retro is filed", "value": "yes",
                       "detail": ""}],
            "outstanding": [], "expired": [], "stop_ship": [], "pending_in_close": []}


def _approved_bug(root: Path) -> None:
    """An Open bug in the batch, touching one small file, with an independent light APPROVE."""
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "fix.py").write_text("x = 1\n", encoding="utf-8")
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{BUG}-fix.md").write_text(
        f"# {BUG}: a fix\n\n> **Status:** Open\n> **Severity:** Medium\n> **Points:** 1\n"
        "> **Affects:** src/fix.py\n\n## Acceptance Criteria\n\n- [ ] **AC1** it works\n"
        "  - **Verify:** shell true\n", encoding="utf-8")
    critic = lean._live("critic")
    ledger = critic.verdicts_path(root)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(critic.HEADER + f"| {BUG} | APPROVE | Rowan Hart (qa) | Dani Okafor "
                      "(engineering) | 2026-09-23 | abc123 | light | - | - |\n", encoding="utf-8")


class DryRunReadRootTests(unittest.TestCase):

    def test_the_dry_run_names_no_unit_the_live_predicate_answers(self) -> None:
        mod = lean._live("sprint")
        critic = lean._live("critic")
        report = lean._live("sprint_report")
        pre = {"blockers": [], "ready": True, "gate_ran": True}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            root.mkdir()
            # The APPROVE is this run's: its review base is the bug's row count before it.
            lean._fixture(root, batch=[BUG], review_base={BUG: 0})
            _approved_bug(root)
            state = mod.run_state.read(root)
            # The premise, on both trees: the real tree meets the seal bar, the copy does not.
            self.assertEqual([], mod.seal_bar_unmet(root, BUG))
            self.assertEqual([], mod.unanswered_units(root, state, "RETRO0001")["unanswered"],
                             "the live predicate must answer the bug, or nothing is under test")
            copy = Path(d) / "copy"
            shutil.copytree(root / "sdlc-studio", copy / "sdlc-studio")
            self.assertEqual(("light", "full"),
                             (critic.tier_for(root, BUG), critic.tier_for(copy, BUG)),
                             "the copy must tier the bug differently, or the read root is moot")
            self.assertTrue(mod.seal_bar_unmet(copy, BUG))
            out = io.StringIO()
            with lean._green_steps(mod, real=("checklist",)), \
                    unittest.mock.patch.object(mod, "close_preflight", lambda *a, **k: pre), \
                    unittest.mock.patch.object(report, "checklist", lambda *a, **k: ANSWERED), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = mod.main(["close", "--retro", "RETRO0001", "--dry-run", "--root", str(root)])
        text = out.getvalue()
        self.assertNotIn("known-issues", text,
                         f"the preview holds a unit the live predicate answers:\n{text}")
        self.assertNotIn(BUG, text, text)
        self.assertIn("ok   checklist:", text, text)
        self.assertEqual(0, rc, text)


if __name__ == "__main__":
    unittest.main()
