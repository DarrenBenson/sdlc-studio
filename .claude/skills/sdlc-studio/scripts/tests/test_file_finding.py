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

    def test_the_round_trip_filed_then_plannable(self) -> None:
        # THE bug. File it the way the tool now allows, and the planner must accept it - a
        # filed artefact the planner still refuses is not a fix.
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
            self.assertEqual(bd["ungroomed"], [], "the planner refused an artefact the filer wrote")
            self.assertTrue(bd["ok"])

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


if __name__ == "__main__":
    unittest.main()
