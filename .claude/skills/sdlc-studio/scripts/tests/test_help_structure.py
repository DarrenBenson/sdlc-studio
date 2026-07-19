"""Tests for the shape of the help catalogue: it is grouped by the process spine.

The catalogue in `help/help.md` and the curated `command_audit.SPINE` map are two views of
the same fact - which stage of the process a command serves. These tests bind them together
so the two cannot disagree: a command placed under the wrong heading, or listed twice, fails
here rather than being discovered by an operator reading the page.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
_REPO = _SCRIPTS.parents[3]   # the real repo (has SKILL.md)
_HELP = _REPO / ".claude" / "skills" / "sdlc-studio" / "help" / "help.md"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
command_audit = _load("command_audit")

# The catalogue heading each spine category is published under. The keys are the `### `
# headings a reader sees; the values are `command_audit.SPINE`'s internal category names.
STAGE_HEADINGS: dict[str, str] = {
    "Raise": "raise",
    "Break Down": "break-down",
    "Sprint and Review": "sprint+review",
    "Levers": "lever",
    "Support": "support",
    "Utility": "utility",
}

_CMD_RE = re.compile(r"/sdlc-studio ([a-z][a-z-]*)")


def _all_command_sections(text: str) -> dict[str, str]:
    """The `### ` subsections of the "All Commands" catalogue, heading -> body.

    Scoped to that one section deliberately: commands are also named in the Getting Started
    examples and the Typical Workflows diagrams, and those are narrative, not the catalogue.
    """
    body = text.split("\n## All Commands\n", 1)[1]
    body = re.split(r"\n## ", body, maxsplit=1)[0]
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def _commands_in(body: str) -> set[str]:
    """The command tokens a catalogue section lists, ignoring redirect signposts (a folded
    command's redirect names it, but does not catalogue it)."""
    lines = [ln for ln in body.splitlines() if not command_audit._REDIRECT_RE.match(ln)]
    return {t for m in _CMD_RE.finditer("\n".join(lines)) if (t := m.group(1).rstrip("-"))}


class HelpSpineGroupingTests(unittest.TestCase):
    """Every catalogued command sits under the heading its spine category maps to."""

    def setUp(self) -> None:
        self.sections = _all_command_sections(_HELP.read_text(encoding="utf-8"))

    def test_every_spine_stage_has_a_section(self) -> None:
        for heading in STAGE_HEADINGS:
            self.assertIn(heading, self.sections, f"no `### {heading}` section in All Commands")

    def test_each_command_sits_under_its_spine_section(self) -> None:
        for heading, category in STAGE_HEADINGS.items():
            for cmd in _commands_in(self.sections.get(heading, "")):
                with self.subTest(heading=heading, command=cmd):
                    self.assertEqual(
                        command_audit.SPINE.get(cmd, "unmapped"), category,
                        f"`{cmd}` is listed under `### {heading}` but SPINE maps it to "
                        f"`{command_audit.SPINE.get(cmd, 'unmapped')}`")

    def test_no_command_is_listed_under_two_sections(self) -> None:
        seen: dict[str, str] = {}
        dupes: list[str] = []
        for heading in STAGE_HEADINGS:
            for cmd in _commands_in(self.sections.get(heading, "")):
                if cmd in seen:
                    dupes.append(f"`{cmd}` in both `{seen[cmd]}` and `{heading}`")
                else:
                    seen[cmd] = heading
        self.assertEqual(dupes, [], "; ".join(dupes))

    def test_every_spine_mapped_command_is_catalogued_somewhere(self) -> None:
        # the complement of the grouping check: a stage section must not be missing a command
        # the spine map knows about, or the rewrite silently dropped it from the page.
        catalogued: set[str] = set()
        for heading in STAGE_HEADINGS:
            catalogued |= _commands_in(self.sections.get(heading, ""))
        folded = set(command_audit._redirects(_HELP.parent.parent))
        missing = sorted(set(command_audit.SPINE) - catalogued - folded)
        self.assertEqual(missing, [], f"spine-mapped but absent from the catalogue: {missing}")


class HelpLeverPrecedenceTests(unittest.TestCase):
    """The document levers are the operator's top-level controls, so they are reached before
    the support and utility tooling."""

    LEVERS = ("prd", "trd", "tsd", "persona")

    def setUp(self) -> None:
        self.text = _HELP.read_text(encoding="utf-8")
        self.sections = _all_command_sections(self.text)

    def _pos(self, heading: str) -> int:
        i = self.text.find(f"\n### {heading}\n")
        self.assertNotEqual(i, -1, f"no `### {heading}` heading")
        return i

    def test_levers_section_precedes_support_and_utility(self) -> None:
        levers = self._pos("Levers")
        self.assertLess(levers, self._pos("Support"), "Levers must precede Support")
        self.assertLess(levers, self._pos("Utility"), "Levers must precede Utility")

    def test_levers_section_names_the_four_document_levers(self) -> None:
        listed = _commands_in(self.sections.get("Levers", ""))
        for lever in self.LEVERS:
            with self.subTest(lever=lever):
                self.assertIn(lever, listed, f"`{lever}` is not listed under `### Levers`")


if __name__ == "__main__":
    unittest.main()
