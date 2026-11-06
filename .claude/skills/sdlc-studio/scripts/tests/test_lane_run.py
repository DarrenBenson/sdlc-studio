"""US1126: `sprint lane run` runs a lane's brief headless in any supported CLI, in the lane's own
worktree, and `lane return` prices the lane from the usage that session printed.

Every case drives `sprint.py lane run` through its entry point against a throwaway repository.
A fake CLI on PATH stands in for each harness (`claude`, `cursor-agent`, `codex`, `copilot`,
`opencode`): it logs its argv and working directory, optionally stages a file, prints that
harness's captured headless output (US1125's fixtures, `fixtures/harness_usage/`) or nothing,
and exits with the status the case asks for. No real CLI is ever called.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import harness_usage, lanes  # noqa: E402

sprint = loader.load_script("sprint")
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "harness_usage"
TEMPLATE = SCRIPTS.parent / "reference-agent-prompt-template.md"
UNIT = "US0101"

#: Each harness: its binary, the fixture it prints, the headless flags its command must carry and
#: the model flag. Typed here from the CLIs' own help and the 2026-11-06 captures, never read
#: from the code under test.
HARNESSES = {
    "claude": ("claude", "claude.json", ["-p", "--output-format", "json"], "--model"),
    "cursor": ("cursor-agent", "cursor.json", ["-p", "--output-format", "json"], "--model"),
    "codex": ("codex", "codex.jsonl", ["exec", "--json"], "-m"),
    "copilot": ("copilot", "copilot.jsonl", ["-p", "--output-format", "json"], "--model"),
    "opencode": ("opencode", "opencode.jsonl", ["run", "--format", "json"], "-m"),
}
#: The claude capture's one call, typed from `fixtures/harness_usage/claude.json`.
CLAUDE = {"session": "4052faf6-ae92-4245-a560-c2c9534b3cec", "model": "claude-haiku-5-5",
          "input": 2, "output": 35, "cache_read": 11382, "cache_write_1h": 17126}

FAKE = r'''#!{python}
import json, os, subprocess, sys
name = os.path.basename(sys.argv[0])
with open(os.path.join(os.environ["FAKE_LOG"], name + ".json"), "w") as fh:
    json.dump({{"argv": sys.argv[1:], "cwd": os.getcwd()}}, fh)
stage = os.environ.get("FAKE_STAGE")
if stage:
    with open(stage, "w") as fh:
        fh.write("LANE = 1\n")
    subprocess.run(["git", "add", "--", stage], check=True)
out = os.environ.get("FAKE_OUT_" + name.replace("-", "_").upper())
if out and os.environ.get("FAKE_MODE") != "silent":
    sys.stdout.write(open(out).read())
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
'''


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _git(cwd: Path, *args: str) -> str:
    return gitutil.git(list(args), cwd, text=True).stdout.strip()


def _rs():
    return sys.modules["lib.run_state"]


class LaneRunTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name).resolve()
        self.root, self.bin, self.log = base / "repo", base / "bin", base / "log"
        self.bin.mkdir()
        self.log.mkdir()
        _write(self.root, "src/a.py", "A = 1\n")
        _write(self.root, ".gitignore", "sdlc-studio/.local/\n.claude/worktrees/\n")
        _write(self.root, f"sdlc-studio/stories/{UNIT}-lane.md",
               f"# {UNIT}: lane\n\n> **Status:** Ready\n> **Points:** 2\n> **Epic:** EP0001\n"
               f"> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
               "- **Verify:** file src/a.py\n")
        gitutil.git(["init", "-q", "-b", "main"], self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the fixture"], self.root)
        env = {"PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
               "FAKE_LOG": str(self.log),
               # an orchestrator transcript the lane must never be priced from
               _rs().TRANSCRIPTS_ENV: str(base / "transcripts")}
        for binary, fixture, _flags, _model in HARNESSES.values():
            path = self.bin / binary
            path.write_text(FAKE.format(python=sys.executable), encoding="utf-8")
            path.chmod(0o755)
            env["FAKE_OUT_" + binary.replace("-", "_").upper()] = str(FIXTURES / fixture)
        patch = unittest.mock.patch.dict(os.environ, env)
        patch.start()
        self.addCleanup(patch.stop)
        for k in ("FAKE_MODE", "FAKE_EXIT", "FAKE_STAGE"):
            os.environ.pop(k, None)
        _write(base / "transcripts", "orchestrator.jsonl", json.dumps(
            {"type": "assistant", "cwd": str(self.root), "message": {
                "id": "msg_orch", "model": "claude-opus-5-5", "role": "assistant",
                "usage": {"input_tokens": 900_000, "output_tokens": 90_000}}}) + "\n")

    # -- driving the command --------------------------------------------------------------
    def _lane(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = sprint.main(["lane", *argv, "--root", str(self.root)])
        return rc, out.getvalue()

    def _run(self, harness: str, *extra: str) -> tuple[int, str]:
        return self._lane("run", "--harness", harness, "--units", UNIT, *extra)

    def _called(self, binary: str) -> dict:
        return json.loads((self.log / f"{binary}.json").read_text(encoding="utf-8"))

    def _record(self) -> dict:
        return json.loads((self.root / lanes.RUN_RECORDS / f"{UNIT}.json").read_text("utf-8"))

    def _worktree(self, name: str = "wt-lane") -> Path:
        wt = self.root.parent / name
        gitutil.git(["worktree", "add", "-q", "-b", f"lane-{name}", str(wt), "main"], self.root)
        return wt.resolve()

    def _open_run(self) -> None:
        _rs().open_run(self.root, batch=[UNIT], goal="g")

    def _delegated(self) -> list[dict]:
        return [r for r in _rs().read(self.root).get(_rs().DELEGATED) or []
                if r.get("unit") == UNIT]

    # -- AC1 --------------------------------------------------------------------------------
    def test_each_harness_runs_its_headless_command_in_the_worktree(self) -> None:
        """AC1. MUTANTS: the CLI run with `cwd` the root rather than the worktree (the logged cwd
        is the root); the brief left off the argv or split across words (no one argument
        carries it); `--model` dropped, or passed when none was given; a harness's headless
        flags missing (the CLI would start interactive); the timeout not handed to the run
        (the spy sees none); the worktree not created when none is named (no lane worktree)."""
        spy = unittest.mock.patch.object(lanes.subprocess, "run", wraps=subprocess.run)
        for harness, (binary, _fixture, flags, model_flag) in HARNESSES.items():
            with self.subTest(harness=harness), spy as run:
                rc, out = self._run(harness, "--model", f"m-{harness}", "--timeout", "77")
                self.assertEqual(0, rc, out)
                called = self._called(binary)
                wt = Path(called["cwd"]).resolve()
                self.assertNotEqual(self.root.resolve(), wt, "the CLI ran in the main tree")
                self.assertEqual(self.root.resolve(), Path(_git(wt, "rev-parse",
                                                                "--git-common-dir")).resolve()
                                 .parent, "the CLI ran outside a worktree of the root")
                self.assertEqual(str(wt), self._record()["worktree"])
                argv = called["argv"]
                for flag in flags:
                    self.assertIn(flag, argv)
                if harness in ("codex", "opencode"):
                    self.assertEqual(flags[0], argv[0], "the subcommand comes first")
                briefs = [a for a in argv if f"Unit: {UNIT}" in a]
                self.assertEqual(1, len(briefs), argv)
                self.assertIn("Acceptance criteria", briefs[0])
                self.assertEqual(f"m-{harness}", argv[argv.index(model_flag) + 1])
                timeouts = [c.kwargs.get("timeout") for c in run.call_args_list
                            if c.args and c.args[0] and Path(c.args[0][0]).name == binary]
                self.assertEqual([77], timeouts)
        rc, out = self._run("opencode")
        self.assertEqual(0, rc, out)
        self.assertNotIn("-m", self._called("opencode")["argv"])
        self.assertNotIn("--model", self._called("opencode")["argv"])

    # -- AC2 --------------------------------------------------------------------------------
    def test_the_lane_is_priced_from_the_recorded_usage(self) -> None:
        """AC2. MUTANTS: the return pricing the orchestrator's transcript (900k input) rather than
        the lane record; the record keeping the raw output rather than the normalised usage
        (no `cache_read` count); the session id or model left off the record; the one-hour
        cache write booked as a five-minute write (the priced figure moves); a record from
        another run priced into this one."""
        self._open_run()
        rc, out = self._run("claude")
        self.assertEqual(0, rc, out)
        rec = self._record()
        self.assertEqual(CLAUDE["session"], rec["session_id"])
        self.assertEqual(CLAUDE["model"], rec["usage_model"])
        self.assertTrue(rec["metered"])
        for k in ("input", "output", "cache_read", "cache_write_1h"):
            self.assertEqual(CLAUDE[k], rec["usage"][k], k)
        self.assertEqual(CLAUDE["cache_write_1h"], rec["usage"]["cache_write"])
        rc, out = self._lane("return", "--units", UNIT)
        self.assertEqual(0, rc, out)
        [got] = self._delegated()
        parts = {"input": 2, "output": 35, "cache_write_5m": 0, "cache_write_1h": 17126,
                 "cache_read": 11382}
        self.assertEqual(parts, got["components"])
        # D0390's weights, typed here: 2 + 5 x 35 + 2.0 x 17126 + 0.1 x 11382
        self.assertEqual(round(2 + 175 + 34252 + 1138.2), got["priced"])
        self.assertEqual(2 + 35 + 17126, got["tokens"])
        self.assertEqual(f"{UNIT}.json", Path(got["transcript"]).name)
        self.assertIn(f"read from {UNIT}.json", out)
        # the capture's own costUSD, 0.00355672, from the shipped price table
        self.assertIn("lane run cost: US$0.0036 (claude-haiku-5-5)", out)
        # a record another run wrote is not this run's lane
        rec["run_id"] = "RUN-OTHER"
        (self.root / lanes.RUN_RECORDS / f"{UNIT}.json").write_text(json.dumps(rec), "utf-8")
        _rs().update(self.root, **{_rs().DELEGATED: []})
        rc, out = self._lane("return", "--units", UNIT)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self._delegated())
        self.assertIn("another run", out)

    # -- AC3 --------------------------------------------------------------------------------
    def test_a_failed_or_silent_cli_leaves_the_lane_unmetered(self) -> None:
        """AC3. MUTANTS: a non-zero exit priced as a metered run; a silent CLI recorded with zero
        counts rather than none; the timeout raising out of the command (no record); the
        worktree removed or its index reset after a failed run (the staged file is gone); the
        return recording a zero-token delegated record for an unmetered lane."""
        self._open_run()
        cases = (("fail", {"FAKE_EXIT": "3"}, harness_usage.NONZERO_EXIT, 1),
                 ("silent", {"FAKE_MODE": "silent"}, harness_usage.NO_USAGE, 0),
                 ("timeout", {}, lanes.TIMED_OUT, 1))
        for name, env, kind, code in cases:
            with self.subTest(case=name):
                wt = self._worktree(f"wt-{name}")
                staged = wt / "src" / "lane.py"
                env = dict(env, FAKE_STAGE=str(staged))
                real = subprocess.run

                def hang(cmd, *a, wt=wt, real=real, **kw):
                    if Path(cmd[0]).name == "codex":
                        _write(wt, "src/lane.py", "LANE = 1\n")
                        real(["git", "add", "--", "src/lane.py"], cwd=wt, check=True)
                        raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
                    return real(cmd, *a, **kw)

                hook = (unittest.mock.patch.object(lanes.subprocess, "run", side_effect=hang)
                        if name == "timeout" else contextlib.nullcontext())
                with unittest.mock.patch.dict(os.environ, env), hook:
                    rc, out = self._run("codex", "--worktree", str(wt))
                self.assertEqual(code, rc, out)
                rec = self._record()
                self.assertFalse(rec["metered"])
                self.assertEqual(kind, rec["unmetered"])
                self.assertTrue(rec["reason"])
                self.assertIn(rec["reason"], out)
                self.assertEqual({}, {k: v for k, v in rec["usage"].items() if v is not None})
                self.assertEqual(["src/lane.py"], rec["staged"])
                self.assertEqual("src/lane.py", _git(wt, "diff", "--cached", "--name-only"))
                rc, out = self._lane("return", "--units", UNIT)
                self.assertEqual(0, rc, out)
                self.assertEqual([], self._delegated())
                self.assertIn("unmetered", out)
                self.assertIn(rec["reason"], out)

    # -- AC4 --------------------------------------------------------------------------------
    def test_the_template_names_lane_run_for_a_harness_without_subagents(self) -> None:
        """AC4. MUTANTS: the template naming only the subagent route (no paragraph names
        `lane run`); the paragraph dropping the one-fresh-session-per-lane rule; a harness
        dropped from the supported set it names."""
        paras = TEMPLATE.read_text(encoding="utf-8").split("\n\n")
        [para] = [p for p in paras if "without subagents" in p and "lane run" in p]
        self.assertRegex(para, r"sprint(\.py)? lane run --harness")
        self.assertRegex(para, r"one fresh session per lane")
        for harness in HARNESSES:
            self.assertIn(f"`{harness}`", para)

    # -- AC5 --------------------------------------------------------------------------------
    def test_claude_lane_starts_lean(self) -> None:
        """AC5. MUTANTS: `--strict-mcp-config` dropped (a bare `--tools` allowlist loads every MCP
        tool in full); `--disable-slash-commands` dropped; `--tools` naming no tool set; the
        first-call context read from the session total rather than the first call (the second
        iteration below moves it); the first-call context left off the record."""
        out_file = self.root.parent / "claude-two-calls.json"
        doc = json.loads((FIXTURES / "claude.json").read_text(encoding="utf-8"))
        second = {"input_tokens": 50, "output_tokens": 9, "cache_read_input_tokens": 28_000,
                  "cache_creation_input_tokens": 400}
        doc["usage"]["iterations"].append(second)
        for key, extra in second.items():  # the session total holds both calls
            doc["usage"][key] += extra
        self.assertNotEqual(2 + 17126 + 11382, sum(doc["usage"][k] for k in (
            "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
            "premise: the session total differs from the first call")
        out_file.write_text(json.dumps(doc), encoding="utf-8")
        with unittest.mock.patch.dict(os.environ, {"FAKE_OUT_CLAUDE": str(out_file)}):
            rc, out = self._run("claude")
        self.assertEqual(0, rc, out)
        argv = self._called("claude")["argv"]
        tools = argv[argv.index("--tools") + 1]
        self.assertEqual({"Bash", "Read", "Edit", "Write", "Glob", "Grep"},
                         set(re.split(r"[ ,]+", tools)))
        self.assertIn("--strict-mcp-config", argv)
        self.assertIn("--disable-slash-commands", argv)
        self.assertEqual(2 + 17126 + 11382, self._record()["first_call_context"])
        self.assertIn(f"first-call context: {2 + 17126 + 11382:,} tokens", out)
        for harness in HARNESSES:
            argv = lanes.headless_command(harness, "brief", None, self.root)
            if "--tools" in argv:
                self.assertIn("--strict-mcp-config", argv, harness)


if __name__ == "__main__":
    unittest.main()
