"""Conformance sweep for the shared CLI argument grammar.

Every batch verb that takes artifact ids must accept the one documented form - a
repeatable `--id` OR a single comma-separated `--ids` (the legacy alias) - and read
them back through `sdlc_md.resolve_ids` to the SAME list. Recorder verbs take the
subject id under the family-standard `--unit` (with any legacy spelling aliased).

The sweep also covers flag PLACEMENT across the whole family: `--root` is a global
flag valid before OR after the subcommand (no per-subcommand default may clobber a
value given before the verb), and a flag whose help advertises it as `combinable`
must MERGE on repeat (`action="append"`), never silently overwrite.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import argparse
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


def _all_parsers() -> list[tuple[str, argparse.ArgumentParser]]:
    """Every shipped script that exposes `build_parser`, as (name, parser). The
    placement sweeps below walk this whole family, not a hand-picked subset - a new
    script reintroducing the class fails the sweep the moment it lands."""
    out: list[tuple[str, argparse.ArgumentParser]] = []
    for path in sorted(DIR.glob("*.py")):
        try:
            mod = _load("sweep_" + path.stem, path.name)
        except Exception:  # noqa: BLE001 - a script that will not import is out of scope here
            continue
        build = getattr(mod, "build_parser", None)
        if build is None:
            continue
        try:
            out.append((path.name, build()))
        except Exception:  # noqa: BLE001 - build_parser must not need runtime state
            continue
    return out


def _walk(parser: argparse.ArgumentParser):
    """Yield (subcommand-path, action) for every optional flag in the tree."""
    stack = [("", parser)]
    while stack:
        prefix, p = stack.pop()
        for a in p._actions:
            if isinstance(a, argparse._SubParsersAction):
                for name, sp in a.choices.items():
                    stack.append((f"{prefix} {name}".strip(), sp))
            elif a.option_strings:
                yield prefix, a


def _subparsers(parser: argparse.ArgumentParser):
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            yield from a.choices.items()


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


class RootPlacementConformance(unittest.TestCase):
    """`--root` is a global option: valid before OR after the subcommand, uniformly
    across the whole script family. `sdlc_md.add_global_root` installs the pattern;
    these assertions fail the moment a script declares `--root` only per-subcommand
    (so `prog --root X sub` is rejected) or lets a subcommand default clobber a value
    given before the subcommand."""

    @staticmethod
    def _declares_root(parser) -> bool:
        """Does this parser deal in a repo root at all? A script that operates on
        --master/--target (pvd) or ~/.claude plan files (plan) declares no --root
        anywhere and is exempt - bolting on a global --root it never reads is a dead
        flag, itself a smell."""
        return any("--root" in a.option_strings for _sub, a in _walk(parser))

    def test_every_root_dealing_script_accepts_root_before_the_subcommand(self) -> None:
        for name, parser in _all_parsers():
            if not self._declares_root(parser):
                continue  # a script with no --root reader opts out (see _declares_root)
            with self.subTest(script=name):
                top = [a for a in parser._actions
                       if "--root" in a.option_strings and a.dest == "root"]
                self.assertTrue(
                    top, f"{name}: no top-level --root; `{name} --root X <sub>` is rejected")
                self.assertEqual(top[0].default, ".", f"{name}: global --root default")

    def test_root_flag_always_binds_the_standard_dest(self) -> None:
        # A `--root` option string bound to a dest OTHER than `root` is the silent-divergence
        # trap: the global --root (dest `root`) cannot feed it, so a value given before the
        # verb is dropped while the verb reads its own dest. Every `--root` must bind `root`.
        for name, parser in _all_parsers():
            for sub, action in _walk(parser):
                if "--root" in action.option_strings:
                    with self.subTest(script=name, sub=sub, flags=tuple(action.option_strings)):
                        self.assertEqual(
                            action.dest, "root",
                            f"{name} {sub}: a --root alias binds dest '{action.dest}', not "
                            f"'root' - the global --root cannot feed it, so a value before "
                            f"the verb is silently dropped")

    def test_subcommand_root_cannot_clobber_the_global_value(self) -> None:
        for name, parser in _all_parsers():
            for sub, action in _walk(parser):
                if "--root" in action.option_strings and action.dest == "root" and sub:
                    with self.subTest(script=name, sub=sub):
                        self.assertIs(
                            action.default, argparse.SUPPRESS,
                            f"{name} {sub}: per-subcommand --root must default to SUPPRESS "
                            f"so it does not overwrite `--root X {sub}` set before the verb")

    def test_root_parses_in_both_positions(self) -> None:
        parser = transition.build_parser()
        before = parser.parse_args(["--root", "/x", "set", "--id", "AA0001", "--status", "Fixed"])
        after = parser.parse_args(["set", "--id", "AA0001", "--status", "Fixed", "--root", "/y"])
        neither = parser.parse_args(["set", "--id", "AA0001", "--status", "Fixed"])
        self.assertEqual(before.root, "/x")
        self.assertEqual(after.root, "/y")
        self.assertEqual(neither.root, ".")


class FormatFlagConformance(unittest.TestCase):
    """`--format` is spelled one way family-wide: `text` and `json` are always offered
    and `text` is the default (`sdlc_md.add_format_arg`). A verb that drops `text` or
    defaults elsewhere makes the agent probe --help for the output switch it already
    knows on every other command."""

    def test_every_format_flag_offers_text_and_json_defaulting_text(self) -> None:
        for name, parser in _all_parsers():
            for sub, action in _walk(parser):
                if "--format" in action.option_strings:
                    with self.subTest(script=name, sub=sub):
                        choices = tuple(action.choices or ())
                        self.assertIn("text", choices, f"{name} {sub}: --format lacks 'text'")
                        self.assertIn("json", choices, f"{name} {sub}: --format lacks 'json'")
                        self.assertEqual(action.default, "text",
                                         f"{name} {sub}: --format must default to 'text'")


class RepeatableFlagConformance(unittest.TestCase):
    """A flag whose help advertises it as `combinable` is a set selector: repeating it
    must MERGE, not silently overwrite an earlier value. Enforced structurally so the
    `store` vs `append` mismatch (a planning tool that drops half the filter without a
    word) cannot be reintroduced on any script."""

    def test_combinable_flags_merge_rather_than_overwrite(self) -> None:
        multi_actions = (argparse._AppendAction, argparse._ExtendAction)
        for name, parser in _all_parsers():
            for sub, action in _walk(parser):
                help_l = (action.help or "").lower()
                if "combinable" in help_l and "not combinable" not in help_l:
                    with self.subTest(script=name, sub=sub, flag=action.option_strings[0]):
                        merges = isinstance(action, multi_actions) or action.nargs in ("+", "*")
                        self.assertTrue(
                            merges,
                            f"{name} {sub} {action.option_strings[0]}: help says 'combinable' "
                            f"but the action overwrites on repeat - use action='append'")


if __name__ == "__main__":
    unittest.main()
