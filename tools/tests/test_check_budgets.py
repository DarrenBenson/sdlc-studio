"""Unit tests for tools/check_budgets.py - recording ceilings, reporting drift (US0657, US0658),
and the size budgets on the always-loaded files (US1129).

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import math
import os
import re
import shutil
import subprocess
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
            # 855 -> 859: US0823's close-refusal doctrine in step 5c, hand-written prose for a
            # delivered behaviour rather than a generated guide, and tightened by four lines
            # before the ceiling moved. The mutant this criterion is about - a ceiling raised to
            # fit a GENERATOR - still fails here, because the value is still pinned.
            "reference-sprint.md": 859,
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


class AlwaysLoadedBudgetTests(unittest.TestCase):
    """US1129 AC3-AC4: AGENTS.md by chars, SKILL.md by estimated tokens and description length."""

    def setUp(self) -> None:
        self.cb = _load(ROOT / "tools/check_budgets.py")

    def _run(self, d: Path) -> tuple[int, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = self.cb.main(["--root", str(d)])
        return rc, err.getvalue()

    def _tree(self, d: Path, *, agents: str | None = None, skill_md: str = "# S\n") -> None:
        skill = d / ".claude/skills/sdlc-studio"
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(skill_md, encoding="utf-8")
        if agents is not None:
            (d / "AGENTS.md").write_text(agents, encoding="utf-8")

    def test_agents_md_over_budget_is_refused_naming_its_size(self) -> None:
        """AC3. MUTANTS: never read AGENTS.md; read it in lines (one line of 7,001 chars passes
        a line count); refuse AT the budget; refuse a tree with no AGENTS.md, such as a hook-test
        fixture (BG1226's regression); a budget constant above 7,000; the lane's rule naming no
        always-loaded file."""
        budget = self.cb.AGENTS_MD_BUDGET
        self.assertLessEqual(budget, 7000)
        cases = {"one line, one over": ("x" * (budget + 1), 1),
                 "many lines, one over": (("y" * 9 + "\n") * (budget // 10) + "zz", 1),
                 "at the budget": ("x" * budget, 0),
                 "many lines, at the budget": (("y" * 9 + "\n") * (budget // 10), 0),
                 "no AGENTS.md": (None, 0)}
        for name, (agents, want) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as t:
                self._tree(Path(t), agents=agents)
                rc, err = self._run(Path(t))
                self.assertEqual(want, rc, err)
                if want:
                    self.assertIn(f"AGENTS.md: {len(agents)} chars > {budget}", err)
        # the lane's rule as the hook states it, through `--list`, which runs no lane
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        listing = subprocess.run([str(ROOT / ".githooks/pre-commit"), "--list"], cwd=ROOT,
                                 capture_output=True, text=True, env=env, timeout=60,
                                 check=False).stdout
        rule = next((ln.split("\t", 1)[1] for ln in listing.splitlines()
                     if ln.split("\t", 1)[0] == "budgets" and "\t" in ln), "")
        self.assertTrue(rule, f"the pre-commit hook lists no budgets lane rule:\n{listing}")
        for name in ("AGENTS.md", "SKILL.md"):
            self.assertIn(name, rule, f"the budgets lane's rule does not name {name}")
        self.assertEqual([], self.cb.always_loaded_faults(ROOT), "the shipped tree is over budget")

    def test_skill_md_token_and_description_budgets_refuse(self) -> None:
        """AC4. MUTANTS: count SKILL.md in lines only (one long line passes); a description cap
        above 600; refuse AT either budget; refuse a SKILL.md with no frontmatter; the shipped
        description over 600 chars or without its `NOT for:` clause or `audit --profile repo`."""
        self.assertLessEqual(self.cb.SKILL_DESCRIPTION_BUDGET, 600)
        tokens, ratio = self.cb.SKILL_MD_TOKEN_BUDGET, self.cb.CHARS_PER_TOKEN
        at = int(tokens * ratio)                       # the most chars that estimate at the budget
        self.assertEqual(tokens, math.ceil(at / ratio))
        cases = {"one line over the token estimate": ("x" * (at + 1), 1, f"~{tokens + 1} tokens"),
                 "at the token estimate": ("x" * at, 0, ""),
                 "a description of 601 chars": ('---\nname: s\ndescription: "' + "d" * 601
                                                + '"\n---\n# S\n', 1, "601 chars > 600"),
                 "a description of 600 chars": ('---\nname: s\ndescription: "' + "d" * 600
                                                + '"\n---\n# S\n', 0, ""),
                 "an unquoted description over": ("---\nname: s\ndescription: " + "d" * 650
                                                  + "\n---\n", 1, "650 chars > 600"),
                 "no frontmatter": ("# S\n", 0, "")}
        for name, (skill_md, want, says) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as t:
                self._tree(Path(t), skill_md=skill_md)
                rc, err = self._run(Path(t))
                self.assertEqual(want, rc, err)
                self.assertIn(says, err)
        desc = self.cb.skill_description((SKILL / "SKILL.md").read_text(encoding="utf-8"))
        self.assertLessEqual(len(desc), 600, desc)
        for clause in ("NOT for:", "audit --profile repo"):
            self.assertIn(clause, desc, f"the shipped description lost {clause!r}")


class ReferenceSprintCeilingTests(unittest.TestCase):
    """US0473 AC4: the prose and its ceiling landed together, not on borrowed headroom.

    The criterion named this class and this method and neither existed, so its stamp was
    evidence for a check nobody could run. What it asserts is a real property and worth
    keeping: `reference-sprint.md` sat at 760 lines against a recorded 724, which passes
    only because `CEILING_TOLERANCE` is 1.05 and 724 x 1.05 = 760.2. A file inside the
    tolerance is a file one line from a red build, and the tolerance exists to report
    drift rather than to hold a ceiling up.

    Mutants this must fail on: lower the recorded ceiling back to 724; delete the
    without-tolerance comparison and assert only that the guard passes.
    """

    FILE = "reference-sprint.md"
    #: The ceiling in force when the prose was written, and the number AC4 says must be beaten.
    SUPERSEDED_CEILING = 724

    def setUp(self) -> None:
        self.cb = _load(ROOT / "tools/check_budgets.py")

    def test_the_recorded_ceiling_admits_the_shipped_file_without_tolerance(self) -> None:
        ceiling = self.cb.ALLOWLIST.get(self.FILE)
        self.assertIsNotNone(ceiling, f"{self.FILE} has no recorded ceiling")
        self.assertGreater(
            ceiling, self.SUPERSEDED_CEILING,
            f"{self.FILE}'s ceiling is back at or below {self.SUPERSEDED_CEILING}, which the "
            f"shipped prose only cleared on the 5% tolerance")
        lines = len((ROOT / ".claude/skills/sdlc-studio" / self.FILE)
                    .read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(
            lines, ceiling,
            f"{self.FILE} is {lines} lines against a ceiling of {ceiling} - it is inside the "
            f"{self.cb.CEILING_TOLERANCE} tolerance rather than under its ceiling, so the "
            f"prose is sitting on headroom the guard lends it rather than on a raised ceiling")

    def test_the_tolerance_is_not_what_is_holding_the_file_up(self) -> None:
        """The positive control, stated as the thing that must NOT be true. Without it, a
        ceiling raised far above every file would pass the test above for the wrong reason."""
        ceiling = self.cb.ALLOWLIST[self.FILE]
        lines = len((ROOT / ".claude/skills/sdlc-studio" / self.FILE)
                    .read_text(encoding="utf-8").splitlines())
        self.assertLess(lines, ceiling * self.cb.CEILING_TOLERANCE)
        self.assertLessEqual(lines, ceiling)


if __name__ == "__main__":
    unittest.main()
