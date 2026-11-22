"""BG1700: `critic.py show` walks the artefact tree a fixed number of times, not per row.

Every ledger row bound to an issued verdict file names its unit's folder through
`sdlc_md.display_id`, which reaches `find_by_id`, and outside a corpus cache `find_by_id` walks
every artefact type on each call. `cmd_show` asks twice per row (once for the label, once inside
`verdict_file_state`), so this repository's ledger of some two thousand rows walked the tree
about four thousand times and the listing took minutes. The listing now runs inside
`sdlc_md.corpus_cache()`, as `critic.brief` does, so the tree is walked once per artefact type.

The walk is counted at `sdlc_md._walk_artifact_files`, the one unmemoised walk, never timed: a
count does not move with the load on the host.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
sdlc_md = critic.sdlc_md

#: Three units, one with a v3 id whose file spelling (`US-01ABCDEF`) is not its ledger key
#: (`US01ABCDEF`), so a display id read from the wrong unit names the wrong folder.
UNITS = ("US0001", "US0002", "US-01ABCDEF")
#: Each row's file state, by position in a unit's rows: the file as recorded, edited since,
#: and never written.
STATES = ("unchanged", "changed", "missing")


def _story(root: Path, uid: str) -> None:
    path = root / "sdlc-studio" / "stories" / f"{uid}-the-widget.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {uid}: the widget\n\n> **Status:** Review\n> **Points:** 1\n",
                    encoding="utf-8")


def _project(root: Path, rows_per_state: int) -> list[dict]:
    """The three units' stories, and a ledger of `rows_per_state` rows per unit and state, each
    bound to its own issued file; returns what each row should read as, in ledger order."""
    for uid in UNITS:
        _story(root, uid)
    ledger = critic.verdicts_path(root)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    lines, want = [critic.HEADER.rstrip("\n")], []
    for n in range(rows_per_state):
        for uid in UNITS:
            key = sdlc_md.norm_id(uid)
            for state in STATES:
                name = f"{n:03d}{state[:2]}-0000.txt"
                rel = f"sdlc-studio/reviews/verdicts/{uid}/{name}"
                data = f"VERDICT: APPROVE\n{key} {state} {n}\n".encode()
                digest = critic.source_cell(name, data).split()[0]
                if state != "missing":
                    path = root / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data if state == "unchanged" else data + b"edited\n")
                date = f"2026-11-{1 + n % 28:02d}"
                lines.append(f"| {key} | APPROVE | qa-seat | eng-seat | {date} | - | full | "
                             f"{digest} {name} | - |")
                want.append({"unit": key, "date": date, "file": rel, "state": state})
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return want


def _show(root: Path, *argv: str) -> tuple[int, str, int]:
    """`critic.py show` in-process: its exit code, its stdout and how often it walked the tree."""
    walks = []
    real = sdlc_md._walk_artifact_files

    def counted(*args, **kwargs):
        walks.append(args[0] if args else kwargs.get("type_"))
        return real(*args, **kwargs)

    out = io.StringIO()
    with unittest.mock.patch.object(sdlc_md, "_walk_artifact_files", counted), \
            contextlib.redirect_stdout(out):
        rc = critic.main(["show", *argv, "--root", str(root)])
    return rc, out.getvalue(), len(walks)


class CriticShowScalesTests(unittest.TestCase):

    def test_a_ledger_ten_times_longer_walks_the_tree_no_more_often(self) -> None:
        """AC1. Mutant: the listing outside `corpus_cache()`, so each row's display id walks
        every artefact type (twice a row), and the long ledger walks ten times as often as the
        short one. Held for the text listing and the JSON one, which share the reader."""
        for fmt in ((), ("--format", "json")):
            with self.subTest(format=fmt or "text"):
                counts = {}
                for size in (1, 10):
                    with tempfile.TemporaryDirectory() as d:
                        root = Path(d)
                        rows = _project(root, size)
                        rc, out, counts[size] = _show(root, *fmt)
                        self.assertEqual(0, rc)
                        self.assertEqual(len(rows), len(out.splitlines()) if not fmt
                                         else len(json.loads(out)))
                self.assertEqual(counts[1], counts[10],
                                 f"the walks grew with the ledger: {counts}")
                self.assertLessEqual(counts[10], len(sdlc_md.ARTIFACT_TYPES),
                                     f"more than one walk per artefact type: {counts}")
                self.assertGreater(counts[10], 0, "premise: the display id reads the tree")

    def test_the_cache_is_closed_when_show_returns(self) -> None:
        """The cache's window is the listing: a memo left open past `show` would serve a later
        writer in the same process its stale corpus."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, 1)
            self.assertFalse(sdlc_md.corpus_cache_active())
            _show(root)
            self.assertFalse(sdlc_md.corpus_cache_active(), "show left the corpus cache open")

    def test_one_unit_shown_reads_inside_the_cache(self) -> None:
        """`show --unit` reads its verdict under the same window, and still answers."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, 2)
            seen = []
            real = critic.verdict_for

            def watched(*args, **kwargs):
                seen.append(sdlc_md.corpus_cache_active())
                return real(*args, **kwargs)

            with unittest.mock.patch.object(critic, "verdict_for", watched):
                rc, out, _walks = _show(root, "--unit", "US0002")
                self.assertEqual(0, rc)
                self.assertIn("US0002", out)
                rc, out, _walks = _show(root, "--unit", "US0002", "--format", "json")
                self.assertEqual("US0002", json.loads(out)["unit"])
            self.assertEqual([True, True], seen, "show --unit read outside the corpus cache")


class CriticShowOutputUnchangedTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.want = _project(self.root, 2)

    def test_each_text_row_reads_its_own_unit_label_file_and_state(self) -> None:
        """AC2, text. Mutants: a cached display id naming another unit's folder (the v3 unit's
        rows would name `US0001` or `US0002`); a state computed from a stale path."""
        rc, out, _walks = _show(self.root)
        self.assertEqual(0, rc)
        notes = {"unchanged": "", "changed": " (changed since it was recorded)",
                 "missing": " (missing)"}
        expected = [f"{w['unit']} APPROVE ({w['date']}) {critic.ISSUED_SOURCE}: {w['file']}"
                    f"{notes[w['state']]}" for w in self.want]
        self.assertEqual(expected, out.splitlines())

    def test_each_json_row_reads_its_own_unit_label_file_and_state(self) -> None:
        """AC2, JSON: the same fields on each row, in ledger order."""
        rc, out, _walks = _show(self.root, "--format", "json")
        self.assertEqual(0, rc)
        got = [{"unit": r["unit"], "date": r["date"], "file": r["verdict_file"],
                "state": r["verdict_file_state"], "provenance": r["provenance"]}
               for r in json.loads(out)]
        self.assertEqual([{**w, "provenance": critic.ISSUED_SOURCE} for w in self.want], got)

    def test_a_transcribed_row_still_names_no_file(self) -> None:
        """A row naming no file reads as transcribed with no state, inside the cache as out."""
        ledger = critic.verdicts_path(self.root)
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write("| US0001 | REJECT | qa-seat | eng-seat | 2026-11-20 | - | full | - | "
                     "[new] a |\n")
        rc, out, _walks = _show(self.root)
        self.assertEqual(f"US0001 REJECT (2026-11-20) {critic.TRANSCRIBED_SOURCE}",
                         out.splitlines()[-1])
        rows = json.loads(_show(self.root, "--format", "json")[1])
        self.assertEqual((None, None), (rows[-1]["verdict_file"], rows[-1]["verdict_file_state"]))


if __name__ == "__main__":
    unittest.main()
