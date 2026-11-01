"""Unit tests for tools/test_census.py - where the suite's cost goes, and what earns it.

Two questions, one report. US0506 asks which module a test covers and what that costs,
because a suite of 4,624 tests cannot be pruned until the expensive areas are visible.
US0507 asks whether a test still discriminates: one that no mutation of its own module
can kill protects nothing measurable, and removing it must record what it stopped
protecting.

The failure mode both halves share is a confident wrong answer. A census that silently
drops the tests it cannot attribute reports a total smaller than the suite it measured,
and a prune report that cannot tell "killed nothing" from "never ran" nominates live
tests for deletion. So most of what follows pins the honest-refusal paths rather than
the happy one.
"""
from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "test_census.py"


def _load():
    spec = importlib.util.spec_from_file_location("test_census", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["test_census"] = mod
    spec.loader.exec_module(mod)
    return mod


tc = _load()


def _junit(cases: list[tuple[str, str, float]]) -> str:
    """A pytest JUnit report over `(classname, name, seconds)` triples.

    Hand-built rather than captured, because the shapes that matter here - a classname
    resolving to no file, a module-level test function with no class - are exactly the
    ones a real capture of a healthy suite does not contain.
    """
    body = "".join(
        f'<testcase classname="{c}" name="{n}" time="{s}" />' for c, n, s in cases)
    total = round(sum(s for _, _, s in cases), 3)
    return ('<?xml version="1.0" encoding="utf-8"?><testsuites name="pytest tests">'
            f'<testsuite name="pytest" tests="{len(cases)}" time="{total}">'
            f'{body}</testsuite></testsuites>')


def _repo(tmp: Path) -> Path:
    """A miniature repo with the two attribution shapes and one unattributable test.

    - pkg/alpha.py       covered by pkg/tests/test_alpha.py   (matching name)
    - pkg/beta.py        covered by pkg/tests/test_beta_paths.py (name misses, references beta)
    - pkg/tests/test_hook_contract.py covers a shell hook, so no module resolves at all
    """
    (tmp / "pkg" / "tests").mkdir(parents=True)
    (tmp / "pkg" / "alpha.py").write_text("def a(): return 1\n", encoding="utf-8")
    (tmp / "pkg" / "beta.py").write_text("def b(): return 2\n", encoding="utf-8")
    (tmp / "pkg" / "tests" / "test_alpha.py").write_text("import alpha\n", encoding="utf-8")
    (tmp / "pkg" / "tests" / "test_beta_paths.py").write_text(
        "# exercises beta end to end\nSCRIPT = 'beta.py'\nimport beta\n", encoding="utf-8")
    (tmp / "pkg" / "tests" / "test_hook_contract.py").write_text(
        "# reads .githooks/pre-commit as text\n", encoding="utf-8")
    return tmp


#: For the importability guard below - the directory whose modules must import under
#: BOTH runners, and the repo root pytest is invoked from.
TESTS_DIR = Path(__file__).resolve().parent
REPO = TESTS_DIR.parents[1]


def tc_conftest_inserts_path(src: str) -> bool:
    """Whether `src` really CALLS `sys.path.insert`, decided by AST rather than by text.

    The conftest's own docstring names the call, so a substring search is satisfied by the
    prose with the call gone - a guard that reads its own explanation (BG0493).
    """
    import ast
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if (isinstance(f, ast.Attribute) and f.attr == "insert"
                and isinstance(f.value, ast.Attribute) and f.value.attr == "path"
                and isinstance(f.value.value, ast.Name) and f.value.value.id == "sys"):
            return True
    return False


class CensusTests(unittest.TestCase):
    """US0506: suite time and count attributed to the module each test covers."""

    def test_time_and_count_are_attributed_per_module(self) -> None:
        """AC1: per module, how many tests and how long they took, dearest first."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = tc.census(_junit([
                ("pkg.tests.test_alpha.AlphaTests", "test_one", 0.1),
                ("pkg.tests.test_alpha.AlphaTests", "test_two", 0.2),
                ("pkg.tests.test_beta_paths.BetaTests", "test_slow", 5.0),
            ]), root)
            rows = {r["module"]: r for r in report["modules"]}
            self.assertEqual(rows["pkg/alpha.py"]["tests"], 2)
            self.assertAlmostEqual(rows["pkg/alpha.py"]["seconds"], 0.3, places=3)
            self.assertEqual(rows["pkg/beta.py"]["tests"], 1)
            self.assertAlmostEqual(rows["pkg/beta.py"]["seconds"], 5.0, places=3)
            # Ordered by cost: the point of the report is to show where the money goes.
            self.assertEqual([r["module"] for r in report["modules"]],
                             ["pkg/beta.py", "pkg/alpha.py"])

    def test_an_unattributable_test_is_named_not_dropped(self) -> None:
        """AC2: a test no module claims is named, and the totals still add up."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = tc.census(_junit([
                ("pkg.tests.test_alpha.AlphaTests", "test_one", 0.1),
                ("pkg.tests.test_hook_contract.HookTests", "test_hook_is_executable", 0.4),
            ]), root)
            named = [u["test"] for u in report["unattributed"]]
            self.assertIn(
                "pkg/tests/test_hook_contract.py::HookTests::test_hook_is_executable", named)
            self.assertTrue(report["unattributed"][0]["reason"])
            # The honest part: nothing vanished between the run and the report.
            self.assertEqual(report["totals"]["tests"], 2)
            self.assertEqual(report["totals"]["attributed"], 1)
            self.assertEqual(report["totals"]["unattributed"], 1)
            self.assertAlmostEqual(report["totals"]["seconds"], 0.5, places=3)
            self.assertAlmostEqual(
                sum(r["seconds"] for r in report["modules"])
                + sum(u["seconds"] for u in report["unattributed"]),
                report["totals"]["seconds"], places=3)

    def test_a_classname_resolving_to_no_file_is_named_not_dropped(self) -> None:
        """A classname that matches no test file on disk is the other way to lose a test."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = tc.census(_junit([
                ("pkg.tests.test_deleted.GhostTests", "test_x", 1.5),
            ]), root)
            self.assertEqual(report["totals"]["tests"], 1)
            self.assertEqual(len(report["unattributed"]), 1)
            self.assertIn("pkg.tests.test_deleted.GhostTests::test_x",
                          report["unattributed"][0]["test"])
            self.assertIn("file", report["unattributed"][0]["reason"])

    def test_attribution_falls_back_to_the_module_the_test_references(self) -> None:
        """test_beta_paths.py names no module, so the name rule cannot place it."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = tc.census(_junit([
                ("pkg.tests.test_beta_paths.BetaTests", "test_slow", 1.0),
            ]), root)
            row = report["modules"][0]
            self.assertEqual(row["module"], "pkg/beta.py")
            self.assertEqual(row["how"], "reference")

    def test_a_test_referencing_two_modules_equally_is_unattributed(self) -> None:
        """A guess between two modules is worse than an admission of not knowing."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            (root / "pkg" / "tests" / "test_both.py").write_text(
                "import alpha, beta\nalpha, beta\n", encoding="utf-8")
            report = tc.census(_junit([
                ("pkg.tests.test_both.BothTests", "test_x", 0.2),
            ]), root)
            self.assertEqual(report["modules"], [])
            self.assertEqual(len(report["unattributed"]), 1)
            self.assertIn("alpha.py", report["unattributed"][0]["reason"])
            self.assertIn("beta.py", report["unattributed"][0]["reason"])

    def test_a_module_level_test_function_is_attributed(self) -> None:
        """pytest emits no class segment for a bare test function; it must still land."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = tc.census(_junit([
                ("pkg.tests.test_alpha", "test_bare", 0.7),
            ]), root)
            self.assertEqual(report["modules"][0]["module"], "pkg/alpha.py")
            self.assertIn("pkg/tests/test_alpha.py::test_bare",
                          report["modules"][0]["test_ids"])


class SkipListScopeTests(unittest.TestCase):
    """BG0445. The skip list is about directories INSIDE the census root. Matched against the
    absolute path, a name appearing anywhere ABOVE the root skipped every file beneath it - so a
    checkout under `.claude/worktrees/` censused zero files and the lane reported an all-clear
    over nothing, in exactly the environment this repo runs its reviewers in."""

    def test_a_root_nested_under_a_skipped_name_still_censuses_its_files(self) -> None:
        for above in sorted(tc.SKIP_DIRS):
            with self.subTest(above=above), tempfile.TemporaryDirectory() as d:
                root = _repo(Path(d) / above / "wt-1")
                found = tc.test_files(root)
                self.assertTrue(
                    found,
                    f"a census root beneath a directory named {above!r} found no test files at "
                    f"all; a name above the root says nothing about the files below it")
                self.assertIn(Path("pkg/tests/test_alpha.py"), found)

    def test_a_skipped_directory_INSIDE_the_root_is_still_skipped(self) -> None:
        """The control. Narrowing the match must not stop the skip list working, or the fix
        trades an empty census for a census of node_modules."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            buried = root / "node_modules" / "dep" / "tests"
            buried.mkdir(parents=True)
            (buried / "test_vendored.py").write_text("import dep\n", encoding="utf-8")
            self.assertNotIn(Path("node_modules/dep/tests/test_vendored.py"),
                             tc.test_files(root))


class MultipleReportTests(unittest.TestCase):
    """This repo's gate cannot be collected in one pytest run, so nor is its report.

    `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests tools/tests` aborts with
    35 collection errors: both directories are packages called `tests`. The gate therefore
    runs them as two invocations, and a census that could read only one of them would
    report half the cost of the suite while looking like all of it - which is the same
    dishonest total the unattributed list exists to prevent, one level up.
    """

    def test_two_junit_reports_are_one_census(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = tc.census([
                _junit([("pkg.tests.test_alpha.AlphaTests", "test_one", 0.1)]),
                _junit([("pkg.tests.test_beta_paths.BetaTests", "test_slow", 5.0)]),
            ], root)
            self.assertEqual(report["totals"]["tests"], 2)
            self.assertAlmostEqual(report["totals"]["seconds"], 5.1, places=3)
            self.assertEqual([r["module"] for r in report["modules"]],
                             ["pkg/beta.py", "pkg/alpha.py"])

    def test_report_cli_takes_one_junit_per_invocation_of_the_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            first, second = root / "a.xml", root / "b.xml"
            first.write_text(_junit([
                ("pkg.tests.test_alpha.AlphaTests", "test_one", 0.1)]), encoding="utf-8")
            second.write_text(_junit([
                ("pkg.tests.test_beta_paths.BetaTests", "test_slow", 5.0)]), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = tc.main(["--root", str(root), "report",
                              "--junit", str(first), "--junit", str(second)])
            self.assertEqual(rc, 0)
            self.assertIn("2 tests", out.getvalue())
            self.assertIn("pkg/beta.py", out.getvalue())
            self.assertIn("pkg/alpha.py", out.getvalue())


class RealRepoTests(unittest.TestCase):
    """Attribution has to work on THIS repo, not only on a fixture shaped to suit it."""

    REPO = Path(__file__).resolve().parents[2]

    #: Test files this repo cannot attribute by construction: they guard a hook, a document, a
    #: contract or a lockfile rather than a sibling Python module. A RATCHET, like the noise
    #: baseline and the verify-lint baseline - it may only shrink, and is lowered when a file
    #: gains a home, never raised to accommodate a new one.
    #:
    #: Recorded because the bare `> 0.8` this replaced was sitting AT 0.8045 with nobody
    #: watching: 179 files, 144 placed. One more cross-cutting guard tipped it, and the guard
    #: gave no warning that it was one file from firing. A threshold nobody can see approaching
    #: is a threshold that fails as a surprise.
    #: Raised 36 -> 37 in BG0556, which is the one direction this number is not supposed to
    #: move, so the reason is recorded rather than asserted. `test_cli_grammar.py` attributed to
    #: `transition.py` by REFERENCE COUNT - it happened to name that module more often than any
    #: other. BG0556 added an inventory of 21 script names to it, `sprint.py` among them, and the
    #: count tied. Nothing about the file's subject changed: it is the family-wide CLI grammar
    #: sweep and has no owner module, which is what the census now says. The previous attribution
    #: was an artefact of counting, and the honest verdict is the one it gives today.
    #:
    #: Filed as BG0578: an owner decided by name frequency changes when a test mentions one more
    #: module, so attribution is stable only for files that reference exactly one.
    #: 37 -> 38 in BG0579 for `tools/tests/test_boundary_marker.py`, whose subject is two SHELL
    #: SCRIPTS - `tools/run-suite.sh` and the CI workflow - and a marker convention. The
    #: name-or-reference rule places Python modules; it cannot place a guard over a hook, and
    #: that is the category this baseline exists to hold rather than a case of it failing.
    #: Distinguished from the 36 -> 37 raise beside it, which was a real defect: there,
    #: attribution moved because a file MENTIONED one more module, and is filed as BG0578.
    #: LOWERED 38 -> 33 when BG0578 gave attribution two DECLARED routes - a module-level
    #: subject marker and a unit's `Affects` naming this file beside exactly one script.
    #: FOUR files gained a home, not five: the constant moved by five, but the tree measured 37
    #: against a declared 38 before the change, so one of those five was slack in the baseline
    #: rather than a file that gained an owner. Measured at the parent commit and at head, on
    #: the same walk this row runs. None was placed by loosening the counting rule.
    UNATTRIBUTED_BASELINE = 33

    def test_this_repos_test_files_are_mostly_attributed(self) -> None:
        """A convention that placed a handful of files would be a report of nothing.

        The floor stays, so the census cannot become vacuous. The ratchet is what makes the
        remaining gap VISIBLE rather than a cliff: 29 of the unattributed guard hooks,
        documents and contracts, which the name-or-reference convention cannot place at all."""
        files = [f for f in tc.test_files(self.REPO)
                 if "bench/fixtures" not in f.as_posix()]
        placed = [f for f in files if tc.attribute(self.REPO, f)[0]]
        self.assertGreater(len(files), 100)          # the suite this exists to measure
        self.assertGreater(len(placed) / len(files), 0.7,
                           "attribution has collapsed - the convention is no longer placing "
                           "most files, which is a different failure from the ratchet below")
        unattributed = len(files) - len(placed)
        self.assertLessEqual(
            unattributed, self.UNATTRIBUTED_BASELINE,
            f"{unattributed} test files are unattributed against a declared {self.UNATTRIBUTED_BASELINE}. "
            f"Give the new one a home, or lower the baseline when one gains a home - never raise "
            f"it to make this green.")

    def test_the_census_attributes_its_own_tests_to_itself(self) -> None:
        """tools/ holds modules literally named test_*.py, so a prefix-based skip rule
        would make the suite's own guards permanently invisible to the census."""
        for test_file, module in (("tools/tests/test_test_census.py", "tools/test_census.py"),
                                  ("tools/tests/test_test_noise.py", "tools/test_noise.py")):
            with self.subTest(test_file):
                self.assertEqual(tc.attribute(self.REPO, test_file), (module, "name"))

    def test_an_unattributed_file_says_why_in_terms_of_the_convention(self) -> None:
        """The reason has to be actionable: which rule missed, and against what.

        The file is DERIVED, not named. This used to assert against
        `tools/tests/test_commit_msg_hook.py`, and it broke the day a fixture inside that file
        had to stub `tools/skill-tests.sh` - one incidental mention of a sibling module's stem
        moved it from unattributed to attributed-by-reference, and a test about the census's
        WORDING failed for a reason that had nothing to do with wording.

        Pinning the property to one file's current content is the selection-bias shape (LL0044):
        the example was chosen by an author, and the test silently became a test of that choice.
        Reading whichever files are unattributed today asserts the rule instead.
        """
        files = [f for f in tc.test_files(self.REPO) if "bench/fixtures" not in f.as_posix()]
        unattributed = [(f, tc.attribute(self.REPO, f)[1])
                        for f in files if tc.attribute(self.REPO, f)[0] is None]
        self.assertTrue(unattributed,
                        "no file is unattributed, so the reason-wording rule is unexercised - "
                        "if the convention now places everything, delete this test deliberately")
        for rel, why in unattributed:
            with self.subTest(rel.as_posix()):
                self.assertIn(rel.name, why, "the reason does not name the file it is about")
                # Every branch of `attribute` that declines to place a file: nothing sits
                # BESIDE it, it could not be READ, it matches no module by NAME and REFERENCES
                # none, or it references several equally. Each names the rule that missed.
                self.assertTrue(
                    any(w in why for w in ("beside", "read", "name", "references")),
                    f"the reason names no rule a reader could act on: {why!r}")


class PruneCandidateTests(unittest.TestCase):
    """US0507: a test no mutation of its own module can kill, and the record of removing it."""

    def _census(self, root: Path) -> dict:
        return tc.census(_junit([
            ("pkg.tests.test_alpha.AlphaTests", "test_kills", 0.1),
            ("pkg.tests.test_alpha.AlphaTests", "test_kills_nothing", 0.9),
        ]), root)

    def test_a_test_no_mutation_kills_is_a_candidate(self) -> None:
        """AC1: killed by others, killed by nothing of its own, so it is a candidate."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = self._census(root)
            killer = "pkg/tests/test_alpha.py::AlphaTests::test_kills"
            idle = "pkg/tests/test_alpha.py::AlphaTests::test_kills_nothing"
            evidence = {
                "tests_run": [killer, idle],
                "mutants": [
                    {"id": "pkg/alpha.py:1:return-1", "file": "pkg/alpha.py",
                     "verdict": "killed", "killed_by": [killer]},
                    {"id": "pkg/alpha.py:1:return-0", "file": "pkg/alpha.py",
                     "verdict": "killed", "killed_by": [killer]},
                ],
            }
            out = tc.prune_candidates(report, evidence)
            cands = {c["test"]: c for c in out["candidates"]}
            self.assertIn(idle, cands)
            self.assertNotIn(killer, cands)
            self.assertEqual(cands[idle]["module"], "pkg/alpha.py")
            # The mutants it failed to catch are NAMED, so the nomination is arguable.
            self.assertEqual(sorted(cands[idle]["uncaught"]),
                             ["pkg/alpha.py:1:return-0", "pkg/alpha.py:1:return-1"])

    def test_a_module_whose_mutants_were_all_survivors_yields_no_candidates(self) -> None:
        """No mutant killed anywhere means the run discriminated nothing: judge nobody."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = self._census(root)
            evidence = {
                "tests_run": ["pkg/tests/test_alpha.py::AlphaTests::test_kills",
                              "pkg/tests/test_alpha.py::AlphaTests::test_kills_nothing"],
                "mutants": [{"id": "m1", "file": "pkg/alpha.py",
                             "verdict": "survived", "killed_by": []}],
            }
            out = tc.prune_candidates(report, evidence)
            self.assertEqual(out["candidates"], [])
            self.assertEqual([i["module"] for i in out["inconclusive"]], ["pkg/alpha.py"])
            self.assertIn("killed", out["inconclusive"][0]["why"])

    def test_evidence_that_does_not_say_which_tests_ran_is_inconclusive(self) -> None:
        """Without the run's test list, 'killed nothing' and 'never ran' are the same fact."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = self._census(root)
            evidence = {"mutants": [
                {"id": "m1", "file": "pkg/alpha.py", "verdict": "killed",
                 "killed_by": ["pkg/tests/test_alpha.py::AlphaTests::test_kills"]}]}
            out = tc.prune_candidates(report, evidence)
            self.assertEqual(out["candidates"], [])
            self.assertEqual(len(out["inconclusive"]), 1)
            self.assertIn("which tests ran", out["inconclusive"][0]["why"])

    def test_a_test_outside_the_mutation_run_is_unjudged_not_a_candidate(self) -> None:
        """A test the mutation command never selected cannot have killed anything."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            report = self._census(root)
            killer = "pkg/tests/test_alpha.py::AlphaTests::test_kills"
            absent = "pkg/tests/test_alpha.py::AlphaTests::test_kills_nothing"
            evidence = {
                "tests_run": [killer],
                "mutants": [{"id": "m1", "file": "pkg/alpha.py", "verdict": "killed",
                             "killed_by": [killer]}],
            }
            out = tc.prune_candidates(report, evidence)
            self.assertEqual([c["test"] for c in out["candidates"]], [])
            self.assertEqual([u["test"] for u in out["unjudged"]], [absent])

    def test_a_removal_records_what_it_no_longer_protects(self) -> None:
        """AC2: the record states what the test asserted and why that is covered now."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = tc.record_removal(root, {
                "test": "pkg/tests/test_alpha.py::AlphaTests::test_kills_nothing",
                "module": "pkg/alpha.py",
                "asserted": "that a() returns a positive integer",
                "superseded_by": "pkg/tests/test_alpha.py::AlphaTests::test_kills, "
                                 "which pins the exact value",
                "evidence": "mutation run 01ABC: 2 killed mutants, none by this test",
            })
            self.assertTrue(path.exists())
            self.assertIn("retros/evidence", path.as_posix())  # tracked, not .local/
            row = json.loads(path.read_text(encoding="utf-8").strip().splitlines()[-1])
            self.assertEqual(row["test"],
                             "pkg/tests/test_alpha.py::AlphaTests::test_kills_nothing")
            self.assertEqual(row["asserted"], "that a() returns a positive integer")
            self.assertIn("test_kills", row["superseded_by"])
            self.assertTrue(row["recorded_at"])

    def test_a_removal_without_a_justification_is_refused_and_writes_nothing(self) -> None:
        """Pruning becomes coverage loss exactly here, so the refusal must leave no file."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError) as ctx:
                tc.record_removal(root, {"test": "pkg/tests/test_alpha.py::T::test_x",
                                         "module": "pkg/alpha.py"})
            self.assertIn("asserted", str(ctx.exception))
            self.assertFalse(tc.removal_record_path(root).exists())

    def test_a_removal_stating_what_it_asserted_but_not_why_is_refused(self) -> None:
        """Half the record is not the record: the 'why safe' half is the load-bearing one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError) as ctx:
                tc.record_removal(root, {"test": "pkg/tests/test_alpha.py::T::test_x",
                                         "module": "pkg/alpha.py",
                                         "asserted": "that a() returns 1"})
            self.assertIn("superseded_by", str(ctx.exception))
            self.assertFalse(tc.removal_record_path(root).exists())


class UnusableEvidenceTests(unittest.TestCase):
    """Evidence that cannot judge anybody has to say so, in the terms of the file given.

    The only mutation evidence this repo produces is `mutation.py`'s run report, and that
    report runs the whole test command per mutant: it knows a mutant died, never what
    killed it. Handed one, `candidates` reported no removal candidates and advised
    checking that the node ids agreed with the suite - a diagnosis of a file that has no
    node ids in it, delivered at exit 0. A tool that answers a question this evidence
    cannot settle is worse than one that refuses, because the answer looks like a result.
    """

    def _report(self, root: Path) -> dict:
        return tc.census(_junit([
            ("pkg.tests.test_alpha.AlphaTests", "test_kills", 0.1),
            ("pkg.tests.test_alpha.AlphaTests", "test_kills_nothing", 0.9),
        ]), root)

    def test_a_mutation_report_without_per_test_attribution_is_refused(self) -> None:
        """mutation.py's own record shape: file, class, occurrence, line, verdict."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            evidence = {
                "run_id": "01TEST",
                "test_cmd": "python3 -m pytest",
                "tests_run": ["pkg/tests/test_alpha.py::AlphaTests::test_kills"],
                "mutations": [
                    {"file": "pkg/alpha.py", "class": "comparison", "occurrence": 0,
                     "line": 1, "verdict": "killed"},
                    {"file": "pkg/alpha.py", "class": "boolean", "occurrence": 0,
                     "line": 2, "verdict": "survived"},
                ],
            }
            with self.assertRaises(ValueError) as ctx:
                tc.prune_candidates(self._report(root), evidence)
            why = str(ctx.exception)
            self.assertIn("killed_by", why)
            self.assertIn("pkg/alpha.py:1", why)

    def test_evidence_with_no_mutant_list_at_all_is_refused(self) -> None:
        """A file that is not mutation evidence must not read as a clean sweep."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError) as ctx:
                tc.prune_candidates(self._report(root), {"tests_run": [], "summary": {}})
            why = str(ctx.exception)
            self.assertIn("mutants", why)
            self.assertIn("mutations", why)

    def test_evidence_whose_mutant_list_is_empty_is_refused(self) -> None:
        """The shape of this repo's own mutation-report.json after a refused run."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError) as ctx:
                tc.prune_candidates(self._report(root),
                                    {"tests_run": [], "mutations": []})
            self.assertIn("no mutant", str(ctx.exception))

    def test_the_mutations_key_is_read_when_it_does_carry_attribution(self) -> None:
        """Refusing the shape is not refusing the source: attributed records still judge."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            killer = "pkg/tests/test_alpha.py::AlphaTests::test_kills"
            idle = "pkg/tests/test_alpha.py::AlphaTests::test_kills_nothing"
            evidence = {
                "tests_run": [killer, idle],
                "mutations": [
                    {"file": "pkg/alpha.py", "class": "comparison", "occurrence": 0,
                     "line": 7, "verdict": "killed", "killed_by": [killer]},
                ],
            }
            out = tc.prune_candidates(self._report(root), evidence)
            self.assertEqual([c["test"] for c in out["candidates"]], [idle])
            # No `id` field in that shape, so the mutant is named by where it sits.
            self.assertEqual(out["candidates"][0]["uncaught"], ["pkg/alpha.py:7:comparison"])

    def test_candidates_cli_refuses_unusable_evidence_instead_of_reporting_none(self) -> None:
        """The refusal has to reach the caller: non-zero, on stderr, no verdict printed."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            junit = root / "j.xml"
            junit.write_text(_junit([
                ("pkg.tests.test_alpha.AlphaTests", "test_kills", 0.1),
            ]), encoding="utf-8")
            ev = root / "ev.json"
            ev.write_text(json.dumps({
                "tests_run": ["pkg/tests/test_alpha.py::AlphaTests::test_kills"],
                "mutations": [{"file": "pkg/alpha.py", "class": "comparison",
                               "occurrence": 0, "line": 1, "verdict": "killed"}],
            }), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = tc.main(["--root", str(root), "candidates",
                              "--junit", str(junit), "--evidence", str(ev)])
            self.assertEqual(rc, 1)
            self.assertIn("killed_by", err.getvalue())
            self.assertNotIn("no removal candidates", out.getvalue())


class CliTests(unittest.TestCase):
    """The refusals have to reach the caller, not just the return value."""

    def test_record_removal_cli_exits_non_zero_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = tc.main(["--root", d, "record-removal",
                              "--test", "pkg/tests/test_alpha.py::T::test_x",
                              "--module", "pkg/alpha.py",
                              "--asserted", "that a() returns 1"])
            self.assertEqual(rc, 1)
            self.assertIn("superseded_by", err.getvalue())
            self.assertFalse(tc.removal_record_path(Path(d)).exists())

    def test_record_removal_cli_records_a_justified_removal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = tc.main(["--root", d, "record-removal",
                              "--test", "pkg/tests/test_alpha.py::T::test_x",
                              "--module", "pkg/alpha.py",
                              "--asserted", "that a() returns 1",
                              "--superseded-by", "test_kills, which pins the value"])
            self.assertEqual(rc, 0)
            self.assertTrue(tc.removal_record_path(Path(d)).exists())

    def test_candidates_cli_does_not_claim_a_clean_sweep_when_nothing_was_judged(self) -> None:
        """Found by running it: evidence whose node ids match no test in the run judged
        nobody, and the CLI still printed 'every test killed a mutant of its own module'.
        A tool must never report a verdict it did not reach."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            junit = root / "j.xml"
            junit.write_text(_junit([
                ("pkg.tests.test_alpha.AlphaTests", "test_kills", 0.1),
            ]), encoding="utf-8")
            ev = root / "ev.json"
            ev.write_text(json.dumps({
                "tests_run": ["pkg/tests/test_alpha.py::AlphaTests::test_renamed_away"],
                "mutants": [{"id": "m1", "file": "pkg/alpha.py", "verdict": "killed",
                             "killed_by": [
                                 "pkg/tests/test_alpha.py::AlphaTests::test_renamed_away"]}],
            }), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = tc.main(["--root", str(root), "candidates",
                              "--junit", str(junit), "--evidence", str(ev)])
            text = out.getvalue()
            self.assertEqual(rc, 0)
            self.assertNotIn("every test killed", text)
            self.assertIn("unjudged", text)
            self.assertIn("test_kills", text)

    def test_candidates_cli_says_so_when_every_judged_test_killed_something(self) -> None:
        """The clean sweep is still sayable, but only once a test was actually judged."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            junit = root / "j.xml"
            junit.write_text(_junit([
                ("pkg.tests.test_alpha.AlphaTests", "test_kills", 0.1),
            ]), encoding="utf-8")
            killer = "pkg/tests/test_alpha.py::AlphaTests::test_kills"
            ev = root / "ev.json"
            ev.write_text(json.dumps({
                "tests_run": [killer],
                "mutants": [{"id": "m1", "file": "pkg/alpha.py", "verdict": "killed",
                             "killed_by": [killer]}],
            }), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = tc.main(["--root", str(root), "candidates",
                              "--junit", str(junit), "--evidence", str(ev)])
            self.assertEqual(rc, 0)
            self.assertIn("every judged test killed", out.getvalue())

    def test_report_cli_prints_the_unattributed_count(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            junit = root / "j.xml"
            junit.write_text(_junit([
                ("pkg.tests.test_alpha.AlphaTests", "test_one", 0.1),
                ("pkg.tests.test_hook_contract.HookTests", "test_hook_is_executable", 0.4),
            ]), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = tc.main(["--root", str(root), "report", "--junit", str(junit)])
            text = out.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("pkg/alpha.py", text)
            self.assertIn("unattributed (1 tests)", text)
            # Named, never a bare count - the file, its cost, and one node id from it.
            self.assertIn("pkg/tests/test_hook_contract.py", text)
            self.assertIn("test_hook_is_executable", text)


class ImportabilityTests(unittest.TestCase):

    def test_a_conftest_puts_this_directory_on_the_path(self) -> None:
        """MUTANT: delete tools/tests/conftest.py.

        Pinned on the FILE, because the per-file inserts it replaces are exactly what gets
        forgotten - and a guard that only checked the two modules which happen to carry one
        would go green the moment a third arrives without it.
        """
        conftest = TESTS_DIR / "conftest.py"
        self.assertTrue(conftest.is_file(),
                        "tools/tests has no conftest.py, so a sibling import resolves under "
                        "unittest and not under pytest")
        self.assertTrue(
            tc_conftest_inserts_path(conftest.read_text(encoding="utf-8")),
            "the conftest does not CALL sys.path.insert - its own docstring names the call, so "
            "a text search is satisfied with the call deleted")

    def test_every_module_here_imports_under_pytest(self) -> None:
        """MUTANT: revert the conftest, or add a module with an unresolvable sibling import.

        Runs pytest in COLLECT-ONLY mode over the whole directory: collection is where an
        unresolvable import fails, and it costs seconds rather than a full suite run.
        """
        result = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", "--collect-only", "-q", str(TESTS_DIR)],
            cwd=REPO, capture_output=True, text=True, timeout=300)
        self.assertEqual(
            0, result.returncode,
            f"a module under tools/tests does not import under pytest:\n"
            f"{result.stdout[-2000:]}\n{result.stderr[-2000:]}")



class HandCopiedMirrorTests(unittest.TestCase):
    """A test file must not hand-list a set the production tree already owns.

    A hand-written mirror is a second copy, and it goes stale the way every second copy does -
    silently, and in the direction that makes the tests pass while covering less. Seven such
    mirrors were found in one suite; `hookutil.py` derives them from the thing that owns them.

    A deliberate exception stays hand-maintained: an INVENTORY that is itself the assertion,
    such as the record of deleted commands in `test_lean_commit_lanes.py`. It is exempt by
    DECLARATION, so the distinction stays a decision rather than a habit.
    """

    #: What a production-owned set looks like when it has been copied into a test: a literal
    #: naming shipped script files. Matched on the CONTENT, not on a variable name, because a
    #: copy renamed is still a copy.
    _SCRIPT_LITERAL = re.compile(r'"[a-z_]+\.py"\s*,\s*"[a-z_]+\.py"\s*,\s*"[a-z_]+\.py"')

    #: How a file declares that its list IS the assertion rather than a mirror of one.
    _INVENTORY_MARKER = "HAND-MAINTAINED ON PURPOSE"

    #: BOTH suite directories. Resolving the scan from `__file__` looked right and searched the
    #: one directory that had almost nothing to find: `tools/tests` held a single declared
    #: inventory, while the directory this guard's own bug named held SIX mirrors it could not
    #: see. A guard aimed at the wrong tree passes for the same reason an empty one does.
    _SUITE_DIRS = ("tools/tests", ".claude/skills/sdlc-studio/scripts/tests")

    #: The mirrors already in the tree when the scan was widened. SHRINK-ONLY: a name may leave
    #: this set, never join it. Failing on six pre-existing files would get the guard switched
    #: off, and a switched-off guard catches nothing; refusing the SEVENTH is what it is for.
    _KNOWN_MIRRORS = frozenset({
        "test_artifact.py", "test_confinement.py", "test_refine.py",
        "test_repo_hygiene.py", "test_repo_map.py",
    })

    def _mirrors(self) -> list[str]:
        found = []
        for rel in self._SUITE_DIRS:
            for path in sorted((REPO / rel).glob("test_*.py")):
                text = path.read_text(encoding="utf-8")
                if self._INVENTORY_MARKER in text:
                    continue                  # a declared inventory, not a mirror
                if self._SCRIPT_LITERAL.search(text):
                    found.append(path.name)
        return found

    def test_no_new_hand_copied_script_list(self) -> None:
        """MUTANT: paste a third copy of the hook's script set into a test file.

        The declared inventory is exempt; anything else with the same shape is the seventh copy
        this guard exists to refuse. Scans BOTH suite directories - the first version resolved
        its directory from `__file__` and never looked at the tree its own bug named.
        """
        offenders = [n for n in self._mirrors() if n not in self._KNOWN_MIRRORS]
        self.assertEqual(
            [], offenders,
            f"these test files hand-list shipped scripts instead of deriving them from the "
            f"thing that owns them (see hookutil.py): {offenders}")

    def test_the_known_mirror_set_only_shrinks(self) -> None:
        """MUTANT: leave a repaired file in the baseline, or widen the baseline to pass.

        A baseline that may grow is not a ratchet, it is a suppression list. Every name in it
        must still be a real mirror; one that has been fixed has to leave, or the set silently
        re-exempts a file that could offend again.
        """
        stale = sorted(self._KNOWN_MIRRORS - set(self._mirrors()))
        self.assertEqual(
            [], stale,
            f"these files are no longer hand-copied mirrors, so they must leave the baseline - "
            f"a set that only ever grows exempts what it forgot: {stale}")


class DuplicateTestClassTests(unittest.TestCase):
    """A test module must not define the same class name twice.

    Python does not complain: the second `class Foo` simply replaces the first, and every test
    on the earlier one stops running. Nothing else notices - the suite still passes, the count
    just goes down, and a `-k` verifier pointed at a vanished test reports "ran NO tests" while
    the test is still sitting in the file.

    Found when `US0609` added a second `FileAndCloseTests` to `test_sprint.py` and silently
    removed ELEVEN tests from the suite. Two units' acceptance verifiers had been failing on it
    for hours and were read as stale selectors rather than as a missing class.
    """

    _SUITE_DIRS = ("tools/tests", ".claude/skills/sdlc-studio/scripts/tests")

    def _duplicates(self) -> dict:
        import ast  # noqa: PLC0415
        out = {}
        for rel in self._SUITE_DIRS:
            for path in sorted((REPO / rel).glob("test_*.py")):
                try:
                    tree = ast.parse(path.read_text(encoding="utf-8"))
                except SyntaxError:
                    continue
                seen, dupes = set(), []
                for node in tree.body:            # module level only - a nested class is scoped
                    if isinstance(node, ast.ClassDef):
                        if node.name in seen:
                            dupes.append(node.name)
                        seen.add(node.name)
                if dupes:
                    out[path.name] = sorted(set(dupes))
        return out

    def test_no_test_module_defines_a_class_name_twice(self) -> None:
        """MUTANT: add a second class of an existing name to any test module.

        Parsed, not grepped: the question is whether two module-level ClassDefs share a name,
        and a grep for `class Foo` cannot tell a definition from a mention in a docstring.
        """
        dupes = self._duplicates()
        self.assertEqual(
            {}, dupes,
            f"these test modules define a class name twice, so the SECOND silently replaces the "
            f"first and every test on the earlier one stops running: {dupes}")

    def test_the_guard_sees_a_planted_duplicate(self) -> None:
        """The control. MUTANT: return {} unconditionally.

        A guard that reports nothing over a clean tree is indistinguishable from one that
        cannot see, which is exactly the state this defect lived in.
        """
        import ast  # noqa: PLC0415
        src = "class A:\n    pass\n\n\nclass A:\n    pass\n"
        names = [n.name for n in ast.parse(src).body if isinstance(n, ast.ClassDef)]
        self.assertEqual(["A", "A"], names,
                         "the detector's own premise is wrong - two module-level ClassDefs of "
                         "one name should both be present in the AST")




class AttributionTests(unittest.TestCase):
    """BG0578: a test file's owner was decided by how often a module's name happened to appear
    in its prose, so adding ONE mention of a sibling moved a file from an owner to unattributed.
    A file's subject changing because somebody wrote a sentence is not attribution."""

    REPO = REPO

    def _tree(self, d) -> Path:
        root = Path(d)
        (root / "pkg").mkdir(parents=True)
        for name in ("alpha", "beta"):
            (root / "pkg" / f"{name}.py").write_text("x = 1\n", encoding="utf-8")
        (root / "pkg" / "tests").mkdir()
        return root

    def _test_file(self, root: Path, name: str, body: str) -> str:
        rel = f"pkg/tests/{name}"
        (root / rel).write_text(body, encoding="utf-8")
        return rel

    def _unit(self, root: Path, uid: str, affects: str) -> None:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Open\n> **Affects:** {affects}\n", encoding="utf-8")

    def test_a_module_level_subject_marker_decides_the_owner(self) -> None:
        """MUTANT: delete the marker lookup from `attribute`.

        The marker outranks the by-name route too: measured over the two test trees, 95 of 204
        files are placed by name, so a marker consulted after it would be ignored on most of
        the corpus."""
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            rel = self._test_file(root, "test_alpha.py",
                                  "# test-census-subject: pkg/beta.py\nimport alpha\n")
            mod, how = tc.attribute(root, rel)
            self.assertEqual("pkg/beta.py", mod, f"the declared subject lost to {how}")
            self.assertEqual("marker", how)

    def test_a_single_script_declaration_decides_and_a_multi_script_one_defers(self) -> None:
        """MUTANT: widen the declaration route to take the first script of a multi-script
        declaration.

        Most files here are declared by several units naming many scripts between them. A rule
        that only handles the single-script case decides almost nothing; a rule that guesses at
        the multi-script case decides the wrong thing."""
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            rel = self._test_file(root, "test_zeta.py", "alpha and beta\n")
            self._unit(root, "BG0001", f"{rel}, pkg/beta.py")
            mod, how = tc.attribute(root, rel)
            self.assertEqual("pkg/beta.py", mod)
            self.assertEqual("affects", how)
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            rel = self._test_file(root, "test_zeta.py", "alpha alpha beta\n")
            self._unit(root, "BG0001", f"{rel}, pkg/alpha.py, pkg/beta.py")
            mod, how = tc.attribute(root, rel)
            self.assertEqual("reference", how,
                             "a declaration naming several scripts decided the owner anyway")

    def test_counting_is_the_fallback_and_says_so(self) -> None:
        """MUTANT: delete the counting fallback so a file with no declared subject is dropped."""
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            rel = self._test_file(root, "test_zeta.py", "alpha alpha alpha beta\n")
            mod, how = tc.attribute(root, rel)
            self.assertEqual("pkg/alpha.py", mod)
            self.assertEqual("reference", how, "the fallback did not say which route answered")

    def test_a_tie_with_a_declared_owner_is_attributed_not_unattributed(self) -> None:
        """MUTANT: return the unattributed result whenever the counts tie, before the declared
        routes are consulted.

        A tie already NAMES its tied candidates today, so asserting the wording alone passes on
        unmodified code. What is false at HEAD is that the file gets an owner at all.

        THE FIXTURE HAS TO TIE. The first cut's body mentioned alpha once and beta once - but
        the marker LINE names alpha too, so the counts were two against one and the mutant's
        branch was never reached. The control below carries the same counting profile with the
        marker replaced by an ordinary comment, and must come back unattributed ON A TIE: that
        is what shows this row reaches the branch it is about."""
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            body = "alpha beta beta\n"
            control = self._test_file(root, "test_eta.py", f"# subject is pkg/alpha.py\n{body}")
            tied_mod, tied_how = tc.attribute(root, control)
            self.assertIsNone(tied_mod,
                              f"the fixture does not TIE, so the branch this row is about is "
                              f"never reached: {tied_how}")
            self.assertIn("equally", tied_how,
                          f"the fixture is unattributed for some reason other than a tie: "
                          f"{tied_how}")
            rel = self._test_file(root, "test_zeta.py",
                                  f"# test-census-subject: pkg/alpha.py\n{body}")
            mod, how = tc.attribute(root, rel)
            self.assertEqual("pkg/alpha.py", mod,
                             "a tie with a declared owner was still reported unattributed")
            self.assertEqual("marker", how)

    def test_a_marker_inside_a_fixture_string_cannot_claim_the_subject(self) -> None:
        """MUTANT: search the whole text for the marker instead of the file's head.

        The guarantee the pattern cannot give on its own. `re.M` anchors at every line start,
        including the lines of a triple-quoted fixture, and this module's own tests carry marker
        text in exactly that position - so a file whose fixture mentions the marker would have
        its OWNER decided by the fixture. The comment claimed this for a whole release while the
        code did not implement it, and no row here noticed."""
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            deep = self._test_file(
                root, "test_theta.py",
                "import alpha\n# alpha is what this file actually covers\n"
                + "# padding\n" * 60
                + 'FIXTURE = """\n# test-census-subject: pkg/beta.py\n"""\n')
            mod, how = tc.attribute(root, deep)
            self.assertNotEqual("pkg/beta.py", mod,
                                f"a marker inside a fixture string claimed the subject: {how}")
            self.assertEqual("pkg/alpha.py", mod,
                             f"the file was not placed by what it actually references: {how}")

    def test_one_more_mention_cannot_move_the_grammar_module(self) -> None:
        """MUTANT: remove the marker branch so mention frequency decides the file again.

        The exact regression: this file was moved to unattributed by an edit that added one
        mention of a sibling. It is edited on a COPY carrying its sibling directory, because a
        copy beside the original is an untracked file the repo-writes lane refuses and a copy
        alone answers that no source module sits beside it."""
        rel = ".claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py"
        before = tc.attribute(self.REPO, rel)
        self.assertIsNotNone(before[0], f"the live file is unattributed: {before[1]}")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # The LAYOUT travels with the copy: a subject marker is a path relative to the
            # root being scanned, so a copy that flattens the tree changes what the marker
            # means. Copying into the same relative place keeps the fixture honest about what
            # the edit changed - one added mention, and nothing else.
            dst = root / ".claude/skills/sdlc-studio/scripts"
            dst.parent.mkdir(parents=True)
            shutil.copytree(self.REPO / ".claude/skills/sdlc-studio/scripts", dst,
                            ignore=shutil.ignore_patterns("__pycache__", ".local"))
            copy = dst / "tests" / "test_cli_grammar.py"
            copy.write_text(copy.read_text(encoding="utf-8")
                            + "\n# transition transition transition\n", encoding="utf-8")
            after = tc.attribute(root, rel)
        self.assertEqual(Path(before[0]).name, Path(after[0] or "").name,
                         f"one more mention moved the owner: {before} -> {after}")

    def test_the_owner_map_is_stable_under_a_prose_only_edit(self) -> None:
        """MUTANT: drop the per-file owner from the entry point's payload, emitting only the
        tally.

        The ratchet counts UNATTRIBUTED files, so an owner flip from one module to another
        leaves its number untouched - the count cannot observe the defect in this bug's own
        title, and the map can."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dst = root / ".claude/skills/sdlc-studio/scripts"
            dst.parent.mkdir(parents=True)
            shutil.copytree(self.REPO / ".claude/skills/sdlc-studio/scripts", dst,
                            ignore=shutil.ignore_patterns("__pycache__", ".local"))
            files = [f for f in tc.test_files(root)]
            self.assertGreater(len(files), 20, "the copied tree carries no test files")
            # THROUGH THE SHIPPED ENTRY POINT, which is what the criterion says and what the
            # declared mutant edits. The first cut called `attribute` in a loop, so dropping the
            # per-file owner from the payload changed nothing it looked at and the mutant
            # survived - three seats found the same hole.
            before = self._owner_map(root, files)
            target = dst / "tests" / "test_cli_grammar.py"
            target.write_text(target.read_text(encoding="utf-8")
                              + "\n# sprint sprint sprint sprint\n", encoding="utf-8")
            after = self._owner_map(root, files)
        # NOT VACUOUS. An entry point that reports no owners at all makes both maps empty and
        # "nothing moved" trivially true, which is precisely the mutant this row names.
        self.assertGreater(len(before), 20,
                           f"the entry point reported owners for {len(before)} file(s), so a "
                           f"comparison over them cannot show a move")
        moved = {k: (before[k], after.get(k)) for k in before if before[k] != after.get(k)}
        self.assertEqual({}, moved, f"a prose-only edit moved these files' owners: {moved}")

    def _owner_map(self, root: Path, files: list) -> dict:
        """The per-file owner map AS THE SHIPPED ENTRY POINT REPORTS IT.

        `census` takes a completed run's junit report, so one is synthesised naming every test
        file in the tree - the map is what is under test, not the timings."""
        cases = "".join(
            f'<testcase classname="{tc.dotted(f)}" name="t" time="0.01"></testcase>'
            for f in files)
        report = tc.census(f'<testsuite name="s">{cases}</testsuite>', root)
        return {tf: row["module"] for row in report["modules"] for tf in row["test_files"]}




class TheGuardSeesTheCallNotTheDocstringTests(unittest.TestCase):
    """BG0493: the conftest guard asserted the TEXT `sys.path.insert` appeared in the file, and
    the file's own docstring names the call - so deleting the call left the guard green. A guard
    reading its own explanation."""

    CONFTEST = Path(__file__).resolve().parent / "conftest.py"

    def test_deleting_the_call_reddens_ac1(self) -> None:
        """MUTANT: read the file's text again instead of parsing it.

        Driven on a COPY: the existing verifier hard-codes the tracked path, and a test that
        edited the real file would trip the repo-writes lane and leave the tree dirty."""
        src = self.CONFTEST.read_text(encoding="utf-8")
        self.assertTrue(tc_conftest_inserts_path(src), "the live conftest makes no such call")
        without = "\n".join(l for l in src.splitlines()
                            if not l.strip().startswith("sys.path.insert("))
        self.assertIn("sys.path.insert", without,
                      "the docstring no longer names the call, so this fixture cannot show the "
                      "difference between reading the prose and reading the code")
        self.assertFalse(tc_conftest_inserts_path(without),
                         "the guard is satisfied with the call deleted, because it is reading "
                         "the docstring that mentions it")


# BG0963: a wall-clock bound in the parallel partition measures the machine's load, not the code.

#: The suite directories the wall-clock census reads, relative to the repository root.
_WALL_CLOCK_DIRS = ("tools/tests", ".claude/skills/sdlc-studio/scripts/tests")
#: The `time` functions a duration is read from.
_CLOCKS = frozenset({"monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "time",
                     "time_ns"})
#: The assertions that order two values, each with whether its first argument is the larger.
#: An equality is not a bound, so it is not read.
_ORDERING_ASSERTS = {"assertLess": False, "assertLessEqual": False, "assertGreater": True,
                     "assertGreaterEqual": True}
_ORDERING_OPS = (ast.Lt, ast.LtE, ast.Gt, ast.GtE)
#: The census reads a clock only through an import of `time`, so a module with no line holding
#: `import ... time` or `from time import` is not parsed. One spelt across lines is not seen.
_IMPORTS_TIME = re.compile(r"\bimport\s[^\n#]*\btime\b|\bfrom\s+time\s+import\b")


def _names_marker(nodes, marker: str, aliases: set[str]) -> bool:
    """Whether decorators or a `pytestmark` value carry `marker`, spelt out or through a name
    an assignment in the module binds to it, such as `serial = pytest.mark.serial_only`."""
    return any((isinstance(sub, ast.Attribute) and sub.attr == marker)
               or (isinstance(sub, ast.Name) and sub.id in aliases)
               for node in nodes for sub in ast.walk(node))


class _Measured:
    """Which expressions in one module carry a clock reading taken in the test's own process.

    A name is measured when a binding gives it a value that reads a clock or a measured name:
    `t0 = time.monotonic()`, `elapsed = time.monotonic() - t0`, `spent.append(perf_counter() -
    t)`, a `self.` attribute any method of the class binds so, and a helper's return, by
    position when the helper returns a tuple (`rc, out, secs = self._commit()`)."""

    def __init__(self, tree: ast.Module) -> None:
        self.modules, self.bare = set(), set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.modules |= {a.asname or a.name for a in node.names if a.name == "time"}
            elif isinstance(node, ast.ImportFrom) and node.module == "time":
                self.bare |= {a.asname or a.name for a in node.names if a.name in _CLOCKS}
        self.returns: dict[str, object] = {}
        self._signs: dict[int, tuple] = {}
        self._pairs: dict[int, list] = {}

    @staticmethod
    def _callee(func) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                and func.value.id in ("self", "cls"):
            return func.attr
        return None

    def _sign(self, node) -> tuple:
        """What `node` reads, walked once: a clock call, the names, and the callees."""
        got = self._signs.get(id(node))
        if got is None:
            clock, names, callees = False, set(), set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    clock = clock or (isinstance(f, ast.Attribute) and f.attr in _CLOCKS
                                      and isinstance(f.value, ast.Name)
                                      and f.value.id in self.modules) \
                        or (isinstance(f, ast.Name) and f.id in self.bare)
                    callees.add(self._callee(f))
                elif isinstance(sub, ast.Name):
                    names.add(sub.id)
                elif isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name) \
                        and sub.value.id in ("self", "cls"):
                    names.add("." + sub.attr)
            got = self._signs[id(node)] = (clock, frozenset(names), frozenset(callees - {None}))
        return got

    def reads(self, node, names: set[str]) -> bool:
        clock, read, callees = self._sign(node)
        if clock or not read.isdisjoint(names):
            return True
        return any(ret is True or (isinstance(ret, list) and any(ret))
                   for ret in map(self.returns.get, callees))

    @staticmethod
    def _keys(target) -> list[str]:
        if isinstance(target, ast.Name):
            return [target.id]
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) \
                and target.value.id in ("self", "cls"):
            return ["." + target.attr]
        if isinstance(target, ast.Starred):
            return _Measured._keys(target.value)
        if isinstance(target, (ast.Tuple, ast.List)):
            return [k for e in target.elts for k in _Measured._keys(e)]
        return []

    def _bindings(self, func) -> list:
        got = self._pairs.get(id(func))
        if got is None:
            got = []
            for node in ast.walk(func):
                if isinstance(node, ast.Assign):
                    got += [(t, node.value) for t in node.targets]
                elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and node.value is not None:
                    got.append((node.target, node.value))
                elif isinstance(node, (ast.For, ast.comprehension)):
                    got.append((node.target, node.iter))
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                        and node.func.attr in ("append", "extend", "add") and node.args:
                    got.append((node.func.value, node.args[0]))
            self._pairs[id(func)] = got
        return got

    def taint(self, func, names: set[str]) -> set[str]:
        """The names `func` binds to a measured value, with `names` measured already."""
        names = set(names)
        while True:
            before = len(names)
            for target, value in self._bindings(func):
                ret = (self.returns.get(self._callee(value.func) or "")
                       if isinstance(value, ast.Call) else None)
                if isinstance(ret, list) and isinstance(target, (ast.Tuple, ast.List)) \
                        and len(ret) == len(target.elts):
                    for elt, hot in zip(target.elts, ret):
                        if hot:
                            names.update(self._keys(elt))
                elif self.reads(value, names):
                    names.update(self._keys(target))
            if len(names) == before:
                return names

    def summarise(self, func, local: set[str]) -> None:
        for node in ast.walk(func):
            if isinstance(node, ast.Return) and node.value is not None:
                if isinstance(node.value, ast.Tuple):
                    self.returns[func.name] = [self.reads(e, local) for e in node.value.elts]
                elif self.reads(node.value, local):
                    self.returns[func.name] = True


def _bounds(measured: _Measured, func, local: set[str]):
    """Each ordering assertion in `func` that holds a measured value below one that is not: an
    `assert`, an `assertLess`-family call, or a comparison handed to `assertTrue`/`False`. A
    lower bound is not one, since load only lengthens a duration; nor are two measured sides,
    such as a deadline polled against the clock."""
    def compares(node, negated=False):
        for cmp in ast.walk(node):
            if isinstance(cmp, ast.Compare):
                sides = [cmp.left, *cmp.comparators]
                for op, a, b in zip(cmp.ops, sides, sides[1:]):
                    if isinstance(op, _ORDERING_OPS):
                        larger_first = isinstance(op, (ast.Gt, ast.GtE)) != negated
                        yield (cmp, b, a) if larger_first else (cmp, a, b)

    for node in ast.walk(func):
        found = []
        if isinstance(node, ast.Assert):
            found = list(compares(node.test))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _ORDERING_ASSERTS and len(node.args) >= 2:
                a, b = node.args[:2]
                found = [(node, b, a) if _ORDERING_ASSERTS[node.func.attr] else (node, a, b)]
            elif node.func.attr in ("assertTrue", "assertFalse") and node.args:
                found = list(compares(node.args[0], node.func.attr == "assertFalse"))
        for site, low, high in found:
            if measured.reads(low, local) and not measured.reads(high, local):
                yield site


def _module_sites(src: str, label: str) -> list[tuple[str, bool]]:
    """`(<label>::<Class>::<function>:<line>, marked)` for each upper bound of a measured
    duration, `marked` when its function carries both `serial_only`, which keeps it out of the
    parallel pass, and `boundary_only`, which keeps it out of a commit's pytest run (not the
    commit hook's unittest fallback: BG1144). Either may sit on the function, its class, or the
    module's `pytestmark`."""
    tree = ast.parse(src)
    measured = _Measured(tree)
    if not (measured.modules or measured.bare):
        return []
    module = [node.value for node in tree.body if isinstance(node, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets)]

    def carries(marker: str):
        aliases = {t.id for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   for t in node.targets if isinstance(t, ast.Name)
                   and _names_marker([node.value], marker, set())}
        return lambda cls, func: _names_marker(
            [*module, *func.decorator_list, *(cls.decorator_list if cls else [])], marker, aliases)

    serial, boundary = carries("serial_only"), carries("boundary_only")
    scopes = [(None, node) for node in tree.body
              if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    scopes += [(node, f) for node in tree.body if isinstance(node, ast.ClassDef)
               for f in node.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
    attrs: dict[str, set[str]] = {}
    for _ in range(3):   # a helper returning another helper's measurement
        for cls, func in scopes:
            local = measured.taint(func, attrs.get(cls.name, set()) if cls else set())
            if cls is not None:
                attrs.setdefault(cls.name, set()).update(n for n in local if n.startswith("."))
            measured.summarise(func, local)
    out = []
    for cls, func in scopes:
        marked = serial(cls, func) and boundary(cls, func)
        local = measured.taint(func, attrs.get(cls.name, set()) if cls else set())
        where = "::".join(x for x in (label, cls.name if cls else None, func.name) if x)
        out += [(f"{where}:{site.lineno}", marked) for site in _bounds(measured, func, local)]
    return out


def _module_bounds(src: str, label: str) -> list[str]:
    """The sites `_module_sites` finds that a commit's pytest run reaches: those not `marked`."""
    return [site for site, marked in _module_sites(src, label) if not marked]


def wall_clock_sites(repo: Path) -> list[tuple[str, bool]]:
    """`_module_sites` over each `test_*.py` in both suite directories that `_IMPORTS_TIME`
    passes, marked and unmarked, so one read gives AC1 both its reach and its finding."""
    out = []
    for rel in _WALL_CLOCK_DIRS:
        for path in sorted((repo / rel).glob("test_*.py")):
            src = path.read_text(encoding="utf-8")
            if _IMPORTS_TIME.search(src):
                out += _module_sites(src, f"{rel}/{path.name}")
    return out


SKILL_TESTS = ".claude/skills/sdlc-studio/scripts/tests"

try:
    import pytest
    #: Running the bounds slowed cost 67 s at a load average of 20, so a commit's pytest run
    #: defers it and the push runs it, beside the bounds it judges (the hook's unittest fallback
    #: does not: BG1144).
    boundary = pytest.mark.boundary_only
except ImportError:     # the unittest runner deselects nothing, so there is no marker to set
    def boundary(test):
        return test

#: The wall-clock bounds in the modules BG0963 names, each kept with its constant, left out of a
#: commit's pytest run and run at push in the serial phase after the parallel pass (the commit
#: hook's unittest fallback still runs them: BG1144). HAND-MAINTAINED ON PURPOSE: the list is
#: the assertion that every one of them still runs and still bounds.
_SERIAL_BOUNDS = (
    f"{SKILL_TESTS}/test_status.py::GatherPerformanceTests::"
    "test_the_shipped_command_answers_a_corpus_shaped_fixture_with_the_headline_first",
    f"{SKILL_TESTS}/test_status.py::HintPerformanceTests::"
    "test_the_hint_command_answers_the_corpus_shaped_fixture_inside_the_bound",
    f"{SKILL_TESTS}/test_lean_test_selection.py::SelectionTests::"
    "test_selection_is_fast_on_this_repository",
    f"{SKILL_TESTS}/test_mutation.py::KilledMutantsCarryTheirKillerTests::"
    "test_a_backgrounded_child_does_not_hang_the_run",
    f"{SKILL_TESTS}/test_mutation.py::TheRunLeavesNothingBehindTests::"
    "test_a_backgrounded_child_is_reaped_on_the_normal_exit_path",
    f"{SKILL_TESTS}/test_mutation.py::TheRunLeavesNothingBehindTests::"
    "test_the_timeout_still_bounds_a_genuinely_hanging_command",
    "tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::"
    "test_the_lanes_run_concurrently",
    "tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::"
    "test_a_hangup_or_terminate_stops_every_lane_with_the_hook",
    "tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::"
    "test_a_lane_that_ignores_terminate_is_killed_rather_than_hanging_the_hook",
)
#: The upper bounds the census found outside those modules, judged by collection and by the
#: census's reach alone: AC3 does not run them under `_SLOW_CLOCK`.
_SERIAL_IN_PROCESS = (
    "tools/tests/test_lean_refusal_log.py::RefusalLogTests::"
    "test_a_refused_commit_logs_its_lane_and_a_clean_one_logs_nothing",
    f"{SKILL_TESTS}/test_config.py::IntegrationTests::"
    "test_status_gathers_a_fixture_never_this_repository",
    f"{SKILL_TESTS}/test_lean_lock_busy_eacces.py::LockBusyEaccesTests::"
    "test_a_busy_lock_reported_as_eacces_is_waited_on",
    f"{SKILL_TESTS}/test_lean_lock_errors.py::LockErrorTests::"
    "test_a_non_busy_flock_error_is_named_at_once",
    f"{SKILL_TESTS}/test_lean_lock_fails_closed.py::LockFailsClosedTests::"
    "test_a_killed_holder_does_not_wedge_the_next_writer",
    f"{SKILL_TESTS}/test_lean_v61_last_lows.py::V61LastLowsTests::"
    "test_the_note_parser_is_linear_on_repeated_names",
    f"{SKILL_TESTS}/test_lean_v61_review_residue.py::V61ReviewResidueTests::"
    "test_the_note_parser_is_linear",
)
#: Bounded by the release gate's own per-verifier ceiling rather than by a clock it reads, so it
#: stays in the parallel pass, and out of a commit's pytest run.
_BOUNDARY_CEILING = ("tools/tests/test_lean_release_verify.py::ReleaseVerifyTests::"
                     "test_the_measured_red_criteria_pass_or_are_retired")

#: A pytest plugin that makes the code under test look a day slower: each process the test
#: starts and each `os.killpg` it calls moves `time.monotonic`, `perf_counter` and `time` on by a
#: day. `subprocess` waits read the clock it bound at import, so no timeout fires early.
_SLOW_CLOCK = '''\
import os, subprocess, time
_late = [0.0]
for _name in ("monotonic", "perf_counter", "time"):
    setattr(time, _name, lambda _real=getattr(time, _name): _real() + _late[0])
def _slowed(call):
    def slowed(*args, **kwargs):
        try:
            return call(*args, **kwargs)
        finally:
            _late[0] += 86400.0
    return slowed
subprocess.Popen.__init__ = _slowed(subprocess.Popen.__init__)
os.killpg = _slowed(os.killpg)
'''

#: The tests BG0963 found comparing a close's printed output, which carries the seconds the
#: close's own pre-flight gate measured: (module, class, test, the module's normaliser or None).
_COMPARED_CLOSES = (
    ("test_lean_lane_yield", "LaneYieldTests",
     "test_a_lane_that_caught_nothing_in_three_runs_is_listed_not_enforced", "_unmeasured"),
    ("test_lean_mutation_ledger_retired", "MutationLedgerRetiredTests",
     "test_brief_and_close_read_no_ledger", "_unmeasured"),
    ("test_sprint", "InertVerifierRepairTests", "test_a_close_emits_its_cost_line", None),
)

#: Runs one of `_COMPARED_CLOSES` with the k-th gate run its closes record carrying `k * step`
#: seconds more than it measured, its normaliser made the identity when `mode` says so,
#: and prints the cost lines the close produced and whether the normaliser is narrow: blind to
#: the seconds, not to the run count beside them.
_VARIED_CLOSE = '''\
import contextlib, importlib.util, io, json, sys, unittest
from pathlib import Path
from unittest import mock
tests, name, cls, test, normaliser, mode, step = sys.argv[1:]
sys.path[:0] = [tests, str(Path(tests).parent)]
spec = importlib.util.spec_from_file_location(name, Path(tests) / f"{name}.py")
mod = sys.modules[name] = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
import loader
sprint = loader.load_script("sprint")
narrow = None
if normaliser != "-":
    unmeasured = getattr(mod, normaliser)
    shape = "close cost: {}s of gate over {} run(s)"
    narrow = (unmeasured(shape.format(0, 1)) == unmeasured(shape.format(399, 1))
              and unmeasured(shape.format(7, 1)) != unmeasured(shape.format(7, 2)))
record, line, lines, calls = sprint.record_execution_run, sprint.close_cost_line, [], [0]
def varied(root, **kw):
    calls[0] += 1
    if kw.get("seconds") is not None:
        kw["seconds"] += float(step) * calls[0]
    return record(root, **kw)
def seen(cost):
    lines.append(line(cost))
    return lines[-1]
with contextlib.ExitStack() as stack:
    stack.enter_context(mock.patch.object(sprint, "record_execution_run", varied))
    stack.enter_context(mock.patch.object(sprint, "close_cost_line", seen))
    if hasattr(mod, "_load"):
        stack.enter_context(mock.patch.object(mod, "_load", lambda: sprint))
    if mode == "identity":
        stack.enter_context(mock.patch.object(mod, normaliser, lambda text: text))
    result = unittest.TextTestRunner(stream=io.StringIO()).run(getattr(mod, cls)(test))
print(json.dumps({"ok": result.wasSuccessful(), "lines": lines, "narrow": narrow,
                  "problems": [p[1][-400:] for p in result.failures + result.errors]}))
'''


class WallClockCensusTests(unittest.TestCase):
    """BG0963. A test that bounds a measured duration by a constant, run beside every other
    module, fails when the machine is busy and passes alone: it measured the load. Commits and
    pushes here were refused on that alone, and a gate that refuses on load trains its users to
    bypass it.

    The census reads both suite directories by AST: a clock reading taken in the test's own
    process (`time.monotonic`, `perf_counter`, `time` and their `_ns` forms, through `import
    time [as x]` or `from time import`), bounded from above by a value that is not one. A lower
    bound is left alone: load can only lengthen a duration. It does not see a duration that
    reaches the test as data - a row's `elapsed_s`, a printed `398s` - so it cannot refuse one;
    the printed seconds BG0963 found are pinned below by name."""

    def _plant(self, body: str) -> list[str]:
        return _module_bounds("import time\nimport unittest\nimport pytest\n\n" + body, "m.py")

    def test_no_parallel_test_bounds_a_measured_duration_by_a_constant(self) -> None:
        """AC1. Read with the markers' exemption off, the census must name every bound listed
        below, or a census that reads nothing would pass. MUTANTS: remove `serial_only` or
        `boundary_only` from any test in `_SERIAL_BOUNDS` or `_SERIAL_IN_PROCESS`; empty
        `_WALL_CLOCK_DIRS`; glob a name no module has; make `_IMPORTS_TIME` pass no module."""
        sites = wall_clock_sites(REPO)
        reach = {site.rsplit(":", 1)[0] for site, _ in sites}
        self.assertIn(_SERIAL_BOUNDS[0], reach,
                      "the census does not name the `status` headline bound even with the "
                      "markers' exemption off, so it read no module")
        self.assertEqual([], [n for n in (*_SERIAL_BOUNDS, *_SERIAL_IN_PROCESS) if n not in reach],
                         "the census no longer reaches these bounds, so it cannot see one lose "
                         "its markers")
        found = [site for site, marked in sites if not marked]
        self.assertEqual([], found,
                         "a commit runs these tests, which bound a duration their own process "
                         "measured, so they fail on a busy machine and pass alone; mark each "
                         "`@pytest.mark.serial_only` and `@pytest.mark.boundary_only`, or take "
                         "the clock out of the assertion:\n"
                         + "\n".join(found))

    def test_the_census_names_a_planted_bound_and_passes_its_near_misses(self) -> None:
        """AC1's control. MUTANTS: read only `assertLess`; skip the tuple-returning helper;
        exempt nothing for the markers; exempt `serial_only` alone; flag a deadline polled
        against the clock; flag a lower bound; read `assertFalse` as `assertTrue`."""
        bound = ("    def test_fast(self):\n        t0 = time.monotonic()\n"
                 "        elapsed = time.monotonic() - t0\n        self.assertLess(elapsed, 3.0)\n")
        cases = {
            "assertLess": ("class T(unittest.TestCase):\n" + bound, ["m.py::T::test_fast:9"]),
            "assert": ("def test_f():\n    t0 = time.perf_counter()\n"
                       "    assert time.perf_counter() - t0 <= 2\n", ["m.py::test_f:7"]),
            "assertTrue": ("class T(unittest.TestCase):\n    def test_t(self):\n"
                           "        s = [time.time()]\n        self.assertTrue(1.5 > s[0])\n",
                           ["m.py::T::test_t:8"]),
            "assertFalse": ("class T(unittest.TestCase):\n    def test_f(self):\n"
                            "        t0 = time.time()\n"
                            "        self.assertFalse(time.time() - t0 > 2)\n",
                            ["m.py::T::test_f:8"]),
            "a lower bound": ("class T(unittest.TestCase):\n    def test_w(self):\n"
                              "        t0 = time.monotonic()\n"
                              "        waited = time.monotonic() - t0\n"
                              "        self.assertGreaterEqual(waited, 0.3)\n"
                              "        assert 0.3 <= waited\n"
                              "        self.assertFalse(waited < 0.3)\n", []),
            "a helper's tuple": (
                "class T(unittest.TestCase):\n    def _run(self):\n        t0 = time.monotonic()\n"
                "        return 0, 'out', time.monotonic() - t0\n    def test_r(self):\n"
                "        rc, out, secs = self._run()\n        self.assertEqual(0, rc)\n"
                "        self.assertLess(len(out), 9)\n        self.assertLess(secs, 4)\n",
                ["m.py::T::test_r:13"]),
            "a class attribute": (
                "class T(unittest.TestCase):\n    @classmethod\n    def setUpClass(cls):\n"
                "        cls.started = time.monotonic()\n    def test_c(self):\n"
                "        self.assertLessEqual(time.monotonic() - self.started, 9)\n",
                ["m.py::T::test_c:10"]),
            "serial_only alone": ("class T(unittest.TestCase):\n    @pytest.mark.serial_only\n"
                                  + bound, ["m.py::T::test_fast:10"]),
            "boundary_only alone": ("class T(unittest.TestCase):\n"
                                    "    @pytest.mark.boundary_only\n" + bound,
                                    ["m.py::T::test_fast:10"]),
            "the method marked": ("class T(unittest.TestCase):\n    @pytest.mark.serial_only\n"
                                  "    @pytest.mark.boundary_only\n" + bound, []),
            "the class marked": ("@pytest.mark.serial_only\n@pytest.mark.boundary_only\n"
                                 "class T(unittest.TestCase):\n" + bound, []),
            "split across levels": ("@pytest.mark.serial_only\nclass T(unittest.TestCase):\n"
                                    "    @pytest.mark.boundary_only\n" + bound, []),
            "an alias marked": ("try:\n    serial = pytest.mark.serial_only\n"
                                "    boundary = pytest.mark.boundary_only\nexcept ImportError:\n"
                                "    serial = boundary = lambda f: f\n\n"
                                "class T(unittest.TestCase):\n    @serial\n    @boundary\n"
                                + bound, []),
            "the module marked": ("pytestmark = [pytest.mark.serial_only,\n"
                                  "              pytest.mark.boundary_only]\n\n"
                                  "class T(unittest.TestCase):\n" + bound, []),
            "a deadline": ("class T(unittest.TestCase):\n    def test_d(self):\n"
                           "        deadline = time.monotonic() + 20\n"
                           "        self.assertLess(time.monotonic(), deadline)\n", []),
            "an equality": ("class T(unittest.TestCase):\n    def test_e(self):\n"
                            "        self.assertEqual(time.time() - time.time(), 0)\n", []),
        }
        for label, (body, expected) in cases.items():
            with self.subTest(case=label):
                self.assertEqual(expected, self._plant(body))
        self.assertEqual([], _module_bounds("import unittest\n\nclass T(unittest.TestCase):\n"
                                            + bound, "m.py"), "no clock is imported")
        for spelt in ("import time", "import time as t", "    import subprocess, time  # x",
                      "from time import monotonic"):
            with self.subTest(prefilter=spelt):
                self.assertTrue(_IMPORTS_TIME.search(f"import os\n{spelt}\n"),
                                "the pre-filter skips a module the census can read")

    def test_compared_output_is_insensitive_to_measured_seconds(self) -> None:
        """AC2. Each comparison runs with the k-th gate run its closes record 7k s longer than
        it measured, so two closes print different seconds; it must still pass. The control:
        with the module's normaliser made the identity, the same run fails. MUTANTS: drop
        `_unmeasured` from either module's comparison; widen its pattern past the seconds;
        assert `398s` again in `test_sprint`."""
        tests = REPO / SKILL_TESTS
        with tempfile.TemporaryDirectory() as d:
            driver = Path(d) / "varied_close.py"
            driver.write_text(_VARIED_CLOSE, encoding="utf-8")

            def run(name, cls, test, normaliser, mode="varied"):
                proc = subprocess.run([sys.executable, "-B", str(driver), str(tests), name, cls,
                                       test, normaliser or "-", mode, "7"], capture_output=True,
                                      text=True, timeout=600, cwd=REPO)
                self.assertEqual(0, proc.returncode, proc.stderr[-2000:])
                return json.loads(proc.stdout.splitlines()[-1])

            for name, cls, test, normaliser in _COMPARED_CLOSES:
                with self.subTest(test=f"{name}::{test}"):
                    got = run(name, cls, test, normaliser)
                    self.assertTrue(got["ok"], got["problems"])
                    seconds = [int(m.group(1)) for line in got["lines"]
                               for m in [re.search(r"(\d+)s of gate over", line)] if m]
                    self.assertEqual(len(got["lines"]), len(seconds), got["lines"])
                    if normaliser is None:
                        self.assertGreaterEqual(min(seconds), 398 + 7, got["lines"])
                        continue
                    self.assertEqual(len(seconds), len(set(seconds)),
                                     f"the closes printed the same seconds, so nothing varied: "
                                     f"{got['lines']}")
                    self.assertTrue(got["narrow"], f"{normaliser} hides more than the seconds")
                    self.assertFalse(run(name, cls, test, normaliser, "identity")["ok"],
                                     "unnormalised, the comparison still passed, so the varied "
                                     "seconds never reached the output it compares")

    @boundary
    def test_the_timing_assertions_still_run_at_the_boundary(self) -> None:
        """AC3. Each bound is collected under `serial_only and boundary_only`, so it runs at
        push, in the serial phase, and a commit's pytest run leaves it out (the commit hook's
        unittest fallback does not: BG1144); each in `_SERIAL_BOUNDS` fails on its own
        assertion when the code under test is slowed (`_SLOW_CLOCK`). The release verifier
        is collected `boundary_only` outside the serial phase and fails when its ceiling is a
        second. A lower bound, `test_a_timed_out_writer_writes_nothing`, stays in the parallel
        partition. MUTANTS: delete or skip a bound; take its `serial_only` or `boundary_only`
        off; turn its `assertLess` into a comparison that cannot fail; mark the lower bound or
        the release verifier serial."""
        env = {**os.environ, "SDLC_STUDIO_BOUNDARY_SUITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
        pytest = [sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q"]
        unmarked = (f"{SKILL_TESTS}/test_status.py::GatherPerformanceTests::"
                    "test_the_headline_is_in_the_buffer_and_flushed_before_gather_is_entered")
        nodes = [*_SERIAL_BOUNDS, *_SERIAL_IN_PROCESS]
        lower = (f"{SKILL_TESTS}/test_lean_lock_fails_closed.py::LockFailsClosedTests::"
                 "test_a_timed_out_writer_writes_nothing")

        def collect(markers):
            got = subprocess.run([*pytest, "--collect-only", "-m", markers, *nodes, unmarked,
                                  lower, _BOUNDARY_CEILING], capture_output=True, text=True,
                                 timeout=300, cwd=REPO, env=env)
            return set(got.stdout.split()), got.stdout[-2000:]

        collected, said = collect("serial_only and boundary_only")
        self.assertEqual([], [n for n in nodes if n not in collected],
                         f"not in the serial phase of the push alone:\n{said}")
        for other in (unmarked, lower, _BOUNDARY_CEILING):
            self.assertNotIn(other, collected, f"{other} was moved out of the parallel pass")
        collected, said = collect("boundary_only and not serial_only")
        self.assertIn(_BOUNDARY_CEILING, collected, f"the release verifier left the push:\n{said}")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "bg0963_slow_clock.py").write_text(_SLOW_CLOCK, encoding="utf-8")
            report = Path(d) / "slow.xml"
            subprocess.run([*pytest, "-p", "bg0963_slow_clock", f"--junitxml={report}",
                            *_SERIAL_BOUNDS], capture_output=True, text=True, timeout=600,
                           cwd=REPO, env={**env, "PYTHONPATH": d})
            failed: dict[str, list[str]] = {}
            for case in ElementTree.parse(report).iter("testcase"):
                for bad in [*case.iter("failure"), *case.iter("error")]:
                    failed.setdefault(case.get("name"), []).append(bad.get("message") or "")
            for node in _SERIAL_BOUNDS:
                name = node.rsplit("::", 1)[1]
                with self.subTest(bound=name):
                    self.assertTrue(failed.get(name), "a slowed run passed, so the bound is gone")
                    self.assertEqual([], [m for m in failed[name] if "not less than" not in m],
                                     "it failed on something other than its own bound")
        ceiling = subprocess.run([*pytest, _BOUNDARY_CEILING], capture_output=True, text=True,
                                 timeout=600, cwd=REPO, env={**env, "SDLC_VERIFY_TIMEOUT": "1"})
        self.assertNotEqual(0, ceiling.returncode, ceiling.stdout[-2000:])
        self.assertIn("red when the release gate runs it", ceiling.stdout)


if __name__ == "__main__":
    unittest.main()
