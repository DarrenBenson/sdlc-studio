"""US0941 and BG0787: a report Maya signed still validates after the tree moves on.

`sprint_report.py check` judged a signed page against today's backlog, lesson store and decisions
log, so RPT0006, RPT0007 and RPT0008 read INVALID within a day of their signatures: a lesson
gained a hit, a finding the run raised was fixed, a unit was re-sized, a waiver's rationale was
amended in place (BG0743). Each test files and signs a page from the one-page report's fixture
run, commits it as the seal does, moves one of those sources the way the backlog moves, and reads
the verdict through the shipped `sprint_report.py check` entry point.

The page's readings of those sources are replayed from the page its signing commit holds, never
from the file on disk: the forgery tests re-derive the page from the moved tree, recompute its
fingerprint and re-render its twin, and `check` must still refuse it.

A unit's review rounds are re-derived, but only from the verdict rows recorded inside the run:
RPT0009 read INVALIDATED once the next run reviewed a unit it had cut (BG0787).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import gitutil  # noqa: E402 - confined, hermetic git for fixtures
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run

sr = lean.sr
DECISIONS = HERE.parent / "decisions.py"
STORE = Path("sdlc-studio") / "lessons.jsonl"
RATIONALE = "the floor is out of scope for this fixture"


def _utc(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _lesson(lid: str, name: str, hits: list[dict]) -> dict:
    return {"id": lid, "class": name, "rule": "a rule", "behaviour": "a behaviour",
            "inject": ["build"], "hits": hits, "state": "active"}


class SignedReportStableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        lean.lean_run(self.root)

    # --- helpers ---------------------------------------------------------------------------

    def _git(self, *args: str) -> None:
        gitutil.git(list(args), self.root)

    def _write_store(self, rows: list[dict]) -> None:
        (self.root / STORE).write_text("".join(json.dumps(r) + "\n" for r in rows),
                                       encoding="utf-8")

    def _file_and_sign(self, as_of: str | None = None, commit: bool = True,
                       commit_signed: bool = True) -> str:
        """File the page, sign it through the seal's own signature writer, and commit the
        signed page, as the seal's commit does. `commit_signed=False` stops before that last
        commit: the window between `sprint sign` and the seal commit."""
        import sprint  # noqa: PLC0415 - the seal's signature writer, not a hand-made one
        if commit:   # the run's work is history before the page is derived, as in a real close
            self._git("init", "-q", ".")
            self._git("add", "-A")
            self._git("-c", "commit.gpgsign=false", "commit", "-qm", "the delivered batch")
        rid = sr.file_report(self.root, sr.build_report(self.root, lean.RETRO, as_of=as_of))
        with contextlib.redirect_stdout(io.StringIO()):
            sprint._write_the_signature(self.root, rid, "Maya Okafor")
        self.assertEqual("Maya Okafor", sr.read_report(self.root, rid)["signature"]["principal"])
        if commit and commit_signed:
            self._git("add", "-A")
            self._git("-c", "commit.gpgsign=false", "commit", "-qm", "sign the report")
        rc, out = self._check(rid)
        self.assertEqual(0, rc, f"the page did not validate before anything moved: {out}")
        return rid

    def _check(self, rid: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "check", "--report", rid])
        return rc, out.getvalue() + err.getvalue()

    def _assert_valid(self, rid: str) -> None:
        rc, out = self._check(rid)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {rid}", out)

    def _replace(self, path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        self.assertEqual(1, text.count(old), f"the edit anchor {old!r} is not unique in {path}")
        path.write_text(text.replace(old, new), encoding="utf-8")

    def _bug(self, bid: str) -> Path:
        return next((self.root / "sdlc-studio" / "bugs").glob(f"{bid}-*.md"))

    @staticmethod
    def _section(report: dict, key: str) -> dict:
        return next(s for s in report["sections"] if s["key"] == key)

    def _fresh(self, rid: str) -> dict:
        """The page re-derived from today's tree over its own window, reading every source."""
        page = sr.read_report(self.root, rid)
        return sr.build_report(self.root, lean.RETRO, as_of=page["generated_at"],
                               window_end=page["window_end"])

    def _forge(self, rid: str) -> dict:
        """Re-derive the page from the moved tree and file it over the signed one, fingerprint
        recomputed and twin re-rendered, so the page on disk is consistent with itself."""
        page = sr.read_report(self.root, rid)
        forged = {**self._fresh(rid), "report_id": rid}
        forged["signature"] = {**page["signature"], "fingerprint": forged["fingerprint"]}
        sr.write_report(self.root, forged)
        self.assertEqual(forged["fingerprint"], sr.fingerprint(sr.read_report(self.root, rid)))
        self.assertNotEqual(page["fingerprint"], forged["fingerprint"])
        return forged

    def _waive(self, rationale: str = RATIONALE) -> None:
        proc = subprocess.run(
            [sys.executable, str(DECISIONS), "waive", "--subject", "rule:engagement-floor",
             "--rationale", rationale, "--root", str(self.root)],
            capture_output=True, text=True, timeout=60, env={**os.environ, "TZ": "UTC"})
        self.assertEqual(0, proc.returncode, proc.stderr)

    def _open_run_an_hour_old(self) -> None:
        """An open run that started an hour ago, so a waiver recorded now falls in its window."""
        live = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(live.read_text(encoding="utf-8"))
        state["started_at"] = _utc(datetime.now(timezone.utc) - timedelta(hours=1))
        state.pop("ended_at")
        live.write_text(json.dumps(state), encoding="utf-8")

    # --- the criteria ----------------------------------------------------------------------

    def test_a_moved_lesson_store_does_not_invalidate(self) -> None:
        """AC1. MUTANT: `_lifecycle_edits` compares every figure outside the digest, the lessons
        and lane-yield sections included, so a hit recorded by the next close reads as a hand
        edit (RPT0008: `lessons.lesson_hits_total[1]: filed 9, the run record gives 21`)."""
        self._write_store([_lesson("LC-001", "mutant never applied",
                                   [{"run": lean.RUN, "unit": "US0001", "source": "retro"}])])
        rid = self._file_and_sign()
        filed = self._section(sr.read_report(self.root, rid), "lessons")
        self.assertEqual(1, filed["rows"][0]["lesson_hits_total"]["value"])

        # The next run's close records a hit on the class and adds a second class.
        self._write_store([
            _lesson("LC-001", "mutant never applied",
                    [{"run": lean.RUN, "unit": "US0001", "source": "retro"},
                     {"run": "RUN-01NEXTRUN", "unit": "US0009", "source": "retro"}]),
            _lesson("LC-002", "criterion words outrun the fixture", [])])
        moved = self._section(self._fresh(rid), "lessons")
        self.assertEqual(2, moved["rows"][0]["lesson_hits_total"]["value"],
                         "the store did not move, so this proves nothing")
        self.assertEqual(2, len(moved["rows"]))
        self._assert_valid(rid)

    def test_a_closed_finding_and_edited_points_do_not_invalidate(self) -> None:
        """AC2. MUTANT: re-derive the open-finding rows and the unit points from today's statuses
        and Points lines rather than the page's own reading - fixing a finding the run raised,
        or re-sizing a unit it delivered, moves `issue_id`, `findings_scan`, `unit_points` and
        `points_delivered`, and the signed page reads INVALIDATED."""
        rid = self._file_and_sign()
        page = sr.read_report(self.root, rid)
        issues = [r["issue_id"]["value"] for r in self._section(page, "known_issues")["rows"]]
        self.assertIn("BG0901", issues)

        self._replace(self._bug("BG0901"), "> **Status:** Open", "> **Status:** Fixed")
        self._replace(self._bug("BG0902"), "> **Severity:** Low", "> **Severity:** High")
        self._replace(self._bug("BG0902"), "# BG0902: the finding BG0902",
                      "# BG0902: the finding BG0902, retitled in triage")
        stories = self.root / "sdlc-studio" / "stories"
        self._replace(next(stories.glob("US0001-*.md")), "> **Points:** 8", "> **Points:** 13")
        # Today's tree really has moved: re-reading it gives other figures.
        fresh = self._fresh(rid)
        self.assertNotEqual(page["fingerprint"], fresh["fingerprint"])
        self.assertNotIn("BG0901", [r["issue_id"]["value"]
                                    for r in self._section(fresh, "known_issues")["rows"]])

        self._assert_valid(rid)
        state = sr.revalidate(self.root, rid)
        self.assertEqual([], state["moved"])
        self.assertEqual([], state["edited"])

    def test_an_amended_waiver_rationale_does_not_invalidate(self) -> None:
        """AC3. MUTANT: freeze the findings and the lessons but still digest the waiver's
        rationale prose from the decisions log - amending it in place, as D0074 was, moves
        `waivers.waiver_reason[0]` and the signed page reads INVALIDATED (BG0743)."""
        self._open_run_an_hour_old()
        self._waive()
        # Derived in a later second than the waiver, which the half-open window would exclude
        # in its own second; the signing commit then lands at or after the window's end.
        time.sleep(1.1)
        rid = self._file_and_sign()
        rows = self._section(sr.read_report(self.root, rid), "waivers")["rows"]
        self.assertEqual([RATIONALE], [r["waiver_reason"]["value"] for r in rows],
                         "the page carries no waiver, so this proves nothing")

        amended = f"{RATIONALE}; SCOPE CORRECTED later - the floor applies to docs only"
        self._replace(self.root / "sdlc-studio" / "decisions.md", RATIONALE, amended)
        self.assertEqual([amended], [r["waiver_reason"]["value"] for r in
                                     self._section(self._fresh(rid), "waivers")["rows"]])
        self._assert_valid(rid)

    def test_a_hand_edited_figure_is_still_invalid(self) -> None:
        """AC4. MUTANT: pass AC1-AC3 by taking every figure out of the digest - a page whose
        delivered count was edited by hand, its twin re-rendered to match as a careful editor
        would, then reads VALID. Run after a finding is closed, so the readings the page
        replays are not what hides the edit."""
        rid = self._file_and_sign()
        self._replace(self._bug("BG0901"), "> **Status:** Open", "> **Status:** Fixed")
        self._assert_valid(rid)                  # the positive control

        path = self.root / "sdlc-studio" / "reports" / f"{rid}.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        count = self._section(report, "delivered")["figures"]["plan_delivered_units"]
        self.assertEqual(2, count["value"])
        count["value"] = 3
        sr.write_report(self.root, report)       # keeps the signed fingerprint, re-renders

        rc, out = self._check(rid)
        self.assertEqual(1, rc, out)
        self.assertIn("INVALID", out)
        self.assertIn("plan_delivered_units", out)
        self.assertIn("filed 3", out)

    # --- the anchor: a page cannot re-sign itself -------------------------------------------

    def test_a_page_forged_to_match_the_moved_tree_is_invalid(self) -> None:
        """MUTANT: replay the readings from the page on disk - a page re-derived from the moved
        tree, its fingerprint recomputed and its twin re-rendered, then certifies itself, so an
        open High can be hidden or a unit's points inflated under a signature that never saw
        them."""
        moves = {
            "hide the open High BG0901": (
                lambda: self._replace(self._bug("BG0901"), "> **Status:** Open",
                                      "> **Status:** Fixed"),
                "known_issues.issue_id"),
            "inflate US0001 from 8 to 21 points": (
                lambda: self._replace(
                    next((self.root / "sdlc-studio" / "stories").glob("US0001-*.md")),
                    "> **Points:** 8", "> **Points:** 21"),
                "delivered.unit_points"),
        }
        for label, (move, figure) in moves.items():
            with self.subTest(label):
                self.setUp()
                rid = self._file_and_sign()
                move()
                self._assert_valid(rid)          # the move alone leaves the signed page valid
                self._forge(rid)
                rc, out = self._check(rid)
                self.assertEqual(1, rc, out)
                self.assertIn("INVALID", out)
                self.assertIn(figure, out)
                self.assertIn("the page signed in", out)
                self.assertNotIn("INVALIDATED", out, "the tree did not move under the signature")

    def test_a_signed_page_no_commit_holds_reads_every_source(self) -> None:
        """A page signed but not yet committed has nothing outside itself to anchor its
        readings to, so none is replayed: every source is read from the tree, and a finding
        closed after the signature invalidates it. MUTANT: replay from the file when history
        holds no signed page - the forgery above then reads VALID on any uncommitted page."""
        rid = self._file_and_sign(commit=False)
        self._replace(self._bug("BG0901"), "> **Status:** Open", "> **Status:** Fixed")
        rc, out = self._check(rid)
        self.assertEqual(1, rc, out)
        self.assertIn("INVALIDATED", out)
        self.assertIn("issue_id", out)

    def _head(self) -> str:
        return gitutil.git(["rev-parse", "HEAD"], self.root, text=True).stdout.strip()

    def _commit(self, message: str) -> str:
        self._git("add", "-A")
        self._git("-c", "commit.gpgsign=false", "commit", "-qm", message)
        return self._head()

    def _moves(self) -> dict:
        """The two forgeries the page must not certify: an open High hidden, and a unit's
        points inflated, each by re-deriving the page from a tree moved that way."""
        return {
            "hide the open High BG0901": (
                lambda: self._replace(self._bug("BG0901"), "> **Status:** Open",
                                      "> **Status:** Fixed"), "known_issues.issue_id"),
            "inflate US0001 from 8 to 21 points": (
                lambda: self._replace(
                    next((self.root / "sdlc-studio" / "stories").glob("US0001-*.md")),
                    "> **Points:** 8", "> **Points:** 21"), "delivered.unit_points")}

    def test_a_page_forged_on_a_merged_branch_is_invalid(self) -> None:
        """BG0775 AC2. MUTANT: read the page's history without `--full-history` - merging a side
        branch with `-X theirs` simplifies the real signing commit out of `git log -- path`, so
        the forged version becomes the earliest signed one and certifies itself."""
        for label, (move, _figure) in self._moves().items():
            with self.subTest(label):
                self.setUp()
                rid = self._file_and_sign()
                signing = self._head()
                main = gitutil.git(["rev-parse", "--abbrev-ref", "HEAD"], self.root,
                                   text=True).stdout.strip()
                move()
                forged = {**self._fresh(rid), "report_id": rid}
                forged["signature"] = {**sr.read_report(self.root, rid)["signature"],
                                       "fingerprint": forged["fingerprint"]}
                self._git("checkout", "-q", "--", ".")
                # A side branch from the commit BEFORE the signature, carrying the forgery.
                self._git("checkout", "-q", "-b", "side", f"{signing}~1")
                sr.write_report(self.root, forged)
                # Backdated, so ordering by date alone would take it for the earlier signature.
                self._git("add", "-A")
                gitutil.git(["-c", "commit.gpgsign=false", "commit", "-qm",
                             "a signed page, from a side branch"], self.root,
                            env_extra={"GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
                                       "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00"})
                side = self._head()
                self._git("checkout", "-q", main)
                self._git("-c", "commit.gpgsign=false", "merge", "-q", "--no-edit",
                          "-X", "theirs", "side")
                self.assertEqual(forged["fingerprint"],
                                 sr.read_report(self.root, rid)["fingerprint"],
                                 "the merge did not bring the forged page in")
                rc, out = self._check(rid)
                self.assertEqual(1, rc, out)
                self.assertIn("INVALID", out)
                self.assertIn(signing[:10], out)
                self.assertIn(side[:10], out)
                # The real signature is the anchor and the side branch the one named, whatever
                # the commit dates say.
                self.assertIn(f"the page signed in {signing[:10]} reads", out)
                self.assertIn(f"committed in {side[:10]}", out)
                self.assertNotIn(f"committed in {signing[:10]}", out)

    def test_a_page_minted_under_a_new_id_does_not_certify_itself(self) -> None:
        """BG0775 AC3. MUTANT: anchor any principal-bearing page to its own first commit - a copy
        of the signed page committed under a new id, a figure forged and the principal kept, is
        then its own anchor, reads VALID and `status` calls it signed."""
        for label, (move, _figure) in self._moves().items():
            with self.subTest(label):
                self.setUp()
                rid = self._file_and_sign()
                move()
                forged = {**self._fresh(rid), "report_id": "RPT0002"}
                forged["signature"] = {**sr.read_report(self.root, rid)["signature"],
                                       "fingerprint": forged["fingerprint"]}
                sr.write_report(self.root, forged)
                self._commit("a second signed page")
                rc, out = self._check("RPT0002")
                self.assertEqual(1, rc, out)
                self.assertTrue(out.startswith("INVALID: RPT0002"), out)
                self.assertIn(f"signed on {rid}, not RPT0002", out)
                state = sr.report_status(self.root)
                self.assertEqual("RPT0002", state["report_id"], "status reads another page")
                line = sr.status_line(state)
                self.assertNotIn("signed by", line)
                self.assertIn("INVALID", line)
                self._assert_valid(rid)          # the run's own signed page still stands

    def _forged_at_current_schema(self, rid: str) -> None:
        """Close the open High BG0901 and file the page re-derived from that tree over the
        signed one, principal kept and fingerprint recomputed."""
        self._replace(self._bug("BG0901"), "> **Status:** Open", "> **Status:** Fixed")
        self._forge(rid)

    def test_a_page_committed_first_by_a_forger_is_not_the_anchor(self) -> None:
        """MUTANT: anchor to the first committed signed version - `sprint sign` does not
        commit the page, so whoever commits first between the signature and the seal commit
        would set the anchor. The run record's fingerprint decides instead."""
        rid = self._file_and_sign(commit_signed=False)
        self._forged_at_current_schema(rid)
        self._commit("the seal commit, made by the forger")
        rc, out = self._check(rid)
        self.assertEqual(1, rc, out)
        self.assertIn("INVALID", out)
        signed_at = sr.run_state.read(self.root)["signature"]["fingerprint"]
        self.assertIn(f"no committed version of {rid} carries the {signed_at}", out)
        line = sr.status_line(sr.report_status(self.root))
        self.assertNotIn("signed by", line)
        self.assertIn("INVALID", line)

    def test_a_page_signed_under_an_older_schema_cannot_be_replaced(self) -> None:
        """MUTANT: consider only signed versions of this schema - the real signing commit, at
        an older schema, drops out, and a page re-filed at this schema with a finding hidden is
        the only signed version left to anchor to."""
        rid = self._file_and_sign(commit_signed=False)
        path = self.root / "sdlc-studio" / "reports" / f"{rid}.json"
        page = json.loads(path.read_text(encoding="utf-8"))
        sr.write_report(self.root, {**page, "schema": sr.SCHEMA - 1})
        signing = self._commit("sign the report, under the older schema")
        self._forged_at_current_schema(rid)
        self._commit("the page re-filed at this schema")
        rc, out = self._check(rid)
        self.assertEqual(1, rc, out)
        self.assertIn(f"signed in {signing[:10]} under report schema {sr.SCHEMA - 1}", out)

    def test_a_page_whose_recorded_fingerprint_alone_is_edited_is_invalid(self) -> None:
        """MUTANT: compare only the figures with the signed page - a page whose figures are
        untouched but whose recorded fingerprint is rewritten reads VALID."""
        rid = self._file_and_sign()
        page = sr.read_report(self.root, rid)
        sr.write_report(self.root, {**page, "fingerprint": "0" * 16})
        rc, out = self._check(rid)
        self.assertEqual(1, rc, out)
        self.assertIn("json fingerprint: filed '0000000000000000'", out)

    def test_a_relative_root_still_finds_the_signed_page(self) -> None:
        """MUTANT: hand git the report path unresolved - from a relative root it is resolved
        against the root a second time, no history is found, nothing is anchored, and a
        finding closed after the signature reads INVALIDATED."""
        rid = self._file_and_sign()
        self._replace(self._bug("BG0901"), "> **Status:** Open", "> **Status:** Fixed")
        here = os.getcwd()
        self.addCleanup(os.chdir, here)
        os.chdir(self.root.parent)
        state = sr.revalidate(Path(self.root.name), rid)
        self.assertTrue(state["valid"], state)

    def test_a_later_signed_version_does_not_replace_the_anchor(self) -> None:
        """BG0775 AC4. MUTANT: anchor to the LATEST signed version - a forgery committed on top
        of the signed page is then the anchor, no figure differs from it, and only the history
        is named."""
        for label, (move, figure) in self._moves().items():
            with self.subTest(label):
                self.setUp()
                rid = self._file_and_sign()
                signing = self._head()
                move()
                self._forge(rid)
                later = self._commit("a later signed version")
                rc, out = self._check(rid)
                self.assertEqual(1, rc, out)
                self.assertIn("INVALID", out)
                self.assertIn(f"{figure}[", out)
                self.assertIn(f"the page signed in {signing[:10]} reads", out)
                self.assertIn(later[:10], out)

    # --- what the replay still re-derives, and what it holds ------------------------------

    def test_a_listed_finding_is_still_placed_in_the_window(self) -> None:
        """The replay holds a listed finding's status, severity and title, never its place in
        the run. MUTANT: replay every listed row without placing it - a listed finding whose
        stamp now falls outside the run's window stays on the page."""
        rid = self._file_and_sign()
        self._replace(self._bug("BG0901"), f"{lean.RUN} 2026-09-20T10:00:00Z",
                      f"{lean.RUN} 2026-08-20T10:00:00Z")
        rc, out = self._check(rid)
        self.assertEqual(1, rc, out)
        self.assertIn("INVALIDATED", out)
        self.assertIn("findings_scan", out)

    def test_a_listed_waiver_amended_or_superseded_and_an_unlisted_one_do_not_invalidate(
            self) -> None:
        """The replay holds a listed waiver's subject and its status, and which waivers the page
        lists. MUTANTS: read the subject from the log; drop a listed waiver once superseded;
        list a waiver the page did not, dated by its day alone on the page's own day."""
        self._open_run_an_hour_old()
        self._waive()
        # Derived in a later second than the waiver, which the half-open window would exclude
        # in its own second; the signing commit then lands at or after the window's end.
        time.sleep(1.1)
        rid = self._file_and_sign()
        page = sr.read_report(self.root, rid)
        self.assertEqual(1, len(self._section(page, "waivers")["rows"]))

        decisions = self.root / "sdlc-studio" / "decisions.md"
        self._replace(decisions, "| waiver: rule:engagement-floor |",
                      "| waiver: rule:engagement-floor (docs only) |")
        self._replace(decisions, "| accepted |", "| superseded |")
        self._waive("a second waiver, recorded after the page")
        # The second waiver's Date cell cut to the page's own day: the legacy date-only shape.
        row = next(ln for ln in decisions.read_text(encoding="utf-8").splitlines()
                   if ln.startswith("| D0002 |"))
        stamp = row.rstrip(" |").rsplit("| ", 1)[1]
        self._replace(decisions, row, row.replace(stamp, page["generated_at"][:10]))
        fresh = self._section(self._fresh(rid), "waivers")["rows"]
        self.assertEqual(1, len(fresh), "the log did not move, so this proves nothing")
        self.assertNotEqual(self._section(page, "waivers")["rows"][0]["waiver_id"]["value"],
                            fresh[0]["waiver_id"]["value"])
        self._assert_valid(rid)

    # --- BG0787: a unit's review rounds are counted inside the run's window ------------------

    LEDGER = Path("sdlc-studio") / "reviews" / "critic-verdicts.md"

    def _record(self, unit: str, verdict: str) -> None:
        """Record a verdict through the shipped `critic.py record`, as a later run's review
        does: dated today, and fixing the unit's review base when an open run holds it."""
        proc = subprocess.run(
            [sys.executable, str(HERE.parent / "critic.py"), "record", "--unit", unit,
             "--verdict", verdict, "--reviewer", "qa-rev-later", "--author", "later-build",
             "--issues", "[new] a finding of the later run", "--root", str(self.root)],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stderr)

    def _rounds(self, report: dict) -> dict:
        return {r["unit_id"]["value"]: r["unit_rounds"]["value"]
                for r in self._section(report, "delivered")["rows"]}

    def _run_ending_now(self) -> str:
        """Move the fixture run onto today, ending now, with its ledger rows dated today and
        its reviewed units' bases fixed: the shape of RUN-01M3BK9Y, whose next run opened and
        reviewed a unit it had not on the same UTC day. Returns that day."""
        now = datetime.now(timezone.utc)
        live = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(live.read_text(encoding="utf-8"))
        state.update({"started_at": _utc(now - timedelta(hours=1)), "ended_at": _utc(now),
                      sr.run_state.REVIEW_BASE: {"US0001": 0, "US0002": 0}})
        live.write_text(json.dumps(state), encoding="utf-8")
        day = state["ended_at"][:10]
        ledger = self.root / self.LEDGER
        ledger.write_text(ledger.read_text(encoding="utf-8").replace("2026-09-20", day),
                          encoding="utf-8")
        return day

    def _open_a_later_run(self, batch: list[str]) -> None:
        """Archive the signed run and open the next one holding `batch`, as the next plan does."""
        sr.run_state.archive(self.root)
        sr.run_state.write(self.root, {"schema": 1, "run_id": "RUN-01LATERRUN",
                                       "started_at": _utc(datetime.now(timezone.utc)),
                                       "outcome": "running",
                                       "batch": batch})

    def test_a_later_run_reviewing_a_batch_unit_does_not_invalidate(self) -> None:
        """BG0787 AC1. MUTANTS: count a unit's rounds over every row in the live ledger - a
        carried unit the next run reviews moves the signed `unit_rounds` from 0 to 2 (RPT0009:
        `unit_rounds[28]: signed 0, now 2`); bound the rows by the window's DAY alone - the next
        run's rows on the page's own day still count; bound them by the later run's review base
        alone - a review recorded on a later day outside any run still counts. The next run
        re-reviews US0001, which this run reviewed, so its base is what bounds US0001."""
        cases = {
            "the next run reviews it on the page's own day": True,
            "a review outside any run on a later day": False,
        }
        for label, same_day in cases.items():
            with self.subTest(label):
                self.setUp()
                day = self._run_ending_now() if same_day else None
                rid = self._file_and_sign()
                signed = self._rounds(sr.read_report(self.root, rid))
                self.assertEqual({"US0001": 2, "US0002": 1, "US0005": 0},
                                 {u: signed[u] for u in ("US0001", "US0002", "US0005")})
                if same_day:
                    self._open_a_later_run(["US0005", "US0001"])
                    self._record("US0001", "approve")
                self._record("US0005", "reject")
                self._record("US0005", "approve")
                later = [ln for ln in (self.root / self.LEDGER).read_text(
                    encoding="utf-8").splitlines() if ln.startswith("| US0005 |")]
                self.assertEqual(2, len(later), "the later review was not recorded")
                if same_day:
                    # Dated inside the window's last day, so only the next run's base places
                    # them outside the run.
                    self.assertTrue(all(f"| {day} |" in ln for ln in later), later)

                self._assert_valid(rid)
                state = sr.revalidate(self.root, rid)
                self.assertEqual([], state["moved"])
                page = sr.read_report(self.root, rid)
                fresh = sr.build_report(self.root, lean.RETRO, as_of=page["generated_at"],
                                        window_end=page["window_end"], run_id=lean.RUN)
                self.assertEqual(signed, self._rounds(fresh))

    def test_a_hand_edited_in_window_round_is_still_invalid(self) -> None:
        """BG0787 AC2. MUTANT: replay the rounds from the signed page, or widen the window past
        the run's own rows - deleting the REJECT that made US0001 a two-round unit then reads
        VALID."""
        rid = self._file_and_sign()
        page = sr.read_report(self.root, rid)
        rows = self._section(page, "delivered")["rows"]
        self.assertEqual("US0001", rows[0]["unit_id"]["value"])
        self.assertEqual(2, rows[0]["unit_rounds"]["value"])
        self._record("US0005", "approve")        # a later review, outside the window
        self._assert_valid(rid)                  # the positive control

        self._replace(self.root / self.LEDGER,
                      "| US0001 | REJECT | a seat | author | 2026-09-20 | - | - | - |\n", "")
        rc, out = self._check(rid)
        self.assertEqual(1, rc, out)
        self.assertIn("INVALID", out)
        self.assertIn("unit_rounds[0]: signed 2, now 1", out)

    def test_rows_before_the_run_s_own_review_base_are_not_its_rounds(self) -> None:
        """BG0787 round 2 (F1). MUTANTS: fall back to the date alone for a unit the run never
        reviewed - an earlier same-day run's two REJECTs on carried US0005 count as this run's;
        ignore the run's own review base - US0002's earlier-run REJECT counts as a second round.
        A run from before review bases keeps the date alone."""
        day = self._run_ending_now()
        row = "| {} | {} | a seat | author | %s | - | - | - |\n" % day
        earlier = (row.format("US0005", "REJECT") * 2) + row.format("US0002", "REJECT")
        ledger = self.root / self.LEDGER
        head, sep, tail = ledger.read_text(encoding="utf-8").partition("| US0001 | REJECT")
        ledger.write_text(head + earlier + sep + tail, encoding="utf-8")
        live = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(live.read_text(encoding="utf-8"))
        state[sr.run_state.REVIEW_BASE] = {"US0001": 0, "US0002": 1}
        live.write_text(json.dumps(state), encoding="utf-8")
        got = self._rounds(sr.build_report(self.root, lean.RETRO))
        self.assertEqual({"US0001": 2, "US0002": 1, "US0005": 0},
                         {u: got[u] for u in ("US0001", "US0002", "US0005")})

        state.pop(sr.run_state.REVIEW_BASE)      # a run from before review bases
        live.write_text(json.dumps(state), encoding="utf-8")
        got = self._rounds(sr.build_report(self.root, lean.RETRO))
        self.assertEqual({"US0001": 2, "US0002": 2, "US0005": 2},
                         {u: got[u] for u in ("US0001", "US0002", "US0005")})

    def test_the_earliest_later_run_bounds_a_unit(self) -> None:
        """MUTANT: take any later run's base rather than the fewest rows - two later runs that
        reviewed US0001 at 3 and at 1 must bound it at 1."""
        for rid, base, hour in (("RUN-01LATER1", 3, 20), ("RUN-01LATER2", 1, 21)):
            sr.run_state.archive(self.root, {
                "run_id": rid, "started_at": f"2026-09-20T{hour}:00:00Z",
                sr.run_state.REVIEW_BASE: {"US0001": base}})
        state = json.loads((self.root / "sdlc-studio" / ".local" / "run-state.json")
                           .read_text(encoding="utf-8"))
        self.assertEqual({"US0001": 1}, sr._later_review_bases(self.root, state))  # noqa: SLF001


if __name__ == "__main__":
    unittest.main()
