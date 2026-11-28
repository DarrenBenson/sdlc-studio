"""`escape trace --confirm` rewrites one bug file, so a bug file that is not valid UTF-8 is
refused with nothing written: the confirm never skips the file or rewrites a lossy decode."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_escape_trace as base  # noqa: E402


class ConfirmOnAnUnreadableBugTests(unittest.TestCase):

    def test_confirm_on_a_non_utf8_bug_refuses_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = base._project(d)
            bug = base._bug(root)
            bug.write_bytes(bug.read_bytes() + b"\nstray byte \xff\xfe in the summary\n")
            before = base._snapshot(root)
            rc, out, err = base._cli(["trace", "--bug", "BG0001", "--confirm", "US0001",
                                      "--root", str(root)])
            self.assertEqual(2, rc, err)
            self.assertIn("refused", err)
            self.assertEqual("", out)
            self.assertEqual(before, base._snapshot(root), "a refused confirm wrote")

    def test_the_confirm_read_itself_stays_loud_when_the_trace_read_passes(self) -> None:
        # The trace reads the bug through the tolerant reader and refuses first, so the confirm's
        # own read is the guard if the file changes between the two: it must raise, not skip.
        with tempfile.TemporaryDirectory() as d:
            root = base._project(d)
            bug = base._bug(root)
            bug.write_bytes(bug.read_bytes() + b"\nstray byte \xff in the summary\n")
            before = base._snapshot(root)
            pick = {"unit": "US0001", "verdict": None}
            fake = {"bug": "BG0001", "path": str(bug), "release": "v1.0.0", "fix_files": [],
                    "units": ["US0001"], "proposals": [pick]}
            real = base.escape.trace
            base.escape.trace = lambda *_a, **_k: fake
            try:
                with self.assertRaises(UnicodeDecodeError):
                    base.escape.confirm(root, "BG0001", "US0001")
            finally:
                base.escape.trace = real
            self.assertEqual(before, base._snapshot(root), "the confirm wrote a lossy decode")

    def test_positive_control_a_utf8_bug_is_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = base._project(d)
            bug = base._bug(root)
            bug.write_bytes(bug.read_bytes() + "\nan accent: café\n".encode("utf-8"))
            rc, _out, err = base._cli(["trace", "--bug", "BG0001", "--confirm", "US0001",
                                       "--root", str(root)])
            self.assertEqual(0, rc, err)
            self.assertIn("> **Escaped-via:** US0001", bug.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
