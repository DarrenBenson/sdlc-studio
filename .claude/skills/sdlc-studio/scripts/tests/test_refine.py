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
            self.assertEqual(bd["ungroomed"], [], "planner refused a story refine called plannable")

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


if __name__ == "__main__":
    unittest.main()
