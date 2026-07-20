"""BG0221: `refine --into` must MERGE a further request's epic-level criteria under the
existing `## Acceptance Criteria (Epic Level)` heading, not append a second one.

The gate this pins is the repo's own markdown lane: markdownlint MD024
(no-duplicate-heading) configured `siblings_only: true`. Two `##` headings with the
same text under the same `#` are siblings, so a second appended section fails the
pre-commit markdown lane - the tool's own output blocking the commit that ships it.

The rule is asserted two ways: a local implementation of MD024/siblings_only (always
runs, so the pin holds without Node), and the REAL `markdownlint` binary with the
repo's own `.markdownlint.json` when it is installed.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k refine
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # sibling helpers (loader, workspace)

import loader  # noqa: E402 - the canonical way to import a script under test
import workspace  # noqa: E402 - the dev-repo-only skip authority
from lib import sdlc_md  # noqa: E402

refine = loader.load_script("refine")

_ATX_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_EPIC_AC_HEADING = "## Acceptance Criteria (Epic Level)"


def md024_siblings_only(text: str) -> list[str]:
    """The headings that violate markdownlint MD024 with `siblings_only: true`: a heading
    whose text repeats an earlier heading at the SAME level under the SAME parent. Returns
    the offending heading texts, in order (empty when the document passes).

    A local re-implementation so the rule is pinned on any machine; `RealMarkdownlintTests`
    cross-checks it against the actual linter.
    """
    dupes: list[str] = []
    seen: dict[tuple[tuple[str, ...], int], set[str]] = {}
    path: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = _ATX_RE.match(line)
        if not m:
            continue
        level, title = len(m.group(1)), m.group(2).strip()
        parent = tuple(path[:level - 1])
        bucket = seen.setdefault((parent, level), set())
        if title in bucket:
            dupes.append(title)
        bucket.add(title)
        path = [*path[:level - 1], title]
    return dupes


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _cr(root: Path, cid: str, criteria: list[str]) -> None:
    """A refinable CR carrying its own `- [ ]` acceptance criteria, so a multi-story
    breakdown carries them to the epic (`_seed_epic_criteria`)."""
    body = "".join(f"- [ ] {c}\n" for c in criteria)
    _write(root / "sdlc-studio" / "change-requests" / f"{cid}-x.md",
           f"# CR-{cid[2:]}: {cid}\n\n> **Status:** Approved\n> **Priority:** P1\n"
           f"> **Type:** Improvement\n> **Size:** L\n\n## Summary\n\ns\n\n"
           f"## Acceptance Criteria\n\n{body}\n## Impact\n\ni\n")


def _two_requests_into_one_epic(root: Path) -> Path:
    """The BG0221 reproduction: CR0001 mints a batch epic (multi-story, so its criteria are
    carried to the epic), then CR0002 refines INTO that same epic, also multi-story."""
    _cr(root, "CR0001", ["the first request is satisfied", "and its second criterion too"])
    _cr(root, "CR0002", ["the second request is satisfied"])
    epic = refine.refine(root, "CR0001", "Batch epic",
                         [("A", 2, None), ("B", 3, None)])["epic"]
    refine.refine(root, "CR0002", None, [("C", 2, None), ("D", 3, None)], into_epic=epic)
    return sdlc_md.find_by_id(root, epic)[0]


class RefineIntoEpicCriteriaMergeTests(unittest.TestCase):
    """BG0221: a second `--into` refine merges its criteria under the one epic-level AC
    heading, keeping the epic clean under MD024/siblings_only."""

    def test_refine_into_does_not_duplicate_the_epic_ac_heading(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = _two_requests_into_one_epic(Path(d))
            text = path.read_text(encoding="utf-8")
            self.assertEqual(md024_siblings_only(text), [],
                             f"MD024 (siblings_only) violation in the epic:\n{text}")
            self.assertEqual(text.count(_EPIC_AC_HEADING), 1,
                             "the epic-level AC heading is written once, merged into")

    def test_refine_into_keeps_both_requests_criteria_under_the_one_heading(self) -> None:
        # Merging must not silently drop the joining request's criteria - the whole point
        # of carrying them is that the epic states its completion bar.
        with tempfile.TemporaryDirectory() as d:
            path = _two_requests_into_one_epic(Path(d))
            text = path.read_text(encoding="utf-8")
            for criterion in ("the first request is satisfied",
                              "and its second criterion too",
                              "the second request is satisfied"):
                self.assertIn(f"- [ ] {criterion}", text)
            head = text.index(_EPIC_AC_HEADING)
            tail = text.index("## Revision History")
            section = text[head:tail]
            self.assertIn("the second request is satisfied", section,
                          "the joining request's criteria land INSIDE the AC section")

    def test_refine_into_attributes_the_merged_criteria_to_their_request(self) -> None:
        # A shared batch epic delivers several requests; which criterion came from which
        # must stay readable after the merge.
        with tempfile.TemporaryDirectory() as d:
            path = _two_requests_into_one_epic(Path(d))
            text = path.read_text(encoding="utf-8")
            self.assertIn("### From CR0002", text)
            self.assertLess(text.index("### From CR0002"),
                            text.index("- [ ] the second request is satisfied"))

    def test_refine_into_thrice_stays_clean_under_md024(self) -> None:
        # Three requests in one batch epic: every added subheading must be distinct too.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _two_requests_into_one_epic(root)
            _cr(root, "CR0003", ["the third request is satisfied"])
            epic = sdlc_md.extract_record_id(path.stem)
            refine.refine(root, "CR0003", None, [("E", 2, None), ("F", 1, None)],
                          into_epic=epic)
            text = path.read_text(encoding="utf-8")
            self.assertEqual(md024_siblings_only(text), [])
            self.assertEqual(text.count(_EPIC_AC_HEADING), 1)
            self.assertIn("### From CR0003", text)

    def test_refine_single_story_into_leaves_the_epic_section_alone(self) -> None:
        # A SINGLE-story breakdown seeds the STORY's ACs, never the epic's - the merge
        # must not have widened what gets carried up.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _two_requests_into_one_epic(root)
            before = path.read_text(encoding="utf-8")
            _cr(root, "CR0004", ["a single-story request"])
            refine.refine(root, "CR0004", None, [("G", 2, None)],
                          into_epic=sdlc_md.extract_record_id(path.stem))
            after = path.read_text(encoding="utf-8")
            self.assertNotIn("a single-story request", after)
            self.assertEqual(before.count(_EPIC_AC_HEADING),
                             after.count(_EPIC_AC_HEADING))


    def test_refine_merging_the_same_request_twice_repeats_no_subheading(self) -> None:
        # Defensive: a repeated `### From CRxxxx` would be the same duplicate-sibling defect
        # one level down, so a second merge for a request extends its existing block.
        with tempfile.TemporaryDirectory() as d:
            path = _two_requests_into_one_epic(Path(d))
            refine._seed_epic_criteria(path, ["a later criterion"], "CR0002")
            text = path.read_text(encoding="utf-8")
            self.assertEqual(md024_siblings_only(text), [])
            self.assertEqual(text.count("### From CR0002"), 1)
            self.assertEqual(text.count(_EPIC_AC_HEADING), 1)
            block = text[text.index("### From CR0002"):]
            self.assertIn("- [ ] a later criterion", block.split("###")[1])
            self.assertEqual(text.count(refine._EPIC_AC_NOTE), 1,
                             "the closing note is written once and stays last")


class Md024HelperTests(unittest.TestCase):
    """The local MD024 implementation must actually detect the shape BG0221 produced,
    or the pin above is vacuous."""

    def test_refine_bug_shape_is_flagged_by_the_local_md024_rule(self) -> None:
        bad = ("# EP0001: e\n\n## Acceptance Criteria (Epic Level)\n\n- [ ] a\n\n"
               "## Acceptance Criteria (Epic Level)\n\n- [ ] b\n")
        self.assertEqual(md024_siblings_only(bad),
                         ["Acceptance Criteria (Epic Level)"])

    def test_refine_md024_allows_repeats_under_different_parents(self) -> None:
        # siblings_only: the same `###` under two different `##` parents is legal.
        ok = ("# t\n\n## One\n\n### Detail\n\n## Two\n\n### Detail\n")
        self.assertEqual(md024_siblings_only(ok), [])


class RealMarkdownlintTests(unittest.TestCase):
    """Cross-check against the actual gate: the repo's markdownlint with its own config."""

    BIN = workspace.REPO / "node_modules" / ".bin" / "markdownlint"
    CONFIG = workspace.REPO / ".markdownlint.json"

    def _md024_from_markdownlint(self, path: Path) -> list[str]:
        proc = subprocess.run(  # noqa: S603 - fixed local binary, generated fixture path
            [str(self.BIN), "--config", str(self.CONFIG), "--json", str(path)],
            capture_output=True, text=True, check=False)
        out = (proc.stdout or "") + (proc.stderr or "")
        try:
            findings = json.loads(out or "[]")
        except json.JSONDecodeError:
            self.fail(f"markdownlint gave no JSON:\n{out}")
        return [f["ruleNames"][0] for f in findings if "MD024" in f["ruleNames"]]

    def setUp(self) -> None:
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        if not self.BIN.is_file() or shutil.which("node") is None:
            self.skipTest("markdownlint not installed (run `npm install`)")

    def test_refine_into_epic_passes_the_real_markdownlint_md024_rule(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = _two_requests_into_one_epic(Path(d))
            self.assertEqual(self._md024_from_markdownlint(path), [],
                             f"the epic fails the real MD024 gate:\n"
                             f"{path.read_text(encoding='utf-8')}")

    def test_refine_bug_shape_really_fails_markdownlint(self) -> None:
        # Proves the real gate is the one being pinned, not an assertion that can never fire.
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "EP0001-e.md"
            bad.write_text("# EP0001: e\n\n## Acceptance Criteria (Epic Level)\n\n- [ ] a\n\n"
                           "## Acceptance Criteria (Epic Level)\n\n- [ ] b\n", encoding="utf-8")
            self.assertEqual(self._md024_from_markdownlint(bad), ["MD024"])


if __name__ == "__main__":
    unittest.main()
