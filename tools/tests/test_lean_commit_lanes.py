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

import ast
import json
import os
import re
import shutil
import subprocess
import sys
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

    Allowed: the helper's own body; the one closing `exit 1` under `if [ "$fail" -ne 0 ]`, which
    only reports what the lanes already decided; and the start-up guards that exit when the hook
    is not inside a repository at all (`rev-parse`, `cd`), which judge no commit."""
    found, stack, in_run, heredoc = [], [], False, None
    for raw in text.splitlines():
        line = raw.strip()
        if heredoc:                 # a heredoc body is data (the `--list` awk), not shell
            heredoc = None if line == heredoc else heredoc
            continue
        tag = re.search(r"<<-?\s*'?(\w+)'?\s*$", line)
        if tag:
            heredoc = tag.group(1)
        if in_run:
            in_run = line != "}"
            continue
        if re.match(r"run\(\)\s*\{", line):
            in_run = True
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
            for name, anchor in (("pre-commit", 'run "links" \\\n'),
                                 ("commit-msg", '  run "repo-writes" \\\n')):
                with self.subTest(added_to=name):
                    hook = root / ".githooks" / name
                    text = hook.read_text(encoding="utf-8")
                    self.assertEqual(1, text.count(anchor), f"the anchor moved in {name}")
                    before = _listed_keys(_list(hook, root)[1])
                    # One lane in the usual four-line shape, one written on a single line.
                    hook.write_text(text.replace(anchor, 'run "added-lane" \\\n'
                                                 '  "the rule the added lane enforces" \\\n'
                                                 '  "the fix" \\\n  -- true\n'
                                                 'run "one-line-lane" "the one-line rule" '
                                                 '"its fix" -- true\n' + anchor),
                                    encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
