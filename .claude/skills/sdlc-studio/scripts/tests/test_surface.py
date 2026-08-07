"""Unit tests for lib/surface.py - the shipped command surface, enumerated once (US0652).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIR))
sys.path.insert(0, str(DIR / "lib"))
import surface  # noqa: E402


class BuildParserCoverageTests(unittest.TestCase):
    """AC1: every CLI script exposes `build_parser`, and the one non-CLI is named."""

    def test_every_cli_script_exposes_build_parser(self) -> None:
        """Asserted BOTH ways, which is what makes it a check rather than a headcount.

        Mutant: remove `build_parser` from one converted script, leaving its inline parser in
        `main()` - the first assertion names it.
        Mutant: add a `build_parser` to `carry_forward.py`, so a library counts as a CLI
        surface - the second assertion names it, and a one-way check would not.
        Mutant: list `autosprint.py` as exempt - it re-exports `sprint`'s, so `getattr` finds
        one, and the exemption set would be wrong on the day it was written.
        """
        missing = surface.missing_build_parser()
        self.assertEqual([], missing,
                         f"CLI script(s) with no module-level build_parser: {missing}. A parser "
                         f"built inside main() is invisible to the enumeration, so its verbs "
                         f"cannot be counted as documented or as missing")

        recs = {r.name: r for r in surface.enumerate_scripts()}
        for name in surface.NON_CLI:
            with self.subTest(exempt=name):
                self.assertIn(name, recs, f"{name} is exempt from a rule it is not subject to")
                self.assertFalse(
                    recs[name].has_build_parser,
                    f"{name} is listed as a non-CLI exemption and HAS a build_parser - either "
                    f"it is a command and the exemption is wrong, or a parser was bolted onto "
                    f"a library to satisfy a blanket rule")
                src = (DIR / name).read_text(encoding="utf-8")
                self.assertNotIn("ArgumentParser", src,
                                 f"{name} is exempt as a non-CLI and builds an ArgumentParser")

        # autosprint.py is NOT an exemption: it re-exports sprint's build_parser.
        self.assertNotIn("autosprint.py", surface.NON_CLI,
                         "autosprint.py re-exports sprint's build_parser, so it is covered "
                         "rather than exempt")
        self.assertTrue(recs["autosprint.py"].has_build_parser)


class SurfaceEnumerationTests(unittest.TestCase):
    """AC2, AC3, AC4: what the enumeration must never do quietly."""

    def _fixture(self, d: Path, body: str, name: str = "broken_thing.py") -> Path:
        """A scripts dir holding one healthy script and one the loader cannot execute."""
        (d / "healthy.py").write_text(
            "import argparse\n"
            "def build_parser():\n"
            "    p = argparse.ArgumentParser(prog='healthy')\n"
            "    s = p.add_subparsers(dest='cmd')\n"
            "    s.add_parser('go')\n"
            "    return p\n", encoding="utf-8")
        (d / name).write_text(body, encoding="utf-8")
        return d

    def test_a_module_that_will_not_import_is_named_not_skipped(self) -> None:
        """AC2. Mutant: swallow the import exception and continue, as `_all_parsers()` did -
        the sweep then reports a count of what happened to load, and nothing says so.

        The unimportable module is SYNTHETIC. No real script in this tree fails to import: a
        claim that three of them did came from a measurement whose own loader fabricated the
        module name, and it did not survive being re-run.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(Path(d), "raise RuntimeError('this module refuses to load')\n")
            recs = {r.name: r for r in surface.enumerate_scripts(root)}
            self.assertIn("broken_thing.py", recs,
                          "the module that would not import was DROPPED, so the enumeration "
                          "reports a count of whatever happened to load")
            self.assertFalse(recs["broken_thing.py"].readable)
            self.assertIn("RuntimeError", recs["broken_thing.py"].error,
                          "the record names no reason, so a reader cannot tell an empty surface "
                          "from an unreadable one")
            # The positive control: the sweep did not stop at the failure.
            self.assertEqual(["go"], recs["healthy.py"].verbs,
                             "one unreadable module ended the sweep")
            self.assertEqual({"broken_thing.py"}, set(surface.unreadable(root)))

    def test_a_build_parser_that_raises_is_named_too(self) -> None:
        """A module that imports and whose parser will not build is the same class of silence.
        Mutant: catch it and continue."""
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(Path(d),
                                 "def build_parser():\n"
                                 "    raise ValueError('needs runtime state')\n")
            recs = {r.name: r for r in surface.enumerate_scripts(root)}
            self.assertIn("ValueError", recs["broken_thing.py"].error or "")
            self.assertTrue(recs["broken_thing.py"].has_build_parser)

    def test_a_positional_choice_is_enumerated_like_a_subcommand(self) -> None:
        """AC3. `verify_ac.py testplan derive` exists as a positional `choices` value, not a
        subparser, and a subparser-only walk misses it - a verb the enumeration cannot see is
        one no coverage number can count as missing.

        Mutant: walk subparsers only, dropping the positional-choices branch.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "positional.py").write_text(
                "import argparse\n"
                "def build_parser():\n"
                "    p = argparse.ArgumentParser(prog='positional')\n"
                "    s = p.add_subparsers(dest='cmd')\n"
                "    tp = s.add_parser('testplan')\n"
                "    tp.add_argument('action', choices=['derive', 'check'])\n"
                "    return p\n", encoding="utf-8")
            verbs = surface.verbs(root)["positional.py"]
            self.assertIn("testplan", verbs)
            self.assertIn("testplan derive", verbs,
                          "a positional `choices` verb was not enumerated, so it can never be "
                          "counted as undocumented")
            self.assertIn("testplan check", verbs)

        # ...and on the real tree, where the case actually lives.
        self.assertIn("testplan derive", surface.verbs().get("verify_ac.py", []))

    def test_the_grammar_tests_read_the_shared_library(self) -> None:
        """AC4, asserted STRUCTURALLY. A whole-module selector passes today and would pass with
        the delegation reverted, which is a criterion that cannot fail on what it claims.

        The shared enumerator is patched to return a surface nothing else could produce, and the
        grammar tests' own `_all_parsers()` is required to move with it.

        Mutant: give `test_cli_grammar.py` back its own parser map.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "grammar_under_test", DIR / "tests" / "test_cli_grammar.py")
        grammar = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(grammar)

        sentinel = surface.ScriptSurface(name="sentinel_only.py", verbs=["invented"],
                                         has_build_parser=True)
        real = surface.enumerate_scripts
        try:
            surface.enumerate_scripts = lambda *a, **k: [sentinel]  # noqa: ARG005
            names = [n for n, _p in grammar._all_parsers()]
        finally:
            surface.enumerate_scripts = real
        self.assertEqual([], names,
                         "the grammar sweep produced parsers the patched enumerator never "
                         "offered, so it is still building its own map rather than reading "
                         "lib/surface.py")


if __name__ == "__main__":
    unittest.main()
