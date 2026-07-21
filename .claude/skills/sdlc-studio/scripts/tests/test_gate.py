"""Unit tests for gate.py - the portable CI quality gate (CR0046)."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the sibling helper
import gitutil  # noqa: E402 - confined git for the fixture repos below
import workspace  # noqa: E402 - the shared "am I in the dev repo?" check

SCRIPT = Path(__file__).resolve().parent.parent / "gate.py"
REPO = Path(__file__).resolve().parents[5]  # repo root (holds sdlc-studio/ artifacts)

#: The dev-repo check now has ONE definition, in `tests/workspace.py`. This alias keeps the
#: local call sites reading as they did; the rule itself is no longer duplicated here (BG0209).
#: Run from an installed copy, `parents[5]` is the home dir with no workspace, so the real-
#: wrapper tests below SKIP visibly rather than failing on environment (BG0069).
_in_dev_repo = workspace.in_dev_repo


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


# The real gate over this repo costs ~35s (now ~7s), and this file used to pay it TWICE - once
# to assert the result's shape, once to discover that `main` returns 0 or 1. That was 71s of a
# 153s suite. Exactly ONE unstubbed end-to-end run is kept, deliberately: it is the only thing
# proving the real lanes wire up and return the documented shape, and a cached shape assertion
# cannot replace it.
#
# The guard is installed at MODULE scope and REFUSES a second one, rather than counting within a
# single class. The adversarial review of RUN-01KY1WCR killed the first attempt at this: the
# structural check matched the literal `gate.run_gate(str(REPO))`, but the test US0284 deleted
# was spelled `gate.main(["--root", str(REPO), ...])` - so pasting that exact test back into a
# neighbouring class restored the full cost (7.7s -> 14.7s) with both guards silent. Every route
# to a full run goes through this module global, including `cmd_gate`'s, so refusing here catches
# any spelling, in any class, and - once installed - in any module that runs after this one.
# That last clause is the whole point and is why nothing restores the original: see the note
# below the guard. A stubbed `run_gate` is not a real run and is not counted.
_REAL_FULL_GATE_RUNS: list[str] = []
_ORIG_RUN_GATE = gate.run_gate


def _guarded_run_gate(root=".", *a, **kw):
    if str(root) == str(REPO) and kw.get("checks") is None and not kw.get("only"):
        _REAL_FULL_GATE_RUNS.append(str(root))
        if len(_REAL_FULL_GATE_RUNS) > 1:
            raise AssertionError(
                "This process has already made its ONE real full-gate run over this repo, in "
                "test_gate.py. That budget is process-wide and deliberate: US0284 removed a "
                "duplicate that cost 35s of the suite, and the guard is not torn down between "
                "modules because handing it back let the duplicate return in a later module "
                "unnoticed. Nothing is wrong with your test - it just needs the result rather "
                "than a second run. Import test_gate and read "
                "GateRealWrapperTests._report(), or scope your call (`only=`/`checks=`), or "
                "stub `run_gate` as test_main_maps_result_to_exit_code_without_rerunning does. "
                "If a second real run is genuinely required, change this guard on purpose.")
    return _ORIG_RUN_GATE(root, *a, **kw)


gate.run_gate = _guarded_run_gate


# The guard is deliberately NOT torn down. It was, briefly: a `tearDownModule` restoring the
# original was added so an unrelated module making its own real run would not fail with a
# message about this file's budget. That handed the guard away - 59 of this suite's 98 test
# modules sort after `test_gate`, and a full run placed in any of them took the suite from
# 7.9s to 14.8s, green. Exactly the doubling US0284 removed, one module over and undetected. The
# process-wide budget IS the contract; the message below carries the explanation instead, so a
# reader who trips it is told what to do rather than blamed.


class GateRealWrapperTests(unittest.TestCase):
    _real_report: dict | None = None

    @classmethod
    def _report(cls) -> dict:
        """The one real run, made on FIRST demand rather than in setUpClass, so a test in this
        class that only needs a stub does not pay 35 seconds to get there. Running the stubbed
        exit-code test alone costs milliseconds; running the class costs one real gate.

        The dev-repo guard lives HERE, not only at the call sites, so a future test that reaches
        for the real run inherits it instead of having to remember it (BG0237). Reaching the real
        gate is exactly what cannot work from an installed copy, so the one place that reaches it
        is the one place the rule belongs.
        """
        if not _in_dev_repo():
            raise unittest.SkipTest(
                "dev-repo-only: the real gate run needs an sdlc-studio/ workspace at the "
                "expected root (running from an installed copy)")
        if cls._real_report is None:
            cls._real_report = gate.run_gate(str(REPO))
        return cls._real_report

    def test_the_real_gate_runs_once_per_class(self) -> None:
        """The saving itself, pinned. Counts FULL runs over this repo across the whole MODULE, so
        re-introducing a second end-to-end run - in any class, by any spelling - fails rather than
        only showing up as a slower suite nobody times.

        No dev-repo guard here: `_report()` carries it, so the rule has one home (BG0237).
        """
        self.assertIsNotNone(self._report())
        self.assertEqual(len(_REAL_FULL_GATE_RUNS), 1)

    def test_main_maps_result_to_exit_code_without_rerunning(self) -> None:
        """`main` returns 0 on a green report and 1 on a red one. That is main's OWN mapping,
        and a stub proves it in milliseconds; the previous test spent 35 seconds running the
        real gate to observe an exit code it then only asserted was 0 or 1."""
        orig = gate.run_gate
        seen: list[dict] = []

        def _stub(root=".", **kw):
            seen.append({"root": root, **kw})
            return _stub.report

        try:
            gate.run_gate = _stub
            _stub.report = {"ok": True, "checks": []}
            self.assertEqual(gate.main(["--root", str(REPO), "--format", "json"]), 0)
            _stub.report = {"ok": False, "checks": []}
            self.assertEqual(gate.main(["--root", str(REPO), "--format", "json"]), 1)
        finally:
            gate.run_gate = orig
        self.assertEqual(len(seen), 2)          # main ran the gate, it did not skip it
        self.assertEqual(seen[0]["root"], str(REPO))   # ...and passed the root through

    def test_a_second_real_full_gate_run_is_refused_by_any_route(self) -> None:
        """The guard's MECHANISM, not just the case that prompted it (L-0138).

        The first version of this test was a regex for the literal `gate.run_gate(str(REPO))`.
        The adversarial review pasted the DELETED test back verbatim - spelled
        `gate.main(["--root", str(REPO), ...])` - into a neighbouring class and both guards
        stayed silent while the suite went 7.7s -> 14.7s. So this exercises BOTH routes, and
        neither actually runs a gate: the guard refuses before delegating.
        """
        saved = list(_REAL_FULL_GATE_RUNS)
        try:
            _REAL_FULL_GATE_RUNS[:] = ["a run already happened"]
            with self.assertRaises(AssertionError):
                gate.run_gate(str(REPO))                       # the direct route
            _REAL_FULL_GATE_RUNS[:] = ["a run already happened"]
            with self.assertRaises(AssertionError):
                gate.main(["--root", str(REPO), "--format", "json"])   # the route that escaped
        finally:
            _REAL_FULL_GATE_RUNS[:] = saved

    def test_the_guard_does_not_fire_on_a_scoped_or_stubbed_run(self) -> None:
        """The other half: a guard that refused everything would pass the test above while
        breaking every legitimate call. A scoped run over this repo, and a run over any other
        root, must not count towards the one-real-run budget."""
        saved = list(_REAL_FULL_GATE_RUNS)
        try:
            _REAL_FULL_GATE_RUNS[:] = ["a run already happened"]
            gate.run_gate(str(REPO), only=["index-derived"])   # scoped: not a full run
            with tempfile.TemporaryDirectory() as d:
                gate.run_gate(d)                               # another root: not this repo
            # str(REPO), NOT ".": with a relative root the first clause is already False, so the
            # `checks` clause is never reached and dropping it from the guard survived. Found by
            # the adversarial review as a surviving mutant on this very test.
            gate.run_gate(str(REPO), checks={"a": _fake(0)})    # injected registry: not real
            self.assertEqual(len(_REAL_FULL_GATE_RUNS), 1)     # ...none of them counted
        finally:
            _REAL_FULL_GATE_RUNS[:] = saved

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

    def test_dev_repo_detector_false_when_the_skill_is_not_under_that_root(self) -> None:
        # The SECOND half of the check, which the workspace-less case above cannot reach:
        # a root that has BOTH a sdlc-studio/ workspace and a .claude/skills/ is still not
        # the dev repo unless this skill actually lives under it. Without this, an installed
        # copy sitting beside any consuming project's workspace reads as the dev repo, and
        # the tests that skip there would run and fail on missing fixtures instead (BG0209).
        # Dropping `and skills.is_dir() and startswith(...)` survives every other test here.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sdlc-studio").mkdir()
            (root / ".claude" / "skills").mkdir(parents=True)
            self.assertFalse(_in_dev_repo(root))

    def test_default_checks_present(self) -> None:
        self.assertEqual(set(gate.DEFAULT_CHECKS),
                         {"conformance", "reconcile", "index-derived", "validate", "constitution",
                          "integrity", "duplicate-id", "provenance", "doc-coverage", "engagement-floor",
                          "disclosure", "doc-freshness", "mutation", "hook-enabled", "batch-size"})

    def test_real_wrappers_run_and_shape(self) -> None:
        # Exercises the real checks end-to-end against this repo; asserts structure,
        # not pass/fail (state-independent, so not fragile). Reads the ONE run made on first
        # demand rather than making a second one of its own, and inherits that helper's
        # dev-repo guard rather than repeating it (BG0237).
        r = self._report()
        self.assertIsInstance(r["ok"], bool)
        self.assertEqual(len(r["checks"]), 15)
        for c in r["checks"]:
            self.assertEqual(set(c), {"check", "count", "blocking", "status", "detail"})

    def test_reconcile_wrapper_counts_drift_not_dict_keys(self) -> None:
        # Regression (hermetic): detect_type returns a 6-key dict; the wrapper must count
        # ["drift"] items, not len(dict). Monkeypatch so it's state-independent.
        import reconcile
        orig = reconcile.detect_type
        orig_d = reconcile.derivable_request_drift
        reconcile.detect_type = lambda t, root: {
            "census_total": 0, "census_counts": {}, "row_counts": {},
            "index_exists": True, "index_summary": {}, "drift": [{"a": 1}, {"b": 2}]}
        # Stubbed too, or "hermetic" stops being true: the wrapper now also consults the
        # derivable-request sweep, which reads the live workspace.
        reconcile.derivable_request_drift = lambda root, explain=True: []
        try:
            count = gate._reconcile(str(REPO))["count"]
        finally:
            reconcile.detect_type = orig
            reconcile.derivable_request_drift = orig_d
        self.assertEqual(count, 2 * len(reconcile.DEFAULT_TYPES))  # 2 drift/type, not 6 keys

    def test_gate_counts_a_derivable_request_that_apply_can_clear(self) -> None:
        """The kind is assembled in the sweep, not in `detect_type`, so the gate could not see
        it: `gate` reported PASS on a tree where `reconcile detect` exited 1, which is how the
        regression this kind exists to catch could return unnoticed."""
        import reconcile
        orig, orig_d = reconcile.detect_type, reconcile.derivable_request_drift
        orig_e = gate.sdlc_md.two_backlog_enforced
        reconcile.detect_type = lambda t, root: {
            "census_total": 0, "census_counts": {}, "row_counts": {},
            "index_exists": True, "index_summary": {}, "drift": []}
        reconcile.derivable_request_drift = lambda root, explain=True: [
            {"id": "CR0001", "kind": "request-derivable", "blocked_by": None}]
        try:
            # The THIRD live dependency, stubbed so this is hermetic rather than dev-repo-only
            # (BG0237). `_reconcile` consults the sweep only when the two-backlog workflow is
            # enforced; from an installed copy that detector is False, the sweep never ran, and
            # this test failed on 0 != 1 for a reason that had nothing to do with what it pins.
            # Stubbing it keeps the test running everywhere; whether the detector is consulted
            # at all is pinned separately, both ways, by the paired test below.
            gate.sdlc_md.two_backlog_enforced = lambda root: True
            res = gate._reconcile(str(REPO))
        finally:
            reconcile.detect_type, reconcile.derivable_request_drift = orig, orig_d
            gate.sdlc_md.two_backlog_enforced = orig_e
        self.assertEqual(res["count"], 1, res)

    def test_gate_does_not_block_on_a_request_another_gate_refuses(self) -> None:
        """Reported in the detail, not counted.

        The reason is FRICTION, not impossibility: an RFC waiting on an open decision is clearable
        by a commit (close the row, or record an override), but not usually by the committer who
        trips the gate, and blocking the whole repo on a pending decision gets the gate bypassed.
        The cost is real - a delivered request behind a resolvable gate reports PASS - and
        `reconcile detect` still exits 1 on it.
        """
        import reconcile
        orig, orig_d = reconcile.detect_type, reconcile.derivable_request_drift
        orig_e = gate.sdlc_md.two_backlog_enforced
        reconcile.detect_type = lambda t, root: {
            "census_total": 0, "census_counts": {}, "row_counts": {},
            "index_exists": True, "index_summary": {}, "drift": []}
        reconcile.derivable_request_drift = lambda root, explain=True: [
            {"id": "RFC0001", "kind": "request-derivable", "blocked_by": "1 Open decision"}]
        try:
            # Stubbed for the same reason as the test above (BG0237): without it, an installed
            # copy skips the sweep entirely and the assertion fails on a missing detail string
            # rather than on the blocked/counted distinction it exists to pin.
            gate.sdlc_md.two_backlog_enforced = lambda root: True
            res = gate._reconcile(str(REPO))
        finally:
            reconcile.detect_type, reconcile.derivable_request_drift = orig, orig_d
            gate.sdlc_md.two_backlog_enforced = orig_e
        self.assertEqual(res["count"], 0, res)
        self.assertIn("awaiting another gate", res["detail"])

    def test_gate_ignores_derivable_requests_where_the_workflow_is_unenforced(self) -> None:
        """The wrapper's own `two_backlog_enforced` guard: both tests above run against the
        enforced repo, so neither could tell whether it was consulted."""
        import reconcile
        orig, orig_d = reconcile.detect_type, reconcile.derivable_request_drift
        orig_e = gate.sdlc_md.two_backlog_enforced
        reconcile.detect_type = lambda t, root: {
            "census_total": 0, "census_counts": {}, "row_counts": {},
            "index_exists": True, "index_summary": {}, "drift": []}
        reconcile.derivable_request_drift = lambda root, explain=True: [
            {"id": "CR0001", "kind": "request-derivable", "blocked_by": None}]
        try:
            gate.sdlc_md.two_backlog_enforced = lambda root: False
            off = gate._reconcile(str(REPO))["count"]
            gate.sdlc_md.two_backlog_enforced = lambda root: True
            on = gate._reconcile(str(REPO))["count"]
        finally:
            reconcile.detect_type, reconcile.derivable_request_drift = orig, orig_d
            gate.sdlc_md.two_backlog_enforced = orig_e
        self.assertEqual((off, on), (0, 1))   # paired, so neither half can pass vacuously

    def test_the_real_run_helper_refuses_from_an_installed_copy(self) -> None:
        """`_report()`'s own guard, pinned DIRECTLY because nothing else can reach it (L-0159).

        Deleting the guard was a surviving mutant while both callers guarded at their own call
        site: they skipped before ever reaching it, so it read as coverage while being pinned by
        nothing. Those call-site copies are now gone and this is the single home of the rule, so
        it needs a test that exercises it rather than one that skips past it.
        """
        cls = type(self)
        g = globals()
        orig_dev, orig_cache = g["_in_dev_repo"], cls._real_report
        try:
            g["_in_dev_repo"] = lambda *a, **k: False
            cls._real_report = None
            with self.assertRaises(unittest.SkipTest):
                cls._report()
        finally:
            g["_in_dev_repo"] = orig_dev
            cls._real_report = orig_cache

    def test_no_test_in_this_class_fails_from_an_installed_copy(self) -> None:
        """The MECHANISM, not the two tests that prompted it (L-0171).

        BG0237 was two tests reading live workspace state without declaring it, which FAILED from
        an installed copy on `0 != 1` - a consumer sees 2 failures in 3,409 with nothing saying
        the cause is location rather than code. Guarding just those two would fix the instances
        and leave the next one to be found by a consumer, which is how the omission happened in
        the first place: three siblings already carried the guard.

        So this runs every OTHER test in the class under the installed-copy condition and demands
        each either PASSES or SKIPS. Failing is the only outcome forbidden. A new real-wrapper
        test that reads live state is caught here however it is spelled, and the failure message
        names it.
        """
        cls = type(self)
        mine = self._testMethodName
        names = [n for n in unittest.TestLoader().getTestCaseNames(cls) if n != mine]
        self.assertGreater(len(names), 1, "the sweep found no siblings - it would pass vacuously")

        g = globals()
        orig_dev = g["_in_dev_repo"]
        orig_enf = gate.sdlc_md.two_backlog_enforced
        orig_cache = cls._real_report
        try:
            # Exactly what an installed copy presents: parents[5] is the home dir, so there is no
            # sdlc-studio/ workspace under it and the two-backlog detector is False.
            g["_in_dev_repo"] = lambda *a, **k: False
            gate.sdlc_md.two_backlog_enforced = lambda root: False
            cls._real_report = None
            suite = unittest.TestSuite(cls(n) for n in names)
            result = unittest.TestResult()
            suite.run(result)
        finally:
            g["_in_dev_repo"] = orig_dev
            gate.sdlc_md.two_backlog_enforced = orig_enf
            cls._real_report = orig_cache

        broken = [f"{t.id().rsplit('.', 1)[-1]}: {tb.strip().splitlines()[-1]}"
                  for t, tb in (result.failures + result.errors)]
        self.assertEqual(broken, [], "these fail from an installed copy - guard them with the "
                                     "dev-repo skip, or stub the live state they read: " +
                                     "; ".join(broken))

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

    # A COMPLETE retro: every required section, a real lesson, and every finding
    # dispositioned (one filed, one declined with a reason).
    COMPLETE_RETRO = """# RETRO-0005: batch
## Delivered
- US0001 - shipped
## What went well
- the gate held
## What was hard / what stalled
- the deploy was slow
## Lessons
- deploys need a preflight check
## Actions raised
| Finding | Disposition |
| --- | --- |
| the deploy was slow | BG0125 |
| flaky CI test | declined: tracked upstream, not ours to fix |
"""

    def test_close_gate_passes_with_a_complete_retro(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            rd = root / "sdlc-studio" / "retros"
            rd.mkdir(parents=True)
            (rd / "RETRO0005-batch.md").write_text(self.COMPLETE_RETRO, encoding="utf-8")
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            self.assertTrue(report["ok"])

    def test_close_gate_fails_a_retro_that_is_only_a_heading(self) -> None:
        """BG0123. This test previously asserted the OPPOSITE - it wrote `# RETRO-0005\\n`,
        a file with no content whatsoever, and required the gate to PASS it. The suite was
        guarding the bug: the leg globbed for a filename, so `touch` satisfied the one gate
        that existed to make the retrospective un-skippable, and any attempt to fix that
        would have been reported as a regression. Existence is not evidence (LL0023).
        """
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            rd = root / "sdlc-studio" / "retros"
            rd.mkdir(parents=True)
            (rd / "RETRO0005-batch.md").write_text("# RETRO-0005\n", encoding="utf-8")
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            self.assertFalse(report["ok"])
            leg = next(c for c in report["checks"] if c["check"] == "retro")
            self.assertEqual(leg["status"], "fail")
            self.assertTrue(leg["blocking"])


class ReleaseGateTests(unittest.TestCase):
    """CR0233: `gate --release` = the standard gate PLUS an EXECUTING verify_ac pass, as one
    exit code. Tagging on a red verify layer must mean ignoring a failing command, not
    misreading a passing-looking one (BG0104's process half)."""

    def _legs(self, root: Path, skip: str = "") -> None:
        """Lay down the four required document legs so the bound `review-legs` release lane is
        satisfied, letting each release test isolate the behaviour it targets. `skip` omits one
        leg to exercise an absent-and-unwaived required leg."""
        b = root / "sdlc-studio"
        b.mkdir(parents=True, exist_ok=True)
        for leg in ("prd", "trd", "tsd"):
            if leg != skip:
                (b / f"{leg}.md").write_text(f"# {leg.upper()}\n", encoding="utf-8")
        if skip != "personas":
            pdir = b / "personas"
            pdir.mkdir(exist_ok=True)
            (pdir / "maya.md").write_text("# Maya\n", encoding="utf-8")

    def _story(self, root: Path, verifier: str, verified: str = "") -> Path:
        self._legs(root)  # a release fixture needs its doc legs present (bound review-legs lane)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        p = sd / "US0001-x.md"
        body = ("# US0001: x\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                f"### AC1: works\n- **Verify:** {verifier}\n")
        if verified:
            body += f"- **Verified:** {verified}\n"
        p.write_text(body, encoding="utf-8")
        return p

    def test_release_fails_on_a_failing_verify_line(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell exit 1")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertFalse(r["ok"])
            lane = next(c for c in r["checks"] if c["check"] == "verify")
            self.assertEqual(lane["status"], "fail")
            self.assertTrue(lane["blocking"])
            self.assertIn("US0001", lane["detail"])   # named failure, not a bare count
            self.assertIn("AC1", lane["detail"])

    def test_release_passes_on_a_green_verify_line(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertTrue(r["ok"], r["checks"])
            self.assertEqual(r["checks"][0]["check"], "verify")

    def test_release_does_not_mutate_story_files_or_the_report(self) -> None:
        # The gate is read-only and is what the pre-commit hook runs: the lane must EXECUTE
        # the verifiers without back-annotating `- **Verified:**` or rewriting the report.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            story = self._story(root, "shell true")  # would flip Verified: none -> yes
            before = story.read_bytes()
            gate.run_gate(str(root), checks={}, release=True)
            self.assertEqual(story.read_bytes(), before)
            self.assertFalse((root / "sdlc-studio" / ".local" / "verify-report.json").exists())

    def test_release_executes_rather_than_trusting_a_stale_green_report(self) -> None:
        # A merged report carries stale greens forward; a stale green is the misread this
        # lane exists to kill. A green report over a red verifier must still FAIL.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell exit 1", verified="yes (2026-01-01)")
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True)
            (local / "verify-report.json").write_text(json.dumps({
                "generated_at": "2026-01-01T00:00:00Z", "dry_run": False,
                "stories": {"US0001-x": {"ac_count": 1, "verified": 1, "failed": 0,
                                         "stale": 0, "manual": 0, "passed": ["AC1"],
                                         "failures": [], "flips": []}}}), encoding="utf-8")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertFalse(r["ok"])

    def test_no_stories_is_not_a_vacuous_pass(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertFalse(r["ok"])
            self.assertIn("no stories", r["checks"][0]["detail"])

    def test_verify_lane_absent_without_release(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell exit 1")
            r = gate.run_gate(str(root), checks={"a": _fake(0)})
            self.assertNotIn("verify", [c["check"] for c in r["checks"]])
            self.assertTrue(r["ok"])  # the standard gate stays read-only and verifier-free

    def test_cli_release_flag_exits_one(self) -> None:
        # The whole point: ONE exit code. Exercises the argparse plumbing, not just run_gate.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell exit 1")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = gate.main(["--root", str(root), "--release", "--format", "json",
                                "--only", "verify,review-legs,changelog-fragments,versions"])
            self.assertEqual(rc, 1)

    def test_verify_lane_blocks_on_error(self) -> None:
        # A crashing verify lane means the gate proved nothing about the AC layer.
        self.assertIn("verify", gate.BLOCKING_ON_ERROR)


class ReleaseSelectionGuardTests(ReleaseGateTests):
    """BG0111 review F1: `--release` must not print a release verdict when the lane that
    DEFINES it was deselected. A green banner over a deselected verify lane is the
    passing-looking command this CR exists to kill - the same false-assurance class the
    unknown-check and no-checks-selected guards already refuse."""

    def test_skip_verify_under_release_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell exit 1")
            r = gate.run_gate(str(root), checks={"a": _fake(0)}, release=True, skip=["verify"])
            self.assertFalse(r["ok"])
            self.assertEqual(r["checks"][0]["check"], "selection")
            self.assertIn("verify", r["checks"][0]["detail"])

    def test_only_excluding_verify_under_release_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell exit 1")
            r = gate.run_gate(str(root), checks={"a": _fake(0)}, release=True, only=["a"])
            self.assertFalse(r["ok"])
            self.assertEqual(r["checks"][0]["check"], "selection")

    def test_cli_release_skip_verify_exits_one_and_prints_no_pass_banner(self) -> None:
        # Sam's F1 reproduction: this printed "gate --release: PASS" and exited 0 over a red AC.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell exit 1")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = gate.main(["--root", str(root), "--release", "--skip", "verify",
                                "--only", "hook-enabled"])
            out = buf.getvalue()
            self.assertEqual(rc, 1)
            self.assertNotIn("PASS", out.splitlines()[-1])
            self.assertNotIn("judgement items", out)

    def test_release_with_verify_selected_still_runs(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            r = gate.run_gate(str(root), checks={}, release=True,
                              only=["verify", "review-legs", "changelog-fragments", "versions"])
            self.assertTrue(r["ok"], r["checks"])


class ReleaseBlockedVerifierTests(ReleaseGateTests):
    """BG0111 review F2: a verifier the trust boundary REFUSED TO RUN is not a red AC. It is
    an unproven one - it must not read as either a failure of the code or as proof."""

    def _external_story(self, root: Path, verifier: str) -> Path:
        self._legs(root)  # release fixture: the bound review-legs lane needs the doc legs present
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        p = sd / "US0001-x.md"
        p.write_text("# US0001: x\n\n> **Status:** Done\n> **Provenance:** external\n\n"
                     f"## Acceptance Criteria\n\n### AC1: works\n- **Verify:** {verifier}\n",
                     encoding="utf-8")
        return p

    def test_blocked_verifier_is_named_blocked_not_red(self) -> None:
        # Sam's F2 reproduction: `shell true` on an external story reported "1 red AC(s)".
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._external_story(root, "shell true")   # would PASS if it were ever run
            r = gate.run_gate(str(root), checks={}, release=True)
            lane = r["checks"][0]
            self.assertFalse(r["ok"])                       # not proven -> not a green release
            self.assertNotIn("red AC", lane["detail"])      # ...but not a red AC either
            self.assertIn("BLOCKED", lane["detail"])
            self.assertIn("--allow-external", lane["detail"])
            self.assertIn("US0001::AC1", lane["detail"])

    def test_allow_external_runs_the_blocked_verifier_green(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._external_story(root, "shell true")
            r = gate.run_gate(str(root), checks={}, release=True, allow_external=True)
            self.assertTrue(r["ok"], r["checks"])           # a green release IS reachable

    def test_allow_external_still_fails_a_genuinely_red_external_ac(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._external_story(root, "shell exit 1")
            r = gate.run_gate(str(root), checks={}, release=True, allow_external=True)
            self.assertFalse(r["ok"])
            self.assertIn("red AC", r["checks"][0]["detail"])

    def test_red_and_blocked_are_reported_separately(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._external_story(root, "shell true")       # blocked
            sd = root / "sdlc-studio" / "stories"
            (sd / "US0002-y.md").write_text(
                "# US0002: y\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: red\n- **Verify:** shell exit 1\n", encoding="utf-8")
            detail = gate.run_gate(str(root), checks={}, release=True)["checks"][0]["detail"]
            self.assertIn("1 red AC(s): US0002::AC1", detail)
            self.assertIn("BLOCKED", detail)
            self.assertIn("US0001::AC1", detail)

    def test_cli_allow_external_flag_wires_through(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._external_story(root, "shell true")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = gate.main(["--root", str(root), "--release", "--allow-external",
                                "--only", "verify,review-legs,changelog-fragments,versions"])
            self.assertEqual(rc, 0)


class ReleaseVacuityTests(ReleaseGateTests):
    """BG0111 review F3: the vacuity guard must reach the VERIFIER set, not stop at the story
    set. Zero executable ACs is nothing proved - so deleting a rotted Verify line must not be
    the way to turn the release gate green."""

    def test_zero_executable_acs_is_not_proof(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: x\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: no verifier at all\n- **Given:** a rotted line was deleted\n"
                "### AC2: human-checked\n- **Verify:** manual eyeball it\n", encoding="utf-8")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertFalse(r["ok"])
            # The deleted verifier is now caught per-story as UNSPECIFIED, and named - not
            # conflated with the declared-manual AC2 into one repo-wide "no executable" count.
            self.assertIn("unspecified", r["checks"][0]["detail"])
            self.assertIn("US0001", r["checks"][0]["detail"])

    def test_one_executable_ac_among_manual_ones_still_proves_something(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._legs(root)  # release-ready: satisfy the bound review-legs lane
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: x\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: executable\n- **Verify:** shell true\n"
                "### AC2: human-checked\n- **Verify:** manual eyeball it\n", encoding="utf-8")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertTrue(r["ok"], r["checks"])
            self.assertIn("1 manual", r["checks"][0]["detail"])


class ReleasePerStoryVacuityTests(ReleaseGateTests):
    """CR0237: the vacuity guard is PER-STORY, not repo-wide. verify_ac distinguishes a story's
    UNSPECIFIED ACs (no Verify: line - an omission) from its DECLARED-manual ACs (a judgement
    call). One green executable AC anywhere used to let every verifier-less story ride along, so
    a grandfathered story with a DELETED Verify line still reached a green release gate - the
    last route by which a rotted verify layer reaches a tag. The guard now names the omission
    story-by-story, while an honestly all-manual story is not over-fired on."""

    def _grandfathered(self, root: Path) -> Path:
        """A story whose ACs carry NO Verify: line at all (a rotted verifier deleted, not fixed)."""
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        p = sd / "US0001-grandfathered.md"
        p.write_text(
            "# US0001: grandfathered\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
            "### AC1: was verified once\n- **Given:** a rotted Verify line was deleted\n"
            "### AC2: also bare\n- **Then:** still no verifier\n", encoding="utf-8")
        return p

    def test_grandfathered_deleted_verify_no_longer_reaches_green(self) -> None:
        # THE RED (the CR0237 hole): a grandfathered story with deleted Verify lines rode along
        # on another story's one green executable AC. Repo-wide `executable = acs - manual` was
        # > 0, so the gate passed. Per-story, the omission is now caught and named.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._legs(root)
            self._grandfathered(root)
            sd = root / "sdlc-studio" / "stories"
            (sd / "US0002-green.md").write_text(
                "# US0002: green\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: executable\n- **Verify:** shell true\n", encoding="utf-8")
            r = gate.run_gate(str(root), checks={}, release=True)
            lane = next(c for c in r["checks"] if c["check"] == "verify")
            self.assertFalse(r["ok"])                       # the hole is closed
            self.assertEqual(lane["status"], "fail")
            self.assertIn("unspecified", lane["detail"])
            self.assertIn("US0001", lane["detail"])         # the omission is named
            self.assertNotIn("US0002", lane["detail"])      # the green story is not over-fired on

    def test_all_manual_story_still_reaches_green(self) -> None:
        # The trap to avoid: a story whose ACs are ALL declared `Verify: manual` is honestly
        # declaring human verification. It must PASS - the guard fires on omission, not on a
        # declared judgement call.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._legs(root)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0001-manual.md").write_text(
                "# US0001: manual\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: human check\n- **Verify:** manual confirm the dashboard loads\n"
                "### AC2: human check\n- **Verify:** manual confirm the export\n", encoding="utf-8")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertTrue(r["ok"], r["checks"])           # all-manual is not over-fired on
            self.assertIn("2 manual", r["checks"][0]["detail"])

    def test_manual_and_unspecified_are_separate_report_counts(self) -> None:
        # The report-shape change: an omitted Verify line and a declared `Verify: manual` are no
        # longer summed into one bucket. Reverting the split reddens this.
        import verify_ac
        with tempfile.TemporaryDirectory() as t:
            story = Path(t) / "US0001-x.md"
            story.write_text(
                "# US0001: x\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: declared manual\n- **Verify:** manual eyeball it\n"
                "### AC2: omitted\n- **Given:** no verifier\n", encoding="utf-8")
            rep = verify_ac.verify_story(story, dry_run=True, timeout=5, repo_root=Path(t))
            self.assertEqual(rep.manual, 1)         # only the DECLARED-manual AC
            self.assertEqual(rep.unspecified, 1)    # the omission is its own count
            self.assertEqual(rep.failed, 0)


class ReviewLegsGateTests(ReleaseGateTests):
    """BG0110: a required DOCUMENT leg (PRD/TRD/TSD/Persona) that is ABSENT and UNWAIVED must
    FAIL the release gate. A prose review can call a missing leg 'optional polish'; the gate
    cannot be talked around - only a present artefact or a recorded waiver turns it green. The
    CODE leg is out of scope (has no single testable artefact - decision D0022)."""

    def _record_waiver(self, root: Path, leg: str, rationale: str = "out of scope here") -> str:
        import decisions
        return decisions.record_waiver(root, f"leg:{leg}", rationale)["id"]

    def test_missing_tsd_no_waiver_fails_release(self) -> None:
        # the Verify oracle: a project missing tsd.md with no waiver FAILS the lane
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._legs(root, skip="tsd")   # prd/trd/personas present; tsd absent
            self._story(root, "shell true")  # verify lane itself is green
            # _story lays all four legs, so re-remove tsd to model the absence
            (root / "sdlc-studio" / "tsd.md").unlink()
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertFalse(r["ok"])
            lane = next(c for c in r["checks"] if c["check"] == "review-legs")
            self.assertEqual(lane["status"], "fail")
            self.assertTrue(lane["blocking"])
            self.assertIn("tsd", lane["detail"])

    def test_recording_a_waiver_turns_it_green(self) -> None:
        # ...and recording a waiver against a decision id turns the lane GREEN
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            (root / "sdlc-studio" / "tsd.md").unlink()   # absent
            did = self._record_waiver(root, "tsd", "single-repo; per-story Verify: discipline")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertTrue(r["ok"], r["checks"])
            lane = next(c for c in r["checks"] if c["check"] == "review-legs")
            self.assertEqual(lane["status"], "pass")
            self.assertIn("waived", lane["detail"])
            self.assertIn(did, lane["detail"])

    def test_all_legs_present_passes_and_states_code_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")   # lays all four legs
            r = gate.run_gate(str(root), checks={}, release=True)
            lane = next(c for c in r["checks"] if c["check"] == "review-legs")
            self.assertEqual(lane["status"], "pass")
            self.assertIn("D0022", lane["detail"])   # names the CODE-leg exclusion and its decision

    def test_review_legs_lane_absent_without_release(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._legs(root, skip="tsd")
            r = gate.run_gate(str(root), checks={"a": _fake(0)})
            self.assertNotIn("review-legs", [c["check"] for c in r["checks"]])
            self.assertTrue(r["ok"])   # a missing leg mid-project is not a standard-gate failure

    def test_review_legs_blocks_on_error(self) -> None:
        self.assertIn("review-legs", gate.BLOCKING_ON_ERROR)

    def test_deselecting_review_legs_under_release_is_refused(self) -> None:
        # the lane cannot be skipped away: a release PASS over an unexamined leg set is the
        # false-assurance class this lane exists to refuse
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            r = gate.run_gate(str(root), checks={}, release=True, skip=["review-legs"])
            self.assertFalse(r["ok"])
            self.assertEqual(r["checks"][0]["check"], "selection")
            self.assertIn("review-legs", r["checks"][0]["detail"])

    def test_a_leg_named_in_prose_only_does_not_pass(self) -> None:
        # the defect: a decision that merely MENTIONS the leg is not a waiver for it
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            (root / "sdlc-studio" / "tsd.md").unlink()
            import decisions
            decisions.add(root, "TSD leg is optional polish, not a gap", "we decided so")
            r = gate.run_gate(str(root), checks={}, release=True)
            self.assertFalse(r["ok"])   # prose reclassification cannot green the lane


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

    def test_refused_report_is_not_a_clean_sweep(self) -> None:
        # a refused run applies no mutant, so its summary is all zeros - rendering
        # that as '0/0 mutations killed' reads as assurance where none was gathered
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, {"refused": True, "baseline": "fail",
                                  "remedy": "a red baseline proves nothing: clean the tree",
                                  "summary": {"applied": 0, "killed": 0, "survived": 0,
                                              "errors": 0, "truncated": 0}})
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertNotIn("0/0 mutations killed", lane["detail"])
            self.assertNotEqual(lane["status"], "pass")

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


class MutationCoverageTests(unittest.TestCase):
    """BG0238: the lane judges COVERAGE of a surface from the accumulating per-run ledger,
    not the freshness of one blob. A per-file entry is keyed on that file's content hash, so
    it survives later commits that touch other files - which is what lets evidence gathered
    per unit during a build still be readable at the close."""

    def _root(self, t, ledger=None, report=None):
        import json as _json
        root = Path(t)
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True)
        if report is not None:
            (local / "mutation-report.json").write_text(_json.dumps(report), encoding="utf-8")
        if ledger is not None:
            (local / "mutation-runs.json").write_text(
                ledger if isinstance(ledger, str) else _json.dumps(ledger), encoding="utf-8")
        return root

    @staticmethod
    def _sha(path: Path) -> str:
        import hashlib
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _entry(target, digest, **kw):
        e = {"target": target, "hash": digest, "git_rev": "0" * 40,
             "generated_at": "2026-07-21T00:00:00Z",
             "summary": {"applied": 2, "killed": 2, "survived": 0, "errors": 0, "unviable": 0}}
        e.update(kw)
        return e

    CLEAN = {"summary": {"applied": 2, "killed": 2, "survived": 0,
                         "errors": 0, "unviable": 0, "truncated": 0}}

    def _commit_all(self, root, msg="c"):
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", msg], cwd=root)

    def test_per_unit_evidence_survives_later_commits_to_other_files(self) -> None:
        """The filed bug: two files mutated in turn during a build, both committed, tree clean
        at the close. Neither file has changed since it was mutated, so the lane reads both as
        covered and PASSes - where a whole-blob git_rev stamp read the whole thing STALE."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            (root / "b.py").write_text("def b():\n    return 2\n", encoding="utf-8")
            self._commit_all(root, "unit one")
            ledger = {"version": 1, "dropped": 0, "entries": [
                self._entry("a.py", self._sha(root / "a.py")),
                self._entry("b.py", self._sha(root / "b.py"))]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps({**self.CLEAN, "git_rev": "0" * 40}), encoding="utf-8")
            (root / "note.md").write_text("later work\n", encoding="utf-8")
            self._commit_all(root, "unit two")
            lane = gate._mutation(str(root))
            self.assertEqual(lane["count"], 0, lane["detail"])
            self.assertIn("2/2", lane["detail"])
            self.assertNotIn("STALE", lane["detail"])

    def test_a_changed_file_with_no_entry_reads_uncovered_and_is_named(self) -> None:
        """An unmutated file in the changed surface is uncovered, named, and counted, while
        its mutated sibling stays covered."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            (root / "a.py").write_text("def a():\n    return 1  # unit\n", encoding="utf-8")
            (root / "c.py").write_text("def c():\n    return 3\n", encoding="utf-8")
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", self._sha(root / "a.py"))]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertIn("1/2", lane["detail"])
            self.assertIn("c.py", lane["detail"])
            self.assertFalse(lane["blocking"])       # advisory, always

    def test_a_file_edited_since_it_was_mutated_reads_stale_and_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", self._sha(root / "a.py"))]}
            (root / "a.py").write_text("def a():\n    return 99\n", encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertIn("STALE", lane["detail"])
            self.assertIn("a.py", lane["detail"])

    def test_coverage_degrades_to_the_ledger_when_git_cannot_name_a_surface(self) -> None:
        """A repo with no commits cannot answer `git diff HEAD`. The lane must then judge the
        ledger's own recorded files rather than raise or claim a surface it does not have."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", self._sha(root / "a.py"))]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps({**self.CLEAN, "git_rev": "0" * 40}), encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertEqual(lane["count"], 0, lane["detail"])
            self.assertIn("1/1", lane["detail"])

    def test_an_unreadable_ledger_never_raises_into_the_gate(self) -> None:
        """A corrupt ledger degrades to no coverage claim; the lane still returns."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, ledger="{not json", report=self.CLEAN)
            lane = gate._mutation(str(root))
            self.assertFalse(lane["blocking"])
            self.assertNotIn("covers", lane["detail"])

    def test_uncovered_surface_never_blocks_the_gate(self) -> None:
        """RFC0048 D3 / BG0212: the mutation lane reports and never refuses a close."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            (root / "c.py").write_text("def c():\n    return 3\n", encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps({"version": 1, "dropped": 0, "entries": []}), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertFalse(lane["blocking"])
            self.assertTrue(report["ok"])
            self.assertNotEqual(lane["status"], "pass")

    def test_an_entry_with_no_recorded_hash_is_not_evidence(self) -> None:
        """A null hash means the target could not be read when it was mutated. Paired with a
        target that cannot be read NOW either, two unknowns compare equal - and 'both
        unreadable' must not read as 'unchanged since the run'."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            ledger = {"version": 1, "dropped": 0, "entries": [self._entry("gone.py", None)]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertIn("STALE", lane["detail"])
            self.assertEqual(lane["count"], 1, lane["detail"])

    def test_the_surface_extensions_match_the_mutator_s_own_profiles(self) -> None:
        """The lane calls a changed file uncovered only if mutation.py could have mutated it.
        Two hand-kept copies of that list would drift into a false 'no evidence' claim."""
        import importlib.util
        path = SCRIPT.parent / "mutation.py"
        spec = importlib.util.spec_from_file_location("mutation_for_gate_test", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(gate._MUTATABLE_SUFFIXES, set(mod.PROFILES))

    def test_a_root_below_the_repository_top_reads_as_unknown_not_clean(self) -> None:
        """git names changed paths relative to the repository TOP, so from a root below it the
        surface cannot be read in this gate's frame. That is 'unknown' (None), a different
        claim from 'nothing changed' ([]) - the surface is dirty in both fixtures here."""
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            gitutil.git(["init", "-q"], cwd=repo)
            sub = repo / "sub"
            sub.mkdir()
            (sub / "x.py").write_text("def x():\n    return 1\n", encoding="utf-8")
            self._commit_all(repo)
            (sub / "x.py").write_text("def x():\n    return 2\n", encoding="utf-8")
            self.assertIsNone(gate._mutation_changed_surface(str(sub)))
            self.assertEqual(gate._mutation_changed_surface(str(repo)), ["sub/x.py"])

    def test_a_long_gap_list_is_bounded_and_says_how_many_it_did_not_print(self) -> None:
        """Truncating the names silently would read as 'that is all of them'."""
        line = gate._name_list([f"pkg/f{i}.py" for i in range(5)])
        self.assertEqual(line.count(".py"), 3)
        self.assertIn("+2 more", line)
        self.assertEqual(gate._name_list(["a.py", "b.py"]), "a.py, b.py")   # no bound noise

    def test_a_raising_coverage_probe_never_breaks_the_lane(self) -> None:
        """Coverage is advisory: whatever it hits, the lane still returns a verdict."""
        orig = gate._mutation_coverage

        def _boom(root, data):
            raise RuntimeError("kaboom")
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, report=self.CLEAN)
            try:
                gate._mutation_coverage = _boom
                lane = gate._mutation(str(root))
            finally:
                gate._mutation_coverage = orig
            self.assertFalse(lane["blocking"])
            self.assertIn("2/2 mutations killed", lane["detail"])

    def test_test_files_are_not_counted_as_uncovered_surface(self) -> None:
        """The surface is production code: a changed test file is the assertion, not a
        mutation target, so it must not read as missing evidence for ever."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            (root / "test_a.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", self._sha(root / "a.py"))]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertNotIn("test_a.py", lane["detail"])
            self.assertEqual(lane["count"], 0, lane["detail"])


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


class RaisingCheckTests(unittest.TestCase):
    """A crashing check in a blocking lane must FAIL the gate - recording it non-blocking
    converted a red gate to green (the vacuous-PASS class at a new location)."""

    def _raiser(self, root):
        raise RuntimeError("boom")

    def test_raising_blocking_lane_fails_the_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = gate.run_gate(d, checks={"validate": self._raiser})
            self.assertFalse(res["ok"])
            row = next(r for r in res["checks"] if r["check"] == "validate")
            self.assertEqual(row["status"], "error")
            self.assertTrue(row["blocking"])

    def test_raising_advisory_lane_still_warns_not_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = gate.run_gate(d, checks={"disclosure": self._raiser})
            self.assertTrue(res["ok"])
            row = next(r for r in res["checks"] if r["check"] == "disclosure")
            self.assertEqual(row["status"], "error")
            self.assertFalse(row["blocking"])

    def test_every_blocking_default_lane_is_declared_blocking_on_error(self) -> None:
        # The declaration must not drift from the lanes' own blocking returns: any DEFAULT
        # check that returns blocking=True on a clean workspace must be in BLOCKING_ON_ERROR.
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir(parents=True)
            for name, fn in gate.DEFAULT_CHECKS.items():
                try:
                    r = fn(str(Path(d)))
                except Exception:
                    continue  # lanes needing more fixture than an empty tree
                if r.get("blocking"):
                    self.assertIn(name, gate.BLOCKING_ON_ERROR,
                                  f"{name} blocks on failure but not on crash")


class HookEnabledLaneTests(unittest.TestCase):
    """CR0202/US0113: warn when the tracked hook exists but is not enabled; silent elsewhere.
    Host git config is isolated: a machine's own global hooksPath must never colour these
    fixtures (critic finding - a contaminated global red-ed the suite)."""

    def setUp(self):
        import os
        self._env = {"GIT_CONFIG_GLOBAL": os.environ.get("GIT_CONFIG_GLOBAL"),
                     "GIT_CONFIG_SYSTEM": os.environ.get("GIT_CONFIG_SYSTEM")}
        os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
        os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"

    def tearDown(self):
        import os
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def _tree(self, d, with_hook=True, git=True, enabled=False):
        import subprocess
        root = Path(d)
        root.mkdir(parents=True, exist_ok=True)
        if with_hook:
            (root / ".githooks").mkdir(parents=True, exist_ok=True)
            (root / ".githooks" / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
        if git:
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            if enabled:
                subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", ".githooks"],
                               check=True)
        return root

    def test_hook_present_but_disabled_warns_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = gate._hook_enabled(str(self._tree(d)))
            self.assertEqual(r["count"], 1)
            self.assertFalse(r["blocking"])
            self.assertIn("enable-hooks.sh", r["detail"])

    def test_hook_enabled_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = gate._hook_enabled(str(self._tree(d, enabled=True)))
            self.assertEqual(r["count"], 0)

    def test_no_tracked_hook_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = gate._hook_enabled(str(self._tree(d, with_hook=False)))
            self.assertEqual(r["count"], 0)

    def test_non_git_dir_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = gate._hook_enabled(str(self._tree(d, git=False)))
            self.assertEqual(r["count"], 0)

    def test_lane_registered_and_advisory(self) -> None:
        self.assertIn("hook-enabled", gate.DEFAULT_CHECKS)
        self.assertNotIn("hook-enabled", gate.BLOCKING_ON_ERROR)


class EngagementFloorLaneTests(unittest.TestCase):
    """The engagement-floor lane is a blocking standard-gate lane by default, and advisory
    (never blocking) when the project sets `engagement_floor: judgement`."""

    def _unit(self, root, *, ac=False):
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        lines = ["# BG0500: sample", "", "> **Status:** Fixed",
                 "> **Affects:** a/one.py, a/two.py", ""]
        if ac:
            lines += ["## Acceptance Criteria", "", "### AC1: works", "- a criterion"]
        (d / "BG0500-sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_lane_registered_and_blocking(self) -> None:
        self.assertIn("engagement-floor", gate.DEFAULT_CHECKS)
        self.assertIn("engagement-floor", gate.BLOCKING_ON_ERROR)

    def test_multifile_no_ac_fails_the_lane(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            r = gate._engagement_floor(str(root))
            self.assertEqual(r["count"], 1)
            self.assertTrue(r["blocking"])

    def test_planning_present_passes_the_lane(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, ac=True)
            r = gate._engagement_floor(str(root))
            self.assertEqual(r["count"], 0)

    def test_judgement_mode_is_advisory_not_blocking(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - the judgement-mode config cannot be read")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "engagement_floor: judgement\n", encoding="utf-8")
            r = gate._engagement_floor(str(root))
            self.assertEqual(r["count"], 1)      # still reported
            self.assertFalse(r["blocking"])       # but never blocks
            # ...so the whole gate stays green over it.
            report = gate.run_gate(str(root), only=["engagement-floor"])
            self.assertTrue(report["ok"])


class HookEnabledEquivalentConfigTests(HookEnabledLaneTests):
    """Critic findings F2/F3: equivalent enabled configs must read enabled; foreign GIT_DIR
    env must not redirect the check."""

    def test_trailing_slash_hookspath_is_enabled(self) -> None:
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", ".githooks/"],
                           check=True)
            self.assertIsNone(gate.hook_enablement_gap(str(root)))

    def test_absolute_hookspath_to_same_dir_is_enabled(self) -> None:
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            subprocess.run(["git", "-C", str(root), "config", "core.hooksPath",
                            str((root / ".githooks").resolve())], check=True)
            self.assertIsNone(gate.hook_enablement_gap(str(root)))

    def test_foreign_git_dir_env_does_not_redirect_the_check(self) -> None:
        import os
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            fixture = self._tree(Path(d) / "fixture")          # hook present, NOT enabled
            other = Path(d) / "other"
            subprocess.run(["git", "init", "-q", str(other)], check=True)
            subprocess.run(["git", "-C", str(other), "config", "core.hooksPath", ".githooks"],
                           check=True)
            old = os.environ.get("GIT_DIR")
            os.environ["GIT_DIR"] = str(other / ".git")
            try:
                gap = gate.hook_enablement_gap(str(fixture))
            finally:
                if old is None:
                    os.environ.pop("GIT_DIR", None)
                else:
                    os.environ["GIT_DIR"] = old
            self.assertIsNotNone(gap, "check must evaluate the fixture, not GIT_DIR's repo")


class LessonsCloseGateTests(unittest.TestCase):
    """CR0236: the close loop is a mechanism, not doctrine. The close gate fails loud on a
    STALE LESSONS-SUMMARY.md (a lesson added or closed since it was last regenerated) and on
    an open lesson past its validity horizon, exactly as it fails loud on a missing retro."""

    FIXTURE = ("# Project Lessons\n\n**Last Updated:** 2026-01-01\n\n"
               "## L-0001: First lesson\n\n- **Added:** 2999-01-01\n- **Rule:** do X\n")

    def _log(self, root: Path, text: str | None = None) -> Path:
        p = root / "sdlc-studio" / ".local" / "lessons.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.FIXTURE if text is None else text, encoding="utf-8")
        (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
        return p

    def _retro(self, root: Path, rid: str = "RETRO0005") -> None:
        """A VALID retro fixture. These tests exercise the lessons lanes, not the retro leg,
        but the retro leg now reads content rather than globbing a filename (BG0123), so a
        bare `# RETRO0005` stub no longer satisfies it - and should not. The fixture has to
        be the artefact the gate actually asks for."""
        (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "retros" / f"{rid}-batch.md").write_text(
            f"""# {rid}: batch
## Delivered
- US0001 - shipped
## What went well
- it held
## What was hard / what stalled
- nothing notable
## Lessons
- keep the fixture honest
## Actions raised
| Finding | Disposition |
| --- | --- |
| nothing worth raising this batch | declined: no issue met the bar for an artefact |
""", encoding="utf-8")

    def _regen(self, root: Path) -> None:
        sys.path.insert(0, str(SCRIPT.parent))  # gate.py's own dir: the scripts/ package root
        import lessons
        with contextlib.redirect_stdout(io.StringIO()):
            lessons.main(["summary", "--project-file",
                          str(root / "sdlc-studio" / ".local" / "lessons.md")])

    def test_close_gate_fails_on_a_stale_summary(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root)  # a populated log, no summary ever generated
            self._retro(root)
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            self.assertFalse(report["ok"])
            lane = next(c for c in report["checks"] if c["check"] == "lessons-summary")
            self.assertEqual(lane["status"], "fail")
            self.assertTrue(lane["blocking"])

    def test_close_gate_passes_once_the_summary_is_regenerated(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root)
            self._retro(root)
            self._regen(root)
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            self.assertTrue(report["ok"], report["checks"])

    def test_close_gate_exit_codes_one_then_zero(self) -> None:
        """The AC in exit-code form: 1 on a stale summary, 0 once regenerated."""
        import argparse
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root)
            self._retro(root)
            args = argparse.Namespace(root=str(root), format="text", skip=None,
                                      only="retro,lessons-summary,lessons-validity",
                                      require_retro="RETRO0005")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(gate.cmd_gate(args), 1)
            self.assertIn("lessons-summary", out.getvalue())
            self._regen(root)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(gate.cmd_gate(args), 0)

    def test_a_lesson_closed_since_the_summary_was_written_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._log(root, self.FIXTURE + "\n## L-0002: Second\n\n"
                                               "- **Added:** 2999-01-01\n- **Rule:** do Y\n")
            self._regen(root)
            p.write_text(p.read_text(encoding="utf-8").replace(
                "- **Rule:** do Y", "- **Rule:** do Y\n- **Status:** Closed - obsolete"),
                encoding="utf-8")
            report = gate.run_gate(str(root), checks={}, require_lessons=True)
            self.assertFalse(report["ok"])
            lane = next(c for c in report["checks"] if c["check"] == "lessons-summary")
            self.assertIn("L-0002", lane["detail"])

    def test_an_expired_open_lesson_fails_the_close_gate(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root, "# Project Lessons\n\n## L-0001: Old\n\n"
                            "- **Review-by:** 2000-01-01\n- **Rule:** do X\n")
            self._regen(root)
            report = gate.run_gate(str(root), checks={}, require_lessons=True)
            self.assertFalse(report["ok"])
            lane = next(c for c in report["checks"] if c["check"] == "lessons-validity")
            self.assertEqual(lane["status"], "fail")
            self.assertTrue(lane["blocking"])
            self.assertIn("L-0001", lane["detail"])

    def test_a_horizon_less_open_lesson_fails_the_close_gate(self) -> None:
        """Review F1: the lane must ACT on `unstamped`, not merely narrate it. A lane that
        prints PASS while its own detail names a finding is the false-assurance class this
        gate exists to abolish - and a legacy log (no horizons anywhere) would close a sprint
        with the re-validation step never performed."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root, "# Project Lessons\n\n## L-0001: Undated\n\n- **Rule:** do X\n")
            self._regen(root)  # summary is current, so only the validity lane can fail
            report = gate.run_gate(str(root), checks={}, require_lessons=True)
            self.assertFalse(report["ok"])
            lane = next(c for c in report["checks"] if c["check"] == "lessons-validity")
            self.assertEqual(lane["status"], "fail")
            self.assertTrue(lane["blocking"])
            self.assertGreaterEqual(lane["count"], 1)  # the count is what makes it FAIL
            self.assertIn("L-0001", lane["detail"])

    def test_a_deleted_log_beside_a_populated_summary_is_refused(self) -> None:
        """Review F2: `rm .local/lessons.md` must not be a one-command defeat of the close
        gate. An absent log is only 'nothing to summarise' when the committed summary agrees
        that there is nothing; a summary still listing lessons with no log behind it is a
        contradiction, and the gate refuses rather than passing over it."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            log = self._log(root)
            self._regen(root)
            self.assertTrue(gate.run_gate(str(root), checks={}, require_lessons=True)["ok"])
            log.unlink()  # the one-command defeat
            report = gate.run_gate(str(root), checks={}, require_lessons=True)
            self.assertFalse(report["ok"])
            lane = next(c for c in report["checks"] if c["check"] == "lessons-summary")
            self.assertEqual(lane["status"], "fail")

    def test_a_greenfield_project_with_no_lessons_at_all_passes(self) -> None:
        # the honest N/A: no log, and a summary that agrees there is nothing (or none at all).
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._retro(root)
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            self.assertTrue(report["ok"], report["checks"])

    def test_require_retro_binds_the_lessons_lanes(self) -> None:
        """No new flag for an agent under effort pressure to forget: the close-gate command
        the doctrine already prescribes (`gate --require-retro`) carries the lessons lanes."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root)
            self._retro(root)
            names = {c["check"] for c in
                     gate.run_gate(str(root), checks={}, require_retro="RETRO0005")["checks"]}
            self.assertIn("lessons-summary", names)
            self.assertIn("lessons-validity", names)

    def test_lessons_lanes_are_absent_from_the_standard_gate(self) -> None:
        # the log is gitignored, so a teammate's clone has no log: a standard-gate lane
        # would false-fire on their machine. The lanes are bound to the CLOSE gate only.
        self.assertNotIn("lessons-summary", gate.DEFAULT_CHECKS)
        self.assertNotIn("lessons-validity", gate.DEFAULT_CHECKS)

    def test_deselecting_a_bound_lessons_lane_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root)
            self._retro(root)
            r = gate.run_gate(str(root), checks={"a": _fake(0)}, require_lessons=True,
                              skip=["lessons-summary"])
            self.assertFalse(r["ok"])
            self.assertEqual(r["checks"][0]["check"], "selection")
            self.assertIn("lessons-summary", r["checks"][0]["detail"])

    def _judgement(self, root: Path) -> None:
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "lessons:\n  loop: judgement\n", encoding="utf-8")

    def test_judgement_makes_the_lessons_summary_lane_advisory(self) -> None:
        # BG0166: the documented opt-out disarmed only the retro lane; it must disarm all three.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root)  # populated log, no summary -> summary lane would fail
            self._retro(root)
            self._judgement(root)
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            lane = next(c for c in report["checks"] if c["check"] == "lessons-summary")
            self.assertFalse(lane["blocking"], "the documented opt-out must disarm the summary lane")
            self.assertGreater(lane["count"], 0, "advisory must still REPORT - silence is not opt-out")
            self.assertTrue(report["ok"], "no blocking lane fails, so the close gate passes")

    def test_judgement_makes_the_lessons_validity_lane_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._log(root, "# Project Lessons\n\n## L-0001: Old\n\n"
                            "- **Review-by:** 2000-01-01\n- **Rule:** do X\n")
            self._regen(root)  # summary current; only the validity lane can fail
            self._retro(root)
            self._judgement(root)
            report = gate.run_gate(str(root), checks={}, require_retro="RETRO0005")
            lane = next(c for c in report["checks"] if c["check"] == "lessons-validity")
            self.assertFalse(lane["blocking"], "the documented opt-out must disarm the validity lane")
            self.assertGreaterEqual(lane["count"], 1, "advisory must still REPORT")
            self.assertTrue(report["ok"], "no blocking lane fails, so the close gate passes")

    def test_lessons_lanes_block_on_error(self) -> None:
        self.assertIn("lessons-summary", gate.BLOCKING_ON_ERROR)
        self.assertIn("lessons-validity", gate.BLOCKING_ON_ERROR)


class BoundLaneRegistryTests(unittest.TestCase):
    """Every lane a mode BINDS must be declared in BOUND_LANE_SUBJECT and must block on
    error. A bound lane is what makes its mode: the refusal message has to be able to name
    what a deselection would have printed a verdict over, and a bound lane that crashed
    proved nothing. Both registries rot silently otherwise - hence the sweep."""

    # (kwarg, the lanes it binds) - the modes run_gate offers
    MODES = [
        ("require_retro", ["retro", "lessons-summary", "lessons-validity"]),
        ("require_lessons", ["lessons-summary", "lessons-validity"]),
        ("require_handoff", ["handoff"]),
        ("release", ["verify", "review-legs"]),
        ("require_close", ["close-owed"]),
    ]

    def test_every_bound_lane_names_its_subject(self) -> None:
        for _mode, lanes in self.MODES:
            for lane in lanes:
                self.assertIn(lane, gate.BOUND_LANE_SUBJECT,
                              f"bound lane '{lane}' has no subject for the refusal message")

    def test_every_bound_lane_blocks_on_error(self) -> None:
        for lane in gate.BOUND_LANE_SUBJECT:
            self.assertIn(lane, gate.BLOCKING_ON_ERROR,
                          f"bound lane '{lane}' blocks on failure but not on crash")

    def test_no_bound_lane_is_in_the_standard_gate(self) -> None:
        # a mode's lane must not fire on a plain `gate` run (it would false-fire on a clone
        # with no retro/handoff due, and train agents to skim the output)
        for lane in gate.BOUND_LANE_SUBJECT:
            self.assertNotIn(lane, gate.DEFAULT_CHECKS, lane)

    def test_deselecting_any_bound_lane_is_refused(self) -> None:
        for mode, lanes in self.MODES:
            for lane in lanes:
                with self.subTest(mode=mode, lane=lane):
                    kw = {mode: True if mode in ("release", "require_lessons", "require_close")
                          else ("RETRO0001" if mode == "require_retro" else "HO0001")}
                    r = gate.run_gate(".", checks={"a": _fake(0)}, skip=[lane], **kw)
                    self.assertFalse(r["ok"])
                    self.assertEqual(r["checks"][0]["check"], "selection")
                    self.assertIn(lane, r["checks"][0]["detail"])

class ReviewCurrencyGateTests(unittest.TestCase):
    """CR0253: the sprint-close review was never gated - doc_freshness is advisory, and
    review-legs checks the docs EXIST, not that a review was RUN. --require-review binds a
    BLOCKING leg: reviews/LATEST.md must be at least as new as every artefact. Presence is not
    currency (BG0123's lesson, one leg over)."""

    def _ws(self, d):
        import os
        root = Path(d)
        (root / "sdlc-studio" / "reviews").mkdir(parents=True)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        bug = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        bug.write_text("# BG0001: x\n> **Status:** Open\n> **Severity:** Low\n## Summary\nx\n")
        return root, bug

    def _leg(self, root):
        import gate
        r = gate.run_gate(str(root), checks={}, require_review=True)
        return next(c for c in r["checks"] if c["check"] == "review-current")

    def test_missing_latest_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root, _ = self._ws(d)
            leg = self._leg(root)
            self.assertEqual(leg["status"], "fail")
            self.assertTrue(leg["blocking"])

    def test_stale_review_fails(self):
        import tempfile, os, time
        with tempfile.TemporaryDirectory() as d:
            root, bug = self._ws(d)
            lat = root / "sdlc-studio" / "reviews" / "LATEST.md"
            lat.write_text("# review\n")
            os.utime(lat, (time.time() - 100, time.time() - 100))   # LATEST older
            os.utime(bug, (time.time(), time.time()))               # artefact newer
            leg = self._leg(root)
            self.assertEqual(leg["status"], "fail", leg["detail"])
            self.assertIn("stale", leg["detail"])

    def test_current_review_passes(self):
        import tempfile, os, time
        with tempfile.TemporaryDirectory() as d:
            root, bug = self._ws(d)
            lat = root / "sdlc-studio" / "reviews" / "LATEST.md"
            lat.write_text("# review\n")
            os.utime(lat, (time.time() + 100, time.time() + 100))   # LATEST newest
            leg = self._leg(root)
            self.assertEqual(leg["status"], "pass", leg["detail"])


class CloseOwedGateLaneTests(unittest.TestCase):
    """The --require-close guard (US0165): a bound, blocking lane that refuses a push/release
    while a sprint close is owed. The soft nudge is on status/hint; this is the hard half."""

    def _story(self, root: Path, sid: str, st: str) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}-s.md").write_text(f"# {sid}: s\n\n> **Status:** {st}\n> **Points:** 2\n",
                                       encoding="utf-8")

    def _owed_project(self, root: Path) -> None:
        import close_owed
        (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
        self._story(root, "US0001", "Done")
        close_owed.stamp_baseline(root, date="2026-01-01")
        self._story(root, "US0005", "Done")  # later work, no retro -> owed

    def test_require_close_fails_when_a_close_is_owed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._owed_project(root)
            report = gate.run_gate(str(root), only=["close-owed"], require_close=True)
            self.assertFalse(report["ok"])

    def test_require_close_passes_once_a_retro_accounts_for_it(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._owed_project(root)
            (root / "sdlc-studio" / "retros" / "RETRO0002-r.md").write_text(
                "# RETRO-0002: s\n\n> **Batch:** US0005\n\n## Delivered\n- shipped\n",
                encoding="utf-8")
            report = gate.run_gate(str(root), only=["close-owed"], require_close=True)
            self.assertTrue(report["ok"])

    def test_close_owed_absent_from_the_plain_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._owed_project(root)
            report = gate.run_gate(str(root))  # no --require-close
            self.assertNotIn("close-owed", [c["check"] for c in report["checks"]])

    def test_require_close_help_does_not_claim_a_default_warning(self) -> None:
        # BG0171: the plain gate never runs close-owed, so the help must not say it "WARNS on
        # every gate by default" - that invites the operator to trust a nudge that never fires.
        parser = gate.build_parser()
        action = next(a for a in parser._actions if "--require-close" in a.option_strings)
        self.assertNotIn("WARNS on every gate", action.help)
        self.assertIn("plain gate never runs it", action.help)

    def test_require_close_fails_on_a_corrupt_baseline(self) -> None:
        # BG0155: a corrupt baseline must BLOCK the close gate, not pass as 'no baseline stamped'.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
            self._story(root, "US0005", "Done")
            (root / "sdlc-studio" / ".close-owed-baseline.json").write_text(
                '["US0005"]', encoding="utf-8")
            report = gate.run_gate(str(root), only=["close-owed"], require_close=True)
            self.assertFalse(report["ok"])


import json as _json  # noqa: E402
import subprocess  # noqa: E402


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _batch_repo(tmp, *, config=True, lines=30):
    """A git repo with one Done 2-point story delivered by one Refs-trailed commit
    changing `lines` lines, its id named in the open run-state batch."""
    root = Path(tmp)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True)
    (d / "US0001-x.md").write_text(
        "# US0001: x\n\n> **Status:** Done\n> **Points:** 2\n", encoding="utf-8")
    (root / "src.py").write_text("\n".join(f"line {i}" for i in range(lines)) + "\n",
                                 encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "feat: deliver x (US0001)\n\nRefs: US0001")
    local = root / "sdlc-studio" / ".local"
    local.mkdir(parents=True)
    (local / "run-state.json").write_text(_json.dumps(
        {"schema": 1, "run_id": "RUN-T", "started_at": "2026-07-16T10:00:00",
         "ended_at": None, "outcome": "running", "goal": "done",
         "batch": ["US0001"], "plan": None, "handoff": None}), encoding="utf-8")
    if config:
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "batch_size:\n  max_lines: 10\n  max_files: 5\n", encoding="utf-8")
    return root


class BatchSizeTests(unittest.TestCase):
    """US0185: the advisory small-batch lane - the AI batch-size failure mode made
    visible at review time, never a hard fail."""

    def test_batch_size_lane_off_without_thresholds(self):
        with tempfile.TemporaryDirectory() as d:
            root = _batch_repo(d, config=False)
            r = gate.DEFAULT_CHECKS["batch-size"](str(root))
            self.assertEqual(r["count"], 0)
            self.assertFalse(r["blocking"])
            self.assertIn("off", r["detail"])
            self.assertIn("batch_size.max_lines", r["detail"])

    def test_batch_size_flags_over_threshold_unit(self):
        with tempfile.TemporaryDirectory() as d:
            root = _batch_repo(d, lines=30)  # 31 lines added > max_lines 10
            r = gate.DEFAULT_CHECKS["batch-size"](str(root))
            self.assertEqual(r["count"], 1)

    def test_batch_size_under_threshold_is_quiet(self):
        with tempfile.TemporaryDirectory() as d:
            root = _batch_repo(d, lines=3)  # story file + 4 lines src < 10... measure asserts
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "batch_size:\n  max_lines: 500\n  max_files: 50\n", encoding="utf-8")
            r = gate.DEFAULT_CHECKS["batch-size"](str(root))
            self.assertEqual(r["count"], 0)

    def test_prefix_id_commit_never_attributed(self):
        # "Refs: US00013" must NOT count as US0001's commit (the anchored-trailer rule);
        # also kills the over-broad bare-uid grep mutant the critic ran.
        with tempfile.TemporaryDirectory() as d:
            root = _batch_repo(d, lines=30)
            _git(root, "commit", "-q", "--amend", "-m",
                 "feat: other unit entirely\n\nRefs: US00013")
            r = gate.DEFAULT_CHECKS["batch-size"](str(root))
            self.assertEqual(r["count"], 0)
            self.assertIn("no identifiable commits", r["detail"])

    def test_batch_size_no_open_run_measures_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            root = _batch_repo(d)
            (root / "sdlc-studio" / ".local" / "run-state.json").unlink()
            r = gate.DEFAULT_CHECKS["batch-size"](str(root))
            self.assertEqual(r["count"], 0)
            self.assertIn("no open run", r["detail"])


class BatchWarnTests(unittest.TestCase):
    def test_batch_warning_names_unit_points_size_threshold_and_is_advisory(self):
        with tempfile.TemporaryDirectory() as d:
            root = _batch_repo(d, lines=30)
            r = gate.DEFAULT_CHECKS["batch-size"](str(root))
            self.assertFalse(r["blocking"])  # NEVER hard-fails
            for needle in ("US0001", "2pt", "lines", "10", "advisory"):
                self.assertIn(needle, r["detail"])

    def test_gate_stays_green_with_batch_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = _batch_repo(d, lines=30)
            report = gate.run_gate(str(root), only=["batch-size"])
            self.assertTrue(report["ok"])  # advisory: the gate never fails on it


class MutationRefusedLaneTests(unittest.TestCase):
    """US0216: a mutation run refused for a red baseline applies no mutant, so its
    summary is all zeros. Rendering that as '0/0 mutations killed' turns a refusal -
    'we learned nothing' - into what reads as a clean sweep. The lane must carry the
    report's own failure state (L-0082), not only its successes."""

    REFUSED = {
        "refused": True,
        "baseline": "fail",
        "remedy": "a red baseline proves nothing: clean the working tree, then re-run",
        "summary": {"applied": 0, "killed": 0, "survived": 0, "errors": 0, "truncated": 0},
    }

    def _lane(self, report_json):
        root = Path(self.tmp)
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True, exist_ok=True)
        (local / "mutation-report.json").write_text(json.dumps(report_json), encoding="utf-8")
        return gate._mutation(str(root))

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.tmp = self._td.name
        self.addCleanup(self._td.cleanup)

    def test_refused_report_names_the_refusal(self) -> None:
        """AC1: the detail says REFUSED and names the baseline, never '0/0 killed'."""
        lane = self._lane(self.REFUSED)
        self.assertIn("REFUSED", lane["detail"])
        self.assertIn("baseline fail", lane["detail"])
        self.assertNotIn("0/0 mutations killed", lane["detail"])

    def test_refused_report_carries_the_remedy(self) -> None:
        """AC2: the reader learns the fix from the lane, not by opening the report."""
        lane = self._lane(self.REFUSED)
        self.assertIn("clean the working tree", lane["detail"])

    def test_refused_report_counts_as_unmet(self) -> None:
        """AC3a: a refusal is not silently zero-as-clean."""
        self.assertGreater(self._lane(self.REFUSED)["count"], 0)

    def test_error_baseline_is_also_refused(self) -> None:
        """A broken test command refuses just as a failing suite does."""
        lane = self._lane({**self.REFUSED, "baseline": "error",
                           "remedy": "the test command errored on unmutated code"})
        self.assertIn("REFUSED", lane["detail"])
        self.assertIn("baseline error", lane["detail"])

    def test_normal_report_is_unchanged(self) -> None:
        """AC3b: the refusal branch must not disturb an ordinary run's rendering."""
        lane = self._lane({"summary": {"applied": 5, "killed": 5, "survived": 0,
                                       "errors": 0, "truncated": 0}})
        self.assertEqual(lane["count"], 0)
        self.assertIn("5/5 mutations killed", lane["detail"])
        self.assertNotIn("REFUSED", lane["detail"])

    def test_survivors_report_is_unchanged(self) -> None:
        """A report with survivors keeps its existing detail wording."""
        lane = self._lane({"summary": {"applied": 5, "killed": 4, "survived": 1,
                                       "errors": 0, "truncated": 0}})
        self.assertIn("1 survived", lane["detail"])
        self.assertNotIn("REFUSED", lane["detail"])
class ReviewCurrentDirtyTests(unittest.TestCase):
    """US0215: an uncommitted-but-current review anchor is not a stale one.

    `_review_current` dates LATEST.md by its last COMMIT, so a review re-run during the
    close - derived but not yet committed - read at its previous commit and the gate
    demanded the operator "run `review`", the exact thing they had just done. Two
    genuinely different states owe two different remedies (CR0335, CR0341).
    """

    def _repo(self, tmp, *, artefact_first: bool, commit_latest: bool):
        """A repo with one story and a LATEST.md, ordered to be current or stale."""
        root = Path(tmp)
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        reviews = root / "sdlc-studio" / "reviews"
        reviews.mkdir(parents=True)
        story = stories / "US0001-x.md"
        latest = reviews / "LATEST.md"
        story.write_text("# US0001: x\n\n> **Status:** Done\n", encoding="utf-8")
        latest.write_text("# Reviews - LATEST\n\nanchor\n", encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-qm", "base")
        if artefact_first:
            # the artefact moves on AFTER the committed review -> genuinely stale
            story.write_text("# US0001: x\n\n> **Status:** Done\n\nchanged\n", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "artefact moves")
        # re-derive the review anchor in the working tree
        latest.write_text("# Reviews - LATEST\n\nre-derived\n", encoding="utf-8")
        if commit_latest:
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "close paperwork")
        return root, latest

    def test_uncommitted_but_current_names_the_commit_remedy(self) -> None:
        """AC1: the remedy is to commit, not to re-run the review."""
        with tempfile.TemporaryDirectory() as t:
            root, _ = self._repo(t, artefact_first=False, commit_latest=False)
            lane = gate._review_current(str(root))
            self.assertIn("UNCOMMITTED", lane["detail"])
            self.assertIn("commit the close paperwork", lane["detail"])
            self.assertNotIn("run `review` before closing", lane["detail"])

    def test_uncommitted_still_blocks(self) -> None:
        """AC2: naming the honest remedy must not turn the failure into a pass."""
        with tempfile.TemporaryDirectory() as t:
            root, _ = self._repo(t, artefact_first=False, commit_latest=False)
            lane = gate._review_current(str(root))
            self.assertTrue(lane["blocking"])
            self.assertGreater(lane["count"], 0)

    def test_dirty_but_genuinely_stale_still_says_run_review(self) -> None:
        """AC3: the dirty path must not mask a real staleness."""
        with tempfile.TemporaryDirectory() as t:
            root, latest = self._repo(t, artefact_first=True, commit_latest=False)
            # force the anchor's mtime behind the artefact so it is genuinely stale
            import os
            st = (root / "sdlc-studio" / "stories" / "US0001-x.md").stat()
            os.utime(latest, (st.st_atime - 3600, st.st_mtime - 3600))
            lane = gate._review_current(str(root))
            self.assertIn("stale", lane["detail"])
            self.assertIn("run `review`", lane["detail"])

    def test_committed_and_current_passes(self) -> None:
        """AC4: the clean path is untouched."""
        with tempfile.TemporaryDirectory() as t:
            root, _ = self._repo(t, artefact_first=False, commit_latest=True)
            lane = gate._review_current(str(root))
            self.assertEqual(lane["count"], 0)
            self.assertIn("current with all artefacts", lane["detail"])


class ReleaseVersionStrictLaneTests(ReleaseGateTests):
    """US0254 AC1: the pre-tag gate binds the strict version check as one exit code.

    The version consistency check and the release gate were two commands, so a tag could
    be cut from a green gate while `check_versions --strict` had never run - or had run
    and had its exit code dropped. The pre-tag gate is one obligation with one exit code.
    """

    def _tools(self, root: Path, rc: int) -> None:
        """A stand-in `tools/check_versions.py` with a chosen exit code.

        The real checker is a repo-only development tool; the gate ships to consuming
        projects that do not have it. The lane therefore invokes it as a subprocess when
        present rather than importing it, and this fixture exercises that contract.
        """
        td = root / "tools"
        td.mkdir(parents=True, exist_ok=True)
        (td / "check_versions.py").write_text(
            "import sys\n"
            "print('version mismatch' if len(sys.argv) > 1 else 'ok')\n"
            f"sys.exit({rc})\n", encoding="utf-8")

    def test_the_lane_is_bound_under_release(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            self._tools(root, 0)
            res = gate.run_gate(str(root), release=True)
            names = [c["check"] for c in res["checks"]]
            self.assertIn("versions", names)

    def test_the_lane_is_absent_from_the_standard_gate(self) -> None:
        """Between releases the version strings legitimately move; only a cut binds this.

        Asserts the lane's ABSENCE only - a minimal fixture fails other standard lanes for
        reasons that have nothing to do with this one.
        """
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            self._tools(root, 1)
            res = gate.run_gate(str(root))
            self.assertNotIn("versions", [c["check"] for c in res["checks"]])

    def test_the_bound_lane_cannot_be_deselected(self) -> None:
        """A release verdict printed over the lane that defines it is false assurance.

        Asserts the SELECTION guard fired and named this lane - not merely that the gate
        came back red. A bare `assertFalse(ok)` passes on a fixture that fails other lanes
        for unrelated reasons, and did: it survived a mutant that unbound the lane entirely.
        """
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            self._tools(root, 1)
            res = gate.run_gate(str(root), checks={}, release=True, skip=["versions"])
            sel = [c for c in res["checks"] if c["check"] == "selection"]
            self.assertTrue(sel, res["checks"])
            self.assertIn("versions", sel[0]["detail"])
            self.assertFalse(res["ok"], res)

    def test_a_project_without_the_checker_reports_rather_than_fails(self) -> None:
        """A consuming project has no tools/check_versions.py. The lane must say so, not
        invent a pass and not fail a release for a development tool it never had."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            res = gate.run_gate(str(root), release=True)
            lane = [c for c in res["checks"] if c["check"] == "versions"][0]
            # run_gate derives status from count, so a not-applicable lane reads pass -
            # the honesty lives in the detail, which must say plainly that nothing ran.
            self.assertFalse(lane["blocking"], lane)
            self.assertIn("n/a", lane["detail"].lower())
            self.assertIn("not present", lane["detail"].lower())


class ReleaseChangelogMismatchTests(ReleaseGateTests):
    """US0254 AC2: a CHANGELOG that disagrees with the shipped version fails the cut.

    `--strict` is exactly the flag that adds the CHANGELOG comparison, so a release gate
    that ran the checker without it would pass a mismatched changelog.
    """

    def _tools(self, root: Path, *, strict_fails: bool) -> None:
        """A checker that fails ONLY when --strict is passed - the CHANGELOG-mismatch shape.
        A lane that forgot the flag therefore goes green here, and the test catches it."""
        td = root / "tools"
        td.mkdir(parents=True, exist_ok=True)
        body = ("import sys\n"
                "strict = '--strict' in sys.argv\n"
                "print('CHANGELOG topmost release does not match' if strict else 'ok')\n"
                f"sys.exit(1 if (strict and {strict_fails}) else 0)\n")
        (td / "check_versions.py").write_text(body, encoding="utf-8")

    def test_a_changelog_mismatch_fails_the_release_gate(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            self._tools(root, strict_fails=True)
            res = gate.run_gate(str(root), release=True)
            self.assertFalse(res["ok"], res)
            lane = [c for c in res["checks"] if c["check"] == "versions"][0]
            self.assertEqual(lane["status"], "fail", lane)
            self.assertTrue(lane["blocking"])

    def test_the_lane_passes_strict_so_the_changelog_is_compared(self) -> None:
        """The load-bearing assertion: without --strict this fixture exits 0 and the
        mismatch above would go unnoticed."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            self._tools(root, strict_fails=True)
            lane = [c for c in gate.run_gate(str(root), release=True)["checks"]
                    if c["check"] == "versions"][0]
            self.assertIn("CHANGELOG", lane["detail"])

    def test_agreeing_versions_pass(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._story(root, "shell true")
            self._tools(root, strict_fails=False)
            lane = [c for c in gate.run_gate(str(root), release=True)["checks"]
                    if c["check"] == "versions"][0]
            self.assertEqual(lane["status"], "pass", lane)


if __name__ == "__main__":
    unittest.main()
