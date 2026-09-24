"""US0907: the backlog holds only the work the lean direction still wants.

These tests read THIS repository, as the criteria name it: the disposition record
`sdlc-studio/reviews/backlog-sweep-2026-09-24.md`, the product-seat ruling it cites in
`sdlc-studio/decisions.md`, and the artefacts the record lists. From an installed copy there is
no such workspace, so they skip.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import workspace  # noqa: E402
from lib import sdlc_md  # noqa: E402

_REPO = workspace.REPO
_RECORD_REL = "sdlc-studio/reviews/backlog-sweep-2026-09-24.md"
_DISPOSED = {"SUPERSEDED", "RETIRE", "MERGE"}
_KEPT = {"KEEP-LEAN", "KEEP-VALUE", "UNSURE"}
#: The abandonment outcomes of each type: a sweep rules work out, it never delivers it. An epic
#: is judged separately, because its close is derived from its children.
_RULED_OUT = {
    "story": {"Superseded", "Won't Implement"},
    "bug": {"Superseded", "Won't Fix"},
    "cr": {"Superseded", "Rejected"},
}
_DELIVERED = {"bug": {"Fixed", "Verified", "Closed"}, "cr": {"Complete"}, "epic": {"Done"}}
#: EP0263, the deletion batch whose stories close the items D0264 holds open.
_EP0263 = {f"US{n:04d}" for n in range(909, 927)}
_US0881_AC4 = "tools/tests/test_lean_push.py::PushBoundaryTests::test_a_stale_red_answer_is_re_read"
_ID = re.compile(r"(?:US|BG|CR|EP|RFC)\d{4}")


def _record() -> tuple[str, list[dict]]:
    """(ruling id, one dict per disposition row) read from the committed record."""
    text = (_REPO / _RECORD_REL).read_text(encoding="utf-8")
    ruling = sdlc_md.extract_field(text, "Ruling") or ""
    m = re.match(r"D\d{4}", ruling)
    rows, header = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "ID":
            header = [c.lower() for c in cells]
        elif header and re.fullmatch(_ID, cells[0]):
            rows.append(dict(zip(header, cells)))
    return (m.group(0) if m else ""), rows


def _artefact(rec_id: str) -> tuple[str, str]:
    """(type, text) of the artefact with this id in this repository."""
    found = sdlc_md.find_by_id(_REPO, rec_id)
    if not found:
        raise AssertionError(f"{rec_id} resolves to no artefact")
    path, type_ = found
    return type_, Path(path).read_text(encoding="utf-8")


def _status(text: str) -> str:
    return sdlc_md.extract_field(text, "Status") or ""


def _revision_rows(text: str) -> list[str]:
    """The Change cells of the artefact's Revision History table."""
    _, _, tail = text.partition("## Revision History")
    out = []
    for line in tail.splitlines():
        if line.startswith("## "):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 3 and re.match(r"\d{4}-\d{2}-\d{2}", cells[0]):
            out.append(cells[2])
    return out


def _cites(row: str, ruling: str) -> bool:
    return re.search(rf"\b{ruling}\b", row) is not None


def _children(epic: str) -> list[str]:
    """The stories whose `Epic:` field names this epic."""
    out = []
    for p in sdlc_md.artifact_files("story", _REPO):
        text = p.read_text(encoding="utf-8")
        if re.match(rf"{epic}\b", sdlc_md.extract_field(text, "Epic") or ""):
            out.append(text)
    return out


class BacklogSweepTests(unittest.TestCase):
    def setUp(self) -> None:
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        # One corpus read per test rather than one tree walk per listed item.
        cache = sdlc_md.corpus_cache()
        cache.__enter__()
        self.addCleanup(cache.__exit__, None, None, None)
        self.ruling, self.rows = _record()
        self.assertRegex(self.ruling, r"^D\d{4}$", "the record names no ruling id")
        self.assertTrue(self.rows, "the record lists no dispositions")

    def _sweep_rows(self, rec_id: str, text: str) -> list[str]:
        return [c for c in _revision_rows(text) if _cites(c, self.ruling)]

    def test_every_ruled_item_is_terminal_with_its_reason(self) -> None:
        """MUTANTS: an item left at its old status; a RETIRE story closed Done; a ruled-out epic
        closed Done with no delivered child; a DELIVERED item left open; a sweep row with no
        ruling id or a different reason; a MERGE row or survivor that does not name the other; a
        ruling recorded by another seat or not citing the record."""
        decisions = (_REPO / "sdlc-studio" / "decisions.md").read_text(encoding="utf-8")
        row = next((ln for ln in decisions.splitlines() if ln.startswith(f"| {self.ruling} |")), "")
        self.assertIn("[seat: product]", row, f"{self.ruling} is not a product-seat ruling")
        self.assertIn(_RECORD_REL, row, f"{self.ruling} does not cite the disposition record")
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)), "an item is listed twice")
        ruled = [r for r in self.rows if r["verdict"] in _DISPOSED | {"DELIVERED"}]
        self.assertTrue(ruled)
        for r in ruled:
            with self.subTest(item=r["id"]):
                type_, text = _artefact(r["id"])
                status = _status(text)
                if r["verdict"] == "DELIVERED":
                    self.assertIn(status, _DELIVERED[type_], f"{r['id']} is DELIVERED but reads {status!r}")
                elif type_ == "epic":
                    delivered = any(sdlc_md.is_delivered_terminal("story", _status(c))
                                    for c in _children(r["id"]))
                    self.assertIn(status, {"Superseded", "Done"} if delivered else {"Superseded"},
                                  f"{r['id']} ({r['verdict']}) reads {status!r}")
                else:
                    self.assertIn(status, _RULED_OUT[type_], f"{r['id']} ({r['verdict']}) reads {status!r}")
                if r["action"] == "already terminal":
                    continue  # disposed earlier in the run; the sweep did not touch it
                sweep = self._sweep_rows(r["id"], text)
                self.assertTrue(sweep, f"{r['id']} carries no revision row citing {self.ruling}")
                self.assertTrue(any(r["reason"] in c for c in sweep),
                                f"{r['id']}'s sweep row does not carry its recorded reason")
                self.assertTrue(any(r["verdict"] in c for c in sweep),
                                f"{r['id']}'s sweep row does not name its verdict {r['verdict']}")
                if r["verdict"] == "MERGE":
                    self.assertRegex(r["into"], rf"^{_ID.pattern}$")
                    self.assertTrue(any(f"merged into {r['into']}" in c for c in sweep),
                                    f"{r['id']} does not name {r['into']}, the unit it merged into")
                    _, survivor = _artefact(r["into"])
                    sources = sdlc_md.extract_field(survivor, "Merged from") or ""
                    self.assertIn(r["id"], _ID.findall(sources),
                                  f"{r['into']} does not name {r['id']} as merged into it")

    def test_kept_and_unsure_items_carry_no_sweep_row(self) -> None:
        """MUTANT: the sweep writes its row to a kept or UNSURE item."""
        kept = [r for r in self.rows if r["verdict"] in _KEPT]
        self.assertTrue(kept)
        for r in kept:
            with self.subTest(item=r["id"]):
                _, text = _artefact(r["id"])
                self.assertEqual(self._sweep_rows(r["id"], text), [],
                                 f"{r['id']} is {r['verdict']} but the sweep wrote to its history")

    def test_bg0709_reads_fixed_by_us0881(self) -> None:
        """MUTANTS: BG0709 left Open; its Verify line pointing anywhere but US0881 AC4's test."""
        _, text = _artefact("BG0709")
        self.assertIn(_status(text), {"Fixed", "Verified", "Closed"})
        verifies = re.findall(r"^\s*-\s*\*\*Verify:\*\*\s*(.+?)\s*$", text, re.M)
        self.assertIn(f"pytest {_US0881_AC4}", verifies)
        self.assertIn("US0881", text)
        module, cls, fn = _US0881_AC4.split("::")
        source = (_REPO / module).read_text(encoding="utf-8")
        self.assertIn(f"class {cls}(", source)
        self.assertIn(f"def {fn}(", source)

    def test_held_items_stay_open_naming_their_closing_story(self) -> None:
        """MUTANTS (D0264): a held item closed anyway; its `Closes with:` field missing, naming a
        story outside EP0263, or disagreeing with the record."""
        held = [r for r in self.rows if r["verdict"] == "HELD"]
        self.assertTrue(held)
        for r in held:
            with self.subTest(item=r["id"]):
                type_, text = _artefact(r["id"])
                self.assertFalse(sdlc_md.is_terminal_status(type_, _status(text)),
                                 f"{r['id']} is held open under D0264 but reads {_status(text)!r}")
                m = re.match(r"OPEN - closes with (.+?) \(D0264\)$", r["action"])
                self.assertIsNotNone(m, f"{r['id']}'s record row names no closing story")
                named = _ID.findall(m.group(1))
                self.assertTrue(named and set(named) <= _EP0263, f"{r['id']}: {named} not EP0263 stories")
                field = _ID.findall(sdlc_md.extract_field(text, "Closes with") or "")
                self.assertEqual(field, named, f"{r['id']}'s Closes with field disagrees with the record")


if __name__ == "__main__":
    unittest.main()
