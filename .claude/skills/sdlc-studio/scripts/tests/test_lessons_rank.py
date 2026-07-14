"""The ranked cross-project digest: what is biting hardest, right now.

A flat, append-only list is a diary. While it grows, the lesson that keeps costing you money
sits in the middle of it, indistinguishable from the one you learned once and fixed - and
eventually the whole thing gets evicted for being too big to read.

Ranking makes it an instrument. The signals are computed from the files, never asserted:
recurrence (how many artefacts cite it), recency, and demotion once a shipped guard makes the
class impossible.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lessons  # noqa: E402

INDEX = """# Cross-Project Lessons

| ID | Title | Tags |
| --- | --- | --- |
| [LL0001](LL0001-a.md) | Never trust a green build | ci, deploy |
| [LL0002](LL0002-b.md) | Fail loud, never report success not achieved | tooling |
| [LL0003](LL0003-c.md) | An old lesson nobody cites | misc |
"""


class RankBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.ldir = self.root / ".claude" / "skills" / "sdlc-studio" / "lessons"
        self.ldir.mkdir(parents=True)
        (self.ldir / "_index.md").write_text(INDEX, encoding="utf-8")
        for n, extra in (("LL0001-a.md", ""), ("LL0002-b.md", ""), ("LL0003-c.md", "")):
            (self.ldir / n).write_text(f"# {n}\n{extra}", encoding="utf-8")
        self.bugs = self.root / "sdlc-studio" / "bugs"
        self.bugs.mkdir(parents=True)

    def cite(self, name: str, text: str) -> None:
        (self.bugs / name).write_text(text, encoding="utf-8")

    def rank(self):
        return lessons.rank_lessons(str(self.root), str(self.ldir))


class RecurrenceRanks(RankBase):
    def test_the_most_cited_lesson_ranks_first(self) -> None:
        """The class that keeps biting should be in front of the person about to repeat it."""
        self.cite("BG0001.md", "this was LL0002 again")
        self.cite("BG0002.md", "LL0002 struck once more")
        self.cite("BG0003.md", "LL0001 here")
        ranked = self.rank()
        self.assertEqual(ranked[0]["id"], "LL0002")
        self.assertEqual(ranked[0]["recurrence"], 2)
        self.assertEqual(ranked[1]["id"], "LL0001")

    def test_an_uncited_lesson_still_appears(self) -> None:
        """Ranked low, never dropped. A lesson nobody has cited yet is not wrong, just
        unproven - and the one you have never paid for is the one you are about to."""
        ids = [r["id"] for r in self.rank()]
        self.assertIn("LL0003", ids)

    def test_the_registry_index_does_not_cite_itself(self) -> None:
        """Every lesson is named in _index.md; counting that as a citation would rank them
        all equally and say nothing."""
        self.assertEqual(self.rank()[0]["recurrence"], 0)


class GuardedIsDemoted(RankBase):
    def test_a_guarded_lesson_sinks_below_every_live_one(self) -> None:
        """Once a shipped guard makes the class impossible, the lesson has done its job. It
        must not crowd out one that can still bite you - demoted, never deleted."""
        self.cite("BG0001.md", "LL0002 " * 5)  # the most-cited by far
        (self.ldir / "LL0002-b.md").write_text(
            "# LL0002\n\n- **Guard:** tests/test_fail_loud.py\n", encoding="utf-8")
        ranked = self.rank()
        self.assertTrue(ranked[-1]["guarded"])
        self.assertEqual(ranked[-1]["id"], "LL0002")
        self.assertFalse(ranked[0]["guarded"], "a live lesson must outrank a guarded one")

    def test_guarded_is_flagged_not_removed(self) -> None:
        (self.ldir / "LL0002-b.md").write_text(
            "# LL0002\n\n- **Guard:** tests/test_x.py\n", encoding="utf-8")
        self.assertIn("LL0002", [r["id"] for r in self.rank()])

    def test_a_bare_guard_field_with_no_value_does_not_demote(self) -> None:
        """`**Guard:**` with nothing after it is not a guard. A lesson must not silence
        itself by declaring an empty defence."""
        (self.ldir / "LL0002-b.md").write_text("# LL0002\n\n- **Guard:**\n", encoding="utf-8")
        by_id = {r["id"]: r for r in self.rank()}
        self.assertFalse(by_id["LL0002"]["guarded"])


class TheDigestIsCarried(RankBase):
    def test_cross_digest_is_the_ranked_list(self) -> None:
        d = lessons.cross_digest(str(self.root), str(self.ldir))
        self.assertEqual(d["count"], 3)
        self.assertEqual([x["id"] for x in d["lessons"]], [r["id"] for r in self.rank()])

    def test_a_project_with_no_registry_degrades_quietly(self) -> None:
        """No registry is not an error - it is a new project. The loop must stay silent when
        it has nothing to say, or it reads as ceremony."""
        empty = Path(self.tmp.name) / "nowhere"
        self.assertEqual(lessons.rank_lessons(str(self.root), str(empty)), [])

class EveryReadPointCarriesTheLessons(unittest.TestCase):
    """CR0242's real acceptance test.

    The CR promised sprint plan AND review AND audit would read the registry. The first pass
    wired only the sprint plan and the CR was marked Complete anyway - reporting a success it
    did not achieve, which is LL0008, in the very change about failing to read LL0008. This
    test exists so that claim is provable rather than asserted.
    """

    def test_sprint_plan_carries_the_cross_project_digest(self) -> None:
        import sprint
        self.assertTrue(hasattr(sprint, "_render_cross_lessons"))

    def test_review_prep_carries_the_lessons_as_lenses(self) -> None:
        import review_prep
        self.assertTrue(hasattr(review_prep, "_render_lens"),
                        "the review must start FROM the lessons, not be told to go and read them")

    def test_the_audit_seeds_its_lenses_from_the_registry(self) -> None:
        """The audit is an agent workflow, so its mechanism is the doc it reads. That is not a
        cop-out: the field evidence is that a prompt inside the artefact you are already
        working in DOES drive behaviour - 8 of 9 retros carried a Lessons section because the
        template asked for one. What gets skipped is an instruction to go and open some OTHER
        file."""
        ref = Path(__file__).resolve().parents[2] / "reference-audit.md"
        text = ref.read_text(encoding="utf-8")
        self.assertIn("lessons.py rank", text)
        self.assertIn("Recall", text)


if __name__ == "__main__":
    unittest.main()
