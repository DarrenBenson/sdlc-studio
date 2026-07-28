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

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
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

    def test_this_repos_test_files_are_mostly_attributed(self) -> None:
        """A convention that placed a handful of files would be a report of nothing."""
        files = [f for f in tc.test_files(self.REPO)
                 if "bench/fixtures" not in f.as_posix()]
        placed = [f for f in files if tc.attribute(self.REPO, f)[0]]
        self.assertGreater(len(files), 100)          # the suite this exists to measure
        self.assertGreater(len(placed) / len(files), 0.8)

    def test_the_census_attributes_its_own_tests_to_itself(self) -> None:
        """tools/ holds modules literally named test_*.py, so a prefix-based skip rule
        would make the suite's own guards permanently invisible to the census."""
        for test_file, module in (("tools/tests/test_test_census.py", "tools/test_census.py"),
                                  ("tools/tests/test_test_noise.py", "tools/test_noise.py")):
            with self.subTest(test_file):
                self.assertEqual(tc.attribute(self.REPO, test_file), (module, "name"))

    def test_an_unattributed_file_says_why_in_terms_of_the_convention(self) -> None:
        """The reason has to be actionable: which rule missed, and against what."""
        module, why = tc.attribute(self.REPO, "tools/tests/test_commit_msg_hook.py")
        self.assertIsNone(module)
        self.assertIn("test_commit_msg_hook.py", why)
        self.assertIn("name", why)


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


if __name__ == "__main__":
    unittest.main()
