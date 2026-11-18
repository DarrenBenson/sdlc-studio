"""US1315: package.json and CR0742 describe SDLC Studio as a harness-agnostic Agent Skill.

The GitHub About box, its topics and package.json's description are the first words a reviewer
reads, and the old ones called SDLC Studio a "Claude Code skill". The About box and topics are
repository settings, not files, so CR0742 carries their exact text for the owner and a
`## Applied` note saying whether `gh repo edit` has applied them. package.json carries the same
description and the same ten topics as its keywords.

Every test also runs its check on a broken copy, so a check that cannot fail is caught by the
test that relies on it.
"""
# test-census-subject: package.json
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / "package.json"
CR0742 = (REPO / "sdlc-studio" / "change-requests"
          / "CR0742-harness-agnostic-and-enterprise-ready-documentation.md")

#: The About description CR0742 proposes, verbatim; package.json carries the same words.
DESCRIPTION = ("Harness-agnostic Agent Skill for governed software delivery, human in the lead. "
               "Works in GitHub Copilot, Claude Code, Cursor, Codex, Gemini CLI and opencode.")
#: CR0742's ten topics, in the order the CR gives them.
TOPICS = ("agent-skills", "sdlc", "software-delivery", "ai-governance", "github-copilot",
          "claude-code", "cursor", "codex", "gemini-cli", "opencode")

_PROPOSED_DESCRIPTION = re.compile(r'Proposed description:\s*"([^"]+)"')
_PROPOSED_TOPICS = re.compile(r"Proposed topics:\s*([^\n]+?)\.?\s*$", re.M)
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_STATUS = re.compile(r"(?i)\b(applied|pending)\b")


def section(text: str, heading: str) -> str:
    """The body under the `## heading` line, up to the next `## ` heading; "" when absent."""
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not match:
        return ""
    rest = text[match.end():]
    end = re.search(r"(?m)^## ", rest)
    return rest[: end.start()] if end else rest


def package_faults(package: dict) -> list[str]:
    """What keeps package.json from describing a harness-agnostic Agent Skill; [] when nothing."""
    faults = []
    if package.get("description") != DESCRIPTION:
        faults.append(f"package.json description is {package.get('description')!r}")
    keywords = package.get("keywords")
    if not isinstance(keywords, list):
        return faults + ["package.json has no keywords list"]
    faults += [f"package.json keywords lack {topic!r}" for topic in TOPICS if topic not in keywords]
    faults += [f"package.json keywords carry {word!r}, not one of CR0742's topics"
               for word in keywords if word not in TOPICS]
    return faults


def cr_faults(text: str) -> list[str]:
    """What keeps CR0742 from recording the About text, the topics and whether they were applied."""
    faults = []
    requested = section(text, "## Requested changes")
    described = _PROPOSED_DESCRIPTION.search(requested)
    if not described or described.group(1) != DESCRIPTION:
        faults.append("CR0742 does not carry the About description verbatim")
    topics = _PROPOSED_TOPICS.search(requested)
    if not topics or tuple(t.strip() for t in topics.group(1).split(",")) != TOPICS:
        faults.append("CR0742 does not carry the ten topics verbatim")
    applied = section(text, "## Applied")
    if not applied.strip():
        return faults + ["CR0742 has no ## Applied note"]
    if "gh repo edit" not in applied:
        faults.append("the ## Applied note does not name gh repo edit")
    if not _STATUS.search(applied):
        faults.append("the ## Applied note does not say whether the text was applied")
    if not _ISO_DATE.search(applied):
        faults.append("the ## Applied note gives no date")
    return faults


class PackageMetadataTests(unittest.TestCase):
    def test_the_description_and_keywords_are_harness_agnostic(self) -> None:
        """AC1: the description is CR0742's About text and the keywords are its ten topics.
        Mutants: the old "Claude Code skill" description, a topic missing, a stray keyword."""
        package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        self.assertEqual(package_faults(package), [])

        old = dict(package, description="Claude Code skill for managing the full software "
                                        "development lifecycle")
        self.assertEqual(package_faults(old), [f"package.json description is "
                                               f"{old['description']!r}"])
        short = dict(package, keywords=[t for t in package["keywords"] if t != "github-copilot"])
        self.assertEqual(package_faults(short), ["package.json keywords lack 'github-copilot'"])
        stray = dict(package, keywords=list(package["keywords"]) + ["claude-code-skill"])
        self.assertEqual(package_faults(stray), ["package.json keywords carry "
                                                 "'claude-code-skill', not one of CR0742's topics"])
        self.assertEqual(package_faults({k: v for k, v in package.items() if k != "keywords"}),
                         ["package.json has no keywords list"])

    def test_cr0742_records_the_about_text_and_whether_it_was_applied(self) -> None:
        """AC2: the CR carries the About description and topics verbatim, and a `## Applied`
        note names `gh repo edit`, says applied or pending, and dates it. Mutants: the text
        paraphrased, a topic dropped, no note, a note with no status or no date."""
        text = CR0742.read_text(encoding="utf-8")
        self.assertEqual(cr_faults(text), [])

        paraphrased = text.replace("governed software delivery", "governed delivery", 1)
        self.assertIn("CR0742 does not carry the About description verbatim",
                      cr_faults(paraphrased))
        dropped = text.replace("github-copilot, ", "", 1)
        self.assertIn("CR0742 does not carry the ten topics verbatim", cr_faults(dropped))

        note = section(text, "## Applied")
        self.assertNotIn("\n## ", note, "the Applied note runs on into the next section")
        self.assertEqual(cr_faults(text.replace("## Applied", "## Notes", 1)),
                         ["CR0742 has no ## Applied note"])
        undated = text.replace(note, _ISO_DATE.sub("later", note), 1)
        self.assertEqual(cr_faults(undated), ["the ## Applied note gives no date"])
        silent = text.replace(note, _STATUS.sub("handled", note), 1)
        self.assertEqual(cr_faults(silent),
                         ["the ## Applied note does not say whether the text was applied"])
        unnamed = text.replace(note, note.replace("gh repo edit", "the settings page"), 1)
        self.assertEqual(cr_faults(unnamed), ["the ## Applied note does not name gh repo edit"])


if __name__ == "__main__":
    unittest.main()
