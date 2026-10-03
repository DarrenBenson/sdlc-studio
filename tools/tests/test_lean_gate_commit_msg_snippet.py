"""BG0888: the commit-msg snippet in help/gate.md degrades as it says when its script is missing.

The guide said the opt-in commit-msg hook exits without blocking when there is no script, but
the snippet ran `python3` on the missing path, which exits 2 and blocks the commit. The snippet
is read out of `help/gate.md` and run as a hook would run it, so the test judges the text a
reader copies, not a paraphrase of it.
"""
# test-census-subject: .claude/skills/sdlc-studio/help/gate.md
from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
GUIDE = SKILL / "help" / "gate.md"


def _snippet() -> str:
    """The bash block under the guide's commit-msg heading."""
    text = GUIDE.read_text(encoding="utf-8")
    section = text.split("### Opt-in commit-msg gate", 1)[1]
    match = re.search(r"```bash\n(.*?)```", section, re.S)
    assert match, "no bash block under the commit-msg heading"
    return match.group(1)


def _run(skill_dir: Path, message: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as t:
        hook = Path(t) / "commit-msg"
        hook.write_text(_snippet(), encoding="utf-8")
        msg = Path(t) / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        env = {**os.environ, "CLAUDE_SKILL_DIR": str(skill_dir)}
        return subprocess.run(["bash", str(hook), str(msg)], cwd=t, capture_output=True,
                              text=True, env=env, timeout=60)


TWO_IDS = "fix: US0001 and BG0002 together\n\nbody\n"


class GateCommitMsgSnippetTests(unittest.TestCase):
    """AC1-AC2."""

    def test_a_missing_script_does_not_block(self) -> None:
        """AC1. MUTANT: the unguarded `python3 "$CLAUDE_SKILL_DIR/scripts/engagement_floor.py"`
        call - python3 exits 2 on the missing file and the commit is blocked."""
        with tempfile.TemporaryDirectory() as empty:
            r = _run(Path(empty), TWO_IDS)
        self.assertEqual(0, r.returncode, "a missing script blocked the commit:\n" + r.stderr)
        lines = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()]
        self.assertEqual(1, len(lines), f"expected one line, got: {lines}")
        self.assertIn("scripts/engagement_floor.py", lines[0], "the line does not name the missing script")

    def test_the_strict_check_still_refuses(self) -> None:
        """AC2. MUTANT: a guard that exits 0 whatever the message. The control: a single-id
        subject passes."""
        r = _run(SKILL, TWO_IDS)
        self.assertNotEqual(0, r.returncode, "a two-id subject with no Refs: trailer was let through")
        self.assertIn("Refs:", r.stdout + r.stderr)
        ok = _run(SKILL, "fix: US0001 alone\n")
        self.assertEqual(0, ok.returncode, ok.stdout + ok.stderr)


if __name__ == "__main__":
    unittest.main()
