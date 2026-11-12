"""The commit hooks print one line on success and the whole per-lane list on refusal (US1134).

Agents piped both hooks through `tail` to find the verdict under forty `ok` lines, and a filter
that keeps the tail hides the lane that refused. These tests RUN THE REAL HOOKS in a throwaway
repo whose every lane script is a stub that passes, unless the test arms one to refuse with a
detail it can find again. git is confined to the fixture (`gitutil.git_env`), HOME included.
A pass still prints the two things its author reads nowhere else, above the summary: the
stamps-staged lane's re-read list (BG0779) and the settle step's report (US0899).
"""
# test-census-subject: .githooks/pre-commit
# test-census-subject: .githooks/commit-msg
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = ".claude/skills/sdlc-studio"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hookutil import hook_skill_scripts, hook_tool_scripts  # noqa: E402


def _load_gitutil():
    path = REPO / SKILL / "scripts/tests/gitutil.py"
    spec = importlib.util.spec_from_file_location("_quiet_hooks_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()

#: A stub that passes, or refuses with `detail` when the file `<name>.refuse` exists beside the
#: repo root - so one fixture serves the green, the red and the verbose run.
ARMED_PY = ("import sys\nfrom pathlib import Path\n"
            "flag = Path({flag!r})\n"
            "if flag.exists():\n"
            "    print(flag.read_text(encoding='utf-8'))\n"
            "    sys.exit(1)\n"
            "sys.exit(0)\n")
ARMED_SH = "#!/usr/bin/env bash\n[ -e {flag!r} ] && {{ cat {flag!r}; exit 1; }}\nexit 0\n"
OK_LINE = re.compile(r"^\s*ok\s+\S", re.M)


class QuietHookTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.root = self.tmp / "r"
        self.style_flag = self.tmp / "style.refuse"
        self.floor_flag = self.tmp / "floor.refuse"
        self._build()

    def _env(self, **extra: str) -> dict:
        env = gitutil.git_env(HOME=str(self.home), XDG_DATA_HOME=str(self.home / "xdg"),
                              TMPDIR=str(self.tmp), **extra)
        env.pop("SDLC_GATE_VERBOSE", None)
        env.update(extra)
        return env

    def _git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True,
                       capture_output=True, env=self._env())

    def _build(self) -> None:
        root, skill = self.root, self.root / SKILL / "scripts"
        for sub in (".githooks", "tools", "node_modules/.bin", str(skill.relative_to(root))):
            (root / sub).mkdir(parents=True, exist_ok=True)
        for hook in ("pre-commit", "commit-msg"):
            dst = root / ".githooks" / hook
            dst.write_text((REPO / ".githooks" / hook).read_text(encoding="utf-8"),
                           encoding="utf-8")
            dst.chmod(0o755)
        passing = ARMED_SH.format(flag=str(self.tmp / "never.refuse"))
        for rel in ("tools/check_action_pins.sh", "node_modules/.bin/markdownlint"):
            (root / rel).write_text(passing, encoding="utf-8")
            (root / rel).chmod(0o755)
        style = root / "tools/lint-style.sh"
        style.write_text(ARMED_SH.format(flag=str(self.style_flag)), encoding="utf-8")
        style.chmod(0o755)
        never = ARMED_PY.format(flag=str(self.tmp / "never.refuse"))
        for name in hook_tool_scripts():
            (root / "tools" / name).write_text(never, encoding="utf-8")
        for rel in hook_skill_scripts():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(never, encoding="utf-8")
        self.gate_flag = self.tmp / "gate.refuse"
        (skill / "gate.py").write_text(ARMED_PY.format(flag=str(self.gate_flag)),
                                       encoding="utf-8")
        (skill / "engagement_floor.py").write_text(ARMED_PY.format(flag=str(self.floor_flag)),
                                                   encoding="utf-8")
        (root / "notes.txt").write_text("notes\n", encoding="utf-8")
        self._git("init", "-q")
        self._git("add", "-A")
        self._git("commit", "-q", "--no-verify", "-m", "fixture")
        (root / "notes.txt").write_text("notes, changed\n", encoding="utf-8")
        self._git("add", "notes.txt")
        self.msg = self.tmp / "MSG"
        self.msg.write_text("docs: change the notes\n", encoding="utf-8")

    def _hook(self, name: str, **env: str) -> tuple[int, str]:
        argv = [str(self.root / ".githooks" / name)] + ([str(self.msg)] if name == "commit-msg"
                                                         else [])
        r = subprocess.run(argv, cwd=self.root, capture_output=True, text=True,
                           env=self._env(**env), timeout=120)
        return r.returncode, r.stdout + r.stderr

    def _summary(self, hook: str, out: str) -> str:
        """The quiet pass's last line, asserted to be the hook's summary and the only one."""
        lines = out.strip().splitlines()
        self.assertTrue(lines, f"{hook} printed nothing on a pass")
        last = lines[-1]
        self.assertRegex(last, rf"^{hook}: (gate green|cheap lanes green|message rules green)"
                               r".* - \d+ lane\(s\) passed", out)
        self.assertTrue(last.endswith("(SDLC_GATE_VERBOSE=1 lists them)"), out)
        self.assertEqual(1, sum(1 for line in lines if "lane(s) passed" in line), out)
        return last

    def test_success_is_one_line_and_failure_is_verbose(self) -> None:
        """AC1. MUTANTS: the EXIT trap printing the summary on a refusal too (the summary is
        asserted absent from both red runs); the replay dropped (`cat ... >&3` removed: the
        failing lane's rule, detail and fix vanish); the buffer never set up (`ok` lines on the
        green run); SDLC_GATE_VERBOSE ignored (the verbose run would be one line)."""
        for hook, flag, key in (("pre-commit", self.style_flag, "style"),
                                ("commit-msg", self.floor_flag, "message-refs")):
            with self.subTest(hook=hook, run="green"):
                rc, out = self._hook(hook)
                self.assertEqual(0, rc, out)
                lines = out.strip().splitlines()
                self.assertEqual(1, len(lines), f"{hook} printed more than one line:\n{out}")
                self._summary(hook, out)
                self.assertIsNone(OK_LINE.search(out), out)
            with self.subTest(hook=hook, run="verbose"):
                rc, out = self._hook(hook, SDLC_GATE_VERBOSE="1")
                self.assertEqual(0, rc, out)
                self.assertRegex(out, rf"(?m)^\s*ok\s+{re.escape(key)}$")
                self.assertNotIn("lane(s) passed", out)
            with self.subTest(hook=hook, run="red"):
                detail = f"DETAIL-{hook}-the-staged-line-breaks-the-rule"
                flag.write_text(detail, encoding="utf-8")
                self.addCleanup(flag.unlink, missing_ok=True)
                rc, out = self._hook(hook)
                flag.unlink()
                self.assertEqual(1, rc, out)
                self.assertRegex(out, rf"(?m)^\s*FAIL\s+{re.escape(key)}$")
                self.assertIn("enforces:", out)
                self.assertIn(detail, out)
                self.assertIn("fix:", out)
                self.assertIn("Genuine emergency only", out)
                self.assertNotIn(f"{hook}: gate green", out)
                self.assertNotIn("lane(s) passed", out)
                if hook == "pre-commit":
                    # the per-lane list, not the failing lane alone: the passing lanes are named
                    self.assertIsNotNone(OK_LINE.search(out), out)
        with self.subTest(hook="commit-msg", run="red after a passing lane"):
            # A suite lane refusing AFTER the message lane passed: the summary must still not be
            # printed, and the list names the lane that passed beside the one that refused.
            handover = self.root / ".git" / "sdlc-gate-suites"
            handover.write_text("precommit_seconds=1\nsuite-selector=tools/tests/test_x.py\n",
                                encoding="utf-8")
            self.gate_flag.write_text("DETAIL-unit-tests-a-selected-test-failed",
                                      encoding="utf-8")
            self.addCleanup(self.gate_flag.unlink, missing_ok=True)
            rc, out = self._hook("commit-msg")
            self.assertEqual(1, rc, out)
            self.assertRegex(out, r"(?m)^\s*ok\s+message-refs$")
            self.assertRegex(out, r"(?m)^\s*FAIL\s+unit-tests$")
            self.assertIn("DETAIL-unit-tests-a-selected-test-failed", out)
            self.assertNotIn("lane(s) passed", out)

    def test_a_pass_still_shows_the_re_read_list_and_the_settle_report(self) -> None:
        """AC1, run quiet as an author commits. MUTANTS: `verdict()` writing no `keep` file (the
        re-read list is gone from the pass); the settle report not copied to `keep` (its
        restage note is gone); `keep` printed after the summary (the summary is no longer the
        last line); a pass printing the held per-lane list (`ok` lines appear)."""
        skill = self.root / SKILL / "scripts"
        (skill / "verify_ac.py").write_text(
            "import sys\nif 'stamps' in sys.argv and '--staged' in sys.argv:\n"
            "    print('verify-stamps: staged: re-read - the criteria whose stamped test this "
            "commit changes:')\n"
            "    print('  US0001 AC1: RE-READ-THIS-CRITERION')\n"
            "sys.exit(0)\n", encoding="utf-8")
        (skill / "reconcile.py").write_text(
            "print('restaged sdlc-studio/stories/_index.md (SETTLE-RESTAGED)')\n"
            "print('left unstaged sdlc-studio/epics/_index.md (SETTLE-LEFT-UNSTAGED)')\n",
            encoding="utf-8")
        story = self.root / "sdlc-studio" / "stories" / "US0001-probe.md"
        story.parent.mkdir(parents=True, exist_ok=True)
        story.write_text("# US0001: probe\n", encoding="utf-8")
        self._git("add", "-A")
        rc, out = self._hook("pre-commit")
        self.assertEqual(0, rc, out)
        self._summary("pre-commit", out)
        above = out.strip().splitlines()[:-1]
        for said in ("verify-stamps: staged: re-read - ", "US0001 AC1: RE-READ-THIS-CRITERION",
                     "SETTLE-RESTAGED", "SETTLE-LEFT-UNSTAGED"):
            self.assertTrue(any(said in line for line in above),
                            f"a quiet pass hid {said!r}, which prints above the summary:\n{out}")
        self.assertEqual(4, len(above),
                         f"a quiet pass printed more than the re-read list and the settle "
                         f"report above its summary:\n{out}")
        self.assertIsNone(OK_LINE.search(out), out)
        with self.subTest(run="verbose"):
            rc, out = self._hook("pre-commit", SDLC_GATE_VERBOSE="1")
            self.assertEqual(0, rc, out)
            self.assertRegex(out, r"(?m)^\s*ok\s+stamps-staged$")
            self.assertIn("RE-READ-THIS-CRITERION", out)
            self.assertIn("SETTLE-RESTAGED", out)
            self.assertNotIn("lane(s) passed", out)


if __name__ == "__main__":
    unittest.main()
