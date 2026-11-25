"""`sprint batch add` says what its Affects check did, and names an entry that is no path.

Under `sprint.affects_check: warn` the unit is added and each Affects finding is a labelled
warning saying so, so no line of the output reads as a refusal. An Affects entry of words and
spaces with no file shape is named as not a path wherever a finding is printed, and is never
told that a file the unit creates is fine. Driven through `sprint.main` in throwaway roots.
"""
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

_CREATES = "(a file the unit CREATES is fine)"
_NOT_A_PATH = "HA scripts foo / bar"


def _main(*argv: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(list(argv))
    return rc, out.getvalue() + err.getvalue()


def _bug(root: Path, num: int, affects: str, verify: str = "pytest src/thing.py") -> None:
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** {affects}\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
        f"### AC1: it works\n\n- **Then** it works\n- **Verify:** {verify}\n",
        encoding="utf-8")


def _repo(root: Path, mode: str, affects: str, verify: str = "pytest src/thing.py") -> None:
    """A run open over a clean BG0001, under `mode`, with BG0002 declaring `affects`."""
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    (root / "src" / "other.py").write_text("y = 1\n", encoding="utf-8")
    _bug(root, 1, "src/thing.py")
    _bug(root, 2, affects, verify)
    (root / "w.txt").write_text("BG0001\n", encoding="utf-8")
    rc, text = _main("plan", "--worklist", str(root / "w.txt"), "--write", "--no-fetch",
                     "--root", str(root))
    assert rc == 0, text
    (root / "sdlc-studio" / ".config.yaml").write_text(
        f"sprint:\n  affects_check: {mode}\n", encoding="utf-8")


def _batch(root: Path) -> list:
    return json.loads(
        (root / "sdlc-studio" / ".local" / "run-state.json").read_text())["batch"]


class BatchAddWordingTests(unittest.TestCase):

    def test_a_warned_add_says_it_added_the_unit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _repo(root, "warn", "src/thing.py, src/GHOST.py", verify="pytest src/other.py")
            rc, text = _main("batch", "add", "BG0002", "--reason", "t", "--root", str(root))
            self.assertEqual(0, rc, text)
            self.assertIn("BG0002", _batch(root))
            findings = [ln for ln in text.splitlines()
                        if "not on disk" in ln or "undeclared" in ln]
            self.assertEqual(2, len(findings), text)       # one per kind of Affects finding
            for line in findings:
                self.assertTrue(line.startswith("  warning: BG0002"), line)
                self.assertIn("added anyway", line)
            self.assertIn("src/GHOST.py " + _CREATES, findings[0])
            self.assertIn("src/other.py", findings[1])
            self.assertNotIn("REFUSED", text)
        with tempfile.TemporaryDirectory() as d:
            # under `block` the same finding is still the refusal it was, and nothing is added
            root = Path(d)
            _repo(root, "block", "src/thing.py, src/GHOST.py")
            rc, text = _main("batch", "add", "BG0002", "--reason", "t", "--root", str(root))
            self.assertEqual(2, rc, text)
            self.assertIn("sprint batch add REFUSED BG0002", text)
            self.assertNotIn("warning:", text)
            self.assertNotIn("added anyway", text)
            self.assertEqual(["BG0001"], _batch(root))

    def test_a_non_path_affects_is_named_as_not_a_path(self) -> None:
        for mode in ("warn", "block"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _repo(root, mode, f"src/thing.py, {_NOT_A_PATH}, src/GHOST.py, docs/My Notes.md")
                _rc, text = _main("batch", "add", "BG0002", "--reason", "t",
                                  "--root", str(root))
                line = next(ln for ln in text.splitlines() if "not on disk" in ln)
                self.assertIn(f"not a path: {_NOT_A_PATH}", line)
                self.assertNotIn(f"{_NOT_A_PATH} {_CREATES}", line)
                self.assertNotIn(f"{_NOT_A_PATH}, ", line)
                if mode == "warn":
                    # a path, spaced or not, is still told a file the unit creates is fine
                    self.assertIn(f"src/GHOST.py, docs/My Notes.md {_CREATES}", line)
                else:
                    self.assertIn("src/GHOST.py, docs/My Notes.md", line)
                    self.assertNotIn(_CREATES, line)
        with tempfile.TemporaryDirectory() as d:
            # the plan's own Affects advisory says the same
            root = Path(d)
            _repo(root, "warn", f"src/thing.py, {_NOT_A_PATH}")
            (root / "w.txt").write_text("BG0002\n", encoding="utf-8")
            _rc, text = _main("plan", "--worklist", str(root / "w.txt"), "--no-fetch",
                              "--root", str(root))
            line = next(ln for ln in text.splitlines() if "not on disk" in ln)
            self.assertIn(f"not a path: {_NOT_A_PATH}", line)
            self.assertNotIn(_CREATES, line)


if __name__ == "__main__":
    unittest.main()
