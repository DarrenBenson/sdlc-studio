"""Unit tests for scripts/lib/sdlc_md.py and the JSON guards that use it.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def _load(name: str, rel: str):
    """Load a module by file path (mirrors the sibling test modules)."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sdlc_md = _load("sdlc_md", "lib/sdlc_md.py")

try:
    import yaml as _yaml  # noqa: F401
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False
repo_map = _load("repo_map", "repo_map.py")
verify_ac = _load("verify_ac", "verify_ac.py")


class TimeTests(unittest.TestCase):
    def test_now_iso8601_shape(self) -> None:
        ts = sdlc_md.now_iso8601()
        self.assertRegex(ts, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_now_date_shape(self) -> None:
        self.assertRegex(sdlc_md.now_date(), r"^\d{4}-\d{2}-\d{2}$")


class JsonTests(unittest.TestCase):
    def test_loads_valid(self) -> None:
        self.assertEqual(sdlc_md.loads('{"a": 1}', None), {"a": 1})

    def test_loads_empty_and_blank_return_default(self) -> None:
        self.assertEqual(sdlc_md.loads("", []), [])
        self.assertEqual(sdlc_md.loads("   ", {}), {})

    def test_loads_malformed_returns_default(self) -> None:
        self.assertEqual(sdlc_md.loads("not json", "x"), "x")

    def test_read_json_missing_file(self) -> None:
        missing = Path(tempfile.gettempdir()) / "sdlc_md_no_such_file_42.json"
        self.assertEqual(sdlc_md.read_json(missing, {"d": 1}), {"d": 1})

    def test_read_json_valid_and_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            good = Path(d) / "good.json"
            good.write_text('{"k": 2}', encoding="utf-8")
            self.assertEqual(sdlc_md.read_json(good, None), {"k": 2})
            bad = Path(d) / "bad.json"
            bad.write_text("{ broken", encoding="utf-8")
            self.assertIsNone(sdlc_md.read_json(bad, None))


class FieldTests(unittest.TestCase):
    SAMPLE = "# Add login\n\n> **Status:** In Progress\n> **Priority:** P1\n"

    def test_extract_field(self) -> None:
        self.assertEqual(sdlc_md.extract_field(self.SAMPLE, "Status"), "In Progress")
        self.assertEqual(sdlc_md.extract_field(self.SAMPLE, "Priority"), "P1")

    def test_extract_field_absent(self) -> None:
        self.assertIsNone(sdlc_md.extract_field(self.SAMPLE, "Owner"))

    def test_extract_h1_title(self) -> None:
        self.assertEqual(sdlc_md.extract_h1_title(self.SAMPLE), "Add login")
        self.assertIsNone(sdlc_md.extract_h1_title("no heading here"))

    def test_extract_record_id(self) -> None:
        self.assertEqual(sdlc_md.extract_record_id("US0001-login"), "US0001")
        self.assertEqual(sdlc_md.extract_record_id("CR-0001-add-auth"), "CR-0001")
        self.assertEqual(sdlc_md.extract_record_id("RFC-0007-design"), "RFC-0007")
        self.assertEqual(sdlc_md.extract_record_id("EP0042"), "EP0042")
        self.assertIsNone(sdlc_md.extract_record_id("readme"))

    def test_extract_ac_id(self) -> None:
        self.assertEqual(sdlc_md.extract_ac_id("### AC1: Happy path"), ("AC1", "Happy path"))
        self.assertEqual(sdlc_md.extract_ac_id("### AC12"), ("AC12", ""))
        self.assertIsNone(sdlc_md.extract_ac_id("## Not an AC"))


class SlugTests(unittest.TestCase):
    def test_slug(self) -> None:
        self.assertEqual(sdlc_md.slug("In Progress"), "in-progress")
        self.assertEqual(sdlc_md.slug("  Feature/Request!  "), "feature-request")


class WalkGlobTests(unittest.TestCase):
    def test_walk_glob_sorted_and_missing_dir(self) -> None:
        self.assertEqual(sdlc_md.walk_glob(Path("/no/such/dir/xyz"), "*.md"), [])
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "US0002-b.md").write_text("x", encoding="utf-8")
            (base / "US0001-a.md").write_text("x", encoding="utf-8")
            (base / "ignore.txt").write_text("x", encoding="utf-8")
            names = [p.name for p in sdlc_md.walk_glob(base, "US*.md")]
            self.assertEqual(names, ["US0001-a.md", "US0002-b.md"])


class JsonGuardRegressionTests(unittest.TestCase):
    """Closes the review gap: corrupt JSON must exit 2, not traceback."""

    def test_repo_map_query_exits_2_on_corrupt_map(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "repo-map.json"
            bad.write_text("{ not json", encoding="utf-8")
            rc = repo_map.main(["query", "--map", str(bad), "--story", "login"])
            self.assertEqual(rc, 2)

    def test_verify_ac_report_exits_2_on_corrupt_report(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "verify-report.json"
            bad.write_text("{ not json", encoding="utf-8")
            rc = verify_ac.main(["report", "--report", str(bad)])
            self.assertEqual(rc, 2)


class ExtractFieldFlexTests(unittest.TestCase):
    def test_blockquote_and_plain_both_extract(self) -> None:
        self.assertEqual(sdlc_md.extract_field("> **Status:** Done\n", "Status"), "Done")
        self.assertEqual(sdlc_md.extract_field("**Status:** Complete\n", "Status"), "Complete")


class ExtractAcTests(unittest.TestCase):
    def test_heading_form(self) -> None:
        self.assertEqual(sdlc_md.extract_ac_id("### AC1: Login works"), ("AC1", "Login works"))

    def test_bold_bullet_form(self) -> None:
        self.assertEqual(sdlc_md.extract_ac_id("- **AC2:** additive migration")[0], "AC2")
        self.assertEqual(sdlc_md.extract_ac_id("* **AC3** something")[0], "AC3")

    def test_non_ac_returns_none(self) -> None:
        self.assertIsNone(sdlc_md.extract_ac_id("- just a bullet"))


class NormIdTests(unittest.TestCase):
    def test_hyphen_and_case_insensitive(self) -> None:
        self.assertEqual(sdlc_md.norm_id("CR-0001"), "CR0001")
        self.assertEqual(sdlc_md.norm_id("cr0001"), "CR0001")
        self.assertEqual(sdlc_md.norm_id("CR0001"), sdlc_md.norm_id("CR-0001"))


class CanonicalStatusTests(unittest.TestCase):
    VOCAB = ["Proposed", "In Progress", "Done", "Won't Implement"]

    def test_strips_decoration(self) -> None:
        self.assertEqual(sdlc_md.canonical_status("Done (v2.83.0) · **CR:** CR-0088", self.VOCAB), "Done")

    def test_multiword_wins_over_prefix(self) -> None:
        self.assertEqual(sdlc_md.canonical_status("In Progress — crew-half", self.VOCAB), "In Progress")

    def test_exact_and_bold(self) -> None:
        self.assertEqual(sdlc_md.canonical_status("**Done**", self.VOCAB), "Done")

    def test_unrecognised_returns_none(self) -> None:
        self.assertIsNone(sdlc_md.canonical_status("Retired", self.VOCAB))
        self.assertIsNone(sdlc_md.canonical_status(None, self.VOCAB))

    def test_no_partial_word_match(self) -> None:
        # 'Doneish' must not canonicalise to 'Done'.
        self.assertIsNone(sdlc_md.canonical_status("Doneish", self.VOCAB))


class ArtifactFilesTests(unittest.TestCase):
    def test_excludes_index_and_consultations(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0001-real.md").write_text(
                "# EP0001: real\n\n> **Status:** Draft\n", encoding="utf-8")
            (ed / "EP0001-consultations.md").write_text("# x\n", encoding="utf-8")
            (ed / "_index.md").write_text("# x\n", encoding="utf-8")
            names = {p.name for p in sdlc_md.artifact_files("epic", root)}
            self.assertEqual(names, {"EP0001-real.md"})

    def test_statusless_companion_excluded_by_header_not_suffix(self) -> None:
        # a -decisions companion under a shared id is a note, not an artifact:
        # exclusion keys on "carries no artifact header", so no suffix allowlist
        # entry is needed and validate/next_id/gate all agree via this one helper
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0244-ladder-policy.md").write_text(
                "# EP0244: ladder policy\n\n> **Status:** Draft\n", encoding="utf-8")
            (ed / "EP0244-ladder-consultations.md").write_text("notes\n", encoding="utf-8")
            (ed / "EP0244-ladder-decisions.md").write_text(
                "# EP0244 ladder - frozen design decisions\n\n1. three tiers\n",
                encoding="utf-8")
            names = {p.name for p in sdlc_md.artifact_files("epic", root)}
            self.assertEqual(names, {"EP0244-ladder-policy.md"})

    def test_malformed_artifact_with_id_title_still_included(self) -> None:
        # a real artifact that LOST its Status line must stay in the set so
        # validate keeps flagging it - exclusion is "not an artifact", never
        # "any status-less file"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0245-broken.md").write_text(
                "# EP0245: broken artifact\n\nprose only\n", encoding="utf-8")
            names = {p.name for p in sdlc_md.artifact_files("epic", root)}
            self.assertEqual(names, {"EP0245-broken.md"})

    def test_declared_companion_suffix_respected(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - conventions degrade to defaults")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "conventions:\n  companion_suffixes: [consultations, appendix]\n",
                encoding="utf-8")
            # even an appendix that LOOKS like an artifact is excluded once declared
            (ed / "EP0001-real.md").write_text(
                "# EP0001: real\n\n> **Status:** Draft\n", encoding="utf-8")
            (ed / "EP0001-appendix.md").write_text(
                "# EP0001: appendix\n\n> **Status:** Draft\n", encoding="utf-8")
            names = {p.name for p in sdlc_md.artifact_files("epic", root)}
            self.assertEqual(names, {"EP0001-real.md"})


class HouseTemplateTests(unittest.TestCase):
    """Parse a consuming repo's house template (consuming repo A/consuming repo B shapes)."""

    INLINE = "> **Status:** Done (v2.94.0) · **Epic:** EP0088 · **CR:** CR-0092 · **Points:** 3\n"

    def test_extract_field_inline_metadata(self) -> None:
        self.assertEqual(sdlc_md.extract_field(self.INLINE, "Status"), "Done (v2.94.0)")
        self.assertEqual(sdlc_md.extract_field(self.INLINE, "Epic"), "EP0088")
        self.assertEqual(sdlc_md.extract_field(self.INLINE, "CR"), "CR-0092")
        self.assertEqual(sdlc_md.extract_field(self.INLINE, "Points"), "3")

    def test_extract_field_standalone_still_works(self) -> None:
        self.assertEqual(sdlc_md.extract_field("> **Status:** Done\n", "Status"), "Done")
        self.assertEqual(sdlc_md.extract_field("**Epic:** [EP0001: x](../e/EP0001-x.md)\n", "Epic"),
                         "[EP0001: x](../e/EP0001-x.md)")
        self.assertIsNone(sdlc_md.extract_field("> **Status:** Done\n", "Epic"))

    def test_ac_bullet_accepts_checkbox(self) -> None:
        m = sdlc_md.AC_BULLET_RE.match("- [ ] **AC1** A header badge renders the summary")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "AC1")
        # the existing colon style still matches
        self.assertIsNotNone(sdlc_md.AC_BULLET_RE.match("- **AC2:** does a thing"))

    def test_verify_accepts_dashless(self) -> None:
        self.assertIsNotNone(sdlc_md.VERIFY_RE.match("**Verify:** unit/component test for the shell"))
        self.assertIsNotNone(sdlc_md.VERIFY_RE.match("- **Verify:** pytest x"))  # dashed still works

    def test_verified_accepts_dashless(self) -> None:
        self.assertIsNotNone(sdlc_md.VERIFIED_RE.match("**Verified:** yes (2026-06-20)"))
        self.assertIsNotNone(sdlc_md.VERIFIED_RE.match("- **Verified:** no"))


class RemediationTests(unittest.TestCase):
    def test_lines_for_present_kinds_in_registry_order(self) -> None:
        lines = sdlc_md.remediation_lines("conformance", {"critiqued", "decomposed"})
        self.assertEqual([l.split(" ->")[0] for l in lines], ["decomposed", "critiqued"])
        self.assertTrue(all(" -> " in l for l in lines))

    def test_absent_kind_yields_no_line(self) -> None:
        self.assertEqual(sdlc_md.remediation_lines("integrity", {"not-a-kind"}), [])

    def test_unknown_check_is_empty(self) -> None:
        self.assertEqual(sdlc_md.remediation_lines("nope", {"dangling"}), [])

    def test_registry_covers_every_emitted_finding_kind(self) -> None:
        # Contract: each check's registry keys are exactly the finding-kinds it can
        # emit, and every hint is non-empty - so adding a finding-kind without a
        # hint (or emptying one) fails here instead of silently giving no guidance.
        expected = {
            "conformance": {"decomposed", "specified", "verifiable", "verified", "reconciled", "critiqued"},
            "integrity": {"missing-required", "dangling"},
            "audit": {"weak-AC", "unmet-deps", "already-terminal", "link-integrity", "underspecified", "not-found"},
            "reconcile": {"status-mismatch", "missing-row", "orphan-row", "missing-index", "count-mismatch"},
        }
        for check, kinds in expected.items():
            reg = sdlc_md.REMEDIATION[check]
            self.assertEqual(set(reg), kinds, f"{check} registry keys drift from its finding-kinds")
            for k, hint in reg.items():
                self.assertTrue(hint.strip(), f"{check}.{k} has an empty hint")


class TableCellsTests(unittest.TestCase):
    """The shared escaped-pipe-aware splitter (BG0021)."""

    def test_escaped_pipe_does_not_shift_columns(self) -> None:
        cells = sdlc_md.table_cells(r"| EP0230 | `All\|Crew` match | Done |")
        self.assertEqual(cells, ["EP0230", "`All|Crew` match", "Done"])

    def test_plain_row(self) -> None:
        self.assertEqual(sdlc_md.table_cells("| a | b | c |"), ["a", "b", "c"])

    def test_separator_and_non_table_are_none(self) -> None:
        self.assertIsNone(sdlc_md.table_cells("| --- | :--: |"))
        self.assertIsNone(sdlc_md.table_cells("not a table row"))


class StatusVocabTests(unittest.TestCase):
    """Base vocab + per-project config extension (CR0027)."""

    def test_blocked_in_base_story_vocab(self) -> None:
        self.assertIn("Blocked", sdlc_md.status_vocab("story"))

    def test_no_root_or_no_config_returns_base(self) -> None:
        base = sdlc_md.status_vocab("story")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(sdlc_md.status_vocab("story", Path(d)), base)

    @unittest.skipUnless(_HAS_YAML, "config extension needs PyYAML")
    def test_project_extension_adds_without_replacing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "status_vocab:\n  story:\n    - Gated\n", encoding="utf-8")
            v = sdlc_md.status_vocab("story", root)
            self.assertIn("Gated", v)
            self.assertIn("Done", v)  # base preserved

    def test_malformed_config_degrades_to_base(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(": : not yaml :", encoding="utf-8")
            self.assertEqual(sdlc_md.status_vocab("story", root), sdlc_md.status_vocab("story"))

    @unittest.skipUnless(_HAS_YAML, "config read needs PyYAML")
    def test_type_confused_override_degrades_to_base(self) -> None:
        base = sdlc_md.status_vocab("story")
        for body in (
            "status_vocab:\n  story: Gated\n",   # value a string, not a list
            "- a\n- b\n",                          # whole config a list, not a dict
            "status_vocab: []\n",                  # status_vocab a list, not a dict
        ):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / "sdlc-studio").mkdir()
                (root / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")
                self.assertEqual(sdlc_md.status_vocab("story", root), base, body)



class RowAndHeaderTests(unittest.TestCase):
    def test_row_from_header_rfc_cells_under_named_columns(self):
        hdr = ["ID", "Title", "Priority", "Status", "Author", "Date", "Spawned CRs"]
        row = sdlc_md.row_from_header(hdr, "[RFC-0001](x.md)", "a title", "Draft",
                                      {"priority": "High", "author": "me", "date": "2026-06-21"})
        self.assertEqual(sdlc_md.table_cells(row),
                         ["[RFC-0001](x.md)", "a title", "High", "Draft", "me", "2026-06-21", "--"])

    def test_row_from_header_cr_cells_under_named_columns(self):
        hdr = ["ID", "Title", "Status", "Priority", "Type", "Date", "Linked Epics"]
        row = sdlc_md.row_from_header(hdr, "[CR-0001](x.md)", "t", "Proposed",
                                      {"priority": "High", "ctype": "Improvement", "date": "2026-06-21"})
        self.assertEqual(sdlc_md.table_cells(row),
                         ["[CR-0001](x.md)", "t", "Proposed", "High", "Improvement", "2026-06-21", "--"])

    def test_find_data_header_skips_summary_table(self):
        lines = ["| Status | Count |", "| --- | --- |", "| Open | 1 |", "",
                 "| ID | Title | Status |", "| --- | --- | --- |"]
        idx, cells = sdlc_md.find_data_header(lines)
        self.assertEqual((idx, cells), (4, ["ID", "Title", "Status"]))
        self.assertIsNone(sdlc_md.find_data_header(["| Status | Count |", "| Open | 1 |"]))

    def test_join_row_round_trips_pipe(self):
        self.assertEqual(sdlc_md.table_cells(sdlc_md.join_row(["a | b", "c"])), ["a | b", "c"])


class ParseCutoffTests(unittest.TestCase):
    """One shared adoption-cutoff parser: accepts a bare int OR a prefixed id, returns
    the numeric id, and fails loud on garbage (BG0039, lesson LL0008)."""

    def test_bare_int_parses(self):
        self.assertEqual(sdlc_md.parse_cutoff(57), 57)
        self.assertEqual(sdlc_md.parse_cutoff(103), 103)

    def test_bare_int_string_parses(self):
        self.assertEqual(sdlc_md.parse_cutoff("57"), 57)
        self.assertEqual(sdlc_md.parse_cutoff("103"), 103)

    def test_prefixed_id_parses(self):
        self.assertEqual(sdlc_md.parse_cutoff("US0103"), 103)
        self.assertEqual(sdlc_md.parse_cutoff("CR0103"), 103)
        self.assertEqual(sdlc_md.parse_cutoff("US-0103"), 103)

    def test_none_returns_none(self):
        # An absent cutoff is a legitimate "no cutoff", not an error.
        self.assertIsNone(sdlc_md.parse_cutoff(None))

    def test_unparseable_raises_clear_error(self):
        # LL0008: a typo must fail loud, never silently disable the gate (return None).
        for bad in ("oops", "US", "abc", ""):
            with self.assertRaises(ValueError) as cm:
                sdlc_md.parse_cutoff(bad)
            self.assertIn("adopt_after", str(cm.exception).lower())  # message names the key
            self.assertIn(str(bad), str(cm.exception))  # message echoes the offending value


class IterTablesTests(unittest.TestCase):
    """The ONE structural table iterator every parser shares - boundaries are
    structural (header + separator, any dash count; a heading ends the table),
    with an optional caller predicate for legacy vocabulary headers."""

    DOC = (
        "# Title\n\n"
        "| loose | row |\n\n"                                  # header-less block
        "## Summary\n\n"
        "| Status | Count |\n|--|--|\n| Open | 2 |\n\n"      # short-dash separators
        "## All\n\n"
        "| ID | Title | Status |\n| --- | --- | --- |\n"
        "| US0001 | a | Done |\n| US0002 | b | Open |\n\n"
        "## Dependencies\n\n"
        "| CR | Depends On | Dependency Status |\n| --- | --- | --- |\n"
        "| CR-0001 | CR-0002 | Done |\n\n"
        "## Revision History\n\n"
        "| Date | Author | Change |\n| --- | --- | --- |\n"
        "| 2026-07-04 | Sam | Filed |\n"
    )

    def test_structural_tables_and_boundaries(self) -> None:
        tables = list(sdlc_md.iter_tables(self.DOC))
        headers = [t["header"] for t in tables]
        self.assertIsNone(headers[0])                       # leading header-less block
        self.assertEqual(headers[1], ["Status", "Count"])   # short-dash separator counts
        self.assertEqual(headers[2], ["ID", "Title", "Status"])
        self.assertEqual(headers[3], ["CR", "Depends On", "Dependency Status"])
        self.assertEqual(headers[4], ["Date", "Author", "Change"])
        # rows stay in their own table: the Dependencies row never joins All
        self.assertEqual([c[0] for _, c in tables[2]["rows"]], ["US0001", "US0002"])
        self.assertEqual([c[0] for _, c in tables[3]["rows"]], ["CR-0001"])

    def test_heading_ends_a_table(self) -> None:
        doc = ("| ID | Status |\n| --- | --- |\n| US0001 | Done |\n"
               "## Notes\n| US0002 | stray |\n")
        tables = list(sdlc_md.iter_tables(doc))
        self.assertEqual(len(tables), 2)
        self.assertEqual(len(tables[0]["rows"]), 1)          # US0002 is NOT in table 0
        self.assertIsNone(tables[1]["header"])               # stray block is header-less

    def test_vocabulary_predicate_opens_a_table(self) -> None:
        # legacy: a header row without a separator, recognised by the caller's rule
        doc = "| ID | Title | Status |\n| US0001 | a | Done |\n"
        no_pred = list(sdlc_md.iter_tables(doc))
        self.assertIsNone(no_pred[0]["header"])              # structurally header-less
        pred = lambda cells: len(cells) > 2 and "status" in [c.lower() for c in cells]
        with_pred = list(sdlc_md.iter_tables(doc, header_predicate=pred))
        self.assertEqual(with_pred[0]["header"], ["ID", "Title", "Status"])
        self.assertEqual(len(with_pred[0]["rows"]), 1)

    def test_row_line_numbers_are_one_based(self) -> None:
        doc = "| ID |\n| --- |\n| US0001 |\n"
        t = next(iter(sdlc_md.iter_tables(doc)))
        self.assertEqual(t["rows"][0][0], 3)


if __name__ == "__main__":
    unittest.main()
