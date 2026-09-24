"""US0879: a commit runs only the checks that catch real defects.

The back-to-basics gate audit found seven per-commit lanes that checked documents against
documents and caught nothing in 1,870 commit messages: runbook, lens-signatures, spec-claims
(whose timing claims deadlocked every fresh worktree, BG0746), practice-rules, the advisory
claim-drift and lane-check, and commit-msg's suite-claim. They are gone from both hooks, and the
pre-commit hook's inline copy of the concurrent-write window guard is gone with them: the gate's
`window` lane is the one implementation.

These tests DRIVE THE REAL HOOKS in the hermetic fixture `test_precommit_window_guard.py` builds
(every hook-invoked script stubbed to pass), so what they pin is what a commit runs, not what the
hook text happens to say.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

# Imported as a MODULE so unittest does not collect and re-run its cases here.
import test_precommit_window_guard as _wg

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / ".githooks"
GATE = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"

#: The lanes the audit deleted, by the key each ran under.
DELETED_LANES = ("runbook", "lens-signatures", "spec-claims", "practice-rules",
                 "claim-drift", "lane-check", "suite-claim")

#: What each deleted lane invoked. A hook that calls one of these runs the lane under any key.
#: HAND-MAINTAINED ON PURPOSE: the deleted set is the assertion, and nothing in the tree owns it
#: any more to derive it from.
DELETED_COMMANDS = ("check_spec_claims.py", "runbook.py", "best_practice_rules.py",
                    "profile --validate", "lane-check", "run-suite.sh")

#: Where the fixture's tripwire stand-ins for the deleted commands log that they were run.
TRIPWIRE_LOG = "sdlc-studio/.local/deleted-lane-tripwire.log"

ROSTER_OPENING = "The pre-commit lanes, recorded here"


def _code(hook: str) -> str:
    """The hook's executable lines: comments say what a lane USED to do, and may."""
    text = (HOOKS / hook).read_text(encoding="utf-8")
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _run_keys(hook: str) -> set:
    return set(re.findall(r'^\s*run\s+"([^"]+)"', _code(hook), re.M))


def _gate_lanes() -> set:
    """The standard gate's lane names, read from its DEFAULT_CHECKS table."""
    block = re.search(r"^DEFAULT_CHECKS = \{(.*?)^\}", GATE.read_text(encoding="utf-8"),
                      re.M | re.S)
    return set(re.findall(r'^\s*"([a-z-]+)":', block.group(1), re.M))


def _roster() -> str:
    """AGENTS.md's per-commit lane roster: its own paragraph, never a window around it."""
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    start = agents.index(ROSTER_OPENING)
    end = agents.find("\n\n", start)
    return agents[start:end if end != -1 else len(agents)]


def _fixture(tmp: Path) -> Path:
    """The hermetic hook fixture: real hooks, every hook-invoked script stubbed to pass."""
    return _wg.WindowGuardTests("run")._repo(tmp)


def _write(root: Path, rel: str, body: str, mode: int | None = None) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def _commit(root: Path, files: dict, message: str = "docs: paperwork") -> tuple[int, str]:
    for rel, body in files.items():
        _write(root, rel, body)
    _wg._git(root, "add", "-A")
    out = subprocess.run(["git", "-C", str(root), "commit", "-m", message],
                         capture_output=True, text=True, env=_wg._clean_env())
    return out.returncode, out.stdout + out.stderr


def _tripwire_py(name: str, when: str = "True") -> str:
    """A stand-in that, when `when` holds for its argv, logs its run and fails - so a deleted
    lane put back into a hook both leaves a trace and refuses the commit."""
    return (
        "import sys\n"
        "args = sys.argv[1:]\n"
        f"if {when}:\n"
        f"    with open({TRIPWIRE_LOG!r}, 'a', encoding='utf-8') as fh:\n"
        f"        fh.write({name!r} + ' ' + ' '.join(args) + '\\n')\n"
        "    print('CLAIM-DRIFT: tripwire', file=sys.stderr)\n"
        "    print('LANE-CHECK: tripwire', file=sys.stderr)\n"
        "    sys.exit(1)\n"
        "sys.exit(0)\n")


def _arm_tripwires(root: Path) -> None:
    """A stand-in for every command a deleted lane ran. `verify_ac.py` and `readiness.py` keep
    their other verbs, so only the deleted verb trips."""
    scripts = ".claude/skills/sdlc-studio/scripts"
    for rel, name in (("tools/check_spec_claims.py", "spec-claims"),
                      ("tools/runbook.py", "runbook"),
                      ("tools/best_practice_rules.py", "practice-rules")):
        _write(root, rel, _tripwire_py(name))
    _write(root, f"{scripts}/verify_ac.py", _tripwire_py("lane-check", "'lane-check' in args"))
    _write(root, f"{scripts}/readiness.py",
           _tripwire_py("lens-signatures", "'--validate' in args"))
    _write(root, "tools/run-suite.sh",
           "#!/usr/bin/env bash\n"
           f"echo \"suite-claim $*\" >> {TRIPWIRE_LOG}\n"
           "echo 'suite verdict: RED' >&2\nexit 1\n", mode=0o755)


def _markdownlint() -> str | None:
    """markdownlint from this checkout, the main clone a worktree shares, or PATH."""
    candidates = [REPO / "node_modules" / ".bin" / "markdownlint"]
    common = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-common-dir"],
                            capture_output=True, text=True, env=_wg._clean_env())
    if common.returncode == 0 and common.stdout.strip():
        main = (REPO / common.stdout.strip()).resolve().parent
        candidates.append(main / "node_modules" / ".bin" / "markdownlint")
    for c in candidates:
        if c.exists():
            return str(c)
    return shutil.which("markdownlint")


class CommitLaneTests(unittest.TestCase):

    def test_the_deleted_lanes_do_not_run(self) -> None:
        """AC1. MUTANTS: put any deleted lane back into either hook - a `run "spec-claims"`
        line, the claim-drift or lane-check block, the suite-claim check - or name one in the
        AGENTS.md roster, or drop a lane that runs from it."""
        # 1. By EXECUTION: a commit shaped to reach every deleted lane - a tools/ change (so the
        # suites are selected), a staged path carrying a unit id (lane-check's trigger) and a
        # message claiming the suites are green (suite-claim's) - over tripwires that log and
        # refuse. The commit lands and no tripwire fires.
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _arm_tripwires(root)
            _wg._git(root, "add", "-A")
            _wg._git(root, "commit", "-q", "--no-verify", "-m", "tripwires")
            rc, out = _commit(root, {"tools/thing.py": "VALUE = 2\n",
                                     "docs/US0001-note.md": "# Note\n"},
                              message="chore: both suites are green")
            log = root / TRIPWIRE_LOG
            fired = log.read_text(encoding="utf-8") if log.exists() else ""
            self.assertEqual("", fired, f"a deleted lane ran:\n{fired}\n{out}")
            self.assertEqual(0, rc, f"the commit was refused:\n{out}")
            for lane in DELETED_LANES:
                self.assertNotRegex(out, rf"\b(ok|FAIL)\b\s+{re.escape(lane)}\b",
                                    f"the hook ran the deleted `{lane}` lane")
            for marker in ("CLAIM-DRIFT", "LANE-CHECK", "suite-claim"):
                self.assertNotIn(marker, out)
            # The positive control: the fixture reached the kept lanes and the end of the gate.
            self.assertRegex(out, r"\bok\b\s+style\b")
            self.assertIn("gate green.", out)
        # 2. In the hooks' executable lines, under any key.
        for hook in ("pre-commit", "commit-msg"):
            code = _code(hook)
            for lane in DELETED_LANES:
                with self.subTest(hook=hook, lane=lane):
                    self.assertNotIn(f'run "{lane}"', code)
            for command in DELETED_COMMANDS:
                with self.subTest(hook=hook, command=command):
                    self.assertNotIn(command, code, f"{hook} still invokes {command}")
        # 3. The roster names exactly the lanes that run, in both directions.
        roster = _roster()
        ticked = set(re.findall(r"`([^`]+)`", roster))
        run_keys = _run_keys("pre-commit") | _run_keys("commit-msg")
        for key in sorted(run_keys):
            with self.subTest(lane=key):
                self.assertIn(key, ticked, f"the `{key}` lane runs and the roster omits it")
        names = {t for t in ticked if re.fullmatch(r"[a-z][a-z0-9-]*", t)}
        allowed = run_keys | _gate_lanes() | {"pre-commit", "commit-msg"}
        self.assertEqual(set(), names - allowed,
                         "the roster names a lane no hook runs")
        for lane in DELETED_LANES:
            self.assertNotIn(lane, roster, f"the roster still names the deleted `{lane}`")
        hook_code = _code("pre-commit") + _code("commit-msg")
        lane_scripts = set(re.findall(r"--\s+(?:python3|bash)\s+\"?(?:\$skill/|\S*/)?"
                                      r"([\w-]+\.(?:py|sh))", hook_code))
        roster_scripts = {m.group(1) for t in ticked
                          for m in [re.match(r"(?:\S*/)?([\w-]+\.(?:py|sh))\b", t)] if m}
        self.assertEqual(set(), lane_scripts - roster_scripts,
                         "a lane's script is missing from the roster")
        self.assertEqual(set(), {s for s in roster_scripts if s not in hook_code},
                         "the roster names a script no hook runs")

    def test_a_slow_first_sample_never_blocks_a_commit(self) -> None:
        """AC2, BG0746. A fresh worktree's timing store holds one sample, and a slow machine's
        first sample sat above the TSD's `measured:` ceiling, so the spec-claims lane refused
        every commit - including the one that would have recorded a faster sample.

        MUTANTS: put the spec-claims lane back (its stand-in here refuses, as the real one did
        over this store); make any timing reading in either hook refuse a slow sample."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            shutil.copy2(REPO / "tools" / "gate_timing.py", root / "tools" / "gate_timing.py")
            _write(root, "tools/check_spec_claims.py", _tripwire_py("spec-claims"))
            _write(root, "sdlc-studio/tsd.md",
                   "# TSD\n\nThe suites take minutes <!-- measured: skill-tests <= 950s --> "
                   "<!-- measured: tool-tests <= 250s -->.\n")
            _wg._git(root, "add", "-A")
            _wg._git(root, "commit", "-q", "--no-verify", "-m", "a TSD with timing claims")
            # AFTER the fixture commit: the store is gitignored local state, one slow sample.
            _write(root, "sdlc-studio/.local/gate-timings.json",
                   json.dumps({"skill-tests": [9999.0], "tool-tests": [9999.0]}))
            rc, out = _commit(root, {"tools/thing.py": "VALUE = 3\n"})
            self.assertEqual(0, rc, f"a timing claim refused the commit:\n{out}")
            self.assertIn("gate green.", out)
            # The control: the suites ran and the timing lanes after them reported, so the slow
            # sample was in play and did not refuse. US0880 replaced the up-front estimate that
            # read it with one elapsed-time report against the 90-second budget.
            self.assertRegex(out, r"this commit took \d+s (of its|against a) 90s budget",
                             f"the timing lanes never ran:\n{out}")
            self.assertFalse((root / TRIPWIRE_LOG).exists(), out)

    def test_the_kept_lint_lanes_still_refuse(self) -> None:
        """AC3. The fixture's style, links and markdown stand-ins are replaced by the REAL
        checkers, so a staged defect of each kind meets the lane that owns it.

        MUTANTS: delete the `style`, `links` or `markdown` lane from the pre-commit hook."""
        linter = _markdownlint()
        cases = [("style", "docs/note.md", "# Note\n\nAn em dash \u2014 here.\n"),
                 ("links", "README.md", "# Notes\n\nSee [the guide](missing-guide.md).\n")]
        if linter:
            cases.append(("markdown", "docs/note.md", "# Note\n\nText.\n- a list with no "
                                                      "blank line above it\n"))
        for lane, rel, body in [("clean", "docs/note.md", "# Note\n\nPlain text.\n")] + cases:
            with self.subTest(lane=lane), tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                _write(root, "tools/lint-style.sh",
                       f'#!/usr/bin/env bash\nexec bash {REPO / "tools" / "lint-style.sh"} "$PWD"\n',
                       mode=0o755)
                _write(root, "tools/check_links.py",
                       "import runpy, sys\n"
                       f"sys.argv[0] = {str(REPO / 'tools' / 'check_links.py')!r}\n"
                       "runpy.run_path(sys.argv[0], run_name='__main__')\n")
                if linter:
                    _write(root, "node_modules/.bin/markdownlint",
                           f'#!/usr/bin/env bash\nexec {linter} "$@"\n', mode=0o755)
                _write(root, "README.md", "# Notes\n")
                _wg._git(root, "add", "-A")
                _wg._git(root, "commit", "-q", "--no-verify", "-m", "real linters")
                rc, out = _commit(root, {rel: body})
                if lane == "clean":
                    self.assertEqual(0, rc, f"the real linters refuse a clean commit:\n{out}")
                    continue
                self.assertNotEqual(0, rc, f"a staged {lane} defect was committed:\n{out}")
                self.assertRegex(out, rf"FAIL\S*\s+\S*{lane}\b",
                                 f"the refusal is not the {lane} lane's:\n{out}")
        if not linter:
            self.skipTest("markdownlint not installed (npm install): the style and links "
                          "cases ran, the markdown case did not")

    def test_there_is_one_window_claim_implementation(self) -> None:
        """AC4. MUTANT: restore the inline window guard in the pre-commit hook.

        Proved by execution in both directions: with the gate stubbed to pass, an open window
        claiming a staged path refuses nothing - no second implementation is left to - and with
        the gate's real `window` lane the same commit is refused by it."""
        claimed = _wg.WindowGuardTests.CLAIMED
        record = {"owner": "reviewer", "opened": "2026-09-24T10:00:00Z", "paths": [claimed]}
        for gate_runs_window in (False, True):
            with self.subTest(gate_window_lane=gate_runs_window), \
                    tempfile.TemporaryDirectory() as d:
                root = _fixture(Path(d))
                if not gate_runs_window:
                    _write(root, ".claude/skills/sdlc-studio/scripts/gate.py", _wg.PASS_PY)
                    _wg._git(root, "add", "-A")
                    _wg._git(root, "commit", "-q", "--no-verify", "-m", "gate passes")
                _write(root, "sdlc-studio/.local/review-window.json", json.dumps(record))
                rc, out = _commit(root, {claimed: "VALUE = 999\n"})
                if gate_runs_window:
                    self.assertNotEqual(0, rc, f"the gate's window lane did not refuse:\n{out}")
                    self.assertIn("[FAIL] window", out)
                    self.assertIn(claimed, out)
                else:
                    self.assertEqual(0, rc, f"a second window check refused the commit:\n{out}")
                    self.assertNotIn("window", out.lower(), out)
        pre_commit = _code("pre-commit")
        for trace in ("window", "fnmatch", "<<'PY'"):
            self.assertNotIn(trace, pre_commit, f"the pre-commit hook still carries `{trace}`")
        self.assertIn('"$skill/gate.py" --root .', pre_commit,
                      "the hook no longer runs the standard gate that carries the window lane")
        self.assertIn("window", _gate_lanes())


if __name__ == "__main__":
    unittest.main()
