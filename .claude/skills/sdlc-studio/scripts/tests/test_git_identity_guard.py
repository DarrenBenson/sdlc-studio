"""BG1507: a run refuses to land or close once the operator's global git identity has changed.

An agent that redirects HOME and runs `git config --global` writes the operator's real
configuration wherever `XDG_CONFIG_HOME` is exported, and every later commit on the host is then
made under that identity. The run records the identity git reads when it opens; `sprint.py lane
land` and `sprint.py close` refuse when it differs, naming the file git now reads, the identity
recorded and the identity found.

Every command here runs with `GIT_CONFIG_GLOBAL`, HOME and `XDG_CONFIG_HOME` inside the fixture's
own temporary directory, so no case reads or writes the operator's configuration. The lane fixture
is `test_lane_land.py`'s, so a landing that is not refused is a full landing.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
from test_lane_land import SPRINT, A, _git, _LaneFixture  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import run_state  # noqa: E402

OPERATOR = ("Op Erator", "op@example.org")
AGENT = ("x", "r@x")
REFUSED = "global git identity has changed"


class GitIdentityGuardTests(_LaneFixture):

    def setUp(self) -> None:
        super().setUp()
        self.home = Path(self._tmp.name).resolve() / "home"
        (self.home / ".config").mkdir(parents=True)
        self.global_config = self.home / "fixture-global.gitconfig"

    def _env(self) -> dict:
        """The fixture's own global configuration, HOME and XDG directory, never the host's."""
        return gitutil.git_env(GIT_CONFIG_GLOBAL=str(self.global_config), HOME=str(self.home),
                               XDG_CONFIG_HOME=str(self.home / ".config"))

    def _set_identity(self, name: str, email: str) -> None:
        for key, value in (("user.name", name), ("user.email", email)):
            gitutil.git(["config", "--file", str(self.global_config), key, value], self.home)

    def _open(self) -> None:
        """Open the run as `sprint plan --write` does, reading git through the fixture's env."""
        transcripts = self.home / "no-transcripts"
        transcripts.mkdir(exist_ok=True)
        with unittest.mock.patch.dict(os.environ, {**self._env(),
                                                   run_state.TRANSCRIPTS_ENV: str(transcripts)}):
            run_state.open_run(self.root, batch=[A], goal="g")

    def _close(self) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(SPRINT), "close", "--root", str(self.root)],
                              capture_output=True, text=True, timeout=300, cwd=str(self.root),
                              env=self._env(), check=False)

    def _lane(self, body: str = "A = 2\n") -> None:
        self._stage("src/a.py", body)
        self._hand_in()

    def _assert_three_facts(self, out: str, found: tuple[str, str]) -> None:
        self.assertIn(REFUSED, out)
        self.assertIn(str(self.global_config), out, "the refusal does not name the file git reads")
        self.assertIn(f"{OPERATOR[0]} <{OPERATOR[1]}>", out, "the recorded identity is not named")
        self.assertIn(f"{found[0]} <{found[1]}>", out, "the identity found is not named")

    def test_lane_land_refuses_when_the_global_identity_changed_since_the_run_opened(self) -> None:
        """AC2. MUTANTS: the guard deleted from `lane land`; the email not compared (the first
        rewrite changes the email alone); the guard placed after the commit; a refusal naming
        no file or only one identity."""
        self._set_identity(*OPERATOR)
        self._open()
        self._lane()
        main_before = _git(self.root, "rev-parse", "main")
        for found in ((OPERATOR[0], AGENT[1]), AGENT):
            with self.subTest(found=found):
                self._set_identity(*found)
                r = self._land(A)
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self._assert_three_facts(r.stderr, found)
                self.assertEqual(main_before, _git(self.root, "rev-parse", "main"),
                                 "main moved under the changed identity")
                self.assertEqual(main_before, _git(self.wt, "rev-parse", "HEAD"),
                                 "the lane was committed under the changed identity")
                self.assertEqual("src/a.py", _git(self.wt, "diff", "--cached", "--name-only"))

    def test_sprint_close_refuses_when_the_global_identity_changed_since_the_run_opened(self) -> None:
        """AC3. MUTANTS: the guard deleted from `close`; the guard after a write that ends the run;
        the refusal naming no file or only one identity."""
        self._set_identity(*OPERATOR)
        self._open()
        opened = run_state.read(self.root)
        self._set_identity(*AGENT)
        r = self._close()
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self._assert_three_facts(r.stderr, AGENT)
        self.assertTrue(run_state.is_open(self.root), "the run did not stay open")
        self.assertEqual(opened, run_state.read(self.root), "the refused close wrote the run")

    def test_an_unchanged_or_unset_identity_lands_and_closes(self) -> None:
        """AC4. MUTANTS: the guard refusing a run whose identity is unchanged; refusing a run
        opened with no global identity (recorded empty, found empty); a fixture command reading
        the host's configuration instead of its own."""
        env = self._env()
        tmp = Path(self._tmp.name).resolve()
        for key in ("GIT_CONFIG_GLOBAL", "HOME", "XDG_CONFIG_HOME"):
            self.assertTrue(Path(env[key]).resolve().is_relative_to(tmp),
                            f"{key} points outside the fixture: {env[key]}")
        self._set_identity(*OPERATOR)
        self._open()
        for label, identity in (("unchanged", OPERATOR), ("never set", None)):
            with self.subTest(identity=label):
                if identity is None:
                    # the second run: the first is ended and the global identity removed entirely
                    run_state.close_run(self.root, run_state.CLOSED[0])
                    self.global_config.unlink()
                    self._open()
                    self.assertNotEqual(first, run_state.read(self.root)["run_id"])
                    gitutil.git(["worktree", "add", "-q", "-b", "lane-us0101", str(self.wt),
                                 "main"], self.root)
                else:
                    first = run_state.read(self.root)["run_id"]
                self._lane(f"A = {label!r}\n")
                r = self._land(A)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertNotIn(REFUSED, r.stdout + r.stderr)
                c = self._close()
                self.assertNotIn(REFUSED, c.stdout + c.stderr, "close was refused on identity")
                # a positive control that the close ran past the guard to its next refusal
                self.assertIn("close refused: no sprint goal", c.stderr)


if __name__ == "__main__":
    unittest.main()
