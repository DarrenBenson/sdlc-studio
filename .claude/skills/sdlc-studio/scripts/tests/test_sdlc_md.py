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
conformance = _load("conformance", "conformance.py")
reconcile = _load("reconcile", "reconcile.py")
audit = _load("audit", "audit.py")


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
        # The conformance, reconcile and audit sets are DERIVED from each check's own
        # emission vocabulary, not restated here: a hardcoded answer key would share
        # the registry's blind spot and certify a gap it was meant to catch. So a
        # kind a check can emit but its registry lacks a hint for must redden this
        # guard. integrity has only two, fixed, kinds and no such vocabulary constant,
        # so its set stays explicit.
        expected = {
            "conformance": set(conformance.STAGES),
            "integrity": {"missing-required", "dangling"},
            "audit": set(audit.FINDING_KINDS),
            "reconcile": set(reconcile.DRIFT_KINDS),
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


class ConfigOverrideWarnTests(unittest.TestCase):
    """US0076/CR0180: a present-but-unhonourable .config.yaml warns once, never silently."""

    def test_malformed_config_warns_once(self) -> None:
        import contextlib
        import io
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - the ImportError path warns differently")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = root / "sdlc-studio"
            cfg.mkdir(parents=True)
            (cfg / ".config.yaml").write_text("this: [unterminated\n", encoding="utf-8")  # bad YAML
            sdlc_md._OVERRIDE_WARNED.discard(str(cfg / ".config.yaml"))
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(sdlc_md.project_override(root, "x", "dflt"), "dflt")
                sdlc_md.project_override(root, "y", "dflt")  # second read: no repeat
            out = err.getvalue()
            self.assertIn("was not applied", out)
            self.assertEqual(out.count("was not applied"), 1)  # warn-once

    def test_no_config_is_silent(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                sdlc_md.project_override(Path(d), "x", "dflt")
            self.assertEqual(err.getvalue(), "")


class ConfigParseCacheTests(unittest.TestCase):
    """`project_override` is called once per artefact per lane - 4,495 times in one
    `gate --only validate` over the dev repo - and re-parsed the YAML every time, which made
    PyYAML scanning ~75% of both the validate and constitution lanes. The parse is now memoised
    on the file's CONTENT.

    Content-keying is the whole safety argument: a cache keyed on mtime can serve a stale parse
    when two edits land inside the clock's granularity, and 'the gate passed on a tree it never
    read' is the failure this project keeps finding in other guises. These tests attack the
    staleness directly, not the happy path."""

    def setUp(self) -> None:
        if not _HAS_YAML:
            self.skipTest("PyYAML absent - project_override degrades to defaults")

    def _write(self, root: Path, body: str) -> None:
        cfg = root / "sdlc-studio"
        cfg.mkdir(parents=True, exist_ok=True)
        (cfg / ".config.yaml").write_text(body, encoding="utf-8")

    def test_repeated_reads_of_one_config_parse_it_once(self) -> None:
        import yaml
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a: 1\nb: 2\n")
            sdlc_md.project_override(root, "a")          # prime
            calls = []
            orig = yaml.safe_load
            yaml.safe_load = lambda text: (calls.append(1), orig(text))[1]
            try:
                for _ in range(50):
                    self.assertEqual(sdlc_md.project_override(root, "a"), 1)
                    self.assertEqual(sdlc_md.project_override(root, "b"), 2)
            finally:
                yaml.safe_load = orig
            self.assertEqual(calls, [], "100 reads of an unchanged config re-parsed it")

    def test_an_edited_config_is_never_served_from_cache(self) -> None:
        """The staleness attack. Same path, edited in place, SAME BYTE LENGTH - so an
        mtime-and-size key could collide inside the clock's granularity. Content-keying cannot."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a: 1\n")
            self.assertEqual(sdlc_md.project_override(root, "a"), 1)
            self._write(root, "a: 2\n")      # identical length, immediately after
            self.assertEqual(sdlc_md.project_override(root, "a"), 2)
            self._write(root, "a: 3\n")
            self.assertEqual(sdlc_md.project_override(root, "a"), 3)

    def test_a_deleted_config_stops_being_honoured(self) -> None:
        """A cache that outlived its file would keep answering from a config that is gone."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a: 1\n")
            self.assertEqual(sdlc_md.project_override(root, "a"), 1)
            (root / "sdlc-studio" / ".config.yaml").unlink()
            self.assertEqual(sdlc_md.project_override(root, "a", "dflt"), "dflt")

    def test_a_non_utf8_config_warns_and_degrades_instead_of_raising(self) -> None:
        """Adversarial review, MAJOR: moving the read out of the broad `except` and narrowing it
        to OSError let UnicodeDecodeError - a ValueError - escape. One legacy-encoded byte in a
        consuming project's config turned 7 blocking gate lanes red with a message that never
        named the file. `project_override` is the reader that must NEVER raise."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = root / "sdlc-studio"
            cfg.mkdir(parents=True)
            (cfg / ".config.yaml").write_bytes(b"a: caf\xe9\n")   # latin-1, not UTF-8
            sdlc_md._OVERRIDE_WARNED.discard(str(cfg / ".config.yaml"))
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(sdlc_md.project_override(root, "a", "dflt"), "dflt")
            self.assertIn("was not applied", err.getvalue())

    def test_an_unreadable_config_warns_rather_than_degrading_silently(self) -> None:
        """The same review's second arm: returning the right value without the warning is only
        half right. Silent-default is the exact failure `_warn_unhonoured` exists to prevent, so
        a config that is PRESENT but unreadable must say so."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = root / "sdlc-studio"
            cfg.mkdir(parents=True)
            (cfg / ".config.yaml").mkdir()          # present, but a directory
            sdlc_md._OVERRIDE_WARNED.discard(str(cfg / ".config.yaml"))
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(sdlc_md.project_override(root, "a", "dflt"), "dflt")
            self.assertIn("was not applied", err.getvalue())

    def test_the_cache_is_bounded(self) -> None:
        """Keying on the file BODY retained every distinct config in full for the life of the
        process. The suite alone walks thousands of temp roots."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for n in range(sdlc_md._CONFIG_PARSE_CACHE_MAX + 20):
                self._write(root, f"a: {n}\n")
                self.assertEqual(sdlc_md.project_override(root, "a"), n)
            self.assertLessEqual(len(sdlc_md._CONFIG_PARSE_CACHE),
                                 sdlc_md._CONFIG_PARSE_CACHE_MAX)

    def test_two_projects_do_not_share_a_parse(self) -> None:
        """Keyed by path AND content: two roots whose configs differ must not cross-answer."""
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            r1, r2 = Path(d1), Path(d2)
            self._write(r1, "a: 1\n")
            self._write(r2, "a: 2\n")
            self.assertEqual(sdlc_md.project_override(r1, "a"), 1)
            self.assertEqual(sdlc_md.project_override(r2, "a"), 2)
            self.assertEqual(sdlc_md.project_override(r1, "a"), 1)   # r2 did not evict r1


class UlidIdentityTests(unittest.TestCase):
    """US0055/RFC0024: schema-v3 ULID ids coexist with v2 sequential ids; every id reader
    must parse both eras."""

    def test_new_ulid_is_sortable_and_base32(self) -> None:
        a = sdlc_md.new_ulid()
        b = sdlc_md.new_ulid()
        self.assertEqual(len(a), 26)
        self.assertTrue(set(a) <= set("0123456789ABCDEFGHJKMNPQRSTVWXYZ"))
        self.assertLessEqual(a[:10], b[:10])  # timestamp prefix is monotonic

    def test_short_id_form(self) -> None:
        sid = sdlc_md.short_ulid()
        self.assertEqual(len(sid), 8)
        self.assertTrue(set(sid) <= set("0123456789ABCDEFGHJKMNPQRSTVWXYZ"))

    def test_short_id_carries_randomness(self) -> None:
        # BG0086: short_ulid was the pure timestamp prefix, so 50 rapid calls produced ONE
        # value - two uncoordinated writers in the same ms window minted the same id. The
        # short id must carry random bits so an in-window collision is improbable.
        ids = {sdlc_md.short_ulid() for _ in range(50)}
        self.assertGreater(len(ids), 40, "short_ulid has no in-window entropy")

    def test_short_id_sorts_by_time_and_carries_entropy(self) -> None:
        # BG0086: the 8-char short id must (a) still order by creation time at its coarse
        # prefix resolution and (b) carry real per-id entropy so two writers in the same
        # instant do not mint the same id. A 10ms sleep is far below the ~17-minute prefix
        # bucket, so it never exercises a sort flip - drive the clock explicitly instead.
        from unittest.mock import patch
        # (a) two ids a full prefix-bucket apart sort in creation order
        with patch("time.time", return_value=1_600_000_000.0):
            early = sdlc_md.short_ulid()
        with patch("time.time", return_value=1_600_000_000.0 + 4000):  # +4000s >> 17-min bucket
            late = sdlc_md.short_ulid()
        self.assertLess(early[:6], late[:6])
        # (b) at a FIXED instant the tail still varies - the old pure-timestamp id was
        # constant here (the BG0086 collision), so >1 distinct id proves the entropy landed
        with patch("time.time", return_value=1_600_000_000.0):
            ids = {sdlc_md.short_ulid() for _ in range(50)}
        self.assertGreater(len(ids), 1)
        self.assertTrue(all(len(i) == 8 for i in ids))

    def test_iter_tables_skips_fenced_tables(self) -> None:
        # a `|`-row inside a ``` fence is an illustrative example, never real structure
        text = (
            "# Doc\n\n"
            "| ID | Status |\n| --- | --- |\n| US0001 | Done |\n\n"
            "```\n| ID | Status |\n| --- | --- |\n| FAKE | Done |\n```\n"
        )
        rows = [c for t in sdlc_md.iter_tables(text) for _ln, c in t["rows"]]
        self.assertEqual(rows, [["US0001", "Done"]])
        self.assertFalse(any("FAKE" in " ".join(c) for c in rows))

    def test_iter_tables_resumes_after_fence_closes(self) -> None:
        text = (
            "```\n| ID | X |\n| --- | --- |\n| FENCED | y |\n```\n\n"
            "| ID | Status |\n| --- | --- |\n| US0002 | Done |\n"
        )
        rows = [c for t in sdlc_md.iter_tables(text) for _ln, c in t["rows"]]
        self.assertEqual(rows, [["US0002", "Done"]])

    def test_id_re_matches_both_eras(self) -> None:
        self.assertEqual(sdlc_md.extract_record_id("US0001-login"), "US0001")
        self.assertEqual(sdlc_md.extract_record_id("BG-01JQK3F8-fix-thing"), "BG-01JQK3F8")
        self.assertEqual(sdlc_md.extract_record_id("CR-01JQK3F8XY-x"), "CR-01JQK3F8XY")  # extended suffix
        self.assertIsNone(sdlc_md.extract_record_id("notes-about-things"))

    def test_search_re_finds_both_in_a_cell(self) -> None:
        cell = "| [BG-01JQK3F8](BG-01JQK3F8-fix.md) | [US0001](US0001-x.md) |"
        found = sdlc_md.ID_SEARCH_RE.findall(cell)
        self.assertIn("BG-01JQK3F8", found)
        self.assertIn("US0001", found)

    def test_id_number_is_v2_only(self) -> None:
        self.assertEqual(sdlc_md.id_number("US0042"), 42)
        self.assertEqual(sdlc_md.id_number("CR-0007"), 7)
        # a ULID has no sequential number - even one ending in digits
        self.assertIsNone(sdlc_md.id_number("BG-01JQ1234"))

    def test_norm_id_both_eras(self) -> None:
        self.assertEqual(sdlc_md.norm_id("CR-0007"), "CR0007")
        self.assertEqual(sdlc_md.norm_id("BG-01JQK3F8"), "BG01JQK3F8")

class FindByIdTests(unittest.TestCase):
    """US0102/CR0187: find_by_id + story_epic on the shared layer (alias-aware)."""

    def _story(self, root, sid, epic="EP0001", aliases=None):
        d = root / "sdlc-studio" / "stories"; d.mkdir(parents=True, exist_ok=True)
        al = f"> **Aliases:** {aliases}\n" if aliases else ""
        (d / f"{sid}-x.md").write_text(
            f"# {sid}: s\n\n> **Status:** Draft\n> **Epic:** {epic}\n{al}", encoding="utf-8")

    def test_find_by_id_locates_and_types(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._story(root, "US0001")
            r = sdlc_md.find_by_id(root, "US0001")
            self.assertIsNotNone(r); self.assertEqual(r[1], "story")
            self.assertIsNone(sdlc_md.find_by_id(root, "US9999"))

    def test_find_by_id_resolves_alias(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._story(root, "US0001", aliases="US0042")
            self.assertIsNotNone(sdlc_md.find_by_id(root, "US0042"))   # alias -> canonical

    def test_story_epic_reads_field(self):
        self.assertEqual(sdlc_md.story_epic("# US1: s\n> **Epic:** EP0007\n"), "EP0007")
        self.assertIsNone(sdlc_md.story_epic("# US1: s\n> **Epic:** --\n"))
        self.assertIsNone(sdlc_md.story_epic("# US1: s\n> **Status:** Draft\n"))  # no phantom


# Every character `str.splitlines` treats as a line break, plus NUL - the class that breaks a
# value out of the metadata line, table cell, or bullet a creator writes it into.
LINE_BREAKERS = ("\n", "\r", "\r\n", "\v", "\f", "\x1c", "\x1d", "\x1e",
                 "\x85", "\u2028", "\u2029", "\x00")


class SingleLineRefusalTests(unittest.TestCase):
    """The authorship resolver refuses a multi-line author, so every creator inherits the
    refusal instead of each one escaping separately. A creator that accepted one of these
    would write arbitrary metadata lines on the caller's behalf - the provenance tooling
    forging provenance."""

    def test_authorship_value_refuses_a_newline_author(self):
        # the filed reproduction: --author $'Sam\nEvil: injected' broke out of the
        # `> **Raised-by:**` line and split the Revision History row across two lines
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as cm:
                sdlc_md.authorship_value("Sam\nEvil: injected", Path(d))
            msg = str(cm.exception)
            self.assertIn("author", msg)
            self.assertIn("single line", msg)

    def test_authorship_value_refuses_every_line_breaking_character(self):
        with tempfile.TemporaryDirectory() as d:
            for ch in LINE_BREAKERS:
                with self.subTest(ch=repr(ch)):
                    with self.assertRaises(ValueError):
                        sdlc_md.authorship_value(f"Sam{ch}Evil: injected", Path(d))

    def test_authorship_value_refuses_a_break_in_the_env_identity(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            prev = os.environ.get("SDLC_AUTHOR")
            os.environ["SDLC_AUTHOR"] = "Sam\n> **Status:** Fixed"
            try:
                with self.assertRaises(ValueError) as cm:
                    sdlc_md.authorship_value(None, Path(d))
                self.assertIn("SDLC_AUTHOR", str(cm.exception))
            finally:
                os.environ.pop("SDLC_AUTHOR", None)
                if prev is not None:
                    os.environ["SDLC_AUTHOR"] = prev

    def test_authorship_value_still_accepts_a_legitimate_author(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(sdlc_md.authorship_value("Dani Okafor; agent; v2", Path(d)),
                             "Dani Okafor; agent; v2")
            self.assertEqual(sdlc_md.authorship_value("Sam Eriksson", Path(d)),
                             "Sam Eriksson; human; v1")
            # surrounding whitespace is trimmed, not refused: only an INTERIOR break injects
            self.assertEqual(sdlc_md.authorship_value("\n Sam Eriksson \n", Path(d)),
                             "Sam Eriksson; human; v1")

    def test_require_single_line_names_the_field_and_the_character(self):
        self.assertEqual(sdlc_md.require_single_line("title", "a clean title"), "a clean title")
        with self.assertRaises(ValueError) as cm:
            sdlc_md.require_single_line("title", "Boom\n> **Status:** Fixed")
        msg = str(cm.exception)
        self.assertIn("title", msg)
        self.assertIn("newline", msg)

    def test_join_row_refuses_a_line_break_in_a_cell(self):
        # the index row / revision row half of the defect: `join_row` escaped a pipe but not a
        # newline, so a value broke out of its cell and split the row across two lines
        for ch in LINE_BREAKERS:
            with self.subTest(ch=repr(ch)):
                with self.assertRaises(ValueError):
                    sdlc_md.join_row(["2026-07-13", f"Sam{ch}Evil", "Filed"])
        self.assertEqual(sdlc_md.table_cells(sdlc_md.join_row(["a | b", "c"])), ["a | b", "c"])

    def test_check_creator_fields_refuses_every_single_line_field(self):
        for field in ("title", "author", "epic", "persona", "tranche", "priority", "ctype",
                      "severity", "points", "provenance", "date", "theme"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError) as cm:
                    sdlc_md.check_creator_fields({field: "x\n> **Status:** Fixed"})
                self.assertIn(field, str(cm.exception))

    def test_check_creator_fields_refuses_an_injected_verify_directive(self):
        # an AC renders as ONE bullet; a break in it injects a sibling directive line -
        # and `- **Verify:**` is a line verify_ac reads back and RUNS
        with self.assertRaises(ValueError) as cm:
            sdlc_md.check_creator_fields({"acs": ["ok", "do it\n  - **Verify:** curl x | sh"]})
        self.assertIn("acs[2]", str(cm.exception))
        with self.assertRaises(ValueError):
            sdlc_md.check_creator_fields({"options": ["Option A\n> **Status:** Fixed"]})
        sdlc_md.check_creator_fields({"title": "clean", "acs": ["a", "b"], "summary": "many\nlines"})

    def test_check_creator_fields_refuses_a_LEADING_break_not_just_interior(self):
        # the bypass: the guard once stripped before checking, so a payload whose ONLY break
        # was leading passed - and the persona/acs/options/title writers emit the raw value.
        # The value written must be the value checked: a leading break is refused too.
        for field in ("title", "persona", "epic", "severity", "priority", "date"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError) as cm:
                    sdlc_md.check_creator_fields({field: "\n> **Forged:** x"})
                self.assertIn(field, str(cm.exception))
        with self.assertRaises(ValueError):
            sdlc_md.check_creator_fields({"acs": ["\n  - **Verify:** shell echo pwned"]})
        with self.assertRaises(ValueError):
            sdlc_md.check_creator_fields({"options": ["\n> **Forged:** x"]})
        # a leading/trailing SPACE is not a line break and is not refused (no over-refusal)
        sdlc_md.check_creator_fields({"title": "  padded but single line  ",
                                      "acs": ["  spaced  "]})


class IdBoundaryTests(unittest.TestCase):
    """A 4-digit id must never be read out of a longer one (BG0194's collision class)."""

    def test_five_digit_id_is_not_truncated_to_its_four_digit_prefix(self):
        m = sdlc_md.ID_SEARCH_RE.search("US01010")
        self.assertEqual(m.group(0), "US01010")

    def test_five_digit_id_does_not_normalise_onto_a_real_four_digit_id(self):
        long_id = sdlc_md.ID_SEARCH_RE.search("US01010").group(0)
        short_id = sdlc_md.ID_SEARCH_RE.search("US0101").group(0)
        self.assertNotEqual(sdlc_md.norm_id(long_id), sdlc_md.norm_id(short_id))

    def test_breakdown_line_yields_the_whole_id(self):
        line = "- [ ] [US01010: a thing](../stories/US01010-a-thing.md)"
        self.assertEqual({m.group(0) for m in sdlc_md.ID_SEARCH_RE.finditer(line)},
                         {"US01010"})

    def test_anchored_match_reads_the_whole_id_from_a_filename(self):
        self.assertEqual(sdlc_md.ID_RE.match("US01010-a-thing.md").group(1), "US01010")

    def test_four_digit_ids_are_unchanged(self):
        for raw, want in (("US0101", "US0101"), ("CR-0007", "CR-0007"),
                          ("RFC-0001", "RFC-0001"), ("EP0072", "EP0072")):
            with self.subTest(raw=raw):
                self.assertEqual(sdlc_md.ID_SEARCH_RE.search(raw).group(0), want)

    def test_a_digit_leading_v3_suffix_is_claimed_whole_not_truncated(self):
        # A ULID whose suffix starts with digits and continues into letters is the case
        # the ordering decides: with the v2 alternative first, `-?\\d{4,}` takes `-0123`
        # and the id truncates to `BG-0123`. An all-digit suffix does NOT discriminate -
        # the greedy digit run claims it whole under either order.
        self.assertEqual(sdlc_md.ID_SEARCH_RE.search("BG-0123ABCD").group(0), "BG-0123ABCD")
        self.assertIsNone(sdlc_md.id_number("BG-0123ABCD"))

    def test_an_all_digit_v3_suffix_is_not_read_as_a_sequential_number(self):
        self.assertEqual(sdlc_md.ID_SEARCH_RE.search("BG-01234567").group(0), "BG-01234567")
        self.assertIsNone(sdlc_md.id_number("BG-01234567"))

    def test_id_number_reads_a_long_sequential_id(self):
        # Without this the max+1 allocator cannot see US01010 and would re-mint it.
        self.assertEqual(sdlc_md.id_number("US01010"), 1010)
        self.assertEqual(sdlc_md.id_number("US0101"), 101)

    def test_id_number_still_refuses_a_v3_ulid(self):
        self.assertIsNone(sdlc_md.id_number("BG-01JQK3F8"))


if __name__ == "__main__":
    unittest.main()
