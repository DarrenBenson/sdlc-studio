"""US0915: a review verdict has one phase, delivery.

The plan-review phase is gone from the CLI: `record` and `brief` refuse `--phase plan-review`
naming the retirement, and no verdict verb offers `--phase` or `--kind`. The plan-review brief,
its footer and the Kind vocabulary are deleted; `phase` survives only as an internal parameter
defaulting to `delivery`, so the historical ledger stays readable. AC1 and AC2 run in throwaway
workspaces through the shipped entry points; AC3 reads this repository, because its criterion
is about this repository's stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run
import workspace  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

REPO = workspace.REPO
CRITIC = SCRIPTS / "critic.py"
UNIT = "US0001"

#: The criteria this story retires, by artefact, in the D0259 pattern. Measured against
#: 70eafefc: every stamped selector naming a test this story deletes.
RETIRED = {
    "BG0596": ("AC8",), "BG0631": ("AC1",), "BG0645": ("AC1", "AC2"), "BG0666": ("AC2",),
    "US0631": ("AC1", "AC2", "AC3"), "US0634": ("AC1", "AC2"),
}
#: BG0510's eight, on checklist lines that carry no AC id.
CHECKLIST_RETIRED = {"BG0510": 8}

#: The test nodes this story deletes: a class, or one method of a class that survives.
DELETED = {
    "test_critic.py": ("PlanReviewBriefTests", "PlanReviewBriefUnauthoredNoteTests",
                       "PlanReviewKindTests", "PlanReviewOriginTests",
                       "PlanReviewBriefTeachesMultiRowTests",
                       "RepairPhaseJoinTests::test_a_delivery_repair_does_not_answer_a_same_text"
                       "_plan_review_rejection"),
    "test_retro.py": ("PlanVersusCodeReviewCostTests",),
    "test_sprint.py": ("EscalationReachesBothRecordingCommandsTests::test_a_plan_review_round_"
                       "does_not_inherit_delivery_batch_rounds",),
}


def _workspace(d: str) -> Path:
    """One story, one seat card, provenance stood down, so `record` needs no brief."""
    root = Path(d)
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / f"{UNIT}-a-unit.md").write_text(
        f"# {UNIT}: a unit\n\n> **Status:** Review\n> **Epic:** EP0001\n> **Points:** 2\n"
        "> **Affects:** src/unit.py\n\n"
        "## Acceptance Criteria\n\n- **AC1:** the unit behaves\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "unit.py").write_text("x = 1\n", encoding="utf-8")
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True)
    (seats / "qa.md").write_text("# QA seat\n", encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "review:\n  require_brief_provenance: false\n", encoding="utf-8")
    return root


def _critic(root: Path, *argv: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, **{run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts-for-tests"})
    return subprocess.run([sys.executable, "-B", str(CRITIC), *argv, "--root", str(root)],
                          capture_output=True, text=True, check=False, env=env, timeout=180)


def _ledger_files(root: Path) -> list[str]:
    reviews = root / "sdlc-studio" / "reviews"
    return sorted(p.name for p in reviews.iterdir()) if reviews.is_dir() else []


def _artefact(uid: str) -> Path:
    kind = "bugs" if uid.startswith("BG") else "stories"
    return next((REPO / "sdlc-studio" / kind).glob(f"{uid}-*.md"))


def _overclaims(text: str) -> list[str]:
    """The `yes`-stamped criteria in `text` that still claim `--phase plan-review` runs on a
    verdict verb, which exits 2 now. `repair --phase` survives (US0914), and a criterion that
    asserts the refusal itself, naming the retirement message, is not an over-claim."""
    import verify_ac  # noqa: PLC0415
    lines = text.splitlines()
    out = []
    for b in verify_ac.criteria_blocks(text):
        if (b.verified_state or "").strip().lower() != "yes":
            continue
        body = "\n".join(lines[b.heading_line:(b.verified_line or b.heading_line) + 1])
        if "plan review is retired" in body:
            continue
        out += [b.ac_id for m in re.finditer(r"--phase[ =]plan-review", body)
                if "repair" not in body[max(0, m.start() - 30):m.start()]]
    return out


class PlanPhaseGoneTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._env

    def test_the_plan_review_phase_is_retired(self) -> None:
        """AC1. MUTANTS: hide `--phase` and `--kind` from `record` and `brief` only (supersede
        and show still offer `--phase`); accept `--phase plan-review` and write to the plan
        ledger; delete the delivery write with the plan one (show reads nothing); drop the cap
        check (a third round is written)."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            for argv in (("record", "--unit", UNIT, "--phase", "plan-review", "--verdict",
                          "REJECT", "--reviewer", "qa", "--author", "dev"),
                         ("record", "--unit", UNIT, "--phase=plan-review", "--verdict",
                          "APPROVE", "--reviewer", "qa", "--author", "dev"),
                         ("brief", "--unit", UNIT, "--seat", "qa", "--phase", "plan-review")):
                with self.subTest(argv=" ".join(argv)):
                    r = _critic(root, *argv)
                    self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                    self.assertIn("plan review is retired", r.stderr)
                    self.assertEqual("", r.stdout, "a refused verb printed a result")
                    self.assertEqual([], _ledger_files(root), "a refused verb wrote a ledger")
            for verb in ("record", "brief", "supersede", "show"):
                with self.subTest(help=verb):
                    r = _critic(root, verb, "--help")
                    self.assertEqual(0, r.returncode, r.stderr)
                    self.assertIn("--root", r.stdout, "the help did not render")
                    self.assertNotIn("--phase", r.stdout)
                    self.assertNotIn("--kind", r.stdout)

            # The control: the delivery path, with no phase flag, and its two-round cap.
            run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
            r = _critic(root, "record", "--unit", UNIT, "--verdict", "REJECT", "--reviewer",
                        "rev-a", "--author", "builder", "--issues", "[new] the parser drops a row")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("[delivery] round 1", r.stdout)
            self.assertEqual(["critic-verdicts.md"], _ledger_files(root))
            shown = _critic(root, "show", "--unit", UNIT)
            self.assertEqual(0, shown.returncode, shown.stderr)
            self.assertIn("'verdict': 'REJECT'", shown.stdout)
            self.assertIn("'reviewer': 'rev-a'", shown.stdout)
            r = _critic(root, "record", "--unit", UNIT, "--verdict", "REJECT", "--reviewer",
                        "rev-a", "--author", "builder", "--issues", "[new] it still drops it")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("carried at the review cap", r.stdout)
            self.assertEqual(1, len(list((root / "sdlc-studio" / "bugs").glob("BG*.md"))))
            r = _critic(root, "record", "--unit", UNIT, "--verdict", "APPROVE", "--reviewer",
                        "rev-a", "--author", "builder")
            self.assertEqual(2, r.returncode, r.stdout + r.stderr)
            import critic  # noqa: PLC0415
            rows = [x for x in critic.read_verdicts(root) if sdlc_md.norm_id(x["unit"]) == UNIT]
            self.assertEqual([1, 2], [x["round"] for x in rows], "a third round was recorded")

    def test_rounds_count_delivery_verdicts_only(self) -> None:
        """AC2. MUTANTS: HEAD's `review_cost_split` (a plan-review arm beside the delivery one);
        fold the plan ledger's rows into the sprint report's rounds; rewrite the plan ledger;
        drop the split's run-unit filter (US0099 counts); stop rendering the split."""
        import retro  # noqa: PLC0415
        units = ["US0001", "US0002", "US0004", "US0005"]
        with tempfile.TemporaryDirectory() as without, tempfile.TemporaryDirectory() as with_:
            control, root = Path(without), Path(with_)
            for r in (control, root):
                lean.lean_run(r)
                # a delivery verdict on a unit outside the run: the split must not count it
                with (r / "sdlc-studio" / "reviews" / "critic-verdicts.md").open(
                        "a", encoding="utf-8") as fh:
                    fh.write("| US0099 | REJECT | a seat | author | 2026-09-20 |\n")
            plan = root / "sdlc-studio" / "reviews" / "plan-review-verdicts.md"
            plan.write_text(
                "# Plan-Review Verdicts\n\n"
                "| Unit | Verdict | Reviewer | Author | Date | Brief | Kind | Issues |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                + "".join(f"| {u} | REJECT | qa | dev | 2026-09-20 | {'a' * 12} | test-plan "
                          f"| a finding |\n" for u in units), encoding="utf-8")
            before = plan.read_bytes()

            split = retro.review_cost_split(root, units)
            self.assertEqual(["delivery"], list(split), "the split still has a plan-review arm")
            # the delivery arm is still measured from its own ledger: US0001 twice, US0002 once
            self.assertEqual({"state": "measured", "passes": 3, "rejected": 1, "units": 2},
                             split["delivery"])
            self.assertEqual(split, retro.review_cost_split(control, units))
            rendered = "\n".join(retro.render_review_cost(split))
            self.assertIn("code review: 3 pass(es) over 2 unit(s), 1 rejected", rendered)
            self.assertNotRegex(rendered, r"(?i)plan[- ]review|test-plan")
            # ...and the split reaches the retro's rendered accuracy output
            shown = "\n".join(retro._points_lines(  # noqa: SLF001
                {"batch": {"review_cost": split, "points": 0}, "n_measured": 0}))
            self.assertIn("code review: 3 pass(es) over 2 unit(s), 1 rejected", shown)

            def rounds(r: Path) -> dict:
                sec = lean._sections(lean.sr.build_report(r, lean.RETRO))["delivered"]
                return {row["unit_id"]["value"]: row["unit_rounds"]["value"]
                        for row in sec["rows"]}

            got = rounds(root)
            self.assertEqual(rounds(control), got, "the plan ledger moved the rework figure")
            self.assertEqual(2, got["US0001"], "the control is not the delivery ledger's rounds")
            self.assertEqual(before, plan.read_bytes(), "the plan-review ledger was rewritten")

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC3, on this repository's stamped criteria. MUTANTS: delete a node without retiring
        its stamp; retire a stamp by deleting its line rather than in the D0259 pattern; keep a
        node the criterion says is deleted; keep a `yes` stamp on a criterion that still names
        `--phase plan-review` on a verdict verb."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        import verify_ac  # noqa: PLC0415
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
        for uid, acs in RETIRED.items():
            blocks = {b.ac_id: b for b in verify_ac.criteria_blocks(
                _artefact(uid).read_text(encoding="utf-8"))}
            for ac in acs:
                with self.subTest(unit=uid, ac=ac):
                    block = blocks.get(ac)
                    self.assertIsNotNone(block, f"{uid} has no {ac}")
                    self.assertTrue((block.verifier or "").startswith(
                        "manual - retired by US0915: "), block.verifier)
                    self.assertEqual("manual", block.verified_state, block)
                    self.assertEqual("retired, superseded by US0915", block.verified_reason,
                                     block)
        checklist = [line for line in _artefact("BG0510").read_text(encoding="utf-8").splitlines()
                     if line.startswith("- [x]") and "*Verify:* manual - retired by US0915: "
                     in line and "*Verified:* manual (" in line
                     and line.endswith(") - retired, superseded by US0915")]
        self.assertEqual(CHECKLIST_RETIRED["BG0510"], len(checklist), "BG0510 is not retired")
        # Every stamped selector naming a touched module still selects something in this tree,
        # judged by AST the way the stamps-staged commit lane judges the index.
        touched = {f".claude/skills/sdlc-studio/scripts/tests/{m}" for m in DELETED}
        names = {rel: verify_ac._ast_nodes((REPO / rel).read_text(encoding="utf-8"))  # noqa: SLF001
                 for rel in touched}
        dead, overclaim = [], []
        for kind in ("stories", "bugs"):
            for path in sorted((REPO / "sdlc-studio" / kind).rglob("*.md")):
                text = path.read_text(encoding="utf-8", errors="replace")
                blocks = [b for b in verify_ac.criteria_blocks(text)
                          if (b.verified_state or "").strip().lower() == "yes"]
                overclaim += [f"{path.name[:6]} {ac}" for ac in _overclaims(text)]
                stamped = [(b.ac_id, b.verifier) for b in blocks if b.verifier]
                # the checklist shape criteria_blocks does not read: `- [x] ... *Verify:* ...`
                stamped += [("checklist", line.split("*Verify:* ", 1)[1].split(" *Verified:*")[0])
                            for line in text.splitlines()
                            if line.startswith("- [x]") and "*Verify:* " in line]
                for ac, verifier in stamped:
                    test_file, node, kpat = verify_ac._selector_parts(verifier, REPO)  # noqa: SLF001
                    if test_file in names and not verify_ac._selector_live(  # noqa: SLF001
                            test_file, node, kpat, names[test_file]):
                        dead.append(f"{path.name[:6]} {ac}: {verifier}")
        self.assertEqual([], dead, "a stamped criterion names a deleted test")
        self.assertEqual([], overclaim, "a `yes` stamp names `--phase plan-review`, which now "
                                        "exits 2: narrow the criterion to its surviving surfaces")
        # BG0769. The guard's two sides, on real criteria: US0915's own AC1 asserts the refusal,
        # so stamped `yes` (as Done writes it) it passes; BG0672 AC1 with its removed clause
        # restored claims the retired flag still runs, so it is still flagged.
        own = re.sub(r"(?m)^(\s*)- \*\*Verify:\*\* pytest [^\n]*$",
                     lambda m: f"{m.group(0)}\n{m.group(1)}- **Verified:** yes (2026-09-25)",
                     _artefact("US0915").read_text(encoding="utf-8"))
        self.assertEqual({"AC1", "AC2", "AC3"}, {b.ac_id for b in verify_ac.criteria_blocks(own)
                                                if b.verified_state == "yes"})
        self.assertEqual([], _overclaims(own), "the guard flags the story that retires the flag")
        clause = "writes a delivery row whose Brief cell holds `0123456789ab` and `unmatched`\n"
        bg0672 = _artefact("BG0672").read_text(encoding="utf-8")
        self.assertEqual(1, bg0672.count(clause), "the regression's anchor moved")
        restored = bg0672.replace(clause, clause[:-1] + ", and the same value recorded with "
                                  "`--phase plan-review` writes a plan-review row carrying the "
                                  "marker too\n")
        self.assertEqual(["AC1"], _overclaims(restored), "the exemption passes a real over-claim")


if __name__ == "__main__":
    unittest.main()
