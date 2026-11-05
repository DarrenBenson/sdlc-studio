"""US1120: the lane brief leaves the commit to `sprint lane land` and holds the builder to a
call budget with a hand-off note in place of a growing context.

The brief's closing commands stage exactly the unit's Affects, name the hand-in files (the commit
message, the unit's claims and mutants) and stop; nothing in the brief tells the builder to
commit or to record its own self-check. Each brief states a tool-call budget formed from the one
per-point constant, and the hand-off note a builder writes at the budget. The prompt template
says when a repair resumes its builder and when it starts a fresh one from that note.

The brief tests drive `sprint.py lane brief` in-process against a throwaway project with an open
run; the template test reads THIS repository's shipped reference, as the criterion names it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
sprint = loader.load_script("sprint")
from lib import run_state, sdlc_md  # noqa: E402

# parents: [0] tests [1] scripts [2] the shipped skill.
SKILL = Path(__file__).resolve().parents[2]
TEMPLATE = SKILL / "reference-agent-prompt-template.md"
SPRINT = SKILL / "scripts" / "sprint.py"
BATCH = ("US0101", "US0102")
POINTS = {"US0101": 1, "US0102": 5}
AFFECTS = {"US0101": "src/other.py, tests/test_other.py, changelog.d/US0101.md",
           "US0102": "src/app.py, tests/test_app.py, changelog.d/US0102.md"}
HAND_IN = "sdlc-studio/.local/lane"


def _live(name: str):
    """The module the command resolves at call time; another test module may re-register it."""
    return sys.modules.get(name) or importlib.import_module(name)


def _project(d: str) -> Path:
    """Two Ready stories of 1 and 5 points and an open run whose batch holds both."""
    root = Path(d) / "repo"
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    for uid in BATCH:
        (stories / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** {AFFECTS[uid]}\n"
            f"> **Points:** {POINTS[uid]}\n\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
            "- **Verify:** file src/app.py\n", encoding="utf-8")
    run_state.open_run(root, batch=list(BATCH), goal="g")
    return root


def _brief(root: Path, uid: str, *extra: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main(["lane", "brief", "--units", uid, "--root", str(root), *extra])
    if rc != 0:
        raise AssertionError(f"lane brief refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _budget(out: str) -> int:
    found = re.findall(r"Budget: (\d+) tool calls", out)
    if len(found) != 1:
        raise AssertionError(f"expected one stated budget, found {found}:\n{out}")
    return int(found[0])


class LaneBriefBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        transcripts = Path(self._tmp.name) / "transcripts"
        transcripts.mkdir()
        env = unittest.mock.patch.dict(os.environ,
                                       {run_state.TRANSCRIPTS_ENV: str(transcripts)})
        env.start()
        self.addCleanup(env.stop)
        self.root = _project(self._tmp.name)

    def test_the_brief_hands_the_commit_to_lane_land(self) -> None:
        """AC1. MUTANTS: the closing step still printing `git commit`; critic's record line
        passed through verbatim, so the builder records its own self-check; the claims or
        mutants file named for the batch's first unit (US0101); `commit-msg.txt` or the hand-in
        path dropped; `sprint lane land` not named; the stage command sweeping (`git add -A`)
        or gone; the JSON dispatch keeping the record line the text drops."""
        out = _brief(self.root, "US0102")
        self.assertNotIn("git commit", out)
        self.assertNotIn("self-check record", out)
        for name in ("US0102-claims.json", "US0102-mutants.json", "commit-msg.txt"):
            self.assertIn(f"{HAND_IN}/{name}", out, name)
        self.assertNotIn("US0101-claims.json", out)
        self.assertNotIn("US0101-mutants.json", out)
        lines = out.splitlines()
        adds = [i for i, ln in enumerate(lines) if ln.strip().startswith("git add")]
        self.assertEqual(1, len(adds), out)
        self.assertEqual(["git", "add", "--", *sdlc_md.affects_files(
            f"> **Affects:** {AFFECTS['US0102']}\n")], shlex.split(lines[adds[0]]))
        # Both the stage step and the stop name lane land as what commits.
        self.assertIn("sprint lane land", lines[adds[0] - 1])
        stops = [ln for ln in lines if re.search(r"(?i)do not commit", ln)]
        self.assertEqual(1, len(stops), out)
        self.assertIn("sprint lane land", stops[0])
        for sweep in ("git add -A", "git add .", "git add --all"):
            self.assertNotIn(sweep, out)
        # The self-check stays critic's own text, but for the hand-in rewrite of its record step.
        real = critic.author_self_check(self.root, "US0102")
        self.assertIn("self-check record", real, "premise: critic says it")
        kept = [ln for ln in _live("sprint")._hand_in_self_check(real, "US0102").splitlines()
                if "do not record them yourself" not in ln]
        at = 0
        for ln in kept:
            at = out.index(ln, at) + len(ln)
        dispatch = json.loads(_brief(self.root, "US0102", "--format", "json"))
        self.assertNotIn("self-check record", dispatch["briefs"][0]["self_check"])

    def test_the_budget_scales_with_points_and_names_the_hand_off(self) -> None:
        """AC2. MUTANTS: a budget figure hard-coded rather than read from the per-point
        constant; the points ignored, so a 1- and a 5-point lane get one budget; the points read
        from another unit; the hand-off note's path, or what is done, the criteria left or the
        next step, dropped from the rule; the rule stopping without saying to return."""
        live = _live("sprint")  # the module `_brief` runs, so the patch below reaches the brief
        fixed, per = live.LANE_CALLS_FIXED, live.LANE_CALLS_PER_POINT
        small, large = _brief(self.root, "US0101"), _brief(self.root, "US0102")
        self.assertEqual(fixed + 1 * per, _budget(small))
        self.assertEqual(fixed + 5 * per, _budget(large))
        self.assertEqual(4 * per, _budget(large) - _budget(small), "the per-point share")
        with unittest.mock.patch.object(live, "LANE_CALLS_PER_POINT", per + 7):
            self.assertEqual(fixed + 1 * (per + 7), _budget(_brief(self.root, "US0101")))
            self.assertEqual(fixed + 5 * (per + 7), _budget(_brief(self.root, "US0102")))
        for out in (small, large):
            rule = next(ln for ln in out.splitlines() if "Budget:" in ln)
            for part in (f"{HAND_IN}/HANDOFF.md", "what is done", "the criteria left",
                         "the next step", "return"):
                self.assertIn(part, rule, part)

    def test_the_prompt_template_names_the_fresh_builder_rule(self) -> None:
        """AC3. MUTANTS: the rule deleted; the context size dropped, so "only below a stated
        size" states none; the fresh builder no longer started from the hand-off note; the
        rule naming a repair but not a second build."""
        text = TEMPLATE.read_text(encoding="utf-8")
        paras = [p for p in re.split(r"\n\s*\n", text) if "fresh builder" in p]
        self.assertEqual(1, len(paras), "one paragraph states the rule")
        rule = " ".join(paras[0].split())
        self.assertRegex(rule, r"(?i)\brepair\b")
        self.assertRegex(rule, r"(?i)second build")
        self.assertRegex(rule, r"(?i)resumes? (its|the) builder only (while [^.]*?)?below \d+k")
        self.assertNotRegex(rule, r"(?i)\b(above|exceeds|over) \d+k")
        self.assertRegex(rule, r"(?i)otherwise[^.]*fresh builder[^.]*hand-off note")


    def test_the_self_check_section_hands_in_rather_than_records(self) -> None:
        """MUTANTS: the hand-in rewrite leaves critic's "Record both" step, or the CLAIMS.json and
        MUTANTS.json placeholders, so the section tells the builder to record what it must only
        hand in; `lane --help` still says the brief carries the record and commit commands."""
        out = _brief(self.root, "US0101")
        section = out[out.index("AUTHOR SELF-CHECK"):out.index("Then, for US0101")]
        self.assertNotIn("Record both", section)
        self.assertNotIn("CLAIMS.json", section)
        self.assertNotIn("MUTANTS.json", section)
        self.assertIn("US0101-claims.json", section)
        self.assertIn("US0101-mutants.json", section)
        lane_help = subprocess.run([sys.executable, str(SPRINT), "lane", "--help"],
                                   capture_output=True, text=True, check=False).stdout
        self.assertNotIn("record the self-check and commit it", " ".join(lane_help.split()))

if __name__ == "__main__":
    unittest.main()
