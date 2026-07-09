"""Unit tests for gate.py - the portable CI quality gate (CR0046)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "gate.py"
REPO = Path(__file__).resolve().parents[5]  # repo root (holds sdlc-studio/ artifacts)


def _in_dev_repo(repo: Path = REPO) -> bool:
    """True only when `repo` is the artefact-bearing dev repo - it holds a `sdlc-studio/`
    workspace AND this skill sits under `repo/.claude/skills/`. Run from an installed copy
    (`~/.claude/skills/sdlc-studio/`), `parents[5]` is the home dir with no workspace, so the
    two real-wrapper tests below must SKIP (visibly), not fail on environment (BG0069)."""
    skills = repo / ".claude" / "skills"
    return (repo / "sdlc-studio").is_dir() and skills.is_dir() \
        and str(Path(__file__).resolve()).startswith(str(skills.resolve()))


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

    def test_unknown_only_fails_loud(self) -> None:
        # BG0059: an --only naming a check that does not exist must FAIL, not run zero
        # checks and report a vacuous PASS (LL0008).
        r = gate.run_gate(".", only=["nonexistent"], checks={"a": _fake(9)})
        self.assertFalse(r["ok"])
        self.assertIn("nonexistent", r["checks"][0]["detail"])

    def test_unknown_skip_fails_loud(self) -> None:
        # BG0059: a --skip naming a non-existent check is a typo, not a no-op.
        r = gate.run_gate(".", skip=["nope"], checks={"a": _fake(0)})
        self.assertFalse(r["ok"])

    def test_skip_all_fails_loud(self) -> None:
        # BG0059: skipping every check leaves nothing to prove - not a PASS.
        r = gate.run_gate(".", skip=["a", "b"], checks={"a": _fake(0), "b": _fake(0)})
        self.assertFalse(r["ok"])


class IndexDerivedCheckTests(unittest.TestCase):
    """US0058/CR0168: _index.md is derived output; a hand edit is caught by the gate."""

    def _repo(self, root: Path, status_in_index: str) -> None:
        sd = root / "sdlc-studio" / "bugs"
        sd.mkdir(parents=True)
        (sd / "BG0001-x.md").write_text(
            "# BG0001: x\n\n> **Status:** Closed\n> **Severity:** Low\n", encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Closed | 1 |\n\n"
            "## All\n\n| ID | Title | Status | Severity | Created | Updated |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            f"| [BG0001](BG0001-x.md) | x | {status_in_index} | Low | -- | -- |\n",
            encoding="utf-8")

    def test_clean_index_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, "Closed")  # index matches the file
            r = gate.run_gate(str(root), only=["index-derived"])
            self.assertTrue(r["ok"], r["checks"])

    def test_hand_edited_row_caught(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, "Open")  # index row hand-edited to the wrong status
            r = gate.run_gate(str(root), only=["index-derived"])
            self.assertFalse(r["ok"])


class GateRealWrapperTests(unittest.TestCase):
    def test_dev_repo_detector_true_here(self) -> None:
        # Guarded like the wrappers: from an install this SKIPS (it must, or it would recreate
        # the misleading FAILED this bug exists to kill). In the dev repo the detector is True.
        if not _in_dev_repo():
            self.skipTest("dev-repo-only: the detector is False from an installed copy")
        self.assertTrue(_in_dev_repo())

    def test_dev_repo_detector_false_for_workspaceless_root(self) -> None:
        # Always-run: exercises the NEGATIVE branch (an install-like root has no sdlc-studio/
        # workspace), so it passes from an install too - never a false FAILED.
        self.assertFalse(_in_dev_repo(Path(tempfile.gettempdir())))

    def test_default_checks_present(self) -> None:
        self.assertEqual(set(gate.DEFAULT_CHECKS),
                         {"conformance", "reconcile", "index-derived", "validate", "constitution",
                          "integrity", "duplicate-id", "provenance", "doc-coverage", "disclosure",
                          "doc-freshness", "mutation"})

    def test_real_wrappers_run_and_shape(self) -> None:
        # Exercises the real checks end-to-end against this repo; asserts structure,
        # not pass/fail (state-independent, so not fragile).
        if not _in_dev_repo():
            self.skipTest("dev-repo-only test: no sdlc-studio/ workspace at the expected "
                          "root (running from an installed copy)")
        r = gate.run_gate(str(REPO))
        self.assertIsInstance(r["ok"], bool)
        self.assertEqual(len(r["checks"]), 12)
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
        if not _in_dev_repo():
            self.skipTest("dev-repo-only test: no sdlc-studio/ workspace at the expected "
                          "root (running from an installed copy)")
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

    def test_truncated_lane_states_sampled_fraction(self) -> None:
        # '12/12 killed (2621 truncated)' reads stronger than 0.5% coverage is;
        # the lane must state the sampled fraction whenever truncation occurred
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, {"summary": {"applied": 12, "killed": 12, "survived": 0,
                                              "errors": 0, "truncated": 2621,
                                              "enumerated": 2633}})
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            detail = report["checks"][0]["detail"]
            self.assertIn("12/2633 enumerated sampled", detail)
            self.assertIn("%", detail)

    def test_untruncated_lane_detail_unchanged(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, {"summary": {"applied": 5, "killed": 5, "survived": 0,
                                              "errors": 0, "truncated": 0,
                                              "enumerated": 5}})
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            self.assertNotIn("sampled", report["checks"][0]["detail"])

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

    def test_hash_stale_report_never_reads_pass(self) -> None:
        # CR0146: same rev, edited target - content hashes catch what rev cannot.
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "sdlc-studio").mkdir(parents=True)
            target = root / "code.py"
            target.write_text("x = 2\n", encoding="utf-8")
            import json as _json
            local = root / "sdlc-studio" / ".local"
            local.mkdir()
            (local / "mutation-report.json").write_text(_json.dumps(
                {"target_hashes": {str(target): "0" * 64},
                 "summary": {"applied": 5, "killed": 5, "survived": 0,
                             "errors": 0, "unviable": 0, "truncated": 0}}), encoding="utf-8")
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertNotEqual(lane["status"], "pass")
            self.assertIn("STALE", lane["detail"])

    def test_hash_staleness_resolves_against_root_not_cwd(self) -> None:
        # critic finding: relative target paths must resolve against --root
        import os, tempfile, hashlib, json as _json
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "proj"
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            target = root / "code.py"
            target.write_text("x = 2\n", encoding="utf-8")
            h = hashlib.sha256(target.read_bytes()).hexdigest()
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(_json.dumps(
                {"target_hashes": {"code.py": h},
                 "summary": {"applied": 1, "killed": 1, "survived": 0,
                             "errors": 0, "unviable": 0, "truncated": 0}}), encoding="utf-8")
            old_cwd = os.getcwd()
            os.chdir(t)   # a sibling dir, NOT the project root
            try:
                report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            finally:
                os.chdir(old_cwd)
            self.assertEqual(report["checks"][0]["status"], "pass",
                             report["checks"][0]["detail"])



class AdvisoryRegistryTests(unittest.TestCase):
    """Every lane that reads not-run (advisory) when its evidence is absent
    must be registered, so the upgrade capability digest can name it - the
    registry rots silently otherwise."""

    def test_every_advisory_when_absent_lane_is_registered(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "sdlc-studio").mkdir()
            for name, fn in gate.DEFAULT_CHECKS.items():
                try:
                    res = fn(str(t))
                except Exception:  # noqa: BLE001 - a lane needing richer state is not this probe's target
                    continue
                if (isinstance(res, dict) and not res.get("blocking", True)
                        and res.get("count") and "not run" in str(res.get("detail", ""))):
                    self.assertIn(name, gate.ADVISORY_WHEN_ABSENT,
                                  f"lane '{name}' reads not-run when absent but is unregistered")

    def test_registry_entries_carry_since_and_baseline(self):
        for name, meta in gate.ADVISORY_WHEN_ABSENT.items():
            self.assertRegex(meta["since"], r"^\d+\.\d+\.\d+$", name)
            self.assertTrue(meta["baseline"], name)


class ConventionsErrorBlocksTests(unittest.TestCase):
    """A mis-shaped conventions block must FAIL the gate, not disable the
    drift-detecting lane as a benign warn - fail loud has to survive the
    gate's one-buggy-check-must-not-abort containment."""

    def test_conventions_error_fails_the_gate(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            sd = root / "sdlc-studio" / "change-requests"
            sd.mkdir(parents=True)
            (sd / "CR0001-x.md").write_text(
                "# CR-0001: x\n\n> **Status:** Proposed\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| CR-0001 | x | Proposed |\n", encoding="utf-8")
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "conventions:\n  status_column: State\n",  # scalar: the wrong shape
                encoding="utf-8")
            try:
                import yaml  # noqa: F401
            except ImportError:
                self.skipTest("PyYAML absent - conventions degrade to defaults")
            report = gate.run_gate(str(root), checks=None, only=["reconcile"])
            lane = report["checks"][0]
            self.assertEqual(lane["status"], "error")
            self.assertTrue(lane["blocking"], lane)     # config error blocks
            self.assertFalse(report["ok"])              # gate FAILs, not green

    def test_ordinary_crash_still_contained_nonblocking(self):
        def boom(root):
            raise RuntimeError("kaboom")
        r = gate.run_gate(".", checks={"boom": boom})
        self.assertTrue(r["ok"])  # unchanged containment for non-config bugs
