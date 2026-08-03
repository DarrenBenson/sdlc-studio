"""RFC-0009's partial supersession by RFC-0038 is recorded on BOTH sides (US0476).

CR0434 was filed for an asymmetry: RFC-0038 declared what it superseded and the superseded RFC
said nothing, so a reader arriving at RFC-0009 saw `Accepted` and no hint that two of its rows had
been replaced. A one-sided record is worse than none, because it reads as settled.

Each element is asserted SEPARATELY, so removing any one reddens its own line. The round-one AC
set recited the status token and the index note inside a Given and checked neither.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RFCS = REPO / "sdlc-studio" / "rfcs"
RFC0009 = RFCS / "RFC0009-code-complexity-signals.md"
RFC0038 = RFCS / "RFC0038-simplify-to-fibonacci-story-points-and-real-wsjf.md"
INDEX = RFCS / "_index.md"

#: `**D5**` / `**WS3**` inside a header declaration.
_MARKED_ID = re.compile(r"\*\*(D\d+|WS\d+)\*\*")
#: An `RFC-0038` reference in any of its written forms.
_RFC_REF = re.compile(r"RFC-?(\d{4})")


def _field(text: str, name: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"> **{name}:**"):
            return stripped.split("**", 2)[2].lstrip(": ").strip()
    return ""


def _index_text() -> str:
    """The live RFC index plus its `archive/**` sub-indexes.

    A row is archived by release once the live table passes `indexes.archive_after`, which is the
    step `reconcile detect` advises on every run - and both RFCs this file checks are terminal, so
    both were in the first sweep that took the advice. Reading only `_index.md` reported their
    supersession note as missing while it sat intact one file over (BG0504). The union is what
    `reconcile.parse_index` reads, for the same reason.
    """
    paths = [INDEX, *sorted((RFCS / "archive").rglob("*.md"))]
    return "\n".join(p.read_text(encoding="utf-8") for p in paths if p.is_file())


def _row(text: str, rfc_id: str) -> str:
    for line in text.splitlines():
        if line.startswith(f"| [{rfc_id}]"):
            return line
    return ""


class RFC0009RecordTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.nine = RFC0009.read_text(encoding="utf-8")
        cls.thirtyeight = RFC0038.read_text(encoding="utf-8")
        cls.index = _index_text()

    def test_each_of_the_five_supersession_elements_is_present(self) -> None:
        """AC1. Five assertions, not one compound: deleting any single element must fail on its
        own line, which a single `all(...)` could not tell you."""
        # 1. the STATUS token, which a reader sees first.
        self.assertEqual("Accepted (partially superseded)", _field(self.nine, "Status"),
                         "RFC-0009's status still reads as plainly Accepted")
        # 2. the header declaration on the superseded side.
        declared = _field(self.nine, "Partially superseded by")
        self.assertTrue(declared, "RFC-0009 declares no superseder in its header")
        # 3. and it LINKS RFC-0038 rather than merely naming it.
        self.assertIn(RFC0038.name, declared,
                      "the declaration does not link RFC-0038's file, so the reference cannot be "
                      "followed or checked by the links guard")
        # 4. the index Title-cell note, so the supersession is visible without opening the file.
        self.assertIn("partially superseded by RFC-0038", _row(self.index, "RFC-0009"),
                      "the RFC index row gives no hint that RFC-0009 is partly superseded")
        # 5. the declaration on the SUPERSEDING side.
        self.assertIn("RFC-0009", _field(self.thirtyeight, "Supersedes (in part)"),
                      "RFC-0038 does not declare that it supersedes part of RFC-0009")

    def test_every_header_named_decision_row_carries_the_superseded_marker(self) -> None:
        """AC2. The id list is PARSED OUT of the header prose, never hard-coded here.

        A hard-coded list would let the check pass by agreeing with itself: naming a sixth id in
        the header without marking its row would go unnoticed. Derived, a new id is held the moment
        it is written.
        """
        declared = _field(self.nine, "Partially superseded by")
        ids = _MARKED_ID.findall(declared)
        self.assertTrue(ids, f"no bold decision or workstream ids in: {declared[:120]}")
        for ident in ids:
            with self.subTest(id=ident):
                row = next((ln for ln in self.nine.splitlines()
                            if ln.startswith(f"| {ident} |")), "")
                self.assertTrue(row, f"the header names {ident} but no table row defines it")
                self.assertIn("Superseded by", row,
                              f"{ident} is named as superseded in the header and its own row does "
                              f"not say so - a reader scanning the table sees it as live")

    def test_rfc0009_and_rfc0038_declare_the_same_pairing(self) -> None:
        """AC3, read from BOTH sides. A later one-sided edit fails here rather than surviving as
        the exact asymmetry CR0434 was filed for."""
        nine_says = set(_RFC_REF.findall(_field(self.nine, "Partially superseded by")))
        thirtyeight_says = set(_RFC_REF.findall(_field(self.thirtyeight, "Supersedes (in part)")))
        self.assertIn("0038", nine_says, "RFC-0009 does not name RFC-0038 as its superseder")
        self.assertIn("0009", thirtyeight_says, "RFC-0038 does not name RFC-0009 among its own")
        # The decision ids must agree too, or one side records a narrower supersession.
        nine_ids = set(_MARKED_ID.findall(_field(self.nine, "Partially superseded by")))
        thirtyeight_text = _field(self.thirtyeight, "Supersedes (in part)")
        after = thirtyeight_text.split("RFC-0009", 1)[-1] if "RFC-0009" in thirtyeight_text else ""
        self.assertTrue(nine_ids <= set(_MARKED_ID.findall(after)) or not nine_ids,
                        f"RFC-0009 records {sorted(nine_ids)} as superseded but RFC-0038's own "
                        f"declaration does not name them all")


class EverySupersededRfcIsRecordedOnBothSidesTests(unittest.TestCase):
    """The CLASS, not just the one instance the story names.

    RFC-0034 had exactly the same gap: RFC-0038 declared it superseded RFC-0034's D1 and D5 and
    RFC-0034's index row said nothing. Fixing only the instance in the story's title would have
    left the defect beside it, so the sweep is derived from RFC-0038's own declaration.
    """

    def test_every_rfc_that_RFC0038_partly_supersedes_says_so_in_the_index(self) -> None:
        declared = _field(RFC0038.read_text(encoding="utf-8"), "Supersedes (in part)")
        ids = sorted(set(_RFC_REF.findall(declared)) - {"0038"})
        self.assertTrue(ids, "RFC-0038 declares no partial supersession at all")
        index = _index_text()
        for num in ids:
            with self.subTest(rfc=num):
                row = _row(index, f"RFC-{num}")
                self.assertTrue(row, f"no index row for RFC-{num}")
                self.assertIn("partially superseded by RFC-0038", row,
                              f"RFC-0038 says it supersedes part of RFC-{num}, and RFC-{num}'s "
                              f"index row does not mention it - the same one-sided record CR0434 "
                              f"was filed for, one row over")


if __name__ == "__main__":
    unittest.main()
