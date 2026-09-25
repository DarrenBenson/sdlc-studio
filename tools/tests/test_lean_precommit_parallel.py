"""US0891 and BG0759: a commit's pre-commit lanes run side by side.

The cheap lanes ran one after another: 67s measured on a docs-only commit, against about 22s
for the slowest of them, the gate lane. They now start together, each lane's output is
buffered, and the verdicts print in the order the hook declares them, so the hook reads as it
always did and costs its slowest lane rather than the sum. BG0759 carried the change onto the
hook's `run` lanes and `--list`, kept the suite handover a refusal, and made a hangup or a
terminate stop every lane with the hook.

These tests RUN THE REAL HOOK over `git commit` in a throwaway repository whose every lane is a
stub outside the tree under test. The lanes are read from `pre-commit --list`, and each lane's
command from the hook, so a lane added to the hook is stubbed here with no edit. Each stub's
cost, verdict and output are set per test, and each records when it ran, so what is asserted is
what executed. The fixture carries no `commit-msg` hook: the handover record `pre-commit` writes
for it then survives the commit and is read back.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import importlib.util
import os
import re
import signal
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"
SKILL = ".claude/skills/sdlc-studio/scripts"

#: How long a stubbed lane takes to stop once it is sent SIGTERM, the way a real lane finishes
#: a write before it exits. Long enough that a hook which does not wait for it exits first.
STOP_SECONDS = 0.5


def _load_gitutil():
    """The shipped git-fixture helper, which confines every fixture git call to the fixture:
    loaded rather than re-implemented, so this module carries no scrub list of its own."""
    path = REPO / SKILL / "tests" / "gitutil.py"
    spec = importlib.util.spec_from_file_location("_us0891_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()

#: A printed verdict line: `  ok   <key>` or `  FAIL <key>` (no colour when captured).
_VERDICT = re.compile(r"^ {2}(ok|FAIL)\s+(\S+)")

#: What a lane invokes: a tools/ checker, a skill script, or markdownlint.
_SCRIPT = re.compile(r'(tools/[\w.-]+|"\$skill/[\w.-]+"|\$md_cmd)')

#: The two lines the hook has always printed when a failed lane skips the suite handover.
SUITE_SKIP = ("  SKIP unit suites - a cheaper lane already failed, so the commit is blocked "
              "either way.\n"
              "       Fix the failure above and commit again; the suites run once the cheap "
              "guards are green.\n")


def _declared_lanes(hook: Path) -> list[tuple[str, str | None]]:
    """`(key, script)` for every lane `hook --list` prints, in its order. `hook` is the
    fixture's copy, run inside the fixture, so nothing resolves to the repository under test.

    `script` is what the lane's command invokes, relative to the repository root, or
    `markdownlint`. A command that is one of the hook's own functions (`gate_lane`) is read
    through that function's body; one that invokes no script (`write_handover`) is None."""
    listed = subprocess.run([str(hook), "--list"], cwd=hook.parent, env=_clean_env(),
                            capture_output=True, text=True, check=True, timeout=60).stdout
    text = hook.read_text(encoding="utf-8")
    lanes = []
    for key in (ln.split("\t", 1)[0] for ln in listed.splitlines() if "\t" in ln):
        after = text.split(f'run "{key}"', 1)[1]
        command = re.search(r"(?:^|\s)-- (.+)$", after, re.M).group(1)
        s = _SCRIPT.search(command)
        if s is None:
            fn = re.search(rf"^{re.escape(command.split()[0])}\(\) \{{(.*?)^\}}", text,
                           re.M | re.S)
            s = _SCRIPT.search(fn.group(1)) if fn else None
        script = (None if s is None else s.group(1).strip('"').replace("$skill", SKILL)
                  .replace("$md_cmd", "markdownlint"))
        lanes.append((key, script))
    return lanes


def _clean_env(**extra: str) -> dict:
    return gitutil.git_env(PYTHONDONTWRITEBYTECODE="1", **extra)


class ParallelLaneTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="us0891-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.root = base / "r"
        self.stubs = base / "stubs"          # each lane's behaviour, outside the repo
        self.finished = base / "finished"    # the order the lanes finished in
        self.tmpdir = base / "hook-tmp"      # the hook's TMPDIR, to see it cleaned up
        for d in (self.root / ".githooks", self.root / "tools", self.root / SKILL,
                  self.root / "node_modules" / ".bin", self.root / "docs", self.stubs,
                  self.tmpdir):
            d.mkdir(parents=True, exist_ok=True)
        hook = self.root / ".githooks" / "pre-commit"
        shutil.copyfile(HOOK, hook)
        hook.chmod(0o755)

        # The lanes that run a script, stubbed here. `suite-handover` writes the record for
        # commit-msg and runs only once the suites are selected, so it is judged separately.
        self.lanes = [(key, script) for key, script in _declared_lanes(hook) if script]
        self.keys = [key for key, _ in self.lanes]
        for key, script in self.lanes:
            if script == "markdownlint":
                continue
            path = self.root / script
            path.parent.mkdir(parents=True, exist_ok=True)
            runner = self.stubs / f"{key}.py"
            if script.endswith(".sh"):
                path.write_text(f'#!/usr/bin/env bash\nexec python3 "{runner}" "$@"\n',
                                encoding="utf-8")
            elif script.endswith("/gate.py"):
                # One script, two callers: the gate lane, and the suite selection below it.
                path.write_text(
                    "import runpy, sys\n"
                    f"name = 'suite-decision' if '--suite-decision' in sys.argv else {key!r}\n"
                    f"runpy.run_path({str(self.stubs)!r} + '/' + name + '.py',"
                    " run_name='__main__')\n", encoding="utf-8")
            else:
                path.write_text(f"import runpy\nrunpy.run_path({str(runner)!r}, "
                                "run_name='__main__')\n", encoding="utf-8")
        md = self.root / "node_modules" / ".bin" / "markdownlint"
        md.write_text('#!/usr/bin/env bash\ncase " $* " in\n'
                      f'  *" --config "*) exec python3 "{self.stubs}/markdown-payload.py" ;;\n'
                      f'  *) exec python3 "{self.stubs}/markdown.py" ;;\nesac\n',
                      encoding="utf-8")
        md.chmod(0o755)
        # Read only when the gate fails, for its drift detail.
        (self.root / SKILL / "reconcile.py").write_text("print('{}')\n", encoding="utf-8")
        for key in self.keys:
            self._behave(key)
        self._select(None)

        # A tracked markdown file for each markdown lane, or the lane prints a SKIP instead.
        (self.root / "docs" / "notes.md").write_text("# notes\n", encoding="utf-8")
        (self.root / ".claude" / "skills" / "sdlc-studio" / "NOTES.md").write_text(
            "# payload\n", encoding="utf-8")
        self._git("init", "-q")
        self._git("add", "-A")
        self._git("commit", "-q", "--no-verify", "-m", "fixture")
        self._git("config", "core.hooksPath", ".githooks")

    # -- fixture helpers ------------------------------------------------------------------

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True,
                              text=True, env=_clean_env(), check=False)

    def _behave(self, key: str, *, sleep: float = 0.0, rc: int = 0,
                kill_lane: bool = False, ignore_term: bool = False) -> None:
        """Lane `key` records its start and pid, sleeps, prints two lines naming itself,
        records its finish, exits `rc`. Sent SIGTERM, it takes STOP_SECONDS to stop and
        records when it did; with `ignore_term` it ignores SIGTERM altogether.

        With `kill_lane` it SIGKILLs its own process group, whose leader is the lane's
        subshell, so the lane ends without an exit status. Only when that group is not this
        test runner's: were the lanes started without a group of their own, the kill would
        take the runner down instead, so the stub then runs as a plain passing lane and the
        test fails on the commit it lets through.

        The gate's lines are spelt the way the hook's filter keeps them."""
        lines = (["[FAIL] probe <<gate>>", "gate: 1 failing <<gate>>"] if key == "gate"
                 else [f"detail-1 <<{key}>>", f"detail-2 <<{key}>>"])
        (self.stubs / f"{key}.py").write_text(
            "import os, signal, sys, time\n"
            "start = time.time()\n"
            "def stop(*_):\n"
            f"    time.sleep({STOP_SECONDS})\n"
            f"    with open({str(self._stopped_log())!r}, 'a') as fh:\n"
            f"        fh.write('%s %f\\n' % ({key!r}, time.time()))\n"
            "    os._exit(143)\n"
            + ("signal.signal(signal.SIGTERM, signal.SIG_IGN)\n" if ignore_term
               else "signal.signal(signal.SIGTERM, stop)\n")
            + f"with open({str(self._started_log())!r}, 'a') as fh:\n"
            f"    fh.write('%s %d\\n' % ({key!r}, os.getpid()))\n"
            + (f"if os.getpgid(0) != {os.getpgid(0)}:\n"
               "    os.kill(os.getpgid(0), signal.SIGKILL)\n" if kill_lane else "")
            + f"time.sleep({sleep})\n"
            f"print({lines[0]!r})\nprint({lines[1]!r})\n"
            f"with open({str(self.finished)!r}, 'a') as fh:\n"
            f"    fh.write({key!r} + '\\n')\n"
            f"with open({str(self.finished)!r} + '.spans', 'a') as fh:\n"
            f"    fh.write('%s %f %f\\n' % ({key!r}, start, time.time()))\n"
            f"sys.exit({rc})\n", encoding="utf-8")

    def _select(self, selectors: list[str] | None) -> None:
        """What the suite selection answers: `run` with these selectors, or `skip`."""
        if selectors is None:
            body = "print('suite-decision: skip - the stub selects nothing')\n"
        else:
            body = ("print('suite-decision: run')\n"
                    + "".join(f"print('suite-selector: {s}')\n" for s in selectors))
        (self.stubs / "suite-decision.py").write_text(
            f"with open({str(self.stubs / 'selections')!r}, 'a') as fh:\n"
            "    fh.write('asked\\n')\n" + body, encoding="utf-8")

    def _stage(self, path: str) -> None:
        """Stage an edit to `path`, and clear the lanes' logs for the run that follows."""
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write("more\n")
        self._git("add", "-A")
        for log in (self.finished, self._spans_log(), self._started_log(),
                    self._stopped_log()):
            if log.exists():
                log.unlink()

    def _commit(self, path: str = "docs/notes.md", **env: str) -> tuple[int, str, float]:
        """Stage an edit to `path` and commit it through the hook: (rc, output, seconds)."""
        self._stage(path)
        t0 = time.monotonic()
        r = subprocess.run(["git", "-C", str(self.root), "commit", "-q", "-m", "a change"],
                           capture_output=True, text=True, check=False, timeout=120,
                           env=_clean_env(TMPDIR=str(self.tmpdir), **env))
        return r.returncode, r.stdout + r.stderr, time.monotonic() - t0

    def _signal_mid_run(self, sig: int, *, sleep: float = 3,
                        stubborn: str | None = None) -> tuple[int, float, float, str]:
        """Run the hook the way a terminal runs it, as the leader of its own process group,
        with every lane taking `sleep` seconds and lane `stubborn`, if named, ignoring SIGTERM.
        Once every lane is running, send `sig` to that group.

        Returns the hook's exit code, when the signal was sent and when the hook had exited
        (both `time.time()`), and what the hook printed."""
        for key in self.keys:
            self._behave(key, sleep=sleep, ignore_term=key == stubborn)
        self._stage("docs/notes.md")
        out_file = self.tmpdir.parent / "hook-output"
        with out_file.open("w", encoding="utf-8") as out:
            hook = subprocess.Popen(["bash", ".githooks/pre-commit"], cwd=self.root,
                                    stdout=out, stderr=subprocess.STDOUT,
                                    start_new_session=True,
                                    env=_clean_env(TMPDIR=str(self.tmpdir)))
            try:
                deadline = time.monotonic() + 20
                while len(self._started()) < len(self.keys) and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertEqual(sorted(self._started()), sorted(self.keys),
                                 "not every lane started, so the test would prove nothing")
                sent = time.time()
                os.killpg(hook.pid, sig)
                rc = hook.wait(timeout=20)
                exited = time.time()
            finally:
                if hook.poll() is None:
                    os.killpg(hook.pid, signal.SIGKILL)
        return rc, sent, exited, out_file.read_text(encoding="utf-8")

    def _assert_every_lane_stopped_with_the_hook(self, exited: float, out: str) -> None:
        """No lane process outlives the hook, none writes after it exits, it printed nothing
        past its header, and no buffer is left under TMPDIR."""
        survivors = [key for key, pid in self._started().items() if _alive(pid)]
        self.assertEqual(survivors, [], "these lanes were still running when the hook exited")
        time.sleep(4)     # past the moment every lane would have finished, had it lived
        survivors = [key for key, pid in self._started().items() if _alive(pid)]
        self.assertEqual(survivors, [], "these lanes outlived the hook")
        self.assertFalse(self.finished.exists(),
                         "a lane ran to completion after the hook was stopped: "
                         + (self.finished.read_text(encoding="utf-8")
                            if self.finished.exists() else ""))
        late = {key: at - exited for key, at in self._stopped().items() if at > exited}
        self.assertEqual(late, {}, "these lanes wrote after the hook exited (seconds after)")
        self.assertEqual(out.strip(), "sdlc-studio pre-commit gate",
                         "the stopped hook printed more than its header")
        self.assertEqual(list(self.tmpdir.iterdir()), [], "the lane buffers were left behind")

    def _started_log(self) -> Path:
        return self.finished.with_name(self.finished.name + ".started")

    def _stopped_log(self) -> Path:
        return self.finished.with_name(self.finished.name + ".stopped")

    def _started(self) -> dict[str, int]:
        """The pid each lane started with, by key."""
        if not self._started_log().exists():
            return {}
        rows = (ln.split() for ln in self._started_log().read_text(encoding="utf-8").splitlines())
        return {key: int(pid) for key, pid in rows}

    def _stopped(self) -> dict[str, float]:
        """When each lane that was sent SIGTERM finished stopping, by key."""
        if not self._stopped_log().exists():
            return {}
        rows = (ln.split() for ln in self._stopped_log().read_text(encoding="utf-8").splitlines())
        return {key: float(at) for key, at in rows}

    def _finish_order(self) -> list[str]:
        return self.finished.read_text(encoding="utf-8").split()

    def _spans_log(self) -> Path:
        return self.finished.with_name(self.finished.name + ".spans")

    def _spans(self) -> dict[str, tuple[float, float]]:
        """When each lane started and finished, by key."""
        rows = (ln.split() for ln in self._spans_log().read_text(encoding="utf-8").splitlines())
        return {key: (float(start), float(end)) for key, start, end in rows}

    def _handoff(self) -> Path:
        return self.root / ".git" / "sdlc-gate-suites"

    # -- the criteria ---------------------------------------------------------------------

    def test_the_lanes_run_concurrently(self) -> None:
        """US0891 AC1, BG0759 AC1. MUTANTS: run each lane to completion before starting the
        next, as the hook did; or run the gate lane in sequence after the others are collected.

        Five lanes, the gate lane among them, each cost 2s; the rest cost nothing. In
        sequence the hook takes at least 10s; together it takes one lane's 2s and the
        overhead. The wall-clock bar alone cannot see the second mutant (2s + 2s is under
        6s), so each lane also records when it ran, and all five must have been running at
        one moment - the gate lane included."""
        slow = ["style", "links", "neutrality", "dead-flags", "gate"]
        for key in slow:
            self.assertIn(key, self.keys, f"pre-commit --list no longer names a {key} lane")
            self._behave(key, sleep=2)
        rc, out, secs = self._commit()
        self.assertEqual(rc, 0, out)
        spans = self._spans()
        for key in slow:
            self.assertIn(key, spans, f"the {key} lane never ran:\n{out}")
        self.assertLess(secs, 0.6 * 2 * len(slow),
                        f"the commit took {secs:.1f}s against {2 * len(slow)}s of lanes, so "
                        f"they still run in sequence:\n{out}")
        last_start = max(spans[k][0] for k in slow)
        first_end = min(spans[k][1] for k in slow)
        self.assertLess(last_start, first_end,
                        f"the five slow lanes were never all running at once: {spans}")

    def test_output_prints_in_declared_order_whatever_finishes_first(self) -> None:
        """US0891 AC2. MUTANT: print each lane's block as it finishes rather than in declared
        order; or let every lane write straight to the terminal, so blocks interleave.

        Each lane sleeps longer the earlier it is declared, so they finish in reverse. Every
        other lane fails, so the output carries whole FAIL blocks (verdict, enforces, the
        lane's own two detail lines, fix) as well as one-line ok blocks."""
        n = len(self.keys)
        failing = set(self.keys[::2])
        for i, key in enumerate(self.keys):
            self._behave(key, sleep=0.25 * (n - i), rc=1 if key in failing else 0)
        for attempt in range(3):
            with self.subTest(run=attempt + 1):
                rc, out, _ = self._commit()
                self.assertNotEqual(rc, 0, out)
                # The Given held: they finished in the reverse of their declared order.
                self.assertEqual(self._finish_order(), list(reversed(self.keys)))
                verdicts = [m.groups() for m in map(_VERDICT.match, out.splitlines()) if m]
                self.assertEqual([k for _, k in verdicts], self.keys,
                                 f"the verdicts did not print in declared order:\n{out}")
                self.assertEqual({k for v, k in verdicts if v == "FAIL"}, failing, out)
                self._assert_blocks_whole(out, failing)

    def _assert_blocks_whole(self, out: str, failing: set) -> None:
        """Every line naming a lane sits inside that lane's own block."""
        owner = None
        for line in out.splitlines():
            m = _VERDICT.match(line)
            if m:
                owner = m.group(2)
                continue
            named = re.findall(r"<<([\w-]+)>>", line)
            for key in named:
                self.assertEqual(key, owner, f"{key}'s output printed inside {owner}'s block, "
                                             f"so the blocks interleave:\n{out}")
        for key in failing:
            block = re.split(r"\n {2}(?=ok|FAIL|SKIP|note)", out.split(f"FAIL {key}\n", 1)[1])[0]
            first = "[FAIL] probe" if key == "gate" else "detail-1"
            self.assertIn(f"{first} <<{key}>>", block, f"{key}'s block lost its output:\n{out}")
            self.assertIn("fix:", block, f"{key}'s block lost its fix:\n{out}")
            self.assertRegex(block, r"^ +enforces: ", f"{key}'s block lost its rule:\n{out}")

    def test_a_failing_lane_still_refuses_and_skips_the_suites(self) -> None:
        """US0891 AC3. MUTANTS: lose a lane's exit status in the background (every lane then
        reads green); stop reading the buffered verdicts before the last lane; run the suite
        selection before the lanes' verdicts are in, so a refused commit still pays for it;
        drop the selection's `suite-selector` lines from the handover.

        Then the control: every lane passing, the staged change selects two modules, and the
        record handed to commit-msg carries them, in order, exactly as the hook wrote them
        before the lanes ran side by side."""
        self._behave("neutrality", rc=1)
        self._select(["tools/tests/test_a.py", "tools/tests/test_b.py::T::test_x"])
        rc, out, _ = self._commit("tools/thing.py")
        self.assertNotEqual(rc, 0, f"a failing lane did not refuse the commit:\n{out}")
        self.assertRegex(out, r"(?m)^  FAIL neutrality\n +enforces: no private consuming-"
                              r"project name.*\n +. details .\n +detail-1 <<neutrality>>\n"
                              r" +detail-2 <<neutrality>>\n +. fix: generalise the name")
        verdicts = [m.groups() for m in map(_VERDICT.match, out.splitlines()) if m]
        self.assertEqual(verdicts, [("FAIL" if k == "neutrality" else "ok", k)
                                    for k in self.keys],
                         f"a lane's verdict is missing or out of place:\n{out}")
        self.assertIn(SUITE_SKIP, out, "the suite skip is not named as it was")
        self.assertIn("Commit blocked.", out)
        self.assertFalse((self.stubs / "selections").exists(),
                         "the suite selection ran for a commit a lane had already refused")
        self.assertFalse(self._handoff().exists(), "a refused commit left a handover behind")
        self.assertEqual(self._git("log", "--format=%s").stdout.split("\n")[0], "fixture")
        self.assertEqual(list(self.tmpdir.iterdir()), [], "the lane buffers were left behind")

        self._behave("neutrality")
        rc, out, _ = self._commit("tools/thing.py")
        self.assertEqual(rc, 0, out)
        self.assertIn("unit suites selected", out)
        record = self._handoff().read_text(encoding="utf-8").splitlines()
        self.assertRegex(record[0], r"^precommit_seconds=\d+$")
        self.assertEqual(record[1:], ["suite-selector=tools/tests/test_a.py",
                                      "suite-selector=tools/tests/test_b.py::T::test_x"])
        self.assertEqual(list(self.tmpdir.iterdir()), [], "the lane buffers were left behind")

    def test_an_unwritable_handover_still_refuses_with_the_lanes_parallel(self) -> None:
        """BG0759 AC2. MUTANT: the naive rebase, where `run "suite-handover"` starts the lane
        in the background and `$fail` is read before anything collects its verdict, so the
        commit passes with the suites never run.

        A directory where the record goes makes the write fail for a reason the hook cannot
        talk itself out of. Every other lane passes. Then the control: the same commit with a
        writable git directory passes and hands the selection over."""
        self._select(["tools/tests/test_a.py"])
        self._handoff().mkdir(parents=True)
        rc, out, _ = self._commit("tools/thing.py")
        self.assertNotEqual(rc, 0, f"an unwritable handover passed the commit:\n{out}")
        verdicts = [m.groups() for m in map(_VERDICT.match, out.splitlines()) if m]
        self.assertEqual(verdicts, [("ok", k) for k in self.keys] + [("FAIL", "suite-handover")],
                         out)
        self.assertIn("the selection could not be written to", out)
        self.assertIn("Commit blocked.", out)
        self.assertNotIn("unit suites selected", out)
        self.assertEqual(self._git("log", "--format=%s").stdout.split("\n")[0], "fixture")

        self._handoff().rmdir()
        rc, out, _ = self._commit("tools/thing.py")
        self.assertEqual(rc, 0, out)
        self.assertIn("  ok   suite-handover", out.splitlines(), out)
        self.assertEqual(self._handoff().read_text(encoding="utf-8").splitlines()[1:],
                         ["suite-selector=tools/tests/test_a.py"])
        self.assertEqual(list(self.tmpdir.iterdir()), [], "the lane buffers were left behind")

    # -- a lane is never left behind, and never silently lost ------------------------------

    def test_a_ctrl_c_stops_every_lane_with_the_hook(self) -> None:
        """MUTANTS: drop the INT trap; or start the lanes without `set -m`, so they share the
        hook's process group and the trap's group kill reaches only each lane's subshell.

        A background job in a script ignores SIGINT, and so does everything it starts.
        SIGINT goes to the hook's group once every lane is running - what Ctrl-C does. Every
        lane process is gone when the hook exits 130, and it prints nothing past its header."""
        rc, _, exited, out = self._signal_mid_run(signal.SIGINT)
        self.assertEqual(rc, 130, out)
        self._assert_every_lane_stopped_with_the_hook(exited, out)

    def test_a_hangup_or_terminate_stops_every_lane_with_the_hook(self) -> None:
        """BG0759 AC3. MUTANTS: no HUP trap (the carried patch), so a dropped SSH session or a
        closed terminal ends the hook and orphans every lane, which `set -m` moved out of the
        group the hangup reaches; drop the TERM trap; drop `stop_lanes`' wait, so the hook
        exits and the EXIT trap removes the buffers while the lanes are still stopping.

        Each lane takes STOP_SECONDS to stop once sent SIGTERM, as a real lane finishing a
        write does, and records when it stopped: all of it must happen before the hook exits.
        The hook stops within 3s of the signal: a lane that stops cannot hold it longer."""
        for sig, code in ((signal.SIGHUP, 129), (signal.SIGTERM, 143)):
            with self.subTest(signal=sig.name):
                rc, sent, exited, out = self._signal_mid_run(sig)
                self.assertEqual(rc, code, out)
                self.assertEqual(sorted(self._stopped()), sorted(self.keys),
                                 "not every lane was stopped by the hook")
                self.assertLess(exited - sent, 3, "the hook took too long to stop")
                self._assert_every_lane_stopped_with_the_hook(exited, out)

    def test_a_lane_that_ignores_terminate_is_killed_rather_than_hanging_the_hook(self) -> None:
        """MUTANTS: poll a lane's group with no bound, so the hook never exits; or stop polling
        without the SIGKILL, so the lane runs on after the hook.

        The neutrality lane ignores SIGTERM and would run 10s. The hook gives the lanes 5s to
        stop, then kills what is left and exits 143 with nothing of that lane still running."""
        rc, sent, exited, out = self._signal_mid_run(signal.SIGTERM, sleep=10,
                                                     stubborn="neutrality")
        self.assertEqual(rc, 143, out)
        self.assertLess(exited - sent, 8, "the hook waited on a lane that ignores SIGTERM")
        pid = self._started()["neutrality"]
        self.assertFalse(_alive(pid), "the lane that ignored SIGTERM outlived the hook")

    def test_a_lane_that_ends_without_a_status_is_named_and_refuses(self) -> None:
        """MUTANTS: read a missing status as a pass (`cat rc || echo 0`); drop the line that
        names the lane.

        The neutrality lane's stub SIGKILLs its own lane's process group, so the slot never
        gets an exit status. The commit is refused, and that lane's verdict line says why, in
        its declared place among the others."""
        self._behave("neutrality", kill_lane=True)
        rc, out, _ = self._commit()
        self.assertNotEqual(rc, 0, f"a lane with no exit status passed the commit:\n{out}")
        self.assertRegex(out, r"(?m)^  FAIL neutrality - the lane ended without an exit "
                              r"status, so its verdict is unknown$")
        verdicts = [m.groups() for m in map(_VERDICT.match, out.splitlines()) if m]
        self.assertEqual([k for _, k in verdicts], self.keys, out)
        self.assertIn("Commit blocked.", out)

    def test_the_markdown_skip_notes_keep_their_place(self) -> None:
        """MUTANT: print either markdown SKIP note directly rather than through a slot. It
        then reaches the terminal before every buffered verdict above it."""
        cases = (("markdown", "docs/notes.md",
                  "  SKIP markdown - no tracked markdown outside the payload."),
                 ("markdown-payload", ".claude/skills/sdlc-studio/NOTES.md",
                  "  SKIP markdown-payload - no tracked markdown under .claude/."))
        for key, only_file, note in cases:
            with self.subTest(skipped=key):
                self._git("rm", "-q", "--cached", "--ignore-unmatch", only_file)
                (self.root / only_file).unlink(missing_ok=True)
                rc, out, _ = self._commit("notes.txt")
                self.assertEqual(rc, 0, out)
                lines = out.splitlines()
                self.assertIn(note, lines, out)
                ran = [k for k in self.keys if k != key]
                self.assertEqual([m.group(2) for m in map(_VERDICT.match, lines) if m], ran,
                                 out)
                # The note sits exactly where the skipped lane's verdict would have: straight
                # after the verdict of the lane declared before it.
                before = _VERDICT.match(lines[lines.index(note) - 1])
                self.assertIsNotNone(before, f"the note is not below a verdict:\n{out}")
                self.assertEqual(before.group(2), self.keys[self.keys.index(key) - 1], out)
                # Put the file back for the next case.
                (self.root / only_file).write_text("# back\n", encoding="utf-8")

    def test_the_markdownlint_absent_note_prints_after_every_verdict(self) -> None:
        """MUTANT: drop the `collect` before the markdownlint-absent SKIP note. The note is
        printed directly, so without it the note lands before every buffered verdict."""
        (self.root / "node_modules" / ".bin" / "markdownlint").unlink()
        path = os.pathsep.join(d for d in os.environ.get("PATH", "").split(os.pathsep)
                               if not (Path(d) / "markdownlint").exists())
        rc, out, _ = self._commit(PATH=path)
        self.assertEqual(rc, 0, out)
        lines = out.splitlines()
        note = next((i for i, ln in enumerate(lines)
                     if ln.startswith("  SKIP markdown - markdownlint not found")), None)
        self.assertIsNotNone(note, out)
        ran = [k for k in self.keys if not k.startswith("markdown")]
        self.assertEqual([m.group(2) for m in map(_VERDICT.match, lines) if m], ran, out)
        self.assertGreater(note, _index_of_verdict(lines, ran[-1]),
                           f"the note printed before the lanes' verdicts:\n{out}")


def _index_of_verdict(lines: list[str], key: str) -> int:
    return next(i for i, ln in enumerate(lines)
                if (m := _VERDICT.match(ln)) and m.group(2) == key)


def _alive(pid: int) -> bool:
    """True while `pid` is a live process; a zombie awaiting its reaper counts as gone."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    stat = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True,
                          text=True, check=False).stdout.strip()
    return bool(stat) and not stat.startswith("Z")


if __name__ == "__main__":
    unittest.main()
