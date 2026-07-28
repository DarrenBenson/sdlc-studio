"""BG0345 / BG0346: the ratchet stories must agree on one design and one scope.

Three unbuilt stories describe one mechanism. US0461 refuses an unbaselined duplicate
Verify selector, US0480 refuses an unbaselined validate warning, and US0482 burns the
duplicate baseline down to empty. They were groomed apart, and drifted apart:

- US0480 compared a total recomputed from the corpus being judged. Such a total always
  equals the actual, so the new instance its own AC1 required to fail never could.
  Neither ratchet story named the other, so the divergence was invisible from either.
- US0480 changed only `validate.py`, but `gate.py._validate` counts `severity == "error"`
  and discards every warning, and the hook runs `gate.py` rather than `validate.py check`,
  so a non-zero exit from validate alone refuses no commit.
- US0482's burn-down was scoped to `sdlc-studio/stories` while the ratchet it serves
  covers stories and bugs, so the bug-side groups would have stayed baselined for good.
  Its AC2 also cited a count of unanswerable groups recorded nowhere in the repository,
  which a test can only hardcode or pass vacuously against.

`check()` states those requirements over the live workspace. The rule about the blocking
lane is DERIVED, not restated: it fires only while the code actually discards warnings
before any lane could refuse on them. Once the three stories are delivered and archived
the guard finds no files and goes quiet, which is the point at which it has no subject.
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


def warnings_reach_no_blocking_lane(root: Path) -> bool:
    """True while a validate warning cannot refuse a commit however validate exits.

    Measured from the two files that decide it, so the requirement this feeds disappears
    by itself if `gate.py` ever stops discarding warnings or the hook starts calling
    `validate.py check` directly.
    """
    gate = root / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"
    hook = root / ".githooks" / "pre-commit"
    if not gate.is_file() or not hook.is_file():
        return False
    g = gate.read_text(encoding="utf-8")
    h = hook.read_text(encoding="utf-8")
    discards = re.search(r"\[.severity.\]\s*==\s*\"error\"", g) is not None
    runs_gate = re.search(r"\$skill/gate\.py\"", h) is not None
    runs_validate = re.search(r"\$skill/validate\.py\" check", h) is not None
    return discards and runs_gate and not runs_validate


def check(root: Path) -> list[str]:
    """Every way the three ratchet stories disagree with each other or with the code."""
    out: list[str] = []
    u480 = _story_text(root, "US0480")
    u461 = _story_text(root, "US0461")
    u482 = _story_text(root, "US0482")

    if u480 is not None:
        affects, criteria = _field(u480, "Affects"), _criteria(u480)
        if "US0461" not in u480:
            out.append("US0480 names no partner: US0461 builds the same ratchet and the "
                       "two designs cannot be compared from either story")
        if not _BASELINE.search(affects):
            out.append("US0480 declares no baseline file in Affects, so the ratchet has no "
                       "reference state to compare against")
        if not re.search(r"identit(?:y|ies)", criteria, re.I):
            out.append("US0480 has no criterion comparing instances by identity: a total "
                       "recomputed from the corpus under judgement always equals the "
                       "actual, so the new instance can never refuse")
        if not (re.search(r"\b(?:flat|unchanged)\b", criteria, re.I)
                and re.search(r"refus", criteria, re.I)):
            out.append("US0480 has no criterion refusing a swap that leaves the total "
                       "unchanged, which is the case a count cannot catch")
        # The escape is a DECLARATION, not a mention. US0480's own notes say the ratchet is
        # "not left CLI-only", and a bare phrase match let that sentence switch the rule off.
        cli_only = re.search(r"\b(?:is|remains|stays)\s+CLI-only\b", u480, re.I)
        if warnings_reach_no_blocking_lane(root) and not cli_only:
            for path, why in (
                    (".claude/skills/sdlc-studio/scripts/gate.py",
                     "gate.py counts only severity == \"error\" and discards every warning"),
                    (".githooks/pre-commit",
                     "the hook runs gate.py, not validate.py check")):
                if path not in affects:
                    out.append(f"US0480 must declare {path} in Affects, or state it is "
                               f"CLI-only: {why}, so changing validate's exit code alone "
                               f"refuses no commit")

    if u461 is not None and "US0480" not in u461:
        out.append("US0461 names no partner: US0480 builds the same ratchet and whichever "
                   "lands second must reuse this machinery rather than a second shape")

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
        if not any(_story_text(REPO, d) for d in ("US0461", "US0480", "US0482")):
            self.skipTest("all three ratchet stories are delivered and archived")
        self.assertEqual(check(REPO), [])


class RatchetStoryAgreementRules(unittest.TestCase):
    """Each rule against the shape the story actually had when it was filed."""

    def _root(self, **stories: str) -> Path:
        root = Path(tempfile.mkdtemp())
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True)
        for disp, text in stories.items():
            (d / f"{disp}-x.md").write_text(text, encoding="utf-8")
        scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        scripts.mkdir(parents=True)
        (scripts / "gate.py").write_text('if v["severity"] == "error":\n', encoding="utf-8")
        hooks = root / ".githooks"
        hooks.mkdir()
        (hooks / "pre-commit").write_text('python3 "$skill/gate.py" --root .\n', encoding="utf-8")
        return root

    def test_a_ratchet_on_a_recomputed_total_is_refused(self) -> None:
        root = self._root(US0480=_COUNT_BASED_480)
        found = " | ".join(check(root))
        self.assertIn("identity", found)
        self.assertIn("US0461", found)
        self.assertIn("reference state", found)

    def test_a_ratchet_that_reaches_no_blocking_lane_is_refused(self) -> None:
        root = self._root(US0480=_COUNT_BASED_480)
        found = " | ".join(check(root))
        self.assertIn("gate.py", found)
        self.assertIn(".githooks/pre-commit", found)

    def test_a_ratchet_stating_it_is_cli_only_is_not_asked_for_a_lane(self) -> None:
        root = self._root(US0480=_COUNT_BASED_480.replace(
            "## Acceptance Criteria", "The ratchet is CLI-only.\n\n## Acceptance Criteria"))
        self.assertNotIn("gate.py", " | ".join(check(root)))

    def test_the_paired_story_that_names_no_partner_is_refused(self) -> None:
        root = self._root(US0461=_UNPAIRED_461)
        self.assertIn("US0480", " | ".join(check(root)))

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


_COUNT_BASED_480 = """# US0480: validate ratchets the warnings against a recorded count

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, CHANGELOG.md
> **Points:** 5

## Acceptance Criteria

### AC1: a new warning instance refuses

- **Given** a workspace whose expected warning count is recomputed from the corpus
- **When** an artefact carries one new `affects-undeclared` warning
- **Then** validate exits non-zero
- **Verify:** pytest x.py::T::test_a_new_instance_refuses

### AC2: the expected count is recomputed from the corpus

- **Given** the corpus under judgement
- **When** the expected total is recomputed from it
- **Then** the actual total is compared against that expected total
- **Verify:** pytest x.py::T::test_the_count_is_recomputed
"""

_UNPAIRED_461 = """# US0461: verify_ac lint --ratchet refuses a duplicate group

> **Status:** Ready
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, sdlc-studio/.verify-lint-baseline.json
> **Points:** 5

## Acceptance Criteria

### AC1: an unbaselined duplicate group refuses

- **Given** a baseline recording the tolerated groups by identity
- **When** the ratchet runs
- **Then** an unrecorded group refuses
- **Verify:** pytest x.py::T::test_an_unbaselined_duplicate_refuses
"""

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
