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


class SprintInFlightControlDocsTests(unittest.TestCase):
    """Every sprint verb is documented as an INVOCATION somebody can run.

    A verb whose name merely appears in prose is not documented: the reader still cannot run
    it, and a page that mentions every word while showing no command passes a word-search while
    teaching nothing.
    """

    SKILL = Path(__file__).resolve().parents[1].parent

    def _parser_verbs(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sprint", self.SKILL / "scripts" / "sprint.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["sprint"] = mod
        spec.loader.exec_module(mod)
        parser = mod.build_parser()
        for action in parser._actions:
            if hasattr(action, "choices") and action.choices and action.dest == "cmd":
                return sorted(action.choices), mod
        self.fail("the sprint parser exposes no subcommand choices")

    def test_every_parser_verb_appears_as_an_invocation_and_a_prose_only_page_fails(self) -> None:
        """MUTANT: document a verb by naming it in a sentence.

        Derived from the PARSER, so a verb added tomorrow is covered without editing this - and
        matched as `sprint.py <verb>`, which prose mentioning the word does not satisfy.
        """
        verbs, _mod = self._parser_verbs()
        page = (self.SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        # EITHER invocation form counts: the script path a script-level reader runs, and the
        # `/sdlc-studio sprint <verb>` slash form a skill user types. Both are real commands, so
        # requiring one spelling would fail a page that documents the other perfectly well.
        missing = [v for v in verbs
                   if f"sprint.py {v}" not in page and f"/sdlc-studio sprint {v}" not in page]
        self.assertEqual([], missing,
                         f"these verbs are not shown as a runnable invocation: {missing}")

    def test_every_extracted_invocation_parses_and_the_extraction_is_not_empty(self) -> None:
        """MUTANT: extract nothing, or document a command the parser rejects.

        The EMPTINESS check is half the test: an extractor that matches nothing reports every
        invocation valid, which is the vacuous-pass shape this project keeps meeting.
        """
        import re as _re
        verbs, mod = self._parser_verbs()
        page = (self.SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        # FENCED blocks only. A verb named in a sentence is prose, not an invocation, and
        # scraping prose pulls in flags and ordinary words - which would make this assert that
        # the English around a command parses.
        fenced = "\n".join(_re.findall(r"```[a-z]*\n(.*?)```", page, _re.S))
        self.assertTrue(fenced.strip(), "the page shows no fenced commands at all")
        found = _re.findall(r"(?:sprint\.py|/sdlc-studio sprint)\s+([a-z][a-z-]*)", fenced)
        self.assertTrue(found, "the extraction matched no invocations at all")
        unknown = sorted({v for v in found if v not in verbs})
        self.assertEqual([], unknown,
                         f"the page shows invocations the parser does not accept: {unknown}")

    def test_reference_sprint_carries_a_named_in_flight_control_section_with_the_invocations(self) -> None:
        """MUTANT: document the controls in help only.

        A reader working through the reference should not have to leave it to learn how to
        change a run that is already open.
        """
        ref = (self.SKILL / "reference-sprint.md").read_text(encoding="utf-8")
        self.assertIn("{#in-flight-controls}", ref,
                      "the reference has no named in-flight-control section to link to")
        for verb in ("batch swap", "batch drop", "stop", "reopen", "goal-review"):
            with self.subTest(verb=verb):
                self.assertIn(f"sprint.py {verb}", ref,
                              f"the reference section does not carry `{verb}`")


if __name__ == "__main__":
    unittest.main()
