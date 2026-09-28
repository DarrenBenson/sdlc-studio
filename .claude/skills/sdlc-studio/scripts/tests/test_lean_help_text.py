"""US0964: every script's --help describes the v6 loop and no retired review step.

Agents read `--help` to decide what to run, so a help line that still asks for a ceremony v6
removed gets performed. The parsers are read in-process through `lib/surface.py`, the one
enumeration of the shipped command surface, and every parser in each tree is formatted: a
subcommand's own options and description live only in ITS help, and its one-line summary only
in its parent's, so a scan of the top-level help alone misses most of what is stale.

The retired surfaces come from US0924's shared list (`retired_surface.py`), imported, not copied.
This module adds only what a help text can say that no doc page does.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
import retired_surface  # noqa: E402

sys.path.insert(0, str(loader.SCRIPTS_DIR / "lib"))
import surface  # noqa: E402

#: v6 signs a run once (`sprint sign`); any other sign-off named in a help text is one v6
#: retired. "Sign-off" for the run's own signature is allowed.
SIGN_OFF = {"a sign-off other than the run's signature":
            re.compile(r"(?i)(?<!run's )(?<!run )\bsign(?:ed|s)?[- ]?offs?\b")}

#: What says a surface is retired, in help text: the shared list's words WITHOUT its refusal
#: words. A help line that names a retired surface beside "refuses" teaches it as live ("the
#: sign-off refuses a run without one"); only a line saying it is gone may name it. Derived from
#: the shared pattern, so a word the list adds later is read here too.
_REFUSAL_WORDS = r"|\brefuse[sd]?\b"
if retired_surface.RETIRED_CONTEXT.pattern.count(_REFUSAL_WORDS) != 1:
    raise RuntimeError("retired_surface.RETIRED_CONTEXT no longer carries the refusal words "
                       "this module removes from it")
HELP_RETIRED_CONTEXT = re.compile(
    retired_surface.RETIRED_CONTEXT.pattern.replace(_REFUSAL_WORDS, ""))

#: A refusal v6 turned into advice, claimed as still in force. A claim of refusal is itself the
#: stale text, so the "refused" that would excuse a retired surface cannot excuse it here. The
#: goal review's escapes (`--goal-review-waived`, `--override-goal-review`) are in the retired
#: list; the refusal they escaped is what this names.
RETIRED_REFUSALS = {
    "the goal-review refusal":
        re.compile(r"(?i)\brefuses?\b[^.\n]*\bgoal\b[^.\n]*\b(?:no seat|unreviewed)\b"
                   r"|\bunreviewed goal\b[^.\n]*\brefused\b"),
}


class _Unwrapped(argparse.HelpFormatter):
    """One line per help entry, so a phrase is never split over a wrap."""

    def __init__(self, prog):
        super().__init__(prog, width=100_000, max_help_position=60)


def _helps(parser: argparse.ArgumentParser, prog: str):
    """(prog, help text) for `parser` and every subparser beneath it."""
    parser.formatter_class = _Unwrapped
    yield prog, parser.format_help()
    for action in parser._actions:  # noqa: SLF001 - argparse's API
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            for name, sub in action.choices.items():
                yield from _helps(sub, f"{prog} {name}")


def stale_lines(parser: argparse.ArgumentParser, prog: str) -> list[str]:
    """Every help line in the tree naming a retired surface or a retired refusal."""
    pats = {**retired_surface.surfaces(), **SIGN_OFF}
    out = []
    for where, text in _helps(parser, prog):
        # Line by line: unwrapped, each line is one whole entry, and argparse's option lines
        # carry no sentence break, so a clause read across them would borrow a neighbour's
        # "retired".
        for line in text.splitlines():
            starts = [m.end() for m in retired_surface._SENTENCE_START.finditer(line)]
            out += [f"{where}: [{label}] {line.strip()}"
                    for label, rx in pats.items()
                    if any(not HELP_RETIRED_CONTEXT.search(
                               retired_surface._clause(line, starts, m.start()))
                           for m in rx.finditer(line))]
            out += [f"{where}: [{label}] {line.strip()}"
                    for label, rx in RETIRED_REFUSALS.items() if rx.search(line)]
    return out


def _parser(script: str) -> argparse.ArgumentParser:
    return loader.load_script(script).build_parser()


class HelpTextTests(unittest.TestCase):

    def test_no_help_names_a_retired_surface(self):
        """AC1. Every script's parser tree, subcommands included. MUTANTS: HEAD's five stale
        strings (sprint.py goal-review, reopen and batch; critic.py correct --boundary;
        mutation.py's description); a walk that formats the top-level help only."""
        # The scanner walks into a nested subcommand's options, excuses a mention that says the
        # surface is retired, and never one beside a refusal: a refusal teaches it as live.
        live = ["held to the sign-off's own rule",
                "the sign-off refuses a run without one",
                "a plan review is refused without one",
                "the sign-off principal, refused when it is the author",
                "`sprint close` refuses a unit whose mutation gate is red"]
        probe = argparse.ArgumentParser(prog="probe.py")
        leaf = probe.add_subparsers().add_parser("outer").add_subparsers().add_parser("inner")
        for i, text in enumerate(live):
            leaf.add_argument(f"--live{i}", help=text)
        leaf.add_argument("--old", help="the sign-off step is retired")
        flagged = stale_lines(probe, "probe.py")
        self.assertEqual(len(flagged), len(live), "\n".join(flagged))
        for text, line in zip(live, flagged):
            self.assertTrue(line.startswith("probe.py outer inner: [") and line.endswith(text),
                            line)

        records = surface.enumerate_scripts(loader.SCRIPTS_DIR)
        unread = {r.name: r.error for r in records
                  if r.error and r.name not in surface.NON_CLI}
        self.assertEqual(unread, {}, "a script the sweep cannot read is a help nobody checked")
        found = []
        for rec in records:
            if rec.readable:
                found += stale_lines(_parser(rec.name[:-3]), rec.name)
        self.assertEqual(found, [], "help text naming a surface v6 retired:\n" + "\n".join(found))

    def test_goal_review_help_says_advice(self):
        """AC2. `sprint.py goal-review --help` says the seats' read is advice printed with the
        plan, never a refusal, as `goal_review_status` behaves. MUTANT: HEAD's help, which says
        `sprint plan --write` refuses a goal no seat has reviewed."""
        sprint = loader.load_script("sprint")
        helps = dict(_helps(sprint.build_parser(), "sprint.py"))
        own = " ".join(helps["sprint.py goal-review"].split())
        summary = " ".join(helps["sprint.py"].split())
        for text in (own, summary):
            self.assertIn("advice printed with the plan", text)
            self.assertIn("never a refusal", text)
        self.assertNotRegex(own, r"(?i)\brefus(?:e[sd]?)\b")
        # The behaviour the words describe: an unreviewed goal is reported, not refused.
        with tempfile.TemporaryDirectory() as root:
            status = sprint.goal_review_status(root, "g")
        self.assertEqual((status["reviewed"], status["status"]), (False, "not read"))


if __name__ == "__main__":
    unittest.main()
