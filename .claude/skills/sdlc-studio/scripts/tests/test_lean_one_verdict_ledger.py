"""US0918: one verdict ledger decides whether a unit was reviewed.

`critic.py evidence`, `critic.py sprint-review` and `sprint.py review-batch` are retired, each
naming `critic.py record`. The evidence ledger (`critic-evidence.md`) is read by nothing. The
batch-review ledger (`sprint-review-record.md`) is the only record that some historical Done
units were reviewed, so it is read frozen: a row dated before `critic.REPAIR_VERB_RETIRED` still
covers the units it names, a later one covers nothing, and every reader applies that one licence
through `critic.sprint_reviews`.

AC1, AC2 and AC3 run in throwaway workspaces through the shipped entry points. AC4 and AC5 read
this repository's generated surface and stamped criteria, because their criteria are about them.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import ast
import contextlib
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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

#: The retired verbs, by script, and the words each refusal must carry.
RETIRED = (("critic.py", "evidence", ("--unit", UNIT, "--reviewer", "rev-a", "--author",
                                      "builder", "--findings", "probed the edges")),
           ("critic.py", "sprint-review", ("--units", UNIT, "--reviewer", "rev-a", "--author",
                                           "builder", "--verdict", "APPROVE", "--findings",
                                           "full-diff pass")),
           ("sprint.py", "review-batch", ("--units", UNIT, "--reviewer", "rev-a", "--author",
                                          "builder", "--findings", "full-diff pass")))

#: The test nodes this story deletes: a whole class, or one method of a class that survives.
DELETED = {
    "test_critic.py": ("EvidenceTests",
                       "CodeSpanEdgeSpaceTests::test_the_evidence_writer_inherits_the_refusal",
                       "CliTests::test_cli_SprintReview_records_and_covers",
                       "CliTests::test_cli_SprintReview_refuses_self_review",
                       # the review round's only writer went with `critic.py sprint-review`
                       "ReviewRoundCountTests::test_recording_a_verdict_increments_the_run_"
                       "review_round",
                       "ReviewRoundCountTests::test_verdict_without_an_open_run_reports_rather_"
                       "than_counts"),
    "test_conformance.py": (
        "SprintReviewCritiquedTests::test_SprintReview_refuses_self_review_and_empty",),
    "test_sprint.py": ("BatchBoundaryReviewTests", "ReviewBatchFieldsFileTests",
                       "EscalationReachesBothRecordingCommandsTests",
                       "TheCloseCertifiesRatherThanReviewsTests"),
    "test_sprint_report.py": (
        "SprintChecklistStageTests::test_a_batch_span_OPENED_is_not_a_review_HELD",),
}
#: The SprintReviewCritiquedTests cases that pin the frozen read survive, and keep their stamps.
KEPT = {"test_conformance.py": (
    "SprintReviewCritiquedTests::test_sprint_review_clears_critiqued_for_covered_unit",
    "SprintReviewCritiquedTests::test_SprintReview_does_not_override_a_per_unit_reject")}

#: The criteria retired, by artefact, and how many each carried, in the D0259 pattern.
#: BG0441 AC1/AC3 and BG0499 AC3 still ship: their stamps are re-pointed at
#: `SurvivingReviewRulesTests`, not retired.
RETIRED_ACS = {"BG0441": 1, "BG0499": 2, "BG0659": 1, "US0247": 1, "US0261": 2, "US0560": 5,
               "US0561": 1, "US0562": 4, "US0563": 1, "US0615": 2}
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0918: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0918\b")

_BATCH_HEAD = ("# Sprint-level Reviews\n\n"
               "| Base | Reviewer | Author | Verdict | Date | Units | Findings |\n"
               "| --- | --- | --- | --- | --- | --- | --- |\n")
_EVIDENCE_HEAD = ("# Critic Evidence\n\n| Unit | Reviewer | Author | Date | Findings |\n"
                  "| --- | --- | --- | --- | --- |\n")


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


def _reviews(root: Path) -> Path:
    path = root / "sdlc-studio" / "reviews"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _batch_row(root: Path, units: str, when: str, reviewer: str = "rev-c",
               author: str = "builder") -> Path:
    """One APPROVE row in the frozen batch ledger, as `review-batch` wrote it, dated `when`."""
    path = _reviews(root) / "sprint-review-record.md"
    path.write_text(_BATCH_HEAD + f"| - | {reviewer} | {author} | APPROVE | {when} | {units} | "
                    "full-diff pass; none blocking |\n", encoding="utf-8")
    return path


def _done_story(root: Path) -> None:
    """US0001 Done, its one criterion verified by hand, and brief provenance stood down so
    `critic.py record` needs no brief."""
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    (stories / f"{UNIT}-a-unit.md").write_text(
        f"# {UNIT}: a unit\n\n> **Status:** Done\n> **Epic:** EP0001\n> **Points:** 2\n"
        "> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n### AC1: the unit behaves\n"
        "- **Verify:** manual a human looked\n- **Verified:** yes (2026-09-01)\n",
        encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "review:\n  require_brief_provenance: false\n", encoding="utf-8")


def _critiqued(root: Path) -> tuple[bool, list, str]:
    """US0001's `critiqued` stage, what it owes, and its line in the text report."""
    _rc, raw = _run(root, "conformance.py", "check", "--format", "json")
    unit = {u["id"]: u for u in json.loads(raw[raw.index("{"):])["units"]}[UNIT]
    _rc, text = _run(root, "conformance.py", "check")
    said = next((ln for ln in text.splitlines() if f"{UNIT} (Done): missing" in ln), "")
    return unit["stages"]["critiqued"], unit["critiqued_missing"], said


class OneVerdictLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._saved is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._saved

    def test_the_ledger_verbs_are_retired(self) -> None:
        """AC1. MUTANTS: keep a verb's subparser (its script's help lists it); refuse with
        argparse's `invalid choice`, which names no successor; name no `critic.py record`;
        write the ledger before refusing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _done_story(root)
            for script, verb, argv in RETIRED:
                for first in (False, True):
                    with self.subTest(verb=verb, root_first=first):
                        rc, out = _run(root, script, verb, *argv, root_first=first)
                        self.assertEqual(2, rc, out)
                        self.assertIn(f"`{script} {verb}` is retired", out)
                        self.assertIn("`critic.py record`", out)
                        self.assertIn("Nothing was written", out)
                        self.assertFalse((root / "sdlc-studio" / "reviews").exists(),
                                         "a refused verb wrote a ledger")
            for script in ("critic.py", "sprint.py"):
                with self.subTest(help=script):
                    rc, out = _run(root, script, "--help")
                    self.assertEqual(0, rc, out)
                    verbs = re.search(r"\{([a-z,-]+)\}", out)
                    self.assertIsNotNone(verbs, f"the help lists no verbs:\n{out}")
                    listed = verbs.group(1).split(",")
                    self.assertIn("record" if script == "critic.py" else "close", listed,
                                  "the control: a live verb is listed")
                    for gone in ("evidence", "sprint-review", "review-batch"):
                        self.assertNotIn(gone, listed)

    def test_only_a_frozen_batch_row_or_a_delivery_approve_covers(self) -> None:
        """AC2. MUTANTS: HEAD (no date licence: the on-constant row covers); delete the batch
        read outright (the pre-constant row stops covering); compare with `<=` (the on-constant
        row covers); read an undated row as history; licence `sprint_review_for` alone (the
        sign's `session_reviewer_ids`, which reads `sprint_reviews`, still counts the
        on-constant row's reviewer)."""
        import critic  # noqa: PLC0415
        on = critic.REPAIR_VERB_RETIRED
        before = (dt.date.fromisoformat(on) - dt.timedelta(days=1)).isoformat()
        for when, covered in ((before, True), (on, False), ("", False)):
            with self.subTest(row_dated=when or "undated"), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _done_story(root)
                ledger = _batch_row(root, UNIT, when)
                met, owes, said = _critiqued(root)
                self.assertIs(covered, met, said)
                if covered:
                    self.assertEqual([], owes)
                    self.assertNotIn("critiqued", said)
                else:
                    import conformance  # noqa: PLC0415
                    self.assertEqual([conformance.HALF_VERDICT], owes)
                    self.assertIn(f"critiqued ({conformance.HALF_VERDICT})", said)
                # every reader of the ledger applies the same licence
                self.assertIs(covered, critic.sprint_review_for(root, UNIT) is not None)
                self.assertIs(covered, "rev-c" in critic.session_reviewer_ids(root, UNIT))
                self.assertIs(covered, critic.coverage_state(root, UNIT)
                              == critic.COVERAGE_APPROVED)
                import sprint  # noqa: PLC0415
                self.assertIs(covered, sprint.review_coverage(root, [UNIT])[UNIT]["covered"])
                # an independent delivery APPROVE covers the unit either way
                rc, out = _run(root, "critic.py", "record", "--unit", UNIT, "--verdict",
                               "APPROVE", "--reviewer", "rev-a", "--author", "builder")
                self.assertEqual(0, rc, out)
                met, owes, said = _critiqued(root)
                self.assertTrue(met, said)
                self.assertEqual([], owes)
                self.assertTrue(ledger.is_file(), "the frozen ledger was removed, not read")

    def test_the_evidence_ledger_is_frozen_and_unread(self) -> None:
        """AC3. MUTANTS: keep any evidence read - `sprint.review_coverage`'s evidence lane,
        `unanswered_units`' at-Review read or `_signoff_author` (the checklist, the close or
        the author moves with the file), or `critic._adversarial_worker_ids` and
        `session_reviewer_ids`; rewrite either ledger."""
        import sprint  # noqa: PLC0415
        outputs = {}
        with tempfile.TemporaryDirectory() as with_, tempfile.TemporaryDirectory() as without:
            for name, root in (("with", Path(with_)), ("without", Path(without))):
                lean.lean_run(root)
                # US0004 is Done with no verdict of its own; US0005 waits at Review
                batch = _batch_row(root, "US0004", "2026-09-20", author="author")
                evidence = None
                if name == "with":
                    evidence = _reviews(root) / "critic-evidence.md"
                    evidence.write_text(
                        _EVIDENCE_HEAD
                        + "| US0004 | rev-b | ev-author | 2026-09-20 | probed the edges |\n"
                        + "| US0005 | rev-b | ev-author | 2026-09-20 | probed the edges |\n",
                        encoding="utf-8")
                saved = {p: p.read_bytes() for p in (batch, evidence) if p}
                state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                                   .read_text(encoding="utf-8"))
                got = {}
                with contextlib.redirect_stderr(io.StringIO()):
                    got["review-coverage"] = sprint.review_coverage(root, state["batch"])
                    got["unanswered"] = sprint.unanswered_units(root, state, lean.RETRO)
                    got["author"] = sprint._signoff_author(root, "US0004")  # noqa: SLF001
                import critic  # noqa: PLC0415
                got["reviewers"] = sorted(critic.session_reviewer_ids(root, "US0004"))
                got["workers"] = sorted(critic._adversarial_worker_ids(  # noqa: SLF001
                    root, "US0004"))
                rc, raw = _run(root, "conformance.py", "check", "--format", "json")
                census = json.loads(raw[raw.index("{"):])
                census.pop("generated_at")
                got["conformance"] = (rc, census, _run(root, "conformance.py", "check"))
                rc, gate = _run(root, "gate.py", "--only", "conformance", "--format", "json")
                checks = json.loads(gate[gate.index("{"):])["checks"]
                got["gate"] = (rc, [{k: v for k, v in c.items() if k != "seconds"}
                                    for c in checks])
                got["close"] = _run(root, "sprint.py", "close", "--dry-run")
                for verb in ("checklist", "operator-summary"):
                    got[verb] = _run(root, "sprint_report.py", verb, "--id", lean.RETRO,
                                     root_first=True)
                outputs[name] = json.loads(json.dumps(got, default=str)
                                           .replace(str(root), "<root>"))
                for path, before in saved.items():
                    self.assertEqual(before, path.read_bytes(), f"{path.name} was rewritten")
        self.assertEqual({"covered": True, "by": "batch review"},
                         outputs["without"]["review-coverage"]["US0004"],
                         "the control: the frozen batch row covers the Done unit")
        for key, value in outputs["without"].items():
            with self.subTest(output=key):
                self.assertEqual(value, outputs["with"][key],
                                 f"the evidence ledger moved the {key} output")
        # and no shipped script reaches for the evidence reader
        callers = []
        for path in sorted(SCRIPTS.rglob("*.py")):
            if "tests" in path.relative_to(SCRIPTS).parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            callers += [f"{path.name}:{n.lineno}" for n in ast.walk(tree)
                        if (isinstance(n, ast.Attribute) and n.attr == "evidence_for")
                        or (isinstance(n, ast.Name) and n.id == "evidence_for")]
        self.assertEqual([], callers, "a shipped script still reads the evidence ledger")

    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC4. MUTANTS: leave a retired verb's row in the surface; leave the surface stale."""
        surface = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        for gone in ("`critic.py evidence`", "`critic.py sprint-review`",
                     "`sprint.py review-batch`"):
            self.assertNotIn(gone, surface)
        self.assertIn("`critic.py record`", surface, "the control: a live verb is listed")
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        rc, out = _run(REPO, "docgen.py", "surface", "--check")
        self.assertEqual(0, rc, out)
        self.assertIn("docgen surface: 0 drift item(s)", out)

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC5. MUTANTS: delete a node without retiring its stamp; retire a stamp without its
        `Verified:` line or naming another retirer; keep a deleted node; delete a kept case."""
        for module in sorted(set(DELETED) | set(KEPT)):
            tree = ast.parse((HERE / module).read_text(encoding="utf-8"))
            classes = {c.name: {getattr(n, "name", "") for n in c.body}
                       for c in tree.body if isinstance(c, ast.ClassDef)}
            for node in DELETED.get(module, ()):
                with self.subTest(deleted=f"{module}::{node}"):
                    cls, _, method = node.partition("::")
                    if method:
                        self.assertIn(cls, classes, f"{cls} was deleted whole")
                        self.assertNotIn(method, classes[cls])
                    else:
                        self.assertNotIn(cls, classes)
            for node in KEPT.get(module, ()):
                with self.subTest(kept=f"{module}::{node}"):
                    cls, _, method = node.partition("::")
                    self.assertIn(method, classes.get(cls, set()), f"{node} was deleted")
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        for uid, count in RETIRED_ACS.items():
            with self.subTest(unit=uid):
                kind = "bugs" if uid.startswith("BG") else "stories"
                text = next((REPO / "sdlc-studio" / kind).glob(f"{uid}-*.md")).read_text(
                    encoding="utf-8")
                self.assertEqual(count, len(RETIRED_VERIFY.findall(text)), uid)
                self.assertEqual(count, len(RETIRED_STAMP.findall(text)), uid)
        us0247 = next((REPO / "sdlc-studio" / "stories").glob("US0247-*.md")).read_text(
            encoding="utf-8")
        for node in KEPT["test_conformance.py"]:
            self.assertIn(f"test_conformance.py::{node}", us0247, "a kept case lost its stamp")
        for uid, count in (("BG0441", 2), ("BG0499", 1)):
            text = next((REPO / "sdlc-studio" / "bugs").glob(f"{uid}-*.md")).read_text(
                encoding="utf-8")
            self.assertEqual(count, text.count("test_lean_one_verdict_ledger.py::"
                                               "SurvivingReviewRulesTests::"),
                             f"{uid}'s shipping rule is not stamped on its re-homed test")
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


class SurvivingReviewRulesTests(unittest.TestCase):
    """The rules the deleted batch-review and escalation classes pinned that still ship, each
    re-homed onto a frozen (pre-constant) batch row or a delivery verdict in place of the
    retired writers."""

    def test_a_reject_is_terminal_beside_a_frozen_batch_approve(self) -> None:
        """BG0441 AC1. MUTANT: drop the terminal-REJECT stop from `sprint.review_coverage`, so
        the REJECT falls through to the batch lane and is laundered into coverage."""
        import critic  # noqa: PLC0415
        import sprint  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _batch_row(root, UNIT, "2026-09-20", reviewer="rev-a", author="author-b")
            got = sprint.review_coverage(root, [UNIT])[UNIT]
            self.assertEqual({"covered": True, "by": "batch review"}, got,
                             "the control: the frozen batch row covers an unrejected unit")
            critic.record_verdict(root, UNIT, "REJECT", reviewer="rev-a", author="author-b",
                                  issues="[new] the repairs are not re-reviewed")
            got = sprint.review_coverage(root, [UNIT])[UNIT]
            self.assertFalse(got["covered"],
                             f"a REJECT was laundered into coverage by the {got['by']} lane")
            self.assertEqual([UNIT], sprint.uncovered_units(root, [UNIT]))

    def test_a_frozen_batch_reject_does_not_cover(self) -> None:
        """MUTANT: drop `sprint_covers_independently` from `sprint.review_coverage`'s lanes,
        leaving only the independence check, so a batch REJECT row clears the gate."""
        import sprint  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (_reviews(root) / "sprint-review-record.md").write_text(
                _BATCH_HEAD + f"| - | rev-a | author-b | REJECT | 2026-09-20 | {UNIT} | "
                "this batch is broken |\n", encoding="utf-8")
            self.assertFalse(sprint.review_coverage(root, [UNIT])[UNIT]["covered"],
                             "a REJECTED batch cleared the coverage gate")
            self.assertEqual([UNIT], sprint.uncovered_units(root, [UNIT]))

    def test_an_unreadable_verdict_ledger_does_not_manufacture_a_rejection(self) -> None:
        """BG0441 AC3. MUTANT: answer 'rejected' when `_no_negative_verdict` cannot read the
        verdict ledger, inventing a verdict nobody gave and holding the unit on an I/O error."""
        import critic  # noqa: PLC0415
        import sprint  # noqa: PLC0415
        from unittest import mock  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _batch_row(root, UNIT, "2026-09-20", reviewer="rev-a", author="author-b")
            with mock.patch.object(critic, "verdict_for",
                                   side_effect=OSError("permission denied")):
                got = sprint.review_coverage(root, [UNIT])[UNIT]
        self.assertEqual({"covered": True, "by": "batch review"}, got,
                         "an unreadable ledger was treated as a REJECT, inventing a verdict")

    def test_the_exclusion_line_names_unpriced_units(self) -> None:
        """MUTANT: fold the unpriced units into the priced total, or drop their clause. The
        control: with nothing excluded, the line makes no arithmetic claim."""
        import sprint  # noqa: PLC0415
        out = sprint.exclusion_line({"built_not_closed": ["US0002"], "built_points": 3,
                                     "points": 5, "unpriced": ["US0003"]})
        self.assertIn("removes 3 point(s)", out)
        self.assertIn("1 unit(s) with no points at all", out)
        self.assertNotIn("batch's 8", out)
        quiet = sprint.exclusion_line({"built_not_closed": ["US0002"], "built_points": 0,
                                       "points": 5, "unpriced": []})
        self.assertIn("US0002", quiet)
        self.assertNotIn("removes", quiet)

    def test_two_rejects_through_critic_record_escalate(self) -> None:
        """BG0499 AC3. MUTANT: drop the escalation call from `critic.cmd_record`. The control:
        one REJECT does not escalate."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            outs = []
            for _ in range(2):
                rc, out = _run(root, "critic.py", "record", "--unit", "US0017", "--verdict",
                               "reject", "--reviewer", "qa-seat", "--author", "builder",
                               "--brief", "abcdef123456", "--issues", "[new] probed the diff")
                self.assertEqual(0, rc, out)
                outs.append(out)
        self.assertNotIn("ESCALATED", outs[0], "a first REJECT escalated")
        self.assertIn("ESCALATED", outs[1],
                      f"two REJECTs recorded through critic.py record notified nobody:\n{outs[1]}")


if __name__ == "__main__":
    unittest.main()
