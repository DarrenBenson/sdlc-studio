"""BG0641: a tracked `.githooks/pre-push` binds the boundary lanes AGENTS.md says bind at push.

Every fixture is a THROWAWAY clone with its own bare remote, `core.hooksPath` at `.githooks`, and
a REAL `.claude/skills/sdlc-studio/scripts/` directory holding a stub `gate.py` (never the symlink
the commit-msg fixtures use, which would point the stub at the tracked tree). The stub APPENDS one
argv line per invocation and prints a lane name, so a second call cannot hide behind the first.
The hook reads the cost from `tools/gate_timing.py`, which the fixture copies from this tree.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-push"
ENABLE = REPO / "tools" / "enable-hooks.sh"
GATE_TIMING = REPO / "tools" / "gate_timing.py"
AGENTS = REPO / "AGENTS.md"

STUB_GH = textwrap.dedent('''
    #!/usr/bin/env python3
    import json, os, sys
    from pathlib import Path
    Path(os.environ["STUB_GH_ARGV"]).open("a").write(" ".join(sys.argv[1:]) + "\\n")
    mode = os.environ.get("STUB_GH_MODE", "empty")
    if mode == "fail":
        sys.stderr.write("gh: not logged in\\n"); raise SystemExit(4)
    args = sys.argv[1:]
    red = {"databaseId": 33731466380, "conclusion": "failure", "url": "https://example.test/runs/33731466380"}
    timed = {"databaseId": 33731466381, "conclusion": "timed_out", "url": "https://example.test/runs/33731466381"}
    green = {"databaseId": 33746859034, "conclusion": "success", "url": "https://example.test/runs/33746859034"}
    newer_other = {"databaseId": 33746859999, "conclusion": "success", "url": "https://example.test/runs/dependabot"}
    if "--workflow" not in args:            # without the filter the NEWER green Dependabot run wins
        print(json.dumps([newer_other]) if mode != "empty" else "[]"); raise SystemExit(0)
    if mode == "garbage":
        print("<html>rate limited</html>"); raise SystemExit(0)
    if mode == "number":
        print("42"); raise SystemExit(0)
    cancelled = {"databaseId": 33731466382, "conclusion": "cancelled", "url": "https://example.test/runs/33731466382"}
    noid = {"conclusion": "failure", "url": "https://example.test/runs/unknown"}
    answer = {"red": [red], "timed_out": [timed], "cancelled": [cancelled], "noid": [noid],
              "green": [green], "empty": []}[mode]
    print(json.dumps(answer))
''').lstrip()

STUB_GATE = textwrap.dedent('''
    import os, sys
    from pathlib import Path
    Path(os.environ["STUB_ARGV"]).open("a").write(" ".join(sys.argv[1:]) + "\\n")
    print("  [FAIL] release-rehearsal STUBBED - the fixture gate refused" if os.environ.get("STUB_RC", "0") != "0"
          else "  [PASS] release-rehearsal STUBBED")
    raise SystemExit(int(os.environ.get("STUB_RC", "0")))
''')


# The repo-locating variables git hands a hook, cleared for every fixture git call so the clone
# is never steered at the outer repository. Held equal to REPO_LOCATING in test_skill_tests_env.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def _git(cwd: Path, *args: str, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    base = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t"}
    for k in _GIT_ENV_VARS:
        base.pop(k, None)
    base.pop("SDLC_PUSH_ACK_RED", None)      # a profile-exported acknowledgement is the caller's, never the fixture's
    if env:
        base.update(env)
    return subprocess.run(["git", "-C", str(cwd), *args], check=check, capture_output=True,
                          text=True, env=base, timeout=300)


class _Clone:
    """A clone with the tracked hook, a stub gate at the invoked path, and a bare remote."""

    def __init__(self, *, timings: list[float] | None = None, no_timings_file: bool = False) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pre_push_"))
        self.remote = self.tmp / "origin.git"
        _git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.clone = self.tmp / "clone"
        _git(self.tmp, "init", "-q", "-b", "main", str(self.clone))
        _git(self.clone, "remote", "add", "origin", str(self.remote))
        hooks = self.clone / ".githooks"
        hooks.mkdir()
        shutil.copy(HOOK, hooks / "pre-push")
        (hooks / "pre-push").chmod(0o755)
        _git(self.clone, "config", "core.hooksPath", ".githooks")
        scripts = self.clone / ".claude" / "skills" / "sdlc-studio" / "scripts"
        scripts.mkdir(parents=True)                    # a REAL directory, never a symlink
        (scripts / "gate.py").write_text(STUB_GATE, encoding="utf-8")
        (self.clone / "tools").mkdir()
        shutil.copy(GATE_TIMING, self.clone / "tools" / "gate_timing.py")
        local = self.clone / "sdlc-studio" / ".local"
        if not no_timings_file:
            local.mkdir(parents=True)
            import json
            data = {"skill-tests": [601.0, 648.0]}
            if timings is not None:
                data["boundary-push"] = timings
            (local / "gate-timings.json").write_text(json.dumps(data), encoding="utf-8")
        (self.clone / "README.md").write_text("fixture\n", encoding="utf-8")
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-q", "-m", "seed")
        self.argv = self.tmp / "gate-argv.txt"

    def stub_path(self, gh_mode: str = "empty") -> Path:
        """A PATH holding ONLY a `gh` stub plus symlinks to the real git, bash and python3, so
        no fixture can reach the live forge and the hook can still exec. `gh_mode` selects the
        stub's answer: red, timed_out, green, empty, fail."""
        d = self.tmp / "path"
        if not d.exists():
            d.mkdir()
            for tool in ("git", "bash", "python3"):
                real = shutil.which(tool)
                assert real, tool
                (d / tool).symlink_to(real)
            (d / "gh").write_text(STUB_GH, encoding="utf-8")
            (d / "gh").chmod(0o755)
        self.gh_mode = gh_mode
        return d

    def push(self, *refspec: str, rc: int = 0, gh_mode: str | None = None,
             ack: str | None = None) -> subprocess.CompletedProcess:
        path = self.stub_path(gh_mode or getattr(self, "gh_mode", "empty"))
        env = {"STUB_ARGV": str(self.argv), "STUB_RC": str(rc), "PATH": str(path),
               "STUB_GH_MODE": self.gh_mode, "STUB_GH_ARGV": str(self.tmp / "gh-argv.txt")}
        if ack is not None:
            env["SDLC_PUSH_ACK_RED"] = ack
        return _git(self.clone, "push", "-q", "origin", *(refspec or ("main",)), check=False, env=env)

    def gh_calls(self) -> list[str]:
        f = self.tmp / "gh-argv.txt"
        return f.read_text(encoding="utf-8").splitlines() if f.exists() else []

    def ack_file(self) -> Path:
        return self.clone / "sdlc-studio" / ".local" / "push-ack.json"

    def remote_count(self) -> int:
        return int(_git(self.remote, "rev-list", "--all", "--count", check=False).stdout.strip() or 0)

    def hook_direct(self, rows: str, rc: int = 0) -> subprocess.CompletedProcess:
        """Run the hook itself with hand-written stdin rows, in the order WRITTEN: git always hands
        the branch row before the tag row, so only a direct call can reach the tag-first order."""
        base = {k: v for k, v in os.environ.items() if k not in _GIT_ENV_VARS and k != "SDLC_PUSH_ACK_RED"}
        path = self.stub_path(getattr(self, "gh_mode", "empty"))     # never the caller's PATH: no fixture reaches the live forge
        base.update({"STUB_ARGV": str(self.argv), "STUB_RC": str(rc), "PATH": str(path),
                     "STUB_GH_MODE": self.gh_mode, "STUB_GH_ARGV": str(self.tmp / "gh-argv.txt")})
        return subprocess.run(["bash", ".githooks/pre-push", "origin", str(self.remote)], cwd=self.clone,
                              input=rows, capture_output=True, text=True, env=base, timeout=300)

    def gate_calls(self) -> list[str]:
        return self.argv.read_text(encoding="utf-8").splitlines() if self.argv.exists() else []

    def commit_more(self) -> None:
        with (self.clone / "more.md").open("a", encoding="utf-8") as f:
            f.write("more\n")                          # appended, so every call has something to commit
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-q", "-m", "more")

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class ThePushBoundaryHasAHookTests(unittest.TestCase):
    """AC1-AC4."""

    def test_a_red_boundary_gate_refuses_the_push(self) -> None:
        """AC1. MUTANTS: (1) an or-true fallback on the gate invocation so its exit code never
        reaches git; (2) capture the gate's output and print none of it, so the refusal carries
        no lane name; (3) leave the gate's stdout on stdout, where git does not show it beside the
        refusal; (4) drop the refusal block's own bypass line."""
        fx = _Clone()
        try:
            r = fx.push(rc=1)
            out = r.stderr      # what git shows the pusher: the criterion says STDERR, so only stderr is read
            self.assertNotEqual(0, r.returncode, "a red boundary gate did not refuse the push:\n" + out)
            self.assertIn("release-rehearsal STUBBED", out, "the lane the stub named is not on the refusal's stream:\n" + out)
            self.assertIn("gate.py --boundary push", out, "the refusal does not name the re-run:\n" + out)
            after_gate = out.split("release-rehearsal STUBBED", 1)[1]
            self.assertIn("bypass once (emergency only): git push --no-verify", after_gate,
                          "the refusal block itself does not name the bypass after the lane:\n" + out)
            self.assertEqual("0", _git(fx.remote, "rev-list", "--all", "--count", check=False).stdout.strip(),
                             "the remote advanced despite the refusal")
        finally:
            fx.cleanup()

    def test_a_green_boundary_gate_lets_the_push_through(self) -> None:
        """AC2, the control. MUTANT: `exit 1` after the gate whatever its exit code."""
        fx = _Clone()
        try:
            r = fx.push(rc=0)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual("1", _git(fx.remote, "rev-list", "--all", "--count").stdout.strip(),
                             "the push reported success but the remote did not advance")
            self.assertEqual(["--boundary push"], fx.gate_calls())
        finally:
            fx.cleanup()

    def test_a_tag_push_runs_the_release_boundary_and_a_deletion_runs_none(self) -> None:
        """AC3. MUTANTS: (1) pass `--boundary push` for every ref, dropping the tag branch;
        (2) run the gate once PER REF, so a branch-plus-tag push runs it twice; (3) run the gate
        for a deletion row as well; (4) read the LOCAL ref column instead of the remote one;
        (5) let a later branch row demote release to push; (6) force rc=0 after the release
        invocation; (7) leave the release invocation's stdout on stdout."""
        fx = _Clone()
        try:
            self.assertEqual(0, fx.push().returncode)
            fx.argv.unlink(missing_ok=True)
            _git(fx.clone, "tag", "v0.0.1")
            self.assertEqual(0, fx.push("v0.0.1").returncode)
            self.assertEqual(["--boundary release"], fx.gate_calls(), "a tag push did not run the release boundary once")
            fx.argv.unlink(missing_ok=True)
            fx.commit_more()
            _git(fx.clone, "tag", "v0.0.2")
            self.assertEqual(0, fx.push("main", "v0.0.2").returncode)
            self.assertEqual(["--boundary release"], fx.gate_calls(),
                             "a branch-plus-tag push must run the gate exactly once, at release")
            fx.argv.unlink(missing_ok=True)
            self.assertEqual(0, fx.push(":refs/tags/v0.0.1").returncode)
            self.assertEqual([], fx.gate_calls(), "a deletion ran the gate")
            # the REMOTE ref column decides: a branch pushed to a tag ref is a release (qa seat, X1)
            fx.argv.unlink(missing_ok=True)
            self.assertEqual(0, fx.push("main:refs/tags/v0.0.3").returncode)
            self.assertEqual(["--boundary release"], fx.gate_calls(),
                             "a branch pushed to a tag ref must be judged by the remote ref, not the local one")
            # a tag row FOLLOWED by a branch row still runs once, at release (engineering seat, H2)
            fx.argv.unlink(missing_ok=True)
            sha = _git(fx.clone, "rev-parse", "HEAD").stdout.strip()
            rows = f"refs/tags/v0.0.2 {sha} refs/tags/v0.0.2 {'0' * 40}\nrefs/heads/main {sha} refs/heads/main {'0' * 40}\n"
            self.assertEqual(0, fx.hook_direct(rows).returncode)
            self.assertEqual(["--boundary release"], fx.gate_calls(),
                             "a later branch row must not demote a release to a push")
            # the release half refuses too: a red gate on a tag push (engineering r2, X1 and S1)
            fx.argv.unlink(missing_ok=True)
            fx.commit_more()
            _git(fx.clone, "tag", "v0.0.4")
            r = fx.push("v0.0.4", rc=1)
            self.assertNotEqual(0, r.returncode, "a red gate did not refuse the tag push:\n" + r.stderr)
            self.assertIn("release-rehearsal STUBBED", r.stderr, "the lane is not on the refusal's stream for a tag push:\n" + r.stderr)
            self.assertIn("gate.py --boundary release", r.stderr, "the refusal does not name the release re-run:\n" + r.stderr)
            self.assertNotIn("v0.0.4", _git(fx.remote, "tag", "-l").stdout, "the remote gained the tag despite the refusal")
        finally:
            fx.cleanup()

    def test_the_hook_announces_its_cost_and_the_bypass_before_running(self) -> None:
        """AC4. MUTANTS: (1) print nothing before invoking the gate; (2) print the estimate only
        when history exists, so the first push announces nothing; (3) never record the
        boundary's duration after the gate; (4) drop the full suite's own median as the middle
        floor, so a first push with a suite series announces the literal; (5) drop the two lane
        names from the literal."""
        seeded = _Clone(timings=[700.0, 720.0])
        try:
            r = seeded.push(rc=1)
            out = r.stderr
            self.assertIn("~710s", out, "the seeded median was not announced:\n" + out)
            self.assertLess(out.index("~710s"), out.index("release-rehearsal STUBBED"),
                            "the cost line did not precede the gate's own output:\n" + out)
            self.assertIn("git push --no-verify", out.split("release-rehearsal STUBBED")[0],
                          "the bypass was not named before the gate ran")
            # the boundary records its own duration, so the second push has a number
            import json
            data = json.loads((seeded.clone / "sdlc-studio" / ".local" / "gate-timings.json").read_text())
            self.assertEqual(3, len(data["boundary-push"]), "the hook did not record its run")
        finally:
            seeded.cleanup()
        # the middle floor: no boundary series, but the full suite's own series (qa seat, X3)
        mid = _Clone()
        try:
            r = mid.push(rc=1)
            out = r.stderr
            self.assertIn("expect at least the full suite (~62", out, "the suite's own median was not the floor:\n" + out)
            self.assertNotIn("about ten minutes", out, "the literal was printed beside the suite's own figure:\n" + out)
            self.assertLess(out.index("at least the full suite"), out.index("release-rehearsal STUBBED"),
                            "the floor line did not precede the gate's own output:\n" + out)
            self.assertIn("git push --no-verify", out.split("release-rehearsal STUBBED")[0],
                          "the bypass was not named before the gate ran")
        finally:
            mid.cleanup()
        bare = _Clone(no_timings_file=True)
        try:
            r = bare.push(rc=1)
            out = r.stderr
            self.assertIn("about ten minutes", out, "with no history the floor literal was not printed:\n" + out)
            self.assertIn("release-rehearsal, revert-check and module-alone", out, "the literal does not name the three lanes:\n" + out)
            self.assertNotIn("at least the full suite", out, "a suite figure was printed with no suite series:\n" + out)
            self.assertLess(out.index("about ten minutes"), out.index("release-rehearsal STUBBED"),
                            "the literal did not precede the gate's own output:\n" + out)
            self.assertIn("git push --no-verify", out.split("release-rehearsal STUBBED")[0],
                          "the bypass was not named before the gate ran")
        finally:
            bare.cleanup()


class ARedMainIsReadBeforeTheNextPushTests(unittest.TestCase):
    """BG0642 AC1-AC4: the hook reads the latest push-triggered Lint run on main BEFORE the gate."""

    def test_a_failed_run_on_main_refuses_the_push_and_names_it(self) -> None:
        """AC1. MUTANTS: (1) drop the comparison on the run's `conclusion` field; (2) drop the
        `--workflow Lint` filter so the newer green Dependabot run is read; (3) invoke the gate
        before reading CI."""
        fx = _Clone()
        try:
            r = fx.push(gh_mode="red", rc=0)
            out = r.stdout + r.stderr
            self.assertNotEqual(0, r.returncode, "a red Lint run on main did not refuse the push:\n" + out)
            self.assertIn("33731466380", out); self.assertIn("failure", out); self.assertIn("https://example.test/runs/33731466380", out)
            self.assertIn("SDLC_PUSH_ACK_RED=33731466380 git push", out, "the acknowledgement command was not printed verbatim:\n" + out)
            self.assertNotIn("--no-verify", out, "the CI refusal must never name the bypass - it names the acknowledgement:\n" + out)
            self.assertEqual([], fx.gate_calls(), "the gate ran before CI was read")
            self.assertEqual(1, len(fx.gh_calls()))
            for flag in ("--workflow Lint", "--branch main", "--event push", "--status completed"):
                self.assertIn(flag, fx.gh_calls()[0], fx.gh_calls())
            self.assertEqual(0, fx.remote_count())
            # the read is of MAIN whatever ref is pushed: a tag pushed from a TOPIC checkout still reads main
            _git(fx.clone, "checkout", "-q", "-b", "topic")
            _git(fx.clone, "tag", "v9.9.9")
            tag = fx.push("v9.9.9", gh_mode="red", rc=0)
            self.assertNotEqual(0, tag.returncode, "a tag push over a red main was not refused:\n" + tag.stderr)
            self.assertIn("--branch main", fx.gh_calls()[-1], "a tag push did not read main:\n" + str(fx.gh_calls()))
            self.assertNotIn("v9.9.9", _git(fx.remote, "tag", "-l").stdout)
        finally:
            fx.cleanup()

    def test_a_non_success_conclusion_refuses_not_only_failure(self) -> None:
        """AC2. MUTANTS: (1) compare `conclusion == "failure"` so `timed_out` reads as green; (2) an
        enumerated `failure || timed_out` list, so `cancelled` reads as green."""
        fx = _Clone()
        try:
            for word in ("timed_out", "cancelled"):
                r = fx.push(gh_mode=word, rc=0)
                self.assertNotEqual(0, r.returncode, f"{word} did not refuse:\n" + r.stdout + r.stderr)
                self.assertIn(word, r.stdout + r.stderr)
        finally:
            fx.cleanup()

    def test_an_acknowledged_red_is_remembered_a_stale_ack_refuses_and_a_green_run_proceeds(self) -> None:
        """AC3. MUTANTS: (1) test `[ -n "$SDLC_PUSH_ACK_RED" ]` instead of comparing it to the run
        id - the wrong-id step survives; (2) proceed whenever `push-ack.json` exists without
        comparing its id - the stale-file step survives; (3) honour the variable and record
        nothing - the later push over the same run is refused; (4) invert the conclusion test so
        `success` refuses."""
        fx = _Clone(no_timings_file=True)     # no .local at all: the hook creates it (AC3)
        try:
            self.assertFalse(fx.ack_file().parent.exists(), "the fixture must start with no .local, so the hook is what creates it")
            for wrong_id in ("1", "3373146638", "133731466380"):      # a profile-exported 1, a prefix, a superstring
                wrong = fx.push(gh_mode="red", rc=0, ack=wrong_id)
                self.assertNotEqual(0, wrong.returncode, f"the WRONG acknowledgement id {wrong_id!r} let the push through")
                self.assertNotIn("--no-verify", wrong.stderr, "the CI refusal must never name the bypass")
                self.assertFalse(fx.ack_file().exists(), f"the wrong acknowledgement {wrong_id!r} was recorded")
            acked = fx.push(gh_mode="red", rc=0, ack="33731466380")
            self.assertEqual(0, acked.returncode, acked.stdout + acked.stderr)
            self.assertEqual(1, fx.remote_count())
            self.assertIn("33731466380", fx.ack_file().read_text(encoding="utf-8"))
            fx.commit_more()
            again = fx.push(gh_mode="red", rc=0)          # variable unset, file remembers it
            self.assertEqual(0, again.returncode, "the remembered acknowledgement was not honoured:\n" + again.stdout + again.stderr)
            self.assertEqual(2, fx.remote_count())
            fx.ack_file().write_text('{"acknowledged": "12345"}', encoding="utf-8")   # stale
            fx.commit_more()
            stale = fx.push(gh_mode="red", rc=0)
            self.assertNotEqual(0, stale.returncode, "a stale acknowledgement let the push through")
            fx.ack_file().unlink()
            # a record that cannot be written is a refusal that says so, never "remembered"
            fx.ack_file().unlink(missing_ok=True)
            fx.ack_file().mkdir()                      # a directory where the file must go
            blocked = fx.push(gh_mode="red", rc=0, ack="33731466380")
            self.assertNotEqual(0, blocked.returncode, "an unwritable record let the push through:\n" + blocked.stderr)
            self.assertIn("could not be written", blocked.stderr)
            self.assertNotIn("remembered", blocked.stderr, "the hook claimed to remember what it could not write")
            fx.ack_file().rmdir()
            green = fx.push(gh_mode="green", rc=0)
            self.assertEqual(0, green.returncode, green.stdout + green.stderr)
            self.assertEqual(3, fx.remote_count())
            # a red run with NO id is unread, never "already acknowledged" by an empty id matching an empty record
            fx.commit_more()
            noid = fx.push(gh_mode="noid", rc=0)
            self.assertEqual(0, noid.returncode, noid.stderr)
            self.assertIn("CI state UNREAD", noid.stderr, "a run with no id was not named unread:\n" + noid.stderr)
            self.assertNotIn("acknowledged", noid.stderr, "an empty id matched an empty record:\n" + noid.stderr)
        finally:
            fx.cleanup()

    def test_an_unreadable_ci_state_is_named_unread_not_green(self) -> None:
        """AC4. MUTANTS: (1) treat a failed `gh` invocation as an empty run list and print
        nothing; (2) refuse when `gh` fails; (3) proceed silently on an empty list."""
        fx = _Clone()
        try:
            unread = fx.push(gh_mode="fail", rc=0)
            out = unread.stdout + unread.stderr
            self.assertEqual(0, unread.returncode, out)
            self.assertIn("CI state UNREAD: could not read the latest Lint run on main", out)
            self.assertEqual(1, fx.remote_count())
            fx.commit_more()
            empty = fx.push(gh_mode="empty", rc=0)
            out2 = empty.stdout + empty.stderr
            self.assertEqual(0, empty.returncode, out2)
            self.assertIn("no completed Lint run on main to read", out2)
            self.assertEqual(2, fx.remote_count())
            fx.commit_more()
            red = fx.push(gh_mode="red", rc=0)
            refusal = red.stdout + red.stderr
            self.assertNotEqual(0, red.returncode)
            self.assertNotIn("CI state UNREAD", refusal); self.assertNotIn("no completed Lint run", refusal)
            for mode in ("garbage", "number", "noid"):   # non-JSON, a JSON number, and a run with no id
                fx.commit_more()                       # something to push, or git never invokes the hook
                odd = fx.push(gh_mode=mode, rc=0)
                self.assertEqual(0, odd.returncode, f"{mode}: an unreadable answer blocked the push:\n" + odd.stderr)
                self.assertIn("CI state UNREAD", odd.stderr, f"{mode}: the answer was not named unread:\n" + odd.stderr)
                self.assertNotIn("already acknowledged", odd.stderr, f"{mode}: an empty id matched an empty record")
        finally:
            fx.cleanup()


class EnableHooksNamesEveryHookTests(unittest.TestCase):
    """AC5. MUTANTS: (1) hard-code the three known hook names in the sentence the script prints;
    (2) print the names without their header lines."""

    def test_enable_hooks_names_each_tracked_hook(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="enable_hooks_"))
        try:
            _git(tmp, "init", "-q", "-b", "main", str(tmp))
            hooks = tmp / ".githooks"; hooks.mkdir()
            for name in ("pre-commit", "commit-msg", "pre-push"):
                shutil.copy(REPO / ".githooks" / name, hooks / name)
            (hooks / "post-merge").write_text("#!/usr/bin/env bash\n# A fixture hook the script cannot know about.\nexit 0\n")
            (hooks / "post-checkout").write_text("#!/usr/bin/env bash\nexit 0\n")
            (tmp / "tools").mkdir(); shutil.copy(ENABLE, tmp / "tools" / "enable-hooks.sh")
            # Scrubbed like every other call in this module: the script runs `git config`, and
            # an inherited GIT_DIR would write core.hooksPath into whatever repository the
            # caller's environment names (delivery review, qa seat).
            env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV_VARS}
            r = subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=tmp, capture_output=True, text=True,
                               timeout=60, env=env)
            out = r.stdout + r.stderr
            self.assertEqual(0, r.returncode, out)
            for name in ("pre-commit", "commit-msg", "pre-push", "post-merge", "post-checkout"):
                self.assertIn(name, out, f"{name} was not named:\n{out}")
            self.assertIn("A fixture hook the script cannot know about.", out, "the header line was not printed:\n" + out)
            self.assertIn("SDLC Studio pre-push gate", out, out)
            self.assertIn("(no description)", out, "a hook without a header was not marked:\n" + out)
            self.assertEqual(".githooks", _git(tmp, "config", "core.hooksPath").stdout.strip())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class AgentsMdNamesTheHookTests(unittest.TestCase):
    """AC8. MUTANT: leave the table, paragraph and bypass sentence as they were."""

    def test_the_refusal_table_and_hooks_paragraph_name_pre_push(self) -> None:
        text = AGENTS.read_text(encoding="utf-8")
        table = text.split("## What will refuse you", 1)[1].split("**Enable the hooks", 1)[0]
        self.assertIn("pre-push", table, "the refusal table has no pre-push row")
        self.assertIn("gate_timing.py estimate --suite boundary-push", table,
                      "the row does not name the command that prints the current cost")
        self.assertIn("three tracked hooks", text, "the hooks paragraph does not say three")
        self.assertIn("`git push --no-verify`", text, "the bypass sentence does not name the push bypass")
        self.assertIn("`.githooks/pre-push`", text, "the boundary prose does not say where the lanes bind")




class KeepaliveTests(unittest.TestCase):
    """BG0654: the pre-push gate pays minutes of boundary lanes before git writes a byte, and an
    ssh connection idle that long is dropped before the push starts - so the gate passes, the
    push fails, and the retry pays the gate again. Nothing set a keepalive and nothing said so."""

    def _clone(self) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="keepalive_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        _git(tmp, "init", "-q", "-b", "main", str(tmp))
        (tmp / ".githooks").mkdir()
        shutil.copy(REPO / ".githooks" / "pre-push", tmp / ".githooks" / "pre-push")
        (tmp / "tools").mkdir(); shutil.copy(ENABLE, tmp / "tools" / "enable-hooks.sh")
        return tmp

    def _env(self) -> dict:
        """The developer's own config POINTED AT /dev/null, not unset.

        Unsetting these two is what lets `~/.gitconfig` answer for the clone, which is the
        opposite of what this control needs - it is also the mechanism this module's own `_git`
        helper already uses."""
        env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV_VARS}
        env["GIT_CONFIG_GLOBAL"] = "/dev/null"
        env["GIT_CONFIG_SYSTEM"] = "/dev/null"
        return env

    def _run(self, tmp: Path):
        return subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=tmp, capture_output=True,
                              text=True, timeout=60, env=self._env())

    def _local(self, tmp: Path) -> str:
        r = subprocess.run(["git", "-C", str(tmp), "config", "--local", "--get",
                            "core.sshCommand"], capture_output=True, text=True, env=self._env())
        return r.stdout.strip()

    def test_enable_hooks_sets_the_keepalive_on_a_clone_that_has_none(self) -> None:
        """MUTANT: delete the core.sshCommand write so a fresh clone gets no keepalive."""
        tmp = self._clone()
        r = self._run(tmp)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        got = self._local(tmp)
        self.assertIn("ServerAliveInterval", got, f"no keepalive interval was set: {got!r}")
        self.assertIn("ServerAliveCountMax", got, f"no keepalive count was set: {got!r}")
        self.assertIn("ServerAliveInterval", r.stdout + r.stderr,
                      "the script set it without saying so")

    def test_an_existing_ssh_command_is_left_alone_and_said_so(self) -> None:
        """MUTANT: drop the guard that reads the existing value first, making the write
        unconditional so it overwrites what the developer set.

        The paired control AC1 cannot supply: deleting the write satisfies `an existing one is
        untouched` trivially, and the likelier careless implementation is the clobber."""
        tmp = self._clone()
        mine = "ssh -i ~/.ssh/mine"
        subprocess.run(["git", "-C", str(tmp), "config", "--local", "core.sshCommand", mine],
                       check=True, capture_output=True, env=self._env())
        r = self._run(tmp)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(mine, self._local(tmp), "the developer's own ssh command was clobbered")
        self.assertIn("Left core.sshCommand", r.stdout + r.stderr,
                      "the script kept the value without saying it had")

    def test_the_hook_names_the_keepalive_the_gate_needs(self) -> None:
        """MUTANT: strip the keepalive sentence from the cost line the hook echoes to stderr.

        The fixture copies the hook alone and never runs the enabling script, so this criterion
        rests on the hook's own text and nothing else."""
        text = (REPO / ".githooks" / "pre-push").read_text(encoding="utf-8")
        self.assertIn("ServerAliveInterval", text,
                      "the hook never names the keepalive the gate needs")
        self.assertIn("enable-hooks.sh", text,
                      "the hook names the need without naming the command that meets it")
        line = next(l for l in text.splitlines() if "ServerAliveInterval" in l and "echo" in l)
        self.assertIn(">&2", line,
                      f"the keepalive line is not on the stream git shows a pusher:\n{line}")


if __name__ == "__main__":
    unittest.main()
