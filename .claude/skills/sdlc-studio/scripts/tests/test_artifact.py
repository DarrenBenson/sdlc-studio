"""Unit tests for artifact.py - deterministic create + close cascade (CR0045)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
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


def _index(repo: Path, type_: str, header: str) -> None:
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
            r = artifact.new(repo, "bug", "a defect")
            self.assertRegex(r["id"], r"^BG-[0-9A-HJKMNP-TV-Z]{8,}$")
            self.assertEqual(r["id"], r["file_id"])   # v3: one canonical form
            self.assertTrue(r["indexed"])
            self.assertTrue(Path(r["path"]).exists())

    def test_v3_two_allocations_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _v3(repo)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            a = artifact.new(repo, "bug", "one")
            b = artifact.new(repo, "bug", "two")
            self.assertNotEqual(a["id"], b["id"])
            self.assertEqual(reconcile.detect_type("bug", repo)["drift"], [])

    def test_v2_default_stays_sequential(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "change")
            self.assertEqual(r["id"], "CR-0001")   # no .config.yaml -> v2 sequential

    def test_v3_findings_file_into_inbox(self) -> None:
        # US0065: under v3 a filed finding lands in `inbox` (file body + index row),
        # not the per-type create status.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _v3(repo)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "a defect")
            self.assertIn("> **Status:** inbox", Path(r["path"]).read_text(encoding="utf-8"))
            idx = (repo / "sdlc-studio" / "bugs" / "_index.md").read_text(encoding="utf-8")
            self.assertIn("| inbox |", idx)
            self.assertEqual(reconcile.detect_type("bug", repo)["drift"], [])

    def test_v2_findings_keep_create_status(self) -> None:
        # No schema_version:3 -> a bug still files Open (era-gating leaves v2 untouched).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "a defect")
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
            r = artifact.new(repo, "cr", "change something")
            self.assertTrue(r["id"].startswith("CR-"))   # dash form
            self.assertTrue(r["file_id"].startswith("CR") and "-" not in r["file_id"])
            self.assertTrue(r["indexed"])

    def test_all_types_scaffold_validates(self) -> None:
        for t in artifact.SPEC:
            with tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                (repo / "sdlc-studio").mkdir(parents=True)
                if t == "story":
                    _epic(repo)  # a story needs an existing parent epic (BG0022)
                fields = {"epic": "EP0001"} if t == "story" else {}
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
            artifact.new(repo, "cr", "widthcheck")
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
            sd = repo / "sdlc-studio" / "change-requests"; sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# Index\n\n## All\n\n| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| [CR-0005](CR0005-x.md) | gone | Done | Medium | Feature | 2026-01-01 | - |\n",
                encoding="utf-8")  # row present, file absent
            r = artifact.new(repo, "cr", "fresh")
            self.assertEqual(r["file_id"], "CR0006")  # above the lingering CR0005 row, not CR0001

    def test_pipe_in_title_escaped_in_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            artifact.new(repo, "cr", "a | b piped")
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
            r = artifact.new(repo, "bug", "no index here")
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
            r = artifact.new(repo, "cr", "preview", dry_run=True)
            self.assertTrue(r["dry_run"])
            self.assertFalse(Path(r["path"]).exists())
            self.assertEqual(idx.read_text(), before)

    def test_close_dry_run_does_not_transition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "to keep open", {"epic": "EP0001"})
            before = Path(r["path"]).read_text()
            import telemetry
            res = artifact.close(repo, r["id"], dry_run=True)
            self.assertTrue(res["dry_run"])
            self.assertEqual(Path(r["path"]).read_text(), before)  # status unchanged
            self.assertEqual(telemetry.read_all(repo), [])         # no telemetry recorded


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


class ProjectTemplateTests(unittest.TestCase):
    """RFC-0023 write path: `new` scaffolds the project's declared template
    (conventions.templates.<type>) so the scaffold matches the house shape the
    read-side checks expect - the skill default stays the fallback."""

    HOUSE = ("<!-- house bug template -->\n\n# {{id}}: {{title}}\n\n"
             "## Symptom\n\n{{symptom}}\n\n## Root cause\n\n{{cause}}\n\n"
             "## Fix (proposed)\n\n{{fix}}\n\n## Verify\n\n{{verify}}\n")

    def _repo(self, d, declare=True, write_template=True):
        repo = Path(d)
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
            r = artifact.new(repo, "bug", "wrong colour", {})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("**Created-by:** sdlc-studio new", text)  # provenance head intact
            self.assertIn("## Symptom", text)                        # house body grafted
            self.assertIn("## Fix (proposed)", text)
            self.assertNotIn("## Steps to Reproduce", text)          # skill body replaced

    def test_undeclared_project_uses_skill_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, declare=False)
            r = artifact.new(repo, "bug", "wrong colour", {})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("## Steps to Reproduce", text)             # v3.4.0 behaviour

    def test_declared_but_missing_template_fails_loud(self) -> None:
        self._yaml()
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, write_template=False)
            from lib import conventions
            with self.assertRaises(conventions.ConventionsError):
                artifact.new(repo, "bug", "wrong colour", {})


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

    def test_new_review_without_index_reports_honestly(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "reviews").mkdir(parents=True)
            res = artifact.meta_new(root, "review", "Adversarial code review")
            self.assertTrue(res["id"].startswith("RV-"))
            self.assertFalse(res["indexed"])                 # no index -> honest False
            self.assertTrue(Path(res["path"]).exists())

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
            r = artifact.new(repo, "bug", "ulid close probe")
            self.assertTrue(sdlc_md.is_v3_id(r["id"]), r["id"])
            res = artifact.close(repo, r["id"], dry_run=True)
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
                                    "--severity", "Low", "--root", str(repo), "--dry-run"])
            self.assertEqual(rc, 0, buf.getvalue())
            self.assertIn("consolidate", buf.getvalue())

    def test_low_consolidation_create_and_append_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d); self._v3_cr_ready(repo)
            for i, expect_created in ((1, "created=True"), (2, "created=False")):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = artifact.main(["new", "--type", "bug", "--title", f"low probe {i}",
                                        "--severity", "Low", "--root", str(repo)])
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
            r = artifact.new(repo, "cr", "from an issue", {"provenance": "external"})
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Provenance:** external", body)
            self.assertEqual(sdlc_md.extract_field(body, "Provenance"), "external")

    def test_default_new_carries_no_provenance_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Date | Linked Epics |")
            r = artifact.new(repo, "cr", "home grown")
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

if __name__ == "__main__":
    unittest.main()
