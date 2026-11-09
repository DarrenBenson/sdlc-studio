"""US1130: the shipped agent-instructions template is every consuming project's always-loaded
AGENTS.md, so its size is paid on every call of every session. It is held to 5,000 characters
and keeps its gates; the text it sheds lives in `reference-doctrine.md#working-habits`.

`reference-sprint.md#cost-anatomy` recommends, and never claims to enforce, a project
`.claude/settings.json` that switches off what a delivery session does not use.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/agent-instructions.md
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
TEMPLATE = SKILL / "templates" / "agent-instructions.md"
DOCTRINE = SKILL / "reference-doctrine.md"
SPRINT_REF = SKILL / "reference-sprint.md"
sys.path.insert(0, str(SCRIPTS))

import init  # noqa: E402

#: The ceiling, in characters, of the whole template file as shipped (10,892 before US1130).
CAP = 5_000
#: Each gate the `## Non-negotiable gates` section states, by its whole rule sentence rather than
#: its heading or opt-out alone, so a gate whose rule is cut or reworded while its heading stays
#: fails here (qa-seat-US1130-r1 round 1). Matched with runs of whitespace folded to one space.
GATES = (
    "**Never release until the full pre-release gate is green.** In order, before any tag:",
    "`/sdlc-studio reconcile --verify` runs every story's `Verify:` expression and fails on any "
    "`no` or `stale`.",
    "`/sdlc-studio review` runs all five legs, **PRD - TRD - TSD - Persona - CODE**",
    "The CODE leg is not optional.",
    "Fix the findings before tagging. Even a production hotfix files a `bug`",
    "**Review is independent of the author.** One independent reviewer, a fresh context that did "
    "not write the change, records each unit's verdict with `critic.py record`, and its APPROVE "
    "decides the unit.",
    "The run is signed once, with `sprint sign`, by its reviewer of record",
    "never a unit's author or reviewer.",
    "Commit each unit to `main` when its gate passes and push `main`; open no PR and push no "
    "branch unless `release_strategy` is `pr-required`.",
    "**No ad-hoc coding.** Every change flows CR / RFC -> Epic -> Story -> code plan -> code "
    "implement -> code verify -> reconcile -> review.",
    "Default to TDD: write the `Verify:` expression or the failing test first.",
    "A change to more than one source file names every existing requirement it interacts with, "
    "and how each is resolved, and writes one acceptance criterion per interaction before any "
    "code.",
    "Opt out with `engagement_floor: judgement`",
)
#: BG0280's shared-temp-path rule, which the template keeps as one line in its `## Don't` list.
TEMP_RULE = "Share a temp path: name it per agent or run, or keep it in your worktree."
#: The habits the template moved out, each stated in the doctrine section it points at.
MOVED = ("canonical status summary", "Verify: manual", "pre-wired scaffolds", "Foundation first",
         "namespace it per agent or per run", "version_check.enabled: false")


def _section(text: str, heading: str) -> str:
    start = text.index(heading)
    level = heading.split(" ", 1)[0]
    nxt = re.search(rf"^#{{1,{len(level)}}} ", text[start + len(heading):], re.M)
    return text[start:start + len(heading) + nxt.start()] if nxt else text[start:]


class AgentInstructionsBudgetTests(unittest.TestCase):

    def test_the_template_fits_and_keeps_its_gates(self) -> None:
        """AC1. MUTANTS: CAP raised above 5,000; the template grown past it; any gate's rule
        sentence in GATES cut or reworded (the engagement floor's rule with its opt-out kept, the
        CR / RFC -> Epic -> Story flow, "not optional" made "optional"); the doctrine pointer
        dropped, or pointing at a section the doctrine lacks or that does not hold the moved
        habits; the temp-path rule deleted, moved into the leading comment, or listed as shed
        by the pointer; the doctrine intro saying the starter carries none of the habits, or
        naming an item that is not the temp-file habit (BG1258)."""
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertLessEqual(CAP, 5_000)
        self.assertLessEqual(len(text), CAP, f"the template is {len(text):,} chars")
        self.assertIn("\n## Operating doctrine\n", text)
        gates = re.sub(r"\s+", " ", _section(text, "## Non-negotiable gates"))
        for gate in GATES:
            self.assertIn(gate, gates, f"the gate list dropped: {gate}")
        # The pointer names the page and its section in prose: a `<skill>/...md#anchor` code span
        # reads as an unresolvable link to the links lane, and a consuming project has no relative path.
        flat = re.sub(r"\s+", " ", text)
        self.assertIn("Working habits section of `<skill>/reference-doctrine.md`", flat)
        # BG0280 put the shared-temp-path rule in the template; it stays in the `## Don't` list,
        # not the leading comment init strips, and the pointer does not list it among the shed.
        self.assertIn(TEMP_RULE, re.sub(r"\s+", " ", _section(text, "## Don't")))
        shed = re.search(r"The other habits \(([^)]*)\) are in the Working habits section", flat)
        self.assertIsNotNone(shed, "the pointer no longer names the habits it sheds")
        self.assertNotIn("temp", shed.group(1).lower(), "the pointer lists the kept temp rule as shed")
        habits = re.sub(r"\s+", " ", _section(DOCTRINE.read_text(encoding="utf-8"),
                                              "## Working habits {#working-habits}"))
        for moved in MOVED:
            self.assertIn(moved, habits, f"the doctrine does not hold the moved: {moved}")
        # The doctrine's intro names the one habit the starter keeps, by an item that is that habit.
        intro = habits.split(" 1. ", 1)[0]
        self.assertNotIn("rather than carries", intro)
        kept = re.search(r"it keeps item (\d+) as one line", intro)
        self.assertIsNotNone(kept, intro)
        item = re.search(rf" {kept.group(1)}\. (.*?)(?: {int(kept.group(1)) + 1}\. |$)", habits)
        self.assertIsNotNone(item, f"the doctrine has no item {kept.group(1)}")
        self.assertIn("namespace it per agent or per run", item.group(1))

    def test_an_initialised_project_s_agents_md_still_validates(self) -> None:
        """AC2. MUTANTS: the trunk rule split over two lines or stripped of its commit clause or
        its `pr-required` opt-in; the doctrine heading cut; a hygiene marker (LATEST.md, the
        compaction rule, `reconcile --verify`) cut, which `validate instructions` reports."""
        text = TEMPLATE.read_text(encoding="utf-8")
        doctrine = re.sub(r"\s+", " ", _section(text, "## Operating doctrine"))
        for words in ("<skill>/reference-doctrine.md", "Read `sdlc-studio/reviews/LATEST.md`",
                      "after any context compaction or reset", "`/sdlc-studio status`"):
            self.assertIn(words, doctrine)  # validate's markers also match these words elsewhere
        trunk = [ln for ln in text.splitlines() if "open no PR and push no branch" in ln]
        self.assertEqual(1, len(trunk), trunk)
        for words in ("Commit each unit to `main` when its gate passes", "push `main`",
                      "unless `release_strategy` is `pr-required`"):
            self.assertIn(words, trunk[0])
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "acme"
            repo.mkdir()
            init.init(repo)
            agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("\n## Operating doctrine\n", agents)
            self.assertIn(trunk[0], agents.splitlines())
            self.assertIn(TEMP_RULE, re.sub(r"\s+", " ", agents))  # BG0280: the agent's own brief
            env = dict(os.environ, HOME=d, XDG_DATA_HOME=d)
            run = subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), "instructions",
                                  "--root", str(repo), "--format", "json"],
                                 capture_output=True, text=True, env=env, timeout=60, check=False)
            self.assertEqual(0, run.returncode, run.stdout + run.stderr)
            summary = json.loads(run.stdout)["summary"]
            self.assertEqual({"errors": 0, "warnings": 0, "info": 0}, summary,
                             json.loads(run.stdout)["violations"])

    def test_reference_sprint_recommends_the_settings_file(self) -> None:
        """AC3. MUTANTS: the recommendation cut; stated as enforced; the claude.ai caveat cut."""
        sec = _section(SPRINT_REF.read_text(encoding="utf-8"), "### Cost anatomy {#cost-anatomy}")
        flat = re.sub(r"\s+", " ", sec)
        named = [s for s in re.split(r"(?<=[.;])\s+", flat) if ".claude/settings.json" in s]
        self.assertTrue(named, "the settings file is not named")
        joined = " ".join(named)
        for words in ("disables the plugins and connectors", "a delivery session does not use",
                      "recommended"):
            self.assertIn(words, joined)
        for s in named:
            self.assertNotRegex(s, r"(?<!not )\benforced\b|\benforces\b|\bis applied\b", s)
        self.assertRegex(flat, r"claude\.ai connector[^.]* may not be switchable per project")


if __name__ == "__main__":
    unittest.main()
