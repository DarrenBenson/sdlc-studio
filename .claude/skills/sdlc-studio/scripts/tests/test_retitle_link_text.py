"""BG1068: `artifact.py retitle` repointed an inbound link's target and left its text, so an epic's
Story Breakdown line kept announcing `US1080: <old title>` over a link to the new file. A link
whose text is the artefact's own `<ID>: <old title>` now carries the new title as well; any other
link text is left alone.

Each case runs `artifact.retitle` (the function `artifact.py retitle` calls) over a throwaway root.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retitle_link_text.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/artifact.py
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import artifact  # noqa: E402
import file_finding  # noqa: E402

OLD = "the mistaken title needing correction now"
NEW = "the corrected title"


def _story(root: Path, title: str = OLD) -> Path:
    folder = root / "sdlc-studio" / "stories"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"US1080-{file_finding._slug(title)}.md"
    path.write_text(
        f"# US1080: {title}\n\n> **Status:** Draft\n\n## User Story\n\nx\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        "| 2026-07-23 | sdlc | Raised |\n", encoding="utf-8")
    (folder / "_index.md").write_text(
        "# Story Index\n\n## All Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [US1080]({path.name}) | {title} | Draft |\n", encoding="utf-8")
    return path


def _epic(root: Path, body: str) -> Path:
    folder = root / "sdlc-studio" / "epics"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "EP0289-container.md"
    path.write_text(f"# EP0289: container\n\n> **Status:** Draft\n\n## Story Breakdown\n\n{body}\n\n"
                    "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n",
                    encoding="utf-8")
    return path


class RetitleLinkTextTests(unittest.TestCase):

    def setUp(self) -> None:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        self.story = _story(self.root)
        self.old_link = f"../stories/{self.story.name}"
        self.new_name = f"US1080-{file_finding._slug(NEW)}.md"

    def _retitle(self, epic_body: str, title: str = NEW) -> str:
        epic = _epic(self.root, epic_body)
        artifact.retitle(self.root, "US1080", title)
        return epic.read_text(encoding="utf-8")

    def test_breakdown_link_text_follows_the_retitle(self) -> None:
        """AC1. Mutants: the target rewritten and the text left as it was; the text rewritten
        for a link to some other file; a dashed id form not recognised."""
        text = self._retitle(f"- [ ] [US1080: {OLD}]({self.old_link})\n"
                             f"- [ ] [US-1080: {OLD}]({self.old_link}#top)")
        self.assertIn(f"- [ ] [US1080: {NEW}](../stories/{self.new_name})\n", text)
        self.assertIn(f"- [ ] [US-1080: {NEW}](../stories/{self.new_name}#top)", text)
        self.assertNotIn(OLD, text)

    def test_any_other_link_text_is_left_alone(self) -> None:
        """The controls. Mutants: every link to the story retexted; a link to another story
        with the same old title retexted; a link quoted in a code span or fence rewritten."""
        other = f"US2000-{file_finding._slug(OLD)}.md"
        text = self._retitle(
            f"- [ ] [read the story]({self.old_link})\n"
            f"- [ ] [US1080 as planned]({self.old_link})\n"
            f"- [ ] [US2000: {OLD}](../stories/{other})\n"
            f"- [ ] [US2000: {OLD}]({self.old_link})\n"
            f"- [ ] [US1080: {OLD}](../stories/US1080-another-file.md)\n"
            f"- [ ] [US1080: a different title]({self.old_link})\n"
            f"- [ ] code `[US1080: {OLD}](../stories/{self.new_name})` quoted\n"
            f"```\n[US1080: {OLD}](../stories/{self.new_name})\n```\n"
            f"- [ ] code `[US1080: {OLD}]({self.old_link})` quoted\n"
            f"```\n[US1080: {OLD}]({self.old_link})\n```")
        self.assertIn(f"- [ ] [read the story](../stories/{self.new_name})\n", text)
        self.assertIn(f"- [ ] [US1080 as planned](../stories/{self.new_name})\n", text)
        self.assertIn(f"- [ ] [US2000: {OLD}](../stories/{other})\n", text)
        self.assertIn(f"- [ ] [US2000: {OLD}](../stories/{self.new_name})\n", text)
        self.assertIn(f"- [ ] [US1080: {OLD}](../stories/US1080-another-file.md)\n", text)
        self.assertIn(f"- [ ] [US1080: a different title](../stories/{self.new_name})\n", text)
        self.assertIn(f"code `[US1080: {OLD}](../stories/{self.new_name})` quoted", text)
        self.assertIn(f"```\n[US1080: {OLD}](../stories/{self.new_name})\n```", text)
        self.assertIn(f"`[US1080: {OLD}]({self.old_link})`", text)
        self.assertIn(f"```\n[US1080: {OLD}]({self.old_link})\n```", text)

    def test_a_title_with_brackets_keeps_the_link_whole(self) -> None:
        """A bracket in the new title is escaped in the link text, so the link still closes."""
        title = "the [fixed] title"
        new_name = f"US1080-{file_finding._slug(title)}.md"
        text = self._retitle(f"- [ ] [US1080: {OLD}]({self.old_link})", title)
        self.assertIn(f"[US1080: the \\[fixed\\] title](../stories/{new_name})", text)

    def test_a_retitle_to_a_new_case_only_still_retexts_the_link(self) -> None:
        """The slug is the same, so the target is unchanged and nothing but the text moves."""
        title = OLD.upper()
        self.assertEqual(file_finding._slug(title), file_finding._slug(OLD))
        text = self._retitle(f"- [ ] [US1080: {OLD}]({self.old_link})", title)
        self.assertIn(f"[US1080: {title}]({self.old_link})", text)


if __name__ == "__main__":
    unittest.main()
