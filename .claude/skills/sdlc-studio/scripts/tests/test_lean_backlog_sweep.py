"""US0907: the backlog holds only the work the lean direction still wants.

BG0772: a held item closes when, and only when, every story its `Closes with:` field names is
Done; the ten holds on the mutation ledger name US0936, which carries the ledger's deletion.

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
import reconcile  # noqa: E402

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
#: EP0263 is the deletion batch whose stories close the items D0264 holds open. Its set is read
#: from each story's `Epic:` field (`_children`), because stories join it after the sweep.
_EP0263 = "EP0263"
#: BG0772 AC2: the holds whose code is the mutation ledger, which US0936 deletes (US0921 did not).
_LEDGER_HOLDS = ("CR0554", "CR0556", "EP0241", "EP0242", "US0731",
                 "US0793", "US0794", "US0795", "US0796", "US0800")
#: BG0772 AC3: the holds whose closing stories were Done when BG0772 closed them.
_DUE_HOLDS = ("BG0679", "BG0683", "BG0684", "BG0685", "BG0693", "BG0697", "BG0698",
              "CR0543", "CR0555", "CR0558", "CR0582", "CR0583",
              "US0682", "US0683", "US0685", "US0686", "US0687", "US0689", "US0690",
              "US0733", "US0801", "US0802", "US0803", "EP0218", "EP0243")
#: The wording of the revision row BG0772's commands write on each due hold as it closes.
_CLOSING_ROW = "Superseded under D0264"
_HOLD_ACTION = re.compile(r"OPEN - closes with (.+?) \(D0264\)$")
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


def _children(epic: str) -> dict[str, str]:
    """{story id: text} of the stories whose `Epic:` field names this epic."""
    out = {}
    for p in sdlc_md.artifact_files("story", _REPO):
        text = p.read_text(encoding="utf-8")
        if re.match(rf"{epic}\b", sdlc_md.extract_field(text, "Epic") or ""):
            out[sdlc_md.extract_record_id(p.stem)] = text
    return out


def _closes_with(text: str) -> list[str]:
    """The story ids an artefact's `Closes with:` field names, in order."""
    return _ID.findall(sdlc_md.extract_field(text, "Closes with") or "")


def _field_faults(row: dict, text: str, ep0263: set[str]) -> list[str]:
    """BG0772 AC4 (US0907 AC4): a held row names its EP0263 closing stories and the artefact's
    `Closes with:` field names the same ones, in the same order."""
    m = _HOLD_ACTION.match(row["action"])
    if m is None:
        return [f"{row['id']}'s record row names no closing story"]
    named = _ID.findall(m.group(1))
    faults = []
    if not named or not set(named) <= ep0263:
        faults.append(f"{row['id']}: {named} not EP0263 stories")
    field = _closes_with(text)
    if field != named:
        faults.append(f"{row['id']}'s Closes with field {field} disagrees with the record {named}")
    return faults


def _close_faults(rec_id: str, type_: str, text: str, story_status) -> list[str]:
    """BG0772 AC1 (D0264): a held item may read terminal only once every story its `Closes
    with:` field names is Done. `story_status` maps a story id to its status."""
    status = _status(text)
    if not sdlc_md.is_terminal_status(type_, status):
        return []
    named = _closes_with(text)
    if not named:
        return [f"{rec_id} reads {status!r} but its Closes with field names no story"]
    return [f"{rec_id} is held open under D0264 but reads {status!r} while {s} is "
            f"{story_status(s)!r}" for s in named if story_status(s) != "Done"]


def _index_status(path: Path) -> str:
    """The Status cell of this artefact's row in its type's `_index.md`, or '' when absent."""
    col = None
    for line in (path.parent / "_index.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "ID" and "Status" in cells:
            col = cells.index("Status")
        elif col is not None and f"]({path.name})" in line:
            return cells[col]
    return ""


def _probe(status: str, closes_with: str | None) -> str:
    """A minimal artefact text for the rule probes; `None` leaves the field out."""
    field = "" if closes_with is None else f"> **Closes with:** {closes_with}\n"
    return f"# BG9999: probe\n\n> **Status:** {status}\n{field}"


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
                                    for c in _children(r["id"]).values())
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

    def _held(self) -> list[dict]:
        held = [r for r in self.rows if r["verdict"] == "HELD"]
        self.assertTrue(held)
        return held

    def _story_status(self, story: str) -> str:
        return _status(_artefact(story)[1])

    def test_held_items_stay_open_naming_their_closing_story(self) -> None:
        """BG0772 AC4. MUTANTS (D0264): a held item's `Closes with:` field missing, naming a
        story outside EP0263, or disagreeing with the record; each probe below must be refused."""
        ep0263 = set(_children(_EP0263))
        row = {"id": "BG9999", "action": "OPEN - closes with US0909 (D0264)"}
        self.assertEqual(_field_faults(row, _probe("Open", "US0909 (D0264)"), ep0263), [])
        for why, probe, rec in (
                ("field missing", _probe("Open", None), row),
                ("field disagreeing with the record", _probe("Open", "US0914 (D0264)"), row),
                ("story outside EP0263", _probe("Open", "US0881 (D0264)"),
                 {"id": "BG9999", "action": "OPEN - closes with US0881 (D0264)"}),
                ("record row naming no story", _probe("Open", "US0909"),
                 {"id": "BG9999", "action": "untouched"}),
                ("record row naming no story id", _probe("Open", "TBD (D0264)"),
                 {"id": "BG9999", "action": "OPEN - closes with TBD (D0264)"})):
            with self.subTest(probe=why):
                self.assertTrue(_field_faults(rec, probe, ep0263), f"a held item with its {why} passed")
        for r in self._held():
            with self.subTest(item=r["id"]):
                _, text = _artefact(r["id"])
                self.assertEqual(_field_faults(r, text, ep0263), [])

    def test_a_hold_closes_only_after_its_story_ships(self) -> None:
        """BG0772 AC1. MUTANTS: the non-terminal assertion deleted for every held item, which lets
        a hold close while the code it names still ships (D0264); any terminal story read as
        shipped; only the first or the last named story checked."""
        for unshipped in ("Draft", "In Progress", "Blocked", "Won't Implement", "Superseded"):
            ledger = {"US0909": "Done", "US0914": unshipped}.get
            for status, field in (("Superseded", "US0914"), ("Superseded", "US0909, US0914"),
                                  ("Superseded", "US0914, US0909"), ("Won't Fix", "US0914")):
                with self.subTest(probe=f"{status} on {field}, US0914 {unshipped}"):
                    faults = _close_faults("BG9999", "bug", _probe(status, field), ledger)
                    self.assertTrue(faults, f"a hold reading {status} while US0914 is {unshipped} passed")
                    self.assertTrue(all("BG9999" in f for f in faults), faults)
                    self.assertTrue(any(f"US0914 is {unshipped!r}" in f for f in faults), faults)
                    self.assertFalse(any("US0909" in f for f in faults), faults)
        ledger = {"US0909": "Done", "US0914": "Draft"}.get
        self.assertEqual(_close_faults("BG9999", "bug", _probe("Superseded", "US0909"), ledger), [])
        self.assertEqual(_close_faults("BG9999", "bug", _probe("Open", "US0914"), ledger), [])
        for r in self._held():
            with self.subTest(item=r["id"]):
                type_, text = _artefact(r["id"])
                self.assertEqual(_close_faults(r["id"], type_, text, self._story_status), [])

    def test_ledger_holds_name_us0936(self) -> None:
        """BG0772 AC2. MUTANT: AC1 landed alone, so the ten ledger holds still name US0921
        (Done) and close while `mutation.py register` and the ledger ship."""
        ep0263 = set(_children(_EP0263))
        self.assertLessEqual({"US0934", "US0935", "US0936"}, ep0263)
        rows = {r["id"]: r for r in self.rows}
        us0936_done = self._story_status("US0936") == "Done"
        expected = {**{i: ["US0936"] for i in _LEDGER_HOLDS}, "EP0227": ["US0918", "US0920", "US0936"]}
        for rec_id, stories in expected.items():
            with self.subTest(item=rec_id):
                type_, text = _artefact(rec_id)
                self.assertEqual(rows[rec_id]["verdict"], "HELD")
                m = _HOLD_ACTION.match(rows[rec_id]["action"])
                self.assertIsNotNone(m, f"{rec_id}'s record row names no closing story")
                self.assertEqual(_ID.findall(m.group(1)), stories, f"{rec_id}'s record row")
                self.assertEqual(_closes_with(text), stories, f"{rec_id}'s Closes with field")
                if not us0936_done:
                    self.assertFalse(sdlc_md.is_terminal_status(type_, _status(text)),
                                     f"{rec_id} reads {_status(text)!r} while US0936 is not Done")

    def test_the_due_holds_are_closed(self) -> None:
        """BG0772 AC3. MUTANTS: 3efa27e9 re-applied with `git revert`, which writes no closing
        revision row (each item's D0265 row already cites D0264 and its story, so only the
        closing row's own wording counts) and restores index rows and count blocks written
        against an older index; one item's closing row deleted."""
        rows = {r["id"]: r for r in self.rows}
        for rec_id in _DUE_HOLDS:
            with self.subTest(item=rec_id):
                self.assertEqual(rows[rec_id]["verdict"], "HELD")
                path, _ = sdlc_md.find_by_id(_REPO, rec_id)
                text = Path(path).read_text(encoding="utf-8")
                self.assertEqual(_status(text), "Superseded")
                stories = _closes_with(text)
                self.assertTrue(stories, f"{rec_id} names no closing story")
                for story in stories:
                    self.assertEqual(self._story_status(story), "Done", f"{rec_id} names {story}")
                self.assertTrue(
                    any(_CLOSING_ROW in c and "BG0772" in c and all(s in c for s in stories)
                        for c in _revision_rows(text)),
                    f"{rec_id} carries no BG0772 row '{_CLOSING_ROW}' naming {', '.join(stories)}")
                self.assertEqual(_index_status(Path(path)), _status(text),
                                 f"{rec_id}'s _index.md row disagrees with its file")
        due = {sdlc_md.norm_id(i) for i in _DUE_HOLDS}
        for type_ in ("story", "bug", "cr", "epic"):
            with self.subTest(index=type_):
                drift = [d for d in reconcile.detect_type(type_, _REPO)["drift"]
                         if d["kind"] == "count-mismatch" or sdlc_md.norm_id(d["id"] or "") in due]
                self.assertEqual(drift, [], f"the {type_} index disagrees with the closures")


if __name__ == "__main__":
    unittest.main()
