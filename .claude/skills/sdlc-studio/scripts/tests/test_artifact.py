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
            errs = [v for v in validate.validate_file(p, "story", repo) if v["severity"] == "error"]
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
                fields = {"epic": "EP0001"} if t == "story" else {}
                r = artifact.new(repo, t, f"a {t}", fields)
                p = Path(r["path"])
                errs = [v for v in validate.validate_file(p, t, repo) if v["severity"] == "error"]
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
        # HIGH regression: a loose id must not substring-match a padded epic.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo, "EP0010")
            r = artifact.new(repo, "story", "loose ref", {"epic": "EP001"})  # not EP0010
            self.assertFalse(r["epic_linked"])
            self.assertNotIn("loose ref", (repo / "sdlc-studio" / "epics" / "EP0010-x.md").read_text())

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

    def test_index_absent_still_creates(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            r = artifact.new(repo, "bug", "no index here")
            self.assertFalse(r["indexed"])
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
            artifact.close(repo, r["id"], metrics={"iterations": 2, "critic_verdict": "approve"})
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
            artifact.close(repo, r["id"])  # default terminal = Done
            self.assertIn("Done", Path(r["path"]).read_text())


if __name__ == "__main__":
    unittest.main()
