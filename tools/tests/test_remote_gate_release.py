"""US1114: `remote-gate.sh push --commit <sha> --release` runs that commit's release gate on the gate
host, and records it green here only when the host passed it.

Built on test_remote_gate_push.py's fixture: a clone, its origin, a fake host's home, and a stubbed
ssh that runs each command there under `env -i` with only HOME, PATH and its own log paths, so no
SDLC_* setting of this side reaches the host unless the script sends it. The clone carries the real remote-gate.sh, and the real
release_cut.py with what it imports, so the green marker is written by the shipped
`release_cut.py record-green`.

The gate either side runs is a stub, but not a single process judged by its own word. It parses
its arguments with the REAL gate's parser, reads the verify settings with the real gate's readers,
and runs, inside the real gate's `boundary_suite_env`, a child that reports the environment a
verifier is handed and a `boundary_only` verifier built on the real `boundary.py`, which is red
wherever it executes. So what the tests compare is what the gate's runners see, on the host and
here. It exits by the integer its tree's committed `verdict` file holds.
"""
# test-census-subject: tools/remote-gate.sh
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_remote_gate_push import REPO, _git, _HostClone  # noqa: E402

SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
MARKER = Path("sdlc-studio") / ".local" / "release-gate-green.json"
COUNTS = ("SDLC_VERIFY_TIMEOUT", "SDLC_VERIFY_BATCH_TIMEOUT", "SDLC_VERIFY_WORKERS")
SUITE = "SDLC_STUDIO_BOUNDARY_SUITE"

#: The stub gate. Records what it was asked, what it reads and what its runners are handed.
RELEASE_GATE = textwrap.dedent('''
    import json, os, subprocess, sys
    from pathlib import Path
    sys.dont_write_bytecode = True
    sys.path.insert(0, SCRIPTS)
    import gate as real
    NAMES = ("SDLC_VERIFY_TIMEOUT", "SDLC_VERIFY_BATCH_TIMEOUT", "SDLC_VERIFY_WORKERS",
             "SDLC_STUDIO_BOUNDARY_SUITE")
    CHILD = "import json, os, sys; print(json.dumps({n: os.environ.get(n) for n in sys.argv[1:]}))"
    args = real.build_parser().parse_args(sys.argv[1:])
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    verdict = int(Path("verdict").read_text().strip()) if Path("verdict").exists() else 0
    record = {"argv": sys.argv[1:], "cwd": os.getcwd(), "head": head, "verdict": verdict,
              "env": {n: os.environ.get(n) for n in NAMES},
              "reads": {"timeout": real._verify_timeout(),
                        "batch": real._ceiling(real.VERIFY_BATCH_TIMEOUT_ENV, real.VERIFY_BATCH_TIMEOUT),
                        "workers": real._verify_workers()[0]}}
    with real.boundary_suite_env(real.resolve_boundary(args)):
        child = subprocess.run([sys.executable, "-c", CHILD, *NAMES], capture_output=True, text=True)
        record["child_env"] = json.loads(child.stdout)
        ran = subprocess.run([sys.executable, "-B", "-m", "unittest", "-v", "verifier_test"],
                             capture_output=True, text=True)
        record["verifier"] = {"rc": ran.returncode, "skipped": "skipped=1" in ran.stderr}
    Path(os.environ["STUB_GATE_LOG"]).open("a").write(json.dumps(record) + "\\n")
    if Path("orphan").exists():
        # a process the gate leaves behind, outside its session, still holding its output for
        # 15 s, that marks its own exit beside the log
        done = Path(os.environ["STUB_GATE_LOG"]).with_name("orphan.done")
        orphan = subprocess.Popen(["sh", "-c", 'sleep 15; : > "$1"', "orphan", str(done)],
                                  start_new_session=True)
        Path(os.environ["STUB_GATE_LOG"]).with_name("orphan.pid").write_text(str(orphan.pid))
    print("  stub-stderr-line", file=sys.stderr)
    print(f"  [{'FAIL' if verdict else 'PASS'}] stub-release STUBBED")
    raise SystemExit(verdict)
''')

#: A criterion's verifier marked `boundary_only`, red wherever it executes.
VERIFIER = textwrap.dedent('''
    import sys, unittest
    sys.path.insert(0, TESTS)
    from boundary import boundary_only

    class Criterion(unittest.TestCase):
        @boundary_only("a fixture criterion only a boundary run executes, for US1114 AC4")
        def test_criterion(self):
            self.fail("executed: this criterion is red wherever a boundary run reaches it")
''')


class _ReleaseClone(_HostClone):
    """_HostClone whose gate is the release stub, with the real release_cut.py beside it."""

    def __init__(self) -> None:
        super().__init__()
        scripts = self.clone / ".claude" / "skills" / "sdlc-studio" / "scripts"
        (scripts / "gate.py").write_text(f"SCRIPTS = {str(SCRIPTS)!r}\n" + RELEASE_GATE,
                                         encoding="utf-8")
        for name in ("release_cut.py", "changelog.py"):
            shutil.copy(SCRIPTS / name, scripts / name)
        shutil.copytree(SCRIPTS / "lib", scripts / "lib",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.clone / "verifier_test.py").write_text(
            f"TESTS = {str(SCRIPTS / 'tests')!r}\n" + VERIFIER, encoding="utf-8")
        self.commit("the release gate stub")
        self.marker = self.clone / MARKER

    def env(self, **extra: str) -> dict:
        """This side's environment: no SDLC_* or GIT_* of the run that holds the test."""
        base = {k: v for k, v in os.environ.items()
                if not k.startswith(("GIT_", "SDLC_")) and k != "PYTHONPATH"}
        base.update({"PATH": str(self.path()), "STUB_GH_MODE": "empty",
                     "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                     "STUB_SSH_LOG": str(self.tmp / "ssh.log"),
                     "STUB_GATE_LOG": str(self.tmp / "gate.log"),
                     "STUB_PREREQ_LOG": str(self.tmp / "prereq.log"),
                     "STUB_HOST_HOME": str(self.host_home), "STUB_HOST_PATH": self.host_path()})
        base.update(extra)
        return base

    def release(self, commit: str, *extra: str, fail: str = "", **env: str) -> subprocess.CompletedProcess:
        """`remote-gate.sh push --commit <commit> --release`, from the clone, with `env` set here."""
        return subprocess.run(["bash", "tools/remote-gate.sh", "push", "--commit", commit, "--release",
                               *extra], cwd=self.clone, env=self.env(STUB_SSH_FAIL=fail, **env),
                              capture_output=True, text=True, timeout=300)

    def local_release(self, **env: str) -> subprocess.CompletedProcess:
        """The local route: the same gate, `gate.py --release`, run here on HEAD."""
        return subprocess.run(["python3", ".claude/skills/sdlc-studio/scripts/gate.py", "--release"],
                              cwd=self.clone, env=self.env(**env), capture_output=True, text=True,
                              timeout=300)

    def host_env(self, body: str) -> None:
        """The host's own ~/sdlc-gate/gate-env.sh."""
        gate_dir = self.host_home / "sdlc-gate"
        gate_dir.mkdir(parents=True, exist_ok=True)
        (gate_dir / "gate-env.sh").write_text(body, encoding="utf-8")

    def last_run(self, *, on_host: bool) -> dict:
        runs = [run for run in self.gate_runs() if self.on_host(run) == on_host]
        assert runs, f"no gate run {'on the host' if on_host else 'here'}: {self.gate_runs()}"
        return runs[-1]

    def head(self) -> str:
        return _git(self.clone, "rev-parse", "HEAD").stdout.strip()


class RemoteReleaseGateTests(unittest.TestCase):

    def setUp(self) -> None:
        self.fx = _ReleaseClone()
        self.addCleanup(self.fx.cleanup)

    def test_the_host_runs_the_commits_own_release_gate(self) -> None:
        """AC1. Mutants: the host runs `gate.py --boundary release`, which binds no verify lane;
        HEAD is judged in place of <sha>; a refusal exits 0; the gate's own exit 2, 4 or 255
        reaches this side unmapped, as could-not-start, a host setup fault or a dropped
        connection; a failed connection or a host setup fault is read as a refusal."""
        fx = self.fx
        green = fx.commit("a green candidate")
        fx.commit("HEAD moves on, and is red", verdict="1\n")
        r = fx.release(green)
        self.assertEqual(r.returncode, 0, r.stderr)
        runs = fx.gate_runs()
        self.assertEqual(len(runs), 1, runs)
        self.assertTrue(fx.on_host(runs[0]), f"the release gate ran outside the host: {runs[0]}")
        self.assertEqual(runs[0]["argv"], ["--release"], "the host did not run gate.py --release")
        self.assertEqual(runs[0]["head"], green, "the host did not judge exactly <sha>")
        self.assertIn("stub-release STUBBED", r.stderr, "the host's output is not on this side")
        for code in ("1", "2", "4", "255"):
            with self.subTest(gate_exit=code):
                refused = fx.commit(f"the gate exits {code}", verdict=f"{code}\n")
                r = fx.release(refused)
                self.assertEqual(r.returncode, 1, f"the host's gate exited {code}:\n{r.stderr}")
                self.assertEqual(fx.gate_runs()[-1]["head"], refused, "the gate never ran")
                self.assertIn("refused commit", r.stderr)
        sha = fx.commit("green again", verdict="0\n")
        for when in ("before", "during"):
            with self.subTest(connection=when):
                r = fx.release(sha, fail=when)
                self.assertEqual(r.returncode, 3, f"a connection failed {when} the gate:\n{r.stderr}")
                self.assertIn("run the release gate on this machine", r.stderr,
                              "the fallback named is not the release gate's")
        for extra in (("--suite", "all"), ("--boundary", "release"), ("--carry", "SDLC_VERIFY_TIMEOUT=5")):
            with self.subTest(combined=extra):
                calls = len(fx.ssh_calls())
                r = fx.release(sha, *extra)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertEqual(len(fx.ssh_calls()), calls, "a refused command line connected")
        lacking = fx.commit("a prerequisite the host lacks", **{"prereq-rc": "1\n"})
        r = fx.release(lacking)
        self.assertEqual(r.returncode, 4, f"a host setup fault:\n{r.stderr}")
        self.assertIn("did not run the release gate", r.stderr)

    def test_the_verify_settings_reach_the_host_and_a_bad_value_is_refused(self) -> None:
        """AC2. Mutants: the settings are not sent, so the host reads its defaults; they are sent
        but the host's gate-env.sh overrides them; one unset here keeps the host's value; a value
        that is not a positive integer is sent, or reaches the remote command line unvalidated."""
        fx = self.fx
        fx.host_env("export SDLC_VERIFY_TIMEOUT=999 SDLC_VERIFY_BATCH_TIMEOUT=999 SDLC_VERIFY_WORKERS=99\n")
        sha = fx.head()
        settings = {"SDLC_VERIFY_TIMEOUT": "600", "SDLC_VERIFY_BATCH_TIMEOUT": "4000",
                    "SDLC_VERIFY_WORKERS": "3"}
        r = fx.release(sha, **settings)
        self.assertEqual(r.returncode, 0, r.stderr)
        host = fx.last_run(on_host=True)
        self.assertEqual(fx.local_release(**settings).returncode, 0)
        local = fx.last_run(on_host=False)
        self.assertEqual(local["reads"], {"timeout": 600, "batch": 4000, "workers": 3})
        self.assertEqual(host["reads"], local["reads"], "the host's gate read other settings")
        for name, value in settings.items():
            self.assertEqual(host["child_env"][name], value, f"{name} did not reach the gate's runners")
        r = fx.release(sha)                              # nothing set here: nothing set there
        self.assertEqual(r.returncode, 0, r.stderr)
        host = fx.last_run(on_host=True)
        self.assertEqual(fx.local_release().returncode, 0)
        self.assertEqual(host["reads"], fx.last_run(on_host=False)["reads"])
        self.assertEqual({n: host["env"][n] for n in COUNTS}, dict.fromkeys(COUNTS),
                         "a setting unset here was set on the host")
        r = fx.release(sha, SDLC_VERIFY_WORKERS="007")   # a leading zero is still a positive integer
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(fx.last_run(on_host=True)["reads"]["workers"], 7)
        calls, runs = len(fx.ssh_calls()), len(fx.gate_runs())
        for name in COUNTS:
            for bad in ("0", "00", "-5", "+5", "1.5", "6e2", " 600", "", "abc", "600;touch PWNED",
                        "600';touch PWNED;'"):
                with self.subTest(name=name, value=bad):
                    r = fx.release(sha, **{name: bad})
                    self.assertEqual(r.returncode, 2, r.stderr)
                    self.assertIn(name, r.stderr, "the refusal does not name the setting")
                    self.assertIn("positive integer", r.stderr)
        self.assertEqual(len(fx.ssh_calls()), calls, "a refused setting still connected")
        self.assertEqual(len(fx.gate_runs()), runs, "a refused setting still ran a gate")
        self.assertEqual([p for p in fx.tmp.rglob("PWNED")], [], "a value ran as a command")
        # The host side holds the same line against a command line it did not get from `push`.
        for carried in ("SDLC_VERIFY_TIMEOUT=0", "PATH=/nowhere", "SDLC_VERIFY_WORKERS"):
            with self.subTest(carried=carried):
                r = subprocess.run(["bash", str(fx.clone / "tools" / "remote-gate.sh"), "remote",
                                    "--clone", "c", "--commit", sha, "--run", "r1", "--release",
                                    "--carry", carried], cwd=fx.tmp, capture_output=True, text=True,
                                   env=fx.env(HOME=str(fx.tmp / "nowhere")), timeout=60)
                self.assertEqual(r.returncode, 4, r.stderr)
                self.assertIn(carried, r.stderr)
        self.assertFalse((fx.tmp / "nowhere").exists(), "the host side acted on a refused setting")

    def test_green_is_recorded_only_for_the_sha_the_host_passed(self) -> None:
        """AC3. Mutants: green is recorded before the exit is read, or on any exit, or for HEAD
        rather than <sha>, or for <sha> as typed rather than the commit it names; a connection
        that fails after the host's gate passed records green; the marker is rewritten on a
        refusal with the same content."""
        fx = self.fx
        red = fx.commit("a red candidate", verdict="1\n")
        self.assertEqual(fx.release(red).returncode, 1)
        self.assertFalse(fx.marker.exists(), "a refusal wrote a green marker")
        before = b'{"commit":  "0123456789abcdef0123456789abcdef01234567"}\n\n'
        fx.marker.parent.mkdir(parents=True, exist_ok=True)
        fx.marker.write_bytes(before)
        self.assertEqual(fx.release(red).returncode, 1)
        self.assertEqual(fx.marker.read_bytes(), before, "a refusal touched the marker")
        green = fx.commit("a green candidate", verdict="0\n")
        for when in ("before", "during"):
            with self.subTest(connection=when):
                self.assertEqual(fx.release(green, fail=when).returncode, 3)
                self.assertEqual(fx.marker.read_bytes(), before, f"a connection failed {when}")
        dropped = fx.gate_runs()[-1]
        self.assertEqual((dropped["head"], dropped["verdict"]), (green, 0),
                         "the host's gate never passed before the connection dropped")
        lacking = fx.commit("a prerequisite the host lacks", **{"prereq-rc": "1\n"})
        self.assertEqual(fx.release(lacking).returncode, 4)
        self.assertEqual(fx.marker.read_bytes(), before, "a host setup fault touched the marker")
        fx.commit("HEAD moves on", **{"prereq-rc": "0\n"})
        r = fx.release(green[:12])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotEqual(fx.head(), green)
        self.assertEqual(json.loads(fx.marker.read_text(encoding="utf-8")), {"commit": green},
                         "the green does not name exactly the commit the host passed")

    def _boundary(self, commit: str) -> subprocess.CompletedProcess:
        """`remote-gate.sh push --commit <commit> --boundary push`, from the clone."""
        return subprocess.run(["bash", "tools/remote-gate.sh", "push", "--commit", commit,
                               "--boundary", "push"], cwd=self.fx.clone,
                              env=self.fx.env(STUB_SSH_FAIL=""), capture_output=True, text=True,
                              timeout=300)

    def test_the_log_a_refusal_names_is_kept_until_the_next_run(self) -> None:
        """BG1514 AC3. A refused boundary run names its full log, and that file exists at the
        named path, holds the gate's whole output, outlives the run's own cleanup, and is
        replaced only by the next boundary run for the clone. MUTANTS: name a path nothing wrote
        (as the gate's own log is, for a lane that is not the suite); write the log inside the
        run's directory, which the cleanup removes; keep the first run's log through the next."""
        fx = self.fx
        red = fx.commit("a refused candidate", verdict="1\n")
        r = self._boundary(red)
        self.assertEqual(r.returncode, 1, r.stderr)
        named = [ln for ln in r.stderr.splitlines() if "the full log is on" in ln]
        self.assertEqual(1, len(named), r.stderr)
        path = Path(named[0].rsplit(" at ", 1)[1])
        self.assertTrue(path.is_absolute(), named[0])
        self.assertTrue(path.is_relative_to(fx.host_home), f"{path} is not on the host")
        self.assertTrue(path.is_file(), f"the refusal names {path}, which does not exist")
        kept = path.read_text(encoding="utf-8")
        self.assertIn("stub-release STUBBED", kept, "the log does not hold the gate's output")
        self.assertIn("FAIL", kept)
        self.assertIn("stub-stderr-line", kept, "the gate's stderr is not in the log")
        self.assertEqual([], list((fx.host_home / "sdlc-gate" / "runs").iterdir()),
                         "the run's own directory outlived its cleanup")
        self.assertEqual(kept, path.read_text(encoding="utf-8"), "the log changed after the run")
        green = fx.commit("a green candidate", verdict="0\n")
        r = self._boundary(green)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("the full log is on", r.stderr, "a green run names a log")
        replaced = path.read_text(encoding="utf-8")
        self.assertIn("PASS", replaced)
        self.assertNotIn("FAIL", replaced, "the first run's log outlived the next boundary run")
        # A release run is no boundary run: its refusal names no log and leaves the kept one alone.
        refused = fx.commit("a refused release", verdict="1\n")
        r = fx.release(refused)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertNotIn("the full log is on", r.stderr)
        self.assertEqual(replaced, path.read_text(encoding="utf-8"),
                         "a release run replaced the boundary log")

    def test_a_process_the_gate_orphans_cannot_hold_the_run_open(self) -> None:
        """BG1514 AC3. The gate leaves a process behind that holds its output for 15 s: the run
        waits for the copy to the log for a bounded 5 s and then ends, with that process still
        alive and the log whole. MUTANTS: no wait at all (the run ends at once); no bound (the
        run lasts as long as the orphan)."""
        import time  # noqa: PLC0415
        fx = self.fx
        red = fx.commit("a refused candidate that leaves a process behind", verdict="1\n",
                        orphan="1\n")
        started = time.monotonic()
        r = self._boundary(red)
        took = time.monotonic() - started
        pid_file = fx.tmp / "orphan.pid"
        self.assertTrue(pid_file.is_file(), r.stderr)
        pid = int(pid_file.read_text(encoding="utf-8"))
        try:
            self.assertEqual(r.returncode, 1, r.stderr)
            os.kill(pid, 0)         # raises when the process is gone: the run outlasted it
            self.assertGreaterEqual(took, 4.0, "the run did not wait for the copy to the log")
            named = [ln for ln in r.stderr.splitlines() if "the full log is on" in ln]
            log = Path(named[0].rsplit(" at ", 1)[1]).read_text(encoding="utf-8")
            self.assertIn("[FAIL] stub-release STUBBED", log)
        finally:
            try:
                os.killpg(pid, 9)
            except ProcessLookupError:
                pass

    def test_a_killed_run_leaves_no_copy_to_the_log_behind(self) -> None:
        """BG1514 AC3. The pusher goes a second after the gate exited, while a process the gate
        orphaned still holds its output for 15 s, so the host stops the run in its bounded wait
        for the copy to the log. The cleanup ends that copy and removes the pipe it read: the
        push's channel closes while the orphan still runs, not when it exits, and the log keeps
        what was copied. MUTANT: the cleanup leaves the copy running (the channel then stays open
        until the orphan has exited)."""
        import signal  # noqa: PLC0415
        import time  # noqa: PLC0415
        fx = self.fx
        red = fx.commit("a refused candidate that leaves a process behind", verdict="1\n",
                        orphan="1\n")
        pid_file = fx.tmp / "orphan.pid"
        push = subprocess.Popen(["bash", "tools/remote-gate.sh", "push", "--commit", red,
                                 "--boundary", "push"], cwd=fx.clone,
                                env=fx.env(STUB_SSH_FAIL=""), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pid = None
        try:
            waited = time.monotonic() + 120
            while pid is None and push.poll() is None and time.monotonic() < waited:
                text = pid_file.read_text(encoding="utf-8") if pid_file.is_file() else ""
                pid = int(text) if text.strip() else None
                time.sleep(0.1)
            self.assertIsNotNone(pid, "the gate left no process behind")
            time.sleep(1.0)
            self.assertIsNone(push.poll(), "the run ended before the pusher went")
            push.send_signal(signal.SIGTERM)
            _out, err = push.communicate(timeout=60)
            self.assertFalse((fx.tmp / "orphan.done").exists(),
                             "the push's channel stayed open until the orphan exited: the copy to "
                             "the log outlived the killed run")
            self.assertEqual([], list((fx.host_home / "sdlc-gate" / "runs").iterdir()),
                             "the run's directory, and the pipe in it, outlived the cleanup")
            kept = next((fx.host_home / "sdlc-gate" / "local").glob("*/boundary-last.log"))
            self.assertIn("[FAIL] stub-release STUBBED", kept.read_text(encoding="utf-8"), err)
        finally:
            if push.poll() is None:
                push.kill()
                push.communicate()
            if pid is not None:
                try:
                    os.killpg(pid, 9)
                except ProcessLookupError:
                    pass

    def test_only_a_boundary_run_replaces_the_kept_log(self) -> None:
        """BG1514 AC3. The kept log is the last boundary run's: a suite run and a commit's
        selection that follow a refused boundary run, each printing what the boundary run did
        not, leave it as it was. MUTANTS: the suite run, or the selection, copies its own output
        to the kept log, so the refusal names a log another run has since rewritten."""
        fx = self.fx
        suite = "#!/usr/bin/env bash\necho \"  stub suite $1 ran\"\nexit 1\n"
        red = fx.commit("a refused candidate", verdict="1\n", **{"tools/run-suite.sh": suite})
        r = self._boundary(red)
        self.assertEqual(r.returncode, 1, r.stderr)
        kept = next((fx.host_home / "sdlc-gate" / "local").glob("*/boundary-last.log"))
        refused = kept.read_text(encoding="utf-8")
        self.assertIn("[FAIL] stub-release STUBBED", refused)
        r = subprocess.run(["bash", "tools/remote-gate.sh", "push", "--commit", red, "--suite",
                            "tools"], cwd=fx.clone, env=fx.env(STUB_SSH_FAIL=""),
                           capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("stub suite tools ran", r.stderr, "the suite did not run on the host")
        self.assertEqual(refused, kept.read_text(encoding="utf-8"), "a suite run replaced the log")
        (fx.clone / "verdict").write_text("0\n", encoding="utf-8")
        _git(fx.clone, "add", "verdict")
        r = subprocess.run(["bash", "tools/remote-gate.sh", "staged", "--test", "verifier_test.py"],
                           cwd=fx.clone, env=fx.env(STUB_SSH_FAIL=""), capture_output=True,
                           text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("[PASS] stub-release STUBBED", r.stderr, "the selection did not run")
        self.assertEqual(refused, kept.read_text(encoding="utf-8"),
                         "a commit's selection replaced the log")

    def test_the_host_and_local_routes_agree_on_boundary_only_verifiers(self) -> None:
        """AC4. Mutants: the host exports SDLC_STUDIO_BOUNDARY_SUITE=1 for the release gate while
        a local `gate.py --release` does not; the host drops it, or changes its value, where this
        side set it; the host's gate-env.sh decides it."""
        fx = self.fx
        fx.host_env(f"export {SUITE}=1\n")
        sha = fx.head()
        cases = (({}, False), ({SUITE: "1"}, True), ({SUITE: "0"}, False), ({SUITE: ""}, False))
        for env, executes in cases:
            with self.subTest(env=env):
                r = fx.release(sha, **env)
                self.assertEqual(r.returncode, 0, r.stderr)
                host = fx.last_run(on_host=True)
                self.assertEqual(fx.local_release(**env).returncode, 0)
                local = fx.last_run(on_host=False)
                self.assertEqual(local["verifier"]["skipped"], not executes,
                                 f"the fixture's verifier does not follow the switch: {local}")
                self.assertEqual(host["child_env"][SUITE], local["child_env"][SUITE],
                                 "the two routes hand the verifier different switches")
                self.assertEqual(host["verifier"], local["verifier"],
                                 "the verifier's verdict depends on the route")
        calls = len(fx.ssh_calls())
        r = fx.release(sha, **{SUITE: "1';touch PWNED;'"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(SUITE, r.stderr, "the refusal does not name the setting")
        self.assertEqual(len(fx.ssh_calls()), calls, "a refused switch still connected")


if __name__ == "__main__":
    unittest.main()
