"""refine's generated surfaces: the epic-level AC merge, the AC heading, and the epic's
derived T-shirt Size.

BG0221: `refine --into` must MERGE a further request's epic-level criteria under the
existing `## Acceptance Criteria (Epic Level)` heading, not append a second one.

BG0233: two mutants survived the close-time mutation run over refine.py, both real
coverage gaps. An invert-guard on `_ac_heading`'s length test truncated short headings
and left long ones whole with nothing noticing, and `_tshirt_for` (the Size an epic is
born with, which feeds sprint planning) was referenced by no test at all. Both are pinned
below: the heading at its length boundary, the Size at every band edge.

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

import argparse

import contextlib
import io
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

try:
    import yaml as _yaml  # noqa: F401 - the recorded opt-out is unreadable without PyYAML
    HAVE_YAML = True
except ImportError:  # pragma: no cover
    HAVE_YAML = False

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
    breakdown carries them to the epic (`_seed_epic_criteria`). It declares a resolvable
    `Affects` (and drops the file on disk), so a story minted with no Affects of its own is
    SEEDED from the request (US0410) rather than refused."""
    body = "".join(f"- [ ] {c}\n" for c in criteria)
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / f"{cid}.py").write_text("", encoding="utf-8")
    _write(root / "sdlc-studio" / "change-requests" / f"{cid}-x.md",
           f"# CR-{cid[2:]}: {cid}\n\n> **Status:** Approved\n> **Priority:** P1\n"
           f"> **Type:** Improvement\n> **Size:** L\n> **Affects:** src/{cid}.py\n\n## Summary\n\ns\n\n"
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


def _phrase(length: int) -> str:
    """A space-separated phrase of EXACTLY `length` characters, free of punctuation.

    Whole five-letter words, the last one padded with `z`s so the total is exact - so a
    test can sit a criterion ON the limit, or one character over it, without counting
    characters by hand. `PhraseHelperTests` pins the exactness, or every boundary case
    built from it would be measuring the wrong boundary.
    """
    if length < 5:
        return "a" * length
    words = ["alpha"] * max(1, (length + 1) // 6)
    words[-1] += "z" * (length - len(" ".join(words)))
    return " ".join(words)


class PhraseHelperTests(unittest.TestCase):
    """`_phrase` must produce the exact length it claims, or the boundary tests below
    assert against a boundary that is not the one in the code."""

    def test_refine_phrase_helper_is_exact_at_the_lengths_the_tests_use(self) -> None:
        for n in (35, 39, 40, 41, 99, 100, 101):
            self.assertEqual(len(_phrase(n)), n, f"_phrase({n}) is not {n} characters")
            self.assertEqual(_phrase(n), " ".join(_phrase(n).split()),
                             "no doubled or trailing whitespace")


class AcHeadingTruncationTests(unittest.TestCase):
    """BG0233: `_ac_heading` truncates ONLY what is over the limit, at a word boundary,
    and never leaves trailing punctuation.

    The invert-guard mutant on the length test is killed twice over: a criterion at the
    limit must come back word-for-word (the mutant truncates it), and one over the limit
    must come back shortened (the mutant leaves it whole).
    """

    LIMIT = 40

    def test_refine_ac_heading_leaves_a_criterion_at_the_limit_word_for_word(self) -> None:
        at = _phrase(self.LIMIT)
        self.assertEqual(refine._ac_heading(at, self.LIMIT), at,
                         "a criterion that fits keeps every word")

    def test_refine_ac_heading_truncates_one_character_over_the_limit(self) -> None:
        over = _phrase(self.LIMIT + 1)
        head = refine._ac_heading(over, self.LIMIT)
        self.assertLessEqual(len(head), self.LIMIT, "an over-long heading is truncated")
        self.assertNotEqual(head, over)
        self.assertTrue(over.startswith(head), "truncation keeps a prefix of the criterion")
        self.assertEqual(over[len(head)], " ", "the cut lands on a word boundary")

    def test_refine_ac_heading_truncation_leaves_no_trailing_punctuation(self) -> None:
        # The cut can expose punctuation the first strip never saw (MD026: no trailing
        # punctuation in a heading), so the second strip is the property, not a tidy-up.
        criterion = "alpha, beta, gamma, delta, epsilon, zeta, eta"
        head = refine._ac_heading(criterion, self.LIMIT)
        self.assertEqual(head, "alpha, beta, gamma, delta, epsilon")
        self.assertLessEqual(len(head), self.LIMIT)
        self.assertFalse(head.endswith((",", ".", ";", ":", "!", "?")))

    def test_refine_ac_heading_keeps_the_last_word_when_the_stripped_form_fits(self) -> None:
        # The stated behaviour of stripping BEFORE the length test: a criterion whose RAW
        # form is over the limit but whose collapsed form fits keeps its last word.
        raw = "alpha  alpha  alpha  alpha  alpha  alpha."
        self.assertGreater(len(raw), self.LIMIT, "the raw form really is over the limit")
        head = refine._ac_heading(raw, self.LIMIT)
        self.assertEqual(head, "alpha alpha alpha alpha alpha alpha")
        self.assertTrue(head.endswith("alpha"), "the last word is not lost to truncation")

    def test_refine_ac_heading_applies_the_same_boundary_at_its_default_limit(self) -> None:
        # The default (100) is the limit every generated AC heading actually gets.
        self.assertEqual(refine._ac_heading(_phrase(100)), _phrase(100))
        self.assertLessEqual(len(refine._ac_heading(_phrase(101))), 100)
        self.assertNotEqual(refine._ac_heading(_phrase(101)), _phrase(101))

    def test_refine_seeded_story_ac_heading_is_truncated_on_the_real_path(self) -> None:
        # End to end: a single-story refine seeds the STORY's ACs from the request's
        # criteria, and the `### ACn:` heading it writes is the truncated one.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            long_criterion = _phrase(140)
            _cr(root, "CR0009", [long_criterion])
            res = refine.refine(root, "CR0009", "One story epic", [("Only", 3, None)])
            story = sdlc_md.find_by_id(root, res["stories"][0])[0]
            heading = next(ln for ln in story.read_text(encoding="utf-8").splitlines()
                           if ln.startswith("### AC1:"))
            title = heading[len("### AC1:"):].strip()
            self.assertLessEqual(len(title), 100)
            self.assertTrue(long_criterion.startswith(title))


class EpicTshirtBandTests(unittest.TestCase):
    """BG0233: the T-shirt Size an epic is born with, derived from its stories' point
    total. Pinned at every band EDGE - a no-op mapper or an off-by-one band shows only
    there - and once through the real creation path, so the derivation and the field it
    lands in are both covered."""

    def test_refine_tshirt_bands_hold_at_each_edge(self) -> None:
        for total, size in ((0, "S"), (1, "S"), (3, "S"), (4, "M"), (8, "M"),
                            (9, "L"), (20, "L"), (21, "XL"), (100, "XL")):
            self.assertEqual(refine._tshirt_for(total), size,
                             f"{total} points must derive Size {size}")

    def test_refine_epic_is_born_with_the_size_its_points_derive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0005", ["a criterion"])
            # 5 points total sits in the M band; 21 in XL. Both through `refine`, so the
            # derived Size is read off the epic on disk, not off the helper.
            m_epic = refine.refine(root, "CR0005", "Small batch",
                                   [("A", 2, None), ("B", 3, None)])["epic"]
            _cr(root, "CR0006", ["another criterion"])
            # Captured, not silenced: a 13-point unit is above the split threshold, so the
            # filer warns. That warning is correct and wanted - it is asserted below - but a
            # green suite must say nothing, or a real error hides in the noise.
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                xl_epic = refine.refine(root, "CR0006", "Large batch",
                                        [("C", 8, None), ("D", 13, None)])["epic"]
            self.assertIn("should be SPLIT", buf.getvalue(),
                          "the over-threshold unit was written without the split warning")
            for epic_id, size in ((m_epic, "M"), (xl_epic, "XL")):
                text = sdlc_md.find_by_id(root, epic_id)[0].read_text(encoding="utf-8")
                self.assertEqual(sdlc_md.read_size(text), size,
                                 f"{epic_id} must be born Size {size}")


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


class AffectsValidatedAtMintTests(unittest.TestCase):
    """US0324: refine mints its epic and stories under one rollback guard, so a bad `Affects` in
    the LAST story of a batch must refuse before the FIRST artefact exists - the run stops rather
    than rolling back what it already wrote."""

    def test_apply_refuses_the_whole_batch_before_minting_the_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            (root / "src").mkdir(exist_ok=True)   # _cr already created src for its own Affects
            (root / "src" / "real.py").write_text("", encoding="utf-8")
            cr_before = (root / "sdlc-studio" / "change-requests"
                         / "CR0001-x.md").read_text(encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                refine.refine(root, "CR0001", "Batch epic",
                              [("A", 2, None), ("B", 3, "src/real.py"),
                               ("C", 2, "wrongdir/ghost.py")],  # only the third is unresolvable
                              skip_personas=True)
            msg = str(cm.exception)
            self.assertIn("wrongdir/ghost.py", msg)            # names the offending path
            self.assertIn("'C'", msg)                          # ... and the story that carried it
            # the tree is untouched: no epic, none of the three stories, CR unchanged
            self.assertFalse((root / "sdlc-studio" / "epics").exists()
                             and any((root / "sdlc-studio" / "epics").glob("EP*.md")))
            stories_dir = root / "sdlc-studio" / "stories"
            minted = list(stories_dir.glob("US*.md")) if stories_dir.exists() else []
            self.assertEqual(minted, [])
            self.assertEqual((root / "sdlc-studio" / "change-requests"
                              / "CR0001-x.md").read_text(encoding="utf-8"), cr_before)


def _cr_no_affects(root: Path, cid: str = "CR0001") -> None:
    """A refinable CR that declares NO Affects - so a story minted with none of its own has
    nothing to seed from, the case US0410 refuses (or, opted out, warns)."""
    _write(root / "sdlc-studio" / "change-requests" / f"{cid}-x.md",
           f"# CR-{cid[2:]}: {cid}\n\n> **Status:** Approved\n> **Priority:** P1\n"
           f"> **Type:** Improvement\n> **Size:** L\n\n## Summary\n\ns\n\n## Impact\n\ni\n")


class AffectsRequiredAtRefineTests(unittest.TestCase):
    """US0410: refine requires OR inherits an Affects per story, so a minted story is plannable
    the moment it exists rather than a grooming task that reads as ready work."""

    def _stories(self, root: Path) -> list[Path]:
        d = root / "sdlc-studio" / "stories"
        return [p for p in d.glob("US*.md")] if d.exists() else []

    def test_a_story_with_no_affects_is_refused_naming_the_fix(self) -> None:
        # No Affects on the story AND none on the request to seed from: refused before any mint,
        # naming the story and how to supply an Affects (the grooming-refusal idiom).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_no_affects(root)
            with self.assertRaises(ValueError) as cm:
                refine.refine(root, "CR0001", "The epic", [("A story", 3, None)],
                              skip_personas=True)
            msg = str(cm.exception)
            self.assertIn("A story", msg)          # names the offending story
            self.assertIn("Affects", msg)          # ... and what is missing
            self.assertIn("inherit", msg)          # ... and how to supply it
            # nothing minted: no epic, no story, the CR stays undecomposed
            self.assertEqual(self._stories(root), [])
            self.assertFalse(any((root / "sdlc-studio" / "epics").glob("EP*.md"))
                             if (root / "sdlc-studio" / "epics").exists() else False)
            self.assertEqual(sdlc_md.decomposed_ids(
                sdlc_md.find_by_id(root, "CR0001")[0].read_text(encoding="utf-8")), [])

    def test_a_story_inherits_the_parent_affects_and_is_plannable(self) -> None:
        # A request naming three files; a story asks to inherit them. The minted story carries the
        # parent-derived Affects and the planner does not refuse it as lacking one.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("a.py", "b.py", "c.py"):
                (root / "src").mkdir(parents=True, exist_ok=True)
                (root / "src" / name).write_text("", encoding="utf-8")
            _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
                   "# CR-0001: X\n\n> **Status:** Approved\n> **Priority:** P1\n"
                   "> **Type:** Improvement\n> **Size:** L\n"
                   "> **Affects:** src/a.py, src/b.py, src/c.py\n\n## Summary\n\ns\n\n## Impact\n\ni\n")
            res = refine.refine(root, "CR0001", "The epic", [("Index it", 3, "inherit")],
                                skip_personas=True)
            story = sdlc_md.find_by_id(root, res["stories"][0])[0]
            body = story.read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.affects_files(body),
                             ["src/a.py", "src/b.py", "src/c.py"])  # derived from the parent
            # plannable: the planner's own breakdown does not report it ungroomed for Affects
            sprint = loader.load_script("sprint")
            bd = sprint.breakdown(root, [{"id": res["stories"][0], "type": "story",
                                          "path": str(story)}], skip_personas=True)
            # FOR AFFECTS, which is this test's subject and what the comment above says. A
            # refined skeleton IS ungroomed on its criteria - that is the whole point of
            # `refine --into`, whose output carries `{{placeholder}}` ACs for a human to
            # author - so asserting the list is EMPTY asserted the opposite of the shipped
            # contract, and the grooming gate had to be blind to criteria for it to hold.
            missing = [m for u in bd["ungroomed"] for m in u["missing"]]
            self.assertNotIn("Affects", missing,
                             "planner refused a story refine called plannable, FOR AFFECTS")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed - the recorded opt-out is unreadable")
    def test_the_opt_out_warns_instead_of_refusing(self) -> None:
        # A project that records `sprint.breakdown: judgement` keeps the old lenient behaviour:
        # a no-Affects story is minted with a warning rather than refused.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_no_affects(root)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "sprint:\n  breakdown: judgement\n", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                res = refine.refine(root, "CR0001", "The epic", [("A story", 3, None)],
                                    skip_personas=True)
            self.assertEqual(len(res["stories"]), 1)          # minted, not refused
            self.assertTrue(self._stories(root))
            self.assertIn("no Affects", err.getvalue())       # ... but never quietly


class InheritSubsetTests(unittest.TestCase):
    """BG0273: `inherit:subset` took three shortcuts the bare `inherit` did not.

    It skipped the parent-declares-none refusal (a subset of nothing was accepted as an
    inheritance), it never checked the named subset was WITHIN the parent's Affects (so
    `inherit:` could ADD a path and call it a narrowing), and the bare keyword was compared
    case-sensitively, so `INHERIT` fell through to the explicit path and minted a story whose
    Affects was the literal word.
    """

    def _parent(self, root: Path, affects: str = "src/a.py, src/b.py, src/c.py") -> None:
        for name in ("a.py", "b.py", "c.py"):
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src" / name).write_text("", encoding="utf-8")
        _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
               "# CR-0001: X\n\n> **Status:** Approved\n> **Priority:** P1\n"
               "> **Type:** Improvement\n> **Size:** L\n"
               f"> **Affects:** {affects}\n\n## Summary\n\ns\n\n## Impact\n\ni\n")

    def test_inherit_subset_from_a_request_that_declares_none_is_refused(self) -> None:
        # The parent-declares-none refusal is the bare keyword's; the narrowed form skipped it
        # entirely and returned the subset as though it had been inherited from something.
        with self.assertRaises(ValueError) as cm:
            refine.resolve_story_affects("CR0001", "", "inherit:src/a.py")
        msg = str(cm.exception)
        self.assertIn("CR0001", msg)                 # names the request that declares none
        self.assertIn("declares none", msg)
        # ... and the same refusal reaches the mint path, before anything is written
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_no_affects(root)
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src" / "a.py").write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                refine.refine(root, "CR0001", "The epic", [("S", 3, "inherit:src/a.py")],
                              skip_personas=True)
            self.assertFalse(any((root / "sdlc-studio" / "stories").glob("US*.md"))
                             if (root / "sdlc-studio" / "stories").exists() else False)

    def test_a_subset_naming_a_path_outside_the_parent_is_refused(self) -> None:
        # `inherit:` NARROWS. A path the parent never declared is an addition wearing the
        # inheritance keyword - the story's footprint would claim a provenance it has not got.
        with self.assertRaises(ValueError) as cm:
            refine.resolve_story_affects("CR0001", "src/a.py, src/b.py",
                                         "inherit:src/a.py, src/elsewhere.py")
        msg = str(cm.exception)
        self.assertIn("src/elsewhere.py", msg)       # the offending path, named
        self.assertNotIn("src/a.py,", msg.split("is not")[0])   # not the one that was fine

    def test_a_subset_the_affects_parser_cannot_read_as_a_path_is_refused(self) -> None:
        # Containment is judged by the parser the planner uses, and prose is not a path in it.
        # Admitting an unreadable token would narrow the parent to something the planner reads
        # as no footprint at all - an unplannable story, which is what the Affects gate exists
        # to prevent.
        for token in ("everything", "the parser"):
            with self.subTest(token=token):
                with self.assertRaises(ValueError) as cm:
                    refine.resolve_story_affects("CR0001", "src/a.py, src/b.py",
                                                 f"inherit:{token}")
                self.assertIn(token, str(cm.exception))
        # a readable path in the same list does not launder the unreadable one beside it
        with self.assertRaises(ValueError) as cm:
            refine.resolve_story_affects("CR0001", "src/a.py", "inherit:src/a.py, everything")
        self.assertIn("everything", str(cm.exception))
        # ... and a backtick-wrapped spelling of a parent path is the SAME path, not an addition
        value, mode = refine.resolve_story_affects("CR0001", "src/a.py, src/b.py",
                                                   "`src/a.py`")
        self.assertEqual((value, mode), ("`src/a.py`", "explicit"))
        self.assertEqual(refine.resolve_story_affects("CR0001", "src/a.py, src/b.py",
                                                      "inherit:`src/a.py`"),
                         ("`src/a.py`", "inherited"))

    def test_a_subset_within_the_parent_narrows_it(self) -> None:
        # The positive control: a genuine narrowing still resolves, to the SUBSET (not the
        # parent's whole footprint), and only the named files reach the minted story.
        value, mode = refine.resolve_story_affects(
            "CR0001", "src/a.py, src/b.py, src/c.py", "inherit:src/b.py")
        self.assertEqual(value, "src/b.py")
        self.assertEqual(mode, "inherited")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._parent(root)
            res = refine.refine(root, "CR0001", "The epic",
                                [("Narrow it", 3, "inherit:src/b.py, src/c.py")],
                                skip_personas=True)
            story = sdlc_md.find_by_id(root, res["stories"][0])[0]
            self.assertEqual(sdlc_md.affects_files(story.read_text(encoding="utf-8")),
                             ["src/b.py", "src/c.py"])

    def test_the_inherit_keyword_is_matched_in_any_case(self) -> None:
        # `INHERIT` is the same instruction typed differently. Case-sensitively matched, it
        # fell through to the explicit path and the story's Affects became the word itself.
        for spelling in ("INHERIT", "Inherit", "iNhErIt"):
            with self.subTest(spelling=spelling):
                value, mode = refine.resolve_story_affects(
                    "CR0001", "src/a.py, src/b.py", spelling)
                self.assertEqual(value, "src/a.py, src/b.py")
                self.assertEqual(mode, "inherited")
        # narrowed, in any case, and it still refuses a path outside the parent
        value, mode = refine.resolve_story_affects("CR0001", "src/a.py, src/b.py",
                                                   "INHERIT:src/a.py")
        self.assertEqual((value, mode), ("src/a.py", "inherited"))
        with self.assertRaises(ValueError):
            refine.resolve_story_affects("CR0001", "src/a.py", "INHERIT:src/zzz.py")
        # end to end: the minted story carries the parent's paths, never the keyword
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._parent(root)
            res = refine.refine(root, "CR0001", "The epic", [("Index it", 3, "INHERIT")],
                                skip_personas=True)
            body = sdlc_md.find_by_id(root, res["stories"][0])[0].read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.affects_files(body),
                             ["src/a.py", "src/b.py", "src/c.py"])
            self.assertNotIn("INHERIT", body)

    def test_a_path_beginning_with_the_keyword_is_still_an_explicit_path(self) -> None:
        # The keyword match must not swallow a real path: `inheritance.py` is a file.
        value, mode = refine.resolve_story_affects("CR0001", "src/a.py", "src/inheritance.py")
        self.assertEqual((value, mode), ("src/inheritance.py", "explicit"))


class BreakdownFileTests(unittest.TestCase):
    """US0353: `refine apply` and `refine add` take the whole breakdown as a JSON or YAML file.

    A bulk refine was long fragile shell lines (one run: ~56 stories across 12 calls), where a
    typo in a points value was found only at mint time and the breakdown could not be reviewed
    or version-controlled as a unit before it ran. The file is validated WHOLE - every fault in
    one refusal, nothing minted - which is the `--story` form's fail-empty discipline applied to
    the input a bulk refine actually arrives as.
    """

    def _bd(self, root: Path, name: str, payload: str) -> Path:
        p = root / name
        p.write_text(payload, encoding="utf-8")
        return p

    def _cli(self, argv: list[str]) -> tuple[int, str]:
        """(exit code, everything the command printed). Both streams are captured: a green
        suite must be silent, and refine writes its seeded-Affects notes and its refusals to
        stderr, so an uncaptured call leaks lines that read like failures on a passing run."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = refine.main(argv)
        return rc, out.getvalue() + err.getvalue()

    def _units(self, root: Path) -> list[tuple[str, str, str]]:
        """(title, points, affects) of every minted story, in id order - the comparable
        shape of a decomposition, free of the ids two runs cannot share."""
        out = []
        for p in sorted((root / "sdlc-studio" / "stories").glob("US*.md")):
            text = p.read_text(encoding="utf-8")
            out.append((sdlc_md.extract_h1_title(text).split(": ", 1)[1],
                        sdlc_md.extract_field(text, "Points"),
                        sdlc_md.extract_field(text, "Affects")))
        return out

    def test_a_breakdown_file_mints_the_same_units_as_repeated_story_flags(self) -> None:
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            flags_root, file_root = Path(d1), Path(d2)
            for root in (flags_root, file_root):
                _cr(root, "CR0001", ["the request is satisfied"])
            rc, _ = self._cli(["apply", "--request", "CR0001", "--root", str(flags_root),
                               "--epic-title", "The epic", "--skip-personas",
                               "--story", "First|2|src/CR0001.py", "--story", "Second|3"])
            self.assertEqual(rc, 0)
            self._bd(file_root, "bd.json", json.dumps({
                "epic-title": "The epic",
                "stories": [{"title": "First", "points": 2, "affects": "src/CR0001.py"},
                            {"title": "Second", "points": 3}]}))
            rc, _ = self._cli(["apply", "--request", "CR0001", "--root", str(file_root),
                               "--skip-personas", "--breakdown", str(file_root / "bd.json")])
            self.assertEqual(rc, 0)
            self.assertEqual(self._units(file_root), self._units(flags_root))
            self.assertEqual(len(self._units(file_root)), 2)
            # ... and the epic the two forms produce carries the same title and point total
            for root in (flags_root, file_root):
                epic = next((root / "sdlc-studio" / "epics").glob("EP*.md"))
                self.assertIn("The epic", epic.read_text(encoding="utf-8"))

    def test_an_invalid_breakdown_mints_nothing_and_names_every_fault(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            bd = self._bd(root, "bd.json", json.dumps({
                "epic-title": "The epic",
                "stories": [{"title": "Fine", "points": 2},
                            {"title": "Off scale", "points": 7},
                            {"points": 3},
                            {"title": "Typo", "points": 2, "pionts": 1}]}))
            rc, msg = self._cli(["apply", "--request", "CR0001", "--root", str(root),
                                 "--skip-personas", "--breakdown", str(bd)])
            self.assertEqual(rc, 2)
            self.assertIn("stories[1]", msg)      # the off-scale points
            self.assertIn("stories[2]", msg)      # the missing title
            self.assertIn("stories[3]", msg)      # the misspelled key
            self.assertIn("3 fault(s)", msg)      # every fault in ONE refusal, not the first
            # fail-empty: no epic, no story, the request still undecomposed
            self.assertEqual(list((root / "sdlc-studio" / "stories").glob("US*.md")), [])
            self.assertFalse((root / "sdlc-studio" / "epics").exists()
                             and list((root / "sdlc-studio" / "epics").glob("EP*.md")))

    def test_the_file_may_name_the_into_target(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the first request is satisfied"])
            _cr(root, "CR0002", ["the second request is satisfied"])
            epic = refine.refine(root, "CR0001", "Batch epic", [("A", 2, None)],
                                 skip_personas=True)["epic"]
            bd = self._bd(root, "bd.json", json.dumps(
                {"into": epic, "stories": [{"title": "B", "points": 3}]}))
            rc, _ = self._cli(["apply", "--request", "CR0002", "--root", str(root),
                               "--skip-personas", "--breakdown", str(bd)])
            self.assertEqual(rc, 0)
            self.assertEqual([sid for sid, _ in sdlc_md.children_of(root, epic)],
                             ["US0001", "US0002"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_yaml_and_json_forms_are_equivalent(self) -> None:
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            json_root, yaml_root = Path(d1), Path(d2)
            for root in (json_root, yaml_root):
                _cr(root, "CR0001", ["the request is satisfied"])
            self._bd(json_root, "bd.json", json.dumps({
                "epic-title": "The epic",
                "stories": [{"title": "First", "points": 2, "affects": "src/CR0001.py"}]}))
            self._bd(yaml_root, "bd.yaml",
                     "epic-title: The epic\nstories:\n  - title: First\n    points: 2\n"
                     "    affects: src/CR0001.py\n")
            for root, name in ((json_root, "bd.json"), (yaml_root, "bd.yaml")):
                rc, _ = self._cli(["apply", "--request", "CR0001", "--root", str(root),
                                   "--skip-personas", "--breakdown", str(root / name)])
                self.assertEqual(rc, 0)
            self.assertEqual(self._units(yaml_root), self._units(json_root))

    def test_breakdown_and_story_flags_together_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            bd = self._bd(root, "bd.json", json.dumps(
                {"epic-title": "The epic", "stories": [{"title": "First", "points": 2}]}))
            rc, msg = self._cli(["apply", "--request", "CR0001", "--root", str(root),
                                 "--skip-personas", "--breakdown", str(bd),
                                 "--story", "Second|3"])
            self.assertEqual(rc, 2)
            self.assertIn("alternatives", msg)
            self.assertEqual(list((root / "sdlc-studio" / "stories").glob("US*.md")), [])

    def test_add_takes_a_breakdown_and_its_epic_title(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            refine.refine(root, "CR0001", "First slice", [("A", 2, None)], skip_personas=True)
            bd = self._bd(root, "bd.yaml" if HAVE_YAML else "bd.json",
                          "epic-title: Second slice\nstories:\n  - title: B\n    points: 3\n"
                          if HAVE_YAML else json.dumps(
                              {"epic-title": "Second slice",
                               "stories": [{"title": "B", "points": 3}]}))
            rc, _ = self._cli(["add", "--request", "CR0001", "--root", str(root),
                               "--breakdown", str(bd)])
            self.assertEqual(rc, 0)
            titles = [t for t, _, _ in self._units(root)]
            self.assertEqual(titles, ["A", "B"])
            epics = sorted(p.read_text(encoding="utf-8")
                           for p in (root / "sdlc-studio" / "epics").glob("EP*.md"))
            self.assertTrue(any("Second slice" in e for e in epics))

    def test_add_refuses_a_breakdown_that_names_an_into_target(self) -> None:
        # `add` mints a further epic and has no --into; a file carrying one describes a
        # different command, so it is refused rather than quietly ignored.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            refine.refine(root, "CR0001", "First slice", [("A", 2, None)], skip_personas=True)
            bd = self._bd(root, "bd.json", json.dumps(
                {"into": "EP0001", "stories": [{"title": "B", "points": 3}]}))
            rc, msg = self._cli(["add", "--request", "CR0001", "--root", str(root),
                                 "--breakdown", str(bd)])
            self.assertEqual(rc, 2)
            self.assertIn("no `into` target", msg)
            self.assertEqual([t for t, _, _ in self._units(root)], ["A"])

    def test_a_missing_or_unreadable_breakdown_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError) as cm:
                refine.load_breakdown(root / "absent.json")
            self.assertIn("absent.json", str(cm.exception))
            bad = self._bd(root, "bd.json", "{not json")
            with self.assertRaises(ValueError) as cm:
                refine.load_breakdown(bad)
            self.assertIn("not valid JSON", str(cm.exception))
            empty = self._bd(root, "empty.json", json.dumps({"epic-title": "x", "stories": []}))
            with self.assertRaises(ValueError) as cm:
                refine.load_breakdown(empty)
            self.assertIn("stories", str(cm.exception))

    def test_a_story_may_be_the_same_pipe_spec_the_flag_takes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = self._bd(root, "bd.json", json.dumps(
                {"epic-title": "The epic", "stories": ["First|2|src/a.py", "Second|3"]}))
            self.assertEqual(refine.load_breakdown(bd)["stories"],
                             [("First", 2, "src/a.py"), ("Second", 3, None)])


class SeededAcShapeTests(unittest.TestCase):
    """BG0291: a seeded AC block used to carry three defects in four lines - the heading
    repeated its own `ACn:` label (the seed prepends one to a source that already had it),
    the `Then` was the heading restated (a criterion that states its own name asserts
    nothing observable), and the whole thing read as authored while being a transcription.

    Worse than the ungroomed marker it replaces: the marker is honestly empty and reads as
    work owed, this looked groomed.
    """

    def _story_text(self, root: Path, res) -> str:
        return sdlc_md.find_by_id(root, res["stories"][0])[0].read_text(encoding="utf-8")

    def _seeded(self, root: Path, criteria: list[str]) -> str:
        _cr(root, "CR0001", criteria)
        res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)],
                            skip_personas=True)
        return self._story_text(root, res)

    def test_the_label_is_not_doubled(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            text = self._seeded(Path(d), ["AC1: plan-time overlap detection without verifiers",
                                          "**AC2** - the second criterion"])
            headings = [ln for ln in text.splitlines() if ln.startswith("### AC")]
            self.assertEqual(headings,
                             ["### AC1: plan-time overlap detection without verifiers",
                              "### AC2: the second criterion"])
            for h in headings:
                with self.subTest(heading=h):
                    self.assertEqual(len(re.findall(r"AC\d", h)), 1, "label repeated in heading")

    def test_a_criterion_that_is_only_a_label_keeps_its_text(self) -> None:
        # The strip must not empty a heading: `AC1:` alone is a poor criterion, but a heading
        # with nothing after the label is a malformed artefact.
        self.assertEqual(refine._strip_ac_label("AC1:"), "AC1:")
        # ... and a mid-sentence mention is not a label at all
        self.assertEqual(refine._strip_ac_label("the gate reports AC2: unresolved"),
                         "the gate reports AC2: unresolved")

    def test_the_then_clause_is_not_the_heading(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            text = self._seeded(Path(d), ["the batch gate refuses an ungroomed unit"])
            ac = text[text.index("## Acceptance Criteria"):]
            heading = next(ln for ln in ac.splitlines() if ln.startswith("### AC1:"))
            then = next(ln for ln in ac.splitlines() if ln.startswith("- **Then**"))
            self.assertNotIn(heading.split(": ", 1)[1], then)
            self.assertIn("{{", then)     # a placeholder: work owed, not an assertion
            self.assertIn("{{executable check}}", ac)   # the Verify stays the author's job

    def test_a_truncated_criterion_is_still_transcribed_in_full(self) -> None:
        """The Then carried the whole criterion, so making it a placeholder must not lose a
        long one that the heading truncates."""
        long_criterion = ("the planner reads the TSD and names the interface each unit touches "
                          "so a reviewer can tell a described change from an asserted one, in "
                          "one line per unit and without opening the diff")
        with tempfile.TemporaryDirectory() as d:
            text = self._seeded(Path(d), [long_criterion])
            self.assertIn(long_criterion, text)
            heading = next(ln for ln in text.splitlines() if ln.startswith("### AC1:"))
            self.assertLess(len(heading), len(long_criterion))   # ... and still a short heading

    def test_no_story_gets_a_siblings_criterion(self) -> None:
        """3 criteria, 2 stories: no story may claim a criterion whose slice is undetermined.
        The mapping is not derivable, so the marker is used instead of a guess and the epic
        carries the list whole.

        Characterisation, not a repair: the multi-story guard already held (BG0205) - the
        defect BG0291 fixes is in the SINGLE-story seed's shape. Pinned because the bug names
        it and because nothing else asserts the criteria are not merely dropped.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            criteria = ["the first criterion", "the second criterion", "the third criterion"]
            _cr(root, "CR0001", criteria)
            res = refine.refine(root, "CR0001", "The epic",
                                [("First", 2, None), ("Second", 3, None)], skip_personas=True)
            for sid in res["stories"]:
                text = sdlc_md.find_by_id(root, sid)[0].read_text(encoding="utf-8")
                with self.subTest(story=sid):
                    self.assertIn(sdlc_md.UNGROOMED_AC_TOKEN, text)
                    for c in criteria:
                        self.assertNotIn(c, text)
            epic = sdlc_md.find_by_id(root, res["epic"])[0].read_text(encoding="utf-8")
            for c in criteria:      # not mis-assigned AND not lost
                self.assertIn(f"- [ ] {c}", epic)


class UngroomedMarkerTests(unittest.TestCase):
    """US0411: a story refine mints without seeded criteria carries an explicit ungroomed
    grooming-placeholder marker in its AC block, not a bare `{{placeholder}}` reading as content."""

    def test_a_refined_story_carries_an_ungroomed_marker(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # A multi-story breakdown seeds no story-level criteria (the epic carries them), so
            # every minted story is ungroomed and takes the marker.
            _cr(root, "CR0001", ["the request is satisfied"])
            res = refine.refine(root, "CR0001", "The epic",
                                [("A", 2, None), ("B", 3, None)], skip_personas=True)
            for sid in res["stories"]:
                body = sdlc_md.find_by_id(root, sid)[0].read_text(encoding="utf-8")
                ac = body[body.index("## Acceptance Criteria"):]
                self.assertIn(sdlc_md.UNGROOMED_AC_TOKEN, ac)   # the explicit marker
                self.assertNotIn("{{", ac)                      # no bare placeholder as content

    def test_marker_names_the_story_template_and_reference_verify(self) -> None:
        """MUTANT: revert the marker to the bare instruction.

        An author meeting it needs two things the token alone does not give them: the SHAPE a
        criterion takes and how to write a `Verify:` that runs. Both targets are asserted to
        EXIST as well as be named - a marker routing to a missing file sends the author nowhere,
        which is worse than not routing at all.
        """
        skill = Path(__file__).resolve().parents[1].parent
        for target in ("templates/core/story.md", "reference-verify.md"):
            with self.subTest(target=target):
                self.assertIn(target, sdlc_md.UNGROOMED_AC_MARKER,
                              f"the marker does not route to {target}")
                self.assertTrue((skill / target).is_file(),
                                f"the marker routes to {target}, which does not exist")

    def test_the_ungroomed_marker_keeps_a_blank_line_before_the_next_heading(self) -> None:
        # The closing review caught this: the marker was glued to `## Revision History` (single
        # newline), failing markdownlint MD022 on every ungroomed mint.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            res = refine.refine(root, "CR0001", "The epic",
                                [("A", 2, None), ("B", 3, None)], skip_personas=True)
            for sid in res["stories"]:
                body = sdlc_md.find_by_id(root, sid)[0].read_text(encoding="utf-8")
                self.assertNotIn(sdlc_md.UNGROOMED_AC_MARKER + "\n## Revision History", body)
                self.assertIn("\n\n## Revision History", body)   # a blank line precedes it


PERSONA_INDEX = (
    "# Persona Index\n\n"
    "## Primary (the design target)\n\n"
    "- [Maya Okafor](maya-okafor-founder-engineer.md) - solo founder-engineer. Well-formed.\n\n"
    "## Negative (deliberately not designed for)\n\n"
    "- [Trevor Hale](trevor-hale-enterprise-pm.md) - enterprise delivery manager.\n"
)


def _registry(root: Path) -> None:
    """Give the fixture project a design-persona registry to resolve against."""
    pdir = root / "sdlc-studio" / "personas"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "index.md").write_text(PERSONA_INDEX, encoding="utf-8")
    for stem in ("maya-okafor-founder-engineer", "trevor-hale-enterprise-pm"):
        (pdir / f"{stem}.md").write_text(f"# {stem}\n", encoding="utf-8")


def _persona_of(root: Path, story_id: str) -> str | None:
    return sdlc_md.extract_field(
        sdlc_md.find_by_id(root, story_id)[0].read_text(encoding="utf-8"), "Persona")


class RefinePersonaTests(unittest.TestCase):
    """US0449: the bulk minting paths resolve the design persona exactly as `new` does, so
    the resolution lives in the commands people actually run - not only in the single-mint
    path a reader is told to use."""

    def test_refined_stories_carry_a_resolved_persona(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _registry(root)
            _cr(root, "CR0001", ["the request is satisfied"])
            res = refine.refine(root, "CR0001", "The epic",
                                [("A", 2, None), ("B", 3, None)], skip_personas=True)
            self.assertTrue(res["stories"])
            for sid in res["stories"]:
                self.assertEqual(_persona_of(root, sid), "Maya Okafor",
                                 f"{sid} was minted with no resolved design persona")

    def test_new_batch_and_refine_agree_on_the_resolved_persona(self) -> None:
        # One test comparing the THREE paths, so a divergence in any of them fails here rather
        # than being invisible to three assertions that each only know their own path.
        artifact = loader.load_script("artifact")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _registry(root)
            _cr(root, "CR0001", ["the request is satisfied"])
            res = refine.refine(root, "CR0001", "The epic",
                                [("A", 2, None), ("B", 3, None)], skip_personas=True)
            epic = res["epic"]
            by_refine = _persona_of(root, res["stories"][0])
            by_new = sdlc_md.extract_field(
                Path(artifact.new(root, "story", "minted one at a time",
                                  {"epic": epic, "affects": "src/CR0001.py"})["path"]
                     ).read_text(encoding="utf-8"), "Persona")
            created = artifact.new_batch(root, "story", [
                {"title": "minted in a batch", "epic": epic, "affects": "src/CR0001.py"}])
            by_batch = sdlc_md.extract_field(
                Path(created["created"][0]["path"]).read_text(encoding="utf-8"), "Persona")
            self.assertEqual({"refine": by_refine, "new": by_new, "batch": by_batch},
                             {"refine": "Maya Okafor", "new": "Maya Okafor",
                              "batch": "Maya Okafor"},
                             "the three minting paths disagree about the resolved persona")


class SeamMapTests(unittest.TestCase):
    """US0538. Thirteen of the seventeen round-one majors in RUN-01KYKVZM were seam defects -
    four directly contradicting PAIRS in one batch, every one of which passed its own criteria.
    A delivery lane reads ONE unit; review is the first actor in the loop that reads two, so
    the pair is invisible until the most expensive moment."""

    def _unit(self, root: Path, uid: str, affects: str, preserves: str = "") -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        line = f"- **Preserves:** {preserves}\n" if preserves else ""
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** {affects}\n\n"
            f"## Acceptance Criteria\n\n### AC1: it works\n\n{line}"
            f"- **Verify:** shell true\n", encoding="utf-8")

    def test_a_pair_sharing_a_property_with_no_preserving_criterion_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py")
            self._unit(root, "US0002", "src/thing.py")
            found = refine.seam_findings(root, ["US0001", "US0002"])
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["shared"], ["src/thing.py"])

    def test_the_us0529_us0530_shape_is_reported(self) -> None:
        """The real pair: one unit fixing a property, its partner reintroducing it. Both
        satisfied their own criteria, which is why nothing before review saw it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0529", "src/init.py, tests/test_init.py")
            self._unit(root, "US0530", "src/init.py, tests/test_init.py")
            found = refine.seam_findings(root, ["US0529", "US0530"])
            self.assertEqual([f["units"] for f in found], [["US0529", "US0530"]])

    def test_a_declared_owner_clears_the_seam(self) -> None:
        """`Preserves:` is what makes the seam owned - the check reports a pair NOBODY has been
        asked about, and must stop reporting one somebody has."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py", preserves="src/thing.py stays idempotent")
            self._unit(root, "US0002", "src/thing.py")
            self.assertEqual(refine.seam_findings(root, ["US0001", "US0002"]), [])

    def test_a_declaration_naming_something_else_does_not_own_the_seam(self) -> None:
        """The case a mutant walked straight through: `owners.append(owner)` for ANY unit
        carrying a `Preserves:` line passed every other test here, because they all declare
        the shared file. A declaration about an unrelated property is not an answer about
        this pair, and accepting one turns the field into a box to tick."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py",
                       preserves="src/unrelated.py keeps its cache warm")
            self._unit(root, "US0002", "src/thing.py")
            self.assertEqual(len(refine.seam_findings(root, ["US0001", "US0002"])), 1,
                             "a Preserves line naming another file owned this seam")

    def test_naming_the_SIBLING_unit_also_owns_the_seam(self) -> None:
        """The other legitimate spelling: saying which unit you must not regress is as good as
        saying which file, and often clearer."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py",
                       preserves="whatever US0002 asserts about the parse order")
            self._unit(root, "US0002", "src/thing.py")
            self.assertEqual(refine.seam_findings(root, ["US0001", "US0002"]), [])

    def test_units_that_share_nothing_are_not_a_seam(self) -> None:
        """A check that fires on everything is not a check."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/a.py")
            self._unit(root, "US0002", "src/b.py")
            self.assertEqual(refine.seam_map(root, ["US0001", "US0002"]), [])

    def test_a_shared_markdown_file_is_not_a_seam(self) -> None:
        """Two units editing one document are not sharing a behaviour, and reporting every doc
        pair would bury the pairs that matter."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "docs/guide.md")
            self._unit(root, "US0002", "docs/guide.md")
            self.assertEqual(refine.seam_map(root, ["US0001", "US0002"]), [])

    def test_an_empty_report_says_what_it_checked_for(self) -> None:
        """A batch with no seams must not be indistinguishable from one nobody mapped."""
        self.assertIn("nothing to own", " ".join(refine.render_seam_findings([], 0)))
        self.assertIn("every one owned", " ".join(refine.render_seam_findings([], 3)))


class SeamOwnershipDefectsTests(unittest.TestCase):
    """BG0388/BG0389/BG0390/BG0396. The seam map shipped with four ways to report an all-clear
    over a batch it had not actually judged - the failure direction that matters, since the
    whole point is to name a pair before review does."""

    @staticmethod
    def _unit(root: Path, uid: str, affects: str, *, in_criterion: str = "",
              outside: str = "") -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        crit = f"- **Preserves:** {in_criterion}\n" if in_criterion else ""
        prose = f"- **Preserves:** {outside}\n" if outside else ""
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** {affects}\n\n"
            f"## User Story\n\n**As a** dev\n{prose}\n"
            f"## Acceptance Criteria\n\n### AC1: it works\n\n{crit}"
            f"- **Verify:** shell true\n", encoding="utf-8")

    def test_a_preserves_naming_only_the_test_file_does_not_own_the_source_seam(self) -> None:
        """BG0388. `'critic.py' in 'tests/test_critic.py'` is true, so a substring match let a
        unit own the seam on its source by naming its own test file.

        The shared path is the BARE `critic.py`: that is what makes it a substring of the test
        path, and it is the shape the defect actually had. A fixture using `src/critic.py`
        passes under the naive matcher too and proves nothing - mutation testing caught exactly
        that here."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "critic.py, tests/test_critic.py",
                       in_criterion="tests/test_critic.py keeps passing")
            self._unit(root, "US0002", "critic.py")
            found = refine.seam_findings(root, ["US0001", "US0002"])
        self.assertEqual(1, len(found), "the seam on critic.py is still unowned")
        self.assertIn("critic.py", found[0]["shared"])

    def test_naming_the_shared_source_itself_does_own_it(self) -> None:
        """The discriminating half - a matcher that never matches is not a fix."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "critic.py, tests/test_critic.py",
                       in_criterion="critic.py keeps its public contract")
            self._unit(root, "US0002", "critic.py")
            self.assertEqual([], refine.seam_findings(root, ["US0001", "US0002"]))

    def test_a_preserves_outside_a_criterion_does_not_own_a_seam(self) -> None:
        """BG0389. `_SEAM_RE` scanned the whole document, so a line under `## User Story` -
        or a revision row quoting one - cleared the seam. The field's own contract says IN A
        CRITERION."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py", outside="src/thing.py stays fast")
            self._unit(root, "US0002", "src/thing.py")
            found = refine.seam_findings(root, ["US0001", "US0002"])
        self.assertEqual(1, len(found), "a declaration outside a criterion owned the seam")

    def test_the_same_file_in_two_accepted_spellings_is_one_seam(self) -> None:
        """BG0390. `resolve_affects` accepts repo-relative and skill-relative paths and the
        corpus uses both, but `seam_map` intersected the raw strings - so one file written two
        ways was not a seam at all."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
            skill.mkdir(parents=True)
            (skill / "sprint.py").write_text("x = 1\n", encoding="utf-8")
            self._unit(root, "US0001", ".claude/skills/sdlc-studio/scripts/sprint.py")
            self._unit(root, "US0002", "scripts/sprint.py")
            seams = refine.seam_map(root, ["US0001", "US0002"])
        self.assertEqual(1, len(seams), "two spellings of one file were not seen as a seam")

    def test_two_genuinely_different_files_are_still_not_a_seam(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/a.py")
            self._unit(root, "US0002", "src/b.py")
            self.assertEqual([], refine.seam_map(root, ["US0001", "US0002"]))

    def test_an_unresolvable_id_is_refused_not_skipped(self) -> None:
        """BG0396. `refine seams --units US9999` printed the all-clear at exit 0. The planner's
        own reader raises on an id not on disk, for the stated reason that a silent skip ships
        a smaller tranche than approved; this had re-implemented it without that."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            err = io.StringIO()
            args = argparse.Namespace(units="US9999,US9998", worklist=None, root=str(root),
                                      format="text")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = refine.cmd_seams(args)
        self.assertEqual(2, rc, "an all-clear over units nobody looked at")
        self.assertIn("US9999", err.getvalue())


class MintedStoryFieldsTests(unittest.TestCase):
    """BG0477, re-grounded. The filed summary claimed the request's criteria "were not seeded";
    they ARE, onto the epic, and commit 7ef88707 removed story-level seeding for a multi-story
    breakdown deliberately - a breakdown cannot know which criterion belongs to which story. So
    seeding is not asked for here. What reproduces is narrower and real: the User Story block
    ships with `{{...}}` fields unfilled, and `refine` reports no price for the grooming it has
    just created, though authoring those criteria was the largest single piece of one sprint's
    planning phase.

    MUTANTS:
      1. drop the `_fill_user_story` call at the mint site -> placeholders survive.
      2. count the owed stories locally instead of asking `sprint.breakdown` -> AC3 fails when
         the two definitions of ungroomed drift.
      3. drop the grooming-owed print -> the price disappears.
    """

    def _cli(self, argv: list[str]) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = refine.main(argv)
        return rc, out.getvalue() + err.getvalue()

    def test_no_template_placeholder_survives_minting(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied", "and its second criterion too"])
            res = refine.refine(root, "CR0001", "An epic",
                                [("First thing", 2, None), ("Second thing", 3, None)])
            self.assertEqual(len(res["stories"]), 2)
            for sid in res["stories"]:
                text = sdlc_md.find_by_id(root, sid)[0].read_text(encoding="utf-8")
                block = text.split("## User Story", 1)[1].split("##", 1)[0]
                self.assertNotIn("{{", block, f"{sid} shipped an unfilled field: {block!r}")
            # and the capability is the story's own title, not a generic filler
            first = sdlc_md.find_by_id(root, res["stories"][0])[0].read_text(encoding="utf-8")
            self.assertIn("First thing", first.split("## User Story", 1)[1].split("##", 1)[0])

    def test_the_SECOND_mint_site_fills_its_fields_too(self) -> None:
        """The batch review's finding 7. `_fill_user_story` is wired into both `_decompose` and
        `_decompose_into` (the `--into` later-slice path), and only the first was exercised - so
        the second wiring could be deleted silently. That is the enumerated-list shape this unit
        exists to repair, left inside the repair.

        MUTANT: delete the `_fill_user_story` call from the `--into` path."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the first request is satisfied"])
            _cr(root, "CR0002", ["the second request is satisfied"])
            epic = refine.refine(root, "CR0001", "Batch epic",
                                 [("A", 2, None), ("B", 3, None)])["epic"]
            res = refine.refine(root, "CR0002", None, [("C", 2, None), ("D", 3, None)],
                                into_epic=epic)
            for sid in res["stories"]:
                text = sdlc_md.find_by_id(root, sid)[0].read_text(encoding="utf-8")
                block = text.split("## User Story", 1)[1].split("##", 1)[0]
                self.assertNotIn("{{", block,
                                 f"{sid} came from the --into path with an unfilled field")

    def test_refine_reports_the_grooming_it_leaves_owed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            rc, out = self._cli(["apply", "--request", "CR0001", "--epic-title", "An epic",
                                 "--story", "First thing|2", "--story", "Second thing|3",
                                 "--root", str(root)])
            self.assertEqual(rc, 0, out)
            self.assertIn("owe authored", out, f"no grooming price was reported: {out}")
            self.assertIn("2 of 2", out, out)
            self.assertIn("NOT priced", out, out)

    def test_the_reported_count_matches_the_breakdown_census(self) -> None:
        """AC3. The count is the planner's own census rather than a second one, so the number
        `refine` prints and the number `sprint plan` refuses on cannot disagree."""
        import sprint
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            res = refine.refine(root, "CR0001", "An epic",
                                [("First thing", 2, None), ("Second thing", 3, None)])
            owed = refine.grooming_owed(root, res["stories"])
            units = [{"id": s, "type": "story", "path": str(sdlc_md.find_by_id(root, s)[0])}
                     for s in res["stories"]]
            bd = sprint.breakdown(root, units, skip_personas=True)
            census = sum(1 for u in bd["ungroomed"] if str(u.get("ac_why") or ""))
            self.assertEqual(owed, census)
            self.assertEqual(owed, 2)

    def test_a_groomed_story_is_not_counted_as_owing(self) -> None:
        """The control. A count that always equals the story total would pass the two tests
        above while measuring nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, "CR0001", ["the request is satisfied"])
            res = refine.refine(root, "CR0001", "An epic",
                                [("First thing", 2, None), ("Second thing", 3, None)])
            path = sdlc_md.find_by_id(root, res["stories"][0])[0]
            text = path.read_text(encoding="utf-8")
            head, _, tail = text.partition("## Acceptance Criteria")
            path.write_text(head + "## Acceptance Criteria\n\n### AC1: it behaves\n\n"
                            "- **Given** a thing\n- **Verify:** shell true\n\n"
                            + tail.split("##", 1)[1] if "##" in tail else
                            head + "## Acceptance Criteria\n\n### AC1: it behaves\n\n"
                            "- **Given** a thing\n- **Verify:** shell true\n",
                            encoding="utf-8")
            self.assertEqual(refine.grooming_owed(root, res["stories"]), 1)


if __name__ == "__main__":
    unittest.main()
