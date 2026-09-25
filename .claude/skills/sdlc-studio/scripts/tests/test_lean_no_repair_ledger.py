"""US0914: a standing REJECT clears only by a round-2 APPROVE or by carrying the unit.

The repair ledger (`critic.py repair`, `repair-record.md`) is deleted from every reader. A REJECT
has two exits: a round-2 APPROVE from the reviewer who rejected, or a round-2 REJECT at the cap,
which files the findings as a bug and drops the unit from the open run's batch. The brief
fingerprint answers a REJECT only between rows recorded before the same-reviewer round rule.
History keeps its answer: a Done story whose REJECT is dated before `critic.REPAIR_VERB_RETIRED`
stays critiqued in the conformance census, on the REJECT's own date, and nowhere else.

AC1, AC2, AC3 and AC7 run in throwaway workspaces through the shipped entry points. AC4 reads a
fixture and, in the dev repo, this repository's ledger. AC5 and AC6 read this repository's
generated surface and stamped criteria, because their criteria are about them.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run
import workspace  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

REPO = workspace.REPO
UNIT = "US0001"
FIRST, SECOND = "the parser drops a trailing row", "the refusal names no remedy"
FINDINGS = f"[new] {FIRST}; [new] {SECOND}"

#: The test nodes this story deletes: a class, or one method of a class that survives.
DELETED = {
    "test_critic.py": ("RepairRecordTests", "ClosureResolutionTests", "ClosureArrowTests",
                       "PartialRepairTests", "FiledDispositionTests", "RepairPlacementTests",
                       "RepairPhaseJoinTests", "RepairStateResolvesFiledIdsTests",
                       # the two classes that also pin surviving behaviour lose only these
                       "ClosureChannelTests::test_evidence_carrying_a_semicolon_is_stored_whole",
                       "ClosureChannelTests::test_ordinary_evidence_still_parses_unchanged",
                       "ClosureChannelTests::test_an_unparseable_chunk_is_refused_rather_than_"
                       "dropped",
                       "ClosureChannelTests::test_a_value_ending_in_a_backslash_does_not_swallow_"
                       "the_next_item",
                       "ClosureChannelTests::test_an_unreadable_row_is_reported_when_read",
                       "ClosureChannelTests::test_a_json_closure_document_needs_no_separator_at_"
                       "all",
                       "LedgerRollupTests::test_every_unanswered_rejection_contributes_its_"
                       "findings",
                       "LedgerRollupTests::test_a_repair_recorded_across_two_calls_reads_complete",
                       "LedgerRollupTests::test_a_genuinely_partial_repair_still_reads_partial",
                       "ThreeStateCoverageTests::test_approved_repaired_and_unreviewed_are_three_"
                       "distinct_states",
                       "ThreeStateCoverageTests::test_the_gates_treatment_of_a_repaired_unit_is_"
                       "declared_and_tested_both_ways",
                       "CleanSpanWidthAndRefusalTests::test_a_refused_repair_leaves_no_row_behind"),
    "test_conformance.py": ("ThreeStateCoverageTests",),
    "test_sprint.py": (
        "PreflightCoverageCountsTests::test_the_shipped_preflight_stops_calling_a_repaired_unit_"
        "uncovered",
        "PreflightCoverageCountsTests::test_a_partly_repaired_unit_is_still_uncovered_in_the_"
        "preflight"),
    "test_transition.py": (
        "RejectNeedsAnAnswerTests::test_a_filed_artefact_id_discharges_the_reject",
        "RejectNeedsAnAnswerTests::test_an_id_naming_no_artefact_is_refused",
        "RejectNeedsAnAnswerTests::test_a_complete_repair_answers_the_reject_as_review_"
        "coverage_does",
        "RejectNeedsAnAnswerTests::test_a_partly_filed_reject_is_refused",
        "ClosedOverRejectNamesTheBugTests::test_the_story_names_every_filed_artefact",
        "ClosedOverRejectNamesTheBugTests::test_the_one_call_close_names_the_filed_artefacts",
        "ClosedOverRejectNamesTheBugTests::test_a_bug_names_the_filed_artefact_at_every_"
        "delivered_terminal",
        "ClosedOverRejectNamesTheBugTests::test_a_terminal_walk_writes_the_line_once"),
}
#: The classes whose criteria survive, edited rather than deleted. ClosureChannelTests and
#: LedgerRollupTests also pin the verdict channel, the seat roll-up, the ledger annotation and
#: the brief's restore obligation, none of which the repair ledger owns.
KEPT = {"test_transition.py": ("RejectNeedsAnAnswerTests", "ClosedOverRejectNamesTheBugTests"),
        "test_critic.py": ("ClosureChannelTests", "LedgerRollupTests")}

#: The criteria retired, by artefact, and how many each carried, in the D0259 pattern.
RETIRED = {"BG0605": 2, "BG0607": 2, "BG0618": 6, "BG0629": 2, "BG0631": 4, "BG0637": 1,
           "BG0677": 7, "BG0704": 3, "US0620": 4, "US0621": 3, "US0622": 3, "US0623": 3,
           "US0624": 1, "US0627": 6, "US0628": 4}
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0914: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0914\b")

#: A repair ledger as `critic.py repair` wrote it: both findings of the REJECT dated `when`
#: closed `fixed:`. At the base ref these rows answer the REJECT.
_LEDGER_HEAD = (
    "# Repair Records\n\n"
    "| Unit | Verdict date | Author | Date | Closed | Outstanding | Phase | Rejection |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |\n")


def _ledger(root: Path, unit: str, when: str, brief: str = "-") -> Path:
    path = root / "sdlc-studio" / "reviews" / "repair-record.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _LEDGER_HEAD + f"| {unit} | {when} | builder | {when} | {FIRST} -> fixed: a test pins "
        f"it; {SECOND} -> fixed: the refusal names one | - | delivery | {brief} |\n",
        encoding="utf-8")
    return path


def _env() -> dict:
    return dict(os.environ, **{run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts-for-tests"})


def _run(root: Path, script: str, *argv: str, root_first: bool = False) -> tuple[int, str]:
    """The script through its shipped entry point. `root_first` for a parser whose `--root` is
    a top-level argument only (`sprint_report.py`)."""
    where = ["--root", str(root)]
    cmd = [*where, *argv] if root_first else [*argv, *where]
    p = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *cmd],
                       capture_output=True, text=True, check=False, env=_env(), timeout=300)
    return p.returncode, p.stdout + p.stderr


def _workspace(d: str) -> Path:
    """US0001 at Review, its one criterion verified by hand and sized for filing, so nothing but
    the review stands between it and Done. Provenance is stood down, so `record` needs no brief."""
    root = Path(d)
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / f"{UNIT}-a-unit.md").write_text(
        f"# {UNIT}: a unit\n\n> **Status:** Review\n> **Epic:** EP0001\n> **Points:** 2\n"
        "> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n### AC1: the unit behaves\n"
        "- **Verify:** manual a human looked\n- **Verified:** yes (2026-09-01)\n",
        encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "unit.py").write_text("x = 1\n", encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "review:\n  require_brief_provenance: false\n", encoding="utf-8")
    return root


def _story(root: Path, uid: str, status: str) -> None:
    """One story with a hand-verified criterion, and the index that lists it."""
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    (stories / f"{uid}-a-unit.md").write_text(
        f"# {uid}: a unit\n\n> **Status:** {status}\n> **Epic:** EP0001\n> **Points:** 2\n"
        "> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n### AC1: the unit behaves\n"
        "- **Verify:** manual a human looked\n- **Verified:** yes (2026-09-01)\n",
        encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "review:\n  require_brief_provenance: false\n", encoding="utf-8")


def _dated_reject(root: Path, uid: str, when: str) -> None:
    """A delivery REJECT of `uid` recorded through `critic.py record`, then re-dated to `when`
    (the verb stamps today)."""
    rc, out = _run(root, "critic.py", "record", "--unit", uid, "--verdict", "REJECT",
                   "--reviewer", "rev-a", "--author", "builder", "--issues", FINDINGS)
    assert rc == 0, out
    import critic  # noqa: PLC0415
    today = critic.read_verdicts(root)[-1]["date"]
    ledger = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
    text = ledger.read_text(encoding="utf-8")
    row = next(ln for ln in text.splitlines() if ln.startswith(f"| {uid} | REJECT |"))
    assert row.count(f"| {today} |") == 1, row
    ledger.write_text(text.replace(row, row.replace(f"| {today} |", f"| {when} |")),
                      encoding="utf-8")


def _record(root: Path, verdict: str, issues: str = "") -> tuple[int, str]:
    argv = ["record", "--unit", UNIT, "--verdict", verdict, "--reviewer", "rev-a",
            "--author", "builder"]
    return _run(root, "critic.py", *argv, *(["--issues", issues] if issues else []))


def _status(root: Path) -> str:
    text = (root / "sdlc-studio" / "stories" / f"{UNIT}-a-unit.md").read_text(encoding="utf-8")
    return sdlc_md.extract_field(text, "Status") or ""


def _artefact(uid: str) -> Path:
    kind = "bugs" if uid.startswith("BG") else "stories"
    return next((REPO / "sdlc-studio" / kind).glob(f"{uid}-*.md"))


class RepairLedgerGoneTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._saved is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._saved

    def _assert_names_the_exits(self, text: str) -> None:
        self.assertIn("round-2 APPROVE from the reviewer who rejected", text)
        self.assertIn("review cap", text)
        # carrying ends the run's hold, not the REJECT: Done still waits on that reviewer
        self.assertIn("A carried unit is still refused Done", text)
        self.assertIn("reaches Done on an APPROVE from the reviewer who rejected it", text)

    def test_the_repair_verb_is_retired(self) -> None:
        """AC1. MUTANTS: keep the `repair` subparser (the help lists it); refuse with argparse's
        `invalid choice`, which names no exit; drop either exit from the message; write the
        ledger before refusing."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            for argv in (("repair", "--unit", UNIT, "--author", "builder", "--closed",
                          f"{FIRST} -> fixed: a test pins it"),
                         ("repair", "--unit", UNIT, "--phase", "delivery")):
                with self.subTest(argv=" ".join(argv)):
                    rc, out = _run(root, "critic.py", *argv)
                    self.assertEqual(2, rc, out)
                    self.assertIn("`critic.py repair` is retired", out)
                    self._assert_names_the_exits(out)
                    self.assertFalse((root / "sdlc-studio" / "reviews").exists(),
                                     "a refused verb wrote a ledger")
            # the global --root before the verb resolves to the same refusal
            p = subprocess.run([sys.executable, "-B", str(SCRIPTS / "critic.py"), "--root",
                                str(root), "repair", "--unit", UNIT],
                               capture_output=True, text=True, check=False, env=_env(),
                               timeout=120)
            self.assertEqual(2, p.returncode, p.stderr)
            self.assertIn("`critic.py repair` is retired", p.stderr)
            rc, out = _run(root, "critic.py", "--help")
            self.assertEqual(0, rc, out)
            verbs = re.search(r"\{([a-z,-]+)\}", out)
            self.assertIsNotNone(verbs, f"the help lists no verbs:\n{out}")
            self.assertIn("record", verbs.group(1).split(","), "the control: a live verb")
            self.assertNotIn("repair", verbs.group(1).split(","))

    def test_a_repair_row_no_longer_answers_a_reject(self) -> None:
        """AC2. MUTANTS: keep the Done-side ledger read (HEAD: the closure rows answer the
        REJECT and the unit lands); keep `critic.py repair` in the refusal's remedy; answer a
        REJECT by an APPROVE from any reviewer (the hand-appended rev-b APPROVE lands the unit),
        or by none; skip the carry, or leave a carried unit held by the close; count a drop as a
        carry by its reason alone, below the cap, or naming a bug that is not on disk."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            self.assertEqual(0, _record(root, "REJECT", FINDINGS)[0])
            import critic  # noqa: PLC0415
            when = critic.read_verdicts(root)[-1]["date"]
            ledger = _ledger(root, UNIT, when)
            rc, out = _run(root, "transition.py", "set", "--id", UNIT, "--status", "Done")
            self.assertNotEqual(0, rc, f"a repair row answered the REJECT:\n{out}")
            self.assertEqual("Review", _status(root))
            said = "\n".join(ln for ln in out.splitlines() if "unanswered delivery REJECT" in ln)
            self.assertTrue(said, out)
            self.assertIn(FIRST, said, "the closed finding is not named as outstanding")
            self._assert_names_the_exits(out)
            self.assertNotIn("critic.py repair", out, "the refusal sends the reader to a retired verb")

            # exit one: the rejecting reviewer's round-2 APPROVE
            self.assertEqual(0, _record(root, "APPROVE")[0])
            rc, out = _run(root, "transition.py", "set", "--id", UNIT, "--status", "Done")
            self.assertEqual(0, rc, out)
            self.assertEqual("Done", _status(root))
            import conformance  # noqa: PLC0415
            self.assertEqual([], conformance.critiqued_unmet(root, UNIT), "critiqued is unmet")
            self.assertTrue(ledger.is_file(), "the ledger was removed rather than left unread")

        with tempfile.TemporaryDirectory() as d:
            # exit two: a round-2 REJECT in an open run carries the unit
            root = _workspace(d)
            run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
            self.assertEqual(0, _record(root, "REJECT", FINDINGS)[0])
            rc, out = _record(root, "REJECT", f"[new] {FIRST} still")
            self.assertEqual(0, rc, out)
            bugs = sorted((root / "sdlc-studio" / "bugs").glob("BG*.md"))
            self.assertEqual(1, len(bugs), out)
            bug = sdlc_md.extract_record_id(bugs[0].stem)
            state = run_state.read(root)
            self.assertEqual(["US0002"], state["batch"])
            self.assertEqual(f"carried at the review cap: {bug}",
                             state["batch_changes"][-1]["reason"])
            import sprint  # noqa: PLC0415
            held = {h["unit"]: h for h in sprint.unanswered_units(root, state)["unanswered"]}
            self.assertIn("US0002", held, "the control: an unfinished unit is still held")
            self.assertNotIn(UNIT, held, f"the close holds a carried unit: {held.get(UNIT)}")
            # the carry answers only while the bug holding the findings is on disk
            bugs[0].unlink()
            held = {h["unit"] for h in sprint.unanswered_units(root, state)["unanswered"]}
            self.assertIn(UNIT, held, "a carry naming a bug that does not exist answered it")

        # A hand drop worded like a carry is not one: a round-1 REJECT stays held, whether the
        # bug it names is missing or on disk.
        for name, bug in (("no such bug", "BG9999"), ("a real bug", "BG0001")):
            with self.subTest(spoof=name), tempfile.TemporaryDirectory() as d:
                root = _workspace(d)
                (root / "sdlc-studio" / "bugs").mkdir(parents=True)
                (root / "sdlc-studio" / "bugs" / "BG0001-a-bug.md").write_text(
                    "# BG0001: a bug\n\n> **Status:** Open\n", encoding="utf-8")
                run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
                self.assertEqual(0, _record(root, "REJECT", FINDINGS)[0])
                rc, out = _run(root, "sprint.py", "batch", "drop", UNIT, "--reason",
                               f"carried at the review cap: {bug}")
                self.assertEqual(0, rc, out)
                state = run_state.read(root)
                self.assertEqual(["US0002"], state["batch"], "the premise: the drop happened")
                held = {h["unit"]: h for h in sprint.unanswered_units(root, state)["unanswered"]}
                self.assertIn(UNIT, held, "a hand drop worded as a carry answered a round-1 "
                                          "REJECT")
                self.assertEqual([], held[UNIT]["filed"])

        with tempfile.TemporaryDirectory() as d:
            # Another reviewer's APPROVE is no exit, even written straight into the ledger past
            # `round_refusal`: only the reviewer who rejected answers the REJECT.
            root = _workspace(d)
            self.assertEqual(0, _record(root, "REJECT", FINDINGS)[0])
            ledger = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
            row = next(ln for ln in ledger.read_text(encoding="utf-8").splitlines()
                       if ln.startswith(f"| {UNIT} | REJECT |"))
            cells = row.strip().strip("|").split("|")
            cells[1], cells[2], cells[-1] = " APPROVE ", " rev-b ", " probed the edges "
            with ledger.open("a", encoding="utf-8") as fh:
                fh.write("|" + "|".join(cells) + "|\n")
            self.assertEqual("rev-b", critic.read_verdicts(root)[-1]["reviewer"])
            rc, out = _run(root, "transition.py", "set", "--id", UNIT, "--status", "Done")
            self.assertNotEqual(0, rc, f"another reviewer's APPROVE answered the REJECT:\n{out}")
            self.assertIn("unanswered delivery REJECT", out)
            self.assertEqual("Review", _status(root))

    def test_the_repair_ledger_is_frozen_and_unread(self) -> None:
        """AC3. MUTANTS: remove the Done-side read but keep `sprint.py` counting closures
        (`review_coverage`, `unanswered_units`, `_rejected_unanswered`) or `sprint_report.py`
        (the coverage rows, the operator summary); keep conformance's repaired-REJECT branch.
        Each output then moves with the file, which HEAD's did."""
        import sprint  # noqa: PLC0415
        unit = "US0004"                 # Done in the lean run, and in its batch
        outputs = {}
        with tempfile.TemporaryDirectory() as with_, tempfile.TemporaryDirectory() as without:
            for name, root in (("with", Path(with_)), ("without", Path(without))):
                lean.lean_run(root)
                with (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").open(
                        "a", encoding="utf-8") as fh:
                    fh.write(f"| {unit} | REJECT | a seat | author | 2026-09-20 | {FINDINGS} |\n")
                ledger = _ledger(root, unit, "2026-09-20") if name == "with" else None
                before = ledger.read_bytes() if ledger else None
                state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                                   .read_text(encoding="utf-8"))
                units = state["batch"]
                got = {}
                with contextlib.redirect_stderr(io.StringIO()):
                    got["review-coverage"] = sprint.review_coverage(root, units)
                    got["unanswered"] = sprint.unanswered_units(root, state, lean.RETRO)
                    got["forecast"] = sprint._rejected_unanswered(root, unit)  # noqa: SLF001
                for verb in ("checklist", "operator-summary"):
                    got[verb] = _run(root, "sprint_report.py", verb, "--id", lean.RETRO,
                                    root_first=True)
                got["conformance"] = _run(root, "conformance.py", "check")
                outputs[name] = json.loads(json.dumps(got, default=str)
                                           .replace(str(root), "<root>"))
                if ledger:
                    self.assertEqual(before, ledger.read_bytes(), "the ledger was rewritten")
        self.assertIn(unit, json.dumps(outputs["without"]["unanswered"]),
                      "the fixture's REJECT holds nothing, so it cannot tell a read")
        for key, value in outputs["without"].items():
            with self.subTest(output=key):
                self.assertEqual(value, outputs["with"][key],
                                 f"the repair ledger moved the {key} output")

    def test_the_fingerprint_key_answers_only_historic_rows(self) -> None:
        """AC4. MUTANTS: HEAD's unscoped fingerprint key (another reviewer's same-brief APPROVE
        answers a REJECT recorded after the round rule); drop the key entirely (the historic
        pair reopens); scope it by the REJECT's date alone."""
        import critic  # noqa: PLC0415
        brief = "0123456789ab"

        def pair(reject_on: str, approve_on: str, approver: str = "rev-b") -> list[dict]:
            return [{"unit": UNIT, "verdict": "REJECT", "reviewer": "rev-a", "author": "dev",
                     "date": reject_on, "brief": brief, "issues": FINDINGS},
                    {"unit": UNIT, "verdict": "APPROVE", "reviewer": approver, "author": "dev",
                     "date": approve_on, "brief": brief, "issues": "-"}]

        after = pair("2026-09-24", "2026-09-24")
        self.assertEqual([after[0]], critic._unanswered_rejects(after),  # noqa: SLF001
                         "another reviewer's same-brief APPROVE answered a new REJECT")
        straddle = pair("2026-08-16", "2026-09-24")
        self.assertEqual([straddle[0]], critic._unanswered_rejects(straddle))  # noqa: SLF001
        historic = pair("2026-08-16", "2026-08-16")
        self.assertEqual([], critic._unanswered_rejects(historic),  # noqa: SLF001
                         "a pair recorded before the round rule no longer matches")
        own = pair("2026-09-24", "2026-09-24", approver="rev-a")
        self.assertEqual([], critic._unanswered_rejects(own),  # noqa: SLF001
                         "the control: the rejecting reviewer's own round 2 answers it")
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        # This ledger's historic pairs stay answered: scoping the key reopens no unit.
        rows = critic.read_verdicts(REPO)
        units = sorted({sdlc_md.norm_id(r["unit"]) for r in rows})

        def standing() -> dict:
            return {u: len(critic._unanswered_rejects(  # noqa: SLF001
                critic._live_verdict_rows(REPO, u))) for u in units}  # noqa: SLF001

        scoped = standing()
        with mock.patch.object(critic, "ROUND_RULE_SHIPPED", "9999-12-31"):
            unscoped = standing()
        self.assertEqual(unscoped, scoped, "a historic REJECT reopened")

    def test_a_unit_done_under_the_frozen_ledger_stays_critiqued(self) -> None:
        """AC7. MUTANTS: no licence (the pre-constant story reads missing critiqued); a licence
        with no date (the on-constant story reads met); the licence in `critic.coverage_state`
        or the transition guard (the In Progress copy reaches Done); the licence on for every
        caller of `verdict_half_ok` (the seal's bar stops asking); the licence met but not
        counted or printed; an undated REJECT read as pre-constant; the licence claiming a unit
        a recorded waiver already answers (the waiver reads as carried by no unit)."""
        import datetime as dt  # noqa: PLC0415
        import critic  # noqa: PLC0415
        on = critic.REPAIR_VERB_RETIRED
        before = (dt.date.fromisoformat(on) - dt.timedelta(days=1)).isoformat()
        copy = "US0002"
        for when, met in ((before, True), (on, False), ("", False)):
            with self.subTest(reject_dated=when), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _story(root, UNIT, "Done")
                _dated_reject(root, UNIT, when)
                self.assertFalse((root / "sdlc-studio" / "reviews" / "repair-record.md").exists())
                _rc, out = _run(root, "conformance.py", "check")
                _rc, raw = _run(root, "conformance.py", "check", "--format", "json")
                result = json.loads(raw[raw.index("{"):])
                unit = {u["id"]: u for u in result["units"]}[UNIT]
                self.assertIs(met, unit["stages"]["critiqued"], out)
                self.assertIs(met, unit["licensed"], out)
                self.assertEqual(int(met), result["summary"]["licensed"], out)
                said = next((ln for ln in out.splitlines() if f"{UNIT} (Done): missing" in ln), "")
                if met:
                    self.assertNotIn("critiqued", said, out)
                    self.assertIn("LICENSED critiqued: 1 unit(s) passed on the repair-ledger "
                                  f"licence, a delivery REJECT dated before {on}", out)
                    self.assertIn(UNIT, out.split("LICENSED critiqued:", 1)[1].splitlines()[0])
                else:
                    self.assertIn("critiqued", said, out)
                    self.assertNotIn("LICENSED", out)
                if not met:
                    continue
                # The licence is history's: the seal's bar and the Done guard still ask for the
                # verdict, so current work has only the two exits.
                import conformance  # noqa: PLC0415
                import sprint  # noqa: PLC0415
                self.assertEqual([conformance.HALF_VERDICT], sprint.seal_bar_unmet(root, UNIT))
                _story(root, copy, "In Progress")
                _dated_reject(root, copy, before)
                rc, moved = _run(root, "transition.py", "set", "--id", copy, "--status", "Done")
                self.assertNotEqual(0, rc, f"the licence answered a REJECT at Done:\n{moved}")
                self.assertIn(f"{copy} carries an unanswered delivery REJECT", moved)
                self._assert_names_the_exits(moved)
                text = (root / "sdlc-studio" / "stories" / f"{copy}-a-unit.md").read_text(
                    encoding="utf-8")
                self.assertEqual("In Progress", sdlc_md.extract_field(text, "Status"))
                # the control: the REJECT was the only thing standing, and its exit clears it
                rc, out = _run(root, "critic.py", "record", "--unit", copy, "--verdict",
                               "APPROVE", "--reviewer", "rev-a", "--author", "builder")
                self.assertEqual(0, rc, out)
                rc, moved = _run(root, "transition.py", "set", "--id", copy, "--status", "Done")
                self.assertEqual(0, rc, moved)

        with tempfile.TemporaryDirectory() as d:
            # A recorded waiver is the older answer and keeps its attribution over the licence.
            root = Path(d)
            _story(root, UNIT, "Done")
            _dated_reject(root, UNIT, before)
            rc, out = _run(root, "decisions.py", "waive", "--subject",
                           f"rule:conformance:critiqued:{UNIT}", "--rationale", "operator ruling")
            self.assertEqual(0, rc, out)
            _rc, out = _run(root, "conformance.py", "check")
            self.assertRegex(out, rf"WAIVED critiqued: 1 unit\(s\) by D\d+ \({UNIT}\)")
            self.assertNotIn("LICENSED", out)
            self.assertNotIn("NOT carried", out)

    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC5. MUTANTS: leave the `repair` row in the surface; leave the surface stale."""
        surface = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        self.assertNotIn("`critic.py repair`", surface)
        self.assertIn("`critic.py record`", surface, "the control: a live verb is listed")
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        rc, out = _run(REPO, "docgen.py", "surface", "--check")
        self.assertEqual(0, rc, out)
        self.assertIn("docgen surface: 0 drift item(s)", out)

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC6. MUTANTS: delete a node without retiring its stamp; retire a stamp without its
        `Verified:` line or naming another retirer; keep a deleted node; delete a kept class."""
        for module, nodes in DELETED.items():
            tree = ast.parse((HERE / module).read_text(encoding="utf-8"))
            classes = {c.name: {getattr(n, "name", "") for n in c.body}
                       for c in tree.body if isinstance(c, ast.ClassDef)}
            for node in nodes:
                with self.subTest(deleted=f"{module}::{node}"):
                    cls, _, method = node.partition("::")
                    if method:
                        self.assertIn(cls, classes, f"{cls} was deleted whole")
                        self.assertNotIn(method, classes[cls])
                    else:
                        self.assertNotIn(cls, classes)
            for cls in KEPT.get(module, ()):
                self.assertIn(cls, classes, f"{cls} is edited, not deleted")
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        for uid, count in RETIRED.items():
            with self.subTest(unit=uid):
                text = _artefact(uid).read_text(encoding="utf-8")
                self.assertEqual(count, len(RETIRED_VERIFY.findall(text)), uid)
                self.assertEqual(count, len(RETIRED_STAMP.findall(text)), uid)
        import verify_ac  # noqa: PLC0415
        touched = {f".claude/skills/sdlc-studio/scripts/tests/{m}" for m in DELETED}
        names = {rel: verify_ac._ast_nodes((REPO / rel).read_text(encoding="utf-8"))  # noqa: SLF001
                 for rel in touched}
        dead = []
        for kind in ("stories", "bugs"):
            for path in sorted((REPO / "sdlc-studio" / kind).rglob("*.md")):
                text = path.read_text(encoding="utf-8", errors="replace")
                stamped = [(b.ac_id, b.verifier) for b in verify_ac.criteria_blocks(text)
                           if (b.verified_state or "").strip().lower() == "yes" and b.verifier]
                for ac, verifier in stamped:
                    test_file, node, kpat = verify_ac._selector_parts(verifier, REPO)  # noqa: SLF001
                    if test_file in names and not verify_ac._selector_live(  # noqa: SLF001
                            test_file, node, kpat, names[test_file]):
                        dead.append(f"{path.name[:6]} {ac}: {verifier}")
        self.assertEqual([], dead, "a `yes` stamp names a deleted test")


if __name__ == "__main__":
    unittest.main()
