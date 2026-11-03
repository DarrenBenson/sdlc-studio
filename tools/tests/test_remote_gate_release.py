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
