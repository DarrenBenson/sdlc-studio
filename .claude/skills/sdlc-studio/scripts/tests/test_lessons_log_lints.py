"""BG1061: the committed project lessons log can be committed where markdownlint's defaults apply.

Every lesson heading was written as its sentence, full stop included, and markdownlint's MD026
(no trailing punctuation in a heading, on by default) refused the log the first time a close
committed it. These tests drive the shipped entry points, `retro.py extract` and `lessons.py
summary`, in a throwaway project root, and judge the log by the rule itself rather than by the
helper that implements the fix: MD026's default punctuation is written out here, and the fixture
ends a lesson in each of its marks, so a helper that strips less than the rule refuses is caught.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import lessons  # noqa: E402

REPO = SCRIPTS.parents[3]

#: markdownlint's MD026 `punctuation` default, as its documentation states it.
MD026_DEFAULT = ".,;:!。，；：！"

LONG = ("A lesson that keeps going " + "and going " * 14 + "until the headline it is given has to be "
        "cut at a word boundary.")


def _retro(rid: str, lessons_md: str) -> str:
    """A retro in the older shape `extract` reads its lessons from (`## Lessons`)."""
    return (f"# {rid}: a sprint\n## Delivered\n- US0001 - shipped it\n## What went well\n- fine\n"
            f"## What was hard / what stalled\n- nothing\n## Lessons\n{lessons_md}"
            "## Actions raised\n| Finding | Disposition |\n| --- | --- |\n"
            "| nothing | declined: clean sprint |\n")


#: The log a project holds from before the fix: every heading ends in its sentence's punctuation,
#: and a one-sentence lesson's body has no copy of the sentence.
OLD_LOG = """# Project Lessons

**Last Updated:** 2026-10-01

<!-- Append new entries at the top. Keep each entry under 10 lines. -->

## L-0002: Name the mutant first.

- **Added:** 2026-10-01
- **Review-by:** 2027-01-01

Name the mutant first. It saves a review round.

Recorded from retro RETRO0001.

## L-0001: Run the full suite before a host gate.

- **Added:** 2026-10-01
- **Review-by:** 2027-01-01

Recorded from retro RETRO0001.
"""

#: The summary that log produced, its titles punctuated as the headings were.
OLD_SUMMARY = """# Lessons Summary

- **L-0002: Name the mutant first.**
- **L-0001: Run the full suite before a host gate.**
"""


class _Project(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.retros = self.root / "sdlc-studio" / "retros"
        self.retros.mkdir(parents=True)
        self.log = self.retros / "LESSONS.md"

    def extract(self, rid: str, lessons_md: str) -> subprocess.CompletedProcess:
        (self.retros / f"{rid}-a-sprint.md").write_text(_retro(rid, lessons_md), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPTS / "retro.py"), "--root", str(self.root),
                               "extract", "--id", rid], capture_output=True, text=True, timeout=120)

    def headings(self) -> list[str]:
        return [ln for ln in self.log.read_text(encoding="utf-8").splitlines() if ln.startswith("## ")]


#: A lesson ending in each mark MD026 refuses by default, so a narrower strip than the rule's is
#: seen, and one ending in `?`, which MD026 allows.
ENDINGS = (
    "Run the full suite before a host gate.",
    "Name the mutant first. It saves a review round.",
    "Every heading here ends in punctuation, and this one in a colon:",
    "A gate that is not run is not a gate!",
    "Keep the fixture's endings varied, this one a comma,",
    "End this one in a semicolon;",
    "\u4ee5\u5168\u89d2\u53e5\u53f7\u7ed3\u5c3e\u3002",
    "\u5168\u89d2\u611f\u53f9\u53f7\uff01",
    "\u5168\u89d2\u9017\u53f7\uff0c",
    "\u5168\u89d2\u5206\u53f7\uff1b",
    "\u5168\u89d2\u5192\u53f7\uff1a",
    "Why did the push fail?",
    LONG,
)

#: Endings a strip that stops at a space, or makes one pass, leaves behind. Each is extracted ALONE:
#: every lesson extract adds rewrites the whole log, so an earlier heading is normalised again
#: by the next add, and only the last lesson's heading shows what one rendering produced.
EDGES = ("Try this: !", "A full-width mark sits behind a full stop here.\uff01")


class LessonsLogLintTests(_Project):

    def test_extracted_log_has_no_trailing_heading_punctuation(self) -> None:
        """AC1. Mutants: the heading is rendered with its sentence's punctuation; the stripped set
        is narrower than MD026's, by any one mark; a mark behind a space survives; an elided
        heading loses its marker; a one-sentence lesson loses its sentence from the record; a
        heading changes when the log is rewritten with nothing edited."""
        r = self.extract("RETRO0001", "".join(f"- {line}\n" for line in ENDINGS))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        heads = self.headings()
        self.assertEqual(len(heads), len(ENDINGS), heads)
        for head in heads:
            self.assertNotIn(head[-1], MD026_DEFAULT, f"MD026 refuses this heading: {head!r}")
        elided = [h for h in heads if h.split(": ", 1)[1].startswith("A lesson that keeps going")]
        self.assertTrue(elided and elided[0].endswith("\u2026"),
                        f"a heading cut mid-sentence no longer says it was cut: {elided}")
        text = self.log.read_text(encoding="utf-8")
        for sentence in ("Run the full suite before a host gate.", "A gate that is not run is not a gate!",
                         "Name the mutant first. It saves a review round."):
            self.assertIn(sentence, text, "the record lost the lesson's own sentence")
        r = self.extract("RETRO0002", "- One more lesson, so the whole log is written again.\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.headings()[1:], heads, "a rewrite with nothing edited changed a heading")
        for n, edge in enumerate(EDGES, start=3):
            with self.subTest(edge=edge):
                r = self.extract(f"RETRO000{n}", f"- {edge}\n")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                newest = self.headings()[0]
                self.assertNotIn(newest[-1], MD026_DEFAULT, f"MD026 refuses this heading: {newest!r}")
        lint = shutil.which("markdownlint") or str(REPO / "node_modules" / ".bin" / "markdownlint")
        config = REPO / ".markdownlint.json"
        if Path(lint).exists() and config.is_file():
            r = subprocess.run([lint, "--config", str(config), str(self.log)],
                               capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, "the repository's markdown rules refuse the log:\n"
                             + r.stdout + r.stderr)

    def test_an_existing_punctuated_log_reads_without_churn(self) -> None:
        """AC2. Mutants: headings are not read back the same way (a lesson's title changes with no
        edit); a one-sentence lesson is not recognised, so it is added twice; the summary's
        comparison does not read the old titles the same way, so `lessons.py summary` refuses."""
        self.log.write_text(OLD_LOG, encoding="utf-8")
        (self.retros / "LESSONS-SUMMARY.md").write_text(OLD_SUMMARY, encoding="utf-8")
        before = {e["id"]: e["title"] for e in lessons.parse_project_lessons(OLD_LOG)}
        r = self.extract("RETRO0002", "".join(f"- {line}\n" for line in (
            "Name the mutant first. It saves a review round.",
            "Run the full suite before a host gate.",
            "Hold each guard alone.")))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        after = {e["id"]: e["title"] for e in lessons.parse_project_lessons(
            self.log.read_text(encoding="utf-8"))}
        self.assertEqual(sorted(after), ["L-0001", "L-0002", "L-0003"],
                         "a lesson already in the log was added again, or one was lost")
        for lid in ("L-0001", "L-0002"):
            self.assertEqual(after[lid], before[lid], f"{lid} changed its title with no edit")
        self.assertEqual(before["L-0001"], "Run the full suite before a host gate",
                         "an old heading is not read the way a new one is written")
        self.assertEqual(after["L-0003"], "Hold each guard alone")
        r = subprocess.run([sys.executable, str(SCRIPTS / "lessons.py"), "summary", "--root", str(self.root)],
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, "the summary's lessons were not found in the log:\n" + r.stderr)


    def test_a_moved_legacy_log_is_normalised(self) -> None:
        """A legacy `.local/lessons.md`, moved to the committed path by an extract that adds
        nothing, arrives with headings MD026 accepts and the same lessons. Mutant: the move copies
        the file byte for byte, leaving a log its first commit refuses."""
        legacy = self.root / "sdlc-studio" / ".local" / "lessons.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(OLD_LOG, encoding="utf-8")
        before = {e["id"]: e["title"] for e in lessons.parse_project_lessons(OLD_LOG)}
        r = self.extract("RETRO0002", "- Run the full suite before a host gate.\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(legacy.exists(), "the legacy log was not moved")
        for head in self.headings():
            self.assertNotIn(head[-1], MD026_DEFAULT, f"a moved heading keeps punctuation MD026 refuses: {head!r}")
        after = {e["id"]: e["title"] for e in lessons.parse_project_lessons(self.log.read_text(encoding="utf-8"))}
        self.assertEqual(after, before, "moving the log changed its lessons")

if __name__ == "__main__":
    unittest.main()
