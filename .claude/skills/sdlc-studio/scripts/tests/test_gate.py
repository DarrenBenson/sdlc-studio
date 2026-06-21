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
                          "duplicate-id", "provenance", "doc-coverage", "disclosure"})

    def test_real_wrappers_run_and_shape(self) -> None:
        # Exercises the real checks end-to-end against this repo; asserts structure,
        # not pass/fail (state-independent, so not fragile).
        r = gate.run_gate(str(REPO))
        self.assertIsInstance(r["ok"], bool)
        self.assertEqual(len(r["checks"]), 9)
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
