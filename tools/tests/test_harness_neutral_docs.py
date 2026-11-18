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
A requirement noun, a "must", a version before "is required" and a list item under a
Requirements heading count as requirement statements; a negation excuses only its own clause,
so a requirement after a comma, a spaced dash, "and" or "but" is refused.

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
#: A version after the vendor, as in "2.0 or later", "2.1+" or "version 2.0".
_VERSION = r"(?:\s+(?i:version\s+|v)?\d+(?:\.\d+)*\+?(?:\s+or\s+(?i:later|newer|higher))?)?"
REQUIRES = "requires Claude Code, Claude or Anthropic"
#: Each banned shape, by the name a finding reports. Names are case-sensitive, so `CLAUDE.md`
#: and the `claude` install target are not the vendor; the verbs are matched in any case.
PATTERNS = {
    "Claude Code skill": re.compile(r"\bClaude[ -]Code\s+[Ss]kill\b"),
    "Claude-Code-only": re.compile(r"\bClaude[ -]Code-only\b|\b(?:Claude|Anthropic)-only\b"),
    REQUIRES: re.compile(
        r"(?i:\b(?:requires?|required|requirements?|needs?|needed|depends\s+on|prerequisites?"
        r"|must\s+(?:have|use|install))\b)[:\s]+(?:(?i:an?|the|your)\s+)?" + _VENDOR),
    # "must be installed" takes no plain word after the vendor, so "Claude Code hooks must be
    # installed" is a step in that harness, not a requirement of it.
    "Claude Code, Claude or Anthropic is required": re.compile(
        _VENDOR + _VERSION + r"(?:(?:\s+[\w-]+){0,2}\s+(?:is|are)\s+"
        r"(?i:required|needed|mandatory|a\s+prerequisite|a\s+requirement)"
        r"|\s+must\s+be\s+(?i:installed|present|available|running|used))\b"),
}
#: A list item that opens with the vendor, below a heading naming requirements or
#: prerequisites, or a bare "Requirements:" or "Prerequisites:" line, and above the next
#: heading. It is matched on the raw text, since a list needs its line breaks, and reported at
#: the item.
REQUIREMENT_LIST = re.compile(
    r"(?m)^(?:#{1,6}[ \t][^\n]*\b(?i:requirements|prerequisites)\b[^\n]*"
    r"|(?:\*\*)?(?i:requirements|prerequisites)(?:\*\*)?:(?:\*\*)?[ \t]*)\n"
    r"(?:(?!#)[^\n]*\n)*?[ \t]*(?:[-*+]|\d+[.)])[ \t]+(?:\*\*)?(?P<hit>" + _VENDOR + ")")
#: A requirement this close after a negation, in the same clause, is a denial ("does not
#: require Anthropic", "no Claude subscription is needed"). A comma, a spaced dash, "and" or
#: "but" ends the clause, so "without Copilot but requires Claude Code" is not one.
_NEGATION = re.compile(r"(?i)(?:\b(?:not|never|no|nor|without)\b|n't)"
                       r"(?:(?!\s-\s|\b(?:and|but)\b)[^.,;:!?]){0,24}$")


def denied(text: str, start: int) -> bool:
    """Whether the match at `start` follows a negation in its own clause and paragraph."""
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
    hits = [(label, m.start(), m.group(0)) for label, pattern in PATTERNS.items()
            for m in pattern.finditer(flat)]
    hits += [(REQUIRES, m.start("hit"), m.group("hit")) for m in REQUIREMENT_LIST.finditer(text)]
    findings = []
    for label, start, phrase in hits:
        if denied(text, start):
            continue
        line = text.count("\n", 0, start) + 1
        findings.append(f"{name}:{line}: {label}: {' '.join(phrase.split())!r}")
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
        refused by file, line and name, including one wrapped across lines, one in bold, one in
        a Requirements list and one after a negated earlier clause; the harness-specific lines
        and a denial pass."""
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
        requires = "requires Claude Code, Claude or Anthropic"
        is_required = "Claude Code, Claude or Anthropic is required"
        #: Each planted phrase, the name it is refused by, and its line below the README's end.
        planted = {
            "SDLC Studio is a Claude Code skill.": ("Claude Code skill", 0),
            "SDLC Studio is a Claude\nCode skill.": ("Claude Code skill", 0),
            "Agentic waves are Claude-Code-only.": ("Claude-Code-only", 0),
            "Running it requires\nClaude Code.": (requires, 0),
            "You need an Anthropic subscription.": (requires, 0),
            "Prerequisites: **Claude Code** and Python.": (requires, 0),
            "An Anthropic API key is required.": (is_required, 0),
            "Claude Code is mandatory here.": (is_required, 0),
            # A requirement noun, a "must" and a version before "is required".
            "Requirements: Claude Code and Python 3.10+.": (requires, 0),
            "You must have Claude Code installed.": (requires, 0),
            "First you must install the Claude Code CLI.": (requires, 0),
            "You must use Claude Code for the waves.": (requires, 0),
            "Claude Code must be installed first.": (is_required, 0),
            "Claude Code 2.0 or later is required.": (is_required, 0),
            "Claude Code version 2.1+ must be present.": (is_required, 0),
            "Claude Code 2.0 or newer must be running.": (is_required, 0),
            # A list naming the vendor under a Requirements or Prerequisites heading or label.
            "## Requirements\n\n- Claude Code\n- Python 3.10+": (requires, 2),
            "## System requirements\n\nYou need:\n\n- Python 3.10+\n- **Claude Code**":
                (requires, 5),
            "**Prerequisites:**\n\n1. Anthropic API access": (requires, 2),
            # A negation excuses only the vendor it denies, not a later clause.
            "Works with or without Copilot but requires Claude Code.": (requires, 0),
            "Runs in any harness, not just Copilot, and needs Claude Code.": (requires, 0),
            "Runs without Copilot and needs Claude Code.": (requires, 0),
            "Not tested on Copilot, it needs Claude Code.": (requires, 0),
            "No GPU is needed - you need Claude Code.": (requires, 0),
        }
        for phrase, (label, offset) in planted.items():
            with self.subTest(phrase=phrase):
                findings = scan("README.md", readme + phrase + "\n")
                self.assertEqual(len(findings), 1, findings)
                self.assertTrue(findings[0].startswith(f"README.md:{at + offset}: {label}: "),
                                findings[0])

        harness_specific = (
            "Claude Code reads it via `@AGENTS.md` in [CLAUDE.md](CLAUDE.md).",
            "| Claude Code | (default - no flag needed) |",
            "In Claude Code, skill edits take effect mid-session.",
            "Claude Code does not read it - keep the `claude` target for Claude Code.",
            "Proudly supported by **Anthropic** through the **Claude for Open Source** programme.",
            "SDLC Studio does not require Anthropic products.",
            "SDLC Studio does not need Claude Code.",
            "No Claude subscription is needed.",
            "It doesn't need Claude Code; Claude Code is not required either.",
            "Install into the Claude Code skills folder, `~/.claude/skills`.",
            "The installer requires the `claude` target for that folder.",
            "The default install (Claude Code\nonly) names each other tool.",
            "Claude Code hooks must be installed once per clone.",
            "Claude Code reads the file that is required.",
            "## Install\n\n- Claude Code: the default target, no flag needed",
            "## Requirements\n\n- Python 3.10+\n\n## Harnesses\n\n- Claude Code",
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
