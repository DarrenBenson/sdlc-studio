"""The close names each untracked file its recorded tree binds into the signature.

The close records its tree as `git add -A` sees it, so an untracked file is part of what
`sign` later checks; tidying one away between the close and the signature makes `sign` refuse.
The close says so before its last line. Driven through `sprint.main` over the shared lean close
fixture, in a git repository whose reports folder is ignored, so the only untracked files are
the ones each test plants.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

_BOUND = "the signature binds"


def _repo(root: Path) -> dict:
    """The lean fixture committed, its filed report pages ignored and the velocity log
    tracked, so nothing the close writes is untracked but the run records the tree digest
    drops; the git env the close runs in."""
    lean._fixture(root)
    (root / "sdlc-studio" / "retros" / "VELOCITY.md").write_text("# Velocity\n",
                                                                encoding="utf-8")
    (root / ".gitignore").write_text(
        "sdlc-studio/reports/RPT*\nsdlc-studio/reports/_index.md\nignored/\n", encoding="utf-8")
    env = gitutil.git_env()
    for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run(["git", "-C", str(root), *argv], env=env, check=True,
                       capture_output=True)
    return env


def _close(root: Path, env: dict) -> tuple[int, list[str], str]:
    with unittest.mock.patch.dict(os.environ, env, clear=True):
        rc, out, err = lean._close(root)
    return rc, out.splitlines(), err


class CloseNamesBoundUntrackedTests(unittest.TestCase):

    def test_a_close_names_each_untracked_file_it_binds(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = _repo(root)
            (root / "notes").mkdir()
            (root / "notes" / "LESSONS.md").write_text("short\n", encoding="utf-8")
            (root / "scratch.txt").write_text("x\n", encoding="utf-8")
            (root / "ignored").mkdir()
            (root / "ignored" / "cache.txt").write_text("x\n", encoding="utf-8")
            rc, lines, err = _close(root, env)
            self.assertEqual(0, rc, err)
            bound = [i for i, ln in enumerate(lines) if _BOUND in ln]
            self.assertEqual(1, len(bound), lines)
            line = lines[bound[0]]
            self.assertIn("2 untracked file(s): notes/LESSONS.md, scratch.txt", line)
            self.assertIn("until the run is signed", line)
            self.assertNotIn("cache.txt", line)               # an ignored file is not bound
            self.assertNotIn("sdlc-studio/.local", line)      # nor the run's own records
            self.assertTrue((root / "sdlc-studio" / "reports" / "runs").is_dir())
            self.assertNotIn("reports/runs", line)
            sign = next(i for i, ln in enumerate(lines) if ln.startswith("sign it with:"))
            self.assertLess(bound[0], sign)
        with tempfile.TemporaryDirectory() as d:
            # the control: a close over a tree holding no untracked file names none
            root = Path(d)
            env = _repo(root)
            rc, lines, err = _close(root, env)
            self.assertEqual(0, rc, err)
            self.assertTrue([ln for ln in lines if ln.startswith("sign it with:")], lines)
            self.assertFalse([ln for ln in lines if _BOUND in ln], lines)
        with tempfile.TemporaryDirectory() as d:
            # a close that files no report owes no signature, so it names nothing as bound
            root = Path(d)
            env = _repo(root)
            (root / "scratch.txt").write_text("x\n", encoding="utf-8")
            sr = lean._live("sprint_report")

            def refuse(*_a, **_k):
                raise sr.ReportError("the run cannot be reported")

            with unittest.mock.patch.object(sr, "build_report", refuse):
                rc, lines, err = _close(root, env)
            self.assertEqual(0, rc, err)
            self.assertFalse([ln for ln in lines if _BOUND in ln], lines)


if __name__ == "__main__":
    unittest.main()
