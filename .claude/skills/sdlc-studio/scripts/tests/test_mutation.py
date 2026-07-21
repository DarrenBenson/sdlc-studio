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
                              "errors": 0, "unviable": 0})
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
                mut.register_mutant(root, root / "nope.py", "m", "t", "killed")
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
                    mut.register_mutant(root, root / "target.py", mutant, test, "killed")
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
                    mut.register_mutant(root, root / "target.py", "m", "t", bad)
            self.assertFalse((root / "sdlc-studio" / ".local" / "mutation-runs.json").exists())

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


if __name__ == "__main__":
    unittest.main()
