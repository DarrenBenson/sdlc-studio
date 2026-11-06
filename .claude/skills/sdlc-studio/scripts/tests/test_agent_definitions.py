"""The lean subagent definitions a builder or reviewer is spawned as (US1131).

`AgentDefinitionTests` pins the definitions themselves: the restricted tool line, the hand-back
contract they and the amigo seats' review renders carry, and this repository's copies matching
the templates a consuming project receives (AC1, AC3 and AC4; AC2 lives in test_init.py). A class
added here for the spawn sites keeps these three tests as they stand; DEFINITIONS and the helpers
below are shared for that purpose.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md
# test-census-subject: .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md
from __future__ import annotations

import re
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


if __name__ == "__main__":
    unittest.main()
