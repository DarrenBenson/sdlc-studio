"""BG0993: whether a sprint run is open is committed, so every checkout sees it.

`sprint close` files the run's record beside the report, still running; `sprint plan --write`
refuses while any tracked record awaits its signature; `sprint sign` takes the run up from that
record in a clone that never held it; and a signed record blocks no plan anywhere. Driven
through the shipped `sprint` entry points across real clones, with only the terminal
transitions stubbed (the shared sign fixture). `gh` is a stub that answers nothing.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

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
        self.assertTrue(record.get("report_fingerprint"))
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
        rc, _out, err = signing._run(self.closer, "stop", "--reason", "abandoned", "--force")
        self.assertEqual(0, rc, err)
        self.assertNotEqual("running", self._record(self.closer)["outcome"])

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


if __name__ == "__main__":
    unittest.main()
