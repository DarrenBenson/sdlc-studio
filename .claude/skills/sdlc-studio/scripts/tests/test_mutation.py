"""Unit tests for mutation.py - the executable mutation-check gate (RED first).

Fixtures are pure-stdlib unittest targets so the bridge's subprocess runs need
nothing beyond python3. Test titles are pinned by TS0002's AC Coverage Matrix.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
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

if __name__ == "__main__":
    unittest.main()
'''

VACUOUS_TEST = '''import unittest
import target

class T(unittest.TestCase):
    def test_classify_runs(self):
        target.classify(1)  # exercises, pins nothing

if __name__ == "__main__":
    unittest.main()
'''

RED_TEST = '''import unittest
import target

class T(unittest.TestCase):
    def test_fails(self):
        self.assertEqual(1, 2)  # a red baseline over unmutated code

if __name__ == "__main__":
    unittest.main()
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
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            rc = mut.main(["run", "--files", str(root / "target.py"),
                           "--test", f"{sys.executable} -m unittest test_vacuous",
                           "--root", str(root)])
            self.assertNotEqual(rc, 0)

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
            rc = mut.main(["run", "--files", str(root / "target.py"),
                           "--test", f"{sys.executable} -m unittest test_red",
                           "--root", str(root)])
            self.assertNotEqual(rc, 0)                  # never a clean-looking zero


class LaneTests(unittest.TestCase):
    def test_files_and_since_select_surface(self) -> None:
        mut = _load()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "other.py").write_text("def noop():\n    return 1\n", encoding="utf-8")
            explicit = mut.select_files(root, files=[str(root / "target.py")])
            self.assertEqual([p.name for p in explicit], ["target.py"])
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
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
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "target.py"], cwd=root, check=True)
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


if __name__ == "__main__":
    unittest.main()
