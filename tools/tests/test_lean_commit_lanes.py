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

US0905 caps the lanes a commit runs (`COMMIT_LANE_CAP`), so a new lane has to displace one. The
cap is the suite's one lane pin: it replaced the exact lane sets every lane change had to edit,
and `LaneCapTests` refuses one coming back under any name.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

# Imported as a MODULE so unittest does not collect and re-run its cases here.
import test_precommit_window_guard as _wg

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / ".githooks"

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

#: The hooks that answer `--list` (US0901).
LISTING_HOOKS = ("pre-commit", "commit-msg")

#: One `--list` line: the lane key, a tab, the rule it enforces.
LIST_LINE = re.compile(r"([a-z][a-z0-9-]*)\t(\S.*)")

#: Where the `--list` fixture's tripwires log that something ran.
LIST_TRIPWIRE_LOG = "list-tripwire.log"

#: TOMBSTONES, not ratchets. The three lists below are closed records of what US0901 itself
#: deleted and retired: they name no live lane, never grow when a lane is added, and are what
#: its AC2 and AC3 name. Kept because the sweep in the AC2 test cannot see two of these pins (no
#: backticked key in them), and the corpus scan in the AC3 test found three `-k` stamps the
#: first pass missed. They can go with this test once US0901's criteria are retired in turn.
#:
#: The prose pins US0901 deletes, by module: the classes and test functions that read AGENTS.md
#: to hold a lane or boundary name there.
DELETED_PINS = {
    "tools/tests/test_check_spec_claims.py": {"GateLaneTests", "StampsStagedRosterTests"},
    "tools/tests/test_precommit_lane_order.py": {"test_the_agents_roster_names_the_lane"},
    "tools/tests/test_repo_writes.py": {"RosterTests"},
}

#: The stamped criteria whose selectors named a deleted pin, retired in the D0259 pattern.
RETIRED_BY_US0901 = {
    "BG0641": ("AC6", "AC7"),
    "BG0649": ("AC3",),
    "BG0651": ("AC3",),
    "BG0653": ("AC4",),
    "BG0662": ("AC5",),
    "BG0569": ("AC5",),
    "US0666": ("AC3",),
    "US0674": ("AC4",),
}

#: The selectors those criteria named, in node and `-k` form, none of which may be stamped
#: anywhere any more.
DELETED_SELECTORS = ("tools/tests/test_boundary_roster.py",
                     "test_check_spec_claims.py::GateLaneTests",
                     "test_check_spec_claims.py::StampsStagedRosterTests",
                     "ChangelogShapeLaneTests::test_the_agents_roster_names_the_lane",
                     "test_repo_writes.py::RosterTests",
                     "test_check_spec_claims.py -k the_lane_roster_names",
                     "test_check_spec_claims.py -k revert_check",
                     "test_repo_writes.py -k the_roster_names_this_lane")

SKILL_SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

#: US0905: the most lanes a commit may run - both hooks' `--list` lines plus the lanes the
#: pre-commit hook's plain `gate.py` run carries. ONE INTEGER, and the suite's one lane pin: a
#: change that adds a lane deletes one in the same change. Deleting a lane needs no edit here.
COMMIT_LANE_CAP = 31


def _code(hook: str) -> str:
    """The hook's executable lines: comments say what a lane USED to do, and may."""
    text = (HOOKS / hook).read_text(encoding="utf-8")
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _run_keys(hook: str) -> set:
    return set(re.findall(r'^\s*run\s+"([^"]+)"', _code(hook), re.M))


def _gate_lanes(root: Path = REPO) -> list[str]:
    """The lanes a plain `gate.py --root .` runs, which is what the pre-commit `gate` lane
    invokes. Read from the gate's own tables the way its plain run reads them: the standard
    lanes, plus any on-demand lane the project set to block. The close-only advisory lanes
    (`CLOSE_ADVISORY_CHECKS`) never run on a commit."""
    sys.path.insert(0, str(SKILL_SCRIPTS))
    try:
        import gate
        enforced = gate._enforced_lanes(str(root))
    finally:
        sys.path.remove(str(SKILL_SCRIPTS))
    return sorted(set(gate.DEFAULT_CHECKS) | (set(gate.ON_DEMAND_CHECKS) & enforced))


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
        line, the claim-drift or lane-check block, the suite-claim check. The roster half of
        this criterion is superseded by US0901: AGENTS.md no longer lists lanes, the hooks do."""
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


def _list(hook: Path, cwd: Path, env: dict | None = None) -> tuple[int, str, str]:
    """`<hook> --list`, executed as the criterion names it."""
    r = subprocess.run([str(hook), "--list"], cwd=cwd, capture_output=True, text=True,
                       env=env if env is not None else _wg._clean_env(), timeout=60)
    return r.returncode, r.stdout, r.stderr


#: A construct that refuses a commit: a write to `fail` other than its `fail=0` start, a FAIL
#: verdict printed, or a non-zero exit.
_FAIL_WRITE = re.compile(r"(?<![\w])fail\+?=(?!0\b)|\(\(\s*fail\b")
_FAIL_PRINT = re.compile(r"\b(printf|echo)\b[^|]*\bFAIL\b")     # printed, not grepped for
_EXIT = re.compile(r"\bexit\s+[1-9]")


def _inline_refusals(text: str) -> list[str]:
    """Every refusal a hook makes OUTSIDE its `run` helper, which `--list` therefore cannot see.

    Allowed: the helper's own body - `run`, or in pre-commit the `lane-helpers` block `run`
    starts its lanes through and `collect` reads their verdicts in; the one closing `exit 1`
    under `if [ "$fail" -ne 0 ]`, which only reports what the lanes already decided; and the
    start-up guards that exit when the hook is not inside a repository at all (`rev-parse`,
    `cd`), which judge no commit."""
    found, stack, helper_end, heredoc = [], [], None, None
    for raw in text.splitlines():
        line = raw.strip()
        if heredoc:                 # a heredoc body is data (the `--list` awk), not shell
            heredoc = None if line == heredoc else heredoc
            continue
        tag = re.search(r"<<-?\s*'?(\w+)'?\s*$", line)
        if tag:
            heredoc = tag.group(1)
        if helper_end:
            helper_end = None if line == helper_end else helper_end
            continue
        if re.match(r"run\(\)\s*\{", line):
            helper_end = "}"
            continue
        if line.startswith("# >>> lane-helpers"):
            helper_end = "# <<< lane-helpers"
            continue
        if not line or line.startswith("#"):
            continue
        body = re.sub(r"^[\w-]+\(\)\s*\{\s*", "", line)
        if re.match(r"if\b", body):
            stack.append(body)
        elif re.match(r"elif\b", body) and stack:
            stack[-1] = body
        elif re.match(r"else\b", body) and stack:
            stack[-1] = "else"
        if _FAIL_WRITE.search(line) or _FAIL_PRINT.search(line):
            found.append(raw)
        elif _EXIT.search(line):
            closing = bool(stack) and '"$fail" -ne 0' in stack[-1]
            startup = "rev-parse" in line or line.startswith("cd ")
            if not (closing or startup):
                found.append(raw)
        if re.search(r"(^|;\s*)fi\b", body) and stack:
            stack.pop()
    return found


def _listed_keys(stdout: str) -> list[str]:
    return [m.group(1) for m in map(LIST_LINE.fullmatch, stdout.splitlines()) if m]


def _tripwire_env(root: Path) -> dict:
    """PATH shims that log and fail for `python3` and `git`, with every fixture script and the
    markdownlint stand-in replaced the same way: whatever a lane runs leaves a line in the log."""
    log = root / LIST_TRIPWIRE_LOG
    trip = f'#!/bin/sh\necho "$0 $*" >> {log}\nexit 1\n'
    for name in ("python3", "git"):
        _write(root, f"shims/{name}", trip, mode=0o755)
    for path in [*root.glob("tools/*.sh"), *root.glob("tools/*.py"),
                 root / "node_modules" / ".bin" / "markdownlint"]:
        _write(root, str(path.relative_to(root)), trip, mode=0o755)
    env = _wg._clean_env()
    env["PATH"] = f"{root / 'shims'}:{env.get('PATH', '')}"
    return env


class LaneListTests(unittest.TestCase):
    """US0901: each hook lists its own lanes, so AGENTS.md does not have to."""

    def test_each_hook_lists_its_lanes_without_running_them(self) -> None:
        """AC1. MUTANTS: `--list` falls through into the hook (the tripwires fire); it prints
        a hand-kept list (the added lane is missing); the gate block stays outside `run` (no
        `gate` line); a line loses its rule."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            env = _tripwire_env(root)
            log = root / LIST_TRIPWIRE_LOG
            listed = {}
            for name in LISTING_HOOKS:
                with self.subTest(hook=name):
                    rc, out, err = _list(root / ".githooks" / name, root, env)
                    fired = log.read_text(encoding="utf-8") if log.exists() else ""
                    self.assertEqual("", fired, f"--list ran something:\n{fired}{out}{err}")
                    self.assertEqual(0, rc, out + err)
                    self.assertTrue(out.strip(), f"{name} --list printed nothing")
                    for line in out.splitlines():
                        self.assertRegex(line, LIST_LINE, f"not `<key><TAB><rule>`: {line!r}")
                    keys = _listed_keys(out)
                    self.assertEqual(len(keys), len(set(keys)), f"a lane is listed twice: {keys}")
                    self.assertEqual(_run_keys(name), set(keys),
                                     f"{name} --list is not the lanes the hook runs")
                    # ...and nothing refuses outside `run`, where the list cannot see it.
                    self.assertEqual([], _inline_refusals(
                        (root / ".githooks" / name).read_text(encoding="utf-8")),
                        f"{name} refuses outside a `run` lane, so --list omits it")
                    listed[name] = set(keys)
            # The scan's positive control: an inline refusal of each shape is found.
            for shape in ('  printf "FAIL x\\n"', "  fail=1", "  exit 1"):
                self.assertEqual(1, len(_inline_refusals(
                    f'if [ -n "$x" ]; then\n{shape}\nfi\n')), shape)
            # The gate used to be an inline block outside `run`, so it would go unlisted.
            # The refusals that used to sit outside `run` (US0901 review round 1).
            self.assertLessEqual({"gate", "suite-handover"}, listed["pre-commit"])
            self.assertLessEqual({"message-refs", "unit-tests", "repo-writes", "suite-collapse"},
                                 listed["commit-msg"])
            # The positive control: the same tripwires fire when the hooks DO run.
            for name in LISTING_HOOKS:
                subprocess.run([str(root / ".githooks" / name)], cwd=root, env=env,
                               capture_output=True, text=True, timeout=60)
            self.assertTrue(log.exists() and log.read_text(encoding="utf-8").strip(),
                            "the tripwires never fire, so their silence above proves nothing")
        # A lane added to a hook is listed with no other file edited.
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            for name in LISTING_HOOKS:
                with self.subTest(added_to=name):
                    hook = root / ".githooks" / name
                    before = _listed_keys(_list(hook, root)[1])
                    # Above the first lane the hook lists, so the anchor names no lane (BG0760).
                    lines = hook.read_text(encoding="utf-8").splitlines(keepends=True)
                    at = _run_start(lines, before[0])
                    # One lane in the usual four-line shape, one written on a single line.
                    hook.write_text("".join(lines[:at] + [
                        'run "added-lane" \\\n  "the rule the added lane enforces" \\\n'
                        '  "the fix" \\\n  -- true\n',
                        'run "one-line-lane" "the one-line rule" "its fix" -- true\n',
                        *lines[at:]]), encoding="utf-8")
                    rc, out, err = _list(hook, root)
                    self.assertEqual(0, rc, out + err)
                    self.assertIn("added-lane\tthe rule the added lane enforces",
                                  out.splitlines())
                    self.assertIn("one-line-lane\tthe one-line rule", out.splitlines())
                    self.assertEqual(sorted(before + ["added-lane", "one-line-lane"]),
                                     sorted(_listed_keys(out)))

    def test_agents_md_points_at_the_lists_and_no_test_pins_its_prose(self) -> None:
        """AC2. MUTANTS: put a lane roster back into AGENTS.md (a backticked lane key); drop
        either `--list` pointer; restore a deleted pin or `tools/boundary_roster.py`; add a test
        that reads AGENTS.md for `run "<key>"`, a backticked key or `--boundary`."""
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        keys: set = set()
        for name in LISTING_HOOKS:
            self.assertIn(f"`.githooks/{name} --list`", agents,
                          f"AGENTS.md does not point at `{name} --list`")
            rc, out, err = _list(HOOKS / name, REPO)
            self.assertEqual(0, rc, out + err)
            keys |= set(_listed_keys(out))
        self.assertTrue(keys, "the hooks listed no lanes, so the check below reads nothing")
        ticked = set(re.findall(r"`([^`\n]+)`", agents))
        self.assertEqual(set(), keys & ticked, "AGENTS.md still carries a lane roster")
        for rel in ("tools/boundary_roster.py", "tools/tests/test_boundary_roster.py"):
            self.assertFalse((REPO / rel).exists(), f"{rel} is not deleted")
        for rel, names in DELETED_PINS.items():
            tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
            defined = {n.name for n in ast.walk(tree)
                       if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
            self.assertEqual(set(), defined & names, f"{rel} keeps a prose pin")
        # The sweep: no test anywhere reads AGENTS.md and holds a lane or boundary name there.
        pin = re.compile("|".join(["--boundary"] + [rf'`{re.escape(k)}`|run "{re.escape(k)}"'
                                                    for k in sorted(keys)]))
        this = Path(__file__).resolve()
        for path in sorted([*(REPO / "tools" / "tests").glob("test_*.py"),
                            *(SKILL_SCRIPTS / "tests").glob("test_*.py")]):
            if path.resolve() == this:      # it asserts the roster's ABSENCE, above
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            aliases = {t.id for n in tree.body if isinstance(n, ast.Assign)
                       and "AGENTS.md" in ast.dump(n.value)
                       for t in n.targets if isinstance(t, ast.Name)}
            for fn in ast.walk(tree):
                if not (isinstance(fn, ast.FunctionDef) and fn.name.startswith("test")):
                    continue
                consts = [c.value for c in ast.walk(fn)
                          if isinstance(c, ast.Constant) and isinstance(c.value, str)]
                names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
                if not (any("AGENTS.md" in c for c in consts) or names & aliases):
                    continue
                hits = sorted({m.group(0) for c in consts for m in pin.finditer(c)})
                self.assertEqual([], hits, f"{path.name}::{fn.name} pins AGENTS.md prose")

    def test_the_roster_criteria_are_retired(self) -> None:
        """AC3. MUTANTS: leave any one retired criterion's Verify line naming its deleted
        selector; retire it without naming US0901 or the reason; leave its Verified line at
        `yes`; drop the supersession row from US0879's revision history."""
        sys.path.insert(0, str(SKILL_SCRIPTS))
        try:
            import verify_ac
        finally:
            sys.path.remove(str(SKILL_SCRIPTS))
        artefacts = REPO / "sdlc-studio"
        for unit, acs in RETIRED_BY_US0901.items():
            folder = "bugs" if unit.startswith("BG") else "stories"
            found = sorted((artefacts / folder).glob(f"{unit}-*.md"))
            self.assertEqual(1, len(found), f"{unit}: {found}")
            blocks = {b.ac_id: b for b in
                      verify_ac.criteria_blocks(found[0].read_text(encoding="utf-8"))}
            for ac in acs:
                block, where = blocks[ac], f"{unit} {ac}"
                self.assertRegex(block.verifier or "", r"^manual - retired by US0901: \S",
                                 f"{where}: Verify is not retired: {block.verifier}")
                self.assertEqual("manual", (block.verified_state or "").lower(), where)
                self.assertIn("retired, superseded by US0901", block.verified_reason, where)
            # The shipped entry point the stamps-staged lane runs, over the retired artefact.
            r = subprocess.run([sys.executable, str(SKILL_SCRIPTS / "verify_ac.py"), "stamps",
                                "--story", str(found[0])], cwd=REPO, capture_output=True,
                               text=True, timeout=120)
            self.assertEqual(0, r.returncode, f"{unit}:\n{r.stdout}{r.stderr}")
        us0879 = next((artefacts / "stories").glob("US0879-*.md")).read_text(encoding="utf-8")
        history = us0879.split("## Revision History", 1)[1]
        self.assertRegex(history, r"\|[^\n]*AC1[^\n]*roster[^\n]*superseded by US0901",
                         "US0879's revision history does not record the supersession")
        for path in sorted([*artefacts.glob("stories/*.md"), *artefacts.glob("bugs/*.md")]):
            for line in path.read_text(encoding="utf-8").splitlines():
                if "**Verify:**" in line:
                    for selector in DELETED_SELECTORS:
                        self.assertNotIn(selector, line, f"{path.name} still stamps it")


def _hook_keys(hook: Path) -> list[str]:
    """The lane keys `<hook> --list` prints, in declared order."""
    rc, out, err = _list(hook, hook.parent.parent)
    if rc != 0:
        raise AssertionError(f"{hook.name} --list exited {rc}:\n{out}{err}")
    return _listed_keys(out)


def _commit_lanes(hooks: Path) -> dict[str, list[str]]:
    """Every lane a commit runs, by where it runs: each hook's `--list` keys, then the gate's."""
    lanes = {name: _hook_keys(hooks / name) for name in LISTING_HOOKS}
    lanes["gate.py"] = _gate_lanes()
    return lanes


def _cap_breach(lanes: dict[str, list[str]], cap: int = COMMIT_LANE_CAP) -> str | None:
    """None at or under the cap; over it, the refusal naming every lane and the trade."""
    count = sum(map(len, lanes.values()))
    if count <= cap:
        return None
    listing = "\n".join(f"  {where} ({len(keys)}): {', '.join(keys)}"
                        for where, keys in lanes.items())
    return (f"a commit runs {count} lanes, over the cap of {cap} (COMMIT_LANE_CAP in "
            f"tools/tests/test_lean_commit_lanes.py): one must go for one to come in - delete "
            f"a lane in the change that adds one. The lanes:\n{listing}")


def _copy_hooks(src: Path, root: Path) -> Path:
    """Both listing hooks copied from `src` into `root/.githooks`, which is returned."""
    hooks = root / ".githooks"
    hooks.mkdir()
    for name in LISTING_HOOKS:
        shutil.copy2(src / name, hooks / name)
    return hooks


def _run_start(lines: list[str], key: str) -> int:
    """The index of the one line that starts the `run "<key>"` lane."""
    start = [i for i, ln in enumerate(lines) if re.match(rf'\s*run "{re.escape(key)}"', ln)]
    assert len(start) == 1, f"{key}: {start}"
    return start[0]


def _add_lanes(hook: Path, keys: list[str]) -> None:
    """One-line `run` lanes inserted above the first lane the hook's `--list` prints, so the
    anchor names no lane and survives any one being deleted."""
    lines = hook.read_text(encoding="utf-8").splitlines(keepends=True)
    at = _run_start(lines, _hook_keys(hook)[0])
    added = [f'run "{k}" "the rule {k} enforces" "its fix" -- true\n' for k in keys]
    hook.write_text("".join(lines[:at] + added + lines[at:]), encoding="utf-8")


def _drop_lane(hook: Path, key: str) -> None:
    """Replace the `run "<key>"` block, from its first line through its `--` command line, with
    `:`, so a lane that was alone in a branch leaves the hook valid bash."""
    lines = hook.read_text(encoding="utf-8").splitlines(keepends=True)
    start = _run_start(lines, key)
    end = next(i for i in range(start, len(lines)) if re.search(r"(^|\s)-- ", lines[i]))
    indent = re.match(r"\s*", lines[start]).group(0)
    hook.write_text("".join(lines[:start] + [f"{indent}:\n"] + lines[end + 1:]),
                    encoding="utf-8")


#: A module- or class-level name holding this many of today's hook lane keys is an exact lane
#: set, whatever it is called: the three US0905 deleted held 15, 6 and 20, and the cheap-first
#: set that stays holds 3.
LANE_PIN_KEYS = 5


def _lane_pins(source: str, keys: set) -> dict[str, list[str]]:
    """Every module- or class-level name in `source` whose assigned value holds at least
    LANE_PIN_KEYS of `keys`, counting what a name it references holds (`A | {...}`)."""
    tree = ast.parse(source)
    held: dict[str, set] = {}
    pins = {}
    for body in [tree.body, *(n.body for n in ast.walk(tree) if isinstance(n, ast.ClassDef))]:
        for node in body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                continue
            found = set()
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Constant) and sub.value in keys:
                    found.add(sub.value)
                elif isinstance(sub, ast.Name):
                    found |= held.get(sub.id, set())
            for target in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                if isinstance(target, ast.Name):
                    held[target.id] = found
                    if len(found) >= LANE_PIN_KEYS:
                        pins[target.id] = sorted(found)
    return pins


def _tree_pins(keys: set) -> dict[str, list[str]]:
    """Every exact lane set of `keys` held by a module in either test tree, by `path::name`."""
    trees = (REPO / "tools" / "tests", SKILL_SCRIPTS / "tests")
    return {f"{p.relative_to(REPO)}::{name}": held
            for tree in trees for p in sorted(tree.glob("*.py"))
            for name, held in _lane_pins(p.read_text(encoding="utf-8"), keys).items()}


def _assert_the_cap_trades(tc: unittest.TestCase, src: Path) -> None:
    """The cap's fixture over a copy of the hooks in `src`: lanes added to reach the cap and one
    past it, then one lane traded out. How many fillers reach the cap is derived from the
    copy's own count: none while the cap is the count at landing, one per lane deleted since."""
    with tempfile.TemporaryDirectory() as d:
        hooks = _copy_hooks(src, Path(d))
        pre = hooks / "pre-commit"
        base = _commit_lanes(hooks)
        spare = COMMIT_LANE_CAP - sum(map(len, base.values()))
        _add_lanes(pre, [f"filler-lane-{i}" for i in range(spare)])
        tc.assertIsNone(_cap_breach(_commit_lanes(hooks)), "at the cap is refused")

        _add_lanes(pre, ["added-lane"])
        breach = _cap_breach(_commit_lanes(hooks))
        tc.assertIsNotNone(breach, "a lane over the cap passed")
        tc.assertIn("one must go for one to come in", breach)
        tc.assertIn(f"{COMMIT_LANE_CAP + 1} lanes, over the cap of {COMMIT_LANE_CAP}", breach)
        # Every lane named, each read independently of the count: the hooks' own lists and the
        # gate's tables.
        gate = _gate_lanes()
        tc.assertTrue(gate, "the gate's tables gave no lanes")
        named = [*_hook_keys(pre), *_hook_keys(hooks / "commit-msg"), *gate]
        tc.assertIn("added-lane", named)
        tc.assertEqual(COMMIT_LANE_CAP + 1, len(named), named)
        listing = breach.split("The lanes:", 1)[1]
        for key in named:
            tc.assertRegex(listing, rf"(?<![\w.-]){re.escape(key)}(?![\w.-])",
                           f"the refusal does not name `{key}`")

        # The trade: one existing lane deleted beside the added one, and it passes again. The
        # lane is whichever the copy listed first before anything was added, never a name.
        _drop_lane(pre, base["pre-commit"][0])
        traded = _commit_lanes(hooks)
        tc.assertNotIn(base["pre-commit"][0], traded["pre-commit"], "the trade did not apply")
        tc.assertIsNone(_cap_breach(traded), "one lane out for one in is still refused")


def _assert_the_pin_scan_discriminates(tc: unittest.TestCase, keys: set) -> None:
    """The scan's controls: it flags an exact lane set by any name, reached through a name it
    references or held on a class, and passes one key short of the threshold. The sets are
    drawn from `keys`, what the hooks list, so the controls name no lane themselves."""
    k = sorted(keys)
    n = LANE_PIN_KEYS
    tc.assertGreaterEqual(len(k), n, f"too few listed lanes to build a pin: {k}")
    tc.assertEqual(["RENAMED"], list(_lane_pins(f"RENAMED = {tuple(k[:n])!r}\n", keys)))
    tc.assertEqual(["MSG"], list(_lane_pins(
        f"E = {set(k[:n - 2])!r}\nMSG = E | {set(k[n - 2:n])!r}\n", keys)))
    tc.assertEqual(["X"], list(_lane_pins(
        f"class C:\n    X = frozenset({list(k[:n])!r})\n", keys)))
    tc.assertEqual({}, _lane_pins(f"UNDER = {set(k[:n - 1])!r}\n", keys))


def _assert_retired_by_us0905(tc: unittest.TestCase, unit: str, ac: str) -> None:
    """`unit`'s `ac` is retired in the D0259 pattern: a manual Verify line naming US0905, a
    Verified line saying so, and `verify_ac.py stamps` clean over the artefact."""
    sys.path.insert(0, str(SKILL_SCRIPTS))
    try:
        import verify_ac
    finally:
        sys.path.remove(str(SKILL_SCRIPTS))
    story = next((REPO / "sdlc-studio").glob(f"*/{unit}-*.md"))
    block = {b.ac_id: b for b in
             verify_ac.criteria_blocks(story.read_text(encoding="utf-8"))}[ac]
    tc.assertRegex(block.verifier or "", r"^manual - retired by US0905: \S",
                   f"{unit} {ac} is not retired: {block.verifier}")
    tc.assertEqual("manual", (block.verified_state or "").lower())
    tc.assertIn("retired, superseded by US0905", block.verified_reason or "")
    r = subprocess.run([sys.executable, str(SKILL_SCRIPTS / "verify_ac.py"), "stamps",
                        "--story", str(story)], cwd=REPO, capture_output=True, text=True,
                       timeout=120)
    tc.assertEqual(0, r.returncode, r.stdout + r.stderr)


class LaneCapTests(unittest.TestCase):
    """US0905: a commit runs at most COMMIT_LANE_CAP lanes, so one must go for one to come in."""

    def test_a_lane_over_the_cap_fails_naming_the_trade(self) -> None:
        """AC1. MUTANTS: compare with `<` (the at-cap fixture then fails); leave either hook or
        the gate out of the count; name only the count, or only the added lane; drop the
        trade from the refusal."""
        # This repository first: the guard itself.
        breach = _cap_breach(_commit_lanes(HOOKS))
        if breach:
            self.fail(breach)
        _assert_the_cap_trades(self, HOOKS)

    def test_the_cap_retires_the_exact_lane_pins(self) -> None:
        """AC2. MUTANTS: restore `EXPECTED_LANES`, `MSG_HOOK_LANES` or the no-lane-lost test;
        restore `test_message_first_gate.py`'s hand-kept `EXPECTED_LANES` tuple, or any exact
        lane set under another name in either test tree; leave US0268 AC4's Verify line naming
        the deleted test, or its Verified at `yes`."""
        # No test module holds an exact lane set, by any name: the cap is the one lane pin.
        keys = {k for name in LISTING_HOOKS for k in _hook_keys(HOOKS / name)}
        self.assertEqual({}, _tree_pins(keys), "an exact lane set is back beside the cap")
        _assert_the_pin_scan_discriminates(self, keys)

        order = ast.parse((REPO / "tools" / "tests" / "test_precommit_lane_order.py")
                          .read_text(encoding="utf-8"))
        assigned = {t.id for n in order.body if isinstance(n, (ast.Assign, ast.AnnAssign))
                    for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                    if isinstance(t, ast.Name)}
        defined = {n.name for n in ast.walk(order) if isinstance(n, ast.FunctionDef)}
        self.assertEqual(set(), assigned & {"EXPECTED_LANES", "MSG_HOOK_LANES"},
                         "an exact lane set is back beside the cap")
        self.assertNotIn("test_no_lane_is_lost_in_the_reorder", defined)
        # The control: the parse reads the module's names, so their absence above is real.
        self.assertIn("EXPENSIVE_LANES", assigned)
        self.assertIn("test_every_lane_key_is_unique", defined)
        self.assertIsInstance(COMMIT_LANE_CAP, int)
        _assert_retired_by_us0905(self, "US0268", "AC4")

    def test_dropping_any_one_listed_lane_leaves_the_cap_tests_green(self) -> None:
        """BG0760 AC1: the cap count is the only lane pin. Every lane either hook's `--list`
        prints is deleted in turn from a copy of the hooks, and every other test in this class
        runs whole with the module's HOOKS pointed at that copy, so a lane named anywhere in a
        cap test - a helper, a control or the test body - fails here. MUTANTS: a control, a
        fixture anchor or a test-body tuple that names a lane (`budgets`, `versions`,
        `run "links"`); a drop that never applied."""
        me = self._testMethodName
        names = [n for n in unittest.TestLoader().getTestCaseNames(type(self)) if n != me]
        self.assertIn("test_a_lane_over_the_cap_fails_naming_the_trade", names)
        self.assertIn("test_the_cap_retires_the_exact_lane_pins", names)
        lanes = [(name, key) for name in LISTING_HOOKS for key in _hook_keys(HOOKS / name)]
        total = sum(map(len, _commit_lanes(HOOKS).values()))
        self.assertGreater(len(lanes), LANE_PIN_KEYS, "the hooks' --list names too few lanes")
        for name, key in lanes:
            with self.subTest(lane=key), tempfile.TemporaryDirectory() as d:
                hooks = _copy_hooks(HOOKS, Path(d))
                _drop_lane(hooks / name, key)
                left = _commit_lanes(hooks)
                self.assertNotIn(key, left[name], "the drop did not apply")
                self.assertEqual(total - 1, sum(map(len, left.values())))
                with mock.patch.object(sys.modules[__name__], "HOOKS", hooks):
                    for test in names:
                        getattr(type(self)(test), test)()

    def test_us0372_ac2_is_retired_rather_than_green_over_a_deleted_lane(self) -> None:
        """BG0760 AC2: US0372 AC2 ("every lane that ran before the move still runs") is
        retired, since its test now reads the lanes from `--list` and passes with one deleted.
        MUTANT: leave it stamped against that test, or its Verified at `yes`."""
        _assert_retired_by_us0905(self, "US0372", "AC2")


if __name__ == "__main__":
    unittest.main()
