"""US0881: a push runs the full suite once, and CI runs it once.

The push boundary ran module-alone (every skill module in its own interpreter), release-rehearsal
(two fixture projects end to end) and revert-check beside the core gate lanes: about 750 s. It
now runs the full suite ONCE, as the gate's `full-suite` lane, plus the core gate lanes; the
heavy lanes stay at the tag. CI's ci job ran the skill suite twice - once through
`tools/skill-tests.sh` and again under `coverage run` - and now runs it once, under coverage.
The pre-push hook re-reads a red answer from the forge once before refusing (BG0709), because
the forge's ordering is eventually consistent and a stale first row read as a red main.

Every gate call here is SCOPED (`--only`), as `BoundaryGateIsNeverDrivenUnscopedTests` requires,
and every fixture is a throwaway directory.
"""
# test-census-subject: .githooks/pre-push
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml

# Imported as a MODULE so unittest does not collect and re-run its cases here.
import test_pre_push_hook as _pp

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
GATE = SCRIPTS / "gate.py"
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
SKILL_TESTS_REL = ".claude/skills/sdlc-studio/scripts/tests"

#: The lanes that cost minutes each and bind at the tag only.
HEAVY_LANES = ("module-alone", "release-rehearsal", "revert-check")

#: A test module that appends one line to a counter file each time it runs.
COUNTING_TEST = textwrap.dedent('''
    import os, unittest
    from pathlib import Path


    class CountTests(unittest.TestCase):
        def test_counts(self):
            with Path(os.environ["LEAN_PUSH_COUNTER"]).open("a", encoding="utf-8") as f:
                f.write({label!r} + "\\n")
''').lstrip()

RED_TEST = textwrap.dedent('''
    import unittest


    class RedTests(unittest.TestCase):
        def test_red_on_purpose(self):
            self.fail("red on purpose")
''').lstrip()

#: Red, and marked `serial_only`: only the lane's serial phase runs it.
SERIAL_RED_TEST = textwrap.dedent('''
    import unittest
    import pytest


    @pytest.mark.serial_only
    class SerialRedTests(unittest.TestCase):
        def test_red_in_the_serial_phase(self):
            self.fail("red on purpose, serially")
''').lstrip()

#: `gh` for the red-main read: the Nth call answers the Nth word of STUB_GH_MODE (the last word
#: repeats), so a fixture can make the forge answer red and then green.
STUB_GH = textwrap.dedent('''
    #!/usr/bin/env python3
    import json, os, sys
    from pathlib import Path
    log = Path(os.environ["STUB_GH_ARGV"])
    with log.open("a") as f:
        f.write(" ".join(sys.argv[1:]) + "\\n")
    calls = len(log.read_text().splitlines())
    words = os.environ.get("STUB_GH_MODE", "green").split("-")
    mode = words[min(calls, len(words)) - 1]
    if mode == "fail":
        sys.stderr.write("gh: not logged in\\n"); raise SystemExit(4)
    runs = {"stale": {"databaseId": 30118629592, "conclusion": "failure",
                      "url": "https://example.test/runs/30118629592"},
            "red": {"databaseId": 35072343531, "conclusion": "failure",
                    "url": "https://example.test/runs/35072343531"},
            "green": {"databaseId": 35072343530, "conclusion": "success",
                      "url": "https://example.test/runs/35072343530"}}
    print(json.dumps([runs[mode]]))
''').lstrip()


def _fixture_root(tmp: Path) -> Path:
    """A project the gate accepts (it refuses a root with no `sdlc-studio/`)."""
    root = tmp / "proj"
    (root / "sdlc-studio").mkdir(parents=True)
    return root


def _env() -> dict:
    """The caller's environment with every GIT_* variable dropped, so no fixture is steered at
    the outer repository by what a hook handed the suite."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _gate(root: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    base = _env()
    base.update(env or {})
    return subprocess.run([sys.executable, "-B", str(GATE), "--root", str(root), *args],
                          capture_output=True, text=True, timeout=600, check=False, env=base)


def _registered(root: Path, boundary: str | None = None) -> set[str]:
    """The lanes the gate registers at `boundary` (None: the plain per-commit gate), read from
    its own refusal of an unknown lane: that refusal lists every valid name and runs none."""
    at = ["--boundary", boundary] if boundary else []
    r = _gate(root, *at, "--only", "no-such-lane")
    m = re.search(r"valid: ([a-z, -]+)", r.stdout + r.stderr)
    assert m, f"the gate printed no lane roster:\n{r.stdout}{r.stderr}"
    return {n.strip() for n in m.group(1).split(",") if n.strip()}


def _core_lanes() -> set[str]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import gate  # noqa: PLC0415
    return set(gate.DEFAULT_CHECKS)


def _ci_commands() -> list[str]:
    """Every live shell command in the ci job, continuation lines joined, comments dropped."""
    job = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["ci"]
    out = []
    for step in job.get("steps", []):
        if step.get("if") in (False, "false", "${{ false }}"):
            continue
        for line in str(step.get("run", "")).replace("\\\n", " ").splitlines():
            code = " ".join(shlex.split(line, comments=True))
            if code:
                out.append(code)
    return out


#: A command that runs the skill suite, in any of the spellings the workflow has used.
_SKILL_SUITE = re.compile(
    r"tools/skill-tests\.sh|scripts/tests|npm (?:run )?test\b|test:skill|pytest|run-suite\.sh")


class PushBoundaryTests(unittest.TestCase):

    def test_push_runs_the_suite_once(self) -> None:
        """AC1. MUTANTS: (1) register the heavy lanes at push again; (2) drop `full-suite` from
        the push boundary; (3) run the selection plan twice inside the lane; (4) return the
        lane advisory (`blocking: False`), so a red suite no longer refuses the push; (5) run
        only the plan's first (parallel) phase; (6) count a collection error once per worker;
        (7) leave an earlier red's log in place after a green run."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture_root(Path(d))
            lanes = _registered(root, "push")
            self.assertIn("full-suite", lanes, f"the push boundary registers no full-suite lane: {lanes}")
            self.assertLessEqual(_core_lanes(), lanes, "the push boundary dropped a core gate lane")
            for heavy in HEAVY_LANES:
                self.assertNotIn(heavy, lanes, f"{heavy} still runs at the push boundary")
            self.assertNotIn("full-suite", _registered(root),
                             "the full suite runs on every plain gate, not only at a boundary")

            # The lane RUNS the suite, both trees, once each.
            (root / SKILL_TESTS_REL).mkdir(parents=True)
            (root / "tools" / "tests").mkdir(parents=True)
            (root / SKILL_TESTS_REL / "test_skill_probe.py").write_text(
                COUNTING_TEST.format(label="skill"), encoding="utf-8")
            (root / "tools" / "tests" / "test_tool_probe.py").write_text(
                COUNTING_TEST.format(label="tools"), encoding="utf-8")
            counter = Path(d) / "counter.txt"
            r = _gate(root, "--boundary", "push", "--only", "full-suite",
                      env={"LEAN_PUSH_COUNTER": str(counter)})
            out = r.stdout + r.stderr
            self.assertEqual(0, r.returncode, out)
            self.assertIn("[PASS] full-suite", out, out)
            self.assertEqual(["skill", "tools"], sorted(counter.read_text().splitlines()),
                             f"the suite did not run each test exactly once:\n{out}")

            # A red test refuses, and the refusal names it.
            (root / SKILL_TESTS_REL / "test_red_probe.py").write_text(RED_TEST, encoding="utf-8")
            red = _gate(root, "--boundary", "push", "--only", "full-suite",
                        env={"LEAN_PUSH_COUNTER": str(counter)})
            line = next((ln for ln in red.stdout.splitlines() if "full-suite" in ln), "")
            self.assertNotEqual(0, red.returncode, f"a red suite did not fail the push gate:\n{red.stdout}")
            self.assertIn("[FAIL] full-suite", line, red.stdout)
            self.assertIn("test_red_on_purpose", line, "the refusal does not name the red test")
            log = root / "sdlc-studio" / ".local" / "boundary-suite-last.log"
            self.assertTrue(log.exists(), "a red run kept no output")

            # A red test the SERIAL phase alone runs refuses too: the parallel phase deselects it.
            (root / SKILL_TESTS_REL / "test_red_probe.py").unlink()
            (root / SKILL_TESTS_REL / "test_serial_probe.py").write_text(SERIAL_RED_TEST, encoding="utf-8")
            serial = _gate(root, "--boundary", "push", "--only", "full-suite",
                           env={"LEAN_PUSH_COUNTER": str(counter)})
            line = next((ln for ln in serial.stdout.splitlines() if "full-suite" in ln), "")
            self.assertIn("[FAIL] full-suite", line, f"the serial phase did not run:\n{serial.stdout}")
            self.assertIn("test_red_in_the_serial_phase", line, serial.stdout)

            # A module that cannot be collected is named ONCE, however many runs report it: this
            # one names the marker, so both phases collect it and both report the same error.
            (root / SKILL_TESTS_REL / "test_serial_probe.py").unlink()
            (root / SKILL_TESTS_REL / "test_broken_probe.py").write_text(
                "# serial_only\ndef broken(:\n", encoding="utf-8")
            broken = _gate(root, "--boundary", "push", "--only", "full-suite",
                           env={"LEAN_PUSH_COUNTER": str(counter)})
            line = next((ln for ln in broken.stdout.splitlines() if "full-suite" in ln), "")
            self.assertIn("[FAIL] full-suite", line, broken.stdout)
            self.assertIn("1 red - ", line, f"one broken module was counted more than once:\n{line}")

            # Green again: the earlier red's log does not outlive it.
            (root / SKILL_TESTS_REL / "test_broken_probe.py").unlink()
            green = _gate(root, "--boundary", "push", "--only", "full-suite",
                          env={"LEAN_PUSH_COUNTER": str(counter)})
            self.assertEqual(0, green.returncode, green.stdout + green.stderr)
            self.assertFalse(log.exists(), "a green run left the earlier red's log behind")

    def test_the_release_boundary_keeps_the_heavy_lanes(self) -> None:
        """AC2. MUTANTS: (1) drop module-alone from the release boundary; (2) drop
        release-rehearsal from it; (3) register the heavy lanes at no boundary at all."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture_root(Path(d))
            lanes = _registered(root, "release")
            for lane in ("full-suite", *HEAVY_LANES):
                self.assertIn(lane, lanes, f"{lane} does not run at the release boundary")
            self.assertLessEqual(_core_lanes(), lanes)
            # Registered AND run: each heavy lane reports at a tag.
            (root / SKILL_TESTS_REL).mkdir(parents=True)
            (root / SKILL_TESTS_REL / "test_alone_probe.py").write_text(
                COUNTING_TEST.format(label="alone"), encoding="utf-8")
            counter = Path(d) / "counter.txt"
            r = _gate(root, "--boundary", "release", "--only", "module-alone,release-rehearsal",
                      env={"LEAN_PUSH_COUNTER": str(counter)})
            out = r.stdout + r.stderr
            self.assertEqual(0, r.returncode, out)
            self.assertIn("[PASS] module-alone", out, out)
            self.assertIn("release-rehearsal", out, out)
            self.assertEqual(["alone"], counter.read_text().splitlines(), out)

    def test_ci_runs_the_suite_once(self) -> None:
        """AC3. MUTANTS: (1) restore the second, uncovered `tools/skill-tests.sh` run beside the
        coverage run; (2) drop SKILL_TESTS_COVERAGE from the suite command, so nothing is
        measured; (3) drop the `coverage report --fail-under` threshold, or lower it to 10;
        (4) make `tools/skill-tests.sh` ignore SKILL_TESTS_COVERAGE; (5) add a second run as
        `python -m pytest` or `bash tools/run-suite.sh`."""
        cmds = _ci_commands()
        # an install line names `pytest` as a package, not as a run
        suite = [c for c in cmds if _SKILL_SUITE.search(c) and "pip install" not in c]
        self.assertEqual(1, len(suite), f"the ci job runs the skill suite {len(suite)} times: {suite}")
        self.assertIn("SKILL_TESTS_COVERAGE=1", shlex.split(suite[0]),
                      f"the one suite run is not under coverage: {suite[0]}")
        after = cmds[cmds.index(suite[0]) + 1:]
        self.assertTrue(any(re.search(r"\bcoverage report\b.*--fail-under=80\b", c) for c in after),
                        "the 80% coverage threshold is not read after the suite run")

        # The variable really runs the suite under coverage: drive the shipped runner on a
        # fixture skill and read back what coverage measured.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = root / "skill"
            (skill / "tests").mkdir(parents=True)
            (skill / "probe_mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            (skill / "tests" / "test_probe_mod.py").write_text(textwrap.dedent('''
                import sys, unittest
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                import probe_mod


                class T(unittest.TestCase):
                    def test_f(self):
                        self.assertEqual(1, probe_mod.f())
            ''').lstrip(), encoding="utf-8")
            (root / "tools").mkdir()
            for name in ("skill-tests.sh", "test_noise.py"):
                shutil.copy(REPO / "tools" / name, root / "tools" / name)
            (root / "tools" / "test-noise-baseline.json").write_text('{"_total": 0}', encoding="utf-8")
            _pp._git(root, "init", "-q", "-b", "main", str(root))
            env = _env()
            env["SKILL_TESTS_COVERAGE"] = "1"
            r = subprocess.run(["bash", "tools/skill-tests.sh", "skill"], cwd=root, env=env,
                               capture_output=True, text=True, timeout=300, check=False)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            rep = subprocess.run([sys.executable, "-m", "coverage", "report"], cwd=root,
                                 capture_output=True, text=True, timeout=120, check=False)
            self.assertEqual(0, rep.returncode, f"coverage recorded nothing:\n{rep.stdout}{rep.stderr}")
            self.assertIn("probe_mod.py", rep.stdout, rep.stdout)

    def test_a_stale_red_answer_is_re_read(self) -> None:
        """AC4 (BG0709). MUTANTS: (1) no re-read - the stale red refuses; (2) re-read but judge
        the FIRST answer; (3) let an unreadable re-read clear the red; (4) re-read even a green
        answer; (5) banks the stale id offered in SDLC_PUSH_ACK_RED before re-reading."""
        fx = _pp._Clone()
        try:
            path = fx.stub_path()
            (path / "gh").write_text(STUB_GH, encoding="utf-8")
            (path / "gh").chmod(0o755)
            log = fx.tmp / "gh-argv.txt"

            # a stale red, then the true green: the push proceeds and nothing is acknowledged
            r = fx.push(gh_mode="stale-green", ack="30118629592")
            self.assertEqual(0, r.returncode, "a stale red refused the push:\n" + r.stderr)
            self.assertEqual(2, len(fx.gh_calls()), f"the red answer was not re-read once: {fx.gh_calls()}")
            for call in fx.gh_calls():
                for flag in ("--workflow Lint", "--branch main", "--event push", "--status completed"):
                    self.assertIn(flag, call, "the re-read is not the same query")
            self.assertEqual(["--boundary push"], fx.gate_calls(), "the gate did not run after the re-read")
            self.assertFalse(fx.ack_file().exists(), "a stale red id was banked as acknowledged")
            self.assertEqual(1, fx.remote_count())

            # red on both reads: refused, after the re-read, naming the re-read's run
            log.unlink()
            fx.commit_more()
            red = fx.push(gh_mode="stale-red")
            self.assertNotEqual(0, red.returncode, "a red main read twice did not refuse")
            self.assertEqual(2, len(fx.gh_calls()), "the refusal came before a re-read")
            self.assertIn("SDLC_PUSH_ACK_RED=35072343531 git push", red.stderr, red.stderr)
            self.assertEqual(1, fx.remote_count())

            # an unreadable re-read never clears a red
            log.unlink()
            unread = fx.push(gh_mode="stale-fail")
            self.assertNotEqual(0, unread.returncode, "an unreadable re-read cleared a red:\n" + unread.stderr)
            self.assertIn("SDLC_PUSH_ACK_RED=30118629592 git push", unread.stderr, unread.stderr)

            # a green first answer is not read twice
            log.unlink()
            green = fx.push(gh_mode="green")
            self.assertEqual(0, green.returncode, green.stderr)
            self.assertEqual(1, len(fx.gh_calls()), "a green answer was read twice")
        finally:
            fx.cleanup()


if __name__ == "__main__":
    unittest.main()
