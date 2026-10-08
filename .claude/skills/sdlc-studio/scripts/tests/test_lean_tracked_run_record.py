"""US0959: a signed sprint report checks in any full clone, from a sealed run record tracked
beside it.

The run is closed by the real `sprint close` and sealed by the real `sprint sign` (only the
terminal transitions are stubbed), committed, and then checked through `sprint_report.py check`
in the signing clone, in a full clone with no `.local`, and in a depth-1 clone. `gh` is a stub
that answers nothing, so no clone reads the live forge.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
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
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - the stubbed seal, shared

#: This repository, and the reports it signed before run records were tracked, each at the
#: fingerprint its signature records.
REPO = Path(__file__).resolve().parents[5]
SIGNED = {"RPT0006": "601f7a5c68719c2f", "RPT0007": "898129ed43c8b31d",
          "RPT0008": "ed21330f92c071cb", "RPT0009": "a1b0bc85adaffbb3",
          "RPT0010": "08b6bb603f8fe5e7"}
RUN = "RUN-LEAN0001"
REPORT = "RPT0001"
LATER = "2099-01-01T00:00:00Z"
#: Paths a real record carries: a plan outside the repository, a session transcript outside it,
#: and one written inside the repository.
PLAN = "/home/someone/.claude/plans/a-plan.md"
TRANSCRIPT = "/home/someone/.claude/projects/-home-someone-repo/0f1e2d3c.jsonl"
#: A session that wrote one reading and no closing one: the cost section names it on the page.
UNCOVERED = "/home/someone/.claude/projects/-home-someone-repo/9a8b7c6d.jsonl"
#: A second such session, whose digest sorts before the first's though its path sorts after.
UNCOVERED_TOO = "/home/someone/.claude/projects/-home-someone-repo/aa11.jsonl"
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

    def _commit_in(self, root: Path, message: str) -> None:
        """Commit everything in `root`, dated after every run's window."""
        self._git("add", "-A", cwd=root)
        self._git("-c", "commit.gpgsign=false", "commit", "-q", "-m", message, cwd=root,
                  later=True)

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
        # The close commits the record too, awaiting its signature (BG0993), so count the
        # signatures the record's history carries rather than the commits that touched it.
        history = self._git("log", "--format=%H", "--", str(self._tracked())).stdout.split()
        rel = self._tracked().relative_to(self.root).as_posix()
        signed = {json.dumps(json.loads(self._git("show", f"{sha}:{rel}").stdout)
                             .get("signature"), sort_keys=True) for sha in history}
        signed.discard("null")
        self.assertEqual(2, len(signed), "the re-seal did not commit a second signature")
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

    GOAL = "the close finishes, in one pass"

    def _signed_before_records_were_tracked(self, marked: bool = False) -> str:
        """A run closed before records were tracked and signed after: its page names two
        uncovered sessions by the paths the tracked record holds only as digests, which sort
        the other way round. `marked` files the page with the portable mark it lacks. Returns
        the report id, committed."""
        import sprint  # noqa: PLC0415 - the seal's own signature writer
        import sprint_report as sr  # noqa: PLC0415
        from lib import run_state  # noqa: PLC0415
        lean._fixture(self.root, ended_at="2026-09-23T02:00:00Z", sprint_goal=self.GOAL,
                      session_token_stamps=[
                          {"tokens": 1000, "source": TRANSCRIPT, "at": "2026-09-23T00:00:00Z",
                           "kind": "open"},
                          {"tokens": 5000, "source": TRANSCRIPT, "at": "2026-09-23T01:00:00Z",
                           "kind": "report"},
                          {"tokens": 700, "source": UNCOVERED, "at": "2026-09-23T00:30:00Z",
                           "kind": "open"},
                          {"tokens": 900, "source": UNCOVERED_TOO, "at": "2026-09-23T00:40:00Z",
                           "kind": "open"}])
        signing._git_repo(self.root)
        page = sr.build_report(self.root, "RETRO0001", portable=False)   # the pre-6.0 close
        if marked:
            page[sr.PORTABLE_PATHS] = "portable"
        rid = sr.file_report(self.root, page)
        with contextlib.redirect_stdout(io.StringIO()):
            sprint._write_the_signature(self.root, rid, "Maya Okafor")
        run_state.file_tracked(self.root, run_state.read(self.root))     # the 6.0 seal
        self._commit(f"sign {rid}")
        return rid

    def test_a_page_derived_before_records_were_tracked_says_so_in_a_clean_clone(self) -> None:
        """US0960. The page names two uncovered sessions by path; the clean clone's tracked
        record holds them as digests, sorted the other way. The clone cannot judge it, says so
        and exits 2, and `render` still prints the page. Mutants: judge it anyway (INVALIDATED
        on `token_coverage`); compare the paths in order rather than as a multiset (the
        inverted digests read INVALIDATED); raise instead of returning the state (`render`
        exits 2 and prints nothing)."""
        import sprint_report as sr  # noqa: PLC0415
        rid = self._signed_before_records_were_tracked()
        page = sr.read_report(self.root, rid)
        coverage = next(s for s in page["sections"]
                        if s["key"] == "cost")["figures"]["token_coverage"]["value"]
        self.assertLess(coverage.index(UNCOVERED), coverage.index(UNCOVERED_TOO))
        digests = [sr.run_state.portable(p, self.root) for p in (UNCOVERED, UNCOVERED_TOO)]
        self.assertGreater(digests[0], digests[1], "premise: the digests sort the other way")
        rc, out = self._check(self.root, rid)
        self.assertEqual(0, rc, f"the positive control, from the live record: {out}")
        clone = self._clone("clean")
        rc, out = self._check(clone, rid)
        self.assertEqual(2, rc, out)
        self.assertIn(f"NOT JUDGED: {rid} predates tracked records", out)
        self.assertNotIn("INVALID", out)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(clone), "render", "--report", rid])
        self.assertEqual(0, rc, err.getvalue())
        self.assertIn(self.GOAL, out.getvalue())
        self.assertNotIn("INVALIDATED", out.getvalue())
        self.assertIn("predates tracked records", err.getvalue())
        line = sr.status_line(sr.report_status(clone))
        self.assertIn("not judged here", line)
        self.assertIn("predates tracked records", line)

    def test_only_a_projected_path_excuses_a_page_that_predates_tracked_records(self) -> None:
        """US0960 round 2. What the clean clone must still judge. Mutants: compare each figure's
        words as a sorted multiset (the goal's words reversed read NOT JUDGED); strip commas
        before comparing (the goal's comma removed reads NOT JUDGED); drop the `not edited`
        guard (a hand-edited page reads NOT JUDGED); drop the tracked-record guard (the same
        projected record read from the run archive reads NOT JUDGED)."""
        import sprint_report as sr  # noqa: PLC0415
        rid = self._signed_before_records_were_tracked()
        clone = self._clone("clean")
        record = self._tracked(clone)
        text = record.read_text(encoding="utf-8")
        self.assertEqual(1, text.count(f'"{self.GOAL}"'))
        reversed_goal = " ".join(reversed(self.GOAL.split()))
        for label, goal in (("the goal's words reversed", reversed_goal),
                            ("the goal's comma removed", self.GOAL.replace(",", ""))):
            with self.subTest(label):
                record.write_text(text.replace(f'"{self.GOAL}"', f'"{goal}"'), encoding="utf-8")
                rc, out = self._check(clone, rid)
                self.assertEqual(1, rc, out)
                self.assertIn("INVALIDATED", out)
                self.assertIn("sprint_goal", out)
        record.write_text(text, encoding="utf-8")
        with self.subTest("a hand-edited page"):
            path = clone / "sdlc-studio" / "reports" / f"{rid}.json"
            filed = path.read_text(encoding="utf-8")
            page = json.loads(filed)
            goal = next(s for s in page["sections"] if s["key"] == "goal")
            goal["figures"]["sprint_goal"]["value"] = "a goal edited by hand"
            sr.write_report(clone, page)
            rc, out = self._check(clone, rid)
            self.assertEqual(1, rc, out)
            self.assertIn("INVALID: ", out)
            self.assertIn("sprint_goal", out)
            self._git("checkout", "-q", "--", ".", cwd=clone)
        with self.subTest("the projected record read from the run archive"):
            archive = clone / "sdlc-studio" / ".local" / "run-archive" / f"{RUN}.json"
            archive.parent.mkdir(parents=True)
            archive.write_text(text, encoding="utf-8")
            record.unlink()
            rc, out = self._check(clone, rid)
            self.assertEqual(1, rc, out)
            self.assertIn("INVALIDATED", out)
            self.assertIn("token_coverage", out)

    def test_the_projection_rule_reads_word_by_word(self) -> None:
        """US0960 round 2: `_moved_only_by_projection`, clause by clause. Mutants: a sorted word
        multiset; commas stripped; the non-path words unread; the paths compared in order; a
        path's trailing punctuation unread; whitespace collapsed; a figure with no path
        excused."""
        import sprint_report as sr  # noqa: PLC0415
        from lib import run_state  # noqa: PLC0415
        one, two = (run_state.portable(p, self.root) for p in (UNCOVERED, UNCOVERED_TOO))
        signed = f"2 session(s); NOT in this total: {UNCOVERED}, {UNCOVERED_TOO}"
        cases = {
            "each path projected, digests in their own order":
                (f"2 session(s); NOT in this total: {two}, {one}", True),
            "each path projected, in the signed order": (
                f"2 session(s); NOT in this total: {one}, {two}", True),
            "a word changed beside the paths": (
                f"3 session(s); NOT in this total: {two}, {one}", False),
            "the words reordered": (f"session(s); 2 NOT in this total: {two}, {one}", False),
            "a comma moved off a path": (f"2 session(s); NOT in this total: {two} {one},",
                                         False),
            "a semicolon dropped from a word": (f"2 session(s) NOT in this total: {two}, {one}",
                                            False),
            "whitespace changed": (f"2 session(s);  NOT in this total: {two}, {one}", False),
            "a path projected to another's digest": (
                f"2 session(s); NOT in this total: {one}, {one}", False),
            "a path left as it was": (
                f"2 session(s); NOT in this total: {UNCOVERED}, {two}", False),
        }
        for label, (current, excused) in cases.items():
            with self.subTest(label):
                self.assertIs(excused, sr._moved_only_by_projection(self.root, signed, current))
        self.assertFalse(sr._moved_only_by_projection(self.root, "a goal, reversed",
                                                      "reversed goal, a"))
        self.assertFalse(sr._moved_only_by_projection(self.root, 3, 4))

    def test_a_marked_page_is_judged_whatever_its_record(self) -> None:
        """US0960 round 2. A page carrying the portable mark was derived through the projection,
        so a figure naming a raw path cannot be excused by it. Mutant: drop the mark guard (the
        page reads NOT JUDGED)."""
        rid = self._signed_before_records_were_tracked(marked=True)
        rc, out = self._check(self._clone("clean"), rid)
        self.assertEqual(1, rc, out)
        self.assertIn("INVALIDATED", out)
        self.assertIn("token_coverage", out)

    @unittest.skipUnless((REPO / "sdlc-studio" / "reports" / "RPT0006.json").is_file(),
                         "names this repository's signed reports")
    def test_this_repos_signed_reports_check_in_a_clean_clone(self) -> None:
        """US0960 AC5, and US0941 AC5. RPT0006-RPT0010 were signed before run records were
        tracked; `migrate --apply` filed their records, and a full-history clone of HEAD with
        no `.local` checks each VALID at the fingerprint it was signed at, while the forge
        answers a failing push run inside every window.

        The clone takes this checkout's tracked records as they stand, committed on top of
        HEAD, so the commit that files them passes its own gate; a clone of a pushed HEAD
        already holds them. Mutants: the records not filed (`no run record names RUN-...`,
        exit 2); a depth-1 clone, as the `ci` job's default checkout is (exit 2, shallow); a
        `check` that asks the forge rather than the record (a failing push lands in the window
        and `dora_value` moves, exit 1). None of the five windows held a cached CI run, so this
        cannot tell a record that froze its runs from one that froze none: the fixture tests
        in test_migrate do that."""
        clone = Path(self.tmp.name) / "repo"
        self._git("clone", "-q", str(REPO), str(clone), cwd=Path(self.tmp.name))
        self.assertFalse((clone / "sdlc-studio" / ".local").exists())
        runs = Path("sdlc-studio") / "reports" / "runs"
        for record in sorted((REPO / runs).glob("*.json")):
            (clone / runs).mkdir(parents=True, exist_ok=True)
            (clone / runs / record.name).write_bytes(record.read_bytes())
        if self._git("status", "--porcelain", cwd=clone).stdout.strip():
            self._commit_in(clone, "the tracked run records as this checkout holds them")
        pages = {rid: json.loads((clone / "sdlc-studio" / "reports" / f"{rid}.json")
                                 .read_text(encoding="utf-8")) for rid in SIGNED}
        forge = []
        for n, page in enumerate(pages.values()):
            goal = next(s for s in page["sections"] if s["key"] == "goal")
            start = datetime.fromisoformat(goal["figures"]["started_at"]["value"]
                                           .replace("Z", "+00:00"))
            at = (start + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            forge.append({"databaseId": 7000 + n, "event": "push", "conclusion": "failure",
                          "headBranch": "main", "headSha": f"{n:07d}", "workflowName": "Lint",
                          "createdAt": at, "updatedAt": at})
        gh = Path(self.tmp.name) / "bin" / "gh"
        gh.write_text(f"#!/bin/sh\ncat <<'EOF'\n{json.dumps(forge)}\nEOF\n", encoding="utf-8")
        for rid, signed in SIGNED.items():
            with self.subTest(rid):
                self.assertEqual(signed, pages[rid]["fingerprint"])
                rc, out = self._check(clone, rid)
                self.assertEqual(0, rc, out)
                self.assertIn(f"VALID: {rid} re-derives to the fingerprint it records "
                              f"({signed})", out)


if __name__ == "__main__":
    unittest.main()
