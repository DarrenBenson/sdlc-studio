"""BG0806: a consuming project's TSD is judged against the project's own code.

`tsd_staleness` compared the TSD with the last change to the skill's scripts, which a consuming
project does not hold, so every consumer read `known: False` and no stale TSD was ever flagged.
Driven against throwaway git repositories with fixed commit dates.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

sprint = loader.load_script("sprint")


def _commit(root: Path, rel: str, when: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{rel} at {when}\n", encoding="utf-8")
    gitutil.git(["add", rel], root)
    gitutil.git(["commit", "-q", "-m", rel], root,
                env_extra={"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})


def _repo(d: str) -> Path:
    root = Path(d)
    gitutil.git(["init", "-q"], root)
    return root


class TsdStalenessTests(unittest.TestCase):

    def test_a_consuming_project_with_later_code_reads_stale(self) -> None:
        """AC1. Mutant: compare against `.claude/skills/sdlc-studio/scripts` (HEAD: known False
        in every consuming project)."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(d)
            self.assertFalse((root / ".claude").exists())
            _commit(root, "sdlc-studio/tsd.md", "2026-01-01T00:00:00+00:00")
            _commit(root, "src/app.py", "2026-02-01T00:00:00+00:00")
            verdict = sprint.tsd_staleness(root)
        self.assertEqual((True, True), (verdict["known"], verdict["stale"]), verdict)
        self.assertTrue(verdict["code_at"].startswith("2026-02-01"), verdict)
        self.assertTrue(verdict["tsd_at"].startswith("2026-01-01"), verdict)
        self.assertIn(verdict["code_at"], verdict["why"])

    def test_a_tsd_revised_after_the_code_reads_current(self) -> None:
        """AC2. Mutant: count commits to `sdlc-studio/` artefacts as code, so the backlog
        commit after the TSD marks it stale; or read a tree with no history as fresh."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(d)
            _commit(root, "src/app.py", "2026-01-01T00:00:00+00:00")
            _commit(root, "sdlc-studio/tsd.md", "2026-02-01T00:00:00+00:00")
            _commit(root, "sdlc-studio/stories/US0001-a-story.md", "2026-03-01T00:00:00+00:00")
            verdict = sprint.tsd_staleness(root)
        self.assertEqual((True, False), (verdict["known"], verdict["stale"]), verdict)
        self.assertTrue(verdict["code_at"].startswith("2026-01-01"), verdict)
        with tempfile.TemporaryDirectory() as d:
            verdict = sprint.tsd_staleness(Path(d))    # not a git repository
        self.assertEqual((False, False), (verdict["known"], verdict["stale"]), verdict)
        self.assertIn("no commit history", verdict["why"])
        self.assertIn("not the same as fresh", verdict["why"])


if __name__ == "__main__":
    unittest.main()
