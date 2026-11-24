"""BG1424: a bare `sprint close` scaffolds the run's retro before its slow pre-flight.

The close computed its whole owed-work pre-flight before it reached the retro scaffold; on a
large repository that took over ten minutes, and a first close killed at 600 s left nothing
scaffolded. The bare close now mints the retro (file, index row and the run's record of it)
first, so a close stopped during the pre-flight still leaves the scaffold on disk.

Driven through `sprint.py close` with no `--retro`, the shipped entry point, in a throwaway
workspace. Nothing reads this repository's own config, ledgers or `.local` state.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import os
import signal
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))
import gitutil  # noqa: E402
import sprint  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

#: A child that runs a bare close whose pre-flight announces itself and then hangs, standing in
#: for the many-minute pre-flight of a large repository; the test kills it there.
CHILD = """
import sys, time
sys.path.insert(0, sys.argv[1])
import sprint
def hang(*_a, **_k):
    print("PREFLIGHT STARTED", flush=True)
    time.sleep(120)
sprint._report_preflight = hang
sys.exit(sprint.main(["close", "--root", sys.argv[2]]))
"""


def _run(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = sprint.main(argv)
    return rc, buf.getvalue()


class ScaffoldFirstTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._env

    def _open_run(self, d: str, goal: str | None = "the widget ships") -> Path:
        root = Path(d)
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        (stories / "US0001-widget.md").write_text(
            "# US0001: widget\n\n> **Status:** Done\n> **Points:** 2\n> **Epic:** EP0001\n\n"
            "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
            encoding="utf-8")
        run_state.open_run(root, batch=["US0001"], goal="done")
        if goal:
            run_state.update(root, sprint_goal=goal)
        return root

    def _retros(self, root: Path) -> list[Path]:
        return sorted((root / "sdlc-studio" / "retros").glob("RETRO*.md"))

    def _index_names(self, root: Path, rid: str) -> bool:
        index = root / "sdlc-studio" / "retros" / "_index.md"
        return index.is_file() and rid in index.read_text(encoding="utf-8")

    def test_the_retro_is_on_disk_before_the_preflight_runs(self) -> None:
        """MUTANT: scaffold after the pre-flight, as before. The pre-flight is stopped where it
        starts, the way an operator's timeout stopped it; the scaffold is already there."""
        seen: dict = {}

        def stopped(root, *_a, **_k):
            retros = self._retros(Path(root))
            rid = sdlc_md.norm_id((run_state.read(root) or {}).get("scaffolded_retro") or "")
            seen.update(retros=retros, rid=rid, indexed=self._index_names(Path(root), rid))
            raise KeyboardInterrupt

        with tempfile.TemporaryDirectory() as d:
            root = self._open_run(d)
            with unittest.mock.patch.object(sprint, "_report_preflight", stopped), \
                    self.assertRaises(KeyboardInterrupt):
                _run(["close", "--root", str(root)])
            self.assertEqual(1, len(seen.get("retros") or []),
                             "no retro on disk when the pre-flight started")
            self.assertTrue(seen["rid"], "the run did not record its retro before the pre-flight")
            self.assertTrue(seen["indexed"], "the retro had no index row before the pre-flight")
            self.assertEqual(seen["retros"], self._retros(root))

    def test_a_killed_bare_close_leaves_its_scaffold_and_the_rerun_reuses_it(self) -> None:
        """The process itself is killed in its pre-flight: the retro, its index row and the
        run's record of it survive, and the next bare close reuses that one retro."""
        with tempfile.TemporaryDirectory() as d:
            root = self._open_run(d)
            env = gitutil.git_env(**{run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts"})
            child = subprocess.Popen(
                [sys.executable, "-c", CHILD, str(SCRIPTS), str(root)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
            try:
                lines = []
                for line in child.stdout:
                    lines.append(line)
                    if "PREFLIGHT STARTED" in line:
                        break
                self.assertIn("PREFLIGHT STARTED", "".join(lines), "".join(lines))
            finally:
                child.send_signal(signal.SIGKILL)
                child.wait(timeout=30)
                child.stdout.close()
            self.assertEqual(-signal.SIGKILL, child.returncode)
            retros = self._retros(root)
            self.assertEqual(1, len(retros), "no retro on disk after the killed close")
            rid = sdlc_md.norm_id((run_state.read(root) or {}).get("scaffolded_retro") or "")
            self.assertEqual(sdlc_md.norm_id(retros[0].stem.split("-")[0]), rid)
            self.assertTrue(self._index_names(root, rid))
            rc, out = _run(["close", "--root", str(root)])
            self.assertEqual(1, rc, out)
            self.assertIn(f"close: retro {rid} already scaffolded", out)
            self.assertEqual(retros, self._retros(root), "the re-run minted a second retro")

    def test_a_first_bare_close_still_reports_its_preflight_then_says_scaffolded(self) -> None:
        """The control: the bare close still runs its pre-flight and stops with the scaffold's
        own words, naming the retro as scaffolded rather than already scaffolded."""
        calls: list = []
        real = sprint._report_preflight

        def counted(*a, **k):
            calls.append(a)
            return real(*a, **k)

        with tempfile.TemporaryDirectory() as d:
            root = self._open_run(d)
            with unittest.mock.patch.object(sprint, "_report_preflight", counted):
                rc, out = _run(["close", "--root", str(root)])
            self.assertEqual(1, rc, out)
            self.assertEqual(1, len(calls), "the bare close skipped its pre-flight")
            (path,) = self._retros(root)
            rid = sdlc_md.norm_id((run_state.read(root) or {}).get("scaffolded_retro") or "")
            self.assertIn(f"close: retro {rid} scaffolded (indexed=True) -> {path}", out)
            self.assertIn(f"fill its sections, then re-run: sprint.py close --retro {rid}", out)
            self.assertNotIn("already scaffolded", out)

    def test_a_run_with_no_sprint_goal_is_refused_and_scaffolds_nothing(self) -> None:
        """The control: the sprint-goal refusal still comes before any retro is minted."""
        with tempfile.TemporaryDirectory() as d:
            root = self._open_run(d, goal=None)
            rc, out = _run(["close", "--root", str(root)])
            self.assertEqual(2, rc, out)
            self.assertIn("close refused: no sprint goal recorded on this run", out)
            self.assertEqual([], self._retros(root))
            self.assertFalse((run_state.read(root) or {}).get("scaffolded_retro"))

    def test_a_named_retro_is_not_scaffolded_over(self) -> None:
        """The control: a close given --retro mints no retro of its own, and a missing one is
        still refused."""
        with tempfile.TemporaryDirectory() as d:
            root = self._open_run(d)
            rc, out = _run(["close", "--root", str(root), "--retro", "RETRO0009"])
            self.assertEqual(2, rc, out)
            self.assertIn("close refused: retro RETRO0009 not found", out)
            self.assertEqual([], self._retros(root))
            self.assertFalse((run_state.read(root) or {}).get("scaffolded_retro"))

    def test_file_and_close_mints_no_retro_ahead_of_its_preflight(self) -> None:
        """The control: `--file-and-close` keeps its own retro handling, so no retro is minted
        before its pre-flight."""
        seen: dict = {}

        def stopped(root, *_a, **_k):
            seen["retros"] = self._retros(Path(root))
            raise KeyboardInterrupt

        with tempfile.TemporaryDirectory() as d:
            root = self._open_run(d)
            with unittest.mock.patch.object(sprint, "_report_preflight", stopped), \
                    self.assertRaises(KeyboardInterrupt):
                _run(["close", "--root", str(root), "--file-and-close"])
            self.assertEqual([], seen["retros"])


if __name__ == "__main__":
    unittest.main()
