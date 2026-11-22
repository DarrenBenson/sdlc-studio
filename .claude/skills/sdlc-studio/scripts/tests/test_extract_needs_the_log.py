"""`retro.py extract` will not start a project lessons log the committed digest outlives.

`lessons summary` refuses to regenerate a digest from a log that lacks a lesson the committed
`LESSONS-SUMMARY.md` lists. `extract` had no such guard: with the log absent it started from the
empty header and wrote a log holding only this retro's lessons. On a clone whose log still sat in
another machine's gitignored `.local/lessons.md`, the close's retro-extract step forked the log,
and that machine's migration then refused as a two-log conflict only a person could merge.

Each case writes a throwaway project and drives `retro.py extract` through `retro.main`.
"""
from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lessons  # noqa: E402
import retro  # noqa: E402

RID = "RETRO9999"
LOG = "sdlc-studio/retros/LESSONS.md"
SUMMARY = "sdlc-studio/retros/LESSONS-SUMMARY.md"
DIGEST = ("# Lessons summary\n\n"
          "- **L-0001: preflight the deploy** - run the preflight before the deploy\n"
          "- **L-0002: pin the runner** - run a new test under the runner CI uses\n")


def _retro(*tries: str) -> str:
    return ("# RETRO-9999: a run\n\n> **Date:** 2026-11-22\n> **Run:** -\n"
            "> **Batch:** US0001\n\n## Keep\n\n- the gate caught it\n\n"
            "## Stop\n\n- skipping the preflight\n\n## Try\n\n"
            + "".join(f"- {t}\n" for t in tries))


class _Project(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="extract_log_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)

    def _write(self, rel: str, body, binary: bool = False) -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if binary:
            p.write_bytes(body)
        else:
            p.write_text(body, encoding="utf-8")
        return p

    def _extract(self, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = retro.main(["--root", str(self.root), "extract", "--id", RID, *extra])
        return rc, out.getvalue(), err.getvalue()

    def _tree(self) -> dict:
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in sorted(self.root.rglob("*")) if p.is_file()}


class ExtractNeedsTheLogTests(_Project):

    def test_extract_refuses_to_start_a_log_the_digest_outlives(self) -> None:
        """AC1. MUTANT: HEAD - the log is started from the empty header and holds one lesson
        while the digest lists two. The refusal names the missing log and the digest's count, and
        the tree is byte-identical, the class store included."""
        self._write(SUMMARY, DIGEST)
        self._write(f"sdlc-studio/retros/{RID}-a-run.md",
                    _retro("Run the preflight before every land.",
                           "[new: unpinned runner] A test is green only under one runner. "
                           "Run it under both."))
        before = self._tree()
        rc, out, err = self._extract()
        self.assertEqual(1, rc, out + err)
        self.assertFalse((self.root / LOG).exists(), "no log is started")
        self.assertIn(LOG, err)
        self.assertIn("2 lesson(s)", err)
        self.assertIn("Nothing was written", err)
        self.assertEqual(before, self._tree(), "nothing in the project moved")

    def test_extract_refuses_to_start_a_log_the_digest_outlives_on_a_dry_run(self) -> None:
        """A dry run reports the same refusal, so the preview does not promise an extract the
        real run would refuse."""
        self._write(SUMMARY, DIGEST)
        self._write(f"sdlc-studio/retros/{RID}-a-run.md", _retro("Run the preflight first."))
        rc, out, err = self._extract("--dry-run")
        self.assertEqual(1, rc, out + err)
        self.assertIn("2 lesson(s)", err)

    def test_a_present_log_is_appended_to(self) -> None:
        """The positive control: with the log present the same extract records the lesson."""
        self._write(SUMMARY, DIGEST)
        self._write(LOG, lessons.PROJECT_HEADER)
        self._write(f"sdlc-studio/retros/{RID}-a-run.md", _retro("Run the preflight first."))
        rc, out, err = self._extract()
        self.assertEqual(0, rc, out + err)
        self.assertIn("Run the preflight first", (self.root / LOG).read_text("utf-8"))

    def test_a_project_with_no_digest_starts_its_log(self) -> None:
        """A fresh project, whose digest lists nothing (absent or empty), starts its log as
        before: there is no record for a new log to fork from."""
        for digest in (None, ""):
            with self.subTest(digest=digest):
                (self.root / LOG).unlink(missing_ok=True)
                if digest is not None:
                    self._write(SUMMARY, digest)
                self._write(f"sdlc-studio/retros/{RID}-a-run.md",
                            _retro("Run the preflight first."))
                rc, out, err = self._extract()
                self.assertEqual(0, rc, out + err)
                self.assertIn("Run the preflight first", (self.root / LOG).read_text("utf-8"))

    def test_a_legacy_log_is_moved_and_then_appended_to(self) -> None:
        """The log still in `.local/lessons.md` is moved first, so it is the log the extract
        writes to and the guard does not fire on a log that exists."""
        self._write(SUMMARY, DIGEST)
        self._write("sdlc-studio/.local/lessons.md", lessons.PROJECT_HEADER)
        self._write(f"sdlc-studio/retros/{RID}-a-run.md", _retro("Run the preflight first."))
        rc, out, err = self._extract()
        self.assertEqual(0, rc, out + err)
        self.assertIn("Run the preflight first", (self.root / LOG).read_text("utf-8"))

    def test_class_tagged_items_alone_write_no_log_and_are_not_refused(self) -> None:
        """A retro whose Try items are all class tags writes the class store and no log, so
        there is no log to fork and the extract goes ahead."""
        self._write(SUMMARY, DIGEST)
        self._write(f"sdlc-studio/retros/{RID}-a-run.md",
                    _retro("[new: unpinned runner] A test is green only under one runner. "
                           "Run it under both."))
        rc, out, err = self._extract()
        self.assertEqual(0, rc, out + err)
        self.assertFalse((self.root / LOG).exists())
        self.assertTrue((self.root / lessons.STORE_FILE).is_file())

    def test_an_unreadable_digest_refuses_by_name(self) -> None:
        """A digest that is not UTF-8 cannot say how many lessons it lists, so the extract
        refuses naming it rather than starting a log it may outlive, and writes nothing."""
        self._write(SUMMARY, b"\xff\xfe- **L-0001: x**\n", binary=True)
        self._write(f"sdlc-studio/retros/{RID}-a-run.md", _retro("Run the preflight first."))
        before = self._tree()
        rc, out, err = self._extract()
        self.assertEqual(1, rc, out + err)
        self.assertIn(SUMMARY, err)
        self.assertEqual(before, self._tree())


if __name__ == "__main__":
    unittest.main()
