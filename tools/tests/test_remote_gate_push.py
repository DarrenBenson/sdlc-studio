"""US1075: a push is judged on the gate host this clone configures.

Every fixture is a throwaway clone with a bare `origin`, the tracked `.githooks/pre-push` and
`tools/remote-gate.sh`, and a stubbed TRANSPORT in place of ssh: `sdlc.gateSsh` names a script that
runs each command in a fake host home with the host's own environment, exactly as ssh would run
it on a real host. The gate the host runs is a stub at the invoked path that records where it ran,
which commit it judged, the pushed range and the latest tag it sees, and exits by a `verdict` file
COMMITTED in the tree - so an uncommitted edit to that file flips the working tree's verdict and
never the pushed commit's.

The hook's own PATH holds only git, bash, python3 and a `gh` stub, as in test_pre_push_hook.py, so
the local side of remote-gate.sh is held to the tools it promises to need.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-push"
REMOTE_GATE = REPO / "tools" / "remote-gate.sh"
GATE_TIMING = REPO / "tools" / "gate_timing.py"
HOST = "gatehost.test"

#: The stub gate: one JSON line per run, then the verdict the committed `verdict` file holds.
STUB_GATE = textwrap.dedent('''
    import json, os, subprocess, sys
    from pathlib import Path
    def git(*a):
        r = subprocess.run(["git", *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    verdict = int(Path("verdict").read_text().strip()) if Path("verdict").exists() else 0
    Path(os.environ["STUB_GATE_LOG"]).open("a").write(json.dumps({
        "argv": sys.argv[1:], "cwd": os.getcwd(), "head": git("rev-parse", "HEAD"),
        "range": git("log", "HEAD", "--not", "--remotes", "--format=%H").split(),
        "tag": git("describe", "--tags", "--abbrev=0"), "verdict": verdict}) + "\\n")
    print("  [FAIL] stub-lane STUBBED - the fixture gate refused" if verdict else "  [PASS] stub-lane STUBBED")
    raise SystemExit(verdict)
''')

#: The prerequisite check: records where it ran; exits by a committed `prereq-rc` file.
STUB_PREREQS = textwrap.dedent('''
    import os, sys
    from pathlib import Path
    rc = int(Path("prereq-rc").read_text().strip()) if Path("prereq-rc").exists() else 0
    Path(os.environ["STUB_PREREQ_LOG"]).open("a").write(os.getcwd() + "\\n")
    print("prereqs: REFUSES coverage - stub" if rc else "prereqs: ok - stub")
    raise SystemExit(rc)
''')

#: The known-issues check a tag push runs locally: records where it ran.
STUB_KNOWN_ISSUES = textwrap.dedent('''
    import os, sys
    from pathlib import Path
    Path(os.environ["STUB_KI_LOG"]).open("a").write(os.getcwd() + " " + " ".join(sys.argv[1:]) + "\\n")
''')

#: The transport. Skips ssh's options, records the call, then runs the command in the host's home
#: with the host's environment. STUB_SSH_FAIL=before fails every call with ssh's own 255;
#: STUB_SSH_FAIL=during runs the gate and then reports 255, a connection dropped mid-run.
STUB_SSH = textwrap.dedent('''
    #!/usr/bin/env bash
    while [ $# -gt 0 ]; do
      case "$1" in -o|-p|-l|-i|-F) shift 2 ;; --) shift; break ;; -*) shift ;; *) break ;; esac
    done
    host="$1"; shift
    printf '%s\\t%s\\n' "$host" "$*" >> "$STUB_SSH_LOG"
    [ "${STUB_SSH_FAIL:-}" = "before" ] && exit 255
    cd "$STUB_HOST_HOME" || exit 255
    /usr/bin/env -i HOME="$STUB_HOST_HOME" PATH="$STUB_HOST_PATH" STUB_GATE_LOG="$STUB_GATE_LOG" \\
      STUB_PREREQ_LOG="$STUB_PREREQ_LOG" bash -c "$*"
    rc=$?
    if [ "${STUB_SSH_FAIL:-}" = "during" ]; then case "$*" in *" remote --clone "*) exit 255 ;; esac; fi
    exit $rc
''').lstrip()

STUB_GH = textwrap.dedent('''
    #!/usr/bin/env python3
    import json, os, sys
    mode = os.environ.get("STUB_GH_MODE", "empty")
    red = {"databaseId": 40000000001, "conclusion": "failure", "url": "https://example.test/runs/40000000001"}
    print(json.dumps({"red": [red], "empty": []}[mode]))
''').lstrip()

_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def _git(cwd: Path, *args: str, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    base = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t"}
    for k in _GIT_ENV_VARS + ("SDLC_PUSH_ACK_RED", "SDLC_STUDIO_BOUNDARY_SUITE", "SDLC_GATE_LOCAL"):
        base.pop(k, None)
    if env:
        base.update(env)
    return subprocess.run(["git", "-C", str(cwd), *args], check=check, capture_output=True,
                          text=True, env=base, timeout=300)


class _HostClone:
    """A clone, its bare origin, a fake gate host's home, and the stubbed transport between them."""

    def __init__(self, *, with_host: bool = True) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="remote_gate_"))
        self.remote = self.tmp / "origin.git"
        _git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.clone = self.tmp / "clone"
        _git(self.tmp, "init", "-q", "-b", "main", str(self.clone))
        _git(self.clone, "remote", "add", "origin", str(self.remote))
        self.host_home = self.tmp / "host-home"
        self.host_home.mkdir()
        (self.clone / ".githooks").mkdir()
        shutil.copy(HOOK, self.clone / ".githooks" / "pre-push")
        (self.clone / "tools").mkdir()
        shutil.copy(REMOTE_GATE, self.clone / "tools" / "remote-gate.sh")
        shutil.copy(GATE_TIMING, self.clone / "tools" / "gate_timing.py")
        (self.clone / "tools" / "gate_prereqs.py").write_text(STUB_PREREQS, encoding="utf-8")
        (self.clone / "tools" / "known_issues.py").write_text(STUB_KNOWN_ISSUES, encoding="utf-8")
        scripts = self.clone / ".claude" / "skills" / "sdlc-studio" / "scripts"
        scripts.mkdir(parents=True)
        (scripts / "gate.py").write_text(STUB_GATE, encoding="utf-8")
        (self.clone / "verdict").write_text("0\n", encoding="utf-8")
        (self.clone / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        self.ssh = self.tmp / "stub-ssh"
        self.ssh.write_text(STUB_SSH, encoding="utf-8")
        self.ssh.chmod(0o755)
        _git(self.clone, "config", "core.hooksPath", ".githooks")
        _git(self.clone, "config", "sdlc.gateSsh", str(self.ssh))
        if with_host:
            _git(self.clone, "config", "sdlc.gateHost", HOST)
        self.commit("seed")

    # --- the fixture's own git -----------------------------------------------------------------
    def commit(self, message: str, **files: str) -> str:
        for name, body in files.items():
            (self.clone / name).write_text(body, encoding="utf-8")
        (self.clone / "log.md").open("a", encoding="utf-8").write(message + "\n")
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-q", "-m", message)
        return _git(self.clone, "rev-parse", "HEAD").stdout.strip()

    def path(self) -> Path:
        d = self.tmp / "path"
        if not d.exists():
            d.mkdir()
            for tool in ("git", "bash"):
                (d / tool).symlink_to(shutil.which(tool))
            (d / "python3").write_text(f'#!/bin/sh\nexec {shlex.quote(sys.executable)} "$@"\n',
                                       encoding="utf-8")
            (d / "python3").chmod(0o755)
            (d / "gh").write_text(STUB_GH, encoding="utf-8")
            (d / "gh").chmod(0o755)
        return d

    def host_path(self) -> str:
        """The host's PATH: a normal one, with this interpreter first as `python3`."""
        d = self.tmp / "host-bin"
        if not d.exists():
            d.mkdir()
            (d / "python3").write_text(f'#!/bin/sh\nexec {shlex.quote(sys.executable)} "$@"\n',
                                       encoding="utf-8")
            (d / "python3").chmod(0o755)
        return os.pathsep.join([str(d), os.environ.get("PATH", "/usr/bin:/bin")])

    def push(self, *refspec: str, gh: str = "empty", fail: str = "", local: bool = False,
             no_verify: bool = False, host_path: str | None = None) -> subprocess.CompletedProcess:
        env = {"PATH": str(self.path()), "STUB_GH_MODE": gh, "STUB_SSH_FAIL": fail,
               "STUB_SSH_LOG": str(self.tmp / "ssh.log"), "STUB_GATE_LOG": str(self.tmp / "gate.log"),
               "STUB_PREREQ_LOG": str(self.tmp / "prereq.log"), "STUB_KI_LOG": str(self.tmp / "ki.log"),
               "STUB_HOST_HOME": str(self.host_home),
               "STUB_HOST_PATH": host_path if host_path is not None else self.host_path()}
        if local:
            env["SDLC_GATE_LOCAL"] = "1"
        args = ["push", "-q"] + (["--no-verify"] if no_verify else []) + ["origin", *(refspec or ("main",))]
        return _git(self.clone, *args, check=False, env=env)

    # --- what happened ---------------------------------------------------------------------------
    def _lines(self, name: str) -> list[str]:
        f = self.tmp / name
        return f.read_text(encoding="utf-8").splitlines() if f.exists() else []

    def gate_runs(self) -> list[dict]:
        return [json.loads(line) for line in self._lines("gate.log")]

    def on_host(self, run: dict) -> bool:
        return Path(run["cwd"]).resolve().is_relative_to(self.host_home.resolve())

    def ssh_calls(self) -> list[str]:
        return self._lines("ssh.log")

    def timings(self) -> dict:
        f = self.clone / "sdlc-studio" / ".local" / "gate-timings.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}

    def cleanup(self) -> None:
        subprocess.run(["chmod", "-R", "u+w", str(self.tmp)], capture_output=True)
        shutil.rmtree(self.tmp, ignore_errors=True)


class RemoteGatePushTests(unittest.TestCase):

    def setUp(self) -> None:
        self.fx = _HostClone()
        self.addCleanup(self.fx.cleanup)

    def test_the_host_judges_exactly_the_pushed_commit(self) -> None:
        """AC1. Mutants: the hook sends HEAD or the working tree instead of the pushed commit;
        it runs the gate locally; the host's red verdict is read as green; the host side is read
        from the working tree's copy of remote-gate.sh rather than the pushed commit's."""
        fx = self.fx
        seed = _git(fx.clone, "rev-parse", "HEAD").stdout.strip()
        _git(fx.clone, "switch", "-q", "-c", "side")
        red = fx.commit("red, on a branch HEAD will not reach", verdict="1\n")
        _git(fx.clone, "switch", "-q", "main")
        fx.commit("main moves on")                            # HEAD neither is nor contains `red`
        self.assertNotEqual(_git(fx.clone, "merge-base", "--is-ancestor", red, "HEAD", check=False).returncode,
                            0, "the fixture's pushed commit must lie outside HEAD's history")
        self.assertNotEqual(seed, red)
        (fx.clone / "verdict").write_text("0\n", encoding="utf-8")   # uncommitted: would flip it green
        local_copy = fx.clone / "tools" / "remote-gate.sh"
        local_copy.write_text(local_copy.read_text(encoding="utf-8").replace(
            'cmd_remote() {\n', 'cmd_remote() {\n  echo "WORKING-TREE-COPY-OF-THE-HOST-SIDE"\n', 1),
            encoding="utf-8")                                         # uncommitted, never pushed
        r = fx.push(f"{red}:refs/heads/main")
        self.assertNotEqual(r.returncode, 0, "a commit the host judged red was pushed:\n" + r.stderr)
        runs = fx.gate_runs()
        self.assertEqual(len(runs), 1, f"expected one gate run, got {runs}\n{r.stderr}")
        self.assertTrue(fx.on_host(runs[0]), f"the gate ran outside the host's checkout: {runs[0]}")
        self.assertEqual(runs[0]["head"], red, "the host did not judge exactly the pushed commit")
        self.assertIn("stub-lane STUBBED", r.stderr, "the host's output is not on the pusher's stderr")
        self.assertNotIn("WORKING-TREE-COPY-OF-THE-HOST-SIDE", r.stderr,
                         "the host ran the working tree's copy of its side, not the pushed commit's")
        self.assertEqual(_git(fx.remote, "rev-parse", "-q", "--verify", "refs/heads/main",
                              check=False).stdout.strip(), "", "the refused commit reached origin")

    def test_the_host_sees_the_same_range_and_tag(self) -> None:
        """AC2. Mutant: only the commit is sent, so the host's pushed range widens to all of
        history and its latest-tag lookup finds nothing."""
        fx = self.fx
        self.assertEqual(fx.push(no_verify=True).returncode, 0)     # origin/main exists
        _git(fx.clone, "tag", "-a", "v1.0.0", "-m", "v1.0.0")
        self.assertEqual(fx.push("v1.0.0", no_verify=True).returncode, 0)
        new = fx.commit("on top")
        local_range = _git(fx.clone, "log", new, "--not", "--remotes", "--format=%H").stdout.split()
        local_tag = _git(fx.clone, "describe", "--tags", "--abbrev=0", new).stdout.strip()
        r = fx.push()
        self.assertEqual(r.returncode, 0, r.stderr)
        run = fx.gate_runs()[-1]
        self.assertTrue(fx.on_host(run))
        self.assertEqual(run["range"], local_range, "the host computed a different pushed range")
        self.assertEqual(local_tag, "v1.0.0")
        self.assertEqual(run["tag"], local_tag, "the host resolved a different latest tag")
        # A tag and a remote-tracking branch the host has been sent, then withdrawn here, both on
        # a commit inside the next push's range: the host's copy must follow this clone, not
        # everything it was ever sent.
        published = _git(fx.clone, "rev-parse", "origin/main").stdout.strip()
        x = fx.commit("x, which a withdrawn tag and branch point at")
        _git(fx.clone, "tag", "-a", "v2.0.0", "-m", "v2.0.0")
        _git(fx.clone, "update-ref", "refs/remotes/origin/feature", x)
        y = fx.commit("y")
        r = fx.push(f"{published}:refs/heads/older")         # judged on the host: it now holds both refs
        self.assertEqual(r.returncode, 0, r.stderr)
        _git(fx.clone, "tag", "-d", "v2.0.0")
        _git(fx.clone, "update-ref", "-d", "refs/remotes/origin/feature")
        local_range = _git(fx.clone, "log", y, "--not", "--remotes", "--format=%H").stdout.split()
        local_tag = _git(fx.clone, "describe", "--tags", "--abbrev=0", y).stdout.strip()
        self.assertEqual(sorted(local_range), sorted([x, y]))
        self.assertEqual(local_tag, "v1.0.0")
        r = fx.push()
        self.assertEqual(r.returncode, 0, r.stderr)
        run = fx.gate_runs()[-1]
        self.assertEqual(run["head"], y)
        self.assertEqual(run["tag"], local_tag, "the host still resolves a tag this clone withdrew")
        self.assertEqual(sorted(run["range"]), sorted(local_range),
                         "a remote-tracking branch this clone pruned still narrows the host's range")

    def test_a_tag_is_judged_at_the_release_boundary_on_the_host(self) -> None:
        """AC3. Mutants: the host always runs `--boundary push`; the known-issues check moves to
        the host or is skipped; the host's output is discarded."""
        fx = self.fx
        tip = fx.commit("release me")
        _git(fx.clone, "tag", "-a", "v2.0.0", "-m", "v2.0.0")
        r = fx.push("v2.0.0")
        self.assertEqual(r.returncode, 0, "a green host run refused the tag:\n" + r.stderr)
        runs = fx.gate_runs()
        self.assertEqual(len(runs), 1, runs)
        self.assertTrue(fx.on_host(runs[0]))
        self.assertEqual(runs[0]["argv"], ["--boundary", "release"])
        self.assertEqual(runs[0]["head"], tip)
        ki = fx._lines("ki.log")
        self.assertTrue(ki, "the known-issues check did not run")
        self.assertTrue(all(Path(line.split()[0]).resolve() == fx.clone.resolve() for line in ki),
                        f"the known-issues check did not run locally: {ki}")
        self.assertIn(f"check --at {_git(fx.clone, 'rev-parse', 'v2.0.0').stdout.strip()}", ki[0])
        self.assertIn("stub-lane STUBBED", r.stderr, "the host's output is not on the pusher's stderr")
        # A branch pushed beside a tag on an OLDER, red commit: each distinct commit is judged,
        # each at its own boundary (BG0870) - never only the first, never all at release.
        (fx.tmp / "gate.log").unlink()
        old_red = fx.commit("an older red release", verdict="1\n")
        _git(fx.clone, "tag", "-a", "v3.0.0", "-m", "v3.0.0")
        tip = fx.commit("a green tip on main", verdict="0\n")
        r = fx.push("main", "v3.0.0")
        self.assertNotEqual(r.returncode, 0, "the red tagged commit was never judged:\n" + r.stderr)
        judged = {run["head"]: run["argv"] for run in fx.gate_runs()}
        self.assertEqual(judged.get(tip), ["--boundary", "push"], f"the branch tip: {judged}")
        self.assertEqual(judged.get(old_red), ["--boundary", "release"], f"the tagged commit: {judged}")

    def test_a_transport_failure_refuses_and_names_the_fallback(self) -> None:
        """AC4. Mutants: a transport failure falls back to the local gate; it is read as a pass;
        the refusal does not name the host or SDLC_GATE_LOCAL=1."""
        fx = self.fx
        fx.commit("one")
        for when in ("before", "during"):
            with self.subTest(when=when):
                (fx.tmp / "gate.log").unlink(missing_ok=True)
                fx.commit(f"push {when}")
                r = fx.push(fail=when)
                self.assertNotEqual(r.returncode, 0, f"a {when}-gate transport failure pushed:\n" + r.stderr)
                lines = r.stderr.splitlines()
                refusal = next((i for i, ln in enumerate(lines) if "could not judge commit" in ln), None)
                self.assertIsNotNone(refusal, f"no transport refusal line:\n{r.stderr}")
                self.assertIn(HOST, lines[refusal], "the refusal line does not name the host")
                self.assertTrue(any("SDLC_GATE_LOCAL=1" in ln for ln in lines[refusal + 1:refusal + 4]),
                                "the refusal does not name SDLC_GATE_LOCAL=1")
                runs = fx.gate_runs()
                self.assertFalse([run for run in runs if not fx.on_host(run)],
                                 f"the gate ran locally after a transport failure: {runs}")
                if when == "before":
                    self.assertEqual(runs, [], "a gate ran though the host was never reached")

    def test_the_gate_runs_where_the_configuration_says(self) -> None:
        """AC5. Mutants: SDLC_GATE_LOCAL=1 ignored; the local path taken with a host configured;
        the host path taken with none."""
        fx = self.fx
        cases = (("no host", False, False), ("host, SDLC_GATE_LOCAL=1", True, True), ("host", True, False))
        for label, host, local in cases:
            with self.subTest(case=label):
                if host:
                    _git(fx.clone, "config", "sdlc.gateHost", HOST)
                else:
                    _git(fx.clone, "config", "--unset", "sdlc.gateHost", check=False)
                (fx.tmp / "gate.log").unlink(missing_ok=True)
                fx.commit(label)
                r = fx.push(local=local)
                self.assertEqual(r.returncode, 0, r.stderr)
                runs = fx.gate_runs()
                self.assertEqual(len(runs), 1, f"{label}: expected one gate run, got {runs}")
                self.assertEqual(fx.on_host(runs[0]), host and not local,
                                 f"{label}: the gate ran in the wrong place: {runs[0]['cwd']}")
                if host and not local:
                    self.assertEqual(fx.timings().get("boundary-push"), local_series,
                                     "a host run's duration entered the local series")
                    self.assertIn(f"pre-push: boundary-push@{HOST}", r.stderr,
                                  "the host push's cost line is not read from the host's own series")
                local_series = fx.timings().get("boundary-push")
        self.assertIn(f"boundary-push@{HOST}", fx.timings(), "the host run's duration was not recorded")

    def test_the_host_path_keeps_the_red_main_read_and_the_preflight(self) -> None:
        """AC6. Mutants: the host path skips the red-main read (D0181); it reads it after the
        send; it skips the preflight on the host's interpreter, or runs the gate past it."""
        fx = self.fx
        fx.commit("red main")
        r = fx.push(gh="red")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("40000000001", r.stderr, "the red run was not named")
        self.assertEqual(fx.ssh_calls(), [], "something was sent to the host before the red main was read")
        fx.commit("a prerequisite the host lacks", **{"prereq-rc": "1\n"})
        r = fx.push()
        self.assertNotEqual(r.returncode, 0, "a host lacking a prerequisite judged the push")
        prereq = fx._lines("prereq.log")
        self.assertTrue(prereq and all(Path(p).resolve().is_relative_to(fx.host_home.resolve())
                                       for p in prereq),
                        f"the preflight did not run on the host's interpreter: {prereq}")
        self.assertEqual(fx.gate_runs(), [], "the host's gate ran past a refusing preflight")
        self.assertIn("refused before the push boundary gate runs", r.stderr)
        self.assertNotIn(f"boundary-push@{HOST}", fx.timings(),
                         "a host run that never reached its gate was recorded as a gate duration")

    def test_a_host_setup_fault_is_named_and_records_no_run(self) -> None:
        """Round-1 review: a host whose ssh PATH has no git is a setup fault there, named as one
        - never a connection failure - and no gate duration is recorded for it."""
        fx = self.fx
        fx.commit("a host without git")
        no_git = str(fx.tmp / "host-bin")
        fx.host_path()                                         # creates host-bin with python3 only
        r = fx.push(host_path=no_git)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("git must be on the PATH", r.stderr, r.stderr)
        self.assertNotIn("connection failed", r.stderr, "a setup fault on the host was named a connection failure")
        self.assertEqual(fx.gate_runs(), [])
        self.assertNotIn(f"boundary-push@{HOST}", fx.timings())


if __name__ == "__main__":
    unittest.main()
