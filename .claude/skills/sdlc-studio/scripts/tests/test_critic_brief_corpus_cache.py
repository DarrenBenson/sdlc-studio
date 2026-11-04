"""BG1114: `critic.brief` reads the unit's file history inside the corpus cache.

`sprint.py lane brief` holds `sdlc_md.corpus_cache()` open around the same
`reconcile.file_history_section` call; `critic.brief` did not. That call is patched with a probe
that records whether the cache is open when the brief reaches it, so the window is observed
rather than inferred from a timing.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
sdlc_md = critic.sdlc_md


def _reconcile():
    """The module the brief's `import reconcile` binds when it runs. Another test module may
    have put its own copy in `sys.modules` since this one was imported (test_reconcile.py does
    at import), so the probe is patched onto that one, never onto a reference held from here."""
    return sys.modules.get("reconcile") or loader.load_script("reconcile")


def _unit(root: Path) -> None:
    """A full-tier unit with an Affects line and the three seat cards `brief` resolves."""
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / "US0001-x.md").write_text(
        "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
        "> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n"
        "### AC1: it behaves\n\n- **Then** it behaves\n", encoding="utf-8")
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True)
    for role in ("engineering", "qa", "product"):
        (seats / f"{role}.md").write_text(
            f"<!-- role: {role} -->\n# A {role} seat\n\n## Lens\n\nJudge as {role}.\n",
            encoding="utf-8")


class CriticBriefCorpusCacheTests(unittest.TestCase):

    def setUp(self) -> None:
        self.assertIsNone(sdlc_md._CORPUS_CACHE, "a cache leaked in from an earlier test")
        self.seen: list[bool] = []

    def _probe(self, root, unit_id, affects):
        self.seen.append(sdlc_md._CORPUS_CACHE is not None)
        return "(probe)"

    def test_the_brief_reads_history_inside_the_corpus_cache(self) -> None:
        """AC1. MUTANTS: drop the `with sdlc_md.corpus_cache()` from `brief` (the probe records
        False); open the cache by assigning `sdlc_md._CORPUS_CACHE = {}` and never reset it (it is
        still open after the return)."""
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(_reconcile(), "file_history_section", self._probe):
            root = Path(d)
            _unit(root)
            text = critic.brief(root, "US0001", "qa", "full")
        self.assertEqual([True], self.seen, "the brief read the file history once, cache open")
        self.assertIn("(probe)", text)
        self.assertIsNone(sdlc_md._CORPUS_CACHE, "the cache outlived the brief")

    def test_a_refused_brief_closes_the_cache_and_a_caller_s_cache_stays_open(self) -> None:
        """A brief refused part-way (an unknown seat) leaves the cache closed, and a brief taken
        inside a caller's cache leaves that cache open. MUTANTS: open and close the cache by hand
        with no `finally` (the refusal leaves it open); reset `_CORPUS_CACHE` to None as the brief
        returns (the caller's sweep loses its cache)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _unit(root)
            with self.assertRaises(ValueError):
                critic.brief(root, "US0001", "wizard", "full")
            self.assertIsNone(sdlc_md._CORPUS_CACHE, "a refused brief left the cache open")
            with mock.patch.object(_reconcile(), "file_history_section", self._probe), \
                    sdlc_md.corpus_cache() as outer:
                critic.brief(root, "US0001", "qa", "full")
                self.assertIs(outer, sdlc_md._CORPUS_CACHE, "the brief closed its caller's cache")
        self.assertEqual([True], self.seen)
        self.assertIsNone(sdlc_md._CORPUS_CACHE)


if __name__ == "__main__":
    unittest.main()
