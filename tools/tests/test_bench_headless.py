"""US1128: tools/bench/runner.py prepares a fixture against a pinned skill commit for one
harness, runs it headless in that harness's CLI and records the usage the CLI printed.

Every CLI here is a fake on PATH that prints a trimmed copy of a real 2026-11-06 capture; no
test calls a real harness. The skill-directory map is the real `install.sh --list-targets`.
"""
# test-census-subject: tools/bench/runner.py
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "bench" / "runner.py"


def _load():
    spec = importlib.util.spec_from_file_location("bench_runner_headless", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bench_runner_headless"] = mod
    spec.loader.exec_module(mod)
    return mod


runner = _load()

# Claude Code `-p --output-format json`, trimmed from the 2026-11-06 capture.
_HAIKU = {"inputTokens": 2, "outputTokens": 35, "cacheReadInputTokens": 11382,
          "cacheCreationInputTokens": 17126, "thinkingTokens": 31,
          "cacheCreationEphemeral5mInputTokens": 0,
          "cacheCreationEphemeral1hInputTokens": 17126, "costUSD": 0.00355672}
CLAUDE_OUT = json.dumps({
    "type": "result", "session_id": "s-claude", "total_cost_usd": 0.00355672,
    "usage": {"input_tokens": 2, "cache_creation_input_tokens": 17126,
              "cache_read_input_tokens": 11382, "output_tokens": 35},
    "modelUsage": {"claude-haiku-5-5": _HAIKU}})
# The same session with a second model beside it, as a session that delegates shows.
CLAUDE_MIXED_OUT = json.dumps({
    "type": "result", "session_id": "s-mixed", "total_cost_usd": 0.00755672,
    "modelUsage": {"claude-haiku-5-5": _HAIKU,
                   "claude-sonnet-5-5": {"inputTokens": 1000, "outputTokens": 200,
                                         "cacheReadInputTokens": 0,
                                         "cacheCreationInputTokens": 0}}})
# Codex CLI `exec --json`: its input_tokens holds the cached tokens.
CODEX_OUT = "\n".join(json.dumps(e) for e in (
    {"type": "thread.started", "thread_id": "t-codex"},
    {"type": "turn.started"},
    {"type": "turn.completed", "usage": {"input_tokens": 14524, "cached_input_tokens": 12288,
                                          "cache_write_input_tokens": 0, "output_tokens": 5,
                                          "reasoning_output_tokens": 0}}))
NO_USAGE_OUT = json.dumps({"type": "result", "result": "OK", "session_id": "s-none"})

# The variables each CLI authenticates from instead of its login file (BG1248), written out
# here rather than read from the runner's table, so a dropped name fails a test.
EXPORTS = {"claude": ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY"),
           "codex": ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN")}

# The brownfield-pagination fix the held-back suite accepts.
FIX = ("def paginate(items, page, page_size):\n"
       "    start = (page - 1) * page_size\n"
       "    return items[start:start + page_size]\n")

# Copilot CLI `-p --output-format json` and OpenCode `run --format json`, one model, one step.
COPILOT_OUT = json.dumps({"type": "session.shutdown", "data": {"accountingSnapshot": {
    "modelMetrics": {"m1": {"usage": {"inputTokens": 100, "outputTokens": 10,
                                      "cacheReadTokens": 40, "cacheWriteTokens": 0}}}}}})
OPENCODE_OUT = json.dumps({"type": "step_finish", "sessionID": "s-oc", "part": {"tokens": {
    "input": 10, "output": 5, "reasoning": 0, "cache": {"read": 0, "write": 0}, "total": 15}}})

# The fake reports the HOME and configuration variables it was given, and which personal copies
# of the skill it could reach by its CLI's own documented lookup (each CLI's help and bundled
# docs, 2026-11-06), read from that environment: never from the runner's table.
_FAKE = """#!{python}
import json, os, pathlib, sys
env = os.environ
home = pathlib.Path(env["HOME"])
def on(var):
    return env.get(var, "").lower() in ("1", "true")
def under(var, default):
    return pathlib.Path(env[var]) if env.get(var) else home / default
agents, claude_home = home / ".agents" / "skills", home / ".claude" / "skills"
opencode = [under("XDG_CONFIG_HOME", ".config") / "opencode" / d for d in ("skills", "skill")]
if not (on("OPENCODE_DISABLE_EXTERNAL_SKILLS") or on("OPENCODE_DISABLE_CLAUDE_CODE_SKILLS")):
    opencode.append(claude_home)
if not on("OPENCODE_DISABLE_EXTERNAL_SKILLS"):
    opencode.append(agents)
name = pathlib.Path(sys.argv[0]).name
roots = {{"claude": [under("CLAUDE_CONFIG_DIR", ".claude") / "skills"],
         "codex": [under("CODEX_HOME", ".codex") / "skills", agents],
         "copilot": [under("COPILOT_HOME", ".copilot") / "skills", agents],
         "opencode": opencode}}.get(name, [])
# The login file each CLI reads from its configuration directory. Copilot's config.json names
# skill directories, so it must stay out of reach as well.
login = {{"claude": under("CLAUDE_CONFIG_DIR", ".claude") / ".credentials.json",
         "codex": under("CODEX_HOME", ".codex") / "auth.json",
         "copilot": under("COPILOT_HOME", ".copilot") / "config.json"}}.get(name)
config = {{v: env.get(v) for v in ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "COPILOT_HOME")}}
with open(env["FAKE_CLI_LOG"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps({{"argv": sys.argv, "cwd": os.getcwd(), "home": str(home),
                         "config": config,
                         "config_is_dir": {{k: bool(v) and os.path.isdir(v)
                                           for k, v in config.items()}},
                         "config_files": {{k: sorted(os.listdir(v)) for k, v in config.items()
                                          if v and os.path.isdir(v)}},
                         "login": {{"text": login.read_text() if login and login.is_file()
                                   else None,
                                   "link": os.readlink(login) if login and login.is_symlink()
                                   else None}},
                         "ceiling": env.get("GIT_CEILING_DIRECTORIES"),
                         "personal": [str(r / "sdlc-studio") for r in roots
                                      if (r / "sdlc-studio" / "SKILL.md").is_file()]}}) + "\\n")
fix = {fix!r}
if fix:
    pathlib.Path("paginate.py").write_text(fix, encoding="utf-8")
sys.stdout.write({out!r})
sys.exit({code})
"""


def _git_env() -> dict:
    """The environment without the git variables a hook exports, so a fixture repo is its own."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=bench",
                           "-c", "user.email=bench@example.invalid", *args],
                          check=True, capture_output=True, text=True,
                          env=_git_env()).stdout.strip()


class BenchHeadlessTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # A repository whose skill differs at the pinned commit, at HEAD and in the tree.
        self.repo = self.tmp / "repo"
        skill = self.repo / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        _git(self.repo, "init", "-q")
        (skill / "SKILL.md").write_text("pinned skill\n", encoding="utf-8")
        (skill / "scripts").mkdir()
        (skill / "scripts" / "tool.py").write_text("PINNED = True\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "pinned")
        self.pinned = _git(self.repo, "rev-parse", "HEAD")
        (skill / "SKILL.md").write_text("head skill\n", encoding="utf-8")
        _git(self.repo, "commit", "-qam", "head")
        (skill / "SKILL.md").write_text("working tree skill\n", encoding="utf-8")
        (skill / "UNTRACKED.md").write_text("not committed\n", encoding="utf-8")
        self.results = self.tmp / "runs.jsonl"
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.log = self.tmp / "cli.log"
        patches = (mock.patch.object(runner, "REPO_ROOT", self.repo),
                   mock.patch.dict(os.environ, {
                       "PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
                       "FAKE_CLI_LOG": str(self.log),
                       # A HOME of the test's own, so the operator's skill copies cannot refuse
                       # a run and the operator's real login is never read.
                       "HOME": str(self.tmp / "home")}))
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        for var in ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "COPILOT_HOME", "XDG_CONFIG_HOME",
                    "GIT_CEILING_DIRECTORIES", *EXPORTS["claude"], *EXPORTS["codex"]):
            os.environ.pop(var, None)  # restored with the rest of os.environ by the patch
        # Fake logins where each CLI looks by default, so a run has a file to authenticate from.
        self.logins = {"claude": self.tmp / "home" / ".claude" / ".credentials.json",
                       "codex": self.tmp / "home" / ".codex" / "auth.json"}
        for harness, path in self.logins.items():
            path.parent.mkdir(parents=True)
            path.write_text(f'{{"fake": "{harness} default login"}}', encoding="utf-8")

    def _fake(self, name: str, out: str, code: int = 0, fix: str = "") -> None:
        path = self.bin / name
        path.write_text(_FAKE.format(python=sys.executable, out=out, code=code, fix=fix),
                        encoding="utf-8")
        path.chmod(0o755)

    def _main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = runner.main(list(argv))
            except (ValueError, RuntimeError) as exc:
                print(f"error: {exc}", file=sys.stderr)
                code = 1
        return code, out.getvalue(), err.getvalue()

    def _run(self, harness: str, run_id: str, *extra: str) -> tuple[int, str, str]:
        return self._main("run", "--fixture", "brownfield-pagination", "--arm", "A",
                          "--harness", harness, "--skill-ref", self.pinned, "--run-id", run_id,
                          "--dest", str(self.tmp / f"ws-{harness}-{run_id}"),
                          "--results", str(self.results), *extra)

    def _rows(self) -> list[dict]:
        return runner.read_all(self.results)

    # AC1
    def test_prepare_installs_the_pinned_skill_for_the_harness(self) -> None:
        for harness, local in (("claude", ".claude/skills"), ("codex", ".agents/skills"),
                               ("copilot", ".github/skills"), ("opencode", ".opencode/skills")):
            dest = self.tmp / f"ws-{harness}"
            code, out, err = self._main("prepare", "--fixture", "brownfield-pagination",
                                        "--arm", "A", "--dest", str(dest),
                                        "--harness", harness, "--skill-ref", self.pinned)
            self.assertEqual(code, 0, err)
            installed = dest / local / "sdlc-studio"
            self.assertEqual((installed / "SKILL.md").read_text(encoding="utf-8"),
                             "pinned skill\n", harness)
            self.assertTrue((installed / "scripts" / "tool.py").is_file(), harness)
            self.assertFalse((installed / "UNTRACKED.md").exists(), harness)
            self.assertTrue((dest / "paginate.py").is_file(), harness)
            self.assertIn(self.pinned, out)
            if local != ".claude/skills":
                self.assertFalse((dest / ".claude" / "skills").exists(), harness)
        # A harness install.sh names no skill directory for is refused by name, before any write.
        dest = self.tmp / "ws-cursor"
        code, _, err = self._main("prepare", "--fixture", "brownfield-pagination", "--arm", "A",
                                  "--dest", str(dest), "--harness", "cursor",
                                  "--skill-ref", self.pinned)
        self.assertEqual(code, 1)
        self.assertIn("'cursor'", err)
        self.assertIn("install.sh --list-targets", err)
        self.assertFalse(dest.exists())
        # A ref that names no commit is refused, and arm B stays free of the skill.
        code, _, err = self._main("prepare", "--fixture", "brownfield-pagination", "--arm", "A",
                                  "--dest", str(self.tmp / "ws-bad"), "--harness", "claude",
                                  "--skill-ref", "no-such-ref")
        self.assertEqual(code, 1)
        self.assertIn("no-such-ref", err)
        dest = self.tmp / "ws-b"
        code, _, err = self._main("prepare", "--fixture", "brownfield-pagination", "--arm", "B",
                                  "--dest", str(dest), "--harness", "claude",
                                  "--skill-ref", self.pinned)
        self.assertEqual(code, 0, err)
        self.assertFalse((dest / ".claude" / "skills").exists())
        # The two flags go together: a harness without a pinned ref is refused.
        code, _, err = self._main("prepare", "--fixture", "brownfield-pagination", "--arm", "A",
                                  "--dest", str(self.tmp / "ws-unpinned"), "--harness", "claude")
        self.assertEqual(code, 1)
        self.assertIn("--skill-ref", err)

    # AC2
    def test_run_records_measured_usage_and_score(self) -> None:
        self._fake("claude", CLAUDE_OUT, fix=FIX)
        code, out, err = self._run("claude", "r1", "--model", "claude-haiku-5-5")
        self.assertEqual(code, 0, err)
        (call,) = [json.loads(line) for line in self.log.read_text().splitlines()]
        argv = call["argv"]
        self.assertEqual(argv[1], "-p")
        self.assertIn("TICKET.md", argv[2])
        self.assertEqual(argv[argv.index("--output-format") + 1], "json")
        self.assertEqual(argv[argv.index("--model") + 1], "claude-haiku-5-5")
        self.assertEqual(Path(call["cwd"]).resolve(), (self.tmp / "ws-claude-r1").resolve())
        (row,) = self._rows()
        self.assertEqual((row["fixture"], row["arm"], row["harness"], row["run_id"]),
                         ("brownfield-pagination", "A", "claude", "r1"))
        self.assertEqual(row["metrics_source"], "measured")
        self.assertEqual(row["skill_ref"], self.pinned)
        self.assertEqual(row["usage"], {"input": 2, "cache_read": 11382, "cache_write": 17126,
                                        "cache_write_1h": 17126, "output": 35, "reasoning": 31})
        self.assertEqual(row["tokens"], 2 + 11382 + 17126 + 35)
        self.assertEqual(row["model"], "claude-haiku-5-5")
        self.assertIsInstance(row["wall_time_s"], float)
        self.assertGreaterEqual(row["wall_time_s"], 0)
        self.assertIs(row["defect_escape"], False)  # the fake's fix passes the held-back suite
        # Codex counts cached tokens inside input_tokens; the normaliser takes them out.
        self._fake("codex", CODEX_OUT)
        code, _, err = self._run("codex", "r1", "--model", "gpt-5.5")
        self.assertEqual(code, 0, err)
        row = self._rows()[-1]
        self.assertEqual(row["harness"], "codex")
        self.assertEqual(row["usage"]["input"], 14524 - 12288)
        self.assertEqual(row["usage"]["cache_read"], 12288)
        self.assertEqual(row["tokens"], 14524 + 5)
        self.assertEqual((row["model"], row["model_source"]), ("gpt-5.5", "caller"))
        self.assertIs(row["defect_escape"], True)  # nothing fixed, the seeded bug escapes
        # A CLI that printed no usage, or exited non-zero, writes no row.
        before = len(self._rows())
        self._fake("claude", NO_USAGE_OUT, fix=FIX)
        code, _, err = self._run("claude", "r2")
        self.assertEqual(code, 1)
        self.assertIn("no row written", err)
        self.assertIn("no usage", err)
        self._fake("claude", CLAUDE_OUT, code=3, fix=FIX)
        code, _, err = self._run("claude", "r3")
        self.assertEqual(code, 1)
        self.assertIn("status 3", err)
        self.assertEqual(len(self._rows()), before)
        # A harness with no headless command, or a used workspace, is refused before the CLI runs.
        calls = len(self.log.read_text().splitlines())
        code, _, err = self._run("gemini", "r4")
        self.assertEqual(code, 1)
        self.assertIn("'gemini'", err)
        code, _, err = self._main("run", "--fixture", "brownfield-pagination", "--arm", "A",
                                  "--harness", "claude", "--skill-ref", self.pinned,
                                  "--run-id", "r5", "--dest", str(self.tmp / "ws-claude-r1"),
                                  "--results", str(self.results))
        self.assertEqual(code, 1)
        self.assertIn("not empty", err)
        self.assertEqual(len(self.log.read_text().splitlines()), calls)

    def _calls(self) -> list[dict]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    # AC2: the row's skill_ref is the skill the session ran, so no personal copy may reach it.
    def test_no_personal_copy_of_the_skill_reaches_the_session(self) -> None:
        home, operator = self.tmp / "home", self.tmp / "operator"
        copies = {name: root / "sdlc-studio" for name, root in (
            ("claude", home / ".claude" / "skills"), ("codex", home / ".codex" / "skills"),
            ("copilot", home / ".copilot" / "skills"), ("agents", home / ".agents" / "skills"),
            ("opencode", home / ".config" / "opencode" / "skills"),
            ("claude-set", operator / "claude" / "skills"),
            ("codex-set", operator / "codex" / "skills"),
            ("copilot-set", operator / "copilot" / "skills"))}
        for copy in copies.values():
            copy.mkdir(parents=True)
            (copy / "SKILL.md").write_text("personal skill\n", encoding="utf-8")
        for harness, login in (("claude", ".credentials.json"), ("codex", "auth.json")):
            (operator / harness / login).write_text("{}", encoding="utf-8")
        patch = mock.patch.dict(os.environ, {
            "HOME": str(home), "CLAUDE_CONFIG_DIR": str(operator / "claude"),
            "CODEX_HOME": str(operator / "codex"), "COPILOT_HOME": str(operator / "copilot")})
        patch.start()
        self.addCleanup(patch.stop)
        os.environ.pop("XDG_CONFIG_HOME", None)
        harnesses = {"claude": CLAUDE_OUT, "codex": CODEX_OUT, "copilot": COPILOT_OUT,
                     "opencode": OPENCODE_OUT}
        for harness, out in harnesses.items():
            self._fake(harness, out, fix=FIX)
            # Positive control: the operator's own environment reaches a personal copy.
            subprocess.run([str(self.bin / harness)], cwd=self.tmp, check=True,
                           capture_output=True)
            self.assertTrue(self._calls()[-1]["personal"], harness)

        def measured(harness: str, run_id: str, arm: str = "A") -> dict:
            calls = len(self._calls())
            code, _, err = self._main(
                "run", "--fixture", "brownfield-pagination", "--arm", arm, "--harness", harness,
                "--skill-ref", self.pinned, "--run-id", run_id, "--dest",
                str(self.tmp / f"ws-{harness}-{run_id}"), "--results", str(self.results))
            self.assertEqual(code, 0, err)
            (call,) = self._calls()[calls:]
            self.assertEqual(call["home"], str(home), harness)
            self.assertEqual(call["personal"], [], harness)
            var = runner.CONFIG_DIR_VAR.get(harness)
            if var:
                private = Path(call["config"][var])
                self.assertTrue(call["config_is_dir"][var], harness)
                self.assertNotEqual(private, operator / harness, harness)
                self.assertNotIn(home, private.parents, harness)
                self.assertFalse(private.exists(), f"{harness}: {private} outlived the run")
            row = self._rows()[-1]
            self.assertEqual((row["harness"], row["arm"], row["skill_ref"],
                              row["metrics_source"]), (harness, arm, self.pinned, "measured"))
            return call

        def refused(harness: str, run_id: str, copy: Path) -> None:
            calls, rows = len(self._calls()), len(self._rows())
            dest = self.tmp / f"ws-{harness}-{run_id}"
            code, _, err = self._run(harness, run_id)
            self.assertEqual(code, 1, harness)
            self.assertIn(str(copy), err, harness)
            self.assertEqual((len(self._calls()), len(self._rows())), (calls, rows), harness)
            self.assertFalse(dest.exists(), harness)

        # Claude Code's personal directory moves with CLAUDE_CONFIG_DIR, for arm A and arm B.
        measured("claude", "a1")
        measured("claude", "b1", arm="B")
        # A copy where no variable of the harness reaches refuses the run, naming the copy.
        refused("codex", "r1", copies["agents"])
        refused("copilot", "r1", copies["agents"])
        refused("opencode", "r1", copies["opencode"])
        # OpenCode's scans of ~/.claude and ~/.agents are switched off; its own global is gone.
        shutil.rmtree(copies["opencode"])
        measured("opencode", "r2")
        # With ~/.agents/skills clear, Codex and Copilot run with their own directory moved.
        shutil.rmtree(copies["agents"])
        measured("codex", "r2")
        measured("copilot", "r2")
        # OpenCode's global directory follows XDG_CONFIG_HOME where the operator sets it.
        self.assertEqual(runner.fixed_skill_dirs("opencode", {"HOME": "/h",
                                                              "XDG_CONFIG_HOME": "/x"})[0],
                         Path("/x/opencode/skills"))

    # BG1248 AC2: the session authenticates from a link to the operator's login file, alone.
    def test_only_the_operators_login_file_is_linked_into_the_private_directory(self) -> None:
        operator = self.tmp / "operator"
        logins = {"claude": operator / "claude" / ".credentials.json",
                  "codex": operator / "codex" / "auth.json",
                  "copilot": operator / "copilot" / "config.json"}
        for harness, login in logins.items():
            skill = login.parent / "skills" / "sdlc-studio"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("personal skill\n", encoding="utf-8")
            (login.parent / "settings.json").write_text("{}", encoding="utf-8")
            login.write_text(f'{{"fake": "{harness} operator login"}}', encoding="utf-8")
        patch = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(operator / "claude"),
                                             "CODEX_HOME": str(operator / "codex"),
                                             "COPILOT_HOME": str(operator / "copilot")})
        patch.start()
        self.addCleanup(patch.stop)
        outs = {"claude": CLAUDE_OUT, "codex": CODEX_OUT, "copilot": COPILOT_OUT}

        def session(harness: str, run_id: str) -> dict:
            self._fake(harness, outs[harness], fix=FIX)
            calls = len(self._calls())
            code, _, err = self._run(harness, run_id)
            self.assertEqual(code, 0, f"{harness}: {err}")
            (call,) = self._calls()[calls:]
            self.assertEqual(call["personal"], [], harness)
            return call

        for harness in ("claude", "codex"):
            login, var = logins[harness], runner.CONFIG_DIR_VAR[harness]
            call = session(harness, "op")
            # A link to the operator's own file, not a copy, and the only entry in the directory.
            self.assertEqual(call["login"], {"text": f'{{"fake": "{harness} operator login"}}',
                                             "link": str(login)}, harness)
            self.assertEqual(call["config_files"][var], [login.name], harness)
            # The run removed its link and left the operator's file as it was.
            self.assertEqual(login.read_text(encoding="utf-8"),
                             f'{{"fake": "{harness} operator login"}}', harness)
        # Copilot's config.json names skill directories, so it is never carried in.
        call = session("copilot", "op")
        self.assertEqual(call["login"], {"text": None, "link": None})
        self.assertEqual(call["config_files"]["COPILOT_HOME"], [])
        # With the variable unset, the login is read from its default directory under HOME.
        for var in ("CLAUDE_CONFIG_DIR", "CODEX_HOME"):
            os.environ.pop(var)
        for harness in ("claude", "codex"):
            call = session(harness, "home")
            self.assertEqual(call["login"]["link"], str(self.logins[harness]), harness)

    # BG1248 AC2: with no login file and nothing exported, the refusal names what a run needs.
    def test_a_run_with_no_login_names_the_exports_it_needs(self) -> None:
        for harness, out in (("claude", CLAUDE_OUT), ("codex", CODEX_OUT)):
            self._fake(harness, out, fix=FIX)
            self.logins[harness].unlink()
            calls = len(self._calls())
            code, _, err = self._run(harness, "nologin")
            self.assertEqual(code, 1, harness)
            self.assertIn(str(self.logins[harness]), err, harness)
            for var in EXPORTS[harness]:
                self.assertIn(var, err, harness)
            self.assertEqual(len(self._calls()), calls, harness)
            self.assertFalse((self.tmp / f"ws-{harness}-nologin").exists(), harness)
            # Positive control: any one export is enough, and no dangling link is made for it.
            for var in EXPORTS[harness]:
                with mock.patch.dict(os.environ, {var: "fake-token"}):
                    code, _, err = self._run(harness, f"env-{var}")
                self.assertEqual(code, 0, f"{harness} {var}: {err}")
                self.assertEqual(
                    self._calls()[-1]["config_files"][runner.CONFIG_DIR_VAR[harness]], [], var)
        # Copilot and OpenCode carry no login file in, so neither is refused for one.
        for harness, out in (("copilot", COPILOT_OUT), ("opencode", OPENCODE_OUT)):
            self._fake(harness, out, fix=FIX)
            code, _, err = self._run(harness, "nologin")
            self.assertEqual(code, 0, f"{harness}: {err}")

    # BG1248 AC1: a dest inside a git work tree is refused before anything is written.
    def test_a_dest_inside_a_git_work_tree_is_refused(self) -> None:
        self._fake("claude", CLAUDE_OUT, fix=FIX)
        (self.repo / "empty").mkdir()
        # A caller's ceiling that would hide the repository from git's discovery hides nothing.
        os.environ["GIT_CEILING_DIRECTORIES"] = str(self.repo)
        for dest in (self.repo / "tools" / "bench" / "ws-nested", self.repo / "empty"):
            code, _, err = self._main("run", "--fixture", "brownfield-pagination", "--arm", "B",
                                      "--harness", "claude", "--skill-ref", self.pinned,
                                      "--run-id", "nested", "--dest", str(dest),
                                      "--results", str(self.results))
            self.assertEqual(code, 1, dest)
            self.assertIn("git work tree", err, dest)
            self.assertIn(os.path.realpath(self.repo), err, dest)
        self.assertFalse((self.repo / "tools").exists())
        self.assertEqual(list((self.repo / "empty").iterdir()), [])
        self.assertEqual((self._calls(), self._rows()), ([], []))
        # Positive control: a dest beside the repository runs, with git's discovery stopped at
        # the workspace's parent in place of the caller's ceiling.
        code, _, err = self._run("claude", "beside")
        self.assertEqual(code, 0, err)
        self.assertEqual(self._calls()[-1]["ceiling"],
                         str((self.tmp / "ws-claude-beside").resolve().parent))

    # AC3
    def test_summary_by_fixture_arm_and_harness_with_dollars(self) -> None:
        self._fake("claude", CLAUDE_OUT, fix=FIX)
        self._fake("codex", CODEX_OUT)
        for harness, model in (("claude", "claude-haiku-5-5"), ("codex", "gpt-5.5")):
            code, _, err = self._run(harness, "r1", "--model", model)
            self.assertEqual(code, 0, err)
        code, out, err = self._main("summary", "--results", str(self.results))
        self.assertEqual(code, 0, err)
        s = json.loads(out)
        self.assertEqual(sorted(s), ["brownfield-pagination::A::claude",
                                     "brownfield-pagination::A::codex"])
        claude, codex = s["brownfield-pagination::A::claude"], s["brownfield-pagination::A::codex"]
        self.assertEqual((claude["n"], codex["n"]), (1, 1))
        self.assertEqual((claude["harness"], codex["harness"]), ("claude", "codex"))
        self.assertEqual(claude["mean_tokens"], 28545)
        self.assertEqual(codex["mean_tokens"], 14529)
        self.assertEqual((claude["defect_escape_rate"], codex["defect_escape_rate"]), (0, 1))
        # 2 x $0.10 + 35 x $0.50 + 11382 x $0.01 + 17126 x $0.20 per million: Claude Code's
        # own costUSD for the captured session.
        self.assertAlmostEqual(claude["mean_usd"], 0.00355672, places=8)
        self.assertEqual(claude["priced_n"], 1)
        self.assertEqual(claude["unpriced"], [])
        self.assertIsNone(codex["mean_usd"])
        self.assertEqual(codex["priced_n"], 0)
        self.assertEqual(len(codex["unpriced"]), 1)
        self.assertIn("gpt-5.5", codex["unpriced"][0])

    def test_a_mixed_model_session_is_priced_per_model(self) -> None:
        self._fake("claude", CLAUDE_MIXED_OUT, fix=FIX)
        code, _, err = self._run("claude", "r1")
        self.assertEqual(code, 0, err)
        (row,) = self._rows()
        self.assertEqual(sorted(row["usage_by_model"]), ["claude-haiku-5-5", "claude-sonnet-5-5"])
        self.assertEqual(row["usage_by_model"]["claude-sonnet-5-5"]["input"], 1000)
        code, out, err = self._main("summary", "--results", str(self.results))
        self.assertEqual(code, 0, err)
        group = json.loads(out)["brownfield-pagination::A::claude"]
        # haiku as captured, plus 1000 x $2 + 200 x $10 per million at sonnet's rate; the
        # summed counts priced at the larger model would be 0.00375672.
        self.assertAlmostEqual(group["mean_usd"], 0.00355672 + 0.004, places=8)
        # Copilot splits its session accounting by model, and its inputTokens hold the cache.
        metrics = {m: {"usage": {"inputTokens": n, "outputTokens": 10, "cacheReadTokens": 40,
                                 "cacheWriteTokens": 0}} for m, n in (("m1", 100), ("m2", 50))}
        copilot = json.dumps({"type": "session.shutdown",
                              "data": {"accountingSnapshot": {"modelMetrics": metrics}}})
        split = runner.usage_by_model("copilot", copilot)
        self.assertEqual({m: c["input"] for m, c in split.items()}, {"m1": 60, "m2": 10})
        self.assertIsNone(runner.usage_by_model("claude", CLAUDE_OUT))  # one model, no split

    def test_legacy_rows_keep_their_fixture_arm_key(self) -> None:
        runner.record({"fixture": "f", "arm": "A", "run_id": "n1", "tokens": 10},
                      self.results)
        code, out, err = self._main("summary", "--results", str(self.results))
        self.assertEqual(code, 0, err)
        s = json.loads(out)
        self.assertEqual(list(s), ["f::A"])
        self.assertNotIn("mean_usd", s["f::A"])


if __name__ == "__main__":
    unittest.main()
