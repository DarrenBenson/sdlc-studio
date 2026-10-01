"""BG0861: the delivery-batch span is retired, and the close no longer reports a finding placement.

US0918 removed the last caller of `run_state.start_batch`, so no span was ever opened again: every
finding was stamped as raised outside a batch, and the close's `finding placement` clause was fed
by nothing. The span API, the filer's attribution to it and the clause are deleted. The
`Raised-in-batch` stamp stays, because `sprint_report` and `close_owed` read its timestamp.

Driven through the shipped CLIs (`file_finding.py`, `sprint.py close --dry-run`) in a throwaway
project tree.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from lib import run_state  # noqa: E402

#: The shape the stamp's readers look for: an ISO-8601 UTC moment as the stamp's last token.
_ISO_TAIL = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _cli(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True,
                          text=True, timeout=300, check=False, env=_env())


def _fixture(root: Path) -> None:
    """An open run whose batch is one story, with a retro for the close to read."""
    state = {"schema": 1, "run_id": "RUN-LEAN0861", "started_at": "2026-09-30T00:00:00Z",
             "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0101"],
             "handoff": None, "sprint_goal": "the span is retired"}
    local = root / "sdlc-studio" / ".local"
    local.mkdir(parents=True)
    (local / "run-state.json").write_text(json.dumps(state), encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / "US0101-widget.md").write_text(
        "# US0101: widget\n\n> **Status:** Review\n> **Points:** 3\n> **Epic:** EP0001\n"
        "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
        "- **Verify:** shell true\n", encoding="utf-8")
    retros = root / "sdlc-studio" / "retros"
    retros.mkdir(parents=True)
    (retros / "RETRO0001-lean.md").write_text(
        "# RETRO-0001: lean\n\n> **Date:** 2026-09-30\n\n## Delivered\n\n- US0101 - shipped\n\n"
        "## Lessons\n\n- learned a thing\n", encoding="utf-8")


class BatchSpanRetiredTests(unittest.TestCase):
    """AC1."""

    def test_the_close_reports_no_finding_placement_and_the_span_api_is_gone(self) -> None:
        """MUTANTS: (1) keep the close's placement clause - its text is printed; (2) drop the
        `Raised-in-batch` stamp with the attribution - the bug carries none; (3) stamp a bare
        'none open' with no moment - the stamp no longer ends in a timestamp; (4) keep any of
        `start_batch`, `open_batch` or `close_batch` on `lib/run_state`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            filed = _cli("file_finding.py", "file", "--type", "bug", "--title", "a defect",
                         "--severity", "High", "--summary", "s", "--steps", "x", "--fix", "y",
                         "--affects", "src/widget.py", "--points", "3", "--root", str(root))
            self.assertEqual(0, filed.returncode, filed.stdout + filed.stderr)
            bugs = sorted((root / "sdlc-studio" / "bugs").glob("BG*.md"))
            self.assertEqual(1, len(bugs), "premise: the finding was filed")

            close = _cli("sprint.py", "close", "--dry-run", "--retro", "RETRO0001",
                         "--root", str(root))
            out = close.stdout + close.stderr
            self.assertIn("RUN-LEAN0861", out, "premise: the dry run read the open run:\n" + out)
            self.assertNotIn("finding placement", out,
                             "the close still reports the retired finding placement:\n" + out)

            stamp = next((ln.split("**Raised-in-batch:**", 1)[1].strip()
                          for ln in bugs[0].read_text(encoding="utf-8").splitlines()
                          if "**Raised-in-batch:**" in ln), None)
            self.assertIsNotNone(stamp, "the filed bug carries no Raised-in-batch stamp")
            self.assertRegex(stamp, _ISO_TAIL,
                             f"the stamp does not end in the moment of filing: {stamp!r}")

            for name in ("start_batch", "open_batch", "close_batch"):
                self.assertFalse(hasattr(run_state, name),
                                 f"lib/run_state still exposes the uncalled span API: {name}")


if __name__ == "__main__":
    unittest.main()
