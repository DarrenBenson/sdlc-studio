"""BG0989: the project lessons log is committed, so a close on another machine cannot wipe the digest.

The log lived at `sdlc-studio/.local/lessons.md`, gitignored, while the summary built from it,
LESSONS-SUMMARY.md, is committed. On any machine but the one that wrote the log, the close
regenerated the summary from an empty log: this repository's own 441 lessons were one close away
from becoming three. The log now lives at `sdlc-studio/retros/LESSONS.md`, beside the summary; a
legacy log is moved there once; and a regeneration that would drop lessons the log does not hold
is refused.

Every write here goes through the shipped CLI, the command the close itself calls, so the
migration and the guard are tested on the path that runs rather than beside it.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import lessons  # noqa: E402

LESSONS = SCRIPTS / "lessons.py"
SKILL = SCRIPTS.parent
COMMITTED = "sdlc-studio/retros/LESSONS.md"
LEGACY = "sdlc-studio/.local/lessons.md"
SUMMARY = "sdlc-studio/retros/LESSONS-SUMMARY.md"


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(LESSONS), *args, "--root", str(root)],
                          capture_output=True, text=True, check=False)


class CommittedLessonsLogTests(unittest.TestCase):

    def _project(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "proj"
        (root / "sdlc-studio" / "retros").mkdir(parents=True)
        return root

    def _add(self, root: Path, title: str, *extra: str) -> subprocess.CompletedProcess:
        r = _cli(root, "add", "--title", title, "--body", f"{title} body.", *extra)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return r

    def test_a_fresh_clone_reads_the_committed_log(self) -> None:
        """AC1. Mutant: DEFAULT_PROJECT_FILE left at `.local/lessons.md` - the clone carries no
        `.local/`, reads no log, and would write a digest of 0 lessons over the committed 2."""
        a = self._project()
        self._add(a, "First lesson")
        self._add(a, "Second lesson")
        self.assertEqual(0, _cli(a, "summary").returncode)
        self.assertTrue((a / COMMITTED).is_file(), "the log was not written to the committed path")
        self.assertFalse((a / LEGACY).exists(), "the log was written to the gitignored path")
        clone = a.parent / "clone"
        shutil.copytree(a, clone, ignore=shutil.ignore_patterns(".local"))
        r = _cli(clone, "summary", "--dry-run", "--format", "json")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(2, json.loads(r.stdout)["open"])
        self.assertFalse(lessons.summary_status(clone)["stale"])

    def test_legacy_log_is_moved_once_and_both_refuse(self) -> None:
        """AC2. Mutant: no migration - the add starts a fresh committed log and the legacy lessons
        stay in `.local/`, where no clone sees them. Mutant: the migration overwrites a committed
        log that already exists - one machine's lessons replace the other's."""
        with self.subTest(case="legacy only: moved, then added to"):
            root = self._project()
            self._add(root, "Legacy lesson", "--project-file", LEGACY)
            moved = self._add(root, "New lesson")
            self.assertFalse((root / LEGACY).exists(), "the legacy log was left behind")
            log = (root / COMMITTED).read_text(encoding="utf-8")
            self.assertIn("Legacy lesson", log)
            self.assertIn("New lesson", log)
            self.assertIn(COMMITTED, moved.stdout + moved.stderr)
            self.assertIn("commit", (moved.stdout + moved.stderr).lower())
        with self.subTest(case="both present: refuse, change nothing"):
            root = self._project()
            self._add(root, "Committed lesson")
            self._add(root, "Legacy lesson", "--project-file", LEGACY)
            before = {p: (root / p).read_bytes() for p in (COMMITTED, LEGACY)}
            r = _cli(root, "add", "--title", "Third", "--body", "b.")
            self.assertNotEqual(0, r.returncode, "two logs were silently reconciled")
            self.assertIn(COMMITTED, r.stderr)
            self.assertIn(LEGACY, r.stderr)
            self.assertEqual(before, {p: (root / p).read_bytes() for p in before})

    def test_legacy_log_is_moved_by_retro_extract_too(self) -> None:
        """AC2, the close's other writer. Mutant: `retro extract` writing the default path without
        the move - the retro's lessons start a fresh committed log and the legacy lessons are left
        in `.local/`. Mutant: the conflict not refused there - one machine's log is extended
        while the other's is silently ignored."""
        def retro(root: Path) -> subprocess.CompletedProcess:
            retros = root / "sdlc-studio" / "retros"
            (retros / "RETRO0001-probe.md").write_text(
                "# RETRO0001: probe\n\n> **Status:** Complete\n\n## Lessons\n\n"
                "- A retro lesson worth keeping. It carries a second sentence so the title cuts.\n",
                encoding="utf-8")
            (retros / "_index.md").write_text(
                "# Retros\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [RETRO0001](RETRO0001-probe.md) | probe | Complete |\n", encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "retro.py"), "--root", str(root),
                                   "extract", "--id", "RETRO0001"],
                                  capture_output=True, text=True, check=False)
        with self.subTest(case="legacy only: moved, then extracted into"):
            root = self._project()
            self._add(root, "Legacy lesson", "--project-file", LEGACY)
            r = retro(root)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertFalse((root / LEGACY).exists(), "the legacy log was left behind")
            log = (root / COMMITTED).read_text(encoding="utf-8")
            self.assertIn("Legacy lesson", log)
            self.assertIn("A retro lesson worth keeping", log)
            self.assertIn("commit", r.stderr.lower())
        with self.subTest(case="both present: refuse, change nothing"):
            root = self._project()
            self._add(root, "Committed lesson")
            self._add(root, "Legacy lesson", "--project-file", LEGACY)
            before = {p: (root / p).read_bytes() for p in (COMMITTED, LEGACY)}
            r = retro(root)
            self.assertNotEqual(0, r.returncode, "two logs were silently reconciled")
            self.assertIn(COMMITTED, r.stderr)
            self.assertEqual(before, {p: (root / p).read_bytes() for p in before})

    def test_a_log_missing_listed_lessons_refuses_regeneration(self) -> None:
        """AC3. Mutant: the summary regenerates from whatever log it finds - a log that does not
        hold the summary's lessons replaces them. Mutant: lessons matched by id alone - a fresh
        log re-allocating L-0001 to a different lesson passes as holding it."""
        root = self._project()
        self._add(root, "Kept lesson one")
        self._add(root, "Kept lesson two")
        self.assertEqual(0, _cli(root, "summary").returncode)
        digest = (root / SUMMARY).read_bytes()
        # Another machine: no log, then a new lesson, which re-allocates L-0001.
        (root / COMMITTED).unlink()
        self._add(root, "Another machine's lesson")
        r = _cli(root, "summary")
        self.assertNotEqual(0, r.returncode, "the digest was regenerated from a log missing lessons")
        self.assertIn("L-0001", r.stderr)
        self.assertIn("L-0002", r.stderr)
        self.assertEqual(digest, (root / SUMMARY).read_bytes(), "the refused summary was written")

    def test_closing_a_lesson_still_shrinks_the_digest(self) -> None:
        """AC3's control. Mutant: the guard refuses any digest smaller than the committed one - a
        closed lesson, which is still in the log, could then never leave the summary."""
        root = self._project()
        self._add(root, "Closes later")
        self._add(root, "Stays open")
        self.assertEqual(0, _cli(root, "summary").returncode)
        closed = _cli(root, "revalidate", "--close", "L-0001", "--reason", "superseded")
        self.assertEqual(0, closed.returncode, closed.stdout + closed.stderr)
        r = _cli(root, "summary")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        text = (root / SUMMARY).read_text(encoding="utf-8")
        self.assertIn("Stays open", text)
        self.assertNotIn("Closes later", text)

    def test_remedy_and_docs_name_the_committed_path(self) -> None:
        """AC4. Mutant: the missing-log remedy still says to clear the digest, the destructive
        step. Mutant: a shipped doc still names `.local/lessons.md` as the log."""
        root = self._project()
        self._add(root, "A lesson")
        self.assertEqual(0, _cli(root, "summary").returncode)
        (root / COMMITTED).unlink()
        reason = lessons.summary_status(root)["reason"]
        self.assertIn(COMMITTED, reason)
        self.assertNotIn("clear the digest", reason)
        docs = [*SKILL.glob("*.md"), *(SKILL / "help").glob("*.md"),
                *(SKILL / "templates").rglob("*.md"), SKILL / "templates" / "config-defaults.yaml",
                SKILL / "scripts" / "README.md", SKILL / "lessons" / "_index.md"]
        stale = [f"{d.relative_to(SKILL)}:{n}" for d in docs if d.is_file()
                 for n, line in enumerate(d.read_text(encoding="utf-8").splitlines(), 1)
                 if ".local/lessons.md" in line and not re.search(r"legacy|migrat", line, re.I)]
        self.assertEqual([], stale, "shipped docs still name the gitignored log as the log")


if __name__ == "__main__":
    unittest.main()
