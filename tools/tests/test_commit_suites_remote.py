# test-census-subject: .githooks/commit-msg
"""The commit-msg hook sends a commit's selected suites to the gate host this clone names.

Each case runs the tracked hook, as git does (a message file as $1), in a throwaway repository
holding the record pre-commit hands over (`sdlc-gate-suites`, with its `suite-selector=` lines)
and stubs at the paths the hook resolves: `tools/remote-gate.sh` exits as STUB_REMOTE_RC says,
`gate.py --run-tests` and `tools/skill-tests.sh` as STUB_LOCAL_RC says, and the selected tools
module, a real unittest module, fails or passes by the same switch. Every one of them records its
call, so a test reads where the selection ran rather than inferring it from the output. Whether
pytest is importable is the fixture's choice too: a `pytest` module on PYTHONPATH that imports,
or one that refuses to.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "commit-msg"
HOST = "gatehost.test"
SKILL_MODULE = ".claude/skills/sdlc-studio/scripts/tests/test_b.py::Sweep"
SELECTION = ["tools/tests/test_a.py", SKILL_MODULE]

#: remote-gate's stub. STUB_REMOTE_RC=block waits, as a host's run does, until an interrupt ends
#: it with remote-gate's own exit for one: 130.
STUB_REMOTE = textwrap.dedent('''\
    #!/usr/bin/env bash
    [ "$STUB_REMOTE_RC" = block ] && trap 'exit 130' INT
    python3 -c 'import json, os, sys
    open(os.environ["STUB_LOG"], "a").write(json.dumps({"runner": "remote-gate", "argv": sys.argv[1:],
        "index": os.environ.get("GIT_INDEX_FILE")}) + "\\n")' "$@"
    n=0
    while [ "$STUB_REMOTE_RC" = block ] && [ $((n += 1)) -lt 1200 ]; do sleep 0.1; done
    echo "HOST-OUTPUT the host's own lines, exit $STUB_REMOTE_RC"
    exit "$STUB_REMOTE_RC"
''')

STUB_GATE = textwrap.dedent('''\
    import json, os, sys
    argv = sys.argv[1:]
    if "--run-tests" in argv:
        open(os.environ["STUB_LOG"], "a").write(json.dumps({"runner": "gate.py", "argv": argv}) + "\\n")
        print("LOCAL-RUN the selection ran on this machine")
        raise SystemExit(int(os.environ["STUB_LOCAL_RC"]))
''')

STUB_SKILL_TESTS = textwrap.dedent('''\
    #!/usr/bin/env bash
    python3 -c 'import json, os, sys
    open(os.environ["STUB_LOG"], "a").write(json.dumps({"runner": "skill-tests", "argv": sys.argv[1:]}) + "\\n")' "$@"
    exit "$STUB_LOCAL_RC"
''')

TOOL_MODULE = textwrap.dedent('''\
    import json, os, unittest

    class ToolTests(unittest.TestCase):
        def test_it(self):
            with open(os.environ["STUB_LOG"], "a") as log:
                log.write(json.dumps({"runner": "unittest"}) + "\\n")
            self.assertEqual("0", os.environ["STUB_LOCAL_RC"])
''')


class _Clone:
    """A repository mid-commit: the handover pre-commit leaves, and the stubbed runners."""

    def __init__(self, *, host: bool = True, selectors: list[str] | None = SELECTION) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="commit_suites_remote_"))
        self.repo = self.tmp / "repo"
        self.log = self.tmp / "runs.log"
        self.git("init", "-q", str(self.repo), cwd=self.tmp)
        if host:
            self.git("config", "sdlc.gateHost", HOST)
        files = {"tools/remote-gate.sh": STUB_REMOTE, "tools/skill-tests.sh": STUB_SKILL_TESTS,
                 ".claude/skills/sdlc-studio/scripts/gate.py": STUB_GATE,
                 "tools/tests/test_a.py": TOOL_MODULE}
        for rel, body in files.items():
            (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / rel).write_text(body, encoding="utf-8")
        handover = ["precommit_seconds=1"] + [f"suite-selector={s}" for s in selectors or []]
        (self.repo / ".git" / "sdlc-gate-suites").write_text("\n".join(handover) + "\n", encoding="utf-8")
        self.msg = self.repo / ".git" / "COMMIT_EDITMSG"
        self.msg.write_text("feat(US1191): a change\n", encoding="utf-8")
        for name, body in (("with-pytest", ""), ("without-pytest", "raise ImportError('no pytest here')\n")):
            (self.tmp / name).mkdir()
            (self.tmp / name / "pytest.py").write_text(body, encoding="utf-8")

    def env(self, **extra: str) -> dict:
        base = {k: v for k, v in os.environ.items()
                if not k.startswith("GIT_") and not k.startswith("SDLC_")}
        base.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                     "STUB_LOG": str(self.log), "TMPDIR": str(self.tmp)})
        base.update(extra)
        return base

    def git(self, *args: str, cwd: Path | None = None) -> None:
        subprocess.run(["git", *args], cwd=cwd or self.repo, env=self.env(), check=True,
                       capture_output=True, text=True, timeout=60)

    def hook_env(self, remote: int | str, local: int, *, pytest: bool = True, verbose: bool = True,
                 **extra: str) -> dict:
        env = self.env(STUB_REMOTE_RC=str(remote), STUB_LOCAL_RC=str(local),
                       PYTHONPATH=str(self.tmp / ("with-pytest" if pytest else "without-pytest")),
                       **extra)
        if verbose:
            env["SDLC_GATE_VERBOSE"] = "1"
        return env

    def commit_msg(self, remote: int, local: int, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(HOOK), str(self.msg)], cwd=self.repo,
                              env=self.hook_env(remote, local, **kwargs),
                              capture_output=True, text=True, timeout=120)

    def start(self, remote: str, local: int) -> subprocess.Popen:
        """The hook as the leader of its own process group, with interrupts at their default, so
        a test can signal the group as a terminal's interrupt would."""
        return subprocess.Popen(["bash", str(HOOK), str(self.msg)], cwd=self.repo,
                                env=self.hook_env(remote, local), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, start_new_session=True,
                                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL))

    def runs(self) -> list[dict]:
        lines = self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []
        return [json.loads(line) for line in lines]

    def runners(self) -> list[str]:
        return [run["runner"] for run in self.runs()]

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


def _remote_argv() -> list[str]:
    return ["staged"] + [arg for s in SELECTION for arg in ("--test", s)]


class CommitSuitesRemoteTests(unittest.TestCase):

    def clone(self, **kwargs) -> _Clone:
        fx = _Clone(**kwargs)
        self.addCleanup(fx.cleanup)
        return fx

    def test_a_named_host_runs_the_selected_suites_and_the_laptop_runs_none(self) -> None:
        """AC1. Mutants: the selection run here as well as on the host, or here alone; the
        host's 1 read as a pass, or its 0 as a refusal; the host's output withheld; the index
        being committed scrubbed from remote-gate's environment; a clone without pytest running
        its unittest lanes beside the host's verdict."""
        for pytest in (True, False):
            with self.subTest(pytest_here=pytest):
                fx = self.clone()
                index = str(fx.repo / ".git" / "index")
                r = fx.commit_msg(0, 1, pytest=pytest, GIT_INDEX_FILE=index)
                out = r.stdout + r.stderr
                self.assertEqual(0, r.returncode, out)
                self.assertEqual(["remote-gate"], fx.runners(), f"a suite ran here with a host named:\n{out}")
                self.assertEqual(_remote_argv(), fx.runs()[0]["argv"])
                self.assertEqual(index, fx.runs()[0]["index"], "the index being committed did not reach remote-gate")
                self.assertIn("ok   unit-tests", out)

                fx = self.clone()
                r = fx.commit_msg(1, 0, pytest=pytest)
                out = r.stdout + r.stderr
                self.assertEqual(1, r.returncode, f"the host's red verdict did not refuse the commit:\n{out}")
                self.assertEqual(["remote-gate"], fx.runners(), f"a suite ran here with a host named:\n{out}")
                self.assertIn("FAIL unit-tests", out)
                self.assertIn("HOST-OUTPUT the host's own lines, exit 1", out, "the host's output was not shown")
                self.assertNotIn("running them on this machine", out, "a red verdict was read as no verdict")

    def test_an_unreachable_host_falls_back_to_the_local_suites(self) -> None:
        """AC2. Mutants: a commit refused only because the host was down or unready; one accepted
        with no suite run anywhere; the fallback line missing, held back on a pass, or naming no
        host or cause; a busy host (5: another run held its lock past the wait a commit allows)
        read as a verdict, or as a cause it is not; a no-pytest clone's fallback skipping its
        unittest lanes; an interrupt while the host judges read as a host that is down, so the
        selection starts here."""
        cases = ((3, 0, True, False, "it could not be reached"),
                 (4, 1, True, True, "its setup refused before any test ran"),
                 (5, 1, True, False, "it was busy: another run held its gate lock past the wait"),
                 (5, 0, True, True, "it was busy: another run held its gate lock past the wait"),
                 (2, 0, True, True, "tools/remote-gate.sh exited 2 before any test verdict"),
                 (127, 1, True, False, "tools/remote-gate.sh exited 127 before any test verdict"),
                 (3, 0, False, True, "it could not be reached"))
        for remote, local, pytest, verbose, cause in cases:
            with self.subTest(remote=remote, local=local, pytest_here=pytest, verbose=verbose):
                fx = self.clone()
                r = fx.commit_msg(remote, local, pytest=pytest, verbose=verbose)
                out = r.stdout + r.stderr
                self.assertEqual(local, r.returncode, f"the verdict is not the local run's:\n{out}")
                said = [ln for ln in out.splitlines() if "did not judge the selected suites" in ln]
                self.assertEqual(1, len(said), f"expected one line saying the host gave no verdict:\n{out}")
                self.assertIn(f"the gate host {HOST}", said[0])
                self.assertIn(cause, said[0])
                self.assertIn("running them on this machine", said[0])
                if verbose:
                    self.assertIn(f"HOST-OUTPUT the host's own lines, exit {remote}", out,
                                  "remote-gate's own account of the failure was dropped")
                self.assertEqual("remote-gate", fx.runners()[0], out)
                if pytest:
                    self.assertEqual(["remote-gate", "gate.py"], fx.runners(), out)
                    self.assertEqual(["--root", ".", "--run-tests", *SELECTION], fx.runs()[1]["argv"])
                else:
                    self.assertEqual(["remote-gate", "skill-tests", "unittest"], fx.runners(), out)
                    self.assertEqual(SKILL_MODULE, fx.runs()[1]["argv"][-1])

        # An interrupt while the host judges is the commit abandoned, not a host that is down.
        fx = self.clone()
        hook = fx.start("block", 0)
        try:
            deadline = time.monotonic() + 60
            while fx.runners() != ["remote-gate"] and time.monotonic() < deadline:
                time.sleep(0.05)
            os.killpg(hook.pid, signal.SIGINT)
            out, _ = hook.communicate(timeout=120)
        finally:
            if hook.poll() is None:
                os.killpg(hook.pid, signal.SIGKILL)
        self.assertNotEqual(0, hook.returncode, out)
        self.assertEqual(["remote-gate"], fx.runners(), f"an interrupt started the selection here:\n{out}")

    def test_no_host_or_the_local_override_runs_the_suites_here(self) -> None:
        """AC3. Mutants: a connection attempted from a clone naming no host; SDLC_GATE_LOCAL=1
        ignored, or any value of it read as the override; a full run with no selection sent to
        the host."""
        for label, kwargs, extra in (("no host", {"host": False}, {}),
                                     ("SDLC_GATE_LOCAL=1", {}, {"SDLC_GATE_LOCAL": "1"})):
            with self.subTest(label):
                fx = self.clone(**kwargs)
                r = fx.commit_msg(0, 0, **extra)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertEqual(["gate.py"], fx.runners(), "remote-gate was called, or nothing ran here")
                self.assertEqual(["--root", ".", "--run-tests", *SELECTION], fx.runs()[0]["argv"])
                self.assertNotIn("gate host", r.stdout + r.stderr)
        fx = self.clone()
        r = fx.commit_msg(0, 0, SDLC_GATE_LOCAL="0")
        self.assertEqual(["remote-gate"], fx.runners(), "a value other than 1 kept the selection here")
        fx = self.clone(selectors=[])
        r = fx.commit_msg(0, 0)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("remote-gate", fx.runners(), "a full run with no selection went to the host")
        self.assertIn("skill-tests", fx.runners())

    def test_contributing_says_where_the_commit_suites_run(self) -> None:
        """AC4. Mutants: the section silent on the commit's suites, on the fallback, on a busy
        host, or on the override, so it reads as though only a push used the gate host, or as
        though a commit queued behind a push."""
        text = (REPO / "CONTRIBUTING.md").read_text(encoding="utf-8")
        section = text.split("### Hooks and the push", 1)[1].split("\n### ", 1)[0]
        prose = re.sub(r"\s+", " ", section)
        for phrase in ("the commit-msg hook sends the test modules pre-commit selected to the gate host "
                       "`sdlc.gateHost` names",
                       "falls back to running them on this machine when the host cannot be reached",
                       "or when another run holds its lock for more than a minute",
                       "a commit waits at most that long behind a push",
                       "`SDLC_GATE_LOCAL=1` keeps them on this machine"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, prose)


if __name__ == "__main__":
    unittest.main()
