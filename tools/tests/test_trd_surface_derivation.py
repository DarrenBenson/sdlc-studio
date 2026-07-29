"""US0458: the TRD's shipped-surface enumerations are DERIVED, not restated from memory.

Four lists in the TRD had drifted from the code they describe. The type list omitted nine of the
router's types (including `migrate`, which section 6 simultaneously said the router carried -
the document answering one question two ways). The gate-tier passage named 14 lanes against a
registry of 17. Both drift-kind passages named the same stale five against a tuple of 17. And a
caveat pointed at CR0132 as outstanding work, which is Complete.

Every comparison here reads the CODE. A restated list is a second copy of a fact, and this is
what a second copy looks like after a few releases.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_us0458", SCRIPTS / f"{name}.py")
    assert spec and spec.loader, f"cannot load {name}.py"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_us0458"] = mod
    spec.loader.exec_module(mod)
    return mod


def _router_types() -> set:
    """The router's own Type Reference table - the shipped surface the TRD describes."""
    rows = re.findall(r"^\| `([a-z][a-z-]*)` \|", (SKILL / "SKILL.md").read_text(encoding="utf-8"),
                      re.M)
    assert rows, "no Type Reference rows in SKILL.md - the table was renamed or reshaped"
    return set(rows)


def _backticked(text: str) -> set:
    return set(re.findall(r"`([a-z][a-z0-9-]*)`", text))


def _block(start: str, end_pattern: str, path: Path = TRD) -> str:
    """The block from `start` to the next `end_pattern`, or an ASSERTION if it is not there.

    Never returns "" for a missing heading: an empty block satisfies every set comparison and
    every absence rule below it, which is the failure mode that would let this whole file pass
    on a document it never read.
    """
    text = path.read_text(encoding="utf-8")
    i = text.find(start)
    assert i != -1, (f"{path.name}: could not locate {start!r} - the passage was renamed, and a "
                     f"guard must not compare an empty block")
    rest = text[i + len(start):]
    m = re.search(end_pattern, rest, re.M)
    return rest[:m.start()] if m else rest


class ShippedSurfaceIsDerived(unittest.TestCase):

    def test_the_trd_type_list_equals_the_router_type_table(self) -> None:
        types = _router_types()
        self.assertGreater(len(types), 20, "the router table parsed to almost nothing")
        block = _block("### Command surface", r"^### ")
        named = _backticked(block) & types
        missing = types - named
        self.assertEqual(set(), missing,
                         f"the TRD's command surface omits router types: {sorted(missing)}")

    def test_the_default_sweep_lane_list_equals_gate_default_checks(self) -> None:
        gate = _mod("gate")
        lanes = set(gate.DEFAULT_CHECKS)
        self.assertGreater(len(lanes), 10, "DEFAULT_CHECKS parsed to almost nothing")
        block = _block("#### The gate tier", r"^---\s*$")
        named = _backticked(block)
        missing = lanes - named
        self.assertEqual(set(), missing,
                         f"the TRD's default-sweep list omits registered lanes: {sorted(missing)}")

    def test_both_drift_kind_passages_equal_reconcile_drift_kinds(self) -> None:
        """Both, so the document cannot answer one question two ways - which is exactly what it
        did: the two passages named the same stale five while the tuple carried seventeen."""
        reconcile = _mod("reconcile")
        kinds = set(reconcile.DRIFT_KINDS)
        self.assertGreater(len(kinds), 10, "DRIFT_KINDS parsed to almost nothing")
        passages = {
            "error/report format": _block("### Error", r"^## "),
            "ADR-003": _block("### ADR-003", r"^### ADR-004"),
        }
        for where, block in passages.items():
            named = _backticked(block)
            missing = kinds - named
            self.assertEqual(set(), missing,
                             f"{where} omits shipped drift kinds: {sorted(missing)}")

    def test_a_renamed_heading_fails_rather_than_comparing_nothing(self) -> None:
        """The positive control for `_block`. An extractor returning "" would satisfy every
        set comparison above, because every set is a superset of the empty set."""
        with self.assertRaises(AssertionError) as ctx:
            _block("### A Heading Nobody Wrote", r"^## ")
        self.assertIn("could not locate", str(ctx.exception))


class ClosedWorkIsNotDescribedAsOutstanding(unittest.TestCase):

    def test_the_cr0132_caveat_is_absent_and_cr0132_resolves_complete(self) -> None:
        """The denylist is JUSTIFIED by the backlog rather than asserted: the sentence is only
        wrong because the work it points at is done, so the guard resolves the id and reads it."""
        import sdlc_md
        block = _block("### Error", r"^## ")
        self.assertNotIn("closing it\nis CR0132", block)
        self.assertNotRegex(block, r"does not yet meet this bar",
                            "the TRD still describes closed work as outstanding")
        found = sdlc_md.find_by_id(REPO, "CR0132")
        self.assertIsNotNone(found, "CR0132 resolves nowhere - the id the caveat named is gone, "
                                    "which is a different finding and must not read as clean")
        status = sdlc_md.extract_field(found[0].read_text(encoding="utf-8"), "Status")
        self.assertEqual("Complete", (status or "").strip(),
                         f"CR0132 is {status!r}, so removing the caveat was not justified")

    def test_an_unresolvable_id_fails_loud(self) -> None:
        """An id that resolves nowhere must name itself, not be skipped as a clean tree."""
        import sdlc_md
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(sdlc_md.find_by_id(Path(d), "CR9999"))


if __name__ == "__main__":
    unittest.main()
