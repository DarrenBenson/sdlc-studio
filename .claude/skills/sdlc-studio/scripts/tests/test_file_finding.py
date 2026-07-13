"""Unit tests for file_finding.py - the deterministic finding filer (RFC0002 WS3).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"


def _load():
    spec = importlib.util.spec_from_file_location("file_finding", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["file_finding"] = mod
    spec.loader.exec_module(mod)
    return mod


ff = _load()
sdlc_md = ff.sdlc_md


def _seed_index(root: Path, type_: str) -> Path:
    """A minimal valid index for a type (summary + empty data table)."""
    dirs = {"bug": ("bugs", "| ID | Title | Status | Severity | Created | Updated |",
                    "| Open | 0 |\n| Fixed | 0 |"),
            "cr": ("change-requests",
                   "| ID | Title | Status | Priority | Type | Date | Linked Epics |",
                   "| Proposed | 0 |\n| Complete | 0 |"),
            "rfc": ("rfcs", "| ID | Title | Priority | Status | Author | Date | Spawned CRs |",
                    "| Draft | 0 |\n| Accepted | 0 |")}
    rel, header, summary = dirs[type_]
    d = root / "sdlc-studio" / rel
    d.mkdir(parents=True, exist_ok=True)
    sep = "|" + " --- |" * (header.count("|") - 1)
    (d / "_index.md").write_text(
        f"# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n{summary}\n"
        f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    return d / "_index.md"


class FileTests(unittest.TestCase):
    def test_v3_files_finding_into_inbox(self) -> None:
        # US0065: the finding filer (the primary agent path) lands a v3 finding in `inbox`,
        # not its per-type create status; dormant under v2 (the other tests file into Open).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "schema_version: 3\n", encoding="utf-8")
            idx = _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a defect",
                                  {"severity": "high", "summary": "s", "steps": "r", "fix": "f"})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Status:** inbox", body)
            self.assertIn("| inbox |", idx.read_text(encoding="utf-8"))

    def test_v2_files_finding_into_create_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a defect",
                                  {"severity": "high", "summary": "s", "steps": "r", "fix": "f"})
            self.assertIn("> **Status:** Open",
                          Path(res["path"]).read_text(encoding="utf-8"))

    def test_files_cr_with_id_structure_and_index_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _seed_index(root, "cr")
            res = ff.file_finding(root, "cr", "Tighten the gate",
                                  {"priority": "High", "ctype": "Improvement",
                                   "summary": "It is loose.", "acs": ["it is tight", "tested"],
                                   "impact": "the gate lets bad units through", "effort": "M",
                                   "date": "2026-06-20"})
            self.assertEqual(res["id"], "CR-0001")
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("# CR-0001: Tighten the gate", body)
            self.assertIn("> **Status:** Proposed", body)
            self.assertIn("- [ ] it is tight", body)          # rich, not hollow
            index = idx.read_text(encoding="utf-8")
            self.assertIn("[CR-0001](CR0001-tighten-the-gate.md)", index)
            self.assertIn("| Proposed | 1 |", index)          # count recomputed
            self.assertIn("| **Total** | **1** |", index)

    def test_ac_with_own_checkbox_not_doubled(self) -> None:
        # An operator habitually passes '- [ ] text' as the AC; the renderer must
        # normalise, not stack a second checkbox in front (the CR0143-0149 defect).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            res = ff.file_finding(root, "cr", "t",
                                  {"priority": "Low", "ctype": "Improvement",
                                   "summary": "s",
                                   "acs": ["- [ ] already boxed", "-[x] ticked variant",
                                           "bare text"],
                                   "impact": "i", "effort": "S",
                                   "date": "2026-07-04"})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("- [ ] already boxed", body)
            self.assertNotIn("- [ ] - [ ]", body)
            self.assertNotIn("- [ ] -[x]", body)
            self.assertIn("- [ ] bare text", body)

    def test_allocates_next_id_no_collision(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            f = {"severity": "High", "summary": "x", "steps": "do y", "fix": "do z"}
            a = ff.file_finding(root, "bug", "first", f)
            b = ff.file_finding(root, "bug", "second", f)
            self.assertEqual(a["id"], "BG0001")
            self.assertEqual(b["id"], "BG0002")

    def test_rfc_records_options(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "rfc")
            res = ff.file_finding(root, "rfc", "Should we X",
                                  {"summary": "weigh it", "options": ["do X", "status quo"]})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertEqual(res["id"], "RFC-0001")
            self.assertIn("- **do X**", body)
            self.assertIn("## Design Options", body)

    def test_refuses_hollow_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            with self.assertRaises(ValueError):  # no acs / summary -> richness guard
                ff.file_finding(root, "cr", "empty", {"priority": "Low", "ctype": "Bug"})

    def test_unknown_type_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                ff.file_finding(Path(d), "story", "x", {"summary": "y"})

    def test_filed_finding_leaves_zero_drift(self) -> None:
        # The whole point of WS3: after filing, reconcile sees no drift.
        import importlib.util
        rc_spec = importlib.util.spec_from_file_location(
            "reconcile", SCRIPT.parent / "reconcile.py")
        rc = importlib.util.module_from_spec(rc_spec)
        sys.modules["reconcile"] = rc
        rc_spec.loader.exec_module(rc)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            ff.file_finding(root, "cr", "a clean finding",
                            {"priority": "High", "ctype": "Improvement",
                             "summary": "s", "acs": ["x"], "impact": "i", "effort": "S",
                             "date": "2026-06-20"})
            drift = rc.detect_type("cr", root)["drift"]
            self.assertEqual(drift, [], f"expected 0 drift, got {drift}")

    def test_pipe_in_title_does_not_corrupt_index(self) -> None:
        import importlib.util
        rc_spec = importlib.util.spec_from_file_location(
            "reconcile", SCRIPT.parent / "reconcile.py")
        rc = importlib.util.module_from_spec(rc_spec)
        sys.modules["reconcile"] = rc
        rc_spec.loader.exec_module(rc)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            res = ff.file_finding(root, "cr", "handle `a | b` inputs",
                                  {"priority": "Low", "ctype": "Bug", "summary": "s",
                                   "acs": ["y"], "impact": "i", "effort": "S",
                                   "date": "2026-06-20"})
            self.assertEqual(res["indexed"], True)
            self.assertEqual(rc.detect_type("cr", root)["drift"], [])  # escaped, parses

    def test_summary_only_index_not_corrupted(self) -> None:
        # An index with a Summary table but no data table: the row is not glued into
        # the summary block (it is left unindexed rather than corrupting).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "_index.md").write_text(
                "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
                "| Proposed | 0 |\n| **Total** | **0** |\n", encoding="utf-8")
            res = ff.file_finding(root, "cr", "x", {"priority": "Low", "ctype": "Bug",
                                                    "summary": "s", "acs": ["y"],
                                                    "impact": "i", "effort": "S"})
            self.assertFalse(res["indexed"])  # no data table -> not appended
            self.assertNotIn("[CR-0001]", (cd / "_index.md").read_text(encoding="utf-8"))


class AppendBoundToMasterTableTests(unittest.TestCase):
    def test_row_lands_in_master_not_a_trailing_view_table(self) -> None:
        # BG0066: append_index_row scanned to EOF and inserted after the LAST `| [` row
        # anywhere - so a trailing "by Epic" view table captured the new row. The insert
        # must stay within the master data table's contiguous rows.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            idx = sd / "_index.md"
            # The trailing view table has LINK-FIRST rows (`| [US...`), which the unbounded
            # scan would treat as the last data row and insert after - escaping the master.
            idx.write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
                "| Done | 1 |\n| **Total** | **1** |\n\n"
                "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | one | Done |\n\n"
                "## Recently Touched\n\n| Story | Status |\n| --- | --- |\n"
                "| [US0001](US0001-x.md) | Done |\n",
                encoding="utf-8")
            ff.append_index_row(root, "story",
                                "| [US0002](US0002-y.md) | two | Ready |")
            text = idx.read_text(encoding="utf-8")
            lines = text.splitlines()
            all_i = lines.index("## All")
            byepic_i = lines.index("## Recently Touched")
            # The new row sits inside the master (## All) block, before the view section.
            new_row_lines = [i for i, ln in enumerate(lines) if "US0002" in ln]
            self.assertTrue(new_row_lines)
            self.assertTrue(all(all_i < i < byepic_i for i in new_row_lines),
                            f"US0002 row escaped the master table: {new_row_lines} "
                            f"(All@{all_i}, byEpic@{byepic_i})")


class ProvenanceAndDryRunTests(unittest.TestCase):
    def test_filed_artifact_is_stamped(self) -> None:
        # CR0057: the filer stamps like `artifact new`, so provenance check no longer
        # false-flags filer-created artifacts.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _seed_index(root, "bug")
            r = ff.file_finding(root, "bug", "a defect",
                                {"severity": "High", "summary": "s", "steps": "x", "fix": "y"})
            self.assertIn("> **Created-by:** sdlc-studio", Path(r["path"]).read_text())

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); idx = _seed_index(root, "bug")
            before = idx.read_text()
            r = ff.file_finding(root, "bug", "preview only",
                                {"severity": "Low", "summary": "s", "steps": "x", "fix": "y"},
                                dry_run=True)
            self.assertTrue(r["dry_run"])
            self.assertFalse(Path(r["path"]).exists())   # no artifact written
            self.assertEqual(idx.read_text(), before)    # index untouched


class EraAwareAllocationTests(unittest.TestCase):
    def test_v3_project_mints_a_ulid_finding_id(self) -> None:
        # BG-era gap: the filer minted v2 sequential ids on schema-v3 projects, undermining
        # collision-free identity exactly on the primary agent filing path.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "schema_version: 3\n", encoding="utf-8")
            idx = _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "era probe",
                                  {"severity": "high", "summary": "s", "steps": "r", "fix": "f"})
            self.assertTrue(sdlc_md.is_v3_id(res["id"]), res["id"])
            self.assertTrue(Path(res["path"]).name.startswith(res["id"] + "-"), res["path"])
            self.assertIn(res["id"], idx.read_text(encoding="utf-8"))

    def test_v2_project_still_mints_sequential(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "era probe",
                                  {"severity": "high", "summary": "s", "steps": "r", "fix": "f"})
            self.assertEqual(res["id"], "BG0001")



class MdSafeProseTests(unittest.TestCase):
    """BG0097: the filer must not mint markdownlint-breaking artefacts - underscore
    identifiers in prose are backtick-wrapped so MD037/MD050 do not fire."""

    def test_underscore_tokens_backticked_in_rendered_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a defect",
                                  {"severity": "high",
                                   "summary": "calls _next_number then __main__ runs",
                                   "steps": "r", "fix": "f"})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("`_next_number`", body)
            self.assertIn("`__main__`", body)
            # no BARE underscore-emphasis pair survives on the summary line
            self.assertNotIn(" _next_number ", body)

    def test_already_backticked_not_doubled(self) -> None:
        self.assertEqual(ff._md_safe("uses `_next_number` here"), "uses `_next_number` here")


def _rev_row(body: str) -> str:
    """The first Revision History data row of a rendered artefact."""
    lines = body.splitlines()
    head = next(i for i, ln in enumerate(lines) if ln.strip().startswith("## Revision History"))
    rows = [ln for ln in lines[head:] if ln.strip().startswith("|")]
    return rows[2]  # header, separator, then the created/filed row


class RevisionAuthorTests(unittest.TestCase):
    """The Revision History Author cell is the authorship of record, not a hardcoded literal:
    the provenance tooling must not mint a false provenance record."""

    FIELDS = {"bug": {"severity": "High", "summary": "s", "steps": "x", "fix": "y"},
              "cr": {"priority": "High", "ctype": "Improvement", "summary": "s",
                     "acs": ["a"], "impact": "i", "effort": "M"},
              "rfc": {"summary": "s", "options": ["Option A"]}}

    def _file(self, root: Path, type_: str, **extra) -> str:
        _seed_index(root, type_)
        res = ff.file_finding(root, type_, "a finding",
                              {**self.FIELDS[type_], "date": "2026-07-13", **extra})
        return Path(res["path"]).read_text(encoding="utf-8")

    def test_named_author_reaches_the_revision_history(self) -> None:
        for type_ in ("bug", "cr", "rfc"):
            with self.subTest(type=type_), tempfile.TemporaryDirectory() as d:
                body = self._file(Path(d), type_, author="Dani Okafor")
                row = _rev_row(body)
                self.assertIn("| Dani Okafor |", row)
                self.assertNotIn("audit", row)

    def test_typed_author_triple_renders_the_name_only(self) -> None:
        # The table cell carries a NAME; the typed triple belongs in `Raised-by`.
        with tempfile.TemporaryDirectory() as d:
            body = self._file(Path(d), "rfc", author="Claude (Fable 5); agent; v5")
            self.assertIn("> **Raised-by:** Claude (Fable 5); agent; v5", body)
            row = _rev_row(body)
            self.assertIn("| Claude (Fable 5) |", row)
            self.assertNotIn(";", row)

    def test_unattributed_filing_names_the_invoking_agent(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as d:
            prev = os.environ.get("SDLC_AUTHOR")
            os.environ["SDLC_AUTHOR"] = "Sprint Driver; agent; v1"
            try:
                body = self._file(Path(d), "bug")
            finally:
                os.environ.pop("SDLC_AUTHOR")
                if prev is not None:
                    os.environ["SDLC_AUTHOR"] = prev
            row = _rev_row(body)
            self.assertIn("| Sprint Driver |", row)
            self.assertNotIn("audit", row)

    def test_pipe_in_author_does_not_shift_the_revision_columns(self) -> None:
        # A raw `|` in a cell silently adds a column and drops the Change value. Every other
        # row writer escapes it; the history row must too.
        with tempfile.TemporaryDirectory() as d:
            row = _rev_row(self._file(Path(d), "bug", author="Sam | Bob"))
            self.assertEqual(len(sdlc_md.table_cells(row)), 3, row)
            self.assertIn("Filed", row)


class ConsolidationRevisionAuthorTests(unittest.TestCase):
    """BG0109's own Steps to Reproduce run through the consolidation branch on schema v3: a
    Low-severity finding never reaches the per-type render, so the CR it folds into must
    resolve its author the same way."""

    def _low_finding(self, root: Path, **extra) -> str:
        _seed_index(root, "bug")
        _seed_index(root, "cr")
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
        res = ff.file_finding(root, "bug", "a low defect",
                              {"severity": "Low", "summary": "s", "steps": "x", "fix": "y",
                               "date": "2026-07-13", **extra})
        return Path(res["path"]).read_text(encoding="utf-8")

    def test_consolidation_cr_names_the_author(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            body = self._low_finding(Path(d), author="Dani Okafor; agent; v2")
            self.assertIn("> **Raised-by:** Dani Okafor; agent; v2", body)
            row = _rev_row(body)
            self.assertIn("| Dani Okafor |", row)
            self.assertNotIn("audit", row)

    def test_unattributed_consolidation_names_the_invoking_agent(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as d:
            prev = os.environ.get("SDLC_AUTHOR")
            os.environ["SDLC_AUTHOR"] = "Sprint Driver; agent; v1"
            try:
                body = self._low_finding(Path(d))
            finally:
                os.environ.pop("SDLC_AUTHOR")
                if prev is not None:
                    os.environ["SDLC_AUTHOR"] = prev
            self.assertIn("| Sprint Driver |", _rev_row(body))


class MetadataInjectionRefusalTests(unittest.TestCase):
    """The filer inherits the resolver's refusal: a field carrying a line break is refused
    before any write, so no artefact is minted with metadata lines nobody asked for and no
    index row splits across two lines."""

    BREAK = "\n> **Status:** Fixed"

    def _bug(self, **over) -> dict:
        return {"severity": "High", "summary": "s", "steps": "r", "fix": "f", **over}

    def _nothing_written(self, root: Path) -> None:
        d = root / "sdlc-studio" / "bugs"
        self.assertEqual([p.name for p in d.glob("*.md") if p.name != "_index.md"], [])
        idx = (d / "_index.md").read_text(encoding="utf-8")
        self.assertEqual([ln for ln in idx.splitlines() if ln.startswith("| [")], [])

    def test_multi_line_author_is_refused_and_nothing_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            with self.assertRaises(ValueError) as cm:
                ff.file_finding(root, "bug", "t", self._bug(author="Sam\nEvil: injected"))
            self.assertIn("author", str(cm.exception))
            self._nothing_written(root)

    def test_multi_line_title_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            with self.assertRaises(ValueError) as cm:
                ff.file_finding(root, "bug", "Silent" + self.BREAK, self._bug())
            self.assertIn("title", str(cm.exception))
            self._nothing_written(root)

    def test_multi_line_severity_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            with self.assertRaises(ValueError):
                ff.file_finding(root, "bug", "t", self._bug(severity="Low" + self.BREAK))
            self._nothing_written(root)

    def test_multi_line_cr_criterion_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            with self.assertRaises(ValueError) as cm:
                ff.file_finding(root, "cr", "t",
                                {"priority": "High", "ctype": "Improvement", "summary": "s",
                                 "impact": "i", "effort": "S",
                                 "acs": ["ok", "do it\n- [ ] and this"]})
            self.assertIn("acs", str(cm.exception))

    def test_a_clean_finding_still_files(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a real defect",
                                  self._bug(author="Dani Okafor; agent; v2"))
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Raised-by:** Dani Okafor; agent; v2", body)
            self.assertTrue(res["indexed"])


if __name__ == "__main__":
    unittest.main()
