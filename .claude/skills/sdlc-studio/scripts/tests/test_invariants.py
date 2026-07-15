"""US0064/CR0185: cross-script invariant tier - the cascade seams the RV0006 review found
unguarded. Each invariant is written to the contract, so it fails on the pre-fix behaviour
(BG0053/BG0060/BG0066) and passes now.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


artifact = _load("artifact")
reconcile = _load("reconcile")
next_id = _load("next_id")
file_finding = _load("file_finding")
telemetry = _load("telemetry")


def _index(repo: Path, type_: str, header: str) -> None:
    d = repo / sdlc_md.ARTIFACT_TYPES[type_][0]
    d.mkdir(parents=True, exist_ok=True)
    ncols = header.count("|") - 1
    sep = "| " + " | ".join(["---"] * ncols) + " |"
    (d / "_index.md").write_text(
        "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 0 |\n"
        "| Proposed | 0 |\n| Draft | 0 |\n| **Total** | **0** |\n\n## All\n\n" + header + "\n" + sep + "\n",
        encoding="utf-8")


def _epic(repo: Path) -> None:
    d = repo / "sdlc-studio" / "epics"; d.mkdir(parents=True, exist_ok=True)
    (d / "EP0001-x.md").write_text(
        "# EP0001: x\n\n> **Status:** Draft\n\n## Story Breakdown\n\n_No stories yet._\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n", encoding="utf-8")


class CascadeInvariants(unittest.TestCase):
    def test_close_emits_exactly_one_telemetry_record(self) -> None:
        # BG0053 seam: transition records on entering terminal; close must not double.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "story", "| ID | Title | Status | Epic | Created | Updated |")
            _epic(repo)
            r = artifact.new(repo, "story", "x", {"epic": "EP0001"})
            artifact.close(repo, r["id"], force=True)
            # one close of THIS artefact = exactly one telemetry record for its id (an epic that
            # auto-completes as a side effect legitimately records its own separate event).
            recs = [x for x in telemetry.read_all(repo)
                    if sdlc_md.norm_id(x.get("id", "")) == sdlc_md.norm_id(r["id"])]
            self.assertEqual(len(recs), 1)

    def test_new_then_reconcile_is_zero_drift(self) -> None:
        # create -> index -> count invariant across representative types.
        cases = {
            "bug": "| ID | Title | Status | Severity | Created | Updated |",
            "cr": "| ID | Title | Status | Priority | Type | Date | Linked Epics |",
        }
        for type_, header in cases.items():
            with tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                _index(repo, type_, header)
                # a delivery unit (bug) is sized in points; a request (cr) in a T-shirt Size
                groom = ({"affects": "src/thing.py", "points": 3} if type_ == "bug"
                         else {"affects": "src/thing.py", "size": "M"} if type_ == "cr"
                         else {})   # a unit must be plannable
                artifact.new(repo, type_, f"a {type_}", groom)
                self.assertEqual(reconcile.detect_type(type_, repo)["drift"], [],
                                 f"{type_}: new-then-reconcile drifted")

    def test_cli_allocate_equals_library(self) -> None:
        # BG0060 seam: the allocate CLI must agree with allocate_number (one authority).
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            sd = repo / "sdlc-studio" / "change-requests"; sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# I\n\n## All\n\n| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| [CR-0005](CR0005-x.md) | gone | Complete | Low | X | 2026-01-01 | - |\n",
                encoding="utf-8")  # lingering row, file absent
            buf = io.StringIO()
            with redirect_stdout(buf):
                next_id.main(["allocate", "--type", "cr", "--root", str(repo), "--format", "json"])
            cli = json.loads(buf.getvalue())["next_id"]
            lib = f"CR{next_id.allocate_number('cr', repo, remote=False):04d}"
            self.assertEqual(cli, lib)

    def test_append_lands_in_master_for_a_multiview_index(self) -> None:
        # BG0066 seam: a trailing link-first view table must not capture the appended row.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            sd = repo / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            idx = sd / "_index.md"
            idx.write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Done | 1 |\n\n"
                "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | one | Done |\n\n"
                "## Recently\n\n| Story | Status |\n| --- | --- |\n| [US0001](US0001-x.md) | Done |\n",
                encoding="utf-8")
            file_finding.append_index_row(repo, "story", "| [US0002](US0002-y.md) | two | Draft |")
            lines = idx.read_text(encoding="utf-8").splitlines()
            all_i = lines.index("## All")
            view_i = lines.index("## Recently")
            new_i = [i for i, ln in enumerate(lines) if "US0002" in ln]
            self.assertTrue(new_i and all(all_i < i < view_i for i in new_i))


    def test_apply_appends_missing_row_into_a_dated_index(self) -> None:
        # BG0071 seam: the self-heal path must not crash on the shipped dated index shapes.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            bd = repo / "sdlc-studio" / "bugs"
            (bd / "BG0001-lost-row.md").write_text(
                "# BG0001: lost row\n\n> **Status:** Open\n> **Severity:** Low\n",
                encoding="utf-8")  # file exists, index row missing
            reconcile.apply_type("bug", repo)  # pre-fix: KeyError 'date'
            self.assertEqual(reconcile.detect_type("bug", repo)["drift"], [])
            self.assertIn("BG0001", (bd / "_index.md").read_text(encoding="utf-8"))

    def test_row_from_header_defaults_every_absent_field(self) -> None:
        # BG0071 unit: an empty fields dict must yield placeholders, never KeyError.
        row = sdlc_md.row_from_header(
            ["ID", "Title", "Status", "Severity", "Created", "Updated"],
            "[BG0001](BG0001-x.md)", "x", "Open", {})
        self.assertIn("| -- |", row)


if __name__ == "__main__":
    unittest.main()
