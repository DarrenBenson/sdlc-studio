"""Unit tests for handoff.py's read-only join + lib/run_state.py.

The class these lock: the join names EVERY remaining item, each with a pointer (file / AC /
check) and a suitability tag. A join that silently omits a remaining item is worse than none
(LL0008), so the omission cases are the load-bearing tests here: a batch id with no file on
disk, and a quarantined unit that was never in the approved batch, both still appear. No
command writes a handoff since US0978; the HO files already written stay resolvable and
reconciled (`RegistrationTests`).
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
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import run_state, sdlc_md  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


handoff = _load("handoff")
artifact = _load("artifact")
next_id = _load("next_id")
sprint = _load("sprint")
reconcile = _load("reconcile")


# --------------------------------------------------------------------------- fixtures
def _story(root: Path, num: int, status: str = "In Progress", acs: int = 1,
           affects: str = "", points: str = "") -> Path:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    body = [f"# US{num:04d}: story {num}", "", f"> **Status:** {status}",
            "> **Epic:** [EP0001: e](../epics/EP0001-e.md)"]
    if affects:
        body.append(f"> **Affects:** {affects}")
    if points:
        body.append(f"> **Story Points:** {points}")
    body += ["", "## Acceptance Criteria", ""]
    for i in range(1, acs + 1):
        body.append(f"- **AC{i}:** it works")
        body.append("  - **Verify:** pytest tests/test_x.py")
    body.append("")
    p = d / f"US{num:04d}-story-{num}.md"
    p.write_text("\n".join(body) + "\n", encoding="utf-8")
    return p


def _cr(root: Path, num: int, status: str = "Proposed") -> Path:
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"CR{num:04d}-change-{num}.md"
    p.write_text(f"# CR-{num:04d}: change {num}\n\n> **Status:** {status}\n"
                 f"> **Priority:** Medium\n\n## Acceptance Criteria\n\n- [ ] it works\n",
                 encoding="utf-8")
    return p


def _handoff_index(root: Path) -> Path:
    d = root / "sdlc-studio" / "handoffs"
    d.mkdir(parents=True, exist_ok=True)
    idx = d / "_index.md"
    idx.write_text("# Handoff Index\n\n**Last Updated:** 2026-07-13\n\n"
                   "| ID | Title | Date |\n| --- | --- | --- |\n", encoding="utf-8")
    return idx


def _old_handoff(root: Path) -> Path:
    """An HO file and its index row as `handoff generate` wrote them before US0978 retired it."""
    _handoff_index(root)
    idx = root / "sdlc-studio" / "handoffs" / "_index.md"
    idx.write_text(idx.read_text(encoding="utf-8").rstrip("\n")
                   + "\n| [HO-0001](HO0001-close.md) | close | 2026-07-13 |\n", encoding="utf-8")
    ho = root / "sdlc-studio" / "handoffs" / "HO0001-close.md"
    ho.write_text("# HO-0001: close\n\n> **Date:** 2026-07-13\n> **Created-by:** sdlc-studio new\n"
                  "\n## Where to pick up\n\n- US0002 - its file\n", encoding="utf-8")
    return ho


def _loop_state(root: Path, units: dict) -> None:
    p = root / "sdlc-studio" / ".local" / "loop-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"units": units}, indent=2), encoding="utf-8")


def _verify_report(root: Path, stories: dict) -> None:
    p = root / "sdlc-studio" / ".local" / "verify-report.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"generated_at": "2026-07-13T00:00:00Z", "stories": stories},
                            indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- run state
class RunStateTests(unittest.TestCase):
    """The run-level context object nothing joined before: one id, one start time, one
    outcome, extensible (the appetite breaker builds on it)."""

    def test_open_run_stamps_id_started_at_and_batch(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            st = run_state.open_run(root, batch=["US0001", "CR0002"], goal="done")
            self.assertTrue(st["run_id"].startswith("RUN-"))
            self.assertTrue(st["started_at"])
            self.assertEqual(st["batch"], ["US0001", "CR0002"])
            self.assertEqual(st["goal"], "done")
            self.assertEqual(st["outcome"], run_state.RUNNING)
            self.assertIsNone(st["ended_at"])
            self.assertEqual(run_state.read(root), st)

    def test_reopening_keeps_the_run_id_and_start_and_ACCUMULATES_the_batch(self) -> None:
        """F1: a mid-run re-plan must never DISCARD an approved unit. The run's batch is
        cumulative - the union of every batch approved under this run_id - because
        `handoff.build` joins over it, and a unit dropped from a re-cut that the loop never
        attempted would otherwise land in no bucket at all and vanish from the handover."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            first = run_state.open_run(root, batch=["US0001", "US0002", "US0003"], goal="done")
            again = run_state.open_run(root, batch=["US0001"], goal="done")   # narrowed re-cut
            self.assertEqual(again["run_id"], first["run_id"])
            self.assertEqual(again["started_at"], first["started_at"])
            self.assertEqual(again["batch"], ["US0001", "US0002", "US0003"])

    def test_the_batch_is_a_union_in_first_approval_order_without_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            run_state.open_run(root, batch=["US0002", "US0001"])
            st = run_state.open_run(root, batch=["US0001", "US0004"])
            self.assertEqual(st["batch"], ["US0002", "US0001", "US0004"])

    def test_a_new_run_does_not_inherit_the_previous_run_s_batch(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            run_state.open_run(root, batch=["US0001", "US0002"])
            run_state.close_run(root, outcome=run_state.BLOCKED)
            st = run_state.open_run(root, batch=["US0009"])
            self.assertEqual(st["batch"], ["US0009"])

    def test_a_corrupt_run_state_fails_loud_it_never_reads_as_no_run(self) -> None:
        """F4: `read_json` swallows a parse error and returns the default, so a truncated
        run-state read as "no run was ever opened" - and the handoff then PRINTED that, over
        a run that was opened, while the close wrote a blank record over the wreckage. A
        silently-dropped field is a lie the next reader inherits."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            run_state.open_run(root, batch=["US0001"], goal="done")
            p = run_state.path(root)
            p.write_text(p.read_text(encoding="utf-8")[:40], encoding="utf-8")  # truncate
            with self.assertRaises(run_state.RunStateError) as ctx:
                run_state.read(root)
            self.assertIn(str(p), str(ctx.exception))
            # ...and nothing may overwrite it behind the operator's back
            for call in (lambda: run_state.update(root, k=1),
                         lambda: run_state.close_run(root, outcome=run_state.BLOCKED),
                         lambda: run_state.open_run(root, batch=["US0002"])):
                with self.assertRaises(run_state.RunStateError):
                    call()

    def test_a_judged_run_left_running_is_refused_not_accumulated(self) -> None:
        """BG0188's property, under BG0527's remedy.

        BG0188 established the harm: a run whose Sprint Goal was JUDGED but whose outcome was
        never finalised stays `running`, and the next `open_run` must NOT accumulate a new batch
        onto it - that reuses the old id and clobbers the recorded verdict. Its remedy was to
        treat the judged run as history and mint a fresh one.

        BG0527 found what that remedy costs. The goal verdict is written BEFORE the close chain,
        not by it, so every run passes through a judged-but-unclosed window in which its units are
        still at Review and its close is still owed. Minting a fresh run there does not clobber
        the verdict - it strands the whole run: no close, no cascade to Done, and no record that
        one was owed. Found live on RUN-01KZ9315, whose own pre-flight reported twenty unmet
        prerequisites while the slot guard had already stood down.

        So the remedy is now a REFUSAL naming the run to close. BG0188's property is strictly
        better served: the batch is not accumulated, the verdict is not clobbered, AND the owed
        close is not silently discarded. `ended_at` and `handoff` still release the slot, because
        those are written BY the close - the test below this one pins that and must keep passing.
        """
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            first = run_state.open_run(root, batch=["US0001", "US0002"], goal="done")
            run_state.update(root, sprint_goal_verdict={"verdict": "achieved", "note": "ok"})
            with self.assertRaises(run_state.DisjointBatchError) as caught:
                run_state.open_run(root, batch=["US0009"], goal="done")
            self.assertEqual(caught.exception.run_id, first["run_id"],
                             "the refusal does not name the run whose close is owed")
            after = run_state.read(root)
            self.assertEqual(after["run_id"], first["run_id"])
            self.assertEqual(after["batch"], ["US0001", "US0002"],
                             "BG0188's harm: the new batch was accumulated onto the judged run")
            self.assertEqual(after["sprint_goal_verdict"]["verdict"], "achieved",
                             "BG0188's harm: the recorded verdict was clobbered")

    def test_a_run_carrying_a_close_artefact_but_running_is_treated_as_closed(self) -> None:
        """BG0188, the wider guard: `ended_at` or a `handoff` recorded while outcome is still
        `running` is the same inconsistent state - a close that stamped its artefacts but did
        not finalise the outcome. Any of them means the run is spent; `open_run` mints fresh."""
        for artefact in ({"ended_at": "2026-07-17T00:00:00Z"}, {"handoff": "HO-0001"}):
            with tempfile.TemporaryDirectory() as t:
                root = Path(t)
                first = run_state.open_run(root, batch=["US0001"], goal="done")
                run_state.update(root, **artefact)
                fresh = run_state.open_run(root, batch=["US0009"], goal="done")
                self.assertNotEqual(fresh["run_id"], first["run_id"],
                                    f"a run carrying {artefact} must not be reopened")
                self.assertEqual(fresh["batch"], ["US0009"])

    def test_a_clean_running_run_still_accumulates(self) -> None:
        """The guard is narrow: a genuinely-open run (no close artefact) still re-plans in
        place and accumulates - BG0188 must not break the cumulative-batch invariant. The re-cut
        OVERLAPS the open batch (a disjoint one is refused by the one-run-slot guard, CR0401)."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            first = run_state.open_run(root, batch=["US0001"], goal="done")
            again = run_state.open_run(root, batch=["US0001", "US0002"], goal="done")
            self.assertEqual(again["run_id"], first["run_id"])
            self.assertEqual(again["batch"], ["US0001", "US0002"])

    def test_parallel_updates_never_lose_a_key(self) -> None:
        """F3: `update` was an unlocked read-modify-write, and concurrent writers lost keys.
        The appetite breaker's spend counter will be a read-increment-write on this object -
        a strictly wider window - so the lock is taken here, not left to every caller."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            run_state.open_run(root, batch=["US0001"])
            prog = (
                "import sys; sys.path.insert(0, %r)\n"
                "from lib import run_state\n"
                "root, w = sys.argv[1], int(sys.argv[2])\n"
                "for i in range(12):\n"
                "    run_state.update(root, **{'k_%%d_%%d' %% (w, i): w})\n" % str(SCR)
            )
            procs = [subprocess.Popen([sys.executable, "-c", prog, str(root), str(w)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                     for w in range(8)]
            for p in procs:
                _out, err = p.communicate(timeout=60)
                self.assertEqual(p.returncode, 0, err.decode())
            st = run_state.read(root)
            missing = [f"k_{w}_{i}" for w in range(8) for i in range(12)
                       if f"k_{w}_{i}" not in st]
            self.assertEqual(missing, [], f"{len(missing)} key(s) lost under 8 writers")
            self.assertEqual(st["batch"], ["US0001"])   # the run itself survived intact

    def test_a_closed_run_reopens_as_a_new_run(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            first = run_state.open_run(root, batch=["US0001"])
            run_state.close_run(root, outcome=run_state.BLOCKED)
            second = run_state.open_run(root, batch=["US0002"])
            self.assertNotEqual(second["run_id"], first["run_id"])
            self.assertEqual(second["outcome"], run_state.RUNNING)

    def test_update_preserves_unknown_keys(self) -> None:
        """The extension point: a later capability (the appetite breaker) adds its own
        fields, and nothing here may drop them."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            run_state.open_run(root, batch=["US0001"])
            run_state.update(root, appetite_batches=3, spend={"batches": 1})
            st = run_state.read(root)
            self.assertEqual(st["appetite_batches"], 3)
            self.assertEqual(st["spend"], {"batches": 1})
            run_state.close_run(root, outcome=run_state.BUDGET_SPENT, handoff="HO-0001")
            st = run_state.read(root)
            self.assertEqual(st["appetite_batches"], 3)   # survives the close
            self.assertEqual(st["outcome"], run_state.BUDGET_SPENT)
            self.assertEqual(st["handoff"], "HO-0001")
            self.assertTrue(st["ended_at"])

    def test_an_unknown_outcome_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                run_state.close_run(Path(t), outcome="finished-ish")

    def test_absent_state_reads_empty_never_fabricated(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(run_state.read(Path(t)), {})
            self.assertFalse(run_state.is_open(Path(t)))


# --------------------------------------------------------------------------- the join
class BuildTests(unittest.TestCase):
    def test_every_remaining_item_carries_a_pointer_and_a_suitability_tag(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done")
            _story(root, 2, status="In Progress")
            _cr(root, 3, status="Proposed")
            r = handoff.build(root, batch=["US0001", "US0002", "CR0003"])
            self.assertEqual([d["id"] for d in r["delivered"]], ["US0001"])
            self.assertEqual(sorted(x["id"] for x in r["remaining"]), ["CR0003", "US0002"])
            for item in r["remaining"]:
                self.assertTrue(item["pointers"], f"{item['id']} has no pointer")
                self.assertIn(item["suitability"]["tag"], handoff.TAGS)
                self.assertTrue(item["suitability"]["reasons"], item["id"])

    def test_a_unit_dropped_by_a_mid_run_replan_still_appears(self) -> None:
        """F1, end to end: the run approved three, a re-plan narrowed the batch to one, and
        the loop never touched the other two. They are open, incomplete and were APPROVED -
        they must be in the handover and in the worklist, not in no bucket at all."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for n in (1, 2, 3):
                _story(root, n, status="In Progress")
            run_state.open_run(root, batch=["US0001", "US0002", "US0003"], goal="done")
            run_state.open_run(root, batch=["US0001"], goal="done")     # the narrowing re-cut
            r = handoff.build(root)
            self.assertEqual(sorted(x["id"] for x in r["remaining"]),
                             ["US0001", "US0002", "US0003"])

    def test_a_terminal_unit_whose_acs_are_RED_is_not_delivered(self) -> None:
        """F2: a story that went Done green and later regressed still carries `Status: Done`.
        Printing it under Delivered - and dropping its failing verifier from the document and
        the worklist - reports a success the run does not have. It is remaining work."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 2, status="Done", acs=2)
            _verify_report(root, {"US0002-story-2": {
                "ac_count": 2, "verified": 0, "failed": 2, "stale": 0, "manual": 0,
                "failures": [{"ac": "AC1", "verifier": "pytest tests/a.py", "kind": "failed"},
                             {"ac": "AC2", "verifier": "pytest tests/b.py", "kind": "failed"}]}})
            r = handoff.build(root, batch=["US0002"])
            self.assertEqual(r["delivered"], [])
            self.assertEqual(r["dropped"], [])
            self.assertEqual([x["id"] for x in r["remaining"]], ["US0002"])
            item = r["remaining"][0]
            self.assertIn("verify:unproven", [p["ref"] for p in item["pointers"]])
            self.assertIn("pytest tests/b.py", json.dumps(item["pointers"]))

    def test_a_terminal_unit_with_STALE_acs_is_not_delivered_and_never_reads_green(self) -> None:
        """F2: `stale` was a pointer for remaining units and IGNORED in delivery evidence, so
        a Done story with 2 stale ACs read "2/2 AC(s) verified" - verified against code that
        has since changed."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done", acs=2)
            _verify_report(root, {"US0001-story-1": {
                "ac_count": 2, "verified": 2, "failed": 0, "stale": 2, "manual": 0,
                "failures": []}})
            r = handoff.build(root, batch=["US0001"])
            self.assertEqual(r["delivered"], [])
            self.assertEqual([x["id"] for x in r["remaining"]], ["US0001"])

    def test_superseded_is_closed_without_delivery_not_delivered(self) -> None:
        """F2: `Superseded` sat in the delivered set because `audit.MET` is a
        DEPENDENCY-SATISFACTION set, not a DELIVERY set. Same vocabulary, same terminal set
        and the same sentence as Won't Implement: the run did not deliver it."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 7, status="Superseded")
            r = handoff.build(root, batch=["US0007"])
            self.assertEqual(r["delivered"], [])
            self.assertEqual([x["id"] for x in r["dropped"]], ["US0007"])

    def test_a_genuinely_green_terminal_unit_is_still_delivered(self) -> None:
        # the fix must not swing the other way: a Done story whose ACs pass IS delivered
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done", acs=2)
            _verify_report(root, {"US0001-story-1": {
                "ac_count": 2, "verified": 2, "failed": 0, "stale": 0, "manual": 0,
                "failures": []}})
            r = handoff.build(root, batch=["US0001"])
            self.assertEqual([x["id"] for x in r["delivered"]], ["US0001"])
            self.assertEqual(r["remaining"], [])

    def test_the_three_buckets_partition_the_joined_set(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done")               # delivered (no report: no red)
            _story(root, 5, status="Won't Implement")    # dropped
            _story(root, 7, status="Superseded")         # dropped
            _story(root, 2, status="In Progress")        # remaining
            r = handoff.build(root, batch=["US0001", "US0005", "US0007", "US0002", "US0404"])
            got = [u["id"] for u in r["delivered"] + r["dropped"] + r["remaining"]]
            self.assertCountEqual(got, ["US0001", "US0005", "US0007", "US0002", "US0404"])
            self.assertEqual(len(got), len(set(got)), "a unit landed in two buckets")
            self.assertEqual(r["summary"]["total"], 5)

    def test_a_dropped_unit_is_terminal_but_never_reported_as_delivered(self) -> None:
        """Terminal is not delivered. A unit closed Won't Implement is finished - it is not
        remaining work - but printing it under Delivered would report a success the run
        never achieved (LL0008)."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done")
            _story(root, 2, status="Won't Implement")
            r = handoff.build(root, batch=["US0001", "US0002"])
            self.assertEqual([u["id"] for u in r["delivered"]], ["US0001"])
            self.assertEqual([u["id"] for u in r["dropped"]], ["US0002"])
            self.assertEqual(r["remaining"], [])
            self.assertEqual(r["summary"]["delivered"], 1)
            self.assertEqual(r["summary"]["dropped"], 1)

    def test_a_failed_attempt_under_the_cap_still_shows_its_signature(self) -> None:
        """The guardrail thresholds are CLI flags. A unit that failed once has a signature
        the next person needs; withholding it until a threshold trips loses the pointer they
        came for - while the tag stays copilot-tail, because one red is a tail."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            src = root / "src"
            src.mkdir()
            (src / "small.py").write_text("def f(a):\n    return a + 1\n", encoding="utf-8")
            _story(root, 2, status="In Progress", acs=1, affects="`src/small.py`")
            _loop_state(root, {"US0002": {"attempts": 1, "signatures": ["test_a::x"]}})
            item = next(x for x in handoff.build(root, batch=["US0002"])["remaining"]
                        if x["id"] == "US0002")
            blocker = next(p for p in item["pointers"] if p["kind"] == "blocker")
            self.assertEqual(blocker["ref"], "failed-attempts")
            self.assertIn("test_a::x", blocker["detail"])
            self.assertEqual(item["suitability"]["tag"], handoff.COPILOT_TAIL)

    def test_a_batch_id_with_no_file_is_still_listed(self) -> None:
        """The omission class: a unit the run cannot find is remaining work, not absent
        work. Silently dropping it is the failure LL0008 names."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done")
            r = handoff.build(root, batch=["US0001", "US0404"])
            ids = [x["id"] for x in r["remaining"]]
            self.assertIn("US0404", ids)
            item = next(x for x in r["remaining"] if x["id"] == "US0404")
            self.assertEqual(item["status"], "missing")
            self.assertTrue(item["pointers"])
            self.assertEqual(item["suitability"]["tag"], handoff.JUDGEMENT)

    def test_a_quarantined_unit_outside_the_batch_is_still_listed(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done")
            _story(root, 9, status="Blocked")
            _loop_state(root, {"US0009": {"attempts": 3,
                                          "signatures": ["test_a::x", "test_a::x", "test_b::y"]}})
            r = handoff.build(root, batch=["US0001"])
            self.assertIn("US0009", [x["id"] for x in r["remaining"]])
            item = next(x for x in r["remaining"] if x["id"] == "US0009")
            sigs = [p for p in item["pointers"] if p["kind"] == "blocker"]
            self.assertTrue(sigs)
            self.assertIn("test_a::x", sigs[0]["detail"])

    def test_a_failing_ac_becomes_an_ac_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 2, status="In Progress", acs=2)
            _verify_report(root, {"US0002-story-2": {
                "ac_count": 2, "verified": 1, "failed": 1, "stale": 0, "manual": 0,
                "failures": [{"ac": "AC2", "verifier": "pytest tests/test_x.py",
                              "kind": "failed"}]}})
            r = handoff.build(root, batch=["US0002"])
            item = next(x for x in r["remaining"] if x["id"] == "US0002")
            acs = [p for p in item["pointers"] if p["kind"] == "ac"]
            self.assertTrue(acs)
            self.assertEqual(acs[0]["ref"], "AC2")
            self.assertIn("pytest", acs[0]["detail"])

    def test_a_repeated_failure_signature_tags_judgement_not_copilot_tail(self) -> None:
        """The same failure recurring is the approach being wrong, not typing left to do."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 2, status="In Progress")
            _loop_state(root, {"US0002": {"attempts": 2,
                                          "signatures": ["test_a::x", "test_a::x"]}})
            item = next(x for x in handoff.build(root, batch=["US0002"])["remaining"]
                        if x["id"] == "US0002")
            self.assertEqual(item["suitability"]["tag"], handoff.JUDGEMENT)
            self.assertIn("quarantine:repeat", item["suitability"]["reasons"])

    def test_a_small_well_specified_unit_tags_copilot_tail(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            src = root / "src"
            src.mkdir()
            (src / "small.py").write_text("def f(a):\n    return a + 1\n", encoding="utf-8")
            _story(root, 2, status="In Progress", acs=1, affects="`src/small.py`")
            item = next(x for x in handoff.build(root, batch=["US0002"])["remaining"]
                        if x["id"] == "US0002")
            self.assertEqual(item["suitability"]["tag"], handoff.COPILOT_TAIL)

    def test_no_batch_source_is_refused_not_reported_empty(self) -> None:
        """Nothing to hand over is not a handoff: an empty batch would render a document
        claiming a clean close it never checked."""
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                handoff.build(Path(t))

    def test_the_batch_falls_back_to_the_run_state_then_the_sprint_plan(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 2, status="In Progress")
            plan = root / "sdlc-studio" / ".local" / "sprint-plan.json"
            plan.parent.mkdir(parents=True, exist_ok=True)
            plan.write_text(json.dumps({"batch": [{"id": "US0002"}]}), encoding="utf-8")
            self.assertEqual([x["id"] for x in handoff.build(root)["remaining"]], ["US0002"])
            self.assertEqual(handoff.build(root)["batch_source"], "sprint-plan.json")
            run_state.open_run(root, batch=["US0002"], goal="done")
            r = handoff.build(root)
            self.assertEqual(r["batch_source"], "run-state.json")
            self.assertEqual(r["run"]["goal"], "done")


# --------------------------------------------------------------------------- generate


# --------------------------------------------------------------------------- AC2: read back


# --------------------------------------------------------------------------- the gate lane


# --------------------------------------------------------------------------- registration
class RegistrationTests(unittest.TestCase):
    """`handoff` is a META artefact - outside the status machinery - so the HO files already
    written resolve and reconcile wherever the other meta types do, and nowhere the pipeline
    types are (no status vocab, no validator walk). No command creates one (US0978), so it is
    not among `artifact.py new`'s types."""

    def test_handoff_is_a_meta_type_not_a_pipeline_type(self) -> None:
        self.assertNotIn("handoff", artifact.META, "a handoff is creatable again (US0978)")
        self.assertIn("handoff", next_id.META_TYPES)
        self.assertNotIn("handoff", sdlc_md.ARTIFACT_TYPES)
        self.assertNotIn("handoff", artifact.SPEC)

    def test_transition_refuses_a_handoff_id_as_a_meta_artefact(self) -> None:
        """F6: the meta guard listed RETRO|RV and not HO, so transitioning a handoff said
        "no artifact found" - false, it exists - instead of the designed refusal. Registering
        a type in some of the places and not the others is the half-registration class."""
        transition = _load("transition")
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _old_handoff(root)
            with self.assertRaises(ValueError) as ctx:
                transition.transition(root, "HO0001", "Done")
            self.assertIn("meta-artifact", str(ctx.exception))
            self.assertNotIn("no artifact found", str(ctx.exception))

    def test_reconcile_covers_the_handoff_index(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _old_handoff(root)
            self.assertEqual(reconcile.meta_index_drift(root), [])
            # an un-indexed handoff file is drift the meta lane reports, like a retro's
            (root / "sdlc-studio" / "handoffs" / "HO0009-hand.md").write_text(
                "# HO-0009: hand\n\n> **Date:** 2026-07-13\n", encoding="utf-8")
            drift = reconcile.meta_index_drift(root)
            self.assertEqual([d["id"] for d in drift], ["HO-0009"])
            self.assertEqual(drift[0]["kind"], "missing-row")


class ClassifyUnreadableTests(unittest.TestCase):
    """BG0646: `_classify` reads a unit through `read_text_safe`, so the dashboard's
    `remaining_count` classifies an unreadable batch file as Unknown and REMAINING - recorded in
    the degradation log - rather than raising out of the run line. `build` still raises on the
    same file from `_open_decisions`, its own `Path.read_text`, as at the base ref: the change
    reaches the count and not the join. MUTANT: read the file in `_classify` with
    `Path.read_text` again, so `remaining_count` raises PermissionError."""

    def test_an_unreadable_batch_file_counts_as_remaining_in_the_run_line(self) -> None:
        import os  # noqa: PLC0415
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root reads every file; the permission bit cannot make one unreadable")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
            p = root / "sdlc-studio" / "stories" / "US0001-a.md"
            p.write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            p.chmod(0)
            try:
                self.assertEqual(1, handoff.remaining_count(root, ["US0001"]))
                c = handoff._classify(root, "US0001", {})
                self.assertEqual(("Unknown", False), (c["status"], c["terminal"]))
                with self.assertRaises(PermissionError):   # the join's own reader, unchanged
                    handoff.build(root, batch=["US0001"])
            finally:
                p.chmod(0o644)


class HandoffKeysResolveInBothSchemasTests(unittest.TestCase):
    """BG0465 AC2, restored by US0978's round 1 against the reader that survives the writer.

    The HO files already written stay readable: an old handoff is located by id through
    `sdlc_md.find_by_id`, whose meta resolver reads the stem with `stem_record_id`
    (`_STEM_ID_RE`). `stem.split("-")[0]` yields the bare prefix `HO` for a v3 key
    `HO-<ulid>-slug`, and `extract_record_id` answers only `ARTIFACT_TYPES`, so both key schemas
    are located here, through the production lookup."""

    def test_an_old_handoff_resolves_under_both_key_schemas(self) -> None:
        """MUTANT: drop the `_V3_SUFFIX` alternative from `_STEM_ID_RE` - the v3 key no longer
        resolves, so an old v3 handoff reads as missing."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            d = root / "sdlc-studio" / "handoffs"
            v3 = "HO-01JQZ0000000000000000000"
            (d / f"{v3}-a-run.md").write_text(f"# {v3}: a run\n\n> **Date:** 2026-07-13\n",
                                              encoding="utf-8")
            (d / "HO0001-close.md").write_text("# HO-0001: close\n\n> **Date:** 2026-07-13\n",
                                               encoding="utf-8")
            for rid, stem in ((v3, f"{v3}-a-run"), ("HO0001", "HO0001-close")):
                with self.subTest(key=rid):
                    hit = sdlc_md.find_by_id(root, rid)
                    self.assertIsNotNone(hit, f"{rid} did not resolve")
                    self.assertEqual((stem, "handoff"), (Path(hit[0]).stem, hit[1]))


class WorklistTests(unittest.TestCase):
    def test_sprint_plan_refuses_cleanly_on_an_unreadable_run_state(self) -> None:
        """F4, at the other writer: `plan --write` would overwrite the wreckage with a blank
        record. It stops instead - loudly, and without a traceback. MUTANT: replace `cmd_plan`'s
        `return 2` on `RunStateError` - the plan proceeds over an unreadable run state."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            # A GROOMED unit, so no later gate refuses the plan first: the run-state guard is
            # the only thing between this `--write` and the wreckage being overwritten.
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0002-s.md").write_text(
                "# US0002: s\n\n> **Status:** Ready\n> **Epic:** EP0001\n> **Points:** 2\n"
                "> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n### AC1: works\n\n"
                "- **Verify:** shell true\n", encoding="utf-8")
            run_state.open_run(root, batch=["US0002"], goal="done")
            p = run_state.path(root)
            p.write_text(p.read_text(encoding="utf-8")[:40], encoding="utf-8")
            err = io.StringIO()
            args = sprint.build_parser().parse_args(
                ["plan", "--stories", "Ready", "--write", "--no-fetch", "--skip-personas",
                 "--root", str(root)])
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = sprint.cmd_plan(args)
            self.assertEqual(rc, 2)
            self.assertIn("not valid JSON", err.getvalue())
            self.assertEqual(len(p.read_text(encoding="utf-8")), 40)  # not overwritten


class DocumentBulletFollowsTheDocumentTests(unittest.TestCase):
    """BG0590 AC3 and AC5-AC10, restored by US0978's round 1 against the code that survives the
    retired retro link: `sdlc_md.document_bullet`, which reads the unordered-list marker a
    document already uses (MD004 `consistent` takes the FIRST), and `artifact._wire_story_to_epic`,
    the epic appender that writes with it. A hardcoded marker makes the next commit uncommittable
    wherever the document disagrees."""

    def test_the_sibling_appender_follows_the_document(self) -> None:
        """AC3. MUTANT: hardcode `- [ ] ` in `artifact._wire_story_to_epic`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            ep = ed / "EP0001-e.md"
            ep.write_text("# EP0001: e\n\n> **Status:** Draft\n\n## Story Breakdown\n\n"
                          "* [ ] [US0009: prior](../stories/US0009-p.md)\n", encoding="utf-8")
            self.assertTrue(
                artifact._wire_story_to_epic(root, "EP0001", "US0001", "t", "US0001", "t"))
            text = ep.read_text(encoding="utf-8")
            self.assertIn("* [ ] [US0001: t]", text)
            self.assertNotIn("- [ ] [US0001", text)

    def _bullet(self, body: str) -> str:
        return sdlc_md.document_bullet("# RETRO0001: t\n\n> **Status:** Draft\n\n" + body)

    def test_a_bullet_inside_fenced_code_is_not_the_documents_style(self) -> None:
        """AC5. MUTANTS: drop the fence skip; return the default - a fenced dash is not a list."""
        self.assertEqual("*", self._bullet("## Evidence\n\n```text\n- a quoted transcript line\n"
                                           "- another\n```\n\n## What went well\n\n"
                                           "* the real list\n"))

    def test_a_blockquoted_list_sets_the_documents_style(self) -> None:
        """AC6. MUTANT: drop the blockquote strip - a quoted list IS a list to markdownlint."""
        self.assertEqual("*", self._bullet("## Verdict\n\n> * the first finding\n> * the second\n"))

    def test_the_first_marker_wins_not_the_last(self) -> None:
        """AC7. MUTANT: return the LAST matching marker rather than the first."""
        self.assertEqual("*", self._bullet("## Mixed\n\n* the first marker in the file\n\n"
                                           "- a later, different one\n"))

    def test_a_plus_bulleted_document_is_followed_too(self) -> None:
        """AC8. MUTANT: drop `+` from the marker class."""
        self.assertEqual("+", self._bullet("## Notes\n\n+ a plus bullet\n"))

    def test_a_spaced_thematic_break_is_not_a_list_marker(self) -> None:
        """AC9. MUTANT: drop the thematic-break guard - the break comes first, so a guard that is
        never reached would read `*` from it."""
        self.assertEqual("-", self._bullet("## Notes\n\n* * *\n\n- a dash bullet\n"))

    def test_a_bullet_indented_as_code_does_not_set_the_style(self) -> None:
        """AC10. MUTANT: relax the leading-space bound from `^ {0,3}` to `^ *`."""
        self.assertEqual("-", self._bullet("## Sample\n\n    * a bullet inside an indented "
                                           "code block\n\n## Notes\n\n- the real list\n"))


if __name__ == "__main__":
    unittest.main()
