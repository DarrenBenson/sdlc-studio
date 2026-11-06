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
#: Each gate the `## Non-negotiable gates` section states, by the words that state it.
GATES = (
    "`/sdlc-studio reconcile --verify`",
    "`/sdlc-studio review`",
    "PRD - TRD - TSD - Persona - CODE",
    "files a `bug`",
    "Review is independent of the author",
    "`critic.py record`",
    "`sprint sign`",
    "Commit each unit to `main` when its gate passes and push `main`",
    "No ad-hoc coding",
    "engagement_floor: judgement",
)
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
        """AC1. MUTANTS: CAP raised above 5,000; the template grown past it; any gate in GATES
        cut from `## Non-negotiable gates`; the doctrine pointer dropped, or pointing at a
        section the doctrine lacks or that does not hold the moved habits."""
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertLessEqual(CAP, 5_000)
        self.assertLessEqual(len(text), CAP, f"the template is {len(text):,} chars")
        self.assertIn("\n## Operating doctrine\n", text)
        gates = _section(text, "## Non-negotiable gates")
        for gate in GATES:
            self.assertIn(gate, gates, f"the gate list dropped: {gate}")
        # The pointer names the page and its section in prose: a `<skill>/...md#anchor` code span
        # reads as an unresolvable link to the links lane, and a consuming project has no relative path.
        flat = re.sub(r"\s+", " ", text)
        self.assertIn("Working habits section of `<skill>/reference-doctrine.md`", flat)
        # BG0280 put the shared-temp-path rule in the template; BG1258 pins that it stays there.
        self.assertIn("Share a temp path: name it per agent or run, or keep it in your worktree.", flat)
        habits = re.sub(r"\s+", " ", _section(DOCTRINE.read_text(encoding="utf-8"),
                                              "## Working habits {#working-habits}"))
        for moved in MOVED:
            self.assertIn(moved, habits, f"the doctrine does not hold the moved: {moved}")

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
