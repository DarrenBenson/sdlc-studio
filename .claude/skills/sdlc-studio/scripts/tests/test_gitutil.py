"""The shared git fixture helper confines its calls to the fixture (BG0230).

The suites build throwaway repos in temp directories and shell out to git. Nothing used to
confine those calls: `git_env()` handed `os.environ` straight through, so an ambient
`GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE` pointing at the parent repository made every
fixture git call operate on the REAL repo. That is not hypothetical here. It emptied this
repository's index once (1845 tracked files staged as deletions), and recurred later when a
fixture ran git unscrubbed under `git commit -a`.

Defence belongs at the fixture, because the hook is not the only source of pollution: a CI
runner, a developer's shell, or a test of git behaviour itself can export the same variables.

Every test below builds its own repos under `tempfile`; none touches the repository this file
lives in. A test for THIS defect must never be reproduced next to a live repo.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import ast
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))  # tests/ dir, for the shared gitutil helper
import gitutil  # noqa: E402

#: An environment with every `GIT_*` variable removed, for the test's OWN bookkeeping git
#: calls. The helper under test must not be used to check up on itself: if it were, a helper
#: that confined nothing would build the victim repo and inspect it through the same broken
#: environment, and the assertions would agree with the defect.
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), env=CLEAN_ENV,
                          capture_output=True, text=True, check=True)


def _victim(root: Path) -> Path:
    """A repo with tracked content, standing in for the parent repository."""
    repo = root / "victim"
    repo.mkdir()
    _git(["init", "-q"], repo)
    for name in ("one.txt", "two.txt", "three.txt"):
        (repo / name).write_text(name, encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["-c", "user.email=v@v", "-c", "user.name=v", "commit", "-qm", "base"], repo)
    return repo


def _index_hash(repo: Path) -> str:
    return hashlib.sha256((repo / ".git" / "index").read_bytes()).hexdigest()


def _pollution(victim: Path) -> dict:
    """The environment `git commit -a` hands a pre-commit hook, pointed at the victim."""
    return {"GIT_DIR": str(victim / ".git"),
            "GIT_WORK_TREE": str(victim),
            "GIT_INDEX_FILE": str(victim / ".git" / "index")}


class _PollutedEnvironment:
    """Sets the pollution in `os.environ` for the body, and restores it afterwards.

    The helper reads `os.environ` at call time, so the pollution has to be really present in
    this process. It is removed again on the way out, including on failure, so one test cannot
    leak its pollution into the next.
    """

    def __init__(self, extra: dict) -> None:
        self._extra = extra
        self._saved: dict = {}

    def __enter__(self) -> None:
        for k, v in self._extra.items():
            self._saved[k] = os.environ.get(k)
            os.environ[k] = v

    def __exit__(self, *exc) -> None:
        for k, old in self._saved.items():
            if old is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = old


class FixtureCallsCannotReachTheParentRepoTests(unittest.TestCase):
    """The incident itself, reproduced against two throwaway repos."""

    def test_a_polluted_environment_cannot_reach_the_victim_repo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            victim = _victim(root)
            fixture = root / "fixture"
            fixture.mkdir()
            _git(["init", "-q"], fixture)
            (fixture / "fixture-only.txt").write_text("x", encoding="utf-8")

            before_hash = _index_hash(victim)
            before_files = _git(["ls-files"], victim).stdout.split()

            with _PollutedEnvironment(_pollution(victim)):
                gitutil.git(["add", "-A"], cwd=fixture)
                gitutil.git(["rm", "--cached", "-q", "--ignore-unmatch", "one.txt"],
                            cwd=fixture, check=False)

            self.assertEqual(_index_hash(victim), before_hash,
                             "a fixture git call rewrote the victim repo's index")
            self.assertEqual(_git(["ls-files"], victim).stdout.split(), before_files,
                             "a fixture git call changed what the victim repo tracks")

    def test_the_hook_shaped_environment_leaves_no_lock_behind(self) -> None:
        """The recurrence vector, in the shape git actually hands it over.

        `git commit -a` runs the pre-commit hook with `GIT_INDEX_FILE` pointing at the OUTER
        repo's `.git/index.lock` as an ABSOLUTE path, and `GIT_PREFIX` set. A staged
        `git add` + `git commit` sets the RELATIVE `.git/index` instead, which resolves inside
        the fixture and does no harm - which is why this read as flaky tests rather than as an
        environment leak, the same commit passing when staged and failing under `-a`. The
        absolute form also strands a lock file in the victim, and a stale `index.lock` blocks
        every later commit in that repository until someone deletes it by hand.

        Simulated, never produced: no `git commit` is run anywhere, and the only repositories
        involved are the two this test builds under `tempfile`.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            victim = _victim(root)
            fixture = root / "fixture"
            fixture.mkdir()
            _git(["init", "-q"], fixture)
            (fixture / "fixture-only.txt").write_text("x", encoding="utf-8")

            before_hash = _index_hash(victim)
            hook_env = {"GIT_DIR": str(victim / ".git"),
                        "GIT_WORK_TREE": str(victim),
                        "GIT_INDEX_FILE": str(victim / ".git" / "index.lock"),
                        "GIT_PREFIX": ""}
            with _PollutedEnvironment(hook_env):
                gitutil.git(["add", "-A"], cwd=fixture)

            self.assertFalse((victim / ".git" / "index.lock").exists(),
                             "a fixture git call stranded a lock in the victim repo, which "
                             "blocks every later commit there")
            self.assertEqual(_index_hash(victim), before_hash,
                             "a fixture git call rewrote the victim repo's index")
            self.assertEqual(_git(["ls-files"], fixture).stdout.split(), ["fixture-only.txt"],
                             "the add never reached the fixture's own index")

    def test_the_confined_call_still_lands_in_the_fixtures_own_index(self) -> None:
        """Anti-vacuity for the test above: a helper that simply failed would also leave the
        victim untouched. The add has to have worked, in the fixture's own index."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            victim = _victim(root)
            fixture = root / "fixture"
            fixture.mkdir()
            _git(["init", "-q"], fixture)
            (fixture / "fixture-only.txt").write_text("x", encoding="utf-8")

            with _PollutedEnvironment(_pollution(victim)):
                gitutil.git(["add", "-A"], cwd=fixture)

            self.assertEqual(_git(["ls-files"], fixture).stdout.split(), ["fixture-only.txt"],
                             "the add never reached the fixture's own index")


class GitEnvTests(unittest.TestCase):
    def test_git_env_drops_every_repo_locating_variable(self) -> None:
        polluted = {n: "/definitely/not/this/repo" for n in gitutil.REPO_LOCATING_GIT_VARS}
        with _PollutedEnvironment(polluted):
            env = gitutil.git_env()
        survived = [n for n in gitutil.REPO_LOCATING_GIT_VARS
                    if env.get(n) == "/definitely/not/this/repo"]
        self.assertEqual(survived, [],
                         f"the helper passed {survived} through to the fixture's git calls")

    def test_git_env_keeps_the_hermeticity_and_identity_settings(self) -> None:
        """The scrub has an upper bound too. Clearing the config-neutralising variables would
        let a developer's global `commit.gpgsign` back in and hang the suite on a passphrase."""
        env = gitutil.git_env()
        self.assertEqual(env["GIT_CONFIG_GLOBAL"], "/dev/null")
        self.assertEqual(env["GIT_CONFIG_SYSTEM"], "/dev/null")
        self.assertEqual(env["GIT_AUTHOR_NAME"], "t")
        self.assertEqual(env["GIT_COMMITTER_EMAIL"], "t@t")

    def test_an_explicit_extra_still_overrides_the_scrub(self) -> None:
        """A test that deliberately wants a repo-locating variable can still set one. What the
        helper refuses is the INHERITED value, not an explicit one.

        Both kinds of key are asserted. A variable the helper merely DROPS is the weaker case:
        it is absent by then, so an extra that only filled in missing keys would satisfy it and
        the assertion would not notice. A variable the helper SETS ITSELF is the one that tells
        an override apart from a default.
        """
        env = gitutil.git_env(GIT_DIR="/explicit/choice",
                              GIT_CEILING_DIRECTORIES="/explicit/ceiling",
                              GIT_AUTHOR_NAME="explicit")
        self.assertEqual(env["GIT_DIR"], "/explicit/choice")
        self.assertEqual(env["GIT_CEILING_DIRECTORIES"], "/explicit/ceiling")
        self.assertEqual(env["GIT_AUTHOR_NAME"], "explicit")

    def test_the_ceiling_is_the_helpers_own_value_never_the_inherited_one(self) -> None:
        with _PollutedEnvironment({"GIT_CEILING_DIRECTORIES": "/inherited/ceiling"}):
            env = gitutil.git_env()
        self.assertEqual(env["GIT_CEILING_DIRECTORIES"], tempfile.gettempdir())


class DiscoveryCannotClimbOutOfTheTempRootTests(unittest.TestCase):
    """The second escape route, which scrubbing alone does not close.

    With the inherited variables gone, git falls back to discovery from the working directory.
    A fixture that has not run `git init` yet, or one whose repo creation failed, then walks UP
    until it finds a repo. That is harmless while temp directories live under `/tmp`, and not
    harmless at all when `TMPDIR` points inside a checkout, which CI runners and agent
    harnesses do set. The helper pins the ceiling at the temp root so the walk stops there.
    """

    def _toplevel_seen_from(self, tmpdir: Path) -> subprocess.CompletedProcess:
        """Run a git call through the helper, in a child whose TMPDIR is `tmpdir`, from a
        directory that is NOT a repo. Returns the child's completed process."""
        probe = (
            "import sys, tempfile, pathlib\n"
            f"sys.path.insert(0, {str(TESTS_DIR)!r})\n"
            "import gitutil\n"
            "work = pathlib.Path(tempfile.mkdtemp()) / 'not-a-repo'\n"
            "work.mkdir()\n"
            "r = gitutil.git(['rev-parse', '--show-toplevel'], cwd=work, check=False)\n"
            "print(r.returncode)\n"
            "print(r.stdout.decode().strip())\n"
        )
        env = {**CLEAN_ENV, "TMPDIR": str(tmpdir)}
        return subprocess.run([sys.executable, "-B", "-c", probe],
                              capture_output=True, text=True, env=env, check=True)

    def test_a_fixture_under_a_tmpdir_inside_a_repo_does_not_discover_that_repo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            victim = _victim(Path(d))
            inside = victim / "tmp"
            inside.mkdir()
            out = self._toplevel_seen_from(inside).stdout.splitlines()
            self.assertNotEqual(out[0], "0",
                                f"discovery climbed out of TMPDIR and found {out[1:]}")
            self.assertNotIn(str(victim), "\n".join(out),
                             "a fixture git call resolved to the surrounding repository")

    def test_a_fixture_that_is_its_own_repo_is_unaffected_by_the_ceiling(self) -> None:
        """The ceiling must not break the normal case, or it would be paid for in broken
        fixtures rather than in safety."""
        with tempfile.TemporaryDirectory() as d:
            fixture = Path(d) / "fixture"
            fixture.mkdir()
            _git(["init", "-q"], fixture)
            sub = fixture / "sub"
            sub.mkdir()
            r = gitutil.git(["rev-parse", "--show-toplevel"], cwd=sub)
            self.assertEqual(Path(r.stdout.decode().strip()).resolve(), fixture.resolve())


#: Test modules that still shell out to git WITHOUT passing an `env`, and how many such call
#: sites each has today. They inherit whatever the ambient environment holds, so the fix in
#: `gitutil` does not reach them: a module that builds its own repo with a bare
#: `subprocess.run(["git", ...])` is the same exposure this file exists to close, one layer
#: further out. Fixing them is not in BG0230's remit, so the count is a ratchet instead - it
#: may fall as call sites move onto the helper, and a rise or a NEW module fails here.
#:
#: What the sweep does NOT judge: a call site that passes `env=` at all is left alone, whether
#: the value is `gitutil.git_env()`, a purpose-built dict, or `os.environ` with the leak still
#: in it. Reading the value would need to resolve a name across the module, which the sweep
#: cannot do honestly, so it counts only the case it can decide.
UNCONFINED_RAW_GIT_CALLS: dict[str, int] = {
    "test_deploy": 1,
    "test_engagement_floor": 6,
    "test_flow": 1,
    "test_gate": 10,
    "test_mutation": 4,
    "test_sprint": 8,
    "test_sprint_rolling": 3,
    "test_status": 2,
}

#: `subprocess` entry points that start a process.
_RUNNERS = frozenset({"run", "check_output", "check_call", "call", "Popen"})


def _unconfined_raw_git_calls(source: str) -> int:
    """Count `subprocess.<runner>(["git", ...])` calls in `source` that pass no `env`.

    AST-based, so `git` named in a comment, a docstring or a string body does not count.
    """
    found = 0
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in _RUNNERS or not node.args:
            continue
        argv = node.args[0]
        if not (isinstance(argv, ast.List) and argv.elts
                and isinstance(argv.elts[0], ast.Constant) and argv.elts[0].value == "git"):
            continue
        if not any(kw.arg == "env" for kw in node.keywords):
            found += 1
    return found


def _unconfined_by_module() -> dict[str, int]:
    counts = {}
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        n = _unconfined_raw_git_calls(path.read_text(encoding="utf-8"))
        if n:
            counts[path.stem] = n
    return counts


class UnconfinedRawGitCallSweepTests(unittest.TestCase):
    """The exposure one layer out from this helper, bounded so it cannot grow.

    Confining `gitutil` protects every fixture that goes through it. It protects nothing in a
    module that calls `subprocess.run(["git", ...])` itself, and 35 such call sites remain. The
    caller-side scrub in `tools/skill-tests.sh` covers them when the suite is run through that
    script, and covers nothing when someone runs `unittest discover` directly - which is the
    command in this bug's own reproduction steps. So the debt is declared and frozen here.
    """

    def test_the_detector_counts_a_bare_git_call(self) -> None:
        self.assertEqual(_unconfined_raw_git_calls('subprocess.run(["git", "init"], cwd=d)'), 1)

    def test_the_detector_ignores_a_call_that_passes_an_env(self) -> None:
        self.assertEqual(
            _unconfined_raw_git_calls('subprocess.run(["git", "init"], env=git_env())'), 0)

    def test_the_detector_ignores_git_named_in_a_string(self) -> None:
        self.assertEqual(_unconfined_raw_git_calls('x = "git init"\nprint("git")'), 0)

    def test_the_detector_still_sees_the_modules_it_guards(self) -> None:
        """A detector that stopped detecting would make the ratchet below vacuously true."""
        counts = _unconfined_by_module()
        self.assertIn("test_gate", counts, "the raw-git detector has stopped detecting")

    def test_no_module_gains_an_unconfined_raw_git_call(self) -> None:
        counts = _unconfined_by_module()
        risen = {mod: (n, UNCONFINED_RAW_GIT_CALLS.get(mod, 0))
                 for mod, n in counts.items() if n > UNCONFINED_RAW_GIT_CALLS.get(mod, 0)}
        self.assertEqual(
            risen, {},
            "these modules shell out to git without an env more often than the frozen count "
            f"(actual, allowed): {risen}. Route the new call through gitutil.git rather than "
            "raising the number - the whole point of the ratchet is that it only falls.")

    def test_the_ratchet_has_no_rotted_entries(self) -> None:
        counts = _unconfined_by_module()
        cleared = sorted(set(UNCONFINED_RAW_GIT_CALLS) - set(counts))
        self.assertEqual(cleared, [],
                         f"these modules no longer call git unconfined: {cleared}. Drop them "
                         "from UNCONFINED_RAW_GIT_CALLS so the debt list stays true.")


if __name__ == "__main__":
    unittest.main()
