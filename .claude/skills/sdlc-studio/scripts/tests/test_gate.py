"""Unit tests for gate.py - the portable CI quality gate (CR0046)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "gate.py"
REPO = Path(__file__).resolve().parents[5]  # repo root (holds sdlc-studio/ artifacts)


def _load():
    spec = importlib.util.spec_from_file_location("gate", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gate"] = mod
    spec.loader.exec_module(mod)
    return mod


gate = _load()


def _fake(count: int, blocking: bool = True):
    return lambda root: {"count": count, "blocking": blocking, "detail": str(count)}


import unittest


class GateLogicTests(unittest.TestCase):
    def test_all_pass(self) -> None:
        r = gate.run_gate(".", checks={"a": _fake(0), "b": _fake(0)})
        self.assertTrue(r["ok"])
        self.assertTrue(all(c["status"] == "pass" for c in r["checks"]))

    def test_blocking_failure_fails_gate(self) -> None:
        r = gate.run_gate(".", checks={"a": _fake(0), "b": _fake(2, blocking=True)})
        self.assertFalse(r["ok"])

    def test_nonblocking_failure_does_not_fail_gate(self) -> None:
        r = gate.run_gate(".", checks={"a": _fake(0), "b": _fake(3, blocking=False)})
        self.assertTrue(r["ok"])  # reported but advisory
        self.assertEqual([c["status"] for c in r["checks"] if c["check"] == "b"], ["fail"])

    def test_only_selects_subset(self) -> None:
        r = gate.run_gate(".", only=["a"], checks={"a": _fake(0), "b": _fake(9)})
        self.assertEqual([c["check"] for c in r["checks"]], ["a"])

    def test_skip_excludes(self) -> None:
        r = gate.run_gate(".", skip=["b"], checks={"a": _fake(0), "b": _fake(9)})
        self.assertNotIn("b", [c["check"] for c in r["checks"]])

    def test_empty_selection_is_ok(self) -> None:
        r = gate.run_gate(".", only=["nonexistent"], checks={"a": _fake(9)})
        self.assertTrue(r["ok"])
        self.assertEqual(r["checks"], [])


class GateRealWrapperTests(unittest.TestCase):
    def test_default_checks_present(self) -> None:
        self.assertEqual(set(gate.DEFAULT_CHECKS),
                         {"conformance", "reconcile", "validate", "constitution", "integrity",
                          "duplicate-id", "provenance", "doc-coverage", "disclosure", "doc-freshness",
                      "mutation"})

    def test_real_wrappers_run_and_shape(self) -> None:
        # Exercises the real checks end-to-end against this repo; asserts structure,
        # not pass/fail (state-independent, so not fragile).
        r = gate.run_gate(str(REPO))
        self.assertIsInstance(r["ok"], bool)
        self.assertEqual(len(r["checks"]), 11)
        for c in r["checks"]:
            self.assertEqual(set(c), {"check", "count", "blocking", "status", "detail"})

    def test_reconcile_wrapper_counts_drift_not_dict_keys(self) -> None:
        # Regression (hermetic): detect_type returns a 6-key dict; the wrapper must count
        # ["drift"] items, not len(dict). Monkeypatch so it's state-independent.
        import reconcile
        orig = reconcile.detect_type
        reconcile.detect_type = lambda t, root: {
            "census_total": 0, "census_counts": {}, "row_counts": {},
            "index_exists": True, "index_summary": {}, "drift": [{"a": 1}, {"b": 2}]}
        try:
            count = gate._reconcile(str(REPO))["count"]
        finally:
            reconcile.detect_type = orig
        self.assertEqual(count, 2 * len(reconcile._DEFAULT_TYPES))  # 2 drift/type, not 6 keys


    def test_duplicate_index_row_fails_gate(self) -> None:
        # CR0055 regression (hermetic): two rows for one id in an index must FAIL the gate
        # (reconcile collapses them to one dict key -> zero drift -> false PASS without this).
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            sd = repo / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| US0001 | a | Done |\n| US0001 | dupe | Done |\n", encoding="utf-8")
            (sd / "US0001-a.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            self.assertEqual(gate._duplicate_id(str(repo))["count"], 1)
            self.assertFalse(gate.run_gate(str(repo), only=["duplicate-id"])["ok"])


    def test_provenance_blocking_follows_enforce(self) -> None:
        import provenance
        orig = provenance.check
        try:
            provenance.check = lambda root: {"findings": [{"blocking": False}], "enforced": False, "ok": True}
            self.assertFalse(gate._provenance(str(REPO))["blocking"])  # advisory
            self.assertTrue(gate.run_gate(str(REPO), only=["provenance"])["ok"])  # advisory -> gate PASS
            provenance.check = lambda root: {"findings": [{"blocking": True}], "enforced": True, "ok": False}
            self.assertTrue(gate._provenance(str(REPO))["blocking"])   # enforced -> blocks
            self.assertFalse(gate.run_gate(str(REPO), only=["provenance"])["ok"])
        finally:
            provenance.check = orig

    def test_duplicate_id_additivity(self) -> None:
        # files + rows are independent sources: one dup row -> 1; dup file + dup row -> 2.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            sd = repo / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| US0001 | a | Done |\n| US0001 | dupe-row | Done |\n", encoding="utf-8")
            (sd / "US0001-a.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            self.assertEqual(gate._duplicate_id(str(repo))["count"], 1)  # one dup row, no dup file
            (sd / "US0002-x.md").write_text("# US0002: x\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "US0002-y.md").write_text("# US0002: y\n\n> **Status:** Done\n", encoding="utf-8")
            self.assertEqual(gate._duplicate_id(str(repo))["count"], 2)  # + one dup file


    def test_a_crashing_check_does_not_abort_the_gate(self):
        def boom(root):
            raise RuntimeError("kaboom")
        r = gate.run_gate(".", checks={"a": _fake(0), "boom": boom})
        statuses = {c["check"]: c["status"] for c in r["checks"]}
        self.assertEqual(statuses["boom"], "error")     # reported, not raised
        self.assertEqual(statuses["a"], "pass")          # other checks still ran
        self.assertTrue(r["ok"])                          # error is non-blocking, gate not failed

    def test_main_returns_exit_code(self) -> None:
        rc = gate.main(["--root", str(REPO), "--format", "json"])
        self.assertIn(rc, (0, 1))

    def test_missing_root_fails_not_vacuous_pass(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:  # no sdlc-studio/ dir
            r = gate.run_gate(d)
            self.assertFalse(r["ok"])
            self.assertEqual(r["checks"][0]["check"], "scope")
        self.assertFalse(gate.run_gate(str(Path(d) / "nonexistent"))["ok"])

    def test_constitution_blocking_follows_enforce(self) -> None:
        import constitution
        orig = constitution.check_constitution
        try:
            constitution.check_constitution = lambda root: {
                "exists": True, "enforced": False, "violations": [{"x": 1}]}
            self.assertFalse(gate._constitution(str(REPO))["blocking"])  # advisory
            constitution.check_constitution = lambda root: {
                "exists": True, "enforced": True, "violations": [{"x": 1}]}
            self.assertTrue(gate._constitution(str(REPO))["blocking"])   # enforced -> blocks
        finally:
            constitution.check_constitution = orig


class ConformanceRemedyTests(unittest.TestCase):
    """CR0121: a conformance failure must name the remedies inline, not print a bare count."""

    def _repo(self, d, *, done_no_anno: int = 0) -> Path:
        repo = Path(d)
        sd = repo / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        for n in range(1, done_no_anno + 1):
            (sd / f"US{n:04d}-x.md").write_text(
                f"# US{n:04d}: s\n\n> **Status:** Done\n"
                "> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell echo ok\n",
                encoding="utf-8")
        return repo

    def test_failure_detail_names_adopt_after_and_verify_ac(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, done_no_anno=3)  # 3 Done units, none annotated -> non-conformant
            detail = gate._conformance(str(repo))["detail"]
            self.assertIn("conformance.adopt_after", detail)  # the cutoff remedy
            self.assertIn("verify_ac", detail)                # the backfill remedy

    def test_bulk_miss_reads_as_debt_not_regression(self) -> None:
        # All Done units mass-miss the same stage -> unadopted discipline (forward-only debt),
        # not a regression introduced by this change.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, done_no_anno=4)
            detail = gate._conformance(str(repo))["detail"]
            self.assertIn("unadopted", detail.lower())

    def test_clean_repo_no_remedy_noise(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, done_no_anno=0)
            r = gate._conformance(str(repo))
            self.assertEqual(r["count"], 0)
            self.assertNotIn("adopt_after", r["detail"])  # no remedy noise on a green check


class GateExitContractTests(unittest.TestCase):
    def test_cmd_gate_maps_ok_to_exit_code(self) -> None:
        import argparse
        orig = gate.run_gate
        args = argparse.Namespace(root=".", only=None, skip=None, format="json")
        try:
            gate.run_gate = lambda *a, **k: {"ok": True, "checks": []}
            self.assertEqual(gate.cmd_gate(args), 0)
            gate.run_gate = lambda *a, **k: {"ok": False, "checks": []}
            self.assertEqual(gate.cmd_gate(args), 1)
        finally:
            gate.run_gate = orig


if __name__ == "__main__":
    unittest.main()


class RetroCloseGateTests(unittest.TestCase):
    """US0042 / CR0129: the sprint close must fail loud without the batch retro."""

    def test_close_gate_requires_retro(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            self.assertFalse(report["ok"])
            retro = next(c for c in report["checks"] if c["check"] == "retro")
            self.assertEqual(retro["status"], "fail")
            self.assertTrue(retro["blocking"])

    def test_close_gate_passes_with_retro(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            rd = root / "sdlc-studio" / "retros"
            rd.mkdir(parents=True)
            (rd / "RETRO0005-batch.md").write_text("# RETRO-0005\n", encoding="utf-8")
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            self.assertTrue(report["ok"])


class MutationLaneTests(unittest.TestCase):
    """The advisory mutation lane: survivors warn, absence reads not-run, never PASS."""

    def _root(self, t, report=None):
        import json as _json
        root = Path(t)
        (root / "sdlc-studio").mkdir(parents=True)
        if report is not None:
            local = root / "sdlc-studio" / ".local"
            local.mkdir()
            (local / "mutation-report.json").write_text(_json.dumps(report), encoding="utf-8")
        return root

    def test_survivors_warn_advisory(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, {"summary": {"applied": 5, "killed": 4, "survived": 1,
                                              "errors": 0, "truncated": 0}})
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertEqual(lane["status"], "fail")       # renders [warn]
            self.assertFalse(lane["blocking"])             # advisory: gate unaffected
            self.assertIn("1 survived", lane["detail"])
            self.assertTrue(report["ok"])

    def test_absent_report_is_not_run(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, report=None)
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertNotEqual(lane["status"], "pass")    # never PASS when not run
            self.assertFalse(lane["blocking"])
            self.assertIn("not run", lane["detail"])

    def test_clean_report_passes(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, {"summary": {"applied": 5, "killed": 5, "survived": 0,
                                              "errors": 0, "truncated": 0}})
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            self.assertEqual(report["checks"][0]["status"], "pass")

    def test_stale_report_never_reads_pass(self) -> None:
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, {"git_rev": "0" * 40,
                                  "summary": {"applied": 5, "killed": 5, "survived": 0,
                                              "errors": 0, "unviable": 0, "truncated": 0}})
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "f.txt").write_text("x", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-qm", "c"], cwd=root, check=True)
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertNotEqual(lane["status"], "pass")
            self.assertIn("STALE", lane["detail"])
