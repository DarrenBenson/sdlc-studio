"""US0981 (CR0607, D0297): a carry bug filed at the review cap does not count against the
triage session cap.

`critic.carry_at_cap` filed the carry bug through the same triage counter as a new finding, so
six carries in RUN-01M3VF2J consumed six of the run's twenty-finding allowance, and a carry at a
full session was refused outright. A carry records a review outcome, not a new finding.

Driven through `critic.py record` and `file_finding.py file`, the shipped entry points, in a
throwaway workspace with its own triage session. Nothing reads this repository's own state.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import file_finding  # noqa: E402
import triage_noise  # noqa: E402
from lib import run_state  # noqa: E402

UNIT = "US0001"


def _workspace(d: str) -> Path:
    root = Path(d)
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / f"{UNIT}-a-unit.md").write_text(
        f"# {UNIT}: a unit\n\n> **Status:** Review\n> **Epic:** EP0001\n> **Points:** 3\n"
        f"> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n"
        f"- [ ] **AC1** the parser keeps every row\n  - **Verify:** shell true\n",
        encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "unit.py").write_text("x = 1\n", encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "review:\n  require_brief_provenance: false\n"
        "triage:\n  enabled: true\n  session_cap: 2\n  low_consolidation: false\n",
        encoding="utf-8")
    return root


def _run(module, argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            rc = module.main(argv)
        except SystemExit as exc:
            rc = exc.code
    return rc, buf.getvalue()


def _file(root: Path, title: str) -> tuple[int, str]:
    """One ordinary finding, filed through the shipped CLI."""
    return _run(file_finding, [
        "file", "--type", "bug", "--title", title, "--severity", "medium",
        "--summary", "s", "--steps", "r", "--fix", "f", "--affects", "src/unit.py",
        "--points", "1", "--root", str(root)])


def _reject(root: Path, issues: str) -> tuple[int, str]:
    return _run(critic, ["record", "--unit", UNIT, "--verdict", "REJECT", "--reviewer", "rev-a",
                         "--author", "builder", "--issues", issues, "--root", str(root)])


class CarryBugUncappedTests(unittest.TestCase):
    def setUp(self) -> None:
        env = mock.patch.dict(os.environ, {
            run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts-for-tests",
            "SDLC_TRIAGE_SESSION": "us0981-session"})
        env.start()
        self.addCleanup(env.stop)

    def test_a_carry_bug_is_filed_past_the_cap_and_not_counted(self) -> None:
        """AC1. MUTANT: HEAD's `carry_at_cap`, which files through the counted path - the carry
        is refused at the full session (the REJECT row is written, then `CarryFailed`). MUTANT:
        file the carry past the cap but still count it - the count reads 3, not 2. The third
        ordinary finding is the control: the cap still refuses what it exists to refuse."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            self.assertTrue(triage_noise.active(root), "premise: the triage controls are live")
            for n in (1, 2):
                rc, out = _file(root, f"ordinary finding {n}")
                self.assertEqual(0, rc, out)
            self.assertEqual(2, triage_noise.session_count(root), "premise: the session is full")
            run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
            self.assertEqual(0, _reject(root, "[new] the parser drops a row")[0])
            rc, out = _reject(root, "[new] the parser still drops the last row")
            self.assertEqual(0, rc, f"the carry at the cap was refused:\n{out}")
            carried = [p for p in (root / "sdlc-studio" / "bugs").glob("BG*.md")
                       if "did not converge in review" in p.read_text(encoding="utf-8")]
            self.assertEqual(1, len(carried), f"no carry bug was filed:\n{out}")
            self.assertEqual(2, triage_noise.session_count(root),
                             "the carry bug counted against the triage session")
            rc, out = _file(root, "ordinary finding 3")
            self.assertNotEqual(0, rc, f"a third ordinary finding was filed past the cap:\n{out}")
            self.assertIn("triage session cap reached", out)


if __name__ == "__main__":
    unittest.main()
