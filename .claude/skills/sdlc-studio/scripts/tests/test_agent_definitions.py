"""The lean subagent definitions a builder or reviewer is spawned as (US1131).

`AgentDefinitionTests` pins the definitions themselves: the restricted tool line, the hand-back
contract they and the amigo seats' review renders carry, and this repository's copies matching
the templates a consuming project receives (AC1, AC3 and AC4; AC2 lives in test_init.py). A class
added here for the spawn sites keeps these three tests as they stand; DEFINITIONS and the helpers
below are shared for that purpose.

`SpawnSiteTests` pins where they are spawned (US1132): every spawn site the references name, the
wave that launches its first agent alone, and the builder traps the lane brief's lessons carry.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md
# test-census-subject: .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md
# test-census-subject: .claude/skills/sdlc-studio/reference-epic.md
# test-census-subject: .claude/skills/sdlc-studio/reference-agent-prompt-template.md
# test-census-subject: .claude/skills/sdlc-studio/reference-sprint.md
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
REPO = SKILL.parents[2]
TEMPLATES = SKILL / "templates" / "agents"
DEFINITIONS = ("sdlc-builder.md", "sdlc-reviewer.md")
SEATS = ("engineering", "product", "qa")
# Exactly the tools run six's 1,432 builder and reviewer calls used: Write because reviewers write
# verdict files, Monitor because lanes wait on long commands. Anything more re-grows the start.
TOOLS = ["Bash", "Read", "Edit", "Write", "Monitor"]
FORBIDDEN = re.compile(r"^(Skill|Agent|Task|WebFetch|WebSearch|mcp__.*)$")
# The hand-back contract, one pattern per clause, matched over whitespace-joined text.
CONTRACT = {
    "foreground": re.compile(r"run every command in the foreground, or wait for it", re.I),
    "three lines": re.compile(r"hand back in at most three lines: the unit, the outcome\b"
                              r"[^.]*, the hand-in path", re.I),
    "no progress": re.compile(r"no progress message unless (you are )?blocked", re.I),
}


def frontmatter(text: str) -> dict[str, str]:
    """The `key: value` lines between a definition's opening `---` fences, or {} with none."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    return dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)


def section(text: str, heading: str) -> str | None:
    """The body under the first `## <heading>...` line, up to the next `## ` heading, with its
    wrapped lines joined; None when no such heading exists."""
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return " ".join(m.group(1).split()) if m else None


class AgentDefinitionTests(unittest.TestCase):

    def _read(self, name: str) -> str:
        path = TEMPLATES / name
        self.assertTrue(path.is_file(), f"{path} is not shipped")
        return path.read_text(encoding="utf-8")

    def test_each_definition_restricts_its_tools(self) -> None:
        """AC1. MUTANTS: the `tools` line deleted (Claude Code then grants every tool); Write or
        Monitor dropped; Skill, Agent or an MCP tool added; the name not the file's stem."""
        for name in DEFINITIONS:
            with self.subTest(definition=name):
                meta = frontmatter(self._read(name))
                self.assertEqual(Path(name).stem, meta.get("name", "").strip())
                self.assertTrue(meta.get("description", "").strip(), "no description")
                self.assertIn("tools", meta, "no tools line - the definition would grant every tool")
                tools = [t.strip() for t in meta["tools"].split(",")]
                self.assertEqual(sorted(TOOLS), sorted(tools))
                self.assertEqual([], [t for t in tools if FORBIDDEN.match(t)])

    def test_the_hand_back_contract_is_carried(self) -> None:
        """AC3. MUTANTS: any one clause deleted from either definition or any one seat; a seat's
        contract placed outside its review render."""
        sources = [(name, self._read(name), "Hand-back") for name in DEFINITIONS]
        for seat in SEATS:
            card = SKILL / "templates" / "personas" / "amigos" / f"{seat}.md"
            sources.append((f"{seat} seat", card.read_text(encoding="utf-8"),
                            "Hand-back *(review render)*"))
        for label, text, heading in sources:
            with self.subTest(source=label):
                body = section(text, heading)
                self.assertIsNotNone(body, f"{label} has no '## {heading}' section")
                for clause, pattern in CONTRACT.items():
                    self.assertRegex(body, pattern, f"{label} omits the {clause} clause")

    def test_this_repository_s_copies_match_the_templates(self) -> None:
        """AC4. MUTANT: a hand edit to this repository's `.claude/agents/` copy, or a copy missing."""
        shipped = sorted(p.name for p in TEMPLATES.glob("*.md"))
        self.assertEqual(sorted(DEFINITIONS), shipped)
        for name in shipped:
            with self.subTest(definition=name):
                ours = REPO / ".claude" / "agents" / name
                self.assertTrue(ours.is_file(), f"{ours} is missing")
                self.assertEqual((TEMPLATES / name).read_bytes(), ours.read_bytes(),
                                 f"{ours} has drifted from the shipped template")


# US1132: the references that spawn a builder or reviewer, each with the passage that does it, from
# its opening marker to the marker after it. reference-sprint.md's wave step is its Build step.
SPAWN_SITES = {
    "reference-epic.md wave example": ("reference-epic.md", r"c\. \*\*Execute Stories in Parallel",
                                       r"d\. \*\*Wait for All Stories"),
    "reference-agent-prompt-template.md": ("reference-agent-prompt-template.md",
                                           r"\*\*Spawning a lane\.\*\*", r"\n\n"),
    "reference-sprint.md Build step": ("reference-sprint.md", r"^2\. \*\*Build\.\*\*",
                                       r"^3\. \*\*Review\.\*\*"),
    "reference-sprint.md Review step": ("reference-sprint.md", r"^3\. \*\*Review\.\*\*",
                                        r"^4\. \*\*Close\.\*\*"),
}
#: the definition each site must spawn
SPAWNS = {"reference-epic.md wave example": ("sdlc-builder",),
          "reference-agent-prompt-template.md": ("sdlc-builder", "sdlc-reviewer"),
          "reference-sprint.md Build step": ("sdlc-builder",),
          "reference-sprint.md Review step": ("sdlc-reviewer",)}
LEAN = {"sdlc-builder", "sdlc-reviewer"}
SUBAGENT_TYPE = re.compile(r'subagent_type="([^"]+)"')
FALLBACK = re.compile(r"`general-purpose`[^.]*\b(fallback|no agent config)\b", re.I)
#: the durable builder traps (run six's builder brief, run seven's builder notes), each by a
#: phrase its rule carries; the lane brief's lessons block must carry every one.
BUILDER_TRAPS = {
    "a test not importing its subject names it": re.compile(r"test-census-subject"),
    "a changed CLI regenerates the surface": re.compile(r"docgen\.py surface"),
    "a new sprint verb is in its help": re.compile(r"help/sprint\.md"),
    "a test's git call is confined": re.compile(r"gitutil\.git_env\(\)"),
    "a scrubbing script registers": re.compile(r"SCRUB_SITES"),
    "a reference at its ceiling cuts a line": re.compile(r"line (budget|ceiling)", re.I),
    "a fragment opens with its section": re.compile(r"<!-- section:"),
    "self-check rulings are bare": re.compile(r"TRUE, FALSE or UNVERIFIABLE"),
    "tests never touch a real harness store": re.compile(r"harness store", re.I),
}


def passage(name: str, start: str, end: str) -> str:
    """The text of reference `name` from the first `start` match up to the next `end` match, or
    "" when either is missing."""
    text = (SKILL / name).read_text(encoding="utf-8")
    m = re.search(rf"({start}.*?)(?={end})", text, re.M | re.S)
    return m.group(1) if m else ""


class SpawnSiteTests(unittest.TestCase):

    def _sites(self) -> dict[str, str]:
        got = {label: passage(*spec) for label, spec in SPAWN_SITES.items()}
        for label, text in got.items():
            self.assertTrue(text, f"{label}: the spawn passage is not where SPAWN_SITES says")
        return got

    def test_every_spawn_site_names_the_lean_definition(self) -> None:
        """AC1. MUTANTS: reference-epic.md's wave example (or any Agent call in the three files)
        spawning `general-purpose`; the Build step not naming `sdlc-builder`, or the Review step
        `sdlc-reviewer`; a site's fallback sentence dropped; the template's fallback not naming
        Codex CLI, or not saying Copilot CLI and OpenCode keep their own."""
        sites = self._sites()
        for name in sorted({spec[0] for spec in SPAWN_SITES.values()}):
            with self.subTest(file=name):
                spawned = SUBAGENT_TYPE.findall((SKILL / name).read_text(encoding="utf-8"))
                self.assertEqual([], [t for t in spawned if t not in LEAN],
                                 f"{name} spawns a definition other than the lean two")
        for label, text in sites.items():
            flat = " ".join(text.split())
            with self.subTest(site=label):
                for agent in SPAWNS[label]:
                    self.assertRegex(flat, rf"`{agent}`|subagent_type=\"{agent}\"",
                                     f"{label} does not spawn {agent}")
                self.assertRegex(flat, FALLBACK, f"{label} names no general-purpose fallback")
        template = " ".join(sites["reference-agent-prompt-template.md"].split())
        self.assertRegex(template, r"no agent config \(Codex CLI\)")
        self.assertRegex(template, r"Copilot CLI and OpenCode keep their own")

    def test_the_wave_launches_its_first_agent_first(self) -> None:
        """AC2. MUTANTS: the Build step launching the wave in one message, or dropping the
        first-alone clause or the warm-prefix reason; reference-epic.md's example back to one
        message with every Agent call, or its later calls not marked as sent after the first has
        started."""
        sites = self._sites()
        build = " ".join(sites["reference-sprint.md Build step"].split())
        self.assertRegex(build, r"launches its first agent alone and the rest after it has started")
        self.assertRegex(build, r"warm shared prefix")
        example = sites["reference-epic.md wave example"]
        for label, text in (("Build step", build), ("epic example", example)):
            with self.subTest(site=label):
                self.assertNotRegex(text, r"(?i)\b(single|one) message\b")
        lines = example.splitlines()
        calls = [n for n, line in enumerate(lines) if "Agent(" in line]
        self.assertGreaterEqual(len(calls), 2, "the example launches fewer than two agents")
        self.assertRegex(" ".join(lines[calls[0] + 1:calls[1]]), r"after the first has started",
                         "the example's second agent is not sent after the first has started")

    def test_the_lane_brief_carries_the_builder_traps(self) -> None:
        """AC3. MUTANTS: a trap filed only in the cross-project registry (`lessons/`), which no
        lane brief reads; its class injected at plan or review but not build; its class pushed
        past the build digest's cap. Each leaves its rule out of the exported lane file."""
        sys.path.insert(0, str(SKILL / "scripts"))
        import sprint  # noqa: PLC0415 - the writer `sprint plan --export-lanes` drives
        with tempfile.TemporaryDirectory() as tmp:
            [path] = sprint._write_lane_worklists([["US1132"]], tmp, REPO)
            lane = Path(path).read_text(encoding="utf-8")
        carried = " ".join(line[1:].strip() for line in lane.splitlines() if line.startswith("#"))
        self.assertIn("Lessons for build", carried)
        missing = [trap for trap, rule in BUILDER_TRAPS.items() if not rule.search(carried)]
        self.assertEqual([], missing, "the lane brief's lessons block omits these builder traps")


if __name__ == "__main__":
    unittest.main()
