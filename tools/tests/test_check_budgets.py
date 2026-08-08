"""Unit tests for tools/check_budgets.py - recording ceilings, reporting drift (US0657, US0658).

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".claude/skills/sdlc-studio"


def _load(src: Path):
    """Load a COPY of check_budgets, so `--record` rewrites the copy and not the real thing."""
    spec = importlib.util.spec_from_file_location(f"cb_{src.stem}_{id(src)}", src)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class RecordTests(unittest.TestCase):
    """AC1: `--record` moves a ceiling, appends its provenance, and rewrites no reason."""

    def _sandbox(self, d: Path, lines: int, ceiling: int):
        """A copy of the checker whose allowlist names one file, beside a tree holding it."""
        skill = d / ".claude/skills/sdlc-studio"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# S\n", encoding="utf-8")
        (skill / "reference-thing.md").write_text("x\n" * lines, encoding="utf-8")
        src = d / "check_budgets.py"
        text = (ROOT / "tools/check_budgets.py").read_text(encoding="utf-8")
        text = re.sub(r"ALLOWLIST = \{.*?\n\}",
                      'ALLOWLIST = {\n    "reference-thing.md": %d,  # Raised 100 -> %d for the '
                      'reasons recorded here\n}' % (ceiling, ceiling),
                      text, count=1, flags=re.S)
        src.write_text(text, encoding="utf-8")
        return src, skill

    def test_record_moves_the_ceiling_appends_provenance_and_rewrites_no_reason(self) -> None:
        """The fixture has GROWN past its ceiling, which is the whole point: one already in
        step makes `--record` a no-op, and the file is byte-identical under the honest
        implementation and under a mutant that writes nothing at all.

        Mutant: leave the ceiling integer untouched while reporting success.
        Mutant: rewrite the whole entry, reason comment included.
        Mutant: edit the existing reason in place rather than appending a new line.
        """
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            src, _skill = self._sandbox(d, lines=250, ceiling=100)
            before = src.read_text(encoding="utf-8")
            self.assertIn("# Raised 100 -> 100 for the reasons recorded here", before)

            mod = _load(src)
            moved = mod.record_ceilings(str(d))

            self.assertEqual(["reference-thing.md 100 -> 250"], moved,
                             "the ceiling integer did not move, so `--record` recorded nothing "
                             "while reporting success")
            after = src.read_text(encoding="utf-8")
            self.assertIn('"reference-thing.md": 250,', after)
            self.assertIn("# Raised 100 -> 100 for the reasons recorded here", after,
                          "the pre-existing reason was rewritten - and the reasons CONTAIN "
                          "their numbers, so an edited one is an argument false about its own "
                          "ceiling")
            self.assertIn("Recorded by `check_budgets.py --record`", after,
                          "no provenance line was appended, so the history does not accumulate")

    def test_a_tree_already_in_step_records_nothing(self) -> None:
        """The control. Without it, a `--record` that always rewrote would pass the test above."""
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            src, _skill = self._sandbox(d, lines=100, ceiling=100)
            before = src.read_text(encoding="utf-8")
            mod = _load(src)
            self.assertEqual([], mod.record_ceilings(str(d)))
            self.assertEqual(before, src.read_text(encoding="utf-8"),
                             "a tree already in step was rewritten anyway")


    def test_the_history_is_bounded_and_sits_beneath_the_block_it_describes(self) -> None:
        """The trail is for a reader deciding whether a ceiling moved recently. Unbounded, it
        pushes the allowlist further down the file on every run and the reader meets the audit
        before the thing audited.

        Mutant: append each stamp without evicting the oldest.
        Mutant: insert the stamp above the allowlist.
        """
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            src, skill = self._sandbox(d, lines=250, ceiling=100)
            mod = _load(src)
            ref = skill / "reference-thing.md"
            for n in range(mod.HISTORY_KEEP + 3):
                ref.write_text("x\n" * (300 + n * 10), encoding="utf-8")
                self.assertTrue(mod.record_ceilings(str(d)), "a grown file recorded nothing")

            text = src.read_text(encoding="utf-8")
            stamps = [ln for ln in text.splitlines() if ln.startswith(mod.STAMP_PREFIX)]
            self.assertEqual(mod.HISTORY_KEEP, len(stamps),
                             f"the history grew to {len(stamps)} entries - it accumulates "
                             f"without bound, so the file grows on every run forever")
            self.assertIn("-> 370", stamps[-1], "the newest run was not the one kept")
            self.assertGreater(text.index(stamps[0]), text.index("ALLOWLIST = {"),
                               "the history sits ABOVE the allowlist it describes")

    def test_a_renamed_anchor_is_refused_by_name(self) -> None:
        """Mutant: look the anchor up with `next(...)`, which raises a bare StopIteration."""
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            src, _skill = self._sandbox(d, lines=250, ceiling=100)
            mod = _load(src)
            with self.assertRaises(SystemExit) as caught:
                mod._allowlist_span("no literal here at all\n", src)
            self.assertIn("ALLOWLIST", str(caught.exception),
                          "the refusal does not name the anchor it lost")


class DriftTests(unittest.TestCase):
    """AC2-AC4, and the two criteria US0658 owns over this checker."""

    def setUp(self) -> None:
        self.cb = _load(ROOT / "tools/check_budgets.py")

    def test_drift_names_the_files_inside_the_tolerance_and_exits_zero(self) -> None:
        """AC2, over a sandbox rather than the live tree, so the assertion does not depend on
        which files happen to be in the band today.

        Mutant: exit non-zero when `--drift` finds a file inside the tolerance.
        """
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            skill = d / ".claude/skills/sdlc-studio"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# S\n", encoding="utf-8")
            for name, n in (("reference-inband.md", 103), ("reference-under.md", 90),
                            ("reference-over.md", 200)):
                (skill / name).write_text("x\n" * n, encoding="utf-8")
            src = d / "check_budgets.py"
            text = (ROOT / "tools/check_budgets.py").read_text(encoding="utf-8")
            text = re.sub(r"ALLOWLIST = \{.*?\n\}",
                          'ALLOWLIST = {\n    "reference-inband.md": 100,\n'
                          '    "reference-under.md": 100,\n    "reference-over.md": 100,\n}',
                          text, count=1, flags=re.S)
            src.write_text(text, encoding="utf-8")
            mod = _load(src)

            band = {name for name, *_rest in mod.drift(str(d))}
            self.assertEqual({"reference-inband.md"}, band,
                             "the tolerance band is not the SET of files inside it - a report "
                             "naming only the worst offender hides the rest")
            self.assertEqual(0, mod.main(["--drift", "--root", str(d)]),
                             "`--drift` exited non-zero, so a report about a file one line from "
                             "failing became a failure of its own")

    def test_the_hard_threshold_still_fails(self) -> None:
        """AC3. `--record` and `--drift` are reporting verbs added beside the gate, not a
        softening of it.

        Mutant: make the hard threshold advisory now that `--drift` reports.
        """
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            skill = d / ".claude/skills/sdlc-studio"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# S\n", encoding="utf-8")
            (skill / "reference-huge.md").write_text("x\n" * 5000, encoding="utf-8")
            self.assertEqual(1, self.cb.main(["--root", str(d)]),
                             "a file far past the un-allowlisted budget did not fail the gate")

    def test_the_unbudgeted_trees_are_reported_and_not_gated(self) -> None:
        """AC4, both directions. A test checking only that a total appears passes on an
        implementation that also added a ceiling.

        Mutant: give the three unbudgeted trees a hard ceiling from their current size.
        Mutant: report the totals from a constant rather than by walking the trees.
        """
        totals = self.cb.tree_totals(str(ROOT))
        self.assertEqual({"help", "best-practices", "templates"}, set(totals))
        for tree, total in totals.items():
            with self.subTest(tree=tree):
                self.assertGreater(total, 0, f"{tree}/ reported no lines at all")
                self.assertNotIn(tree, self.cb.ALLOWLIST,
                                 f"{tree}/ acquired a ceiling - a hard budget over a tree "
                                 f"nobody has pruned fails on day one and is waived on day two")
        # Walked, not constant: a tree with one file must report that file's length.
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / ".claude/skills/sdlc-studio/help").mkdir(parents=True)
            (d / ".claude/skills/sdlc-studio/help/x.md").write_text("a\nb\nc\n", encoding="utf-8")
            self.assertEqual(3, self.cb.tree_totals(str(d))["help"],
                             "the total is a constant rather than a walk of the tree")

    def test_a_justification_naming_a_reading_guide_must_have_one(self) -> None:
        """US0658 AC5, with its positive control. After this work `reference-sprint.md` is the
        only justification naming a guide, so a checker matching NOTHING would pass a
        refusal-only assertion for the wrong reason.

        Mutant: accept a justification that names a Reading Guide the file does not have.
        """
        self.assertEqual([], self.cb.guide_justification_faults(str(ROOT)),
                         "a ceiling justification names a Reading Guide over a file that has "
                         "none, so the argument for that ceiling is false about its own file")

        # The refusal fires when the guide is gone - checked on a COPY, never the live tree.
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            shutil.copytree(SKILL, d / ".claude/skills/sdlc-studio",
                            ignore=shutil.ignore_patterns("scripts", ".local", "__pycache__"))
            target = d / ".claude/skills/sdlc-studio/reference-sprint.md"
            body = target.read_text(encoding="utf-8")
            self.assertIn("Reading Guide", body, "the positive control has no guide to remove")
            target.write_text(body.replace("Reading Guide", "Section Index"), encoding="utf-8")
            self.assertIn("reference-sprint.md", self.cb.guide_justification_faults(str(d)),
                          "the guide was removed and the justification still passed")

    def test_the_recorded_ceilings_are_unchanged_by_the_guides(self) -> None:
        """US0658 AC4, pinned as VALUES. Asserting that the budgets merely PASS is the wrong
        direction: raising a ceiling makes them pass more easily, so the mutant this criterion
        is about would strengthen its own test.

        Mutant: raise a ceiling to fit the generated guide.
        """
        expected = {
            "reference-epic.md": 1102,
            "reference-story.md": 1091,
            "reference-code.md": 974,
            "reference-outputs.md": 869,
            "reference-decisions.md": 812,
            "reference-test-best-practices.md": 788,
            "reference-config.md": 695,
            "reference-review.md": 819,
            "reference-sprint.md": 855,
            "reference-consult.md": 634,
            "reference-prd.md": 660,
        }
        for name, ceiling in expected.items():
            with self.subTest(reference=name):
                self.assertEqual(ceiling, self.cb.ALLOWLIST.get(name),
                                 f"{name}'s ceiling moved from the value recorded when the "
                                 f"guides landed - a ceiling raised to fit a generator is the "
                                 f"ratchet running backwards")

    def test_skill_md_ceiling_is_unchanged(self) -> None:
        """US0659 AC3. Asserting SKILL.md is INSIDE its budget is vacuous - it sits at 271
        against 500, so the assertion is green before a word is written, and the mutant it
        names would make it pass more easily still.

        The checker enforces `n >= SKILL_MD_BUDGET`, so the effective cap is 499.

        Mutant: raise SKILL.md's ceiling to fit the additions.
        """
        self.assertEqual(500, self.cb.SKILL_MD_BUDGET,
                         "SKILL.md's ceiling moved - the router's size is the reason it is a "
                         "router, and a section added past the ceiling trades that away")


if __name__ == "__main__":
    unittest.main()
