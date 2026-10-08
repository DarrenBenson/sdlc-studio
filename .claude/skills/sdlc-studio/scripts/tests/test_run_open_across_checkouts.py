"""BG0993: whether a sprint run is open is committed, so every checkout sees it.

`sprint close` files the run's record beside the report, still running; `sprint plan --write`
refuses while any tracked record awaits its signature; `sprint sign` takes the run up from that
record in a clone that never held it; and a signed record blocks no plan anywhere. Driven
through the shipped `sprint` entry points across real clones, with only the terminal
transitions stubbed (the shared sign fixture). `gh` is a stub that answers nothing.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - the stubbed seal, shared

RUN = "RUN-LEAN0001"
REPORT = "RPT0001"
LATER = "2099-01-01T00:00:00Z"
RECORD = f"sdlc-studio/reports/runs/{RUN}.json"


class RunOpenAcrossCheckoutsTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        stub = self.base / "bin"
        stub.mkdir()
        (stub / "gh").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (stub / "gh").chmod(0o755)
        (self.base / "transcripts").mkdir()
        env = gitutil.git_env(PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(self.base / "transcripts"))
        patch = unittest.mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.closer = self.base / "closer"
        self.closer.mkdir()

    # --- the fixture ------------------------------------------------------------------------

    def _git(self, root: Path, *argv: str) -> subprocess.CompletedProcess:
        return gitutil.git(list(argv), root, text=True,
                           env_extra={"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER})

    def _commit(self, root: Path, message: str) -> None:
        """Commit everything, dated after the run's window so no commit moves a figure."""
        self._git(root, "add", "-A")
        self._git(root, "commit", "-q", "--allow-empty", "-m", message)

    def _close(self) -> None:
        """A run closed through the shipped `sprint close` in one checkout, and its paperwork
        committed there."""
        lean._fixture(self.closer)
        signing._git_repo(self.closer)
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "close paperwork")

    def _clone(self, name: str, source: Path | None = None) -> Path:
        dest = self.base / name
        self._git(self.base, "clone", "-q", f"file://{source or self.closer}", str(dest))
        return dest

    def _pull(self, root: Path, source: Path) -> None:
        self._git(root, "fetch", "-q", f"file://{source}", "HEAD")
        self._git(root, "merge", "-q", "--ff-only", "FETCH_HEAD")

    @staticmethod
    def _plan(root: Path) -> tuple[int, str, str]:
        return signing._run(root, "plan", "--stories", "Ready", "--write", "--no-fetch")

    @staticmethod
    def _record(root: Path) -> dict:
        return json.loads((root / RECORD).read_text(encoding="utf-8"))

    @staticmethod
    def _live(root: Path) -> dict:
        p = root / "sdlc-studio" / ".local" / "run-state.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}

    # --- the criteria -----------------------------------------------------------------------

    def test_close_commits_an_awaiting_signature_record(self) -> None:
        """AC1. Mutant: the close files no record, so only `.local` says the run is open."""
        self._close()
        self.assertIn(RECORD, self._git(self.closer, "ls-files").stdout.splitlines(),
                      "the close filed no tracked run record beside the report")
        clone = self._clone("fresh")
        self.assertFalse((clone / "sdlc-studio" / ".local").exists())
        record = self._record(clone)
        self.assertEqual(RUN, record["run_id"])
        self.assertEqual("running", record["outcome"])
        self.assertEqual(REPORT, record["report"])
        filed = json.loads((clone / "sdlc-studio" / "reports" / f"{REPORT}.json")
                           .read_text(encoding="utf-8"))
        self.assertEqual(filed["fingerprint"], record.get("report_fingerprint"))
        self.assertTrue(record.get("close_tree"), "the record carries no tree to sign against")
        self.assertIsNone(record.get("signature"))

    def test_plan_refused_by_an_unsigned_committed_run(self) -> None:
        """AC2. Mutant: `plan --write` reads only this checkout's `.local`, so a fresh clone
        opens a second run beside the one awaiting its signature."""
        self._close()
        clone = self._clone("fresh")
        rc, _out, err = self._plan(clone)
        self.assertEqual(2, rc, err)
        self.assertIn(RUN, err)
        self.assertIn(REPORT, err)
        self.assertIn(f"sprint.py sign --report {REPORT}", err)
        self.assertEqual({}, self._live(clone), "a refused plan opened a run")
        # A stale local record of an older, sealed run (the second machine's shape) is refused
        # the same way.
        stale = clone / "sdlc-studio" / ".local" / "run-state.json"
        stale.parent.mkdir(parents=True)
        stale.write_text(json.dumps({"schema": 1, "run_id": "RUN-OLDER001",
                                     "outcome": "goal-reached", "batch": ["US0001"]}),
                         encoding="utf-8")
        rc, _out, err = self._plan(clone)
        self.assertEqual(2, rc, err)
        self.assertIn(RUN, err)
        self.assertEqual("RUN-OLDER001", self._live(clone)["run_id"])
        # The checkout that closed the run holds it open, so its refusal is the one-run
        # refusal it has always given, not this one.
        rc, _out, err = self._plan(self.closer)
        self.assertEqual(2, rc, err)
        self.assertIn(f"{RUN} is already open", err)

    def test_sign_from_a_fresh_clone(self) -> None:
        """AC3. Mutants: `sign` reads only `.local`, so a clone that never held the run cannot
        seal it; or the tree digest counts the run records, so the clone's tree never matches
        the one the close recorded."""
        self._close()
        clone = self._clone("fresh")
        rc, _out, err = signing._sign(clone, REPORT)
        self.assertEqual(0, rc, err)
        record = self._record(clone)
        self.assertEqual("goal-reached", record["outcome"])
        self.assertEqual(REPORT, record["signature"]["report"])
        self.assertTrue(record["signature"]["fingerprint"])
        # The tree check still holds in the clone: a file changed since the close is refused.
        other = self._clone("edited")
        (other / "src" / "widget.py").write_text("x = 2\n", encoding="utf-8")
        rc, _out, err = signing._sign(other, REPORT)
        self.assertEqual(2, rc, err)
        self.assertIn("since the close", err)
        self.assertEqual("running", self._record(other)["outcome"])

    def test_sign_from_a_clone_holding_an_older_sealed_run(self) -> None:
        """AC3, the observed shape. Mutant: refuse as 'already sealed' on the older run."""
        self._close()
        clone = self._clone("second-machine")
        local = clone / "sdlc-studio" / ".local"
        local.mkdir(parents=True)
        (local / "run-state.json").write_text(json.dumps(
            {"schema": 1, "run_id": "RUN-OLDER001", "outcome": "goal-reached",
             "batch": ["US0001"]}), encoding="utf-8")
        rc, _out, err = signing._sign(clone, REPORT)
        self.assertEqual(0, rc, err)
        self.assertEqual(RUN, self._live(clone)["run_id"])
        self.assertTrue((local / "run-archive" / "RUN-OLDER001.json").is_file(),
                        "the older run was overwritten, not archived")
        # A run still OPEN in that checkout is never discarded to take another up.
        third = self._clone("busy")
        (third / "sdlc-studio" / ".local").mkdir(parents=True)
        (third / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
            {"schema": 1, "run_id": "RUN-BUSY0001", "outcome": "running",
             "batch": ["US0002"]}), encoding="utf-8")
        rc, _out, err = signing._sign(third, REPORT)
        self.assertEqual(2, rc, err)
        self.assertIn("RUN-BUSY0001", err)
        self.assertEqual("RUN-BUSY0001", self._live(third)["run_id"])

    def test_signed_record_does_not_block(self) -> None:
        """AC4. Mutants: a signed record still counted as awaiting; or the checkout that closed
        the run, still holding it open in `.local`, refusing to plan after it was signed
        elsewhere."""
        self._close()
        signer = self._clone("signer")
        rc, _out, err = signing._sign(signer, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(signer, "seal")
        rc, _out, err = self._plan(self._clone("after", source=signer))
        self.assertEqual(0, rc, err)
        self.assertNotIn("awaits a signature", err)
        # The closing checkout: open in `.local`, signed in the record it pulls.
        self.assertEqual("running", self._live(self.closer)["outcome"])
        self._pull(self.closer, signer)
        rc, _out, err = self._plan(self.closer)
        self.assertEqual(0, rc, err)
        self.assertIn(f"{RUN} was signed in another checkout", err)
        self.assertNotEqual(RUN, self._live(self.closer)["run_id"], "no new run was opened")
        archived = self.closer / "sdlc-studio" / ".local" / "run-archive" / f"{RUN}.json"
        self.assertEqual("goal-reached", json.loads(archived.read_text())["outcome"])

    def test_a_run_ended_without_a_signature_stops_awaiting(self) -> None:
        """A run the close filed and then stopped awaits nothing. Mutant: `close_run` leaves
        the tracked record running, so every clone is refused a plan for good."""
        self._close()
        rc, out, err = signing._run(self.closer, "stop", "--reason", "abandoned", "--force")
        self.assertEqual(0, rc, err)
        self.assertNotEqual("running", self._record(self.closer)["outcome"])
        self.assertIn(f"stop: commit {RECORD}", out)

    def test_a_tree_recorded_with_the_run_records_still_signs(self) -> None:
        """A run closed before the digest left the records out recorded a tree holding them.
        Mutant: count paths under the records directory as changes since the close, so every
        run in flight at the upgrade is refused its signature."""
        self._close()
        old = self.closer / "sdlc-studio" / "reports" / "runs" / "RUN-OLDER001.json"
        old.write_text(json.dumps({"run_id": "RUN-OLDER001", "outcome": "goal-reached"}),
                       encoding="utf-8")
        self._commit(self.closer, "an older run's record")
        idx = self.base / "index"
        env = {"GIT_INDEX_FILE": str(idx)}
        for argv in (["read-tree", "HEAD"], ["add", "-A"],
                     ["rm", "--cached", "-r", "-q", "--ignore-unmatch", "sdlc-studio/.local"]):
            gitutil.git(argv, self.closer, env_extra=env, text=True)
        tree = gitutil.git(["write-tree"], self.closer, env_extra=env,
                           text=True).stdout.strip()
        state = self._live(self.closer)
        state["close_tree"] = tree
        (self.closer / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        rc, _out, err = signing._sign(self.closer, REPORT)
        self.assertEqual(0, rc, err)

    # --- round 2: a checkout's own newer state is never overwritten by its record ------------

    def test_a_reopen_here_is_never_discarded_by_plan(self) -> None:
        """Mutant: take up any sealed, signed record of the run held here, which reads a run
        signed here and then reopened here as signed elsewhere, discards the reopen and opens a
        new run."""
        self._close()
        rc, _out, err = signing._sign(self.closer, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "seal")
        rc, _out, err = signing._run(self.closer, "reopen", "--reason", "a late review landed")
        self.assertEqual(0, rc, err)
        rc, _out, err = self._plan(self.closer)
        self.assertEqual(2, rc, err)
        self.assertIn(f"{RUN} is already open", err)
        self.assertNotIn("signed in another checkout", err)
        live = self._live(self.closer)
        self.assertEqual(RUN, live["run_id"])
        self.assertEqual(1, len(live.get("reopened") or []), "the reopen was discarded")

    def test_a_reopen_here_is_never_sealed_over_by_sign(self) -> None:
        """Mutant: read a run held open with no report (a reopen cleared it) as one this
        checkout does not hold, take up the stale awaiting record and seal the broken page."""
        self._close()
        rc, _out, err = signing._run(self.closer, "reopen", "--reason", "the page is wrong")
        self.assertEqual(0, rc, err)
        rc, _out, err = signing._sign(self.closer, REPORT)
        self.assertEqual(2, rc, err)
        self.assertIn("is not this run's report", err)
        live = self._live(self.closer)
        self.assertEqual("running", live["outcome"])
        self.assertIsNone(live.get("report"))
        self.assertIsNone(live.get("signature"))
        self.assertEqual(1, len(live.get("reopened") or []), "the reopen was discarded")

    def test_a_refused_sign_in_a_fresh_clone_writes_nothing(self) -> None:
        """Mutant: take the record up before the checks, so a sign the tree check refuses has
        already replaced the clone's live state."""
        self._close()
        clone = self._clone("edited")
        (clone / "src" / "widget.py").write_text("x = 2\n", encoding="utf-8")
        rc, _out, err = signing._sign(clone, REPORT)
        self.assertEqual(2, rc, err)
        self.assertEqual({}, self._live(clone), "a refused sign wrote a live state")

    def _signed_elsewhere_then_pulled(self) -> dict:
        """The closing checkout, after another clone signed its run and it pulled the seal.
        Returns the signature the pulled record carries."""
        self._close()
        signer = self._clone("signer")
        rc, _out, err = signing._sign(signer, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(signer, "seal")
        self._pull(self.closer, signer)
        self.assertEqual("running", self._live(self.closer)["outcome"])
        return self._record(self.closer)["signature"]

    def _check_valid(self) -> None:
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = sprint_report.main(["--root", str(self.closer), "check", "--report", REPORT])
        self.assertEqual(0, rc, buf.getvalue())
        self.assertIn(f"VALID: {REPORT}", buf.getvalue())

    def test_a_reclose_never_strips_a_signature_made_elsewhere(self) -> None:
        """Mutants: the close never reads the tracked record, so re-running it (the remedy a
        refused sign prints) files a second page for a sealed run; or it files the awaiting
        record over the signed one, and the signed page reads INVALID."""
        signed = self._signed_elsewhere_then_pulled()
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(2, rc, err)
        self.assertIn("signed in another checkout", err)
        self.assertEqual(signed, self._record(self.closer)["signature"])
        self.assertEqual("goal-reached", self._live(self.closer)["outcome"])
        self.assertEqual([], list((self.closer / "sdlc-studio" / "reports").glob("RPT0002*")))
        self._check_valid()

    def test_a_sign_in_the_closing_checkout_takes_up_a_signature_made_elsewhere(self) -> None:
        """Mutant: `sign` never reads the tracked record, so the closing checkout is refused
        over the files the seal commit changed and told to re-run the close."""
        signed = self._signed_elsewhere_then_pulled()
        rc, _out, err = signing._sign(self.closer, REPORT)
        self.assertEqual(2, rc, err)
        self.assertIn("signed in another checkout", err)
        self.assertIn("already sealed", err)
        self.assertNotIn("Re-run the close", err)
        self.assertEqual(signed, self._live(self.closer)["signature"])
        self._check_valid()

    def test_the_close_never_files_over_a_signed_record(self) -> None:
        """Mutant: `_file_awaiting_record` writes without reading the record already there.
        Driven directly, because the close refuses this state before it reaches the filing."""
        self._close()
        record = self._record(self.closer)
        record.update(outcome="goal-reached", signature={"principal": "elsewhere",
                                                         "report": REPORT,
                                                         "fingerprint": "f" * 16})
        (self.closer / RECORD).write_text(json.dumps(record), encoding="utf-8")
        before = (self.closer / RECORD).read_bytes()
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            signing.sprint._file_awaiting_record(self.closer)
        self.assertEqual(before, (self.closer / RECORD).read_bytes())
        self.assertIn("is sealed and no reopen here supersedes it", err.getvalue())

    def test_an_unreadable_record_refuses_the_plan(self) -> None:
        """Mutant: skip a record that does not parse, which reads a possibly open run as
        absent."""
        self._close()
        clone = self._clone("damaged")
        (clone / RECORD).write_text("{not json", encoding="utf-8")
        rc, _out, err = self._plan(clone)
        self.assertEqual(2, rc, err)
        self.assertIn(RECORD.rsplit("/", 1)[-1], err)

    def test_sign_takes_up_only_the_named_report(self) -> None:
        """Mutant: ignore `--report` when choosing the record to take up, so two runs awaiting
        a signature leave nothing to choose and the named one cannot be signed."""
        self._close()
        other = dict(self._record(self.closer), run_id="RUN-OTHER0001", report="RPT0099")
        (self.closer / "sdlc-studio" / "reports" / "runs" / "RUN-OTHER0001.json").write_text(
            json.dumps(other), encoding="utf-8")
        self._commit(self.closer, "a second run awaiting its signature")
        clone = self._clone("fresh")
        rc, _out, err = signing._sign(clone, REPORT)
        self.assertEqual(0, rc, err)
        self.assertEqual(RUN, self._live(clone)["run_id"])
        self.assertEqual("goal-reached", self._record(clone)["outcome"])
        other_now = json.loads((clone / "sdlc-studio" / "reports" / "runs" /
                                "RUN-OTHER0001.json").read_text(encoding="utf-8"))
        self.assertEqual("running", other_now["outcome"])

    # --- round 3: a reopen meeting a signature made in another checkout ---------------------

    def _report_ids(self, root: Path) -> list[str]:
        return sorted(p.stem for p in (root / "sdlc-studio" / "reports").glob("RPT*.json"))

    def test_a_reopen_before_pulling_a_signature_never_strips_it(self) -> None:
        """Mutant: the close guards a signed record by reopen counts alone and files the live
        copy as it stands, so a reopen of the UNSIGNED copy made before the signature was
        pulled files an unsigned record over the signed one, and the signed page reads INVALID
        in every clone."""
        self._close()
        signer = self._clone("signer")
        rc, _out, err = signing._sign(signer, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(signer, "seal")
        signed = self._record(signer)["signature"]
        rc, _out, err = signing._run(self.closer, "reopen", "--reason", "one more change")
        self.assertEqual(0, rc, err)
        self._pull(self.closer, signer)
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "re-close after the pull")
        record = self._record(self.closer)
        self.assertEqual(signed, record.get("signature"), "the signature was stripped")
        self.assertEqual("running", record["outcome"])
        # The reopen overtook the signed page, so it reads INVALIDATED, as it does after any
        # reopen; it is never INVALID, which is the verdict on a stripped signature.
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            sprint_report.main(["--root", str(self.closer), "check", "--report", REPORT])
        self.assertTrue(buf.getvalue().startswith(f"INVALIDATED: {REPORT}"), buf.getvalue())
        self.assertNotIn("never removed", buf.getvalue())
        # Every clone still sees the run open, awaiting the re-closed page's signature.
        rc, _out, err = self._plan(self._clone("after"))
        self.assertEqual(2, rc, err)
        self.assertIn(f"awaits a signature on {record['report']}", err)

    def test_a_resignature_elsewhere_after_a_local_reopen_is_taken_up(self) -> None:
        """Mutant: `sealed_elsewhere` also requires this copy's own signature to equal the
        record's, which a copy that kept its first signature through a reopen never does, so
        the closing checkout's plan is refused for a signed run and its close files a third
        page."""
        self._close()
        rc, _out, err = signing._sign(self.closer, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "seal")
        rc, _out, err = signing._run(self.closer, "reopen", "--reason", "a late review landed")
        self.assertEqual(0, rc, err)
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "re-close")
        refiled = self._live(self.closer)["report"]
        signer = self._clone("signer")
        rc, _out, err = signing._sign(signer, refiled)
        self.assertEqual(0, rc, err)
        self._commit(signer, "re-seal")
        self._pull(self.closer, signer)
        before = self._report_ids(self.closer)
        rc, _out, err = self._plan(self.closer)
        self.assertEqual(0, rc, err)
        self.assertIn(f"{RUN} was signed in another checkout", err)
        self.assertEqual(before, self._report_ids(self.closer), "a page was filed")
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = sprint_report.main(["--root", str(self.closer), "check", "--report", refiled])
        self.assertEqual(0, rc, buf.getvalue())

    # --- round 4: a copy older than its record never files over it --------------------------

    def test_a_stale_copy_never_files_over_a_newer_record(self) -> None:
        """Mutant: the close compares reopen counts only against a SEALED record, so a closing
        checkout whose copy predates another clone's reopen and re-close files its older copy
        over the newer awaiting record, erasing that reopen, and the next signature of the
        re-closed page reads INVALID."""
        self._close()
        other = self._clone("other")
        rc, _out, err = signing._sign(other, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(other, "seal")
        rc, _out, err = signing._run(other, "reopen", "--reason", "a late review landed")
        self.assertEqual(0, rc, err)
        rc, _out, err = lean._close(other)
        self.assertEqual(0, rc, err)
        self._commit(other, "re-close")
        newer = self._record(other)
        self._pull(self.closer, other)
        self.assertEqual(0, len(self._live(self.closer).get("reopened") or []))
        before = self._report_ids(self.closer)
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(2, rc, err)
        self.assertIn("reopened and re-closed in another checkout", err)
        self.assertIn(f"sprint.py sign --report {newer['report']}", err)
        self.assertEqual(newer, self._record(self.closer), "the newer record was filed over")
        self.assertEqual(before, self._report_ids(self.closer), "a page was filed")
        # The stale checkout now holds the newer record, so it can sign the re-closed page.
        rc, _out, err = signing._sign(self.closer, newer["report"])
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "re-seal")
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = sprint_report.main(["--root", str(self._clone("checked")), "check", "--report",
                                     newer["report"]])
        self.assertEqual(0, rc, buf.getvalue())

    def test_a_repeated_reclose_refreshes_a_record_carrying_a_signature(self) -> None:
        """Mutant: the close leaves ANY signed record as it is when this copy records no more
        reopens, sealed or not, so a second re-close over a carried signature leaves the record
        stale, its tree no longer the close's, and no clone can sign the page."""
        self._close()
        signer = self._clone("signer")
        rc, _out, err = signing._sign(signer, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(signer, "seal")
        rc, _out, err = signing._run(self.closer, "reopen", "--reason", "one more change")
        self.assertEqual(0, rc, err)
        self._pull(self.closer, signer)
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "re-close")
        (self.closer / "src" / "widget.py").write_text("x = 3\n", encoding="utf-8")
        self._commit(self.closer, "a fix after the re-close")
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(0, rc, err)
        self._commit(self.closer, "close again")
        self.assertEqual(self._live(self.closer)["close_tree"],
                         self._record(self.closer)["close_tree"], "the record is stale")
        rc, _out, err = signing._sign(self._clone("fresh"), self._record(self.closer)["report"])
        self.assertEqual(0, rc, err)

    def test_the_close_never_files_over_a_record_with_more_reopens(self) -> None:
        """Mutant: `_file_awaiting_record` files over a running record that records more
        reopens than this copy. Driven directly, because the close refuses this state first."""
        self._close()
        record = self._record(self.closer)
        record["reopened"] = [{"at": "2099-01-01T00:00:00Z", "run_id": RUN,
                               "from_outcome": "goal-reached", "reason": "elsewhere"}]
        (self.closer / RECORD).write_text(json.dumps(record), encoding="utf-8")
        before = (self.closer / RECORD).read_bytes()
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            signing.sprint._file_awaiting_record(self.closer)
        self.assertEqual(before, (self.closer / RECORD).read_bytes())
        self.assertIn("records more reopens than this copy", err.getvalue())


if __name__ == "__main__":
    unittest.main()
