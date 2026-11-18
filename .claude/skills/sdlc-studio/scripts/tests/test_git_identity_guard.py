"""BG1507: a run refuses to land or close once the operator's global git identity has changed.

An agent that redirects HOME and runs `git config --global` writes the operator's real
configuration wherever `XDG_CONFIG_HOME` is exported, and every later commit on the host is then
made under that identity. The run records the identity git reads when it opens; `sprint.py lane
land` and `sprint.py close` refuse when it differs, naming the file git now reads, the identity
recorded and the identity found.

Two routes are driven. `GIT_CONFIG_GLOBAL` names one file of the fixture's own; and the default
route, with no `GIT_CONFIG_GLOBAL`, where a ~/.gitconfig holding no identity sits beside the XDG
file that holds it, and the agent's leak (`git config --global` under its own HOME) rewrites the
XDG file. Every command runs with HOME, `XDG_CONFIG_HOME` and any `GIT_CONFIG_GLOBAL` inside the
fixture's own temporary directory, so no case reads or writes the operator's configuration. The
lane fixture is `test_lane_land.py`'s, so a landing that is not refused is a full landing.
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
#: the two routes git reads a global identity by: one named file, or the XDG file and ~/.gitconfig
ONE_FILE, BOTH_FILES = "GIT_CONFIG_GLOBAL", "XDG file and ~/.gitconfig"


class GitIdentityGuardTests(_LaneFixture):

    def setUp(self) -> None:
        super().setUp()
        self._route(ONE_FILE)

    def _route(self, route: str) -> None:
        """Give the fixture `route`. On BOTH_FILES the XDG file exists, empty, and ~/.gitconfig
        holds only a `[safe]` entry, as a host with one does: `git config --global --get` reads
        ~/.gitconfig alone there, while a commit reads both."""
        self.route = route
        base = Path(self._tmp.name).resolve()
        self.home, self.agent_home = base / "home", base / "agent-home"
        self.xdg_config = self.home / ".config" / "git" / "config"
        self.xdg_config.parent.mkdir(parents=True, exist_ok=True)
        self.agent_home.mkdir(exist_ok=True)
        self.global_config = self.home / "fixture-global.gitconfig"
        if route == BOTH_FILES:
            self.xdg_config.write_text("", encoding="utf-8")
            (self.home / ".gitconfig").write_text("[safe]\n\tdirectory = *\n", encoding="utf-8")

    def _fresh(self, route: str) -> None:
        """A new repository, worktree and identity for `route`: each route is its own fixture."""
        self._tmp.cleanup()
        _LaneFixture.setUp(self)
        self._route(route)

    @property
    def identity_file(self) -> Path:
        """The file the identity is set in, and the one a refusal must name."""
        return self.global_config if self.route == ONE_FILE else self.xdg_config

    def _env(self, home: Path | None = None) -> dict:
        """The fixture's own global configuration, HOME and XDG directory, never the host's.
        On BOTH_FILES there is no `GIT_CONFIG_GLOBAL`, so git takes its default route; `home`
        stands in for the agent's own redirected HOME."""
        if self.route == ONE_FILE:
            return gitutil.git_env(GIT_CONFIG_GLOBAL=str(self.global_config),
                                   HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / ".config"))
        env = gitutil.git_env(HOME=str(home or self.home),
                              XDG_CONFIG_HOME=str(self.home / ".config"))
        env.pop("GIT_CONFIG_GLOBAL")
        return env

    def _set_identity(self, name: str, email: str) -> None:
        """On ONE_FILE, write the named file. On BOTH_FILES, the leak itself: `git config
        --global` under the agent's own HOME, with the fixture's XDG directory exported."""
        for key, value in (("user.name", name), ("user.email", email)):
            if self.route == ONE_FILE:
                gitutil.git(["config", "--file", str(self.global_config), key, value], self.home)
            else:
                subprocess.run(["git", "config", "--global", key, value], cwd=self.agent_home,
                               env=self._env(self.agent_home), check=True, capture_output=True)
        if self.route == BOTH_FILES:
            self.assertFalse((self.agent_home / ".gitconfig").exists())
            self.assertIn(f"name = {name}", self.xdg_config.read_text(encoding="utf-8"))

    def _carried(self) -> str:
        """`name <email>` as a commit made in the fixture's own environment would carry it."""
        env = {k: v for k, v in self._env().items()
               if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}
        r = subprocess.run(["git", "var", "GIT_AUTHOR_IDENT"], cwd=self.home, env=env,
                           capture_output=True, text=True, check=True)
        return r.stdout.rsplit(">", 1)[0] + ">"

    def _open(self) -> None:
        """Open the run as `sprint plan --write` does, reading git through the fixture's env."""
        transcripts = self.home / "no-transcripts"
        transcripts.mkdir(exist_ok=True)
        with unittest.mock.patch.dict(os.environ, {**self._env(),
                                                   run_state.TRANSCRIPTS_ENV: str(transcripts)},
                                      clear=True):
            run_state.open_run(self.root, batch=[A], goal="g")

    def _close(self, home: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(SPRINT), "close", "--root", str(self.root)],
                              capture_output=True, text=True, timeout=300, cwd=str(self.root),
                              env=self._env(home), check=False)

    def _land_as(self, home: Path) -> subprocess.CompletedProcess:
        """`lane land` from the agent's own environment: its HOME, the shared XDG directory."""
        return subprocess.run(
            [sys.executable, "-B", str(SPRINT), "lane", "land", "--worktree", str(self.wt),
             "--units", A, "--root", str(self.root)], capture_output=True, text=True,
            timeout=600, cwd=str(self.root), env=self._env(home), check=False)

    def _lane(self, body: str = "A = 2\n") -> None:
        self._stage("src/a.py", body)
        self._hand_in()

    def _assert_three_facts(self, out: str, found: tuple[str, str]) -> None:
        self.assertIn(REFUSED, out)
        self.assertIn(f" in {self.identity_file}.", out,
                      "the refusal does not name the file git reads, alone")
        self.assertIn(f"{OPERATOR[0]} <{OPERATOR[1]}>", out, "the recorded identity is not named")
        self.assertIn(f"{found[0]} <{found[1]}>", out, "the identity found is not named")

    def test_lane_land_refuses_when_the_global_identity_changed_since_the_run_opened(self) -> None:
        """AC2, on both routes. MUTANTS: the guard deleted from `lane land`; the email not
        compared (the first rewrite changes the email alone); the guard placed after the
        commit; a refusal naming no file or only one identity; the identity read with `git
        config --global`, which on BOTH_FILES reads ~/.gitconfig alone and so finds no change;
        the first file's value kept over a later one's; a process whose route shares the XDG
        file with the opening one's (the agent's own HOME) never compared."""
        for route in (ONE_FILE, BOTH_FILES):
            with self.subTest(route=route):
                self._fresh(route)
                self._set_identity(*OPERATOR)
                self._open()
                self._lane()
                main_before = _git(self.root, "rev-parse", "main")
                for found in ((OPERATOR[0], AGENT[1]), AGENT):
                    with self.subTest(route=route, found=found):
                        self._set_identity(*found)
                        self.assertEqual(f"{found[0]} <{found[1]}>", self._carried())
                        runs = [self._land(A)]
                        if route == BOTH_FILES:
                            runs.append(self._land_as(self.agent_home))
                        for r in runs:
                            self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                            self._assert_three_facts(r.stderr, found)
                        self.assertEqual(main_before, _git(self.root, "rev-parse", "main"),
                                         "main moved under the changed identity")
                        self.assertEqual(main_before, _git(self.wt, "rev-parse", "HEAD"),
                                         "the lane was committed under the changed identity")
                        self.assertEqual("src/a.py",
                                         _git(self.wt, "diff", "--cached", "--name-only"))

    def test_sprint_close_refuses_when_the_global_identity_changed_since_the_run_opened(self) -> None:
        """AC3, on both routes. MUTANTS: the guard deleted from `close`; the guard after a write
        that ends the run; the refusal naming no file or only one identity; the identity read
        with `git config --global`, blind to the XDG file beside a ~/.gitconfig."""
        for route in (ONE_FILE, BOTH_FILES):
            with self.subTest(route=route):
                self._fresh(route)
                self._set_identity(*OPERATOR)
                self._open()
                opened = run_state.read(self.root)
                self.assertEqual(OPERATOR, (opened[run_state.GIT_IDENTITY]["name"],
                                            opened[run_state.GIT_IDENTITY]["email"]),
                                 "the run recorded another identity than a commit carries")
                self._set_identity(*AGENT)
                r = self._close()
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self._assert_three_facts(r.stderr, AGENT)
                self.assertTrue(run_state.is_open(self.root), "the run did not stay open")
                self.assertEqual(opened, run_state.read(self.root),
                                 "the refused close wrote the run")

    def test_an_unchanged_or_unset_identity_lands_and_closes(self) -> None:
        """AC4. MUTANTS: the guard refusing a run whose identity is unchanged; refusing a run
        opened with no global identity (recorded empty, found empty); a fixture command reading
        the host's configuration instead of its own; on the default route, the identity read
        with `git config --global`, which finds none once a ~/.gitconfig appears, and the first
        file's value kept over ~/.gitconfig's, which a commit carries."""
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
        # The default route, where a commit's identity did not change though a file did: a
        # ~/.gitconfig holding none appearing beside the XDG file, and the XDG file rewritten
        # under a ~/.gitconfig whose own identity a commit still carries.
        for label in ("a ~/.gitconfig with no identity appears", "~/.gitconfig wins over XDG"):
            with self.subTest(identity=label):
                self._fresh(BOTH_FILES)
                env, tmp = self._env(), Path(self._tmp.name).resolve()
                self.assertNotIn("GIT_CONFIG_GLOBAL", env)
                for key in ("HOME", "XDG_CONFIG_HOME"):
                    self.assertTrue(Path(env[key]).resolve().is_relative_to(tmp),
                                    f"{key} points outside the fixture: {env[key]}")
                dotfile = self.home / ".gitconfig"
                if label.startswith("a ~"):
                    dotfile.unlink()
                    self._set_identity(*OPERATOR)
                    self._open()
                    dotfile.write_text("[safe]\n\tdirectory = *\n", encoding="utf-8")
                else:
                    self._set_identity(*AGENT)
                    dotfile.write_text(f"[user]\n\tname = {OPERATOR[0]}\n\temail = "
                                       f"{OPERATOR[1]}\n", encoding="utf-8")
                    self._open()
                    self._set_identity("y", "y@y")
                self.assertEqual(f"{OPERATOR[0]} <{OPERATOR[1]}>", self._carried())
                self._lane(f"A = {label!r}\n")
                r = self._land(A)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertNotIn(REFUSED, r.stdout + r.stderr)
                c = self._close()
                self.assertNotIn(REFUSED, c.stdout + c.stderr, "close was refused on identity")
                self.assertIn("close refused: no sprint goal", c.stderr)
                if label.startswith("~"):
                    # the control: ~/.gitconfig's own identity rewritten is caught, and named
                    dotfile.write_text(f"[user]\n\tname = {AGENT[0]}\n\temail = {AGENT[1]}\n",
                                       encoding="utf-8")
                    c = self._close()
                    self.assertEqual(2, c.returncode, c.stdout + c.stderr)
                    self.assertIn(f"found {AGENT[0]} <{AGENT[1]}> in {dotfile}.", c.stderr)
        with self.subTest(identity="another GIT_CONFIG_GLOBAL, sharing no file"):
            # a route sharing no file with the opening one's reads another configuration
            self._fresh(ONE_FILE)
            self._set_identity(*OPERATOR)
            self._open()
            other = self.home / "another.gitconfig"
            gitutil.git(["config", "--file", str(other), "user.name", AGENT[0]], self.home)
            c = subprocess.run([sys.executable, "-B", str(SPRINT), "close", "--root",
                                str(self.root)], capture_output=True, text=True, timeout=300,
                               cwd=str(self.root), check=False,
                               env={**self._env(), "GIT_CONFIG_GLOBAL": str(other)})
            self.assertNotIn(REFUSED, c.stdout + c.stderr, "another configuration was refused")
            self.assertIn("close refused: no sprint goal", c.stderr)


if __name__ == "__main__":
    unittest.main()
