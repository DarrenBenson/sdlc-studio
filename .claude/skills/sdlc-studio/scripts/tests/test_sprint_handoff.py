"""US1141: `sprint.py handoff` writes the bounded resume brief and `sprint.py resume` reaches its
next action in a fresh process.

Each fixture is a throwaway workspace holding only what `lib/resume_brief.py` reads: the run
state and the sprint plan under `sdlc-studio/.local/`, the QA brief `sprint lane land` writes
there, and the batch's artefacts. The handoff and the resume run as separate processes through
the shipped entry point, so nothing a process holds can carry the next action between them.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py -q
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import docgen  # noqa: E402
import sprint  # noqa: E402
from lib import resume_brief, run_state  # noqa: E402

RUN = "RUN-01TESTRUN"
STARTED = "2026-01-01T00:00:00Z"
BRIEF_REL = Path("sdlc-studio") / ".local" / "resume-brief.md"


def _env(home: str) -> dict:
    """The child's environment with every home and harness store under a temp directory."""
    env = dict(os.environ)
    for key in ("HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME",
                "COPILOT_HOME"):
        env[key] = home
    env["OPENCODE_DB"] = str(Path(home) / "opencode.db")
    return env


class Workspace:
    """An open run of two units in two waves, US0001 briefed and in flight."""

    def __init__(self, tmp: str):
        self.root = Path(tmp) / "ws"
        self.home = Path(tmp) / "home"
        self.home.mkdir(parents=True)
        self.local = self.root / "sdlc-studio" / ".local"
        self.local.mkdir(parents=True)
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid in ("US0001", "US0002"):
            (stories / f"{uid}-fixture.md").write_text(
                f"# {uid}: Fixture unit {uid}\n\n> **Status:** Ready\n", encoding="utf-8")
        (self.local / "sprint-plan.json").write_text(
            json.dumps({"waves": [["US0001"], ["US0002"]]}), encoding="utf-8")
        self.state = {"schema": 1, "run_id": RUN, "outcome": "running", "goal": "done",
                      "batch": ["US0001", "US0002"], "sprint_goal": "Resume at one action",
                      "rulings": [], "plan": "sdlc-studio/.local/sprint-plan.json",
                      "lanes_in_flight": [{"unit": "US0001", "started_at": STARTED}]}
        self.save()

    @property
    def brief(self) -> Path:
        return self.root / BRIEF_REL

    def save(self) -> None:
        (self.local / "run-state.json").write_text(json.dumps(self.state), encoding="utf-8")

    def land(self, uid: str) -> None:
        """What `sprint lane land` writes: the unit's QA brief, after the lane's `started_at`."""
        path = self.local / "briefs" / f"{uid}-qa.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"QA brief for {uid}\n", encoding="utf-8")

    def run(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / "sprint.py"), *argv,
                               "--root", str(self.root)], capture_output=True, text=True,
                              env=_env(str(self.home)), timeout=120)


def _action(out: str, prefix: str) -> str:
    """The text after the first line of `out` that opens with `prefix`, or ''."""
    for line in out.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].split(": ", 1)[1]
    return ""


class HandoffCliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_handoff_writes_the_bounded_brief_and_refuses_without_a_run_or_over_budget(self):
        ws = Workspace(self._tmp.name)
        # no open run: refused by name, nothing written
        (ws.local / "run-state.json").unlink()
        r = ws.run("handoff")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("no open run", r.stderr)
        self.assertFalse(ws.brief.exists(), "a brief was written with no open run")
        ws.state["outcome"] = "goal-reached"   # a closed run is not an open one either
        ws.save()
        r = ws.run("handoff")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertFalse(ws.brief.exists(), "a brief was written over a closed run")

        ws.state["outcome"] = "running"
        ws.save()
        before = (ws.local / "run-state.json").read_bytes()
        r = ws.run("handoff", "--agent", "US0001=agent-7f3", "--issue", "the meter reads low",
                   "--issue", "a second known issue")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(ws.brief.is_file(), r.stdout)
        text = ws.brief.read_text(encoding="utf-8")
        self.assertEqual(resume_brief.parse(text)["agents"], {"US0001": "agent-7f3"})
        self.assertIn("- the meter reads low", text)
        self.assertIn("- a second known issue", text)
        self.assertIn(str(ws.brief), r.stdout)
        estimate = resume_brief.estimate_tokens(text)
        self.assertIn(f"an estimated {estimate:,} tokens of the 8,000 budget", r.stdout)
        step = resume_brief.next_action(ws.root)
        self.assertEqual(_action(r.stdout, "handoff: next action"), step.text)
        self.assertEqual(step.rung, 1, "the fixture's in-flight lane is the first rung")
        # the surface US0978 retired stays retired: no HO file, no `handoff` key, no state write
        self.assertFalse((ws.root / "sdlc-studio" / "handoffs").exists())
        self.assertNotIn("handoff", run_state.read(ws.root))
        self.assertEqual((ws.local / "run-state.json").read_bytes(), before)

        # an --agent value without `=`, or with an empty half, is refused and writes nothing
        written = ws.brief.read_bytes()
        for bad in ("US0001", "US0001agent-7f3", "=agent-7f3", "US0001="):
            ws.brief.unlink(missing_ok=True)
            r = ws.run("handoff", "--agent", bad)
            self.assertEqual(r.returncode, 2, f"{bad!r}: {r.stdout}{r.stderr}")
            self.assertIn("--agent", r.stderr)
            self.assertIn(bad, r.stderr)
            self.assertFalse(ws.brief.exists(), f"--agent {bad!r} was accepted")
        ws.brief.write_bytes(written)

        # over budget: refused naming the estimate and the budget, the brief on disk untouched
        r = ws.run("handoff", "--issue", "x" * 33_000)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("over the budget of 8,000", r.stderr)
        self.assertEqual(ws.brief.read_bytes(), written, "an over-budget brief was written")
        self.assertNotIn("handoff: wrote", r.stdout)


class ResumeCliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_resume_in_a_fresh_process_reaches_the_handoffs_next_action_and_names_drift(self):
        ws = Workspace(self._tmp.name)
        # no brief on disk: refused, pointing at the handoff
        r = ws.run("resume")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("sprint.py handoff", r.stderr)

        handed = ws.run("handoff")
        self.assertEqual(handed.returncode, 0, handed.stdout + handed.stderr)
        recorded = _action(handed.stdout, "handoff: next action")
        self.assertIn("await the in-flight lane: US0001", recorded)
        text = ws.brief.read_text(encoding="utf-8")

        # an unchanged tree: the brief, then the handoff's own next action, and nothing stale
        r = ws.run("resume")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(text, r.stdout)
        self.assertEqual(_action(r.stdout, "resume: next action"), recorded)
        self.assertNotIn("stale", r.stdout)

        # the tree moved (US0001 landed): the action the tree yields now, the brief's named stale
        ws.land("US0001")
        now = resume_brief.next_action(ws.root)
        self.assertEqual((now.rung, now.kind), (2, "review"))
        r = ws.run("resume")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(_action(r.stdout, "resume: next action"), now.text)
        self.assertEqual(_action(r.stdout, "resume: stale"), recorded)
        current = [ln for ln in r.stdout.splitlines() if ln.startswith("resume: next action")]
        self.assertEqual(len(current), 1, r.stdout)
        self.assertNotIn(recorded, current[0], "the stale action was printed as current")

        # a brief naming another run is refused, and none of it is printed
        ws.brief.write_text(text.replace(RUN, "RUN-01ELSEWHERE"), encoding="utf-8")
        r = ws.run("resume")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("RUN-01ELSEWHERE", r.stderr)
        self.assertIn(RUN, r.stderr)
        self.assertNotIn("Resume brief", r.stdout)
        # ...as is a brief over a tree with no open run, and a file that is no brief
        ws.brief.write_text(text, encoding="utf-8")
        ws.state["outcome"] = "goal-reached"
        ws.save()
        r = ws.run("resume")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn(f"the brief names {RUN} and there is no open run", r.stderr)
        ws.state["outcome"] = "running"
        ws.save()
        ws.brief.write_text("not a brief\n", encoding="utf-8")
        r = ws.run("resume")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)


def _capture(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            rc = sprint.main(argv)
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, buf.getvalue()


def _plannable(root: Path) -> None:
    """Two groomed Open bugs in a workspace whose every artefact folder holds an index."""
    for sub in ("bugs", "stories", "epics", "change-requests", "retros", "reviews", "rfcs"):
        (root / "sdlc-studio" / sub).mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / sub / "_index.md").write_text(
            "# Index\n\n| ID | Title | Status |\n| --- | --- | --- |\n", encoding="utf-8")
    rows = []
    for num in (1, 2):
        (root / "src").mkdir(exist_ok=True)
        (root / "src" / f"bg{num:04d}.py").write_text("", encoding="utf-8")
        (root / "sdlc-studio" / "bugs" / f"BG{num:04d}-x.md").write_text(
            f"# BG{num:04d}: b{num}\n\n> **Status:** Open\n> **Severity:** Medium\n"
            f"> **Affects:** src/bg{num:04d}.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
            f"### AC1: it behaves as recorded\n\n- **Given** the recorded state\n"
            f"- **Verify:** shell true\n", encoding="utf-8")
        rows.append(f"| [BG{num:04d}](BG{num:04d}-x.md) | b{num} | Open |\n")
    idx = root / "sdlc-studio" / "bugs" / "_index.md"
    idx.write_text(idx.read_text(encoding="utf-8") + "".join(rows), encoding="utf-8")


class PlanNextStepTests(unittest.TestCase):
    def test_plan_write_names_a_fresh_session_as_its_next_step(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "ws"
            _plannable(root)
            old = os.environ.get("HOME")
            os.environ["HOME"] = d
            self.addCleanup(lambda: os.environ.__setitem__("HOME", old) if old is not None
                            else os.environ.pop("HOME", None))
            argv = ["plan", "--bugs", "Open", "--no-fetch", "--root", str(root),
                    "--sprint-goal", "ship the fixture batch"]
            rc, out = _capture(argv)
            self.assertEqual(rc, 0, out)
            self.assertFalse(run_state.read(root).get("run_id"), "the preview opened a run")
            self.assertNotIn("sprint.py handoff", out)
            self.assertNotIn("sprint.py resume", out)

            rc, out = _capture([*argv, "--write"])
            self.assertEqual(rc, 0, out)
            self.assertTrue(run_state.read(root).get("run_id"), out)
            last = [ln for ln in out.splitlines() if ln.strip()][-1]
            self.assertRegex(last, r"sprint\.py handoff.*then.*wave 1.*fresh session.*"
                                   r"sprint\.py resume")


def _invocations(page: str, verb: str) -> list[str]:
    """Each fenced-block line of `page` that invokes `sprint.py <verb>`."""
    out, fenced = [], False
    for line in page.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif fenced and re.match(rf"python3 <skill>/scripts/sprint\.py {verb}\b", line.strip()):
            out.append(line.strip())
    return out


class HelpTests(unittest.TestCase):
    def test_help_and_the_command_surface_list_handoff_and_resume(self):
        page = (SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        for verb, func in (("handoff", sprint.cmd_handoff), ("resume", sprint.cmd_resume)):
            lines = _invocations(page, verb)
            self.assertTrue(lines, f"help/sprint.md shows no fenced `sprint.py {verb}`")
            for line in lines:
                argv = [re.sub(r"<[^>]+>", "x", tok) for tok in shlex.split(line)[2:]]
                buf = io.StringIO()
                with contextlib.redirect_stderr(buf):
                    try:
                        args = sprint.build_parser().parse_args(argv)
                    except SystemExit:
                        self.fail(f"the parser refuses the documented `{line}`: {buf.getvalue()}")
                self.assertIs(args.func, func, line)
            rows = {inv for inv, _note in docgen.surface_rows()}
            self.assertIn(f"sprint.py {verb}", rows)
            surface = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
            self.assertIn(f"| `sprint.py {verb}` |", surface,
                          "reference-scripts-surface.md was not regenerated")


if __name__ == "__main__":
    unittest.main()
