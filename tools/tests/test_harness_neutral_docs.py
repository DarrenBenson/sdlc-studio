"""US1320: no public document says Claude Code, Claude or Anthropic is required.

SDLC Studio is an Agent Skill that runs in six harnesses, and a reviewer who reads "a Claude Code
skill", "Claude-Code-only" or "requires Claude Code" on a public page concludes it needs one
vendor. The guard scans the pages a reviewer or an evaluating agent reads: README.md, every page
under docs/, llms.txt, package.json, the SKILL.md front matter, the skill's help pages,
AGENTS.md, CONTRIBUTING.md, SUPPORT.md and SECURITY.md.

Harness-specific lines are not generic requirements and pass: an install row naming Claude Code,
AGENTS.md's line on how Claude Code imports it, a note that a step applies in Claude Code, and a
statement that SDLC Studio does not require Anthropic products. The patterns name the phrase and
the requirement verbs, not the README's wording, so a rewrite of any page is judged the same way.

Every test also runs its check on a broken copy, so a check that cannot fail is caught by the
test that relies on it.
"""
# test-census-subject: docs/INSTALL.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
INSTALL = REPO / "docs" / "INSTALL.md"
WHY = REPO / "docs" / "why-sdlc-studio.md"
HARNESSES_PAGE = REPO / "docs" / "harnesses.md"

#: The root pages the guard scans whole.
ROOT_PAGES = ("README.md", "llms.txt", "package.json", "AGENTS.md", "CONTRIBUTING.md",
              "SUPPORT.md", "SECURITY.md")

_VENDOR = r"(?:Claude(?:[ -]Code)?|Anthropic)\b"
#: Each banned shape, by the name a finding reports. Names are case-sensitive, so `CLAUDE.md`
#: and the `claude` install target are not the vendor; the verbs are matched in any case.
PATTERNS = {
    "Claude Code skill": re.compile(r"\bClaude[ -]Code\s+[Ss]kill\b"),
    "Claude-Code-only": re.compile(r"\bClaude[ -]Code-only\b|\b(?:Claude|Anthropic)-only\b"),
    "requires Claude Code, Claude or Anthropic": re.compile(
        r"(?i:\b(?:requires?|required|needs?|needed|depends\s+on|prerequisites?)\b)[:\s]+"
        r"(?:(?i:an?|the|your)\s+)?" + _VENDOR),
    "Claude Code, Claude or Anthropic is required": re.compile(
        _VENDOR + r"(?:\s+[\w-]+){0,2}\s+(?:is|are)\s+"
        r"(?i:required|needed|mandatory|a\s+prerequisite|a\s+requirement)\b"),
}
#: A requirement this close after a negation, in the same sentence and paragraph, is a denial
#: ("does not require Anthropic", "no Claude subscription is needed").
_NEGATION = re.compile(r"(?i)(?:\b(?:not|never|no|nor|without)\b|n't)[^.;:!?]{0,24}$")


def denied(text: str, start: int) -> bool:
    """Whether the match at `start` follows a negation in its own sentence and paragraph."""
    window = text[max(0, start - 60):start].rsplit("\n\n", 1)[-1]
    return bool(_NEGATION.search(flatten(window)))


def surfaces(root: Path = REPO) -> dict[str, str]:
    """`{relative path: text}` for every public surface the guard scans; the SKILL.md entry is
    its front matter alone, since the body is routing for the agent, not a public claim."""
    found = {}
    for name in ROOT_PAGES:
        path = root / name
        if path.is_file():
            found[name] = path.read_text(encoding="utf-8")
    pages = sorted((root / "docs").rglob("*.md")) + sorted((root / SKILL.relative_to(REPO)
                                                             / "help").glob("*.md"))
    for path in pages:
        found[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
    skill_md = root / SKILL.relative_to(REPO) / "SKILL.md"
    if skill_md.is_file():
        parts = skill_md.read_text(encoding="utf-8").split("---", 2)
        found[skill_md.relative_to(root).as_posix()] = "---" + parts[1] if len(parts) > 2 else ""
    return found


def flatten(text: str) -> str:
    """The text with line breaks, blockquote marks and emphasis turned to spaces, so a phrase
    wrapped across lines or set in bold still matches; every offset stays where it was."""
    text = re.sub(r"(?m)^>", " ", text)
    return text.translate(str.maketrans("\n*`", "   "))


def scan(name: str, text: str) -> list[str]:
    """`name:line: pattern: 'match'` for each banned phrase in `text`; [] when it has none."""
    flat = flatten(text)
    findings = []
    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(flat):
            if denied(text, match.start()):
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(f"{name}:{line}: {label}: {' '.join(match.group(0).split())!r}")
    return findings


def link_targets(text: str) -> list[str]:
    """The target of every inline markdown link, without its anchor."""
    return [t.split("#", 1)[0] for t in re.findall(r"\]\(([^)\s]+)\)", text)]


def install_faults(text: str) -> list[str]:
    """What keeps docs/INSTALL.md from installing a skill and linking the harness page."""
    faults = []
    quick = text.split("## Quick start", 1)[1].split("\n## ", 1)[0] if "## Quick start" in text \
        else ""
    if not quick:
        faults.append("docs/INSTALL.md has no Quick start section")
    elif PATTERNS["Claude Code skill"].search(flatten(quick)):
        faults.append("the quick install calls the default the Claude Code skill")
    if "harnesses.md" not in link_targets(text):
        faults.append("docs/INSTALL.md does not link docs/harnesses.md")
    return faults


def agentic_line(text: str) -> str:
    """The why page's agentic-execution bullet; "" when it has none."""
    return next((ln for ln in text.splitlines() if ln.startswith("- **Agentic execution.**")), "")


def why_faults(text: str) -> list[str]:
    """What keeps the why page's agentic-execution line from stating the fallback."""
    line = agentic_line(text)
    if not line:
        return ["docs/why-sdlc-studio.md has no agentic-execution line"]
    wanted = {"sub-agents": r"(?i)\bsub-?agents\b", "one at a time": r"(?i)\bone at a time\b",
              "dependency order": r"(?i)\bdependency order\b"}
    return [f"the agentic-execution line does not say {label}" for label, p in wanted.items()
            if not re.search(p, line)]


class HarnessNeutralDocsTests(unittest.TestCase):
    def test_no_public_document_says_claude_code_or_anthropic_is_required(self) -> None:
        """AC1. Every surface scans clean; each banned phrase planted in a copy of the README is
        refused by file, line and name, including one wrapped across lines and one in bold; the
        harness-specific lines and a denial pass."""
        found = surfaces()
        for name in ("README.md", "llms.txt", "package.json", "AGENTS.md", "CONTRIBUTING.md",
                     "SUPPORT.md", "SECURITY.md"):
            self.assertIn(name, found, f"{name} is missing, so the guard scans nothing there")
        for name in ("docs/INSTALL.md", "docs/harnesses.md", "docs/enterprise.md",
                     "docs/why-sdlc-studio.md", ".claude/skills/sdlc-studio/help/epic.md",
                     ".claude/skills/sdlc-studio/SKILL.md"):
            self.assertIn(name, found, f"the guard does not scan {name}")
        self.assertIn("compatibility:", found[".claude/skills/sdlc-studio/SKILL.md"])
        self.assertNotIn("# SDLC Studio", found[".claude/skills/sdlc-studio/SKILL.md"])
        self.assertEqual([f for name, text in found.items() for f in scan(name, text)], [])

        readme = found["README.md"] + "\n\n"
        at = readme.count("\n") + 1
        planted = {
            "SDLC Studio is a Claude Code skill.": "Claude Code skill",
            "SDLC Studio is a Claude\nCode skill.": "Claude Code skill",
            "Agentic waves are Claude-Code-only.": "Claude-Code-only",
            "Running it requires\nClaude Code.": "requires Claude Code, Claude or Anthropic",
            "You need an Anthropic subscription.": "requires Claude Code, Claude or Anthropic",
            "Prerequisites: **Claude Code** and Python.": "requires Claude Code, Claude or Anthropic",
            "An Anthropic API key is required.": "Claude Code, Claude or Anthropic is required",
            "Claude Code is mandatory here.": "Claude Code, Claude or Anthropic is required",
        }
        for phrase, label in planted.items():
            with self.subTest(phrase=phrase):
                findings = scan("README.md", readme + phrase + "\n")
                self.assertEqual(len(findings), 1, findings)
                self.assertTrue(findings[0].startswith(f"README.md:{at}: {label}: "),
                                findings[0])

        harness_specific = (
            "Claude Code reads it via `@AGENTS.md` in [CLAUDE.md](CLAUDE.md).",
            "| Claude Code | (default - no flag needed) |",
            "In Claude Code, skill edits take effect mid-session.",
            "Claude Code does not read it - keep the `claude` target for Claude Code.",
            "Proudly supported by **Anthropic** through the **Claude for Open Source** programme.",
            "SDLC Studio does not require Anthropic products.",
            "It doesn't need Claude Code; Claude Code is not required either.",
            "Install into the Claude Code skills folder, `~/.claude/skills`.",
            "The installer requires the `claude` target for that folder.",
        )
        for line in harness_specific:
            with self.subTest(line=line):
                self.assertEqual(scan("README.md", line), [])
        # A negation in the paragraph before does not excuse a requirement in this one.
        self.assertEqual(scan("README.md", "## Not supported\n\nYou need Claude Code.\n"),
                         ["README.md:3: requires Claude Code, Claude or Anthropic: "
                          "'need Claude Code'"])

    def test_install_md_is_neutral_and_links_the_harness_page(self) -> None:
        """AC2. Mutants: the old quick-install wording, and the harness-page link removed."""
        text = INSTALL.read_text(encoding="utf-8")
        self.assertEqual(install_faults(text), [])
        self.assertTrue(HARNESSES_PAGE.is_file())

        quick = text.split("## Quick start", 1)[1].split("\n## ", 1)[0]
        first = next(ln for ln in quick.splitlines() if ln.startswith("macOS / Linux"))
        old = text.replace(first, "macOS / Linux (installs the Claude Code skill, globally):", 1)
        self.assertEqual(install_faults(old),
                         ["the quick install calls the default the Claude Code skill"])
        unlinked = re.sub(r"\]\(harnesses\.md(#[^)]*)?\)", "](INSTALL.md)", text)
        self.assertEqual(install_faults(unlinked),
                         ["docs/INSTALL.md does not link docs/harnesses.md"])
        named = unlinked + "\nSee `harnesses.md` beside this page.\n"
        self.assertEqual(install_faults(named), ["docs/INSTALL.md does not link docs/harnesses.md"])

    def test_the_why_page_states_the_agentic_fallback(self) -> None:
        """AC3. Mutant: the old line, naming Claude Code with no fallback."""
        text = WHY.read_text(encoding="utf-8")
        self.assertEqual(why_faults(text), [])

        old = text.replace(agentic_line(text), "- **Agentic execution.** `epic implement "
                           "--agentic` runs safe waves of parallel implementation agents (Claude "
                           "Code), with quality gates at every wave boundary.", 1)
        self.assertEqual(why_faults(old), ["the agentic-execution line does not say sub-agents",
                                           "the agentic-execution line does not say one at a time",
                                           "the agentic-execution line does not say dependency "
                                           "order"])
        self.assertEqual(why_faults(text.replace(agentic_line(text), "", 1)),
                         ["docs/why-sdlc-studio.md has no agentic-execution line"])


if __name__ == "__main__":
    unittest.main()
