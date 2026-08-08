"""Unit tests for gate.py - the portable CI quality gate (CR0046)."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil as _shutil
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


import pathlib
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
                          "integrity", "duplicate-id", "provenance", "doc-coverage", "doc-surface",
                          "engagement-floor",
                          "disclosure", "doc-freshness", "mutation", "window", "hook-enabled",
                          "batch-size", "changelog-fragments"})

    def test_real_wrappers_run_and_shape(self) -> None:
        # Exercises the real checks end-to-end against this repo; asserts structure,
        # not pass/fail (state-independent, so not fragile). Reads the ONE run made on first
        # demand rather than making a second one of its own, and inherits that helper's
        # dev-repo guard rather than repeating it (BG0237).
        r = self._report()
        self.assertIsInstance(r["ok"], bool)
        self.assertEqual(len(r["checks"]), 18)   # +doc-surface (US0655), advisory
        for c in r["checks"]:
            # `seconds` is part of the row shape: the cost report derives the dominant lane
            # from it, and a lane with no share of the total cannot be named as the cause.
            self.assertEqual(set(c),
                             {"check", "count", "blocking", "status", "detail", "seconds"})
        self.assertIn("cost", r, "every run reports its own cost, not only its verdict")

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
            # An EMPTY root, not the dev repo: the lane now reads the whole shared sweep, and
            # pointing it at the live workspace made this stubbed test re-read the artefact
            # corpus for detectors it has nothing to say about (~18s a call, four calls in
            # this class). The stubs decide the assertion either way; the empty tree only
            # removes work whose answer is not being tested.
            with tempfile.TemporaryDirectory() as d:
                count = gate._reconcile(d)["count"]
        finally:
            reconcile.detect_type = orig
            reconcile.derivable_request_drift = orig_d
        self.assertEqual(count, 2 * len(reconcile.DEFAULT_TYPES))  # 2 drift/type, not 6 keys

    def test_the_gate_lane_sees_every_drift_source_reconcile_detect_does(self) -> None:
        """BG0331. The lane counted `detect_type` plus one sweep-level kind, so the other
        sweep-level detectors were exempt by omission: a tree on which `reconcile detect`
        exits 1 passed the pre-commit hook and CI, and AGENTS.md's documented gate
        disagreed with the executed one.

        Driven from a real tree rather than a stub, because the defect WAS the enumeration:
        a test that stubs the detectors it remembered would exempt the ones it forgot in
        exactly the same way the lane did.
        """
        import reconcile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            retros = root / "sdlc-studio" / "retros"
            retros.mkdir(parents=True)
            # A meta-index source: a numbered retro with no `retros/_index.md`. Assembled in
            # the sweep, never in `detect_type`, so the old lane could not see it.
            (retros / "RETRO0001-x.md").write_text(
                "# RETRO0001: x\n\n> **Date:** 2026-01-01\n", encoding="utf-8")
            sweep = reconcile.meta_index_drift(root)
            self.assertTrue(sweep, "fixture must actually produce sweep-level drift")
            res = gate._reconcile(str(root))
        self.assertEqual(res["count"], len(sweep),
                         f"the gate lane must count what `reconcile detect` counts; "
                         f"reconcile saw {len(sweep)}, the gate saw {res['count']}")

    def test_the_lane_reads_the_shared_sweep_rather_than_its_own_list(self) -> None:
        """The structural half, and the one that stops the defect coming back. A lane that
        re-derives its own total passes the fixture above the moment somebody adds the one
        detector it happens to remember; only reading `reconcile.detect_all` makes the two
        unable to disagree. Asserted at the CALL SITE - the lane, not the helper."""
        import reconcile
        calls: list = []
        real = reconcile.detect_all

        def spy(root, scope=None):
            calls.append((str(root), scope))
            return real(root, scope)

        with tempfile.TemporaryDirectory() as d:
            reconcile.detect_all = spy
            try:
                gate._reconcile(d)
            finally:
                reconcile.detect_all = real
        self.assertEqual(len(calls), 1,
                         "the reconcile lane must take its drift from the shared sweep")
        self.assertIsNone(calls[0][1], "the lane judges the full default sweep, not a scope")

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
            with tempfile.TemporaryDirectory() as d:   # empty root: see the note above
                res = gate._reconcile(d)
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
            with tempfile.TemporaryDirectory() as d:   # empty root: see the note above
                res = gate._reconcile(d)
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
            with tempfile.TemporaryDirectory() as d:   # empty root: see the note above
                gate.sdlc_md.two_backlog_enforced = lambda root: False
                off = gate._reconcile(d)["count"]
                gate.sdlc_md.two_backlog_enforced = lambda root: True
                on = gate._reconcile(d)["count"]
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


class BatchScopedConformanceTests(unittest.TestCase):
    """CR0421 US0434: the close's conformance lane judges only the batch's units. On a clean
    tree the diff scope is empty, so conformance judges the WHOLE workspace and out-of-batch
    debt blocks an in-batch close. An explicit `scope_ids` (the run's batch) narrows the per-unit
    ledger to exactly the units this close owns."""

    def _repo(self, d, n: int) -> Path:
        repo = Path(d)
        sd = repo / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        for i in range(1, n + 1):
            (sd / f"US{i:04d}-x.md").write_text(
                f"# US{i:04d}: s\n\n> **Status:** Done\n"
                "> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell echo ok\n",
                encoding="utf-8")
        return repo

    def test_close_conformance_lane_judges_only_the_batch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, 3)  # US0001..US0003, all nonconformant
            whole = gate._conformance(str(repo))
            scoped = gate._conformance(str(repo), scope_ids={"US0001"})
            self.assertGreaterEqual(whole["count"], 3, "whole workspace charges all three")
            # Scoping to one batch unit drops the other two from the count - any repo-wide
            # global failure stays in both, so the difference is exactly the units scoped out.
            self.assertEqual(whole["count"] - scoped["count"], 2,
                             "the two out-of-batch units are no longer charged")

    def test_an_empty_batch_scope_charges_nothing_per_unit(self) -> None:
        # A bug-only batch owns no story units: scoping to the empty set must not silently fall
        # back to judging everything (the truthiness trap _post_transition_conformance guards).
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, 3)
            whole = gate._conformance(str(repo))
            scoped = gate._conformance(str(repo), scope_ids=set())
            self.assertEqual(whole["count"] - scoped["count"], 3,
                             "no story unit is in the batch, so none is charged")

    def _conf_check(self, report) -> dict:
        return next(c for c in report["checks"] if c["check"] == "conformance")

    def test_run_gate_scopes_conformance_to_the_batch(self) -> None:
        # The end-to-end wiring: run_gate(conformance_scope=...) must reach the conformance lane,
        # so the close's gate run judges its batch and not the whole workspace.
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, 3)
            whole = self._conf_check(gate.run_gate(str(repo), only=["conformance"]))
            scoped = self._conf_check(gate.run_gate(
                str(repo), only=["conformance"], conformance_scope={"US0001"}))
            self.assertEqual(whole["count"] - scoped["count"], 2,
                             "the batch scope reached the lane and dropped the two out-of-batch units")


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
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, {"git_rev": "0" * 40,
                                  "summary": {"applied": 5, "killed": 5, "survived": 0,
                                              "errors": 0, "unviable": 0, "truncated": 0}})
            gitutil.git(["init", "-q"], cwd=root)
            (root / "f.txt").write_text("x", encoding="utf-8")
            gitutil.git(["add", "-A"], cwd=root)
            gitutil.git(["-c", "user.email=t@t", "-c", "user.name=t",
                         "commit", "-qm", "c"], cwd=root)
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

    def test_a_report_hash_of_null_is_not_evidence_in_the_FALLBACK_either(self) -> None:
        """The fallback's twin of `test_an_entry_with_no_recorded_hash_is_not_evidence`.

        The `recorded is None` clause was copied into `_report_hash_stale` and its test was not,
        so dropping it left the whole module green - a SURVIVING mutant found by the round-2
        review, and the third instance this sprint of a guard that reads as coverage while pinned
        by nothing (L-0159). A null recorded hash means the target could not be read when the
        report was written; paired with a target that cannot be read now either, `current` is also
        None and two unknowns compare EQUAL, so the file reads as unchanged since the run.

        This is the fallback path, so there must be no ledger and no changed surface for it to be
        reached at all.
        """
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t, report={**self.CLEAN, "git_rev": "0" * 40,
                                         "target_hashes": {"gone.py": None}})
            lane = gate._mutation(str(root))          # no ledger written: the fallback path
            self.assertIn("STALE", lane["detail"], lane)
            self.assertIn("gone.py", lane["detail"], lane)
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

    def test_the_lane_says_which_of_the_two_non_surfaces_it_fell_back_from(self) -> None:
        """None (git could not answer) and [] (nothing changed) are different claims, and a
        reader of the coverage line has to be able to tell them apart: one figure is about a
        surface that could not be read, the other about files this change did not touch.
        Collapsing both to one label makes the None/[] distinction unobservable."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", self._sha(root / "a.py"))]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            # no commit yet: `git diff HEAD` cannot answer, so the surface is unknown
            self.assertIsNone(gate._mutation_changed_surface(str(root)))
            unknown = gate._mutation(str(root))["detail"]
            self._commit_all(root)
            # committed and clean: git answers, and the answer is "nothing changed"
            self.assertEqual(gate._mutation_changed_surface(str(root)), [])
            clean = gate._mutation(str(root))["detail"]
            self.assertIn("1/1", unknown)
            self.assertIn("1/1", clean)
            self.assertNotEqual(unknown, clean)
            self.assertIn("git could not name the changed files", unknown)
            self.assertIn("nothing changed since HEAD", clean)

    def test_a_target_the_report_names_but_no_mutant_ran_on_is_not_evidence(self) -> None:
        """The reviewer's second reproduction. `mutation.py` writes `target_hashes` for every
        file NAMED as a target, before any verdict exists; the ledger enters a target only
        when the suite returned killed or survived on it. Reading the report's hashes as
        coverage let three changed files read 3/3 covered when one mutant had run, on one
        file - the ledger held a.py alone and the lane PASSED."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "seed.md").write_text("seed\n", encoding="utf-8")
            self._commit_all(root)
            for name in ("a.py", "b.py", "c.py"):
                (root / name).write_text(f"def {name[0]}():\n    return 1\n", encoding="utf-8")
            hashes = {n: self._sha(root / n) for n in ("a.py", "b.py", "c.py")}
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", hashes["a.py"])]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps({**self.CLEAN, "targets": list(hashes),
                            "target_hashes": hashes}), encoding="utf-8")
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertIn("1/3", lane["detail"])
            self.assertIn("b.py", lane["detail"])
            self.assertIn("c.py", lane["detail"])
            self.assertEqual(lane["count"], 2, lane["detail"])
            self.assertNotEqual(lane["status"], "pass")

    def test_a_summary_from_another_rev_says_whose_numbers_it_is_printing(self) -> None:
        """Coverage is per FILE and comes from the ledger; the survivor summary is per RUN and
        comes from the report, so the two can be about different things. Judging coverage must
        not lose what the old whole-blob check said out loud: on this repo the lane printed
        '3 survived of 16 applied' from a report at another rev with nothing marking it as
        another change's numbers. Attribution only - it is not a finding and must not count."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", self._sha(root / "a.py"))]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps({**self.CLEAN, "git_rev": "0" * 40}), encoding="utf-8")
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertIn("1/1", lane["detail"])              # the per-file evidence still reads
            self.assertIn("run at 000000000", lane["detail"])  # ...and whose summary it is
            self.assertEqual(lane["count"], 0, lane["detail"])
            self.assertEqual(lane["status"], "pass")

    def test_a_summary_from_this_rev_is_not_annotated(self) -> None:
        """The other half: an attribution printed on every run would be noise, and noise on a
        line that is usually fine is how a real warning stops being read."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            head = gitutil.git(["rev-parse", "HEAD"], cwd=root).stdout.decode().strip()
            ledger = {"version": 1, "dropped": 0,
                      "entries": [self._entry("a.py", self._sha(root / "a.py"))]}
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                json.dumps(ledger), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps({**self.CLEAN, "git_rev": head}), encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertNotIn("run at", lane["detail"])
            self.assertIn("1/1", lane["detail"])

    def test_a_refused_run_carries_no_coverage_claim(self) -> None:
        """The reviewer's first reproduction. A refusal applies no mutant, so no target has a
        verdict and the ledger enters none of them - but the report still names them all. One
        lane line said 'no mutants applied, nothing was proven' and 'covers 1/1' at once."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            head = gitutil.git(["rev-parse", "HEAD"], cwd=root).stdout.decode().strip()
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps({"refused": True, "baseline": "fail", "git_rev": head,
                            "targets": ["a.py"],
                            "target_hashes": {"a.py": self._sha(root / "a.py")},
                            "summary": {"applied": 0, "killed": 0, "survived": 0,
                                        "errors": 0, "unviable": 0, "truncated": 0}}),
                encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertIn("nothing was proven", lane["detail"])
            self.assertNotIn("covers", lane["detail"])

    def test_a_report_from_another_rev_with_no_ledger_still_reads_stale(self) -> None:
        """The degraded fallback has to be REACHABLE, not merely present. Every report
        `mutation.py` writes carries `target_hashes`, so while those doubled as evidence the
        whole-blob rev check could never run: a report from a foreign rev whose hashes happen
        to match read 'covers 1/1' and PASSED."""
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps({**self.CLEAN, "git_rev": "0" * 40, "targets": ["a.py"],
                            "target_hashes": {"a.py": self._sha(root / "a.py")}}),
                encoding="utf-8")
            report = gate.run_gate(str(root), checks={"mutation": gate._mutation})
            lane = report["checks"][0]
            self.assertIn("STALE", lane["detail"])
            self.assertNotIn("covers", lane["detail"])
            self.assertNotEqual(lane["status"], "pass")

    def test_a_long_gap_list_is_bounded_and_says_how_many_it_did_not_print(self) -> None:
        """Truncating the names silently would read as 'that is all of them'."""
        line = gate._name_list([f"pkg/f{i}.py" for i in range(5)])
        self.assertEqual(line.count(".py"), 3)
        self.assertIn("+2 more", line)
        self.assertEqual(gate._name_list(["a.py", "b.py"]), "a.py, b.py")   # no bound noise

    def test_a_raising_coverage_probe_never_breaks_the_lane(self) -> None:
        """Coverage is advisory: whatever it hits, the lane still returns a verdict."""
        orig = gate._mutation_coverage

        def _boom(root):
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


class MutationProvenanceTests(unittest.TestCase):
    """BG0245 / D0048: the ledger now holds two kinds of entry. A `measured` one is a run that
    applied the mutant and watched the suite; a `registered` one is a builder's report that they
    applied one by hand, which nothing here can check. Both are evidence, they are not the same
    strength, and a lane that printed one figure over both would quietly downgrade every measured
    entry in the ledger to the weaker claim - a worse defect than the empty lane being fixed.
    """

    _root = MutationCoverageTests._root
    _commit_all = MutationCoverageTests._commit_all
    _sha = staticmethod(MutationCoverageTests._sha)
    _entry = staticmethod(MutationCoverageTests._entry)
    CLEAN = MutationCoverageTests.CLEAN

    def _mutation_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("mutation_for_gate_prov",
                                                      SCRIPT.parent / "mutation.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _fixture(self, t, entries):
        """One committed file, a ledger of the given entries, and a clean report."""
        root = self._root(t)
        gitutil.git(["init", "-q"], cwd=root)
        (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
        self._commit_all(root)
        (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
            json.dumps({"version": 1, "dropped": 0, "entries": entries(root)}),
            encoding="utf-8")
        (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
            json.dumps(self.CLEAN), encoding="utf-8")
        return root

    def test_a_file_covered_only_by_a_self_report_is_named_as_one(self) -> None:
        """The whole point of D0048's constraint: the file IS covered, and the reader is told
        the cover is a claim, so a lane reading 1/1 cannot be mistaken for a measured sweep."""
        with tempfile.TemporaryDirectory() as t:
            root = self._fixture(t, lambda r: [
                self._entry("a.py", self._sha(r / "a.py"), provenance="registered")])
            lane = gate._mutation(str(root))
            self.assertIn("1/1", lane["detail"])
            self.assertIn("self-reported", lane["detail"])
            self.assertIn("a.py", lane["detail"])
            self.assertEqual(lane["count"], 0, lane["detail"])   # evidence, so not a finding

    def test_a_measured_entry_is_never_labelled_self_reported(self) -> None:
        """The other half. A marker printed over measured evidence too would say nothing, and a
        label that is always there is a label nobody reads."""
        with tempfile.TemporaryDirectory() as t:
            root = self._fixture(t, lambda r: [
                self._entry("a.py", self._sha(r / "a.py"), provenance="measured")])
            lane = gate._mutation(str(root))
            self.assertIn("1/1", lane["detail"])
            self.assertNotIn("self-reported", lane["detail"])

    def test_a_measured_entry_outranks_a_self_report_on_the_same_file(self) -> None:
        """Both kinds can name one file: a builder registers a hand-applied mutant and a run
        later measures the same content. The file is then measured, and calling it self-reported
        because a weaker entry also exists would understate what was actually done."""
        with tempfile.TemporaryDirectory() as t:
            root = self._fixture(t, lambda r: [
                self._entry("a.py", self._sha(r / "a.py"), provenance="registered"),
                self._entry("a.py", self._sha(r / "a.py"), provenance="measured")])
            lane = gate._mutation(str(root))
            self.assertIn("1/1", lane["detail"])
            self.assertNotIn("self-reported", lane["detail"])

    def test_an_entry_written_before_provenance_existed_reads_as_measured(self) -> None:
        """Only a run could write an entry before `register` existed, so an unmarked entry is a
        run's. Reading it as a claim would retro-actively weaken evidence really gathered."""
        with tempfile.TemporaryDirectory() as t:
            root = self._fixture(t, lambda r: [self._entry("a.py", self._sha(r / "a.py"))])
            lane = gate._mutation(str(root))
            self.assertIn("1/1", lane["detail"])
            self.assertNotIn("self-reported", lane["detail"])

    def test_a_self_report_goes_stale_on_an_edit_like_any_other_entry(self) -> None:
        """Provenance changes how an entry is WEIGHTED, never whether it expires: a claim about
        bytes the file no longer has is not weaker evidence, it is evidence about other code."""
        with tempfile.TemporaryDirectory() as t:
            root = self._fixture(t, lambda r: [
                self._entry("a.py", self._sha(r / "a.py"), provenance="registered")])
            (root / "a.py").write_text("def a():\n    return 99\n", encoding="utf-8")
            lane = gate._mutation(str(root))
            self.assertIn("STALE", lane["detail"])
            self.assertEqual(lane["count"], 1, lane["detail"])

    def _changed(self, t, entries):
        """One file CHANGED since HEAD, so the lane judges a real surface rather than falling
        back to whatever the ledger happens to hold. This is the shape the finding was
        reproduced in, and the fallback shape judges nothing and so proves nothing."""
        root = self._root(t)
        gitutil.git(["init", "-q"], cwd=root)
        (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
        self._commit_all(root)
        (root / "a.py").write_text("def a():\n    return 2\n", encoding="utf-8")
        (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
            json.dumps({"version": 1, "dropped": 0, "entries": entries(root)}),
            encoding="utf-8")
        (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
            json.dumps(self.CLEAN), encoding="utf-8")
        return root

    def _registered(self, r, **summary):
        base = {"applied": 1, "killed": 0, "survived": 0, "errors": 0, "unviable": 0}
        base.update(summary)
        return [self._entry("a.py", self._sha(r / "a.py"), provenance="registered",
                            summary=base)]

    def test_a_self_reported_survivor_is_reported_as_the_finding_it_is(self) -> None:
        """The one verdict that means "the test you just wrote does not catch this" reached the
        ledger and stopped there: nothing downstream read a registered entry's summary, so the
        adverse half of `register` was write-only while its coverage half read loud and clear.
        """
        with tempfile.TemporaryDirectory() as t:
            root = self._changed(t, lambda r: self._registered(r, survived=1))
            lane = gate._mutation(str(root))
            self.assertIn("surviv", lane["detail"].lower(),
                          f"a registered survivor is unsayable: {lane['detail']}")
            self.assertIn("a.py", lane["detail"])
            self.assertGreaterEqual(lane["count"], 1, lane["detail"])

    def test_reporting_a_survivor_is_never_quieter_than_reporting_nothing(self) -> None:
        """The incentive, which is the actual defect: registering a survivor moved the file
        from `no evidence` to `covered` and took the finding with it, so the honest builder's
        lane was quieter than the silent one's. Whatever else changes, that must not."""
        with tempfile.TemporaryDirectory() as t:
            silent = gate._mutation(str(self._changed(t, lambda r: [])))
        with tempfile.TemporaryDirectory() as t:
            honest = gate._mutation(str(self._changed(t,
                                                      lambda r: self._registered(r, survived=1))))
        self.assertIn("no evidence", silent["detail"])      # the fixture judges a real surface
        self.assertGreaterEqual(silent["count"], 1, silent["detail"])
        self.assertGreaterEqual(honest["count"], silent["count"],
                                f"honest={honest['detail']!r} silent={silent['detail']!r}")

    def test_a_registered_kill_still_reads_as_evidence_gained(self) -> None:
        """The positive control. If every registration counted, the subcommand would be a way
        to make your own lane worse and nobody would use it - the same incentive, inverted."""
        with tempfile.TemporaryDirectory() as t:
            root = self._changed(t, lambda r: self._registered(r, killed=1))
            lane = gate._mutation(str(root))
            self.assertIn("1/1", lane["detail"])
            self.assertNotIn("surviv", lane["detail"].lower())
            self.assertEqual(lane["count"], 0, lane["detail"])

    def test_a_measured_entry_s_survivors_are_left_to_the_report_lane(self) -> None:
        """The docstring says this, so something has to hold it: a run's survivors already
        reach the operator through mutation-report.json, and counting them here as well would
        report one run's findings twice in one line."""
        with tempfile.TemporaryDirectory() as t:
            root = self._changed(t, lambda r: [
                self._entry("a.py", self._sha(r / "a.py"), provenance="measured",
                            summary={"applied": 3, "killed": 2, "survived": 1,
                                     "errors": 0, "unviable": 0})])
            lane = gate._mutation(str(root))
            self.assertIn("1/1", lane["detail"])
            self.assertNotIn("SELF-REPORTED SURVIVOR", lane["detail"])
            self.assertEqual(lane["count"], 0, lane["detail"])

    def test_the_recorder_and_the_lane_agree_end_to_end_on_a_survivor(self) -> None:
        """Through the real writer, not a hand-built ledger: `register --verdict survived` calls
        the verdict a finding in its own help, and the lane must be where that becomes true."""
        mod = self._mutation_module()
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            mod.register_mutant(root, "a.py", "returned 2 instead of 1", "test_a", "survived",
                                line=2)
            self.assertIn("surviv", gate._mutation(str(root))["detail"].lower())

    def test_the_lane_reads_the_same_provenance_values_the_recorder_writes(self) -> None:
        """Two hand-kept copies of the vocabulary would drift into a lane that silently stops
        recognising self-reports and prints them as measured - which is exactly the failure the
        marking exists to prevent."""
        mod = self._mutation_module()
        self.assertEqual(gate._PROVENANCE_MEASURED, mod.PROVENANCE_MEASURED)
        self.assertEqual(gate._PROVENANCE_REGISTERED, mod.PROVENANCE_REGISTERED)

    def test_the_lane_reads_the_same_covering_verdicts_the_ledger_defines(self) -> None:
        """`COVERING_VERDICTS` is documented as THE definition of covering evidence and was
        used nowhere: this lane summed `killed` + `survived` inline, under a comment pointing at
        a `_covering` that did not exist. That is the single-source hazard the same commit fixed
        for the summary counters, re-created 200 lines away - a verdict added to one list would
        never reach the lane that reports coverage."""
        mod = self._mutation_module()
        self.assertEqual(gate._COVERING_VERDICTS, mod.COVERING_VERDICTS)
        self.assertNotIn(mod.EQUIVALENT_VERDICT, gate._COVERING_VERDICTS,
                         "an equivalent mutant proves nothing about the tests")


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
        root = Path(d)
        root.mkdir(parents=True, exist_ok=True)
        if with_hook:
            (root / ".githooks").mkdir(parents=True, exist_ok=True)
            (root / ".githooks" / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
        if git:
            gitutil.git(["init", "-q", str(root)], cwd=root)
            if enabled:
                gitutil.git(["config", "core.hooksPath", ".githooks"], cwd=root)
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
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            gitutil.git(["config", "core.hooksPath", ".githooks/"], cwd=root)
            self.assertIsNone(gate.hook_enablement_gap(str(root)))

    def test_absolute_hookspath_to_same_dir_is_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._tree(d)
            gitutil.git(["config", "core.hooksPath",
                         str((root / ".githooks").resolve())], cwd=root)
            self.assertIsNone(gate.hook_enablement_gap(str(root)))

    def test_foreign_git_dir_env_does_not_redirect_the_check(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as d:
            fixture = self._tree(Path(d) / "fixture")          # hook present, NOT enabled
            other = Path(d) / "other"
            other.mkdir()
            gitutil.git(["init", "-q", str(other)], cwd=other)
            gitutil.git(["config", "core.hooksPath", ".githooks"], cwd=other)
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


def _git(cwd, *args):
    gitutil.git(list(args), cwd=cwd)


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


class ReviewCurrencyByRecordTests(unittest.TestCase):
    """CR0421 US0436: review currency is a property of the review RECORD, not the anchor file's
    commit time. A re-run review that re-stamped LATEST.md byte-identically kept its old commit
    time (git saw no change) and read stale - only a substantive edit to an already-correct anchor
    cleared it. review-state.json records that the review ran, so an artefact older than that record
    is current even when the anchor's commit time is not."""

    def _repo(self, tmp, *, last_reviewed: str | None) -> Path:
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
        # Backdate the anchor's commit deterministically - git commit time is second-granularity,
        # so two commits in the same test second collide and the anchor would not read as older.
        old = dict(os.environ)
        old_env = {"GIT_COMMITTER_DATE": "2020-01-01T00:00:00", "GIT_AUTHOR_DATE": "2020-01-01T00:00:00"}
        try:
            os.environ.update(old_env)
            _git(root, "commit", "-qm", "base")
        finally:
            os.environ.clear()
            os.environ.update(old)
        # The artefact moves on AFTER the committed anchor: by commit time the anchor is stale.
        story.write_text("# US0001: x\n\n> **Status:** Done\n\nchanged\n", encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-qm", "artefact moves")
        # The review record: written when `review` last ran. A far-future stamp means the review
        # post-dates the artefact - current by the record, though the anchor commit is older.
        if last_reviewed is not None:
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "review-state.json").write_text(
                json.dumps({"artifacts": {"US0001": {"last_reviewed": last_reviewed}}}),
                encoding="utf-8")
        return root

    def test_currency_is_judged_by_the_review_record(self) -> None:
        # Anchor commit-time says stale; the record says the review post-dates the artefact.
        root = self._repo(self.enterContext(tempfile.TemporaryDirectory()),
                          last_reviewed="2999-01-01T00:00:00Z")
        lane = gate._review_current(str(root))
        self.assertEqual(lane["count"], 0, "the record makes it current")
        self.assertIn("current", lane["detail"])

    def test_without_a_record_it_falls_back_to_the_anchor_commit_time(self) -> None:
        # No review-state.json: needs_review is True for the artefact, so the commit-time verdict
        # stands and a genuinely newer artefact still reads stale - the fix cannot weaken the gate.
        root = self._repo(self.enterContext(tempfile.TemporaryDirectory()), last_reviewed=None)
        lane = gate._review_current(str(root))
        self.assertGreater(lane["count"], 0, "no record -> commit-time behaviour, still stale")
        self.assertIn("stale", lane["detail"])

    def test_the_lane_and_the_currency_checker_agree(self) -> None:
        import review_prep
        root = self._repo(self.enterContext(tempfile.TemporaryDirectory()),
                          last_reviewed="2999-01-01T00:00:00Z")
        lane_current = gate._review_current(str(root))["count"] == 0
        record_current = not review_prep.staleness(Path(root))["US0001"]["needs_review"]
        self.assertTrue(lane_current)
        self.assertEqual(lane_current, record_current,
                         "the close lane and review_prep.staleness agree on identical state")


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


class WindowCheckTests(unittest.TestCase):
    """US0307 AC3/AC4 (CR0388): a declared rewrite window is a FAILING gate check, naming who
    holds it and what they claimed.

    D0053 ruled REFUSE, not warn. The incident was caught only by luck - the file a concurrent
    process left happened to break the suite - and a warning is exactly what that failure mode
    defeats, because a rewrite that leaves the suite green (a SURVIVING mutant, by definition)
    produces a passing run in which a warning reads as noise."""

    def _root(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "sdlc-studio").mkdir(parents=True)
        return root

    def _open(self, root: Path, owner: str = "the reviewer", paths=("scripts/retro.py",)) -> None:
        import importlib.util as _il
        spec = _il.spec_from_file_location("mutation", SCRIPT.parent / "mutation.py")
        mod = _il.module_from_spec(spec)
        sys.modules["mutation"] = mod
        spec.loader.exec_module(mod)
        mod.open_window(root, owner, list(paths), note="hand-applying mutants")

    def _lane(self, root: Path) -> dict:
        return gate.DEFAULT_CHECKS["window"](str(root))

    def test_an_open_window_fails_the_gate_naming_owner_and_paths(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            self._open(root)
            lane = self._lane(root)
            self.assertEqual(lane["count"], 1, lane)
            self.assertTrue(lane["blocking"], lane)      # refuse, never warn
            self.assertIn("the reviewer", lane["detail"])
            self.assertIn("scripts/retro.py", lane["detail"])
            self.assertIn("window close", lane["detail"])

    def test_no_window_leaves_the_gate_result_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            clean = self._lane(root)
            self.assertEqual(clean["count"], 0, clean)
            before = gate.run_gate(str(root))
            self._open(root)
            after = gate.run_gate(str(root))
            self.assertNotEqual(before["ok"], after["ok"])   # the window, and only the window
            other_before = {c["check"]: (c["status"], c["count"]) for c in before["checks"]
                            if c["check"] != "window"}
            other_after = {c["check"]: (c["status"], c["count"]) for c in after["checks"]
                           if c["check"] != "window"}
            self.assertEqual(other_before, other_after)

    def test_an_unreadable_record_still_fails_the_lane(self) -> None:
        # The one direction this may never be wrong in is "closed": a truncated record means a
        # process declared a window and its record did not survive, not that nobody is writing.
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            p = root / "sdlc-studio" / ".local" / "mutation-window.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("{truncated", encoding="utf-8")
            lane = self._lane(root)
            self.assertEqual(lane["count"], 1, lane)
            self.assertTrue(lane["blocking"], lane)

    def test_the_lane_blocks_on_crash_too(self) -> None:
        # A lane whose failure blocks must block when it CRASHES: a green gate over an
        # unproven blocking lane is the false-assurance class.
        self.assertIn("window", gate.BLOCKING_ON_ERROR)

    def test_an_open_window_fails_the_whole_gate(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            self._open(root)
            report = gate.run_gate(str(root), only=["window"])
            self.assertFalse(report["ok"])
            self.assertEqual(report["checks"][0]["status"], "fail")


class WindowLaneIsPathScopedTests(unittest.TestCase):
    """The lane judges the STAGED PATHS, not the record's existence.

    Reproduced by the independent review of RUN-01KY3MFX: one pre-commit run printed both
    `No staged path is claimed by it, so this commit proceeds.` (the hook's own guard) and
    `[FAIL] window: a rewrite window is OPEN` (this lane, reached through `gate.py --root .`)
    and then `Commit blocked.` The two halves of the same feature contradicted each other, and
    the blocking half won: while ANY window was open, NO commit could land whatever it staged.
    A reviewer holding a window froze the whole tree, which is the opposite of the promise the
    story, the hook's remedy text and the reference all make.

    Every case below is a REAL git repo with a REAL index, because the behaviour under test is
    "what is staged": a fixture that never stages anything can only assert the fallback.
    """

    def _repo(self, t) -> Path:
        root = Path(t)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "tools").mkdir()
        (root / "tools" / "thing.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "README.md").write_text("notes\n", encoding="utf-8")
        gitutil.git(["init", "-q"], cwd=root)
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", "fixture"], cwd=root)
        return root

    def _record(self, root: Path, paths, name="mutation-window.json") -> None:
        p = root / "sdlc-studio" / ".local" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"owner": "the reviewer", "opened_at": "2026-07-22T10:00:00Z",
                                 "paths": paths}), encoding="utf-8")

    def _stage(self, root: Path, rel: str, body: str) -> None:
        (root / rel).write_text(body, encoding="utf-8")
        gitutil.git(["add", rel], cwd=root)

    def test_an_open_window_claiming_no_staged_path_does_not_refuse(self) -> None:
        """The ceremony commit during a review: the reviewer holds `tools/thing.py`, the author
        stages a note. This is the case the hook already allowed and the lane already blocked."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._record(root, ["tools/thing.py"])
            self._stage(root, "README.md", "notes and more notes\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 0, lane["detail"])

    def test_the_unclaimed_case_still_REPORTS_the_open_window(self) -> None:
        """Not refusing is not the same as saying nothing: an author running the gate must
        still learn a concurrent writer is active before they stage into its paths."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._record(root, ["tools/thing.py"])
            self._stage(root, "README.md", "notes and more notes\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertIn("OPEN", lane["detail"])
            self.assertIn("the reviewer", lane["detail"])
            self.assertIn("tools/thing.py", lane["detail"])

    def test_a_staged_path_the_window_claims_still_refuses(self) -> None:
        """The half that must not be lost while fixing the half above."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._record(root, ["tools/thing.py"])
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertIn("tools/thing.py", lane["detail"])
            self.assertTrue(lane["blocking"])

    def test_an_index_that_cannot_be_read_refuses_rather_than_passing(self) -> None:
        """"I cannot tell" must never be reported as "nothing is staged". A root that is not a
        git repo at all is the reachable shape of it."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            self._record(root, ["tools/thing.py"])
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertIn("could not be read", lane["detail"])

    def test_a_claim_the_matcher_cannot_interpret_claims_everything(self) -> None:
        """Fail SAFE, the direction the record's whole purpose demands. `paths` holding objects,
        nested lists or numbers used to be str()-ed into patterns that matched nothing, and an
        absolute claim can never equal a repo-relative staged path."""
        for claim in ([{"path": "tools/thing.py"}], [["tools/thing.py"]], [0], ["/elsewhere/x"]):
            with self.subTest(claim=claim), tempfile.TemporaryDirectory() as t:
                root = self._repo(t)
                self._record(root, claim)
                self._stage(root, "README.md", "notes, uninterpretable-claim case\n")
                lane = gate.DEFAULT_CHECKS["window"](str(root))
                self.assertEqual(lane["count"], 1, lane["detail"])

    def test_a_window_naming_no_paths_claims_everything(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._record(root, [])
            self._stage(root, "README.md", "notes, path-less-record case\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])

    def test_a_record_in_the_windows_directory_is_read_by_the_lane_too(self) -> None:
        """Both spellings of the published contract, through the one reader in `mutation`."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            (root / "sdlc-studio" / ".local" / "windows").mkdir(parents=True)
            self._record(root, ["tools/thing.py"], name="windows/reviewer.json")
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertIn("the reviewer", lane["detail"])

    def test_no_window_open_is_silent_and_passes(self) -> None:
        """The negative control: without it every assertion above is satisfied by a lane that
        refuses on everything."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 0, lane["detail"])
            self.assertEqual(lane["detail"], "no rewrite window is open")

    def test_the_count_names_every_window_that_claims_a_staged_path(self) -> None:
        """The lane was generalised to read N records and kept a count of `1 if claimed_any`,
        so the multi-writer case it exists to read could not be reported: two windows over one
        staged path counted the same as one."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._record(root, ["tools/thing.py"], name="a-window.json")
            self._record(root, ["tools/thing.py"], name="b-window.json")
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 2, lane["detail"])

    def test_only_the_windows_that_claim_a_staged_path_are_counted(self) -> None:
        """The control on the count: an open window claiming nothing staged is REPORTED and not
        counted, so the figure stays "how many writers claim what this commit stages"."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._record(root, ["tools/thing.py"], name="a-window.json")
            self._record(root, ["docs/"], name="b-window.json")
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertIn("docs/", lane["detail"], "the unclaiming window is still reported")

    def test_a_malformed_owner_does_not_change_which_paths_are_claimed(self) -> None:
        """The round-2 finding. This lane read `{"paths": ["tools/thing.py"]}` as claiming the
        WHOLE TREE - the reader discarded `paths` whenever `owner` was falsy - while the
        pre-commit hook read it as claiming one file and let the commit proceed. The hook runs
        this lane a few lines later, so the blocking half won: the same contradiction round 1
        was rejected for, one field along."""
        for record in ('{"paths": ["tools/thing.py"]}',
                       '{"owner": "", "paths": ["tools/thing.py"]}',
                       '{"owner": null, "paths": ["tools/thing.py"]}',
                       '{"owner": "rev", "paths": ["  ", "tools/thing.py"]}'):
            with self.subTest(record=record), tempfile.TemporaryDirectory() as t:
                root = self._repo(t)
                (root / "sdlc-studio" / ".local" / "review-window.json").write_text(
                    record, encoding="utf-8")
                self._stage(root, "README.md", "notes, malformed-owner case\n")
                lane = gate.DEFAULT_CHECKS["window"](str(root))
                self.assertEqual(lane["count"], 0, lane["detail"])
                self.assertIn("tools/thing.py", lane["detail"],
                              "the record's own claims must still be reported")

    def test_a_malformed_owner_still_refuses_the_path_it_does_claim(self) -> None:
        """The control on the case above: keeping the claims must not lose the refusal."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            (root / "sdlc-studio" / ".local" / "review-window.json").write_text(
                '{"paths": ["tools/thing.py"]}', encoding="utf-8")
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])

    def test_the_detail_reports_the_claims_the_lane_actually_matched_on(self) -> None:
        """The self-contradicting line the review read off the screen: the detail listed the
        claims - blanks included - and then named a staged path that was not among them. It
        printed the RAW field and matched on something else. A refusal a reader cannot check on
        its face is a refusal they route around."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            (root / "sdlc-studio" / ".local" / "review-window.json").write_text(
                '{"owner": "rev", "paths": ["  ", "tools/thing.py"]}', encoding="utf-8")
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            detail = gate.DEFAULT_CHECKS["window"](str(root))["detail"]
            claimed = detail.split("has claimed ")[1].split(" since ")[0]
            self.assertEqual(claimed, "tools/thing.py",
                             f"the detail reported claims the lane did not match on: {detail}")

    def test_a_traversal_claim_covers_the_file_it_names(self) -> None:
        """`tools/../tools/thing.py` is relative, so round 1's absolute-path normalisation
        never saw it, and neither matcher normalises traversal: the claim matched NOTHING and
        the commit rewriting that exact file proceeded. Fail-open is the one direction this
        feature may never be wrong in."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._record(root, ["tools/../tools/thing.py"])
            self._stage(root, "tools/thing.py", "VALUE = 999\n")
            lane = gate.DEFAULT_CHECKS["window"](str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])


class EquivalentIsNotCoverageTests(unittest.TestCase):
    """An `equivalent` registration is evidence about the MUTANT, never about the tests.

    Found by the independent review of RUN-01KY3MFX. `equivalent` joined the registrable
    vocabulary and `--test` became optional for it - correctly, since there is no test to name.
    But this lane counted ANY registered entry on matching content as coverage, so registering
    one equivalent with no `--test` at all took a file from `no evidence` to `covered` and
    DROPPED the lane's finding count from 1 to 0: the silent decrement `register_mutant`'s own
    docstring promises to prevent, produced by the one verdict that asserts no test could have
    killed the mutant.
    """

    _root = MutationCoverageTests._root
    _commit_all = MutationCoverageTests._commit_all
    _sha = staticmethod(MutationCoverageTests._sha)
    _entry = staticmethod(MutationCoverageTests._entry)
    CLEAN = MutationCoverageTests.CLEAN
    _changed = MutationProvenanceTests._changed

    def _registered(self, r, **summary):
        base = {"applied": 1, "killed": 0, "survived": 0, "errors": 0, "unviable": 0,
                "equivalent": 0}
        base.update(summary)
        return [self._entry("a.py", self._sha(r / "a.py"), provenance="registered",
                            summary=base)]

    def test_an_equivalent_only_registration_is_not_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._changed(t, lambda r: self._registered(r, equivalent=1))
            lane = gate._mutation(str(root))
            self.assertIn("0/1", lane["detail"])
            self.assertIn("no evidence", lane["detail"])
            self.assertGreaterEqual(lane["count"], 1, lane["detail"])

    def test_registering_an_equivalent_never_makes_the_lane_quieter(self) -> None:
        """The incentive, stated as the property. Registering an equivalent must not be a way
        to lower your own finding count below what registering NOTHING would give."""
        with tempfile.TemporaryDirectory() as t:
            silent = gate._mutation(str(self._changed(t, lambda r: [])))
        with tempfile.TemporaryDirectory() as t:
            excused = gate._mutation(str(self._changed(
                t, lambda r: self._registered(r, equivalent=1))))
        self.assertGreaterEqual(excused["count"], silent["count"],
                                f"excused={excused['detail']!r} silent={silent['detail']!r}")

    def test_the_exclusion_is_NAMED_rather_than_read_as_nothing_registered(self) -> None:
        """A file with an equivalent registration is not the same as a file nobody touched, and
        the line has to say so or the builder is told to do work they already did."""
        with tempfile.TemporaryDirectory() as t:
            root = self._changed(t, lambda r: self._registered(r, equivalent=1))
            self.assertIn("EQUIVALENT-ONLY", gate._mutation(str(root))["detail"])

    def test_a_kill_alongside_an_equivalent_still_covers(self) -> None:
        """The positive control. The exclusion is of the equivalent's evidence, not of the
        entry: a builder who registered a kill AND an equivalent has covered the file."""
        with tempfile.TemporaryDirectory() as t:
            root = self._changed(t, lambda r: self._registered(r, killed=1, equivalent=1,
                                                               applied=2))
            lane = gate._mutation(str(root))
            self.assertIn("1/1", lane["detail"])
            self.assertNotIn("EQUIVALENT-ONLY", lane["detail"])
            self.assertEqual(lane["count"], 0, lane["detail"])

    def test_the_recorder_and_the_lane_agree_end_to_end(self) -> None:
        """Through the real writer, not a hand-built ledger: `register --verdict equivalent`
        with no `--test` at all, which is the exact command the review reproduced with."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("mutation_for_gate_equiv",
                                                      SCRIPT.parent / "mutation.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as t:
            root = self._root(t)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
            self._commit_all(root)
            (root / "a.py").write_text("def a():\n    return 2\n", encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "mutation-report.json").write_text(
                json.dumps(self.CLEAN), encoding="utf-8")
            before = gate._mutation(str(root))
            mod.register_mutant(root, "a.py", "return 1 -> return 1", None,
                                mod.EQUIVALENT_VERDICT, reason="no observable behaviour change")
            after = gate._mutation(str(root))
            self.assertGreaterEqual(after["count"], before["count"],
                                    f"before={before['detail']!r} after={after['detail']!r}")
            self.assertIn("no evidence", after["detail"])


def _lane(report, name):
    return next(c for c in report["checks"] if c["check"] == name)


_SOUND_CHANGELOG = ("# Changelog\n\n## [Unreleased]\n\n### Added\n\n- an entry\n\n"
                    "## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")
_REPEATED_HEADING = ("# Changelog\n\n## [Unreleased]\n\n### Added\n\n- first\n\n"
                     "### Added\n\n- second\n\n## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")


class ChangelogStructureLaneTests(unittest.TestCase):
    """US0331 AC1/AC2: the structural check joins the EXISTING `changelog-fragments` lane
    (no second changelog lane appears), and it binds in BOTH gates because a structural fault
    is committed, not tagged - while the stray-fragment reading stays release-only."""

    def _repo(self, tmp, changelog_text, fragments=()):
        root = Path(tmp)
        (root / "CHANGELOG.md").write_text(changelog_text, encoding="utf-8")
        d = root / "changelog.d"
        d.mkdir(exist_ok=True)
        for name, body in fragments:
            (d / name).write_text(body, encoding="utf-8")
        return root

    def test_the_structural_fault_fails_the_existing_lane_under_its_existing_name(self):
        # a repeated `### Added` inside [Unreleased], and no stray fragments: the release gate's
        # changelog-fragments lane fails naming the fault, and no SECOND changelog lane exists.
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp, _REPEATED_HEADING)  # changelog.d present but empty (no strays)
            report = gate.run_gate(str(root), checks={}, release=True)
            lane = _lane(report, "changelog-fragments")
            self.assertEqual(lane["status"], "fail")
            self.assertIn("repeated", lane["detail"])          # the structural fault named
            self.assertIn("### Added", lane["detail"])
            changelog_lanes = [c["check"] for c in report["checks"] if "changelog" in c["check"]]
            self.assertEqual(changelog_lanes, ["changelog-fragments"])  # exactly one, same name
        # the lane's name is wired into BOTH the standard registry and the release registry
        self.assertIn("changelog-fragments", gate.DEFAULT_CHECKS)
        self.assertIs(gate.DEFAULT_CHECKS["changelog-fragments"], gate._changelog)

    def test_structure_binds_in_both_gates_while_strays_stay_release_only(self):
        std_lane = {"changelog-fragments": gate.DEFAULT_CHECKS["changelog-fragments"]}
        # (a) a structural fault with no strays fails BOTH the standard gate and the release gate
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp, _REPEATED_HEADING)
            std = gate.run_gate(str(root), checks=std_lane)
            self.assertFalse(std["ok"])
            self.assertEqual(_lane(std, "changelog-fragments")["status"], "fail")
            rel = gate.run_gate(str(root), checks={}, release=True)
            self.assertEqual(_lane(rel, "changelog-fragments")["status"], "fail")
        # (b) a stray fragment over a sound CHANGELOG passes the standard gate (no nagging about
        # the normal between-releases state) but fails the release gate at the cut
        frag = [("US0001.md", "<!-- section: Added -->\n- **a thing (US0001).**\n")]
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp, _SOUND_CHANGELOG, fragments=frag)
            std = gate.run_gate(str(root), checks=std_lane)
            self.assertTrue(std["ok"])                                   # standard: silent on strays
            self.assertEqual(_lane(std, "changelog-fragments")["status"], "pass")
            rel = gate.run_gate(str(root), checks={}, release=True)
            rel_lane = _lane(rel, "changelog-fragments")
            self.assertEqual(rel_lane["status"], "fail")                 # release: refuses the stray
            self.assertIn("US0001.md", rel_lane["detail"])


class HandEditedChangelogTests(unittest.TestCase):
    """US0331 AC3/AC4: a staged hand-edit of [Unreleased] while changelog.d/ is live fails
    the commit, naming CHANGELOG.md and the changelog.py command; the same edit accompanied
    by a consumed fragment passes, and an edit OUTSIDE [Unreleased] is never refused."""

    BASE = ("# Changelog\n\n## [Unreleased]\n\n### Added\n\n- shipped thing\n\n"
            "## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")

    def _repo(self, root, base=None, fragments=("US0001.md",)):
        """Init a git repo committing BASE CHANGELOG and a live changelog.d/ with a fragment,
        so HEAD is a clean baseline the staged diff is read against."""
        gitutil.git(["init", "-q"], cwd=root)
        (root / "CHANGELOG.md").write_text(base or self.BASE, encoding="utf-8")
        d = root / "changelog.d"
        d.mkdir(exist_ok=True)
        for name in fragments:
            (d / name).write_text("<!-- section: Added -->\n- **a thing.**\n", encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", "base"], cwd=root)
        return root

    def test_a_staged_unreleased_edit_without_a_consumed_fragment_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            # two fragments live, so consuming one below still leaves changelog.d/ a directory
            # (git removes a directory it empties) - the escape is exercised, not the adoption
            # guard.
            root = self._repo(Path(tmp), fragments=("US0001.md", "US0002.md"))
            # hand-insert a bullet under [Unreleased] and stage ONLY CHANGELOG.md (no fragment
            # consumed): exactly the RUN-01KY3MFX hand-edit.
            edited = self.BASE.replace("- shipped thing\n",
                                       "- shipped thing\n- **a hand-typed entry.**\n")
            (root / "CHANGELOG.md").write_text(edited, encoding="utf-8")
            gitutil.git(["add", "CHANGELOG.md"], cwd=root)
            lane = gate._changelog(str(root))
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertIn("CHANGELOG.md", lane["detail"])
            self.assertIn("changelog.py", lane["detail"])   # the command that would have done it
            # the SAME staged edit, but with a fragment consumed in the same commit, passes -
            # changelog.d/ still exists (US0002.md remains), so this proves the fragment-consumed
            # escape, not merely an absent fragment directory.
            gitutil.git(["rm", "-q", "changelog.d/US0001.md"], cwd=root)
            self.assertTrue((root / "changelog.d").is_dir())
            passed = gate._changelog(str(root))
            self.assertEqual(passed["count"], 0, passed["detail"])

    def test_an_edit_outside_unreleased_is_not_refused(self):
        # (a) an edit to an already-released section - correcting published history
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(Path(tmp))
            released = self.BASE.replace("- old\n", "- old\n- **a correction.**\n")
            (root / "CHANGELOG.md").write_text(released, encoding="utf-8")
            gitutil.git(["add", "CHANGELOG.md"], cwd=root)
            self.assertEqual(gate._changelog(str(root))["count"], 0,
                             gate._changelog(str(root))["detail"])
        # (b) an edit to the file header
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(Path(tmp))
            header = self.BASE.replace("# Changelog\n", "# Changelog\n\nAll notable changes.\n")
            (root / "CHANGELOG.md").write_text(header, encoding="utf-8")
            gitutil.git(["add", "CHANGELOG.md"], cwd=root)
            self.assertEqual(gate._changelog(str(root))["count"], 0,
                             gate._changelog(str(root))["detail"])
        # (c) the section rename a release cut performs: [Unreleased]'s entries move DOWN under a
        # new version heading, and a fresh empty [Unreleased] is left. Nothing is ADDED to
        # [Unreleased], so the cut is not a hand-edit.
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(Path(tmp))
            cut = ("# Changelog\n\n## [4.2.0] - 2026-07-23\n\n### Added\n\n- shipped thing\n\n"
                   "## [Unreleased]\n\n## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")
            (root / "CHANGELOG.md").write_text(cut, encoding="utf-8")
            gitutil.git(["add", "CHANGELOG.md"], cwd=root)
            self.assertEqual(gate._changelog(str(root))["count"], 0,
                             gate._changelog(str(root))["detail"])

    def test_a_project_not_using_fragments_is_not_policed(self):
        # no changelog.d/ dir: the guard is silent - a project that never adopted fragments is
        # not forced onto them (kills the drop-the-adoption-guard mutant).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gitutil.git(["init", "-q"], cwd=root)
            (root / "CHANGELOG.md").write_text(self.BASE, encoding="utf-8")
            gitutil.git(["add", "-A"], cwd=root)
            gitutil.git(["commit", "-qm", "base"], cwd=root)
            edited = self.BASE.replace("- shipped thing\n",
                                       "- shipped thing\n- **a hand-typed entry.**\n")
            (root / "CHANGELOG.md").write_text(edited, encoding="utf-8")
            gitutil.git(["add", "CHANGELOG.md"], cwd=root)
            self.assertEqual(gate._changelog_hand_edit_faults(str(root)), [])


class DiffScopedLaneTests(unittest.TestCase):
    """US0354 AC3: the pre-commit gate scopes the `conformance` and `validate` lanes to the
    diff; `--release` keeps them whole-workspace. One code path, one flag - the two modes are
    the same function called with `changed` set differently, not a second set of rules.
    """

    def _repo(self, t) -> Path:
        """One conformant, valid story that the commit TOUCHES, and one non-conformant,
        invalid story committed and left alone - the pre-existing debt."""
        root = Path(t)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0001-good.md").write_text(
            "# US0001: good\n\n> **Status:** Ready\n"
            "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
            "## Acceptance Criteria\n\n### AC1: works\n- **Given** a thing\n"
            "- **Verify:** shell true\n", encoding="utf-8")
        (sd / "US0002-bad.md").write_text(
            "# US0002: bad\n\n> **Status:** Bananas\n"
            "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
            "## Acceptance Criteria\n\n### AC1: works\n- **Given** a thing\n",
            encoding="utf-8")
        gitutil.git(["init", "-q"], cwd=root)
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", "baseline"], cwd=root)
        (sd / "US0001-good.md").write_text(
            (sd / "US0001-good.md").read_text(encoding="utf-8") + "\n<!-- edited -->\n",
            encoding="utf-8")
        return root

    def test_precommit_scopes_the_lanes_and_release_keeps_them_whole_workspace(self) -> None:
        lanes = {"conformance": gate.DEFAULT_CHECKS["conformance"],
                 "validate": gate.DEFAULT_CHECKS["validate"]}
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)

            plain = gate.run_gate(str(root), checks=dict(lanes))
            for name in ("conformance", "validate"):
                lane = _lane(plain, name)
                self.assertEqual(lane["status"], "pass", lane["detail"])
                self.assertEqual(lane["count"], 0)
                # the debt is NAMED in the detail as advisory - never silently dropped
                self.assertIn("advisory", lane["detail"].lower())
                self.assertIn("US0002", lane["detail"])
            self.assertTrue(plain["ok"])

            rel = gate.run_gate(str(root), checks=dict(lanes), release=True)
            for name in ("conformance", "validate"):
                lane = _lane(rel, name)
                self.assertEqual(lane["status"], "fail", lane["detail"])
                self.assertEqual(lane["count"], 1)
                self.assertNotIn("advisory", lane["detail"].lower())
            self.assertFalse(rel["ok"])

    def test_the_scoped_lanes_are_the_same_function_as_the_whole_workspace_ones(self) -> None:
        """No second set of rules: the pre-commit binding is `changed=True` over the very
        function `--release` calls with `changed=False`."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self.assertEqual(gate._conformance(str(root), changed=True),
                             gate.DEFAULT_CHECKS["conformance"](str(root)))
            self.assertEqual(gate._validate(str(root), changed=True),
                             gate.DEFAULT_CHECKS["validate"](str(root)))
            self.assertEqual(gate._conformance(str(root))["count"], 1)   # whole-workspace default
            self.assertEqual(gate._validate(str(root))["count"], 1)

    def test_a_lane_a_caller_injected_is_not_swapped_by_release(self) -> None:
        """The release swap targets the SHIPPED scoped lane by identity. A caller's own
        `conformance` entry keeps running - the swap must not reach into an injected registry."""
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            r = gate.run_gate(str(root), checks={"conformance": _fake(0)}, release=True)
            self.assertEqual(_lane(r, "conformance")["detail"], "0")

    def test_changed_paths_returns_none_where_git_cannot_answer(self) -> None:
        """The degradation contract the whole design rests on: unknown, never empty."""
        with tempfile.TemporaryDirectory() as t:
            self.assertIsNone(gate.changed_paths(t))          # not a repo at all
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            sub = root / "sdlc-studio"
            self.assertIsNone(gate.changed_paths(str(sub)))   # not the repository top level
            self.assertIn("sdlc-studio/stories/US0001-good.md", gate.changed_paths(str(root)))
        # ... and when the probe RAISES rather than returning non-zero. A root that is not a
        # directory makes the subprocess itself fail, which is the branch a caught exception
        # covers: it must reach the same "unknown" answer, not an empty diff.
        with tempfile.TemporaryDirectory() as t:
            missing = Path(t) / "gone" / "deeper"
            self.assertIsNone(gate.changed_paths(str(missing)))

    def test_a_clean_tree_judges_the_WHOLE_workspace_not_nothing(self) -> None:
        """The regression the closing review caught: scoping was bound to DEFAULT_CHECKS, so
        EVERY caller scoped - including the ones that run against a clean checkout by
        construction (CI, deploy preflight, close preflight). git answers `[]` there, an empty
        scope judged zero units, and the gate printed PASS over a broken artefact that the same
        tree failed on before scoping existed. An empty diff is not an empty scope."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            # a story with a status outside the vocabulary - validate must catch it
            (sd / "US0001-broken.md").write_text(
                "# US0001: broken\n\n> **Status:** Bananas\n\n"
                "## Acceptance Criteria\n\n### AC1: x\n- **Verify:** shell true\n",
                encoding="utf-8")
            gitutil.git(["init", "-q"], cwd=root)
            gitutil.git(["add", "-A"], cwd=root)
            gitutil.git(["commit", "-qm", "baseline"], cwd=root)   # tree now CLEAN

            lane = gate.DEFAULT_CHECKS["validate"](str(root))
            self.assertIn("no diff to scope to", lane["detail"])
            self.assertTrue(lane["blocking"], lane["detail"])
            self.assertGreaterEqual(lane["count"], 1, lane["detail"])

    def test_a_repo_wide_failure_still_blocks_a_scoped_run(self) -> None:
        """The rule that stops the scope becoming a hiding place: with the per-unit ledger
        narrowed to an empty diff, a repo-GLOBAL stage failure is still counted and still
        fails the lane."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            # Done, fully conformant per-unit, and NO stories/_index.md -> the repo-global
            # `reconciled` stage fails and nothing else does.
            (sd / "US0001-done.md").write_text(
                "# US0001: done\n\n> **Status:** Done\n"
                "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Given** a thing\n"
                "- **Verify:** shell true\n- **Verified:** manual (2026-01-01)\n",
                encoding="utf-8")
            gitutil.git(["init", "-q"], cwd=root)
            gitutil.git(["add", "-A"], cwd=root)
            gitutil.git(["commit", "-qm", "baseline"], cwd=root)
            # A REAL diff that touches no story, so the run is genuinely SCOPED. Leaving the tree
            # clean no longer scopes at all: an empty diff has nothing to narrow to, so the lane
            # judges the whole workspace (a clean CI checkout was otherwise judging ZERO units and
            # printing PASS over a broken artefact). Scoping needs a diff to be scoping.
            (root / "unrelated.txt").write_text("touched\n", encoding="utf-8")
            gitutil.git(["add", "-A"], cwd=root)

            lane = gate.DEFAULT_CHECKS["conformance"](str(root))
            self.assertNotIn("no diff to scope to", lane["detail"])   # genuinely scoped
            self.assertEqual(lane["count"], 1, lane["detail"])
            self.assertTrue(lane["blocking"])
            self.assertIn("repo-wide", lane["detail"])
            # and it is the GLOBAL that carries it - no unit was judged at all
            import conformance
            res = conformance.detect_conformance(root, changed=True)
            self.assertEqual(res["summary"]["nonconformant"], 0)
            self.assertEqual(res["summary"]["judged"], 0)
            self.assertEqual(res["summary"]["global_failures"], 1)


class ReleaseGateCostTests(unittest.TestCase):
    """BG0293: `gate --release` could not be completed inside any usable timeout.

    The cause was measured, not guessed: the whole-workspace conformance and validate lanes
    that `--release` swaps in cost 21.94s and 0.63s, while the `verify` lane it ADDS executes
    every acceptance criterion in the workspace - 694 of 1,223 Verify lines are pytest, each
    paying a ~1.26s cold start, so the spawns alone were ~15 minutes. Jest had had batch
    treatment since batch mode was added; pytest had not.
    """

    def test_the_release_gate_completes_within_its_declared_budget(self) -> None:
        """AC1. The fix is not "run it less" - it is one scoped pytest run instead of 694
        cold starts. The property under test is that `--release` REQUESTS batching, since a
        release run that still spawns per criterion is the unrunnable lane again."""
        seen = {}

        def spy(root, timeout=None, allow_external=False, batch=False):
            seen["batch"] = batch
            return {"count": 0, "blocking": True, "detail": "spy"}

        original = gate._verify_acs
        gate._verify_acs = spy
        try:
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / "sdlc-studio").mkdir()
                gate.run_gate(root=d, release=True, skip=["mutation"])
        finally:
            gate._verify_acs = original
        self.assertIs(seen.get("batch"), True,
                      "--release must batch the verify lane; per-AC spawns made it unrunnable")
        # The budget is DECLARED, so it is a number the lane is measured against rather than
        # an unstated hope. 300s against a lane that took over 600s before the fix.
        self.assertTrue(hasattr(gate, "VERIFY_LANE_BUDGET_S"))
        self.assertLessEqual(gate.VERIFY_LANE_BUDGET_S, 600)

    def test_a_scoped_run_does_not_silently_batch(self) -> None:
        """The negative control. Without --release the lane keeps its per-AC behaviour, so
        this test proves the assertion above is about --release and not about the lane always
        reporting True."""
        seen = {}

        def spy(root, timeout=None, allow_external=False, batch=False):
            seen["batch"] = batch
            return {"count": 0, "blocking": True, "detail": "spy"}

        original = gate._verify_acs
        gate._verify_acs = spy
        try:
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / "sdlc-studio").mkdir()
                gate.run_gate(root=d, release=False)
        finally:
            gate._verify_acs = original
        self.assertNotEqual(seen.get("batch"), True,
                            "only --release may batch")

    def test_a_non_conformant_unit_anywhere_still_fails_the_release_gate(self) -> None:
        """AC2. The speedup must not narrow what is judged. A red AC in ANY story fails the
        lane, whether or not that story is in a diff - which is the whole reason --release
        restores the whole-workspace scope after US0354's diff scoping made the ordinary gate
        judge zero units on a clean tree."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0001-good.md").write_text(
                "# US0001: good\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
                "- **Verify:** shell true\n", encoding="utf-8")
            (stories / "US0002-red.md").write_text(
                "# US0002: red\n\n## Acceptance Criteria\n\n### AC1: b\n\n"
                "- **Verify:** shell false\n", encoding="utf-8")
            res = gate._verify_acs(str(root), batch=True)
        self.assertTrue(res["blocking"])
        self.assertGreater(res["count"], 0, "a red AC anywhere must fail the release lane")
        self.assertIn("US0002", res["detail"], "the failing unit must be named")

    def test_an_absent_node_is_never_resolved_from_the_cache(self) -> None:
        """AC2, the guarantee the speedup must not trade away. A batch that resolved an
        unknown node would turn the release gate green by running nothing - strictly worse
        than the slowness it fixes. An absent node must fall through to its own subprocess,
        which is where the deleted-target case is reported as VACUOUS."""
        import verify_ac
        cache = {"tests/test_x.py::C::test_a": True}
        self.assertIsNone(verify_ac.resolve_pytest_from_cache(
            "pytest tests/test_x.py::C::test_missing", cache))
        hit = verify_ac.resolve_pytest_from_cache("pytest tests/test_x.py::C::test_a", cache)
        self.assertTrue(hit.ok)

    def test_a_skipped_test_is_not_a_pass(self) -> None:
        """AC2. A skipped verifier proves nothing; reporting it green is the vacuous pass the
        whole AC layer exists to refuse."""
        import verify_ac
        xml = (
            '<testsuites><testsuite>'
            '<testcase classname="tests.test_x.C" name="test_ok" />'
            '<testcase classname="tests.test_x.C" name="test_skip"><skipped /></testcase>'
            '<testcase classname="tests.test_x.C" name="test_bad"><failure /></testcase>'
            '</testsuite></testsuites>')
        nodes = verify_ac._parse_junit_xml(xml, ["tests/test_x.py"])
        self.assertTrue(nodes["tests/test_x.py::C::test_ok"])
        self.assertFalse(nodes["tests/test_x.py::C::test_skip"], "a skip is not a pass")
        self.assertFalse(nodes["tests/test_x.py::C::test_bad"])

    def test_the_run_reports_its_duration_and_the_scope_it_judged(self) -> None:
        """AC3. A `--release` run that got fast by judging LESS is the exact defect --release
        exists to catch, so the verdict must state both the cost and the scope - otherwise a
        fast run and a narrowed one are indistinguishable without rerunning."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0001-x.md").write_text(
                "# US0001: x\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
                "- **Verify:** manual read the thing\n", encoding="utf-8")
            res = gate._verify_acs(str(root))
        self.assertRegex(res["detail"], r"\d+s",
                         "the lane must state how long it took")
        self.assertIn("story", res["detail"],
                      "the lane must state the scope it judged")


class ReviewCurrentSelfStalenessTests(unittest.TestCase):
    """The close chain transitions the batch in steps 5-7 and refreshes the anchor in step 7,
    while the review-currency gate is step 4. So re-running the documented close flow failed on
    changes its own previous run had made, and the printed remedy was to re-run an adversarial
    review over a tree whose only change was a set of status stamps. The honest way out was to
    touch the anchor - exactly what the lane exists to stop being done casually."""

    def _repo(self, d: str):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        gitutil.git(["init", "-q"], cwd=root)
        gitutil.git(["config", "user.email", "t@example.com"], cwd=root)
        gitutil.git(["config", "user.name", "t"], cwd=root)
        return root

    def _commit(self, root: Path, msg: str, when: str | None = None) -> str:
        """Commit with an EXPLICIT date when given. Git timestamps have one-second resolution,
        so two commits made in the same second tie and nothing reads as newer than the anchor -
        the fixture then passes for the wrong reason and proves nothing about staleness."""
        prior = {k: os.environ.get(k) for k in ("GIT_COMMITTER_DATE", "GIT_AUTHOR_DATE")}
        if when:
            os.environ["GIT_COMMITTER_DATE"] = when
            os.environ["GIT_AUTHOR_DATE"] = when
        try:
            gitutil.git(["add", "-A"], cwd=root)
            gitutil.git(["commit", "-q", "-m", msg], cwd=root)
            return gitutil.git(["rev-parse", "HEAD"], cwd=root).stdout.strip()
        finally:
            for k, v in prior.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_the_close_own_transitions_do_not_stale_the_anchor(self) -> None:
        """AC1. A unit whose only change since the anchor is its Status line is the close
        recording a verdict already reached, not content a reviewer would judge differently."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            story = root / "sdlc-studio" / "stories" / "US0001-x.md"
            story.write_text("# US0001: x\n\n> **Status:** Review\n\nbody text\n",
                             encoding="utf-8")
            base = self._commit(root, "seed")
            story.write_text("# US0001: x\n\n> **Status:** Done\n\nbody text\n",
                             encoding="utf-8")
            self._commit(root, "close: transition", "2026-06-01T00:00:00+00:00")
            self.assertTrue(
                gate._close_owned_change_only(root, story, base),
                "a status-only transition is the close's own bookkeeping")

    def test_a_real_content_change_still_stales_the_review(self) -> None:
        """The negative control, and the one that matters most: this carve-out must not become
        a hole through which an edited acceptance criterion reaches a close unreviewed."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            story = root / "sdlc-studio" / "stories" / "US0002-y.md"
            story.write_text("# US0002: y\n\n> **Status:** Review\n\n### AC1: old\n",
                             encoding="utf-8")
            base = self._commit(root, "seed")
            story.write_text("# US0002: y\n\n> **Status:** Done\n\n### AC1: REWRITTEN\n",
                             encoding="utf-8")
            self._commit(root, "sneak an AC change in with the transition")
            self.assertFalse(
                gate._close_owned_change_only(root, story, base),
                "a changed acceptance criterion is review content, whatever else moved with it")

    def test_an_unreadable_diff_falls_back_to_stale(self) -> None:
        """Honest degrade. A carve-out that opened up when git could not be read would open up
        exactly when nothing can be checked."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            missing = root / "sdlc-studio" / "nope.md"
            self.assertFalse(gate._close_owned_change_only(root, missing, "deadbeef"))
            self.assertEqual(gate._anchor_last_commit(root, missing), "")

    def test_the_LANE_does_not_block_on_a_close_only_transition(self) -> None:
        """The lane test, not the helper test. Mutating the CALL SITE - dropping the carve-out
        so `judged = stale` - left every helper test green, because a helper that returns the
        right answer to nobody proves nothing. This drives `_review_current` itself."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            reviews = root / "sdlc-studio" / "reviews"
            reviews.mkdir(parents=True, exist_ok=True)
            (reviews / "LATEST.md").write_text("# Reviews - LATEST\n\nprose\n", encoding="utf-8")
            story = root / "sdlc-studio" / "stories" / "US0001-x.md"
            story.write_text("# US0001: x\n\n> **Status:** Review\n\nbody\n", encoding="utf-8")
            self._commit(root, "seed with the anchor", "2026-01-01T00:00:00+00:00")
            # ...then the close transitions the unit, AFTER the anchor's commit
            story.write_text("# US0001: x\n\n> **Status:** Done\n\nbody\n", encoding="utf-8")
            self._commit(root, "close: transition", "2026-06-01T00:00:00+00:00")
            res = gate._review_current(str(root))
        self.assertFalse(res["blocking"],
                         "the close's own transition must not stale the anchor against itself")
        self.assertIn("close bookkeeping", res["detail"])

    def test_a_hand_flip_straight_to_done_is_not_close_bookkeeping(self) -> None:
        """BG0336. The carve-out asked only whether the changed line CONTAINED `Status:`,
        with no reading of the direction or the values, so a unit hand-flipped from Draft
        (or Blocked) straight to Done was exempted as 'the close recording a verdict
        already reached' - over a verdict no reviewer ever reached."""
        for frm in ("Draft", "Blocked", "Ready"):
            with self.subTest(frm=frm), tempfile.TemporaryDirectory() as d:
                root = self._repo(d)
                story = root / "sdlc-studio" / "stories" / "US0001-x.md"
                story.write_text(f"# US0001: x\n\n> **Status:** {frm}\n\nbody text\n",
                                 encoding="utf-8")
                base = self._commit(root, "seed")
                story.write_text("# US0001: x\n\n> **Status:** Done\n\nbody text\n",
                                 encoding="utf-8")
                self._commit(root, "hand-flip", "2026-06-01T00:00:00+00:00")
                self.assertFalse(
                    gate._close_owned_change_only(root, story, base),
                    f"{frm} -> Done is not a transition the close tooling records")

    def test_a_reopen_of_a_terminal_status_is_not_close_bookkeeping(self) -> None:
        """The other direction the substring test could not see. Reopening Done puts the
        unit back in flight; nothing about that is a close stamping a reached verdict."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            story = root / "sdlc-studio" / "stories" / "US0001-x.md"
            story.write_text("# US0001: x\n\n> **Status:** Done\n\nbody text\n",
                             encoding="utf-8")
            base = self._commit(root, "seed")
            story.write_text("# US0001: x\n\n> **Status:** In Progress\n\nbody text\n",
                             encoding="utf-8")
            self._commit(root, "reopen", "2026-06-01T00:00:00+00:00")
            self.assertFalse(gate._close_owned_change_only(root, story, base),
                             "a reopen is a change a reviewer would judge")

    def test_the_LANE_blocks_on_a_hand_flip_to_done(self) -> None:
        """The CALL SITE, not the helper. A helper that returns the right answer to nobody
        proves nothing - this drives `_review_current`, which is what the gate runs."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            reviews = root / "sdlc-studio" / "reviews"
            reviews.mkdir(parents=True, exist_ok=True)
            (reviews / "LATEST.md").write_text("# Reviews - LATEST\n\nprose\n", encoding="utf-8")
            story = root / "sdlc-studio" / "stories" / "US0001-x.md"
            story.write_text("# US0001: x\n\n> **Status:** Draft\n\nbody\n", encoding="utf-8")
            self._commit(root, "seed with the anchor", "2026-01-01T00:00:00+00:00")
            story.write_text("# US0001: x\n\n> **Status:** Done\n\nbody\n", encoding="utf-8")
            self._commit(root, "hand-flip to Done", "2026-06-01T00:00:00+00:00")
            res = gate._review_current(str(root))
        self.assertTrue(res["blocking"],
                        "a status nobody reviewed must stale the review anchor")

    def test_a_non_status_close_field_is_still_bookkeeping(self) -> None:
        """The negative control on the narrowing: only the Status line gained direction and
        value awareness. The close's other stamps are still its own bookkeeping, or this
        repair would block every close it was written to unblock."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            story = root / "sdlc-studio" / "stories" / "US0001-x.md"
            story.write_text("# US0001: x\n\n> **Status:** Done\n\nbody text\n",
                             encoding="utf-8")
            base = self._commit(root, "seed")
            story.write_text("# US0001: x\n\n> **Status:** Done\n"
                             "> **Verified:** 2026-06-01\n\nbody text\n", encoding="utf-8")
            self._commit(root, "close: stamp the verification", "2026-06-01T00:00:00+00:00")
            self.assertTrue(gate._close_owned_change_only(root, story, base),
                            "an unchanged Status plus a new Verified stamp is close paperwork")

    def test_the_LANE_still_blocks_on_a_real_content_change(self) -> None:
        """The paired lane control. Without this, the test above is satisfied by a lane that
        never blocks at all."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            reviews = root / "sdlc-studio" / "reviews"
            reviews.mkdir(parents=True, exist_ok=True)
            (reviews / "LATEST.md").write_text("# Reviews - LATEST\n\nprose\n", encoding="utf-8")
            story = root / "sdlc-studio" / "stories" / "US0001-x.md"
            story.write_text("# US0001: x\n\n> **Status:** Review\n\n### AC1: old\n",
                             encoding="utf-8")
            self._commit(root, "seed with the anchor", "2026-01-01T00:00:00+00:00")
            story.write_text("# US0001: x\n\n> **Status:** Review\n\n### AC1: REWRITTEN\n",
                             encoding="utf-8")
            self._commit(root, "edit an acceptance criterion", "2026-06-01T00:00:00+00:00")
            res = gate._review_current(str(root))
        self.assertTrue(res["blocking"], "an edited AC must still stale the review")

    def test_the_two_staleness_causes_give_different_remedies(self) -> None:
        """AC2. A genuinely stale anchor and a self-staled one must not print the same
        instruction - and neither may tell the operator to edit the thing being measured."""
        real = ("reviews/LATEST.md is stale - 3 artefact(s) changed since the last review "
                "(US0001, US0002, US0003); run `review` before closing")
        book = ("reviews/LATEST.md is current - the 3 artefact(s) newer than it changed only "
                "in close bookkeeping (status, verification), which is not review content")
        self.assertNotEqual(real, book)
        self.assertIn("run `review`", real)
        self.assertNotIn("run `review`", book,
                         "self-staleness must not send the operator to re-review status stamps")


class TestRelevantSetTests(unittest.TestCase):
    """US0368: the test-relevant set covers every path a shipped test reads.

    The set decides whether a commit pays for the unit suites. Its first version named
    three directories by hand, and a hand list is a lower bound - right about what somebody
    thought of, silent about the rest. These tests hold the set to a measurement.
    """

    @staticmethod
    def _suite_repo(tmp: Path, module_src: str) -> Path:
        """A minimal tree with one shipped suite module, for measuring the measurement."""
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        (tmp / "docs").mkdir()
        (tmp / "docs" / "read-by-a-test.md").write_text("# read\n", encoding="utf-8")
        (tmp / "docs" / "read-by-nobody.md").write_text("# unread\n", encoding="utf-8")
        (suite / "test_thing.py").write_text(module_src, encoding="utf-8")
        return tmp

    def test_every_path_a_shipped_test_reads_is_in_the_set(self) -> None:
        """AC1. The set is measured from the suites, not enumerated.

        Two halves. On a synthetic tree, a doc named only by a new suite module lands in
        the set with nobody having listed it - which no hand enumeration can do. On the
        real repo, paths the shipped suites demonstrably read are in it; every one of them
        was outside the hand-written scripts/templates/tools set.
        """
        src = (
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "DOC = REPO / 'docs' / 'read-by-a-test.md'\n"
            "def test_doc():\n"
            "    assert DOC.read_text()\n"
        )
        with tempfile.TemporaryDirectory() as d:
            root = self._suite_repo(Path(d), src)
            measured = gate.test_relevant_paths(str(root))
            self.assertIn("docs/read-by-a-test.md", measured,
                          "a path a suite module reads must be measured into the set")
            self.assertNotIn("docs/read-by-nobody.md", measured,
                             "a doc no test reads must stay skippable - otherwise the "
                             "fast path is not narrowed, it is deleted")

        if not _in_dev_repo():
            self.skipTest("no dev repo here, so there are no shipped suites to measure")
        real = gate.test_relevant_paths(str(REPO))
        # Each of these is read by a shipped suite and was outside the hand-written set.
        for path in (".githooks/pre-commit",
                     ".githooks/commit-msg",
                     "install.sh",
                     "package.json",
                     ".github/workflows/lint.yml",
                     ".claude/skills/sdlc-studio/help/help.md",
                     ".claude/skills/sdlc-studio/reference-sprint.md",
                     "sdlc-studio/reviews/root-census.md"):
            self.assertTrue(gate._matches_relevant(path, real),
                            f"{path} is read by a shipped suite but is not test-relevant")
            self.assertFalse(gate._matches_relevant(path, set(gate.LEGACY_TEST_RELEVANT)),
                             f"{path} is already in the hand-written set, so it proves "
                             "nothing about measuring")

    def test_a_doc_a_test_reads_defeats_the_docs_only_skip(self) -> None:
        """AC2. The docs-only fast path is exactly where a test that reads a doc gets
        bypassed, so a commit touching such a doc must not be taken for docs-only."""
        src = (
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "def test_doc():\n"
            "    assert (REPO / 'docs' / 'read-by-a-test.md').read_text()\n"
        )
        with tempfile.TemporaryDirectory() as d:
            root = str(self._suite_repo(Path(d), src))
            self.assertTrue(gate.is_test_relevant(["docs/read-by-a-test.md"], root),
                            "a docs-only commit over a doc a test reads must NOT skip")
            self.assertFalse(gate.is_test_relevant(["docs/read-by-nobody.md"], root),
                             "a doc no test reads must still take the fast path")

        if not _in_dev_repo():
            self.skipTest("no dev repo here, so there is no hook to bind")
        doc = ".claude/skills/sdlc-studio/reference-sprint.md"
        self.assertTrue(gate.is_test_relevant([doc], str(REPO)),
                        f"{doc} is asserted over by a shipped suite, so a commit touching "
                        "only it must run the suites")
        hook = REPO / ".githooks" / "pre-commit"
        if hook.exists():
            self.assertIn("--test-relevant", hook.read_text(encoding="utf-8"),
                          "the hook must ask gate.py for the measured set; a regex of its "
                          "own is the hand enumeration this story removed")

    def test_deleting_a_file_a_test_reads_is_still_test_relevant(self) -> None:
        """BG0329. The set is measured from the suite SOURCES, so a path the suites name is
        relevant whether or not it is still on disk. Measuring only what exists drops a file
        at the exact moment it is deleted - the commit that breaks the suite reading it."""
        src = (
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "DOC = REPO / 'docs' / 'read-by-a-test.md'\n"
            "def test_doc():\n"
            "    assert DOC.read_text()\n"
        )
        with tempfile.TemporaryDirectory() as d:
            root = self._suite_repo(Path(d), src)
            os.remove(root / "docs" / "read-by-a-test.md")   # the commit under test DELETES it
            measured = gate.test_relevant_paths(str(root))
            self.assertIn("docs/read-by-a-test.md", measured,
                          "a suite-read file must stay in the set once deleted - that commit "
                          "is precisely the one that breaks the suite")
            self.assertTrue(gate.is_test_relevant(["docs/read-by-a-test.md"], str(root)))
            # The control: dropping the existence check must not make everything relevant.
            self.assertFalse(gate.is_test_relevant(["docs/read-by-nobody.md"], str(root)),
                             "a doc no test reads must still take the fast path")

    def test_deleting_a_structural_tree_is_still_test_relevant(self) -> None:
        """BG0329, the sibling path in the same function: the structural entries were
        unioned in only when they existed, so removing one removed the obligation to run
        the suites it feeds."""
        src = (
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "def test_doc():\n"
            "    assert (REPO / 'docs' / 'read-by-a-test.md').read_text()\n"
        )
        with tempfile.TemporaryDirectory() as d:
            root = str(self._suite_repo(Path(d), src))   # this tree has no tools/ at all
            self.assertTrue(gate.is_test_relevant(["tools/lint-style.sh"], root),
                            "a structural tree absent from disk must still be relevant - "
                            "deleting it is the commit that needs the suites")

    def test_the_set_drops_only_entries_another_entry_already_covers(self) -> None:
        """The prune that keeps the listing readable must be verdict-preserving: an entry
        is dropped only when a covering entry answers identically."""
        entries = {"tools", "tools/lint-style.sh", "docs/a.md", "install.sh"}
        minimal = gate._minimal(entries)
        self.assertEqual(minimal, {"tools", "docs/a.md", "install.sh"})
        for probe in ("tools/lint-style.sh", "tools/tests/x.py", "docs/a.md", "install.sh"):
            self.assertEqual(gate._matches_relevant(probe, minimal),
                             gate._matches_relevant(probe, entries), probe)
        self.assertFalse(gate._matches_relevant("docs/b.md", minimal))

    def test_deleting_a_directory_a_test_globs_is_still_test_relevant(self) -> None:
        """BG0329, the sibling path: a directory read-site drops out the same way."""
        src = (
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "def test_docs():\n"
            "    assert list((REPO / 'docs').glob('*.md'))\n"
        )
        with tempfile.TemporaryDirectory() as d:
            root = self._suite_repo(Path(d), src)
            _shutil.rmtree(root / "docs")                    # the commit under test DELETES it
            self.assertTrue(gate.is_test_relevant(["docs/read-by-a-test.md"], str(root)),
                            "a globbed directory must stay relevant once deleted")



def _git_fixture(root: Path, files: dict) -> None:
    """A real git repo, because the surface is now every TRACKED file rather than a measured
    read set. Patching `test_relevant_paths` no longer reaches surface_files."""
    import subprocess as sp
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
    sp.run(["git", "init", "-q"], cwd=root, check=True, env=env)
    sp.run(["git", "add", "-A"], cwd=root, check=True, env=env)





class GateBudgetTests(unittest.TestCase):
    """US0496: the gate reports its OWN cost against a budget, per run.

    A regression in gate time is absorbed silently today - nobody notices thirty seconds
    becoming forty, and by the time anyone does the cause is a dozen commits back. It is
    reported the same way a regression in behaviour is: a number, a budget, and the lane
    that dominated the total, because the total alone names nothing to fix.
    """

    @staticmethod
    def _root(tmp: Path, budget) -> str:
        (tmp / "sdlc-studio").mkdir(parents=True)
        (tmp / "sdlc-studio" / ".config.yaml").write_text(
            f"gate:\n  budget_seconds: {budget}\n", encoding="utf-8")
        return str(tmp)

    @staticmethod
    def _slow(seconds: float):
        import time as _t

        def check(_root):
            _t.sleep(seconds)
            return {"count": 0, "blocking": False, "detail": "ok"}
        return check

    def test_each_run_reports_cost_against_budget(self) -> None:
        """AC1: the elapsed cost, the budget, and the direction against the baseline."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(Path(d), 30)
            checks = {"a": self._slow(0.01), "b": self._slow(0.0)}
            report = gate.run_gate(root, checks=checks)
            cost = report["cost"]
            self.assertGreater(cost["seconds"], 0.0)
            self.assertEqual(cost["budget"], 30.0)
            self.assertFalse(cost["over"])
            self.assertIsNone(cost["baseline"], "nothing recorded yet: no direction to give")
            self.assertIn("no baseline", cost["detail"].lower())
            # Every lane carries its own share, or the dominant one cannot be derived.
            self.assertTrue(all("seconds" in c for c in report["checks"]))

            # With a baseline recorded, the run states the DIRECTION of travel.
            gate.record_gate_cost(root, 100.0)
            self.assertEqual(gate.read_gate_cost_baseline(root), 100.0)
            again = gate.run_gate(root, checks=checks)
            self.assertEqual(again["cost"]["baseline"], 100.0)
            self.assertIn("faster", again["cost"]["detail"])

            # ...and the CLI prints it, or the number exists and nobody sees it.
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                gate.cmd_gate(argparse.Namespace(
                    root=root, only=None, skip=None, format="text", release=False))
            self.assertIn("gate cost:", buf.getvalue())
            self.assertIn("budget", buf.getvalue())

    def test_an_over_budget_run_names_the_dominant_lane(self) -> None:
        """AC2: the overage is stated plainly, WITH the lane that caused it.

        A total over budget with no lane named sends a reader to bisect a gate by hand,
        which is the same as not reporting it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(Path(d), 0.001)
            report = gate.run_gate(root, checks={"quick": self._slow(0.0),
                                                 "hog": self._slow(0.08)})
            cost = report["cost"]
            self.assertTrue(cost["over"], "a run past its budget must say so")
            self.assertEqual(cost["dominant"], "hog",
                             "the slowest lane is the one a reader can act on")
            self.assertIn("OVER", cost["detail"])
            self.assertIn("hog", cost["detail"])
            self.assertIn("0.001", cost["detail"])
            # A lane that RAISED is still timed: an error lane that dominated the run is
            # exactly the one somebody needs named.
            def boom(_root):
                raise RuntimeError("nope")
            raised = gate.run_gate(root, checks={"boom": boom})
            self.assertIn("seconds", _lane(raised, "boom"))


class ProvenanceBlockingTests(unittest.TestCase):
    """An UNREADABLE artefact is a hole in the census, not a missing stamp, so the checker marks it
    blocking regardless of provenance.enforce. The lane consuming that verdict derived blocking
    from `enforced` alone and dropped it. Reverting that survived every test in this file, so the
    repair shipped unpinned - the vacuous-verifier defect one layer out."""

    def _stub(self, enforced, findings):
        import provenance
        orig = provenance.check
        provenance.check = lambda root: {"enforced": enforced, "findings": findings}
        self.addCleanup(lambda: setattr(provenance, "check", orig))

    def test_an_unreadable_artefact_blocks_even_when_not_enforced(self):
        self._stub(False, [{"blocking": True, "id": "US0001", "reason": "unreadable"}])
        self.assertTrue(gate._provenance(".")["blocking"],
                        "a finding the checker marked blocking must block, whatever enforce says")

    def test_an_unstamped_artefact_stays_advisory_when_not_enforced(self):
        self._stub(False, [{"blocking": False, "id": "US0001", "reason": "unstamped"}])
        self.assertFalse(gate._provenance(".")["blocking"],
                         "the advisory class must not become blocking - that is the other error")



class SurfaceCompletenessTests(unittest.TestCase):
    """The review proved the measured read-set was the wrong instrument for "did anything change":
    it omitted 233 tracked files, so editing SKILL.md left the digest byte-identical while three
    tests went red. The surface is now every TRACKED file."""

    def test_a_tracked_file_no_suite_measurably_reads_is_still_in_the_surface(self):
        files = gate.surface_files(".")
        self.assertIn(".claude/skills/sdlc-studio/SKILL.md", files,
                      "SKILL.md is tracked and a shipped test asserts over it; a digest that "
                      "omits it can mask a change the suite catches")
        for tracked in ("README.md", "AGENTS.md", "CHANGELOG.md"):
            self.assertIn(tracked, files)

    def test_no_volatile_directory_is_in_the_surface(self):
        self.assertFalse([f for f in gate.surface_files(".") if f.startswith(".git/")],
                         "a digest over churning git objects differs every commit, so the skip "
                         "it exists to enable can never fire")


class BoundaryNeverReusesTests(unittest.TestCase):
    """A boundary that can reuse inherits every gap in whatever produced the earlier verdict and
    stops being the backstop selection leans on."""

    def test_commit_is_selective_and_boundary_is_full(self):
        for boundary in gate.BOUNDARIES:
            d = gate.suite_decision(".", boundary=boundary)
            self.assertTrue(d["run"], f"boundary {boundary} must always run")
            self.assertEqual(d["mode"], "full", f"boundary {boundary} must run in FULL")


class UnattributableSelectionTests(unittest.TestCase):
    """A module whose measured read set is empty told us nothing; counting that as "reaches
    nothing" excluded the very module a change reddened."""

    def test_selection_comes_from_the_import_graph(self):
        r = gate.select_tests(".", [".claude/skills/sdlc-studio/scripts/command_audit.py"])
        self.assertTrue(r["resolved"])
        self.assertTrue(any("test_command_audit" in s for s in r["selectors"]),
                        "a change must select the test module named after it")

    def test_modules_with_an_unmeasurable_read_set_are_always_included(self):
        # Compare against TEST modules only - the read map also holds package helpers
        # (__init__, loader, gitutil) which are not selectable units.
        empty = {m for m, paths in gate.suite_read_map(".").items()
                 if not paths and "/test_" in m}
        self.assertTrue(empty, "fixture assumption: some test module measures empty")
        r = gate.select_tests(".", [".claude/skills/sdlc-studio/scripts/command_audit.py"])
        self.assertTrue(empty.issubset(set(r["selectors"])),
                        "an unmeasurable read set is an unanswered question, not an answer of "
                        "'this module reaches nothing'")


class SurfaceHashTests(unittest.TestCase):
    """The surface is every TRACKED file. The digest must move on any tracked change and stay
    still on none, and be UNANSWERABLE where git cannot enumerate."""

    def test_an_unchanged_surface_reuses_the_last_green_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git_fixture(root, {"a.py": "x = 1\n"})
            gate.record_suite_verdict(str(root), run="RUN1", status="green", mode="full")
            dec = gate.suite_decision(str(root))
            self.assertFalse(dec["run"], dec["reason"])
            self.assertEqual(dec["mode"], "reuse")

    def test_a_changed_surface_forces_a_real_run(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git_fixture(root, {"a.py": "x = 1\n"})
            gate.record_suite_verdict(str(root), run="RUN1", status="green", mode="full")
            (root / "a.py").write_text("x = 2\n", encoding="utf-8")
            self.assertTrue(gate.suite_decision(str(root))["run"])

    def test_an_unreadable_verdict_runs_the_suite(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git_fixture(root, {"a.py": "x = 1\n"})
            rec = root / gate.SUITE_VERDICT_REL
            rec.parent.mkdir(parents=True, exist_ok=True)
            rec.write_text("{not json", encoding="utf-8")
            self.assertTrue(gate.suite_decision(str(root))["run"])


    def test_editing_a_test_forces_a_run(self):
        """A changed assertion is a changed question even when the code it asks about is
        untouched. Restored after a repair rewrote this class and deleted it, leaving US0493's
        AC3 pointing at nothing - the rotted-verifier class, self-inflicted."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git_fixture(root, {"a.py": "x = 1\n", "tests/test_a.py": "def test_x(): assert True\n"})
            gate.record_suite_verdict(str(root), run="RUN1", status="green", mode="full")
            self.assertFalse(gate.suite_decision(str(root))["run"], "fixture: starts reusable")
            (root / "tests" / "test_a.py").write_text("def test_x(): assert 1 == 1\n", encoding="utf-8")
            self.assertTrue(gate.suite_decision(str(root))["run"],
                            "editing a test must force a run - the surface covers tests too")

    def test_a_tree_git_cannot_enumerate_is_unanswerable(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.py").write_text("x = 1\n", encoding="utf-8")   # no git init
            self.assertIsNone(gate.surface_hash(d),
                              "an empty surface is git declining to answer; hashing nothing "
                              "yields a stable digest and the skip would fire for ever")
            self.assertTrue(gate.suite_decision(d)["run"])


class BoundaryPolicyTests(unittest.TestCase):
    """A boundary is the backstop selection leans on, so it never reuses and never selects."""

    def test_commit_is_selective_and_boundary_is_full(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git_fixture(root, {"a.py": "x = 1\n"})
            gate.record_suite_verdict(str(root), run="RUN1", status="green", mode="full")
            for boundary in gate.BOUNDARIES:
                dec = gate.suite_decision(str(root), boundary=boundary)
                self.assertTrue(dec["run"], f"{boundary} must run")
                self.assertEqual(dec["mode"], "full", f"{boundary} must run in full")

    def test_an_unknown_boundary_is_refused_not_ignored(self):
        import argparse
        with self.assertRaises(gate.BoundaryError):
            gate.resolve_boundary(argparse.Namespace(boundary="tuesday"))

    def test_the_hook_consumes_the_selection_rather_than_only_naming_it(self):
        hook = Path(".githooks/commit-msg").read_text(encoding="utf-8")
        self.assertIn("suite-selector=", hook,
                      "commit-msg is where the suites run; a selection it never reads is inert")
        self.assertIn("--record-suite-verdict", hook,
                      "without a recorded green the reuse branch is unreachable in production")


class TestSelectionTests(unittest.TestCase):
    """Selection must never claim resolved over a set that misses a real dependent."""

    def test_selection_comes_from_the_import_graph(self):
        r = gate.select_tests(".", [".claude/skills/sdlc-studio/scripts/command_audit.py"])
        self.assertTrue(r["resolved"])
        self.assertTrue(any("test_command_audit" in s for s in r["selectors"]))


    def test_selection_does_not_replace_the_boundary_run(self):
        """AC4's guarantee, strengthened by review: a boundary does not merely decline a green
        earned by a selected run - it never reuses at all, so selection can only ever trade WHEN
        coverage is paid, never WHETHER."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git_fixture(root, {"a.py": "x = 1\n"})
            for mode in ("selected", "full"):
                gate.record_suite_verdict(str(root), run="R", status="green", mode=mode)
                for boundary in gate.BOUNDARIES:
                    dec = gate.suite_decision(str(root), boundary=boundary)
                    self.assertTrue(dec["run"], f"{boundary} must run over a {mode} green")
                    self.assertEqual(dec["mode"], "full")

    def test_a_selected_run_reports_what_it_excluded(self):
        r = gate.select_tests(".", [".claude/skills/sdlc-studio/scripts/next_id.py"])
        self.assertTrue(r["resolved"])
        self.assertGreater(r["excluded"], 0)
        self.assertIn("excluded", r["reason"])

    def test_an_unresolvable_change_runs_everything(self):
        r = gate.select_tests(".", ["no/such/path/at/all.py"])
        self.assertFalse(r["resolved"], "an unresolvable change must widen, never narrow")


class WorkspaceRelevanceGranularityTests(unittest.TestCase):
    """BG0383. One module censusing the whole artefact workspace recorded the bare directory,
    `_minimal` absorbed every narrower read under it, and every artefact commit in the repo
    then paid for both unit suites. The census is not wrong to read the tree - it reads the
    tree's SHAPE, and only a file appearing, vanishing or moving can change that answer."""

    @staticmethod
    def _repo(tmp: Path) -> Path:
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        ws = tmp / "sdlc-studio"
        (ws / "bugs").mkdir(parents=True)
        (ws / "bugs" / "BG0001-x.md").write_text("# a bug\n", encoding="utf-8")
        (ws / "trd.md").write_text("# trd\n", encoding="utf-8")
        (suite / "test_census.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "GATE_LISTING_ONLY = ('sdlc-studio',)\n"
            "WS = REPO / 'sdlc-studio'\n"
            "TRD = REPO / 'sdlc-studio' / 'trd.md'\n"
            "def test_census():\n"
            "    assert list(WS.glob('**/*.md'))\n"
            "    assert TRD.read_text()\n", encoding="utf-8")
        return tmp

    def test_a_body_only_edit_under_a_listing_only_tree_is_not_relevant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            self.assertIn("sdlc-studio", gate.listing_only_paths(root))
            self.assertFalse(
                gate.is_test_relevant(["sdlc-studio/bugs/BG0001-x.md"], root, structural=set()),
                "editing the prose inside an artefact cannot change what the census counts")

    def test_a_structural_change_under_the_same_tree_still_is(self) -> None:
        """The other half, and it is what stops the carve-out becoming a blanket exemption of
        the workspace: the census DOES see a file arrive, leave or move."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            added = "sdlc-studio/bugs/BG0002-new.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}))

    def test_a_narrower_read_under_it_keeps_its_content_relevance(self) -> None:
        """The absorbing `_minimal` is what made this expensive. A file a suite genuinely
        OPENS must survive underneath a listing-only directory, or the repair would trade one
        false green for another."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            self.assertIn("sdlc-studio/trd.md", gate.test_relevant_paths(root))
            self.assertTrue(gate.is_test_relevant(["sdlc-studio/trd.md"], root, structural=set()))

    def test_an_undeclared_whole_tree_read_stays_fully_relevant(self) -> None:
        """The declaration is opt-in and the default is unchanged. A module that censuses a
        tree without saying so is treated exactly as before - the safe direction, and the
        reason a wrong declaration cannot widen anything by accident."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            mod = root / ".claude/skills/sdlc-studio/scripts/tests/test_census.py"
            mod.write_text(mod.read_text().replace("GATE_LISTING_ONLY = ('sdlc-studio',)\n", ""),
                           encoding="utf-8")
            self.assertEqual(gate.listing_only_paths(str(root)), set())
            self.assertTrue(gate.is_test_relevant(["sdlc-studio/bugs/BG0001-x.md"], str(root),
                                                  structural=set()))

    def test_a_declaration_cannot_exempt_the_shipped_code_trees(self) -> None:
        """A declaration is a narrowing, so it needs a floor. `scripts/`, `templates/` and
        `tools/` are imported and asserted over; writing their names down must not make an
        edit to them skippable."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            (root / "tools").mkdir()
            (root / "tools" / "x.py").write_text("x = 1\n", encoding="utf-8")
            mod = root / ".claude/skills/sdlc-studio/scripts/tests/test_census.py"
            mod.write_text(mod.read_text().replace(
                "GATE_LISTING_ONLY = ('sdlc-studio',)",
                "GATE_LISTING_ONLY = ('sdlc-studio', 'tools')")
                .replace("WS = REPO / 'sdlc-studio'",
                         "WS = REPO / 'sdlc-studio'\nTOOLS = REPO / 'tools'")
                .replace("    assert list(WS.glob('**/*.md'))",
                         "    assert list(WS.glob('**/*.md'))\n    assert list(TOOLS.glob('*.py'))"),
                encoding="utf-8")
            self.assertNotIn("tools", gate.listing_only_paths(str(root)))
            self.assertTrue(gate.is_test_relevant(["tools/x.py"], str(root), structural=set()))

    def test_an_unknown_change_kind_is_treated_as_structural(self) -> None:
        """`structural=None` means the caller could not say. An unanswered question runs the
        suites; that is the direction every other unknown in this module degrades to."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            self.assertTrue(gate.is_test_relevant(["sdlc-studio/bugs/BG0001-x.md"], root))

    def test_name_status_input_is_parsed_and_a_bare_path_list_still_works(self) -> None:
        """The hook now pipes `--name-status`. Both spellings must answer, or the verdict
        depends on how the caller was written rather than on what changed."""
        paths, structural = gate._split_name_status(["M\tsdlc-studio/bugs/a.md"])
        self.assertEqual(paths, ["sdlc-studio/bugs/a.md"])
        self.assertEqual(structural, set())
        paths, structural = gate._split_name_status(["A\tsdlc-studio/bugs/b.md"])
        self.assertEqual(structural, {"sdlc-studio/bugs/b.md"})
        # A rename names both sides, and the old path vanishing is as structural as the new
        # one arriving - counting only the new name would call the deletion a content edit.
        paths, structural = gate._split_name_status(["R100\tsdlc-studio/bugs/a.md\tsdlc-studio/bugs/b.md"])
        self.assertEqual(sorted(paths), ["sdlc-studio/bugs/a.md", "sdlc-studio/bugs/b.md"])
        self.assertEqual(len(structural), 2)
        paths, structural = gate._split_name_status(["sdlc-studio/bugs/a.md"])
        self.assertEqual(paths, ["sdlc-studio/bugs/a.md"])
        self.assertIsNone(structural, "a bare list says nothing about the change kind")

    def test_the_tool_reports_which_entry_matched(self) -> None:
        """AC4. One reader collapsing the set was invisible from the tool and had to be found
        by reading the read map by hand."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            matched = gate._matched_entries(["sdlc-studio/trd.md"], root, structural=set())
            self.assertIn("sdlc-studio/trd.md", matched)
            added = "sdlc-studio/bugs/BG0002-new.md"
            matched = gate._matched_entries([added], root, structural={added})
            self.assertTrue(any("listing-only" in m for m in matched), matched)

    def test_the_repo_s_own_workspace_narrows_only_when_every_reader_agrees(self) -> None:
        """The rule, asserted against the REAL repository.

        The electorate comes from `gate.content_readers`, the same subtraction the rule itself
        makes. Re-deriving it here from the raw read map is what made this test assert the
        SUSPENSION as though it were the rule: two modules named `sdlc-studio`, one of them only
        probing that it exists, and counting the prober held the narrowing off the whole repo.

        Asserted as the RULE rather than as the current answer, so this test says something
        true whichever way the repository's declarations go."""
        root = str(REPO)
        readers = gate.content_readers(root).get("sdlc-studio", set())
        declared = set(gate.listing_only_scopes(root))
        declarers = {m for m in readers
                     if "GATE_LISTING_ONLY" in (REPO / m).read_text(encoding="utf-8")}
        if readers - declarers:
            self.assertNotIn("sdlc-studio", declared,
                             f"{len(readers)} modules read this entry for content and it is "
                             f"narrowed anyway - one module's declaration is silencing "
                             f"another's read")
        # Whichever way that went, a file the suites genuinely OPEN stays relevant.
        self.assertTrue(gate.is_test_relevant(["sdlc-studio/trd.md"], root, structural=set()),
                        "a file the suites genuinely open must stay relevant")


class CloseCarveOutIsTypeGeneralTests(unittest.TestCase):
    """BG0373. BG0336 fixed the direction-blindness of the review-currency carve-out, and the
    concern here is that the repair still reasons in stories - so the hand-edited status change
    it was filed about stays reachable through a bug or a change request.

    It does not reproduce: `_artifact_type_of` derives the type from `ARTIFACT_TYPES` and
    `_close_recorded_transition` reads `status_vocab`, `terminal_statuses` and `_IMPL_TARGETS`
    per type. Verified rather than assumed - and the property is asserted ACROSS TYPES here,
    which is what the finding actually asked for and what was genuinely missing: a story-only
    fixture cannot tell a type-general rule from one that happens to work for stories."""

    #: (type, from, to, is a close-recorded transition). One row per delivery type, each with
    #: its own vocabulary, and each paired with the hand-flip that must NOT be exempt.
    CASES = (
        ("story", "Review", "Done", True),
        ("story", "Draft", "Done", False),
        ("bug", "In Progress", "Fixed", True),
        ("bug", "Open", "Fixed", False),
        ("cr", "In Progress", "Complete", True),
        ("cr", "Proposed", "Complete", False),
    )

    def test_the_carve_out_reads_every_delivery_type(self) -> None:
        for type_, frm, to, expected in self.CASES:
            with self.subTest(type=type_, frm=frm, to=to):
                self.assertEqual(
                    expected, gate._close_recorded_transition(type_, frm, to, str(REPO)),
                    f"{type_}: {frm} -> {to} was judged wrongly; the carve-out must read the "
                    f"type's own vocabulary, not a story's")

    def test_every_declared_type_resolves_from_its_directory(self) -> None:
        """The other half of the generality: a type whose path does not resolve gets
        `type_ = None`, and the carve-out then refuses - safe, but it means the exemption
        silently stops working for that type rather than being wrong loudly."""
        from lib import sdlc_md as _md
        for type_, (dirname, _prefix) in _md.ARTIFACT_TYPES.items():
            with self.subTest(type=type_):
                probe = Path(REPO) / dirname / "X0001-probe.md"
                self.assertEqual(type_, gate._artifact_type_of(Path(REPO), probe))

    def test_a_reopen_is_never_exempt_for_any_type(self) -> None:
        """Terminal to anything is a reopen, and terminal to terminal is a re-labelling. Both
        are changes a reviewer judges, for every type."""
        for type_, terminal, other in (("story", "Done", "In Progress"),
                                       ("bug", "Fixed", "In Progress"),
                                       ("cr", "Complete", "In Progress")):
            with self.subTest(type=type_):
                self.assertFalse(
                    gate._close_recorded_transition(type_, terminal, other, str(REPO)))


class CloseOwedLaneIsOptInTests(unittest.TestCase):
    """BG0311. The specs documented `--require-close` as a blocking push-or-release guard and
    it ran at NEITHER moment: the lane bound only when the flag was passed, `--release` did not
    imply it, no pre-push hook exists and CI ran the plain gate.

    The enforcement point chosen is the TAG (`release_cut.tag_allowed`), not `--release` and not
    every push. `--release` is a documented contract consuming projects depend on, and quietly
    adding a blocking lane to it changes their gate as well as this one; blocking every push on
    a trunk-based repo that commits straight to main in small green units would train the
    bypass the guard exists to prevent."""

    def test_the_explicit_flag_binds_it(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            report = gate.run_gate(d, require_close=True, checks=dict(gate.DEFAULT_CHECKS))
        self.assertIn("close-owed", {c["check"] for c in report["checks"]})

    def test_neither_release_nor_the_ordinary_gate_binds_it(self) -> None:
        """Asserted so the decision is visible: this is where the rule is NOT enforced, and a
        later change to either would be a change to a consuming project's gate."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            for kwargs in ({}, {"release": True}):
                with self.subTest(**kwargs):
                    report = gate.run_gate(d, checks=dict(gate.DEFAULT_CHECKS), **kwargs)
                    self.assertNotIn("close-owed", {c["check"] for c in report["checks"]})

    def test_the_lane_is_bound_so_the_flag_cannot_be_deselected(self) -> None:
        """A verdict printed over a deselected lane is the false assurance this gate refuses."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            report = gate.run_gate(d, require_close=True, skip=["close-owed"],
                                   checks=dict(gate.DEFAULT_CHECKS))
        self.assertFalse(report["ok"])
        self.assertEqual("selection", report["checks"][0]["check"])


class ScopedRunIsNotABaselineTests(unittest.TestCase):
    """BG0363. The cost baseline was written on every CLI run, `--only` and `--skip` included.
    A scoped run covers a fraction of the lanes, so recording one LOWERED the number the next
    full run is judged against - and that run then read as a regression against a figure that
    never measured the same thing."""

    @staticmethod
    def _lane(_root):
        return {"count": 0, "blocking": False, "detail": "d"}

    def _root(self, tmp: str) -> str:
        (Path(tmp) / "sdlc-studio").mkdir()
        return tmp

    def test_a_scoped_run_does_not_write_the_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            gate.record_gate_cost(root, 300.0)
            gate.run_gate(root, only=["a"], checks={"a": self._lane, "b": self._lane},
                          record_cost=True)
            self.assertEqual(300.0, gate.read_gate_cost_baseline(root),
                             "a scoped run overwrote the full-run baseline")

    def test_a_skipped_run_does_not_write_the_baseline_either(self) -> None:
        """`--skip` narrows the run exactly as `--only` does - a fix covering one is the
        enumerated-list shape this repo's carried lessons already name."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            gate.record_gate_cost(root, 300.0)
            gate.run_gate(root, skip=["b"], checks={"a": self._lane, "b": self._lane},
                          record_cost=True)
            self.assertEqual(300.0, gate.read_gate_cost_baseline(root))

    def test_a_full_run_still_writes_it(self) -> None:
        """The discriminating half: a baseline nothing writes is a baseline nobody has."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            gate.record_gate_cost(root, 300.0)
            gate.run_gate(root, checks={"a": self._lane}, record_cost=True)
            self.assertNotEqual(300.0, gate.read_gate_cost_baseline(root))

    def test_a_scoped_run_is_not_compared_with_the_baseline_and_says_so(self) -> None:
        """The same defect read from the other side, and the more misleading of the two: a
        fraction of the lanes measured against a full baseline reports a saving nobody made,
        and it looks like good news."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            gate.record_gate_cost(root, 300.0)
            report = gate.run_gate(root, only=["a"], checks={"a": self._lane},
                                   record_cost=True)
            detail = report["cost"]["detail"]
        self.assertTrue(report["cost"]["scoped"])
        self.assertFalse(report["cost"]["recorded"])
        self.assertIn("SCOPED", detail, "a scoped run must SAY it is not the baseline")
        self.assertNotIn("faster than", detail)
        self.assertNotIn("slower than", detail)


class VerifyBatchRemovalTests(unittest.TestCase):
    """US0479. The removed batching flag was parsed, passed to `run_gate` and read by nothing.
    `--release` implies batching and assigns the verify lane itself, so the flag promised a
    behaviour no invocation of the gate has ever produced - a documented option that is accepted
    and ignored is worse than an absent one, because it is chosen.

    The option string is BUILT rather than written, so `tools/tests/test_dead_flag_docs.py` can
    assert it appears in no tracked skill file without this test being its own counter-example
    and without that guard needing an exemption that would blunt it."""

    REMOVED_FLAG = "--verify" + "-batch"

    def test_the_dead_flag_and_its_parameter_are_gone(self) -> None:
        import contextlib
        import inspect
        import io
        self.assertNotIn("verify_batch", inspect.signature(gate.run_gate).parameters,
                         "run_gate still declares a parameter nothing reads")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            gate.build_parser().parse_args([self.REMOVED_FLAG])
        self.assertNotEqual(0, caught.exception.code)

    def test_release_still_batches_and_a_scoped_run_registers_no_verify_lane(self) -> None:
        """Removing the flag must change no gate behaviour, which is the whole claim: the
        release run batches because `--release` assigns the lane that way, and a scoped run
        registers no verify lane at all."""
        seen = {}

        def spy(root, timeout=None, allow_external=False, batch=False):
            seen["batch"] = batch
            return {"count": 0, "blocking": True, "detail": "spy"}

        original = gate._verify_acs
        gate._verify_acs = spy
        try:
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / "sdlc-studio").mkdir()
                gate.run_gate(root=d, release=True)
                self.assertTrue(seen.get("batch"), "the release lane must still batch")
                seen.clear()
                gate.run_gate(root=d, release=False)
        finally:
            gate._verify_acs = original
        self.assertNotIn("batch", seen, "a scoped run registers no verify lane at all")


class DeclarationScopedToItsDeclarerTests(unittest.TestCase):
    """BG0398. A declaration is ONE module's statement about its OWN read, and it was honoured
    tree-wide - so a second module's content read of the same directory went silent, and an
    edit it asserts over answered `test-relevant: no` while its own assertion would have
    failed. `.githooks` was unprotected too, though it is a directory-level content read."""

    @staticmethod
    def _repo(tmp: Path, second: str) -> Path:
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        docs = tmp / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("# guide\n", encoding="utf-8")
        (suite / "test_census.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "GATE_LISTING_ONLY = ('docs',)\n"
            "DOCS = REPO / 'docs'\n"
            "def test_census():\n"
            "    assert list(DOCS.glob('*.md'))\n", encoding="utf-8")
        (suite / "test_other.py").write_text(second, encoding="utf-8")
        return tmp

    #: A second module that READS the same directory and declares nothing.
    UNDECLARED = ("from pathlib import Path\n"
                  "REPO = Path(__file__).resolve().parents[5]\n"
                  "DOCS = REPO / 'docs'\n"
                  "def test_other():\n"
                  "    assert list(DOCS.iterdir())\n")
    #: The same module, agreeing.
    DECLARED = ("from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "GATE_LISTING_ONLY = ('docs',)\n"
                "DOCS = REPO / 'docs'\n"
                "def test_other():\n"
                "    assert list(DOCS.iterdir())\n")

    def test_one_modules_declaration_does_not_silence_anothers_read(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.UNDECLARED))
            self.assertNotIn("docs", gate.listing_only_paths(root),
                             "the undeclared reader's view was overridden by its neighbour")
            added = "docs/new.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}))

    def test_a_directory_every_reader_declares_is_still_narrowed(self) -> None:
        """The discriminating half: unanimity is a condition, not a refusal of the feature."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.DECLARED))
            self.assertIn("docs", gate.listing_only_paths(root))
            self.assertFalse(gate.is_test_relevant(["docs/guide.md"], root, structural=set()))

    def test_a_content_read_directory_can_never_be_declared_listing_only(self) -> None:
        """`.githooks` is read at directory level for its CONTENTS. A declaration is a
        narrowing, so its floor has to be stated rather than inferred."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = self._repo(tmp, self.DECLARED)
            hooks = root / ".githooks"
            hooks.mkdir()
            (hooks / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
            suite = root / ".claude/skills/sdlc-studio/scripts/tests"
            (suite / "test_hooks.py").write_text(
                "from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "GATE_LISTING_ONLY = ('.githooks',)\n"
                "H = REPO / '.githooks'\n"
                "def test_hooks():\n"
                "    assert list(H.iterdir())\n", encoding="utf-8")
            self.assertNotIn(".githooks", gate.listing_only_paths(str(root)))
        self.assertIn(".githooks", gate.CONTENT_READ_DIRS)


class FalseGreenPathsAreClosedTests(unittest.TestCase):
    """The three ways the listing-only narrowing could answer `test-relevant: no` for a file
    that CAN change a test outcome, all found by the closing review of RUN-01KYNKDP.

    This is the catastrophic class for a test-selection mechanism: every other defect in that
    sprint made the gate slower or noisier, and these made it blind."""

    @staticmethod
    def _repo(tmp: Path, decl: str, *, extra: str = "") -> Path:
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        ws = tmp / "sdlc-studio"
        (ws / "bugs").mkdir(parents=True)
        # A REAL artefact shape. A declared id now resolves against the artefact index rather
        # than a filename pattern, so a fixture whose heading is `# named` is not an
        # artefact - which is the point: a stray `BG288-repro.md` must not satisfy a
        # declaration either.
        (ws / "bugs" / "BG0288-named.md").write_text(
            "# BG0288: named\n\n> **Status:** Open\n", encoding="utf-8")
        (suite / "test_census.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            f"GATE_LISTING_ONLY = {decl}\n"
            "WS = REPO / 'sdlc-studio'\n"
            f"{extra}"
            "def test_census():\n"
            "    assert list(WS.glob('**/BG0288*.md'))\n", encoding="utf-8")
        return tmp

    def test_a_declared_id_that_resolves_to_nothing_withholds_the_narrowing(self) -> None:
        """A typo is the likeliest wrong declaration and was the one shape the fail-safe list
        missed: `BG288` for `BG0288` is a good tuple of a good string that matches nothing, so
        the tree narrowed to an id no file carries."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), "({'path': 'sdlc-studio', 'ids': ('BG288',)},)"))
            self.assertEqual({"sdlc-studio": None}, gate.listing_only_scopes(root),
                             "a declared id matching no artefact still narrowed the tree")
            added = "sdlc-studio/bugs/BG0288-named.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}),
                            "a structural change to the artefact the module asserts about "
                            "answered `no` - a false green from a typo")

    def test_a_resolvable_id_still_narrows(self) -> None:
        """The discriminating half - a validation that voids every declaration is not a fix."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), "({'path': 'sdlc-studio', 'ids': ('BG0288',)},)"))
            self.assertEqual({"sdlc-studio": frozenset({"BG0288"})},
                             gate.listing_only_scopes(root))
            other = "sdlc-studio/bugs/BG0002-new.md"
            self.assertFalse(gate.is_test_relevant([other], root, structural={other}))

    def test_declaring_a_file_cannot_make_it_listing_only(self) -> None:
        """A file has no listing, so a file declaration is a pure content-blindness switch.
        `rel in protected` was an exact-string test, so a path UNDER a protected tree walked
        past a floor written to be absolute."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = self._repo(tmp, "('sdlc-studio',)")
            hooks = root / ".githooks"
            hooks.mkdir()
            (hooks / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
            suite = root / ".claude/skills/sdlc-studio/scripts/tests"
            (suite / "test_hooks.py").write_text(
                "from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "GATE_LISTING_ONLY = ('.githooks/pre-commit',)\n"
                "HOOK = REPO / '.githooks' / 'pre-commit'\n"
                "def test_hook():\n"
                "    assert HOOK.read_text()\n", encoding="utf-8")
            scopes = gate.listing_only_scopes(str(root))
            self.assertNotIn(".githooks/pre-commit", scopes)
            self.assertTrue(
                gate.is_test_relevant([".githooks/pre-commit"], str(root), structural=set()),
                "a plain content edit to a hook the suite READS answered `no`")

    def test_a_directory_under_a_protected_tree_cannot_be_declared(self) -> None:
        """The PREFIX half on its own. The test above declares a FILE under a protected tree, so
        the `isdir` check rejects it too and either guard alone keeps that fixture green - both
        mutants survived individually, and only removing both reddened anything.

        A DIRECTORY under a protected tree is the case only the prefix check can refuse: it is a
        real directory, so `isdir` passes it, and the absolute floor is the sole thing standing
        between a declaration and a content read going blind."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = self._repo(tmp, "('sdlc-studio',)")
            lib = root / ".githooks" / "lib"
            lib.mkdir(parents=True)
            (lib / "shared.sh").write_text("# shared\n", encoding="utf-8")
            suite = root / ".claude/skills/sdlc-studio/scripts/tests"
            (suite / "test_hooklib.py").write_text(
                "from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "GATE_LISTING_ONLY = ('.githooks/lib',)\n"
                "LIB = REPO / '.githooks' / 'lib'\n"
                "def test_lib():\n"
                # The DIRECTORY must be what the module is measured as reading, or `rel not in
                # paths` rejects the declaration before either guard under test is reached and
                # the case asserts nothing. Naming a file inside it attributes the file.
                "    assert list(LIB.glob('*.sh'))\n", encoding="utf-8")
            scopes = gate.listing_only_scopes(str(root))
            self.assertNotIn(".githooks/lib", scopes,
                             "a directory under the content-read floor was declared away")
            self.assertTrue(
                gate.is_test_relevant([".githooks/lib/shared.sh"], str(root), structural=set()),
                "a content edit under a protected tree the suite READS answered `no`")

    def test_a_declared_plain_file_outside_any_protected_tree_is_still_refused(self) -> None:
        """The ISDIR half on its own. A file outside every protected tree passes the prefix
        check, so this is the case only `isdir` can refuse - 'listing-only' is meaningless for a
        file, which has no listing, and honouring it would be a pure content-blindness switch."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = self._repo(tmp, "('sdlc-studio',)")
            note = root / "sdlc-studio" / "NOTES.md"
            note.write_text("# notes\n", encoding="utf-8")
            suite = root / ".claude/skills/sdlc-studio/scripts/tests"
            (suite / "test_notes.py").write_text(
                "from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "GATE_LISTING_ONLY = ('sdlc-studio/NOTES.md',)\n"
                "NOTE = REPO / 'sdlc-studio' / 'NOTES.md'\n"
                "def test_note():\n"
                "    assert NOTE.read_text()\n", encoding="utf-8")
            self.assertNotIn("sdlc-studio/NOTES.md", gate.listing_only_scopes(str(root)),
                             "a plain file was accepted as a listing-only directory")

    def test_an_existence_probe_does_not_veto_a_listing_only_declaration(self) -> None:
        """BG0400. Unanimity is right, and it was counting the wrong readers.

        `(repo / "sdlc-studio").is_dir()` asks whether the checkout has a workspace at all. No
        file under that directory can change the answer - filing, editing or deleting an
        artefact leaves it exactly as it was - so the module asking it is not a CONTENT reader
        and has no stake in a listing-only narrowing. Counting it as one outvoted a real
        declaration and made every artefact-only commit pay the full unit suites."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = self._repo(tmp, "({'path': 'sdlc-studio', 'ids': ('BG0288',)},)")
            suite = root / ".claude/skills/sdlc-studio/scripts/tests"
            (suite / "test_shape.py").write_text(
                "from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "def test_shape():\n"
                "    assert (REPO / 'sdlc-studio').is_dir()\n", encoding="utf-8")
            self.assertEqual({"sdlc-studio": frozenset({"BG0288"})},
                             gate.listing_only_scopes(str(root)),
                             "an existence probe outvoted the declaration of a real reader")
            self.assertIn("sdlc-studio", gate.test_relevant_paths(str(root)),
                          "the prober lost its path entirely - deleting the tree would now "
                          "skip the suite that asserts the tree is there")

    def test_a_module_that_also_reads_the_contents_keeps_its_veto(self) -> None:
        """The discriminating half. Probing AND globbing the same tree is a content read: the
        stronger evidence wins, or the subtraction becomes a way to launder a real dependency
        by adding an `exists()` call beside it."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = self._repo(tmp, "({'path': 'sdlc-studio', 'ids': ('BG0288',)},)")
            suite = root / ".claude/skills/sdlc-studio/scripts/tests"
            (suite / "test_shape.py").write_text(
                "from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "WS = REPO / 'sdlc-studio'\n"
                "def test_shape():\n"
                "    assert WS.is_dir()\n"
                "    assert list(WS.glob('*'))\n", encoding="utf-8")
            self.assertEqual({}, gate.listing_only_scopes(str(root)),
                             "a module that globs the tree lost its vote to its own exists()")

    def test_an_unanswered_change_kind_still_runs_the_suites(self) -> None:
        """`structural=None` means the caller could not say. The id scope was answering a
        question nobody asked, turning the documented fail-safe into a `no`."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), "({'path': 'sdlc-studio', 'ids': ('BG0288',)},)"))
            self.assertTrue(gate.is_test_relevant(["sdlc-studio/bugs/BG0999-new.md"], root),
                            "an unanswered question answered itself `no`")


class LaneCostAttributionTests(unittest.TestCase):
    """US0533 (CR0465). The gate reported one total and named its dominant lane, which says
    where the worst of the cost went but not what the second and third lanes cost - and that is
    what a decision about where to spend effort needs. CR0465's own 25 seconds were invisible
    for exactly this reason: nothing attributed gate seconds to a lane."""

    @staticmethod
    def _slow_registry():
        import time as _t

        def fast(_root):
            return {"count": 0, "blocking": False, "detail": "quick"}

        def slow(_root):
            _t.sleep(0.05)
            return {"count": 0, "blocking": False, "detail": "the expensive one"}

        return {"fast": fast, "slow": slow}

    def test_each_lane_reports_its_own_seconds(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            report = gate.run_gate(d, checks=self._slow_registry())
        timed = {c["check"]: c["seconds"] for c in report["checks"] if "seconds" in c}
        self.assertEqual({"fast", "slow"}, set(timed), "every lane carries its own seconds")
        self.assertGreater(timed["slow"], timed["fast"],
                           "the seconds must be the lane's own, not the run's")
        self.assertEqual("slow", report["cost"]["dominant"],
                         "and the dominant lane is named, so the number is actionable")

    def test_a_lane_that_raised_is_still_timed(self) -> None:
        """An error lane that dominated the run is exactly the one that needs naming."""
        def boom(_root):
            raise RuntimeError("lane exploded")

        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            report = gate.run_gate(d, checks={"boom": boom})
        self.assertEqual("error", report["checks"][0]["status"])
        self.assertIsInstance(report["checks"][0]["seconds"], float)

    def test_the_text_report_prints_each_lane_s_seconds(self) -> None:
        """Recorded but unprinted is the state this was already in - the field had existed since
        the cost report was added and no reader ever saw it. Asserted against the real renderer,
        because "the data is in the dict" is precisely what was already true."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                gate.main(["--root", d, "--only", "duplicate-id,integrity"])
            printed = out.getvalue()
        lanes = [line for line in printed.splitlines() if line.lstrip().startswith("[")]
        self.assertTrue(lanes, f"no lane lines in the report:\n{printed}")
        for line in lanes:
            with self.subTest(line=line):
                self.assertRegex(line, r"\[\d+\.\d+s\]",
                                 "a lane line with no seconds is the unprinted state")

    def test_an_untimed_lane_prints_no_seconds_rather_than_zero(self) -> None:
        """Untimed is not instant. A lane stamped `0.0s` because nobody measured it would send
        a reader looking for cost anywhere but the lane that has it."""
        # Through gate's OWN renderer, not a copy of its formatting expression. The previous
        # form re-implemented the conditional inline and asserted it against itself, so no
        # change to gate.py could redden it - a test that measures only its own arithmetic.
        self.assertEqual("", gate.lane_stamp({"check": "x", "status": "pass", "detail": "d"}),
                         "an unmeasured lane was stamped")
        self.assertEqual("", gate.lane_stamp({"check": "x", "seconds": None}),
                         "an explicit null was read as a number")
        # The POSITIVE CONTROL: without it, a renderer that stamps nothing at all passes.
        self.assertEqual(" [1.2s]", gate.lane_stamp({"check": "x", "seconds": 1.25}))
        self.assertEqual(" [0.0s]", gate.lane_stamp({"check": "x", "seconds": 0.0}),
                         "a MEASURED zero is a measurement and must still print")


class SuiteVerdictReuseTests(unittest.TestCase):
    """The commit hook's suite verdict and the reuse decision it feeds (US0493).

    Renamed from `CloseVerdictReuseTests` when US0553 was reverted: the CLOSE has no business
    writing here, because `gate.main` runs no test suite and any green it recorded was
    fabricated. These tests cover the mechanism itself, whose one honest writer is
    `.githooks/commit-msg` after it has actually run the suites."""

    @staticmethod
    def _repo(tmp: Path) -> Path:
        """A tracked git tree - `surface_hash` reads `git ls-files` and returns None for a
        directory git cannot enumerate, so an untracked fixture would make every assertion
        here a comparison of two Nones."""
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        (suite / "test_thing.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "SRC = REPO / 'sdlc-studio' / 'trd.md'\n"
            "def test_thing():\n"
            "    assert SRC.read_text()\n", encoding="utf-8")
        ws = tmp / "sdlc-studio"
        ws.mkdir(parents=True)
        (ws / "trd.md").write_text("# trd\n", encoding="utf-8")
        (ws / ".local").mkdir()
        gitutil.git(["init", "-q"], cwd=tmp)
        gitutil.git(["add", "-A"], cwd=tmp)
        gitutil.git(["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "c"], cwd=tmp)
        return tmp

    def test_a_recorded_green_carries_the_hash_of_the_tree_it_verified(self) -> None:
        """The gate-side half of the contract. That the CLOSE makes this call is asserted in
        `test_sprint.py::CloseVerdictReuseTests` - naming that here would be a test whose name
        promises a caller it never exercises."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            self.assertIsNone(gate.read_suite_verdict(root), "nothing recorded yet")
            gate.record_suite_verdict(root, run="RUN-CLOSE", status="green", mode="full")
            recorded = gate.read_suite_verdict(root)
            self.assertEqual("green", recorded["status"])
            self.assertEqual("full", recorded["mode"])
            digest = gate.surface_hash(root)
            self.assertIsNotNone(digest, "an unhashable fixture would make the next line vacuous")
            self.assertEqual(digest, recorded["surface_hash"],
                             "the verdict must carry the hash of the tree it verified")

    def test_a_close_phase_commit_over_an_unchanged_surface_reuses_the_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            gate.record_suite_verdict(root, run="RUN-CLOSE", status="green", mode="full")
            decision = gate.suite_decision(root)
            self.assertFalse(decision["run"], decision["reason"])
            self.assertEqual("reuse", decision["mode"])
            self.assertEqual("RUN-CLOSE", decision["reused"])

    def test_a_moved_surface_refuses_the_reuse(self) -> None:
        """The half that stops the saving becoming a blind spot, and the reason the reason
        string matters: a refusal has to say the surface moved, not report a match."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            gate.record_suite_verdict(str(root), run="RUN-CLOSE", status="green", mode="full")
            src = root / ".claude/skills/sdlc-studio/scripts/tests/test_thing.py"
            src.write_text(src.read_text() + "\ndef test_more():\n    assert True\n",
                           encoding="utf-8")
            decision = gate.suite_decision(str(root))
            self.assertTrue(decision["run"])
            self.assertNotEqual("reuse", decision["mode"])
            self.assertIn("surface", decision["reason"].lower())

    def test_a_verdict_from_a_selected_run_is_not_reused_at_a_boundary(self) -> None:
        """A green from a SELECTED run is evidence about the tests that ran, not the suite.
        A close is a boundary, so it must decline that verdict rather than inherit it."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            gate.record_suite_verdict(root, run="RUN-PARTIAL", status="green", mode="selected")
            decision = gate.suite_decision(root, boundary="close")
            self.assertTrue(decision["run"], "a boundary cannot inherit a selected green")
            self.assertNotEqual("reuse", decision["mode"])

    def test_a_red_verdict_is_never_reused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d)))
            gate.record_suite_verdict(root, run="RUN-RED", status="red", mode="full")
            decision = gate.suite_decision(root)
            self.assertTrue(decision["run"])
            self.assertNotEqual("reuse", decision["mode"])


class ListingOnlyIdScopeTests(unittest.TestCase):
    """US0554. A listing-only declaration was a DIRECTORY, so a module whose structural read
    depends on four named ids made every new file anywhere under that tree structural - and
    filing an artefact is most of what a sprint close does. A declaration may now name the ids
    it depends on; naming none keeps the whole directory, which is what every existing
    declaration means and the direction a wrong one has to fail in."""

    @staticmethod
    def _repo(tmp: Path, decl: str) -> Path:
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        ws = tmp / "sdlc-studio"
        (ws / "bugs").mkdir(parents=True)
        # A REAL artefact shape. A declared id now resolves against the artefact index rather
        # than a filename pattern, so a fixture whose heading is `# named` is not an
        # artefact - which is the point: a stray `BG288-repro.md` must not satisfy a
        # declaration either.
        (ws / "bugs" / "BG0288-named.md").write_text(
            "# BG0288: named\n\n> **Status:** Open\n", encoding="utf-8")
        (ws / "bugs" / "BG0001-other.md").write_text(
            "# BG0001: other\n\n> **Status:** Open\n", encoding="utf-8")
        (ws / "trd.md").write_text("# trd\n", encoding="utf-8")
        (suite / "test_census.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            f"GATE_LISTING_ONLY = {decl}\n"
            "WS = REPO / 'sdlc-studio'\n"
            "TRD = REPO / 'sdlc-studio' / 'trd.md'\n"
            "def test_census():\n"
            "    assert list(WS.glob('**/BG0288*.md'))\n"
            "    assert TRD.read_text()\n", encoding="utf-8")
        return tmp

    #: The mapping form: the directory read as a listing, plus the ids that read depends on.
    SCOPED = "({'path': 'sdlc-studio', 'ids': ('BG0288',)},)"

    def test_a_declaration_parses_its_directory_and_its_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.SCOPED))
            self.assertIn("sdlc-studio", gate.listing_only_paths(root),
                          "the mapping form still declares its directory listing-only")
            self.assertEqual({"sdlc-studio": frozenset({"BG0288"})},
                             gate.listing_only_scopes(root))

    def test_a_malformed_id_set_is_refused_rather_than_partially_honoured(self) -> None:
        """A declaration nobody can read must not become a narrowing nobody intended. It
        degrades to the whole directory - the meaning it had before ids existed."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), "({'path': 'sdlc-studio', 'ids': 17},)"))
            self.assertIn("sdlc-studio", gate.listing_only_paths(root))
            self.assertEqual({"sdlc-studio": None}, gate.listing_only_scopes(root),
                             "an unreadable id set falls back to the whole directory")
            added = "sdlc-studio/bugs/BG0002-new.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}))

    def test_an_unnamed_id_is_not_structural(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.SCOPED))
            added = "sdlc-studio/bugs/BG0002-new.md"
            self.assertFalse(
                gate.is_test_relevant([added], root, structural={added}),
                "filing an artefact the declaring module never reads cannot change its answer")

    def test_a_named_id_stays_structural(self) -> None:
        """The other half, and the one that stops the narrowing becoming an exemption."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.SCOPED))
            added = "sdlc-studio/bugs/BG0288-named.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}))

    def test_a_declaration_with_no_ids_keeps_the_whole_directory_structural(self) -> None:
        """The form every existing declaration uses. The narrowing is opt-in, so a module
        that omits its ids is slower than it needs to be rather than wrong."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), "('sdlc-studio',)"))
            self.assertEqual({"sdlc-studio": None}, gate.listing_only_scopes(root))
            added = "sdlc-studio/bugs/BG0002-new.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}))

    def test_an_empty_id_tuple_falls_back_to_the_whole_directory(self) -> None:
        """An empty set is not "depends on nothing" - read that way it would exempt the entire
        tree, which is the opposite of what a narrowing may do. It means the same as omitting
        the key: the whole directory."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), "({'path': 'sdlc-studio', 'ids': ()},)"))
            self.assertEqual({"sdlc-studio": None}, gate.listing_only_scopes(root))
            added = "sdlc-studio/bugs/BG0002-new.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}))

    def test_two_modules_reading_one_tree_take_the_union_of_their_ids(self) -> None:
        """One module's narrowing must never speak for another's read - the class BG0398
        records. Two scoped declarations union; a bare one beside a scoped one wins outright,
        because the module that named no ids depends on all of them."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), self.SCOPED)
            suite = root / ".claude/skills/sdlc-studio/scripts/tests"
            second = suite / "test_other_census.py"
            second.write_text(
                "from pathlib import Path\n"
                "REPO = Path(__file__).resolve().parents[5]\n"
                "GATE_LISTING_ONLY = ({'path': 'sdlc-studio', 'ids': ('BG0001',)},)\n"
                "WS = REPO / 'sdlc-studio'\n"
                "def test_other():\n"
                "    assert list(WS.glob('**/BG0001*.md'))\n", encoding="utf-8")
            self.assertEqual({"sdlc-studio": frozenset({"BG0288", "BG0001"})},
                             gate.listing_only_scopes(str(root)))
            second.write_text(second.read_text().replace(
                "({'path': 'sdlc-studio', 'ids': ('BG0001',)},)", "('sdlc-studio',)"),
                encoding="utf-8")
            self.assertEqual({"sdlc-studio": None}, gate.listing_only_scopes(str(root)),
                             "a module that named no ids depends on all of them")

    def test_a_structural_file_carrying_no_id_stays_relevant_under_a_scoped_directory(self) -> None:
        """An id is how a path is matched against the scope. A file whose name carries none
        cannot be judged, and an unanswered question runs the suites - the same direction
        `structural=None` degrades in."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.SCOPED))
            added = "sdlc-studio/notes/scratch.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}))

    def test_a_body_edit_is_still_irrelevant_whichever_id_it_is(self) -> None:
        """The id scope narrows the STRUCTURAL half only. Editing prose could never change a
        listing, and that must stay true for a named id as much as an unnamed one."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.SCOPED))
            for path in ("sdlc-studio/bugs/BG0288-named.md", "sdlc-studio/bugs/BG0001-other.md"):
                with self.subTest(path=path):
                    self.assertFalse(gate.is_test_relevant([path], root, structural=set()))

    def test_a_narrower_read_under_a_scoped_directory_keeps_its_content_relevance(self) -> None:
        """The trap `_minimal` set for BG0383, re-checked against the scoped form: a file the
        suite genuinely OPENS must survive underneath the census that only counts."""
        with tempfile.TemporaryDirectory() as d:
            root = str(self._repo(Path(d), self.SCOPED))
            self.assertIn("sdlc-studio/trd.md", gate.test_relevant_paths(root))
            self.assertTrue(gate.is_test_relevant(["sdlc-studio/trd.md"], root, structural=set()))


class SilenceWithholdsTheNarrowingTests(unittest.TestCase):
    """BG0407. `listing_only_scopes` built its electorate from `suite_read_map`, which cannot
    see a path assembled at run time - 59 of 170 modules here measure an EMPTY read set. Such a
    module was not counted as a reader, so its content read was silenced by another module's
    declaration. The contradiction was inside one file: `select_tests` reads an empty read map
    as an unanswered question and always includes the module; `listing_only_scopes` read the
    identical silence as 'not a reader, so the declaration is unanimous'."""

    @staticmethod
    def _repo(tmp: Path, *, dynamic_reader: bool) -> str:
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        ws = tmp / "sdlc-studio"
        (ws / "bugs").mkdir(parents=True)
        # A REAL artefact shape. A declared id now resolves against the artefact index rather
        # than a filename pattern, so a fixture whose heading is `# named` is not an
        # artefact - which is the point: a stray `BG288-repro.md` must not satisfy a
        # declaration either.
        (ws / "bugs" / "BG0288-named.md").write_text(
            "# BG0288: named\n\n> **Status:** Open\n", encoding="utf-8")
        (suite / "test_census.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            "GATE_LISTING_ONLY = ('sdlc-studio',)\n"
            "WS = REPO / 'sdlc-studio'\n"
            "def test_census():\n"
            "    assert list(WS.glob('**/*.md'))\n", encoding="utf-8")
        if dynamic_reader:
            # The module BG0407 is about: it reads the SAME tree for CONTENT, but assembles the
            # path at run time from an imported constant, so the static scanner measures it
            # empty and it never appears in the electorate.
            (suite / "test_dynamic.py").write_text(
                "from pathlib import Path\n"
                "import os\n"
                "BASE = os.environ.get('WS_DIR', 'sdlc-studio')\n"
                "def test_content():\n"
                "    REPO = Path(__file__).resolve().parents[5]\n"
                "    assert (REPO / BASE / 'bugs' / 'BG0288-named.md').read_text()\n",
                encoding="utf-8")
        return str(tmp)

    def test_an_unmeasurable_module_withholds_the_narrowing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), dynamic_reader=True)
            self.assertEqual({}, gate.listing_only_scopes(root),
                             "a module whose read set could not be measured was counted as a "
                             "non-reader, so its content read was silenced by another "
                             "module's declaration")

    def test_with_every_module_measurable_the_narrowing_still_applies(self) -> None:
        """The positive control. Withholding on silence must not become withholding always -
        that would delete the mechanism rather than fix it."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), dynamic_reader=False)
            self.assertIn("sdlc-studio", gate.listing_only_scopes(root),
                          "a declaration every reader agrees with was withheld anyway")

    def test_the_two_readings_of_silence_agree(self) -> None:
        """AC2, asserted directly: what `select_tests` treats as unanswered,
        `listing_only_scopes` must also treat as unanswered. Both derive the set the same way."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), dynamic_reader=True)
            unattributable = {m for m, paths in gate.suite_read_map(root).items() if not paths}
            self.assertTrue(unattributable, "fixture did not produce an unmeasurable module")
            self.assertEqual(unattributable, set(gate.unmeasurable_modules(root)),
                             "the two readings of an empty read map disagree")

    def test_the_withheld_cost_is_reported_not_silent(self) -> None:
        """AC3: say how many modules were unmeasurable when the narrowing is withheld, so the
        cost is attributable and someone can make those reads visible."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), dynamic_reader=True)
            notes = gate.withheld_narrowings(root)
            joined = " ".join(notes)
            self.assertTrue(notes, "the narrowing was withheld with no report at all")
            self.assertIn("sdlc-studio", joined)
            self.assertRegex(joined, r"\b1\b", "the count of unmeasurable modules is not named")


class ADeclaredIdMustNameARealArtefactTests(unittest.TestCase):
    """BG0411. `_declared_ids` required a declared id to RESOLVE, but resolved it by matching
    the id pattern against any BASENAME under the directory. One stray `BG288-repro.png` - a
    screenshot, an attachment, a scratch note - makes a typo'd `BG288` resolve and restores the
    false green in full. The check validated a filename pattern, not the artefact it claims to
    require."""

    @staticmethod
    def _repo(tmp: Path, decl: str, *, stray: str | None = None) -> str:
        suite = tmp / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
        suite.mkdir(parents=True)
        ws = tmp / "sdlc-studio"
        (ws / "bugs").mkdir(parents=True)
        (ws / "bugs" / "BG0288-named.md").write_text(
            "# BG0288: named\n\n> **Status:** Open\n", encoding="utf-8")
        if stray:
            (ws / stray).parent.mkdir(parents=True, exist_ok=True)
            (ws / stray).write_bytes(b"\x89PNG not an artefact")
        (suite / "test_census.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path(__file__).resolve().parents[5]\n"
            f"GATE_LISTING_ONLY = {decl}\n"
            "WS = REPO / 'sdlc-studio'\n"
            "def test_census():\n"
            "    assert list(WS.glob('**/BG0288*.md'))\n", encoding="utf-8")
        return str(tmp)

    TYPO = "({'path': 'sdlc-studio', 'ids': ('BG288',)},)"

    def test_a_typod_id_withholds_the_narrowing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), self.TYPO)
            self.assertEqual({"sdlc-studio": None}, gate.listing_only_scopes(root),
                             "an unresolvable id narrowed the tree instead of voiding")

    def test_a_stray_non_artefact_does_not_restore_the_narrowing(self) -> None:
        """The defect itself. A file merely MATCHING the id filename pattern must not satisfy
        a declaration that says it requires the artefact."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), self.TYPO, stray="BG288-repro.png")
            self.assertEqual({"sdlc-studio": None}, gate.listing_only_scopes(root),
                             "a stray screenshot resolved a typo'd id and restored a false green")
            added = "sdlc-studio/bugs/BG0288-named.md"
            self.assertTrue(gate.is_test_relevant([added], root, structural={added}),
                            "the declaring module's own artefact answered `not relevant`")

    def test_a_real_artefact_still_resolves(self) -> None:
        """Positive control: requiring a real artefact must not refuse every declaration."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), "({'path': 'sdlc-studio', 'ids': ('BG0288',)},)")
            self.assertEqual({"sdlc-studio": frozenset({"BG0288"})},
                             gate.listing_only_scopes(root))

    def test_the_withheld_narrowing_is_reported_without_sdlc_debug(self) -> None:
        """A declaration that has STOPPED working should be as visible as one that never
        worked. It was reported only through `sdlc_md.debug`, a no-op without SDLC_DEBUG=1,
        so the author saw only a gate that never got faster."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), self.TYPO)
            os.environ.pop("SDLC_DEBUG", None)
            notes = " ".join(gate.withheld_narrowings(root))
            self.assertIn("BG288", notes, "the unresolvable id is not named")
            self.assertIn("sdlc-studio", notes, "the declaration is not named")


class LaneCheckLaneTests(unittest.TestCase):
    """The lane-check must run in the gate, advisorily, with its yield recorded.

    A detector nobody runs finds nothing, and a yield nobody accumulates cannot support the
    decision to make it block. Both halves are pinned because the first version of the
    claim-drift accumulator wrote to a TRACKED path and dirtied the tree on every commit
    (BG0481).
    """

    # scripts/tests -> scripts -> sdlc-studio -> skills -> .claude -> REPO ROOT
    HOOK = Path(__file__).resolve().parents[5] / ".githooks" / "pre-commit"

    def test_the_lane_runs_and_does_not_block(self) -> None:
        """MUTANT: delete the lane from the hook, or let its exit code reach the gate."""
        text = self.HOOK.read_text(encoding="utf-8")
        self.assertIn("lane-check", text,
                      "the pre-commit hook never runs lane-check, so the detector finds "
                      "nothing on any real commit")
        self.assertIn("verify_ac.py", text,
                      "the hook mentions lane-check but never invokes verify_ac")
        block = text.split("lane-check")[1][:600]
        self.assertIn("|| true", block,
                      "the lane can fail the commit - it ships ADVISORY until its yield is "
                      "measured")

    def test_the_pass_runs_through_its_own_command(self) -> None:
        """MUTANT: break the `lane-check` subcommand wiring in verify_ac's parser.

        Added because the lane-check REPORTED THIS UNIT: its other two verifiers assert on the
        hook's text and never enter verify_ac at all, so a broken subcommand would leave them
        both green. The detector caught its own author, which is the strongest evidence it
        discriminates.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "verify_ac", Path(__file__).resolve().parent.parent / "verify_ac.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["verify_ac"] = mod
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                rc = mod.main(["lane-check", "--root", str(root)])
        self.assertEqual(0, rc, "the lane-check command is not advisory - it failed the gate")
        self.assertIn("lane-check", buf_out.getvalue() + buf_err.getvalue(),
                      "the command produced no report at all")

    def test_the_yield_accumulates_under_local(self) -> None:
        """MUTANT: point the accumulator at a tracked path, as BG0481 did.

        A hook-written record under a tracked path dirties the working tree on every commit
        with a file the author never touched and the hook never stages.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "verify_ac", Path(__file__).resolve().parent.parent / "verify_ac.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["verify_ac"] = mod
        spec.loader.exec_module(mod)
        self.assertIn("/.local/", mod._LANE_YIELD_REL,
                      f"the yield is written to {mod._LANE_YIELD_REL}, which is not under "
                      f".local/ - it would dirty the tree on every commit")


class ReviewCadenceTests(unittest.TestCase):
    """A sprint close gates on ITS OWN review coverage, not on an unrelated periodic ceremony.

    Measured on a real close: nine units, each with independent adversarial evidence, an
    APPROVE verdict after repair, a confirmation pass and a reviewer-of-record sign-off - and
    the close still stopped, because the repo-wide unified review was 59 artefacts stale, all
    of it predating the run. The documented bounded exit refused it too, classing the lane a
    hard correctness blocker.
    """

    def _mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gate", Path(__file__).resolve().parent.parent / "gate.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["gate"] = mod
        spec.loader.exec_module(mod)
        return mod

    def _root(self, d, *, covered: bool):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        for uid in ("US0001", "US0002"):
            (root / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
                f"# {uid}: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
                f"> **Affects:** src/a.py\n", encoding="utf-8")
        import json
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"run_id": "RUN-T", "batch": ["US0001", "US0002"]}), encoding="utf-8")
        if covered:
            import critic
            for uid in ("US0001", "US0002"):
                critic.record_verdict(root, uid, "APPROVE", "qa seat", "author",
                                      issues="none blocking", brief="abcdef123456")
        return root

    def test_a_covered_batch_closes_with_a_stale_unified_review(self) -> None:
        """MUTANT: keep `blocking: True` when the batch is covered."""
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, covered=True)
            covered, why = mod._batch_is_independently_covered(root)
        self.assertTrue(covered, f"a fully covered batch was not recognised as covered: {why}")

    def test_an_uncovered_batch_still_refuses(self) -> None:
        """The positive control. MUTANT: return True unconditionally.

        Without this the change becomes a way to close an UNREVIEWED batch, which is the
        opposite failure and a worse one.
        """
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, covered=False)
            covered, _why = mod._batch_is_independently_covered(root)
        self.assertFalse(covered, "a batch with no recorded verdicts was treated as covered")

    def test_no_open_run_is_not_covered(self) -> None:
        """MUTANT: treat an absent run as vacuously covered.

        Fails CLOSED: absent evidence must never turn a blocking lane advisory, or the
        exemption is reachable by deleting the run state.
        """
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            covered, _why = mod._batch_is_independently_covered(root)
        self.assertFalse(covered, "an absent run state read as covered - the exemption is "
                                  "reachable by deleting a file")

    def test_the_staleness_is_reported_even_when_it_does_not_block(self) -> None:
        """MUTANT: drop the detail when the lane stops blocking.

        Proceeding and forgetting must stay different events. A lane that goes quiet the moment
        it stops blocking has simply been switched off.
        """
        mod = self._mod()
        src = (Path(__file__).resolve().parent.parent / "gate.py").read_text(encoding="utf-8")
        block = src.split("_batch_is_independently_covered(rr)")[1][:900]
        self.assertIn("CADENCE DEBT", block,
                      "the non-blocking path does not report the staleness at all")
        self.assertIn("still owed", block,
                      "the report does not say the repo-wide review remains owed")


class LoaderRouteTests(unittest.TestCase):
    """A test module is selected for the script it LOADS, not only the one it is named after.

    The naming route reaches `x.py -> test_x.py` and nothing else, while the class is broader:
    `test_two_backlogs.py` loads `refine.py`. Measured, that module is currently selected
    anyway - but only because it measures EMPTY and is swept in as unattributable. The moment
    it gains resolvable reads it stops being unattributable and would be DROPPED for changes to
    the very script it tests, which is the latent defect this closes.
    """

    def _mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gate", Path(__file__).resolve().parent.parent / "gate.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["gate"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_the_index_is_derived_from_the_loader_calls(self) -> None:
        """MUTANT: build the index from the filename convention instead.

        Uses the repo's own modules: `test_two_backlogs.py` loads `refine.py` under a name
        that shares nothing with its own, so a convention-derived index cannot contain it.
        """
        mod = self._mod()
        # tests -> scripts -> sdlc-studio -> skills -> .claude -> REPO ROOT
        root = str(Path(__file__).resolve().parents[5])
        index = mod.loader_index(root)
        loaders = index.get("refine", set())
        self.assertTrue(
            any(m.endswith("test_two_backlogs.py") for m in loaders),
            "a module that loads refine.py under a different name is not in the index")

    def test_a_module_with_real_reads_is_still_selected_for_what_it_loads(self) -> None:
        """MUTANT: delete the loader route from select_tests.

        THE point of the fix. Built on a fixture whose test module has resolvable reads, so it
        is NOT unattributable and the fallback sweep cannot rescue it - which is precisely the
        state the repo's own modules move into as they gain reads.
        """
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tests = root / ".claude/skills/sdlc-studio/scripts/tests"
            tests.mkdir(parents=True)
            (root / ".claude/skills/sdlc-studio/scripts" / "subject.py").write_text(
                "def f():\n    return 1\n", encoding="utf-8")
            (tests / "test_unrelated_name.py").write_text(
                'import importlib.util\n'
                'spec = importlib.util.spec_from_file_location("subject", "x")\n'
                '# a resolvable read, so this module is NOT unattributable:\n'
                'DOC = "sdlc-studio/trd.md"\n', encoding="utf-8")
            index = mod.loader_index(str(root))
            # THROUGH `select_tests`, which is what the docstring's mutant names. The first
            # version asserted only on `loader_index`, so deleting the two lines the fix added
            # to `select_tests` left all 391 tests of this module green - the repair was
            # unpinned by its own criterion.
            selected = mod.select_tests(
                str(root), [".claude/skills/sdlc-studio/scripts/subject.py"])
        self.assertIn("subject", index,
                      "the loader index does not resolve a script loaded under another name")
        self.assertTrue(any(m.endswith("test_unrelated_name.py") for m in index["subject"]),
                        "the module that loads it was not attributed to it")
        self.assertTrue(
            selected.get("resolved"),
            f"the selection did not resolve, so it falls back to running everything and the "
            f"loader route proves nothing: {selected.get('reason')}")
        self.assertTrue(
            any("test_unrelated_name.py" in s for s in selected.get("selectors") or []),
            f"`select_tests` did not select the module that LOADS the changed script - the "
            f"loader route is not wired into the selection: {selected.get('selectors')}")



class ReleaseVerifyScopeTests(unittest.TestCase):
    """BG0530 AC5: the release verify lane walks stories only, and never said so.

    No bug's acceptance criteria has entered the release gate in ANY version - 534 files, 55%
    of the delivery corpus, silently outside a pass the lane reports on "the AC layer". A
    verification pass taken over a fraction of the corpus while reporting on the whole is the
    same false green one level up.
    """

    def test_the_release_lane_states_its_scope(self) -> None:
        """Mutant: drop the scope statement - the lane keeps reporting a pass over 55% of the
        delivery corpus it never looked at, and no reader can tell.

        The count is DERIVED from the tree, not typed, so it moves when the scope does.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gate_scope_bg0530", Path(__file__).resolve().parents[1] / "gate.py")
        g = importlib.util.module_from_spec(spec)
        sys.modules["gate_scope_bg0530"] = g
        spec.loader.exec_module(g)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: it behaves\n\n- **Then** it behaves\n- **Verify:** shell true\n",
                encoding="utf-8")
            for n in (1, 2, 3):
                (root / "sdlc-studio" / "bugs" / f"BG{n:04d}-x.md").write_text(
                    f"# BG{n:04d}: b\n\n> **Status:** Open\n\n## Acceptance Criteria\n\n"
                    f"### AC1: it behaves\n\n- **Then** it behaves\n", encoding="utf-8")
            res = g._verify_acs(str(root), batch=False)
            detail = res.get("detail", "")
            self.assertIn("SCOPE", detail,
                          "the release verify lane reports a pass without naming what it "
                          f"did not walk: {detail}")
            self.assertIn("3 bug file(s)", detail,
                          f"the skipped count is not derived from the tree: {detail}")


class DocSurfaceLaneTests(unittest.TestCase):
    """US0655: the verb-coverage number reaches the places people already look."""

    def _mod(self, name):
        import importlib.util, sys as _s
        d = pathlib.Path(__file__).resolve().parent.parent
        _s.path.insert(0, str(d)); _s.path.insert(0, str(d / "lib"))
        spec = importlib.util.spec_from_file_location(name, d / f"{name}.py")
        m = importlib.util.module_from_spec(spec)
        _s.modules[name] = m
        spec.loader.exec_module(m)
        return m

    def test_the_lane_reports_verbs_distinguishably_and_does_not_change_the_exit_code(self):
        """AC1. `gate.py` ALREADY prints "N undocumented" from `doc-coverage`, which counts
        SCRIPTS - a different granularity of the same word. Two lanes saying it are two numbers
        a reader has to reconcile with nothing telling them they differ.

        Mutant: make the lane fail the gate when the count is non-zero.
        Mutant: word the detail as "N undocumented", identical to the sibling lane.
        """
        g = self._mod("gate")
        res = g._doc_surface(str(pathlib.Path(__file__).resolve().parents[4]))
        self.assertFalse(res["blocking"],
                         "the doc-surface lane blocks, so under-documentation fails a commit")
        self.assertIn("verb", res["detail"],
                      "the lane's wording does not say VERBS, so it reads as the script-level "
                      "doc-coverage number beside it")

    def test_both_readers_move_when_the_defining_module_is_patched(self):
        """AC4. Asserting the two readers AGREE proves nothing: two correct readers over one
        tree agree by construction, and the re-derivation mutant survives an equality check.

        The patch is on `command_audit`, THE MODULE THAT DEFINES the measurement, and each
        reader must call through it rather than bind the name at import.

        Mutant: give the gate lane its own re-derivation of the count.
        Mutant: have a reader bind the measurement by `from ... import` at load time.
        """
        g = self._mod("gate")
        sr = self._mod("sprint_report")
        ca = self._mod("command_audit")
        root = str(pathlib.Path(__file__).resolve().parents[4])
        sentinel = {"verbs": 4242, "documented": 4242, "undocumented": 4242, "ratio": 42.0,
                    "missing": []}
        real = ca.verb_coverage
        try:
            ca.verb_coverage = lambda *a, **k: sentinel  # noqa: ARG005
            lane = g._doc_surface(root)
            _state, value, _detail = sr._ck_doc_surface({"root": root})
        finally:
            ca.verb_coverage = real
        self.assertEqual(4242, lane["count"],
                         "the gate lane did not move when the DEFINING module was patched, so "
                         "it re-derives its own count")
        self.assertIn("4242", value,
                      "the close row did not move when the defining module was patched")

    def test_an_unmeasurable_lane_does_not_render_as_perfect_coverage(self):
        """AC1's other half. Zero is this lane's CLEAN state, so a broken measurement reported as
        zero renders identically to full coverage, and a reader scanning counts never reads the
        word `unreadable` beside it.

        Mutant: return count 0 when the measurement raises.
        Mutant: let the exception escape, breaking an advisory lane's whole gate.
        """
        g = self._mod("gate")
        ca = self._mod("command_audit")
        root = str(pathlib.Path(__file__).resolve().parents[4])
        real = ca.verb_coverage
        try:
            def _boom(*a, **k):  # noqa: ARG001
                raise RuntimeError("the enumerator is broken")
            ca.verb_coverage = _boom
            res = g._doc_surface(root)
        finally:
            ca.verb_coverage = real
        self.assertFalse(res["blocking"], "an advisory lane broke the gate")
        self.assertNotEqual(0, res["count"],
                            "a measurement that RAISED reported the same count as full "
                            "coverage - the failure is invisible to anyone reading numbers")
        self.assertIn("NOT MEASURED", res["detail"])
        self.assertIn("RuntimeError", res["detail"], "the detail does not name what broke")

    def test_the_lint_aggregate_runs_disclosure_and_the_aggregate_still_passes(self):
        """AC2's SECOND clause, which was true by hand and pinned nowhere. The whole point of
        joining `lint:disclosure` to `npm run lint` is that it reports without failing it; a
        script under the aggregate that exits non-zero turns an advisory report into a blocker
        for every contributor.

        Mutant: add `lint:disclosure` to the aggregate but let disclosure.py exit non-zero.
        Mutant: drop `lint:disclosure` from the aggregate again.
        """
        import json, subprocess
        root = pathlib.Path(__file__).resolve().parents[5]   # the REPO root, not .claude/
        pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
        scripts = pkg["scripts"]
        self.assertIn("lint:disclosure", scripts["lint"],
                      "the disclosure lane is not in the `npm run lint` aggregate, so the "
                      "checker that would catch this gap still runs nowhere")
        proc = subprocess.run(scripts["lint:disclosure"], shell=True, cwd=root,  # noqa: S602
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(0, proc.returncode,
                         f"`lint:disclosure` exited {proc.returncode} inside the aggregate, so "
                         f"`npm run lint` now fails on an advisory report: {proc.stderr[-400:]}")
        self.assertTrue(proc.stdout.strip(), "the lane produced no report at all")



if __name__ == "__main__":
    unittest.main()
