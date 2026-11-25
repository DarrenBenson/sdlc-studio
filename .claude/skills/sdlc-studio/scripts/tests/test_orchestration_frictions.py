"""Two orchestration frictions, each through the shipped entry point in a throwaway root.

`sprint batch add` refuses an id no artefact file carries, naming it, before anything is
written. `critic.py record` reads a verdict whose `BLOCKING: none` is followed by a further
section (a prior-finding ruling) as having no blocking item.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")
critic = loader.load_script("critic")

CRITIC = Path(__file__).resolve().parent.parent / "critic.py"


def _main(*argv: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(list(argv))
    return rc, out.getvalue() + err.getvalue()


def _bug(root: Path, num: int) -> None:
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        "> **Affects:** src/thing.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
        "### AC1: it works\n\n- **Then** it works\n- **Verify:** pytest src/thing.py\n",
        encoding="utf-8")


def _open_run(root: Path) -> None:
    """A run opened over BG0001, with BG0002 filed and not in its batch."""
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _bug(root, 1)
    _bug(root, 2)
    (root / "w.txt").write_text("BG0001\n", encoding="utf-8")
    rc, text = _main("plan", "--worklist", str(root / "w.txt"), "--write", "--no-fetch",
                     "--root", str(root))
    assert rc == 0, text


def _batch(root: Path) -> list:
    return json.loads(
        (root / "sdlc-studio" / ".local" / "run-state.json").read_text())["batch"]


class OrchestrationFrictionsTests(unittest.TestCase):

    def test_batch_add_refuses_an_id_with_no_artefact_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _open_run(root)
            for fmt in ("text", "json"):
                with self.subTest(fmt=fmt):
                    rc, text = _main("batch", "add", "BG9999", "--reason", "found mid-run",
                                     "--format", fmt, "--root", str(root))
                    self.assertEqual(2, rc, text)
                    self.assertIn("sprint batch add REFUSED BG9999", text)
                    self.assertIn("no artefact file carries that id", text)
                    self.assertIn("NOTHING was added", text)
                    self.assertEqual(["BG0001"], _batch(root))
            # a schema v3 id prints as typed, never as the hyphenless key no file carries
            rc, text = _main("batch", "add", "us-01abcdef", "--reason", "found mid-run",
                             "--root", str(root))
            self.assertEqual(2, rc, text)
            self.assertIn("sprint batch add REFUSED us-01abcdef:", text)
            self.assertNotIn("US01ABCDEF", text)
            self.assertEqual(["BG0001"], _batch(root))
            # the positive control: a filed unit is added as before
            rc, text = _main("batch", "add", "BG0002", "--reason", "found mid-run",
                             "--root", str(root))
            self.assertEqual(0, rc, text)
            self.assertIn("added BG0002 to the batch", text)
            self.assertEqual(["BG0001", "BG0002"], _batch(root))
            # a drop is not held to a file: a unit whose file is gone can still leave the batch
            (root / "sdlc-studio" / "bugs" / "BG0002-x.md").unlink()
            rc, text = _main("batch", "drop", "BG0002", "--reason", "its file was removed",
                             "--root", str(root))
            self.assertEqual(0, rc, text)
            self.assertEqual(["BG0001"], _batch(root))

    def test_blocking_none_before_a_further_section_records_no_blocking_item(self) -> None:
        block = ("VERDICT: APPROVE\nISSUES: [pre-existing] BG0123 the gate is slow\n"
                 "BLOCKING: none\n\nPRIOR FINDING RULING\n"
                 "- F1 (the missing pin): resolved by test_x\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            verdict = root / "verdict.txt"
            verdict.write_text(block, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(CRITIC), "record", "--unit", "US0001", "--reviewer",
                 "QA seat", "--author", "builder", "--from-verdict", str(verdict),
                 "--root", str(root)], capture_output=True, text=True, timeout=60)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            row = critic.verdict_for(root, "US0001")
            self.assertIsNotNone(row, "nothing was recorded")
            issues = row["issues"]
            self.assertEqual([], critic.blocking_findings(issues), issues)
            self.assertNotIn("BLOCKING:", issues)
            self.assertIn("PRIOR FINDING RULING", critic.row_rulings(issues))
            self.assertIn("resolved by test_x", critic.row_rulings(issues))


if __name__ == "__main__":
    unittest.main()
