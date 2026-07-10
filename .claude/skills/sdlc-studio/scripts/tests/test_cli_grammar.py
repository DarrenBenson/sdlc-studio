"""Conformance sweep for the shared CLI argument grammar.

Every batch verb that takes artifact ids must accept the one documented form - a
repeatable `--id` OR a single comma-separated `--ids` (the legacy alias) - and read
them back through `sdlc_md.resolve_ids` to the SAME list. Recorder verbs take the
subject id under the family-standard `--unit` (with any legacy spelling aliased).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


transition = _load("transition", "transition.py")
audit = _load("audit", "audit.py")
artifact = _load("artifact", "artifact.py")
ledger = _load("ledger", "ledger.py")
sdlc_md = transition.sdlc_md

# (module, base argv that reaches the id verb, extra required flags)
ID_VERBS = [
    ("transition set", transition.build_parser, ["set"], ["--status", "Fixed"]),
    ("audit check", audit.build_parser, ["check"], []),
    ("artifact revision", artifact.build_parser, ["revision"], ["--note", "x"]),
]


class IdGrammarConformance(unittest.TestCase):
    def test_every_id_verb_accepts_both_forms_identically(self) -> None:
        for label, build, verb, extra in ID_VERBS:
            with self.subTest(verb=label):
                parser = build()
                a_repeat = parser.parse_args(verb + ["--id", "AA0001", "--id", "AA0002"] + extra)
                a_comma = parser.parse_args(verb + ["--ids", "AA0001,AA0002"] + extra)
                self.assertEqual(sdlc_md.resolve_ids(a_repeat), ["AA0001", "AA0002"], label)
                self.assertEqual(sdlc_md.resolve_ids(a_comma), ["AA0001", "AA0002"], label)

    def test_resolve_ids_merges_and_dedupes_in_order(self) -> None:
        parser = transition.build_parser()
        a = parser.parse_args(["set", "--id", "AA0001", "--ids", "AA0001,AA0002",
                               "--status", "Fixed"])
        self.assertEqual(sdlc_md.resolve_ids(a), ["AA0001", "AA0002"])

    def test_single_scalar_id_still_reads_as_one(self) -> None:
        parser = artifact.build_parser()
        a = parser.parse_args(["revision", "--id", "AA0001", "--note", "x"])
        self.assertEqual(sdlc_md.resolve_ids(a), ["AA0001"])

    def test_recorder_takes_unit_alias(self) -> None:
        # ledger record historically took --tranche; --unit is the family-standard spelling
        # (critic/loop_guard already use it) and must resolve to the same dest.
        parser = ledger.build_parser()
        a = parser.parse_args(["record", "--unit", "CR0020", "--decision", "d"])
        self.assertEqual(a.tranche, "CR0020")
        b = parser.parse_args(["record", "--tranche", "CR0020", "--decision", "d"])
        self.assertEqual(b.tranche, "CR0020")


if __name__ == "__main__":
    unittest.main()
