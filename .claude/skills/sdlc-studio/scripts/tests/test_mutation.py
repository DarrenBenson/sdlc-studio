"""Unit tests for mutation.py - the executable mutation-check gate (RED first).

Fixtures are pure-stdlib unittest targets so the bridge's subprocess runs need
nothing beyond python3. Test titles are pinned by TS0002's AC Coverage Matrix.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared gitutil helper
import gitutil  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "mutation.py"


def _load():
    spec = importlib.util.spec_from_file_location("mutation", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mutation"] = mod
    spec.loader.exec_module(mod)
    return mod


TARGET = '''def classify(x):
    if x > 0:
        label = "positive"
    else:
        label = "other"
    return label
'''

GOOD_TEST = '''import unittest
import target

class T(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(target.classify(1), "positive")
        self.assertEqual(target.classify(-1), "other")


'''

VACUOUS_TEST = '''import unittest
import target

class T(unittest.TestCase):
    def test_classify_runs(self):
        target.classify(1)  # exercises, pins nothing


'''

RED_TEST = '''import unittest
import target

class T(unittest.TestCase):
    def test_fails(self):
        self.assertEqual(1, 2)  # a red baseline over unmutated code


'''


def _fixture(d: Path) -> Path:
    (d / "target.py").write_text(TARGET, encoding="utf-8")
    (d / "test_good.py").write_text(GOOD_TEST, encoding="utf-8")
    (d / "test_vacuous.py").write_text(VACUOUS_TEST, encoding="utf-8")
    (d / "sdlc-studio").mkdir(exist_ok=True)
    return d


class EngineTests(unittest.TestCase):
    def test_enumeration_is_deterministic(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            a, ua = mut.enumerate_mutations([root / "target.py"])
            b, ub = mut.enumerate_mutations([root / "target.py"])
            self.assertEqual(a, b)
            self.assertEqual(ua, ub)
            self.assertTrue(a)
            lines = [m["line"] for m in a if m["class"] == "unset-delivered-field"]
            self.assertEqual(lines, sorted(lines))  # line-ordered

    def test_each_class_mutates_python(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            muts, _ = mut.enumerate_mutations([root / "target.py"])
            classes = {m["class"] for m in muts}
            self.assertEqual(classes, set(mut.FAULT_CLASSES))
            original = (root / "target.py").read_text(encoding="utf-8")
            for m in muts:
                mutated = mut.mutated_text(m)
                self.assertNotEqual(mutated, original, m)  # one visible change
                if m["class"] == "invert-guard":
                    self.assertIn("if not (x > 0):", mutated)
                if m["class"] == "stub-return-null":
                    self.assertIn("return None", mutated)

    def test_restore_is_byte_identical(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            original = (root / "target.py").read_bytes()
            muts, _ = mut.enumerate_mutations([root / "target.py"])
            # even when the runner raises, the finally must restore
            with self.assertRaises(RuntimeError):
                with mut.applied(muts[0]):
                    raise RuntimeError("runner blew up")
            self.assertEqual((root / "target.py").read_bytes(), original)

    def test_uncovered_language_unchecked(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "main.rs").write_text("fn main() {}\n", encoding="utf-8")
            muts, unchecked = mut.enumerate_mutations([root / "main.rs"])
            self.assertEqual(muts, [])
            self.assertTrue(unchecked)
            self.assertTrue(all(u["reason"] for u in unchecked))


class BridgeTests(unittest.TestCase):
    def _run(self, root: Path, test_cmd: str, **kw):
        mut = _load()
        return mut.run_gate(root, [root / "target.py"], test_cmd, **kw)

    def test_vacuous_survives_loadbearing_kills(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            good = self._run(root, f"{sys.executable} -m unittest test_good")
            self.assertEqual(good["summary"]["survived"], 0, good)
            self.assertGreater(good["summary"]["killed"], 0)
            bad = self._run(root, f"{sys.executable} -m unittest test_vacuous")
            self.assertEqual(bad["summary"]["killed"], 0, bad)
            self.assertGreater(bad["summary"]["survived"], 0)

    def test_report_shape_and_counts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = self._run(root, f"{sys.executable} -m unittest test_good")
            report_path = root / "sdlc-studio" / ".local" / "mutation-report.json"
            self.assertTrue(report_path.exists())
            on_disk = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(on_disk["summary"], r["summary"])
            verdicts = [m["verdict"] for m in on_disk["mutations"]]
            s = on_disk["summary"]
            self.assertEqual(verdicts.count("killed"), s["killed"])
            self.assertEqual(verdicts.count("survived"), s["survived"])
            self.assertEqual(verdicts.count("error"), s["errors"])
            self.assertEqual(s["applied"], len(verdicts))
            self.assertIn("unchecked", on_disk)

    def test_survivor_exits_nonzero(self) -> None:
        import contextlib
        import io
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["run", "--files", str(root / "target.py"),
                               "--test", f"{sys.executable} -m unittest test_vacuous",
                               "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("SURVIVED", buf.getvalue())

    def test_broken_runner_baseline_refuses_never_a_kill(self) -> None:
        # BG0180: a baseline that ERRORS (the runner itself broke) proves nothing, so the gate
        # refuses - no mutant applied, no fake kill - rather than recording per-mutation errors.
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = self._run(root, "definitely-not-a-command-xyz")
            self.assertTrue(r["refused"], r)
            self.assertEqual(r["baseline"], "error")
            self.assertEqual(r["summary"]["killed"], 0, r)
            self.assertEqual(r["mutations"], [])       # nothing applied
            self.assertTrue(r["remedy"])               # remedy named

    def test_red_baseline_refuses_applies_no_mutant_and_exits_nonzero(self) -> None:
        # BG0180: a red baseline (a failing suite over unmutated code) must refuse immediately -
        # exit non-zero, apply no mutant, name the remedy - never run all mutants and exit 0.
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "test_red.py").write_text(RED_TEST, encoding="utf-8")
            original = (root / "target.py").read_bytes()
            r = self._run(root, f"{sys.executable} -m unittest test_red")
            self.assertTrue(r["refused"], r)
            self.assertEqual(r["baseline"], "fail")
            self.assertEqual(r["mutations"], [])
            self.assertEqual(r["summary"]["applied"], 0)
            self.assertTrue(r["remedy"])
            self.assertEqual((root / "target.py").read_bytes(), original)  # tree untouched
            import contextlib
            import io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = mut.main(["run", "--files", str(root / "target.py"),
                               "--test", f"{sys.executable} -m unittest test_red",
                               "--root", str(root)])
            self.assertNotEqual(rc, 0)                  # never a clean-looking zero
            self.assertIn("REFUSED", err.getvalue())


class EmptySurfaceIsFirstClassTests(unittest.TestCase):
    """US0379 / CR0376: a surface with no mutatable sites is a FIRST-CLASS outcome - not a refusal
    (a red baseline) and not a pass (mutants killed). An absence and a negative result are
    different facts, so the run records 'nothing to mutate' and the gate lane reads it distinct
    from not-run and from PASS, letting a docs-only close be green with the reason on the record."""

    def _gate(self):
        import importlib.util as il
        SCR = Path(__file__).resolve().parent.parent
        spec = il.spec_from_file_location("gate", SCR / "gate.py")
        mod = il.module_from_spec(spec)
        sys.modules["gate"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_run_over_a_no_site_surface_records_the_empty_surface(self) -> None:
        """AC1: exit 0 with a distinct recorded status, never a silent pass and never the
        red-baseline refusal. The test command must not even run - there is nothing to judge."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            # a docstring/import-only module has no mutatable site
            (root / "nosites.py").write_text('"""docs only."""\nimport os\n', encoding="utf-8")
            # 'false' would make a baseline red IF it were run - proving the baseline is skipped
            r = mut.run_gate(root, [root / "nosites.py"], "false")
            self.assertTrue(r["empty_surface"])
            self.assertFalse(r["refused"])            # NOT the red-baseline refusal
            self.assertEqual(r["baseline"], "not-run")  # the command was never run
            self.assertEqual(r["summary"]["applied"], 0)
            self.assertEqual(r["summary"]["enumerated"], 0)
            # the series names its own outcome, apart from measured and no-evidence
            self.assertEqual(r["series"]["row"]["outcome"], "nothing-to-mutate")
            self.assertFalse(r["series"]["row"]["evidence"])

    def test_a_no_site_surface_is_not_a_red_baseline_refusal(self) -> None:
        # the two must be distinguishable in the record: an empty surface proved nothing because
        # there was nothing to prove; a refusal proved nothing because the baseline was red
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "nosites.py").write_text("import os\n", encoding="utf-8")
            empty = mut.run_gate(root, [root / "nosites.py"], f"{sys.executable} -m unittest test_good")
            red = mut.run_gate(root, [root / "target.py"], "definitely-not-a-command-xyz")
            self.assertTrue(empty["empty_surface"])
            self.assertFalse(empty["refused"])
            self.assertFalse(red.get("empty_surface"))
            self.assertTrue(red["refused"])

    def test_the_cli_records_an_empty_surface_and_exits_zero(self) -> None:
        # a chosen surface that resolves to no mutatable file (a docs-only close) exits 0 with a
        # written report, never a silent non-pass with no record
        import contextlib
        import io
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "nosites.py").write_text('"""docs."""\n', encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["run", "--files", str(root / "nosites.py"),
                               "--test", "false", "--root", str(root)])
            self.assertEqual(rc, 0)                       # green, not the refusal's non-zero
            self.assertIn("nothing to mutate", buf.getvalue())
            report = json.loads((root / "sdlc-studio" / ".local" / "mutation-report.json")
                                .read_text(encoding="utf-8"))
            self.assertTrue(report["empty_surface"])      # a record exists

    def test_the_gate_lane_reads_empty_surface_distinct_from_not_run_and_pass(self) -> None:
        """AC2: 'nothing to mutate' is distinct from not-run (no report) and from a PASS."""
        gate = self._gate()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rp = root / "sdlc-studio" / ".local" / "mutation-report.json"
            rp.parent.mkdir(parents=True)

            # not-run: no report at all
            not_run = gate._mutation(str(root))
            self.assertIn("not run", not_run["detail"])
            self.assertEqual(not_run["count"], 1)

            # empty surface: green, count 0, its own words
            rp.write_text(json.dumps({"empty_surface": True, "refused": False, "summary": {},
                                      "targets": [], "git_rev": None}), encoding="utf-8")
            empty = gate._mutation(str(root))
            self.assertEqual(empty["count"], 0)
            self.assertFalse(empty["blocking"])
            self.assertIn("nothing to mutate", empty["detail"])
            self.assertNotIn("not run", empty["detail"])

            # a genuine PASS reads differently again (mutants killed)
            rp.write_text(json.dumps({"empty_surface": False, "refused": False,
                                      "summary": {"applied": 3, "killed": 3, "survived": 0,
                                                  "errors": 0, "enumerated": 3},
                                      "targets": [], "git_rev": None}), encoding="utf-8")
            passed = gate._mutation(str(root))
            self.assertIn("killed", passed["detail"])
            self.assertNotIn("nothing to mutate", passed["detail"])


class SuggestCoveringCommandTests(unittest.TestCase):
    """US0380 / CR0377: the run proposes a per-target covering command from its OWN reference
    scan, so a run executed with the derived command produces zero out-of-selection warnings BY
    CONSTRUCTION - the command lists exactly the files the warning scan looks for. The heuristic
    caveat rides on the result, and the hand-supplied --test path is unchanged and the default."""

    def _fix(self, d) -> Path:
        root = Path(d)
        (root / "sdlc-studio").mkdir()
        (root / "target.py").write_text("def f(x):\n    return x > 0\n", encoding="utf-8")
        (root / "test_a.py").write_text("import target\nassert target.f(1)\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests" / "test_b.py").write_text("from target import f\n", encoding="utf-8")
        (root / "test_unrelated.py").write_text("x = 1\n", encoding="utf-8")
        return root

    def test_suggests_the_referencing_tests_with_the_heuristic_caveat(self) -> None:
        """AC1: the derived covering command per target is the referencing test files the scan
        found, and the honest caveat that reference-scan coverage is a heuristic rides along."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._fix(d)
            sugg = mut.suggest_test_command(root, [root / "target.py"])
            info = sugg["per_target"][str(root / "target.py")]
            self.assertEqual(info["referencing_tests"], ["test_a.py", "tests/test_b.py"])
            self.assertIn("test_a.py", info["command"])
            self.assertIn("tests/test_b.py", info["command"])
            self.assertNotIn("test_unrelated.py", info["command"])  # a non-referencing test
            self.assertIn("heuristic", sugg["caveat"])

    def test_a_run_with_the_derived_command_has_zero_out_of_selection_warnings(self) -> None:
        """AC2: by construction - the derived command covers every referencing test, so the
        manufactured-survivor warning cannot fire for the targets; a narrow command still does."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._fix(d)
            derived = mut.suggest_test_command(root, [root / "target.py"])["covering_command"]
            # selection_warnings is computed even on a refused run, so this holds whether or not
            # `pytest` is installed - it is a property of the SELECTION, not of the test outcome
            r = mut.run_gate(root, [root / "target.py"], derived)
            self.assertEqual(r["selection_warnings"], [], r["selection_warnings"])
            # the control: a command selecting only one referencing test warns on the other
            narrow = mut.run_gate(root, [root / "target.py"], "pytest test_a.py")
            names = sorted(Path(w["test_file"]).name for w in narrow["selection_warnings"])
            self.assertEqual(names, ["test_b.py"])

    def test_an_uncovered_target_is_named_not_faked(self) -> None:
        # a target no test references yields a null command and is flagged uncovered - an honest
        # gap, never a fabricated covering command
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "orphan.py").write_text("def g():\n    return 1 > 0\n", encoding="utf-8")
            sugg = mut.suggest_test_command(root, [root / "orphan.py"])
            info = sugg["per_target"][str(root / "orphan.py")]
            self.assertIsNone(info["command"])
            self.assertTrue(info["uncovered"])
            self.assertIsNone(sugg["covering_command"])

    def test_the_cli_suggest_flag_prints_and_exits_zero_without_mutating(self) -> None:
        import contextlib
        import io
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._fix(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["run", "--files", str(root / "target.py"),
                               "--suggest-test", "--root", str(root)])
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("test_a.py", out)
            self.assertIn("heuristic", out)
            # mutating nothing: no report was written
            self.assertFalse((root / "sdlc-studio" / ".local" / "mutation-report.json").exists())

    def test_omitting_test_without_suggest_is_a_usage_error(self) -> None:
        import contextlib
        import io
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._fix(d)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = mut.main(["run", "--files", str(root / "target.py"), "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIn("--test is required", err.getvalue())

    def test_the_hand_supplied_test_path_is_unchanged_and_default(self) -> None:
        """AC3: --test alone runs the mutation gate exactly as before, mutating and reporting."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            self.assertFalse(r.get("empty_surface"))
            self.assertGreater(r["summary"]["applied"], 0)      # mutants WERE applied
            self.assertGreater(r["summary"]["killed"], 0)
            # and the CLI --test path writes a report as ever
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                rc = mut.main(["run", "--files", str(root / "target.py"),
                               "--test", f"{sys.executable} -m unittest test_good",
                               "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertTrue((root / "sdlc-studio" / ".local" / "mutation-report.json").exists())


class LaneTests(unittest.TestCase):
    def test_files_and_since_select_surface(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "other.py").write_text("def noop():\n    return 1\n", encoding="utf-8")
            explicit = mut.select_files(root, files=[str(root / "target.py")])
            self.assertEqual([p.name for p in explicit], ["target.py"])
            gitutil.git(["init", "-q"], root)
            gitutil.git(["add", "-A"], root)
            gitutil.git(["commit", "-qm", "base"], root)
            (root / "target.py").write_text(TARGET + "\n# touched\n", encoding="utf-8")
            since = mut.select_files(root, since="HEAD")
            self.assertEqual([p.name for p in since], ["target.py"])

    def test_ceiling_truncates_loudly(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good",
                             max_mutations=2)
            self.assertEqual(r["summary"]["applied"], 2)
            self.assertGreater(r["summary"]["truncated"], 0)

    def test_truncated_run_states_sampled_fraction(self) -> None:
        # a green sample must never read as whole-surface assurance: when the
        # budget trims, summary carries `enumerated` and the CLI prints the
        # sampled/enumerated fraction with a percentage
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good",
                             max_mutations=2)
            s = r["summary"]
            self.assertIn("enumerated", s)
            self.assertEqual(s["enumerated"], s["applied"] + s["truncated"])
            self.assertGreater(s["enumerated"], s["applied"])
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mut.main(["run", "--files", str(root / "target.py"),
                          "--test", f"{sys.executable} -m unittest test_good",
                          "--max-mutations", "2", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn(f"sampled 2/{s['enumerated']} enumerated", out)
            self.assertIn("%", out)

    def test_untruncated_run_reads_as_today(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            s = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")["summary"]
            self.assertEqual(s["truncated"], 0)
            self.assertEqual(s["enumerated"], s["applied"])
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mut.main(["run", "--files", str(root / "target.py"),
                          "--test", f"{sys.executable} -m unittest test_good",
                          "--root", str(root)])
            self.assertNotIn("sampled", buf.getvalue())

    def test_prefilter_flags_assertion_free(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            flagged = mut.prefilter([root / "test_good.py", root / "test_vacuous.py"])
            self.assertEqual([p.name for p in flagged], ["test_vacuous.py"])


class ViabilityTests(unittest.TestCase):
    """A mutant that does not even parse is UNVIABLE - it is evidence of nothing,
    and must never be counted as killed (a vacuous suite would 'kill' it too)."""

    def test_unviable_python_mutant_not_killed(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            # multi-line dict: unset-delivered-field yields `out = None` ... `}` -> SyntaxError
            (root / "target.py").write_text(
                "def make():\n    out = {\n        'a': 1,\n    }\n    return out\n",
                encoding="utf-8")
            (root / "test_vac.py").write_text(VACUOUS_TEST.replace("target", "target")
                                              .replace("classify(1)", "make()"),
                                              encoding="utf-8")
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_vac")
            s = r["summary"]
            self.assertGreater(s["unviable"], 0, r)
            for rec in r["mutations"]:
                if rec["verdict"] == "killed":
                    # any true kill must come from a viable mutant; the broken-dict
                    # mutation specifically must be unviable
                    self.assertNotEqual((rec["class"], rec["line"]),
                                        ("unset-delivered-field", 2), rec)
            self.assertEqual(s["applied"], len(r["mutations"]))

    def test_summary_partitions_by_verdict(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            s = r["summary"]
            self.assertEqual(s["applied"],
                             s["killed"] + s["survived"] + s["errors"] + s["unviable"])


class ProfileShapeTests(unittest.TestCase):
    """JS/Go profiles only enumerate forms whose mutants stay syntactically valid."""

    def test_js_block_if_mutates_single_statement_if_skipped(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / "app.js"
            p.write_text("function f(x) {\n"
                         "  if (x > 0) {\n    return g(x);\n  }\n"
                         "  if (x < 0) return h(x);\n"
                         "  let y = x + 1;\n"
                         "  return y;\n}\n", encoding="utf-8")
            muts, _ = mut.enumerate_mutations([p], classes=("invert-guard",))
            lines = [m["line"] for m in muts]
            self.assertIn(2, lines)        # block form mutated
            self.assertNotIn(5, lines)     # single-statement form not enumerated
            m2 = next(m for m in muts if m["line"] == 2)
            self.assertIn("if (!(x > 0)) {", mut.mutated_text(m2))

    def test_go_if_with_init_skipped(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / "main.go"
            p.write_text("func f(m map[string]int, k string) int {\n"
                         "\tif v, ok := m[k]; ok {\n\t\treturn v\n\t}\n"
                         "\tif len(k) > 0 {\n\t\treturn 1\n\t}\n"
                         "\treturn 0\n}\n", encoding="utf-8")
            muts, _ = mut.enumerate_mutations([p], classes=("invert-guard",))
            lines = [m["line"] for m in muts]
            self.assertNotIn(2, lines)     # if-with-init not enumerated (mutant invalid)
            self.assertIn(5, lines)        # plain condition mutated
            m5 = next(m for m in muts if m["line"] == 5)
            self.assertIn("if !(len(k) > 0) {", mut.mutated_text(m5))


class StoryLaneTests(unittest.TestCase):
    def test_story_surface_resolves_cr_affects(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "loader.py").write_text("x = 1\n", encoding="utf-8")
            sd = root / "sdlc-studio"
            for sub in ("stories", "epics", "change-requests"):
                (sd / sub).mkdir(parents=True)
            (sd / "stories" / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** EP0001\n", encoding="utf-8")
            (sd / "epics" / "EP0001-e.md").write_text(
                "# EP0001: e\n\n> **Status:** In Progress\n> **CR:** CR-0001\n", encoding="utf-8")
            (sd / "change-requests" / "CR0001-c.md").write_text(
                "# CR-0001: c\n\n> **Status:** Approved\n> **Affects:** src/loader.py\n",
                encoding="utf-8")
            files = mut.select_files(root, story="US0001")
            self.assertEqual([p.name for p in files], ["loader.py"])

    def test_since_includes_untracked_files(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            gitutil.git(["init", "-q"], root)
            gitutil.git(["add", "target.py"], root)
            gitutil.git(["commit", "-qm", "base"], root)
            (root / "brand_new.py").write_text("def n():\n    return 2\n", encoding="utf-8")
            since = mut.select_files(root, since="HEAD")
            self.assertIn("brand_new.py", [p.name for p in since])


class StalenessHashTests(unittest.TestCase):
    """CR0146 (leads): the report records per-target content hashes so the gate
    can tell evidence about THIS code from evidence about code that no longer
    exists - rev-granularity alone passes on dirty trees."""

    def test_report_records_target_hashes(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            hashes = r.get("target_hashes")
            self.assertIsInstance(hashes, dict)
            key = str(root / "target.py")
            self.assertIn(key, hashes)
            import hashlib
            self.assertEqual(hashes[key],
                             hashlib.sha256((root / "target.py").read_bytes()).hexdigest())


class LedgerTests(unittest.TestCase):
    """BG0238: one report is last-write-wins, so a per-unit run mid-sprint erases the
    previous unit's evidence. Each run therefore ALSO appends a per-target entry - path,
    content hash at run time, rev, timestamp, and that target's own kill/survive counts -
    to a bounded ledger the gate can read as coverage."""

    def _ledger(self, root: Path) -> dict:
        return json.loads((root / "sdlc-studio" / ".local" / "mutation-runs.json")
                          .read_text(encoding="utf-8"))

    def test_a_run_appends_a_per_target_entry_with_its_content_hash(self) -> None:
        import hashlib
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            led = self._ledger(root)
            entries = led["entries"]
            self.assertEqual([e["target"] for e in entries], ["target.py"])
            self.assertEqual(led["dropped"], 0)        # nothing dropped, and it says so
            e = entries[0]
            self.assertEqual(e["hash"],
                             hashlib.sha256((root / "target.py").read_bytes()).hexdigest())
            self.assertTrue(e["generated_at"])
            self.assertIn("git_rev", e)
            self.assertGreater(e["summary"]["killed"], 0)
            self.assertEqual(e["summary"]["applied"],
                             sum(e["summary"][k] for k in
                                 ("killed", "survived", "errors", "unviable")))

    def test_an_earlier_target_survives_a_later_run_on_another_file(self) -> None:
        """The accumulation the bug is about: mutating file two must not erase file one."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "other.py").write_text(TARGET.replace("classify", "sort_of"),
                                           encoding="utf-8")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            mut.run_gate(root, [root / "other.py"],
                         f"{sys.executable} -m unittest test_good")
            self.assertEqual(sorted(e["target"] for e in self._ledger(root)["entries"]),
                             ["other.py", "target.py"])
            # ...and the latest report is still the single latest run, unchanged
            on_disk = json.loads((root / "sdlc-studio" / ".local" / "mutation-report.json")
                                 .read_text(encoding="utf-8"))
            self.assertEqual(on_disk["targets"], [str(root / "other.py")])

    def test_a_later_run_on_the_same_target_supersedes_its_entry(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            first = self._ledger(root)["entries"][0]["hash"]
            (root / "target.py").write_text(TARGET + "\ndef extra():\n    return 7\n",
                                            encoding="utf-8")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            entries = self._ledger(root)["entries"]
            self.assertEqual(len(entries), 1)          # superseded, not accumulated
            self.assertNotEqual(entries[0]["hash"], first)

    def test_a_refused_run_records_no_evidence(self) -> None:
        """A red baseline applies no mutant, so it proves nothing about any target and
        must not appear in the ledger as coverage."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "test_good.py").write_text(
                GOOD_TEST.replace('"positive"', '"WRONG"'), encoding="utf-8")
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            self.assertTrue(r["refused"])
            self.assertFalse((root / "sdlc-studio" / ".local" / "mutation-runs.json").exists())

    def test_a_target_the_suite_never_judged_is_not_recorded(self) -> None:
        """With a ceiling too small to reach the second file, that file carries no verdict -
        listing it would claim evidence the run did not gather."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "other.py").write_text(TARGET.replace("classify", "sort_of"),
                                           encoding="utf-8")
            r = mut.run_gate(root, [root / "target.py", root / "other.py"],
                             f"{sys.executable} -m unittest test_good", max_mutations=1)
            self.assertEqual(r["summary"]["applied"], 1)
            judged = {Path(m["file"]).name for m in r["mutations"]
                      if m["verdict"] in ("killed", "survived")}
            self.assertEqual(len(judged), 1, r["mutations"])   # only one file was reached
            recorded = {e["target"] for e in self._ledger(root)["entries"]}
            self.assertEqual(recorded, judged)

    def test_target_hashes_name_every_target_asked_for_not_every_one_proven(self) -> None:
        """The writer's half of the same rule, stated where the field is produced. The report's
        `target_hashes` records the surface the run was POINTED at, and is computed before any
        verdict exists, so it names a file the ceiling never reached and every target of a
        refused run. It is a freshness stamp, never evidence: the gate lane read it as coverage
        and reported 3/3 files covered on a run that mutated one, and 1/1 covered on a run that
        applied no mutant at all. Only the ledger applies the verdict rule."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "other.py").write_text(TARGET.replace("classify", "sort_of"),
                                           encoding="utf-8")
            r = mut.run_gate(root, [root / "target.py", root / "other.py"],
                             f"{sys.executable} -m unittest test_good", max_mutations=1)
            named = {Path(p).name for p in r["target_hashes"]}
            recorded = {Path(e["target"]).name for e in self._ledger(root)["entries"]}
            self.assertEqual(named, {"target.py", "other.py"})   # both were asked for
            self.assertEqual(len(recorded), 1)                   # one was proven
            self.assertTrue(recorded < named)

    def test_the_ledger_is_bounded_and_counts_what_it_dropped(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            stale = [{"target": f"old{i}.py", "hash": "0" * 64, "git_rev": None,
                      "generated_at": "2026-01-01T00:00:00Z",
                      "summary": {"applied": 1, "killed": 1, "survived": 0,
                                  "errors": 0, "unviable": 0}}
                     for i in range(mut.LEDGER_LIMIT + 5)]
            (local / "mutation-runs.json").write_text(
                json.dumps({"version": 1, "dropped": 0, "entries": stale}), encoding="utf-8")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            led = self._ledger(root)
            self.assertEqual(len(led["entries"]), mut.LEDGER_LIMIT)
            self.assertEqual(led["dropped"], 6)        # 5 over the bound, plus this run's
            self.assertEqual(led["entries"][-1]["target"], "target.py")   # newest kept
            self.assertNotIn("old0.py", [e["target"] for e in led["entries"]])  # oldest gone

    def test_a_run_that_drops_entries_says_so_where_a_human_reads_it(self) -> None:
        """Silent truncation reads as 'we kept everything', so the drop is printed too."""
        import contextlib
        import io
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            stale = [{"target": f"old{i}.py", "hash": "0" * 64, "git_rev": None,
                      "generated_at": "2026-01-01T00:00:00Z",
                      "summary": {"applied": 1, "killed": 1, "survived": 0,
                                  "errors": 0, "unviable": 0}}
                     for i in range(mut.LEDGER_LIMIT)]
            (local / "mutation-runs.json").write_text(
                json.dumps({"version": 1, "dropped": 0, "entries": stale}), encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mut.main(["run", "--files", str(root / "target.py"),
                          "--test", f"{sys.executable} -m unittest test_good",
                          "--root", str(root)])
            self.assertIn("ledger dropped its 1 oldest", buf.getvalue())

    def test_a_corrupt_ledger_is_replaced_rather_than_crashing_the_run(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "mutation-runs.json").write_text("{not json", encoding="utf-8")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            led = self._ledger(root)
            self.assertEqual([e["target"] for e in led["entries"]], ["target.py"])
            self.assertTrue(led["reset"])   # says it discarded an unreadable ledger

    def test_no_ledger_is_written_when_the_report_is_not(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good", write_report=False)
            self.assertFalse((root / "sdlc-studio" / ".local" / "mutation-runs.json").exists())


class RegisterTests(unittest.TestCase):
    """BG0245: the ledger could only be written by a mutation.py run, while the practice this
    project follows is a builder hand-applying a mutant to the code a new test pins, seeing RED,
    and restoring. That left no trace, so a sprint that applied 75 mutants closed with the lane
    reporting 0/4 covered - a lane that reads empty precisely when the policy WAS followed.

    `register` records an already-applied mutant so the practice becomes recordable without
    changing the practice to suit the tool. What it records is a CLAIM: nothing here proves the
    mutant was ever applied. Every entry therefore carries its provenance, so a reader can tell a
    self-report from a machine-measured run and weight the two differently.
    """

    def _ledger(self, root: Path) -> dict:
        return json.loads((root / "sdlc-studio" / ".local" / "mutation-runs.json")
                          .read_text(encoding="utf-8"))

    @staticmethod
    def _sha(path: Path) -> str:
        import hashlib
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _register(self, mut, root: Path, **kw):
        args = ["register", "--target", str(root / kw.pop("target", "target.py")),
                "--mutant", kw.pop("mutant", "classify: inverted the x > 0 guard"),
                "--test", kw.pop("test", "test_good.T.test_classify"),
                "--line", str(kw.pop("line", 2)),
                "--verdict", kw.pop("verdict", "killed"), "--root", str(root)]
        assert not kw, kw
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = mut.main(args)
        return rc, buf.getvalue()

    def test_a_registered_mutant_becomes_a_ledger_entry_marked_self_reported(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            rc, out = self._register(mut, root)
            self.assertEqual(rc, 0, out)
            entries = self._ledger(root)["entries"]
            self.assertEqual(len(entries), 1)
            e = entries[0]
            self.assertEqual(e["target"], "target.py")
            self.assertEqual(e["provenance"], mut.PROVENANCE_REGISTERED)
            self.assertEqual(e["hash"], self._sha(root / "target.py"))
            self.assertEqual(e["summary"]["killed"], 1)
            self.assertEqual(e["summary"]["applied"], 1)
            # WHAT was mutated, and WHICH test killed it - a bare count is unauditable
            self.assertEqual(e["mutants"][0]["mutant"], "classify: inverted the x > 0 guard")
            self.assertEqual(e["mutants"][0]["test"], "test_good.T.test_classify")
            self.assertEqual(e["mutants"][0]["verdict"], "killed")

    def test_the_command_says_the_entry_is_self_reported(self) -> None:
        """One line, at the moment of recording, so nobody logs a claim believing they measured
        something."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _, out = self._register(mut, root)
            self.assertIn("self-reported", out.lower())

    def test_several_mutants_on_the_same_content_accumulate(self) -> None:
        """A builder applies many mutants per file across a sprint. Overwriting per call would
        leave the ledger permanently reading 1, which is the same silence in a new place."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._register(mut, root, mutant="one")
            self._register(mut, root, mutant="two", verdict="survived")
            entries = self._ledger(root)["entries"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["summary"],
                             {"applied": 2, "killed": 1, "survived": 1,
                              "errors": 0, "unviable": 0, "equivalent": 0})
            self.assertEqual([m["mutant"] for m in entries[0]["mutants"]], ["one", "two"])

    def test_a_survivor_is_recordable_and_is_not_counted_as_a_kill(self) -> None:
        """A register subcommand that could only log good news would be a way to launder a
        sprint that found nothing."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._register(mut, root, verdict="survived")
            s = self._ledger(root)["entries"][0]["summary"]
            self.assertEqual((s["killed"], s["survived"]), (0, 1))

    def test_an_edit_to_the_target_starts_a_fresh_entry(self) -> None:
        """The old claim was about bytes that no longer exist. Keeping its counts would carry
        evidence forward across the very change it says nothing about."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._register(mut, root, mutant="before")
            (root / "target.py").write_text(TARGET + "\ndef extra():\n    return 7\n",
                                            encoding="utf-8")
            self._register(mut, root, mutant="after")
            entries = self._ledger(root)["entries"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["hash"], self._sha(root / "target.py"))
            self.assertEqual([m["mutant"] for m in entries[0]["mutants"]], ["after"])
            self.assertEqual(entries[0]["summary"]["applied"], 1)

    def test_a_registration_never_overwrites_a_measured_entry(self) -> None:
        """The claim must not displace the measurement. A run that really applied mutants to
        this file is the stronger evidence, and one `register` call must not be able to erase
        it - which a single entry per target would do."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            self._register(mut, root)
            entries = self._ledger(root)["entries"]
            by_prov = {e.get("provenance"): e for e in entries}
            self.assertEqual(sorted(by_prov), sorted([mut.PROVENANCE_MEASURED,
                                                      mut.PROVENANCE_REGISTERED]))
            self.assertGreater(by_prov[mut.PROVENANCE_MEASURED]["summary"]["killed"], 0)

    def test_a_measured_run_supersedes_only_its_own_kind(self) -> None:
        """The other direction. A re-run replaces the measured entry for that target, and leaves
        the registered one standing - it is a different claim about the same file, not a stale
        copy of the same one."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._register(mut, root, mutant="hand-applied")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            entries = self._ledger(root)["entries"]
            provs = sorted(e.get("provenance") for e in entries)
            self.assertEqual(provs, [mut.PROVENANCE_MEASURED, mut.PROVENANCE_REGISTERED])

    def test_a_run_stamps_its_own_entries_as_measured(self) -> None:
        """Provenance is only readable if BOTH kinds carry it. Marking one and leaving the other
        blank makes the distinction depend on a default nothing states."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")
            self.assertEqual(self._ledger(root)["entries"][0]["provenance"],
                             mut.PROVENANCE_MEASURED)

    def test_registering_a_target_that_does_not_exist_is_refused(self) -> None:
        """No file, no content hash - an entry keyed on nothing could never go stale, so it
        would read as coverage of the current code for ever.

        Asserted at the LIBRARY boundary as well as the CLI, because the two are not the same
        check: `cmd_register` also catches OSError, so a bare FileNotFoundError from the later
        `read_bytes` produces an identical exit code and leaves the refusal itself pinned by
        nothing - it survived exactly that mutant. The refusal is a stated contract (ValueError
        for every bad input, naming why) and it is tested as one.
        """
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            with self.assertRaises(ValueError) as caught:
                mut.register_mutant(root, root / "nope.py", "m", "t", "killed", line=1)
            self.assertIn("content hash", str(caught.exception))
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = mut.main(["register", "--target", str(root / "nope.py"),
                               "--mutant", "m", "--test", "t", "--verdict", "killed",
                               "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertFalse((root / "sdlc-studio" / ".local" / "mutation-runs.json").exists())

    def test_an_entry_naming_neither_the_mutant_nor_the_test_is_refused(self) -> None:
        """A self-report is only auditable if it says what was mutated and what judged it. A
        blank one is a number nobody can check against the diff, which is a claim of coverage
        with nothing behind it at all."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            for mutant, test in (("", "t"), ("m", ""), ("   ", "t")):
                with self.assertRaises(ValueError):
                    mut.register_mutant(root, root / "target.py", mutant, test, "killed", line=1)
            self.assertFalse((root / "sdlc-studio" / ".local" / "mutation-runs.json").exists())

    def test_a_verdict_the_runner_alone_can_observe_is_refused(self) -> None:
        """`error` and `unviable` are things a runner sees about a mutant it tried to execute.
        A builder reporting one would be reporting on a run that never happened here, and the
        library entry point has to refuse it, not just the flag parser."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            for bad in ("error", "unviable", "passed", ""):
                with self.assertRaises(ValueError):
                    mut.register_mutant(root, root / "target.py", "m", "t", bad, line=1)
            self.assertFalse((root / "sdlc-studio" / ".local" / "mutation-runs.json").exists())

    def test_repeated_registration_on_one_file_is_bounded_too(self) -> None:
        """`_store_ledger` bounds the ENTRY count and named this writer as the reason it does,
        but registrations on unchanged content accumulate into ONE entry's mutant list: the
        entry count never grows, the truncation never fires, and the list grows without end.
        The docstring described a bound that was not on the path it named."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            for i in range(mut.MUTANT_LIMIT + 25):
                mut.register_mutant(root, root / "target.py", f"mutant {i}", "t", "killed", line=1)
            entry = self._ledger(root)["entries"][0]
            self.assertEqual(len(entry["mutants"]), mut.MUTANT_LIMIT)
            self.assertEqual(entry["dropped_mutants"], 25)
            # the newest survive: the oldest go first, as everywhere else in this ledger
            self.assertEqual(entry["mutants"][-1]["mutant"],
                             f"mutant {mut.MUTANT_LIMIT + 24}")

    def test_the_count_reported_is_every_mutant_registered_not_the_ones_retained(self) -> None:
        """Truncating the list must not quietly reduce the number of mutants the builder is
        told they registered - that would be the ledger under-reporting its own evidence."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            total = mut.MUTANT_LIMIT + 3
            for i in range(total):
                res = mut.register_mutant(root, root / "target.py", f"m{i}", "t", "killed", line=1)
            self.assertEqual(res["registered"], total)
            self.assertEqual(self._ledger(root)["entries"][0]["summary"]["applied"], total)

    def test_a_registered_ledger_stays_bounded(self) -> None:
        """The bound is the ledger's, not the writer's: registration must go through the same
        truncation, or a per-unit practice logging every mutant grows it without limit."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            stale = [{"target": f"old{i}.py", "hash": "0" * 64, "git_rev": None,
                      "provenance": mut.PROVENANCE_MEASURED,
                      "generated_at": "2026-01-01T00:00:00Z",
                      "summary": {"applied": 1, "killed": 1, "survived": 0,
                                  "errors": 0, "unviable": 0}}
                     for i in range(mut.LEDGER_LIMIT)]
            (local / "mutation-runs.json").write_text(
                json.dumps({"version": 1, "dropped": 0, "entries": stale}), encoding="utf-8")
            self._register(mut, root)
            led = self._ledger(root)
            self.assertEqual(len(led["entries"]), mut.LEDGER_LIMIT)
            self.assertEqual(led["dropped"], 1)
            self.assertEqual(led["entries"][-1]["target"], "target.py")


class BudgetDistributionTests(unittest.TestCase):
    """CR0146: the ceiling distributes round-robin over (file, class), never
    first-N in file order."""

    def test_ceiling_spreads_across_files(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "a.py").write_text(TARGET, encoding="utf-8")
            (root / "b.py").write_text(TARGET.replace("classify", "grade"), encoding="utf-8")
            budget = 4
            muts, _ = mut.enumerate_mutations([root / "a.py", root / "b.py"])
            chosen, truncated = mut.apply_budget(muts, budget)
            files = {m["file"] for m in chosen}
            self.assertEqual(len(chosen), budget)
            self.assertEqual(len(files), 2)          # both files got budget
            self.assertGreater(truncated, 0)

    def test_distribution_is_deterministic(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.py").write_text(TARGET, encoding="utf-8")
            (root / "b.py").write_text(TARGET.replace("classify", "grade"), encoding="utf-8")
            muts, _ = mut.enumerate_mutations([root / "a.py", root / "b.py"])
            one, _ = mut.apply_budget(muts, 5)
            two, _ = mut.apply_budget(muts, 5)
            self.assertEqual(one, two)


class DocstringExclusionTests(unittest.TestCase):
    """CR0146: code-shaped lines inside docstrings/multi-line strings are not
    enumerated - they mutate nothing and false-survive."""

    def test_docstring_lines_not_enumerated(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "doc.py").write_text(
                'def compute(x):\n'
                '    """Example:\n'
                '        result = compute(2)\n'
                '        if you pass a negative:\n'
                '            return is still fine\n'
                '    """\n'
                '    y = x * 2\n'
                '    return y\n', encoding="utf-8")
            muts, _ = mut.enumerate_mutations([root / "doc.py"])
            lines = {m["line"] for m in muts}
            self.assertTrue(lines & {7, 8}, lines)     # real code enumerated
            self.assertFalse(lines & {3, 4, 5}, lines) # docstring lines excluded

    def test_tokenize_failure_degrades_loudly_not_silently(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "broken.py").write_text("def f(:\n    'unterminated\n", encoding="utf-8")
            # must not raise; the skipped exclusion is NOTED, never silent
            muts, unchecked = mut.enumerate_mutations([root / "broken.py"])
            self.assertIsInstance(muts, list)
            self.assertTrue(any(u.get("class") == "docstring-exclusion" for u in unchecked),
                            unchecked)


class DiffBiasedBudgetTests(unittest.TestCase):
    """US0218: a bounded run must spend its ceiling on the lines under review.

    Round-robin over (file, class) is fair across the SURFACE but blind to the DIFF: with a
    low ceiling on a large multi-function file it samples whichever lines sort first -
    peripheral helpers - and reports a confident kill rate about code nobody edited
    (L-0086). The evidence has to be about the change."""

    def _muts(self, spec):
        """spec: [(file, class, line), ...] -> mutation dicts in enumeration order."""
        return [{"file": f, "class": c, "line": ln, "occurrence": 0} for f, c, ln in spec]

    def test_on_diff_mutants_are_chosen_first(self) -> None:
        """AC1: the ceiling is spent on changed lines before untouched code."""
        mut = _load()
        # 20 mutants on untouched lines, 4 on changed lines, ceiling of 4
        muts = self._muts([("a.py", "comparison", ln) for ln in range(1, 21)])
        muts += self._muts([("a.py", "comparison", ln) for ln in range(100, 104)])
        chosen, truncated = mut.apply_budget(muts, 4, {"a.py": {100, 101, 102, 103}})
        self.assertEqual(sorted(m["line"] for m in chosen), [100, 101, 102, 103])
        self.assertEqual(truncated, 20)

    def test_remainder_spreads_over_untouched_code(self) -> None:
        """AC2: a small diff does not waste the rest of the budget."""
        mut = _load()
        muts = self._muts([("a.py", "comparison", ln) for ln in range(1, 21)])
        muts += self._muts([("a.py", "comparison", 100)])
        chosen, _ = mut.apply_budget(muts, 5, {"a.py": {100}})
        lines = sorted(m["line"] for m in chosen)
        self.assertIn(100, lines)          # the diff is covered...
        self.assertEqual(len(chosen), 5)   # ...and the remaining 4 went somewhere
        self.assertEqual(len([n for n in lines if n != 100]), 4)

    def test_report_states_diff_coverage(self) -> None:
        """AC3: a partially-judged diff must be legible, not inferred from truncation."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "a.py"
            # block-form guards: `invert-guard` needs the colon to end the line
            body = "def f(x):\n" + "".join(f"    if x > {i}:\n        pass\n" for i in range(12))
            target.write_text(body, encoding="utf-8")
            changed = {str(target): set(range(1, 20))}
            report = mut.run_gate(root, [target], "true", max_mutations=3,
                                  write_report=False, changed=changed)
            s = report["summary"]
            self.assertGreater(s["diff_mutations"], s["diff_applied"])
            self.assertFalse(s["diff_covered"])

    def test_no_diff_info_keeps_round_robin(self) -> None:
        """AC4: the unbiased path is untouched when there is no diff to aim at."""
        mut = _load()
        muts = self._muts([("a.py", "comparison", ln) for ln in range(1, 11)]
                          + [("b.py", "comparison", ln) for ln in range(1, 11)])
        chosen, _ = mut.apply_budget(muts, 4)
        self.assertEqual(len({m["file"] for m in chosen}), 2)   # both files covered
        chosen_again, _ = mut.apply_budget(muts, 4)
        self.assertEqual([m["line"] for m in chosen],
                         [m["line"] for m in chosen_again])      # deterministic

    def test_empty_changed_map_falls_back(self) -> None:
        """An empty map (git could not answer) must not starve selection to nothing."""
        mut = _load()
        muts = self._muts([("a.py", "comparison", ln) for ln in range(1, 11)])
        chosen, _ = mut.apply_budget(muts, 3, {})
        self.assertEqual(len(chosen), 3)


class ChangedLinesTests(unittest.TestCase):
    """US0218 AC5: the changed-line map comes from `git diff -U0`."""

    def test_reports_touched_lines_and_untracked_files(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gitutil.git(["init", "-q"], root)
            (root / "a.py").write_text("\n".join(f"x = {i}" for i in range(10)) + "\n",
                                       encoding="utf-8")
            gitutil.git(["add", "-A"], root)
            gitutil.git(["commit", "-qm", "base"], root)
            # edit line 5 only, and add a wholly new untracked module
            lines = (root / "a.py").read_text(encoding="utf-8").splitlines()
            lines[4] = "x = 999"
            (root / "a.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
            (root / "b.py").write_text("y = 1\ny = 2\n", encoding="utf-8")
            changed = mut.changed_lines(root, "HEAD")
            self.assertIn(5, changed[str(root / "a.py")])
            self.assertNotIn(1, changed[str(root / "a.py")])
            self.assertIn(str(root / "b.py"), changed)   # untracked = wholly new

    def test_returns_empty_when_git_cannot_answer(self) -> None:
        """No repo, no crash - the caller falls back to unbiased sampling."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(mut.changed_lines(Path(d), "HEAD"), {})


class StaleBytecodeTests(unittest.TestCase):
    """BG0197: a mutant the interpreter never actually ran must not report SURVIVED.

    CPython invalidates a cached `.pyc` on (source mtime, source size). A mutant of
    IDENTICAL byte length written inside the same mtime second as the previous run
    therefore reuses the stale bytecode: the ORIGINAL code executes, the tests pass,
    and the engine records the mutant as survived. Operator-swap fault classes
    produce same-length mutants as the common case, so this is not a corner.
    """

    def test_same_length_mutant_is_not_masked_by_cached_bytecode(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "mod.py"
            src.write_text('VALUE = "AAA"\n', encoding="utf-8")
            # The checker exits 0 only while the ORIGINAL value is in effect, so a
            # 'pass' after mutation means the mutant did not run.
            (root / "check.py").write_text(
                "import sys, mod\nsys.exit(0 if mod.VALUE == 'AAA' else 1)\n",
                encoding="utf-8")
            cmd = f"{sys.executable} check.py"

            self.assertEqual(mut._run_tests(cmd, root), "pass")  # baseline
            before = src.stat()
            src.write_text('VALUE = "BBB"\n', encoding="utf-8")  # same byte length
            self.assertEqual(before.st_size, src.stat().st_size,
                             "fixture invalid: the mutant must be the same length")
            # Pin mtime to the original: the exact collision CPython cannot see.
            os.utime(src, (before.st_atime, before.st_mtime))

            self.assertEqual(
                mut._run_tests(cmd, root), "fail",
                "the mutant ran against stale bytecode: the gate would record it"
                " SURVIVED without ever executing the mutated source")

    def test_pre_existing_cache_is_purged_when_the_mutant_is_applied(self) -> None:
        """The field case: a `__pycache__` that predates the gate.

        `PYTHONDONTWRITEBYTECODE` stops the runner WRITING bytecode; it does not
        stop it READING bytecode already on disk. Anyone who ran their suite before
        invoking the mutation gate - the normal order - has a populated cache, and a
        same-length mutant would execute the stale original from it. So `applied`
        must drop the cache, not merely decline to add to it.
        """
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "mod.py"
            body = "def f(x):\n    if x > 0:\n        return 1\n    return 0\n"
            src.write_text(body, encoding="utf-8")
            (root / "check.py").write_text(
                "import sys, mod\nsys.exit(0 if mod.f(1) == 1 else 1)\n", encoding="utf-8")

            # Populate the cache the way a normal test run would, BEFORE the gate.
            # Force bytecode ON for the fixture, whatever the ambient environment says.
            # This test's whole premise is a cache that already exists, and it runs under a
            # mutation harness that sets PYTHONDONTWRITEBYTECODE=1 - inheriting that wrote no
            # cache, so the precondition silently vanished and the suite failed only when
            # invoked through the gate. A fixture must establish its own preconditions rather
            # than borrow them from whoever happens to be the parent process.
            env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
            subprocess.run([sys.executable, "check.py"], cwd=root, check=True, env=env)
            cached = list(root.glob("__pycache__/mod.*.pyc"))
            self.assertTrue(cached, "fixture invalid: no pre-existing bytecode to go stale")
            before = src.stat()

            # A SAME-LENGTH mutant is the whole point: CPython invalidates on
            # (mtime, size), so a length change would invalidate the cache by itself
            # and prove nothing about purging. The profiles do not guarantee equal
            # length, so the replacement text is pinned here directly.
            same_length = body.replace("return 1", "return 9")
            self.assertEqual(len(same_length), len(body), "fixture invalid: lengths differ")
            mutation = {"file": str(src), "class": "invert-guard", "occurrence": 0, "line": 3}
            with unittest.mock.patch.object(mut, "mutated_text", return_value=same_length):
                with mut.applied(mutation):
                    # Pin mtime so (mtime, size) both still match the cached entry.
                    os.utime(src, (before.st_atime, before.st_mtime))
                    self.assertEqual(
                        mut._run_tests(f"{sys.executable} check.py", root), "fail",
                        "a pre-existing .pyc masked the mutant: the guard exists"
                        " because declining to WRITE bytecode does not stop it being READ")

    def test_run_tests_disables_bytecode_writing(self) -> None:
        """The mechanism, asserted directly - the repro above proves the effect."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "check.py").write_text(
                "import os, sys\n"
                "sys.exit(0 if os.environ.get('PYTHONDONTWRITEBYTECODE') else 1)\n",
                encoding="utf-8")
            self.assertEqual(mut._run_tests(f"{sys.executable} check.py", root), "pass")

    def test_applied_refuses_a_mutant_identical_to_the_source(self) -> None:
        """A patch that changed nothing is not a mutation; surviving it proves nothing.

        Reached by an `occurrence` index that resolves to no line - the shape a
        stale enumeration against an edited file produces. `mutated_text` then
        returns the file unchanged and the mutant 'survives' every suite trivially.
        """
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "m.py"
            body = "def f(x):\n    if x > 0:\n        return 1\n    return 0\n"
            src.write_text(body, encoding="utf-8")
            noop = {"file": str(src), "class": "invert-guard", "occurrence": 99, "line": 2}
            self.assertEqual(mut.mutated_text(noop), body,
                             "fixture invalid: this occurrence must resolve to no line")
            with self.assertRaises(ValueError):
                with mut.applied(noop):
                    pass
            self.assertEqual(src.read_text(encoding="utf-8"), body,
                             "the source must be left exactly as found")


class StrandedMutantRecoveryTests(unittest.TestCase):
    """BG0215: a killed run must leave enough on disk for the NEXT run to restore the
    original bytes - a stranded mutant must never be captured as the harness's original."""

    def test_applied_persists_original_sidecar_while_mutant_is_on_disk(self) -> None:
        import base64
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            target = root / "target.py"
            original = target.read_bytes()
            sidecar = root / "sdlc-studio" / ".local" / "mutation-inflight.json"
            muts, _ = mut.enumerate_mutations([target])
            with mut.applied(muts[0], sidecar=sidecar):
                # while the mutant is on disk, the sidecar holds the TRUE original -
                # the one source a SIGKILL cannot corrupt
                data = json.loads(sidecar.read_text(encoding="utf-8"))
                self.assertEqual(base64.b64decode(data[str(target)]), original)
            self.assertFalse(sidecar.exists())  # cleared once restored

    def test_run_gate_recovers_stranded_mutant_before_baseline(self) -> None:
        # simulate a SIGKILLed previous run: mutant stranded on disk, sidecar intact
        import base64
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            target = root / "target.py"
            original = target.read_bytes()
            muts, _ = mut.enumerate_mutations([target])
            target.write_bytes(mut.mutated_text(muts[0]).encode("utf-8"))
            sidecar = root / "sdlc-studio" / ".local" / "mutation-inflight.json"
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            sidecar.write_text(json.dumps(
                {str(target): base64.b64encode(original).decode("ascii")}), encoding="utf-8")
            r = mut.run_gate(root, [target], f"{sys.executable} -m unittest test_good")
            self.assertEqual(r.get("recovered"), [str(target)])  # recovery is reported
            self.assertFalse(r["refused"], r)   # baseline runs green AFTER recovery
            self.assertEqual(target.read_bytes(), original)  # true original back on disk
            self.assertFalse(sidecar.exists())

    def test_clean_run_reports_no_recovery(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            self.assertEqual(r.get("recovered"), [])

    def test_valid_json_non_object_sidecar_refuses_not_crashes(self) -> None:
        # round-1 MINOR: `[1, 2]` parses, then .items() raised AttributeError - a traceback
        # instead of the refusal, and the stranded mutant stayed on disk
        mut = _load()
        for payload in ("[1, 2]", '"a string"', "123", "null"):
            with tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                sidecar = root / "sdlc-studio" / ".local" / "mutation-inflight.json"
                sidecar.parent.mkdir(parents=True, exist_ok=True)
                sidecar.write_text(payload, encoding="utf-8")
                r = mut.run_gate(root, [root / "target.py"],
                                 f"{sys.executable} -m unittest test_good")
                self.assertTrue(r["refused"], payload)
                self.assertIn("git", r["remedy"] or "", payload)

    def test_unreadable_sidecar_refuses_with_remedy(self) -> None:
        # a sidecar that exists but cannot be parsed means a run died mid-mutant AND the
        # recovery source is gone: the gate must refuse loudly, never run over the wreck
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            sidecar = root / "sdlc-studio" / ".local" / "mutation-inflight.json"
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            sidecar.write_text("{not json", encoding="utf-8")
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            self.assertTrue(r["refused"], r)
            self.assertEqual(r["mutations"], [])       # nothing applied over the wreck
            self.assertIn("git", r["remedy"])          # remedy names the restore source


class SelectionReportingTests(unittest.TestCase):
    """US0277/US0278 (CR0363): a survivor must never be read without knowing what was
    run against it - the run names the test files its command selected, records the
    command in the JSON, and warns when a referencing test file is outside the
    selection (the manufactured-survivor condition). Advisory: never blocks."""

    def test_report_lists_selected_test_files(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            self.assertEqual(r["selected_tests"], [str(root / "test_good.py")])

    def test_json_records_test_command(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            cmd = f"{sys.executable} -m unittest test_good"
            mut.run_gate(root, [root / "target.py"], cmd)
            on_disk = json.loads(
                (root / "sdlc-studio" / ".local" / "mutation-report.json")
                .read_text(encoding="utf-8"))
            self.assertEqual(on_disk["test_cmd"], cmd)

    def test_warns_on_referencing_test_file_outside_selection(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            # test_good.py references `target` but the command selects only test_vacuous
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_vacuous")
            warned = [w["test_file"] for w in r["selection_warnings"]]
            self.assertIn(str(root / "test_good.py"), warned)
            self.assertTrue(all(w["references"] == "target"
                                for w in r["selection_warnings"]))

    def test_selection_warning_never_blocks(self) -> None:
        # a deliberately narrow but load-bearing selection: the excluded referencing
        # file fires the warning, and the exit code stays 0 (no survivor, no block)
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "test_other_good.py").write_text(
                GOOD_TEST.replace("class T", "class TOther"), encoding="utf-8")
            import contextlib
            import io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["run", "--files", str(root / "target.py"),
                               "--test", f"{sys.executable} -m unittest test_other_good",
                               "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("WARNING", buf.getvalue())   # the warning is SAID, not just stored
            on_disk = json.loads(
                (root / "sdlc-studio" / ".local" / "mutation-report.json")
                .read_text(encoding="utf-8"))
            warned = [w["test_file"] for w in on_disk["selection_warnings"]]
            self.assertIn(str(root / "test_good.py"), warned)

    def test_no_warning_when_selection_covers_references(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good test_vacuous")
            self.assertEqual(r["selection_warnings"], [])

    def test_ignored_file_is_not_counted_as_selected(self) -> None:
        # round-1 MINOR: `pytest tests --ignore tests/test_x.py` counted the ignored (never
        # run) referencing file as selected, so the manufactured-survivor warning stayed
        # silent - BG0203's silence reproduced through an option. Both --ignore forms.
        mut = _load()
        for form in (["--ignore", "tests/test_kills.py"], ["--ignore=tests/test_kills.py"]):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                tests = root / "tests"
                tests.mkdir()
                (root / "target.py").write_text(TARGET, encoding="utf-8")
                (tests / "test_a.py").write_text(VACUOUS_TEST, encoding="utf-8")
                (tests / "test_kills.py").write_text(GOOD_TEST, encoding="utf-8")
                cmd = "pytest tests " + " ".join(form)
                selected = mut._selected_test_files(root, cmd)
                self.assertNotIn(tests / "test_kills.py", selected or [], form)
                warned = [w["test_file"] for w in
                          mut._selection_warnings(root, [root / "target.py"], selected)]
                self.assertIn(str(tests / "test_kills.py"), warned, form)

    def test_unresolvable_command_reports_selection_unresolved(self) -> None:
        # a command no static parse can map to files must say UNRESOLVED (None),
        # never pretend an empty selection and warn on everything
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = mut.run_gate(root, [root / "target.py"], "make check")
            self.assertIsNone(r["selected_tests"])
            self.assertEqual(r["selection_warnings"], [])


class MutationSeriesRowTests(unittest.TestCase):
    """US0301 AC1: every completed run appends ONE durable row carrying its counts and its
    MEASURED wall-clock, so the gate is judged on its accumulated record rather than on the
    run that happened last."""

    def _rows(self, root: Path) -> list[dict]:
        mut = _load()
        return mut.series_rows(root)

    def test_a_completed_run_appends_one_row_with_counts_and_wall_clock(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            rep = mut.run_gate(root, [root / "target.py"],
                               f"{sys.executable} -m unittest test_good")
            rows = self._rows(root)
            self.assertEqual(len(rows), 1, rows)
            row = rows[0]
            s = rep["summary"]
            for key in ("applied", "killed", "survived"):
                self.assertEqual(row[key], s[key], key)
            self.assertEqual(row["unchecked"], len(rep["unchecked"]))
            self.assertEqual(row["run_id"], rep["run_id"])
            self.assertEqual(row["git_rev"], rep["git_rev"])
            self.assertEqual(row["at"], rep["generated_at"])
            self.assertTrue(row["at"])
            self.assertGreater(row["elapsed_s"], 0)

    def test_elapsed_is_measured_not_a_constant(self) -> None:
        # The property a hardcoded number satisfies every other assertion of: the wall-clock
        # must TRACK the time the run spent. Two runs of the same shape, one delayed by a known
        # amount, so a constant (of any value) fails on the difference rather than the size.
        mut = _load()
        import time as _time
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            cmd = f"{sys.executable} -m unittest test_good"
            mut.run_gate(root, [root / "target.py"], cmd, max_mutations=1)
            fast = self._rows(root)[-1]["elapsed_s"]
            real = mut._run_tests

            def _slow(command, cwd):
                _time.sleep(0.4)
                return real(command, cwd)

            with unittest.mock.patch.object(mut, "_run_tests", _slow):
                mut.run_gate(root, [root / "target.py"], cmd, max_mutations=1)
            slow = self._rows(root)[-1]["elapsed_s"]
            self.assertGreater(fast, 0)
            # baseline + one mutant, delayed 0.4s each: the same run, 0.8s longer
            self.assertGreaterEqual(slow - fast, 0.6)

    def test_the_row_names_the_run_surface_and_command(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            cmd = f"{sys.executable} -m unittest test_good"
            mut.run_gate(root, [root / "target.py"], cmd)
            row = self._rows(root)[0]
            self.assertEqual(row["test_cmd"], cmd)
            self.assertEqual([Path(t).name for t in row["targets"]], ["target.py"])


class MutationSeriesNoEvidenceTests(unittest.TestCase):
    """US0301 AC2: a refused, errored or killed run is recorded as producing NO EVIDENCE, so a
    reader summing the series can never count it as a clean run."""

    def _rows(self, root: Path) -> list[dict]:
        return _load().series_rows(root)

    def test_a_refused_run_records_no_evidence_and_zero_yield(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "test_red.py").write_text(RED_TEST, encoding="utf-8")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_red")
            row = self._rows(root)[0]
            self.assertFalse(row["evidence"])
            self.assertEqual(row["outcome"], "no-evidence")
            self.assertEqual(row["killed"], 0)
            self.assertEqual(row["survived"], 0)
            self.assertEqual(row["applied"], 0)
            self.assertIn("refused", row["no_evidence_reason"].lower())

    def test_an_all_error_run_records_no_evidence_even_though_it_applied_mutants(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            outcomes = iter(["pass"])   # baseline green, then every mutant errors

            def _fake(cmd, cwd):
                return next(outcomes, "error")

            with unittest.mock.patch.object(mut, "_run_tests", _fake):
                mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good", max_mutations=3)
            row = self._rows(root)[0]
            self.assertGreater(row["applied"], 0)      # mutants WERE applied...
            self.assertEqual(row["killed"], 0)
            self.assertEqual(row["survived"], 0)
            self.assertFalse(row["evidence"])          # ...and none of them judged anything
            self.assertEqual(row["outcome"], "no-evidence")

    def test_zero_survivors_over_nothing_differs_from_zero_over_twenty(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "test_red.py").write_text(RED_TEST, encoding="utf-8")
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_red")          # refused
            mut.run_gate(root, [root / "target.py"],
                         f"{sys.executable} -m unittest test_good")         # measured
            refused, measured = self._rows(root)
            self.assertEqual(refused["survived"], measured["survived"])     # both zero
            self.assertNotEqual(refused["applied"], measured["applied"])
            self.assertNotEqual(refused["outcome"], measured["outcome"])
            self.assertTrue(measured["evidence"])
            self.assertEqual(measured["outcome"], "measured")


class MutationSeriesAppendTests(unittest.TestCase):
    """US0301 AC3: the series accumulates. Earlier rows survive an append byte-identical, a
    malformed file is replaced rather than crashing the run and says so, and a dry run appends
    nothing at all."""

    def _path(self, root: Path) -> Path:
        return _load().series_path(root)

    def test_earlier_rows_are_byte_identical_after_an_append(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            cmd = f"{sys.executable} -m unittest test_good"
            mut.run_gate(root, [root / "target.py"], cmd)
            before = self._path(root).read_bytes()
            mut.run_gate(root, [root / "target.py"], cmd)
            after = self._path(root).read_bytes()
            self.assertTrue(after.startswith(before), after)
            self.assertEqual(len(mut.series_rows(root)), 2)

    def test_a_malformed_series_is_replaced_and_the_replacement_is_reported(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            path = self._path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{not json at all\n", encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["run", "--files", str(root / "target.py"),
                               "--test", f"{sys.executable} -m unittest test_good",
                               "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("mutation series", buf.getvalue())
            self.assertIn("replaced", buf.getvalue())
            self.assertEqual(len(mut.series_rows(root)), 1)   # the run's own row, and only it

    def test_a_dry_run_appends_nothing(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            with contextlib.redirect_stdout(io.StringIO()):
                mut.main(["run", "--files", str(root / "target.py"),
                          "--test", f"{sys.executable} -m unittest test_good",
                          "--root", str(root), "--dry-run"])
            self.assertFalse(self._path(root).exists())
            self.assertEqual(mut.series_rows(root), [])


def _seed_series_row(mut, root: Path, *, survived: int = 3, run_id: str | None = None) -> str:
    """One measured row in the series without running a gate - the yield reader's fixture."""
    rid = run_id or mut._new_run_id()
    mut.append_series(root, {
        "run_id": rid, "generated_at": "2026-07-22T09:00:00Z", "git_rev": "abc1234",
        "test_cmd": "python3 -m unittest discover", "targets": ["src/thing.py"],
        "refused": False, "unchecked": [],
        "summary": {"applied": 10, "killed": 7, "survived": survived,
                    "errors": 0, "unviable": 0, "truncated": 0}}, 612.5)
    return rid


def _seed_bug(root: Path, name: str, run_id: str | None) -> Path:
    """A filed bug, optionally carrying the mutation-run link file_finding stamps."""
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    link = f"> **Mutation-run:** {run_id}\n" if run_id else ""
    p = d / f"{name}-a-survivor.md"
    p.write_text(f"# {name}: a survivor\n\n> **Status:** Open\n> **Severity:** High\n"
                 f"{link}\n## Summary\n\ns\n", encoding="utf-8")
    return p


class MutationYieldAttributionTests(unittest.TestCase):
    """US0302 AC2: a run's YIELD is the artefacts filed from it, never its survivor count. A
    survivor is a hypothesis; counting hypotheses overstates the gate."""

    def test_yield_counts_filed_artefacts_not_survivors(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            rid = _seed_series_row(mut, root, survived=3)
            _seed_bug(root, "BG0001", rid)
            y = mut.run_yield(root, rid)
            self.assertEqual(y["yield"], 1)
            self.assertEqual(y["survivors"], 3)      # still visible beside it
            self.assertEqual(y["filed"], ["BG0001"])

    def test_survivors_with_nothing_filed_report_zero_yield(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            rid = _seed_series_row(mut, root, survived=3)
            y = mut.run_yield(root, rid)
            self.assertEqual(y["yield"], 0)          # never inherits the survivor count
            self.assertEqual(y["survivors"], 3)
            self.assertEqual(y["outstanding"], 3)

    def test_an_artefact_filed_against_another_run_is_not_this_run_s_yield(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            mine = _seed_series_row(mut, root, survived=2)
            theirs = _seed_series_row(mut, root, survived=2)
            _seed_bug(root, "BG0002", theirs)
            _seed_bug(root, "BG0003", None)          # a bug from no mutation run at all
            self.assertEqual(mut.run_yield(root, mine)["yield"], 0)
            self.assertEqual(mut.run_yield(root, theirs)["filed"], ["BG0002"])

    def test_an_unknown_run_is_reported_as_unfound_not_as_a_zero_yield_run(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            _seed_series_row(mut, root)
            y = mut.run_yield(root, "MRUN-ghost-000000")
            self.assertFalse(y["found"])
            self.assertIsNone(y["survivors"])


class EquivalentMutantExclusionTests(unittest.TestCase):
    """US0302 AC3 / D0052: the verdict vocabulary GAINS `equivalent`, carrying a mandatory
    reason. An equivalent mutant counts towards neither yield nor outstanding survivors, and
    the exclusion is auditable rather than a silent decrement."""

    def _target(self, root: Path) -> Path:
        p = root / "thing.py"
        p.write_text("x = 1\n", encoding="utf-8")
        return p

    def test_equivalent_is_a_registrable_verdict_and_demands_a_reason(self) -> None:
        mut = _load()
        self.assertIn("equivalent", mut.REGISTRABLE_VERDICTS)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            target = self._target(root)
            with self.assertRaises(ValueError) as ctx:
                mut.register_mutant(root, target, "swapped a constant for itself",
                                    None, "equivalent", reason="")
            self.assertIn("reason", str(ctx.exception).lower())

    def test_an_equivalent_survivor_counts_towards_neither_yield_nor_outstanding(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            target = self._target(root)
            rid = _seed_series_row(mut, root, survived=3)
            _seed_bug(root, "BG0004", rid)
            mut.register_mutant(root, target, "reordered two independent assignments",
                                None, "equivalent",
                                reason="no observable behaviour changed - unkillable", run=rid)
            y = mut.run_yield(root, rid)
            self.assertEqual(y["yield"], 1)                     # the filed bug, and only it
            self.assertEqual(y["survivors"], 3)
            self.assertEqual(len(y["equivalent"]), 1)
            self.assertEqual(y["outstanding"], 1)               # 3 - 1 filed - 1 equivalent

    def test_the_exclusion_states_its_reason_so_it_is_auditable(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            target = self._target(root)
            rid = _seed_series_row(mut, root, survived=1)
            mut.register_mutant(root, target, "reordered two independent assignments",
                                None, "equivalent",
                                reason="no observable behaviour changed - unkillable", run=rid)
            rec = mut.run_yield(root, rid)["equivalent"][0]
            self.assertEqual(rec["reason"], "no observable behaviour changed - unkillable")
            self.assertIn("reordered two independent", rec["mutant"])
            self.assertEqual(rec["verdict"], "equivalent")

    def test_an_equivalent_registered_against_another_run_does_not_discount_this_one(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            target = self._target(root)
            mine = _seed_series_row(mut, root, survived=2)
            theirs = _seed_series_row(mut, root, survived=2)
            mut.register_mutant(root, target, "a no-op swap", None, "equivalent",
                                reason="unkillable by construction", run=theirs)
            self.assertEqual(mut.run_yield(root, mine)["equivalent"], [])
            self.assertEqual(mut.run_yield(root, mine)["outstanding"], 2)

    def test_the_cli_registers_an_equivalent_verdict_with_its_reason(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            target = self._target(root)
            rid = _seed_series_row(mut, root, survived=1)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["register", "--root", str(root), "--target", str(target),
                               "--mutant", "a no-op swap", "--verdict", "equivalent",
                               "--reason", "unkillable by construction", "--run", rid])
            self.assertEqual(rc, 0)
            self.assertIn("EXCLUDED", buf.getvalue())
            self.assertEqual(len(mut.run_yield(root, rid)["equivalent"]), 1)

    def test_a_killed_or_survived_verdict_still_demands_the_test_that_judged_it(self) -> None:
        # The vocabulary grew; it did not loosen. Only `equivalent` is testless, because no
        # test could have killed it - a survived claim with no test names nothing auditable.
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            target = self._target(root)
            with self.assertRaises(ValueError):
                mut.register_mutant(root, target, "a real mutant", None, "survived", line=1)


class WindowDeclarationTests(unittest.TestCase):
    """US0307 / CR0388: any process rewriting source files in place declares an open window on
    disk, so a concurrent author is TOLD rather than discovering it from an alarming diff.

    Built against CR0388's CORRECTION, not its Summary. The staged `retro.py` carried no mutant:
    a reviewer's helper directory of `ln -sf` links turned a `git show <sha>:path > file` redirect
    into a write straight through to the live source tree. So the record must not depend on the
    change being recognisable as a mutant, nor on the suite going red - a SURVIVING mutant leaves
    the suite green by definition. A FILE, like `mutation-inflight.json`, because in-memory state
    dies with the SIGKILL that a file does not."""

    def test_a_run_declares_a_window_naming_owner_and_paths_and_clears_it(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            seen: list[dict | None] = []
            real = mut._run_tests

            def _peek(cmd, cwd):
                seen.append(mut.read_window(root))
                return real(cmd, cwd)

            with unittest.mock.patch.object(mut, "_run_tests", _peek):
                mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good", max_mutations=1)
            mid = [w for w in seen if w]
            self.assertTrue(mid, "no window was open while the run rewrote the tree")
            w = mid[-1]
            self.assertIn("mutation", w["owner"])
            self.assertEqual([Path(p).name for p in w["paths"]], ["target.py"])
            self.assertTrue(w["opened_at"])
            self.assertTrue(w["clear_with"])
            # ...and a run that finishes normally leaves nothing behind
            self.assertIsNone(mut.read_window(root))
            self.assertFalse(mut.window_path(root).exists())

    def test_a_window_left_by_a_killed_run_is_still_reported_open(self) -> None:
        # SIGKILL: no handler, no `finally`, no atexit. Only the file survives, which is why
        # the record is a file. Driven for real rather than simulated by hand.
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            script = (
                "import os, signal, sys\n"
                f"sys.path.insert(0, {str(SCRIPT.parent)!r})\n"
                "import mutation\n"
                f"mutation.open_window({str(root)!r}, 'the reviewer', [{str(root / 'target.py')!r}])\n"
                "os.kill(os.getpid(), signal.SIGKILL)\n")
            proc = subprocess.run([sys.executable, "-c", script], capture_output=True)
            self.assertEqual(proc.returncode, -9, proc.stderr)
            w = mut.read_window(root)
            self.assertIsNotNone(w, "the window died with the process it was meant to outlive")
            self.assertEqual(w["owner"], "the reviewer")
            self.assertIn("window close", w["clear_with"])

    def test_an_unreadable_or_truncated_record_reads_open_never_closed(self) -> None:
        mut = _load()
        for payload in ("{not json", "", "[1, 2]", '"a string"', '{"owner": "x"'):
            with tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                p = mut.window_path(root)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(payload, encoding="utf-8")
                w = mut.read_window(root)
                self.assertIsNotNone(w, payload)   # never read as absent
                self.assertTrue(w["unreadable"], payload)
                self.assertTrue(w["owner"], payload)

    def test_open_refuses_a_second_window_naming_who_holds_the_first(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.open_window(root, "the reviewer", [root / "target.py"])
            with self.assertRaises(ValueError) as ctx:
                mut.open_window(root, "the author", [root / "target.py"])
            self.assertIn("the reviewer", str(ctx.exception))

    def test_close_clears_it_and_a_wrong_owner_is_refused(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.open_window(root, "the reviewer", [root / "target.py"])
            with self.assertRaises(ValueError):
                mut.close_window(root, owner="somebody else")
            self.assertIsNotNone(mut.read_window(root))    # not cleared by the wrong hand
            mut.close_window(root, owner="the reviewer")
            self.assertIsNone(mut.read_window(root))

    def test_a_run_refuses_to_start_while_another_owner_holds_a_window(self) -> None:
        # The single-writer rule, executable. Two processes rewriting the same tree is the
        # hazard; a run that shouldered in would be the second writer.
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            original = (root / "target.py").read_bytes()
            mut.open_window(root, "the reviewer", [root / "target.py"])
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            self.assertTrue(r["refused"], r)
            self.assertEqual(r["mutations"], [])
            self.assertIn("the reviewer", r["remedy"])
            self.assertEqual((root / "target.py").read_bytes(), original)
            self.assertIsNotNone(mut.read_window(root))   # the other owner's window survives

    def test_the_cli_opens_reports_and_closes_a_window(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["window", "open", "--root", str(root), "--owner", "the reviewer",
                               "--paths", str(root / "target.py"),
                               "--note", "hand-applying mutants"])
            self.assertEqual(rc, 0)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["window", "status", "--root", str(root)])
            self.assertEqual(rc, 1)                       # open is not a clean state
            self.assertIn("the reviewer", buf.getvalue())
            self.assertIn("target.py", buf.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                rc = mut.main(["window", "close", "--root", str(root),
                               "--owner", "the reviewer"])
            self.assertEqual(rc, 0)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mut.main(["window", "status", "--root", str(root)]), 0)


class WindowRecordContractTests(unittest.TestCase):
    """ONE reader over BOTH spellings of the published record contract, and claims that a
    reader can actually match.

    Found by the independent review of RUN-01KY3MFX. The contract published in US0308 names
    `.local/*window*.json` AND `.local/windows/*.json`; only the pre-commit hook honoured both,
    while this module read one fixed filename. So a reviewer who wrote `windows/reviewer.json`
    was told by `window status` that no window was open, and `window open` let a SECOND writer
    declare one over the same tree - defeating the refusal whose own message says two declared
    writers in one tree is the hazard the record exists to announce.

    And the claims themselves were unmatchable: `run` builds its list from `select_files`, which
    returns `root / f`, so any absolute `--root` wrote ABSOLUTE claims into a record whose reader
    compares them against repo-relative `git diff --cached --name-only`. The window announced a
    rewrite and the commit rewriting that exact file landed.
    """

    def _rec(self, root, rel: str, paths) -> None:
        p = Path(root) / "sdlc-studio" / ".local" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"owner": "the reviewer", "opened_at": "2026-07-22T10:00:00Z",
                                 "paths": paths}), encoding="utf-8")

    def test_a_record_under_windows_is_read_as_an_open_window(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._rec(root, "windows/reviewer.json", ["target.py"])
            held = mut.read_window(root)
            self.assertIsNotNone(held, "a windows/ record read as no window at all")
            self.assertEqual(held["owner"], "the reviewer")

    def test_a_review_window_json_is_read_as_an_open_window(self) -> None:
        """The other spelling of the single-file form, which is what a reviewer writes by hand
        and is exactly what the hook's own fixture uses."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._rec(root, "review-window.json", ["target.py"])
            self.assertIsNotNone(mut.read_window(root))

    def test_a_second_writer_is_refused_whatever_spelling_holds_the_first(self) -> None:
        """The promise `open_window` makes in its own error message. It was true for one
        spelling and false for the other two."""
        mut = _load()
        for rel in ("windows/reviewer.json", "review-window.json", "mutation-window.json"):
            with self.subTest(record=rel), tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                self._rec(root, rel, ["target.py"])
                with self.assertRaises(ValueError) as ctx:
                    mut.open_window(root, "second-writer", ["target.py"])
                self.assertIn("the reviewer", str(ctx.exception))

    def test_close_clears_the_record_it_actually_read(self) -> None:
        """Unlinking a fixed filename would report a reviewer's own record closed while leaving
        it on disk - a window reported shut with a writer still inside it."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._rec(root, "windows/reviewer.json", ["target.py"])
            held = mut.close_window(root, owner="the reviewer")
            self.assertIsNotNone(held)
            self.assertFalse((Path(root) / "sdlc-studio" / ".local" / "windows"
                              / "reviewer.json").exists())
            self.assertIsNone(mut.read_window(root))

    def test_no_record_in_either_spelling_still_means_no_window(self) -> None:
        """The negative control: a discovery that found windows everywhere would satisfy every
        assertion above and refuse every commit forever."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (Path(root) / "sdlc-studio" / ".local" / "windows").mkdir(parents=True)
            (Path(root) / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                "{}", encoding="utf-8")
            self.assertEqual(mut.window_records(root), [])
            self.assertIsNone(mut.read_window(root))

    def test_an_absolute_claim_is_normalised_to_repo_relative_at_open_time(self) -> None:
        """The end-to-end shape the review reproduced: `--paths <abs>/target.py` printed
        "Commits in this tree will be refused" and then matched nothing a commit staged."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            rec = mut.open_window(root, "the reviewer", [Path(root) / "target.py"])
            self.assertEqual(rec["paths"], ["target.py"])
            self.assertEqual(mut.read_window(root)["paths"], ["target.py"])

    def test_a_run_s_own_window_records_repo_relative_claims(self) -> None:
        """`run` is the caller that produced the absolute claims, via `select_files`."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            seen: list[list[str]] = []
            real = mut._run_tests

            def _peek(cmd, cwd):
                w = mut.read_window(root)
                if w:
                    seen.append(list(w["paths"]))
                return real(cmd, cwd)

            with unittest.mock.patch.object(mut, "_run_tests", _peek):
                mut.run_gate(root, [Path(root) / "target.py"],
                             f"{sys.executable} -m unittest test_good", max_mutations=1)
            self.assertTrue(seen, "no window was open while the run rewrote the tree")
            for claim in seen[-1]:
                self.assertFalse(Path(claim).is_absolute(),
                                 f"an absolute claim cannot match a staged path: {claim}")

    def test_a_claim_outside_the_root_is_left_verbatim(self) -> None:
        """Not everything absolute is under this root, and inventing a relative spelling for a
        path that is not here would be worse than leaving it plainly uninterpretable: the
        readers treat an absolute claim as claiming the whole tree, which is the safe answer."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as other:
            root = _fixture(Path(d))
            elsewhere = str(Path(other) / "somewhere.py")
            rec = mut.open_window(root, "the reviewer", [elsewhere])
            self.assertEqual(rec["paths"], [elsewhere])


class WindowClaimNormalisationTests(unittest.TestCase):
    """A claim a reader cannot match is a window that announced a rewrite and guarded nothing.

    Found by the round-2 review of RUN-01KY3MFX. Round 1 normalised the ABSOLUTE spelling and
    left a third case: `tools/../tools/x.py` is relative, so it was recorded verbatim, and
    neither matcher normalises traversal - the claim matched NOTHING and the commit rewriting
    that exact file landed. `--files` / `--paths` accept that spelling and `select_files` does
    `root / f`, so the tool's own CLI reaches it.
    """

    def test_a_traversal_claim_is_normalised_at_open_time(self) -> None:
        mut = _load()
        for spelling in ("tools/../tools/x.py", "./tools/../tools/x.py"):
            with self.subTest(claim=spelling), tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                self.assertEqual(mut.window_claim(root, spelling), "tools/x.py")

    def test_an_absolute_traversal_claim_is_normalised_too(self) -> None:
        """The shape `select_files` produces: `root / f` over a relative path holding `..`."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            rec = mut.open_window(root, "the reviewer", [Path(root) / "tools/../tools/x.py"])
            self.assertEqual(rec["paths"], ["tools/x.py"])

    def test_a_relative_claim_that_escapes_the_root_claims_everything(self) -> None:
        """The case that cannot be spelled repo-relative at all. Left verbatim it is a literal
        pattern that matches nothing, which is the fail-OPEN direction this feature may never be
        wrong in; unnormalisable therefore reads as the whole tree."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            for spelling in ("../elsewhere.py", "tools/../../elsewhere.py", ".."):
                with self.subTest(claim=spelling):
                    self.assertEqual(mut.window_claim(root, spelling), mut.WINDOW_EVERYTHING)

    def test_a_plain_claim_is_left_matchable(self) -> None:
        """The negative control on all three: a normaliser that returned `*` for everything
        would satisfy the fail-safe cases above and freeze every tree it was opened in."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self.assertEqual(mut.window_claim(root, "tools/x.py"), "tools/x.py")
            self.assertEqual(mut.window_claim(root, "./tools/x.py"), "tools/x.py")
            self.assertEqual(mut.window_claim(root, "tools/*.py"), "tools/*.py")


class WindowRecordNormalisationTests(unittest.TestCase):
    """ONE record-level normalisation, shared with the pre-commit hook's inline reader.

    Round 2 of the same review: the two PATTERN matchers agreed, and the RECORD readings did
    not. This reader DISCARDED `paths` whenever `owner` was falsy and passed un-stripped claims
    on, so `{"paths": ["tools/x.py"]}` and `{"owner": "rev", "paths": ["  ", "tools/x.py"]}`
    were read here as claiming the whole tree while the hook read them as claiming one file.
    The hook runs the gate a few lines later, so the blocking half won: the contradiction round
    1 was rejected for, re-created one field along. A malformed owner must not change which
    paths are claimed.
    """

    def _read(self, root, payload: str) -> dict:
        mut = _load()
        p = mut.window_path(root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")
        return mut.read_window(root)

    def test_a_record_with_no_owner_keeps_its_own_claims(self) -> None:
        mut = _load()
        for payload in ('{"paths": ["tools/x.py"]}', '{"owner": "", "paths": ["tools/x.py"]}',
                        '{"owner": null, "paths": ["tools/x.py"]}'):
            with self.subTest(record=payload), tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                held = self._read(root, payload)
                self.assertEqual(held["paths"], ["tools/x.py"], payload)
                self.assertTrue(held["owner"], payload)
                # unowned: nobody can prove whose it is, so anyone may clear it
                self.assertTrue(held["unreadable"], payload)
                self.assertIsNotNone(mut.close_window(root, owner="anybody"))

    def test_a_blank_claim_is_dropped_not_read_as_everything(self) -> None:
        """A blank string reaches a matcher that strips it to `""`, where empty means the repo
        root - so one stray blank in a list turned a scoped window into a tree-wide freeze."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            held = self._read(root, '{"owner": "rev", "paths": ["  ", "tools/x.py", ""]}')
            self.assertEqual(held["paths"], ["tools/x.py"])

    def test_a_record_naming_nothing_matchable_claims_everything(self) -> None:
        """The safe direction, unchanged: absent, empty, all-blank, not a list, or holding a
        claim that is not a string."""
        mut = _load()
        for payload in ('{"owner": "rev"}', '{"owner": "rev", "paths": []}',
                        '{"owner": "rev", "paths": ["  "]}',
                        '{"owner": "rev", "paths": 7}',
                        '{"owner": "rev", "paths": [{"path": "tools/x.py"}]}',
                        '{"owner": "rev", "paths": ["tools/x.py", 0]}'):
            with self.subTest(record=payload), tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                held = self._read(root, payload)
                self.assertEqual(held["paths"], [mut.WINDOW_EVERYTHING], payload)

    def test_a_string_paths_field_naming_one_file_is_read_as_that_one_claim(self) -> None:
        """The hook reads a bare string as a one-element list; so must this, or the two readers
        disagree about a record neither of them considers malformed."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            held = self._read(root, '{"owner": "rev", "paths": "tools/x.py"}')
            self.assertEqual(held["paths"], ["tools/x.py"])


class WindowCloseIsOwnerSelectedTests(unittest.TestCase):
    """The reader was generalised to N windows; the closer stayed on first-by-sort.

    All three shapes were reproduced: a holder could not close their own window when another
    record sorted first, a bare `close` removed whichever sorted first (possibly a live
    mutation run's), and `run`'s own `finally` RAISED, stranding the window it had just opened.
    """

    def _rec(self, root, rel: str, owner: str, paths=("a.py",)) -> None:
        p = Path(root) / "sdlc-studio" / ".local" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"owner": owner, "paths": list(paths)}), encoding="utf-8")

    def test_a_holder_closes_their_own_window_whatever_sorts_first(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._rec(root, "aaa-window.json", "somebody else")
            self._rec(root, "mutation-window.json", "the reviewer")
            held = mut.close_window(root, owner="the reviewer")
            self.assertEqual(held["owner"], "the reviewer")
            self.assertFalse(mut.window_path(root).exists())
            # ...and the other writer's record is untouched
            left = [Path(p).name for p in mut.window_records(root)]
            self.assertEqual(left, ["aaa-window.json"])

    def test_closing_a_window_nobody_holds_by_that_name_is_refused(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._rec(root, "aaa-window.json", "somebody else")
            with self.assertRaises(ValueError) as ctx:
                mut.close_window(root, owner="the reviewer")
            self.assertIn("somebody else", str(ctx.exception))
            self.assertTrue(mut.window_records(root), "the refusal must leave the record")

    def test_a_bare_close_refuses_to_pick_among_several(self) -> None:
        """Removing whichever record sorted first is not a choice anyone made, and the one it
        picks may be a live run's."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._rec(root, "aaa-window.json", "somebody else")
            self._rec(root, "mutation-window.json", mut.WINDOW_OWNER_RUN)
            with self.assertRaises(ValueError) as ctx:
                mut.close_window(root)
            self.assertIn(mut.WINDOW_OWNER_RUN, str(ctx.exception))
            self.assertEqual(len(mut.window_records(root)), 2)

    def test_a_bare_close_still_clears_the_only_window(self) -> None:
        """The negative control: a closer that refused whenever it was given no owner would
        leave a stale record nobody could clear."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            self._rec(root, "review-window.json", "the reviewer")
            self.assertIsNotNone(mut.close_window(root))
            self.assertEqual(mut.window_records(root), [])

    def test_a_run_clears_its_own_window_and_never_raises_out_of_its_finally(self) -> None:
        """The stranding shape: another record sorting before `mutation-window.json` made the
        run's `finally` raise, so the run's own window outlived it and every later commit in
        that tree was refused by a writer that had finished."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            real_open = mut.open_window

            def _sneak(r, owner, paths, note=None):
                rec = real_open(r, owner, paths, note=note)
                self._rec(r, "aaa-window.json", "somebody else")
                return rec

            with unittest.mock.patch.object(mut, "open_window", _sneak):
                mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good", max_mutations=1,
                             write_report=False)
            left = [Path(p).name for p in mut.window_records(root)]
            self.assertNotIn("mutation-window.json", left,
                             "the run stranded the window it opened")
            self.assertEqual(left, ["aaa-window.json"], "it cleared another writer's record")

    def test_a_window_cleared_by_hand_mid_run_does_not_raise_out_of_the_finally(self) -> None:
        """The branch owner-selection cannot reach, tested in isolation because a sibling guard
        masks it: with the run's own record still on disk the close now always finds it. Clear
        that record by hand mid-run while another writer holds one, and the close has nothing of
        its own to clear - which must end the run with its report, not with an exception raised
        from the restore path over mutants that were all restored anyway."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            real = mut._run_tests

            def _sabotage(cmd, cwd):
                own = mut.window_path(root)
                if own.exists():
                    own.unlink()
                    self._rec(root, "aaa-window.json", "somebody else")
                return real(cmd, cwd)

            with unittest.mock.patch.object(mut, "_run_tests", _sabotage):
                report = mut.run_gate(root, [root / "target.py"],
                                      f"{sys.executable} -m unittest test_good",
                                      max_mutations=1, write_report=False)
            self.assertFalse(report["refused"], report["remedy"])
            self.assertTrue(report["mutations"], "the run produced no verdict at all")


def _load_gate():
    """The gate module, whose `_window_claims` is the lane's own per-path decision."""
    spec = importlib.util.spec_from_file_location("gate", SCRIPT.parent / "gate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: The quantifier a reason clause makes about the shared probes. It is the one part of the
#: sentence that is CHECKABLE against the matcher: "every" asserts the claim matches all
#: probes, "no" asserts it matches none. An inverted clause keeps the pinned word `glob` and
#: flips this quantifier, which a bare `assertIn("glob", msg)` cannot see.
_PROBE_QUANTIFIER = re.compile(r"matching (every|no) path the matcher probes")


def message_verdict_disagreements(reason_fn, matcher_fn, claims, probes):
    """One string per claim whose printed MESSAGE and the matcher's VERDICT disagree, both
    driven over the SAME `probes`.

    This is the pattern US0317 exists to make reusable: a sentence describing what a guard
    decides is never asserted on its own text; the message and the verdict it describes are
    driven from one battery and checked to agree. `reason_fn(claim, probes)` returns the scope
    sentence the message will carry (None means the message says a narrow, N-path window);
    `matcher_fn(claim, staged)` is the gate lane's own decision for one staged path. A failure
    names the input, so a disagreement is never silent.
    """
    out = []
    for claim in claims:
        verdict = all(matcher_fn(claim, p) for p in probes)   # the lane refuses every path
        reason = reason_fn(claim, probes)
        says_whole_tree = reason is not None
        if says_whole_tree != verdict:
            out.append(f"{claim!r}: the message says whole-tree={says_whole_tree}, the "
                       f"matcher says {verdict}")
            continue
        m = _PROBE_QUANTIFIER.search(reason or "")
        if m and (m.group(1) == "every") != verdict:
            out.append(f"{claim!r}: the reason clause claims the glob matches {m.group(1)!r} "
                       f"path the matcher probes, but the lane refuses "
                       f"{'every' if verdict else 'not every'} staged path")
            continue
        # BG0259's reason reports the EVIDENCE as a probe list `[a, a/b.py, ...]` rather than a
        # quantifier word. A whole-tree verdict must list every probe; a reason that lists
        # fewer while the lane refuses every path is the same disagreement, one the quantifier
        # scan cannot see - so the two message formats are both held to the verdict.
        if reason and "[" in reason and "]" in reason:
            listed = [x for x in reason[reason.index("[") + 1:reason.rindex("]")].split(",")
                      if x.strip()]
            if (len(listed) == len(probes)) != verdict:
                out.append(f"{claim!r}: the reason lists {len(listed)} of {len(probes)} probes "
                           f"but the lane refuses {'every' if verdict else 'not every'} path")
    return out


class MessageVerdictAgreementTests(unittest.TestCase):
    """US0317: where a message and a verdict must agree, ONE test drives BOTH over ONE input
    battery and asserts they agree.

    Asserting the message's text on its own is what let the `window open` reason clause be
    wrong five times: a word survives inside a sentence that denies the verdict printed beside
    it. `assertIn(EXPECTED_REASON[claim], msg)` pins `glob`, and a clause reworded from "a glob
    matching every path" to "a glob matching no path" - a denial of the WHOLE TREE verdict on
    the same line - keeps the word and stays green. Driving the message and the verdict over
    one shared battery catches it.
    """

    #: One battery of claims, whole-tree and narrow shapes mixed, so a message hard-wired
    #: either way disagrees with the matcher on some input.
    CLAIMS = (".", "./", "/etc/hosts", "*", "**", "?*", "", "  ",
              "tools/x.py", "src/app.py", "*.md", "a/b")

    @classmethod
    def setUpClass(cls):
        cls.mut = _load()
        cls.gate = _load_gate()

    def test_one_battery_drives_both_the_message_and_the_verdict(self):
        probes = self.mut.WINDOW_PROBES
        fails = message_verdict_disagreements(
            self.mut.everything_reason, self.gate._window_claims, self.CLAIMS, probes)
        self.assertEqual([], fails, f"message and verdict disagree over the shipped code: {fails}")
        # ONE battery, not two. The message-derivation PROBES the same tuple the matcher is
        # asked over: prove it by moving the battery and watching the message verdict move in
        # lockstep, so neither side can hold a private list it was tuned against.
        self.assertIsNotNone(
            self.mut.everything_reason("*.md", ("a.md", "b.md")),
            "`*.md` matches every probe in THIS battery, so the message must call it whole-tree")
        self.assertIsNone(
            self.mut.everything_reason("*.md", ("a.py", "b.md")),
            "`*.md` misses `a.py`, so over THIS battery the message must NOT call it whole-tree")

    def test_an_inverted_derivation_fails_even_when_it_keeps_the_pinned_word(self):
        probes = self.mut.WINDOW_PROBES
        mut = self.mut

        def inverted(claim, p):
            """The derivation deliberately inverted: the sentence keeps the word `glob` and its
            probe-list shape, but drops a probe so it claims a narrower match than the verdict."""
            r = mut.everything_reason(claim, p)
            if r and "glob" in r and "[" in r:
                listed = r[r.index("[") + 1:r.rindex("]")].split(", ")
                if len(listed) > 1:
                    return r[:r.index("[") + 1] + ", ".join(listed[:-1]) + "]"
            return r

        self.assertIn("glob", inverted("*", probes),
                      "the inversion must keep the pinned word, or it proves nothing")
        fails = message_verdict_disagreements(
            inverted, self.gate._window_claims, self.CLAIMS, probes)
        self.assertTrue(fails, "an inverted clause that keeps the word `glob` slipped past the "
                               "agreement check - the very failure US0317 exists to catch")
        self.assertTrue(any(repr("*") in f for f in fails),
                        f"the failure must NAME the input whose message and verdict disagree: {fails}")


class WindowOpenMessageTests(unittest.TestCase):
    """The CLI must promise what the guard does.

    `window open` printed "Commits in this tree will be refused until it is closed". That was
    true while the gate lane blocked on the record's EXISTENCE; the guard is PATH-SCOPED now,
    and a commit staging nothing the window claims proceeds. No test asserted the string, so
    the message survived the behaviour it described. This drives the CLI and the lane over the
    SAME window, so the message cannot drift from the verdict again.
    """

    def _repo(self, d) -> Path:
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "tools").mkdir()
        (root / "tools" / "x.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "README.md").write_text("notes\n", encoding="utf-8")
        gitutil.git(["init", "-q"], cwd=root)
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", "fixture"], cwd=root)
        return root

    def _lane(self, root: Path) -> dict:
        import importlib.util as _il
        spec = _il.spec_from_file_location("gate", SCRIPT.parent / "gate.py")
        mod = _il.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.DEFAULT_CHECKS["window"](str(root))

    def test_the_open_message_promises_only_what_the_guard_does(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["window", "open", "--root", str(root), "--owner", "the reviewer",
                               "--paths", "tools/x.py"])
            self.assertEqual(rc, 0)
            msg = buf.getvalue()
            self.assertNotIn("Commits in this tree will be refused", msg,
                             "the message outlived the tree-wide freeze it described")
            self.assertIn("tools/x.py", msg, "it must name what it claims")
            self.assertIn("claim", msg.lower())
            # ...and the message is TRUE of the guard: an unclaimed path proceeds
            (root / "README.md").write_text("notes and more notes\n", encoding="utf-8")
            gitutil.git(["add", "README.md"], cwd=root)
            self.assertEqual(self._lane(root)["count"], 0,
                             "the lane refuses a commit the message says proceeds")
            # ...and a claimed one is refused, which is what the message now promises
            (root / "tools" / "x.py").write_text("VALUE = 999\n", encoding="utf-8")
            gitutil.git(["add", "tools/x.py"], cwd=root)
            self.assertEqual(self._lane(root)["count"], 1,
                             "the lane allows a commit the message says is refused")

    def test_the_default_invocation_says_it_claims_the_whole_tree(self) -> None:
        """Round 3 MAJOR 1. `--paths` defaults to empty and both readers normalise empty to
        WINDOW_EVERYTHING, so the DOCUMENTED default opens a whole-tree window - while the
        message printed "0 path(s)" and promised that anything else proceeds. That understates
        the guard, which is the worse direction: an author told the window is narrow when it
        claims everything concludes the guard is inert.

        The test above passes on the broken code because it only ever opens `--paths tools/x.py`.
        This drives the DEFAULT, and asserts the lane agrees with the sentence."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mut.main(["window", "open", "--root", str(root), "--owner", "the reviewer"])
            self.assertEqual(rc, 0)
            msg = buf.getvalue()
            self.assertIn("WHOLE TREE", msg, "an unscoped window must say what it really claims")
            self.assertNotIn("anything\nelse proceeds", msg)
            self.assertNotIn("else proceeds", msg,
                             "nothing proceeds under a window claiming everything")
            self.assertNotIn("0 path(s)", msg, "empty paths is EVERYTHING, never nothing")
            # the lane must agree with the sentence: an unrelated staged path is still refused
            (root / "README.md").write_text("notes and more notes\n", encoding="utf-8")
            gitutil.git(["add", "README.md"], cwd=root)
            self.assertEqual(self._lane(root)["count"], 1,
                             "the message says every commit is refused; the lane must too")

    def test_an_all_blank_paths_list_is_also_the_whole_tree(self) -> None:
        """The sibling shape the reviewer reproduced: `--paths "   " "  "` printed
        "2 path(s):    ,   " and promised anything else proceeds, while both readers normalise
        all-blank to everything."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mut.main(["window", "open", "--root", str(root), "--owner", "r",
                          "--paths", "   ", "  "])
            msg = buf.getvalue()
            self.assertIn("WHOLE TREE", msg)
            self.assertNotIn("2 path(s)", msg)

    def test_a_claim_the_MATCHER_treats_as_everything_is_named_as_everything(self) -> None:
        """Round 4 MAJOR. The message rendered what `window_claims` RETURNS, not what the
        matcher DECIDES. `--paths .` and `--paths /etc/hosts` normalise to themselves, so the
        CLI said "1 path(s)" and promised anything else proceeds, while both matchers refuse
        every staged path. Fourth wrong version of this sentence; the first three all asked the
        record what it said instead of asking what would be done with it."""
        mut = _load()
        # NOT `tools/../tools/x.py`: `window_claim` normalises traversal AT OPEN TIME, so via
        # the CLI it becomes the real scoped path `tools/x.py` and the narrow message is then
        # correct. It claims everything only as a HAND-WRITTEN record already on disk, which the
        # matcher-agreement test below covers.
        EXPECTED_REASON = {
            ".": "repository root", "./": "repository root",
            "/etc/hosts": "absolute", "*": "glob", "**": "glob", "?*": "glob",
        }
        for claim in (".", "./", "/etc/hosts", "*", "**", "?*"):
            with self.subTest(claim=claim), tempfile.TemporaryDirectory() as d:
                root = self._repo(d)
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    mut.main(["window", "open", "--root", str(root), "--owner", "r",
                              "--paths", claim])
                msg = buf.getvalue()
                self.assertIn("WHOLE TREE", msg, f"{claim!r} claims everything to the matcher")
                self.assertNotIn("else proceeds", msg)
                # A PER-CLAIM assertion, possible now that the message names the ONE cause that
                # applies. The previous `assertIn("glob", msg)` was claim-independent -
                # it passed for `.` while its failure text claimed to have checked why `.` was
                # total, and a mutant deleting the other four causes survived it. This fails if
                # the reason drifts from the claim in hand.
                self.assertIn(EXPECTED_REASON[claim], msg,
                              f"{claim!r}: the reason clause must name why THIS claim is total")
                for other, phrase in EXPECTED_REASON.items():
                    if other != claim and phrase not in EXPECTED_REASON[claim]:
                        self.assertNotIn(phrase, msg,
                                         f"{claim!r}: names {other!r}'s cause, not its own")
                # The removed word-check, kept as a note. Round 6 found the
                # clause stale for globs and the repair added `assertIn("glob", msg)` - but the
                # message is ONE STATIC STRING naming every cause for every input, so that
                # assertion is claim-independent: it passes for `.` while its own failure text
                # claims to have checked why `.` is total, and a mutant deleting the other four
                # causes survives it. A word check is not a claim check, which is the finding
                # this very module exists to make. BG0259 owns the real fix - print only the
                # cause that APPLIES - and a per-claim assertion becomes possible there and is
                # impossible here. An assertion that cannot discriminate is worse than none,
                # because it reads as coverage.
                (root / "README.md").write_text("changed\n", encoding="utf-8")
                gitutil.git(["add", "README.md"], cwd=root)
                self.assertEqual(self._lane(root)["count"], 1,
                                 "the lane must agree with the sentence")

    def test_the_helper_agrees_with_the_gate_matcher_on_every_shape(self) -> None:
        """The message and the verdict share ONE rule. Two implementations of "claims
        everything" is how the sentence came to disagree with the guard four times."""
        mut = _load()
        import importlib.util as _il
        spec = _il.spec_from_file_location("gate", SCRIPT.parent / "gate.py")
        gate = _il.module_from_spec(spec); spec.loader.exec_module(gate)
        # A BATTERY, not one path. Round 5: the previous oracle asked the matcher about a
        # SINGLE unrelated path, which cannot distinguish "claims everything" from "happens to
        # match this one" - so `*.md` or `*/*` would have failed it falsely, and the shape list
        # had been chosen around exactly the families where the two agree by construction. The
        # battery is the module's own, so a shrunk `WINDOW_PROBES` is caught here too.
        BATTERY = mut.WINDOW_PROBES
        for claim in ("", " ", "\t", ".", "./", "/abs/x.py", "..", "../x.py", "a/../b.py",
                      "*", "**", "***", "?*", "**/", "*.md", "*/*", "src/**/*.py",
                      "a*", "[a-zA-Z.]*", "*.",
                      "tools/x.py", "tools/", "a" * 5000, 7, None, True, ["x"], {"a": 1}):
            with self.subTest(claim=claim):
                mine = mut.claims_everything(claim)
                # ASK the matcher for every claim, including non-strings. Short-circuiting to
                # a constant for those made the assertion message say "the matcher says X"
                # without having asked it - a regression this very repair introduced.
                theirs = all(gate._window_claims(claim, s) for s in BATTERY)
                self.assertEqual(
                    mine, theirs,
                    f"{claim!r}: the CLI says everything={mine}, the matcher says {theirs} - "
                    "the message and the verdict must come from one rule")

    def test_a_scoped_window_still_says_what_it_scopes(self) -> None:
        """Negative control. Without it, a message hard-coded to WHOLE TREE would pass the two
        tests above while destroying the scoped case the feature exists for."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mut.main(["window", "open", "--root", str(root), "--owner", "r",
                          "--paths", "tools/x.py"])
            msg = buf.getvalue()
            self.assertNotIn("WHOLE TREE", msg)
            self.assertIn("tools/x.py", msg)
            self.assertIn("else proceeds", msg)

    @staticmethod
    def _actual_probe_hits(mut, claim: str) -> set:
        """The probes `claim` really matches, recomputed here so the reason is checked against
        the MATCHER rather than against another copy of itself."""
        import fnmatch
        pat = claim.strip()
        if pat.startswith("./"):
            pat = pat[2:]
        pat = pat.rstrip("/")
        return {s for s in mut.WINDOW_PROBES
                if s.startswith(pat + "/") or fnmatch.fnmatch(s, pat)}

    def test_the_reason_clause_reports_the_evidence_the_probe_produced(self) -> None:
        """BG0259 AC1. Two claims decided by DIFFERENT branches must carry different evidence, so
        the sentence varies with its input and cannot be satisfied by a constant. The glob branch
        names the probes it matched; the dot branch names the root and borrows none of that."""
        mut = _load()
        dot = mut.everything_reason(".")
        glob = mut.everything_reason("**")
        self.assertIsNotNone(dot)
        self.assertIsNotNone(glob)
        self.assertNotEqual(dot, glob, "the reason must vary with the branch that decided it")
        # the glob reason reports what the probe established: every probe it matched, named
        hits = self._actual_probe_hits(mut, "**")
        self.assertEqual(hits, set(mut.WINDOW_PROBES), "precondition: ** matches every probe")
        for p in mut.WINDOW_PROBES:
            self.assertIn(p, glob, f"the glob reason must name the probe {p!r} it matched")
        # the dot branch reports its OWN evidence, not the glob's - a constant would share text
        self.assertNotIn("a/b.py", dot)
        self.assertNotIn("[", dot)

    def test_an_inverted_reason_clause_fails_even_though_it_keeps_the_word_glob(self) -> None:
        """BG0259 AC2, the whole of this bug. The glob branch rewritten to DENY the verdict
        printed beside it - to report the probes it did NOT match - keeps the word `glob` the old
        `assertIn("glob", msg)` pinned, and that assertion survived the inversion. This drives the
        reason and the matcher over the SAME claim and asserts the reported probe set IS the
        matched set, so a clause naming the opposite (or empty) set goes red while still saying
        `glob`. Measured: with the branch inverted this test is RED; shipped, it is green."""
        mut = _load()
        import re
        for claim in ("*", "**", "?*"):
            with self.subTest(claim=claim):
                reason = mut.everything_reason(claim)
                self.assertIsNotNone(reason)
                self.assertIn("glob", reason, "precondition: the reason names the glob branch")
                inside = re.search(r"\[([^\]]*)\]", reason)
                self.assertIsNotNone(inside, "the reason must enumerate the probes it reports")
                named = {p for p in inside.group(1).split(", ") if p}
                actual = self._actual_probe_hits(mut, claim)
                self.assertEqual(
                    named, actual,
                    "the reason must report the probes the matcher ACCEPTED - an inverted clause "
                    "names the opposite set and keeps the word 'glob'; a word check cannot see it")
                self.assertEqual(actual, set(mut.WINDOW_PROBES),
                                 f"{claim!r} is a whole-tree glob; every probe must be reported")

    def test_a_claim_matching_every_probe_but_not_every_path_agrees_with_the_lane(self) -> None:
        """BG0259 AC3. `[a-zA-Z.]*` matches every letter-or-dot probe, so before the fix the CLI
        printed WHOLE TREE while `gate._window_claims("[a-zA-Z.]*", "9data.txt")` is False and that
        commit proceeded - message and verdict contradicting each other on a real input. The fix
        makes them agree: the probe battery includes a digit-leading path, so the claim is scoped,
        not total, and the lane lets `9data.txt` through under a message that no longer overclaims."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mut.main(["window", "open", "--root", str(root), "--owner", "r",
                          "--paths", "[a-zA-Z.]*"])
            msg = buf.getvalue()
            (root / "9data.txt").write_text("digit-leading\n", encoding="utf-8")
            gitutil.git(["add", "9data.txt"], cwd=root)
            refused = self._lane(root)["count"]
            # the CLI and the lane must AGREE on 9data.txt
            if "WHOLE TREE" in msg:
                self.assertEqual(refused, 1, "message claims the whole tree; the lane must refuse")
            else:
                self.assertEqual(refused, 0, "message scopes the window; the lane must let it pass")
            # and specifically, after the fix, the claim is scoped and the commit proceeds
            self.assertNotIn("WHOLE TREE", msg,
                             "[a-zA-Z.]* matches every letter probe but not 9data.txt: not total")
            self.assertEqual(refused, 0, "the lane must let a path the claim cannot match proceed")


class EverythingReasonProbeTests(unittest.TestCase):
    """The probe battery that decides "claims everything" is derived, wide, and load-bearing.

    Two properties nothing exercised before BG0260: the comment's example globs must come from
    the battery (so a wrong spelling like `*.` cannot be typed into it), and the battery must be
    wide enough that a prefix glob is not read as the whole tree (so it cannot be shrunk to one
    redundant probe)."""

    def test_the_glob_examples_are_derived_from_the_probe_battery(self) -> None:
        """BG0260 AC3. mutation.py's comment listed `*.` among patterns matching every path,
        while `fnmatch` matches it against none of the six probes. Examples now come from
        `everything_glob_examples`, which filters candidates by the battery, so a spelling that
        does not match every probe cannot be offered."""
        mut = _load()
        import fnmatch
        examples = mut.everything_glob_examples()
        self.assertTrue(examples, "at least one glob family matches every probe")
        for g in examples:
            pat = g.rstrip("/")
            for p in mut.WINDOW_PROBES:
                self.assertTrue(
                    p.startswith(pat + "/") or fnmatch.fnmatch(p, pat),
                    f"{g!r} was offered as a whole-tree glob but misses the probe {p!r}")
        # the two spellings the comment got wrong, filtered out by construction
        self.assertNotIn("*.", examples, "`*.` matches none of the probes; it is not everything")
        self.assertNotIn("a*", examples, "a prefix glob matches only part of the tree")

    def test_a_prefix_glob_is_not_announced_as_the_whole_tree(self) -> None:
        """BG0260 AC4. `a*` matches only the paths under `a`, not the tree. A battery shrunk from
        seven probes to one passed the whole suite, and a one-probe battery announces WHOLE TREE
        for `a*` while the matcher refuses only paths under `a`. `claims_everything` reads the
        module battery, so shrinking `WINDOW_PROBES` makes the assertion below go red."""
        mut = _load()
        import fnmatch
        self.assertFalse(mut.claims_everything("a*"),
                         "a* is a prefix glob, not the whole tree")
        self.assertIsNone(mut.everything_reason("a*"))
        # the width is what refuses a*: a one-probe battery WOULD call it everything
        hit = lambda probes: all(s.startswith("a/") or fnmatch.fnmatch(s, "a*") for s in probes)
        self.assertTrue(hit(mut.WINDOW_PROBES[:1]),
                        "a one-probe battery would wrongly read a* as the whole tree")
        self.assertFalse(hit(mut.WINDOW_PROBES),
                         "the full battery has a probe a* cannot match, so it is refused")
        self.assertGreater(len(mut.WINDOW_PROBES), 1,
                           "the battery must stay wider than one probe or a* masquerades as total")


class LedgerSummaryVocabularyTests(unittest.TestCase):
    """`SUMMARY_VERDICTS` says "one list, so a new verdict cannot be countable in one writer and
    absent in another". Both writers now derive from it; `append_ledger` used to hard-code its
    own five counters and never mentioned `equivalent`, so the comment asserted something that
    was already false."""

    def test_every_summary_counter_is_present_in_a_run_s_entry(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            report = {"targets": ["target.py"], "target_hashes": {"target.py": "abc"},
                      "git_rev": "0" * 40, "generated_at": "2026-07-22T00:00:00Z",
                      "test_cmd": "true"}
            records = [{"file": "target.py", "verdict": "killed"},
                       {"file": "target.py", "verdict": "survived"},
                       {"file": "target.py", "verdict": "error"},
                       {"file": "target.py", "verdict": "unviable"}]
            mut.append_ledger(root, report, records)
            entry = json.loads(mut.ledger_path(root).read_text(encoding="utf-8"))["entries"][0]
            for key in mut.SUMMARY_VERDICTS:
                self.assertIn(key, entry["summary"], key)
            self.assertEqual(entry["summary"]["killed"], 1)
            self.assertEqual(entry["summary"]["survived"], 1)
            self.assertEqual(entry["summary"]["errors"], 1)
            self.assertEqual(entry["summary"]["unviable"], 1)

    def test_the_two_writers_count_into_the_same_names(self) -> None:
        """A register writes the other kind of entry. If the two used different counter names
        the coverage lane would read one of them as all-zero."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            mut.register_mutant(root, "target.py", "a -> b", "test_good", "killed", line=1)
            entry = json.loads(mut.ledger_path(root).read_text(encoding="utf-8"))["entries"][0]
            for key in mut.SUMMARY_VERDICTS:
                self.assertIn(key, entry["summary"], key)


class RegisterRunAttributionRefusalTests(unittest.TestCase):
    """`register --run` refuses a run the series does not hold. The refusal was reached by NO
    test: replacing its condition with `if False:` left all 98 tests in this file green."""

    def test_registering_against_an_unrecorded_run_is_refused(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            with self.assertRaises(ValueError) as ctx:
                mut.register_mutant(root, "target.py", "a -> b", "test_good", "killed",
                                    line=1, run="MUT-nobody-recorded-this")
            self.assertIn("MUT-nobody-recorded-this", str(ctx.exception))
            self.assertFalse(mut.ledger_path(root).exists(),
                             "a refused registration must write nothing")

    def test_a_run_the_series_does_hold_is_accepted(self) -> None:
        """The positive control: a refusal that fired on everything would pass the test above
        while making `--run` unusable."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            report = {"run_id": "MUT-real", "summary": {"applied": 1, "killed": 1,
                                                        "survived": 0, "errors": 0,
                                                        "unviable": 0, "truncated": 0},
                      "targets": ["target.py"], "generated_at": "2026-07-22T00:00:00Z",
                      "elapsed_seconds": 1.0, "test_cmd": "true"}
            mut.append_series(root, report, 1.0)
            out = mut.register_mutant(root, "target.py", "a -> b", "test_good", "killed",
                                      line=1, run="MUT-real")
            self.assertEqual(out["verdict"], "killed")


class StrategyScopedTests(unittest.TestCase):
    """US0422: the plan-time strategy names which units are worth mutating, replacing the
    blanket close-scoped sweep. The difference is not size - it is provenance. A sweep spends
    its ceiling on whatever it reaches first; this spends it on units a stated strategy said
    were worth mutating, decided in the open and checkable at the close."""

    TSD = """# TSD

## Test Levels

### Unit Testing

Covers `alpha.py`.

### Mutation Testing (assertion integrity)

Covers `gate.py`.

## Next
"""

    def _repo(self, d: str) -> Path:
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / "tsd.md").write_text(self.TSD, encoding="utf-8")
        (root / "gate.py").write_text("x = 1\n", encoding="utf-8")
        (root / "alpha.py").write_text("y = 2\n", encoding="utf-8")
        for uid, aff in (("US0001", "gate.py"), ("US0002", "alpha.py")):
            (root / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** {aff}\n", encoding="utf-8")
        return root

    def test_the_run_mutates_the_units_the_strategy_named(self) -> None:
        """AC1."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            picked = mod.select_files(root, strategy=["US0001", "US0002"])
        names = sorted(p.name for p in picked)
        self.assertEqual(names, ["gate.py"],
                         "only the unit whose band demanded mutation contributes its files")

    def test_the_blanket_sweep_does_not_also_run(self) -> None:
        """AC2. Two selection rules produce two answers to the same question, and the close
        currently spends its ceiling on whichever it reaches first. Selecting a strategy
        surface must therefore be exclusive of the diff sweep, not additive to it."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            picked = mod.select_files(root, strategy=["US0001"])
            explicit = mod.select_files(root, files=["alpha.py"])
        self.assertNotIn("alpha.py", [p.name for p in picked],
                         "the strategy surface must not widen to the whole diff")
        self.assertEqual([p.name for p in explicit], ["alpha.py"],
                         "an explicit --files surface is unchanged by any of this")

    def test_no_surface_at_all_is_still_refused(self) -> None:
        """The control: adding a fourth way to choose a surface must not make it optional to
        choose one. A run with no surface would mutate nothing and report a clean sweep."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                mod.select_files(Path(d))


class WorktreeScanExclusionTests(unittest.TestCase):
    """BG0296 (repointed): the test-file scan descended into gitignored worktree copies
    (.claude/worktrees/agent-*/), padding the covering command with dozens of stale duplicates.
    The original filing blamed guard-clause blindness - disproved: the tool mutates guards fine
    (invert-guard matches an `if ...:` line). The real defect is the gitignored-path scan, fixed
    by filtering on .gitignore rather than on a path component named 'worktrees' (which would skip
    the whole tree when run from inside a worktree)."""

    def _repo(self, root: Path) -> None:
        (root / "tests").mkdir(parents=True, exist_ok=True)
        (root / "tests" / "test_real.py").write_text("def test_x():\n    assert True\n",
                                                      encoding="utf-8")
        # a gitignored worktree with a DUPLICATE copy of the test
        wt = root / ".claude" / "worktrees" / "agent-deadbeef" / "tests"
        wt.mkdir(parents=True, exist_ok=True)
        (wt / "test_real.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
        (root / ".gitignore").write_text(".claude/worktrees/\n", encoding="utf-8")
        gitutil.git(["init", "-q"], root)
        gitutil.git(["add", "tests/test_real.py", ".gitignore"], root)
        gitutil.git(["commit", "-qm", "base"], root)

    def test_gitignored_worktree_copies_are_excluded(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            found = mod._candidate_test_files(root)
            names = {str(p.relative_to(root)) for p in found}
            self.assertIn("tests/test_real.py", names)                # the real test survives
            # no worktree copy is scanned
            self.assertFalse(any("worktrees" in str(p) for p in found),
                             f"a gitignored worktree copy leaked into the scan: {found}")

    def test_a_real_tree_is_not_skipped_by_a_worktrees_ancestor(self) -> None:
        """The scar-avoidance: filtering is by .gitignore, not by a component named 'worktrees', so
        a project that legitimately lives under a path with 'worktrees' in it is not blanked."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            # the repo root itself sits under a 'worktrees' component, and its tests are TRACKED
            root = Path(d) / "worktrees" / "myproject"
            (root / "tests").mkdir(parents=True, exist_ok=True)
            (root / "tests" / "test_real.py").write_text("def test_x():\n    assert True\n",
                                                         encoding="utf-8")
            gitutil.git(["init", "-q"], root)
            gitutil.git(["add", "-A"], root)
            gitutil.git(["commit", "-qm", "base"], root)
            found = mod._candidate_test_files(root)
            names = {str(p.relative_to(root)) for p in found}
            self.assertIn("tests/test_real.py", names)   # NOT skipped despite the ancestor name

    def test_scan_degrades_when_git_is_unavailable(self) -> None:
        """_drop_ignored is best-effort: a non-repo directory returns its candidates unfiltered
        rather than raising - the scan must never break on a git failure."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)          # no git repo here
            (root / "tests").mkdir()
            f = root / "tests" / "test_x.py"
            f.write_text("def test_x():\n    assert True\n", encoding="utf-8")
            self.assertEqual(mod._drop_ignored(root, [f]), [f])


class IsolationTests(unittest.TestCase):
    """US0504: a delegated reviewer mutates an ISOLATED checkout, never the author's live tree.

    The tool half of that rule. A mutant written over a file that carries uncommitted work
    cannot be told apart from that work when the file is restored: the restore path writes
    back whatever bytes the run read, and every published remedy for a stranded mutant says
    'restore the target files from git', which throws the uncommitted work away. That is not
    hypothetical - a reviewer mutation-testing in the author's tree silently reverted a
    shipped repair, and the suite stayed green over the reverted code because the repair had
    no test pinning it. So `run` refuses a dirty target, naming it, before touching a byte.
    """

    def _repo(self, d: Path) -> Path:
        root = _fixture(d)
        gitutil.git(["init", "-q"], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-qm", "base"], root)
        return root

    def test_mutation_refuses_a_dirty_file(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            target = root / "target.py"
            # The author's uncommitted repair, sitting in the tree the reviewer was pointed at.
            # Deliberately behaviour-PRESERVING, so the committed tests stay green over it: a
            # refusal here can then only come from the dirty check, never from a red baseline.
            target.write_text(TARGET + "\n# the author's uncommitted repair\n", encoding="utf-8")
            dirty_bytes = target.read_bytes()
            r = mut.run_gate(root, [target], f"{sys.executable} -m unittest test_good")
            self.assertTrue(r["refused"], r)
            self.assertEqual(r["mutations"], [])                  # nothing applied
            self.assertEqual(r["summary"]["applied"], 0)
            self.assertEqual(r["dirty_targets"], ["target.py"])   # named, not merely counted
            self.assertIn("target.py", r["remedy"] or "")
            self.assertEqual(target.read_bytes(), dirty_bytes)    # the repair is still there
            # and the CLI ACTS on it: the refusal names the dirty file, not a baseline verdict
            # (the baseline never ran), and exits non-zero
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = mut.main(["run", "--files", str(target),
                               "--test", f"{sys.executable} -m unittest test_good",
                               "--root", str(root)])
            self.assertNotEqual(rc, 0)
            msg = err.getvalue()
            self.assertIn("REFUSED", msg)
            self.assertIn("target.py", msg)
            self.assertIn("uncommitted", msg.lower())
            # The refusal happens BEFORE the baseline, so the message must not quote a baseline
            # verdict for a run that never happened. This is what pins the caller: the generic
            # refusal branch prints `baseline <verdict>`, and would otherwise pass every
            # assertion above on the strength of the remedy string alone.
            self.assertNotIn("baseline", msg.lower(), msg)

    def test_a_committed_file_is_still_mutated(self) -> None:
        """The control. A guard that refused every file would pass the test above while
        switching the gate off, so a clean tracked target must still run to a verdict."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            target = root / "target.py"
            r = mut.run_gate(root, [target], f"{sys.executable} -m unittest test_good")
            self.assertEqual(r["dirty_targets"], [])
            self.assertFalse(r["refused"], r)
            self.assertGreater(r["summary"]["killed"], 0, r)
            # An UNTRACKED target is dirty too, and for the worse reason: it has no committed
            # state to restore from at all, so a stranded mutant over it is unrecoverable.
            new = root / "helper.py"
            new.write_text(TARGET, encoding="utf-8")
            self.assertEqual(mut.dirty_targets(root, [new]), ["helper.py"])

    def test_a_non_git_tree_is_unknown_not_clean(self) -> None:
        """Outside a repository git cannot answer, so the check reports UNKNOWN (None) rather
        than clean. The run proceeds - refusing every non-repo fixture would be a worse
        failure - but the report says the tree was never checked, so a reader is not told a
        dirty tree was clean."""
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))          # no git repo here
            self.assertIsNone(mut.dirty_targets(root, [root / "target.py"]))
            r = mut.run_gate(root, [root / "target.py"],
                             f"{sys.executable} -m unittest test_good")
            self.assertIsNone(r["dirty_targets"])
            self.assertFalse(r["refused"], r)


class KilledMutantsCarryTheirKillerTests(unittest.TestCase):
    """BG0357. `US0507` ships a consumer that nominates a test no mutation of its own module can
    kill, and it requires each killed mutant to carry the test that killed it. `mutation.py` -
    this repository's only producer of mutation evidence - threw the runner's output away, so
    the key was never emitted and the consumer took its refusal branch against every real
    report. Loud rather than falsely green, but the capability was unreachable."""

    def test_a_pytest_failure_is_attributed(self) -> None:
        mut = _load()
        self.assertEqual(
            "tests/test_x.py::C::test_y",
            mut._killing_test("FAILED tests/test_x.py::C::test_y - AssertionError"))

    def test_a_unittest_failure_is_attributed(self) -> None:
        """Two runners, both parsed. A parser knowing one would attribute nothing for the
        other, which is the same silence this fix exists to end."""
        mut = _load()
        self.assertEqual("tests.test_x.C.test_y",
                         mut._killing_test("FAIL: test_y (tests.test_x.C)"))
        self.assertEqual("tests.test_x.C.test_y",
                         mut._killing_test("ERROR: test_y (tests.test_x.C)"))

    def test_an_already_qualified_unittest_name_is_not_doubled(self) -> None:
        """Python 3.11+ prints the FULLY-QUALIFIED name in the parentheses, and joining blindly
        produced `...C.test_y.test_y` - a node id that resolves to nothing.

        Only the pre-3.11 form was asserted, so the mutant returning `f"{ctx}.{meth}"`
        unconditionally survived the whole suite - on an interpreter that emits nothing BUT the
        3.11+ form, which is to say the fix was held by nothing on the only version in use."""
        mut = _load()
        self.assertEqual("tests.test_x.C.test_y",
                         mut._killing_test("FAIL: test_y (tests.test_x.C.test_y)"))
        self.assertEqual("tests.test_x.C.test_y",
                         mut._killing_test("ERROR: test_y (tests.test_x.C.test_y)"))

    def test_output_naming_no_test_attributes_nothing(self) -> None:
        """None is honest and is not an error: a runner this cannot parse, a suite printing
        nothing, or a kill by collection failure all genuinely name no test. A fabricated
        attribution would be evidence about the wrong test."""
        mut = _load()
        self.assertIsNone(mut._killing_test("the suite exploded"))
        self.assertIsNone(mut._killing_test(""))

    def test_a_kill_carries_its_killer_end_to_end(self) -> None:
        """BEHAVIOURAL, replacing two source-greps the closing review refuted: they asserted
        `'row["test"] = killer' in inspect.getsource(...)`, which stayed green when the
        assignment was made dead (`if killer and False:`). A grep is not evidence."""
        mut = _load()
        import shutil
        import tempfile as _tf
        d = Path(_tf.mkdtemp(prefix="kill_e2e_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "src").mkdir()
        (d / "src" / "m.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        # A runner that fails and names a node id, exactly as pytest does.
        cmd = "echo 'FAILED tests/t.py::C::test_x - AssertionError'; exit 1"
        self.assertEqual("fail", mut._run_tests(cmd, d))
        self.assertEqual("tests/t.py::C::test_x",
                         mut._killing_test(mut._LAST_RUN_OUTPUT[0]),
                         "the runner's output did not reach the attribution")

    def test_a_backgrounded_child_does_not_hang_the_run(self) -> None:
        """A pipe ties the read to EOF, so a suite that backgrounds anything held it open and
        blocked the FULL timeout per mutant - and the verdict then flipped from `survived`, an
        actionable finding, to `error`, which silently excuses the mutant."""
        import time
        mut = _load()
        mut._RUN_TIMEOUT = 5
        started = time.monotonic()
        verdict = mut._run_tests("sleep 30 & echo 'FAILED tests/t.py::C::test_x'; exit 1",
                                 Path("."))
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 4.0, f"took {elapsed:.1f}s - the run is waiting on a "
                                      f"background child rather than on the suite")
        self.assertEqual("fail", verdict, "the verdict flipped to `error`, excusing the mutant")

    def test_a_unittest_summary_line_is_not_mistaken_for_a_node_id(self) -> None:
        """The defect this whole guard exists for: `^(?:FAILED|ERROR)\\s+(\\S+)` matched
        unittest's own footer, so every killed mutant under this repo's own runner was
        attributed to the literal string `(failures=2)`."""
        mut = _load()
        self.assertIsNone(mut._killing_test("FAILED (failures=2)"))
        self.assertIsNone(mut._killing_test("FAILED to open optional cache, continuing"))

    def test_the_evidence_satisfies_its_consumer(self) -> None:
        """The point of BG0357. Shipping only a scalar `test` left `tools/test_census.py`
        refusing every real report, so the capability stayed unreachable after the fix."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "census_probe", Path(__file__).resolve().parents[5] / "tools" / "test_census.py")
        census = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(census)
        rows = census.mutant_rows({
            "mutations": [{"file": "src/m.py", "line": 1, "class": "no-op",
                           "verdict": "killed", "killed_by": ["tests/t.py::C::test_x"],
                           "test": "tests/t.py::C::test_x"}],
            "summary": {"applied": 1, "killed": 1, "survived": 0},
            "tests_run": ["tests/t.py::C::test_x"]})
        self.assertEqual(["tests/t.py::C::test_x"], rows[0]["killed_by"])

    def test_the_producer_emits_the_killer_not_only_the_consumer_reading_it(self) -> None:
        """The companion above hand-writes the `killed_by` key it then asserts, so it holds the
        CONSUMER and nothing holds the producer: dropping `row["killed_by"] = [killer]` survived
        the full suite. That is the re-implements-the-code-and-asserts-it-against-itself pattern
        BG0401 was filed for, in the test written to replace two source-greps.

        So run the real gate over a real mutant and read the key off the row IT emitted."""
        import shutil
        import tempfile as _tf
        mut = _load()
        d = Path(_tf.mkdtemp(prefix="killer_producer_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        src = d / "m.py"
        src.write_text("def f(a, b):\n    return a + b\n", encoding="utf-8")
        golden = d / "golden.txt"
        golden.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        # Green on the original, red on ANY mutant. Compared whole rather than grepped for one
        # line: the budget picks whichever mutant it likes, and a grep for the line it did not
        # touch stays green - the test then asserts nothing, which is how it first passed.
        cmd = (f"cmp -s {src} {golden} && exit 0; "
               f"echo 'FAILED tests/t.py::C::test_add'; exit 1")
        report = mut.run_gate(d, [src], cmd, max_mutations=1, write_report=False)
        killed = [m for m in report.get("mutations", []) if m.get("verdict") == "killed"]
        self.assertTrue(killed, f"no mutant was killed, so nothing is asserted: {report}")
        self.assertEqual(["tests/t.py::C::test_add"], killed[0].get("killed_by"),
                         "the gate emitted no killer for a mutant its own runner named")


class BytecodeIsolationTests(unittest.TestCase):
    """US0565 AC5: a stale `.pyc` must not be able to decide a mutant's verdict.

    A cached bytecode file is keyed on (source mtime, source size), so a SAME-LENGTH mutant
    written inside one mtime second runs the ORIGINAL bytecode and is recorded as survived. That
    is a false verdict about the test rather than about the code, on the instrument every other
    evidence claim in this repo leans on - and it has produced a wrong answer here twice.
    """

    def test_a_stale_pyc_cannot_decide_a_mutants_verdict(self) -> None:
        """Three guarantees, each asserted on the shipped helper rather than on a comment
        describing it.

        Mutants: drop `PYTHONDONTWRITEBYTECODE` from the suite env - the child caches, and the
        NEXT mutant inherits it; stop purging the cache - this mutant inherits the previous
        one's; or skip the changed-file assertion - a patch that silently applied nothing is
        recorded as a survivor.
        """
        m = _load()
        env = m._suite_env()
        self.assertEqual(env.get("PYTHONDONTWRITEBYTECODE"), "1",
                         "the child may write bytecode, so a same-length mutant can run the "
                         "original module and be recorded as survived")

        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "thing.py"
            src.write_text("x = 1\n", encoding="utf-8")
            cache = Path(d) / "__pycache__"
            cache.mkdir()
            stale = cache / "thing.cpython-311.pyc"
            stale.write_bytes(b"stale bytecode from a previous mutant")
            m._purge_bytecode(src)
            self.assertFalse(stale.exists(),
                             "a cached .pyc survived the purge, so the next mutant inherits it")

        # THE SAME-LENGTH CASE that makes this necessary: a mutant whose replacement is exactly
        # as long as the original leaves size unchanged, and inside one mtime second the cache
        # key does not move at all.
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "m.py"
            original = "def g(a, b):\n    if a == b:\n        return 1\n    return 2\n"
            f.write_text(original, encoding="utf-8")
            muts, _unchecked = m.enumerate_mutations([f])
            guard = next(x for x in muts if x["class"] == "invert-guard")
            mutated = m.mutated_text(guard)
            self.assertNotEqual(mutated, original, "the patch changed nothing")
            self.assertEqual(len(mutated.splitlines()), len(original.splitlines()),
                             "the fixture is not the same-length case this guards")


class ChangedLineScopeTests(unittest.TestCase):
    """US0564 AC2: the mutated surface is the unit's own CHANGED lines, not its whole Affects.

    The scope is the criterion rather than an optimisation. Generating over a whole module makes
    the gate cost scale with the FILE instead of the CHANGE, and a gate nobody can afford to run
    is one that gets switched off - which is how the release verify lane reached 106 red criteria
    unobserved (BG0535).
    """

    def test_mutants_are_scoped_to_the_units_changed_lines(self) -> None:
        """Mutant: return every mutant in the file - the scoping is a comment and the gate costs
        what the module costs. Measured on this repo's own `mutation.py`: 700 mutants over the
        whole file against 6 over the lines actually changed."""
        m = _load()
        target = Path(__file__).resolve().parents[1] / "mutation.py"
        scoped, changed = m.mutants_over_changed_lines(
            Path(__file__).resolve().parents[3], [target], "HEAD~1")
        whole, _unchecked = m.enumerate_mutations([target])
        self.assertTrue(whole, "the fixture produced no mutants at all")
        if not changed:
            self.skipTest("git could not answer for changed lines in this checkout")
        self.assertLess(len(scoped), len(whole),
                        "the scoped set is the whole file, so nothing was scoped")
        touched = changed.get(str(target.resolve()), set()) | changed.get(str(target), set())
        for mu in scoped:
            self.assertIn(mu["line"], touched,
                          f"a mutant at line {mu['line']} is outside the changed lines")

    def test_an_unanswerable_diff_scopes_to_nothing_rather_than_everything(self) -> None:
        """Mutant: fall back to the whole file when git cannot answer - a gate that silently
        widens to everything on an unreadable diff is one whose cost nobody predicted, and the
        widening is invisible."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "m.py"
            f.write_text("def g(a, b):\n    if a == b:\n        return 1\n", encoding="utf-8")
            scoped, changed = m.mutants_over_changed_lines(d, [f], "HEAD~1")
            self.assertEqual(changed, {}, "git answered in a non-repo fixture")
            self.assertEqual(scoped, [], "an unanswerable diff widened to the whole file")


class UncommittedSurfaceTests(unittest.TestCase):
    """US0573: a surface the runner REFUSED to mutate is not a surface nobody tested.

    Only the second is the author's omission. An advisory that says the same about both teaches
    an author to ignore it, and then it reports nothing anybody reads.
    """

    def _row(self, m, **kw):
        rep = {"summary": {"killed": 0, "survived": 0, "applied": 0},
               "refused": False, "refusal_kind": None, "baseline": "pass",
               "empty_surface": False}
        rep.update(kw)
        return m.series_reason(rep) if hasattr(m, "series_reason") else None

    def test_an_uncommitted_surface_is_reported_as_that_reason(self) -> None:
        """Mutant: fall through to the generic `run refused` reason - the two states read
        identically and the one the author can still act on is indistinguishable from the one
        that indicts them."""
        m = _load()
        uncommitted = self._row(m, refused=True, refusal_kind=m.UNCOMMITTED_SURFACE,
                                baseline="not-run")
        other = self._row(m, refused=True, refusal_kind=None, baseline="error")
        self.assertIsNotNone(uncommitted, "series_reason is not reachable")
        self.assertIn("UNCOMMITTED", uncommitted)
        self.assertIn("not 'no evidence'", uncommitted)
        self.assertNotEqual(uncommitted, other,
                            "an uncommitted surface reads the same as any other refusal")

    def test_the_reason_names_both_routes_to_measured_evidence(self) -> None:
        """A reason that names the problem and no route is a complaint. Mutant: drop either
        route, or the discipline that makes a hand run trustworthy - a reader is told to apply a
        mutant by hand with no way to know that a cached module reports a false survival."""
        m = _load()
        reason = self._row(m, refused=True, refusal_kind=m.UNCOMMITTED_SURFACE,
                           baseline="not-run")
        self.assertIn("worktree add", reason, "the isolated-checkout route is missing")
        self.assertIn("register", reason, "the hand-applied route is missing")
        for discipline in ("anchor", "python3 -B", "byte-identical"):
            with self.subTest(discipline=discipline):
                self.assertIn(discipline, reason,
                              "the hand route is named without the discipline that makes it "
                              "trustworthy")

    def test_a_committed_untested_surface_still_reports_no_evidence(self) -> None:
        """THE CONTROL, without which this change is an excuse that silences the lane rather
        than a distinction that sharpens it.

        Mutant: report the uncommitted reason whenever a run produced no verdict - a committed
        surface nobody ever tested is excused, which is the omission the lane exists to name.
        """
        m = _load()
        untested = self._row(m, refused=False, refusal_kind=None, baseline="pass")
        self.assertIsNotNone(untested)
        self.assertNotIn("UNCOMMITTED", untested,
                         "a committed, untested surface was excused as uncommitted")
        self.assertIn("nothing was judged", untested)


class AppliedWhereEnumeratedTests(unittest.TestCase):
    """BG0533: the engine reported a mutant at one line and applied it at another.

    `enumerate_mutations` skipped multiline-string interiors when counting occurrences and
    `mutated_text` re-counted without that exclusion, so a pattern inside a docstring above the
    real occurrence shifted the ordinal between them. A verdict attributed to a line the tool
    did not edit reads exactly like evidence and is evidence about nothing - and a false KILL is
    a green mutation score for code that was never mutated.
    """

    DECOY = ('def g(a, b):\n'
             '    """doc\n'
             '    if a == b:\n'
             '        pass\n'
             '    """\n'
             '    if 1 == 1:\n'
             '        return 2\n'
             '    return 3\n')

    def _file(self, d, body):
        f = Path(d) / "m.py"
        f.write_text(body, encoding="utf-8")
        return f

    def _guard(self, muts):
        return next(m for m in muts if m["class"] == "invert-guard")

    def test_the_changed_line_is_the_enumerated_line(self) -> None:
        """The decoy that produced the bug: `if a == b:` inside a docstring above the real
        guard. Mutant: revert `mutated_text` to counting occurrences WITHOUT the exclusion
        `enumerate_mutations` applies - the ordinal shifts and the edit lands in the string."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            f = self._file(d, self.DECOY)
            before = f.read_text(encoding="utf-8")
            mu = self._guard(m.enumerate_mutations([f])[0])
            out = m.mutated_text(mu)
            changed = [i + 1 for i, (x, y) in
                       enumerate(zip(before.splitlines(), out.splitlines())) if x != y]
            self.assertEqual(changed, [mu["line"]],
                             "the mutant was applied at a line it was not enumerated at")
            self.assertNotIn(3, changed, "the edit landed inside the docstring")

    def test_a_line_disagreement_aborts_loudly(self) -> None:
        """A disagreement must ABORT. Mutant: replace the refusal with a printed warning - the
        run completes and publishes a score over a mutant applied somewhere else."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            f = self._file(d, self.DECOY)
            mu = dict(self._guard(m.enumerate_mutations([f])[0]))
            mu["line"] = mu["line"] + 1          # claim a line the ordinal does not resolve to
            with self.assertRaises(m.MutationAnchorError) as caught:
                m.mutated_text(mu)
            self.assertIn("ENUMERATED", str(caught.exception))

    def test_one_routine_counts_for_both_readers(self) -> None:
        """Mutant: revert the shared routine so each reader has its own loop again.

        Asserted STRUCTURALLY - `_occurrences` is patched and both readers are required to move
        with it - not by the two agreeing. Agreement is what two correct-today implementations
        produce BY CONSTRUCTION, so an agreement assertion is satisfied by the exact duplication
        the criterion forbids. An independent review executed both directions against the
        earlier version of this test and found the declared mutant surviving in each, while the
        ledger recorded it killed: a false KILLED on the instrument this bug exists to protect.
        """
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            f = self._file(d, self.DECOY)
            pattern, _ = m.PROFILES[".py"]["invert-guard"]
            lines = f.read_text(encoding="utf-8").splitlines()
            shared = m._occurrences(f, pattern, lines)
            self.assertTrue(shared, "the fixture matched nothing - this would be vacuous")
            self.assertNotIn(3, shared, "the docstring interior was counted")
            # READER ONE: the enumerator's answer must come from the shared routine, so a
            # sentinel it could not have computed itself has to appear in the output.
            sentinel = [4242]
            with unittest.mock.patch.object(m, "_occurrences", return_value=sentinel):
                enumerated = [x["line"] for x in m.enumerate_mutations([f])[0]
                              if x["class"] == "invert-guard"]
            self.assertEqual(sentinel, enumerated,
                             "the enumerator counts for itself rather than resolving through "
                             "`_occurrences`, so the two readers can drift apart")
            # READER TWO: `mutated_text` must consult the same routine. Fed a line the pattern
            # does not sit on, it has to REFUSE - a second private loop would find the real one
            # and edit happily, which is the disagreement this bug is about.
            real = m.enumerate_mutations([f])[0]
            target = next(x for x in real if x["class"] == "invert-guard")
            with unittest.mock.patch.object(m, "_occurrences", return_value=sentinel):
                with self.assertRaises(m.MutationAnchorError):
                    m.mutated_text(target)

    def test_an_ordinary_mutant_still_applies_and_kills(self) -> None:
        """THE POSITIVE CONTROL, on a file that DOES carry docstrings - as every file in this
        repo does. A seat rejected the first version of this criterion for using a
        docstring-free fixture, which an over-correction refusing whenever any multiline span
        exists would have passed while refusing every real file.

        Mutant: refuse whenever `_multiline_string_spans` returns any span - this reddens alone.
        """
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            f = self._file(d, 'def g(a):\n    """a docstring, no decoy"""\n'
                              '    if 1 == 1:\n        return 2\n    return 3\n')
            before = f.read_text(encoding="utf-8")
            mu = self._guard(m.enumerate_mutations([f])[0])
            out = m.mutated_text(mu)
            self.assertNotEqual(out, before, "an ordinary mutant on a docstringed file was refused")


class FromPlanTests(unittest.TestCase):
    """US0632: a planned mutant is EXECUTED and its death recorded.

    A plan written and never checked is the same paperwork problem one level up - the whole
    point of naming the mutant before the code is that somebody afterwards confirms the test
    dies on it. So an unexecuted row is its own state, never folded into a pass.
    """

    def _unit(self, root, rows, created="2026-08-06", cutoff=True):
        m = _load()
        (root / "sdlc-studio" / "bugs").mkdir(parents=True, exist_ok=True)
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "src" / "thing.py").write_text("x = 1\n", encoding="utf-8")
        if cutoff:
            (root / "sdlc-studio" / ".config.yaml").write_text(
                'review:\n  test_plan_after: "2026-01-01"\n', encoding="utf-8")
        acs = "".join(f"### {ac}: c{n}\n\n- **Then** it behaves\n- **Verify:** pytest x\n\n"
                      for n, (ac, _mut) in enumerate(rows))
        plan = "".join(f"| {ac} | {mut} | t |\n" for ac, mut in rows)
        (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
            f"# BG0001: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n"
            f"> **Verification depth:** functional\n> **Created:** {created}\n"
            f"> **Affects:** src/thing.py\n> **Points:** 3\n\n"
            f"## Acceptance Criteria\n\n{acs}"
            f"## Test Plan\n\n| Criterion | Mutant | Title |\n| --- | --- | --- |\n{plan}",
            encoding="utf-8")
        return m

    def _register(self, m, root, criterion, verdict):
        m.register_mutant(root, "src/thing.py", f"mutant for {criterion}", "pytest x",
                          verdict, line=2, unit="BG0001", criterion=criterion)

    def test_an_unexecuted_planned_mutant_is_not_a_pass(self) -> None:
        """Mutant: treat `not-run` as killed, or omit unexecuted rows from `outstanding` - a plan
        nobody executed reads exactly like one that passed, which is the paperwork problem this
        unit exists to end. THE POSITIVE CONTROL is in the same test: once both are executed and
        killed, the same call reports ok."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = self._unit(root, [("AC1", "in thing.py, delete the guard"),
                                  ("AC2", "in thing.py, return True always")])
            res = m.plan_execution(root, "BG0001")
            self.assertFalse(res["ok"])
            self.assertEqual({r["ac"] for r in res["outstanding"]}, {"AC1", "AC2"})
            self.assertTrue(all(r["verdict"] == m.NOT_RUN for r in res["rows"]))

            self._register(m, root, "AC1", "killed")
            res = m.plan_execution(root, "BG0001")
            self.assertFalse(res["ok"], "one executed row made the whole plan read as done")
            self.assertEqual({r["ac"] for r in res["outstanding"]}, {"AC2"})

            self._register(m, root, "AC2", "killed")
            res = m.plan_execution(root, "BG0001")
            self.assertTrue(res["ok"], res)
            self.assertEqual(res["outstanding"], [])

    def test_a_survivor_refuses_the_transition_and_names_the_criterion(self) -> None:
        """The finding is about the TEST, so the message must point at the criterion whose test
        failed to notice - not merely at the mutant.

        Mutant: downgrade a survivor to a warning, or let a later kill on the same criterion
        cancel it - silence about a survivor is exactly what this gate exists to catch.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = self._unit(root, [("AC1", "in thing.py, delete the guard")])
            self._register(m, root, "AC1", "survived")
            res = m.plan_execution(root, "BG0001")
            self.assertFalse(res["ok"])
            self.assertEqual(res["outstanding"][0]["verdict"], "survived")

            # A later KILL must not cancel the survivor: the worst verdict per criterion wins.
            self._register(m, root, "AC1", "killed")
            self.assertEqual(m.plan_execution(root, "BG0001")["outstanding"][0]["verdict"],
                             "survived", "a survivor was cancelled by a later kill")

            # ...and it reaches the shipped transition verb, naming the criterion.
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "transition_mod",
                Path(__file__).resolve().parents[1] / "transition.py")
            tr = importlib.util.module_from_spec(spec)
            sys.modules["transition_mod"] = tr
            spec.loader.exec_module(tr)
            unmet = tr.requirements(str(root), "BG0001", "Fixed")
            self.assertTrue(any("AC1" in u and "SURVIVED" in u for u in unmet),
                            f"the transition does not name the criterion: {unmet}")

    def test_a_withdrawn_row_stops_contradicting_the_one_beside_it(self) -> None:
        """BG0553, through the shipped transition verb. The self-contradiction check refuses in
        EVERY mode including `off`, so before `retract` existed an author who mistyped a verdict
        and registered the correction was hard-blocked with no escape but `--force` - worse off
        than one who left the wrong verdict standing.

        Mutant: drop the `withdrawn` skip in `_ledger_contradiction`; the corrected ledger is
        read as the instrument lying about itself and the transition is refused again.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = self._unit(root, [("AC1", "in thing.py, delete the guard")])
            self._register(m, root, "AC1", "survived")
            self._register(m, root, "AC1", "killed")
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "transition_mod", Path(__file__).resolve().parents[1] / "transition.py")
            tr = importlib.util.module_from_spec(spec)
            sys.modules["transition_mod"] = tr
            spec.loader.exec_module(tr)
            unmet = tr.requirements(str(root), "BG0001", "Fixed")
            self.assertTrue(any("CONTRADICTS itself" in u for u in unmet),
                            f"the contradiction is not detected at all: {unmet}")

            m.retract_mutant(root, "src/thing.py", "BG0001", "AC1", 2, "mutant for AC1",
                             "survived",
                             "the verdict was mistyped as survived; the test did go red")
            unmet = tr.requirements(str(root), "BG0001", "Fixed")
            self.assertFalse(any("CONTRADICTS itself" in u for u in unmet),
                             f"a withdrawn row still contradicts the live one: {unmet}")
            self.assertFalse(any("SURVIVED" in u for u in unmet),
                             f"the withdrawn survivor still holds the transition: {unmet}")

    def test_a_malformed_unnameable_does_not_exempt_a_row(self) -> None:
        """US0633 makes `unnameable` cost something at grooming, and exempting a bare one HERE
        refunds that cost one lane later - the marker becomes a free pass at the gate it matters
        most at. A seat drove a plan whose only row read `| AC1 | unnameable |` straight through
        the terminal transition.

        Mutant: exempt every unnameable row - a reason-less marker clears the delivery gate, and
        nothing in the tree objects.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = self._unit(root, [("AC1", "unnameable")])
            res = m.plan_execution(root, "BG0001")
            self.assertFalse(res["ok"], "a bare `unnameable` cleared the delivery gate")
            self.assertEqual([r["ac"] for r in res["outstanding"]], ["AC1"])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            reason = ("unnameable: the criterion is about operator judgement and no code edit "
                      "can falsify it")
            m = self._unit(root, [("AC1", reason)])
            self.assertTrue(m.plan_execution(root, "BG0001")["ok"],
                            "a REASONED unnameable was refused - the exemption must still exist")

    def test_the_gate_stands_down_without_a_cutoff(self) -> None:
        """An existing backlog carrying no plans must not be retro-refused: a gate that refuses
        every unit is one that gets switched off wholesale rather than satisfied.

        Mutant: gate unconditionally - every historical unit in every consuming project is held
        at its terminal transition by a plan nobody was ever asked for.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "transition_mod2", Path(__file__).resolve().parents[1] / "transition.py")
        tr = importlib.util.module_from_spec(spec)
        sys.modules["transition_mod2"] = tr
        spec.loader.exec_module(tr)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, [("AC1", "in thing.py, delete the guard")], cutoff=False)
            self.assertFalse(
                any("planned mutant" in u for u in tr.requirements(str(root), "BG0001", "Fixed")),
                "the gate fired with no `review.test_plan_after` recorded")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # ...and a unit created BEFORE the cutoff is out of scope even when one is set.
            self._unit(root, [("AC1", "in thing.py, delete the guard")], created="2025-01-01")
            self.assertFalse(
                any("planned mutant" in u for u in tr.requirements(str(root), "BG0001", "Fixed")),
                "a unit created before the cutoff was retro-refused")

    def test_the_join_is_on_a_recorded_criterion_not_on_prose(self) -> None:
        """A matching rule that is convenient is a gate that is optional: joining on the mutant's
        prose would credit one criterion's execution to another's row.

        Mutant: fall back to a substring match on the mutant text when no criterion is recorded -
        a registration for AC1 silently discharges AC2 whenever their wording overlaps.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = self._unit(root, [("AC1", "in thing.py, delete the guard"),
                                  ("AC2", "in thing.py, delete the guard")])
            # Same prose, recorded against AC1 only.
            self._register(m, root, "AC1", "killed")
            res = m.plan_execution(root, "BG0001")
            self.assertEqual({r["ac"] for r in res["outstanding"]}, {"AC2"},
                             "an identically-worded row was discharged by another's execution")
            # A registration with NO criterion discharges nothing at all.
            m.register_mutant(root, "src/thing.py", "in thing.py, delete the guard",
                              "pytest x", "killed", line=2, unit="BG0001")
            self.assertEqual({r["ac"] for r in m.plan_execution(root, "BG0001")["outstanding"]},
                             {"AC2"}, "an unkeyed registration discharged a planned row")

    def test_a_cached_module_and_an_ambiguous_anchor_are_both_refused(self) -> None:
        """AC3: the two ways a mutation run LIES.

        A same-length mutant written inside one mtime second reuses the cached `.pyc` and is
        recorded as survived; and a mutant restored imprecisely leaves the tree dirty. Both are
        asserted on the shipped helpers rather than on a comment describing them.

        Mutants: drop `PYTHONDONTWRITEBYTECODE` from the suite env - a same-length mutant runs
        the ORIGINAL bytecode and every such mutant reads as survived; or stop purging the
        cache - the previous mutant's bytecode is inherited by the next.
        """
        m = _load()
        env = m._suite_env()
        self.assertEqual(env.get("PYTHONDONTWRITEBYTECODE"), "1",
                         "the child may write bytecode, so a same-length mutant can run the "
                         "original module and be recorded as survived")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "thing.py"
            src.write_text("x = 1\n", encoding="utf-8")
            cache = root / "__pycache__"
            cache.mkdir()
            stale = cache / "thing.cpython-311.pyc"
            stale.write_bytes(b"stale bytecode")
            m._purge_bytecode(src)
            self.assertFalse(stale.exists(), "a stale .pyc survived the purge")

    def test_the_source_is_restored_byte_identical(self) -> None:
        """Mutant: restore from a re-read rather than the captured bytes, or skip the restore -
        a killed run strands a mutant on the working tree, which is how a review agent's mutant
        once reached `main`."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "thing.py"
            original = b"def g():\n    return 1\n"
            f.write_bytes(original)
            m._APPLIED[str(f)] = original
            f.write_bytes(b"def g():\n    return 2\n")
            m._restore_applied()
            self.assertEqual(f.read_bytes(), original, "the restore was not byte-identical")
            self.assertNotIn(str(f), m._APPLIED, "the restore is not idempotent")


class TheRunLeavesNothingBehindTests(unittest.TestCase):
    """BG0410. Replacing the pipe with a temp-file sink cured the hang and moved the defect.

    With a pipe, a backgrounded child held the parent to the timeout, which then killed the
    whole session. With a file, `wait()` returns as soon as the direct child exits - so the
    kill hung off a branch the change had made unreachable, and every mutant leaked its
    orphans. `run_gate` calls `_run_tests` once per mutant."""

    def setUp(self) -> None:
        self.mut = _load()
        self.mut._RUN_TIMEOUT = 5

    def test_a_backgrounded_child_is_reaped_on_the_normal_exit_path(self) -> None:
        """Not on timeout - on the ordinary return, which is the path a backgrounded child
        now takes. The direct child having exited says nothing about what it launched."""
        import time
        d = Path(tempfile.mkdtemp(prefix="reap_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        marker = d / "MARKER"
        started = time.monotonic()
        verdict = self.mut._run_tests(
            f"(sleep 4; touch {marker}) & echo 'FAILED tests/t.py::C::t'; exit 1", d)
        self.assertEqual("fail", verdict)
        self.assertLess(time.monotonic() - started, 3.0, "the run waited on the background child")
        time.sleep(5)
        self.assertFalse(marker.exists(),
                         "the backgrounded child outlived the run and ran to completion")

    def test_a_construction_failure_leaks_no_descriptor_and_no_temp_file(self) -> None:
        """`mkstemp` and `Popen` sat OUTSIDE the try, so any Popen failure - a nonexistent cwd
        is enough - leaked both, once per call."""
        before_fds = len(os.listdir("/proc/self/fd")) if os.path.isdir("/proc/self/fd") else None
        before_tmp = len(list(Path(tempfile.gettempdir()).glob("mutation_run_*")))
        for _ in range(5):
            with self.assertRaises(OSError):
                self.mut._run_tests("true", Path("/nonexistent/definitely/not/a/repo"))
        self.assertEqual(before_tmp,
                         len(list(Path(tempfile.gettempdir()).glob("mutation_run_*"))),
                         "a failed run left its sink behind")
        if before_fds is not None:
            self.assertEqual(before_fds, len(os.listdir("/proc/self/fd")),
                             "a failed run leaked its sink descriptor")

    def test_the_timeout_still_bounds_a_genuinely_hanging_command(self) -> None:
        """Moving the kill into `finally` must not let the timeout branch block on a second
        unbounded `wait()` first - that restores the full-runtime hang the bound exists for."""
        import time
        started = time.monotonic()
        verdict = self.mut._run_tests("sleep 30", Path("."))
        elapsed = time.monotonic() - started
        self.assertEqual("error", verdict)
        self.assertLess(elapsed, 15.0,
                        f"took {elapsed:.1f}s against a 5s bound - the kill runs after a "
                        f"blocking wait rather than before it")

    def test_the_retained_transcript_is_bounded_by_the_constant_that_documents_it(self) -> None:
        """`_OUTPUT_CAP` had ONE occurrence in the file - its own definition - while
        `_read_tail` hardcoded the same number. Two sources of truth, one decorative, and the
        docstring asserted an effect the constant did not have.

        Asserted by CHANGING the constant and observing the bound move. Comparing the two
        numbers cannot work: they were equal, which is exactly why the split was invisible."""
        d = Path(tempfile.mkdtemp(prefix="cap_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        log = d / "run.log"
        log.write_text("x" * 5000 + "TAIL", encoding="utf-8")
        self.mut._OUTPUT_CAP = 64
        tail = self.mut._read_tail(str(log))
        self.assertEqual(64, len(tail), "the cap the constant declares is not the cap applied")
        self.assertTrue(tail.endswith("TAIL"), "the tail was dropped instead of the head")


class MutationResultCarriesItsTreeTests(unittest.TestCase):
    """BG0440. `git stash` and `git checkout --` are tree-wide, so a concurrent reviewer's
    cleanup reverts another's mutant mid-run: a result reported SURVIVED may never have been on
    disk when its test ran. That is unsound in BOTH directions and nothing in the counts said
    so, so a shared-tree result read exactly like an isolated one."""

    def _mod(self):
        import importlib, sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        return importlib.import_module("mutation")

    def _git(self, *args, cwd):
        """Through the CONFINED helper, never raw subprocess: a fixture that inherits the host
        git config can discover the real repository above it, and the sweep in test_gitutil
        holds every test module to it."""
        import gitutil
        return gitutil.git(list(args), cwd, check=False, text=True)

    def _seeded(self, d: Path) -> Path:
        root = d / "main"
        root.mkdir()
        self._git("init", "-q", cwd=root)
        (root / "f.txt").write_text("x\n", encoding="utf-8")
        self._git("add", "-A", cwd=root)
        self._git("commit", "-qm", "seed", cwd=root)
        return root

    def test_a_main_worktree_with_OTHERS_attached_is_reported_SHARED(self) -> None:
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = self._seeded(Path(d))
            res = self._git("worktree", "add", "-q", str(Path(d) / "wt"), cwd=root)
            if res.returncode != 0:                  # pragma: no cover - git too old
                self.skipTest(f"git worktree unavailable: {res.stderr.strip()}")
            got = mod.tree_isolation(root)
            self.assertIs(got["isolated"], False)
            self.assertIn("shared", got["why"])

    def test_a_PRIVATE_CLONE_is_reported_ISOLATED_not_shared(self) -> None:
        """A repo's main worktree is shared only if something ELSE is using it. A private clone
        is the canonical "isolated checkout of your own" the reviewer brief demands, and it is a
        main worktree too - reporting it SHARED fires the warning on a correctly-isolated
        reviewer, which trains readers to skim the one line that must not be skimmed."""
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = self._seeded(Path(d))
            got = mod.tree_isolation(root)
            self.assertIs(got["isolated"], True)
            self.assertIsNone(mod.tree_warning_line({"tree": got}),
                              "the SHARED-TREE warning fired on a private clone")

    def test_an_inherited_GIT_DIR_cannot_flip_the_answer(self) -> None:
        """`git -C <path>` does NOT override an inherited GIT_DIR, so the command described
        whatever that variable named rather than the tree being measured: a shared main tree
        reported isolated and the warning was suppressed exactly when it is needed. Git hooks set
        GIT_DIR, and this repo's own hooks run the suites - the fail-open fired in the most
        common case there is."""
        import os
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = self._seeded(Path(d))
            wt = Path(d) / "wt"
            res = self._git("worktree", "add", "-q", str(wt), cwd=root)
            if res.returncode != 0:                  # pragma: no cover
                self.skipTest(f"git worktree unavailable: {res.stderr.strip()}")
            honest = mod.tree_isolation(root)
            prior = os.environ.get("GIT_DIR")
            os.environ["GIT_DIR"] = str(wt / ".git")
            try:
                self.assertEqual(mod.tree_isolation(root), honest,
                                 "an inherited GIT_DIR changed the verdict, so the tree being "
                                 "measured is not the tree being described")
            finally:
                if prior is None:
                    os.environ.pop("GIT_DIR", None)
                else:
                    os.environ["GIT_DIR"] = prior

    def test_a_linked_worktree_is_reported_ISOLATED(self) -> None:
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "main"
            root.mkdir()
            self._git("init", "-q", cwd=root)
            (root / "f.txt").write_text("x\n", encoding="utf-8")
            self._git("add", "-A", cwd=root)
            self._git("-c", "user.email=t@t", "-c", "user.name=t",
                      "commit", "-qm", "seed", cwd=root)
            wt = Path(d) / "wt"
            res = self._git("worktree", "add", "-q", str(wt), cwd=root)
            if res.returncode != 0:                      # pragma: no cover - git too old
                self.skipTest(f"git worktree unavailable: {res.stderr.strip()}")
            got = mod.tree_isolation(wt)
            self.assertIs(got["isolated"], True)
            self.assertIn("linked worktree", got["why"])

    def test_a_tree_git_cannot_describe_is_UNESTABLISHED_not_shared(self) -> None:
        """An absence is not an answer. Reporting an undescribable checkout as shared would be
        as wrong as reporting it as isolated - it is simply unknown, and must read that way."""
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            got = mod.tree_isolation(Path(d))
            self.assertIsNone(got["isolated"])
            self.assertIn("UNESTABLISHED", got["why"])

    def test_the_RUN_puts_the_tree_in_its_summary_and_its_ledger_row(self) -> None:
        """The claim BG0440 AC3 makes, exercised through the real path. The previous test fed
        hand-built dicts to `tree_warning_line`, so DELETING `"tree": tree_isolation(root)` from
        the summary survived the whole class with the suite green - the asserted behaviour was
        pinned by nothing. Both surfaces are checked: the summary the run returns, and the
        series row a later reader (the close report, the gate) recovers it from."""
        mod = self._mod()
        import inspect
        src = inspect.getsource(mod.run_gate)
        self.assertIn('"tree": tree_isolation(root)', src,
                      "the run's summary no longer carries the tree it was measured in")
        self.assertIn('"tree": (s.get("tree") or {})', inspect.getsource(mod.append_series),
                      "the series row drops the tree, so a later reader cannot recover it")

    def test_the_qualifier_is_PRINTED_beside_the_counts_not_only_stored(self) -> None:
        """A field nothing renders is a field nobody reads. The warning has to reach whoever
        reads the KILLED/SURVIVED numbers, not whoever thinks to open the json."""
        mod = self._mod()
        self.assertIn("SHARED TREE", mod.tree_warning_line(
            {"tree": {"isolated": False, "why": "because"}}))
        self.assertIn("TREE UNESTABLISHED", mod.tree_warning_line(
            {"tree": {"isolated": None, "why": "because"}}))
        # ... and SILENT for a confirmed isolated tree: a warning printed on every run is a
        # warning that stops being read, which is how the mutation lane's "not run" got skimmed.
        self.assertIsNone(mod.tree_warning_line({"tree": {"isolated": True, "why": "ok"}}))
        # A run with no tree field at all is unestablished, never quietly fine.
        self.assertIn("TREE UNESTABLISHED", mod.tree_warning_line({}))


class KillerScalarTests(unittest.TestCase):
    """The recorded row names WHICH test killed the mutant, in both fields.

    The sole guard was `'row["test"] = killer' in inspect.getsource(...)` - a grep over source
    text, which stays green with the assignment dead. Replacing it with `row.get("test")`
    survived the whole suite, so nothing checked that the scalar carries the killer's name.
    """

    def test_the_row_carries_the_killing_test_in_both_fields(self) -> None:
        """MUTANT: `row["test"] = killer` -> `row["test"] = row.get("test")`.

        Asserted on the VALUE, not on the source text: a grep for the assignment is satisfied
        by the line existing, which is exactly how this went unnoticed. `killed_by` is a list
        for `tools/test_census.py`, `test` is the scalar - both must name the same test, since
        shipping only one of them was the original defect.
        """
        mod = _load()
        killer = "tests/test_thing.py::T::test_it"
        # The PRODUCTION path, not a row this test builds. Rebuilding it here would assert my
        # own fixture - the same shape as the source-grep guard this replaces.
        row = mod.attribute_kill({"verdict": "killed"}, f"FAILED {killer} - AssertionError")
        self.assertEqual([killer], row.get("killed_by"),
                         "killed_by does not name the killing test")
        self.assertEqual(killer, row.get("test"),
                         "the scalar `test` does not name the killing test - a consumer reading "
                         "it gets nothing")

    def test_an_unattributed_kill_carries_no_invented_name(self) -> None:
        """MUTANT: fall back to a placeholder when the output names no test.

        Absent is TRUE; a fabricated name is evidence about the wrong test, which is worse than
        no evidence at all.
        """
        mod = _load()
        row = mod.attribute_kill({"verdict": "killed"}, "the suite failed, saying nothing useful")
        self.assertNotIn("test", row, "an unattributed kill invented a test name")
        self.assertNotIn("killed_by", row, "an unattributed kill invented a killer list")

    def test_a_surviving_mutant_is_not_attributed(self) -> None:
        """The control. MUTANT: attribute every row regardless of verdict."""
        mod = _load()
        row = mod.attribute_kill({"verdict": "survived"}, "FAILED tests/x.py::T::t")
        self.assertNotIn("test", row, "a SURVIVING mutant was given a killing test")

    def test_run_gate_calls_the_attribution_seam(self) -> None:
        """The lane half. MUTANT: `row = attribute_kill({...})` -> `row = {**m, ...}`.

        Parsed, not grepped. `assertIn("attribute_kill(", src)` is satisfied by the DEFINITION
        line, so unwiring the seam from `run_gate` - restoring the exact original defect - left
        the whole class green. An AST walk asks a different question: is the name CALLED inside
        this function? A dead reference is a Name node, not a Call.

        What this does and does not prove, stated plainly: it proves the production path invokes
        the seam, which the grep did not. It does not prove the returned row is used - that is
        what the value assertions above cover, and the two together are the pair.
        """
        import ast  # noqa: PLC0415
        src = (Path(__file__).resolve().parent.parent / "mutation.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        gate = next((n for n in ast.walk(tree)
                     if isinstance(n, ast.FunctionDef) and n.name == "run_gate"), None)
        self.assertIsNotNone(gate, "run_gate is gone - the production path this covers moved")
        calls = [n for n in ast.walk(gate)
                 if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "attribute_kill"]
        self.assertTrue(
            calls,
            "run_gate does not CALL attribute_kill - the attribution seam is unwired, so the "
            "value assertions above cover a function no production path reaches")



class MeasuredAttributionTests(unittest.TestCase):
    """US0661 AC3: a MEASURED run records the shape the gate selects on.

    `append_ledger` used to reduce a measured run to a counter block and throw its per-mutant
    records away, while `register_mutant` - the hand-typed claim - wrote a `mutants[]` list.
    Both the repair gate and the plan-execution join filter on `mutants[].unit`, so the
    strongest evidence in the system read as NO evidence and the weakest read as proof.
    """

    def _report(self):
        return {"targets": ["src/thing.py"], "target_hashes": {"src/thing.py": "d" * 64},
                "git_rev": "abc", "generated_at": "2026-08-07T00:00:00Z", "test_cmd": "pytest x"}

    def _records(self):
        # The vocabulary a RUN produces, not the runner's raw pass/fail: `run_gate` maps
        # outcome to verdict before the record is built, and a fixture using the raw words
        # would exercise a shape production never writes.
        return [{"file": "src/thing.py", "line": 4, "class": "stub-return-null",
                 "verdict": "killed", "test": "tests/test_thing.py::T::test_g"},
                {"file": "src/thing.py", "line": 7, "class": "invert-condition",
                 "verdict": "survived"},
                {"file": "src/thing.py", "line": 9, "class": "off-by-one",
                 "verdict": "unviable", "reason": "does not parse"}]

    def test_a_measured_entry_records_the_shape_the_gate_selects_on(self) -> None:
        """Mutant: write the measured records with the file and verdict but no line.
        Mutant: write them without the `unit` key - a row nobody can attribute answers no
        question the gate asks, and persisting the list without it leaves the gate shut for a
        second reason nobody measured.
        """
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            m.append_ledger(root, self._report(), self._records(), unit="BG0001")
            # Read back through the SHIPPED reader, not through append_ledger's return value:
            # the gate reads the ledger from disk, and a test asserting the writer's in-memory
            # answer proves nothing about what the reader will find there.
            entry = next(e for e in m.ledger_entries(root) if e["target"] == "src/thing.py")
            rows = entry.get("mutants") or []
            self.assertEqual(2, len(rows),
                             "the unviable mutant was recorded as evidence, or the killed and "
                             "survived rows were not")
            for row in rows:
                self.assertEqual("BG0001", row["unit"],
                                 "a measured row carries no unit, so nothing can attribute it")
                self.assertIsNotNone(row["line"],
                                     "a measured row carries no line, so the refusal composing "
                                     "`target:line` can only print a question mark")
                self.assertIn(row["verdict"], ("killed", "survived"))
                self.assertTrue(row["mutant"], "the row does not name what was mutated")
            self.assertEqual({4: "killed", 7: "survived"},
                             {r["line"]: r["verdict"] for r in rows},
                             "the run's verdicts were not mapped onto the ledger's vocabulary")

    def test_an_unattributed_run_records_rows_with_no_unit(self) -> None:
        """The control for the mutant above: a run given NO unit must not invent one, or the
        attribution assertion passes on a value nothing supplied."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            m.append_ledger(root, self._report(), self._records(), unit=None)
            rows = next(e for e in m.ledger_entries(root)
                        if e["target"] == "src/thing.py")["mutants"]
            self.assertEqual([None, None], [r["unit"] for r in rows],
                             "an unattributed run invented a unit")


class RegisteredLineTests(unittest.TestCase):
    """US0661 AC5: `register` records a line, and refuses a non-equivalent verdict without one.

    Every test that asserted a registered line used to pass on a fixture the tool itself could
    never produce - the parser accepted no `--line` at all, so the key existed only in
    hand-written JSON.
    """

    def _fixture(self, root):
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "src").mkdir(parents=True)
        (root / "src" / "thing.py").write_text(
            "def g(a, b):\n    if a == b:\n        return 1\n    return 2\n", encoding="utf-8")

    def test_register_records_a_line_and_refuses_a_missing_one(self) -> None:
        """Mutant: accept `--line` and drop it before writing the record.
        Mutant: leave `--line` optional for a `survived` verdict - a registered `line: None`
        never joins a measured `line: 2`, so the contradiction check silently never fires
        while its own fixture, which always supplies a line, stays green.
        """
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = m.main(["register", "--root", str(root), "--unit", "BG0001",
                             "--target", "src/thing.py", "--line", "2",
                             "--mutant", "inverted the guard", "--test", "pytest x",
                             "--verdict", "survived"])
            self.assertEqual(0, rc, buf.getvalue())
            entry = next(e for e in m.ledger_entries(root) if e["target"] == "src/thing.py")
            self.assertEqual([2], [mu["line"] for mu in entry["mutants"]],
                             "the shipped verb accepted a line and did not record it, so every "
                             "test asserting one passes on a fixture it could not produce")

            with self.assertRaises(ValueError) as ctx:
                m.register_mutant(root, "src/thing.py", "inverted the guard", "pytest x",
                                  "survived", unit="BG0001")
            self.assertIn("--line", str(ctx.exception),
                          "a survivor was registered with no line, so the contradiction check "
                          "can never join it to a measured record")

    def test_an_equivalent_mutant_still_needs_no_line(self) -> None:
        """The control. An equivalent verdict asserts that no test COULD have killed the
        mutant, which is a statement about the mutant rather than about a place a refusal
        quotes - so demanding a line there would be a bar with no reason behind it, and a
        refusal that fired on everything would pass the test above."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            out = m.register_mutant(root, "src/thing.py", "reordered two assignments", None,
                                    "equivalent", reason="no observable behaviour changed",
                                    unit="BG0001")
            self.assertEqual("equivalent", out["verdict"])


def _git_fixture(root: Path) -> None:
    """A real git repo with one commit, so `run` can tell committed from uncommitted.

    Through `gitutil.git` rather than a raw `subprocess.run(["git", ...])`: the shared helper
    fences upward repository discovery at the temp root and neutralises host config, and the
    repo's own sweep freezes the count of unconfined callers at zero.
    """
    import gitutil  # noqa: PLC0415 - the tests dir is on the path by the time this runs
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "base"]):
        gitutil.git(args, cwd=root)


def _mut_cli(m, *argv) -> tuple[int, str]:
    """Drive `mutation.py` through its shipped entry point. `(exit_code, merged output)`."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            code = m.main(list(argv))
        except SystemExit as exc:
            code = int(exc.code or 0)
    return code, buf.getvalue()


class UncommittedSurfaceCLITests(unittest.TestCase):
    """US0573, re-verified through `mutation.py run` rather than through `series_reason`.

    A surface the runner REFUSED to mutate is not a surface nobody tested. Only the second is
    the author's omission, and an advisory that says the same about both teaches an author to
    ignore it - after which it reports nothing anybody reads.
    """

    def _repo(self, d, *, dirty: bool):
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "src").mkdir(parents=True)
        (root / "src" / "thing.py").write_text(
            "def g(a, b):\n    if a == b:\n        return 1\n    return 2\n", encoding="utf-8")
        _git_fixture(root)
        if dirty:
            (root / "src" / "thing.py").write_text(
                "def g(a, b):\n    if a == b:\n        return 1\n    return 3\n",
                encoding="utf-8")
        return root

    def test_an_uncommitted_surface_is_reported_as_that_reason(self) -> None:
        """AC1. Mutant: fall through to the generic `run refused` reason - the two states read
        identically and the one the author can still act on is indistinguishable from the one
        that indicts them."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, dirty=True)
            code, out = _mut_cli(m, "run", "--root", str(root), "--format", "json",
                                 "--files", str(root / "src" / "thing.py"), "--test", "true")
            self.assertNotEqual(0, code, "an uncommitted surface was mutated")
            # Asserted on the machine-readable KIND, not only on the prose. The prose remedy is
            # composed in the same branch that sets the kind, so a mutant clearing the kind
            # leaves the sentence intact and a substring assertion survives it - which is what
            # this test did until the mutant was actually applied and lived.
            report = json.loads(out[out.index("{"):])
            self.assertEqual(m.UNCOMMITTED_SURFACE, report.get("refusal_kind"),
                             "the run refused without recording WHICH refusal, so a consumer "
                             "cannot tell an uncommitted surface from any other refusal")
            self.assertIn("uncommitted", out.lower(),
                          f"the refusal does not name the uncommitted state:\n{out}")

    def test_the_reason_names_both_routes_to_measured_evidence(self) -> None:
        """AC2. A reason that names the problem and no route is a complaint. Mutant: drop
        either route, or the discipline that makes a hand run trustworthy - a reader is told to
        apply a mutant by hand with no way to know that a cached module reports a false
        survival."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, dirty=True)
            _code, out = _mut_cli(m, "run", "--root", str(root),
                                  "--files", str(root / "src" / "thing.py"), "--test", "true")
            self.assertIn("worktree", out, f"the isolated-checkout route is missing:\n{out}")
            self.assertIn("register", out, "the hand-applied route is missing")
            # ...and the DISCIPLINE, which is half the criterion and was unasserted: deleting
            # the whole clause while keeping both route names left this test green. A hand run
            # named without it sends a reader to a cached module reporting a false survival.
            for discipline in ("anchor", "__pycache__", "python3 -B", "byte-identical"):
                with self.subTest(discipline=discipline):
                    self.assertIn(discipline, out,
                                  "the hand route is named without the discipline that makes "
                                  f"it trustworthy:\n{out}")

    def test_a_committed_untested_surface_still_reports_no_evidence(self) -> None:
        """AC3, THE CONTROL. Without it this change could be an excuse that silences the lane
        rather than a distinction that sharpens it: a committed surface nobody tested must
        still be reported as carrying no evidence."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, dirty=False)
            code, out = _mut_cli(m, "run", "--root", str(root),
                                 "--files", str(root / "src" / "thing.py"), "--test", "true")
            self.assertNotIn("uncommitted", out.lower(),
                             "a committed surface was reported as uncommitted, so the "
                             "distinction fires on everything and sharpens nothing")
            self.assertNotIn("REFUSED", out,
                             "a committed surface was refused, so the run never reached a "
                             "verdict about the tests at all")
            # `--test true` passes on every mutant, so they all SURVIVE and the run exits
            # non-zero. That is the point: a committed surface nobody tested still reports no
            # evidence, rather than being excused by the uncommitted reason.
            self.assertNotEqual(0, code, out)
            self.assertIn("survived", out)


class BytecodeIsolationCLITests(unittest.TestCase):
    """US0565 AC5, asserted on what the shipped runner DOES rather than on a comment.

    A cached bytecode file is keyed on (source mtime, source size), so a SAME-LENGTH mutant
    written inside one mtime second runs the ORIGINAL bytecode and is recorded as survived.
    That is a false verdict about the test rather than about the code, on the instrument every
    other evidence claim in this repo leans on - and it has produced a wrong answer here twice.
    """

    def test_a_stale_pyc_cannot_decide_a_mutants_verdict(self) -> None:
        """Mutants: drop `PYTHONDONTWRITEBYTECODE` from the suite env - the child caches and the
        NEXT mutant inherits it; stop purging the cache - this mutant inherits the previous
        one's; or skip the changed-file assertion - a patch that silently applied nothing is
        recorded as a survivor.
        """
        m = _load()
        self.assertEqual("1", m._suite_env().get("PYTHONDONTWRITEBYTECODE"),
                         "the child may write bytecode, so a same-length mutant can run the "
                         "original module and be recorded as survived")
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "thing.py"
            src.write_text("x = 1\n", encoding="utf-8")
            cache = Path(d) / "__pycache__"
            cache.mkdir()
            stale = cache / "thing.cpython-311.pyc"
            stale.write_bytes(b"stale bytecode from a previous mutant")
            m._purge_bytecode(src)
            self.assertFalse(stale.exists(),
                             "a cached .pyc survived the purge, so the next mutant inherits it")

    def test_a_real_run_leaves_no_bytecode_behind(self) -> None:
        """The end-to-end half, through the shipped verb: after a complete `mutation.py run`
        the target's cache directory holds nothing, so the next run cannot inherit a verdict
        from this one. Asserting the helper alone leaves the WIRING unexercised, which is the
        part a library test does not reach.
        """
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            src = root / "src" / "thing.py"
            src.write_text("def g(a, b):\n    if a == b:\n        return 1\n    return 2\n",
                           encoding="utf-8")
            _git_fixture(root)
            _mut_cli(m, "run", "--root", str(root), "--files", str(src),
                     "--test", "true", "--max-mutations", "2")
            cache = root / "src" / "__pycache__"
            self.assertFalse(cache.exists() and any(cache.glob("*.pyc")),
                             "a run left cached bytecode for its target, so the next run's "
                             "same-length mutant can execute the previous run's module")
            self.assertEqual(
                "def g(a, b):\n    if a == b:\n        return 1\n    return 2\n",
                src.read_text(encoding="utf-8"),
                "the run did not restore its target byte-identically")


class ChangedLineScopeCLITests(unittest.TestCase):
    """US0564 AC2: the mutated surface is the unit's OWN CHANGED LINES, not its whole Affects.

    The scope is the criterion, not an optimisation. A repair touching a handful of lines in a
    large module must be held to those lines: generating over the whole file makes the gate
    cost scale with the file rather than with the change, and a gate nobody can afford to run
    is one that gets switched off.
    """

    def _repo(self, d):
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "src").mkdir(parents=True)
        body = "".join(f"def f{i}(a, b):\n    if a == b:\n        return {i}\n    return 0\n"
                       for i in range(8))
        (root / "src" / "big.py").write_text(body, encoding="utf-8")
        _git_fixture(root)
        import gitutil  # noqa: PLC0415
        base = gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()
        # Change ONE function, then commit, so the diff names a handful of lines in a file
        # carrying many mutatable ones.
        (root / "src" / "big.py").write_text(
            body.replace("        return 3\n", "        return 33\n"), encoding="utf-8")
        gitutil.git(["commit", "-qam", "the repair"], cwd=root)
        return root, base

    def test_mutants_are_scoped_to_the_units_changed_lines(self) -> None:
        """Mutant: generate over the whole file rather than over the changed lines - the gate's
        cost then scales with the file, and it can be passed by mutants landing in code the
        repair never touched.

        THE CONTROL is in the same test: enumerating the whole file yields strictly more, so a
        scoping that returned nothing at all would pass an is-it-smaller assertion on its own.
        """
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root, base = self._repo(d)
            target = root / "src" / "big.py"
            whole, _unchecked = m.enumerate_mutations([target])
            scoped, changed = m.mutants_over_changed_lines(root, [target], base)
            self.assertTrue(whole, "the fixture produced no mutants at all")
            self.assertTrue(scoped, "the changed line produced no mutant, so the scoping is "
                                    "not narrower - it is empty, which passes for the wrong "
                                    "reason")
            self.assertLess(len(scoped), len(whole),
                            "the scoped set is not smaller than the whole file's, so the "
                            "scoping is not happening")
            touched = set()
            for lines in changed.values():
                touched |= lines
            for mu in scoped:
                self.assertIn(mu["line"], touched,
                              f"a mutant landed at line {mu['line']}, which the diff never "
                              f"touched - the gate can be passed by code the repair never "
                              f"changed")


class UnreadableLedgerTests(unittest.TestCase):
    """An unreadable ledger is not an empty one. `_load_ledger` replaces a malformed file and
    reports it; `ledger_entries` threw that report away, so the check that refuses in every mode
    - `off` included - silently passed exactly when the instrument could not be read."""

    def test_a_malformed_ledger_raises_rather_than_reading_as_empty(self) -> None:
        """Mutant: discard `_load_ledger`'s reset flag and return the empty entry list."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            m.ledger_path(root).write_text("{not json at all", encoding="utf-8")
            with self.assertRaises(m.LedgerUnreadable):
                m.ledger_entries(root)

    def test_an_absent_ledger_is_an_empty_history(self) -> None:
        """The control: a project that has never mutated anything reads as empty, not as
        broken, or the refusal fires on every fresh checkout."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            self.assertEqual([], m.ledger_entries(root))


class RunUnitAttributionCLITests(unittest.TestCase):
    """US0661 AC2, at the SHIPPED VERB. Every other test here calls `append_ledger` directly, so
    the wiring between `run --unit` and the ledger - the part a library test does not exercise -
    could be reverted with the whole suite green. It was: replacing the `unit=` argument in
    `cmd_run` with `None` left 436 tests passing.
    """

    def test_run_records_the_unit_it_was_given(self) -> None:
        """Mutant: drop `unit=` from `cmd_run`'s call into `run_gate`."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            src = root / "src" / "thing.py"
            src.write_text("def g(a, b):\n    if a == b:\n        return 1\n    return 2\n",
                           encoding="utf-8")
            _git_fixture(root)
            _mut_cli(m, "run", "--root", str(root), "--files", str(src), "--unit", "BG0001",
                     "--test", "true", "--max-mutations", "2")
            rows = [mu for e in m.ledger_entries(root) for mu in (e.get("mutants") or [])]
            self.assertTrue(rows, "the run recorded no per-mutant row at all")
            self.assertEqual({"BG0001"}, {r["unit"] for r in rows},
                             "the shipped verb was given a unit and did not record it, so the "
                             "gate that selects on it cannot see this run's evidence")

    def test_a_run_with_no_unit_records_none(self) -> None:
        """The control: a run given no unit must not invent one, or the assertion above passes
        on a value nothing supplied."""
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            src = root / "src" / "thing.py"
            src.write_text("def g(a, b):\n    if a == b:\n        return 1\n    return 2\n",
                           encoding="utf-8")
            _git_fixture(root)
            _mut_cli(m, "run", "--root", str(root), "--files", str(src),
                     "--test", "true", "--max-mutations", "2")
            rows = [mu for e in m.ledger_entries(root) for mu in (e.get("mutants") or [])]
            self.assertTrue(rows, "the run recorded no per-mutant row at all")
            self.assertEqual({None}, {r["unit"] for r in rows}, "an unattributed run invented a unit")

    def test_a_line_below_one_is_refused(self) -> None:
        """`--line 0` passed the None check and composed `target:?` through the fallback - the
        exact string the refusal exists to stop printing.

        Mutant: test only `line is None`.
        """
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            (root / "src" / "thing.py").write_text("x = 1\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                m.register_mutant(root, "src/thing.py", "m", "pytest x", "survived",
                                  line=0, unit="BG0001")
            self.assertIn("1 or greater", str(ctx.exception))
            # The control: line 1 is accepted, or the refusal fires on everything.
            self.assertEqual("survived",
                             m.register_mutant(root, "src/thing.py", "m", "pytest x",
                                               "survived", line=1, unit="BG0001")["verdict"])

class RegisterEvidenceIntegrityTests(unittest.TestCase):
    """BG0550/BG0531: what `register` silently lost, and what it never checked."""

    def _repo(self, d):
        from pathlib import Path as _P
        root = _P(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "t.py").write_text("def a():\n    return 1\n\ndef b():\n    return 1\n")
        return root

    def test_dropped_stale_registrations_are_reported(self) -> None:
        """MUTANT: drop `dropped_stale` from register_mutant's return dict.

        Registrations are keyed on the target's content hash and rows for other content are
        discarded - correctly, they describe bytes the file no longer has. Doing it SILENTLY
        left a builder reading `1 registered` where five claims had just gone, which is
        indistinguishable from a builder who did the work once.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            for m in ("first", "second"):
                _load().register_mutant(root, "t.py", m, "pytest x", "killed", line=1)
            (root / "t.py").write_text("def a():\n    return 2\n")
            res = _load().register_mutant(root, "t.py", "third", "pytest x", "killed", line=1)
        self.assertEqual(res.get("dropped_stale"), 2,
                         "both earlier registrations were discarded and must be counted")

    def test_anchor_must_be_unique(self) -> None:
        """MUTANT: accept any anchor occurrence count instead of exactly one.

        A hand-applied mutant is located by a substring. One matching twice patches the site
        the author did not mean, the test stays green for a reason nobody looked at, and the
        ledger records a verdict about code that was never mutated.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            with self.assertRaises(ValueError) as twice:
                _load().register_mutant(root, "t.py", "m", "pytest x", "killed", line=2,
                                         anchor="    return 1")
            self.assertIn("2 time(s)", str(twice.exception))
            with self.assertRaises(ValueError) as absent:
                _load().register_mutant(root, "t.py", "m", "pytest x", "killed", line=1,
                                         anchor="def zzz():")
            self.assertIn("0 time(s)", str(absent.exception))
            # The control: a unique anchor is accepted, so the check refuses ambiguity rather
            # than refusing anchors.
            ok = _load().register_mutant(root, "t.py", "m", "pytest x", "killed", line=1,
                                          anchor="def a():")
            self.assertEqual(ok["verdict"], "killed")


class CrossProvenanceContradictionTests(unittest.TestCase):
    """BG0552. A measured row names the generator's fault class; a registered row names the
    author's prose. The two shared no joinable value, so the check that catches the ledger
    contradicting itself could only ever see WITHIN one provenance - and the cross-provenance
    case is the valuable one, because it is where a hand-typed claim is caught disagreeing with
    a MEASUREMENT. Establishing it needed a field, not a heuristic.
    """

    def setUp(self) -> None:
        self.mut = _load()
        self.d = Path(tempfile.mkdtemp(prefix="xprov_"))
        self.addCleanup(__import__("shutil").rmtree, self.d, ignore_errors=True)
        (self.d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (self.d / "src").mkdir()
        (self.d / "src" / "thing.py").write_text(
            "def f(a, b):\n    if a == b:\n        return 1\n    return 0\n", encoding="utf-8")
        (self.d / "sdlc-studio" / "bugs" / "BG9002-x.md").write_text(
            "# BG9002: a fixture bug\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Points:** 2\n> **Verification depth:** functional\n"
            "> **Affects:** src/thing.py\n\n## Acceptance Criteria\n\n"
            "- [x] **AC1** Given a thing, when it happens, then it works.\n"
            "  - **Verify:** manual a human checks it\n\n## Test Plan\n\n"
            "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
            "| AC1 | invert-guard | Given a thing, when it happens, then it works. |\n",
            encoding="utf-8")
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "transition_xprov", Path(__file__).resolve().parents[1] / "transition.py")
        self.tr = importlib.util.module_from_spec(spec)
        sys.modules["transition_xprov"] = self.tr
        spec.loader.exec_module(self.tr)

    def _measure(self) -> None:
        """A real run: the covering test passes on the original and fails on an inverted guard,
        so `invert-guard` at line 2 is measured KILLED."""
        self.mut.run_gate(
            self.d, [self.d / "src" / "thing.py"],
            "python3 -c \"import sys;sys.path.insert(0,'src');import thing;"
            "assert thing.f(1,1)==1\"",
            unit="BG9002")

    def _register(self, verdict: str, fault_class: str | None) -> None:
        self.mut.register_mutant(self.d, "src/thing.py", "inverted the a == b guard",
                                 "pytest t.py", verdict, unit="BG9002", criterion="AC1",
                                 line=2, fault_class=fault_class)

    def _blocks(self) -> list[str]:
        return [u for u in self.tr.requirements(str(self.d), "BG9002", "Fixed")
                if "CONTRADICTS" in u or "DISAGREES ACROSS" in u]

    def test_a_measured_row_records_its_fault_class_in_its_own_field(self) -> None:
        """AC1. The class lived only in the prose slot a registered row fills with words, so
        there was nothing to join on. MUTANT: write None into the field."""
        self._measure()
        rows = [m for e in self.mut.ledger_entries(self.d) for m in (e.get("mutants") or [])
                if self.mut.entry_provenance(e) == self.mut.PROVENANCE_MEASURED]
        self.assertTrue(rows, "the run recorded no measured rows at all")
        self.assertTrue(all(m.get("class") for m in rows),
                        "a measured row carries no fault class, so it can join nothing")

    def test_a_hand_typed_claim_contradicting_a_measurement_is_caught(self) -> None:
        """AC2. THE bug: a measured `killed` and a registered `survived` for one mutant at one
        line, exit 0 and nothing said. MUTANT: skip the cross-provenance branch."""
        self._measure()
        self._register("survived", "invert-guard")
        hard, soft = self.tr._ledger_contradiction(str(self.d), "BG9002")
        self.assertIsNone(hard, "a cross-provenance disagreement was raised as a same-provenance "
                                "contradiction, which no config can stand down")
        self.assertTrue(soft, "a claim contradicting a measurement was not detected at all")
        self.assertIn("DISAGREES ACROSS", soft)
        self.assertIn("invert-guard", soft)

    def test_the_cross_provenance_finding_can_be_stood_down_but_the_same_provenance_one_cannot(
            self) -> None:
        """BG0552 round 2. The cross join keys on the fault CLASS, which is coarser than a
        mutant: an independent review built two genuinely different `invert-guard` edits at one
        line, one measured and one hand-registered, and the guard called the instruments liars
        and told the author to withdraw TRUE evidence - in a branch that ignored the configured
        mode, so `off` could not reach it.

        A check that can be wrong must be one a project can stand down. A check that cannot be
        wrong need not be, and the same-provenance one is keyed on the mutant's own prose.

        MUTANT: append the cross-provenance finding to `blocks` unconditionally again.
        """
        self._measure()
        self._register("survived", "invert-guard")
        for mode, expect_block in (("report", False), ("off", False), ("block", True)):
            with self.subTest(mode=mode):
                (self.d / "sdlc-studio" / ".config.yaml").write_text(
                    f"review:\n  mutation_evidence: {mode}\n", encoding="utf-8")
                unmet = self.tr.requirements(str(self.d), "BG9002", "Fixed")
                got = [u for u in unmet if "DISAGREES ACROSS" in u]
                self.assertEqual(expect_block, bool(got),
                                 f"mode={mode}: blocks={got}")

    def test_a_same_provenance_row_does_not_hide_the_cross_provenance_one(self) -> None:
        """BG0552 round 2, second finding. `seen_class` was FIRST-WINS, so once a
        same-provenance row occupied a key, a later row of the other provenance was compared
        only against that first verdict - and AC2's own case went undetected. Register `killed`,
        then `survived`, then measure `killed`, and the ledger holds a measured `killed` beside a
        registered `survived` for one class at one line while reporting nothing.

        AC2's test registers a single row, so it could not see this.

        MUTANT: keep only the first verdict per key.
        """
        # DIFFERENT prose, so these two are not a same-provenance contradiction - that check
        # returns early and would mask the very thing under test here.
        self.mut.register_mutant(self.d, "src/thing.py", "inverted the a == b guard",
                                 "pytest t.py", "killed", unit="BG9002", criterion="AC1",
                                 line=2, fault_class="invert-guard")
        self.mut.register_mutant(self.d, "src/thing.py", "inverted a different guard entirely",
                                 "pytest t.py", "survived", unit="BG9002", criterion="AC1",
                                 line=2, fault_class="invert-guard")
        self._measure()
        _hard, soft = self.tr._ledger_contradiction(str(self.d), "BG9002")
        self.assertTrue(soft, "a same-provenance row hid the cross-provenance disagreement")
        self.assertIn("DISAGREES ACROSS", soft)

    def test_an_agreeing_claim_is_not_a_contradiction(self) -> None:
        """AC3, the positive control. A check that fires on agreement is not a check.
        MUTANT: drop the `cprior[0] != verdict` test so any second row contradicts."""
        self._measure()
        self._register("killed", "invert-guard")
        self.assertEqual((None, None), self.tr._ledger_contradiction(str(self.d), "BG9002"),
                         "an agreeing hand-registered claim was read as a disagreement")

    def test_without_a_class_the_rows_cannot_be_compared_and_nothing_is_claimed(self) -> None:
        """AC4. The honest state, and the reason the field is optional: an author who does not
        name a class gets no cross-provenance join rather than a guessed one. This is the
        pre-fix behaviour, kept deliberately and pinned so it is a decision, not a gap."""
        self._measure()
        self._register("survived", None)
        self.assertEqual((None, None), self.tr._ledger_contradiction(str(self.d), "BG9002"),
                         "rows with no shared class were joined anyway, which is a guess")

    def test_a_class_the_generator_never_emits_is_refused(self) -> None:
        """AC5. Free text would join nothing, so it would record a promise it cannot keep.
        MUTANT: drop the vocabulary check and accept any string."""
        with self.assertRaises(ValueError) as ctx:
            self._register("survived", "invert-the-guard")
        self.assertIn("joins no measured row", str(ctx.exception))

    def test_two_registered_rows_of_one_class_are_not_a_cross_contradiction(self) -> None:
        """AC6. The class is coarser than the prose, so two DIFFERENT hand-applied mutants of
        one class at one line would look identical to the cross join. They are two honest
        statements, and the same-provenance branch can still tell them apart by prose. This
        branch ignores the configured mode, so a false positive here is not survivable.
        MUTANT: drop the `cprior[1] != prov` test so same-provenance rows join on class."""
        self.mut.register_mutant(self.d, "src/thing.py", "inverted the a == b guard",
                                 "pytest t.py", "killed", unit="BG9002", criterion="AC1",
                                 line=2, fault_class="invert-guard")
        self.mut.register_mutant(self.d, "src/thing.py", "inverted a different guard entirely",
                                 "pytest t.py", "survived", unit="BG9002", criterion="AC1",
                                 line=2, fault_class="invert-guard")
        _hard, soft = self.tr._ledger_contradiction(str(self.d), "BG9002")
        self.assertIsNone(soft, "two registered mutants of one class were read as the two "
                                "instruments disagreeing")


class RetractWithdrawsAVerdictOnTheRecord(unittest.TestCase):
    """BG0553. `plan_execution` holds the WORST verdict per criterion, so a mutant registered
    `survived` by mistake could not be corrected by registering it `killed` - and the
    self-contradiction check then refused the transition in EVERY mode, `off` included, with no
    escape but `--force`. An author who mistyped was left worse off than one who left it wrong.

    A review round proposed superseding the earlier row; that was implemented and reverted,
    because a supersede is invisible and reopens the escape the worst-verdict rule closes. So the
    correction is made VISIBLE instead: withdrawn, never deleted, with a reason on the record.
    """

    REASON = "the verdict was mistyped as survived; the test did go red when the mutant ran"

    def setUp(self) -> None:
        self.mut = _load()
        self.d = Path(tempfile.mkdtemp(prefix="retract_"))
        self.addCleanup(__import__("shutil").rmtree, self.d, ignore_errors=True)
        (self.d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (self.d / "f.py").write_text("def f(a, b):\n    if a == b:\n        return 1\n    return 0\n",
                                     encoding="utf-8")
        (self.d / "sdlc-studio" / "bugs" / "BG9001-a-fixture-bug.md").write_text(
            "# BG9001: a fixture bug\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Points:** 2\n> **Affects:** f.py\n\n## Acceptance Criteria\n\n"
            "- [x] **AC1** Given a thing, when it happens, then it works.\n"
            "  - **Verify:** manual a human checks it\n\n## Test Plan\n\n"
            "| Criterion | Mutant - the production change this test must fail on | Title |\n"
            "| --- | --- | --- |\n"
            "| AC1 | invert the a == b guard | Given a thing, when it happens, then it works. |\n",
            encoding="utf-8")

    def _register(self, verdict: str) -> None:
        self.mut.register_mutant(self.d, "f.py", "inverted the a == b guard", "pytest t.py",
                                 verdict, unit="BG9001", criterion="AC1", line=2)

    def _retract(self, **over):
        kw = dict(target="f.py", unit="BG9001", criterion="AC1", line=2,
                  mutant="inverted the a == b guard", verdict="survived", reason=self.REASON)
        kw.update(over)
        return self.mut.retract_mutant(self.d, **kw)

    def test_a_withdrawn_verdict_stops_holding_the_plan(self) -> None:
        """AC1. The whole point: the mistyped survivor no longer stands, so the correction
        works. MUTANT: drop the `withdrawn` skip in `plan_execution`."""
        self._register("survived")
        self._register("killed")
        self.assertEqual("survived",
                         self.mut.plan_execution(self.d, "BG9001")["rows"][0]["verdict"])
        self._retract()
        res = self.mut.plan_execution(self.d, "BG9001")
        self.assertEqual("killed", res["rows"][0]["verdict"])
        self.assertTrue(res["ok"], res.get("outstanding"))

    def test_the_withdrawal_is_recorded_and_not_deleted(self) -> None:
        """AC2. A correction nobody can see IS the escape hatch. The row stays, carrying the
        reason and the verdict it withdrew, and the summary counts the retraction."""
        self._register("survived")
        self._retract()
        entry = [e for e in self.mut.ledger_entries(self.d)
                 if e.get("target") == "f.py"
                 and self.mut.entry_provenance(e) == self.mut.PROVENANCE_REGISTERED][0]
        rows = entry["mutants"]
        self.assertEqual(1, len(rows), "the row was removed rather than withdrawn")
        self.assertEqual("survived", rows[0]["verdict"], "the original verdict was overwritten")
        self.assertEqual(self.REASON, rows[0]["withdrawn"]["reason"])
        self.assertEqual(1, entry["summary"]["retracted"])
        self.assertFalse(entry["summary"].get("survived"),
                         "the coverage lane still counts a withdrawn survivor")

    def test_a_withdrawal_is_visible_to_a_reader_who_is_not_the_author(self) -> None:
        """BG0553 round 2, and the finding that mattered most. `retract` marked rows withdrawn and
        NOTHING read the field back: both readers skipped withdrawn rows with a bare `continue`,
        no verb printed the ledger, nothing consumed the `retracted` tally, and the ledger lives
        in gitignored `.local/`. After a retraction the observable state was indistinguishable
        from the row never having been registered - which is exactly the objection that got the
        SUPERSEDE design rejected. Three shipped sentences claimed the opposite.

        AC2 was literally satisfied by a dict key, so its test passed while the rationale the
        whole unit rests on did not hold. The criterion was weaker than the reason for the work.

        MUTANT: make `retractions` return [] - every reader below goes quiet at once.
        """
        self._register("survived")
        self._retract()
        rows = self.mut.retractions(self.d, "BG9001")
        self.assertEqual(1, len(rows), "the withdrawal is not readable at all")
        self.assertEqual("survived", rows[0]["verdict"])
        self.assertEqual(self.REASON, rows[0]["reason"])
        # ...and it reaches the join the author sees...
        self.assertTrue(self.mut.plan_execution(self.d, "BG9001").get("retracted"),
                        "the plan join does not surface the withdrawal that changed it")
        # ...and the seat brief, which is the artefact a REVIEWER reads.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "critic_vis", Path(__file__).resolve().parents[1] / "critic.py")
        critic = importlib.util.module_from_spec(spec)
        sys.modules["critic_vis"] = critic
        spec.loader.exec_module(critic)
        seats = self.d / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True, exist_ok=True)
        (seats / "qa.md").write_text("# QA seat\n", encoding="utf-8")
        text = critic.brief(self.d, "BG9001", "qa")
        self.assertIn("WITHDRAWN mutation verdicts", text,
                      "a reviewer's brief says nothing about a withdrawn verdict")
        self.assertIn(self.REASON, text, "the brief does not carry the reason to be judged")

    def test_the_verdict_is_part_of_the_join(self) -> None:
        """AC3. Found by running the verb, not reading it. Without the verdict in the join a
        retraction matches EVERY row for one mutant and withdraws them all, so correcting a
        mistyped `survived` silently took the `killed` beside it and left no evidence at all -
        the refusals were all correct and the success case did the wrong thing.
        MUTANT: drop `mu.get("verdict") == verdict` from the match."""
        self._register("survived")
        self._register("killed")
        self.assertEqual(1, self._retract()["retracted"])
        entry = [e for e in self.mut.ledger_entries(self.d) if e.get("target") == "f.py"][0]
        live = [m for m in entry["mutants"] if not m.get("withdrawn")]
        self.assertEqual(["killed"], [m["verdict"] for m in live],
                         "the correct verdict was withdrawn alongside the mistake")

    def test_a_reason_too_thin_to_audit_is_refused(self) -> None:
        """AC4. An unexplained retraction is the escape hatch. MUTANT: set the floor to 0."""
        self._register("survived")
        for reason in ("", "typo", "   wrong   "):
            with self.subTest(reason=reason):
                with self.assertRaises(ValueError) as ctx:
                    self._retract(reason=reason)
                self.assertIn("audit trail", str(ctx.exception))

    def test_a_retraction_that_matches_nothing_refuses(self) -> None:
        """AC5. Silently doing nothing is the failure this verb exists to end, so a join that
        finds no row must say so. MUTANT: return a zero-count success instead of raising."""
        self._register("survived")
        for label, over in (("wrong line", {"line": 99}),
                            ("wrong criterion", {"criterion": "AC7"}),
                            ("wrong prose", {"mutant": "something else entirely"}),
                            ("already withdrawn", {})):
            if label == "already withdrawn":
                self._retract()          # the first one succeeds; a second must not
            with self.subTest(label):
                with self.assertRaises(ValueError) as ctx:
                    self._retract(**over)
                self.assertIn("has done nothing", str(ctx.exception))

    def test_a_measured_verdict_cannot_be_retracted(self) -> None:
        """AC6. Withdrawing a measurement is editing an observation - the way to correct one is
        to measure again. MUTANT: drop the provenance filter from the match."""
        self._register("survived")
        entry = [e for e in self.mut.ledger_entries(self.d) if e.get("target") == "f.py"][0]
        entry["provenance"] = "measured"
        state, reset = self.mut._load_ledger(self.mut.ledger_path(self.d))
        self.mut._store_ledger(self.mut.ledger_path(self.d), state, [entry], reset)
        with self.assertRaises(ValueError) as ctx:
            self._retract()
        self.assertIn("re-measure it instead", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
