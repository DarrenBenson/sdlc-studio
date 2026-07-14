"""Repo-only test for the tracked .githooks/commit-msg shim (CR0239).

The hook's DECISION logic is unit-tested in the shipped engagement_floor suite
(CommitMsgCheckTests). This test exercises the bash shim end-to-end: it warns without
blocking by default, blocks only under the strict opt-in, and degrades honestly (no
python3 / no script / unreadable message never blocks a legitimate commit).
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / ".githooks" / "commit-msg"


def _run(message: str, *, strict: bool = False, path: str | None = None,
         cwd: str | None = None):
    with tempfile.TemporaryDirectory() as d:
        msg = Path(d) / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        env = dict(os.environ)
        if strict:
            env["SDLC_ENGAGEMENT_STRICT"] = "1"
        target = path if path is not None else str(msg)
        return subprocess.run(["bash", str(HOOK), target], capture_output=True,
                              text=True, env=env, cwd=cwd)


class CommitMsgHookShimTests(unittest.TestCase):
    def test_multi_id_without_refs_warns_not_blocks(self):
        r = _run("US0301 US0302: batch fix")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Refs:", r.stderr)

    def test_strict_opt_in_blocks(self):
        r = _run("US0301 US0302: batch fix", strict=True)
        self.assertEqual(r.returncode, 1)

    def test_refs_trailer_is_clean(self):
        r = _run("US0301 US0302: batch fix\n\nRefs: US0301, US0302", strict=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stderr.strip(), "")

    def test_solo_id_is_clean(self):
        r = _run("US0301: solo fix", strict=True)
        self.assertEqual(r.returncode, 0)

    def test_missing_message_file_does_not_block(self):
        r = _run("", path="/nonexistent/COMMIT_EDITMSG", strict=True)
        self.assertEqual(r.returncode, 0)

    def test_outside_a_repo_with_the_script_degrades_to_pass(self):
        # Run from a bare temp dir: `git rev-parse --show-toplevel` finds no repo carrying the
        # engagement_floor script, so the hook cannot judge and must let the commit through.
        with tempfile.TemporaryDirectory() as elsewhere:
            r = _run("US0301 US0302: batch fix", strict=True, cwd=elsewhere)
            self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
