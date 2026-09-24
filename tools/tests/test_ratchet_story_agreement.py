"""BG0345 / BG0346: the ratchet stories must agree on one design and one scope.

Three unbuilt stories describing one mechanism were groomed apart, and drifted apart. US0461
refused an unbaselined duplicate Verify selector, US0480 an unbaselined validate warning, and
US0482 burns the duplicate baseline down to empty. US0896 retired US0480's ratchet with its lane,
so the rules that held US0480 and its pairing with US0461 are gone; US0482's remain.

- US0482's burn-down was scoped to `sdlc-studio/stories` while the ratchet it serves
  covers stories and bugs, so the bug-side groups would have stayed baselined for good.
  Its AC2 also cited a count of unanswerable groups recorded nowhere in the repository,
  which a test can only hardcode or pass vacuously against.

`check()` states those requirements over the live workspace. Once the stories are delivered
and archived the guard finds no files and goes quiet, which is the point at which it has no
subject.
"""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: A ratchet needs a reference state on disk. Any dot-file baseline under the workspace.
_BASELINE = re.compile(r"sdlc-studio/\.[\w.-]*baseline\.json")

#: A literal group count inside an acceptance criterion: a number the repository does not
#: hold, which a test can only hardcode or ignore.
_LITERAL_GROUP_COUNT = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:\w+\s+){0,2}groups?\b",
    re.I)


def _story_text(root: Path, disp: str) -> str | None:
    """The live story text for `disp`, or None once it is delivered and archived."""
    hits = sorted((root / "sdlc-studio" / "stories").glob(f"{disp}-*.md"))
    return hits[0].read_text(encoding="utf-8") if hits else None


def _field(text: str, name: str) -> str:
    m = re.search(rf"^>\s*\*\*{name}:\*\*\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def _criteria(text: str) -> str:
    """Just the Acceptance Criteria section. Prose elsewhere may legitimately discuss the
    design that was rejected, so a phrase check over the whole file would fire on the
    sentence explaining why the phrase is wrong."""
    m = re.search(r"^## Acceptance Criteria\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def check(root: Path) -> list[str]:
    """Every way the ratchet stories disagree with each other or with the code."""
    out: list[str] = []
    u482 = _story_text(root, "US0482")

    if u482 is not None:
        affects, criteria = _field(u482, "Affects"), _criteria(u482)
        if "sdlc-studio/bugs" not in affects:
            out.append("US0482 omits sdlc-studio/bugs from Affects while the ratchet it "
                       "serves covers stories and bugs, so the bug-side groups would stay "
                       "baselined for good")
        if not _BASELINE.search(affects):
            out.append("US0482 omits from Affects the baseline file its burn-down must empty")
        points = _field(u482, "Points")
        if points.isdigit() and int(points) < 8:
            out.append(f"US0482 is sized {points} for the stories-only scope; the widened "
                       f"scope carries half as many groups again")
        hit = _LITERAL_GROUP_COUNT.search(criteria)
        if hit:
            out.append(f"US0482 criterion cites {hit.group(0)!r}, a set no record in the "
                       f"repository holds, so a test can only hardcode it or pass vacuously")
        if not re.search(r"selector_resolves|resolver", criteria):
            out.append("US0482 has no criterion deriving the unanswerable groups by running "
                       "the resolver, which is the only reference a test can appeal to")
    return out


class RatchetStoryAgreement(unittest.TestCase):
    def test_the_live_stories_agree_on_one_ratchet_design(self) -> None:
        if _story_text(REPO, "US0482") is None:
            self.skipTest("US0482 is delivered and archived")
        self.assertEqual(check(REPO), [])


class RatchetStoryAgreementRules(unittest.TestCase):
    """Each rule against the shape the story actually had when it was filed."""

    def _root(self, **stories: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True)
        for disp, text in stories.items():
            (d / f"{disp}-x.md").write_text(text, encoding="utf-8")
        return root

    def test_a_burndown_narrower_than_the_ratchet_it_serves_is_refused(self) -> None:
        root = self._root(US0482=_STORIES_ONLY_482)
        found = " | ".join(check(root))
        self.assertIn("sdlc-studio/bugs", found)
        self.assertIn("baseline", found)

    def test_a_criterion_citing_a_group_count_no_record_holds_is_refused(self) -> None:
        root = self._root(US0482=_STORIES_ONLY_482)
        found = " | ".join(check(root))
        self.assertIn("four groups", found)
        self.assertIn("resolver", found)

    def test_a_burndown_sized_for_the_narrower_scope_is_refused(self) -> None:
        root = self._root(US0482=_STORIES_ONLY_482)
        self.assertIn("sized 5", " | ".join(check(root)))


_STORIES_ONLY_482 = """# US0482: the baselined duplicate Verify groups are split

> **Status:** Draft
> **Affects:** sdlc-studio/stories, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Points:** 5

## Acceptance Criteria

### AC1: no intra-record duplicate group remains

- **Given** the duplicate groups confined within a single record
- **When** the lint runs over the workspace
- **Then** it reports none
- **Verify:** pytest x.py::T::test_no_intra_record_duplicate_group_remains

### AC2: the four groups unanswerable by collection are named

- **Given** the four groups unanswerable by collection
- **When** the lint runs
- **Then** each is named individually
- **Verify:** pytest x.py::T::test_the_unanswerable_groups_are_named
"""


if __name__ == "__main__":
    unittest.main()
