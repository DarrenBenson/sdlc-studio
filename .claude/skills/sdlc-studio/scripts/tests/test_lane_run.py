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
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import harness_usage, lanes, prices  # noqa: E402

sprint = loader.load_script("sprint")
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "harness_usage"
TEMPLATE = SCRIPTS.parent / "reference-agent-prompt-template.md"
HELP = SCRIPTS.parent / "help" / "sprint.md"
REPO = SCRIPTS.parents[3]
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
#: The capture's haiku share as the delegated record books it, and its list price per million
#: tokens typed from `templates/model-prices.json`: 0.10 input, 0.50 output, 0.20 one-hour write,
#: 0.01 cache read.
HAIKU_PARTS = {"input": 2, "output": 35, "cache_write_5m": 0, "cache_write_1h": 17126,
               "cache_read": 11382}
HAIKU_USD = (2 * 0.10 + 35 * 0.50 + 17126 * 0.20 + 11382 * 0.01) / 1e6

FAKE = r'''#!{python}
import json, os, subprocess, sys
LATE = ("import subprocess, sys, time; time.sleep(4); open(sys.argv[1], 'w').write('LATE = 1'); "
        "subprocess.run(['git', 'add', '--', sys.argv[1]], check=True)")
name = os.path.basename(sys.argv[0])
with open(os.path.join(os.environ["FAKE_LOG"], name + ".json"), "w") as fh:
    json.dump({{"argv": sys.argv[1:], "cwd": os.getcwd()}}, fh)
stage = os.environ.get("FAKE_STAGE")
if stage:
    with open(stage, "w") as fh:
        fh.write("LANE = 1\n")
    subprocess.run(["git", "add", "--", stage], check=True)
late = os.environ.get("FAKE_LATE")
if late:
    # a child that writes and stages `late` 4 s after it starts, while this CLI waits on it
    child = subprocess.Popen([sys.executable, "-c", LATE, late])
    with open(os.path.join(os.environ["FAKE_LOG"], "late.pid"), "w") as fh:
        fh.write(str(child.pid))
    if os.environ.get("FAKE_SIGNAL"):
        os.kill(os.getppid(), int(os.environ["FAKE_SIGNAL"]))
    child.wait()
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


def _running(pid: int) -> bool:
    """Whether `pid` is a live process, a zombie counting as dead."""
    stat = Path(f"/proc/{pid}/stat")
    if Path("/proc/self/stat").exists():
        try:
            return stat.read_text().rsplit(")", 1)[1].split()[0] != "Z"
        except OSError:
            return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _outlives(pid: int, seconds: float = 1.0) -> bool:
    """Whether `pid` is still running `seconds` from now, polled: a killed process is reaped by
    whoever inherits it, a moment after the kill. Well inside the late child's 4 s, so a child
    that was never killed is still running when the wait ends."""
    deadline = time.monotonic() + seconds
    while _running(pid):
        if time.monotonic() > deadline:
            return True
        time.sleep(0.02)
    return False


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
               # no real harness state is ever read or written
               "HOME": str(base / "home"), "XDG_DATA_HOME": str(base / "xdg"),
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
        for k in ("FAKE_MODE", "FAKE_EXIT", "FAKE_STAGE", "FAKE_LATE", "FAKE_SIGNAL"):
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

    def _records(self) -> list[Path]:
        return sorted((self.root / lanes.RUN_RECORDS / UNIT).glob("*.json"))

    def _record(self) -> dict:
        """The latest session's lane record."""
        return json.loads(self._records()[-1].read_text("utf-8"))

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
        spy = unittest.mock.patch.object(lanes, "_run_in_group", wraps=lanes._run_in_group)
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
        [path] = self._records()
        self.assertEqual(str(path), got["transcript"])
        self.assertIn(f"read from {path.name}", out)
        # the capture's own costUSD, 0.00355672, from the shipped price table
        self.assertIn("lane run cost: US$0.0036 (claude-haiku-5-5)", out)
        # a record another run wrote is not this run's lane
        rec["run_id"] = "RUN-OTHER"
        path.write_text(json.dumps(rec), "utf-8")
        _rs().update(self.root, **{_rs().DELEGATED: []})
        rc, out = self._lane("return", "--units", UNIT)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self._delegated())
        self.assertIn("another run", out)

    def test_every_session_of_a_lane_is_priced_once(self) -> None:
        """AC2, a repair's session. MUTANTS: one lane record per unit, overwritten by each run (the
        builder's 17,163 tokens read [19163]); the record's source keyed per unit rather than per
        session (the second return supersedes the first); `lane return` pricing only the latest
        session; a session's record or output deleted by the next run (one file left); a second
        return of the same sessions adding them again (four records)."""
        self._open_run()
        self.assertEqual((0, 0), (self._run("claude")[0],
                                  self._lane("return", "--units", UNIT)[0]))
        second = json.loads((FIXTURES / "claude.json").read_text("utf-8"))
        second["session_id"] = "second-session"
        for usage in (second["usage"], second["usage"]["iterations"][0]):
            usage["input_tokens"] += 2000
        second["modelUsage"]["claude-haiku-5-5"]["inputTokens"] += 2000
        _write(self.log, "second.json", json.dumps(second))
        with unittest.mock.patch.dict(os.environ,
                                      {"FAKE_OUT_CLAUDE": str(self.log / "second.json")}):
            rc, out = self._run("claude")
        self.assertEqual(0, rc, out)
        self.assertEqual("second-session", self._record()["session_id"])
        records = self._records()
        self.assertEqual(2, len(records), records)
        self.assertEqual(2, len(list(records[0].parent.glob("*.out"))))
        self.assertEqual(CLAUDE["session"],
                         json.loads(records[0].read_text("utf-8"))["session_id"])
        # the repair returned after its builder was, then both returned at once, twice over
        for fresh in (False, True, False):
            if fresh:
                _rs().update(self.root, **{_rs().DELEGATED: []})
            rc, out = self._lane("return", "--units", UNIT)
            self.assertEqual(0, rc, out)
            got = self._delegated()
            self.assertEqual([17_163, 19_163], sorted(r["tokens"] for r in got))
            self.assertEqual(sorted(map(str, records)), sorted(r["transcript"] for r in got))
        self.assertIn("19,163 tokens", out)
        self.assertIn("17,163 tokens", out)

    # -- BG1252: a session's per-model split --------------------------------------------------
    def _unit_usd(self) -> float | None:
        """The unit's dollars as the page prices them: its delegated split, by `run_state.usd`."""
        totals = _rs().unit_agent_totals(_rs().read(self.root))[UNIT]
        return _rs().usd(totals[_rs().BY_MODEL], prices.load(self.root))["usd"]

    def test_a_two_model_session_is_priced_per_model(self) -> None:
        """BG1252 AC2. The claude capture with claude-opus-5-5 beside its haiku: 1,000 input,
        2,000 output and a 500-token five-minute write, so haiku still carries the most tokens.
        MUTANTS: the lane record keeping no `by_model`, or `run_reading` carrying none, so the
        whole session is booked under haiku (US$0.0047, not US$0.0501); one model's counts booked
        under the other; the one-hour write booked as a five-minute write; the split's models
        summed into one; a split that does not sum to the session priced anyway; the
        reference still saying a session is priced at its largest model."""
        doc = json.loads((FIXTURES / "claude.json").read_text("utf-8"))
        haiku = doc["modelUsage"]["claude-haiku-5-5"]
        doc["modelUsage"]["claude-opus-5-5"] = dict(
            haiku, inputTokens=1000, outputTokens=2000, thinkingTokens=0,
            cacheReadInputTokens=0, cacheCreationInputTokens=500,
            cacheCreationEphemeral1hInputTokens=0)
        _write(self.log, "two-model.json", json.dumps(doc))
        self._open_run()
        with unittest.mock.patch.dict(os.environ,
                                      {"FAKE_OUT_CLAUDE": str(self.log / "two-model.json")}):
            rc, out = self._run("claude")
        self.assertEqual(0, rc, out)
        self.assertEqual("claude-haiku-5-5", self._record()["usage_model"])
        rc, out = self._lane("return", "--units", UNIT)
        self.assertEqual(0, rc, out)
        [got] = self._delegated()
        opus = {"input": 1000, "output": 2000, "cache_write_5m": 500, "cache_write_1h": 0,
                "cache_read": 0}
        self.assertEqual({"claude-haiku-5-5": HAIKU_PARTS, "claude-opus-5-5": opus},
                         got[_rs().BY_MODEL])
        self.assertEqual({k: HAIKU_PARTS[k] + opus[k] for k in opus}, got["components"])
        # opus at its own rate, per million: 4.00 input, 20.00 output, 5.00 five-minute write
        self.assertAlmostEqual(HAIKU_USD + (1000 * 4.00 + 2000 * 20.00 + 500 * 5.00) / 1e6,
                               self._unit_usd(), places=10)
        section = (SCRIPTS.parent / "reference-sprint.md").read_text("utf-8").split(
            "### Dollar cost {#dollar-cost}", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("most tokens", section)
        self.assertIn("each model at its own rate", " ".join(section.split()))
        # a split that does not sum to the session's own usage is refused, never priced
        [path] = self._records()
        rec = json.loads(path.read_text("utf-8"))
        rec["by_model"]["claude-opus-5-5"]["output"] += 1
        path.write_text(json.dumps(rec), "utf-8")
        _rs().update(self.root, **{_rs().DELEGATED: []})
        rc, out = self._lane("return", "--units", UNIT)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self._delegated())
        self.assertIn("does not sum to the session's usage", out)

    def test_a_record_without_a_split_prices_at_its_one_model(self) -> None:
        """BG1252 AC3. A single-model session, then the same lane record as one written before the
        split (`by_model` null, then absent), each returned in turn: every return books the
        session under its one named model at the capture's own US$0.0036. MUTANTS: a record
        without a split read as unreadable or unpriced (no delegated record, no dollars); one
        booked under no model, so the page prices none of it; the one-model fallback dropped
        from `record_delegated_tokens`."""
        self._open_run()
        rc, out = self._run("claude")
        self.assertEqual(0, rc, out)
        [path] = self._records()
        self.assertEqual({CLAUDE["model"]}, set(self._record()["by_model"]))
        for shape in ("split", "null", "absent"):
            with self.subTest(record=shape):
                rec = json.loads(path.read_text("utf-8"))
                if shape == "null":
                    rec["by_model"] = None
                elif shape == "absent":
                    rec.pop("by_model", None)
                path.write_text(json.dumps(rec), "utf-8")
                rc, out = self._lane("return", "--units", UNIT)
                self.assertEqual(0, rc, out)
                [got] = self._delegated()
                self.assertEqual({CLAUDE["model"]: HAIKU_PARTS}, got[_rs().BY_MODEL])
                self.assertAlmostEqual(HAIKU_USD, self._unit_usd(), places=10)
                self.assertIn("lane run cost: US$0.0036 (claude-haiku-5-5)", out)

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
                real = lanes._run_in_group

                def hang(cmd, *a, wt=wt, real=real, **kw):
                    if Path(cmd[0]).name == "codex":
                        _write(wt, "src/lane.py", "LANE = 1\n")
                        gitutil.git(["add", "--", "src/lane.py"], wt)
                        raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
                    return real(cmd, *a, **kw)

                hook = (unittest.mock.patch.object(lanes, "_run_in_group", side_effect=hang)
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

    # -- BG1245 -----------------------------------------------------------------------------
    def test_a_timed_out_lane_s_children_are_killed(self) -> None:
        """BG1245 AC1. MUTANTS: the CLI started in no session of its own, or no `killpg` on
        `TimeoutExpired` (the late child outlives the return and stages `src/late.py`); the
        staged set read while the group still runs (it differs from the index); no reaper for a
        signal while the lane runs (a SIGTERM to `sprint.py` leaves the late child running in
        the session it no longer shares)."""
        wt = self._worktree()
        env = {"FAKE_STAGE": str(wt / "src" / "lane.py"), "FAKE_LATE": str(wt / "src" / "late.py")}
        with unittest.mock.patch.dict(os.environ, env):
            rc, out = self._run("codex", "--worktree", str(wt), "--timeout", "2")
        self.assertEqual(1, rc, out)
        pid = int((self.log / "late.pid").read_text(encoding="utf-8"))
        self.assertFalse(_outlives(pid), "the CLI's child outlived the timeout")
        self.assertFalse((wt / "src" / "late.py").exists(), "a write landed after the return")
        rec = self._record()
        self.assertEqual(lanes.TIMED_OUT, rec["unmetered"])
        self.assertEqual(["src/lane.py"], rec["staged"])
        self.assertEqual(rec["staged"], _git(wt, "diff", "--cached", "--name-only").split())
        # a SIGTERM to `sprint.py` mid-lane kills the lane's group before it ends the command
        (self.log / "late.pid").unlink()
        wt = self._worktree("wt-signal")
        env = gitutil.git_env(FAKE_LATE=str(wt / "src" / "late.py"),
                              FAKE_SIGNAL=str(int(signal.SIGTERM)))
        done = subprocess.run(
            [sys.executable, str(SCRIPTS / "sprint.py"), "lane", "run", "--harness", "codex",
             "--units", UNIT, "--worktree", str(wt), "--timeout", "60", "--root", str(self.root)],
            env=env, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(-signal.SIGTERM, done.returncode, done.stdout + done.stderr)
        pid = int((self.log / "late.pid").read_text(encoding="utf-8"))
        self.assertFalse(_outlives(pid), "the lane's child outlived a SIGTERM to sprint.py")
        self.assertFalse((wt / "src" / "late.py").exists())

    def test_a_refused_or_repeated_lane_run_leaves_no_stale_state(self) -> None:
        """BG1245 AC2. MUTANTS: the in-flight marker taken before `lanes.run`'s refusals pass
        (the refused run leaves the unit in flight, or its span opened); the marker and span not
        taken at all once they pass (the positive controls); `_lane_worktree` always passing
        `-b` (the second run exits 2 on the branch that exists); the branch deleted and made
        again from HEAD rather than reused (the lane's own commit is gone)."""
        self._open_run()
        in_flight = lambda: [r["unit"] for r in _rs().lanes_in_flight(self.root)]  # noqa: E731
        spans = lambda: _rs().read(self.root).get(_rs().UNIT_ACTUALS) or {}  # noqa: E731
        rc, out = self._run("codex", "--worktree", "/nonexistent")
        self.assertEqual(2, rc, out)
        self.assertNotIn(UNIT, in_flight())
        self.assertNotIn(UNIT, spans())
        rc, out = self._run("codex")
        self.assertEqual(0, rc, out)
        self.assertIn(UNIT, in_flight())
        self.assertIn(UNIT, spans())
        wt = Path(self._record()["worktree"])
        self.assertEqual(f"lane-{UNIT.lower()}", _git(wt, "symbolic-ref", "--short", "HEAD"))
        _write(wt, "src/b.py", "B = 1\n")
        gitutil.git(["add", "--", "src/b.py"], wt)
        gitutil.git(["commit", "-q", "-m", "chore: the lane's own work"], wt)
        kept = _git(wt, "rev-parse", "HEAD")
        gitutil.git(["worktree", "remove", str(wt)], self.root)
        self.assertFalse(wt.exists())
        rc, out = self._run("codex")
        self.assertEqual(0, rc, out)
        self.assertEqual(str(wt), self._record()["worktree"])
        self.assertEqual(f"lane-{UNIT.lower()}", _git(wt, "symbolic-ref", "--short", "HEAD"))
        self.assertEqual(kept, _git(wt, "rev-parse", "HEAD"))

    def test_each_builder_can_write_and_a_zero_reading_is_not_priced(self) -> None:
        """BG1245 AC3. MUTANTS: codex `--sandbox workspace-write` dropped, or its `--add-dir`
        dropped or naming other than the repository's git directory (the builder cannot stage
        from a worktree); copilot `--allow-all-tools` dropped; cursor `--force` dropped (each
        CLI asks before it writes, and headless nobody answers); the `tokens <= 0` guard in
        `run_reading` replaced by `if False:` (a zero reading priced)."""
        wt = self._worktree()
        common = Path(_git(self.root, "rev-parse", "--path-format=absolute",
                           "--git-common-dir")).resolve()
        writes = {"codex": {"--sandbox": "workspace-write", "--add-dir": str(common)},
                  "copilot": {"--allow-all-tools": None}, "cursor": {"--force": None}}
        for harness, flags in writes.items():
            with self.subTest(harness=harness):
                rc, out = self._run(harness, "--worktree", str(wt))
                self.assertEqual(0, rc, out)
                argv = self._called(HARNESSES[harness][0])["argv"]
                for flag, value in flags.items():
                    self.assertIn(flag, argv)
                    if value is not None:
                        got = argv[argv.index(flag) + 1]
                        self.assertEqual(value, str(Path(got).resolve()) if flag == "--add-dir"
                                         else got)
        self._open_run()
        rc, out = self._run("claude", "--worktree", str(wt))
        self.assertEqual(0, rc, out)
        path = self._records()[-1]
        rec = json.loads(path.read_text(encoding="utf-8"))
        reading, why = lanes.run_reading(path, UNIT, rec["run_id"])
        self.assertEqual(2 + 35 + 17126, reading["tokens"], why)  # the positive control
        rec["usage"].update(input=0, output=0, cache_write=0, cache_write_1h=0, cache_read=500)
        path.write_text(json.dumps(rec), encoding="utf-8")
        reading, why = lanes.run_reading(path, UNIT, rec["run_id"])
        self.assertIsNone(reading)
        self.assertIn("no input, output or cache write", why)
        rc, out = self._lane("return", "--units", UNIT)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self._delegated())
        self.assertIn("no input, output or cache write", out)

    def test_the_unmetered_warning_names_its_session_record(self) -> None:
        """BG1245 AC4. MUTANTS: the unmetered warning naming only the unit (no session's record
        in it); the warning naming the metered session's record; the help or US1126's fragment
        naming the default worktree other than as it is created, lowercased."""
        self._open_run()
        self.assertEqual(0, self._run("claude")[0])
        with unittest.mock.patch.dict(os.environ, {"FAKE_MODE": "silent"}):
            self.assertEqual(0, self._run("claude")[0])
        metered, silent = self._records()
        rc, out = self._lane("return", "--units", UNIT)
        self.assertEqual(0, rc, out)
        [warning] = [ln for ln in out.splitlines() if ln.startswith("WARNING") and "unmetered" in ln]
        self.assertIn(str(silent), warning)
        self.assertNotIn(str(metered), warning)
        self.assertEqual([str(metered)], [r["transcript"] for r in self._delegated()])
        created = Path(self._record()["worktree"]).name
        self.assertEqual(f"lane-{UNIT.lower()}", created)
        # the fragment is collated into CHANGELOG.md, and deleted, at a release
        fragment = REPO / "changelog.d" / "US1126.md"
        for doc in (HELP, fragment if fragment.exists() else REPO / "CHANGELOG.md"):
            self.assertIn(f"`{created}`", " ".join(doc.read_text(encoding="utf-8").split()), doc)


if __name__ == "__main__":
    unittest.main()
