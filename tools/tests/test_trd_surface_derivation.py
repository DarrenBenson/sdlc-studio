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


#: A comma-or-and separated run of backticked names, the shape every enumeration in the TRD uses.
_NAME = r"`[a-z][a-z0-9-]*`"
_RUN = re.compile(_NAME + r"(?:(?:,\s*(?:and\s+)?|\s+and\s+)" + _NAME + r")+")


def _enumerated(block: str, where: str) -> set:
    """The names the passage ENUMERATES, addressed as the list rather than as loose words.

    Every backticked word in a block drags in the prose around the list, and a set intersected
    with the shipped registry is a subset of it by construction - which is how the first version
    of this guard came to have no reverse direction at all. Addressing the run itself lets the
    comparison below be an EQUALITY, so a name the code does not carry reddens as surely as one
    it does.

    Refuses when the block does not hold exactly one run of more than three names: a reshaped
    passage must fail rather than have the guard silently compare some other list.
    """
    runs = [r for r in _RUN.findall(block) if r.count("`") > 6]
    assert len(runs) == 1, (
        f"{where}: expected one enumeration of more than three backticked names, found "
        f"{len(runs)} - the passage was reshaped, and a guard must not compare the wrong list")
    return set(re.findall(r"`([a-z][a-z0-9-]*)`", runs[0]))


def _assert_passage_matches(case: unittest.TestCase, block: str, shipped: set, prose: set,
                            where: str) -> None:
    """BOTH directions, against the shipped registry.

    `prose` is the small, declared set of backticked words the passage uses for something other
    than a member of this enumeration. Anything else the passage names - inside the run or
    smuggled into the sentences around it - is a name the code does not carry, and reddens.
    """
    named = _enumerated(block, where)
    case.assertEqual(shipped, named,
                     f"{where}: the passage enumerates {sorted(named - shipped)}, which the "
                     f"shipped registry does not carry, and omits {sorted(shipped - named)}")
    stray = _backticked(block) - shipped - prose
    case.assertEqual(set(), stray,
                     f"{where}: {sorted(stray)} is named in the passage but is not in the "
                     f"shipped registry. If it is prose rather than a member, declare it in the "
                     f"passage's prose set so the addition is a decision somebody made")


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
    """EQUALITY against the shipped registry, in both directions.

    The first version of every comparison here computed `named = _backticked(block) & <shipped
    set>` and asserted `<shipped set> - named == set()`. The intersection made `named` a subset
    of the shipped set by construction, so the reverse direction - the document naming something
    the code does NOT have - was not merely unchecked, it was unrepresentable. Removing a lane
    from `gate.DEFAULT_CHECKS`, removing a drift kind from `reconcile.DRIFT_KINDS` and inserting
    a fictional `telepathy-lane` into the TRD's gate-tier prose each survived the whole file.

    `_assert_passage_matches` replaces it: the passage's enumeration must EQUAL the registry,
    and no other backticked name may appear in the passage outside its declared prose set. The
    discrimination is pinned on its own in `TheSurfaceComparisonFailsInBothDirections`.
    """

    #: Backticked words each passage uses for something other than a member of its enumeration.
    #: Kept per-passage and tiny: an allowlist that grows is a guard being switched off.
    _COMMAND_PROSE = {"action", "type", "autosprint"}
    _DRIFT_PROSE = {"apply", "fix", "validate"}

    def test_the_trd_type_list_equals_the_router_type_table(self) -> None:
        types = _router_types()
        self.assertGreater(len(types), 20, "the router table parsed to almost nothing")
        _assert_passage_matches(self, _block("### Command surface", r"^### "), types,
                                self._COMMAND_PROSE, "the TRD's command surface")

    def test_the_default_sweep_lane_list_equals_gate_default_checks(self) -> None:
        gate = _mod("gate")
        lanes = set(gate.DEFAULT_CHECKS)
        self.assertGreater(len(lanes), 10, "DEFAULT_CHECKS parsed to almost nothing")
        _assert_passage_matches(self, _block("#### The gate tier", r"^---\s*$"), lanes,
                                set(), "the TRD's default-sweep list")

    def test_both_drift_kind_passages_equal_reconcile_drift_kinds(self) -> None:
        """Both, so the document cannot answer one question two ways - which is exactly what it
        did: the two passages named the same stale five while the tuple carried seventeen."""
        reconcile = _mod("reconcile")
        kinds = set(reconcile.DRIFT_KINDS)
        self.assertGreater(len(kinds), 10, "DRIFT_KINDS parsed to almost nothing")
        passages = {
            "error/report format": (_block("### Error", r"^## "), self._DRIFT_PROSE),
            "ADR-003": (_block("### ADR-003", r"^### ADR-004"), set()),
        }
        for where, (block, prose) in passages.items():
            with self.subTest(passage=where):
                _assert_passage_matches(self, block, kinds, prose, where)

    def test_a_renamed_heading_fails_rather_than_comparing_nothing(self) -> None:
        """The positive control for `_block`. An extractor returning "" would satisfy every
        set comparison above, because every set is a superset of the empty set."""
        with self.assertRaises(AssertionError) as ctx:
            _block("### A Heading Nobody Wrote", r"^## ")
        self.assertIn("could not locate", str(ctx.exception))


class TheSurfaceComparisonFailsInBothDirections(unittest.TestCase):
    """The discriminator itself, over synthetic passages, so the property is pinned rather than
    inferred from a green run against a document that happens to agree today.

    A comparison run over the real TRD can only demonstrate the direction the real TRD is
    currently wrong in, which is none of them. These drive the helper at a registry of four
    names and vary one thing at a time.
    """

    SHIPPED = {"alpha", "beta", "gamma", "delta"}
    AGREES = "The sweep runs `alpha`, `beta`, `gamma` and `delta`.\n"

    def test_a_passage_that_matches_the_registry_passes(self) -> None:
        """The positive control. Without it, every refusal below is satisfied by a helper that
        refuses everything."""
        _assert_passage_matches(self, self.AGREES, self.SHIPPED, set(), "fixture")

    def test_the_comparison_fails_in_both_directions_and_outside_the_enumeration(self) -> None:
        cases = {
            "a name the registry does not carry":
                "The sweep runs `alpha`, `beta`, `gamma`, `delta` and `telepathy-lane`.\n",
            "a name the registry carries and the passage omits":
                "The sweep runs `alpha`, `beta` and `gamma`.\n",
            "a name smuggled into the prose outside the enumeration":
                self.AGREES + "The `telepathy-lane` runs last.\n",
        }
        for where, block in cases.items():
            with self.subTest(case=where):
                with self.assertRaises(AssertionError) as ctx:
                    _assert_passage_matches(self, block, self.SHIPPED, set(), "fixture")
                self.assertIn("fixture", str(ctx.exception),
                              "the refusal does not name the passage it read")

    def test_a_declared_prose_word_is_not_read_as_a_member(self) -> None:
        """The escape the allowlist exists for, and its bound: a declared word is tolerated in
        the prose, and is still refused inside the enumeration."""
        _assert_passage_matches(self, self.AGREES + "Each lane returns a `verdict`.\n",
                                self.SHIPPED, {"verdict"}, "fixture")
        with self.assertRaises(AssertionError):
            _assert_passage_matches(self,
                                    "The sweep runs `alpha`, `beta`, `gamma`, `delta` and "
                                    "`verdict`.\n", self.SHIPPED, {"verdict"}, "fixture")

    def test_a_passage_whose_enumeration_cannot_be_addressed_fails(self) -> None:
        """A block with no list, and a block with two, both fail naming the block. Comparing
        the wrong run is the same class of defect as comparing an empty one."""
        for block in ("The sweep runs every registered lane.\n",
                      self.AGREES + "Bound lanes are `one`, `two`, `three` and `four`.\n"):
            with self.subTest(block=block.strip()[:40]):
                with self.assertRaises(AssertionError) as ctx:
                    _enumerated(block, "fixture")
                self.assertIn("fixture", str(ctx.exception))


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
