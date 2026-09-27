"""BG0795: the sprint report's CI runs are read fresh at PREPARE and frozen on the run record.

The close and the seal are the real `sprint close` and `sprint sign` (only the chain's steps and
the terminal transitions are stubbed). `gh` is a stub on PATH whose answer each test sets, so no
test reaches the live forge, and a test can change the forge's answer after the page is signed.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - the stubbed seal, shared

SCRIPTS = Path(__file__).resolve().parent.parent
REPORT = "RPT0001"
LATER = "2099-01-01T00:00:00Z"
CACHE = Path("sdlc-studio") / ".local" / "ci-runs.json"


def _run(rid: int, at: str, conclusion: str = "success") -> dict:
    """One `gh run list --json` row: a push-triggered run on main."""
    return {"databaseId": rid, "event": "push", "conclusion": conclusion, "headBranch": "main",
            "headSha": f"{rid:07d}", "workflowName": "Lint", "createdAt": at,
            "updatedAt": at}


#: The lean fixture's run opens 2026-09-23T00:00:00Z and is closed now, so both are inside it.
INSIDE = _run(4242, "2026-09-23T00:30:00Z")
#: The per-clone cache as RPT0010's clone held it: written before the run opened.
STALE = [_run(1111, "2026-09-17T07:58:50Z")]
#: A different forge answer, given after the page is signed: a red run and a green one.
MOVED = [_run(5151, "2026-09-23T00:40:00Z", "failure"), _run(5252, "2026-09-23T00:50:00Z")]


class FrozenCiRunsTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.bin = base / "bin"
        self.bin.mkdir()
        (base / "transcripts").mkdir()
        self._forge([])
        env = gitutil.git_env(PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(base / "transcripts"))
        patch = unittest.mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.root = base / "signer"
        self.root.mkdir()

    # --- the fixture ------------------------------------------------------------------------

    def _forge(self, rows: list[dict]) -> None:
        """What the stub `gh run list` answers from now on."""
        gh = self.bin / "gh"
        gh.write_text(f"#!/bin/sh\ncat <<'EOF'\n{json.dumps(rows)}\nEOF\n", encoding="utf-8")
        gh.chmod(0o755)

    def _git(self, *argv: str, cwd: Path | None = None):
        return gitutil.git(list(argv), cwd or self.root, text=True,
                           env_extra={"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER})

    def _commit(self, message: str) -> None:
        """Commit everything, dated after the run's window so no commit moves a figure."""
        self._git("add", "-A")
        self._git("commit", "-q", "--allow-empty", "-m", message)

    def _close(self) -> dict:
        lean._fixture(self.root)
        signing._git_repo(self.root)
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        return lean._read(self.root)

    @staticmethod
    def _dora(page: dict) -> dict:
        rows = next(s for s in page["sections"] if s["key"] == "dora")["rows"]
        return {r["dora_key"]["value"]: r["dora_value"]["value"] for r in rows}

    @staticmethod
    def _check(root: Path) -> tuple[int, str]:
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint_report.main(["--root", str(root), "check", "--report", REPORT])
        return rc, out.getvalue() + err.getvalue()

    # --- the criteria -----------------------------------------------------------------------

    def test_the_close_reads_the_forge_not_a_stale_cache(self) -> None:
        """AC1. Mutant: HEAD's `_ci_runs`, which returns the cache whenever it exists - the
        page then reads no forge data and the record carries nothing."""
        import sprint_report as sr  # noqa: PLC0415
        cache = self.root / CACHE
        cache.parent.mkdir(parents=True)
        cache.write_text(json.dumps(STALE), encoding="utf-8")
        # The forge answers its history too: the run before the window is not the run's.
        self._forge([INSIDE, *STALE])
        state = self._close()
        frozen = state.get("ci_runs") or {}
        self.assertEqual([4242], [r.get("databaseId") for r in frozen.get("runs") or []],
                         f"the run record does not carry the window's forge runs: {frozen}")
        self.assertEqual("gh run list", frozen.get("source"))
        dora = self._dora(sr.read_report(self.root, state["report"]))
        self.assertEqual(1, dora["Deployment frequency"], dora)
        self.assertEqual("0%", dora["Change failure rate"], dora)
        self.assertEqual("no restore needed", dora["Time to restore"], dora)

    def test_a_signed_report_rederives_dora_from_its_record(self) -> None:
        """AC2. Mutant: re-derive DORA from a live `gh run list` - once the forge answers a
        different set, the signed page reads INVALIDATED in every clone."""
        import sprint_report as sr  # noqa: PLC0415
        self._forge([INSIDE])
        self._close()
        self._commit("close paperwork")
        rc, _out, err = signing._sign(self.root, REPORT)
        self.assertEqual(0, rc, err)
        self._commit("seal")
        # The positive control: the page is not empty of forge data, so a moved answer could
        # move it.
        self.assertEqual(1, self._dora(sr.read_report(self.root, REPORT))["Deployment frequency"])
        tracked = json.loads((self.root / "sdlc-studio" / "reports" / "runs" /
                              "RUN-LEAN0001.json").read_text(encoding="utf-8"))
        self.assertEqual([4242], [r["databaseId"] for r in tracked["ci_runs"]["runs"]],
                         "the sealed record the seal commit tracks carries no CI runs")
        self._forge(MOVED)
        rc, out = self._check(self.root)
        self.assertEqual(0, rc, out)
        clone = Path(self.tmp.name) / "clean"
        self._git("clone", "-q", f"file://{self.root}", str(clone), cwd=Path(self.tmp.name))
        self.assertFalse((clone / "sdlc-studio" / ".local").exists())
        rc, out = self._check(clone)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {REPORT}", out)

    def test_a_record_that_froze_no_runs_rederives_none(self) -> None:
        """The pages signed before runs were frozen (this repository's RPT0006-RPT0010) read
        none inside their windows, and their sealed records carry no `ci_runs`. Mutant: read
        the live forge for such a record - once the forge answers a run inside the window, the
        signed page reads INVALIDATED."""
        import sprint  # noqa: PLC0415
        import sprint_report as sr  # noqa: PLC0415
        lean._fixture(self.root, ended_at="2026-09-23T02:00:00Z", outcome="goal-reached")
        signing._git_repo(self.root)
        page = sr.build_report(self.root, "RETRO0001")
        self.assertNotIn("ci_runs", lean._read(self.root))
        rid = sr.file_report(self.root, page)
        self.assertEqual(REPORT, rid)
        with contextlib.redirect_stdout(io.StringIO()):
            sprint._write_the_signature(self.root, rid, "Maya Okafor")
        self._commit(f"sign {rid}")
        self._forge([INSIDE])
        rc, out = self._check(self.root)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {REPORT}", out)

    def test_no_per_clone_ci_cache_remains(self) -> None:
        """AC3. Mutant: keep the per-clone cache as a second source beside the record - its
        name in a script, or a preview that writes it."""
        import sprint_report as sr  # noqa: PLC0415
        named = sorted(str(p.relative_to(SCRIPTS)) for p in SCRIPTS.rglob("*.py")
                       if "tests" not in p.relative_to(SCRIPTS).parts
                       and "ci-runs.json" in p.read_text(encoding="utf-8"))
        self.assertEqual([], named, "a script still names the per-clone CI cache")
        # An unfrozen preview reads the forge live and leaves nothing behind in `.local`.
        lean._fixture(self.root)
        self._forge([INSIDE])
        page = sr.build_report(self.root, "RETRO0001")
        self.assertEqual(1, self._dora(page)["Deployment frequency"])
        self.assertFalse((self.root / CACHE).exists(), "the preview wrote a per-clone cache")


if __name__ == "__main__":
    unittest.main()
