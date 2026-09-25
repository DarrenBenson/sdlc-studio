"""US0878: `sprint sign` checks what it seals and records what actually happened.

Driven through `sprint.main`, the shipped entry point, in throwaway project trees. The seal's
own writes (terminal transitions, cascade) are stubbed where a test is about the checks around
them, so each test judges one thing.
"""
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
import loader  # noqa: E402

sprint = loader.load_script("sprint")
run_state = sprint.run_state


def _state(root: Path, **over) -> dict:
    state = {
        "schema": 1, "run_id": "RUN-LEAN0002", "started_at": "2026-09-23T00:00:00Z",
        "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0101"],
        "handoff": None, "report": "RPT0001", "sprint_goal": "sign checks the tree",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"},
    }
    state.update(over)
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")
    return state


def _read(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())


def _run(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


@contextlib.contextmanager
def _seal_stubbed():
    """The terminal transitions stubbed green: these tests judge the checks and the outcome."""
    with unittest.mock.patch.object(sprint, "_principal_refusals", lambda *a, **k: []), \
            unittest.mock.patch.object(sprint, "_seal_units", lambda *a, **k: 0), \
            unittest.mock.patch.object(sprint, "_cascade_after_signature", lambda *a, **k: None):
        yield


def _sign(root: Path, report: str = "RPT0001") -> tuple[int, str, str]:
    with _seal_stubbed():
        return _run(root, "sign", "--report", report, "--principal", "Darren")


class SignChecksTests(unittest.TestCase):

    def test_sign_refuses_a_report_that_is_not_the_runs(self) -> None:
        """Mutant: sign whichever report is named."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _state(root, report="RPT0001")
            rc, _out, err = _sign(root, report="RPT0002")
            self.assertEqual(2, rc)
            self.assertIn("RPT0001", err)
            self.assertIn("RPT0002", err)
            self.assertEqual("running", _read(root)["outcome"])
            self.assertIsNone(_read(root).get("signature"))

    def test_sign_refuses_a_tree_changed_since_close(self) -> None:
        """Mutant: never compare the tree, or compare it and sign anyway."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = gitutil.git_env()
            (root / "src").mkdir()
            (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
            (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
            for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
                subprocess.run(["git", "-C", str(root), *argv], env=env, check=True,
                               capture_output=True)
            with unittest.mock.patch.dict(os.environ, env, clear=True):
                _state(root, close_tree=sprint.tree_digest(root))   # as the close left it
                (root / "src" / "widget.py").write_text("x = 2\n", encoding="utf-8")
                rc, _out, err = _sign(root)
                self.assertEqual(2, rc, err)
                self.assertIn("src/widget.py", err)
                self.assertEqual("running", _read(root)["outcome"])
                # the positive control: the tree back as the close left it signs
                (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
                rc, _out, err = _sign(root)
            self.assertEqual(0, rc, err)
            self.assertEqual("goal-reached", _read(root)["outcome"])

    def test_a_resumed_sign_is_not_refused_over_its_own_writes(self) -> None:
        """Mutant: drop the re-record after the seal's writes, so a sign that failed part-way is
        refused on its next attempt over the files it wrote itself."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = gitutil.git_env()
            story = root / "sdlc-studio" / "stories" / "US0101-widget.md"
            story.parent.mkdir(parents=True)
            story.write_text("# US0101: widget\n\n> **Status:** Review\n", encoding="utf-8")
            (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
            for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
                subprocess.run(["git", "-C", str(root), *argv], env=env, check=True,
                               capture_output=True)

            def half_seal(*_a, **_k):
                story.write_text(story.read_text().replace("Review", "Done"), encoding="utf-8")
                return 1                                  # wrote, then stopped part-way

            with unittest.mock.patch.dict(os.environ, env, clear=True):
                _state(root, close_tree=sprint.tree_digest(root))
                with unittest.mock.patch.object(sprint, "_principal_refusals",
                                                lambda *a, **k: []), \
                        unittest.mock.patch.object(sprint, "_seal_units", half_seal):
                    rc, _out, _err = _run(root, "sign", "--report", "RPT0001",
                                          "--principal", "Darren")
                self.assertEqual(1, rc)
                rc, _out, err = _sign(root)               # the resumed sign
            self.assertEqual(0, rc, err)


class OutcomeTests(unittest.TestCase):

    def test_a_signed_partial_run_is_not_labelled_stopped(self) -> None:
        """Mutant: every verdict but `achieved` recorded as `stopped`."""
        for verdict in ("partial", "missed"):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _state(root, sprint_goal_verdict={"verdict": verdict, "note": "short"})
                rc, _out, err = _sign(root)
                self.assertEqual(0, rc, err)
                self.assertEqual(verdict, _read(root)["outcome"])
                archived = json.loads((root / "sdlc-studio" / ".local" / "run-archive"
                                       / "RUN-LEAN0002.json").read_text())
                self.assertEqual(verdict, archived["outcome"])

    def test_a_plain_stop_records_the_operator_as_cause(self) -> None:
        """Mutant: a stop without --force recorded as `pending-decision` with nothing pending."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _state(root, batch=[], report=None, sprint_goal_verdict=None)
            rc, _out, err = _run(root, "stop", "--reason", "the operator called it")
            self.assertEqual(0, rc, err)
            stop = _read(root)["stop"]
            self.assertEqual("operator", stop["cause"])
            self.assertEqual(0, stop["pending"])


def _git_repo(root: Path) -> dict:
    """`root` as a committed git repository, `sdlc-studio/.local/` ignored; the env to use."""
    env = gitutil.git_env()
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run(["git", "-C", str(root), *argv], env=env, check=True, capture_output=True)
    return env


class SignTreeTests(unittest.TestCase):
    """The review's findings 1-3: what the tree check reads, and when it cannot read."""

    def test_an_edited_report_the_close_filed_is_refused(self) -> None:
        """Mutant: pass every path untracked NOW, so the report the close filed - uncommitted
        when sign runs - is never compared."""
        import test_lean_close as lean  # noqa: PLC0415 - the close fixture, shared
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)
            env = _git_repo(root)
            with unittest.mock.patch.dict(os.environ, env, clear=True):
                rc, _out, err = lean._close(root)
                self.assertEqual(0, rc, err)
                report = root / "sdlc-studio" / "reports" / "RPT0001.json"
                signed = report.read_bytes()
                report.write_bytes(signed.replace(b"the close finishes in one pass",
                                                  b"a goal nobody set", 1))
                self.assertNotEqual(signed, report.read_bytes(), "the edit did not apply")
                rc, _out, err = _sign(root)
                self.assertEqual(2, rc, err)
                self.assertIn("sdlc-studio/reports/RPT0001.json", err)
                self.assertEqual("running", _read(root)["outcome"])
                # the positive control: the report as the close filed it signs
                report.write_bytes(signed)
                rc, _out, err = _sign(root)
            self.assertEqual(0, rc, err)

    def test_a_file_added_after_the_close_and_left_untracked_is_not_counted(self) -> None:
        """Mutant: count every path the diff names, so a scratch file refuses the signature."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
            env = _git_repo(root)
            with unittest.mock.patch.dict(os.environ, env, clear=True):
                _state(root, close_tree=sprint.tree_digest(root))
                (root / "notes.txt").write_text("scratch\n", encoding="utf-8")
                rc, _out, err = _sign(root)
            self.assertEqual(0, rc, err)

    def test_a_recorded_tree_git_cannot_read_is_refused(self) -> None:
        """Mutant: an unreadable recorded tree reads as unchanged."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
            env = _git_repo(root)
            with unittest.mock.patch.dict(os.environ, env, clear=True):
                _state(root, close_tree="0" * 40)
                rc, _out, err = _sign(root)
            self.assertEqual(2, rc, err)
            self.assertIn("cannot be read", err)
            self.assertEqual("running", _read(root)["outcome"])

    def test_a_recorded_tree_with_no_git_to_compare_is_refused(self) -> None:
        """Mutant: warn and sign when a tree was recorded but git cannot read this one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)                                # not a git repository
            _state(root, close_tree="4b825dc642cb6eb9a060e54bf8d69288fbee4904")
            rc, _out, err = _sign(root)
            self.assertEqual(2, rc, err)
            self.assertIn("git cannot read", err)
            self.assertEqual("running", _read(root)["outcome"])
            # the control: no tree recorded at all signs on the report alone
            _state(root)
            rc, _out, err = _sign(root)
            self.assertEqual(0, rc, err)


class StopShipSignTests(unittest.TestCase):
    """D0257: the signer decides over a stop-ship ruling, and cannot miss one."""

    def test_sign_prints_every_stop_ship_issue_before_sealing(self) -> None:
        """Mutant: seal without printing, print after the seal line, or refuse the seal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _state(root, close_known_issues=[
                {"source": "review-coverage", "detail": "US0101 covered by no review"},
                {"source": "checklist", "stop_ship": True,
                 "detail": "BG0009 is ruled STOP-SHIP in the retro's carried-issues table"},
                {"source": "checklist", "stop_ship": True,
                 "detail": "BG0010 is ruled STOP-SHIP in the retro's carried-issues table"}])
            rc, out, err = _sign(root)
            self.assertEqual(0, rc, err)
            sealed = out.index("sealed RUN-LEAN0002")
            for fid in ("BG0009", "BG0010"):
                self.assertLess(out.index(fid), sealed, out)
            self.assertIn("STOP-SHIP", out[:sealed])
            self.assertNotIn("US0101", out, "a known issue that is not stop-ship is not repeated")
            self.assertEqual("goal-reached", _read(root)["outcome"])


class SealedReportStaysValidTests(unittest.TestCase):
    """Finding 5: a partial or missed run, once sealed, still re-derives to its fingerprint."""

    def test_a_sealed_partial_or_missed_report_still_checks_valid(self) -> None:
        """Mutant: judge a figure the seal moves (the outcome, the end time) into the digest."""
        import test_lean_close as lean  # noqa: PLC0415
        for verdict in ("partial", "missed"):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                lean._fixture(root, sprint_goal_verdict={"verdict": verdict, "note": "short"})
                env = _git_repo(root)
                with unittest.mock.patch.dict(os.environ, env, clear=True):
                    rc, _out, err = lean._close(root)
                    self.assertEqual(0, rc, err)
                    # the operator commits the close's paperwork, after the page was written
                    later = {**env, "GIT_COMMITTER_DATE": "2099-01-01T00:00:00Z"}
                    for argv in (["add", "-A"], ["commit", "-q", "-m", "close paperwork"]):
                        subprocess.run(["git", "-C", str(root), *argv], env=later, check=True,
                                       capture_output=True)
                    rc, _out, err = _sign(root)
                    self.assertEqual(0, rc, err)
                    self.assertEqual(verdict, _read(root)["outcome"])
                    import sprint_report  # noqa: PLC0415
                    check = sprint_report.revalidate(root, "RPT0001")
                self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
