"""US0959: a signed sprint report checks in any full clone, from a sealed run record tracked
beside it.

The run is closed by the real `sprint close` and sealed by the real `sprint sign` (only the
terminal transitions are stubbed), committed, and then checked through `sprint_report.py check`
in the signing clone, in a full clone with no `.local`, and in a depth-1 clone. `gh` is a stub
that answers nothing, so no clone reads the live forge.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
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
#: Paths a real record carries: a plan outside the repository, a session transcript outside it,
#: and one written inside the repository.
PLAN = "/home/someone/.claude/plans/a-plan.md"
TRANSCRIPT = "/home/someone/.claude/projects/-home-someone-repo/0f1e2d3c.jsonl"
#: A session that wrote one reading and no closing one: the cost section names it on the page.
UNCOVERED = "/home/someone/.claude/projects/-home-someone-repo/9a8b7c6d.jsonl"
ABSOLUTE = re.compile(r"^(/|[A-Za-z]:[\\/])")


def _strings(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)
    elif isinstance(value, str):
        yield value


class TrackedRunRecordTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        stub = base / "bin"
        stub.mkdir()
        (stub / "gh").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (stub / "gh").chmod(0o755)
        (base / "transcripts").mkdir()
        self.env = gitutil.git_env(PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}",
                                   SDLC_STUDIO_TRANSCRIPTS=str(base / "transcripts"))
        patch = unittest.mock.patch.dict(os.environ, self.env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.root = base / "signer"
        self.root.mkdir()

    # --- the fixture ------------------------------------------------------------------------

    def _git(self, *argv: str, cwd: Path | None = None, later: bool = False):
        extra = {"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER} if later else {}
        return gitutil.git(list(argv), cwd or self.root, env_extra=extra, text=True)

    def _commit(self, message: str) -> str:
        """Commit everything, dated after the run's window so no commit moves a figure."""
        self._git("add", "-A")
        self._git("commit", "-q", "--allow-empty", "-m", message, later=True)
        return self._git("rev-parse", "HEAD").stdout.strip()

    def _seal(self) -> str:
        """A run closed and signed through the shipped entry points, and committed. Returns
        the seal commit."""
        inside = str(self.root / "sdlc-studio" / "notes" / "handover.md")
        lean._fixture(self.root, plan=PLAN, handover_note=inside,
                      session_token_stamps=[
                          {"tokens": 1000, "source": TRANSCRIPT, "at": "2026-09-23T00:00:00Z",
                           "kind": "open", "model": "m"},
                          {"tokens": 5000, "source": TRANSCRIPT, "at": "2026-09-23T01:00:00Z",
                           "kind": "report", "model": "m"},
                          {"tokens": 700, "source": UNCOVERED, "at": "2026-09-23T00:30:00Z",
                           "kind": "open", "model": "m"}],
                      unit_actuals={"US0101": {"started_at": "2026-09-23T00:10:00Z",
                                               "start_tokens": 1000, "start_source": TRANSCRIPT,
                                               "open": True}})
        signing._git_repo(self.root)
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self._commit("close paperwork")
        rc, _out, err = signing._sign(self.root, REPORT)
        self.assertEqual(0, rc, err)
        return self._commit("seal")

    def _tracked(self, root: Path | None = None) -> Path:
        return (root or self.root) / "sdlc-studio" / "reports" / "runs" / f"{RUN}.json"

    def _clone(self, name: str, *flags: str) -> Path:
        dest = Path(self.tmp.name) / name
        self._git("clone", "-q", *flags, f"file://{self.root}", str(dest),
                  cwd=Path(self.tmp.name))
        return dest

    @staticmethod
    def _check(root: Path, report: str = REPORT) -> tuple[int, str]:
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint_report.main(["--root", str(root), "check", "--report", report])
        return rc, out.getvalue() + err.getvalue()

    def _local_records(self) -> list[Path]:
        local = self.root / "sdlc-studio" / ".local"
        return [local / "run-state.json", local / "run-archive" / f"{RUN}.json"]

    # --- the criteria -----------------------------------------------------------------------

    def test_sign_files_a_portable_sealed_record(self) -> None:
        """AC1. Mutant: copy `.local/run-state.json` verbatim, which commits the home directory
        and the session transcript ids; or write no record at all."""
        self._seal()
        path = self._tracked()
        self.assertTrue(path.is_file(), "sign filed no tracked run record")
        record = json.loads(path.read_text(encoding="utf-8"))
        live = json.loads(self._local_records()[0].read_text(encoding="utf-8"))
        self.assertEqual(live["signature"], record.get("signature"))
        self.assertEqual("goal-reached", record.get("outcome"))
        self.assertEqual(live["ended_at"], record.get("ended_at"))
        self.assertTrue(record.get("ended_at"))
        leaked = [s for s in _strings(record) if ABSOLUTE.match(s)]
        self.assertEqual([], leaked, "the tracked record carries absolute paths")
        # One projection: inside the repository reads repo-relative, outside reads as a digest
        # that still groups a session's stamps together.
        self.assertEqual("sdlc-studio/notes/handover.md", record["handover_note"])
        self.assertRegex(record["plan"], r"^sha256:[0-9a-f]{12}$")
        sources = [s["source"] for s in record["session_token_stamps"]]
        self.assertEqual(2, len(set(sources)), sources)
        self.assertEqual(sources[0], sources[1])
        self.assertEqual(sources[0], record["unit_actuals"]["US0101"]["start_source"])
        for session_id in ("0f1e2d3c", "9a8b7c6d"):
            self.assertNotIn(session_id, path.read_text(encoding="utf-8"))
        # The seal commit carries it.
        self.assertIn(f"sdlc-studio/reports/runs/{RUN}.json",
                      self._git("ls-files").stdout.splitlines())

    def test_a_clean_clone_checks_the_signed_report(self) -> None:
        """AC2. Mutant: `_run_state_for` looking only in `.local`, which exits 2 'no run record
        names RUN-...' in any clone but the one that signed."""
        self._seal()
        rc, out = self._check(self.root)
        self.assertEqual(0, rc, out)                      # the positive control
        clone = self._clone("clean")
        self.assertFalse((clone / "sdlc-studio" / ".local").exists())
        rc, out = self._check(clone)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {REPORT}", out)

    def test_the_signature_is_read_from_tracked_history(self) -> None:
        """AC3. Mutants: read the signature from `.local` (stripped or re-pointed there, the
        report reads INVALID); read it from the tracked record's working copy or its newest
        commit (a re-pointed signature certifies itself, or is judged without naming the version
        first committed with it)."""
        seal = self._seal()
        signed = {p: p.read_text(encoding="utf-8") for p in self._local_records()}
        for how in ("stripped", "re-pointed"):
            for p in self._local_records():
                rec = json.loads(signed[p])
                if how == "stripped":
                    rec.pop("signature", None)
                else:
                    rec["signature"] = {**rec["signature"], "fingerprint": "0123456789abcdef"}
                p.write_text(json.dumps(rec), encoding="utf-8")
            rc, out = self._check(self.root)
            self.assertEqual(0, rc, f".local signature {how}: {out}")
        # The tracked record re-pointed in a later commit, with no reopen recorded.
        path = self._tracked()
        rec = json.loads(path.read_text(encoding="utf-8"))
        rec["signature"] = {**rec["signature"], "fingerprint": "0123456789abcdef"}
        path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        rc, out = self._check(self.root)
        self.assertEqual(1, rc, f"an uncommitted re-point certified itself: {out}")
        self._commit("re-point the signature")
        rc, out = self._check(self.root)
        self.assertEqual(1, rc, out)
        self.assertIn("0123456789abcdef", out)
        self.assertIn(seal[:10], out, "the re-point is not named against the version first "
                                      "committed with the signature")
        self.assertIn("no reopen", out)

    def test_a_reopened_and_resigned_run_checks_valid(self) -> None:
        """AC4. Mutant: anchor the first committed signature unconditionally, which reads every
        legitimate re-seal as forged."""
        self._seal()
        rc, out, err = signing._run(self.root, "reopen", "--reason", "a late review landed")
        self.assertEqual(0, rc, err)
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        refiled = lean._read(self.root)["report"]
        self._commit("close paperwork again")
        rc, _out, err = signing._sign(self.root, refiled)
        self.assertEqual(0, rc, err)
        self._commit("seal again")
        history = self._git("log", "--format=%H", "--", str(self._tracked())).stdout.split()
        self.assertEqual(2, len(history), "the re-seal did not commit a second signature")
        rc, out = self._check(self.root, refiled)
        self.assertEqual(0, rc, out)
        rc, out = self._check(self._clone("clean"), refiled)
        self.assertEqual(0, rc, out)

    def test_a_stripped_signature_with_a_fake_reopen_is_named(self) -> None:
        """Round-1 finding 2. Mutants: accept a later version whose signature is gone once its
        `reopened` list grows, or accept a re-signature from the working copy. Either way the
        signature is lost, nothing anchors the page, and a page re-derived from a moved tree
        and re-filed under the old signature reads VALID."""
        import sprint_report as sr  # noqa: PLC0415
        self._seal()
        # The forgery: a figure the page replays from its signed version is moved and the page
        # re-derived over it, keeping the signature block.
        story = self.root / "sdlc-studio" / "stories" / "US0101-widget.md"
        text = story.read_text(encoding="utf-8")
        self.assertEqual(1, text.count("> **Points:** 3"))
        story.write_text(text.replace("> **Points:** 3", "> **Points:** 8"), encoding="utf-8")
        page = sr.read_report(self.root, REPORT)
        forged = sr.build_report(self.root, page["retro_id"], as_of=page["generated_at"],
                                 window_end=page["window_end"], run_id=RUN)
        sr.write_report(self.root, {**forged, "report_id": REPORT,
                                    "signature": page["signature"]})
        rc, out = self._check(self.root)
        self.assertEqual(1, rc, f"the positive control: the anchor names the forgery: {out}")
        path = self._tracked()
        signed = path.read_text(encoding="utf-8")
        fake_reopen = {"at": "2099-01-01T00:00:00Z", "run_id": RUN, "reason": "fake"}
        # A re-signature, reopen and all, that only the working copy carries is not accepted.
        rec = json.loads(signed)
        rec["signature"] = {**rec["signature"], "fingerprint": forged["fingerprint"]}
        rec["reopened"] = [*(rec.get("reopened") or []), fake_reopen]
        path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        rc, out = self._check(self.root)
        self.assertEqual(1, rc, out)
        self.assertIn("a signature changes only in a commit", out)
        rec = json.loads(signed)
        rec.pop("signature")
        rec["reopened"] = [*(rec.get("reopened") or []), fake_reopen]
        path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        rc, out = self._check(self.root)
        self.assertEqual(1, rc, f"a stripped working copy with a fake reopen passed: {out}")
        self.assertIn("carries no signature", out)
        self._commit("strip the signature and fake a reopen")
        rc, out = self._check(self.root)
        self.assertEqual(1, rc, f"a committed strip with a fake reopen passed: {out}")
        self.assertIn("carries no signature", out)

    def test_a_page_checks_as_it_was_derived_before_and_after_records_were_tracked(self) -> None:
        """Round-1 finding 1. A page derived before US0959 names an uncovered session by its
        path; one derived after names it as the tracked record does. Each re-derives in its own
        shape, from the live record and from the archive. Mutants: read every record through
        the projection (a page signed before US0959 reads INVALIDATED on `token_coverage`), or
        none (a page derived since cannot match its tracked record)."""
        import sprint  # noqa: PLC0415
        import sprint_report as sr  # noqa: PLC0415
        lean._fixture(self.root, session_token_stamps=[
            {"tokens": 1000, "source": TRANSCRIPT, "at": "2026-09-23T00:00:00Z", "kind": "open"},
            {"tokens": 5000, "source": TRANSCRIPT, "at": "2026-09-23T01:00:00Z",
             "kind": "report"},
            {"tokens": 700, "source": UNCOVERED, "at": "2026-09-23T00:30:00Z", "kind": "open"}])
        signing._git_repo(self.root)
        live = self._local_records()[0]
        record = live.read_text(encoding="utf-8")
        for portable, named in ((False, UNCOVERED), (True, "sha256:")):
            with self.subTest(portable=portable):
                live.write_text(record, encoding="utf-8")
                page = sr.build_report(self.root, "RETRO0001", portable=portable)
                self.assertEqual(portable, sr.PORTABLE_PATHS in page)
                cost = {s["key"]: s for s in page["sections"]}["cost"]
                self.assertIn(named, cost["figures"]["token_coverage"]["value"])
                rid = sr.file_report(self.root, page)
                with contextlib.redirect_stdout(io.StringIO()):
                    sprint._write_the_signature(self.root, rid, "Maya Okafor")
                self._commit(f"sign {rid}")
                rc, out = self._check(self.root, rid)
                self.assertEqual(0, rc, out)
                # The next run opens: this one is read from the archive.
                archive = self._local_records()[1]
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_text(live.read_text(encoding="utf-8"), encoding="utf-8")
                live.unlink()
                rc, out = self._check(self.root, rid)
                self.assertEqual(0, rc, out)
                archive.unlink()

    def test_a_shallow_clone_cannot_judge_and_says_so(self) -> None:
        """AC5. Mutant: re-derive in a depth-1 clone, which reads the run's window with none of
        its commits and calls the signed page INVALIDATED."""
        self._seal()
        shallow = self._clone("shallow", "--depth", "1")
        self.assertEqual("true", self._git("rev-parse", "--is-shallow-repository",
                                           cwd=shallow).stdout.strip())
        self.assertTrue(self._tracked(shallow).is_file())
        rc, out = self._check(shallow)
        self.assertEqual(2, rc, out)
        self.assertIn("shallow", out)
        self.assertNotIn("INVALID", out)
        # The positive control: the same history, full, judges.
        rc, out = self._check(self._clone("full"))
        self.assertEqual(0, rc, out)


if __name__ == "__main__":
    unittest.main()
