"""Behaviour an operator must be able to discover from `help/`, not from the hook.

A policy that lives only in a shell script is a policy nobody can look up. The gate's
boundary rule is the first of these: it decides when a commit pays for the whole suite and
when it pays for a selection, and an operator who cannot read that anywhere will either
distrust the fast commits or assume the slow ones are broken.

These tests pin the DOC against the CODE, not against a phrase: the moments the gate treats
as boundaries are read out of `gate.py` and each one must appear in the help page, so adding
a boundary without documenting it fails here.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
GATE = SKILL / "scripts" / "gate.py"
HELP = SKILL / "help" / "gate.md"


def _gate():
    sys.path.insert(0, str(GATE.parent))
    spec = importlib.util.spec_from_file_location("gate_for_help_coverage", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class GatePolicyDocsTests(unittest.TestCase):
    """US0495 AC2: the boundary policy is stated where an operator reads it."""

    def test_the_boundary_policy_is_documented(self) -> None:
        text = HELP.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("boundary", lowered,
                      "help/gate.md must state that some moments run the full suite")
        for moment in _gate().BOUNDARIES:
            self.assertIn(moment, lowered,
                          f"{moment} is a boundary in gate.py but is not named in "
                          f"help/gate.md - a policy only the hook knows is undiscoverable")
        # Both halves, or the page states only the expensive one and a reader still cannot
        # tell what a plain commit costs.
        self.assertIn("--suite-decision", text,
                      "the command that answers the question must be documented")
        self.assertTrue(
            "selection" in lowered or "selected" in lowered,
            "the page must say that a non-boundary run tests a SELECTION, not everything")
        self.assertIn("--boundary", text,
                      "the flag that declares a boundary must be documented, or the "
                      "policy cannot be invoked deliberately")


SPRINT = SKILL / "scripts" / "sprint.py"
SPRINT_HELP = SKILL / "help" / "sprint.md"

#: How a queue verb identifies ITSELF. The set is derived by asking the parser which verbs
#: describe themselves as charter/queue work, never by listing them here - a list in the test is
#: a second source of truth that goes stale exactly when a verb is added, which is the moment
#: this check exists for. AC1 says so in terms, and the first draft of this test broke it.
_QUEUE_MARKERS = ("charter", "queue")


def _sprint():
    sys.path.insert(0, str(SPRINT.parent))
    spec = importlib.util.spec_from_file_location("sprint_for_help_coverage", SPRINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class QueueDocsTests(unittest.TestCase):
    """US0492. The queue lifecycle documented beside the run lifecycle, pinned against the
    PARSER so a verb added without documentation fails here rather than being discovered by an
    operator who cannot find it.

    MUTANTS:
      1. read the expected verbs from a list here instead of from the parser -> a new verb is
         silently exempt.
      2. accept a verb named in prose rather than shown as an invocation -> the page describes
         a command nobody can copy.
    """

    def _queue_subverbs(self, parser) -> set:
        for action in parser._actions:
            if isinstance(getattr(action, "choices", None), dict) and "queue" in action.choices:
                q = action.choices["queue"]
                for sub in q._actions:
                    if isinstance(getattr(sub, "choices", None), dict):
                        return set(sub.choices)
        return set()

    def _queue_verbs(self, parser) -> set:
        """The queue verbs, asked OF THE PARSER: a top-level verb whose own help describes it as
        charter or queue work. Derived, so a verb added later is covered without editing this."""
        found = set()
        for action in parser._actions:
            if not isinstance(getattr(action, "choices", None), dict):
                continue
            # The parser's OWN help table - where `add_parser(help=...)` lands. A verb that is
            # queue lifecycle work says so in its own help, and this reads that rather than
            # matching on a name or a list kept here.
            for choice in getattr(action, "_choices_actions", []):
                blurb = (choice.help or "").lower()
                if any(m in blurb for m in _QUEUE_MARKERS):
                    found.add(choice.dest)
            break
        return found

    def _shown(self, page) -> list:
        """Only real INVOCATIONS - a command line, not a verb named in a sentence."""
        return [ln.strip() for ln in page.splitlines()
                if ln.strip().startswith("python3 <skill>/scripts/sprint.py")]

    def test_every_parser_verb_is_documented(self) -> None:
        page = SPRINT_HELP.read_text(encoding="utf-8")
        parser = _sprint().build_parser()
        verbs = self._queue_verbs(parser)
        self.assertTrue(verbs, "the parser describes no queue verb - the derivation is broken, "
                               "not the page")
        shown = self._shown(page)
        for verb in sorted(verbs):
            # An INVOCATION, not a mention: a verb named in prose is one nobody can copy.
            self.assertTrue(any(f"sprint.py {verb}" in ln for ln in shown),
                            f"`sprint {verb}` is a parser verb the queue docs never SHOW as a "
                            f"command - naming it in a sentence is not documenting it")
        for sub in sorted(self._queue_subverbs(parser)):
            self.assertTrue(any(f"sprint.py queue {sub}" in ln for ln in shown),
                            f"`sprint queue {sub}` is never shown as a command")

    def test_every_documented_invocation_parses(self) -> None:
        """An example that the command would reject is worse than no example: it costs the
        reader a round trip and teaches them to distrust the page."""
        import shlex
        page = SPRINT_HELP.read_text(encoding="utf-8")
        parser = _sprint().build_parser()
        shown = self._shown(page)
        verbs = self._queue_verbs(parser)
        queue_lines = [ln for ln in shown if any(f"sprint.py {v}" in ln for v in verbs)]
        self.assertTrue(queue_lines, "the page shows no queue invocation to check")
        for line in queue_lines:
            argv = shlex.split(line.replace("python3 <skill>/scripts/sprint.py", "").strip())
            argv = [a for a in argv if a != "\\"]
            with self.subTest(line=line):
                try:
                    parser.parse_args(argv)
                except SystemExit:
                    self.fail(f"the page shows an invocation the parser rejects: {line}")

    def test_the_materialise_late_reasoning_is_documented(self) -> None:
        """A reader arriving expecting frozen queued plans must find the DESIGN ANSWER, not the
        absence of a feature. The reasoning is what stops somebody 'fixing' it into a frozen
        batch later."""
        page = SPRINT_HELP.read_text(encoding="utf-8")
        head, _, tail = page.partition("## The charter queue")
        self.assertTrue(tail, "the queue lifecycle has no section in the run lifecycle's page")
        # Whitespace-normalised: a phrase split across a line break is still present, and
        # whether a doc happens to wrap mid-sentence must not decide a criterion.
        flat = " ".join(tail.split())
        for phrase in ("as it stands", "backlog"):
            self.assertIn(phrase, flat,
                          f"the queue section never says the batch is resolved {phrase!r}")
        self.assertTrue(
            any(w in flat for w in ("decays", "because", "would")),
            "the section states WHAT happens but never WHY - a design answer nobody can find "
            "is one somebody will reverse")


if __name__ == "__main__":
    unittest.main()
