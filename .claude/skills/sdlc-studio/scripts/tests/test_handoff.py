"""Unit tests for handoff.py + lib/run_state.py (RED first - neither exists yet).

The class these lock: a run that stops short of its goal must hand a human a single
document naming EVERY remaining item, each with a pointer (file / AC / check) and a
suitability tag, and the next sprint must be able to read it back as a batch. A handoff
that silently omits a remaining item is worse than no handoff (LL0008), so the omission
cases are the load-bearing tests here: a batch id with no file on disk, and a quarantined
unit that was never in the approved batch, both still appear.
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
gate = _load("gate")
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


def _retro(root: Path, num: int = 21) -> Path:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"RETRO{num:04d}-a-sprint.md"
    p.write_text(f"# RETRO-{num:04d}: a sprint\n\n> **Date:** 2026-07-13\n\n"
                 f"## Delivered\n\n- US0001\n\n## Lessons\n\n- something\n", encoding="utf-8")
    return p


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
            gen = handoff.generate(root, title="c", batch=["US0002"], outcome=run_state.BLOCKED)
            self.assertIn("US0002", Path(gen["worklist"]).read_text(encoding="utf-8"))

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
            self.assertNotIn("2/2 AC(s) verified", handoff.render_body(r))

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
            body = handoff.render_body(r)
            self.assertIn("## Closed without delivery (1)", body)
            self.assertNotIn("US0002", body.split("## Closed without delivery")[0])

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
class GenerateTests(unittest.TestCase):
    def test_generate_is_tool_created_indexed_and_leaves_no_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 1, status="Done")
            _story(root, 2, status="In Progress")
            r = handoff.generate(root, title="run close", batch=["US0001", "US0002"],
                                 outcome=run_state.BLOCKED)
            self.assertEqual(r["id"], "HO-0001")
            self.assertTrue(r["indexed"])
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertNotIn("{{", text)          # L-0005: no leaked placeholder
            self.assertIn("US0002", text)         # the remaining unit
            self.assertIn("US0001", text)         # ...and the delivered one, with evidence
            self.assertIn("HO-0001", text)
            self.assertTrue(any(tag in text for tag in handoff.TAGS), "no suitability tag")
            index = (root / "sdlc-studio" / "handoffs" / "_index.md").read_text(encoding="utf-8")
            self.assertIn("[HO-0001](HO0001", index)   # the row is tool-appended

    def test_generate_title_from_a_goal_sentence_yields_an_h1_without_trailing_punctuation(self) -> None:
        # BG0179: the Sprint Goal sentence ends in a full stop; the H1 built from it must not,
        # or markdownlint MD026 blocks the close commit in the generator's own repo.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            r = handoff.generate(root, title="Close the run and prove every gate ran.",
                                 batch=["US0002"], outcome=run_state.BLOCKED)
            h1 = Path(r["path"]).read_text(encoding="utf-8").splitlines()[0]
            self.assertTrue(h1.startswith("# HO-0001:"))
            self.assertFalse(h1.rstrip()[-1] in ".,;:!?…",
                             f"H1 ends in punctuation (MD026): {h1!r}")

    def test_generate_bootstraps_a_missing_index_rather_than_minting_drift(self) -> None:
        """A project's FIRST handoff must not land as reconcile drift the operator then
        clears by hand: the index is created from the shipped template, and the row lands."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 2, status="In Progress")          # no handoffs/_index.md at all
            r = handoff.generate(root, title="first", batch=["US0002"],
                                 outcome=run_state.BLOCKED)
            idx = root / "sdlc-studio" / "handoffs" / "_index.md"
            self.assertTrue(idx.exists())
            self.assertNotIn("{{", idx.read_text(encoding="utf-8"))
            self.assertTrue(r["indexed"])
            self.assertEqual(reconcile.meta_index_drift(root), [])

    def test_generate_closes_the_run_with_its_outcome_and_handoff_id(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            run_state.open_run(root, batch=["US0002"], goal="done")
            r = handoff.generate(root, title="stopped short",
                                 outcome=run_state.BUDGET_SPENT)
            st = run_state.read(root)
            self.assertEqual(st["outcome"], run_state.BUDGET_SPENT)
            self.assertEqual(st["handoff"], r["id"])
            self.assertTrue(st["ended_at"])

    def test_generate_links_the_handoff_from_the_retro(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            retro = _retro(root, 21)
            _story(root, 2, status="In Progress")
            r = handoff.generate(root, title="close", batch=["US0002"],
                                 outcome=run_state.BLOCKED, retro="RETRO0021")
            self.assertTrue(r["retro_linked"])
            text = retro.read_text(encoding="utf-8")
            self.assertIn("## Handoff", text)
            self.assertIn(r["id"], text)

    def test_linking_a_retro_that_does_not_exist_is_refused_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            with self.assertRaises(ValueError):
                handoff.generate(root, title="close", batch=["US0002"],
                                 outcome=run_state.BLOCKED, retro="RETRO9999")
            self.assertEqual(list((root / "sdlc-studio" / "handoffs").glob("HO*.md")), [])

    def test_the_retro_link_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            retro = _retro(root, 21)
            _story(root, 2, status="In Progress")
            handoff.generate(root, title="a", batch=["US0002"], outcome=run_state.BLOCKED,
                             retro="RETRO0021")
            handoff.generate(root, title="b", batch=["US0002"], outcome=run_state.BLOCKED,
                             retro="RETRO0021")
            self.assertEqual(retro.read_text(encoding="utf-8").count("## Handoff"), 1)


# --------------------------------------------------------------------------- AC2: read back
class WorklistTests(unittest.TestCase):
    def test_generate_emits_a_worklist_the_next_sprint_plan_reads(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 1, status="Done")
            _story(root, 2, status="In Progress")
            _cr(root, 3, status="Proposed")
            r = handoff.generate(root, title="close", batch=["US0001", "US0002", "CR0003"],
                                 outcome=run_state.BUDGET_SPENT)
            wl = Path(r["worklist"])
            self.assertTrue(wl.exists())
            plan = sprint.build_plan(root, worklist=str(wl), order="priority")
            self.assertEqual(sorted(u["id"] for u in plan["batch"]), ["CR0003", "US0002"])

    def test_a_missing_unit_is_not_planned_but_is_never_silently_dropped(self) -> None:
        """`sprint plan --worklist` refuses an id with no file on disk, so an unresolvable
        id must not be a plannable LINE - it would abort the next plan. It is still named,
        as a comment in the worklist and as an item in the handoff: unplannable is a fact
        to report, not an item to lose."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            r = handoff.generate(root, title="close", batch=["US0002", "US0404"],
                                 outcome=run_state.BLOCKED)
            wl = Path(r["worklist"]).read_text(encoding="utf-8")
            plannable = [ln.strip() for ln in wl.splitlines()
                         if ln.strip() and not ln.strip().startswith("#")]
            self.assertEqual(plannable, ["US0002"])
            self.assertIn("US0404", wl)                       # named, as a comment
            self.assertIn("US0404", Path(r["path"]).read_text(encoding="utf-8"))
            plan = sprint.build_plan(root, worklist=r["worklist"], order="priority")
            self.assertEqual([u["id"] for u in plan["batch"]], ["US0002"])

    def test_sprint_plan_refuses_cleanly_on_an_unreadable_run_state(self) -> None:
        """F4, at the other writer: `plan --write` would overwrite the wreckage with a blank
        record. It stops instead - loudly, and without a traceback."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 2, status="Ready")
            run_state.open_run(root, batch=["US0002"], goal="done")
            p = run_state.path(root)
            p.write_text(p.read_text(encoding="utf-8")[:40], encoding="utf-8")
            err = io.StringIO()
            args = sprint.build_parser().parse_args(
                ["plan", "--stories", "Ready", "--write", "--root", str(root)])
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = sprint.cmd_plan(args)
            self.assertEqual(rc, 2)
            self.assertIn("not valid JSON", err.getvalue())
            self.assertEqual(len(p.read_text(encoding="utf-8")), 40)  # not overwritten

    def test_sprint_plan_surfaces_the_open_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            handoff.generate(root, title="close", batch=["US0002"], outcome=run_state.BLOCKED)
            pending = sprint.pending_handoff(root)
            self.assertIsNotNone(pending)
            self.assertEqual(pending["id"], "HO-0001")
            self.assertEqual(pending["remaining"], 1)
            self.assertTrue(Path(pending["worklist"]).exists())


# --------------------------------------------------------------------------- the gate lane
class GateLaneTests(unittest.TestCase):
    def _project(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)

    def test_require_handoff_fails_when_the_handoff_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._project(root)
            r = gate.run_gate(str(root), checks={}, require_handoff="HO0001")
            self.assertFalse(r["ok"])
            lane = next(c for c in r["checks"] if c["check"] == "handoff")
            self.assertEqual(lane["status"], "fail")

    def test_require_handoff_fails_when_no_retro_links_it(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._project(root)
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            handoff.generate(root, title="close", batch=["US0002"], outcome=run_state.BLOCKED)
            r = gate.run_gate(str(root), checks={}, require_handoff="HO0001")
            self.assertFalse(r["ok"])
            lane = next(c for c in r["checks"] if c["check"] == "handoff")
            self.assertIn("no retro links", lane["detail"])

    def test_require_handoff_passes_when_present_and_linked(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._project(root)
            _handoff_index(root)
            _retro(root, 21)
            _story(root, 2, status="In Progress")
            handoff.generate(root, title="close", batch=["US0002"],
                             outcome=run_state.BLOCKED, retro="RETRO0021")
            r = gate.run_gate(str(root), checks={}, require_handoff="HO-0001")
            self.assertTrue(r["ok"], r["checks"])

    def test_deselecting_the_bound_handoff_lane_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._project(root)
            r = gate.run_gate(str(root), checks={"a": lambda _r: {"count": 0, "blocking": True,
                                                                  "detail": ""}},
                              require_handoff="HO0001", skip=["handoff"])
            self.assertFalse(r["ok"])
            self.assertEqual(r["checks"][0]["check"], "selection")
            self.assertIn("handoff", r["checks"][0]["detail"])

    def test_a_bare_mention_of_the_id_does_not_satisfy_the_link_check(self) -> None:
        """F5: the lane was a substring scan, so a retro whose prose DENIES the handoff
        exists ("we never wrote HO-0001") passed it. The link is a markdown link to the
        handoff file - that is the shape the writer emits, and the shape a reader can
        follow, so that is the shape the gate checks."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._project(root)
            _handoff_index(root)
            retro = _retro(root, 21)
            _story(root, 2, status="In Progress")
            handoff.generate(root, title="close", batch=["US0002"], outcome=run_state.BLOCKED)
            with retro.open("a", encoding="utf-8") as fh:
                fh.write("\nThe run stopped early; we never wrote HO-0001.\n")
            r = gate.run_gate(str(root), checks={}, require_handoff="HO0001")
            self.assertFalse(r["ok"], "a prose mention passed as a link")
            lane = next(c for c in r["checks"] if c["check"] == "handoff")
            self.assertIn("no retro links", lane["detail"])

    def test_the_handoff_lane_blocks_on_error(self) -> None:
        self.assertIn("handoff", gate.BLOCKING_ON_ERROR)

    def test_the_handoff_lane_is_absent_from_the_standard_gate(self) -> None:
        self.assertNotIn("handoff", gate.DEFAULT_CHECKS)


# --------------------------------------------------------------------------- registration
class RegistrationTests(unittest.TestCase):
    """`handoff` is a META artefact - tool-created, outside the status machinery - so it
    must be registered everywhere the other meta types are, and nowhere the pipeline types
    are (no status vocab, no validator walk)."""

    def test_handoff_is_a_meta_type_not_a_pipeline_type(self) -> None:
        self.assertIn("handoff", artifact.META)
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
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            handoff.generate(root, title="close", batch=["US0002"], outcome=run_state.BLOCKED)
            with self.assertRaises(ValueError) as ctx:
                transition.transition(root, "HO0001", "Done")
            self.assertIn("meta-artifact", str(ctx.exception))
            self.assertNotIn("no artifact found", str(ctx.exception))

    def test_reconcile_covers_the_handoff_index(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _handoff_index(root)
            _story(root, 2, status="In Progress")
            handoff.generate(root, title="close", batch=["US0002"], outcome=run_state.BLOCKED)
            self.assertEqual(reconcile.meta_index_drift(root), [])
            # an un-indexed handoff file is drift the meta lane reports, like a retro's
            (root / "sdlc-studio" / "handoffs" / "HO0009-hand.md").write_text(
                "# HO-0009: hand\n\n> **Date:** 2026-07-13\n", encoding="utf-8")
            drift = reconcile.meta_index_drift(root)
            self.assertEqual([d["id"] for d in drift], ["HO-0009"])
            self.assertEqual(drift[0]["kind"], "missing-row")


if __name__ == "__main__":
    unittest.main()
