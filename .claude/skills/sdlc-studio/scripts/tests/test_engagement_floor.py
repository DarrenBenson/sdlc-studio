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
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
        subprocess.run(["git", "-C", str(root), *args], check=True,
                       capture_output=True, text=True)

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
        subprocess.run(["git", "-C", str(root), *args], check=True,
                       capture_output=True, text=True)

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
        subprocess.run(["git", "-C", str(root), *args], check=True,
                       capture_output=True, text=True)

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
        subprocess.run(["git", "-C", str(root), *args], check=True,
                       capture_output=True, text=True)

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


if __name__ == "__main__":
    unittest.main()
