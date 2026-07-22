"""Unit tests for engagement_floor.py (RED first - the deterministic floor does not exist yet).

The floor is not a judgement: a shipped multi-file unit with no acceptance criterion and no
linked plan FAILS, and the failure cannot be dodged by omitting the declared `Affects` field
(a git cross-check independently establishes the file count). The escape valves are auditable:
an `adopt_after` cutoff, the `engagement_floor: judgement` config mode, and a recorded waiver.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import subprocess
import io
import contextlib
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the git helper
import gitutil  # noqa: E402 - confined git for the fixture repos below

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "engagement_floor.py"


def _load():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("engagement_floor", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["engagement_floor"] = mod
    spec.loader.exec_module(mod)
    return mod


_LOC = {"story": ("stories", "US"), "bug": ("bugs", "BG"), "cr": ("change-requests", "CR")}


def _write_unit(root, type_, num, *, status, affects=None, ac=False, plan=False,
                verify=False):
    rel, prefix = _LOC[type_]
    d = root / "sdlc-studio" / rel
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# {prefix}{num:04d}: sample", "", f"> **Status:** {status}"]
    if affects:
        lines.append(f"> **Affects:** {', '.join(affects)}")
    lines.append("")
    if ac:
        lines += ["## Acceptance Criteria", "", "### AC1: works", "- a real criterion"]
    if verify:
        lines += ["- **Verify:** shell echo ok"]
    if plan:
        lines += ["", "Implements plan PL0001 (linked)."]
    path = d / f"{prefix}{num:04d}-sample.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _config(root, text):
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")


def _units(root):
    return {u["id"]: u for u in _load().detect(root)["units"]}


class FiresTests(unittest.TestCase):
    """The core rule, seen red first: a shipped multi-file unit with no AC/plan is a violation."""

    def test_multifile_shipped_no_planning_is_a_violation(self):
        # THE red-first case: a Done story touching two source files, no AC, no plan, no waiver,
        # after no cutoff - must FAIL the floor.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            u = _units(root)["US0100"]
            self.assertTrue(u["multi_file"])
            self.assertFalse(u["has_planning"])
            self.assertTrue(u["violation"])
            self.assertEqual(_load().detect(root)["summary"]["violations"], 1)

    def test_bug_and_cr_are_judged_not_only_stories(self):
        # The floor extends past conformance's story scope to bug (Fixed) and CR (Complete).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 200, status="Fixed", affects=["x/a.py", "x/b.py"])
            _write_unit(root, "cr", 300, status="Complete", affects=["y/a.py", "y/b.py"])
            units = _units(root)
            self.assertTrue(units["BG0200"]["violation"])
            self.assertTrue(units["CR0300"]["violation"])


class PassesTests(unittest.TestCase):
    """The same unit passes with an AC, a plan, a verify line, below the floor, or before adoption."""

    def test_ac_satisfies_the_floor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"], ac=True)
            self.assertFalse(_units(root)["US0100"]["violation"])

    def test_linked_plan_satisfies_the_floor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"], plan=True)
            self.assertFalse(_units(root)["US0100"]["violation"])

    def test_verify_line_satisfies_the_floor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"], verify=True)
            self.assertFalse(_units(root)["US0100"]["violation"])

    def test_single_file_is_below_the_floor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done", affects=["a/only.py"])
            u = _units(root)["US0100"]
            self.assertFalse(u["multi_file"])
            self.assertFalse(u["violation"])

    def test_unshipped_status_is_not_judged(self):
        # A bug still Open, or a story In Progress, has not shipped - the floor does not apply.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 200, status="Open", affects=["x/a.py", "x/b.py"])
            _write_unit(root, "story", 100, status="In Progress",
                        affects=["a/one.py", "a/two.py"])
            self.assertEqual(_load().detect(root)["summary"]["violations"], 0)

    def test_negative_outcome_is_not_judged(self):
        # Won't Fix / Rejected / Superseded shipped no code - not a floor case.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 200, status="Won't Fix", affects=["x/a.py", "x/b.py"])
            _write_unit(root, "cr", 300, status="Rejected", affects=["y/a.py", "y/b.py"])
            self.assertEqual(_load().detect(root)["summary"]["violations"], 0)

    def test_docs_only_change_is_not_multifile(self):
        # Two markdown files are not two SOURCE files - a pure docs change is below the floor.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done",
                        affects=["docs/a.md", "docs/b.md"])
            self.assertFalse(_units(root)["US0100"]["violation"])


class CutoffTests(unittest.TestCase):
    """The adopt_after cutoff grandfathers pre-adoption ids forward-only, so turning the
    floor on does not redden the existing backlog."""

    def test_id_at_or_below_cutoff_is_exempt(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "engagement_floor:\n  adopt_after: 150\n")
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            u = _units(root)["US0100"]
            self.assertTrue(u["exempt"])
            self.assertFalse(u["violation"])

    def test_id_above_cutoff_still_judged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "engagement_floor:\n  adopt_after: 99\n")
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            u = _units(root)["US0100"]
            self.assertFalse(u["exempt"])
            self.assertTrue(u["violation"])


class WaiverTests(unittest.TestCase):
    """Reuses BG0110's waiver primitive: a per-unit waiver exempts one unit, a project-global
    waiver exempts the whole floor - both auditable decisions-log rows, never a silent bypass."""

    def _decisions(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        import decisions
        return decisions

    def test_per_unit_waiver_exempts_only_that_unit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dec = self._decisions()
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            _write_unit(root, "story", 101, status="Done",
                        affects=["b/one.py", "b/two.py"])
            dec.record_waiver(root, "rule:engagement-floor:US0100", "legacy carve-out")
            units = _units(root)
            self.assertTrue(units["US0100"]["waived"])
            self.assertFalse(units["US0100"]["violation"])
            self.assertFalse(units["US0101"]["waived"])
            self.assertTrue(units["US0101"]["violation"])

    def test_project_waiver_exempts_the_whole_floor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dec = self._decisions()
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            dec.record_waiver(root, "rule:engagement-floor", "operator accepts the risk")
            self.assertEqual(_load().detect(root)["summary"]["violations"], 0)


class GitCrossCheckTests(unittest.TestCase):
    """The signal cannot be escaped by omitting Affects: git independently counts the source
    files the unit's commits touched, and the count is the UNION of the two."""

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def _init_repo(self, root):
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "t@t")
        self._git(root, "config", "user.name", "t")

    def test_git_touched_files_raise_the_count_past_omitted_affects(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            # Unit declares only ONE file in Affects (understating the change)...
            _write_unit(root, "bug", 200, status="Fixed", affects=["src/one.py"])
            # ...but its commit touched TWO source files.
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            (root / "src" / "two.py").write_text("y = 2\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "BG0200: fix the thing across two files")
            u = _units(root)["BG0200"]
            self.assertGreaterEqual(u["source_files"], 2)
            self.assertTrue(u["multi_file"])
            self.assertTrue(u["violation"])

    def test_dashed_commit_spelling_still_matches_undashed_id(self):
        # A repo whose commits write `CR-0300` must still be cross-checked against unit CR0300 -
        # a spelling mismatch would silently zero the git signal.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "cr", 300, status="Complete")  # id CR0300, no Affects
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            (root / "src" / "two.py").write_text("y = 2\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "CR-0300: change spanning two files")
            self.assertTrue(_units(root)["CR0300"]["violation"])

    def test_omitting_affects_entirely_does_not_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "bug", 200, status="Fixed")  # no Affects at all
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            (root / "src" / "two.py").write_text("y = 2\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "BG0200 fix spanning two files")
            self.assertTrue(_units(root)["BG0200"]["violation"])


class OmissionHoleTests(unittest.TestCase):
    """F1 (critic reject): the floor may not be dodged by omission. A shipped unit skips the
    planning pass only by DECLARING it is below the floor (an `Affects` field it can be held to)
    - a unit with neither a planning artefact nor a declaration fails as `undeclared`, so the
    blank ticket + terse commit the weak model produces cannot buy a silent pass."""

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def _init_repo(self, root):
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "t@t")
        self._git(root, "config", "user.name", "t")

    def test_omitted_id_multifile_story_does_not_escape(self):
        # THE red test the critic reproduced: a Done story, three real .py files, a commit that
        # does NOT name the story id, no Affects, no AC. The git leg cannot see it (no id in the
        # message) and nothing is declared - the old floor was SILENT. It must now fail.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "story", 301, status="Done")  # no Affects, no AC
            (root / "src").mkdir()
            for n in ("one", "two", "three"):
                (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "wire up three modules for the widget feature")
            u = _units(root)["US0301"]
            self.assertTrue(u["violation"])
            self.assertEqual(u["kind"], "undeclared")

    def test_undeclared_no_planning_unit_fails_without_git(self):
        # No git at all: a shipped unit that declares no Affects and has no planning cannot be
        # shown to be below the floor, so it fails (declare, plan, or waive).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 400, status="Fixed")  # no Affects, no AC
            u = _units(root)["BG0400"]
            self.assertTrue(u["violation"])
            self.assertEqual(u["kind"], "undeclared")

    def test_declared_single_file_no_planning_passes(self):
        # Declaring a single-file Affects IS showing you are below the floor - it passes.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 400, status="Fixed", affects=["src/only.py"])
            u = _units(root)["BG0400"]
            self.assertFalse(u["violation"])
            self.assertTrue(u["declared"])

    def test_planning_without_declaration_passes(self):
        # A unit that did the planning pass (an AC) need not also declare Affects - the floor's
        # goal is met. Only a unit skipping planning must show it is small.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 400, status="Fixed", ac=True)  # no Affects
            self.assertFalse(_units(root)["BG0400"]["violation"])


class DeclarationIsCheckableTests(unittest.TestCase):
    """R1 (critic reject): a declaration must be a CHECKABLE footprint - a real file path - not
    just non-empty text. `Affects: n/a` / `various` can be held to nothing, so they are
    omission-equivalent and must NOT satisfy the floor."""

    def test_affects_na_is_not_a_declaration(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 600, status="Fixed", affects=["n/a"])
            u = _units(root)["BG0600"]
            self.assertFalse(u["declared"])
            self.assertTrue(u["violation"])
            self.assertEqual(u["kind"], "undeclared")

    def test_affects_prose_is_not_a_declaration(self):
        for noise in ("various", "multiple files", "see the commits", "TBD"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _write_unit(root, "bug", 601, status="Fixed", affects=[noise])
                u = _units(root)["BG0601"]
                self.assertFalse(u["declared"], noise)
                self.assertTrue(u["violation"], noise)

    def test_real_path_is_a_declaration(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 602, status="Fixed", affects=["src/only.py"])
            self.assertTrue(_units(root)["BG0602"]["declared"])
            self.assertFalse(_units(root)["BG0602"]["violation"])


class ExtensionlessFootprintTests(unittest.TestCase):
    """BG0118: a checkable footprint is not only a dotted path. An extension-less real file
    (Makefile, Dockerfile, LICENSE, Containerfile) or a dotfile (.gitignore, .env) is a real,
    checkable single-file declaration and must satisfy the floor - forcing a waiver on such an
    honest single-file change would train reflexive waivering, the anti-pattern the floor avoids.
    A version string (v1.2) and prose (n/a) are still NOT files."""

    def test_known_extensionless_file_is_a_declaration(self):
        for name in ("Makefile", "Dockerfile", "LICENSE", "Containerfile"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _write_unit(root, "bug", 620, status="Fixed", affects=[name])
                u = _units(root)["BG0620"]
                self.assertTrue(u["declared"], name)
                self.assertFalse(u["violation"], name)

    def test_dotfile_is_a_declaration(self):
        for name in (".gitignore", ".env"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _write_unit(root, "bug", 621, status="Fixed", affects=[name])
                u = _units(root)["BG0621"]
                self.assertTrue(u["declared"], name)
                self.assertFalse(u["violation"], name)

    def test_extensionless_file_under_a_directory_is_a_declaration(self):
        # The basename is what must look like a file - a path segment carrying a known
        # extension-less name still counts.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 622, status="Fixed", affects=["docker/Dockerfile"])
            self.assertTrue(_units(root)["BG0622"]["declared"])

    def test_version_string_is_not_a_declaration(self):
        # BG0118 sibling false-accept: `v1.2` is a version, not a file - its `.2` is a numeric
        # extension. It must NOT satisfy the floor.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 623, status="Fixed", affects=["v1.2"])
            u = _units(root)["BG0623"]
            self.assertFalse(u["declared"])
            self.assertTrue(u["violation"])
            self.assertEqual(u["kind"], "undeclared")

    def test_na_bearing_a_slash_is_still_not_a_declaration(self):
        # `n/a` bears a `/` but its basename `a` is not a file - a bare `/` cannot buy a pass.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "bug", 624, status="Fixed", affects=["n/a"])
            u = _units(root)["BG0624"]
            self.assertFalse(u["declared"])
            self.assertTrue(u["violation"])


class RecogniserAgreementTests(unittest.TestCase):
    """BG0119: the declared-boolean and the source-file count must recognise a real file footprint
    the SAME way. The declared boolean (`_affects_declared`) and the file count both route through
    one recogniser, so a token that is a real file is never seen by one and missed by the other. R1
    (prose/version strings are not files) must stay closed in both."""

    def test_bare_source_file_declared_and_counted_agree(self):
        # RED before the fix: a bare code filename (no directory) was seen as a declaration by
        # `_affects_declared` (real file) but counted 0 by `_declared_source_files`, which used the
        # narrower `affects_files` (a non-slash token only counts on .py/.md/.yaml/.yml/.sh). The
        # two recognisers disagreed on the same field. After: both see one real source footprint.
        ef = _load()
        text = "> **Affects:** engine.rs\n"
        self.assertEqual(len(ef._declared_source_files(text)), 1)  # the count-side recogniser
        self.assertTrue(ef._affects_declared(text))                # the boolean-side recogniser

    def test_makefile_recogniser_and_declared_boolean_agree(self):
        # The house-rule case: `Affects: Makefile`. The declared boolean sees one real file; the
        # shared file recogniser (`_declared_file_tokens`) must see exactly the same one. (Makefile
        # is a real file but not a SOURCE file, so it legitimately adds 0 to the source count - the
        # agreement is at the recogniser layer, not the source-suffix filter.)
        ef = _load()
        text = "> **Affects:** Makefile\n"
        self.assertEqual(len(ef._declared_file_tokens(text)), 1)
        self.assertTrue(ef._affects_declared(text))
        self.assertEqual(bool(ef._declared_file_tokens(text)), ef._affects_declared(text))

    def test_r1_prose_and_version_string_are_footprints_in_neither_recogniser(self):
        # R1 must stay closed in BOTH recognisers: prose (`n/a`) and a version string (`v1.2`) can
        # be held to nothing, so neither the declared boolean nor the file recogniser may accept them.
        ef = _load()
        for noise in ("n/a", "various", "v1.2"):
            text = f"> **Affects:** {noise}\n"
            self.assertEqual(ef._declared_file_tokens(text), [], noise)
            self.assertFalse(ef._affects_declared(text), noise)
            self.assertEqual(ef._declared_source_files(text), set(), noise)


class BatchCommitUnderstatementLimitTests(unittest.TestCase):
    """R2 (documented LIMIT, not a hole to close): understatement (declare 1 file, touch 3) is
    NOT caught when the unit shares its commit with another judged id, because F3's batch-skip
    strips the git cross-check and git cannot attribute a file to one id among several. This test
    PINS that boundary so the gap is visible in the suite, not silently assumed closed. Closing it
    needs a commit-id convention (a tracked follow-on CR), out of scope for git-log-grep."""

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def test_understatement_in_a_multi_id_commit_is_not_caught(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._git(root, "init", "-q")
            self._git(root, "config", "user.email", "t@t")
            self._git(root, "config", "user.name", "t")
            # BG0700 declares ONE file but the change (shared commit with BG0701) touched three.
            _write_unit(root, "bug", 700, status="Fixed", affects=["src/one.py"])
            (root / "src").mkdir()
            for n in ("one", "two", "three"):
                (root / "src" / f"{n}.py").write_text("x=1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "BG0700 BG0701: batch fix across three files")
            u = _units(root)["BG0700"]
            # The known limit: the batch-skip means git contributes nothing, so the understated
            # single-file declaration stands and the unit PASSES. Documented, not silently closed.
            self.assertFalse(u["violation"])
            self.assertEqual(u["source_files"], 1)


class RefsTrailerAttributionTests(unittest.TestCase):
    """CR0239: a `Refs: <id>` commit trailer gives the git leg per-id attribution a bare co-named
    subject cannot. When a commit body carries `Refs: US0301`, that commit's files attribute to
    US0301 even though the subject also names US0302 - closing the shared-commit understatement
    gap D0026 disclosed. A Refs trailer is trusted BECAUSE it is explicit, but it is ADDITIVE: it
    can only ever raise a count, never lower one, and it never divides a commit's files between the
    ids it names (each named id gets the full set)."""

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def _init_repo(self, root):
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "t@t")
        self._git(root, "config", "user.name", "t")

    def _commit_three_files(self, root, subject, body=""):
        (root / "src").mkdir(exist_ok=True)
        for n in ("one", "two", "three"):
            (root / "src" / f"{n}.py").write_text("x=1\n", encoding="utf-8")
        self._git(root, "add", "-A")
        msg = subject if not body else f"{subject}\n\n{body}"
        self._git(root, "commit", "-q", "-m", msg)

    def test_refs_trailer_attributes_a_shared_commit_and_violates(self):
        # THE red-then-green case: a commit whose SUBJECT names US0301 and US0302, three source
        # files, body `Refs: US0301`, and US0301 carries NO plan. Before Refs, the batch-skip fed
        # US0301 zero files and it passed (understatement uncaught). After Refs, all three files
        # attribute to US0301 -> multi-file, no plan -> it VIOLATES.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "story", 301, status="Done")  # no Affects, no AC
            _write_unit(root, "story", 302, status="Done", ac=True)  # planned, not our concern
            self._commit_three_files(root, "US0301 US0302: batch across three files",
                                     body="Refs: US0301")
            units = _units(root)
            u = units["US0301"]
            self.assertEqual(u["source_files"], 3)
            self.assertTrue(u["multi_file"])
            self.assertTrue(u["violation"])
            self.assertEqual(u["kind"], "unplanned")

    def test_id_not_named_in_refs_is_still_skipped(self):
        # US0302 is co-named in the subject but NOT in the Refs trailer: the floor cannot attribute
        # the commit's files to it (only Refs makes a shared commit attributable), so its git leg
        # stays empty - the pre-CR0239 behaviour, unchanged.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            self._commit_three_files(root, "US0301 US0302: batch across three files",
                                     body="Refs: US0301")
            ef = _load()
            self.assertEqual(len(ef._git_touched_source_files(root, "US0301")), 3)
            self.assertEqual(ef._git_touched_source_files(root, "US0302"), set())

    def test_multi_id_commit_without_refs_still_skips(self):
        # No Refs trailer at all: the shared commit still feeds NO id (F3 batch-skip), unchanged.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            self._commit_three_files(root, "US0301 US0302: batch across three files")
            ef = _load()
            self.assertEqual(ef._git_touched_source_files(root, "US0301"), set())
            self.assertEqual(ef._git_touched_source_files(root, "US0302"), set())

    def test_refs_naming_two_ids_gives_each_the_full_set(self):
        # `Refs: US0301, US0302` -> BOTH ids get all three files. Refs never divides a commit's
        # files between the ids it names, so it cannot LOWER a count below the real footprint.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            self._commit_three_files(root, "US0301 US0302: shared change",
                                     body="Refs: US0301, US0302")
            ef = _load()
            self.assertEqual(len(ef._git_touched_source_files(root, "US0301")), 3)
            self.assertEqual(len(ef._git_touched_source_files(root, "US0302")), 3)

    def test_refs_is_additive_and_never_lowers_a_solo_count(self):
        # A solo commit (subject names only US0301) touching three files feeds US0301 three files.
        # A self-naming Refs trailer must not change that - Refs only ever adds attribution.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            self._commit_three_files(root, "US0301: solo change", body="Refs: US0301")
            ef = _load()
            self.assertEqual(len(ef._git_touched_source_files(root, "US0301")), 3)

    def test_refs_grammar_accepts_multiple_lines_and_dashed_ids(self):
        # Grammar: repeatable `Refs:` lines, and the dashed id spelling (`US-0301`) matches too.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            self._commit_three_files(root, "US0301 US0302: shared change",
                                     body="Refs: US-0301\nRefs: US0302")
            ef = _load()
            self.assertEqual(len(ef._git_touched_source_files(root, "US0301")), 3)
            self.assertEqual(len(ef._git_touched_source_files(root, "US0302")), 3)

    def test_solo_subject_with_foreign_refs_still_counts_the_solo_footprint(self):
        # THE safety hole (critic reject). A commit whose SUBJECT names only US0301 (a solo
        # commit), body carrying a see-also `Refs: US0302` (a DIFFERENT id), touching three files;
        # US0301 declares one. The `Refs:` convention means see-also in universal git usage, so an
        # author WILL write this. The solo cross-check must still count all three files and VIOLATE
        # - a body `Refs:` naming a foreign id must never disarm the subject id's own attribution.
        # (Before the subject-line batch test, the foreign id inflated the full-message batch count
        # and dropped US0301 to zero: understatement escaped a case the pre-Refs floor caught.)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "story", 301, status="Done", affects=["src/one.py"])
            self._commit_three_files(root, "US0301: solo change", body="Refs: US0302")
            ef = _load()
            self.assertEqual(len(ef._git_touched_source_files(root, "US0301")), 3)
            u = _units(root)["US0301"]
            self.assertEqual(u["source_files"], 3)
            self.assertTrue(u["multi_file"])
            self.assertTrue(u["violation"])

    def test_refs_never_lowers_count_below_the_no_refs_baseline(self):
        # The load-bearing invariant, proven across the matrix: for EVERY `Refs:` body variant and
        # every subject shape, a unit's git-attributed source-file count is never below the count it
        # gets with NO `Refs:` line at all (the pre-convention baseline). A trailer only ever raises.
        subjects = ("US0301: solo change", "US0301 US0302: shared change")
        bodies = ("Refs: US0301", "Refs: US0302", "Refs: US0301, US0302", "Refs: US0399", "")
        ef = _load()
        for subject in subjects:
            for target in ("US0301", "US0302"):
                # Baseline: the same subject with no Refs line at all.
                with tempfile.TemporaryDirectory() as d0:
                    base = Path(d0)
                    self._init_repo(base)
                    self._commit_three_files(base, subject)
                    baseline = len(ef._git_touched_source_files(base, target))
                for body in bodies:
                    with tempfile.TemporaryDirectory() as d1:
                        root = Path(d1)
                        self._init_repo(root)
                        self._commit_three_files(root, subject, body=body)
                        got = len(ef._git_touched_source_files(root, target))
                        self.assertGreaterEqual(
                            got, baseline,
                            f"{target} lowered below baseline: subject={subject!r} "
                            f"body={body!r} got={got} baseline={baseline}")


class CommitMsgCheckTests(unittest.TestCase):
    """CR0239 commit-msg hook brain: `check_commit_message` warns when a subject names more than
    one judged id WITHOUT a Refs: trailer covering them - the nudge to add Refs so the floor can
    attribute per id. It never blocks unless strict, and never blocks on a message it cannot make
    sense of (degrade honestly)."""

    def _check(self, text, strict=False):
        return _load().check_commit_message(text, strict=strict)

    def test_multi_id_subject_without_refs_warns(self):
        code, warning = self._check("US0301 US0302: batch fix")
        self.assertEqual(code, 0)  # warn, do not block
        self.assertIsNotNone(warning)
        self.assertIn("US0301", warning)
        self.assertIn("US0302", warning)

    def test_multi_id_subject_without_refs_blocks_under_strict(self):
        code, warning = self._check("US0301 US0302: batch fix", strict=True)
        self.assertEqual(code, 1)
        self.assertIsNotNone(warning)

    def test_multi_id_subject_fully_covered_by_refs_is_clean(self):
        code, warning = self._check("US0301 US0302: batch fix\n\nRefs: US0301, US0302", strict=True)
        self.assertEqual(code, 0)
        self.assertIsNone(warning)

    def test_multi_id_subject_partially_covered_names_the_gap(self):
        code, warning = self._check("US0301 US0302: batch fix\n\nRefs: US0301")
        self.assertEqual(code, 0)
        self.assertIsNotNone(warning)
        self.assertIn("US0302", warning)
        self.assertNotIn("US0301", warning)  # covered ids are not flagged

    def test_solo_id_subject_is_clean(self):
        code, warning = self._check("US0301: solo fix", strict=True)
        self.assertEqual(code, 0)
        self.assertIsNone(warning)

    def test_no_judged_id_is_clean(self):
        code, warning = self._check("chore: tidy up", strict=True)
        self.assertEqual(code, 0)
        self.assertIsNone(warning)

    def test_comment_lines_are_ignored_when_finding_the_subject(self):
        # git may prepend a blank/comment scaffold; the subject is the first real line.
        code, warning = self._check("# please enter the commit message\n\nUS0301 US0302: fix")
        self.assertIsNotNone(warning)


class ForwardCutoffTests(unittest.TestCase):
    """F2 (critic reject): a forward cutoff (adopt_after above the highest existing id) is a
    silent whole-project disarm, worse than judgement mode. It must be flagged, not honoured
    silently, and exempted-would-violate units must remain visible."""

    def test_cutoff_above_max_id_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "engagement_floor:\n  adopt_after: 99999\n")
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            result = _load().detect(root)
            self.assertTrue(result["summary"]["cutoff_forward"])
            # ...and the gate lane blocks on it rather than reporting a vacuous 0.
            import gate
            r = gate._engagement_floor(str(root))
            self.assertTrue(r["blocking"])
            self.assertGreaterEqual(r["count"], 1)

    def test_cutoff_at_max_id_is_honoured(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "engagement_floor:\n  adopt_after: 100\n")
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            result = _load().detect(root)
            self.assertFalse(result["summary"]["cutoff_forward"])
            self.assertTrue(result["units"][0]["exempt"])

    def test_exempt_would_violate_is_surfaced(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "engagement_floor:\n  adopt_after: 100\n")
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])  # exempt, but would violate
            result = _load().detect(root)
            self.assertEqual(result["summary"]["exempt_would_violate"], 1)


class BatchCommitTests(unittest.TestCase):
    """F3 (critic characterisation): the git leg must not attribute a batch commit's whole file
    set to every id it names - it cannot know which file belongs to which id."""

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def _init_repo(self, root):
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "t@t")
        self._git(root, "config", "user.name", "t")

    def test_multi_id_commit_does_not_feed_the_git_leg(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("x=1\n", encoding="utf-8")
            (root / "src" / "b.py").write_text("y=2\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "BG0500 BG0501: batch fix across two files")
            ef = _load()
            # A commit naming two ids attributes its files to neither id's git leg.
            self.assertEqual(ef._git_touched_source_files(root, "BG0500"), set())

    def test_single_id_commit_still_feeds_the_git_leg(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            (root / "src").mkdir()
            (root / "src" / "c.py").write_text("z=3\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "BG0502: single-id fix")
            ef = _load()
            touched = ef._git_touched_source_files(root, "BG0502")
            self.assertTrue(any(t.endswith("c.py") for t in touched))


class BatchGitAttributionAgreesTests(unittest.TestCase):
    """`detect` used to call `_git_touched_source_files` once per shipped unit - 842 git
    subprocesses on the dev repo, 10.5s of an 11.0s lane. It now calls `_git_touched_by_id`
    ONCE and looks each id up. That is only safe if the two agree, so this asserts it directly
    across the shapes the attribution rule turns on, rather than trusting that the rewrite
    preserved it."""

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def _init_repo(self, root):
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "t@t")
        self._git(root, "config", "user.name", "t")

    def _commit(self, root, name, msg):
        (root / "src").mkdir(exist_ok=True)
        (root / "src" / name).write_text("x=1\n", encoding="utf-8")
        self._git(root, "add", "-A")
        self._git(root, "commit", "-q", "-m", msg)

    def test_batch_and_single_id_git_attribution_agree(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            # Every shape the attribution rule turns on, in one history.
            self._commit(root, "a.py", "US0301: solo subject")
            self._commit(root, "b.py", "US0302 US0303: batch subject, no trailer")
            self._commit(root, "c.py", "US0304 US0305: batch subject\n\nRefs: US0304")
            self._commit(root, "d.py", "chore: no id in subject\n\nRefs: US0306")
            self._commit(root, "e.py", "US0307: solo subject\n\nalso see US0308 in the body")
            self._commit(root, "f.py", "US-0309: hyphenated spelling")
            ef = _load()
            batch = ef._git_touched_by_id(root)
            for rid in ("US0301", "US0302", "US0303", "US0304", "US0305",
                        "US0306", "US0307", "US0308", "US0309"):
                self.assertEqual(
                    batch.get(rid, set()), ef._git_touched_source_files(root, rid),
                    f"batch and per-id attribution disagree for {rid}")

    def test_the_batch_pass_runs_one_git_log_not_one_per_id(self) -> None:
        """The saving itself. Without this, reverting to a per-id loop inside the batch function
        would keep every attribution test green while restoring the whole cost."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            for i, n in enumerate("abcdefgh"):
                self._commit(root, f"{n}.py", f"US03{i:02d}: solo subject")
            ef = _load()
            calls = []
            orig = ef.subprocess.run

            def _counting(cmd, *a, **kw):
                if isinstance(cmd, list) and "log" in cmd:
                    calls.append(cmd)
                return orig(cmd, *a, **kw)

            ef.subprocess.run = _counting
            try:
                by_id = ef._git_touched_by_id(root)
            finally:
                ef.subprocess.run = orig
            self.assertEqual(len(calls), 1, f"expected 1 git log, made {len(calls)}")
            self.assertGreaterEqual(len(by_id), 8)   # ...and it still found every id


class SummaryShapeTests(unittest.TestCase):
    """F3 (characterisation): the summary must count multi-file units separately from all judged
    shipped units, so the report cannot call every shipped unit 'multi-file'."""

    def test_multifile_count_is_separate_from_judged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done", affects=["a/one.py"])  # single
            _write_unit(root, "story", 101, status="Done",
                        affects=["b/one.py", "b/two.py"], ac=True)  # multi, planned
            s = _load().detect(root)["summary"]
            self.assertEqual(s["judged"], 2)
            self.assertEqual(s["multi_file"], 1)


class ModeTests(unittest.TestCase):
    """`engagement_floor: judgement` is the project-global opt-out already shipped by the prose
    half: the floor still reports, but the gate lane is advisory, not blocking."""

    def test_judgement_mode_reported_but_advisory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "engagement_floor: judgement\n")
            _write_unit(root, "story", 100, status="Done",
                        affects=["a/one.py", "a/two.py"])
            result = _load().detect(root)
            self.assertEqual(result["mode"], "judgement")
            # Still counted (visible), but the gate lane must not block in judgement mode.
            self.assertEqual(result["summary"]["violations"], 1)

    def test_default_mode_is_floor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done", affects=["a/one.py"])
            self.assertEqual(_load().detect(root)["mode"], "floor")


class PendingCommitTests(unittest.TestCase):
    """BG0251: the floor could not see a violation the gating commit itself creates.

    `_git_touched_by_id` derives "what this unit touched" from `git log --grep` over the
    HISTORY, so a commit's own files attach to a unit only once that commit exists. The
    pre-commit gate therefore structurally could not detect a violation the commit it is
    gating is about to introduce - observed during RUN-01KY321Q, where the floor reported
    0 violations, the gate passed, the commit landed, and the same check immediately
    afterwards reported 2 NEW violations in files nothing had touched.

    `detect(root, include_staged=True)` folds the STAGED index in, so the same verdict is
    available one commit earlier. The equivalence test below is the point of the fix: the
    pending verdict and the post-commit verdict must be the same verdict.
    """

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def _init_repo(self, root):
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "t@t")
        self._git(root, "config", "user.name", "t")

    def _stage_a_multifile_delivery(self, root, num=251):
        """A bug artefact declaring ONE file and carrying no planning artefact, staged to
        Fixed alongside three source files. Below the floor on committed evidence; a
        violation the instant the commit exists."""
        self._init_repo(root)
        _write_unit(root, "bug", num, status="Fixed", affects=["src/one.py"])
        (root / "src").mkdir(exist_ok=True)
        for n in ("one", "two", "three"):
            (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
        self._git(root, "add", "-A")

    def test_the_pending_commit_is_invisible_to_the_committed_evidence_leg(self):
        """The defect itself, pinned. Everything is staged and nothing is committed, so
        the floor's own history leg has nothing to attribute and the unit reads clean."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage_a_multifile_delivery(root)
            u = _units(root)["BG0251"]
            self.assertFalse(u["violation"])
            self.assertEqual(u["source_files"], 1)   # the declared Affects, and nothing else

    def test_a_unit_this_commit_puts_below_the_floor_is_seen_before_it_lands(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage_a_multifile_delivery(root)
            u = {x["id"]: x for x in
                 _load().detect(root, include_staged=True)["units"]}["BG0251"]
            self.assertTrue(u["violation"], "the pending commit's own files were not counted")
            self.assertEqual(u["kind"], "unplanned")
            self.assertTrue(u["staged_new"],
                            "the violation is one THIS commit creates, and must say so")
            self.assertGreaterEqual(u["source_files"], 3)

    def test_the_pending_verdict_is_the_verdict_the_commit_actually_produces(self):
        """The equivalence the fix rests on, and the only thing that makes the pending leg
        worth trusting: what it says before the commit is what the unchanged history leg
        says after it. Without this, the pending leg could be flagging something the floor
        would never have flagged, and the gate would be refusing commits for its own
        reasons."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage_a_multifile_delivery(root)
            pending = {x["id"]: x for x in
                       _load().detect(root, include_staged=True)["units"]}["BG0251"]
            # The real delivery-commit shape: ids in the BODY, none in the subject.
            self._git(root, "commit", "-q", "-m",
                      "fix: three modules\n\nBG0251 the thing that spans them")
            landed = _units(root)["BG0251"]
            self.assertTrue(landed["violation"], "premise: the commit does create a violation")
            self.assertEqual(pending["kind"], landed["kind"])
            self.assertEqual(pending["source_files"], landed["source_files"])

    def test_a_planned_unit_is_not_flagged_by_the_pending_leg(self):
        """The negative control. The pending leg raises a FILE COUNT; it does not invent a
        new rule, so a unit with a planning artefact is still below the floor."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "bug", 252, status="Fixed", affects=["src/one.py"], ac=True)
            (root / "src").mkdir()
            for n in ("one", "two", "three"):
                (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            u = {x["id"]: x for x in
                 _load().detect(root, include_staged=True)["units"]}["BG0252"]
            self.assertFalse(u["violation"])
            self.assertFalse(u["staged_new"])

    def test_nothing_staged_leaves_the_verdict_unchanged(self):
        """The common commit stages no judged artefact at all. The flag must then be a
        no-op, or every unrelated commit inherits the whole backlog's footprint."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "bug", 253, status="Fixed", affects=["src/one.py"])
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "chore: baseline")
            (root / "src" / "two.py").write_text("y = 2\n", encoding="utf-8")
            (root / "src" / "three.py").write_text("z = 3\n", encoding="utf-8")
            self._git(root, "add", "-A")   # source only: no judged artefact staged
            u = {x["id"]: x for x in
                 _load().detect(root, include_staged=True)["units"]}["BG0253"]
            self.assertFalse(u["violation"],
                             "a commit staging no artefact for this unit must not feed it")

    def test_a_unit_named_only_in_the_pending_message_is_still_invisible(self):
        """The residual gap, tested so the claim of coverage stays exact. A pre-commit hook
        is NOT given the commit message it is gating - git writes COMMIT_EDITMSG after the
        hook runs, so at hook time that file still holds the PREVIOUS commit's message. A
        unit this commit will name in prose alone, staging no artefact for it, therefore
        cannot be judged until the commit exists. The floor is still one commit behind for
        that case, and this test is what stops the docstring claiming otherwise."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "bug", 254, status="Fixed", affects=["src/one.py"])
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "chore: baseline")
            for n in ("two", "three"):
                (root / "src" / f"{n}.py").write_text("y = 2\n", encoding="utf-8")
            self._git(root, "add", "-A")
            before = {x["id"]: x for x in
                      _load().detect(root, include_staged=True)["units"]}["BG0254"]
            self.assertFalse(before["violation"])
            # ...and once the commit lands, naming it, the floor sees what it could not.
            self._git(root, "commit", "-q", "-m", "chore: more modules\n\nper BG0254")
            self.assertTrue(_units(root)["BG0254"]["violation"],
                            "premise: the landed commit DOES create the violation")

    def test_only_judged_artefact_ids_are_attributed(self):
        """The pending leg's id set is "the judged units this commit stages", and both
        halves of that need saying. An epic staged beside them is not a judged type, and a
        SOURCE file whose name happens to start with an id is not an artefact at all."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "bug", 260, status="Fixed", affects=["src/one.py"])
            epics = root / "sdlc-studio" / "epics"
            epics.mkdir(parents=True, exist_ok=True)
            (epics / "EP0103-sample.md").write_text("# EP0103: sample\n", encoding="utf-8")
            (root / "src").mkdir(exist_ok=True)
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            (root / "src" / "BG0261-helper.py").write_text("y = 2\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self.assertEqual(set(_load()._pending_touched_by_id(root)), {"BG0260"})

    def test_the_pending_leg_never_lowers_a_verdict(self):
        """One-directional by construction: it can only add files. A unit already in
        violation on committed evidence must not become clean because something is staged."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._init_repo(root)
            _write_unit(root, "bug", 255, status="Fixed",
                        affects=["src/one.py", "src/two.py"])
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            ef = _load()
            plain = {x["id"]: x for x in ef.detect(root)["units"]}["BG0255"]
            staged = {x["id"]: x for x in
                      ef.detect(root, include_staged=True)["units"]}["BG0255"]
            self.assertTrue(plain["violation"])
            self.assertTrue(staged["violation"])
            self.assertFalse(staged["staged_new"],
                             "a pre-existing violation is not one this commit creates")

    def test_the_flag_defaults_off_so_every_existing_caller_is_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage_a_multifile_delivery(root, num=256)
            result = _load().detect(root)
            self.assertFalse(result["summary"]["staged_evaluated"])
            self.assertEqual(result["summary"]["staged_new"], 0)
            self.assertFalse(result["units"][0]["staged_new"])


class PendingCliTests(unittest.TestCase):
    """`check --pending` is the lane the pre-commit hook runs: it judges the commit in
    hand, and says exactly what it could and could not see."""

    def _git(self, root, *args):
        gitutil.git(list(args), cwd=root, text=True)

    def _run(self, root, *args):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _load().main(["check", "--root", str(root), *args])
        return code, buf.getvalue()

    def _stage(self, root):
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "t@t")
        self._git(root, "config", "user.name", "t")
        _write_unit(root, "bug", 251, status="Fixed", affects=["src/one.py"])
        (root / "src").mkdir()
        for n in ("one", "two", "three"):
            (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
        self._git(root, "add", "-A")

    def test_pending_exits_non_zero_and_names_the_unit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage(root)
            code, out = self._run(root, "--pending")
            self.assertEqual(code, 1, out)
            self.assertIn("BG0251", out)

    def test_pending_reports_only_what_this_commit_creates(self):
        """The lane must not re-report the backlog the standing gate lane already fails
        on: a duplicated failure teaches an author to read past both."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._git(root, "init", "-q")
            self._git(root, "config", "user.email", "t@t")
            self._git(root, "config", "user.name", "t")
            # A pre-existing violation, committed and untouched by this commit...
            _write_unit(root, "story", 100, status="Done",
                        affects=["old/a.py", "old/b.py"])
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "chore: baseline")
            # ...and a clean staged commit.
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            code, out = self._run(root, "--pending")
            self.assertEqual(code, 0, out)
            self.assertNotIn("US0100", out)

    def test_pending_states_what_it_cannot_see(self):
        """The refusal covers the staged index; it does not cover the commit message,
        which git does not give a pre-commit hook."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage(root)
            _, out = self._run(root, "--pending")
            self.assertIn("commit message", out.lower())

    def test_the_green_pending_lane_also_states_its_scope(self):
        """And this is the one that matters, because a PASS is what gets read as "this
        commit is compliant" - which is the overclaim BG0251 filed. The refusal carrying
        the caveat while the pass drops it would leave the misreading exactly where it
        was."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._git(root, "init", "-q")
            self._git(root, "config", "user.email", "t@t")
            self._git(root, "config", "user.name", "t")
            _write_unit(root, "bug", 251, status="Fixed", affects=["src/one.py"], ac=True)
            (root / "src").mkdir()
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            self._git(root, "add", "-A")
            code, out = self._run(root, "--pending")
            self.assertEqual(code, 0, out)
            self.assertIn("commit message", out.lower())

    def test_the_gate_facing_detail_says_its_evidence_is_committed_history(self):
        """The same honesty, in the string the GATE prints. The CLI line and this one are
        separate strings, and only this one reaches an author running `gate.py`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done", affects=["a/one.py"])
            ef = _load()
            detail = ef.remedy_detail(ef.detect(root))
            self.assertIn("committed evidence", detail)

    def test_the_standing_lane_says_its_evidence_is_committed_history(self):
        """The adjacent honesty problem BG0251 names: a green floor means 'no ALREADY
        SHIPPED unit violates', not 'this commit is compliant'."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_unit(root, "story", 100, status="Done", affects=["a/one.py"])
            _, out = self._run(root)
            self.assertIn("committed", out.lower())

    def test_judgement_mode_keeps_the_pending_lane_advisory(self):
        """The project-global opt-out must reach the new lane too, or a project that opted
        out of the floor is blocked by it anyway."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage(root)
            _config(root, "engagement_floor: judgement\n")
            code, out = self._run(root, "--pending")
            self.assertEqual(code, 0, out)
            self.assertIn("BG0251", out)     # still reported, never silently dropped


class StagedIndexUnreadableTests(unittest.TestCase):
    """An unreadable index must REFUSE, never print a clean.

    Found by the closing review of RUN-01KY3MFX. `_staged_paths` returned `[]` both when git
    said nothing was staged and when git could not be asked, so a lane that could not read the
    index printed 'no new violation' and exited 0. That is a false clean on the one signal this
    leg exists to provide, and it is the floor committing the defect class the floor was built
    to catch."""

    def test_an_unreadable_index_raises_rather_than_reading_as_empty(self) -> None:
        mod = _load()   # ONE module object: `_load()` re-imports, so a second call would
                        # hand back a DIFFERENT exception class and assertRaises would miss it
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)          # not a git repository at all
            self.assertIsNone(mod._staged_paths(root),
                              "git could not be asked - that is None, never []")
            with self.assertRaises(mod.StagedIndexUnreadable):
                mod._pending_touched_by_id(root)

    def test_git_being_absent_entirely_is_also_unreadable_not_empty(self) -> None:
        """Found by a SURVIVING mutant. The non-git-directory case above reaches the
        `returncode != 0` branch, so the OSError branch - git missing from PATH, or the call
        raising - was pinned by nothing while reading as covered. Reverting it to `[]` left the
        suite green, which is the original defect returning unnoticed."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(mod.subprocess, "run",
                                   side_effect=OSError("git is not installed")):
                self.assertIsNone(mod._staged_paths(Path(d)))
            with mock.patch.object(mod.subprocess, "run",
                                   side_effect=mod.subprocess.TimeoutExpired("git", 5)):
                self.assertIsNone(mod._staged_paths(Path(d)),
                                  "a timeout is git failing to answer, not an empty index")

    def test_the_LANE_refuses_an_unreadable_index_not_just_the_library(self) -> None:
        """Found by round 2, and it is the whole user-visible half of this fix.

        The three tests above stop at `_staged_paths`, `_pending_touched_by_id` and `detect`.
        None of them enters `_cmd_check_pending`, which is what the pre-commit hook actually
        runs and what prints the verdict a human reads. Mutating that renderer's guard to
        `if False:` left all 3,891 tests green while the lane printed the original false clean
        verbatim - so the fix for the false-clean finding was itself unpinned, and its
        Resolution claimed it was mutation-proven.

        A library test is not a lane test. This asserts the exit code AND the printed text,
        because a silent refusal and a clean-looking refusal are the same to the reader."""
        mod = _load()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = mod._cmd_check_pending(
                {"summary": {"staged_unreadable": True, "judged": 7, "staged_new": 0},
                 "units": [], "mode": "enforce"})
        printed = out.getvalue()
        self.assertEqual(rc, 1, "an unreadable index must REFUSE, never exit 0")
        self.assertIn("REFUSED", printed)
        self.assertNotIn("no new violation", printed,
                         "the false-clean sentence must not be what the reader sees")

    def test_the_lane_still_reports_an_honest_clean_when_the_index_WAS_read(self) -> None:
        """The negative control. Without it a renderer that refused unconditionally would pass
        the test above while blocking every commit in the repository."""
        mod = _load()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = mod._cmd_check_pending(
                {"summary": {"staged_unreadable": False, "judged": 7, "staged_new": 0},
                 "units": [], "mode": "enforce"})
        printed = out.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("no new violation", printed)
        self.assertNotIn("REFUSED", printed)

    def test_detect_marks_the_run_unreadable_instead_of_reporting_no_violations(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = _load().detect(Path(d), include_staged=True)
            self.assertTrue(res["summary"]["staged_unreadable"])
            self.assertEqual(res["summary"]["staged_new"], 0,
                             "and the zero is explicitly NOT to be read as a clean")

    def test_an_empty_index_is_still_an_honest_empty(self) -> None:
        """The negative control. Without it, a function that always raised would pass the two
        assertions above while making the lane useless on every real commit."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gitutil.git(["init", "-q", "."], cwd=root)
            self.assertEqual(_load()._staged_paths(root), [],
                             "git ANSWERED that nothing is staged")
            self.assertEqual(_load()._pending_touched_by_id(root), {})


if __name__ == "__main__":
    unittest.main()
