"""Unit tests for file_finding.py - the deterministic finding filer (RFC0002 WS3).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for gitutil

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:  # pragma: no cover - the stdlib-only machine
    HAVE_YAML = False

SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"


def _load():
    spec = importlib.util.spec_from_file_location("file_finding", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["file_finding"] = mod
    spec.loader.exec_module(mod)
    return mod


ff = _load()
sdlc_md = ff.sdlc_md

# Every bug/CR fixture below is GROOMED - it names the files it will touch and its job size -
# because both creators now REFUSE a finding `sprint plan` could not plan (BG0136). The ungroomed
# shape is the subject of GroomingGateTests, never an accident in a fixture. Size by what a thing
# IS: a bug carries `points` (a measured delivery unit), a CR carries a T-shirt `size` (a request,
# sized before decomposition). This fixture carries both so it grooms whichever type uses it - the
# bug renderer reads `points`, the CR renderer reads `size`, and neither writes the other's field.
GROOM = {"affects": "src/thing.py", "points": 3, "size": "M"}
BUG = {"severity": "high", "summary": "s", "steps": "r", "fix": "f", **GROOM}

# BG0144: the grooming gate now REFUSES a bug/CR whose declared `Affects` paths ALL fail to
# resolve on disk. Every groomed fixture below declares a path from this superset, so the shared
# setup makes each one REAL at the repo root. Deliberate-refusal fixtures (missing/bad Affects,
# multi-line fields, unknown type) declare no path from here - or none at all - so they stay
# refused for the reason under test.
_STUB_AFFECTS = ("src/thing.py", "src/other.py", "src/x.py", "src/gate.py")


def _affect(root: Path, rel: str) -> None:
    """Make a declared `Affects` path real on disk so the grooming gate can resolve it."""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")


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
    for rel in _STUB_AFFECTS:
        _affect(root, rel)
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
            res = ff.file_finding(root, "bug", "a defect", dict(BUG))
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Status:** inbox", body)
            self.assertIn("| inbox |", idx.read_text(encoding="utf-8"))

    def test_v2_files_finding_into_create_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a defect", dict(BUG))
            self.assertIn("> **Status:** Open",
                          Path(res["path"]).read_text(encoding="utf-8"))

    def test_files_cr_with_id_structure_and_index_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _seed_index(root, "cr")
            res = ff.file_finding(root, "cr", "Tighten the gate",
                                  {"priority": "High", "ctype": "Improvement",
                                   "summary": "It is loose.", "acs": ["it is tight", "tested"],
                                   "impact": "the gate lets bad units through", "size": "M",
                                   "affects": "src/gate.py", "date": "2026-06-20"})
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
                                   "impact": "i", "size": "M", "affects": "src/x.py",
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
            f = {"severity": "High", "summary": "x", "steps": "do y", "fix": "do z", **GROOM}
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
                             "summary": "s", "acs": ["x"], "impact": "i", "size": "M",
                             "affects": "src/x.py", "date": "2026-06-20"})
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
                                   "acs": ["y"], "impact": "i", "size": "M",
                                   "affects": "src/x.py", "date": "2026-06-20"})
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
            _affect(root, "src/x.py")
            res = ff.file_finding(root, "cr", "x", {"priority": "Low", "ctype": "Bug",
                                                    "summary": "s", "acs": ["y"],
                                                    "impact": "i", "size": "M",
                                                    "affects": "src/x.py"})
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
                                {"severity": "High", "summary": "s", "steps": "x", "fix": "y",
                                 **GROOM})
            self.assertIn("> **Created-by:** sdlc-studio", Path(r["path"]).read_text())

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); idx = _seed_index(root, "bug")
            before = idx.read_text()
            r = ff.file_finding(root, "bug", "preview only",
                                {"severity": "Low", "summary": "s", "steps": "x", "fix": "y",
                                 **GROOM},
                                dry_run=True)
            self.assertTrue(r["dry_run"])
            self.assertFalse(Path(r["path"]).exists())   # no artifact written
            self.assertEqual(idx.read_text(), before)    # index untouched


class ProseMetadataLineTests(unittest.TestCase):
    """BG0117: a prose field (summary/steps/fix/impact/recommendation) is multi-line by
    design, so it stays unguarded - but a line inside it that mimics a `> **Field:** value`
    metadata declaration must be rendered so neither extract_field nor a reader mistakes body
    prose for a provenance stamp."""

    def test_summary_cannot_invent_a_metadata_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _seed_index(root, "bug")
            r = ff.file_finding(root, "bug", "prose metadata",
                                {"severity": "High",
                                 "summary": "ok\n> **Waived:** yes",
                                 "steps": "x", "fix": "y", **GROOM})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIsNone(sdlc_md.extract_field(text, "Waived"),
                              "a prose line must not forge a Waived metadata field")
            self.assertIn("Waived", text)   # the author's words are still present, not dropped

    def test_bare_metadata_shape_without_blockquote_also_neutralised(self) -> None:
        # extract_field's `>` is optional, so a leading `**Field:**` (no `>`) forges a field
        # the head lacks just as readily - the escape must catch it too.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _seed_index(root, "bug")
            r = ff.file_finding(root, "bug", "bare metadata",
                                {"severity": "High",
                                 "summary": "detail\n**Injected:** x",
                                 "steps": "x", "fix": "y", **GROOM})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIsNone(sdlc_md.extract_field(text, "Injected"))

    def test_inline_middot_metadata_run_neutralised(self) -> None:
        # extract_field anchors a field on TWO branches: a line start (optional `>`) AND an
        # inline ` · `-separated run. A line-start-only escape leaks the inline shape, so the
        # escape must mirror both branches - exactly what extract_field can read, no wider.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _seed_index(root, "bug")
            r = ff.file_finding(root, "bug", "inline metadata",
                                {"severity": "High",
                                 "summary": "ok · **Waived:** yes",
                                 "steps": "x", "fix": "y", **GROOM})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIsNone(sdlc_md.extract_field(text, "Waived"),
                              "an inline `·`-separated run must not forge a metadata field")
            self.assertIn("Waived", text)   # the author's words stay present

    def test_non_ascii_whitespace_after_anchor_neutralised(self) -> None:
        # extract_field uses `\s*` after its anchor, which matches NBSP (U+00A0), thin space,
        # form feed, etc. A `[ \t]` escape is NARROWER, so an invisible NBSP after a `·` or `>`
        # leaks a forged field. The escape must mirror the whole whitespace class (bar newline).
        variants = {
            "Waived": "affects auth ·\xa0**Waived:** yes",     # NBSP after the middot
            "Approved": ">\xa0**Approved:** true",              # NBSP after the blockquote
            "Injected": "\xa0**Injected:** x",                  # leading NBSP, bare declaration
        }
        for field, summary in variants.items():
            with tempfile.TemporaryDirectory() as d:
                root = Path(d); _seed_index(root, "bug")
                r = ff.file_finding(root, "bug", f"nbsp {field}",
                                    {"severity": "High", "summary": summary,
                                     "steps": "x", "fix": "y", **GROOM})
                text = Path(r["path"]).read_text(encoding="utf-8")
                self.assertIsNone(sdlc_md.extract_field(text, field),
                                  f"non-ASCII whitespace before {field} must not forge a field")

    def test_middot_then_newline_field_caught_by_line_start_branch(self) -> None:
        # A `·\n**Field:**` run (middot, newline, field at the next line start) must still be
        # caught - by the line-start branch, since the field now opens a line. The `·` branch is
        # deliberately horizontal-only (no newline crossing); the two branches together cover it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _seed_index(root, "bug")
            r = ff.file_finding(root, "bug", "middot newline",
                                {"severity": "High",
                                 "summary": "lead ·\n**Waived:** yes",
                                 "steps": "x", "fix": "y", **GROOM})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIsNone(sdlc_md.extract_field(text, "Waived"))

    def test_genuine_inline_bold_is_not_over_escaped(self) -> None:
        # extract_field does NOT read `**important:**` in mid-sentence prose (no line-start /
        # no `·` anchor), so the escape must leave it alone - match extract_field exactly.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _seed_index(root, "bug")
            r = ff.file_finding(root, "bug", "inline bold",
                                {"severity": "High",
                                 "summary": "the **important:** note stays bold",
                                 "steps": "x", "fix": "y", **GROOM})
            text = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("the **important:** note", text)   # untouched, not escaped


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
            res = ff.file_finding(root, "bug", "era probe", dict(BUG))
            self.assertTrue(sdlc_md.is_v3_id(res["id"]), res["id"])
            self.assertTrue(Path(res["path"]).name.startswith(res["id"] + "-"), res["path"])
            self.assertIn(res["id"], idx.read_text(encoding="utf-8"))

    def test_v2_project_still_mints_sequential(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "era probe", dict(BUG))
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
                                   "steps": "r", "fix": "f", **GROOM})
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

    FIELDS = {"bug": {"severity": "High", "summary": "s", "steps": "x", "fix": "y", **GROOM},
              "cr": {"priority": "High", "ctype": "Improvement", "summary": "s",
                     "acs": ["a"], "impact": "i", "size": "M", "affects": "src/x.py"},
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
                               "date": "2026-07-13", **GROOM, **extra})
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
        return {"severity": "High", "summary": "s", "steps": "r", "fix": "f", **GROOM, **over}

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
                                 "impact": "i", "size": "M", "affects": "src/x.py",
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


class BugSizeTests(unittest.TestCase):
    """A bug declares a job SIZE. It only ever carried Severity, which is urgency, so a bug
    could not be sized even in principle and always planned at the neutral default. The size is
    `Points` on the modified Fibonacci scale - the one size vocabulary (see test_points.py)."""

    FIELDS = {"severity": "High", "summary": "s", "steps": "x", "fix": "y",
              "affects": "src/thing.py"}

    def test_declared_points_land_in_the_filed_bug(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a defect", {**self.FIELDS, "points": 8})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.read_points(body), 8)

    def test_cli_accepts_points_for_a_bug(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc = ff.main(["file", "--type", "bug", "--title", "a defect", "--severity", "High",
                          "--summary", "s", "--steps", "x", "--fix", "y", "--points", "3",
                          "--affects", "src/thing.py", "--root", str(root)])
            self.assertEqual(rc, 0)
            filed = next((root / "sdlc-studio" / "bugs").glob("BG0001-*.md"))
            self.assertEqual(
                sdlc_md.read_points(filed.read_text(encoding="utf-8")), 3)


def _load_sprint():
    """The planner, loaded as the tests load every sibling - the filer is judged against the
    REAL gate, not a re-description of it."""
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT.parent / "sprint.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod


class GroomingGateTests(unittest.TestCase):
    """BG0136: the filer wrote artefacts the planner then refused.

    `sprint plan` refuses an UNGROOMED unit - one declaring neither the files it touches nor a
    size - but `file_finding` had no `--affects` flag at all, so every bug it filed was born
    ungroomed and unplannable. The two ends of one pipeline disagreed about what a complete
    artefact IS (LL0016).

    The load-bearing pair is the ROUND TRIP, through the public CLI: a bug filed with no
    `--affects` is REFUSED, and the same bug filed WITH `--affects`/`--points` is accepted AND
    then passes the planner's own breakdown gate. Behaviour only - nothing here greps a source
    file for a string.
    """

    def _file(self, root: Path, *extra: str) -> tuple[int, str]:
        err = io.StringIO()
        argv = ["file", "--type", "bug", "--title", "the parser drops a dash",
                "--severity", "High", "--summary", "s", "--steps", "x", "--fix", "y",
                "--root", str(root), *extra]
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = ff.main(argv)
        except ValueError as exc:      # the refusal the CLI wrapper turns into exit 1
            return 1, str(exc)
        return rc, err.getvalue()

    def _bugs(self, root: Path) -> list[Path]:
        return [p for p in (root / "sdlc-studio" / "bugs").glob("*.md") if p.name != "_index.md"]

    def _breakdown(self, root: Path, filed: Path) -> dict:
        """The PLANNER's verdict on the filed artefact - `sprint.breakdown` itself, the same
        predicate `sprint plan` refuses on."""
        sprint = _load_sprint()
        return sprint.breakdown(root, [{"id": filed.stem.split("-")[0], "type": "bug",
                                        "path": str(filed)}], skip_personas=True)

    def test_a_bug_filed_without_affects_is_refused_and_nothing_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _seed_index(root, "bug")
            before = idx.read_text(encoding="utf-8")
            rc, msg = self._file(root, "--points", "5")
            self.assertEqual(rc, 1)
            self.assertEqual(self._bugs(root), [])          # no artefact minted
            self.assertEqual(idx.read_text(encoding="utf-8"), before)   # no index row, no id burnt
            self.assertIn("Affects", msg)                   # the refusal names what is missing
            self.assertIn("--affects", msg)                 # ... and the flag that supplies it

    def test_a_bug_filed_without_a_size_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, msg = self._file(root, "--affects", "src/thing.py")
            self.assertEqual(rc, 1)
            self.assertEqual(self._bugs(root), [])
            self.assertIn("--points", msg)

    def test_the_round_trip_filed_then_plannable_on_its_footprint(self) -> None:
        # THE bug. File it the way the tool now allows, and the planner must not refuse it for
        # anything the FILER could have prevented - a filed artefact refused on its footprint is
        # not a fix.
        #
        # BG0511 narrowed this deliberately, and the narrowing is the point rather than a
        # concession. The contract used to be "filed, therefore plannable", full stop, and that
        # is precisely what let sixteen units reach a plannable backlog carrying criteria nobody
        # could judge - five with no criteria at all, which `transition` then refused outright.
        # The filer writes what the evidence supports: a criterion derived from the finding's own
        # prose, or a stated absence when even that is unsupported. Neither is a criterion a
        # reviewer can rule on, and both are the RIGHT thing to write at capture time.
        #
        # So the boundary now sits where the knowledge does. Footprint - `Affects`, `Points` -
        # is known at filing and is refused at filing. Criteria are authored at grooming and are
        # refused at planning. Two gates, each asking for something its caller can actually
        # supply.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, _ = self._file(root, "--affects", "src/thing.py, src/other.py",
                               "--points", "5")
            self.assertEqual(rc, 0)
            filed = self._bugs(root)[0]
            text = filed.read_text(encoding="utf-8")
            # the field is not just present - the planner's own parser reads it back
            self.assertEqual(sdlc_md.affects_files(text), ["src/thing.py", "src/other.py"])
            bd = self._breakdown(root, filed)
            gaps = " ".join(bd["ungroomed"][0]["missing"]) if bd["ungroomed"] else ""
            self.assertNotIn("Affects", gaps, "the planner refused the footprint the filer wrote")
            self.assertNotIn("Points", gaps, "the planner refused the size the filer wrote")

    def test_a_freshly_filed_finding_still_owes_its_criteria_at_plan_time(self) -> None:
        """The other half of the narrowed contract, pinned so it cannot quietly revert. A filed
        finding is capture; it is not yet plannable work. If this ever passes as groomed, the
        census is back to admitting units nobody can judge - which is BG0511."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, _ = self._file(root, "--affects", "src/thing.py", "--points", "3")
            self.assertEqual(rc, 0)
            bd = self._breakdown(root, self._bugs(root)[0])
            self.assertEqual([u["id"] for u in bd["ungroomed"]], ["BG0001"])
            self.assertIn("Acceptance Criteria", " ".join(bd["ungroomed"][0]["missing"]))
            self.assertFalse(bd["ok"])

    def test_an_affects_the_planner_cannot_read_is_refused(self) -> None:
        # The filer asks the PLANNER, so a value that is not a readable path list counts as no
        # `Affects` at all - a restated rule would have accepted this and minted a unit the
        # planner then refuses, which is the bug in a new place.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, msg = self._file(root, "--affects", "everything", "--points", "5")
            self.assertEqual(rc, 1)
            self.assertEqual(self._bugs(root), [])
            self.assertIn("Affects", msg)

    def test_dry_run_refuses_too(self) -> None:
        # A preview that says "would file" over an artefact the filer would refuse is a lie.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, _ = self._file(root, "--dry-run")
            self.assertEqual(rc, 1)

    def test_an_rfc_needs_no_grooming(self) -> None:
        # An RFC is not a unit of sprint work - the planner never selects one - and its files
        # are the OUTPUT of the decision it exists to settle. Demanding `Affects` of it would be
        # a field nothing downstream reads. It still RECORDS one when the author has it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "rfc")
            res = ff.file_finding(root, "rfc", "how ids should be minted",
                                  {"summary": "weigh it", "options": ["A", "B"]})
            self.assertTrue(Path(res["path"]).exists())
            res2 = ff.file_finding(root, "rfc", "another design",
                                   {"summary": "s", "options": ["A"], "affects": "src/ids.py"})
            self.assertEqual(
                sdlc_md.affects_files(Path(res2["path"]).read_text(encoding="utf-8")),
                ["src/ids.py"])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed - config-driven opt-out unreadable")
class GroomingOptOutTests(unittest.TestCase):
    """The escape is the PLANNER's, honoured at the filer: a project that records
    `sprint.breakdown: judgement` has decided the lane reports instead of blocking, and it must
    not then be blocked at the filer. Omission is not an escape."""

    def _config(self, root: Path, body: str) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")

    def test_judgement_mode_files_the_ungroomed_bug_with_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self._config(root, "sprint:\n  breakdown: judgement\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                res = ff.file_finding(root, "bug", "a defect",
                                      {"severity": "High", "summary": "s", "steps": "x",
                                       "fix": "y"})
            self.assertTrue(Path(res["path"]).exists())     # written: the operator opted out
            self.assertIn("ungroomed", err.getvalue())      # ... but never quietly

    def test_an_absent_config_still_demands_the_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self._config(root, "schema_version: 2\n")       # config present, no opt-out recorded
            with self.assertRaises(ValueError):
                ff.file_finding(root, "bug", "a defect",
                                {"severity": "High", "summary": "s", "steps": "x", "fix": "y"})


class FilerSurvivesUnreadableSiblingTests(unittest.TestCase):
    """M1 end-to-end (from review): filing a NEW, unrelated finding must not raise and must leave a
    consistent index even when a sibling artefact on disk is non-UTF-8 - the crash the earlier fix
    relocated into reconcile.file_census (past the write) rather than removing."""

    def test_file_finding_survives_a_non_utf8_sibling_and_leaves_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _seed_index(root, "bug")
            # a corrupted sibling from a crashed session
            (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_bytes(b"# BG0001: x\n\xff\xfe\n")
            # filing an unrelated new bug must complete, not raise
            res = ff.file_finding(root, "bug", "an unrelated new defect", dict(BUG))
            self.assertIn("id", res)
            self.assertTrue(Path(res["path"]).exists())
            # and the index must be consistent: the new id appears, no crash mid-recompute
            import reconcile
            drift = reconcile.detect_type("bug", root)
            new_id = res["file_id"]
            self.assertNotIn(new_id, [x.get("id") for x in drift.get("missing_rows", [])])


class FilingTimeDuplicateTests(unittest.TestCase):
    """CR0264: at filing, a finding overlapping an OPEN artefact (shared Affects + similar wording)
    is surfaced with the candidate named, before the id is minted - a warning, never a refusal."""

    def test_near_duplicate_is_warned_not_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            ff.file_finding(root, "bug", "check_links misses an anchor link defect",
                            {"severity": "high", "affects": "src/thing.py", "points": 3,
                             "steps": "r", "fix": "f",
                             "summary": "check_links does not catch a broken anchor link defect"})
            res = ff.file_finding(root, "bug", "anchor link defect not caught by check_links",
                                  {"severity": "high", "affects": "src/thing.py", "points": 3,
                                   "steps": "r", "fix": "f",
                                   "summary": "a broken anchor link defect is not caught by check_links"})
            self.assertIn("id", res)  # it still filed - a warning, never a refusal
            warns = res.get("duplicate_warnings", [])
            self.assertTrue(warns, "expected a duplicate warning")
            self.assertEqual(warns[0]["shared"], ["src/thing.py"])

    def test_distinct_finding_has_no_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            ff.file_finding(root, "bug", "colour the status output",
                            {"severity": "high", "affects": "src/thing.py", "points": 3,
                             "steps": "r", "fix": "f", "summary": "status should render green"})
            res = ff.file_finding(root, "bug", "parser drops a trailing field",
                                  {"severity": "high", "affects": "src/other.py", "points": 3,
                                   "steps": "r", "fix": "f", "summary": "the parser loses the last column"})
            self.assertNotIn("duplicate_warnings", res)  # different file, different words

    def test_no_affects_no_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            # a finding with no declared Affects has nothing structural to compare
            self.assertEqual(ff.duplicate_candidates(root, "some title", {"summary": "x"}), [])


def _rfc_body(root: Path, title: str, f: dict) -> str:
    _seed_index(root, "rfc")
    return Path(ff.file_finding(root, "rfc", title, f)["path"]).read_text(encoding="utf-8")


def _decision_rows(body: str) -> list[str]:
    """The `| D1 | ... | ... |` rows of the Open Decisions table."""
    rows, in_section = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            in_section = "decision" in line.lower()
            continue
        if in_section and re.match(r"^\s*\|\s*D\d+\s*\|", line):
            rows.append(line)
    return rows


class RfcDecisionRowsFromOptionsTests(unittest.TestCase):
    """US0245 AC1: the decision row states the choice the finding actually poses.

    `_render` already receives the finding's real options and renders them into Design
    Options, then hard-codes a decision row that ignores them. The data was always there.
    """

    def test_the_row_names_the_options_it_decides_between(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            body = _rfc_body(Path(d), "Which cache?", {
                "summary": "weigh it", "options": ["keep the in-process cache", "move to redis"]})
            rows = _decision_rows(body)
            self.assertEqual(len(rows), 1, rows)
            self.assertIn("keep the in-process cache", rows[0])
            self.assertIn("move to redis", rows[0])

    def test_three_options_all_appear_in_the_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            body = _rfc_body(Path(d), "Which store?", {
                "summary": "weigh it", "options": ["sqlite", "postgres", "flat files"]})
            row = _decision_rows(body)[0]
            for opt in ("sqlite", "postgres", "flat files"):
                self.assertIn(opt, row)

    def test_the_row_is_still_Open(self) -> None:
        """Deriving the wording must not accidentally pre-decide it."""
        with tempfile.TemporaryDirectory() as d:
            body = _rfc_body(Path(d), "Which cache?", {
                "summary": "weigh it", "options": ["a", "b"]})
            self.assertTrue(_decision_rows(body)[0].rstrip().endswith("| Open |"))


class RfcBoilerplateDecisionRowRetiredTests(unittest.TestCase):
    """US0245 AC2: the content-free row is never emitted, with or without options.

    RFC0010 condemned this row in June; the CRs cited as fixing it never touched the
    generator, so it kept manufacturing the rot that the accept gate then had to catch.
    """

    BOILERPLATE = "Act on this finding or keep status quo"

    def test_boilerplate_is_absent_when_options_are_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            body = _rfc_body(Path(d), "Which cache?", {
                "summary": "weigh it", "options": ["a", "b"]})
            self.assertNotIn(self.BOILERPLATE, body)

    def test_a_finding_with_no_options_names_its_own_subject(self) -> None:
        """Driven against the helper: `file_finding` refuses an RFC with no options at all
        (the hollow-artefact guard), so this branch is unreachable end to end. It still
        guards the fallback, and the fallback must pose the finding's own subject - the
        boilerplate existed precisely because a generic sentence was the easy default."""
        self.assertNotIn(self.BOILERPLATE, ff._decision_question("Retire the legacy importer", []))
        self.assertIn("retire the legacy importer",
                      ff._decision_question("Retire the legacy importer", []).lower())
        self.assertNotIn(self.BOILERPLATE, ff._decision_question("Retire it", None))

    def test_the_filer_still_refuses_an_rfc_with_no_options(self) -> None:
        """The guard the test above relies on. If this ever stops refusing, the fallback
        becomes reachable and the case above must go back to an end-to-end assertion."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "rfc")
            with self.assertRaises(ValueError) as cm:
                ff.file_finding(root, "rfc", "Retire the legacy importer", {"summary": "x"})
            self.assertIn("options", str(cm.exception))

    def test_a_single_option_is_not_a_choice_between_two(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            body = _rfc_body(Path(d), "Adopt the new parser", {
                "summary": "weigh it", "options": ["adopt the new parser"]})
            row = _decision_rows(body)[0]
            self.assertNotIn(self.BOILERPLATE, row)
            self.assertIn("adopt the new parser", row)


def _load_mutation():
    spec = importlib.util.spec_from_file_location(
        "mutation", Path(__file__).resolve().parent.parent / "mutation.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mutation"] = mod
    spec.loader.exec_module(mod)
    return mod


def _seed_run(root: Path, *, survived: int = 3, run_id: str | None = None) -> str:
    """One measured row in the mutation series, without running a mutation gate."""
    mut = _load_mutation()
    rid = run_id or mut._new_run_id()
    report = {"run_id": rid, "generated_at": "2026-07-22T09:00:00Z", "git_rev": "abc1234",
              "test_cmd": "python3 -m unittest discover", "targets": ["src/thing.py"],
              "refused": False, "unchecked": [],
              "summary": {"applied": 10, "killed": 7, "survived": survived,
                          "errors": 0, "unviable": 0, "truncated": 0}}
    mut.append_series(root, report, 612.5)
    return rid


class MutationRunAttributionTests(unittest.TestCase):
    """US0302 AC1: a finding filed from a surviving mutant names the run that found it, and a
    filing against a run nobody recorded is REFUSED rather than stamped as an unresolvable
    reference."""

    def test_a_finding_filed_from_a_survivor_records_the_run_and_the_target(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _seed_run(root)
            res = ff.file_finding(root, "bug", "a survivor nobody kills",
                                  {**BUG, "mutation_run": rid})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.extract_field(body, "Mutation-run"), rid)
            # the mutated surface travels with the link - derived from the run when unstated
            self.assertEqual(sdlc_md.extract_field(body, "Mutation-target"), "src/thing.py")

    def test_an_explicit_target_wins_over_the_derived_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _seed_run(root)
            res = ff.file_finding(root, "bug", "a survivor nobody kills",
                                  {**BUG, "mutation_run": rid,
                                   "mutation_target": "src/other.py"})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.extract_field(body, "Mutation-target"), "src/other.py")

    def test_filing_against_an_unknown_run_is_refused_naming_the_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            _seed_run(root)
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "bug", "a survivor nobody kills",
                                {**BUG, "mutation_run": "MRUN-nope-000000"})
            self.assertIn("MRUN-nope-000000", str(ctx.exception))
            # nothing was minted against the missing run
            self.assertEqual([p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                              if p.name != "_index.md"], [])

    def test_the_cli_exposes_the_link_and_refuses_an_unknown_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _seed_run(root)
            argv = ["file", "--type", "bug", "--title", "a survivor nobody kills",
                    "--severity", "High", "--summary", "s", "--steps", "x", "--fix", "y",
                    "--affects", "src/thing.py", "--points", "3", "--root", str(root)]
            with contextlib.redirect_stdout(io.StringIO()):
                rc = ff.main([*argv, "--mutation-run", rid])
            self.assertEqual(rc, 0)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = ff.main([*argv, "--mutation-run", "MRUN-ghost-000000"])
            self.assertEqual(rc, 1)
            self.assertIn("MRUN-ghost-000000", err.getvalue())


#: The payload CR0384 is about: reproduction steps whose content is COMMANDS. A backtick pair
#: and a `$(...)` are command substitution inside a double-quoted shell argument, so on the flag
#: path the shell ATE them - BG0240 lost two commands silently and BG0242 executed `git commit
#: -a` twice against the live repository while being filed. `{sentinel}` is substituted with a
#: path inside the test's own temp tree (never the working tree - L-0158), so an execution of
#: this text leaves a mark the test can see.
#:
#: Deliberately free of bare `snake_case` tokens and of any `**Field:**` line, so the filer's
#: markdown-safety pass is the identity here and "character for character" means exactly that.
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


def _git_repo(root: Path) -> None:
    """A throwaway git work tree with a commit, a staged change and an unstaged one, so the
    no-side-effect assertion has real state to be unchanged."""
    import gitutil
    gitutil.git(["init", "-q", "-b", "main"], root)
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    gitutil.git(["add", "seed.txt"], root)
    gitutil.git(["commit", "-qm", "seed"], root)
    (root / "staged.txt").write_text("staged\n", encoding="utf-8")
    gitutil.git(["add", "staged.txt"], root)
    (root / "seed.txt").write_text("seed edited\n", encoding="utf-8")


def _git_state(root: Path) -> tuple[str, bytes]:
    import gitutil
    head = gitutil.git(["rev-parse", "HEAD"], root).stdout.decode()
    return head, (root / ".git" / "index").read_bytes()


def _section(body: str, heading: str) -> str:
    """The text of one `## heading` section, verbatim."""
    m = re.search(rf"^## {re.escape(heading)}\n\n(.*?)(?=\n## )", body, re.S | re.M)
    assert m, f"no {heading} section in\n{body}"
    return m.group(1).rstrip("\n")


class JsonInputFidelityTests(unittest.TestCase):
    """US0305 AC1: a finding handed over as a JSON document is stored character for character -
    the whole point of an input path no shell ever sees."""

    def _fields_file(self, root: Path, payload: str) -> Path:
        p = root / "finding.json"
        p.write_text(json.dumps({
            "title": "filing executes the steps it is given",
            "severity": "High", "summary": "the filer runs its own reproduction",
            "steps": payload, "fix": "read the fields from a file", **GROOM,
        }), encoding="utf-8")
        return p

    def test_a_finding_supplied_as_json_is_stored_character_for_character(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            payload = STEPS_PAYLOAD.format(sentinel=root / "EXECUTED")
            spec = self._fields_file(root, payload)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = ff.main(["file", "--type", "bug", "--fields-file", str(spec),
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            filed = next(p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                         if p.name != "_index.md")
            body = filed.read_text(encoding="utf-8")
            self.assertEqual(_section(body, "Steps to Reproduce"), payload.rstrip("\n"))
            self.assertIn(payload, body)          # every character, in one contiguous run
            self.assertIn("`git commit -a`", body)
            self.assertIn("$(git rev-parse HEAD)", body)
            self.assertIn("backslash \\", body)

    def test_the_title_need_not_pass_through_a_shell_either(self) -> None:
        # `--title` is the other field a caller must supply, so it has to be suppliable from
        # the file - otherwise "no field passes through a shell" is false by construction.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            spec = root / "finding.json"
            spec.write_text(json.dumps({
                "title": "a title carrying `$(id)` verbatim", "severity": "High",
                "summary": "s", "steps": "x", "fix": "y", **GROOM}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = ff.main(["file", "--type", "bug", "--fields-file", str(spec),
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            filed = next(p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                         if p.name != "_index.md")
            self.assertIn("a title carrying `$(id)` verbatim",
                          filed.read_text(encoding="utf-8"))

    def test_a_flag_still_wins_over_the_file_so_the_two_paths_compose(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            spec = self._fields_file(root, "plain steps")
            with contextlib.redirect_stdout(io.StringIO()):
                ff.main(["file", "--type", "bug", "--fields-file", str(spec),
                         "--severity", "Low", "--root", str(root)])
            filed = next(p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                         if p.name != "_index.md")
            self.assertIn("> **Severity:** Low", filed.read_text(encoding="utf-8"))

    def test_an_unknown_key_in_the_document_is_refused_not_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            spec = root / "finding.json"
            spec.write_text(json.dumps({"title": "t", "severity": "High", "summary": "s",
                                        "steps": "x", "fix": "y", "stpes": "typo", **GROOM}),
                            encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = ff.main(["file", "--type", "bug", "--fields-file", str(spec),
                              "--root", str(root)])
            self.assertEqual(rc, 1)
            self.assertIn("stpes", err.getvalue())


class JsonInputNoSideEffectTests(unittest.TestCase):
    """US0305 AC2: filing that same content changes nothing. HEAD and the index are what they
    were, and no process was spawned to evaluate any field - BG0242's `git commit -a` ran twice
    against the live repository, and only a red pre-commit gate made the damage zero."""

    def test_filing_a_destructive_payload_leaves_head_and_the_index_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git_repo(root)
            _seed_index(root, "bug")
            sentinel = root / "EXECUTED"
            payload = STEPS_PAYLOAD.format(sentinel=sentinel)
            spec = root / "finding.json"
            spec.write_text(json.dumps({
                "title": "a bug about destructive commands", "severity": "High",
                "summary": "s", "steps": payload, "fix": "f", **GROOM}), encoding="utf-8")
            before = _git_state(root)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = ff.main(["file", "--type", "bug", "--fields-file", str(spec),
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(_git_state(root), before)   # HEAD and index byte-identical
            self.assertFalse(sentinel.exists())          # nothing evaluated the payload

    def test_no_spawned_process_carries_any_field_of_the_finding(self) -> None:
        import subprocess as sp
        seen: list[str] = []
        real_run, real_popen = sp.run, sp.Popen

        def _rec_run(cmd, *a, **kw):
            seen.append(repr(cmd))
            return real_run(cmd, *a, **kw)

        def _rec_popen(cmd, *a, **kw):
            seen.append(repr(cmd))
            return real_popen(cmd, *a, **kw)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            payload = STEPS_PAYLOAD.format(sentinel=root / "EXECUTED")
            spec = root / "finding.json"
            spec.write_text(json.dumps({
                "title": "a bug about destructive commands", "severity": "High",
                "summary": "s", "steps": payload, "fix": "f", **GROOM}), encoding="utf-8")
            with unittest.mock.patch.object(sp, "run", _rec_run), \
                    unittest.mock.patch.object(sp, "Popen", _rec_popen), \
                    contextlib.redirect_stdout(io.StringIO()):
                rc = ff.main(["file", "--type", "bug", "--fields-file", str(spec),
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            for marker in ("commit -a", "EXECUTED", "touch"):
                self.assertFalse([c for c in seen if marker in c],
                                 f"{marker!r} reached a spawned process: {seen}")


class ShellHazardReportTests(unittest.TestCase):
    """US0305 AC3: a field arriving on the FLAG path already mangled is reported at file time.
    BG0240 is the case this exists for: two reproduction commands were silently removed and the
    artefact read complete - the worse of the two outcomes, because nothing signalled it."""

    def _file(self, root: Path, steps: str) -> str:
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            ff.main(["file", "--type", "bug", "--title", "a defect", "--severity", "High",
                     "--summary", "s", "--steps", steps, "--fix", "y",
                     "--affects", "src/thing.py", "--points", "3", "--root", str(root)])
        return err.getvalue()

    def test_an_unbalanced_backtick_is_reported_naming_the_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            out = self._file(root, "run `git status and read it")
            self.assertIn("steps", out)
            self.assertIn("backtick", out.lower())
            self.assertIn("--fields-file", out)      # the fix is named, not just the fault

    def test_a_dollar_parenthesis_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self.assertIn("$(", self._file(root, "capture $(git rev-parse HEAD)"))

    def test_a_trailing_backslash_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self.assertIn("backslash", self._file(root, "continue the command \\").lower())

    def test_clean_prose_is_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self.assertEqual(self._file(root, "run the command and read the output"), "")

    def test_a_balanced_backtick_pair_is_not_a_hazard(self) -> None:
        # PARITY is the signal, not presence: a pair that survived the shell intact is a code
        # span, and reporting it would make the warning noise on every well-formed filing.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self.assertEqual(self._file(root, "run `git status` and read the output"), "")

    def test_two_pairs_are_still_not_a_hazard_but_three_backticks_are(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self.assertEqual(self._file(root, "run `a` then `b` and compare"), "")
            self.assertIn("backtick", self._file(root, "run `a` then `b and compare").lower())

    def test_the_report_is_a_report_not_a_refusal(self) -> None:
        # The finding is still filed: refusing would lose the content the author has in hand,
        # and the flag path survives for compatibility. What must not happen is silence.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            self._file(root, "run `git status and read it")
            self.assertTrue([p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                             if p.name != "_index.md"])

    def test_the_json_path_is_not_reported_because_nothing_mangled_it(self) -> None:
        # The hazard is what a SHELL did to the value. A `$(` that arrived intact through a
        # file is data, and warning about it would train the reader to ignore the warning.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            spec = root / "finding.json"
            spec.write_text(json.dumps({
                "title": "a defect", "severity": "High", "summary": "s",
                "steps": "capture $(git rev-parse HEAD) and a stray ` too",
                "fix": "y", **GROOM}), encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = ff.main(["file", "--type", "bug", "--fields-file", str(spec),
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(err.getvalue(), "")


class FieldsFileMetadataTests(unittest.TestCase):
    """US0418 / CR0417: a writer's --fields-file accepts the metadata fields its CLI accepts, not
    only its prose, so one document is the whole invocation - while the shell-hazard check still
    covers only the prose fields (the ones a shell can mangle)."""

    def _hazards_checked(self, flags: dict, allowed, metadata_keys):
        """Run resolve_prose_fields with report_shell_hazards captured, returning the keys it
        hazard-checked."""
        captured = {}
        real = ff.report_shell_hazards

        def spy(fields, keys=None, **kw):
            captured["keys"] = keys
            return real(fields, keys=keys, **kw)

        with unittest.mock.patch.object(ff, "report_shell_hazards", spy):
            ff.resolve_prose_fields(None, flags, allowed, metadata_keys=metadata_keys)
        return captured.get("keys")

    def test_metadata_accepted_and_only_prose_hazard_checked(self) -> None:
        """AC1. A fields-file supplying a prose field and a metadata field returns both, and the
        hazard check covers the prose keys - everything not declared metadata."""
        with tempfile.TemporaryDirectory() as d:
            spec = Path(d) / "f.json"
            spec.write_text(json.dumps({"body": "the lesson prose", "tags": "a,b"}),
                            encoding="utf-8")
            allowed = ("title", "body", "tags", "epic")
            metadata = ("tags", "epic")
            out = ff.resolve_prose_fields(str(spec), {}, allowed, metadata_keys=metadata)
            self.assertEqual(out["body"], "the lesson prose")
            self.assertEqual(out["tags"], "a,b")           # metadata accepted from the document
            # the hazard check runs over the prose keys (allowed minus metadata), not the metadata
            checked = self._hazards_checked({"body": "x", "tags": "y"}, allowed, metadata)
            self.assertEqual(tuple(checked), ("title", "body"))

    def test_an_unknown_key_is_still_refused(self) -> None:
        """AC2. A key outside the full field set is refused by name; widening to metadata does not
        become accept-anything."""
        with tempfile.TemporaryDirectory() as d:
            spec = Path(d) / "f.json"
            spec.write_text(json.dumps({"body": "x", "nonsense": "y"}), encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                ff.resolve_prose_fields(str(spec), {}, ("title", "body", "tags"),
                                        metadata_keys=("tags",))
            self.assertIn("nonsense", str(cm.exception))

    def test_prose_only_caller_unchanged(self) -> None:
        """AC3. A caller that passes no metadata_keys hazard-checks the whole allowed set, exactly
        as before - the back-compatible default preserves the narrower contract."""
        allowed = ("title", "body")
        checked = self._hazards_checked({"title": "x", "body": "y"}, allowed, None)
        self.assertEqual(tuple(checked), allowed)          # every allowed key checked when no metadata

    def test_a_forgotten_prose_field_stays_checked(self) -> None:
        """BG0298: the direction is fail-SAFE. A caller that declares only some metadata and
        FORGETS that `summary` is prose must still have `summary` hazard-checked - a field nobody
        classified defaults to checked, never to skipped."""
        allowed = ("title", "summary", "tags")
        # the caller declares tags as metadata but omits nothing about summary
        checked = self._hazards_checked({"title": "x", "summary": "y", "tags": "z"},
                                        allowed, ("tags",))
        self.assertIn("summary", checked)                  # NOT silently skipped
        self.assertIn("title", checked)
        self.assertNotIn("tags", checked)                  # the one declared metadata is skipped


class DuplicateScopeParityTests(unittest.TestCase):
    """BG0297: the two duplicate-detection entry points must agree on SCOPE, not just algorithm.
    Given a `type_`, the finding filer scopes to that one type - matching `artifact new <type>` -
    so a bug is compared to bugs, not to a similarly-titled CR."""

    EXISTING = ("The scrub-site sweep's worktrees exclusion matches any path component named "
                "worktrees, so it skips the ENTIRE tree when run from inside a worktree")
    REFILING = ("the site-sweep test is unrunnable inside a git worktree: an ancestor 'worktrees' "
                "path component makes SKIP_DIRS match every file, so sites={} and the pre-commit "
                "gate must be bypassed with --no-verify on parallel-worktree builds")

    def _artefact(self, root: Path, rel: str, cid: str, title: str, meta: str) -> None:
        d = root / "sdlc-studio" / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{cid}-x.md").write_text(f"# {cid}: {title}\n\n{meta}\n> **Affects:** src/thing.py\n",
                                       encoding="utf-8")

    def test_both_entry_points_agree_on_a_terminal_same_type_duplicate(self) -> None:
        import artifact
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            (root / "src").mkdir(exist_ok=True); (root / "src" / "thing.py").write_text("x\n")
            # a TERMINAL (Fixed) bug that the new title restates
            self._artefact(root, "bugs", "BG0269", self.EXISTING,
                           "> **Status:** Fixed\n> **Severity:** High\n> **Points:** 2")
            fields = {"affects": "src/thing.py"}
            via_finding = ff.duplicate_candidates(root, self.REFILING, fields, type_="bug")
            via_mint = artifact.duplicate_candidates(root, "bug", self.REFILING, fields)
            self.assertEqual([c["id"] for c in via_finding], [c["id"] for c in via_mint])
            self.assertIn("BG0269", [c["id"] for c in via_finding])   # terminal, still caught

    def test_the_filer_no_longer_warns_across_types(self) -> None:
        """The residual BG0297 closes: a bug filing scoped to bugs does NOT surface a
        similarly-titled CR - comparing a bug to a CR is the structural-pairing noise the
        within-type scope avoids, and the two entry points would otherwise disagree."""
        import artifact
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            (root / "src").mkdir(exist_ok=True); (root / "src" / "thing.py").write_text("x\n")
            # ONLY a CR carries the title; no bug does
            self._artefact(root, "change-requests", "CR0100", self.EXISTING,
                           "> **Status:** Complete\n> **Priority:** P1\n> **Type:** Feature\n"
                           "> **Size:** M")
            fields = {"affects": "src/thing.py"}
            # filing a BUG scopes to bugs -> the CR is not surfaced (matches artifact new bug)
            via_finding = ff.duplicate_candidates(root, self.REFILING, fields, type_="bug")
            via_mint = artifact.duplicate_candidates(root, "bug", self.REFILING, fields)
            self.assertEqual([c["id"] for c in via_finding], [c["id"] for c in via_mint])
            self.assertNotIn("CR0100", [c["id"] for c in via_finding])
            # the type-agnostic form (type_=None) still scans every type, so it DOES see the CR
            any_type = ff.duplicate_candidates(root, self.REFILING, fields)
            self.assertIn("CR0100", [c["id"] for c in any_type])


class FiledCriteriaTests(unittest.TestCase):
    """US0516/CR0458: a filed bug carried Steps to Reproduce and a Proposed Fix and NO acceptance
    criteria, so a lane picking it up had to infer the contract from a summary - and the
    engagement floor read the unit as unplanned. The criterion is DERIVED from the finding's own
    evidence, and where the evidence cannot support one that is STATED rather than scaffolded: a
    `{{placeholder}}` reads like content and a checkbox nobody derived buys a false pass at the
    floor."""

    EVIDENCED = {
        "severity": "High",
        "summary": "The close chain skips the velocity row when the retro id arrives dashed.",
        "steps": "Run `sprint close --retro RETRO-0049` against a tree holding RETRO0049-x.md.",
        "fix": "Normalise the retro id through sdlc_md.norm_id before globbing for the file.",
        "affects": "src/thing.py", "points": 3,
    }

    def test_a_filed_finding_carries_a_criterion(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a defect", dict(self.EVIDENCED))
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("## Acceptance Criteria", body)
            # the criterion is CHECKABLE, so the engagement floor and the lane both read it
            self.assertGreater(sdlc_md.count_acs(body), 0, body)
            # ... and DERIVED from this finding's own evidence, not boilerplate: the criteria
            # quote the steps and the fix the author actually wrote
            acs = "\n".join(ln for ln in body.splitlines() if ln.startswith("- [ ]"))
            self.assertIn("norm_id", acs)
            self.assertIn("RETRO-0049", acs)
            self.assertNotIn("{{", body)

    def test_thin_evidence_is_stated_not_scaffolded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            res = ff.file_finding(root, "bug", "a defect",
                                  {"severity": "High", "summary": "s", "steps": "r", "fix": "f",
                                   "affects": "src/thing.py", "points": 3})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("## Acceptance Criteria", body)
            # stated, in the artefact, naming the thin fields
            self.assertIn(ff.THIN_EVIDENCE_MARK, body)
            self.assertIn("steps", body)
            # ... and NOT a scaffold: no placeholder, and no checkbox nobody derived - a
            # checkbox here would satisfy the engagement floor on a finding that planned nothing
            self.assertNotIn("{{", body)
            self.assertEqual(sdlc_md.count_acs(body), 0, body)

    def test_an_authored_criterion_is_never_overwritten(self) -> None:
        # A CR arrives with its own acceptance criteria; the derivation must not displace them.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            res = ff.file_finding(root, "cr", "t",
                                  {"priority": "Low", "ctype": "Improvement", "summary": "s",
                                   "acs": ["the operator's own criterion"], "impact": "i",
                                   "size": "M", "affects": "src/x.py"})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("- [ ] the operator's own criterion", body)
            self.assertEqual(sdlc_md.count_acs(body), 1, body)


class AffectsFootprintTests(unittest.TestCase):
    """US0517/CR0458: `Affects` is where the FIX LANDS. Filers kept writing the file the evidence
    was READ in, which is a different file - so the plan's collision analysis grouped the unit by
    the wrong surface and the footprint was understated by the test file besides. The evidence
    location is now recorded AS evidence, and an existing companion test is put in the footprint
    rather than merely mentioned in a warning nobody acts on."""

    def _tree(self, root: Path) -> None:
        _seed_index(root, "bug")
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "thing.py").write_text("x\n", encoding="utf-8")
        (root / "scripts" / "tests").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "tests" / "test_thing.py").write_text("x\n", encoding="utf-8")
        ev = root / "sdlc-studio" / "reviews"
        ev.mkdir(parents=True, exist_ok=True)
        (ev / "RV0021-round-two.md").write_text("x\n", encoding="utf-8")

    def _affects_line(self, body: str) -> str:
        return next(ln for ln in body.splitlines() if ln.startswith("> **Affects:**"))

    def test_affects_names_the_fix_site(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                res = ff.file_finding(root, "bug", "a defect",
                                      {"severity": "High", "summary": "s", "steps": "r",
                                       "fix": "f", "points": 3,
                                       "affects": "scripts/thing.py",
                                       "evidence": "sdlc-studio/reviews/RV0021-round-two.md:88"})
            body = Path(res["path"]).read_text(encoding="utf-8")
            line = self._affects_line(body)
            # the footprint is the FIX site, as the planner's own parser reads it
            self.assertIn("scripts/thing.py", sdlc_md.affects_files(line))
            # ... and the evidence site is NOT in it
            self.assertNotIn("RV0021", line)
            self.assertTrue(all("RV0021" not in p for p in sdlc_md.affects_files(line)), line)
            # ... it is recorded as evidence instead, so the trace is kept, not discarded
            self.assertIn("> **Evidence:** sdlc-studio/reviews/RV0021-round-two.md:88", body)

    def test_the_companion_test_is_included(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                res = ff.file_finding(root, "bug", "a defect",
                                      {"severity": "High", "summary": "s", "steps": "r",
                                       "fix": "f", "points": 3, "affects": "scripts/thing.py"})
            body = Path(res["path"]).read_text(encoding="utf-8")
            declared = sdlc_md.affects_files(self._affects_line(body))
            self.assertIn("scripts/thing.py", declared)
            self.assertIn("scripts/tests/test_thing.py", declared)
            self.assertIn("scripts/tests/test_thing.py", err.getvalue())  # and said so

    def test_a_test_with_no_source_partner_is_left_alone(self) -> None:
        # Nothing is invented: with no companion on disk the footprint is written as declared.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            (root / "scripts").mkdir(parents=True, exist_ok=True)
            (root / "scripts" / "lonely.py").write_text("x\n", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                res = ff.file_finding(root, "bug", "a defect",
                                      {"severity": "High", "summary": "s", "steps": "r",
                                       "fix": "f", "points": 3, "affects": "scripts/lonely.py"})
            declared = sdlc_md.affects_files(
                self._affects_line(Path(res["path"]).read_text(encoding="utf-8")))
            self.assertEqual(declared, ["scripts/lonely.py"])

    def test_the_cli_takes_the_evidence_flag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc = ff.main(["file", "--type", "bug", "--title", "a defect",
                              "--severity", "High", "--summary", "s", "--steps", "r", "--fix", "f",
                              "--affects", "scripts/thing.py", "--points", "3",
                              "--evidence", "sdlc-studio/reviews/RV0021-round-two.md:88",
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            filed = [p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                     if p.name != "_index.md"]
            self.assertIn("> **Evidence:** sdlc-studio/reviews/RV0021-round-two.md:88",
                          filed[0].read_text(encoding="utf-8"))


class CompanionTestFootprintTests(unittest.TestCase):
    """BG0343: a declared `Affects` that names a source file and NOT its existing companion test
    is an understated footprint. Nothing refused it, so the plan's collision analysis, the
    engagement floor and gate's changed-surface pass all read a unit smaller than it is - silently,
    because the filing exits 0. The filer names the missing path at the moment it can."""

    def _tree(self, root: Path, *, with_test: bool = True) -> None:
        _seed_index(root, "bug")
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "thing.py").write_text("x\n", encoding="utf-8")
        if with_test:
            (root / "scripts" / "tests").mkdir(parents=True, exist_ok=True)
            (root / "scripts" / "tests" / "test_thing.py").write_text("x\n", encoding="utf-8")

    def test_missing_companion_test_is_named_by_the_predicate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            self.assertEqual(ff.missing_companion_tests(root, "scripts/thing.py", "bug"),
                             [("scripts/thing.py", "scripts/tests/test_thing.py")])

    def test_a_declared_test_file_satisfies_the_check(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            self.assertEqual(
                ff.missing_companion_tests(
                    root, "scripts/thing.py, scripts/tests/test_thing.py", "bug"), [])

    def test_no_companion_on_disk_means_no_invented_path(self) -> None:
        # The tool never sends an author to a file it made up: with no test beside the source
        # there is nothing to name, so it says nothing.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root, with_test=False)
            self.assertEqual(ff.missing_companion_tests(root, "scripts/thing.py", "bug"), [])

    def test_a_package_sibling_suite_is_found(self) -> None:
        # `scripts/lib/sdlc_md.py` is tested by `scripts/tests/test_sdlc_md.py` - one directory UP,
        # which is exactly the shape the audit's 16 bugs all under-declared.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            (root / "scripts" / "lib").mkdir(parents=True, exist_ok=True)
            (root / "scripts" / "lib" / "parser.py").write_text("x\n", encoding="utf-8")
            (root / "scripts" / "tests").mkdir(parents=True, exist_ok=True)
            (root / "scripts" / "tests" / "test_parser.py").write_text("x\n", encoding="utf-8")
            self.assertEqual(ff.missing_companion_tests(root, "scripts/lib/parser.py", "bug"),
                             [("scripts/lib/parser.py", "scripts/tests/test_parser.py")])

    def test_a_root_level_source_has_no_parent_sibling_suite(self) -> None:
        # The `..` candidate must never escape the repo root into a path nobody can resolve.
        self.assertTrue(all(not c.startswith("..")
                            for c in ff.companion_test_candidates("thing.py")))

    def test_a_dot_directory_path_compares_intact(self) -> None:
        # This repo's own sources live under `.claude/`. A normalisation that stripped the leading
        # dot would compare two mangled spellings and warn about a test that IS declared.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            src = root / ".claude" / "scripts"
            src.mkdir(parents=True, exist_ok=True)
            (src / "thing.py").write_text("x\n", encoding="utf-8")
            (src / "tests").mkdir(exist_ok=True)
            (src / "tests" / "test_thing.py").write_text("x\n", encoding="utf-8")
            self.assertEqual(
                ff.missing_companion_tests(
                    root, ".claude/scripts/thing.py, .claude/scripts/tests/test_thing.py", "bug"),
                [])
            self.assertEqual(
                ff.missing_companion_tests(root, ".claude/scripts/thing.py", "bug"),
                [(".claude/scripts/thing.py", ".claude/scripts/tests/test_thing.py")])

    def test_an_rfc_footprint_is_not_checked(self) -> None:
        # An RFC's declared files are the OUTPUT of its decision, exactly as the resolvable
        # check skips it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            self.assertEqual(ff.missing_companion_tests(root, "scripts/thing.py", "rfc"), [])

    def test_the_cli_reports_the_missing_test_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = ff.main(["file", "--type", "bug", "--title", "a defect", "--severity", "High",
                              "--summary", "s", "--steps", "r", "--fix", "f",
                              "--affects", "scripts/thing.py", "--points", "3",
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("scripts/tests/test_thing.py", err.getvalue())
            self.assertIn("Affects", err.getvalue())

    def test_it_is_a_warning_not_a_refusal(self) -> None:
        # Losing the finding would be worse than under-declaring it: the artefact is still written.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                ff.main(["file", "--type", "bug", "--title", "a defect", "--severity", "High",
                         "--summary", "s", "--steps", "r", "--fix", "f",
                         "--affects", "scripts/thing.py", "--points", "3", "--root", str(root)])
            self.assertTrue([p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                             if p.name != "_index.md"])

    def test_a_complete_footprint_files_silently(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                ff.main(["file", "--type", "bug", "--title", "a defect", "--severity", "High",
                         "--summary", "s", "--steps", "r", "--fix", "f",
                         "--affects", "scripts/thing.py, scripts/tests/test_thing.py",
                         "--points", "3", "--root", str(root)])
            self.assertEqual(err.getvalue(), "")


class StripCodeBlocksFenceTests(unittest.TestCase):
    """BG0349: the shell-hazard scrubber drops fenced illustration by the ONE shared CommonMark
    tracker. A naive toggle released a four-backtick block on its inner three-backtick fence, so
    the quoted command below it was scanned as a stored value and reported as a hazard."""

    TICK = "`"

    def test_inner_fence_inside_a_longer_block_is_not_a_closer(self) -> None:
        value = (self.TICK * 4 + "markdown\n"
                 + self.TICK * 3 + "\n"
                 "rm -rf build\n"
                 + self.TICK * 3 + "\n"
                 + self.TICK * 4 + "\n")
        self.assertEqual(ff._strip_code_blocks(value).strip(), "")

    def test_a_fence_carrying_an_info_string_never_closes(self) -> None:
        value = (self.TICK * 3 + "markdown\n"
                 + self.TICK * 3 + "text\n"
                 "rm -rf build\n"
                 + self.TICK * 3 + "\n")
        self.assertEqual(ff._strip_code_blocks(value).strip(), "")

    def test_prose_after_the_matching_closer_survives(self) -> None:
        value = (self.TICK * 4 + "\n" + self.TICK * 3 + "\nfenced\n"
                 + self.TICK * 3 + "\n" + self.TICK * 4 + "\nreal prose\n")
        self.assertEqual(ff._strip_code_blocks(value).strip(), "real prose")


class AuthoredCriteriaSurviveTests(unittest.TestCase):
    """`derived_criteria` returns nothing when the author supplied their own, on the stated rule
    that an authored criterion is never displaced by a derived one. Nothing then RENDERED them,
    so the block fell through to the stated absence - and the finding asserted that nothing said
    what fixed would look like, over four criteria that did."""

    AUTHORED = ["THE FIRST AUTHORED CRITERION", "THE SECOND AUTHORED CRITERION"]

    def _fields(self, **over):
        f = {"severity": "Low", "priority": "Low", "points": 2, "affects": "src/thing.py",
             "summary": "a summary with plenty of substantive words in it",
             "steps": "run the command and read the output it prints",
             "fix": "change the renderer so the authored criteria are written"}
        f.update(over)
        return f

    def test_authored_criteria_are_rendered_not_replaced_by_a_stated_absence(self) -> None:
        block = ff.criteria_block("bug", self._fields(acs=list(self.AUTHORED)))
        for a in self.AUTHORED:
            self.assertIn(a, block)
        self.assertNotIn(ff.THIN_EVIDENCE_MARK, block)

    def test_they_are_counted_as_criteria_by_the_floor_that_reads_them(self) -> None:
        """The engagement floor counts with `count_acs`. Rendering the words somewhere in the
        document is not enough - they have to count, or the floor reads a finding that planned
        nothing and agrees with it."""
        block = ff.criteria_block("bug", self._fields(acs=list(self.AUTHORED)))
        self.assertEqual(sdlc_md.count_acs(f"## Acceptance Criteria\n\n{block}\n"),
                         len(self.AUTHORED))

    def test_a_finding_with_no_authored_criteria_still_derives_or_states_the_absence(self) -> None:
        """The carve-out must not widen: with nothing authored, the derived path and the stated
        absence both still work, so this is a precedence change and not an exemption."""
        derived = ff.criteria_block("bug", self._fields())
        self.assertNotIn(ff.THIN_EVIDENCE_MARK, derived)
        self.assertTrue(derived.strip().startswith("- [ ]"))
        thin = ff.criteria_block("bug", self._fields(summary="x", steps="y", fix="z"))
        self.assertIn(ff.THIN_EVIDENCE_MARK, thin)

    def test_an_authored_criterion_already_carrying_a_checkbox_is_not_doubled(self) -> None:
        # The PROPERTY is that a supplied checkbox is not doubled - asserted on the shape rather
        # than on a literal, because BG0530 added the `ACn` marker the parser requires and a
        # string match would have read that as a regression when the property was untouched.
        block = ff.criteria_block("bug", self._fields(acs=["- [ ] ALREADY BOXED"]))
        self.assertIn("ALREADY BOXED", block)
        self.assertNotIn("- [ ] - [ ]", block)
        self.assertEqual(block.count("- [ ]"), 1, f"the checkbox was doubled: {block!r}")


class NoSuppliedFieldIsDiscardedTests(unittest.TestCase):
    """BG0399. The CR renderer emitted Summary, Impact and Acceptance Criteria and nothing
    else, so a `steps` or `fix` supplied at filing reached no section and was discarded without
    a word. `artifact.py` was repaired for this class; this filer was not - and the field it
    ate was the Proposed Fix of a change request about wasted time.

    A field accepted at the CLI and dropped by the renderer is content the author believes they
    filed, which is the one failure a filer must not have."""

    #: Every field any renderer REQUIRES, so a type is never skipped for want of a key - the
    #: field under test is overridden with its own marker.
    BASE = {"summary": "S", "impact": "I", "acs": ["a criterion"], "steps": "generic steps",
            "fix": "generic fix", "priority": "High", "ctype": "enhancement",
            "severity": "High", "points": 3}

    def _body(self, type_: str, **extra) -> str:
        return ff._render(type_, f"{type_.upper()}-9999", "a title", "2026-07-29",
                          {**self.BASE, **extra})

    def test_a_crs_steps_and_fix_reach_the_document(self) -> None:
        body = self._body("cr", steps="REPRODUCE LIKE THIS", fix="REMEDY LIKE THIS")
        self.assertIn("REPRODUCE LIKE THIS", body)
        self.assertIn("REMEDY LIKE THIS", body)
        self.assertIn("## Steps to Reproduce", body)
        self.assertIn("## Proposed Fix", body)

    def test_a_landed_section_precedes_the_revision_history(self) -> None:
        """Appended content must keep the document's shape, or every consumer that reads to
        the history gets a surprise."""
        body = self._body("cr", fix="REMEDY LIKE THIS")
        self.assertLess(body.index("## Proposed Fix"), body.index("## Revision History"))

    def test_a_field_the_type_already_homes_is_not_duplicated(self) -> None:
        body = self._body("bug", steps="REPRODUCE LIKE THIS", fix="REMEDY LIKE THIS")
        self.assertEqual(1, body.count("## Steps to Reproduce"))
        self.assertEqual(1, body.count("## Proposed Fix"))

    def test_an_rfcs_impact_reaches_the_document(self) -> None:
        """The third renderer, checked by the same rule rather than by remembering it exists -
        the omission this bug is about was one renderer nobody re-read."""
        body = ff._render("rfc", "RFC-9999", "a title", "2026-07-29",
                          {**self.BASE, "options": ["A", "B"], "impact": "THE IMPACT"})
        self.assertIn("THE IMPACT", body)

    def test_every_landable_field_reaches_every_type(self) -> None:
        """DERIVED over the types and the fields, so a renderer added later is covered without
        anyone remembering to add a case."""
        for type_ in ("bug", "cr", "rfc"):
            for key, heading in ff._LANDABLE:
                with self.subTest(type=type_, field=key):
                    marker = f"UNIQUE-{key.upper()}-MARKER"
                    body = ff._render(type_, f"{type_.upper()}-9999", "a title", "2026-07-29",
                                      {**self.BASE, "options": ["A", "B"], key: marker})
                    self.assertIn(marker, body, f"{type_} discards {key}")
                    self.assertIn(f"## {heading}", body)

    def test_an_unsupplied_field_adds_no_empty_section(self) -> None:
        body = ff._render("cr", "CR-9999", "a title", "2026-07-29",
                          {k: v for k, v in self.BASE.items() if k not in ("steps", "fix")})
        self.assertNotIn("## Steps to Reproduce", body)
        self.assertNotIn("## Proposed Fix", body)


class LandedProseCannotForgeADeclarationTests(unittest.TestCase):
    """The landing path skipped the escaping every renderer beside it applies.

    Both halves below shipped as repairs with NO test - `test_file_finding.py` was not in the
    commit at all - so each reverted cleanly under the full suite. The fixes were right and held
    by nothing, which is the same as not having them once someone refactors."""

    BASE = {"summary": "S", "impact": "I", "acs": ["a criterion"], "priority": "High",
            "ctype": "enhancement", "severity": "High", "points": 3}

    def test_a_metadata_shaped_line_in_landed_prose_does_not_parse_as_a_declaration(self) -> None:
        """A CR's `steps` has no home in the CR renderer, so it LANDS - and landed raw, a line
        shaped like `> **Points:** 99` was read back by `extract_field` as a real declaration
        the head never made. Forgery through the one path that skipped `_prose_safe`."""
        body = ff._render("cr", "CR-9999", "a title", "2026-07-29",
                          {**self.BASE, "steps": "first do this\n> **Points:** 99\nthen that"})
        self.assertIn("first do this", body, "the author's words were dropped, not escaped")
        self.assertIn("then that", body)
        self.assertIsNone(sdlc_md.extract_field(body, "Points"),
                          "landed prose forged a Points declaration the filer never made")

    def test_a_heading_merely_mentioned_in_prose_does_not_suppress_the_section(self) -> None:
        """The already-homed test read the WHOLE body, so a finding whose prose discussed
        `## Impact` was refused as already-homed - with a false message and no remedy. A project
        that files bugs about its own renderers writes that prose constantly."""
        marker = "THE IMPACT ITSELF"
        body = ff._render("bug", "BG-9999", "a title", "2026-07-29",
                          {**self.BASE, "steps": "s", "fix": "f",
                           "summary": "the renderer emits `## Impact` in the wrong place",
                           "impact": marker})
        self.assertIn(marker, body, "a heading named in prose swallowed the real section")
        self.assertIn("## Impact", body)


class TheFilerCannotMintAFenceItsOwnGateRefusesTests(unittest.TestCase):
    """BG0412. `file_finding` wrote an author's fenced block through verbatim, so a finding
    whose evidence quotes a command block arrived with a bare ``` opener - which markdownlint
    MD040 refuses. The deterministic filer produced artefacts the deterministic gate rejected,
    and the only way past was to hand-edit the file the filer exists to stop you hand-writing.
    Two of this run's own findings hit it."""

    BASE = {"summary": "s", "severity": "Medium", "points": 2, "affects": "a.py",
            "evidence": "e", "acs": ["one"], "steps": "s", "fix": "f"}

    def _fenced(self, block: str) -> str:
        return ff._render("bug", "BG-9999", "a title", "2026-07-29",
                          {**self.BASE, "summary": f"before\n\n{block}\n\nafter"})

    def test_an_unlabelled_opening_fence_is_given_a_language(self) -> None:
        body = self._fenced("```\ngit status\n```")
        self.assertIn("```text\ngit status\n```", body,
                      "the bare opener survived: MD040 refuses this artefact")

    def test_the_closing_fence_is_never_given_a_language(self) -> None:
        """A language on a closer is not a closer (CommonMark 4.5), so a naive
        'label every fence line' fix releases the block early and turns the illustration
        beneath it into live document content."""
        body = self._fenced("```\ngit status\n```")
        self.assertNotIn("```text\ngit status\n```text", body)
        opener, closer = [i for i, ln in enumerate(body.splitlines())
                          if ln.strip().startswith("```")][:2]
        lines = body.splitlines()
        self.assertEqual(lines[closer].strip(), "```", "the closer was labelled")
        self.assertEqual(lines[opener].strip(), "```text")

    def test_a_fence_that_already_declares_a_language_is_untouched(self) -> None:
        body = self._fenced("```python\nx = 1\n```")
        self.assertIn("```python\nx = 1\n```", body)
        self.assertNotIn("```text", body)

    def test_the_authors_content_is_preserved_verbatim(self) -> None:
        """Only the missing language is supplied - nothing inside the block is rewritten,
        including lines that would otherwise be normalised as prose."""
        body = self._fenced("```\nsome_snake_case and > **Points:** 99\n```")
        self.assertIn("some_snake_case and > **Points:** 99", body,
                      "content inside a fence was rewritten by a prose normaliser")

    def test_a_longer_opening_run_keeps_its_own_length(self) -> None:
        """A ````markdown wrapper's inner ``` is CONTENT, not a second opener - labelling it
        would corrupt an illustration of markdown itself, which this repo files constantly."""
        body = self._fenced("````markdown\n```\ninner\n```\n````")
        self.assertIn("````markdown\n```\ninner\n```\n````", body,
                      "the inner fence of a longer-run block was treated as an opener")

    def test_labelling_keeps_the_openers_own_run_length(self) -> None:
        """A four-backtick block wrapping a three-backtick illustration, UNLABELLED. Rewriting
        the opener to a fixed ``` makes the inner fence close the outer block, so the rest of
        the illustration escapes into the document. Caught by mutation: the sibling test used a
        ````markdown opener, which already carries an info string and is never labelled, so
        nothing covered the run length of a fence this function actually rewrites."""
        body = self._fenced("````\n```\ninner\n```\n````")
        self.assertIn("````text\n```\ninner\n```\n````", body)
        opener = next(ln for ln in body.splitlines() if ln.strip().endswith("text"))
        self.assertEqual(opener.strip(), "````text",
                         "the outer fence was rewritten at a different run length")

    def test_a_tilde_fence_is_labelled_too(self) -> None:
        body = self._fenced("~~~\nplain\n~~~")
        self.assertIn("~~~text\nplain\n~~~", body)

    def test_a_fence_inside_an_indented_code_block_is_content(self) -> None:
        """The correctness defect an independent reviewer found. `fence_step` has no notion of
        a four-space indented code block, so a literal ``` inside one was taken for a real
        fence. That desynchronised the state machine TWICE over: the author's content was
        rewritten, and the genuine bare opener further down was consumed as that block's closer
        and left bare - so the function corrupted the document AND still failed MD040 on the
        input that motivated it."""
        block = ("    ```\n    literal opener only\n\nreal block:\n\n"
                 "```\nlive content\n```")
        body = self._fenced(block)
        self.assertIn("    ```\n    literal opener only", body,
                      "content inside an indented code block was rewritten")
        self.assertIn("```text\nlive content\n```", body,
                      "the real bare opener was consumed as the indented block's closer")

    def test_line_endings_are_preserved(self) -> None:
        """A CRLF document came back with a single LF spliced into the opener line."""
        out = sdlc_md.normalise_fence_languages("intro\r\n```\r\nx\r\n```\r\n")
        self.assertEqual(out, "intro\r\n```text\r\nx\r\n```\r\n")

    def test_an_indented_fence_keeps_its_indent(self) -> None:
        """A surviving mutant: dropping the indent when labelling would de-indent a fence
        inside a list item and break the list. Nothing covered it."""
        out = sdlc_md.normalise_fence_languages("- item\n\n  ```\n  x\n  ```\n")
        self.assertEqual(out, "- item\n\n  ```text\n  x\n  ```\n")

    def test_a_filed_artefact_passes_the_real_markdown_lane(self) -> None:
        """The lane-level assertion, not the unit one. A unit test can only assert the shape
        this fix chose; markdownlint is the thing that actually refused two of this run's
        findings, so the guard has to be the tool itself or a new rule can silently reopen it."""
        import shutil
        import subprocess
        mdl = shutil.which("markdownlint") or str(
            Path(__file__).resolve().parents[5] / "node_modules/.bin/markdownlint")
        if not Path(mdl).exists():
            self.skipTest("markdownlint not installed - CI enforces this lane")
        body = self._fenced("```\ngit status\n```")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "BG-9999-a-title.md"
            p.write_text(body, encoding="utf-8")
            r = subprocess.run([mdl, "--disable", "MD013", "MD041", "--", str(p)],
                               capture_output=True, text=True, check=False)
        self.assertNotIn("MD040", r.stdout + r.stderr,
                         f"the filer minted an artefact its own gate refuses:\n{r.stdout}{r.stderr}")

    def test_an_unclosed_fence_is_left_alone(self) -> None:
        """An opener with no closer is malformed markdown either way; supplying a language
        would make a broken block look deliberate rather than leave it visibly broken."""
        body = self._fenced("```\nnever closed")
        self.assertIn("```\nnever closed", body)
        self.assertNotIn("```text", body)


class AFindingIsPricedWhereTheWorkWasTests(unittest.TestCase):
    """US0561 (CR0500). A finding raised while a delivery batch is open is that batch's work.
    Without the stamp, every finding reads as close overhead whenever it was actually raised,
    and the claim 'defects are found inside the sprint' cannot be checked at all."""

    FIELDS = {"title": "a defect", "summary": "s", "severity": "Medium", "points": 2,
              "affects": "a.py", "evidence": "e", "acs": ["one"], "steps": "s", "fix": "f"}

    def _repo(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        (root / "a.py").write_text("x = 1\n", encoding="utf-8")   # the declared Affects resolves
        return root

    def _file(self, root):
        with contextlib.redirect_stdout(io.StringIO()):
            f = dict(self.FIELDS)
            res = ff.file_finding(root, "bug", f.pop("title"), f)
        return Path(res["path"]).read_text(encoding="utf-8")

    def test_a_finding_records_the_open_batch(self) -> None:
        from lib import run_state
        root = self._repo()
        run_state.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        run_state.start_batch(root, ["US0001"])
        text = self._file(root)
        stamped = sdlc_md.extract_field(text, "Raised-in-batch") or ""
        self.assertTrue(stamped and "none open" not in stamped,
                        f"the finding was not attributed to the open batch: {stamped!r}")
        self.assertIn("BG0001", run_state.open_batch(root)["findings_raised"],
                      "the batch span does not carry the finding raised against it")

    def test_the_filer_attributes_through_the_real_path(self) -> None:
        """M11 from the guard review: making `_attribute_to_open_batch` always return None
        SURVIVED, because no test covered attribution THROUGH the filer - only the run_state
        helper underneath it. This asserts the span itself gained the id."""
        from lib import run_state
        root = self._repo()
        run_state.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        run_state.start_batch(root, ["US0001"])
        self._file(root)
        self.assertIn("BG0001", run_state.open_batch(root)["findings_raised"],
                      "the filer did not record the finding against the open batch")

    def test_filing_is_not_ten_seconds_slower_for_the_attribution(self) -> None:
        """The attribution took the SAME advisory lock the filer already holds. flock is
        per open-file-description, so the process contended with itself for the whole 10s
        timeout on every filing - and `allocation_lock` then proceeds UNSERIALISED, losing
        the very serialisation it exists for. Measured, because a comment cannot fail."""
        import time
        from lib import run_state
        root = self._repo()
        run_state.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        run_state.start_batch(root, ["US0001"])
        start = time.monotonic()
        self._file(root)
        elapsed = time.monotonic() - start
        self.assertLess(elapsed, 3.0,
                        f"filing took {elapsed:.1f}s - the attribution is re-entering the "
                        f"allocation lock the filer already holds")

    def test_filing_never_fabricates_a_run_state(self) -> None:
        """`_mutate` persists whatever its callback returns, so seeding a blank record minted
        a run state on the first filing in a project that had never opened one - breaking
        `read`'s "never fabricated" invariant and letting `sprint close` proceed against a
        phantom running run with a null id."""
        root = self._repo()
        state = root / "sdlc-studio" / ".local" / "run-state.json"
        self.assertFalse(state.exists())
        self._file(root)
        self.assertFalse(state.exists(),
                         "filing a finding minted a run state in a project with no run")

    def test_no_open_batch_is_stated_not_guessed(self) -> None:
        """An absence stated is evidence; an absence omitted is indistinguishable from an
        attribution nobody made. Attributing to the last CLOSED span would price a close-time
        finding as batch work and invert the very measurement this exists to take."""
        from lib import run_state
        root = self._repo()
        run_state.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        run_state.start_batch(root, ["US0001"])
        run_state.close_batch(root, reviewer="reviewer-a", author="author-b", verdict="APPROVE")
        text = self._file(root)
        stamped = sdlc_md.extract_field(text, "Raised-in-batch") or ""
        self.assertIn("none open", stamped,
                      f"a finding raised outside any batch was attributed to one: {stamped!r}")


def _load_audit_cost():
    spec = importlib.util.spec_from_file_location(
        "audit_cost", Path(__file__).resolve().parent.parent / "audit_cost.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_cost"] = mod
    spec.loader.exec_module(mod)
    return mod


def _register(root: Path, run_id: str = "RUN-AUDIT-01") -> str:
    """One row in the audit-run REGISTER, which is the git-tracked audit-cost ledger."""
    ac = _load_audit_cost()
    ac.record(root, {"run_id": run_id, "lenses": 5, "rounds": 3, "votes": 3,
                     "estimated_agents": 50, "estimated_tokens": 1_000_000,
                     "actual_agents": 55, "actual_tokens": 1_200_000})
    return run_id


#: A lens that really exists in a shipped pack, and the pack that owns it.
LIVE_LENS = "accepted-without-running"
LIVE_PROFILE = "process"


def _bugs(root: Path) -> list:
    return [p for p in (root / "sdlc-studio" / "bugs").glob("*.md") if p.name != "_index.md"]


class AuditAttributionTests(unittest.TestCase):
    """US0462: a finding records the lens, the profile and a resolvable audit run."""

    def test_lens_profile_and_run_are_stamped_as_metadata(self) -> None:
        """AC1. Read as FIELDS, because 108 findings already hide their run id in `Raised-by`
        prose and counting a class from that needs a regex over free text."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _register(root)
            res = ff.file_finding(root, "bug", "a finding with an attribution",
                                  {**BUG, "lens": LIVE_LENS, "audit_run": rid})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertEqual(LIVE_LENS, sdlc_md.extract_field(body, "Audit-lens"))
            self.assertEqual(rid, sdlc_md.extract_field(body, "Audit-run"))
            # DERIVED, not supplied: the lens resolves to exactly one pack.
            self.assertEqual(LIVE_PROFILE, sdlc_md.extract_field(body, "Audit-profile"))

    def test_an_undeclared_lens_or_profile_is_refused_before_an_id_is_minted(self) -> None:
        """AC2, and the mutant that matters is PLACEMENT, not refusal.

        MUTANT: move `check_audit_attribution` from beside `check_mutation_run` to inside
        `_file_finding_locked` after the mint. The refusal still fires with an identical message
        and exit code, and an id is burned - so the AC asserts the id sequence did NOT advance,
        which a refusal-only assertion cannot see.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _register(root)
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "bug", "x",
                                {**BUG, "lens": "no-such-lens-anywhere", "audit_run": rid})
            self.assertIn("no-such-lens-anywhere", str(ctx.exception))
            self.assertEqual([], _bugs(root), "an id was minted for a refused attribution")

            # A profile that exists but does not own the lens: a consistent-looking pair naming
            # the wrong pack, which a per-field existence check cannot catch.
            with self.assertRaises(ValueError) as ctx2:
                ff.file_finding(root, "bug", "x", {**BUG, "lens": LIVE_LENS,
                                                   "profile": "code", "audit_run": rid})
            self.assertIn("belongs to", str(ctx2.exception))
            self.assertEqual([], _bugs(root))

    def test_a_lens_without_a_run_or_a_run_without_a_lens_is_refused(self) -> None:
        """AC4, all-or-none. THREE fixtures, because the obvious wrong implementation
        (`if lens and not run and not profile`) passes with only the first two.

        MUTANT: refuse when ANY of the three is absent - the wrong reading. It dies to the
        none-of-the-three control below, which is the regression guard over 923 existing findings.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _register(root)
            for label, fields in (
                    ("lens with no run", {"lens": LIVE_LENS}),
                    ("run with no lens", {"audit_run": rid}),
                    ("lens+profile, no run", {"lens": LIVE_LENS, "profile": LIVE_PROFILE})):
                with self.subTest(label=label):
                    with self.assertRaises(ValueError):
                        ff.file_finding(root, "bug", "x", {**BUG, **fields})
                    self.assertEqual([], _bugs(root))

            # THE CONTROL: none of the three must stay legal.
            res = ff.file_finding(root, "bug", "an ordinary finding with no attribution", BUG)
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIsNone(sdlc_md.extract_field(body, "Audit-lens"),
                              "an unattributed filing gained an empty attribution line")

    def test_the_flags_reach_the_cli_and_the_fields_file_path(self) -> None:
        """AC5, driven through `main(["file", ...])` and through `--fields-file`.

        MUTANT: delete `"lens": args.lens` from `cmd_file`'s hand-enumerated flags dict. The flag
        is then parsed and silently DROPPED, the filing succeeds UNATTRIBUTED, and every test
        above still passes because they call `file_finding()` directly.

        SECOND MUTANT: leave `lens`/`profile`/`audit_run` out of `FIELDS_FILE_KEYS`.
        `load_fields_file` RAISES on any key outside that tuple, so the one path that does not
        cross a shell - the path a prose-heavy audit finding must use - would be refused outright.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _register(root)
            for rel in GROOM["affects"].split(", "):
                _affect(root, rel.strip())

            doc = {"title": "filed through the command an operator types", **BUG,
                   "lens": LIVE_LENS, "audit_run": rid}
            fp = root / "fields.json"
            fp.write_text(json.dumps(doc), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc = ff.main(["file", "--type", "bug", "--root", str(root),
                              "--fields-file", str(fp)])
            self.assertEqual(0, rc, "the CLI refused a well-formed attributed filing")
            filed = _bugs(root)
            self.assertEqual(1, len(filed))
            body = filed[0].read_text(encoding="utf-8")
            self.assertEqual(LIVE_LENS, sdlc_md.extract_field(body, "Audit-lens"),
                             "the flag was parsed and silently dropped on the way to the filer")
            self.assertEqual(rid, sdlc_md.extract_field(body, "Audit-run"))

    def test_the_flags_reach_the_filer_as_ARGPARSE_FLAGS_not_only_via_a_fields_file(self) -> None:
        """The mutant the sibling AC5 test MISSED, found by mutation and fixed here.

        Deleting `"lens": getattr(args, "lens", None)` from `cmd_file`'s hand-enumerated flags
        dict SURVIVED the fields-file test above, because `--fields-file` is read by
        `load_fields_file` and never touches that dict. Two different code paths carry the same
        three keys, and only one of them was held.

        So this drives `--lens` and `--audit-run` as real command-line FLAGS. An explicit flag
        overrides the document, which is what makes the combination legal and the assertion sharp.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _register(root)
            for rel in GROOM["affects"].split(", "):
                _affect(root, rel.strip())
            doc = {"title": "filed with the attribution passed as flags", **BUG}
            fp = root / "flagfields.json"
            fp.write_text(json.dumps(doc), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc = ff.main(["file", "--type", "bug", "--root", str(root),
                              "--fields-file", str(fp),
                              "--lens", LIVE_LENS, "--audit-run", rid])
            self.assertEqual(0, rc)
            body = _bugs(root)[0].read_text(encoding="utf-8")
            self.assertEqual(LIVE_LENS, sdlc_md.extract_field(body, "Audit-lens"),
                             "--lens was parsed and silently dropped by cmd_file's flags dict")
            self.assertEqual(rid, sdlc_md.extract_field(body, "Audit-run"),
                             "--audit-run was parsed and silently dropped by cmd_file's dict")

    def test_a_mismatched_profile_passed_as_a_FLAG_is_still_refused(self) -> None:
        """MUTANT: drop `"profile": getattr(args, "profile", None)` from `cmd_file`'s flags dict.

        This one survives the sibling flag test, because the profile is DERIVED - dropping it
        means `--profile` is merely ignored and the correct value fills in anyway. The single
        observable loss is that a MISMATCH supplied on the command line stops being caught, which
        is the one thing `--profile` is accepted for at all.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _register(root)
            for rel in GROOM["affects"].split(", "):
                _affect(root, rel.strip())
            fp = root / "mismatch.json"
            fp.write_text(json.dumps({"title": "a mismatched profile on the flag path", **BUG}),
                          encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                rc = ff.main(["file", "--type", "bug", "--root", str(root),
                              "--fields-file", str(fp), "--lens", LIVE_LENS,
                              "--profile", "code", "--audit-run", rid])
            self.assertEqual(1, rc,
                             "a lens/profile mismatch passed as a flag was accepted, so --profile "
                             "never reached the guard")
            self.assertIn("belongs to", err.getvalue())
            self.assertEqual([], _bugs(root), "an id was minted for a refused attribution")

    def test_the_fields_file_allowlist_names_the_three_keys(self) -> None:
        """The direct read of the second mutant above: the allowlist is a tuple a reader RAISES
        on, so a key absent from it is not ignored - the whole document is refused."""
        for key in ("lens", "profile", "audit_run"):
            self.assertIn(key, ff.FIELDS_FILE_KEYS,
                          f"a --fields-file carrying {key!r} would be refused outright")


class AuditAttributionUnheldInvariantsTests(unittest.TestCase):
    """The invariants the first cut ASSERTED IN PROSE and held with nothing.

    Twelve of twenty-four mutants survived the full suite. Every test here names the one it kills.
    """

    def _root(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="attr_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _seed_index(d, "bug")
        _seed_index(d, "cr")
        _seed_index(d, "rfc")
        for rel in GROOM["affects"].split(", "):
            _affect(d, rel.strip())
        return d

    def test_a_refusal_does_not_ADVANCE_THE_ID_SEQUENCE(self) -> None:
        """MUTANT: relocate `check_audit_attribution` into `_file_finding_locked`, after the id is
        allocated. The refusal still fires with an identical message and exit code, and an id is
        burned - so `assertEqual([], _bugs(root))` ("no file was written") cannot see it.

        The first cut's docstring claimed to assert the sequence did not advance. It asserted the
        absence of a file. This asserts the sequence, via the allocator itself.
        """
        import next_id
        root = self._root()
        rid = _register(root)
        before = next_id.allocate_number("bug", root)
        for bad in ({"lens": "no-such-lens-at-all", "audit_run": rid},
                    {"lens": LIVE_LENS, "audit_run": "RUN-NOT-REGISTERED"},
                    {"lens": LIVE_LENS, "profile": "code", "audit_run": rid},
                    {"lens": LIVE_LENS}):
            with self.subTest(bad=sorted(bad)):
                with self.assertRaises(ValueError):
                    ff.file_finding(root, "bug", "x", {**BUG, **bad})
        after = next_id.allocate_number("bug", root)
        self.assertEqual(before, after,
                         f"the id sequence advanced from {before} to {after} across four "
                         f"refusals - an id was minted and then thrown away")

    def test_a_CR_and_an_RFC_carry_the_attribution_too(self) -> None:
        """MUTANTS: delete `_audit_attribution_lines` from the CR template, and from the RFC one.
        Both survived, because all seven original tests filed a BUG - two of the three replaced
        call sites were unheld. A CR is what `refine` produces from an audit and where a
        consolidated Low finding lands, so it is not the minor case.
        """
        root = self._root()
        rid = _register(root)
        for type_ in ("cr", "rfc"):
            with self.subTest(type=type_):
                spec = ({"priority": "High", "ctype": "Improvement",
                         "summary": "found by an audit lens", "acs": ["it is fixed"],
                         "impact": "the class recurs", "size": "M",
                         "affects": "src/thing.py", "date": "2026-07-30"}
                        if type_ == "cr" else
                        {"summary": "weigh it", "options": ["do X", "status quo"]})
                res = ff.file_finding(root, type_, f"an attributed {type_}",
                                      {**spec, "lens": LIVE_LENS, "audit_run": rid})
                body = Path(res["path"]).read_text(encoding="utf-8")
                self.assertEqual(LIVE_LENS, sdlc_md.extract_field(body, "Audit-lens"),
                                 f"the {type_} template does not render the attribution")
                self.assertEqual(rid, sdlc_md.extract_field(body, "Audit-run"))
                self.assertEqual(LIVE_PROFILE, sdlc_md.extract_field(body, "Audit-profile"))

    def test_each_refusal_EXPLAINS_itself_as_its_AC_requires(self) -> None:
        """MUTANTS: delete either half-attribution refusal (the guards downstream still raise
        `ValueError`, so `assertRaises(ValueError)` passes); or replace both messages with
        "a half-stamped attribution"; or strip the register path and hint from the run refusal.
        All three survived the full suite.

        AC4's Then is "refused EXPLAINING that a class is counted per run"; AC3's is "refused by
        name POINTING AT THE REGISTER PATH". Those are behaviours, so they are asserted.
        """
        root = self._root()
        rid = _register(root)
        cases = [
            ({"lens": LIVE_LENS}, ["--audit-run is required", "detector owed"]),
            ({"audit_run": rid}, ["--lens is required", "PER LENS"]),
            ({"lens": LIVE_LENS, "audit_run": "RUN-NOPE"},
             ["RUN-NOPE", str(cost_evidence()), "typo"]),
        ]
        for fields, needles in cases:
            with self.subTest(fields=sorted(fields)):
                with self.assertRaises(ValueError) as ctx:
                    ff.file_finding(root, "bug", "x", {**BUG, **fields})
                msg = str(ctx.exception)
                for needle in needles:
                    self.assertIn(needle, msg,
                                  f"the refusal does not explain itself: {msg[:160]}")

    def test_profile_ALONE_is_refused_and_an_unknown_profile_is_named(self) -> None:
        """MUTANTS: (1) narrow the all-or-none trigger to `if not (lens or run)`, so `--profile`
        alone is accepted, silently discarded, and the filing succeeds unattributed. (2) drop the
        unknown-profile branch, so a profile no pack declares falls through to a message naming
        `--audit-run`, a flag the operator never supplied - which is what AC2's "refused by name
        listing what the resolver does declare" forbids.
        """
        root = self._root()
        with self.assertRaises(ValueError) as ctx:
            ff.file_finding(root, "bug", "x", {**BUG, "profile": LIVE_PROFILE})
        self.assertIn("--lens is required", str(ctx.exception))
        self.assertEqual([], _bugs(root), "a profile-only filing was minted")

        with self.assertRaises(ValueError) as ctx2:
            ff.file_finding(root, "bug", "x", {**BUG, "profile": "no-such-pack-anywhere"})
        msg = str(ctx2.exception)
        self.assertIn("no-such-pack-anywhere", msg)
        self.assertIn(LIVE_PROFILE, msg, "the refusal does not list the packs that do exist")

    def test_a_stub_pack_elsewhere_does_not_break_an_unrelated_filing(self) -> None:
        """A half-written pack is an EXPECTED state - `reference-audit.md#audit-extend` invites a
        project to add packs. Unguarded, `resolve_profile` raised for the stub and refused every
        attributed filing in the project, naming a file the operator had never mentioned.

        MUTANT: drop the per-pack `try/except UnknownProfile`.
        """
        root = self._root()
        rid = _register(root)
        packs = Path(ff.__file__).resolve().parent.parent / "templates" / "audit-profiles"
        stub = packs / "zz-review-stub.md"
        stub.write_text("# A pack a project started\n\nTBD.\n", encoding="utf-8")
        self.addCleanup(stub.unlink, missing_ok=True)
        res = ff.file_finding(root, "bug", "filed while a stub pack sits beside the real ones",
                              {**BUG, "lens": LIVE_LENS, "audit_run": rid})
        body = Path(res["path"]).read_text(encoding="utf-8")
        self.assertEqual(LIVE_LENS, sdlc_md.extract_field(body, "Audit-lens"))

    def test_an_AMBIGUOUS_lens_is_refused_rather_than_resolved_alphabetically(self) -> None:
        """MUTANT: `profile or owners[0]`.

        Every doc rests on "a lens resolves to exactly one pack" and nothing enforced it. Worse
        than the silent pick: with two owners, SUPPLYING `--profile zz-dupe` was accepted while
        OMITTING it stamped `process` - two different records for one finding, from the check that
        claims to be stronger than requiring all three.
        """
        root = self._root()
        rid = _register(root)
        packs = Path(ff.__file__).resolve().parent.parent / "templates" / "audit-profiles"
        dupe = packs / "zz-review-dupe.md"
        dupe.write_text((packs / f"{LIVE_PROFILE}.md").read_text(encoding="utf-8"),
                        encoding="utf-8")
        self.addCleanup(dupe.unlink, missing_ok=True)
        with self.assertRaises(ValueError) as ctx:
            ff.file_finding(root, "bug", "x", {**BUG, "lens": LIVE_LENS, "audit_run": rid})
        self.assertIn("more than one pack", str(ctx.exception))
        self.assertEqual([], _bugs(root))

    def test_the_three_keys_go_through_the_SHARED_field_guard(self) -> None:
        """MUTANT: delete a bespoke `require_single_line` loop inside the attribution check - which
        is what the first cut had, and it survived.

        `check_creator_fields` is the one choke point every creation path already runs, so the keys
        belong in `SINGLE_LINE_FIELDS` rather than in a second copy of the rule. `audit_run` is the
        sharp one: it is free-form, so a markdown link in it lands verbatim in a tracked artefact
        and can red the repo's own links guard.
        """
        for key in ("lens", "profile", "audit_run"):
            self.assertIn(key, sdlc_md.SINGLE_LINE_FIELDS,
                          f"{key} escapes the shared single-line guard")
        with self.assertRaises(ValueError):
            sdlc_md.check_creator_fields(
                {"title": "t", "audit_run": "RUN-1\nsecond line"})

    def test_detector_for_lens_reaches_all_THREE_surfaces_that_can_carry_it(self) -> None:
        """MUTANTS, all three of which survived a first pass because `detector-owed --file` calls
        `file_finding()` DIRECTLY and so exercises none of them:

        (1) drop `detector_for_lens` from `cmd_file`'s hand-enumerated flags dict - the flag is
            then parsed and silently discarded;
        (2) drop it from `FIELDS_FILE_KEYS` - `load_fields_file` RAISES on an unknown key, so a
            fields-file carrying it is refused outright;
        (3) drop it from `SINGLE_LINE_FIELDS` - it escapes the one choke point every creation path
            already runs.

        Three surfaces can carry this field and only the programmatic one was held.
        """
        self.assertIn("detector_for_lens", ff.FIELDS_FILE_KEYS)
        self.assertIn("detector_for_lens", sdlc_md.SINGLE_LINE_FIELDS)
        with self.assertRaises(ValueError):
            sdlc_md.check_creator_fields({"title": "t", "detector_for_lens": "a\nb"})

        root = self._root()
        fp = root / "det.json"
        fp.write_text(json.dumps({"title": "build the detector", **BUG}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc = ff.main(["file", "--type", "bug", "--root", str(root),
                          "--fields-file", str(fp), "--detector-for-lens", "correctness"])
        self.assertEqual(0, rc)
        body = _bugs(root)[0].read_text(encoding="utf-8")
        self.assertEqual("correctness", sdlc_md.extract_field(body, "Detector-for-lens"),
                         "--detector-for-lens was parsed and silently dropped by cmd_file")

        # And through the fields-file document itself, which the allowlist gates separately.
        fp2 = root / "det2.json"
        fp2.write_text(json.dumps({"title": "build another detector", **BUG,
                                   "detector_for_lens": "architecture"}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc2 = ff.main(["file", "--type", "bug", "--root", str(root),
                           "--fields-file", str(fp2)])
        self.assertEqual(0, rc2, "a fields-file carrying the key was refused outright")
        bodies = [b.read_text(encoding="utf-8") for b in _bugs(root)]
        self.assertIn("architecture",
                      [sdlc_md.extract_field(b, "Detector-for-lens") for b in bodies])

    def test_a_LOW_severity_finding_says_so_rather_than_dropping_the_attribution(self) -> None:
        """The v3 silent drop. A Low-severity finding consolidates into a shared CR that carries no
        per-finding lens, so the attribution was validated pre-mint - run checked against the
        register, lens against the packs, pair cross-checked - and then discarded without a word.

        `triage_noise` already had the loud precedent for `tranche` (the EP0014 principle); a third
        field family was added to the filer without extending it. The long tail of Low findings is
        exactly the population a recurring-class count is for.
        """
        import triage_noise
        root = self._root()
        rid = _register(root)
        res = triage_noise.consolidate_low_finding(
            root, "bug", "a low finding with an attribution",
            {**BUG, "severity": "Low", "lens": LIVE_LENS, "audit_run": rid}, "2026-07-30")
        self.assertIn("attribution_dropped", res,
                      "the attribution was discarded with no record that it had been")
        self.assertEqual({"lens": LIVE_LENS, "audit_run": rid}, res["attribution_dropped"])


def cost_evidence():
    """The register's directory, as the refusal must name it."""
    return _load_audit_cost().EVIDENCE


class AuditRunRegisterTests(unittest.TestCase):
    """US0462 AC3: the register is a real writer's output, not a reader with nothing behind it."""

    def test_an_unregistered_run_id_is_refused_before_an_id_is_minted(self) -> None:
        """AC3. A ONE-CHARACTER typo is the fixture, because that is the whole point: an
        unregistered id accepted would manufacture a second distinct run and with it a false
        detector-owed verdict.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rid = _register(root, "RUN-AUDIT-01")
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "bug", "x",
                                {**BUG, "lens": LIVE_LENS, "audit_run": rid[:-1]})
            msg = str(ctx.exception)
            self.assertIn(rid[:-1], msg)
            self.assertIn("register", msg)
            self.assertEqual([], _bugs(root), "an id was minted against an unregistered run")

    def test_the_register_has_a_WRITER_and_it_is_not_under_dot_local(self) -> None:
        """The dead-path check the design review demanded: for every reader, name its writer.

        A register under `.local/` would have been gitignored - empty on every clone but the one
        that wrote it, while the findings citing it stayed tracked. That is a reader whose data
        exists nowhere, which is the defect this story was one edit away from shipping.
        """
        ac = _load_audit_cost()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _register(root, "RUN-AUDIT-77")
            self.assertIsNotNone(ac.run_row(root, rid), "the writer's row is not readable")
            self.assertEqual({rid: ac.PROVENANCE_RECORDED}, ac.registered_run_ids(root))
            written = ac.ledger_path(root)
            self.assertTrue(written.is_file())
            self.assertNotIn(".local", written.parts,
                             "the register was written under a gitignored directory, so it is "
                             "empty on every other clone")

    def test_a_backfilled_row_is_marked_apart_from_a_recorded_one(self) -> None:
        """MUTANT: write every row as `recorded`. Five historical `wf_` ids were minted by
        nothing and lifted from prose written for another purpose - laundering them into the same
        authority as a measured run is what the provenance split exists to stop."""
        ac = _load_audit_cost()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ac.record(root, {"run_id": "wf_deadbeef", "lenses": 1,
                             "provenance": ac.PROVENANCE_BACKFILLED})
            self.assertEqual({"wf_deadbeef": ac.PROVENANCE_BACKFILLED},
                             ac.registered_run_ids(root))
            self.assertNotEqual(ac.PROVENANCE_RECORDED, ac.PROVENANCE_BACKFILLED)



class WriterMatchesParserTests(unittest.TestCase):
    """BG0530: the module that WRITES a bug's criteria and the module that EXECUTES them
    disagreed about their shape, for 400 bugs, undetected.

    `file_finding.py:127` claims of a neighbouring mechanism that the runner and the validator
    "cannot drift into contradicting each other again". They had - by a different route, in the
    same file - and nothing noticed because `verify_ac run` exited 0 when it parsed nothing.
    """

    def test_a_freshly_filed_bug_parses(self) -> None:
        """The fixture is built by CALLING the filer, never by hand - a hand-written example
        that happens to match is exactly how the two drifted while looking fine.

        Mutant: drop the `ACn` marker from the criteria renderer, returning it to the bare
        `- [ ] <prose>` bullet it emitted for 400 bugs - this reddens.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "verify_ac_bg0530", Path(__file__).resolve().parents[1] / "verify_ac.py")
        va = importlib.util.module_from_spec(spec)
        sys.modules["verify_ac_bg0530"] = va
        spec.loader.exec_module(va)

        block = ff.criteria_block("bug", {"acs": ["it refuses an empty batch",
                                                        "it accepts a full one"]})
        text = ("# BG9999: x\n\n> **Status:** Open\n\n## Acceptance Criteria\n\n"
                + block + "\n")
        parsed = va.parse_story(text)
        self.assertEqual(len(parsed), 2,
                         f"the filer writes a shape verify_ac cannot read:\n{block}")
        self.assertEqual([b.ac_id for b in parsed], ["AC1", "AC2"])

    def test_the_derived_shape_parses_too(self) -> None:
        """The tool-derived path is the one 19 open bugs are in, and it is the path a filer
        takes when nobody supplies criteria.

        Mutant: mark only the authored branch - a filed finding is still invisible to the runner.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "verify_ac_bg0530b", Path(__file__).resolve().parents[1] / "verify_ac.py")
        va = importlib.util.module_from_spec(spec)
        sys.modules["verify_ac_bg0530b"] = va
        spec.loader.exec_module(va)
        # Fields with real substance: the derivation refuses to invent a criterion from fewer
        # than five words, and a thin fixture would exercise the stated-absence note instead of
        # the derived block this criterion is about.
        block = ff.criteria_block("bug", {
            "summary": "the close reports a refusal it could not attribute to any lane",
            "steps": "run sprint close over a run whose gate failed on a timed lane",
            "fix": "widen the lane pattern so a timing stamp does not defeat attribution"})
        text = ("# BG9999: x\n\n> **Status:** Open\n\n## Acceptance Criteria\n\n"
                + block + "\n")
        self.assertTrue(va.parse_story(text),
                        f"the DERIVED criteria block is unreadable:\n{block}")


class VerifySelectorWriteGuardTests(unittest.TestCase):
    """US0667/US0668 (CR0508): a `Verify:` selector naming no test is refused where it is WRITTEN.

    `verify_ac.selector_resolves` already answered this and no writer called it, so an AC could be
    authored, committed and read as evidence while pointing at nothing - surfacing only if
    somebody later ran `verify_ac`. This repository's scar: four units shipped with Verify lines
    verifying NOTHING, and it recurred twice in one session.
    """

    _SCRIPTS = Path(__file__).resolve().parents[1]

    def _file(self, ac):
        import json, subprocess, tempfile  # noqa: PLC0415
        fields = {"title": "probe", "severity": "Low", "points": 1,
                  "affects": ".claude/skills/sdlc-studio/scripts/file_finding.py",
                  "summary": "probe", "steps": "probe", "fix": "probe", "acs": [ac]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(fields, fh)
            path = fh.name
        return subprocess.run(
            [sys.executable, str(self._SCRIPTS / "file_finding.py"), "file", "--type", "bug",
             "--fields-file", path, "--dry-run"],
            capture_output=True, text=True, timeout=900, check=False)

    _ROOT = Path(__file__).resolve().parents[5]

    def _new(self, verify, title="probe"):
        """The OTHER writer. `artifact.py new` is a documented creation path, and US0667's
        criterion says BOTH refuse - so the test must drive both or it asserts half its claim."""
        import subprocess  # noqa: PLC0415
        return subprocess.run(
            [sys.executable, str(self._SCRIPTS / "artifact.py"), "--root", str(self._ROOT),
             "new", "--type", "story", "--epic", "EP0215", "--title", title, "--points", "1",
             "--dry-run", "--ac", "it works", "--verify", verify],
            capture_output=True, text=True, timeout=900, check=False)

    def test_a_verify_selector_naming_no_test_is_refused_at_write(self) -> None:
        # A REAL file, a REAL method name, the WRONG class - the exact shape that recurred twice.
        # BOTH writers, because that is what the criterion claims. Asserting only the filer is how
        # this shipped stamped `Verified: yes` while `artifact.py new` wrote the dead selector
        # through: the two writers hold `verify` in different shapes, so a reader that saw one
        # shape was a guard with a documented side door.
        dead = ("pytest .claude/skills/sdlc-studio/scripts/tests/"
                "test_validate.py::NoSuchClassHere::test_nope")
        r = self._file(f"it works. **Verify:** {dead}")
        self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("names no test that exists", r.stdout + r.stderr)

        n = self._new(dead)
        self.assertNotEqual(0, n.returncode,
                            "artifact.py new accepted a selector the filer refused:\n"
                            + n.stdout + n.stderr)
        self.assertIn("names no test that exists", n.stdout + n.stderr)

    def test_a_node_absent_from_an_existing_file_is_still_refused(self) -> None:
        """BG0570 AC1: the narrowing must not DISARM the guard.

        A distinct claim from US0667 AC1, which asserts both writers refuse. This one asserts the
        one case that survived the narrowing: the file listed its nodes and this node is not among
        them. Every other False verdict is now accepted, so a guard that had lost this case would
        pass every other test in this class while refusing nothing at all.
        """
        target = ".claude/skills/sdlc-studio/scripts/tests/test_validate.py"
        for writer, run in (("file_finding.file",
                             lambda s: self._file(f"it works. **Verify:** {s}")),
                            ("artifact.py new", self._new)):
            with self.subTest(writer=writer):
                r = run(f"pytest {target}::ThisClassIsNotInThatFile::test_x")
                self.assertNotEqual(0, r.returncode,
                                    f"{writer} accepted a node absent from a file that EXISTS "
                                    f"and collects:\n{r.stdout}{r.stderr}")
                self.assertIn("names no test that exists", r.stdout + r.stderr)

    def test_a_selector_that_is_not_a_typo_is_accepted_and_reported(self) -> None:
        """BG0570 AC2. `selector_resolves` answers False for four different facts and only two are
        typos. Refusing the others told an author their test did not exist while it sat on disk,
        and refused the first story of every greenfield project.

        Asserted on the REPORT, not on the absence of a refusal: a silent accept satisfies
        "not refused" too, and would pass this criterion while telling the author nothing.
        """
        import tempfile  # noqa: PLC0415
        tmp = Path(tempfile.mkdtemp(prefix="ff_notatypo_"))
        try:
            # A file that EXISTS but will not collect - a missing import. The environment case.
            broken = tmp / "test_will_not_collect.py"
            broken.write_text("import a_module_that_does_not_exist_xyz\n")
            cases = [
                # (selector, the fragment the report must carry, or "" for REQUIRED SILENCE)
                # A file that EXISTS but will not collect: abnormal, so it is named.
                (f"pytest {broken}::AnyClass::test_x", "will not collect"),
                # A file that does not exist and whose basename exists nowhere: the ORDINARY
                # ordering. Accepted SILENTLY - a note here fires on every story in a greenfield
                # project, and a warning on the normal case costs the signal in the case that
                # matters.
                ("pytest tests/test_nothing_of_this_name_anywhere_xyz.py::C::test_x", ""),
            ]
            for selector, fragment in cases:
                # BOTH writers, because the Then clause says both. Driving only the filer is the
                # exact half-assertion that let `artifact.py new` ship the guard's own hole.
                for writer, run in (("file_finding.file",
                                     lambda s: self._file(f"it works. **Verify:** {s}")),
                                    ("artifact.py new", self._new)):
                    with self.subTest(selector=selector, writer=writer):
                        r = run(selector)
                        self.assertEqual(0, r.returncode,
                                         f"{writer} REFUSED a non-typo:\n{r.stdout}{r.stderr}")
                        out = r.stdout + r.stderr
                        if fragment:
                            self.assertIn("not judged here", out,
                                          f"{writer} accepted the abnormal case SILENTLY:\n{out}")
                            self.assertIn(fragment, out,
                                          f"{writer} gave the wrong reason:\n{out}")
                        else:
                            # The silence is a CLAIM, asserted, not an omission in the test.
                            self.assertNotIn("not judged here", out,
                                             f"{writer} noted the NORMAL ordering - that note "
                                             f"fires on every greenfield story:\n{out}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a_misspelled_test_filename_is_still_refused(self) -> None:
        """BG0570 AC3. Without this, AC2 launders every mistyped PATH into 'greenfield ordering' -
        the hole the guard exists to close. Same two-way split `fictional_affects` draws for
        declared paths: a basename that exists elsewhere is a typo, one that exists nowhere is a
        file not yet written."""
        # A real test file, reached by a path that is wrong - the directory prefix is mistyped.
        r = self._file("it works. **Verify:** pytest wrong/dir/test_validate.py::C::test_x")
        self.assertNotEqual(0, r.returncode,
                            "a mistyped path was accepted as greenfield ordering:\n"
                            + r.stdout + r.stderr)
        # ... and it must NAME the path it found. Asserting only the refusal is weaker than the
        # criterion: the guard already computed the near miss, and a refusal that discards it
        # sends the author back to grep - the step the guard exists to remove.
        out = r.stdout + r.stderr
        self.assertIn("did you mean", out, f"the refusal named no near path:\n{out}")
        self.assertIn("tests/test_validate.py", out,
                      f"the near path did not name the real file:\n{out}")

    def test_one_reader_answers_which_file_a_selector_targets(self) -> None:
        """BG0570 AC4. Replacing the helper must move the WRITER's verdict. An inlined regex in
        the guard would pass every other test here while re-creating the divergence: `verify_ac`
        already parsed a selector's target in three places with two different predicates."""
        sys.path.insert(0, str(self._SCRIPTS))
        import file_finding as ff, verify_ac  # noqa: PLC0415
        real_target, real_coll = verify_ac.selector_target_file, verify_ac.selector_collected
        dead = "pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::Nope::test_x"
        try:
            # Force the helper to report a target that exists nowhere, with no basename match.
            # Point the helper at a path that does NOT exist but whose BASENAME does. Following
            # the helper means refusing (a mistyped path, near miss named); parsing the selector
            # privately means reading its own real path, which EXISTS, and accepting it as
            # uncollectable. Refuse versus accept - an inlined parser cannot reach the same
            # verdict, which an earlier version of this test allowed by asserting only acceptance.
            verify_ac.selector_target_file = lambda *a, **k: "no/such/dir/test_validate.py"  # noqa: ARG005
            verify_ac.selector_collected = lambda *a, **k: False  # noqa: ARG005
            with self.assertRaises(ValueError) as caught:
                ff.check_verify_selectors(".", {"acs": [f"x. **Verify:** {dead}"]})
            self.assertIn("no/such/dir/test_validate.py", str(caught.exception),
                          "the guard parsed the target itself instead of asking the helper")
            # ... and back: a helper reporting a collected file must restore the refusal.
            verify_ac.selector_collected = lambda *a, **k: True  # noqa: ARG005
            with self.assertRaises(ValueError):
                ff.check_verify_selectors(".", {"acs": [f"x. **Verify:** {dead}"]})
        finally:
            verify_ac.selector_target_file, verify_ac.selector_collected = real_target, real_coll

    def test_the_refusal_names_the_near_miss(self) -> None:
        """CR0508: a refusal saying only 'this does not resolve' sends the author back to grep -
        the step they skipped to get here. Right file, right METHOD, wrong class must name the
        class they meant."""
        import subprocess  # noqa: PLC0415
        target = (".claude/skills/sdlc-studio/scripts/tests/test_validate.py")
        collected = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", target],
            capture_output=True, text=True, timeout=900, check=False, cwd=str(self._ROOT))
        node = next((ln.strip() for ln in collected.stdout.splitlines()
                     if "::" in ln and not ln.startswith(" ")), None)
        self.assertIsNotNone(node, "could not collect a real node to build the near miss from")
        cls, meth = node.split("::")[1], node.split("::")[-1]
        r = self._file(f"it works. **Verify:** pytest {target}::NotThe{cls}::{meth}")
        self.assertNotEqual(0, r.returncode)
        out = r.stdout + r.stderr
        self.assertIn("did you mean", out, f"the refusal named no near miss:\n{out}")
        self.assertIn(cls, out, f"the near miss did not name the real class {cls}:\n{out}")

    def test_one_reader_answers_whether_a_selector_resolves(self) -> None:
        """AC2: `verify_ac.selector_resolves` decides, never a second copy. Replacing it must move
        the WRITER - a divergent reader is the defect this repository has filed four times, and it
        would be especially pointless here where the first implementation is complete and tested.
        """
        sys.path.insert(0, str(self._SCRIPTS))
        import file_finding as ff, verify_ac  # noqa: PLC0415
        real = verify_ac.selector_resolves
        try:
            verify_ac.selector_resolves = lambda *a, **k: False  # noqa: ARG005
            with self.assertRaises(ValueError):
                ff.check_verify_selectors(".", {"acs": ["x. **Verify:** shell true"]})
            verify_ac.selector_resolves = lambda *a, **k: True  # noqa: ARG005
            self.assertEqual([], ff.check_verify_selectors(
                ".", {"acs": ["x. **Verify:** pytest nowhere::Nope::test_nope"]}),
                "the writer did not follow the shared resolver")
        finally:
            verify_ac.selector_resolves = real

    def test_a_resolving_verify_selector_is_accepted(self) -> None:
        # The positive control: the guard must discriminate, not refuse every write.
        r = self._file("it works. **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/"
                       "test_validate.py -k WarningRatchetExitCode")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_an_unjudgeable_selector_is_accepted_and_reported(self) -> None:
        # US0668. Refusing what cannot be judged would make every writer unusable on a machine
        # missing one runner - a worse failure than the one being fixed.
        r = self._file("it works. **Verify:** shell true")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("not judged here", r.stdout + r.stderr)

    def test_a_judgeable_unresolvable_selector_is_still_refused(self) -> None:
        # The control for the control: "accept what cannot be judged" is otherwise satisfied by
        # accepting everything.
        r = self._file("it works. **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/"
                       "test_validate.py::AlsoNotAClass::test_nope")
        self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)


class AffectsInferenceScopeTests(unittest.TestCase):
    """BG0564/BG0538: two ways the affects checks punished correct behaviour."""

    REPO = SCRIPT.parents[3]

    def test_a_common_basename_is_not_treated_as_a_typo(self) -> None:
        """MUTANT: drop the `_AMBIGUOUS_BASENAMES` early return from `basename_matches`.

        The typo inference asks whether the basename exists elsewhere. That is sound for a
        distinctive name and worthless for `__init__.py`, where a match says only that Python
        projects have those everywhere - so a unit CREATING one was refused with a suggestion
        list of dozens of unrelated files.
        """
        self.assertEqual([], ff.basename_matches(self.REPO, "newpkg/__init__.py"))
        self.assertEqual([], ff.basename_matches(self.REPO, "docs/newthing/README.md"))

    def test_a_distinctive_basename_is_still_reported(self) -> None:
        """The control - the inference was narrowed, not removed."""
        hits = ff.basename_matches(self.REPO, "wrong/dir/verify_ac.py")
        self.assertTrue(hits, "a distinctive basename in the wrong directory is a typo")

    def test_a_consumed_changelog_fragment_is_not_fictional(self) -> None:
        """MUTANT: drop the `_is_transient_path` guard from `unresolvable_affects`.

        The repo asks every behaviour change to declare its `changelog.d/<ID>.md` fragment, and
        `changelog compose` unlinks it at the release cut - so every COMPLYING unit reported a
        fictional file, and the warning was loudest for those that followed the rule.
        """
        self.assertEqual([], ff.unresolvable_affects(self.REPO, ["changelog.d/BG9999.md"]))

    def test_a_missing_path_elsewhere_is_still_reported(self) -> None:
        """The control - the exemption is one directory, not a hole."""
        self.assertEqual(["scripts/definitely_not_here.py"],
                         ff.unresolvable_affects(self.REPO, ["scripts/definitely_not_here.py"]))


class DerivedDetectorSeesItsOwnWriterTests(unittest.TestCase):
    """BG0585: `is_derived_criterion` matched ZERO output of the writer in its own module.

    It shipped 2026-08-04; `criteria_block` gained the `**ACn**` marker two days later, and
    nothing re-ran the detector against its own writer. For twelve days the `derived-only` limb
    of `conformance.unit_is_ungroomed` was inert, so the placeholder that reads like content -
    the shape that "satisfies every has-criteria check in the repo while being unjudgeable" -
    passed every gate in the repository. A goal-review seat found it by executing the predicate
    while judging a batch, not by reading the code.

    Every fixture below is built by CALLING the writer where it can be, because a hand-typed
    example that happens to match is exactly how the two drifted while looking fine.
    """

    def test_the_detector_matches_its_own_writers_output(self) -> None:
        """MUTANT: delete the `_AC_NUMBER_RE.sub` line - the defect as filed.

        THE ONE THAT MATTERS. Driven through `criteria_block`, so the assertion is about the
        bytes the module actually emits rather than about a string in this test.
        """
        block = ff.criteria_block("bug", {"acs": ["The behaviour described is corrected: X"]})
        lines = [ln for ln in block.splitlines() if ln.strip().startswith("- [")]
        self.assertTrue(lines, block)
        for line in lines:
            self.assertTrue(ff.is_derived_criterion(line),
                            f"the detector does not match its own writer:\n{line}")

    def test_the_unnumbered_form_still_matches(self) -> None:
        """REGRESSION CONTROL. MUTANT: anchor the pattern so it REQUIRES the number.

        The bare form predates the marker and is still in the corpus; a fix that only reads the
        new spelling trades one blindness for another.
        """
        self.assertTrue(ff.is_derived_criterion(
            "- [ ] The behaviour described is corrected: X"))

    def test_an_authored_numbered_criterion_is_not_derived(self) -> None:
        """POSITIVE CONTROL. MUTANT: strip the number and return True unconditionally.

        Without this, "make everything derived" passes the two tests above, and the grooming
        gate would refuse every authored criterion in the repository.
        """
        self.assertFalse(ff.is_derived_criterion(
            "- [ ] **AC1** Given a design rung, when it closes, then it refuses"))
        # A word that merely BEGINS with those letters must survive the strip untouched.
        self.assertFalse(ff.is_derived_criterion(
            "- [ ] ACCEPTED: The behaviour described is corrected: X"))
        # LOWER-CASE `the` HERE MADE THIS VACUOUS. `_derived_patterns` is
        # case-sensitive, so the line was False whether or not `ACCEPTED:` was eaten,
        # and the row's own mutant (`^AC\\w*`) survived all 6603 tests. A review found
        # it. The boundary cases go beside it, so one spelling cannot carry the claim.
        for line in ("- [ ] AC power: The behaviour described is corrected: X",
                     "- [ ] ACL check: The behaviour described is corrected: X",
                     "- [ ] ACCEPT: The behaviour described is corrected: X"):
            with self.subTest(line=line):
                self.assertFalse(ff.is_derived_criterion(line), line)

    def test_the_heading_form_matches_too(self) -> None:
        """MUTANT: strip the `ACn` label but not the leading `###`.

        `criteria_are_all_derived` deliberately collects heading lines, so leaving the heading
        spelling blind is an enumerated list exempting what it forgot - the fourth carried
        lesson in this run's own brief.
        """
        self.assertTrue(ff.is_derived_criterion(
            "### AC4: The behaviour described is corrected: X"))

    def test_every_spelling_the_writer_can_emit_is_covered(self) -> None:
        """MUTANT: handle `AC1 ` but not `AC1: `.

        The separator is optional in the corpus and both spellings occur, so the pattern must
        consume either. Asserted as a set so a fix covering half of them cannot pass.
        """
        for line in ("- [ ] **AC1** The behaviour described is corrected: X",
                     "- [ ] AC1: The behaviour described is corrected: X",
                     "- [x] **AC12** The behaviour described is corrected: X",
                     "* [ ] **AC3** The proposed fix lands, pinned by a test: X",
                     "### AC4: The behaviour described is corrected: X"):
            with self.subTest(line=line):
                self.assertTrue(ff.is_derived_criterion(line), line)

    def test_sprint_plan_refuses_the_numbered_scaffold(self) -> None:
        """THE WIRING TEST. MUTANT: revert `is_derived_criterion`, and the CLI reports 0 ungroomed.

        Driven through the shipped entry point in a throwaway fixture, because a library test
        cannot see whether a predicate is WIRED. This repository spent a whole sprint with
        `brief_fingerprint(brief(...))` passing in-process while `critic.py brief` printed
        nothing, and every seat reviewing this unit named that scar by name.

        It drives `plan`, which REFUSES, rather than `breakdown`, which reports and exits 0.
        The first cut named `plan` in the criterion and ran `breakdown` in the test, so no
        refusal was ever asserted - the wiring guarantee the criterion exists for was the one
        thing it did not check. A review found that.
        """
        import subprocess  # noqa: PLC0415 - the point is to leave this process
        script = Path(__file__).resolve().parents[1] / "sprint.py"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / "bugs" / "BG9001-scaffold.md").write_text(
                "# BG9001: a scaffolded finding\n\n> **Status:** Open\n> **Severity:** Medium\n"
                "> **Points:** 2\n> **Affects:** scripts/x.py\n\n## Summary\n\nA thing is "
                "broken.\n\n## Acceptance Criteria\n\n- [ ] **AC1** The behaviour described "
                "is corrected: a thing is broken.\n", encoding="utf-8")
            wl = root / "wl.txt"
            wl.write_text("BG9001\n", encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "-B", str(script), "plan", "--root", str(root),
                 "--worklist", str(wl)],
                capture_output=True, text=True)
            # The CONTROL, in the same fixture: one hand-authored criterion and the identical
            # command plans. Without it, a `plan` that refused everything would pass the
            # assertions below.
            (root / "sdlc-studio" / "bugs" / "BG9001-scaffold.md").write_text(
                "# BG9001: a scaffolded finding\n\n> **Status:** Open\n> **Severity:** Medium\n"
                "> **Points:** 2\n> **Affects:** scripts/x.py\n\n## Summary\n\nA thing is "
                "broken.\n\n## Acceptance Criteria\n\n- [ ] **AC1** Given a widget at rest, "
                "when it is poked, then it wobbles.\n", encoding="utf-8")
            ok = subprocess.run(
                [sys.executable, "-B", str(script), "plan", "--root", str(root),
                 "--worklist", str(wl)],
                capture_output=True, text=True)
        page = r.stdout + r.stderr
        # `breakdown` was asserted here first. It is READ-ONLY and exits 0, so it could not
        # show that anything REFUSES - and its two assertions held identically for a fixture
        # with no criteria at all, which a review demonstrated. The exit code is the claim.
        self.assertNotEqual(0, r.returncode, page)
        self.assertIn("REFUSED", page, page)
        self.assertIn("ungroomed", page, page)
        self.assertIn("BG9001", page, page)
        self.assertEqual(0, ok.returncode, ok.stdout + ok.stderr)

    # The four shapes two review seats measured as derived-only, captured VERBATIM from the
    # artefacts as they stood when the measurement was taken. They are held here rather than
    # read from the live corpus because grooming a bug is a legitimate act that must not turn
    # this test red: BG0578 and BG0581 were groomed the day after the measurement and the
    # earlier form of this test, which globbed them off disk, went red for that reason alone.
    # A pin whose subject is allowed to change is a pin on nothing.
    DERIVED_ONLY_SHAPES = {
        "BG0578": (
            "- [ ] **AC1** The behaviour described is corrected: `test_census.attribute` places "
            "a test file by counting how often it names each sibling module and taking the "
            "most-mentioned.\n"
            "- [ ] **AC2** The proposed fix lands, pinned by a test: Attribution should prefer "
            "a DECLARED owner over a counted one: a unit's `Affects` already names the file, "
            "and a module-level marker in the test would state its...\n"),
        "BG0581": (
            "- [ ] **AC1** The behaviour described is corrected: `reachable_end_state("
            "repo_root, batch)` takes the root and the batch and nothing else.\n"),
        "BG0537": (
            "- [ ] **AC1** The behaviour described is corrected: <the summary, restated>.\n"),
        "BG0547": (
            "- [ ] **AC1** The behaviour described is corrected: <the summary, restated>.\n"
            "- [ ] **AC2** Following the recorded steps no longer reproduces the defect: "
            "<the steps, restated>.\n"),
    }

    @staticmethod
    def _artefact(uid: str, criteria: str) -> str:
        return (f"# {uid}: a finding\n\n> **Status:** Open\n> **Severity:** Medium\n"
                f"> **Points:** 2\n> **Affects:** scripts/x.py\n\n## Summary\n\n"
                f"A thing is broken.\n\n## Acceptance Criteria\n\n{criteria}\n## Impact\n\n"
                f"It misreports.\n")

    def test_the_measured_derived_only_shapes_still_read_derived_only(self) -> None:
        """MUTANT: broaden the pattern to `^AC.*?:` - it would swallow authored criteria.

        Two review seats independently measured these four shapes before the fix was written.
        Pinning them means an over-reaching fix fails HERE rather than by refusing somebody's
        plan a week later. The TEXT is the subject, not the id: see DERIVED_ONLY_SHAPES.
        """
        import conformance as _c  # noqa: PLC0415 - sibling, resolved via the tests path
        for uid, criteria in self.DERIVED_ONLY_SHAPES.items():
            with self.subTest(uid=uid):
                _, why = _c.unit_is_ungroomed("bug", self._artefact(uid, criteria))
                self.assertEqual("derived-only", why,
                                 f"the {uid} shape was measured as derived-only by two seats")

    def test_an_authored_criterion_is_not_read_as_derived(self) -> None:
        """MUTANT: return `derived-only` unconditionally - the control the id pins cannot give.

        Every shape above is a POSITIVE case, so all four pass for a detector that says yes to
        everything. This is the negative one, in the same fixture shape, so the pair
        discriminates.
        """
        import conformance as _c  # noqa: PLC0415 - sibling, resolved via the tests path
        authored = ("- [ ] **AC1** Given a widget at rest, when it is poked, then it wobbles\n"
                    "- [ ] **AC2** Given a poked widget, when it settles, then it is still\n")
        _, why = _c.unit_is_ungroomed("bug", self._artefact("BG9002", authored))
        self.assertNotEqual("derived-only", why,
                            "authored Given/When/Then criteria must not read as tool-derived")

    def test_the_corpus_census_stays_within_its_measured_bounds(self) -> None:
        """MUTANT: make `is_derived_criterion` return True unconditionally.

        Naming shapes pins nothing about REACH: a review made that mutation and every shape
        assertion above still passed, while the census went 17 bugs / 0 stories -> 364 / 669.
        The NUMBER is the claim. Bounded rather than exact, because filing or grooming a bug
        must not turn this red - the ceiling is what an over-reach breaches, and stories are
        asserted at zero because the whole corpus of them is authored.
        """
        import conformance as _c  # noqa: PLC0415 - sibling, resolved via the tests path
        repo = Path(__file__).resolve().parents[5]
        bugs_dir = repo / "sdlc-studio" / "bugs"
        self.assertTrue(bugs_dir.is_dir(), f"{bugs_dir} is not the repo's bug corpus - the "
                                           f"root resolved to {repo}, so this census would "
                                           f"measure nothing while reporting green")

        def census(kind: str, dirname: str) -> int:
            n = 0
            for f in sorted((repo / "sdlc-studio" / dirname).glob("*.md")):
                if f.name == "_index.md":
                    continue
                _, why = _c.unit_is_ungroomed(kind, f.read_text(encoding="utf-8"))
                n += (why == "derived-only")
            return n

        bugs = census("bug", "bugs")
        self.assertLess(bugs, 60, f"{bugs} bugs read derived-only - the fix is over-reaching; "
                                  f"it was 13 before and 17 after, measured by two seats")
        self.assertEqual(0, census("story", "stories"),
                         "no story in this corpus carries tool-derived criteria, so any "
                         "story reading derived-only is the pattern eating authored prose")


class ScalarForListTests(unittest.TestCase):
    """BG0610 - a scalar supplied where a list is expected was ITERATED, not stored."""

    def _doc(self, root: Path, **fields) -> Path:
        p = root / "fields.json"
        p.write_text(json.dumps(fields), encoding="utf-8")
        return p

    def test_a_scalar_where_a_list_is_expected_is_refused(self) -> None:
        """MUTANT: in `file_finding._refuse_scalar_for_list`, return without checking.

        `for i, v in enumerate(f.get("verify") or [])` iterates a STRING's characters, so one
        Verify expression became one letter per criterion - the six criteria of a story were
        written with verifiers reading p, y, t, e, s, t - and the command reported success. The
        keys were validated; the types were not."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            doc = self._doc(root, title="probe", acs=["one", "two"], options="a single option")
            with self.assertRaises(ValueError) as caught:
                ff.load_fields_file(doc)
            self.assertIn("options", str(caught.exception))
            self.assertIn("not a list", str(caught.exception))

    def test_a_proper_list_is_accepted(self) -> None:
        """The paired control. The check must refuse a scalar, not every fields-file - a guard
        that refused the documented path would be worse than the defect."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            doc = self._doc(root, title="probe", acs=["one"], options=["a", "b"])
            out = ff.load_fields_file(doc)
            self.assertEqual(["a", "b"], out["options"])

    def test_a_scalar_for_a_scalar_field_is_still_accepted(self) -> None:
        """The second control. The rule is about LIST-valued fields; demanding lists everywhere
        would refuse `title`, `summary` and every other single-value field in the contract."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            doc = self._doc(root, title="a plain string title", acs=["one"])
            self.assertEqual("a plain string title", ff.load_fields_file(doc)["title"])

    def test_both_readers_share_the_rule(self) -> None:
        """MUTANT: apply the check in one caller rather than in the shared loader.

        `artifact.py` and `file_finding.py` read the same contract through the same function,
        so the rule belongs there - a check wired into one caller leaves the other carrying the
        defect, which is how a repair ships half-applied."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            doc = self._doc(root, title="probe", acs="one criterion as a string")
            for allowed in (ff.FIELDS_FILE_KEYS,):
                with self.assertRaises(ValueError) as caught:
                    ff.load_fields_file(doc, allowed)
                self.assertIn("acs", str(caught.exception))


class SeverityVocabularyTests(unittest.TestCase):
    """BG0624: a severity outside the recognised set is REFUSED at the point of filing.

    Both writers of the field carry the vocabulary. Guarding one leaves the class open through
    the other, so "stopping the class beats catching the instance" is a claim only both together
    can make. Refused rather than normalised: guessing what `major` meant would put a word
    nobody chose on the record.
    """

    _SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"

    @staticmethod
    def _ARGV(root, severity):
        return ["file", "--root", str(root), "--type", "bug", "--title", "t",
                "--summary", "s", "--steps", "s", "--fix", "f", "--points", "2",
                "--affects", "a.py", "--severity", severity,
                "--ac", "given x, when y, then z ||| shell true"]

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "schema_version: 3\n", encoding="utf-8")
        (root / "sdlc-studio" / "bugs" / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n", encoding="utf-8")
        return root

    def _run(self, root, severity):
        import subprocess  # noqa: PLC0415
        return subprocess.run(
            [sys.executable, str(self._SCRIPT), *self._ARGV(root, severity)],
            capture_output=True, text=True, timeout=300, check=False)

    def test_an_unrecognised_severity_is_refused_at_filing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            bad = self._run(root, "major")
            self.assertNotEqual(0, bad.returncode, bad.stdout + bad.stderr)
            self.assertIn("major", bad.stdout + bad.stderr)
            # The POSITIVE control, named here rather than inherited from a neighbouring suite:
            # a guard comparing against the wrong set, or case-sensitively, refuses both.
            good = self._run(root, "High")
            self.assertNotIn("invalid choice", good.stdout + good.stderr,
                             "a recognised severity was refused")


if __name__ == "__main__":
    unittest.main()
