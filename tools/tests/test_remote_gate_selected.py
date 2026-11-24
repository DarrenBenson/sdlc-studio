# test-census-subject: tools/remote-gate.sh
"""remote-gate.sh's staged-tree mode: the gate host judges the tree a commit stages.

Built on test_remote_gate_push.py's fixture (a clone, a fake host home, a stubbed transport) and
test_remote_gate_runs.py's relaying transport. The gate the host runs is a stub at the invoked
path that records its argv, where it ran, which commit and tree it judged, what the staged file
held, whether the untracked file came with it and the two settings the host's run sets, then
exits by the `verdict` file of the tree it judged - so a verdict staged and a verdict in the
working tree differ, and only the staged one may decide.

remote-gate.sh's local side runs on a PATH holding only git, bash, python3 and a `gh` stub, as
the hooks' fixtures run it, so its staged mode is held to the tools its header promises.
"""
from __future__ import annotations

import fcntl
import os
import re
import shutil
import signal
import subprocess
import sys
import textwrap
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_remote_gate_push import HOST, REMOTE_GATE, _git, _HostClone  # noqa: E402
from test_remote_gate_runs import _alive, _RunsClone, _until  # noqa: E402

#: The stub selection runner: one JSON line per run, then the verdict its tree's `verdict` holds.
STAGED_GATE = textwrap.dedent('''
    import json, os, subprocess, sys
    from pathlib import Path
    def git(*a):
        r = subprocess.run(["git", *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    def text(name):
        return Path(name).read_text() if Path(name).exists() else None
    verdict = int(text("verdict").strip()) if text("verdict") else 0
    Path(os.environ["STUB_GATE_LOG"]).open("a").write(json.dumps({
        "argv": sys.argv[1:], "cwd": os.getcwd(), "pid": os.getpid(),
        "head": git("rev-parse", "HEAD"), "parent": git("rev-parse", "-q", "--verify", "HEAD^"),
        "tree": git("rev-parse", "HEAD^{tree}"), "staged": text("staged.txt"),
        "untracked": Path("untracked.txt").exists(), "local": os.environ.get("SDLC_GATE_LOCAL"),
        "boundary": os.environ.get("SDLC_STUDIO_BOUNDARY_SUITE"), "verdict": verdict}) + "\\n")
    if verdict:
        print("FAILED tools/tests/test_red.py::RedTests::test_the_staged_change - the stub's red")
    else:
        print("unit-tests: the stub passed the selection")
    raise SystemExit(verdict)
''')

#: The same, blocking until STUB_RELEASE exists, and logging its start and its end.
BLOCKING_STAGED_GATE = textwrap.dedent('''
    import json, os, sys, time
    from pathlib import Path
    log = Path(os.environ["STUB_GATE_LOG"])
    tag = Path("staged.txt").read_text().strip()
    verdict = int(Path("verdict").read_text().strip())
    def note(event):
        log.open("a").write(json.dumps({"event": event, "tag": tag, "pid": os.getpid(),
                                        "cwd": os.getcwd()}) + "\\n")
    note("start")
    release = Path(os.environ["STUB_RELEASE"])
    deadline = time.monotonic() + float(os.environ.get("STUB_DEADLINE", "180"))
    while not release.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    note("end")
    raise SystemExit(verdict)
''')

GATE_PY = Path(".claude") / "skills" / "sdlc-studio" / "scripts" / "gate.py"
MODULES = ["tools/tests/test_a1.py", ".claude/skills/sdlc-studio/scripts/tests/test_b.py::Sweep"]


def _picked(*modules: str) -> list[str]:
    return [arg for m in modules for arg in ("--test", m)]


class _Staging:
    """What both fixtures share: staging a file, and reading what a run left on the host."""

    def stage(self, **files: str) -> None:
        for name, body in files.items():
            (self.clone / name).write_text(body, encoding="utf-8")
            _git(self.clone, "add", "--", name)

    def host_leftovers(self) -> list[str]:
        """Any run directory, or any run ref in any clone repository, left on the host."""
        base = self.host_home / "sdlc-gate"
        runs = sorted(p.name for p in (base / "runs").iterdir()) if (base / "runs").exists() else []
        for repo in sorted((base / "clones").glob("*.git")) if (base / "clones").exists() else []:
            runs += _git(repo, "for-each-ref", "--format=%(refname)", "refs/gate-runs").stdout.split()
        return runs


class _StagedClone(_Staging, _HostClone):
    """_HostClone whose committed gate is the staged-tree stub, with a staged file to judge."""

    def __init__(self) -> None:
        super().__init__()
        (self.clone / GATE_PY).write_text(STAGED_GATE, encoding="utf-8")
        self.commit("the staged-tree stub", **{"staged.txt": "committed\n"})
        self.scratch = self.tmp / "scratch"           # remote-gate's TMPDIR, read for leftovers
        self.scratch.mkdir()

    def env(self, **extra: str) -> dict:
        """remote-gate.sh's environment: no git identity, no global config, the tight PATH."""
        base = {k: v for k, v in os.environ.items()
                if not k.startswith("GIT_") and k not in ("SDLC_GATE_LOCAL", "SDLC_STUDIO_BOUNDARY_SUITE")}
        base.update({"PATH": str(self.path()), "GIT_CONFIG_GLOBAL": "/dev/null",
                     "GIT_CONFIG_SYSTEM": "/dev/null", "TMPDIR": str(self.scratch),
                     "STUB_SSH_LOG": str(self.tmp / "ssh.log"), "STUB_GATE_LOG": str(self.tmp / "gate.log"),
                     "STUB_PREREQ_LOG": str(self.tmp / "prereq.log"),
                     "STUB_HOST_HOME": str(self.host_home), "STUB_HOST_PATH": self.host_path()})
        base.update(extra)
        return base

    def staged(self, *args: str, cwd: Path | None = None, timeout: int = 300,
               **extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", "tools/remote-gate.sh", *args], cwd=cwd or self.clone,
                              env=self.env(**extra), capture_output=True, text=True, timeout=timeout)

    def snapshot(self, clone: Path | None = None) -> dict:
        """What the run must leave as it was. The index is read as bytes first, before any git
        command here could refresh it."""
        clone = clone or self.clone
        return {"index": (clone / ".git" / "index").read_bytes(),
                "head": _git(clone, "rev-parse", "-q", "--verify", "HEAD", check=False).stdout,
                "refs": _git(clone, "for-each-ref", "--format=%(refname) %(objectname)").stdout,
                "reachable": _git(clone, "rev-list", "--all").stdout,
                "entries": _git(clone, "ls-files", "-s").stdout,
                "files": {p.name: p.read_bytes() for p in clone.iterdir() if p.is_file()}}

    def index_tree(self, clone: Path | None = None, index: Path | None = None) -> str:
        """The tree the clone's index (or `index`) holds, written from a copy of it."""
        clone = clone or self.clone
        copy = self.tmp / "expected-index"
        shutil.copyfile(index or clone / ".git" / "index", copy)
        tree = _git(clone, "write-tree", env={"GIT_INDEX_FILE": str(copy)}).stdout.strip()
        copy.unlink()
        return tree


class _BlockingStagedClone(_Staging, _RunsClone):
    """The relaying transport, with a staged-tree gate that blocks until it is released."""

    def __init__(self) -> None:
        super().__init__()
        (self.clone / GATE_PY).write_text(BLOCKING_STAGED_GATE, encoding="utf-8")
        self.commit("the blocking staged-tree stub", **{"staged.txt": "base\n", "verdict": "0\n"})
        self.scratch = self.tmp / "scratch"
        self.scratch.mkdir()

    def env(self, **extra: str) -> dict:
        return {**super().env(), "TMPDIR": str(self.scratch), **extra}

    def start_staged(self, name: str) -> subprocess.Popen:
        out = (self.tmp / f"{name}.err").open("w")
        return subprocess.Popen(["bash", "tools/remote-gate.sh", "staged", *_picked(MODULES[0])],
                                cwd=self.clone, env=self.env(), stdout=out, stderr=subprocess.STDOUT)

    def events(self) -> list[tuple[str, str]]:
        return [(run["event"], run["tag"]) for run in self.gate_runs()]


class RemoteGateSelectedTests(unittest.TestCase):

    def test_the_host_judges_the_staged_tree_and_only_the_selected_modules(self) -> None:
        """AC1. Mutants: the tree written from HEAD or the working tree; GIT_INDEX_FILE ignored;
        the tree written in the clone's own index rather than a copy; the scratch index left in
        TMPDIR; the commit parented on nothing, or on an unborn HEAD; a clone with no identity
        refusing the wrapping commit; the whole suite or the boundary gate run in place of the
        selection; the host's run left free to forward its own suites or to run the push's
        boundary_only tests."""
        fx = _StagedClone()
        self.addCleanup(fx.cleanup)
        # A clone that refuses a commit made with no configured identity, if the wrapping commit
        # took the clone's own.
        _git(fx.clone, "config", "user.useConfigOnly", "true")
        (fx.host_home / "sdlc-gate").mkdir()
        (fx.host_home / "sdlc-gate" / "gate-env.sh").write_text(
            "export SDLC_STUDIO_BOUNDARY_SUITE=1\nexport SDLC_GATE_LOCAL=0\n", encoding="utf-8")
        fx.stage(**{"staged.txt": "staged\n"})
        (fx.clone / "staged.txt").write_text("unstaged\n", encoding="utf-8")
        (fx.clone / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        before = fx.snapshot()
        r = fx.staged("staged", *_picked(*MODULES))
        after = fx.snapshot()
        self.assertEqual(0, r.returncode, r.stderr)
        runs = fx.gate_runs()
        self.assertEqual(1, len(runs), f"expected one run on the host, got {runs}\n{r.stderr}")
        run = runs[0]
        self.assertTrue(fx.on_host(run), f"the selection ran outside the host's checkout: {run}")
        self.assertEqual(["--root", ".", "--run-tests", *MODULES], run["argv"],
                         "the host did not run exactly the named modules through gate.py --run-tests")
        self.assertEqual("staged\n", run["staged"], "the host did not judge the staged content")
        self.assertFalse(run["untracked"], "the untracked file reached the host's tree")
        self.assertEqual(fx.index_tree(), run["tree"], "the host's tree is not the staged tree")
        self.assertEqual(before["head"].strip(), run["parent"], "the judged commit does not sit on HEAD")
        self.assertEqual("1", run["local"], "the host's run may send its own suites on to a host")
        self.assertIsNone(run["boundary"], "a commit's selection ran the push's boundary_only tests")
        self.assertIn("unit-tests: the stub passed the selection", r.stderr,
                      "the host's output did not reach the caller's stderr")
        self.assertIn(f"running 2 selected test module(s) on {run['head']}", r.stderr,
                      "the host did not say what it was running")
        self.assertEqual(before, after, "the clone's index, HEAD, refs or working tree changed")
        self.assertEqual([], list(fx.scratch.iterdir()), "the run left a scratch file in TMPDIR")
        self.assertEqual([], fx.host_leftovers(), "the run left its tree or its ref on the host")

        # The index GIT_INDEX_FILE names, as `git commit -a` or `git commit <path>` hands a hook.
        other = fx.tmp / "other-index"
        shutil.copyfile(fx.clone / ".git" / "index", other)
        blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=fx.clone, input="other\n",
                              capture_output=True, text=True, env=fx.env(), check=True).stdout.strip()
        _git(fx.clone, "update-index", "--cacheinfo", f"100644,{blob},staged.txt",
             env={"GIT_INDEX_FILE": str(other)})
        r = fx.staged("staged", *_picked(MODULES[0]), GIT_INDEX_FILE=str(other))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("other\n", fx.gate_runs()[-1]["staged"],
                         "the host judged the clone's index, not the one GIT_INDEX_FILE names")

        # A clone with no commit yet: the staged tree goes as a commit with no parent.
        fresh = fx.tmp / "fresh"
        _git(fx.tmp, "init", "-q", "-b", "main", str(fresh))
        for rel in ("tools/remote-gate.sh", "tools/gate_prereqs.py", str(GATE_PY)):
            (fresh / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(fx.clone / rel, fresh / rel)
        (fresh / "staged.txt").write_text("first\n", encoding="utf-8")
        _git(fresh, "add", "-A")
        _git(fresh, "config", "sdlc.gateHost", HOST)
        _git(fresh, "config", "sdlc.gateSsh", str(fx.ssh))
        r = fx.staged("staged", *_picked(MODULES[0]), cwd=fresh)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(("first\n", ""), (fx.gate_runs()[-1]["staged"], fx.gate_runs()[-1]["parent"]),
                         "an unborn HEAD's staged tree was not judged as a root commit")

        usage = subprocess.run(["bash", str(REMOTE_GATE)], capture_output=True, text=True,
                               env=fx.env(), timeout=60)
        self.assertEqual(2, usage.returncode)
        self.assertIn("staged --test <module> [--test <module>]...", usage.stderr,
                      "the usage line does not name the staged-tree mode's flags")

    def test_a_red_selected_module_exits_1_with_its_output(self) -> None:
        """AC2. Mutants: the host's red read as green; a selection's own exit 4 (pytest's usage
        error) or 255 passed on as an unready host or a dropped connection, which the caller
        would retry locally; the red named as some other kind of refusal."""
        fx = _StagedClone()
        self.addCleanup(fx.cleanup)
        (fx.clone / "verdict").write_text("0\n", encoding="utf-8")       # the working tree: green
        for verdict in ("1", "4", "255"):
            with self.subTest(selection_exit=verdict):
                fx.stage(verdict=f"{verdict}\n")
                (fx.clone / "verdict").write_text("0\n", encoding="utf-8")
                r = fx.staged("staged", *_picked(MODULES[0]))
                self.assertEqual(1, r.returncode, f"a red selection exiting {verdict} is not exit 1:\n{r.stderr}")
                self.assertEqual(int(verdict), fx.gate_runs()[-1]["verdict"])
                self.assertIn("FAILED tools/tests/test_red.py::RedTests::test_the_staged_change", r.stderr,
                              "the failing test's name and output did not reach the caller")
                self.assertIn(f"remote-gate: the selected test modules were red on {HOST}", r.stderr)
                self.assertNotIn("could not judge", r.stderr)
                self.assertNotIn("the full log is on", r.stderr, "a red selection pointed at a log it never wrote")

    def test_an_unreachable_or_unready_host_is_not_a_verdict(self) -> None:
        """AC3. Mutants: a failed connection or a host whose setup refused read as red (1) or
        green (0); a call naming no module, or one that cannot travel, connecting anyway;
        `push` taking the staged mode's --test; a --test with nothing after it never ending."""
        fx = _StagedClone()
        self.addCleanup(fx.cleanup)
        fx.stage(**{"staged.txt": "staged\n"})
        exits = []
        r = fx.staged("staged", *_picked(MODULES[0]), STUB_SSH_FAIL="before")
        exits.append(r.returncode)
        self.assertIn(f"the gate host {HOST} could not judge commit", r.stderr)
        self.assertIn("it could not be reached", r.stderr)
        self.assertIn("or run the selection on this machine: python3 .claude/skills/sdlc-studio/"
                      f"scripts/gate.py --run-tests {MODULES[0]}", r.stderr)
        self.assertNotIn("git push", r.stderr, "the unreachable host's advice is the push's")
        self.assertNotIn("nothing ran locally in its place", r.stderr,
                         "the staged mode spoke for its caller, which runs the selection here")

        fx.stage(**{"prereq-rc": "1\n"})
        r = fx.staged("staged", *_picked(MODULES[0]))
        exits.append(r.returncode)
        self.assertIn("refused before the selected test modules run", r.stderr)
        self.assertIn(f"remote-gate: {HOST} did not run the selected test modules for commit", r.stderr)
        self.assertEqual([], fx.gate_runs(), "a test ran on a host whose setup refused")

        calls = len(fx.ssh_calls())
        r = fx.staged("staged")
        exits.append(r.returncode)
        self.assertIn("staged names no test module", r.stderr)
        self.assertEqual([3, 4, 2], exits, "an unreachable, unready or empty call read as a verdict")

        head = _git(fx.clone, "rev-parse", "HEAD").stdout.strip()
        for args, says in ((("staged", "--test", "-k"), "--test needs a test module path, not '-k'"),
                           (("staged", "--test", "it's"), "not 'it's'"),
                           (("staged", "--test", "/etc/passwd"), "not '/etc/passwd'"),
                           (("staged", "--test"), "--test needs a test module after it"),
                           (("staged", "--suite", "all"), "unknown argument: --suite"),
                           (("push", "--commit", head, "--test", MODULES[0]), "--test goes with staged"),
                           (("push", "--commit", head, "--test"), "--test needs a test module after it")):
            with self.subTest(args=args):
                r = fx.staged(*args, timeout=60)           # each refuses before it connects
                self.assertEqual(2, r.returncode, r.stderr)
                self.assertIn(says, r.stderr)
        self.assertEqual(calls, len(fx.ssh_calls()), "a call that could not start still connected")
        self.assertEqual([], fx.host_leftovers())

        # The push form beside it is unchanged: its unreachable host keeps the push's own advice.
        r = fx.staged("push", "--commit", head, STUB_SSH_FAIL="before")
        self.assertEqual(3, r.returncode, r.stderr)
        self.assertIn("nothing ran locally in its place", r.stderr)
        self.assertIn("SDLC_GATE_LOCAL=1 git push", r.stderr)

    def test_runs_are_serialised_and_leave_no_tree_on_the_host(self) -> None:
        """AC4. Mutants: the staged mode run outside the host's lock, so two selections run at
        once; a run's own tree reused by the next; an abandoned run's tree or ref left on the
        host."""
        fx = _BlockingStagedClone()
        self.addCleanup(fx.cleanup)
        fx.stage(**{"staged.txt": "first\n", "verdict": "0\n"})
        first = fx.start_staged("first")
        _until("the first run to start", lambda: ("start", "first") in fx.events())
        fx.stage(**{"staged.txt": "second\n", "verdict": "1\n"})
        second = fx.start_staged("second")
        _until("the second run to wait for the lock", lambda: "for the run holding" in fx.text("second"))
        self.assertEqual([("start", "first")], fx.events(), "the second run did not wait for the first")
        fx.release.touch()
        self.assertEqual(0, first.wait(timeout=240), fx.text("first"))
        self.assertEqual(1, second.wait(timeout=240), fx.text("second"))
        self.assertEqual([("start", "first"), ("end", "first"), ("start", "second"), ("end", "second")],
                         fx.events(), "the two runs were not taken one after the other")
        cwds = [run["cwd"] for run in fx.gate_runs() if run["event"] == "start"]
        self.assertNotEqual(cwds[0], cwds[1], "two runs shared one checkout")
        self.assertEqual([], fx.host_leftovers(), "a finished run left its tree or its ref on the host")

        fx.release.unlink()
        fx.stage(**{"staged.txt": "third\n", "verdict": "0\n"})
        third = fx.start_staged("third")
        try:
            gate = _until("the third run to start",
                          lambda: next((g for g in fx.gate_runs() if g["tag"] == "third"), None))
            third.send_signal(signal.SIGTERM)
            third.wait(timeout=240)
            _until("the abandoned run's gate to stop", lambda: not _alive(gate["pid"]))
            _until("the abandoned run's tree and ref to go", lambda: fx.host_leftovers() == [])
        finally:
            if third.poll() is None:
                third.kill()
        self.assertFalse(Path(gate["cwd"]).exists(), "the abandoned run's checkout is still on the host")
        self.assertNotIn(("end", "third"), fx.events(), "the abandoned run's gate ran to its end")

    def test_a_held_lock_turns_a_commit_away_and_keeps_a_push_waiting(self) -> None:
        """AC4. A commit's selection waits for the host's lock at most the script's own bound,
        STAGED_LOCK_WAIT, 60 seconds, then leaves with 5, no verdict, having run nothing and left
        nothing; a push waits for as long as the lock is held, then runs; a free lock runs the
        selection on the host. The fixture's copy of the script is the shipped one with that bound
        shortened, and a `flock` on the host's PATH records each call before it runs the real
        one, so the wait each mode asks for is read from the call itself. Mutants: the bound
        changed, or a literal in its place; no bound, so a commit queues behind a push; the bound
        on a push too; the busy exit taken as a refusal (4) or a red (1)."""
        shipped = REMOTE_GATE.read_text(encoding="utf-8")
        found = re.findall(r"^STAGED_LOCK_WAIT=(\d+)$", shipped, re.M)
        self.assertEqual(["60"], found, "the staged mode's bound on the host's lock is not 60 seconds")
        short = 2
        fx = _StagedClone()
        self.addCleanup(fx.cleanup)
        flock_log = fx.tmp / "flock.log"
        wrapper = Path(fx.host_path().split(os.pathsep)[0]) / "flock"
        wrapper.write_text(f'#!/bin/sh\nprintf \'%s\\n\' "$*" >> {flock_log}\n'
                           f'exec {shutil.which("flock")} "$@"\n', encoding="utf-8")
        wrapper.chmod(0o755)
        fx.commit("the gate with a short bound", **{
            "tools/remote-gate.sh": shipped.replace("STAGED_LOCK_WAIT=60", f"STAGED_LOCK_WAIT={short}")})
        base = fx.host_home / "sdlc-gate"
        base.mkdir()
        (base / "run.holder").write_text("run held-by-the-test\n", encoding="utf-8")
        held = (base / "run.lock").open("w")
        self.addCleanup(held.close)
        fcntl.flock(held, fcntl.LOCK_EX)

        def flock_calls() -> list[str]:
            return flock_log.read_text(encoding="utf-8").splitlines() if flock_log.exists() else []

        fx.stage(**{"staged.txt": "busy\n"})
        busy = fx.staged("staged", *_picked(MODULES[0]), timeout=240)
        self.assertEqual(5, busy.returncode, busy.stdout + busy.stderr)
        self.assertIn(f"-E 50 -w {short} 9", flock_calls(), "the staged mode did not bound its wait")
        self.assertIn(f"waiting up to {short}s for the run holding", busy.stdout + busy.stderr)
        self.assertIn("held-by-the-test", busy.stdout + busy.stderr, "the busy run does not name the holder")
        self.assertIn(f"busy: another run held its gate lock past {short}s, so the selected test modules "
                      "did not run there", busy.stderr)
        self.assertEqual([], fx.gate_runs(), "a turned-away selection ran on the host")
        self.assertEqual([], fx.host_leftovers(), "a turned-away selection left its tree or ref on the host")

        sha = _git(fx.clone, "rev-parse", "HEAD").stdout.strip()
        out = (fx.tmp / "push.err").open("w")
        self.addCleanup(out.close)
        push = subprocess.Popen(["bash", "tools/remote-gate.sh", "push", "--commit", sha], cwd=fx.clone,
                                env=fx.env(), stdout=out, stderr=subprocess.STDOUT)
        self.addCleanup(lambda: push.poll() is None and push.kill())
        _until("the push to wait for the lock", lambda: flock_calls().count("9") == 1)
        time.sleep(short + 3)
        self.assertIsNone(push.poll(), "a push stopped waiting for the host's lock: "
                          + (fx.tmp / "push.err").read_text(encoding="utf-8"))
        self.assertNotIn("waiting up to", (fx.tmp / "push.err").read_text(encoding="utf-8"))
        fcntl.flock(held, fcntl.LOCK_UN)
        self.assertEqual(0, push.wait(timeout=240), (fx.tmp / "push.err").read_text(encoding="utf-8"))
        self.assertEqual([["--boundary", "push"]], [run["argv"] for run in fx.gate_runs()])

        fx.stage(**{"staged.txt": "free\n"})
        free = fx.staged("staged", *_picked(MODULES[0]), timeout=240)
        self.assertEqual(0, free.returncode, free.stdout + free.stderr)
        self.assertEqual("free\n", fx.gate_runs()[-1]["staged"], "a free lock did not run the selection on the host")
        self.assertEqual([], fx.host_leftovers())

    def _ssh_on_path(self, fx: _StagedClone) -> Path:
        """Replace the configured transport with a `ssh` on remote-gate's PATH, so the script's own
        default is what runs. It records each call's argv, then behaves as a dropped-packet host
        does to a call WITHOUT the bound ssh would honour: it hangs. HANG=connect gives a call
        carrying ConnectTimeout the connect failure (255) that bound produces; HANG=run does the
        same for the run's own call when both keepalive options are present. Anything else is the
        stub transport."""
        _git(fx.clone, "config", "--unset", "sdlc.gateSsh")
        log = fx.tmp / "opts.log"
        ssh = fx.path() / "ssh"
        ssh.write_text(textwrap.dedent(f'''
            #!/usr/bin/env bash
            args="$*"; printf '%s\\n' "$args" >> {log}
            connect=""; alive=""
            case "$args" in *"-o ConnectTimeout="*) connect=1 ;; esac
            case "$args" in *"-o ServerAliveInterval="*"-o ServerAliveCountMax="*) alive=1 ;; esac
            case "${{HANG:-}}" in
              connect) [ -n "$connect" ] && {{ sleep 0.2; exit 255; }}; sleep 120; exit 255 ;;
              run) case "$args" in *" remote --clone "*)
                     [ -n "$connect" ] && [ -n "$alive" ] && {{ sleep 0.2; exit 255; }}; sleep 120; exit 255 ;;
                   esac ;;
            esac
            exec {fx.ssh} "$@"
        ''').lstrip(), encoding="utf-8")
        ssh.chmod(0o755)
        return log

    def test_a_silent_host_is_bounded_and_is_not_a_verdict(self) -> None:
        """A host that drops packets reaches the caller's local run, never a pass. The bounds are
        the script's named constants, read here; every ssh the script makes carries the connect
        bound, a commit's selection carries the short keepalive and a push the patient one.
        Mutants: ConnectTimeout missing from the default, from the staged call or from one of its
        calls; the staged keepalive left at the push's, or the push's changed; a hung connect or a
        connection that dies mid-run read as a pass (0), a red (1) or no end."""
        shipped = REMOTE_GATE.read_text(encoding="utf-8")
        const = {k: int(v) for k, v in re.findall(r"^([A-Z_]+)=(\d+)$", shipped, re.M)}
        self.assertEqual((10, 15, 4, 60, 10), tuple(const[k] for k in (
            "CONNECT_TIMEOUT", "STAGED_ALIVE_INTERVAL", "STAGED_ALIVE_COUNT",
            "PUSH_ALIVE_INTERVAL", "PUSH_ALIVE_COUNT")))
        self.assertLessEqual(const["STAGED_ALIVE_INTERVAL"] * const["STAGED_ALIVE_COUNT"], 60,
                             "a dead connection is given up after more than a minute of silence")
        fx = _StagedClone()
        self.addCleanup(fx.cleanup)
        log = self._ssh_on_path(fx)
        fx.stage(**{"staged.txt": "staged\n"})

        def seen() -> list[str]:
            return log.read_text(encoding="utf-8").splitlines() if log.exists() else []

        staged_opts = ("-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 "
                       "-o ServerAliveCountMax=4")
        r = fx.staged("staged", *_picked(MODULES[0]), timeout=120)
        self.assertEqual(0, r.returncode, r.stderr)
        calls = seen()
        self.assertGreaterEqual(len(calls), 3, "the prepare, the send and the run did not all connect")
        for call in calls:
            self.assertIn(staged_opts, call, "a staged call's ssh lacks its bounds")

        log.unlink()
        head = _git(fx.clone, "rev-parse", "HEAD").stdout.strip()
        fx.staged("push", "--commit", head, timeout=120)
        calls = seen()
        self.assertGreaterEqual(len(calls), 3)
        for call in calls:
            self.assertIn("-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=60 "
                          "-o ServerAliveCountMax=10", call, "a push's ssh lost the connect bound")

        log.unlink()
        fx.commit("a prerequisite list for doctor to send", **{"requirements-dev.txt": "pytest\n",
                                                                 "tools/gate_prereqs.py": "print()\n"})
        fx.staged("doctor", timeout=120)
        self.assertTrue(seen(), "doctor made no ssh call")
        for call in seen():
            self.assertIn("-o ConnectTimeout=10", call, "doctor's ssh has no connect bound")

        # A host that never answers the connect: the bound ends it, 3, the caller's run follows.
        before = len(fx.gate_runs())
        r = fx.staged("staged", *_picked(MODULES[0]), HANG="connect", timeout=60)
        self.assertEqual(3, r.returncode, r.stdout + r.stderr)
        self.assertIn("it could not be reached", r.stderr)
        self.assertIn(f"gate.py --run-tests {MODULES[0]}", r.stderr)

        # A connection that dies after the gate began: the keepalive ends it, 3, never a pass.
        r = fx.staged("staged", *_picked(MODULES[0]), HANG="run", timeout=60)
        self.assertEqual(3, r.returncode, r.stdout + r.stderr)
        self.assertIn("the connection failed while it ran", r.stderr)
        self.assertEqual(before, len(fx.gate_runs()), "a hung host produced a test run")


if __name__ == "__main__":
    unittest.main()
