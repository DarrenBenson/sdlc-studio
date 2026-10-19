"""US1076: runs on a gate host are serialised, and an abandoned push stops its run.

Built on test_remote_gate_push.py's fixture, with two stubs made realistic for what this unit
claims:

* the TRANSPORT relays the pusher's stdin to a host command it starts in a session of its own, as
  a real host's sshd would - so a signal to the pusher's process group never reaches the host side
  directly, and the only news the host gets of an abandoned push is the end of that stdin. When the
  file STUB_SSH_DROP names appears, it closes the host's stdin and exits 255: a dropped connection.
* the GATE starts a CHILD, as the real gate starts its suite's workers, records both pids and its
  checkout, then blocks until the file STUB_RELEASE names exists. Killing the gate's pid alone would
  leave the child running, so a test that sees only the leader cannot tell the two apart.

Every wait synchronises on an event (a record written, a directory made, a line printed) under a
ceiling, never on a sleep: these tests run on a gate host shared with a CI runner, where a
wall-clock bound has failed before (BG1031). The ceiling is generous because it is only a ceiling:
the first full-suite run of this module on that host, eight-way parallel beside a CI job, took
more than a minute to bring one push's gate up. Each abandonment case has a fixture of its own,
and a case that fails kills its own push and releases its gate, so it cannot leak into the next.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import textwrap
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_remote_gate_push import HOST, _git, _HostClone  # noqa: E402

CEILING = 240.0

BLOCKING_GATE = textwrap.dedent('''
    import json, os, signal, subprocess, sys, time
    from pathlib import Path
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    release = os.environ["STUB_RELEASE"]
    child = subprocess.Popen([sys.executable, "-c",
        "import os, sys, time\\nwhile not os.path.exists(sys.argv[1]): time.sleep(0.05)", release])
    Path(os.environ["STUB_GATE_LOG"]).open("a").write(json.dumps(
        {"pid": os.getpid(), "child": child.pid, "cwd": os.getcwd(), "head": head,
         "argv": sys.argv[1:], "sigint_ignored": signal.getsignal(signal.SIGINT) == signal.SIG_IGN})
        + "\\n")
    print("  [PASS] stub-lane STUBBED", flush=True)
    release = Path(os.environ["STUB_RELEASE"])
    deadline = time.monotonic() + 180
    while not release.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
''')

RELAY_SSH = textwrap.dedent('''
    #!/usr/bin/env python3
    import os, subprocess, sys, threading, time
    args, i = sys.argv[1:], 0
    while i < len(args):
        if args[i] in ("-o", "-p", "-l", "-i", "-F"):
            i += 2; continue
        if args[i] == "--":
            i += 1; break
        if args[i].startswith("-"):
            i += 1; continue
        break
    host, cmd = args[i], " ".join(args[i + 1:])
    with open(os.environ["STUB_SSH_LOG"], "a") as log:
        log.write(host + "\\t" + cmd + "\\n")
    env = {"HOME": os.environ["STUB_HOST_HOME"], "PATH": os.environ["STUB_HOST_PATH"]}
    for key in ("STUB_GATE_LOG", "STUB_PREREQ_LOG", "STUB_RELEASE"):
        if key in os.environ:
            env[key] = os.environ[key]
    child = subprocess.Popen(["bash", "-c", cmd], cwd=env["HOME"], env=env, stdin=subprocess.PIPE,
                             start_new_session=True)
    def relay():
        try:
            while True:
                chunk = os.read(0, 65536)
                if not chunk:
                    break
                child.stdin.write(chunk)
                child.stdin.flush()
        except OSError:
            pass
        try:
            child.stdin.close()
        except OSError:
            pass
    threading.Thread(target=relay, daemon=True).start()
    drop = os.environ.get("STUB_SSH_DROP", "")
    while child.poll() is None:
        if drop and os.path.exists(drop):
            try:
                child.stdin.close()
            except OSError:
                pass
            os._exit(255)
        time.sleep(0.05)
    sys.exit(child.returncode)
''').lstrip()


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _until(what: str, check, ceiling: float = CEILING):
    """Poll `check` until it returns something truthy; fail naming `what` past the ceiling."""
    deadline = time.monotonic() + ceiling
    while time.monotonic() < deadline:
        found = check()
        if found:
            return found
        time.sleep(0.05)
    raise AssertionError(f"timed out after {ceiling:.0f}s waiting for {what}")


class _RunsClone(_HostClone):
    """_HostClone with the relaying transport and the blocking gate."""

    def __init__(self) -> None:
        super().__init__()
        self.ssh.write_text(RELAY_SSH, encoding="utf-8")
        scripts = self.clone / ".claude" / "skills" / "sdlc-studio" / "scripts"
        (scripts / "gate.py").write_text(BLOCKING_GATE, encoding="utf-8")
        self.commit("blocking gate")
        self.release = self.tmp / "release"
        self.drop = self.tmp / "drop"

    def env(self) -> dict:
        base = {k: v for k, v in os.environ.items()
                if not k.startswith("GIT_") and k not in ("SDLC_GATE_LOCAL", "SDLC_PUSH_ACK_RED",
                                                          "SDLC_STUDIO_BOUNDARY_SUITE")}
        base.update({"PATH": str(self.path()), "STUB_GH_MODE": "empty",
                     "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                     "STUB_SSH_LOG": str(self.tmp / "ssh.log"), "STUB_GATE_LOG": str(self.tmp / "gate.log"),
                     "STUB_PREREQ_LOG": str(self.tmp / "prereq.log"), "STUB_KI_LOG": str(self.tmp / "ki.log"),
                     "STUB_HOST_HOME": str(self.host_home), "STUB_HOST_PATH": self.host_path(),
                     "STUB_RELEASE": str(self.release), "STUB_SSH_DROP": str(self.drop)})
        return base

    def start_run(self, commit: str, name: str) -> subprocess.Popen:
        """remote-gate.sh's local side, as the hook calls it, in the background."""
        out = (self.tmp / f"{name}.err").open("w")
        return subprocess.Popen(["bash", "tools/remote-gate.sh", "push", "--commit", commit],
                                cwd=self.clone, env=self.env(), stdout=out, stderr=subprocess.STDOUT)

    def start_push(self) -> subprocess.Popen:
        """The real hook, through `git push`, as the leader of its own process group, so a
        test can signal the group as a terminal's interrupt would."""
        out = (self.tmp / "push.err").open("w")
        return subprocess.Popen(["git", "push", "-q", "origin", "main"], cwd=self.clone, env=self.env(),
                                stdout=out, stderr=subprocess.STDOUT, start_new_session=True)

    def runs_dir(self) -> Path:
        return self.host_home / "sdlc-gate" / "runs"

    def run_dirs(self) -> list[Path]:
        return sorted(p for p in self.runs_dir().iterdir()) if self.runs_dir().exists() else []

    def run_refs(self) -> list[str]:
        """The refs/gate-runs/* the host's bare repository for this clone holds."""
        clone_id = _git(self.clone, "config", "--get", "sdlc.gateCloneId", check=False).stdout.strip()
        repo = self.host_home / "sdlc-gate" / "clones" / f"{clone_id}.git"
        if not clone_id or not repo.exists():
            return []
        listed = _git(repo, "for-each-ref", "--format=%(refname)", "refs/gate-runs", check=False)
        return listed.stdout.split()

    def text(self, name: str) -> str:
        f = self.tmp / f"{name}.err"
        return f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""

    def cleanup(self) -> None:
        self.release.touch()                  # never leave a blocked stub gate behind
        super().cleanup()


class GateHostRunTests(unittest.TestCase):

    def setUp(self) -> None:
        if self._testMethodName == "test_an_abandoned_push_leaves_nothing_running":
            return                            # one fixture per abandonment case, made in the test
        self.fx = _RunsClone()
        self.addCleanup(self.fx.cleanup)

    def test_each_run_has_its_own_tree(self) -> None:
        """AC1. Mutant: the run directory keyed on the commit alone and removed before reuse, as
        the trial script did, so the second run deletes the first run's tree from under it."""
        fx = self.fx
        commit = fx.commit("judge me twice")
        first = fx.start_run(commit, "first")
        run = _until("the first run's gate to start", lambda: fx.gate_runs())[0]
        second = fx.start_run(commit, "second")
        dirs = _until("a second run directory", lambda: (lambda d: d if len(d) == 2 else None)(fx.run_dirs()))
        self.assertNotEqual(dirs[0], dirs[1])
        refs = _until("a ref for each live run", lambda: (lambda r: r if len(r) == 2 else None)(fx.run_refs()))
        self.assertEqual(len(set(refs)), 2, f"two live runs share one ref: {refs}")
        self.assertTrue(Path(run["cwd"]).is_dir(), "the second run removed the first run's tree")
        self.assertTrue(any(Path(run["cwd"]).resolve().is_relative_to(d.resolve()) for d in dirs),
                        "the first run's tree is not inside its own run directory")
        fx.release.touch()
        self.assertEqual(first.wait(CEILING), 0, fx.text("first"))
        self.assertEqual(second.wait(CEILING), 0, fx.text("second"))
        runs = fx.gate_runs()
        self.assertEqual(len(runs), 2, runs)
        self.assertNotEqual(runs[0]["cwd"], runs[1]["cwd"], "both runs judged in one tree")
        self.assertEqual(fx.run_dirs(), [], "a run directory was left behind")
        self.assertEqual(fx.run_refs(), [], "a finished run's ref was left on the host")
        self.assertRegex(fx.text("first"), r"judging [0-9a-f]+ at --boundary push with .*, load [\d.]+ [\d.]+ [\d.]+",
                         "the host's judging line does not state its load")

    def test_the_hosts_gate_keeps_interrupts_at_their_default(self) -> None:
        """The host launches its gate as a background job, which a non-interactive shell starts
        with SIGINT ignored; a suite test that interrupts a hook it runs then cannot (the first
        host run of this unit failed test_a_ctrl_c_stops_every_lane_with_the_hook exactly so).
        Mutant: the gate launched without restoring SIGINT's default disposition."""
        fx = self.fx
        run = fx.start_run(fx.commit("interrupts reach the suite"), "first")
        gate = _until("the gate to start", lambda: fx.gate_runs())[0]
        self.assertFalse(gate["sigint_ignored"], "the host's gate runs with SIGINT ignored")
        fx.release.touch()
        self.assertEqual(run.wait(CEILING), 0, fx.text("first"))

    def test_a_second_run_waits_and_says_so(self) -> None:
        """AC2. Mutant: no lock, so both suites run at once and nothing says a run is waiting."""
        fx = self.fx
        older = fx.commit("first in")
        newer = fx.commit("second in")
        first = fx.start_run(older, "first")
        _until("the first run's gate to start", lambda: fx.gate_runs())
        second = fx.start_run(newer, "second")
        line = _until("the second run to say it is waiting",
                      lambda: next((ln for ln in fx.text("second").splitlines() if "waiting" in ln), None))
        self.assertIn(older, line, f"the waiting run does not name the run it waits for: {line}")
        self.assertEqual(len(fx.gate_runs()), 1, "the second run's gate started while the first held the host")
        fx.release.touch()
        self.assertEqual(first.wait(CEILING), 0, fx.text("first"))
        self.assertEqual(second.wait(CEILING), 0, fx.text("second"))
        self.assertEqual([r["head"] for r in fx.gate_runs()], [older, newer],
                         "the waiting run did not start when the first ended")

    def test_an_abandoned_push_leaves_nothing_running(self) -> None:
        """AC3. Mutants: the host's gate left running, or its tree left behind, after the pusher
        goes - interrupted, terminated, or its connection dropped mid-run."""
        for how in ("SIGINT", "SIGTERM", "drop"):
            with self.subTest(how=how):
                fx = _RunsClone()
                push = None
                try:
                    fx.commit(f"abandon by {how}")
                    push = fx.start_push()
                    run = _until("the host's gate to start", lambda: fx.gate_runs())[0]
                    if how == "drop":
                        fx.drop.touch()
                    else:
                        os.killpg(push.pid, getattr(signal, how))
                    self.assertNotEqual(push.wait(CEILING), 0, f"an abandoned push ({how}) was let through")
                    _until(f"the host's gate to stop after {how}", lambda: not _alive(run["pid"]))
                    _until(f"the gate's child process to stop after {how}", lambda: not _alive(run["child"]))
                    _until(f"the host's run directory to go after {how}", lambda: fx.run_dirs() == [])
                    self.assertFalse(Path(run["cwd"]).exists(), f"the run's tree survived {how}")
                    self.assertEqual(_git(fx.remote, "rev-parse", "-q", "--verify", "refs/heads/main",
                                          check=False).stdout.strip(), "", "an abandoned push reached origin")
                finally:
                    if push is not None and push.poll() is None:
                        os.killpg(push.pid, signal.SIGKILL)
                    for gate in fx.gate_runs():
                        for pid in (gate["pid"], gate.get("child")):
                            if pid and _alive(pid):
                                os.kill(pid, signal.SIGKILL)
                    fx.cleanup()

if __name__ == "__main__":
    unittest.main()
