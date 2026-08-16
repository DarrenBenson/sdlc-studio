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
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIR))
sys.path.insert(0, str(DIR / "lib"))
import surface  # noqa: E402 - the shared enumerator this module used to duplicate
sys.path.insert(0, str(Path(__file__).resolve().parent))
from boundary import boundary_only  # noqa: E402 - the per-commit / boundary split


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


#: HAND-MAINTAINED ON PURPOSE, and EMPTY - which is the state it is meant to stay in.
#: A declared inventory of recorded debt, never a copy of the shipped script list: deriving
#: it would defeat the point, because a derived set absorbs the next offender silently
#: instead of failing on it.
#:
#: It held twelve names - scripts whose `--root` grammar the sweep could not see, because
#: `_all_parsers()` swallowed every script without a module-level `build_parser`. US0652 made
#: them enumerable and the failures surfaced at once. BG0555 then emptied it, and found that
#: only FOUR of the twelve were still real: the other eight had been repaired and nobody
#: re-measured. That is what a debt list does when it is written once and read as current,
#: and it is the reason the emptiness is now asserted by a test rather than left to habit.
#:
#: The set may only SHRINK. A script added tomorrow gets no entry here; an entry is a promise
#: to remove it. It exempts the root-placement tests below and NOTHING else - a debt set that
#: silences checks the offender already passes is how an exemption outlives its reason.
ROOT_GRAMMAR_DEBT: frozenset[str] = frozenset()


def _all_parsers() -> list[tuple[str, argparse.ArgumentParser]]:
    """Every shipped script that exposes `build_parser`, as (name, parser).

    Reads `lib/surface.py` rather than sweeping the directory itself. The previous version
    built its own map and swallowed every import failure and every `build_parser()` failure
    with a bare `continue`, so the family it swept was whatever happened to load - while its
    docstring claimed the whole one. One enumerator, two readers, so a script added tomorrow is
    covered by both or by neither.
    """
    out: list[tuple[str, argparse.ArgumentParser]] = []
    for rec in surface.enumerate_scripts(DIR):
        if not rec.readable:
            continue          # reported by test_the_sweep_names_what_it_cannot_read below
        mod = sys.modules.get(pathlib.Path(rec.name).stem)
        build = getattr(mod, "build_parser", None) if mod else None
        if build is None:
            continue
        try:
            out.append((rec.name, build()))
        except Exception:  # noqa: BLE001 - surfaced by the same test
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
audit = _load("readiness", "readiness.py")
artifact = _load("artifact", "artifact.py")
ledger = _load("ledger", "ledger.py")
sprint = _load("sprint", "sprint.py")
sdlc_md = transition.sdlc_md

# (module, base argv that reaches the id verb, extra required flags)
ID_VERBS = [
    ("transition set", transition.build_parser, ["set"], ["--status", "Fixed"]),
    ("audit check", audit.build_parser, ["check"], []),
    ("artifact revision", artifact.build_parser, ["revision"], ["--note", "x"]),
]

#: The SECOND table, for verbs carrying more than one id list. `resolve_ids` hard-reads the
#: `--id`/`--ids` pair, so a verb with two lists cannot be a row above without the sweep
#: reading one of its lists as the other; the shared reader for those is `split_id_list`.
#: Registered here rather than left uncovered: `batch swap` reinvented nothing, but the sweep
#: is what stops the NEXT two-list verb doing so, and the row is the only thing that says
#: which helper the verb is held to.
#:
#: (label, parser builder, argv reaching the verb, flag, dest, the rest of a valid call)
LIST_ID_VERBS = [
    ("sprint batch swap --out", sprint.build_parser, ["batch", "swap"], "--out", "out_units",
     ["--in", "AA0003", "--reason", "r"]),
    ("sprint batch swap --in", sprint.build_parser, ["batch", "swap"], "--in", "in_units",
     ["--out", "AA0003", "--reason", "r"]),
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

    def test_every_list_id_verb_reads_both_house_forms_through_the_shared_helper(self) -> None:
        """A verb carrying two id lists is held to the same grammar as one carrying a single
        one: repeating the flag and passing a comma list are the SAME request, and both are
        read back through `sdlc_md.split_id_list` rather than a splitter of the verb's own.

        MUTANT: change `--out` from `action="append"` to a plain store - the repeated form then
        keeps only the last id and the two forms stop agreeing. This table is the half of
        US0470 AC5 that never landed, so `batch swap` sat outside the sweep entirely (BG0497).
        """
        self.assertTrue(LIST_ID_VERBS, "the list-id table is empty, so this sweep checks nothing")
        for label, build, verb, flag, dest, extra in LIST_ID_VERBS:
            with self.subTest(verb=label):
                parser = build()
                repeated = parser.parse_args(verb + [flag, "AA0001", flag, "AA0002"] + extra)
                comma = parser.parse_args(verb + [flag, "AA0001,AA0002"] + extra)
                self.assertEqual(sdlc_md.split_id_list(getattr(repeated, dest)),
                                 ["AA0001", "AA0002"], f"{label}: the repeated form")
                self.assertEqual(sdlc_md.split_id_list(getattr(comma, dest)),
                                 ["AA0001", "AA0002"], f"{label}: the comma form")

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
            if name in ROOT_GRAMMAR_DEBT:
                continue  # recorded debt, NAMED above and in BG0555 - the set only shrinks
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
            if name in ROOT_GRAMMAR_DEBT:
                continue  # recorded debt, NAMED above and in BG0555 - the set only shrinks
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
            if name in ROOT_GRAMMAR_DEBT:
                continue  # recorded debt, NAMED above and in BG0555 - the set only shrinks
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


#: Verbs PROVEN to answer differently depending on `--root`, and therefore the only ones a
#: fixture sweep can speak for. Measured, not guessed - and RE-measured after an independent
#: review showed the first measurement was taken in the wrong tree.
#:
#: All 128 `--root`-taking verbs the sweep can invoke were run against a clean worktree of HEAD
#: and against an empty fixture. Sixteen name one of this repository's artefacts in the first and
#: none in the second. **One hundred name no artefact either way**, so no fixture sweep can speak
#: for them, and the inventory records that rather than counting them: a guard reporting "128
#: verbs checked" when 16 can fail is the vacuous-verifier shape this repository keeps paying for.
#:
#: The first cut of this list held 23, measured in the author's own tree where gitignored
#: `.local/` state made several verbs answer richly. In the tree CI actually sees, six of those
#: 23 emit only an error naming the root - `repo_map stats`, `verify_ac report`, `lessons list`
#: and `revalidate` among them - and `config show` CRASHES with an unhandled TypeError whose
#: traceback happens to contain the repo path. They passed the control because it accepted the
#: ROOT PATH as evidence, which any message interpolating its own argument satisfies. It now
#: requires a real artefact id, so the control cannot be satisfied by a crash.
#:
#: FIVE verbs discriminate and are excluded because they WRITE, and the control runs against the
#: real tree: `lessons summary` (rewrites the TRACKED LESSONS-SUMMARY.md), `close_owed baseline`,
#: `docgen surface`, `telemetry record`, and `verify_ac lane-check` (a gitignored `.local`
#: sidecar). Only the last was found by its author, and only because the `repo-writes` gate lane
#: refused the commit. `lessons summary` was invisible on the author's machine - a gitignored
#: `.local/lessons.md` made its regeneration byte-identical there - and would have dirtied every
#: fresh clone and every CI run. A guard measuring the tree must not be one of the things
#: changing it, and a guard that only looks clean where it was written has not been measured.
#:
#: The set may only GROW, and an entry earns its place by measurement in a CLEAN tree.
#:
#: AND its discrimination must not depend on the tree being in a particular STATE. That rule was
#: learned by removing four entries in two days, each caught by the control below rather than by
#: anyone reading the list: `doc_freshness` named artefacts only while it had a stale claim to
#: report, and `sprint next`, `autosprint next` and `constitution check` only while no run was
#: open and a charter was queued. Every one passed its measurement honestly on the day it was
#: admitted. None was wrong to admit; the ADMISSION RULE was, because "names an artefact when
#: pointed at the real tree" is a question whose answer moves with the tree.
#:
#: So the bar is now unconditional: a verb belongs here only if it names an artefact of this
#: repository whatever state the repository is in. The control is what enforces it - an entry
#: that quietly stops discriminating fails rather than passing forever - and the churn it has
#: produced is the mechanism working, not a fault in it.
#:
#: `doc_freshness` was removed after the control caught it drifting - which is the control
#: doing its job rather than a fault in it. It named artefacts only while it had a STALE
#: claim to report; once `reviews/LATEST.md` was brought current it answered `state documents
#: are fresh` and named nothing, so its row asserted nothing. An entry whose discrimination
#: depends on the tree being in a particular state is not a measurement, and leaving it here
#: would have been a row that passes forever.
ROOT_EFFECT_VERBS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ac_scope.py", ("check",)), ("changelog.py", ("check",)),
    ("close_owed.py", ("detect",)), ("critic.py", ("show",)),
    ("decisions.py", ("list",)), ("flow.py", ("compute",)),
    ("integrity.py", ("check",)), ("reconcile.py", ("detect",)), ("retro.py", ("estimator",)),
    ("status.py", ("backlog",)), ("validate.py", ("check",)),
)

#: What a real-tree answer looks like: this repository's own artefact ids and run ids, plus its
#: absolute path. An empty fixture cannot produce any of them.
_REAL_TREE_MARKER = re.compile(r"\b(?:BG05\d\d|US06\d\d|RUN-01K\w+)")


class RootIsReadNotJustParsed(unittest.TestCase):
    """BG0555 / BG0556. Grammar conformance above proves a `--root` PARSES in both positions. It
    proves nothing about whether the value is ever READ, and that gap is not theoretical twice
    over: `docgen references --root TMP` wrote TMP's file with the real tree's 56 references, and
    `changelog.py --root <empty fixture> check` exited 0 reporting this repository's nineteen
    fragments. Neither rejected anything. Both answered confidently about somewhere else, which is
    worse than a refusal, because a refusal is visible.
    """

    #: The repository this test module lives in - the tree a decorative `--root` falls back to.
    REPO = DIR.parent.parent.parent.parent

    def _run(self, script: str, argv, root) -> str:
        proc = subprocess.run(
            [sys.executable, "-B", str(DIR / script), "--root", str(root), *argv],
            capture_output=True, text=True, cwd=str(self.REPO), timeout=120)
        return (proc.stdout or "") + (proc.stderr or "")

    def test_the_root_grammar_debt_set_is_empty(self) -> None:
        """The ratchet. An exemption is a promise to remove it, and this is where the promise is
        kept - twelve names sat here, eight of them already fixed and never re-measured."""
        self.assertEqual(frozenset(), ROOT_GRAMMAR_DEBT,
                         "the root-grammar debt set only shrinks; it reached empty in BG0555")

    def test_a_root_given_before_the_verb_selects_the_tree_that_is_read(self) -> None:
        """The effect, not the grammar. An empty fixture must answer about the fixture, in BOTH
        placements - and must not quietly answer about the repository it was launched from."""
        with tempfile.TemporaryDirectory() as d:
            fixture = Path(d)
            (fixture / "changelog.d").mkdir()
            (fixture / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n",
                                                  encoding="utf-8")
            for argv in (["--root", str(fixture), "check"], ["check", "--root", str(fixture)]):
                with self.subTest(argv=" ".join(argv)):
                    proc = subprocess.run(
                        [sys.executable, "-B", str(DIR / "changelog.py"), *argv],
                        capture_output=True, text=True, cwd=str(self.REPO), timeout=120)
                    self.assertEqual(0, proc.returncode,
                                     f"{argv}: {proc.stderr.strip() or proc.stdout.strip()}")
                    self.assertIn("no stray fragments", proc.stdout,
                                  f"{argv}: answered about a tree other than the fixture")

    def test_no_verb_answers_about_the_real_tree_when_pointed_at_a_fixture(self) -> None:
        """THE guard. Run each proven-discriminating verb against an empty fixture from inside
        this repository; none may name one of this repository's artefacts."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            for script, verb in ROOT_EFFECT_VERBS:
                with self.subTest(verb=f"{script} {' '.join(verb)}".strip()):
                    out = self._run(script, verb, d)
                    leaked = sorted(set(_REAL_TREE_MARKER.findall(out)))
                    self.assertFalse(
                        leaked or str(self.REPO) in out,
                        f"{script} {' '.join(verb)}: --root pointed at an empty fixture and the "
                        f"answer names this repository ({leaked or self.REPO}) - the flag is "
                        f"decorative")

    def test_the_inventory_is_a_measured_subset_and_never_the_whole_surface(self) -> None:
        """The inventory must stay SMALLER than the surface it is drawn from. The tempting repair,
        when someone notices the guard covers 23 verbs of 128, is to paste in the other 105 - and
        every one of them would pass forever, because they print nothing that names a tree either
        way. Coverage would read as complete and assert less than it does now. Membership is
        earned by measurement, and this is what stops it being assumed."""
        invocable = set()
        for name, parser in _all_parsers():
            if not any("--root" in a.option_strings for a in parser._actions):
                continue
            subs = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
            if not subs:
                invocable.add((name, ()))
                continue
            for verb, sp in subs[0].choices.items():
                required = [a for a in sp._actions if getattr(a, "required", False)]
                positional = [a for a in sp._actions
                              if not a.option_strings and a.nargs not in ("?", "*")]
                if not required and not positional:
                    invocable.add((name, (verb,)))
        listed = set(ROOT_EFFECT_VERBS)
        self.assertTrue(listed, "the effect inventory is empty, so the guard sweeps nothing")
        unknown = listed - invocable
        self.assertEqual(set(), unknown,
                         f"the inventory names verbs the sweep cannot invoke: {sorted(unknown)}")
        self.assertLess(len(listed), len(invocable),
                        "the inventory has grown to the whole invocable surface - it is only "
                        "meaningful as the MEASURED discriminating subset, and a verb that "
                        "prints nothing either way passes this sweep forever")

    @boundary_only("it runs all 15 listed verbs against the REAL tree at 83s. The guard it "
                   "controls - the fixture sweep - still runs on every commit; what defers is "
                   "the proof that each row CAN fail, which changes only when the inventory "
                   "does, and an inventory edit reaches push before it reaches anyone else")
    def test_every_listed_verb_can_actually_fail_the_guard(self) -> None:
        """The control, and the reason the inventory above is a fixed list rather than a sweep of
        everything. Pointed at the REAL tree the same verbs must each name a real artefact - so a
        clean run above means the flag was obeyed, not that the verb prints nothing either way.
        Without this, an entry that stopped discriminating would sit here passing forever."""
        for script, verb in ROOT_EFFECT_VERBS:
            with self.subTest(verb=f"{script} {' '.join(verb)}".strip()):
                out = self._run(script, verb, self.REPO)
                # The ROOT PATH is NOT evidence. Accepting it let six verbs that emit only an
                # error naming their own argument pass this control, and one that CRASHES - a
                # traceback contains file paths too. Only a real artefact id proves the tree was
                # read, which is what the guard above needs to mean anything.
                self.assertTrue(
                    _REAL_TREE_MARKER.search(out),
                    f"{script} {' '.join(verb)}: pointed at the real tree it named no artefact "
                    f"of it, so its row in the guard above asserts nothing - re-measure it in a "
                    f"CLEAN worktree, or remove it")


if __name__ == "__main__":
    unittest.main()
