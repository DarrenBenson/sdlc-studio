"""US0917: the operator's signature seals the run, and no per-unit sign-off row is written.

`sprint.py sign` moves each batch unit to its terminal status and writes the one run signature.
The review bar it still holds - an independent delivery APPROVE, as `conformance` judges
`critiqued` - is the bar the close reads too, so a Review unit the close does not list is one
the seal will move, and one it lists is one the seal refuses. `sprint.py preflight` is retired;
`close_preflight` still runs inside `sprint.py close`.

AC1 to AC3 drive the shipped entry points in throwaway workspaces. AC4 and AC5 read this
repository, because their criteria name its surface table and its stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import workspace  # noqa: E402
import conformance  # noqa: E402
import critic  # noqa: E402
import sprint  # noqa: E402
import sprint_report  # noqa: E402
import test_lean_no_two_role as stamps  # noqa: E402 - the derived deleted-node check (US0916)

REPO = workspace.REPO
RUN = "RUN-LEAN0917"

#: Nodes this story deletes, as (class, test) - a whole class as (class, ""). The full deleted
#: set is DERIVED; these prove the derivation reads the right base, since each must appear in it.
AC5_DELETED = {
    "test_sprint.py": (
        ("OnePreflightCountReadByBothRenderersTests", ""),
        ("PreflightChecklistTests", "test_the_shipped_preflight_verb_reports_the_checklist"),
        ("CloseCostRecordingTests", "test_the_shipped_preflight_verb_records_its_gate"),
        ("SealTests", "test_one_principal_writes_the_unit_rows_and_the_run_signature")),
    "test_sprint_report.py": (("SignoffProvenanceTests", ""),),
}


def _unit(root: Path, uid: str, *, green: bool = True, verdict: str | None = "independent",
          status: str = "Review") -> None:
    """A story at `status` with one executable criterion, its verify-report entry (green or
    red) and, by `verdict`, an independent APPROVE, a self-review APPROVE or no review."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{uid}-x.md").write_text(
        f"# {uid}: unit\n\n> **Status:** {status}\n> **Points:** 2\n> **Epic:** EP0001\n\n"
        "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
        encoding="utf-8")
    rp = root / "sdlc-studio" / ".local" / "verify-report.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    report = json.loads(rp.read_text(encoding="utf-8")) if rp.is_file() else {"stories": {}}
    report["stories"][f"{uid}-x"] = {"failed": 0 if green else 1, "stale": 0,
                                     "failures": [] if green else [{"ac": "AC1"}],
                                     "ac_count": 1, "verified_at": "2099-01-01T00:00:00Z"}
    rp.write_text(json.dumps(report), encoding="utf-8")
    if verdict == "independent":
        critic.record_verdict(root, uid, "APPROVE", reviewer="qa-seat", author="builder",
                              issues="probed the edges; none blocking")
    elif verdict == "self":
        critic.record_verdict(root, uid, "APPROVE", reviewer="builder", author="builder",
                              issues="looked at my own work")


def _run_state(root: Path, batch: list[str], **over) -> dict:
    state = {"schema": 1, "run_id": RUN, "started_at": "2026-09-25T00:00:00Z",
             "ended_at": None, "outcome": "running", "goal": "done", "batch": batch,
             "handoff": None, "report": "RPT0001", "sprint_goal": "sign seals once",
             "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"}}
    state.update(over)
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")
    return state


def _cli(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _sign(root: Path) -> tuple[int, str, str]:
    return _cli(root, "sign", "--report", "RPT0001", "--principal", "Darren")


def _status(root: Path, uid: str) -> str:
    text = (root / "sdlc-studio" / "stories" / f"{uid}-x.md").read_text(encoding="utf-8")
    return text.split("> **Status:** ", 1)[1].splitlines()[0].strip()


def _signoff_rows(root: Path) -> list:
    path = root / "sdlc-studio" / "reviews" / "signoff-record.md"
    return [ln for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.startswith("| US")] if path.is_file() else []


def _run(script: str, *argv: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv, "--root",
                           str(root)], capture_output=True, text=True, check=False, timeout=300)


class SignSealsOnceTests(unittest.TestCase):

    def test_sign_writes_no_signoff_rows(self) -> None:
        """AC1. MUTANTS: HEAD's `_apply_signoff`, which writes a sign-off row per unit; a seal
        that drops the review bar and moves an unreviewed or self-reviewed unit to Done, or
        judges only the units it moves, so one moved to Done by hand walks round it; a seal that
        drops the terminal gate and moves a red unit to Done; a close that lists a Review unit
        carrying an independent APPROVE, disagreeing with the seal that moves it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for uid in ("US0101", "US0102"):
                _unit(root, uid)
            state = _run_state(root, ["US0101", "US0102"])
            # The close and the seal agree: a Review unit whose only owed step is the signature
            # is not a known issue at the close.
            self.assertEqual([], sprint.unanswered_units(root, state)["unanswered"])
            rc, out, err = _sign(root)
            self.assertEqual(0, rc, out + err)
            self.assertEqual(["Done", "Done"], [_status(root, u) for u in ("US0101", "US0102")])
            self.assertEqual([], _signoff_rows(root), "sign wrote a per-unit sign-off row")
            run = sprint.run_state.read(root)
            self.assertEqual("Darren", run["signature"]["principal"])
            self.assertEqual("goal-reached", run["outcome"])
            # The close-status block the close stamped said the signature was owed; it now says
            # the signature landed.
            anchor = (root / "sdlc-studio" / "reviews" / "LATEST.md").read_text(encoding="utf-8")
            self.assertIn(f"{RUN} closed goal-reached", anchor)
            self.assertIn("run is SIGNED", anchor)
        # THE CONTROLS: one unit whose criteria are red, one with no review, one reviewed only by
        # its own author, one moved to Done by hand with no review. Each stops naming the unit
        # and its unmet bar and leaves the run open.
        for case, kw, bar in (("red", {"green": False}, "AC"),
                              ("unreviewed", {"verdict": None}, "independent APPROVE"),
                              ("self-review", {"verdict": "self"}, "independent APPROVE"),
                              ("hand-moved", {"verdict": None, "status": "Done"},
                               "independent APPROVE")):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _unit(root, "US0101")
                _unit(root, "US0102", **kw)
                state = _run_state(root, ["US0101", "US0102"])
                rc, out, err = _sign(root)
                self.assertNotEqual(0, rc, out + err)
                stop = [ln for ln in err.splitlines() if "US0102" in ln]
                self.assertTrue(stop, f"the stop does not name US0102:\n{err}")
                self.assertIn(bar, " ".join(stop), err)
                if case != "hand-moved":
                    self.assertNotEqual("Done", _status(root, "US0102"))
                run = sprint.run_state.read(root)
                self.assertEqual("running", run["outcome"], "the run was sealed")
                self.assertIsNone(run.get("signature"), "a stopped seal wrote the signature")
                self.assertEqual([], _signoff_rows(root))
                if case == "red":
                    continue
                # The review bar is judged over the whole batch before anything moves, and the
                # close names exactly the unit the seal refuses: a Review unit as a known issue,
                # a unit already at Done through its conformance lane's `critiqued` stage.
                self.assertEqual("Review", _status(root, "US0101"))
                held = [h["unit"] for h in sprint.unanswered_units(root, state)["unanswered"]]
                if case == "hand-moved":
                    self.assertEqual([], held)
                    units = {u["id"]: u for u in conformance.detect_conformance(root)["units"]}
                    self.assertIn("critiqued", units["US0102"]["missing"])
                else:
                    self.assertEqual(["US0102"], held)

    def test_preflight_is_retired(self) -> None:
        """AC2. MUTANTS: keep the verb; keep it in the parser; delete `close_preflight` with it,
        or stop `sprint.py close` calling it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _run_state(root, ["US0101"])
            rc, out, err = _cli(root, "preflight", "--retro", "RETRO0001")
            self.assertEqual(2, rc, out + err)
            self.assertIn("retired", err)
            self.assertIn("sprint.py close", err)
            proc = _run("sprint.py", "--help", root=root)
            self.assertEqual(0, proc.returncode, proc.stderr)
            verbs = proc.stdout.split("{", 1)[1].split("}", 1)[0].split(",")
            self.assertIn("close", verbs)
            self.assertNotIn("preflight", verbs)
            # close_preflight still runs inside `sprint.py close`: spied, and the close refused
            # later for a reason of its own (no sprint goal).
            _run_state(root, ["US0101"], sprint_goal=None)
            calls = []
            with unittest.mock.patch.object(
                    sprint, "close_preflight",
                    lambda *a, **k: calls.append(a) or {"ready": True, "blockers": [],
                                                        "gate_ran": False}):
                rc, out, err = _cli(root, "close", "--retro", "RETRO0001")
            self.assertEqual(2, rc, out + err)
            self.assertIn("no sprint goal", err)
            self.assertEqual(1, len(calls), "the close no longer runs its pre-flight")

    def test_the_report_carries_no_per_unit_signoff(self) -> None:
        """AC3. MUTANTS: keep the checklist's sign-off row; keep the operator summary's
        `signed_by` capacity; keep `_signoff_owed` feeding the close-status block, which then
        says sign-off is owed for units with no sign-off row; restore the stop's
        awaiting-sign-off count."""
        self.assertNotIn("signoff", [row["id"] for row in sprint_report.CHECKLIST])
        self.assertFalse(hasattr(sprint_report, "_ck_signoff"))
        self.assertFalse(hasattr(sprint, "_signoff_owed"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _unit(root, "US0101")
            state = _run_state(root, ["US0101"])
            ck = sprint_report.checklist(root, "RETRO0001", unit_ids=["US0101"])
            titles = " ".join(r["title"].lower() for r in ck["items"])
            self.assertNotIn("sign-off", titles)
            rep = {"ok": True, "units": ["US0101"], "sprint_goal": "sign seals once",
                   "sprint_goal_verdict": {"verdict": "achieved"}}
            summary = sprint_report.operator_summary(root, "RETRO0001", rep=rep)
            self.assertEqual([{"unit": "US0101"}], summary["shipped"])
            page = sprint_report.render_operator_summary(summary)
            self.assertIn("Shipped (1): US0101", page)
            self.assertNotIn("signed", page.lower())
            # The close-status block states the run's one signature, never a per-unit sign-off.
            ok, detail, _remedy = sprint._close_review_anchor(root, "RETRO0001", state)
            self.assertTrue(ok, detail)
            anchor = (root / "sdlc-studio" / "reviews" / "LATEST.md").read_text(encoding="utf-8")
            block = anchor.split(sprint.ANCHOR_BEGIN, 1)[1].split(sprint.ANCHOR_END, 1)[0]
            self.assertNotIn("sign-off", block.lower())
            self.assertNotIn("two-role", block)
            self.assertIn("run signature is OWED", block)
            sprint.run_state.update(root, signature={"principal": "Darren"})
            sprint._close_review_anchor(root, "RETRO0001", sprint.run_state.read(root))
            anchor = (root / "sdlc-studio" / "reviews" / "LATEST.md").read_text(encoding="utf-8")
            self.assertIn("run is SIGNED", anchor)
            self.assertNotIn("OWED", anchor)
            # `stop` counts no unit as awaiting a sign-off, on its page or its record.
            rc, out, err = _cli(root, "stop", "--reason", "enough")
            self.assertEqual(0, rc, out + err)
            self.assertNotIn("sign-off", (out + err).lower())
            self.assertNotIn("awaiting_signoff", sprint.run_state.read(root)["stop"])

    @unittest.skipUnless(workspace.in_dev_repo(), workspace.SKIP_REASON)
    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC4. MUTANT: retire the verb without rerunning `docgen.py surface`, so the table still
        lists it and `--check` reports drift."""
        text = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        self.assertTrue("`sprint.py sign`" in text, "the surface lost a live verb")
        for script in ("sprint.py", "autosprint.py"):
            self.assertFalse(f"`{script} preflight`" in text,
                             f"the surface lists {script} preflight")
        r = _run("docgen.py", "surface", "--check", root=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("docgen surface: 0 drift item(s)", r.stdout)

    @unittest.skipUnless(workspace.in_dev_repo(), workspace.SKIP_REASON)
    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC5. MUTANTS: leave a retired criterion's `Verified: yes` stamp in place; keep a
        deleted class in its module.

        The deleted nodes are DERIVED, as US0916's check derives them: every class and `test_`
        function a changed test module defined at the base and no longer defines, the base
        being the parent of the commit that added this module (HEAD while it is uncommitted)."""
        base = _base_ref()
        if base is None:
            self.skipTest("no git history here to derive the deleted tests from")
        deleted = stamps._deleted_nodes(base)
        for module, nodes in AC5_DELETED.items():
            gone = deleted.get(module, {}).get("gone", set())
            for node in nodes:
                self.assertIn(node, gone, f"{module}::{node} was to be deleted ({base})")
        tests = ".claude/skills/sdlc-studio/scripts/tests/test_sprint.py"
        controls = {
            "live": ([f"- **Verify:** pytest {tests}::OnePreflightCountReadByBothRenderersTests",
                      "- **Verified:** yes (2026-08-18)"], ["live:1"]),
            "retired": ([f"- **Verify:** pytest {tests}::OnePreflightCountReadByBothRenderersTests",
                         "- **Verified:** manual (2026-09-25) - retired, superseded by US0917"],
                        []),
        }
        for label, (lines, want) in controls.items():
            self.assertEqual(stamps._live_stamps([(label, lines)], deleted), want, label)
        live = stamps._live_stamps(((path.relative_to(REPO), path.read_text(
            encoding="utf-8", errors="replace").splitlines())
            for path in sorted((REPO / "sdlc-studio").rglob("*.md"))), deleted)
        self.assertEqual(live, [], "a live stamp selects only deleted test nodes")


def _base_ref() -> str | None:
    """The parent of the commit that added this module, or HEAD while it is uncommitted."""
    rel = Path(__file__).resolve().relative_to(REPO).as_posix()
    added = stamps._git("log", "--diff-filter=A", "--format=%H", "--", rel)
    if added is None:
        return None
    ref = f"{added.split()[0]}^" if added.split() else "HEAD"
    return ref if stamps._git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") else None


if __name__ == "__main__":
    unittest.main()
